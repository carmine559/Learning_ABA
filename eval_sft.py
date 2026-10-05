"""Greedy generation (k=1) on the evaluation problems, scored by src.aba_score.

    python eval_sft.py --adapter runs/sft_endpoint/adapter --out results/sft/endpoint
    python eval_sft.py --out results/sft/base                  # no adapter: the base model
    python eval_sft.py --out results/sft/endpoint --score-only # re-score on CPU

Rows: eval.jsonl (test, held-out t8/t9) and table1_eval.jsonl. Greedy is the
argmax of the model under evaluation: repetition_penalty is 1.0 for every arm,
where Qwen's generation_config applies 1.05. Every arm gets the same budget,
TOKENS.json `max_new_tokens`. generations.jsonl keeps each raw output and why
generation stopped, and is appended as it goes, so a killed job resumes; the
scores are always recomputed from it.

Before reading summary.json: read sample.md (20 rows, fixed seed) by hand.
"""
from __future__ import annotations

import argparse
import collections
import json
import random
import sys
from pathlib import Path
from typing import Dict, List, Optional

from src.aba_corpus import _sha256
from src.aba_score import YES_NO, load_eval, reference, reward, score_output
from src.aba_tracelog import _git_rev
from src.aba_train import encode, load_audit, model_id, revision, verified, versions

_KEEP = ("problem_id", "tier", "split", "class")


def _read(path: Path) -> List[Dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def generate(a, corpus: Path, out: Path, items) -> None:
    audit = load_audit(corpus, a.model)
    budget = a.max_new_tokens or audit["max_new_tokens"]
    manifest = {
        "model": model_id(a.model), "revision": revision(model_id(a.model)),
        "adapter": a.adapter,
        "adapter_sha256": _sha256(Path(a.adapter) / "adapter_model.safetensors")
                          if a.adapter else None,
        "decoding": {"greedy": True, "repetition_penalty": 1.0, "max_new_tokens": budget},
        "code_rev": _git_rev(), "versions": versions(),
        "sha256": verified(corpus, [n for n in ("problems.jsonl", "eval.jsonl",
                                                "table1_problems.jsonl", "table1_eval.jsonl")
                                    if (corpus / n).exists()]),
    }
    mpath, gpath = out / "EVAL_MANIFEST.json", out / "generations.jsonl"
    if gpath.exists() and mpath.exists():
        old = json.loads(mpath.read_text(encoding="utf-8"))
        same = ("model", "adapter_sha256", "decoding", "sha256")
        if any(old[k] != manifest[k] for k in same):
            raise SystemExit(f"{out} holds generations of another run; use a new --out")
    mpath.write_text(json.dumps(manifest, indent=1), encoding="utf-8")

    import torch
    from src.aba_model import LocalHFBackend
    backend = LocalHFBackend(a.model, dtype=a.dtype, device=a.device, adapter=a.adapter)
    manifest.update(cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0)
                    if torch.cuda.is_available() else None)
    mpath.write_text(json.dumps(manifest, indent=1), encoding="utf-8")

    done = {g["problem_id"] for g in _read(gpath)}
    todo = [row for row, _, _ in items if row["problem_id"] not in done]
    print(f"generating {len(todo)} rows ({len(done)} already done), budget {budget}")
    with open(gpath, "a", encoding="utf-8") as f:
        for i, row in enumerate(todo, 1):
            resp = backend.generate(row["prompt"], temperature=0.0, max_tokens=budget,
                                    repetition_penalty=1.0)
            assert resp.prompt_tokens == encode(backend.tok, row["prompt"])[1]
            f.write(json.dumps({**{k: row[k] for k in _KEEP},
                                "raw_output": resp.text,
                                "finish": "length" if resp.completion_tokens >= budget
                                          else "stop",
                                "completion_tokens": resp.completion_tokens,
                                "latency_s": round(resp.latency_s, 2)}) + "\n")
            f.flush()
            if i % 10 == 0 or i == len(todo):
                print(f"  {i}/{len(todo)}  last {resp.completion_tokens} tokens "
                      f"in {resp.latency_s:.0f}s", flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# Scoring and the summary
# ─────────────────────────────────────────────────────────────────────────────

def _mean(xs) -> Optional[float]:
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 4) if xs else None


def _balanced(c: collections.Counter) -> Optional[float]:
    """Mean of the recall on truth-yes and on truth-no; 0.5 for any constant answer."""
    yes, no = c["yes/yes"] + c["yes/no"], c["no/no"] + c["no/yes"]
    return round((c["yes/yes"] / yes + c["no/no"] / no) / 2, 4) if yes and no else None


def _aggregate(rs: List[Dict]) -> Dict:
    r3 = collections.Counter(f"{'yes' if r['ref_defeasible'] else 'no'}/"
                             f"{'yes' if r['defeasible'] else 'no'}"
                             for r in rs if r["defeasible"] is not None)
    r2 = collections.Counter()
    for r in rs:
        r2.update(r["r2_bodies"])
    out = {
        "n": len(rs),
        **{k: _mean(r[k] for r in rs) for k in ("parse_ok", "truncated", "valid",
                                                  "clean", "exact", "agreement", "reward")},
        "algorithm_choice": _mean(r["algorithm_choice"] for r in rs),
        "r2_exact": round(r2["exact"] / r2["n"], 4) if r2["n"] else None,
        "r3_balanced": _balanced(r3),
        "trace_f1": _mean(r["trace_fidelity"]["f1"] for r in rs     # None: unparseable
                          if r["trace_fidelity"] and r["trace_fidelity"]["has_trace"]),
        "trace_f1_ceiling": _mean(r["ceiling_f1"] for r in rs),     # the gold trace's own
        "errors": dict(collections.Counter(r["error"] for r in rs)),
    }
    audits = [r["audit"] for r in rs if r["audit"]]
    if audits:
        conf = {k: collections.Counter() for k in YES_NO}
        for au in audits:
            for k, c in au["confusion"].items():
                conf[k].update(c)
        out["audit"] = {"n": len(audits),
                        "accuracy": _mean(au["accuracy"] for au in audits),
                        "any_illegal": _mean(bool(au["illegal"]) for au in audits),
                        "balanced": {k: _balanced(c) for k, c in conf.items()}}
    return out


def score(out: Path, items) -> int:
    gens = {g["problem_id"]: g for g in _read(out / "generations.jsonl")}
    scored = []
    with open(out / "scores.jsonl", "w", encoding="utf-8") as f:
        for row, problem, meta in items:
            g = gens.get(row["problem_id"])
            if g is None:
                continue
            ref = reference(problem)
            assert (ref.trace_target, ref.endpoint_target) == (
                row["trace_target"], row["endpoint_target"]), "reference changed since the build"
            card = score_output(g["raw_output"], ref, meta, truncated=g["finish"] == "length")
            rec = {**{k: g[k] for k in _KEEP + ("finish", "completion_tokens")},
                   "reward": reward(card), "ceiling_f1": row["ceiling"]["f1"],
                   **card.to_dict()}
            f.write(json.dumps(rec) + "\n")
            scored.append(rec)
    if not scored:
        print(f"nothing to score in {out}")
        return 1

    groups = collections.defaultdict(list)
    for r in scored:
        for key in ("all", f"split:{r['split']}", f"tier:{r['tier']}"):
            groups[key].append(r)
    summary = {k: _aggregate(v) for k, v in groups.items()}
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")

    cols = ("parse_ok", "truncated", "valid", "clean", "exact", "agreement",
            "algorithm_choice")
    print(f"\n{'group':18s} {'n':>4s} " + " ".join(f"{c[:8]:>8s}" for c in cols)
          + f" {'audit':>8s}")
    for k, s in summary.items():
        cells = " ".join(f"{'-' if s[c] is None else f'{s[c]:.3f}':>8s}" for c in cols)
        acc = s.get("audit", {}).get("accuracy")
        print(f"{k:18s} {s['n']:4d} {cells} {'-' if acc is None else f'{acc:.3f}':>8s}")
    print(f"missing: {len(items) - len(scored)} rows without a generation")

    with open(out / "sample.md", "w", encoding="utf-8") as f:
        f.write(f"# Hand audit: 20 rows of {out}\n\n")
        for r in sorted(random.Random(0).sample(scored, min(20, len(scored))),
                        key=lambda r: r["problem_id"]):
            f.write(f"## {r['problem_id']} ({r['split']}, {r['class']})\n\n"
                    f"error `{r['error']}`, finish `{r['finish']}`, valid {r['valid']}, "
                    f"clean {r['clean']}, exact {r['exact']}\n\n"
                    f"```\n{gens[r['problem_id']]['raw_output']}\n```\n\n")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--adapter", default=None, help="LoRA adapter dir; none = base model")
    ap.add_argument("--corpus", default="corpus/v1")
    ap.add_argument("--model", default="qwen2.5-7b")
    ap.add_argument("--score-only", action="store_true")
    ap.add_argument("--limit", type=int, default=None, help="first N rows (smoke test)")
    ap.add_argument("--max-new-tokens", type=int, default=None,
                    help="override TOKENS.json (smoke test only)")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    a = ap.parse_args(argv)

    corpus, out = Path(a.corpus), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    items = load_eval(corpus)[:a.limit]
    if not a.score_only:
        generate(a, corpus, out, items)
    return score(out, items)


if __name__ == "__main__":
    sys.exit(main())
