"""Definition-1 side conditions and intensionality of a learnt framework."""
from __future__ import annotations
import re
from typing import List, Optional

from src.aba_types import Rule, ABAFramework


def rule_contains_constant(rule: Rule) -> bool:
    """
    True if the rule head or body mentions any individual constant — both the
    normalised form ``p(X) :- X = c`` and a bare ground fact ``p(c).``.
    A genuinely intensional rule contains only variables.

    Single implementation, shared with ``Rule.is_intensional`` so the two
    checks cannot drift apart.
    """
    return rule.contains_constant()


def is_intensional_strict(framework: ABAFramework) -> bool:
    """
    Strict intensionality: NO new rule mentions any individual constant.
    Stricter than an equality-only check.
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


_VAR_RE = re.compile(r'\b[A-Z_]\w*\b')
_CMP_RE = re.compile(r'^([^()]+?)\s*(!=|<=|>=|=|<|>)\s*([^()]+)$')


def _unsafe_vars(rule) -> List[str]:
    """Variables of `rule` that Clingo cannot bind: none of its positive atoms
    holds them and no `=` chain ties them to a bound term ('_' is anonymous)."""
    vars_of = lambda t: set(_VAR_RE.findall(t)) - {"_"}
    bound, eqs = set(), []
    for b in rule.body:
        b = b.strip()
        m = _CMP_RE.match(b)
        if m:
            if m.group(2) == "=":
                eqs.append((vars_of(m.group(1)), vars_of(m.group(3)), m.group(1).strip(),
                            m.group(3).strip()))
        elif not b.startswith("not "):
            bound |= vars_of(b)
    grew = True
    while grew:                                     # X = t binds X once t is bound
        grew = False
        for lv, rv, lt, rt in eqs:
            for var, term, other in ((lt, rv, lv), (rt, lv, rv)):
                if var in other and len(other) == 1 and term <= bound and var not in bound:
                    bound.add(var)
                    grew = True
    return sorted(vars_of(" ".join([rule.head, *rule.body])) - bound)


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
            even though the parser files it under "NEW ASSUMPTIONS";
      learnability: nor may it be learnable. Definition 1 requires
            T ∩ pred(A) = ∅, and examples are non-assumptions (p. 3447); the
            learnt framework keeps both, or declaring the positive examples
            assumptions would be a solution with no rule learnt.
      safety: every variable of a NEW rule occurs in a positive body atom or
            an equality to a constant; Clingo cannot ground the ASP encoding
            (Definition 2(a)) of a rule that breaks this.
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
        free = _unsafe_vars(r)
        if free:
            viol.append(f"unsafe rule: {', '.join(free)} not bound in the body "
                        f"of '{r.to_prolog()}'")

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
        elif p and p in learn:
            viol.append(f"new assumption predicate '{p}' is learnable "
                        f"(Definition 1: T and the assumptions are disjoint)")

    return viol
