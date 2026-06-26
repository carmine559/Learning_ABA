"""
aba_graded.py
A graded-argumentation layer that brings ArgLLM-style gradual semantics
(Freedman et al., AAAI 2025) into the ABA-learning project.

MOTIVATION
----------
The ABA-learning pipeline produces a *symbolic structure* (rules, assumptions,
contraries) that Clingo evaluates with crisp stable-extension semantics: an atom
is bravely entailed or it is not.  ArgLLMs instead reason over a *Quantitative
Bipolar Argumentation Framework* (QBAF) with continuous intrinsic strengths and
a deterministic gradual semantics (DF-QuAD), yielding a real-valued strength in
[0, 1] together with a faithful, contestable explanation.

This module fuses the two WITHOUT contradiction by a single design rule:

    The LLM's plastic, uncertain judgement enters ONLY through the base scores
    of the defeasible elements (the ABA assumptions).  Everything else — the
    structure of arguments and attacks, and their resolution — is handled by a
    deterministic gradual semantics.

We therefore obtain two readings of the SAME learned framework:
  * crisp   : Clingo brave entailment (binary)        -> aba_validator
  * graded  : DF-QuAD strength in [0, 1] (continuous)  -> this module

The graded reading adds three things the crisp one cannot give:
  1. a confidence/robustness signal for each entailment,
  2. a faithful explanation (the QBAF tree the verdict is computed from),
  3. contestability (change a base score, get a predictable change in strength).

The base scores can come from three sources (StrengthSource):
  * UNIFORM        : every assumption = 0.5  (ArgLLMs' "0.5 Base Arg" baseline)
  * SAMPLE_FREQ    : frequency of the assumption across the k LLM samples
                     (uses the model's own distribution; no extra prompting)
  * LLM_ELICITED   : a dedicated LLM call scores each assumption (ArgLLMs' E)
"""
from __future__ import annotations
import re
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Tuple, Set

from src.aba_types import Rule, ABAFramework
from src.aba_validator import check_brave_entailment


# ──────────────────────────────────────────────────────────────────────────────
# DF-QuAD gradual semantics  (Rago et al. 2016; as used by ArgLLMs)
# ──────────────────────────────────────────────────────────────────────────────
#
# For an argument a with base score v0, attacker strengths v1..vn and supporter
# strengths v'1..v'm:
#     sigma(a) = C(v0, F(v1..vn), F(v'1..v'm))
# where
#     F([])      = 0
#     F(v1..vn)  = 1 - PROD_i (1 - vi)              # probabilistic OR
#     C(v0, va, vs):
#         if va == vs:  v0
#         if va >  vs:  v0 - v0 * |vs - va|         # net attack weakens
#         if va <  vs:  v0 + (1 - v0) * |vs - va|   # net support strengthens
# The semantics is deterministic and closed-form.

def df_quad_F(strengths: List[float]) -> float:
    """Aggregate a list of attacker (or supporter) strengths."""
    if not strengths:
        return 0.0
    prod = 1.0
    for v in strengths:
        prod *= (1.0 - v)
    return 1.0 - prod


def df_quad_C(v0: float, va: float, vs: float) -> float:
    """Combine base score v0 with aggregated attack va and support vs."""
    if abs(va - vs) < 1e-12:
        return v0
    if va > vs:
        return v0 - v0 * (va - vs)
    return v0 + (1.0 - v0) * (vs - va)


# ──────────────────────────────────────────────────────────────────────────────
# QBAF node  (a restricted QBAF for a claim is a tree rooted at that claim)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class QBAFNode:
    """A node in the argument tree built for one query atom."""
    atom:        str
    base_score:  float = 1.0
    kind:        str = "derived"          # "fact" | "assumption" | "derived"
    supporters:  List["QBAFNode"] = field(default_factory=list)
    attackers:   List["QBAFNode"] = field(default_factory=list)
    strength:    float = 0.0              # filled by evaluate()

    def evaluate(self) -> float:
        """Bottom-up DF-QuAD evaluation of this subtree."""
        sup = [s.evaluate() for s in self.supporters]
        att = [a.evaluate() for a in self.attackers]
        self.strength = df_quad_C(self.base_score, df_quad_F(att), df_quad_F(sup))
        return self.strength

    def to_text(self, indent: int = 0) -> str:
        pad = "  " * indent
        tag = {"fact": "[fact]", "assumption": "[asm]", "derived": ""}[self.kind]
        line = f"{pad}{self.atom} {tag} base={self.base_score:.2f} σ={self.strength:.2f}"
        out = [line]
        for s in self.supporters:
            out.append(pad + "  +support:")
            out.append(s.to_text(indent + 2))
        for a in self.attackers:
            out.append(pad + "  -attack:")
            out.append(a.to_text(indent + 2))
        return "\n".join(out)


# ──────────────────────────────────────────────────────────────────────────────
# Base-score sources
# ──────────────────────────────────────────────────────────────────────────────

class StrengthSource(Enum):
    UNIFORM      = "uniform"        # all assumptions = 0.5
    SAMPLE_FREQ  = "sample_freq"    # frequency across k LLM samples
    LLM_ELICITED = "llm_elicited"   # dedicated LLM scoring call


def assumption_scores_from_samples(
    sample_frameworks: List[ABAFramework],
) -> Dict[str, float]:
    """
    SAMPLE_FREQ source: the base score of an assumption predicate is the
    fraction of k sampled frameworks in which it appears. Uses the model's
    own distribution as a confidence signal — no extra prompting.
    """
    if not sample_frameworks:
        return {}
    counts: Dict[str, int] = {}
    for fw in sample_frameworks:
        present = set()
        for a in fw.assumptions:
            present.add(_pred(a))
        for p in present:
            counts[p] = counts.get(p, 0) + 1
    n = len(sample_frameworks)
    return {p: c / n for p, c in counts.items()}


def assumption_scores_from_llm(
    framework: ABAFramework,
    backend,
    context: str = "",
    domain: Optional[List[str]] = None,
) -> Dict[str, float]:
    """
    LLM_ELICITED source: ask the model, for each assumption, how confident it is
    that the assumption holds by default.

    Compared with the original ArgLLMs Figure-4 prompt, this version is grounded
    in the actual problem data:
      1. It pre-computes (via Clingo) which domain constants have the contrary
         already derivable from the background — these are the "exceptions".
      2. It shows the LLM the full rules, the exception distribution, and the
         data-driven base rate, giving it concrete numbers to reason from.
      3. The fallback (if the LLM returns garbage) is the base rate, not 0.5.
    """
    from src.aba_validator import check_brave_entailment as _brave

    # Resolve domain from explicit argument or by scanning ground facts in rules
    dom: List[str] = list(domain) if domain else []
    if not dom:
        seen: Dict[str, int] = {}
        for r in framework.rules:
            if not r.body:
                m = re.search(r'\(([a-z]\w*)\)', r.head)
                if m and m.group(1) not in seen:
                    seen[m.group(1)] = 1
                    dom.append(m.group(1))

    scores: Dict[str, float] = {}
    for asm in framework.assumptions:
        pred = _pred(asm)
        contrary_tmpl = framework.contraries.get(asm, f"c_{asm}")

        # Pre-compute which constants already have the contrary derivable
        # (i.e., the assumption is attacked there) using the symbolic framework.
        fire_consts: List[str] = []
        clear_consts: List[str] = []
        for c in dom:
            c_atom = re.sub(r'\b[A-Z]\w*\b', c, contrary_tmpl)
            try:
                ok, _, _ = _brave(framework, [c_atom], [], dom)
                (fire_consts if ok else clear_consts).append(c)
            except Exception:
                clear_consts.append(c)

        n_total = len(dom)
        n_clear = len(clear_consts)
        # Data-driven base rate: fraction of constants where assumption is unattacked
        base_rate_pct = round(100 * n_clear / n_total) if n_total > 0 else 50

        rules_text = "\n".join(f"  {r.to_prolog()}" for r in framework.rules)

        prompt = (
            "You are estimating the prior strength of a defeasible assumption "
            "in an argumentation framework.\n\n"
            f"PROBLEM: {context}\n\n"
            f"BACKGROUND RULES:\n{rules_text}\n\n"
            f"ASSUMPTION: {asm}\n"
            f"  Holds by default for every domain constant UNLESS its contrary\n"
            f"  '{contrary_tmpl}' is derived from the background.\n\n"
            f"DOMAIN ANALYSIS — {n_total} constants: {', '.join(dom) or 'unknown'}\n"
            f"  Contrary '{_pred(contrary_tmpl)}' is already derivable (exception "
            f"applies) for: {', '.join(fire_consts) if fire_consts else 'none'}\n"
            f"  Assumption holds unattacked for: "
            f"{', '.join(clear_consts) if clear_consts else 'none'}\n\n"
            f"Observed base rate: {n_clear} / {n_total} = {base_rate_pct}% of "
            f"constants have the assumption unattacked.\n\n"
            "QUESTION:\n"
            f"What prior probability (0-100) should '{asm}' carry for a TYPICAL "
            "or NEW domain constant, BEFORE any attacks are applied?\n"
            "Consider: (a) the observed base rate above, (b) whether the background "
            "rules suggest the exception is structurally common or rare.\n"
            "Answer with ONLY an integer 0-100."
        )
        try:
            resp = backend.generate(prompt, temperature=0.0, max_tokens=16)
            m = re.search(r'\d{1,3}', resp.text)
            val = min(100, max(0, int(m.group(0)))) / 100.0 if m else base_rate_pct / 100.0
        except Exception:
            val = base_rate_pct / 100.0
        scores[pred] = val
    return scores


# ──────────────────────────────────────────────────────────────────────────────
# ABA → QBAF construction
# ──────────────────────────────────────────────────────────────────────────────

def _pred(atom: str) -> str:
    m = re.match(r'^([a-z]\w*)', atom.strip())
    return m.group(1) if m else atom.strip()


def _args(atom: str) -> str:
    m = re.search(r'\(([^)]*)\)', atom)
    return m.group(1) if m else ""


def _ground_rule(rule: Rule, const: str) -> Tuple[str, List[str]]:
    """Instantiate a single-variable rule's head and body with `const`.

    Rules from the RoLe phase have the form  p(X) :- X = c_k.  — a ground fact
    encoded with an equality guard.  If the query constant differs from c_k we
    must NOT fire this rule.  Without this check, substituting the query const
    into the head makes the head-equality check always pass, causing every
    equality-constrained rule to contribute an always-fires supporter (base=1.0)
    to every query, collapsing all σ values to 1.0.
    """
    for b in rule.body:
        m = re.match(r'^[A-Z]\w*\s*=\s*([a-z]\w*)', b.strip())
        if m:
            if m.group(1) != const:
                return ("", [])   # sentinel: head will never match the query atom
            break   # matching constant — proceed with normal grounding

    def subst(s: str) -> str:
        return re.sub(r'\b[A-Z]\w*\b', const, s)
    return subst(rule.head), [subst(b) for b in rule.body
                              if not re.match(r'^[A-Z]\w*\s*=', b.strip())]


class GradedABA:
    """
    Builds and evaluates a QBAF for a query atom over a learned ABA framework.

    The argument tree is grown from the query down to facts and assumptions:
      * a derived atom is SUPPORTED by the bodies of rules that derive it;
      * an assumption is a leaf whose base score is its (LLM-derived) strength,
        ATTACKED by the argument for its contrary (if derivable);
      * a fact is a leaf with base score 1.0.
    Bounded depth + visited-set prevents infinite recursion on cyclic programs.
    """

    def __init__(
        self,
        framework: ABAFramework,
        domain: List[str],
        assumption_scores: Optional[Dict[str, float]] = None,
        default_score: float = 0.5,
        max_depth: int = 8,
    ):
        self.fw = framework
        self.domain = domain
        self.scores = assumption_scores or {}
        self.default_score = default_score
        self.max_depth = max_depth
        # Pre-index facts and rules by head predicate for speed
        self._facts: Set[str] = set()
        self._rules_by_pred: Dict[str, List[Rule]] = {}
        for r in framework.rules:
            if not r.body and _args(r.head) and _args(r.head)[0].islower():
                self._facts.add(r.head.strip())
            self._rules_by_pred.setdefault(_pred(r.head), []).append(r)
        self._asm_preds = {_pred(a) for a in framework.assumptions}
        self._contrary_of = {                       # pred(assumption) -> contrary atom
            _pred(a): framework.contraries.get(a, f"c_{a}")
            for a in framework.assumptions
        }

    # ── strength lookup ──────────────────────────────────────────────────────
    def _asm_base(self, atom: str) -> float:
        return self.scores.get(_pred(atom), self.default_score)

    # ── tree construction ────────────────────────────────────────────────────
    def build(self, query: str) -> QBAFNode:
        return self._build(query.strip(), depth=0, visiting=set())

    def _build(self, atom: str, depth: int, visiting: Set[str]) -> QBAFNode:
        atom = atom.strip()
        const = _args(atom)

        # Fact leaf
        if atom in self._facts:
            return QBAFNode(atom, base_score=1.0, kind="fact")

        # Assumption leaf (attacked by its contrary if derivable)
        if _pred(atom) in self._asm_preds:
            node = QBAFNode(atom, base_score=self._asm_base(atom),
                            kind="assumption")
            contrary = self._contrary_of[_pred(atom)]
            contrary_atom = re.sub(r'\b[A-Z]\w*\b', const, contrary) if const else contrary
            if (depth < self.max_depth and contrary_atom not in visiting
                    and self._derivable(contrary_atom)):
                node.attackers.append(
                    self._build(contrary_atom, depth + 1, visiting | {atom})
                )
            return node

        # Derived atom: TRUE only if some rule body fires. Model it as a node
        # with base score 0 whose SUPPORTERS are the rule bodies; DF-QuAD's F
        # gives probabilistic-OR over the alternative derivations. A derived
        # atom has no intrinsic strength of its own, hence base 0.
        node = QBAFNode(atom, base_score=0.0, kind="derived")
        if depth >= self.max_depth or atom in visiting:
            return node

        for rule in self._rules_by_pred.get(_pred(atom), []):
            head_g, body_g = _ground_rule(rule, const) if const else (rule.head, rule.body)
            if head_g.strip() != atom:
                continue
            body_literals = [b for b in body_g if _pred(b) != "dom"]
            if body_literals:
                body_nodes = [
                    self._build(b, depth + 1, visiting | {atom})
                    for b in body_literals
                ]
                # A rule body is a CONJUNCTION -> aggregate by product.
                conj = QBAFNode(f"body_of({atom})", base_score=1.0, kind="derived")
                conj.supporters = body_nodes
                conj.evaluate = _product_eval(conj)  # type: ignore
                node.supporters.append(conj)
            else:
                # Empty body (after dropping dom/equalities) -> always fires.
                node.supporters.append(
                    QBAFNode(f"{atom}<-rule", base_score=1.0, kind="fact")
                )
        return node

    def _derivable(self, atom: str) -> bool:
        """Crisp check: is `atom` bravely entailed? (delegates to Clingo)."""
        ok, _, _ = check_brave_entailment(self.fw, [atom], [], self.domain)
        return ok

    # ── public evaluation ────────────────────────────────────────────────────
    def graded_entailment(self, query: str) -> Tuple[float, QBAFNode]:
        """Return (strength in [0,1], explanation tree) for the query."""
        tree = self.build(query)
        strength = tree.evaluate()
        return strength, tree


def _product_eval(node: QBAFNode):
    """Return an evaluate() that aggregates a rule body as a conjunction (product)."""
    def _ev() -> float:
        if not node.supporters:
            node.strength = 1.0
            return 1.0
        prod = 1.0
        for child in node.supporters:
            prod *= child.evaluate()
        node.strength = prod
        return prod
    return _ev


# ──────────────────────────────────────────────────────────────────────────────
# Contestability  (ArgLLMs Properties 1 & 2)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ContestationResult:
    query:        str
    original:     float
    contested:    float
    intervention: str
    direction_ok: bool      # did strength move in the expected direction?


def contest_base_score(
    framework: ABAFramework,
    domain: List[str],
    query: str,
    assumption_pred: str,
    old_scores: Dict[str, float],
    new_value: float,
) -> ContestationResult:
    """
    Intervene on one assumption's base score and measure the effect on the
    query's strength. Mirrors ArgLLMs' base-score contestability: raising the
    strength of a pro element should not decrease the conclusion's strength.
    """
    g0 = GradedABA(framework, domain, old_scores)
    s0, _ = g0.graded_entailment(query)

    new_scores = dict(old_scores)
    old_value = old_scores.get(assumption_pred, 0.5)
    new_scores[assumption_pred] = new_value

    g1 = GradedABA(framework, domain, new_scores)
    s1, _ = g1.graded_entailment(query)

    raised = new_value > old_value
    # For a pro assumption, raising it should not decrease the conclusion.
    direction_ok = (s1 >= s0 - 1e-9) if raised else (s1 <= s0 + 1e-9)
    return ContestationResult(
        query=query, original=s0, contested=s1,
        intervention=f"{assumption_pred}: {old_value:.2f} -> {new_value:.2f}",
        direction_ok=direction_ok,
    )


# ──────────────────────────────────────────────────────────────────────────────
# Crisp vs. graded comparison  (the analysis the thesis reports)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class GradedReport:
    query:            str
    crisp_entailed:   bool
    graded_strength:  float
    agree:            bool       # crisp(>0.5) matches graded(>0.5)
    explanation:      str


def compare_crisp_vs_graded(
    framework: ABAFramework,
    domain: List[str],
    queries: List[str],
    assumption_scores: Optional[Dict[str, float]] = None,
    threshold: float = 0.5,
) -> List[GradedReport]:
    """
    For each query, report the crisp brave-entailment verdict and the graded
    DF-QuAD strength, and whether they agree under a 0.5 threshold.
    """
    g = GradedABA(framework, domain, assumption_scores)
    reports = []
    for q in queries:
        crisp, _, _ = check_brave_entailment(framework, [q], [], domain)
        strength, tree = g.graded_entailment(q)
        graded_bool = strength > threshold
        reports.append(GradedReport(
            query=q,
            crisp_entailed=crisp,
            graded_strength=round(strength, 3),
            agree=(crisp == graded_bool),
            explanation=tree.to_text(),
        ))
    return reports
