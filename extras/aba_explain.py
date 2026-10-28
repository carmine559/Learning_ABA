"""
aba_explain.py
Explainability layer: a structured account of one answer beside the algorithm's,
on the problem as posed.

Three complementary views:
  1. Rule-level diff   — what the LLM wrote vs. the algorithm's answer, aligned
                         by the predicate they define.
  2. Example outcomes  — which posed examples the answer gets right, one at a time.
  3. Mechanism tags    — a categorical label for the *kind* of rule the model
                         wrote (folding, assumption-introduction, condition-copying,
                         memorisation, ...).

This is descriptive, not normative: the score card (src/aba_score.py) decides
success, and this explains it, grounded in the rules the model actually wrote.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from src.aba_types import Rule, ABAFramework, LearningProblem
from src.aba_dataset import DatasetEntry
from src.aba_generalization import rule_contains_constant
from src.aba_validator import check_brave_entailment
from src.aba_prompts import parse_llm_output
from src.aba_score import Reference, ScoreCard


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
# Per-example outcomes on the posed examples
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ExampleOutcome:
    example:     str
    is_positive: bool
    correct:     bool


def example_outcomes(
    llm_framework: ABAFramework,
    problem: LearningProblem,
) -> List[ExampleOutcome]:
    """
    Each posed example checked on its own. Weaker than Definition 1, which asks
    for ONE extension accepting every positive and no negative: this says which
    examples an invalid answer gets wrong.
    """
    domain = problem.get_domain()
    outcomes: List[ExampleOutcome] = []
    for e in problem.positive:
        ok, _, _ = check_brave_entailment(llm_framework, [e], [], domain)
        outcomes.append(ExampleOutcome(e, True, ok))
    for e in problem.negative:
        ok, _, _ = check_brave_entailment(llm_framework, [], [e], domain)
        outcomes.append(ExampleOutcome(e, False, ok))
    return outcomes


# ──────────────────────────────────────────────────────────────────────────────
# Full per-problem explanation
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ProblemExplanation:
    problem_id:     str
    mode:           str
    # From the score card (src/aba_score.py), so explanations.md and summary.json
    # cannot disagree about which answers succeeded.
    valid:          bool
    clean:          bool
    exact:          bool
    intensional:    bool
    agreement:      Optional[float]
    comparisons:    List[RuleComparison]
    outcomes:       List[ExampleOutcome]
    narrative:      str = ""
    violations:     List[str] = field(default_factory=list)
    self_defeating: List[str] = field(default_factory=list)


def explain_sample(
    entry: DatasetEntry,
    ref: Reference,
    raw_output: str,
    card: ScoreCard,
    mode: str = "direct",
) -> Optional[ProblemExplanation]:
    """One answer beside the algorithm's, from its raw output and its score card."""
    background = entry.problem.background
    candidate = parse_llm_output(raw_output, background)
    if candidate is None:
        return None
    expl = ProblemExplanation(
        problem_id=entry.problem.problem_id,
        mode=mode,
        valid=card.valid,
        clean=card.clean,
        exact=card.exact,
        intensional=card.intensional,
        agreement=card.agreement,
        comparisons=compare_rules(candidate, ref.solution, background),
        outcomes=example_outcomes(candidate, entry.problem),
        violations=list(card.illformed),
        self_defeating=list(card.self_defeating),
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
    A short account of the answer, grounded in the rules it wrote and the
    verified outcomes.
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
    if expl.clean:
        lines.append(
            f"On '{pid}', the answer is an intensional solution (Definition 1): one "
            f"stable extension accepts every positive example and no negative one."
        )
    elif expl.valid:
        why = []
        if not expl.intensional:
            why.append("it keeps ground facts")
        if expl.self_defeating:
            why.append(f"it is self-defeating on {', '.join(expl.self_defeating)}")
        if expl.violations:
            why.append("it is ill-formed")
        lines.append(f"On '{pid}', the answer is a solution but not a clean one: "
                     f"{'; '.join(why)}.")
    else:
        wrong = [o.example for o in expl.outcomes if not o.correct]
        lines.append(
            f"On '{pid}', the answer is not a solution: no stable extension accepts "
            f"every positive example and no negative one."
            + (f" Taken one at a time, it gets {len(wrong)} of {len(expl.outcomes)} "
               f"posed examples wrong ({', '.join(wrong[:4])}"
               f"{', ...' if len(wrong) > 4 else ''})." if wrong else "")
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

        if all(rule_contains_constant(r) for r in candidate.new_rules):
            lines.append(
                "These are all ground facts: the answer restates examples instead "
                "of learning a general rule."
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
                        f"satisfying them."
                    )
        if candidate.new_assumptions:
            lines.append(
                f"It also introduced the assumption(s) "
                f"{', '.join(candidate.new_assumptions)} to make a rule "
                f"defeasible, capturing exceptions."
            )

    # 3. Comparison with the algorithm's answer
    if expl.exact:
        lines.append("It is the algorithm's answer, up to assumption names and body order.")
    else:
        different = [c for c in expl.comparisons if not c.identical]
        if different:
            diffs = "; ".join(
                f"{c.predicate}: model wrote {c.llm_rules or ['nothing']}, "
                f"the algorithm has {c.reference_rules or ['nothing']}"
                for c in different[:3]
            )
            lines.append(f"It differs from the algorithm's answer on: {diffs}.")
    if expl.agreement is not None and expl.agreement < 1:
        lines.append(
            f"Off the posed examples, it decides {expl.agreement:.0%} of the example "
            f"predicate's atoms as the algorithm's answer does."
        )

    return " ".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Aggregate mechanism statistics across a run
# ──────────────────────────────────────────────────────────────────────────────

def mechanism_statistics(
    explanations: List[ProblemExplanation],
) -> Dict[str, float]:
    """
    Across all explained answers: how often did each mechanism co-occur with a
    clean answer?
    """
    from collections import defaultdict
    mech_total: Dict[str, int] = defaultdict(int)
    mech_clean: Dict[str, int] = defaultdict(int)

    for expl in explanations:
        seen = set()
        for c in expl.comparisons:
            for m in c.llm_mechanism:
                seen.add(m)
        for m in seen:
            mech_total[m] += 1
            if expl.clean:
                mech_clean[m] += 1

    return {
        m: round(mech_clean[m] / mech_total[m], 3)
        for m in mech_total if mech_total[m] > 0
    }
