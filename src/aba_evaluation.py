"""
aba_evaluation.py  (refactored)
Evaluation with held-out generalization testing and k-sampling.

Key methodological upgrades over the original:
  - Example-level train/test split: the LLM learns from TRAIN examples and is
    scored on HELD-OUT examples, distinguishing learning from memorisation.
  - k-sampling: each problem is attempted n_samples times; we report pass@1
    (mean) and pass@k (any success), with standard deviation.
  - Structured error profile instead of a single first-match error label.
  - Semantic comparison with the symbolic reference instead of string equality.
"""
from __future__ import annotations
import json
import time
import statistics
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any

from src.aba_types import Rule, ABAFramework, LearningProblem
from src.aba_dataset import ABADataset, DatasetEntry
from src.aba_validator import (
    validate_llm_solution, check_brave_entailment, check_has_stable_extension,
    run_rote_learning,
)
from src.aba_prompts import problem_to_prompt, parse_llm_output
from src.aba_model import LLMBackend, ModelResponse
from src.aba_generalization import (
    SplitProblem, split_problem_examples, evaluate_generalization,
    GeneralizationResult, semantic_equivalence, is_intensional_strict,
)


# ──────────────────────────────────────────────────────────────────────────────
# Single-sample result
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SampleResult:
    """Result of one LLM attempt at one problem."""
    problem_id:   str
    mode:         str
    model_name:   str
    source:       str
    sample_idx:   int = 0

    # Parsing
    parse_success: bool = False
    raw_output:    str  = ""

    # Stability
    has_extension: bool = False

    # Fit + generalisation (the core signals)
    fit_valid:            bool  = False
    gen_valid:            bool  = False
    generalization_score: float = 0.0
    overfit_gap:          float = 0.0

    # Solution quality
    intensional:   bool = False
    is_degenerate: bool = False
    n_new_rules:       int = 0
    n_new_assumptions: int = 0

    # Error profile
    unentailed_positives: int = 0
    spurious_negatives:   int = 0
    error_type:           str = "none"

    # Reference comparison (semantic)
    semantic_match:        bool  = False
    semantic_agreement:    float = 0.0

    # Cost
    llm_latency_s:     float = 0.0
    clingo_time_s:     float = 0.0
    prompt_tokens:     int = 0
    completion_tokens: int = 0

    def to_dict(self) -> Dict:
        return asdict(self)


def _classify_error(
    parse_success: bool,
    has_extension: bool,
    gen: GeneralizationResult,
) -> str:
    if not parse_success:
        return "parse_error"
    if not has_extension:
        return "stability_error"
    if gen.unentailed_positives > 0 and gen.spurious_negatives > 0:
        return "both_errors"
    if gen.unentailed_positives > 0:
        return "completeness_error"
    if gen.spurious_negatives > 0:
        return "soundness_error"
    if not gen.gen_valid:
        return "generalization_error"   # fits train, fails held-out
    if gen.is_degenerate:
        return "degenerate"             # memorised but happened to generalise
    return "none"


# ──────────────────────────────────────────────────────────────────────────────
# One sample
# ──────────────────────────────────────────────────────────────────────────────

def evaluate_one_sample(
    entry: DatasetEntry,
    split: SplitProblem,
    backend: LLMBackend,
    mode: str,
    sample_idx: int = 0,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    precomputed_role_facts: Optional[List[Rule]] = None,
) -> SampleResult:
    problem = split.train          # the LLM only ever sees the training problem
    r = SampleResult(
        problem_id=entry.problem.problem_id,
        mode=mode,
        model_name=getattr(backend, "model", type(backend).__name__),
        source=entry.source,
        sample_idx=sample_idx,
    )

    # 1. Prompt + generate
    prompt = problem_to_prompt(
        problem, mode=mode, precomputed_role_facts=precomputed_role_facts
    )
    try:
        resp = backend.generate(prompt, temperature=temperature, max_tokens=max_tokens)
    except Exception as exc:
        import traceback
        r.error_type = "llm_error"
        # Keep the full traceback: an opaque "AttributeError:" with no frames
        # cost us a cluster run to diagnose. This lands in results_<mode>.jsonl.
        r.raw_output = (f"[LLM ERROR] {type(exc).__name__}: {exc}\n"
                        + traceback.format_exc())
        return r
    r.llm_latency_s     = resp.latency_s
    r.raw_output        = resp.text
    r.prompt_tokens     = resp.prompt_tokens
    r.completion_tokens = resp.completion_tokens

    # 2. Parse
    candidate = parse_llm_output(resp.text, problem.background)
    r.parse_success = candidate is not None
    if candidate is None:
        r.error_type = "parse_error"
        return r

    r.n_new_rules       = len(candidate.new_rules)
    r.n_new_assumptions = len(candidate.new_assumptions)

    # 3. Stability + generalisation
    domain = entry.problem.get_domain()
    try:
        r.has_extension = check_has_stable_extension(candidate, domain)
        gen = evaluate_generalization(candidate, split, domain=domain)
    except Exception:
        r.parse_success = False
        r.error_type = "parse_error"
        return r

    r.fit_valid            = gen.fit_valid
    r.gen_valid            = gen.gen_valid
    r.generalization_score = gen.generalization_score
    r.overfit_gap          = gen.overfit_gap
    r.intensional          = gen.is_intensional
    r.is_degenerate        = gen.is_degenerate
    r.unentailed_positives = gen.unentailed_positives
    r.spurious_negatives   = gen.spurious_negatives
    r.error_type           = _classify_error(r.parse_success, r.has_extension, gen)

    # 4. Semantic comparison with the symbolic reference (if available)
    if entry.solution is not None:
        target = entry.problem.learnable[0] if entry.problem.learnable else None
        if target:
            match, frac = semantic_equivalence(
                candidate, entry.solution, target, domain
            )
            r.semantic_match     = match
            r.semantic_agreement = frac

    return r


# ──────────────────────────────────────────────────────────────────────────────
# k-sampling per problem
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ProblemResult:
    """Aggregated result over k samples of one problem."""
    problem_id: str
    mode:       str
    model_name: str
    source:     str
    samples:    List[SampleResult] = field(default_factory=list)

    # pass@1 — mean over independent samples
    fit_at_1:  float = 0.0
    gen_at_1:  float = 0.0
    # pass@k — success if ANY sample succeeds
    fit_at_k:  bool  = False
    gen_at_k:  bool  = False
    # STRICT success (the ABA-Learning definition): the sample fits ALL
    # training examples AND generalises to held-out AND is stable AND is not
    # degenerate — i.e. error_type == "none". gen@k alone flatters solutions
    # that violate the training negatives (e.g. 80% gen@k with 0% fit on t3).
    clean_at_1: float = 0.0
    clean_at_k: bool  = False
    # variability
    gen_score_mean: float = 0.0
    gen_score_std:  float = 0.0
    # quality (over samples that produced a parseable, valid-fit solution)
    intensional_rate: float = 0.0
    degenerate_rate:  float = 0.0
    parse_rate:       float = 0.0
    mean_overfit_gap: float = 0.0

    def compute(self) -> None:
        n = len(self.samples)
        if n == 0:
            return
        self.parse_rate = sum(s.parse_success for s in self.samples) / n
        self.fit_at_1   = sum(s.fit_valid for s in self.samples) / n
        self.gen_at_1   = sum(s.gen_valid for s in self.samples) / n
        self.fit_at_k   = any(s.fit_valid for s in self.samples)
        self.gen_at_k   = any(s.gen_valid for s in self.samples)
        clean = [s.error_type == "none" for s in self.samples]
        self.clean_at_1 = sum(clean) / n
        self.clean_at_k = any(clean)
        scores = [s.generalization_score for s in self.samples]
        self.gen_score_mean = statistics.mean(scores)
        self.gen_score_std  = statistics.pstdev(scores) if n > 1 else 0.0
        self.mean_overfit_gap = statistics.mean(s.overfit_gap for s in self.samples)
        # quality among fit-valid samples
        fit_samples = [s for s in self.samples if s.fit_valid]
        if fit_samples:
            self.intensional_rate = sum(s.intensional for s in fit_samples) / len(fit_samples)
            self.degenerate_rate  = sum(s.is_degenerate for s in fit_samples) / len(fit_samples)

    def to_dict(self) -> Dict:
        d = {k: v for k, v in asdict(self).items() if k != "samples"}
        d["n_samples"] = len(self.samples)
        return d


def evaluate_problem(
    entry: DatasetEntry,
    backend: LLMBackend,
    mode: str,
    n_samples: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    test_ratio: float = 0.34,
    split_seed: int = 42,
) -> ProblemResult:
    # Build the train/test split once
    split = split_problem_examples(
        entry.problem, test_ratio=test_ratio, seed=split_seed
    )

    # Precompute RoLe facts once for guided mode (avoids repeated ASP calls).
    # IMPORTANT: RoLe is run on the TRAIN problem only — no test-set leakage.
    precomputed = None
    if mode == "guided":
        precomputed, _ok, _ = run_rote_learning(split.train)

    result = ProblemResult(
        problem_id=entry.problem.problem_id,
        mode=mode,
        model_name=getattr(backend, "model", type(backend).__name__),
        source=entry.source,
    )
    for i in range(n_samples):
        s = evaluate_one_sample(
            entry, split, backend, mode,
            sample_idx=i,
            temperature=temperature,
            max_tokens=max_tokens,
            precomputed_role_facts=precomputed,
        )
        result.samples.append(s)
    result.compute()
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Dataset-level evaluation
# ──────────────────────────────────────────────────────────────────────────────

def evaluate_dataset(
    dataset: ABADataset,
    backend: LLMBackend,
    mode: str,
    n_samples: int = 5,
    temperature: float = 0.7,
    max_tokens: int = 1024,
    test_ratio: float = 0.34,
    verbose: bool = True,
) -> List[ProblemResult]:
    results: List[ProblemResult] = []
    n = len(dataset)
    _api_error_shown = False
    for i, entry in enumerate(dataset):
        pid = entry.problem.problem_id
        if verbose:
            print(f"  [{i+1}/{n}] {pid} (k={n_samples}) ...", end=" ")
        pr = evaluate_problem(
            entry, backend, mode,
            n_samples=n_samples,
            temperature=temperature,
            max_tokens=max_tokens,
            test_ratio=test_ratio,
        )
        results.append(pr)
        if verbose:
            print(f"gen@1={pr.gen_at_1:.0%} gen@k={'yes' if pr.gen_at_k else 'no'} "
                  f"fit@1={pr.fit_at_1:.0%} parse={pr.parse_rate:.0%}")

        # Surface the actual LLM error the first time it happens — otherwise an
        # invalid model id or a backend bug looks like a silent parse failure.
        if not _api_error_shown:
            llm_errs = [s for s in pr.samples if s.error_type == "llm_error"]
            if llm_errs:
                _api_error_shown = True
                backend_name = type(backend).__name__
                print(f"\n  [!] LLM ERROR DETECTED (backend={backend_name}) - "
                      "the generate() call is failing, not the parser.")
                print(f"     {llm_errs[0].raw_output}")
                if backend_name == "GroqBackend":
                    print("     Check model ids at "
                          "https://console.groq.com/docs/models\n")
                elif backend_name == "LocalHFBackend":
                    print("     Check the HF model id / VRAM fit; "
                          "full traceback above.\n")
                else:
                    print("     Common causes: invalid --model id, missing or "
                          "expired API key, or rate limiting.\n")
    return results


# ──────────────────────────────────────────────────────────────────────────────
# Aggregation
# ──────────────────────────────────────────────────────────────────────────────

def aggregate_results(results: List[ProblemResult]) -> Dict:
    if not results:
        return {}
    n = len(results)

    def _mean(key):
        return sum(getattr(r, key) for r in results) / n

    error_counts: Dict[str, int] = {}
    for r in results:
        for s in r.samples:
            error_counts[s.error_type] = error_counts.get(s.error_type, 0) + 1

    return {
        "n_problems":        n,
        "parse_rate":        round(_mean("parse_rate"), 3),
        "fit_at_1":          round(_mean("fit_at_1"), 3),
        "gen_at_1":          round(_mean("gen_at_1"), 3),
        "fit_at_k":          round(sum(r.fit_at_k for r in results) / n, 3),
        "gen_at_k":          round(sum(r.gen_at_k for r in results) / n, 3),
        "clean_at_1":        round(_mean("clean_at_1"), 3),
        "clean_at_k":        round(sum(r.clean_at_k for r in results) / n, 3),
        "gen_score_mean":    round(_mean("gen_score_mean"), 3),
        "mean_overfit_gap":  round(_mean("mean_overfit_gap"), 3),
        "intensional_rate":  round(_mean("intensional_rate"), 3),
        "degenerate_rate":   round(_mean("degenerate_rate"), 3),
        "error_breakdown":   error_counts,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Complexity analysis (for scatter plots)
# ──────────────────────────────────────────────────────────────────────────────

def complexity_analysis(
    dataset: ABADataset,
    results: List[ProblemResult],
) -> List[Dict]:
    rows = []
    rmap = {r.problem_id: r for r in results}
    for entry in dataset:
        pid = entry.problem.problem_id
        r = rmap.get(pid)
        if r is None:
            continue
        rows.append({
            "problem_id":         pid,
            "n_background_rules": len(entry.problem.background.rules),
            "n_assumptions":      len(entry.problem.background.assumptions),
            "n_positive":         len(entry.problem.positive),
            "n_negative":         len(entry.problem.negative),
            "domain_size":        len(entry.problem.get_domain()),
            "valid":              r.gen_at_k,          # use generalisation
            "gen_at_1":           r.gen_at_1,
            "intensional":        r.intensional_rate >= 0.5,
        })
    return rows


# ──────────────────────────────────────────────────────────────────────────────
# Symbolic reference comparison
# ──────────────────────────────────────────────────────────────────────────────

def compare_with_reference(
    dataset: ABADataset,
    results: List[ProblemResult],
) -> Dict:
    rmap = {r.problem_id: r for r in results}
    n_ref = sum(1 for e in dataset if e.solution is not None)
    n_gen = sum(1 for r in results if r.gen_at_k)
    n_semantic = 0
    for r in results:
        if any(s.semantic_match for s in r.samples):
            n_semantic += 1
    return {
        "reference_solutions_available": n_ref,
        "llm_generalises_at_k":          n_gen,
        "llm_semantically_matches_ref":  n_semantic,
    }