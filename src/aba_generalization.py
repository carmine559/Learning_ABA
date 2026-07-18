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
from src.aba_validator import check_brave_entailment


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
    True if the rule head or body mentions any individual constant
    (a lowercase atom that is not a predicate symbol or keyword).
    A genuinely intensional rule contains only variables.
    """
    # Explicit equality X = const
    for atom in rule.body:
        if re.search(r'\b[A-Z]\w*\s*=\s*[a-z]\w*', atom):
            return True
    # Constant appearing as a predicate argument, e.g. flies(tweety)
    for token in [rule.head, *rule.body]:
        # arguments inside parentheses
        for arg_group in re.findall(r'\(([^)]*)\)', token):
            for arg in arg_group.split(','):
                arg = arg.strip()
                if arg and arg[0].islower() and arg not in _KEYWORDS:
                    return True
    return False


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
            genuinely new predicates (e.g. contraries of new assumptions)
            are unrestricted;
      (iv)  the contrary of every BACKGROUND assumption must be unchanged;
      flatness: no assumption predicate (old or new) may occur as a rule head;
      freshness: a NEW assumption's predicate must not already occur in the
            background language (the paper introduces new assumption symbols,
            or reuses EXISTING assumptions - it never repurposes background
            predicates as assumptions).
    """
    viol: List[str] = []

    # Background language: predicates of rules (heads + bodies), assumptions,
    # and contraries.
    bg_lang: set = set()
    for r in background.rules:
        for atom in [r.head, *r.body]:
            p = _pred_of(atom)
            if p:
                bg_lang.add(p)
    for a in background.assumptions:
        p = _pred_of(a)
        if p:
            bg_lang.add(p)
    for c in background.contraries.values():
        p = _pred_of(c)
        if p:
            bg_lang.add(p)

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
        if p and p in bg_lang:
            viol.append(f"new assumption predicate '{p}' already occurs in "
                        f"the background language")

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

    # Derived
    generalization_score: float = 0.0       # fraction of test examples correct
    overfit_gap:          float = 0.0       # fit (1/0) − gen_score
    is_degenerate:        bool  = False
    is_intensional:       bool  = False

    # Structured error profile (M9)
    unentailed_positives:   int = 0         # train positives NOT entailed
    spurious_negatives:     int = 0         # train negatives wrongly entailed

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
    for e in train_neg:
        ok, _, _ = check_brave_entailment(framework, [], [e], dom, timeout)
        if not ok:                       # ':- e' unsat ⟺ e entailed
            res.spurious_negatives += 1

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

    # DIAGNOSTIC per-example score on the held-out set only (each example
    # checked in isolation; brave per example). Used for the graded
    # generalization_score and error localisation, NOT for validity.
    for e in split.test_positive:
        ok, _, _ = check_brave_entailment(framework, [e], [], dom, timeout)
        if ok:
            res.test_pos_correct += 1
    for e in split.test_negative:
        ok, _, _ = check_brave_entailment(framework, [], [e], dom, timeout)
        if ok:                           # correctly NOT entailed
            res.test_neg_correct += 1

    n_test = res.n_test_pos + res.n_test_neg
    if n_test > 0:
        res.generalization_score = (
            (res.test_pos_correct + res.test_neg_correct) / n_test
        )
    else:
        # No held-out set (problem too small): score falls back to fit
        res.generalization_score = 1.0 if res.fit_valid else 0.0

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
