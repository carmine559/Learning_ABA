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
import re
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
    wellformed_violations,
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
    # Every repair the parser applied to reach a framework (misfiled rules,
    # multiple answer blocks, echoed problem statement). Kept so a score can
    # always be traced back to what the model literally wrote.
    parse_repairs: List[str] = field(default_factory=list)

    # Stability
    has_extension: bool = False

    # Fit + generalisation (the core signals)
    fit_valid:            bool  = False
    gen_valid:            bool  = False       # brave: SOME extension is right
    gen_determined:       bool  = False       # strict: EVERY train-consistent
                                              # extension is right
    determinacy_score:    float = 0.0
    n_free_heldout:       int   = 0
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
    # The failing TRAIN examples themselves, not just how many. Makes the
    # qualitative error analysis possible directly from results_<mode>.jsonl
    # ("which examples does this model systematically get wrong?") without
    # re-running the solver.
    unentailed_positive_atoms: List[str] = field(default_factory=list)
    spurious_negative_atoms:   List[str] = field(default_factory=list)
    error_type:           str = "none"
    # Definition-1 side conditions ((ii), (iv), flatness) violated by the
    # candidate, if any — such samples are ill-formed regardless of entailment.
    wellformed_violations: List[str] = field(default_factory=list)

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

def score_llm_output(
    entry: DatasetEntry,
    split: SplitProblem,
    raw_output: str,
    mode: str,
    model_name: str,
    sample_idx: int = 0,
) -> SampleResult:
    """Score one raw LLM answer. The single source of truth for every metric.

    Kept separate from generation so that `rescore.py` can recompute metrics
    from the `raw_output` already stored in results_<mode>.jsonl, without
    spending GPU time again — and so that no second copy of the scoring logic
    can drift from this one.
    """
    problem = split.train          # the LLM only ever sees the training problem
    r = SampleResult(
        problem_id=entry.problem.problem_id,
        mode=mode,
        model_name=model_name,
        source=entry.source,
        sample_idx=sample_idx,
    )
    r.raw_output = raw_output

    # 2. Parse
    candidate = parse_llm_output(raw_output, problem.background,
                                 repairs=r.parse_repairs)
    r.parse_success = candidate is not None
    if candidate is None:
        r.error_type = "parse_error"
        return r

    r.n_new_rules       = len(candidate.new_rules)
    r.n_new_assumptions = len(candidate.new_assumptions)

    # 2b. Definition-1 well-formedness ((ii) learnable heads, (iv) unchanged
    #     contraries, flatness, assumption freshness). An ill-formed candidate
    #     is not a legal solution regardless of what it entails.
    r.wellformed_violations = wellformed_violations(
        candidate, entry.problem.background, entry.problem.learnable
    )
    if r.wellformed_violations:
        r.error_type = "illformed_solution"
        return r

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
    r.gen_determined       = gen.gen_determined
    r.determinacy_score    = gen.determinacy_score
    r.n_free_heldout       = gen.n_free_heldout
    r.generalization_score = gen.generalization_score
    r.overfit_gap          = gen.overfit_gap
    r.intensional          = gen.is_intensional
    r.is_degenerate        = gen.is_degenerate
    r.unentailed_positives = gen.unentailed_positives
    r.spurious_negatives   = gen.spurious_negatives
    r.unentailed_positive_atoms = list(gen.unentailed_positive_atoms)
    r.spurious_negative_atoms   = list(gen.spurious_negative_atoms)
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
    """Prompt the model once, then score its answer with `score_llm_output`.

    Deliberately ONE turn. The thesis measures whether a model can execute
    ASP-ABAlearnB unaided; any follow-up turn that carries the solver's verdict
    back to the model would be measuring oracle-guided search instead, and a
    result obtained that way could not be reported as replication.
    """
    model_name = getattr(backend, "model", type(backend).__name__)

    prompt = problem_to_prompt(
        split.train, mode=mode, precomputed_role_facts=precomputed_role_facts
    )
    try:
        resp = backend.generate(prompt, temperature=temperature, max_tokens=max_tokens)
    except Exception as exc:
        import traceback
        r = SampleResult(
            problem_id=entry.problem.problem_id, mode=mode,
            model_name=model_name, source=entry.source, sample_idx=sample_idx,
        )
        r.error_type = "llm_error"
        # Keep the full traceback: an opaque "AttributeError:" with no frames
        # cost us a cluster run to diagnose. This lands in results_<mode>.jsonl.
        r.raw_output = (f"[LLM ERROR] {type(exc).__name__}: {exc}\n"
                        + traceback.format_exc())
        return r

    r = score_llm_output(entry, split, resp.text, mode, model_name, sample_idx)
    r.llm_latency_s     = resp.latency_s
    r.prompt_tokens     = resp.prompt_tokens
    r.completion_tokens = resp.completion_tokens
    # A truncated answer is a budget failure, not a reasoning failure — record
    # it so --max-tokens can be ruled in or out as a cause. Prefer the
    # backend's own finish_reason where it reports one; fall back to the token
    # count, which is all some backends expose.
    if getattr(resp, "finish_reason", None) == "length" or (
        resp.completion_tokens and resp.completion_tokens >= max_tokens
    ):
        r.parse_repairs.append(f"output hit the {max_tokens}-token cap")
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
    # STRICT generalisation (every train-consistent extension gets the held-out
    # examples right). gen_* alone cannot separate learning from a framework
    # that merely leaves the unseen atoms free.
    det_at_1:  float = 0.0
    det_at_k:  bool  = False
    determinacy_mean: float = 0.0
    free_heldout_mean: float = 0.0
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
        self.det_at_1   = sum(s.gen_determined for s in self.samples) / n
        self.det_at_k   = any(s.gen_determined for s in self.samples)
        self.determinacy_mean  = statistics.mean(s.determinacy_score
                                                 for s in self.samples)
        self.free_heldout_mean = statistics.mean(float(s.n_free_heldout)
                                                 for s in self.samples)
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

def wilson_interval(successes: float, n: int, z: float = 1.96) -> List[float]:
    """Wilson 95% score interval for a proportion.

    Reported alongside every headline rate: at n≈103 problems the sampling
    error is several points wide, which matters when comparing model×mode
    cells that differ by less than that.
    """
    if n <= 0:
        return [0.0, 0.0]
    p = successes / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return [round(max(0.0, (centre - half) / denom), 3),
            round(min(1.0, (centre + half) / denom), 3)]


def aggregate_results(results: List[ProblemResult]) -> Dict:
    if not results:
        return {}
    n = len(results)

    def _mean(key):
        return sum(getattr(r, key) for r in results) / n

    def _rate(key):
        """Mean of a per-problem @k boolean, with its Wilson interval."""
        s = sum(bool(getattr(r, key)) for r in results)
        return round(s / n, 3), wilson_interval(s, n)

    error_counts: Dict[str, int] = {}
    repair_counts: Dict[str, int] = {}
    for r in results:
        for s in r.samples:
            error_counts[s.error_type] = error_counts.get(s.error_type, 0) + 1
            for rep in s.parse_repairs:
                key = rep.split(":")[0]
                repair_counts[key] = repair_counts.get(key, 0) + 1

    # Quality rates are only defined over samples that produced a fitting
    # solution. Averaging the 0.0 that a problem with no such sample carries
    # would report "0% intensional" where the honest answer is "undefined".
    with_fit = [r for r in results if any(s.fit_valid for s in r.samples)]
    n_fit = len(with_fit)

    def _quality(key):
        if not with_fit:
            return None
        return round(sum(getattr(r, key) for r in with_fit) / n_fit, 3)

    fit_k, fit_ci     = _rate("fit_at_k")
    gen_k, gen_ci     = _rate("gen_at_k")
    det_k, det_ci     = _rate("det_at_k")
    clean_k, clean_ci = _rate("clean_at_k")

    return {
        "n_problems":        n,
        "parse_rate":        round(_mean("parse_rate"), 3),
        "fit_at_1":          round(_mean("fit_at_1"), 3),
        "gen_at_1":          round(_mean("gen_at_1"), 3),
        "det_at_1":          round(_mean("det_at_1"), 3),
        "fit_at_k":          fit_k,
        "gen_at_k":          gen_k,
        "det_at_k":          det_k,
        "clean_at_1":        round(_mean("clean_at_1"), 3),
        "clean_at_k":        clean_k,
        "ci95": {
            "fit_at_k":   fit_ci,
            "gen_at_k":   gen_ci,
            "det_at_k":   det_ci,
            "clean_at_k": clean_ci,
        },
        "gen_score_mean":    round(_mean("gen_score_mean"), 3),
        "determinacy_mean":  round(_mean("determinacy_mean"), 3),
        "free_heldout_mean": round(_mean("free_heldout_mean"), 3),
        "mean_overfit_gap":  round(_mean("mean_overfit_gap"), 3),
        "n_problems_with_fit": n_fit,
        "intensional_rate":  _quality("intensional_rate"),
        "degenerate_rate":   _quality("degenerate_rate"),
        "error_breakdown":   error_counts,
        "parse_repairs":     repair_counts,
    }


_TIER_RE = re.compile(r"^(t\d+_[a-z]+)_\d+")


def tier_breakdown(
    results_by_mode: Dict[str, List[ProblemResult]],
) -> Dict[str, Dict[str, Dict]]:
    """Aggregate per benchmark tier: mode -> tier -> metrics.

    The tier is read from the problem-id prefix (``t1_mono_0007[_anon]`` ->
    ``t1_mono``); the three built-ins group as ``builtin``. Returns {} when no
    benchmark problems are present, so the section only appears for
    ``--benchmark`` runs.
    """
    out: Dict[str, Dict[str, Dict]] = {}
    any_tier = False
    for mode, results in results_by_mode.items():
        groups: Dict[str, List[ProblemResult]] = {}
        for pr in results:
            m = _TIER_RE.match(pr.problem_id)
            any_tier = any_tier or bool(m)
            groups.setdefault(m.group(1) if m else "builtin", []).append(pr)
        out[mode] = {tier: aggregate_results(prs) for tier, prs in groups.items()}
    return out if any_tier else {}


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