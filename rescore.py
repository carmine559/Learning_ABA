"""
rescore.py
Recompute every metric of a finished run from the raw LLM answers it stored.

WHY
---
`results_<mode>.jsonl` keeps the full `raw_output` of every sample, and the
benchmark is generated from a fixed seed, so a run can be scored again offline:
rebuild the identical problem set and the algorithm's run on each problem, and
re-score each stored answer. A change to the parser or the scorer costs minutes
of CPU instead of a day of GPU.

USAGE
-----
    # rescore in place (rows and summary.json)
    python rescore.py results/e2e_whole_v4/bench_qwen2.5-7b

    # several runs, into a separate tree
    python rescore.py "results/e2e_whole_v4/bench_*" --out rescored/

    # step probes
    python rescore.py experiments/06_probes_v3/bench_qwen2.5-3b --probes

An end-to-end run is rebuilt from the `run` block of its summary.json. Runs that
held out examples (sets 00-03 and set 05's end-to-end half) have no such block
and are refused: they are kept as the as-run record (METHOD_HISTORY, Phase 13).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from typing import Dict, List, Optional

from main import build_dataset, build_references
from src.aba_dataset import DatasetEntry
from src.aba_evaluation import (
    ProblemResult, SampleResult, aggregate_results, score_sample, sha256, summarise,
)
from src.aba_probes import (
    KINDS as PROBE_KINDS, ProbeResult, aggregate_probes, generate_probes,
    score_probe,
)
from src.aba_prompts import _parse_rule_line, problem_to_prompt
from src.aba_tracelog import _git_rev

MODES = ["direct", "cot", "guided", "algorithm"]
LEGACY = ("superseded end-to-end run (held-out example split, METHOD_HISTORY "
          "Phase 13); not rescorable")


def _read_rows(path: str) -> List[Dict]:
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def rescore_run(run_dir: str, out_dir: Optional[str] = None) -> Optional[Dict]:
    """Re-score an end-to-end run against the algorithm's run on each problem."""
    summary_path = os.path.join(run_dir, "summary.json")
    paths = {m: os.path.join(run_dir, f"results_{m}.jsonl") for m in MODES}
    paths = {m: p for m, p in paths.items() if os.path.exists(p)}
    if not paths:
        print(f"  no results_<mode>.jsonl in {run_dir}")
        return None
    run = None
    if os.path.exists(summary_path):
        with open(summary_path, encoding="utf-8") as fh:
            run = json.load(fh).get("run")
    rows_by_mode = {m: _read_rows(p) for m, p in paths.items()}
    if any("gen_valid" in r for rows in rows_by_mode.values() for r in rows):
        print(f"  {LEGACY}")
        return None
    if run is None:
        print("  no run block in summary.json: rerun main.py into the same --output "
              "to finish the run")
        return None

    d = run["dataset"]
    ds = build_dataset(benchmark_per_tier=d["benchmark_per_tier"],
                       n_synthetic=d["n_synthetic"], n_complex=d["n_complex"],
                       synthetic_seed=d["seed"], solve_symbolic=False,
                       anonymize=d["anonymize"], anonymize_scheme=d["anonymize_scheme"])
    refs, structures, problem_sha, _, ref_rows = build_references(ds)
    references_sha = sha256("".join(json.dumps(r) + "\n" for r in ref_rows))
    if references_sha != run.get("references_sha256"):
        print("  warning: the algorithm's answers differ from the run's references; "
              "scores are against the current ones")
    entries = {e.problem.problem_id: e for e in ds}

    results_by_mode: Dict[str, List[ProblemResult]] = {}
    drift = set()
    for mode, rows in rows_by_mode.items():
        by_pid: Dict[str, ProblemResult] = {}
        for row in rows:
            s = SampleResult.from_dict(row)
            pid = s.problem_id
            if pid not in refs:
                raise SystemExit(f"{pid}: no reference in the rebuilt dataset")
            if s.problem_sha256 != problem_sha[pid]:
                raise SystemExit(f"{pid}: the rebuilt problem differs from the run's")
            ref = refs[pid]
            role = ([_parse_rule_line(f) for f in ref.record.role_facts]
                    if mode == "guided" else None)
            if sha256(problem_to_prompt(entries[pid].problem, mode=mode,
                                        precomputed_role_facts=role)) != s.prompt_sha256:
                drift.add(f"{mode}:{pid}")
            if s.error != "llm_error":
                s.card, s.error = score_sample(ref, s.raw_output, s.finish == "length",
                                               run.get("audit", False))
            by_pid.setdefault(pid, ProblemResult(pid, mode, s.model_name,
                                                 structure=structures[pid])).samples.append(s)
        order = [e.problem.problem_id for e in ds]
        results_by_mode[mode] = [by_pid[p] for p in order if p in by_pid]
    if drift:
        print(f"  warning: {len(drift)} prompts differ from the ones the run sent "
              f"(e.g. {sorted(drift)[:3]}); scores are of the answers as given")

    run = {**run, "rescored": {"code_rev": _git_rev(), "prompt_drift": len(drift),
                               "references_sha256": references_sha}}
    out_dir = out_dir or run_dir
    os.makedirs(out_dir, exist_ok=True)
    for mode, results in results_by_mode.items():
        with open(os.path.join(out_dir, f"results_{mode}.jsonl"), "w", encoding="utf-8") as fh:
            for pr in results:
                for s in pr.samples:
                    fh.write(json.dumps(s.to_dict()) + "\n")
    summary = summarise(results_by_mode, run)
    with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    for mode, results in results_by_mode.items():
        agg = aggregate_results(results)
        print(f"  {mode:<10} clean@k={agg['clean_at_k']:.1%}  exact@k={agg['exact_at_k']:.1%}  "
              f"valid@1={agg['valid_at_1']:.1%}  parse={agg['parse_rate']:.1%}")
    print(f"  -> {os.path.join(out_dir, 'summary.json')}")
    return summary


def rescore_probes(run_dir: str, entries: Dict[str, DatasetEntry],
                   out_dir: Optional[str] = None,
                   max_per_kind: int = 2, seed: int = 42) -> Optional[Dict]:
    """Re-score a finished probe run from its stored answers.

    Probe generation is deterministic — ids are `<pid>::<kind>::<n>` plus
    `#<sample>`, and the sampling RNG is seeded per problem — so regenerating
    the probes reproduces the exact items the run was given, and each stored
    `raw_output` can be scored again offline.
    """
    path = os.path.join(run_dir, "probes.jsonl")
    if not os.path.exists(path):
        return None

    rows: List[dict] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    by_problem: Dict[str, List[dict]] = {}
    for row in rows:
        by_problem.setdefault(row["problem_id"], []).append(row)

    results: List[ProbeResult] = []
    skipped = 0
    for pid, prows in by_problem.items():
        entry = entries.get(pid)
        if entry is None:
            skipped += len(prows)
            continue
        probes = {p.probe_id: p for p in
                  generate_probes(entry.problem, max_per_kind=max_per_kind,
                                  seed=seed)}
        for row in prows:
            # Stored ids carry the sample suffix the probe ids do not.
            probe = probes.get(row["probe_id"].rsplit("#", 1)[0])
            if probe is None:
                skipped += 1
                continue
            correct, score, parsed = score_probe(
                probe, row.get("raw_output") or "", entry.problem)
            results.append(ProbeResult(
                probe_id=row["probe_id"], problem_id=pid, kind=probe.kind,
                model_name=row.get("model_name", "unknown"),
                raw_output=row.get("raw_output", ""),
                parsed=parsed, oracle_repr=row.get("oracle_repr", ""),
                correct=correct, score=score,
                oracle_bool=probe.oracle if isinstance(probe.oracle, bool)
                else None,
                error=row.get("error", ""),
                # Costs belong to the original generation, not to scoring.
                llm_latency_s=row.get("llm_latency_s", 0.0),
                prompt_tokens=row.get("prompt_tokens", 0),
                completion_tokens=row.get("completion_tokens", 0),
            ))

    if not results:
        print(f"  probes    no items matched the rebuilt dataset "
              f"({skipped} skipped) — check --benchmark/--seed")
        return None

    out_dir = out_dir or run_dir
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "probes.jsonl"), "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps(r.to_dict()) + "\n")

    # Carry the generating prompt version through: re-scoring does not change
    # which prompts produced the answers. A run with no recorded version is v1.
    old = os.path.join(run_dir, "probe_summary.json")
    version = "v1"
    if os.path.exists(old):
        with open(old, encoding="utf-8") as fh:
            version = json.load(fh).get("probe_prompt_version", "v1")

    summary = aggregate_probes(results, prompt_version=version)
    with open(os.path.join(out_dir, "probe_summary.json"),
              "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    print(f"  {'probe':<12}{'n':>5}{'acc':>8}{'score':>8}{'balanced':>10}"
          f"{'chance':>8}" + (f"   [{skipped} skipped]" if skipped else ""))
    for kind in PROBE_KINDS:
        e = summary.get(kind)
        if not e:
            continue
        ba = e.get("balanced_accuracy")
        print(f"  {kind:<12}{e['n']:>5}{e['accuracy']:>8.3f}{e['score']:>8.3f}"
              f"{(f'{ba:.3f}' if ba is not None else '-'):>10}"
              f"{e['chance']:>8.2f}")
    print(f"  -> {os.path.join(out_dir, 'probe_summary.json')}")
    return summary


def main() -> None:
    p = argparse.ArgumentParser(
        description="Recompute metrics for finished runs from their stored raw "
                    "LLM answers (no LLM calls, no GPU).")
    p.add_argument("run_dirs", nargs="+",
                   help="Run directories containing results_<mode>.jsonl or probes.jsonl")
    p.add_argument("--out", default=None,
                   help="Write rescored files here instead of in place. A "
                        "subdirectory per run is created.")
    p.add_argument("--probes", action="store_true",
                   help="Rescore probes.jsonl instead of the end-to-end modes "
                        "(step probes: role, fold, check, introduce, subsume).")
    g = p.add_argument_group("the probe run's dataset (end-to-end runs record theirs)")
    g.add_argument("--benchmark", type=int, default=20, metavar="N",
                   help="Problems per tier the run used (default 20).")
    g.add_argument("--n-synthetic", type=int, default=0)
    g.add_argument("--n-complex", type=int, default=0)
    g.add_argument("--seed", type=int, default=42)
    g.add_argument("--anonymize", action=argparse.BooleanOptionalAction, default=True)
    g.add_argument("--anonymize-scheme", choices=["letters", "indexed"],
                   default="letters")
    g.add_argument("--probes-per-kind", type=int, default=2, metavar="N",
                   help="Must match the value the probe run used (default 2), "
                        "otherwise the regenerated probes will not line up.")
    args = p.parse_args()

    # Shell globs are not expanded by cmd/PowerShell — do it here so the
    # documented `results/<set>/bench_*` form works everywhere.
    run_dirs: List[str] = []
    for pattern in args.run_dirs:
        matches = sorted(glob.glob(pattern))
        run_dirs.extend(matches or [pattern])

    entries: Optional[Dict[str, DatasetEntry]] = None
    if args.probes:
        ds = build_dataset(benchmark_per_tier=args.benchmark, n_synthetic=args.n_synthetic,
                           n_complex=args.n_complex, synthetic_seed=args.seed,
                           solve_symbolic=False, anonymize=args.anonymize,
                           anonymize_scheme=args.anonymize_scheme)
        entries = {e.problem.problem_id: e for e in ds}

    if args.out:
        names = [os.path.basename(d.rstrip("/\\")) for d in run_dirs]
        if len(set(names)) < len(names):
            raise SystemExit("two runs share a folder name and would overwrite each other "
                             "under --out; rescore them separately")

    for run_dir in run_dirs:
        if not os.path.isdir(run_dir):
            print(f"[skip] not a directory: {run_dir}")
            continue
        out = (os.path.join(args.out, os.path.basename(run_dir.rstrip("/\\")))
               if args.out else None)
        print(f"\n=== {run_dir} ===")
        if args.probes:
            if rescore_probes(run_dir, entries, out_dir=out,
                              max_per_kind=args.probes_per_kind,
                              seed=args.seed) is None:
                print("  no probes.jsonl here")
            continue
        rescore_run(run_dir, out_dir=out)


if __name__ == "__main__":
    main()
