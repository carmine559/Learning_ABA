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
from typing import Any, Dict, List, Optional

from src.aba_dataset import ABADataset, DatasetEntry
from src.aba_evaluation import (
    ProblemResult, SampleResult, score_llm_output, aggregate_results,
    tier_breakdown,
)
from src.aba_generalization import split_problem_examples
from src.aba_algorithm import solve_aba_learning
from src.aba_trace import score_trace
from src.aba_probes import (
    KINDS as PROBE_KINDS, ProbeResult, aggregate_probes, generate_probes,
    score_probe,
)


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


def trace_stats_for_mode(path: str, mode: str,
                         entries: Dict[str, DatasetEntry],
                         gold: Dict[str, Any]) -> Optional[Dict]:
    """Secondary, descriptive trace-fidelity statistics for one mode.

    Rule-keyed only. An earlier symbol-sequence measure was dropped because
    random sequences scored 0.28-0.49 on it — matching a canonical RULE has a
    chance rate of ~0 instead. Averaged over samples that produced a trace at
    all, with that rate reported, since `algorithm` mode at Qwen2.5-3B has a
    median output of 73 characters and nothing to score.
    """
    import statistics
    f1s, r2s, r3s, ht, n = [], [], [], 0, 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            entry = entries.get(row["problem_id"])
            tr = gold.get(row["problem_id"])
            if entry is None or tr is None:
                continue
            n += 1
            sc = score_trace(row.get("raw_output") or "", tr,
                             entry.problem.background, entry.problem.learnable)
            if sc.has_trace:
                ht += 1
                f1s.append(sc.f1)
                r2s.append(sc.r2_recall)
                r3s.append(sc.r3_recall)
    if not n:
        return None
    m = lambda v: round(statistics.mean(v), 3) if v else 0.0
    return {"n": n, "n_with_trace": ht, "has_trace_rate": round(ht / n, 3),
            "f1": m(f1s), "r2_recall": m(r2s), "r3_recall": m(r3s)}


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
    # which prompts produced the answers. Runs made before the field existed
    # are v1 by definition.
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


def rescore_run(run_dir: str, entries: Dict[str, DatasetEntry],
                out_dir: Optional[str] = None,
                gold_traces: Optional[Dict[str, Any]] = None) -> Dict:
    out_dir = out_dir or run_dir
    os.makedirs(out_dir, exist_ok=True)

    summary: Dict[str, dict] = {}
    results_by_mode: Dict[str, List[ProblemResult]] = {}
    trace_stats: Dict[str, Dict] = {}
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

        # `direct` is excluded deliberately: it asks for an answer, not a
        # derivation, so it has no trace to score and any hits are artefacts.
        if gold_traces and mode != "direct":
            st = trace_stats_for_mode(path, mode, entries, gold_traces)
            if st:
                trace_stats[mode] = st

    if summary and trace_stats:
        summary["trace_fidelity"] = trace_stats
        print("\n  Trace fidelity (rule-keyed; 'direct' excluded, it has no "
              "trace by construction)")
        print(f"  {'mode':<10}{'has_trace':>11}{'f1':>8}{'r2_rec':>8}"
              f"{'r3_rec':>8}")
        for mode, st in trace_stats.items():
            print(f"  {mode:<10}{st['has_trace_rate']:>10.1%}{st['f1']:>8.3f}"
                  f"{st['r2_recall']:>8.3f}{st['r3_recall']:>8.3f}")

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
    p.add_argument("--probes", action="store_true",
                   help="Rescore probes.jsonl instead of the end-to-end modes "
                        "(step probes: role, fold, check, introduce, subsume).")
    p.add_argument("--probes-per-kind", type=int, default=2, metavar="N",
                   help="Must match the value the probe run used (default 2), "
                        "otherwise the regenerated probes will not line up.")
    p.add_argument("--trace", action="store_true",
                   help="Also compute the secondary trace-fidelity statistics "
                        "(how much of the symbolic execution the model's own "
                        "reasoning reproduces). Solves every problem "
                        "symbolically first; adds a couple of seconds.")
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

    gold_traces: Optional[Dict[str, Any]] = None
    if args.trace:
        print("Solving each problem symbolically for the trace reference...")
        gold_traces = {}
        for pid, entry in entries.items():
            try:
                _, tr = solve_aba_learning(entry.problem)
                gold_traces[pid] = tr
            except Exception as exc:
                print(f"  [skip] {pid}: {type(exc).__name__}: {exc}")
        print(f"  {len(gold_traces)} reference traces.")

    for run_dir in run_dirs:
        if not os.path.isdir(run_dir):
            print(f"[skip] not a directory: {run_dir}")
            continue
        out = (os.path.join(args.out, os.path.basename(run_dir.rstrip("/\\")))
               if args.out else None)
        if args.probes:
            print(f"\n=== {run_dir} ===")
            if rescore_probes(run_dir, entries, out_dir=out,
                              max_per_kind=args.probes_per_kind,
                              seed=args.seed) is None:
                print("  no probes.jsonl here")
            continue
        rescore_run(run_dir, entries, out_dir=out, gold_traces=gold_traces)


if __name__ == "__main__":
    main()
