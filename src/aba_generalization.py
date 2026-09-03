"""
aba_generalization.py
Example-level train/test methodology — the core scientific instrument.

The research question is whether an LLM can *learn* an ABA framework, i.e.
produce rules that generalise beyond the observed examples. A framework that
merely asserts the training positives as ground facts fits the training set but
does not generalise. To distinguish learning from memorisation we:

  1. Split each problem's examples into a TRAIN set (shown to the LLM) and a
     held-out TEST set (never shown).
  2. Ask the LLM to learn a framework from the TRAIN examples only.
  3. Evaluate the learned framework on the held-out TEST examples.

The gap between training fit and held-out generalisation is the central
quantity of the thesis.
"""
from __future__ import annotations
import random
import re
from dataclasses import dataclass, field, replace
from typing import List, Tuple, Optional, Dict

from src.aba_types import Rule, ABAFramework, LearningProblem
from src.aba_validator import (
    check_brave_entailment, conditioned_status, witness_extension, _norm,
)


# ──────────────────────────────────────────────────────────────────────────────
# Train/test split at the example level
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SplitProblem:
    """A learning problem split into train and held-out test examples."""
    train: LearningProblem          # what the LLM sees
    test_positive: List[str]        # held-out positives
    test_negative: List[str]        # held-out negatives
    original_id: str = ""

    def has_test_set(self) -> bool:
        return bool(self.test_positive or self.test_negative)


def split_problem_examples(
    problem: LearningProblem,
    test_ratio: float = 0.34,
    min_train_each: int = 1,
    seed: int = 42,
) -> SplitProblem:
    """
    Hold out a fraction of positive AND negative examples for testing.

    Guarantees at least `min_train_each` positive and negative examples remain
    in the training set (so the LLM has something to learn from), and holds out
    at least one of each when possible.
    """
    rng = random.Random(seed)
    pos = list(problem.positive)
    neg = list(problem.negative)
    rng.shuffle(pos)
    rng.shuffle(neg)

    def _split(items: List[str]) -> Tuple[List[str], List[str]]:
        if len(items) <= min_train_each:
            return items, []                      # too few to hold out
        n_test = max(1, int(round(len(items) * test_ratio)))
        n_test = min(n_test, len(items) - min_train_each)
        return items[n_test:], items[:n_test]     # (train, test)

    train_pos, test_pos = _split(pos)
    train_neg, test_neg = _split(neg)

    train_problem = replace(
        problem,
        positive=train_pos,
        negative=train_neg,
        problem_id=problem.problem_id,
    )
    return SplitProblem(
        train=train_problem,
        test_positive=test_pos,
        test_negative=test_neg,
        original_id=problem.problem_id,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Degeneracy detection
# ──────────────────────────────────────────────────────────────────────────────

_CONST_RE = re.compile(r'\b[a-z][a-z0-9_]*\b')
_KEYWORDS = {"not", "true", "false", "dom"}


def rule_contains_constant(rule: Rule) -> bool:
    """
    True if the rule head or body mentions any individual constant — both the
    normalised form ``p(X) :- X = c`` and a bare ground fact ``p(c).``.
    A genuinely intensional rule contains only variables.

    Single implementation, shared with ``Rule.is_intensional`` so the strict
    and permissive notions can never drift apart again.
    """
    return rule.contains_constant()


def is_degenerate_solution(
    framework: ABAFramework,
    train_positive: List[str],
) -> bool:
    """
    A solution is degenerate (pure memorisation) if every newly learnt rule is a
    ground fact (mentions a constant) — i.e. it contains no general rule at all.
    An empty new-rule set is NOT degenerate (it may rely on the background).
    """
    new_rules = framework.new_rules
    if not new_rules:
        return False
    return all(rule_contains_constant(r) for r in new_rules)


def is_intensional_strict(framework: ABAFramework) -> bool:
    """
    Strict intensionality: NO new rule mentions any individual constant.
    Replaces the permissive equality-only check.
    """
    return all(not rule_contains_constant(r) for r in framework.new_rules)


# ──────────────────────────────────────────────────────────────────────────────
# Definition-1 well-formedness (side conditions entailment checks cannot see)
# ──────────────────────────────────────────────────────────────────────────────

_PRED_NAME_RE = re.compile(r'^(?:not\s+)?([a-z]\w*)')
_EQ_ATOM_RE   = re.compile(r'^[A-Z]\w*\s*=')
_RESERVED     = {"dom", "true", "false", "not"}


def _pred_of(atom: str) -> Optional[str]:
    """Predicate symbol of an atom string; None for equalities/reserved."""
    atom = atom.strip()
    if _EQ_ATOM_RE.match(atom):
        return None
    m = _PRED_NAME_RE.match(atom)
    if not m or m.group(1) in _RESERVED:
        return None
    return m.group(1)


def wellformed_violations(
    candidate: ABAFramework,
    background: ABAFramework,
    learnable: List[str],
) -> List[str]:
    """
    Check the side conditions of Definition 1 (De Angelis et al., ECAI 2024)
    that the entailment checks cannot detect. Returns human-readable violation
    messages (empty list = well-formed).

      (ii)  every NEW rule head whose predicate already occurs in the
            background language must be a LEARNABLE predicate; heads with
            genuinely new predicates (e.g. the contrary of a NEW assumption)
            are unrestricted. Note this covers contraries too: the contrary of
            a BACKGROUND assumption is part of the background language, so
            learning rules for it requires it to be in T -- exactly as the
            paper does in Example 3 (T = {pacifist, abnormal_quaker});
      (iv)  the contrary of every BACKGROUND assumption must be unchanged;
      flatness: no assumption predicate (old or new) may occur as a rule head;
      freshness: a NEW assumption's predicate must not REPURPOSE a background
            NON-assumption predicate. Re-listing an EXISTING background
            assumption is legal reuse (Definition 4) and is NOT a violation,
            even though the parser files it under "NEW ASSUMPTIONS".
    """
    viol: List[str] = []

    # Background predicates split by role: assumptions vs everything else.
    bg_asm_preds: set = {_pred_of(a) for a in background.assumptions} - {None}
    bg_nonasm: set = set()
    for r in background.rules:
        for atom in [r.head, *r.body]:
            p = _pred_of(atom)
            if p and p not in bg_asm_preds:
                bg_nonasm.add(p)
    for c in background.contraries.values():
        p = _pred_of(c)
        if p and p not in bg_asm_preds:
            bg_nonasm.add(p)
    bg_lang = bg_asm_preds | bg_nonasm

    asm_preds = {_pred_of(a) for a in candidate.assumptions} - {None}
    learn = set(learnable)

    for r in candidate.new_rules:
        hp = _pred_of(r.head)
        if hp is None:
            viol.append(f"reserved or malformed head: '{r.head}'")
            continue
        if hp in asm_preds:
            viol.append(f"flatness violated: assumption '{hp}' used as rule head")
        elif hp in bg_lang and hp not in learn:
            viol.append(f"condition (ii) violated: head '{hp}' is a background "
                        f"predicate not in the learnable set")

    for a in background.assumptions:
        old_c = background.contraries.get(a)
        new_c = candidate.contraries.get(a)
        if old_c is not None and new_c is not None and old_c != new_c:
            viol.append(f"condition (iv) violated: contrary of existing "
                        f"assumption '{a}' changed from '{old_c}' to '{new_c}'")

    for a in candidate.new_assumptions:
        p = _pred_of(a)
        # Legal reuse of an existing assumption (Def 4) is fine; only flag a
        # predicate that is defined in the background as a NON-assumption.
        if p and p in bg_nonasm:
            viol.append(f"new assumption predicate '{p}' repurposes background "
                        f"non-assumption predicate '{p}'")

    return viol


# ──────────────────────────────────────────────────────────────────────────────
# Generalisation evaluation
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class GeneralizationResult:
    # Fit (training examples — what the LLM saw)
    fit_valid:        bool = False
    n_train_pos:      int  = 0
    n_train_neg:      int  = 0

    # Generalisation (held-out examples — never shown)
    gen_valid:        bool = False          # all held-out examples correct
    n_test_pos:       int  = 0
    n_test_neg:       int  = 0
    test_pos_correct: int  = 0              # held-out positives correctly entailed
    test_neg_correct: int  = 0              # held-out negatives correctly rejected

    # Strict generalisation: every held-out example gets the right label in
    # EVERY extension consistent with the training examples. Rules out the
    # free-choice frameworks that brave entailment cannot distinguish from
    # genuine learning.
    gen_determined:    bool  = False
    n_free_heldout:    int   = 0            # held-out atoms the framework leaves open
    determinacy_score: float = 0.0          # fraction determined AND correct

    # Derived
    generalization_score: float = 0.0       # fraction of test examples correct
    overfit_gap:          float = 0.0       # fit (1/0) − gen_score
    is_degenerate:        bool  = False
    is_intensional:       bool  = False

    # Structured error profile (M9)
    unentailed_positives:   int = 0         # train positives NOT entailed
    spurious_negatives:     int = 0         # train negatives wrongly entailed
    # The same failures as atoms rather than counts. Recorded in the loops that
    # already compute the counts (no extra solver calls) so the self-verification
    # turn can tell the model WHICH examples broke, not just how many.
    unentailed_positive_atoms: List[str] = field(default_factory=list)
    spurious_negative_atoms:   List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        from dataclasses import asdict
        return asdict(self)


def evaluate_generalization(
    framework: ABAFramework,
    split: SplitProblem,
    domain: Optional[List[str]] = None,
    timeout: int = 30,
) -> GeneralizationResult:
    """
    Evaluate a learned framework on both the training and held-out test sets.
    """
    dom = domain or split.train.get_domain()
    train_pos = split.train.positive
    train_neg = split.train.negative

    res = GeneralizationResult(
        n_train_pos=len(train_pos),
        n_train_neg=len(train_neg),
        n_test_pos=len(split.test_positive),
        n_test_neg=len(split.test_negative),
    )

    # ── Fit on training examples (jointly) ──────────────────────────────────
    res.fit_valid, _, _ = check_brave_entailment(
        framework, train_pos, train_neg, dom, timeout
    )

    # ── Structured error profile on the training set (M9) ───────────────────
    for e in train_pos:
        ok, _, _ = check_brave_entailment(framework, [e], [], dom, timeout)
        if not ok:
            res.unentailed_positives += 1
            res.unentailed_positive_atoms.append(e)
    for e in train_neg:
        ok, _, _ = check_brave_entailment(framework, [], [e], dom, timeout)
        if not ok:                       # ':- e' unsat ⟺ e entailed
            res.spurious_negatives += 1
            res.spurious_negative_atoms.append(e)

    # ── Generalisation ───────────────────────────────────────────────────────
    # HEADLINE CHECK (Definition 1 of De Angelis et al. 2024, on the FULL
    # problem): gen_valid holds iff the framework admits ONE stable extension
    # accepting ALL original examples (train + held-out positives) and NONE of
    # the original negatives (train + held-out) — a single joint ASP check.
    # A per-example check would be wrong twice over: held-out positives could
    # be accepted in DIFFERENT extensions, and ":- e" alone only asks whether
    # SOME extension avoids e, which is near-vacuous on multi-extension
    # frameworks. gen_valid == "the framework solves the full learning problem
    # the symbolic algorithm solves".
    res.gen_valid, _, _ = check_brave_entailment(
        framework,
        train_pos + split.test_positive,
        train_neg + split.test_negative,
        dom, timeout,
    )

    # DIAGNOSTIC per-example score, read off ONE witness extension of the
    # training problem. Checking each held-out example in isolation instead
    # asks "does SOME extension get this right", which is near-vacuous for a
    # negative on a multi-extension framework and made this score routinely
    # exceed fit.
    witness = witness_extension(framework, train_pos, train_neg, dom, timeout)
    if witness is not None:
        res.test_pos_correct = sum(1 for e in split.test_positive
                                   if _norm(e) in witness)
        res.test_neg_correct = sum(1 for e in split.test_negative
                                   if _norm(e) not in witness)

    n_test = res.n_test_pos + res.n_test_neg
    if n_test > 0:
        res.generalization_score = (
            (res.test_pos_correct + res.test_neg_correct) / n_test
        )
    else:
        # No held-out set (problem too small): score falls back to fit
        res.generalization_score = 1.0 if res.fit_valid else 0.0

    # STRICT CHECK: is each held-out label forced, or merely achievable?
    if n_test > 0:
        status = conditioned_status(
            framework, train_pos, train_neg,
            split.test_positive + split.test_negative, dom, timeout,
        )
        res.n_free_heldout = sum(1 for v in status.values() if v == "FREE")
        determined_ok = (
            sum(1 for e in split.test_positive if status.get(e) == "ALWAYS")
            + sum(1 for e in split.test_negative if status.get(e) == "NEVER")
        )
        res.determinacy_score = determined_ok / n_test
        res.gen_determined = res.fit_valid and determined_ok == n_test
    else:
        res.determinacy_score = 1.0 if res.fit_valid else 0.0
        res.gen_determined = res.fit_valid

    res.overfit_gap = (1.0 if res.fit_valid else 0.0) - res.generalization_score
    res.is_degenerate = is_degenerate_solution(framework, train_pos)
    res.is_intensional = is_intensional_strict(framework)

    return res


# ──────────────────────────────────────────────────────────────────────────────
# Semantic comparison with a reference solution (M5)
# ──────────────────────────────────────────────────────────────────────────────

def semantic_equivalence(
    framework_a: ABAFramework,
    framework_b: ABAFramework,
    target_predicate: str,
    domain: List[str],
    timeout: int = 30,
) -> Tuple[bool, float]:
    """
    Two frameworks are semantically equivalent (w.r.t. a target predicate) if
    they bravely entail the same atoms target(c) for every constant c in the
    domain. Far more meaningful than exact-string comparison.

    Returns (equivalent, agreement_fraction).
    """
    agree = 0
    total = 0
    for c in domain:
        atom = f"{target_predicate}({c})"
        a_entails, _, _ = check_brave_entailment(framework_a, [atom], [], domain, timeout)
        b_entails, _, _ = check_brave_entailment(framework_b, [atom], [], domain, timeout)
        total += 1
        if a_entails == b_entails:
            agree += 1
    frac = agree / total if total else 1.0
    return (agree == total), frac
