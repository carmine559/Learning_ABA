"""
aba_explain.py
Explainability layer: turn raw evaluation results into a structured account of
HOW and WHY an LLM generalised (or failed to) on each problem.

Three complementary views:
  1. Rule-level diff      — what the LLM wrote vs. the symbolic ground truth,
                            aligned by the predicate they define.
  2. Generalisation trace — per held-out example, did the learned framework get
                            it right, and which rule was responsible.
  3. Mechanism tags       — a categorical label for the *kind* of generalisation
                            the model performed (folding, assumption-introduction,
                            condition-copying, memorisation, ...).

This is descriptive, not normative: it explains the behaviour that the
Clingo-verified metrics already established, so claims about "how" the model
generalised are grounded in the actual learned rules, not speculation.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

from src.aba_types import Rule, ABAFramework, LearningProblem
from src.aba_dataset import DatasetEntry
from src.aba_generalization import (
    SplitProblem, split_problem_examples, rule_contains_constant,
    evaluate_generalization, wellformed_violations,
)
from src.aba_validator import check_brave_entailment
from src.aba_prompts import parse_llm_output


# ──────────────────────────────────────────────────────────────────────────────
# Rule structure helpers
# ──────────────────────────────────────────────────────────────────────────────

def _head_pred(rule: Rule) -> str:
    m = re.match(r'^([a-z]\w*)', rule.head)
    return m.group(1) if m else rule.head


def _body_preds(rule: Rule) -> List[str]:
    preds = []
    for atom in rule.body:
        m = re.match(r'^([a-z]\w*)', atom.strip())
        if m and m.group(1) not in ("dom",):
            preds.append(m.group(1))
    return preds


def classify_rule_mechanism(rule: Rule, background: ABAFramework) -> str:
    """
    Label the *kind* of generalisation a single learnt rule represents.

    Returns one of:
      - "ground_fact"        : p(X) :- X = c        (memorisation)
      - "assumption_guarded" : body contains an assumption (defeasible rule)
      - "contrary_rule"      : head is a contrary of some assumption
      - "intensional_copy"   : body re-uses background predicates, no constants
      - "mixed"              : both a constant and general structure
    """
    has_const = rule_contains_constant(rule)
    bg_asms = set(background.assumptions)
    bg_contraries = set(background.contraries.values())

    head = rule.head
    body_set = set(a.strip() for a in rule.body)

    # head defines a contrary of an assumption?
    if head in bg_contraries or any(head == c for c in background.contraries.values()):
        return "contrary_rule"
    # body contains an assumption -> defeasible
    if body_set & bg_asms:
        return "assumption_guarded"
    if has_const and len(_body_preds(rule)) == 0:
        return "ground_fact"
    if has_const:
        return "mixed"
    return "intensional_copy"


# ──────────────────────────────────────────────────────────────────────────────
# Rule-level diff against the symbolic reference
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class RuleComparison:
    predicate:        str
    llm_rules:        List[str]
    reference_rules:  List[str]
    identical:        bool
    llm_mechanism:    List[str]   # mechanism tag per LLM rule


def compare_rules(
    llm_framework: ABAFramework,
    reference: ABAFramework,
    background: ABAFramework,
) -> List[RuleComparison]:
    """
    Align the LLM's new rules and the reference's new rules by head predicate
    and report, per predicate, how they differ.
    """
    def _by_pred(rules: List[Rule]) -> Dict[str, List[Rule]]:
        d: Dict[str, List[Rule]] = {}
        for r in rules:
            d.setdefault(_head_pred(r), []).append(r)
        return d

    llm_by  = _by_pred(llm_framework.new_rules)
    ref_by  = _by_pred(reference.new_rules)
    all_preds = sorted(set(llm_by) | set(ref_by))

    comparisons = []
    for pred in all_preds:
        llm_rs = llm_by.get(pred, [])
        ref_rs = ref_by.get(pred, [])
        llm_strs = sorted(r.to_prolog() for r in llm_rs)
        ref_strs = sorted(r.to_prolog() for r in ref_rs)
        comparisons.append(RuleComparison(
            predicate=pred,
            llm_rules=llm_strs,
            reference_rules=ref_strs,
            identical=(llm_strs == ref_strs),
            llm_mechanism=[classify_rule_mechanism(r, background) for r in llm_rs],
        ))
    return comparisons


# ──────────────────────────────────────────────────────────────────────────────
# Per-example generalisation trace
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ExampleOutcome:
    example:     str
    is_positive: bool
    held_out:    bool
    correct:     bool


def generalisation_trace(
    llm_framework: ABAFramework,
    split: SplitProblem,
    domain: List[str],
) -> List[ExampleOutcome]:
    """
    For every example (train and held-out), record whether the learned
    framework classified it correctly.
    """
    outcomes: List[ExampleOutcome] = []

    def _check(example: str, positive: bool, held: bool):
        if positive:
            ok, _, _ = check_brave_entailment(llm_framework, [example], [], domain)
        else:
            ok, _, _ = check_brave_entailment(llm_framework, [], [example], domain)
        outcomes.append(ExampleOutcome(example, positive, held, ok))

    for e in split.train.positive:   _check(e, True,  False)
    for e in split.train.negative:   _check(e, False, False)
    for e in split.test_positive:    _check(e, True,  True)
    for e in split.test_negative:    _check(e, False, True)
    return outcomes


# ──────────────────────────────────────────────────────────────────────────────
# Full per-problem explanation
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ProblemExplanation:
    problem_id:        str
    mode:              str
    fit:               bool
    generalises:       bool
    generalization_score: float
    is_degenerate:     bool
    semantic_match:    bool
    comparisons:       List[RuleComparison]
    outcomes:          List[ExampleOutcome]
    narrative:         str = ""
    # Definition-1 side conditions the candidate violates, if any. A violating
    # candidate is not a legal solution however well it scores on entailment.
    violations:        List[str] = field(default_factory=list)
    gen_determined:    bool = False


def explain_sample(
    entry: DatasetEntry,
    raw_output: str,
    mode: str = "direct",
    test_ratio: float = 0.34,
    split_seed: int = 42,
) -> Optional[ProblemExplanation]:
    """
    Reconstruct the full explanation for one LLM attempt from its raw output.
    Requires the dataset entry to carry the symbolic reference solution.
    """
    background = entry.problem.background
    candidate = parse_llm_output(raw_output, background)
    if candidate is None:
        return None

    split = split_problem_examples(entry.problem, test_ratio=test_ratio,
                                   seed=split_seed)
    domain = entry.problem.get_domain()

    # Rule diff (only if a reference exists)
    comparisons = []
    if entry.solution is not None:
        comparisons = compare_rules(candidate, entry.solution, background)

    outcomes = generalisation_trace(candidate, split, domain)

    # Derived flags — taken from the SAME function that produces summary.json.
    # Recomputing them here with per-example checks made explanations.md and
    # summary.json disagree about which samples succeeded.
    gen = evaluate_generalization(candidate, split, domain=domain)
    fit          = gen.fit_valid
    generalises  = gen.gen_valid
    gen_score    = gen.generalization_score
    is_degen     = gen.is_degenerate
    violations   = wellformed_violations(
        candidate, background, entry.problem.learnable
    )
    semantic = False
    if entry.solution is not None and entry.problem.learnable:
        from src.aba_generalization import semantic_equivalence
        semantic, _ = semantic_equivalence(
            candidate, entry.solution, entry.problem.learnable[0], domain
        )

    expl = ProblemExplanation(
        problem_id=entry.problem.problem_id,
        mode=mode,
        fit=fit,
        generalises=generalises,
        generalization_score=gen_score,
        is_degenerate=is_degen,
        semantic_match=semantic,
        comparisons=comparisons,
        outcomes=outcomes,
        violations=violations,
        gen_determined=gen.gen_determined,
    )
    expl.narrative = build_narrative(expl, candidate, entry)
    return expl


# ──────────────────────────────────────────────────────────────────────────────
# Natural-language narrative
# ──────────────────────────────────────────────────────────────────────────────

def build_narrative(
    expl: ProblemExplanation,
    candidate: ABAFramework,
    entry: DatasetEntry,
) -> str:
    """
    Produce a short human-readable explanation of how the model generalised.
    Grounded entirely in the learned rules and the verified outcomes.
    """
    lines: List[str] = []
    pid = expl.problem_id

    # 0. Legality comes first: an ill-formed candidate is not a solution, so
    # nothing below it should be read as success.
    if expl.violations:
        lines.append(
            f"On '{pid}', the candidate is NOT a legal solution: "
            f"{'; '.join(expl.violations)}. The outcome below is reported for "
            f"diagnosis only."
        )

    # 1. Outcome summary
    if expl.generalises:
        lines.append(
            f"On '{pid}', the model produced a framework that fits the training "
            f"examples and solves the full problem in one stable extension."
            + ("" if expl.gen_determined else
               " Note that the held-out labels are NOT forced: some other "
               "extension consistent with the training examples labels them "
               "differently, so this is a legal solution rather than evidence "
               "of a learnt generalisation.")
        )
    elif expl.fit:
        lines.append(
            f"On '{pid}', the model fits the training examples but only "
            f"classifies {expl.generalization_score:.0%} of held-out examples "
            f"correctly — partial generalisation."
        )
    else:
        lines.append(
            f"On '{pid}', the model failed to fit the training examples."
        )

    # 2. Mechanism account
    if candidate.new_rules:
        mech_counts: Dict[str, int] = {}
        for r in candidate.new_rules:
            m = classify_rule_mechanism(r, entry.problem.background)
            mech_counts[m] = mech_counts.get(m, 0) + 1
        mech_desc = ", ".join(f"{v} {k.replace('_', ' ')}"
                              for k, v in mech_counts.items())
        lines.append(f"It introduced {len(candidate.new_rules)} new rule(s): {mech_desc}.")

        if expl.is_degenerate:
            lines.append(
                "These are all ground facts — the model MEMORISED the training "
                "positives rather than learning a general rule, which is why it "
                "fails on held-out examples."
            )
        elif any("intensional_copy" in classify_rule_mechanism(r, entry.problem.background)
                 for r in candidate.new_rules):
            # Identify which background predicate it generalised over
            general_rules = [r for r in candidate.new_rules
                             if not rule_contains_constant(r)]
            for r in general_rules[:2]:
                bps = _body_preds(r)
                if bps:
                    lines.append(
                        f"The rule '{r.to_prolog()}' generalises by conditioning "
                        f"the target on the background predicate(s) "
                        f"{', '.join(bps)}, so it applies to any constant "
                        f"satisfying them — including unseen ones."
                    )
        if candidate.new_assumptions:
            lines.append(
                f"It also introduced the assumption(s) "
                f"{', '.join(candidate.new_assumptions)} to make a rule "
                f"defeasible, capturing exceptions."
            )

    # 3. Comparison with the symbolic reference
    if expl.comparisons:
        identical = [c for c in expl.comparisons if c.identical]
        different = [c for c in expl.comparisons if not c.identical]
        if expl.semantic_match:
            lines.append(
                "Semantically, the learned framework is equivalent to the "
                "symbolic reference (same entailments over the whole domain), "
                + ("via identical rules."
                   if not different else
                   "even though some rules are written differently.")
            )
        elif different:
            diffs = "; ".join(
                f"{c.predicate}: model wrote {c.llm_rules or ['nothing']}, "
                f"reference has {c.reference_rules or ['nothing']}"
                for c in different[:3]
            )
            lines.append(f"It differs from the symbolic reference on: {diffs}.")

    return " ".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Aggregate mechanism statistics across a run
# ──────────────────────────────────────────────────────────────────────────────

def mechanism_statistics(
    explanations: List[ProblemExplanation],
) -> Dict[str, float]:
    """
    Aggregate: across all explained samples, how often did each mechanism
    co-occur with successful generalisation?
    """
    from collections import defaultdict
    mech_total: Dict[str, int] = defaultdict(int)
    mech_gen:   Dict[str, int] = defaultdict(int)

    for expl in explanations:
        seen = set()
        for c in expl.comparisons:
            for m in c.llm_mechanism:
                seen.add(m)
        for m in seen:
            mech_total[m] += 1
            if expl.generalises:
                mech_gen[m] += 1

    return {
        m: round(mech_gen[m] / mech_total[m], 3)
        for m in mech_total if mech_total[m] > 0
    }