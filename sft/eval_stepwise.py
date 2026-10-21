"""Greedy evaluation of arm S2: the model answers each step of Algorithm 1 (src/aba_steps.py).

    python sft/eval_stepwise.py --protocol chained --adapter runs/sft_step/adapter --out results/sft-step/s2/chained
    python sft/eval_stepwise.py --protocol chained --adapter runs/sft_step/adapter \
        --corpus corpus/v1-permuted --out results/sft-step-permuted/s2
    python sft/eval_stepwise.py --protocol gold --adapter runs/sft_step/adapter --out results/sft-step/s2/gold
    python sft/eval_stepwise.py ... --score-only           # re-score on CPU
    python sft/eval_stepwise.py ... --dry-run              # no model: hashes, reference runs, lengths
    python sft/eval_stepwise.py ... --smoke --limit 2      # CPU, the cached tiny Qwen2

As eval_sft.py: batch 1, greedy, repetition_penalty 1.0; each step under its kind's budget,
corpus/v1-step TOKENS.json `max_new_tokens`. Two protocols:

- chained: the reference keeps Algorithm 1's control flow and the model answers every step
  (ModelOracle), on its own path. The run, rendered in the trace grammar, is scored by
  eval_sft.score unchanged. Sets: the eval rows of --corpus (v1: test, held-out, Table 1;
  v1-permuted: test and held-out re-posed).
- gold: every state the reference visits on v1 test, held-out and Table 1 is asked once.
  yes/no by equality, folds by order (and by set), scans by set, RoLe and contrary facts by
  `_optimal`, the lines-16/18 failing examples by set where the answer set is unique.

calls.jsonl keeps every raw answer with its prompt's hash, appended as it goes, so a killed
job resumes; every score is recomputed from it. A chained run is replayed from its calls (the
replay must reproduce the run) to judge each call against the reference's answer at the same
state, with the call's signal cell on the run's own path (as `harvest` assigns it on the
reference's) and whether the state is still the reference's (on_path).

In --out: calls.jsonl (every raw answer), call_scores.jsonl (each call judged),
step_summary.json, sample.md; chained also generations.jsonl (each run's text and stop),
scores.jsonl and summary.json (eval_sft.score), run_scores.jsonl (per run: stop, first
check, exact and strict exact: no illegal item in any call), calls_sample.md.

Gold baseline: the majority train verdict (corpus/v1-step) among the steps with the same
position facets: kind, tier, source of the fact, first fact, fold rank capped at 2, first
check; without the tier where its votes are missing or tied (Table 1), else no. It reads
where a step falls in the run, never the problem.

Before reading the summaries: read sample.md and, for chained, calls_sample.md by hand.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import sys
import traceback
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # the repo root

from sft.eval_sft import _KEEP, _read, score
from sft.train_sft import _write
from sft.train_step import SMOKE_MODEL, load as load_steps
from src.aba_algorithm import ORACLE_KINDS, _current_framework, solve_aba_learning
from src.aba_corpus import _jsonl, _sha256
from src.aba_score import _key, _optimal, load_eval, reference
from src.aba_steps import (DECISIONS, STEP_PROMPT_VERSION, WITNESSED, ModelOracle,
                           RecordingOracle, StepStop, _pred, chained_run, gold_backend,
                           harvest, parse_answer, question, render_answer, render_state,
                           signal_cell, step_prompt)
from src.aba_tracelog import _git_rev
from src.aba_train import encode, model_id, revision, verified, versions
from src.aba_validator import _norm as _norm_atom

PROTOCOLS = ("chained", "gold")
_TRACES = ("traces.jsonl", "table1_traces.jsonl")
_FILES = ("problems.jsonl", "eval.jsonl", "table1_problems.jsonl", "table1_eval.jsonl") + _TRACES
_SAME = ("protocol", "model", "adapter_sha256", "decoding", "sha256")   # a resumed run's


def _h(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def budgets(a, steps: Path) -> Dict[str, int]:
    """Each kind's max_new_tokens, from the step corpus's token audit."""
    t = json.loads((steps / "TOKENS.json").read_text(encoding="utf-8"))
    m = json.loads((steps / "MANIFEST.json").read_text(encoding="utf-8"))
    assert t["sha256"] == m["sha256"] and t["prompt_version"] == STEP_PROMPT_VERSION, \
        "TOKENS.json is stale"
    assert a.smoke or t["model"] == model_id(a.model), f"TOKENS.json is for {t['model']}"
    return {k: min(v, a.max_new_tokens or v) for k, v in t["max_new_tokens"].items()}


def stored_records(corpus: Path) -> Dict[str, Dict]:
    return {r["problem_id"]: {"role_facts": r["role_facts"], "events": r["events"]}
            for n in _TRACES for r in _read(corpus / n)}


def gold_rows(problem, stored: Dict) -> List[Dict]:
    """The states the reference visits (`harvest`); its record must be the build's."""
    rows, record = harvest(problem, extra=False)
    if {"role_facts": record.role_facts, "events": [e.to_dict() for e in record.events]} != stored:
        raise SystemExit(f"{problem.problem_id}: the reference changed since the build")
    return rows


# ─────────────────────────────────────────────────────────────────────────────
# Generation
# ─────────────────────────────────────────────────────────────────────────────

def recorder(backend, budget: Dict[str, int], log: List[Dict]) -> Callable[[str, str], str]:
    """generate(prompt, kind): the model, greedy, under the kind's budget; each call logged."""
    def generate(prompt: str, kind: str) -> str:
        resp = backend.generate(prompt, temperature=0.0, max_tokens=budget[kind],
                                repetition_penalty=1.0)
        if resp.prompt_tokens != encode(backend.tok, prompt)[1]:   # ends the job, not the problem
            raise SystemExit("generation is not fed the ids the model was trained after")
        log.append({"kind": kind, "prompt_sha256": _h(prompt), "prompt_tokens": resp.prompt_tokens,
                    "raw": resp.text,
                    "finish": "length" if resp.completion_tokens >= budget[kind] else "stop",
                    "completion_tokens": resp.completion_tokens,
                    "latency_s": round(resp.latency_s, 2)})
        return resp.text
    return generate


def run(problem, oracle) -> Tuple[Optional[str], str, Optional[int], Optional[str]]:
    """(error, text, retractions, traceback) of a chained run; a crash ends the problem, not the job."""
    try:
        r = chained_run(problem, oracle)
        return r["error"], r["text"], r["retractions"], None
    except Exception as e:
        return f"crash:{type(e).__name__}", "", None, traceback.format_exc(limit=8)


def open_run(a, corpus: Path, steps: Path, out: Path, budget: Dict[str, int]):
    """EVAL_MANIFEST.json (a resumed run must be the same run), then the model."""
    mid = SMOKE_MODEL if a.smoke else model_id(a.model)
    tm = Path(a.adapter).parent / "TRAINING_MANIFEST.json" if a.adapter else None
    if tm is not None and tm.exists():
        cfg = json.loads(tm.read_text(encoding="utf-8"))["config"]
        assert cfg.get("prompt_version") == STEP_PROMPT_VERSION, \
            f"{a.adapter} was not trained on {STEP_PROMPT_VERSION} step prompts"
    manifest = {
        "protocol": a.protocol, "prompt_version": STEP_PROMPT_VERSION,
        "model": mid, "revision": revision(mid), "adapter": a.adapter,
        "adapter_sha256": _sha256(Path(a.adapter) / "adapter_model.safetensors")
                          if a.adapter else None,
        "decoding": {"greedy": True, "repetition_penalty": 1.0, "max_new_tokens": budget},
        "code_rev": _git_rev(), "versions": versions(),
        "sha256": verified(corpus, [n for n in _FILES if (corpus / n).exists()]),
        "steps_sha256": {"TOKENS.json": _sha256(steps / "TOKENS.json")},
    }
    mpath = out / "EVAL_MANIFEST.json"
    if mpath.exists() and (out / "calls.jsonl").exists():
        old = json.loads(mpath.read_text(encoding="utf-8"))
        if any(old.get(k) != manifest[k] for k in _SAME):
            raise SystemExit(f"{out} holds calls of another run; use a new --out")
    _write(mpath, manifest)

    import torch
    from src.aba_model import LocalHFBackend
    backend = (LocalHFBackend(SMOKE_MODEL, dtype="float32", device="cpu", adapter=a.adapter)
               if a.smoke else
               LocalHFBackend(a.model, dtype=a.dtype, device=a.device, adapter=a.adapter))
    manifest.update(cuda=torch.version.cuda, gpu=torch.cuda.get_device_name(0)
                    if torch.cuda.is_available() else None)
    _write(mpath, manifest)
    return backend


def generate_chained(backend, budget: Dict[str, int], out: Path, items) -> None:
    cpath, gpath = out / "calls.jsonl", out / "generations.jsonl"
    done = {g["problem_id"] for g in _read(gpath)}
    calls = _read(cpath)
    if any(c["problem_id"] not in done for c in calls):     # killed before its generation line
        _jsonl(cpath, [c for c in calls if c["problem_id"] in done])
    todo = [(row, p) for row, p, _ in items if row["problem_id"] not in done]
    print(f"chained: {len(todo)} problems ({len(done)} already done), budgets {budget}")
    with open(cpath, "a", encoding="utf-8") as fc, open(gpath, "a", encoding="utf-8") as fg:
        for n, (row, problem) in enumerate(todo, 1):
            pid = row["problem_id"]
            assert reference(problem).trace_target == row["trace_target"], \
                f"{pid}: the reference changed since the build"
            log: List[Dict] = []
            error, text, retractions, tb = run(problem, ModelOracle(
                problem, recorder(backend, budget, log)))
            fc.writelines(json.dumps({"problem_id": pid, "i": i, **c}) + "\n"
                          for i, c in enumerate(log))
            fc.flush()
            fg.write(json.dumps({**{k: row[k] for k in _KEEP}, "raw_output": text,
                                 "finish": "stopped" if error else "stop", "error": error,
                                 "n_calls": len(log), "retractions": retractions,
                                 "completion_tokens": sum(c["completion_tokens"] for c in log),
                                 "latency_s": round(sum(c["latency_s"] for c in log), 2),
                                 "traceback": tb}) + "\n")
            fg.flush()
            if n % 10 == 0 or n == len(todo):
                print(f"  {n}/{len(todo)}  last: {len(log)} calls, {error or 'ok'}", flush=True)


def generate_gold(backend, budget: Dict[str, int], out: Path, items, corpus: Path) -> None:
    cpath = out / "calls.jsonl"
    done = {(c["problem_id"], c["k"]) for c in _read(cpath)}
    stored = stored_records(corpus)
    print(f"gold: {len(items)} problems ({len(done)} states already asked), budgets {budget}")
    with open(cpath, "a", encoding="utf-8") as fc:
        for n, (row, problem, _) in enumerate(items, 1):
            pid = row["problem_id"]
            for r in gold_rows(problem, stored[pid]):
                if (pid, r["k"]) in done:
                    continue
                log: List[Dict] = []
                recorder(backend, budget, log)(step_prompt(problem, r["kind"], r["state"]), r["kind"])
                fc.write(json.dumps({"problem_id": pid, "k": r["k"], **log[0]}) + "\n")
                fc.flush()
            if n % 10 == 0 or n == len(items):
                print(f"  {n}/{len(items)} problems", flush=True)


# ─────────────────────────────────────────────────────────────────────────────
# Judging a step
# ─────────────────────────────────────────────────────────────────────────────

class ShadowOracle(ModelOracle):
    """ModelOracle that also keeps, per call, its payload and the reference's and model's answers."""

    def __call__(self, kind, state, compute):
        n, box = len(self.log), {}

        def shadow():
            box["gold"] = compute()
            return box["gold"]
        try:
            answer = super().__call__(kind, state, shadow)
        finally:
            if len(self.log) > n:
                self.log[-1].update(payload=state, gold=box.get("gold"))
        if len(self.log) > n:
            self.log[-1]["answer"] = answer
        return answer


def replay(calls: List[Dict]) -> Callable[[str, str], str]:
    """generate(prompt, kind) answering with the recorded calls, in order, prompt for prompt."""
    it = iter(calls)

    def generate(prompt: str, kind: str) -> str:
        c = next(it, None)
        if c is None or (c["kind"], c["prompt_sha256"]) != (kind, _h(prompt)):
            raise SystemExit("the replay leaves the recorded run: the code or calls.jsonl changed")
        return c["raw"]
    return generate


def shown(kind: str, answer) -> str:
    """The reference's answer as the step's target (decisions: the verdict only)."""
    if kind in DECISIONS:
        return "yes." if answer else "no."
    if kind in ("role", "contrary_facts") and not answer[1]:
        return "(no answer set)"
    return render_answer(kind, answer)


def facts_optimal(problem, kind: str, facts, s: Dict) -> bool:
    """`facts` are an optimal answer of line 8's program (role) or line 44's, on the
    framework asm_intro_options builds for it."""
    if kind == "role":
        return _optimal(facts, problem.background, problem, list(problem.learnable))
    fold = s["folded"].to_prolog()
    learnt = [r for r in s["learnt"] if r.to_prolog() != fold] + [s["guarded"]]
    fw = _current_framework(problem.background, learnt, {**s["new_asms"], s["asm"]: s["contrary"]})
    return _optimal(facts, fw, problem, [_pred(s["contrary"])])


def judge_run(problem, log: List[Dict]) -> List[Dict]:
    """Each call of a chained run against the reference's answer at the same state."""
    out, role, folds = [], set(), {}
    event, src, checks, on_path = -1, "role", 0, True
    for i, e in enumerate(log):
        kind, s, gold, ans = e["kind"], e["payload"], e["gold"], e.get("answer")
        if kind == "subsume":
            event += 1
            src = "role" if s["rule"].to_prolog() in role else "contrary"
        f = {"kind": kind, "event": event, "src": src, "extra": False}
        if kind == "check":
            fl, fold = folds.get(s["rule"].to_prolog(), []), s["folded"].to_prolog()
            f.update(rank=fl.index(fold) if fold in fl else None, first=checks == 0)
            checks += 1
        same = bool(e.get("correct"))
        rec = {"i": i, **f, "cell": signal_cell(f), "on_path": on_path, "error": e.get("error"),
               "illegal": e.get("illegal", 0), "same": same, "correct": same,
               "raw": e["raw"], "shadow": shown(kind, gold)}
        if kind in DECISIONS:
            rec.update(truth=gold, said=ans)
            if kind in WITNESSED:
                rec["witness"] = e.get("witness")
        if ans is not None and kind == "reuse_scan":
            rec["correct"] = set(ans) == set(gold)
        if ans is not None and kind in ("role", "contrary_facts"):
            rec["correct"] = facts_optimal(problem, kind, ans[0], s)
        out.append(rec)
        if ans is None:                         # the call that stopped the run
            break
        on_path = on_path and same
        if kind == "role":
            role = {r.to_prolog() for r in ans[0]}
        if kind == "fold_candidates":
            folds[s["rule"].to_prolog()] = [r.to_prolog() for r, _ in ans]
    return out


def judge_gold(problem, r: Dict, raw: str) -> Dict:
    """One asked state against the reference's answer there."""
    kind = r["kind"]
    rec = {"error": None, "illegal": 0, "correct": False}
    if kind in DECISIONS:
        rec.update(truth=r["verdict"], said=None)
    try:
        ans, notes = parse_answer(kind, raw, problem, r["answer"], r["payload"])
    except StepStop as e:
        rec["error"] = e.code
        return rec
    rec["illegal"] = notes["illegal"]
    if kind in DECISIONS:
        rec.update(said=ans, correct=ans == r["verdict"])
        if kind in WITNESSED and r["n_models"] == 1:
            w = notes.get("witness")
            rec["witness_correct"] = (w is not None and {_norm_atom(x) for x in w}
                                      == {_norm_atom(x) for x in r["witness"]})
    elif kind == "fold_candidates":
        got, want = [_key(x) for x, _ in ans], [_key(x) for x, _ in r["answer"]]
        rec.update(correct=got == want, set_correct=set(got) == set(want))
    elif kind == "reuse_scan":
        rec["correct"] = set(ans) == set(r["answer"])
    else:
        rec["correct"] = facts_optimal(problem, kind, ans[0], r["payload"])
    return rec


class Baseline:
    """The majority train verdict among steps with the same position facets (module doc)."""

    def __init__(self, rows: List[Dict]):
        self.votes = collections.defaultdict(collections.Counter)
        for r in rows:
            if r["kind"] in DECISIONS and not r["extra"]:
                for key in self.keys(r, r["tier"]):
                    self.votes[key][r["verdict"]] += 1

    @staticmethod
    def keys(r: Dict, tier: str) -> List[Tuple]:
        f = (r["kind"], r["src"], r["event"] == 0, min(r.get("rank") or 0, 2), bool(r.get("first")))
        return [(tier,) + f, (None,) + f]

    def guess(self, r: Dict, tier: str) -> bool:
        for key in self.keys(r, tier):
            c = self.votes.get(key)
            if c and c[True] != c[False]:
                return c[True] > c[False]
        return False


# ─────────────────────────────────────────────────────────────────────────────
# Scoring and the summaries
# ─────────────────────────────────────────────────────────────────────────────

def _rate(xs) -> Optional[float]:
    xs = [bool(x) for x in xs]
    return round(sum(xs) / len(xs), 4) if xs else None


def _balanced(pairs) -> Optional[float]:
    """Mean recall on truth-yes and truth-no, None unless both occur; said None is a miss."""
    yes = [s is True for t, s in pairs if t]
    no = [s is False for t, s in pairs if not t]
    return round((sum(yes) / len(yes) + sum(no) / len(no)) / 2, 4) if yes and no else None


def _groups(rs: List[Dict]) -> Dict[str, List[Dict]]:
    out = collections.defaultdict(list)
    for r in rs:
        for k in ("all", f"split:{r['split']}", f"tier:{r['tier']}"):
            out[k].append(r)
    return dict(out)


def _stats(rs: List[Dict]) -> Dict:
    s = {"n": len(rs), "acc": _rate(r["correct"] for r in rs),
         "unusable": sum(r["error"] is not None for r in rs),
         "with_illegal": sum(r["illegal"] > 0 for r in rs),
         "truncated": sum(r["finish"] == "length" for r in rs)}
    dec = [r for r in rs if "truth" in r]
    if dec:
        s["truth_yes"] = _rate(r["truth"] for r in dec)
        s["balanced"] = _balanced([(r["truth"], r["said"]) for r in dec])
        if all("baseline" in r for r in dec):
            s["baseline_acc"] = _rate(r["baseline"] == r["truth"] for r in dec)
            s["baseline_balanced"] = _balanced([(r["truth"], r["baseline"]) for r in dec])
    for k in ("set_correct", "witness_correct", "same"):
        xs = [r[k] for r in rs if k in r]
        if xs:
            s[k] = {"n": len(xs), "acc": _rate(xs)}
    return s


def _table(rs: List[Dict], key: str) -> Dict:
    by = collections.defaultdict(list)
    for r in rs:
        by[r[key]].append(r)
    order = ORACLE_KINDS if key == "kind" else sorted(by)
    return {k: _stats(by[k]) for k in order if k in by}


def calls_summary(recs: List[Dict], on_path: bool = False) -> Dict:
    out = {}
    for name, rs in _groups(recs).items():
        out[name] = {"by_kind": _table(rs, "kind"), "by_cell": _table(rs, "cell")}
        if on_path:
            out[name]["at_reference_state"] = _table([r for r in rs if r["on_path"]], "kind")
    return out


def run_stats(rs: List[Dict]) -> Dict:
    """Per set of chained runs: stops, exact (strict: no illegal item in any call), first check."""
    reached = [r for r in rs if r["first_check"]]
    pair = lambda r: ((r["first_check"]["truth"], r["first_check"]["said"]) if r["first_check"]
                      else (r["gold_first_check"], None))
    return {
        "n": len(rs), "exact": _rate(r["exact"] for r in rs),
        "strict_exact": _rate(r["strict_exact"] for r in rs),
        "stops": dict(collections.Counter(r["error"] or "ok" for r in rs)),
        "calls_mean": round(sum(r["n_calls"] for r in rs) / len(rs), 2),
        "reference_steps_mean": round(sum(r["gold_steps"] for r in rs) / len(rs), 2),
        "first_check": {
            "reached": len(reached), "at_reference_state": sum(r["first_check"]["on_path"]
                                                               for r in reached),
            "balanced_reached": _balanced([pair(r) for r in reached]),
            # not reached: a miss, against the reference's first verdict
            "balanced": _balanced([pair(r) for r in rs
                                   if r["first_check"] or r["gold_first_check"] is not None])},
    }


def gold_path(problem) -> Tuple[int, Optional[bool]]:
    """(steps the reference takes, its first line-18 verdict)."""
    orc = RecordingOracle()
    solve_aba_learning(problem, oracle=orc)
    return len(orc.calls), next((a for k, _, a in orc.calls if k == "check"), None)


def score_chained(out: Path, items) -> int:
    gens = {g["problem_id"]: g for g in _read(out / "generations.jsonl")}
    calls = collections.defaultdict(list)
    for c in _read(out / "calls.jsonl"):
        calls[c["problem_id"]].append(c)
    recs, runs, show = [], [], []
    for row, problem, _ in items:
        pid, g = row["problem_id"], gens.get(row["problem_id"])
        if g is None:
            continue
        cs = sorted(calls[pid], key=lambda c: c["i"])
        oracle = ShadowOracle(problem, replay(cs))
        error, text, _, _ = run(problem, oracle)
        if (error, text, len(oracle.log)) != (g["error"], g["raw_output"], len(cs)):
            raise SystemExit(f"{pid}: the replay does not reproduce the recorded run")
        judged, meta = judge_run(problem, oracle.log), {k: row[k] for k in _KEEP}
        for r, c, e in zip(judged, cs, oracle.log):
            r.update(meta, finish=c["finish"])
            show.append((r, e["state"]))
        recs += judged
        steps, first_gold = gold_path(problem)
        first = next((r for r in judged if r.get("first")), None)
        runs.append({**meta, "error": error, "n_calls": len(cs), "gold_steps": steps,
                     "first_check": first and {k: first[k] for k in ("truth", "said", "on_path")},
                     "gold_first_check": first_gold,
                     "any_illegal": any(r["illegal"] for r in judged),
                     "truncated_calls": sum(c["finish"] == "length" for c in cs)})
    if not runs:
        print(f"nothing to score in {out}")
        return 1
    _jsonl(out / "call_scores.jsonl", recs)
    rc = score(out, items)                    # eval_sft: scores.jsonl, summary.json, sample.md
    exact = {r["problem_id"]: r["exact"] for r in _read(out / "scores.jsonl")}
    for r in runs:
        r["exact"] = exact[r["problem_id"]]
        r["strict_exact"] = r["exact"] and not r["any_illegal"]
    _jsonl(out / "run_scores.jsonl", runs)
    summary = {"runs": {k: run_stats(v) for k, v in _groups(runs).items()},
               "calls": calls_summary(recs, on_path=True)}
    _write(out / "step_summary.json", summary)
    _print(summary["calls"])
    for k in [k for k in summary["runs"] if k == "all" or k.startswith("split:")]:
        s = summary["runs"][k]
        print(f"{k:14s} exact {s['exact']} strict {s['strict_exact']}  first check: reached "
              f"{s['first_check']['reached']}/{s['n']}, balanced {s['first_check']['balanced']}"
              f"  stops {s['stops']}")
    sample_runs(out / "calls_sample.md", runs, show)
    return rc


def score_gold(out: Path, items, corpus: Path, steps: Path) -> int:
    calls = {(c["problem_id"], c["k"]): c for c in _read(out / "calls.jsonl")}
    if not calls:
        print(f"nothing to score in {out}")
        return 1
    base = Baseline(load_steps(steps)[2]["train"])
    stored = stored_records(corpus)
    recs, show = [], []
    for row, problem, _ in items:
        pid = row["problem_id"]
        for r in gold_rows(problem, stored[pid]):
            c = calls.get((pid, r["k"]))
            if c is None:
                continue
            if (c["kind"], c["prompt_sha256"]) != (r["kind"], _h(step_prompt(problem, r["kind"],
                                                                               r["state"]))):
                raise SystemExit(f"{pid}#{r['k']}: not the state that was asked")
            rec = {**{k: row[k] for k in _KEEP}, "k": r["k"], "kind": r["kind"], "cell": r["cell"],
                   "event": r["event"], "src": r["src"], "rank": r.get("rank"),
                   "first": r.get("first"), "n_models": r.get("n_models"), "finish": c["finish"],
                   **judge_gold(problem, r, c["raw"]), "raw": c["raw"], "target": r["target"]}
            if r["kind"] in DECISIONS:
                rec["baseline"] = base.guess(r, row["tier"])
            recs.append(rec)
            show.append((rec, r["state"]))
    _jsonl(out / "call_scores.jsonl", recs)
    summary = calls_summary(recs)
    _write(out / "step_summary.json", summary)
    _print(summary)
    sample_gold(out / "sample.md", show)
    print(f"scored {len(recs)} asked states; {len(calls) - len(recs)} recorded calls outside "
          f"these problems")
    return 0


def _print(summary: Dict) -> None:
    for name in [k for k in summary if k == "all" or k.startswith("split:")]:
        print(f"\n{name}")
        for kind, s in summary[name]["by_kind"].items():
            bal = f"  balanced {s['balanced']}" if s.get("balanced") is not None else ""
            base = (f"  baseline {s['baseline_balanced']}"
                    if s.get("baseline_balanced") is not None else "")
            print(f"  {kind:16s} n={s['n']:5d}  acc {s['acc']}{bal}{base}  "
                  f"unusable {s['unusable']}")


def _shown_call(rec: Dict, state: Dict, gold: str) -> str:
    ctx = "" if rec["kind"] == "role" else render_state(state) + "\n\n"
    return (f"## {rec['problem_id']} {rec['kind']} ({rec['cell']}): correct {rec['correct']}, "
            f"error `{rec['error']}`\n\n```\n{ctx}{question(rec['kind'], state)}\n```\n\n"
            f"reference:\n```\n{gold}\n```\nmodel:\n```\n{rec['raw']}\n```\n\n")


def sample_gold(path: Path, show) -> None:
    rng, by = random.Random(0), collections.defaultdict(list)
    for rec, state in show:
        by[rec["kind"]].append((rec, state))
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Hand audit: 3 asked states per kind of {path.parent.as_posix()}\n\n")
        for kind in ORACLE_KINDS:
            for rec, state in rng.sample(by[kind], min(3, len(by[kind]))):
                f.write(_shown_call(rec, state, rec["target"]))


def sample_runs(path: Path, runs: List[Dict], show) -> None:
    pick = {r["problem_id"] for r in random.Random(0).sample(runs, min(5, len(runs)))}
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Hand audit: every call of 5 chained runs of {path.parent.as_posix()}\n\n")
        for r in runs:
            if r["problem_id"] in pick:
                f.write(f"# {r['problem_id']} ({r['split']}, {r['class']}): {r['n_calls']} calls, "
                        f"stop `{r['error']}`, exact {r['exact']}\n\n")
                f.writelines(_shown_call(rec, st, rec["shadow"]) for rec, st in show
                             if rec["problem_id"] == r["problem_id"])


# ─────────────────────────────────────────────────────────────────────────────
# Dry run
# ─────────────────────────────────────────────────────────────────────────────

def dry_run(a, corpus: Path, items, budget: Dict[str, int]) -> int:
    """No model: the hashes, the reference on every problem (chained: its answers through the
    controller reproduce the trace target), the longest prompt plus budget on its path."""
    from transformers import AutoConfig, AutoTokenizer
    mid = SMOKE_MODEL if a.smoke else model_id(a.model)
    tok = AutoTokenizer.from_pretrained(mid)
    verified(corpus, [n for n in _FILES if (corpus / n).exists()])
    stored = stored_records(corpus) if a.protocol == "gold" else None
    kinds, longest = collections.Counter(), (0, "")
    for row, problem, _ in items:
        pid = row["problem_id"]
        if stored is not None:
            rows = gold_rows(problem, stored[pid])
        else:
            rows, _ = harvest(problem, extra=False)
            text = chained_run(problem, ModelOracle(problem, gold_backend(rows, problem)))["text"]
            assert text == row["trace_target"], f"{pid}: gold answers do not reproduce the trace"
        for r in rows:
            kinds[r["kind"]] += 1
            n = encode(tok, step_prompt(problem, r["kind"], r["state"]))[1] + budget[r["kind"]]
            longest = max(longest, (n, f"{pid}#{r['k']} {r['kind']}"))
    context = AutoConfig.from_pretrained(mid).max_position_embeddings
    print(f"{a.protocol}: {len(items)} problems, {sum(kinds.values())} steps on the reference's "
          f"path {dict(kinds)}\n  longest prompt + budget {longest[0]} tokens ({longest[1]}), "
          f"context {context}")
    assert longest[0] <= context, "a step would not fit the context"
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--protocol", choices=PROTOCOLS, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--adapter", default=None, help="LoRA adapter dir; none = the base model")
    ap.add_argument("--corpus", default="corpus/v1")
    ap.add_argument("--steps", default="corpus/v1-step", help="budgets, and the baseline's rows")
    ap.add_argument("--model", default="qwen2.5-7b")
    ap.add_argument("--score-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="no model (login node)")
    ap.add_argument("--limit", type=int, default=None, help="first N problems (smoke test)")
    ap.add_argument("--max-new-tokens", type=int, default=None,
                    help="cap every kind's budget (smoke test only)")
    ap.add_argument("--smoke", action="store_true", help=f"{SMOKE_MODEL} on CPU; needs --limit")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--dtype", default="bfloat16")
    a = ap.parse_args(argv)
    if a.smoke and not a.limit:
        ap.error("--smoke needs --limit")
    corpus, steps, out = Path(a.corpus), Path(a.steps), Path(a.out)
    if a.protocol == "gold" and not (corpus / "traces.jsonl").exists():
        ap.error(f"the gold protocol needs the reference's records; {corpus} has none")

    budget = budgets(a, steps)
    items = load_eval(corpus)[:a.limit]
    if a.dry_run:
        return dry_run(a, corpus, items, budget)
    out.mkdir(parents=True, exist_ok=True)
    if not a.score_only:
        backend = open_run(a, corpus, steps, out, budget)
        if a.protocol == "chained":
            generate_chained(backend, budget, out, items)
        else:
            generate_gold(backend, budget, out, items, corpus)
    return score_chained(out, items) if a.protocol == "chained" else \
        score_gold(out, items, corpus, steps)


if __name__ == "__main__":
    sys.exit(main())
