"""
main.py
Single-pipeline orchestration for the three ABA experiments:

  Task 1 (default)  : can an LLM replicate the ASP-ABAlearnB algorithm?
  Task 2 (--graded) : gradual ABA semantics (BSAF vs BAF baseline)
  Task 3            : ArgLLMs + RAG  (planned; see argllm/README.md)

Usage:
    python main.py --symbolic-only                              # ASP-ABAlearnB reference only
    python main.py --backend google_ai --modes algorithm guided # Task 1 (anonymised by default)
    python main.py --backend groq --model llama3-70b --n-samples 5
    python main.py --no-anonymize --modes algorithm             # keep real predicate names
    python main.py --graded                                     # Task 1 + Task 2 graded analysis
    python main.py --graded --graded-source llm_elicited        # elicit base scores from the LLM
    python main.py --graded --export                            # also export frameworks + figures
"""
from __future__ import annotations
import argparse
import json
import os
from typing import List, Dict, Optional, Any

# ── project imports ──────────────────────────────────────────────────────────
from src.aba_types      import ABAFramework
from src.aba_dataset    import ABADataset
from src.aba_algorithm  import solve_aba_learning
from src.aba_model      import get_backend, LLMBackend
from src.aba_evaluation import (
    ProblemResult, evaluate_dataset, aggregate_results, complexity_analysis,
    tier_breakdown,
)
from src.aba_probes import (
    run_probes, aggregate_probes, KINDS as PROBE_KINDS,
)
from extras.aba_visualization import save_all_plots


# ─────────────────────────────────────────────────────────────────────────────
# Dataset builder
# ─────────────────────────────────────────────────────────────────────────────

def _save_name_maps(ds: ABADataset, output_dir: str) -> None:
    """Persist the anonymisation maps so anonymised results can be read back."""
    os.makedirs(output_dir, exist_ok=True)
    maps = {}
    for entry in ds:
        nm = entry.name_map
        if nm is not None:
            maps[entry.problem.problem_id] = nm.to_dict()
    path = os.path.join(output_dir, "name_maps.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(maps, f, indent=2)
    print(f"  Anonymisation maps saved to {path}")


def build_dataset(
    n_synthetic: int = 0,
    n_complex: int = 0,
    benchmark_per_tier: int = 0,
    synthetic_seed: int = 42,
    solve_symbolic: bool = True,
    anonymize: bool = True,
    anonymize_scheme: str = "letters",
    output_dir: Optional[str] = None,
) -> ABADataset:
    ds = ABADataset()

    # Built-in benchmarks (always included)
    ds.load_builtin_benchmarks(solve=solve_symbolic)
    print(f"  Loaded {len(ds)} built-in benchmark problems.")

    # Stratified benchmark suite (massive testing: one tier per capability)
    if benchmark_per_tier > 0:
        ds.add_benchmark_suite(n_per_tier=benchmark_per_tier,
                               seed=synthetic_seed, solve=solve_symbolic)
        print(f"  After benchmark suite: {len(ds)} problems.")

    # Synthetic (single-path)
    if n_synthetic > 0:
        ds.add_synthetic(n=n_synthetic, seed=synthetic_seed, solve=solve_symbolic)
        print(f"  After synthetic generation: {len(ds)} problems.")

    # Complex synthetic (two-path — richer QBAF, non-binary sigma values)
    if n_complex > 0:
        ds.add_complex_synthetic(n=n_complex, seed=synthetic_seed + 1,
                                 solve=solve_symbolic)
        print(f"  After complex synthetic generation: {len(ds)} problems.")

    # Anonymisation — strip semantic predicate/constant names so the LLM cannot
    # lean on world knowledge.  Bijective => symbolic results are preserved.
    if anonymize:
        ds.anonymize(scheme=anonymize_scheme, anonymize_constants=True)
        if solve_symbolic:
            for entry in ds:
                entry.solution = ds._solve_with_role(entry.problem)
        print(f"  Anonymised all problems (scheme={anonymize_scheme}).")
        if output_dir:
            _save_name_maps(ds, output_dir)

    stats = ds.stats()
    print(f"  Solved: {stats['solved']}/{stats['total']}  "
          f"avg_bg_rules={stats['avg_background_rules']}")
    return ds


# ─────────────────────────────────────────────────────────────────────────────
# Symbolic baseline  (ASP-ABAlearnB)
# ─────────────────────────────────────────────────────────────────────────────

def run_symbolic_baseline(ds: ABADataset, verbose: bool = False,
                          output_dir: Optional[str] = None) -> Dict:
    """Run ASP-ABAlearnB twice per problem, for two different purposes.

      * on the FULL problem — the reference solution used for export and for
        the semantic comparison; this is the algorithm doing its published job;
      * on the TRAIN split only, then scored on the held-out examples exactly
        like an LLM sample. Only this second number is comparable with the LLM
        rows: every LLM sees the training split alone, so a 100% built from the
        full problem is a different task, not a ceiling.
    """
    from src.aba_generalization import split_problem_examples, evaluate_generalization

    print("\n=== Symbolic baseline (ASP-ABAlearnB) ===")
    results = {
        "total": 0, "solved": 0, "intensional": 0,
        "train_solved": 0, "train_gen": 0, "train_determined": 0,
        "problems": [],
    }
    traces: List[Dict] = []

    for entry in ds:
        problem = entry.problem
        results["total"] += 1
        solution, trace = solve_aba_learning(problem, verbose=verbose)
        ok = solution is not None and trace.success
        inten = ok and solution.is_intensional()
        results["solved"]      += int(ok)
        results["intensional"] += int(inten)

        # Promote the Gen-phase intensional solution into the dataset entry so
        # that run_graded_analysis uses intensional rules (giving non-binary σ)
        # rather than the raw RoLe ground facts stored by _solve_with_role.
        if ok and solution is not None:
            entry.solution = solution

        # The execution trace, not just its length. `DatasetEntry.trace` has
        # existed all along but was never assigned, so the only thing about the
        # symbolic run that reached disk was `n_steps`. The trace is what makes
        # the step probes possible: it names the states the algorithm visits.
        entry.trace = trace
        traces.append(trace.to_dict())

        # ── the comparable, train-only run ───────────────────────────────────
        split = split_problem_examples(problem)
        tr_sol, tr_trace = solve_aba_learning(split.train)
        tr_ok = tr_sol is not None and tr_trace.success
        tr_gen = tr_det = False
        if tr_ok:
            g = evaluate_generalization(tr_sol, split, domain=problem.get_domain())
            tr_gen, tr_det = g.gen_valid, g.gen_determined
        results["train_solved"]     += int(tr_ok)
        results["train_gen"]        += int(tr_gen)
        results["train_determined"] += int(tr_det)

        results["problems"].append({
            "problem_id": problem.problem_id,
            "solved": ok,
            "intensional": inten,
            "n_steps": len(trace.steps),
            "n_new_rules": len(solution.new_rules) if solution else 0,
            "train_solved": tr_ok,
            "train_gen_valid": tr_gen,
            "train_gen_determined": tr_det,
        })

        status = "OK intensional" if inten else ("OK ground" if ok else "FAIL")
        print(f"  {problem.problem_id}: {status}"
              f"   [train-only: {'gen' if tr_gen else 'no-gen'}"
              f"/{'determined' if tr_det else 'undetermined'}]")

    n = results["total"]
    print(f"\nSymbolic (full problem): {results['solved']}/{n} solved, "
          f"{results['intensional']}/{n} intensional")
    print(f"Symbolic (train only, comparable with the LLM rows): "
          f"{results['train_gen']}/{n} generalise, "
          f"{results['train_determined']}/{n} determined")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, "symbolic_traces.jsonl")
        with open(path, "w", encoding="utf-8") as fh:
            for t in traces:
                fh.write(json.dumps(t) + "\n")
        print(f"Symbolic traces saved to {path}")
    return results


# ─────────────────────────────────────────────────────────────────────────────
# LLM prompt evaluation
# ─────────────────────────────────────────────────────────────────────────────

def run_prompt_experiments(
    ds: ABADataset,
    backend: LLMBackend,
    modes: List[str],
    n_samples: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    output_dir: str = "./results",
) -> Dict[str, List[ProblemResult]]:
    os.makedirs(output_dir, exist_ok=True)
    results_by_mode: Dict[str, List[ProblemResult]] = {}

    for mode in modes:
        print(f"\n=== Mode: {mode} ===")
        try:
            results = evaluate_dataset(
                ds, backend, mode,
                n_samples=n_samples,
                temperature=temperature,
                max_tokens=max_tokens,
                verbose=True,
            )
        except Exception as exc:
            print(f"  [!] Mode '{mode}' crashed: {type(exc).__name__}: {exc}")
            print(f"  Skipping '{mode}' and continuing with the remaining modes.")
            continue

        results_by_mode[mode] = results
        agg = aggregate_results(results)
        print(f"  -> clean@k={agg['clean_at_k']:.1%}  gen@k={agg['gen_at_k']:.1%}  "
              f"det@k={agg['det_at_k']:.1%}  fit@1={agg['fit_at_1']:.1%}")

        # Save raw per-sample results per mode immediately, so a later crash
        # never loses work already completed.
        path = os.path.join(output_dir, f"results_{mode}.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            for pr in results:
                for s in pr.samples:
                    f.write(json.dumps(s.to_dict()) + "\n")

    return results_by_mode


# ─────────────────────────────────────────────────────────────────────────────
# Step probes  (src/aba_probes.py)
# ─────────────────────────────────────────────────────────────────────────────

def run_probe_experiment(
    ds: ABADataset,
    backend: LLMBackend,
    max_per_kind: int = 2,
    n_samples: int = 1,
    max_tokens: int = 512,
    output_dir: str = "./results",
    verbose: bool = True,
) -> Dict:
    """Ask the model one ASP-ABAlearnB decision at a time.

    Complements the end-to-end modes rather than replacing them: those measure
    whether a Definition-1 solution comes out, these measure whether each step
    of the algorithm can be performed. The gap between the two is the point.
    """
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n=== Step probes (max {max_per_kind}/kind/problem, "
          f"k={n_samples}, greedy) ===")
    results = run_probes(ds, backend, max_per_kind=max_per_kind,
                         n_samples=n_samples, temperature=0.0,
                         max_tokens=max_tokens, verbose=verbose)

    path = os.path.join(output_dir, "probes.jsonl")
    with open(path, "w", encoding="utf-8") as f:
        for r in results:
            f.write(json.dumps(r.to_dict()) + "\n")

    summary = aggregate_probes(results)
    with open(os.path.join(output_dir, "probe_summary.json"),
              "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\n  {'probe':<12}{'n':>5}{'acc':>8}{'score':>8}"
          f"{'balanced':>10}{'chance':>8}")
    for kind in PROBE_KINDS:
        e = summary.get(kind)
        if not e:
            continue
        ba = e.get("balanced_accuracy")
        print(f"  {kind:<12}{e['n']:>5}{e['accuracy']:>8.3f}{e['score']:>8.3f}"
              f"{(f'{ba:.3f}' if ba is not None else '-'):>10}"
              f"{e['chance']:>8.2f}")
    print("\n  Binary probes (check, subsume) must be read against the 0.50 "
          "floor:\n  balanced accuracy puts a constant YES/NO answer at exactly "
          "0.50.")
    print(f"  -> {path}")
    return summary


# ─────────────────────────────────────────────────────────────────────────────
# Graded semantics analysis  (gradual/aba_graded.py)
# ─────────────────────────────────────────────────────────────────────────────

def run_graded_analysis(
    ds: ABADataset,
    backend,                                      # LLMBackend | None
    source: str = "uniform",
    results_by_mode: Optional[Dict[str, List[ProblemResult]]] = None,
    output_dir: str = "./results",
    kernel: str = "dfquad_prod",
    claim_mode: str = "max",
) -> Dict:
    """
    Compute graded entailment for every solved problem under TWO semantics and
    compare both with Clingo's crisp brave-entailment verdict:

      * BSAF (headline)  — the correct assumption-based gradual ABA semantics of
        Rapberger et al. (KR 2025): iterative strength-evolution fixpoint over
        the BSAF abstraction.  This is what `graded_strength` reports.
      * BAF baseline     — the argument-tree DF-QuAD of aba_graded.py, i.e. the
        paper's argument/QBAF baseline (Section 5), reported alongside for the
        same BSAF-vs-BAF comparison the paper performs.

    source (assumption base scores):
      "uniform"      — all = 0.5  (no extra calls)
      "sample_freq"  — frequency across k LLM samples    (needs results_by_mode)
      "llm_elicited" — one dedicated LLM call per assumption (needs backend)

    kernel: BSAF modular kernel (dfquad_prod | dfquad_min | qe_prod | qe_min).
    claim_mode: how claim strength is read from assumption strengths
                (max=brave, min, avg, noisy_or=accrual).
    """
    from gradual.aba_bsaf import compare_crisp_vs_graded_bsaf
    from gradual.aba_graded import (
        compare_crisp_vs_graded,            # the BAF baseline (argument tree)
        assumption_scores_from_samples,
        assumption_scores_from_llm,
    )
    from src.aba_prompts import parse_llm_output

    print(f"\n=== Graded semantics analysis (source={source}, "
          f"BSAF kernel={kernel}, claim={claim_mode}) ===")
    print("    columns: crisp | sigma_BSAF (headline) | sigma_BAF (baseline)")

    # Build a flat lookup: problem_id -> List[ProblemResult] across all modes
    prs_by_pid: Dict[str, List[ProblemResult]] = {}
    if results_by_mode:
        for mode_prs in results_by_mode.values():
            for pr in mode_prs:
                prs_by_pid.setdefault(pr.problem_id, []).append(pr)

    rows = []
    n_agree_bsaf = n_agree_baf = n_queries_total = 0

    for entry in ds:
        problem = entry.problem
        pid = problem.problem_id
        framework = entry.solution
        if framework is None:
            print(f"  {pid}: skipped (no symbolic solution)")
            continue

        domain = problem.get_domain()
        queries = problem.positive + problem.negative

        # ── Base scores ───────────────────────────────────────────────────────
        if source == "sample_freq" and pid in prs_by_pid:
            # Re-parse the raw LLM outputs to collect assumption occurrence counts
            sample_fws = []
            for pr in prs_by_pid[pid]:
                for s in pr.samples:
                    if s.parse_success and s.raw_output:
                        fw = parse_llm_output(s.raw_output, problem.background)
                        if fw is not None:
                            sample_fws.append(fw)
            scores = assumption_scores_from_samples(sample_fws) if sample_fws else {}
        elif source == "llm_elicited" and backend is not None:
            scores = assumption_scores_from_llm(framework, backend,
                                                context=pid, domain=domain)
        else:
            scores = {}  # uniform: default_score=0.5

        # ── Both semantics ────────────────────────────────────────────────────
        bsaf = compare_crisp_vs_graded_bsaf(
            framework, domain, queries, assumption_scores=scores,
            kernel=kernel, claim_mode=claim_mode,
        )
        baf = compare_crisp_vs_graded(
            framework, domain, queries, assumption_scores=scores,
        )
        baf_by_q = {r.query: r for r in baf}

        n_agree_b = sum(r.agree for r in bsaf)
        agree_bsaf = n_agree_b / len(bsaf) if bsaf else 1.0
        n_agree_bsaf  += n_agree_b
        n_agree_baf   += sum(r.agree for r in baf)
        n_queries_total += len(bsaf)

        all_conv = all(r.converged for r in bsaf)
        scores_str = (", ".join(f"{k}={v:.2f}" for k, v in scores.items())
                      if scores else "uniform 0.50")
        conv_str = "" if all_conv else "  [BSAF did NOT converge]"
        print(f"  {pid}: BSAF agreement={agree_bsaf:.0%}  "
              f"[{scores_str}]{conv_str}")
        for r in bsaf:
            b = baf_by_q.get(r.query)
            sb = b.graded_strength if b else float("nan")
            marker = "+" if r.agree else "-"
            print(f"    {marker} {r.query:<22}  crisp={str(r.crisp_entailed):<5}  "
                  f"BSAF={r.graded_strength:.3f}  BAF={sb:.3f}")

        rows.append({
            "problem_id":       pid,
            "strength_source":  source,
            "kernel":           kernel,
            "claim_mode":       claim_mode,
            "n_assumptions":    len(framework.assumptions),
            "assumption_scores": scores,
            "agreement_rate":   round(agree_bsaf, 3),          # BSAF (headline)
            "bsaf_converged":   all_conv,
            "queries": [
                {
                    "query":            r.query,
                    "crisp_entailed":   r.crisp_entailed,
                    "graded_strength":  r.graded_strength,     # BSAF (headline)
                    "agree":            r.agree,               # BSAF (headline)
                    "baseline_strength": (baf_by_q[r.query].graded_strength
                                          if r.query in baf_by_q else None),
                    "baseline_agree":   (baf_by_q[r.query].agree
                                          if r.query in baf_by_q else None),
                    "converged":        r.converged,
                }
                for r in bsaf
            ],
        })

    overall_bsaf = n_agree_bsaf / n_queries_total if n_queries_total else 1.0
    overall_baf  = n_agree_baf  / n_queries_total if n_queries_total else 1.0
    print(f"\nOverall crisp agreement - "
          f"BSAF (headline): {n_agree_bsaf}/{n_queries_total} ({overall_bsaf:.0%})  |  "
          f"BAF baseline: {n_agree_baf}/{n_queries_total} ({overall_baf:.0%})")

    result = {
        "source":             source,
        "kernel":             kernel,
        "claim_mode":         claim_mode,
        "n_problems":         len(rows),
        "overall_agreement":  round(overall_bsaf, 3),          # BSAF (headline)
        "overall_agreement_baseline": round(overall_baf, 3),
        "problems":           rows,
    }
    path = os.path.join(output_dir, "graded_results.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"Graded results saved to {path}")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Reporting
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(
    results_by_mode: Dict[str, List[ProblemResult]],
    symbolic_results: Optional[Dict],
    ds: ABADataset,
    output_dir: str,
) -> None:
    os.makedirs(os.path.join(output_dir, "figures"), exist_ok=True)

    summary = {
        mode: aggregate_results(results)
        for mode, results in results_by_mode.items()
    }
    if symbolic_results:
        n = max(symbolic_results["total"], 1)
        # NOT comparable with the LLM rows — the algorithm sees every example.
        # Kept because it is the reference the export and semantic comparison
        # are built from.
        summary["symbolic_full_problem"] = {
            "n_problems":          symbolic_results["total"],
            "parse_rate":          1.0,
            "fit_at_1":            symbolic_results["solved"] / n,
            "gen_at_1":            symbolic_results["solved"] / n,
            "det_at_1":            symbolic_results["solved"] / n,
            "fit_at_k":            symbolic_results["solved"] / n,
            "gen_at_k":            symbolic_results["solved"] / n,
            "det_at_k":            symbolic_results["solved"] / n,
            "clean_at_1":          symbolic_results["solved"] / n,
            "clean_at_k":          symbolic_results["solved"] / n,
            "intensional_rate":    symbolic_results["intensional"] / n,
            "degenerate_rate":     0.0,
            "mean_overfit_gap":    0.0,
            "note":                "sees ALL examples; not an LLM-comparable ceiling",
        }
        # THE comparable row: same train/test split, same scoring.
        summary["symbolic_train_only"] = {
            "n_problems":          symbolic_results["total"],
            "parse_rate":          1.0,
            "fit_at_1":            symbolic_results["train_solved"] / n,
            "gen_at_1":            symbolic_results["train_gen"] / n,
            "det_at_1":            symbolic_results["train_determined"] / n,
            "fit_at_k":            symbolic_results["train_solved"] / n,
            "gen_at_k":            symbolic_results["train_gen"] / n,
            "det_at_k":            symbolic_results["train_determined"] / n,
            "clean_at_1":          symbolic_results["train_gen"] / n,
            "clean_at_k":          symbolic_results["train_gen"] / n,
            "intensional_rate":    symbolic_results["intensional"] / n,
            "degenerate_rate":     0.0,
            "mean_overfit_gap":    0.0,
            "note":                "same split and scoring as the LLM rows",
        }

    # Per-tier breakdown (benchmark suite): WHICH capability does the LLM
    # replicate? Problem ids carry the tier prefix, e.g. t2_defeas_0003[_anon].
    by_tier = tier_breakdown(results_by_mode)
    if by_tier:
        summary["by_tier"] = by_tier

    # Save summary JSON
    summary_path = os.path.join(output_dir, "summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved to {summary_path}")

    # Print formatted table. clean@k is the STRICT criterion (error_type ==
    # "none": fits ALL train examples AND generalises) — the honest measure of
    # "replicates the algorithm"; gen@k alone can be high while fit is 0.
    print("\n=== Results table ===")
    metrics = ["clean_at_k", "gen_at_k", "det_at_k", "fit_at_1",
               "intensional_rate", "parse_rate"]
    header = f"{'Config':<24}" + "".join(f"{m:>18}" for m in metrics)
    print(header)
    print("-" * len(header))
    for name, agg in summary.items():
        if name == "by_tier":
            continue
        row = f"{name:<24}"
        for m in metrics:
            v = agg.get(m)
            # A quality rate is None when no sample ever fitted: "undefined",
            # which must not be printed as a measured 0%.
            cell = "n/a" if v is None else (
                f"{v:.1%}" if ("rate" in m or "_at_" in m) else f"{v:.2f}")
            row += f"{cell:>18}"
        print(row)
    print("\n  clean@k = legal+stable+fits+generalises+non-degenerate (brave)")
    print("  gen@k   = solves the full problem in SOME stable extension")
    print("  det@k   = held-out labels are forced in EVERY train-consistent "
          "extension\n            (gen@k minus det@k is how much of gen@k is "
          "free choice, not learning)")

    if by_tier:
        print("\n=== Per-tier breakdown: gen@k / clean@k "
              "(clean = fits train AND generalises) ===")
        tiers = sorted({t for mode_t in by_tier.values() for t in mode_t})
        header = f"{'Mode':<12}" + "".join(f"{t:>14}" for t in tiers)
        print(header)
        print("-" * len(header))
        for mode, tier_aggs in by_tier.items():
            row = f"{mode:<12}"
            for t in tiers:
                agg = tier_aggs.get(t)
                if agg:
                    cell = f"{agg['gen_at_k']:.0%}/{agg.get('clean_at_k', 0):.0%}"
                    row += f"{cell:>14}"
                else:
                    row += f"{'-':>14}"
            print(row)

    # Generate figures
    try:
        complexity_rows = []
        for mode, results in results_by_mode.items():
            complexity_rows.extend(complexity_analysis(ds, results))

        save_all_plots(
            results_by_mode=results_by_mode,
            complexity_rows=complexity_rows,
            summary=summary,
            output_dir=os.path.join(output_dir, "figures"),
            fmt="pdf",
        )
    except Exception as e:
        print(f"Warning: figure generation failed: {e}")

    # ── Generate per-problem explanations ───────────────────────────────────
    try:
        _write_explanations(ds, results_by_mode, output_dir)
    except Exception as e:
        print(f"Warning: explanation generation failed: {e}")


def _write_explanations(ds, results_by_mode, output_dir):
    """
    For each problem, reconstruct a grounded explanation of how the model
    generalised, using the best (generalising, else best-fit) sample.
    Writes a human-readable explanations.md and aggregate mechanism stats.
    """
    from extras.aba_explain import explain_sample, mechanism_statistics
    entry_by_id = {e.problem.problem_id: e for e in ds}

    md_lines = ["# Per-problem explanations\n"]
    all_expls = []

    for mode, results in results_by_mode.items():
        md_lines.append(f"\n## Mode: {mode}\n")
        for pr in results:
            entry = entry_by_id.get(pr.problem_id)
            if entry is None or entry.solution is None:
                continue
            # Pick the most informative sample: a generalising one if any,
            # otherwise the first parseable one.
            chosen = next((s for s in pr.samples if s.gen_valid), None)
            if chosen is None:
                chosen = next((s for s in pr.samples if s.parse_success), None)
            if chosen is None:
                continue
            expl = explain_sample(entry, chosen.raw_output, mode=mode)
            if expl is None:
                continue
            all_expls.append(expl)
            md_lines.append(f"### {pr.problem_id}  (gen@1={pr.gen_at_1:.0%}, "
                            f"gen@k={'yes' if pr.gen_at_k else 'no'})")
            md_lines.append(expl.narrative + "\n")

    # Aggregate mechanism -> generalisation correlation
    mech_stats = mechanism_statistics(all_expls)
    if mech_stats:
        md_lines.append("\n## Mechanism vs. generalisation (success rate)\n")
        md_lines.append("How often each rule mechanism co-occurred with full "
                        "generalisation:\n")
        for mech, rate in sorted(mech_stats.items(), key=lambda x: -x[1]):
            md_lines.append(f"- **{mech.replace('_', ' ')}**: {rate:.0%}")

    path = os.path.join(output_dir, "explanations.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Explanations saved to {path}")


# ─────────────────────────────────────────────────────────────────────────────
# Framework export  (extras/aba_export.py + extras/aba_explain.py)
# ─────────────────────────────────────────────────────────────────────────────

def run_export(
    ds: ABADataset,
    results_by_mode: Optional[Dict[str, List[ProblemResult]]] = None,
    graded_data: Optional[Dict] = None,
    source_name: str = "llm",
    output_dir: str = "./results",
    basename: str = "frameworks",
) -> Dict[str, str]:
    """
    Export all learned ABA frameworks — symbolic ground truth and every LLM
    sample — to JSONL, Markdown, and CSV, enriched with:

      * natural-language translation of each rule (Rule.to_text)
      * mechanism tag per rule  (ground_fact | assumption_guarded | …)
      * per-sample narrative from aba_explain.build_narrative
      * graded entailment table from aba_graded  (if --graded was also run)

    Writes: frameworks.jsonl, frameworks.md, defeasibility.csv
    """
    from extras.aba_export import FrameworkRecord, export_frameworks, enrich_record
    from extras.aba_explain import explain_sample
    from src.aba_prompts import parse_llm_output

    entry_by_id = {e.problem.problem_id: e for e in ds}

    # Build a graded lookup: problem_id -> {query -> graded dict}
    graded_by_pid: Dict[str, Dict[str, Any]] = {}
    if graded_data:
        for row in graded_data.get("problems", []):
            pid = row["problem_id"]
            graded_by_pid[pid] = {
                q["query"]: {
                    "crisp":     q["crisp_entailed"],
                    "strength":  q["graded_strength"],
                    "agree":     q["agree"],
                    "explanation": q.get("explanation", ""),
                }
                for q in row.get("queries", [])
            }

    records: List[FrameworkRecord] = []

    # ── Symbolic reference solutions ─────────────────────────────────────────
    for entry in ds:
        if entry.solution is None:
            continue
        pid = entry.problem.problem_id
        rec = FrameworkRecord.from_framework(
            entry.solution,
            problem_id=pid,
            source="symbolic",
            mode="",
            sample_idx=-1,
            valid=True,
            generalises=True,
        )
        enrich_record(rec, entry.problem.background,
                      graded_scores=graded_by_pid.get(pid))
        records.append(rec)

    # ── LLM samples ──────────────────────────────────────────────────────────
    if results_by_mode:
        for mode, prs in results_by_mode.items():
            for pr in prs:
                pid = pr.problem_id
                entry = entry_by_id.get(pid)
                bg = entry.problem.background if entry else None
                for idx, s in enumerate(pr.samples):
                    if not s.parse_success or not s.raw_output:
                        continue
                    fw = parse_llm_output(s.raw_output, bg) if bg else None
                    if fw is None:
                        continue
                    rec = FrameworkRecord.from_framework(
                        fw,
                        problem_id=pid,
                        source=source_name,
                        mode=mode,
                        sample_idx=idx,
                        valid=getattr(s, "fit_valid",  s.parse_success),
                        generalises=getattr(s, "gen_valid", None),
                    )
                    # Mechanism tags need the background framework
                    narrative_text: Optional[str] = None
                    if entry is not None and bg is not None:
                        enrich_record(rec, bg)
                        expl = explain_sample(entry, s.raw_output, mode=mode)
                        if expl is not None:
                            narrative_text = expl.narrative
                    enrich_record(rec, bg or ABAFramework(),
                                  narrative=narrative_text,
                                  graded_scores=graded_by_pid.get(pid))
                    records.append(rec)

    print(f"\n=== Exporting {len(records)} framework record(s) ===")
    paths = export_frameworks(records, output_dir, basename=basename)
    for fmt, path in paths.items():
        print(f"  {fmt}: {path}")
    return paths


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "ABA framework learning - three experiments:\n"
            "  Task 1 (default) : can an LLM replicate the ASP-ABAlearnB algorithm?\n"
            "  Task 2 (--graded): gradual ABA semantics (BSAF vs BAF baseline)\n"
            "  Task 3           : ArgLLMs + RAG  (planned; see argllm/README.md)"
        )
    )

    # ── LLM backend ──────────────────────────────────────────────────────────
    g_llm = p.add_argument_group("LLM backend")
    g_llm.add_argument("--backend", default="mock",
                       choices=["mock", "groq", "hf_api", "google_ai", "local"],
                       help=(
                           "LLM backend to use.\n"
                           "  groq      : free API, Llama 3.3 70B (set GROQ_API_KEY)\n"
                           "  hf_api    : HuggingFace serverless, free (set HF_TOKEN)\n"
                           "  google_ai : Google AI Studio, Gemini (set GOOGLE_API_KEY)\n"
                           "  local     : run a HF model ON THE GPU/CUDA (cluster)\n"
                           "  mock      : hard-coded responses, for testing\n"
                       ))
    g_llm.add_argument("--model", default=None,
                       help=(
                           "Model name or alias. Defaults per backend:\n"
                           "  groq      -> llama-3.3-70b-versatile\n"
                           "  hf_api    -> Qwen/Qwen2.5-7B-Instruct\n"
                           "  google_ai -> gemini-2.5-flash\n"
                           "  local     -> Qwen/Qwen2.5-7B-Instruct (alias: qwen2.5-7b,\n"
                           "               qwen2.5-14b, qwen2.5-32b, llama3-8b, mistral-7b)\n"
                       ))
    g_llm.add_argument("--thinking", action="store_true",
                       help="Enable Gemini thinking mode (google_ai, gemini-2.5-*): "
                            "a hidden chain-of-thought that helps multi-step ABA "
                            "reasoning, at higher latency/token cost.")
    g_llm.add_argument("--load-4bit", action="store_true",
                       help="local backend only: load the model in 4-bit (nf4). "
                            "Needed to fit big models (32B) on an L40, or any 7B on "
                            "an 11 GB RTX 2080 Ti.")
    g_llm.add_argument("--min-interval", type=float, default=0.0,
                       help="Minimum seconds between API requests (rate-limit "
                            "throttle). Try 2-4 on free tiers.")
    g_llm.add_argument("--temperature", type=float, default=0.7)
    g_llm.add_argument("--max-tokens", type=int, default=1024)

    # ── Dataset ──────────────────────────────────────────────────────────────
    g_data = p.add_argument_group("Dataset")
    g_data.add_argument("--benchmark", type=int, default=0, metavar="N",
                        help="Massive testing: add the stratified benchmark suite "
                             "with N problems per tier (t1_mono, t2_defeas, "
                             "t3_noise, t4_domain, t5_twopath). The per-tier "
                             "breakdown in the report shows WHICH part of the "
                             "algorithm the LLM replicates.")
    g_data.add_argument("--n-synthetic", type=int, default=0,
                        help="Number of single-path synthetic problems to add.")
    g_data.add_argument("--n-complex", type=int, default=0,
                        help="Number of two-path complex synthetic problems to add "
                             "(richer QBAFs -> intermediate sigma under Task 2).")
    g_data.add_argument("--anonymize", action=argparse.BooleanOptionalAction,
                        default=True,
                        help=(
                            "Rename every predicate/constant to an abstract symbol "
                            "(p, q, ... / a, b, ...) before the LLM sees the problem. "
                            "ON BY DEFAULT for Task 1; use --no-anonymize to keep real "
                            "names (e.g. for Task 3 / RAG, or human inspection). "
                            "Controls hallucination and knowledge leakage; the rewrite "
                            "is a bijection so symbolic results are unchanged. Name "
                            "maps are saved to name_maps.json."
                        ))
    g_data.add_argument("--anonymize-scheme", choices=["letters", "indexed"],
                        default="letters",
                        help=(
                            "Abstract naming scheme:\n"
                            "  letters : p,q,r,... / a,b,c,...  (readable)\n"
                            "  indexed : p0,p1,... / c0,c1,...   (scales)\n"
                        ))

    # ── Task 1: LLM learning ─────────────────────────────────────────────────
    g_t1 = p.add_argument_group("Task 1 - LLM learning")
    g_t1.add_argument("--modes", nargs="+",
                      default=["direct", "cot", "guided", "algorithm"],
                      choices=["direct", "cot", "guided", "algorithm"],
                      help=(
                          "Prompt modes to run (increasing guidance):\n"
                          "  direct    : problem only\n"
                          "  cot       : step-by-step reasoning instructions\n"
                          "  guided    : problem + precomputed RoLe ground facts\n"
                          "  algorithm : the full ASP-ABAlearnB algorithm to EXECUTE\n"
                      ))
    g_t1.add_argument("--n-samples", type=int, default=5,
                      help="LLM samples per problem (for pass@k).")
    g_t1.add_argument("--symbolic-only", action="store_true",
                      help="Run only the symbolic ASP-ABAlearnB reference, no LLM.")

    # ── Task 1b: step probes ─────────────────────────────────────────────────
    g_pr = p.add_argument_group("Task 1b - step probes")
    g_pr.add_argument("--probes", action="store_true",
                      help=("Run STEP PROBES instead of the end-to-end modes: "
                            "one decision of ASP-ABAlearnB per prompt, each with "
                            "a Clingo or syntactic oracle (R1 RoLe, R2 Folding, "
                            "the solution check, R3 Assumption Introduction, "
                            "R4 Fact Subsumption)."))
    g_pr.add_argument("--probes-per-kind", type=int, default=2, metavar="N",
                      help="Max probes of each kind per problem (default 2, "
                           "giving ~7-8 probes per problem).")
    g_pr.add_argument("--probe-samples", type=int, default=1, metavar="K",
                      help="Samples per probe (default 1: power comes from the "
                           "~780 probe items, not from repeated draws).")

    # ── Task 2: gradual semantics ────────────────────────────────────────────
    g_t2 = p.add_argument_group("Task 2 - gradual semantics")
    g_t2.add_argument("--graded", action="store_true",
                      help="Run gradual ABA semantics (BSAF headline + BAF baseline).")
    g_t2.add_argument("--graded-source",
                      choices=["uniform", "sample_freq", "llm_elicited"],
                      default="uniform",
                      help=(
                          "Base-score source for the assumption strengths:\n"
                          "  uniform      : all = 0.5 (no extra calls)\n"
                          "  sample_freq  : frequency across k LLM samples\n"
                          "  llm_elicited : one dedicated LLM call per assumption\n"
                      ))
    g_t2.add_argument("--graded-kernel",
                      choices=["dfquad_prod", "dfquad_min", "qe_prod", "qe_min"],
                      default="dfquad_prod",
                      help="BSAF modular kernel (default dfquad_prod, most robust).")
    g_t2.add_argument("--graded-claim-mode",
                      choices=["max", "min", "avg", "noisy_or"],
                      default="max",
                      help="Claim reading from assumption strengths "
                           "(default max = faithful brave entailment).")

    # ── Reporting / output ───────────────────────────────────────────────────
    g_out = p.add_argument_group("Reporting / output")
    g_out.add_argument("--output", default="./results",
                       help="Output directory for results and figures.")
    g_out.add_argument("--export", action="store_true",
                       help="Export learned frameworks to frameworks.{jsonl,md,csv} "
                            "(natural-language rules, mechanism tags, narratives, and "
                            "graded scores if --graded).")
    g_out.add_argument("--verbose", action="store_true")

    return p.parse_args()


def _build_backend_kwargs(args: argparse.Namespace) -> dict:
    """Collect backend-specific constructor kwargs from parsed args."""
    kwargs: dict = {}
    if args.backend in ("groq", "google_ai") and args.min_interval > 0:
        kwargs["min_interval_s"] = args.min_interval
    if args.backend == "google_ai" and getattr(args, "thinking", False):
        kwargs["thinking"] = True
    if args.backend == "local" and getattr(args, "load_4bit", False):
        kwargs["load_4bit"] = True
    return kwargs


def main() -> None:
    args = parse_args()
    os.makedirs(args.output, exist_ok=True)

    print("=" * 60)
    print("ABA Framework Learning - Thesis Experiments")
    print("=" * 60)

    # ── Dataset ──────────────────────────────────────────────────────────────
    print("\n[1/4] Building dataset...")
    ds = build_dataset(
        n_synthetic=args.n_synthetic,
        n_complex=args.n_complex,
        benchmark_per_tier=args.benchmark,
        solve_symbolic=True,
        anonymize=args.anonymize,
        anonymize_scheme=args.anonymize_scheme,
        output_dir=args.output,
    )

    # ── Symbolic baseline ─────────────────────────────────────────────────────
    print("\n[2/4] Symbolic baseline (ASP-ABAlearnB)...")
    symbolic_results = run_symbolic_baseline(ds, verbose=args.verbose,
                                             output_dir=args.output)

    if args.symbolic_only:
        report_path = os.path.join(args.output, "symbolic_results.json")
        with open(report_path, "w") as f:
            json.dump(symbolic_results, f, indent=2)
        print(f"\nSymbolic results saved to {report_path}")

        sym_graded_data: Optional[Dict] = None
        if args.graded:
            # For symbolic-only runs, sample_freq has no samples to draw from;
            # llm_elicited needs a backend — create one only if required.
            graded_backend = None
            if args.graded_source == "llm_elicited":
                backend_kwargs = _build_backend_kwargs(args)
                graded_backend = get_backend(
                    args.backend, model=args.model, **backend_kwargs
                )
            sym_graded_data = run_graded_analysis(
                ds, graded_backend,
                source=args.graded_source,
                output_dir=args.output,
                kernel=args.graded_kernel,
                claim_mode=args.graded_claim_mode,
            )
        if args.export:
            print("\n[Optional] Exporting symbolic frameworks...")
            run_export(ds, graded_data=sym_graded_data, output_dir=args.output)
        return

    # ── LLM prompt experiments ────────────────────────────────────────────────
    print(f"\n[3/4] LLM experiments (backend={args.backend}, "
          f"model={args.model or 'default'})...")
    backend_kwargs = _build_backend_kwargs(args)
    backend = get_backend(args.backend, model=args.model, **backend_kwargs)

    if args.probes:
        run_probe_experiment(
            ds, backend,
            max_per_kind=args.probes_per_kind,
            n_samples=args.probe_samples,
            max_tokens=min(args.max_tokens, 512),
            output_dir=args.output,
            verbose=True,
        )
        return

    results_by_mode = run_prompt_experiments(
        ds, backend,
        modes=args.modes,
        n_samples=args.n_samples,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        output_dir=args.output,
    )

    # ── Report ────────────────────────────────────────────────────────────────
    print("\n[4/4] Generating report and figures...")
    generate_report(results_by_mode, symbolic_results, ds, args.output)

    # ── Optional graded semantics analysis ───────────────────────────────────
    graded_data: Optional[Dict] = None
    if args.graded:
        print("\n[Optional] Running graded semantics analysis...")
        graded_data = run_graded_analysis(
            ds, backend,
            source=args.graded_source,
            results_by_mode=results_by_mode,
            output_dir=args.output,
            kernel=args.graded_kernel,
            claim_mode=args.graded_claim_mode,
        )

    # ── Optional framework export ─────────────────────────────────────────────
    if args.export:
        print("\n[Optional] Exporting frameworks...")
        run_export(
            ds,
            results_by_mode=results_by_mode,
            graded_data=graded_data,
            source_name=args.model or args.backend,
            output_dir=args.output,
        )

    print("\nDone.")


if __name__ == "__main__":
    main()