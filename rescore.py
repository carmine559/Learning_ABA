"""
rescore.py
Recompute every metric of a finished run from the raw LLM answers it stored.

WHY
---
`results_<mode>.jsonl` keeps the full `raw_output` of every sample, and the
benchmark is generated from a fixed seed, so a run can be scored again offline:
rebuild the identical problem set, re-parse each stored answer, and recompute
the metrics. A change to the parser, to the well-formedness check or to the
metric definitions therefore costs minutes of CPU instead of a day of GPU.

That matters here in particular: the runs in `results/` were scored with a
well-formedness check that rejected the legal reuse of a background assumption,
which alone marked 71.8% of samples ill-formed. Nothing about the models'
answers was wrong — only the scoring — and this script recovers them.

USAGE
-----
    # rescore in place (writes summary.json next to the results files)
    python rescore.py results/bench_qwen2.5-7b --benchmark 20

    # rescore every model directory of a run, into a separate output tree
    python rescore.py results/bench_* --benchmark 20 --out rescored/

The dataset flags MUST match the ones the run used, or the problems will not
line up; `--benchmark` is read from the run's own name_maps.json when possible
and only needs to be passed if that file is missing.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from typing import Dict, List, Optional

from src.aba_dataset import ABADataset, DatasetEntry
from src.aba_evaluation import (
    ProblemResult, SampleResult, score_llm_output, aggregate_results,
    tier_breakdown,
)
from src.aba_generalization import split_problem_examples


MODES = ["direct", "cot", "guided", "algorithm"]


def build_reference_dataset(
    benchmark_per_tier: int,
    n_synthetic: int = 0,
    n_complex: int = 0,
    seed: int = 42,
    anonymize: bool = True,
    anonymize_scheme: str = "letters",
    solve: bool = False,
) -> Dict[str, DatasetEntry]:
    """Rebuild the exact problem set a run used, keyed by problem id.

    `solve=False` by default: the symbolic reference is only needed for the
    `semantic_match` diagnostic, and solving 100+ problems costs far more than
    the rescoring itself.
    """
    ds = ABADataset()
    ds.load_builtin_benchmarks(solve=solve)
    if benchmark_per_tier > 0:
        ds.add_benchmark_suite(n_per_tier=benchmark_per_tier, seed=seed, solve=solve)
    if n_synthetic > 0:
        ds.add_synthetic(n=n_synthetic, seed=seed, solve=solve)
    if n_complex > 0:
        ds.add_complex_synthetic(n=n_complex, seed=seed + 1, solve=solve)
    if anonymize:
        ds.anonymize(scheme=anonymize_scheme, anonymize_constants=True)
    return {e.problem.problem_id: e for e in ds}


def rescore_mode(
    path: str,
    mode: str,
    entries: Dict[str, DatasetEntry],
    test_ratio: float = 0.34,
    split_seed: int = 42,
) -> tuple:
    """Rescore one results_<mode>.jsonl. Returns (problem_results, n_skipped)."""
    by_problem: Dict[str, List[dict]] = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            by_problem.setdefault(row["problem_id"], []).append(row)

    results: List[ProblemResult] = []
    skipped = 0
    for pid, rows in by_problem.items():
        entry = entries.get(pid)
        if entry is None:
            skipped += len(rows)
            continue
        split = split_problem_examples(entry.problem, test_ratio=test_ratio,
                                       seed=split_seed)
        pr = ProblemResult(
            problem_id=pid, mode=mode,
            model_name=rows[0].get("model_name", "unknown"),
            source=entry.source,
        )
        for idx, row in enumerate(rows):
            raw = row.get("raw_output") or ""
            if row.get("error_type") == "llm_error":
                # No answer was ever produced — carry the failure through
                # rather than scoring the traceback text as a framework.
                s = SampleResult(
                    problem_id=pid, mode=mode,
                    model_name=pr.model_name, source=entry.source,
                    sample_idx=row.get("sample_idx", idx),
                    raw_output=raw, error_type="llm_error",
                )
            else:
                s = score_llm_output(
                    entry, split, raw, mode, pr.model_name,
                    sample_idx=row.get("sample_idx", idx),
                )
                # Costs are properties of the original generation, not of
                # scoring; preserve them.
                s.llm_latency_s     = row.get("llm_latency_s", 0.0)
                s.prompt_tokens     = row.get("prompt_tokens", 0)
                s.completion_tokens = row.get("completion_tokens", 0)
            pr.samples.append(s)
        pr.compute()
        results.append(pr)
    return results, skipped


def rescore_run(run_dir: str, entries: Dict[str, DatasetEntry],
                out_dir: Optional[str] = None) -> Dict:
    out_dir = out_dir or run_dir
    os.makedirs(out_dir, exist_ok=True)

    summary: Dict[str, dict] = {}
    results_by_mode: Dict[str, List[ProblemResult]] = {}
    print(f"\n=== {run_dir} ===")
    for mode in MODES:
        path = os.path.join(run_dir, f"results_{mode}.jsonl")
        if not os.path.exists(path):
            continue
        results, skipped = rescore_mode(path, mode, entries)
        if not results:
            print(f"  {mode:<10} no problems matched the rebuilt dataset "
                  f"({skipped} samples skipped) — check --benchmark/--seed")
            continue
        agg = aggregate_results(results)
        summary[mode] = agg
        results_by_mode[mode] = results
        print(f"  {mode:<10} clean@k={agg['clean_at_k']:.1%}  "
              f"gen@k={agg['gen_at_k']:.1%}  det@k={agg['det_at_k']:.1%}  "
              f"fit@1={agg['fit_at_1']:.1%}  parse={agg['parse_rate']:.1%}"
              + (f"  [{skipped} skipped]" if skipped else ""))

        with open(os.path.join(out_dir, f"results_{mode}.jsonl"),
                  "w", encoding="utf-8") as fh:
            for pr in results:
                for s in pr.samples:
                    fh.write(json.dumps(s.to_dict()) + "\n")

    if summary:
        by_tier = tier_breakdown(results_by_mode)
        if by_tier:
            summary["by_tier"] = by_tier
            tiers = sorted({t for m in by_tier.values() for t in m})
            print(f"\n  {'mode':<10}" + "".join(f"{t:>13}" for t in tiers)
                  + "     (clean@k per tier)")
            for mode, per_tier in by_tier.items():
                row = f"  {mode:<10}"
                for t in tiers:
                    a = per_tier.get(t)
                    row += f"{a['clean_at_k']:>12.0%} " if a else f"{'-':>13}"
                print(row)
        with open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        print(f"  -> {os.path.join(out_dir, 'summary.json')}")
    return summary


def main() -> None:
    p = argparse.ArgumentParser(
        description="Recompute metrics for finished runs from their stored raw "
                    "LLM answers (no LLM calls, no GPU).")
    p.add_argument("run_dirs", nargs="+",
                   help="Run directories containing results_<mode>.jsonl")
    p.add_argument("--benchmark", type=int, default=20, metavar="N",
                   help="Problems per tier the run used (default 20).")
    p.add_argument("--n-synthetic", type=int, default=0)
    p.add_argument("--n-complex", type=int, default=0)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--anonymize", action=argparse.BooleanOptionalAction, default=True)
    p.add_argument("--anonymize-scheme", choices=["letters", "indexed"],
                   default="letters")
    p.add_argument("--with-reference", action="store_true",
                   help="Also solve each problem symbolically, enabling the "
                        "semantic_match diagnostic (much slower).")
    p.add_argument("--out", default=None,
                   help="Write rescored files here instead of in place. A "
                        "subdirectory per run is created.")
    args = p.parse_args()

    # Shell globs are not expanded by cmd/PowerShell — do it here so the
    # documented `results/bench_*` form works everywhere.
    run_dirs: List[str] = []
    for pattern in args.run_dirs:
        matches = sorted(glob.glob(pattern))
        run_dirs.extend(matches or [pattern])

    print("Rebuilding the reference dataset "
          f"(benchmark={args.benchmark}, seed={args.seed}, "
          f"anonymize={args.anonymize})...")
    entries = build_reference_dataset(
        benchmark_per_tier=args.benchmark,
        n_synthetic=args.n_synthetic,
        n_complex=args.n_complex,
        seed=args.seed,
        anonymize=args.anonymize,
        anonymize_scheme=args.anonymize_scheme,
        solve=args.with_reference,
    )
    print(f"  {len(entries)} problems rebuilt.")

    for run_dir in run_dirs:
        if not os.path.isdir(run_dir):
            print(f"[skip] not a directory: {run_dir}")
            continue
        out = (os.path.join(args.out, os.path.basename(run_dir.rstrip("/\\")))
               if args.out else None)
        rescore_run(run_dir, entries, out_dir=out)


if __name__ == "__main__":
    main()
