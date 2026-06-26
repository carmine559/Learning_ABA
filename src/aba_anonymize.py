"""
aba_anonymize.py
Rename every predicate and constant symbol in a learning problem to abstract,
semantically empty names  (p, q, r, ... and a, b, c, ...).

WHY
---
An LLM carries vast world knowledge.  When a problem talks about `flies`,
`penguin`, `quaker` or `republican`, the model can:
  * HALLUCINATE — assert facts it "knows" (penguins don't fly) that were never
    given in the ABA framework, and
  * LEAK external knowledge — let priors about the concepts infect the
    derivation, instead of reasoning purely from the supplied rules and examples.

Anonymisation removes the semantic anchors.  `flies(tweety)` becomes `p(a)`,
`penguin(X)` becomes `q(X)`, and the model has nothing to fall back on but the
*structure* of the rules.  This isolates genuine logical reasoning from
concept-pattern-matching.

SOUNDNESS
---------
Renaming is a bijection on symbols, and both ASP-ABAlearnB (the symbolic solver)
and Clingo (the validator) are purely syntactic — so the anonymised problem is
ISOMORPHIC to the original: the symbolic solve succeeds on exactly the same
problems and produces structurally identical solutions.  Only the LLM's verdict
can change.  `verify_invariance()` checks this.

USAGE
-----
    anon_problem, name_map = anonymize_problem(problem)            # letters
    anon_problem, name_map = anonymize_problem(problem, scheme="indexed")
    original_fw = deanonymize_framework(learned_fw, name_map)      # for reporting
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

from src.aba_types import Rule, ABAFramework, LearningProblem


# Predicates and the equality / domain machinery that must NOT be renamed.
RESERVED_PREDS = {"dom", "not", "true", "false"}

# Disjoint alphabets so a predicate letter never collides with a constant letter
# (keeps  p(a) :- q(a)  unambiguous).
PRED_LETTERS  = "pqrstuvw"            # 8
CONST_LETTERS = "abcdefghijklmno"     # 15

_ATOM_RE = re.compile(r'^([a-z]\w*)\s*(?:\((.*)\))?$')
_EQ_RE   = re.compile(r'^(\w+)\s*=\s*(\w+)$')


# ──────────────────────────────────────────────────────────────────────────────
# Name map
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class NameMap:
    """Bijective renaming of predicate and constant symbols (original -> anon)."""
    pred_map:  Dict[str, str] = field(default_factory=dict)
    const_map: Dict[str, str] = field(default_factory=dict)

    def inverse(self) -> "NameMap":
        return NameMap(
            pred_map={v: k for k, v in self.pred_map.items()},
            const_map={v: k for k, v in self.const_map.items()},
        )

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        return {"pred_map": dict(self.pred_map), "const_map": dict(self.const_map)}


def _gen_name(scheme: str, kind: str, i: int) -> str:
    """i-th abstract name for `kind` in {'pred','const'} under `scheme`."""
    if scheme == "indexed":
        return (f"p{i}" if kind == "pred" else f"c{i}")
    # "letters"
    letters = PRED_LETTERS if kind == "pred" else CONST_LETTERS
    base = letters[i % len(letters)]
    grp = i // len(letters)
    return base if grp == 0 else f"{base}{grp}"


# ──────────────────────────────────────────────────────────────────────────────
# Atom-level rewriting
# ──────────────────────────────────────────────────────────────────────────────

def _split_args(s: str) -> List[str]:
    return [a.strip() for a in s.split(",") if a.strip()]


def rewrite_atom(atom: str, nm: NameMap) -> str:
    """Rewrite one atom string under the name map.

    Handles ordinary atoms `pred(args)` / `pred`, equality literals `X = c`,
    and leaves variables (uppercase), numbers and reserved predicates intact.
    """
    atom = atom.strip()
    if not atom:
        return atom

    m = _EQ_RE.match(atom)
    if m:
        lhs, rhs = m.group(1), m.group(2)
        lhs = nm.const_map.get(lhs, lhs) if lhs[:1].islower() else lhs
        rhs = nm.const_map.get(rhs, rhs) if rhs[:1].islower() else rhs
        return f"{lhs} = {rhs}"

    m = _ATOM_RE.match(atom)
    if not m:
        return atom
    pred, args = m.group(1), m.group(2)
    new_pred = pred if pred in RESERVED_PREDS else nm.pred_map.get(pred, pred)
    if args is None:
        return new_pred
    new_args = []
    for a in _split_args(args):
        if a[:1].islower():                       # constant
            new_args.append(nm.const_map.get(a, a))
        else:                                     # variable / number
            new_args.append(a)
    return f"{new_pred}({', '.join(new_args)})"


def rewrite_rule(rule: Rule, nm: NameMap) -> Rule:
    return Rule(head=rewrite_atom(rule.head, nm),
                body=[rewrite_atom(b, nm) for b in rule.body])


def rewrite_framework(fw: ABAFramework, nm: NameMap) -> ABAFramework:
    return ABAFramework(
        rules=[rewrite_rule(r, nm) for r in fw.rules],
        assumptions=[rewrite_atom(a, nm) for a in fw.assumptions],
        contraries={rewrite_atom(k, nm): rewrite_atom(v, nm)
                    for k, v in fw.contraries.items()},
        new_rules=[rewrite_rule(r, nm) for r in fw.new_rules],
        new_assumptions=[rewrite_atom(a, nm) for a in fw.new_assumptions],
    )


# ──────────────────────────────────────────────────────────────────────────────
# Symbol collection + problem anonymisation
# ──────────────────────────────────────────────────────────────────────────────

def _scan_atom(atom: str, preds: List[str], consts: List[str]) -> None:
    atom = atom.strip()
    m = _EQ_RE.match(atom)
    if m:
        for x in m.groups():
            if x[:1].islower() and x not in consts:
                consts.append(x)
        return
    m = _ATOM_RE.match(atom)
    if not m:
        return
    pred, args = m.group(1), m.group(2)
    if pred not in RESERVED_PREDS and pred not in preds:
        preds.append(pred)
    if args:
        for a in _split_args(args):
            if a[:1].islower() and a not in consts:
                consts.append(a)


def collect_symbols(problem: LearningProblem) -> Tuple[List[str], List[str]]:
    """Collect, in stable first-appearance order, all predicate and constant
    symbols across the whole problem (background, examples, learnable, domain)."""
    preds: List[str] = []
    consts: List[str] = []
    bg = problem.background
    for r in bg.rules:
        _scan_atom(r.head, preds, consts)
        for b in r.body:
            _scan_atom(b, preds, consts)
    for a in bg.assumptions:
        _scan_atom(a, preds, consts)
    for k, v in bg.contraries.items():
        _scan_atom(k, preds, consts)
        _scan_atom(v, preds, consts)
    for e in list(problem.positive) + list(problem.negative):
        _scan_atom(e, preds, consts)
    for p in problem.learnable:                   # bare predicate names
        if p not in RESERVED_PREDS and p not in preds:
            preds.append(p)
    for c in problem.get_domain():
        if c[:1].islower() and c not in consts:
            consts.append(c)
    return preds, consts


def build_name_map(
    preds: List[str],
    consts: List[str],
    scheme: str = "letters",
    anonymize_constants: bool = True,
) -> NameMap:
    pmap = {p: _gen_name(scheme, "pred", i) for i, p in enumerate(preds)}
    cmap = ({c: _gen_name(scheme, "const", i) for i, c in enumerate(consts)}
            if anonymize_constants else {})
    return NameMap(pred_map=pmap, const_map=cmap)


def anonymize_problem(
    problem: LearningProblem,
    scheme: str = "letters",
    anonymize_constants: bool = True,
    name_map: Optional[NameMap] = None,
) -> Tuple[LearningProblem, NameMap]:
    """Return an anonymised copy of `problem` plus the name map used.

    scheme: "letters" -> p,q,r,... / a,b,c,...   "indexed" -> p0,p1,... / c0,c1,...
    Pass an existing `name_map` to reuse one mapping across several problems
    (e.g. to anonymise a shared few-shot example consistently).
    """
    if name_map is None:
        preds, consts = collect_symbols(problem)
        name_map = build_name_map(preds, consts, scheme, anonymize_constants)
    nm = name_map

    new_bg = rewrite_framework(problem.background, nm)
    new_problem = LearningProblem(
        background=new_bg,
        positive=[rewrite_atom(e, nm) for e in problem.positive],
        negative=[rewrite_atom(e, nm) for e in problem.negative],
        learnable=[nm.pred_map.get(p, p) for p in problem.learnable],
        domain=[nm.const_map.get(c, c) for c in problem.get_domain()],
        problem_id=(problem.problem_id + "_anon") if problem.problem_id else "anon",
    )
    return new_problem, nm


# ──────────────────────────────────────────────────────────────────────────────
# De-anonymisation (for human-readable reporting)
# ──────────────────────────────────────────────────────────────────────────────

def deanonymize_atom(atom: str, nm: NameMap) -> str:
    """Map an anonymised atom back to original names where possible.

    Invented symbols not present in the map (e.g. assumptions the solver/LLM
    created, like `normal_p` or `alpha`) are left unchanged.
    """
    return rewrite_atom(atom, nm.inverse())


def deanonymize_framework(fw: ABAFramework, nm: NameMap) -> ABAFramework:
    return rewrite_framework(fw, nm.inverse())


# ──────────────────────────────────────────────────────────────────────────────
# Soundness check
# ──────────────────────────────────────────────────────────────────────────────

def verify_invariance(problem: LearningProblem, scheme: str = "letters") -> bool:
    """Check that anonymisation preserves symbolic solvability (isomorphism).

    Returns True iff ASP-ABAlearnB succeeds on the original problem exactly when
    it succeeds on the anonymised one.  A False here means the rewrite broke the
    structure — a bug, not an experimental result.
    """
    from src.aba_algorithm import solve_aba_learning

    anon, _ = anonymize_problem(problem, scheme=scheme)
    sol_o, tr_o = solve_aba_learning(problem)
    sol_a, tr_a = solve_aba_learning(anon)
    ok_o = sol_o is not None and tr_o.success
    ok_a = sol_a is not None and tr_a.success
    return ok_o == ok_a
