"""
aba_bsaf.py
Correct gradual ABA semantics, following Rapberger, Russo, Rago & Toni,
"On Gradual Semantics for Assumption-Based Argumentation" (KR 2025).

WHY THIS MODULE EXISTS
----------------------
`aba_graded.py` evaluates a per-query ARGUMENT TREE with a depth cap.  That is
(a) the paper's *baseline* (argument/BAF-based, Section 5), and (b) only an
approximation of it, because the depth cap truncates cyclic structures instead
of solving them.  This module implements the paper's actual contribution: the
*assumption-based* gradual semantics computed over the BSAF abstraction with an
iterative strength-evolution fixpoint (Section 4, Figure 1).

THE PIPELINE  (Definitions 3.4, 4.17, 4.18)
-------------------------------------------
    ABAF D = (L, A, R, contrary, tau),  tau : A -> [0,1]

  1. ABSTRACTION   build the BSAF  F_D = (A, R_D, S_D):
       nodes      = ground assumptions
       R_D        = { (E, a) : E |- contrary(a) }   (set-attacks)
       S_D        = { (E, a) : E |- a via rules }   (set-supports, non-flat only)
  2. SET STRENGTH  each set-attacker/-supporter E -> scalar  zeta({s(b):b in E})
  3. AGGREGATE     per assumption a:  w = alpha(attacker-scalars, supporter-scalars)
  4. INFLUENCE     s_{t+1}(a) = iota(tau(a), w)
  5. REPEAT 2-4 until convergence.   sigma(a) = lim_t s(t)_a

  CLAIM STRENGTH (brave reading): for a derivable claim p,
       sigma(p) = max_{E in supp(p)}  beta_Pi({sigma(b) : b in E})
  i.e. the strongest argument for p (Proposition 5.5: beta_Pi is well-behaved).
  Facts have empty support -> product over empty set = 1.0.

MODULAR KERNEL  (Tables 1-3)
----------------------------
  set-aggregation  zeta : {Prod, Min}        (Prop 4.5: only these are sound)
  aggregation      alpha: {Prod (DF-QuAD), Sum (QE)}
  influence        iota : {lin (DF-QuAD), quad (QE)}
  DF-QuAD = (zeta_Pi|zeta_min, alpha_Pi, iota_lin)   <- most robust, the default
  QE      = (zeta,             alpha_Sum, iota_quad)
"""
from __future__ import annotations

import re
import itertools
from dataclasses import dataclass
from typing import List, Dict, Optional, Set, FrozenSet, Callable

from src.aba_types import Rule, ABAFramework


# ──────────────────────────────────────────────────────────────────────────────
# Modular kernel functions  (Tables 1, 2, 3 of the paper)
# ──────────────────────────────────────────────────────────────────────────────

# ---- set-aggregation  zeta(S)  : multiset of assumption strengths -> scalar ----
def zeta_prod(strengths: List[float]) -> float:
    """zeta_Pi: product. zeta_Pi(empty) = 1 (a no-assumption attack is certain)."""
    p = 1.0
    for s in strengths:
        p *= s
    return p


def zeta_min(strengths: List[float]) -> float:
    """zeta_min: weakest link. min(S union {1}); min(empty) = 1."""
    return min(strengths) if strengths else 1.0


# ---- aggregation  alpha(A, S) : attacker scalars, supporter scalars -> w -------
def alpha_prod(attackers: List[float], supporters: List[float]) -> float:
    """alpha_Pi (DF-QuAD):  Prod_a (1-a)  -  Prod_s (1-s)."""
    pa = 1.0
    for a in attackers:
        pa *= (1.0 - a)
    ps = 1.0
    for s in supporters:
        ps *= (1.0 - s)
    return pa - ps


def alpha_sum(attackers: List[float], supporters: List[float]) -> float:
    """alpha_Sum (QE):  Sum(S) - Sum(A)."""
    return sum(supporters) - sum(attackers)


# ---- influence  iota(b, w) : base score, aggregate -> updated strength ---------
def iota_lin(b: float, w: float, k: float = 1.0) -> float:
    """iota^k_lin (DF-QuAD): b + (b/k) min(0,w) + ((1-b)/k) max(0,w)."""
    return b + (b / k) * min(0.0, w) + ((1.0 - b) / k) * max(0.0, w)


def _h(w: float) -> float:
    m = max(0.0, w)
    return (m * m) / (1.0 + m * m)


def iota_quad(b: float, w: float, k: float = 1.0) -> float:
    """iota^k_q (QE): b - b*h(-w/k) + (1-b)*h(w/k).

    The (1-b) coefficient on the positive term is the standard quadratic-energy
    form; the KR-2025 PDF prints it as b*h(w/k), an OCR artefact.
    """
    return b - b * _h(-w / k) + (1.0 - b) * _h(w / k)


@dataclass(frozen=True)
class Kernel:
    """A modular (zeta, alpha, iota) kernel (Definition 4.20)."""
    name:  str
    zeta:  Callable[[List[float]], float]
    alpha: Callable[[List[float], List[float]], float]
    iota:  Callable[[float, float], float]


# The two named semantics from the paper, with both sound set-aggregations.
KERNELS: Dict[str, Kernel] = {
    "dfquad_prod": Kernel("DF-QuAD/Prod", zeta_prod, alpha_prod, iota_lin),
    "dfquad_min":  Kernel("DF-QuAD/Min",  zeta_min,  alpha_prod, iota_lin),
    "qe_prod":     Kernel("QE/Prod",      zeta_prod, alpha_sum,  iota_quad),
    "qe_min":      Kernel("QE/Min",       zeta_min,  alpha_sum,  iota_quad),
}
DEFAULT_KERNEL = "dfquad_prod"


# ──────────────────────────────────────────────────────────────────────────────
# Grounding:  ABA-with-variables  ->  propositional ground ABAF
# ──────────────────────────────────────────────────────────────────────────────

_VAR_RE = re.compile(r'\b[A-Z]\w*\b')
_EQ_RE  = re.compile(r'^([A-Z]\w*)\s*=\s*([a-z]\w*|\d+)$')


def _pred(atom: str) -> str:
    m = re.match(r'^([a-z]\w*)', atom.strip())
    return m.group(1) if m else atom.strip()


def _subst(s: str, binding: Dict[str, str]) -> str:
    return _VAR_RE.sub(lambda m: binding.get(m.group(0), m.group(0)), s)


def _vars(text: str) -> Set[str]:
    return set(_VAR_RE.findall(text))


def _ground_rule(rule: Rule, domain: List[str]) -> List[Rule]:
    """Instantiate one (possibly variabled) rule over the domain.

    Handles the RoLe residual form  p(X) :- X = c.  (binds X=c, drops the
    equality) and drops dom(...) guards.  Returns all ground instances.
    """
    # Separate equality bindings, dom-guards, and ordinary body atoms.
    eq_binding: Dict[str, str] = {}
    real_body: List[str] = []
    for b in rule.body:
        b = b.strip()
        m = _EQ_RE.match(b)
        if m:
            eq_binding[m.group(1)] = m.group(2)
            continue
        if _pred(b) == "dom":
            continue
        real_body.append(b)

    free = (_vars(rule.head) | {v for b in real_body for v in _vars(b)}) - set(eq_binding)
    free = sorted(free)

    instances: List[Rule] = []
    if not free:
        binding = dict(eq_binding)
        head = _subst(rule.head, binding)
        body = [_subst(b, binding) for b in real_body]
        instances.append(Rule(head=head, body=body))
        return instances

    for combo in itertools.product(domain, repeat=len(free)):
        binding = dict(eq_binding)
        binding.update(dict(zip(free, combo)))
        head = _subst(rule.head, binding)
        body = [_subst(b, binding) for b in real_body]
        instances.append(Rule(head=head, body=body))
    return instances


@dataclass
class GroundABAF:
    """A fully ground (propositional) ABAF."""
    rules:        List[Rule]
    assumptions:  List[str]                  # ground assumption atoms
    contraries:   Dict[str, str]             # ground assumption -> ground contrary
    base_scores:  Dict[str, float]           # ground assumption -> tau in [0,1]


def ground_framework(
    fw: ABAFramework,
    domain: List[str],
    assumption_scores: Optional[Dict[str, float]] = None,
    default_score: float = 0.5,
) -> GroundABAF:
    """Ground a (possibly variabled) ABAFramework over `domain`.

    `assumption_scores` may be keyed by ground atom OR by predicate; the ground
    atom is tried first, then the predicate, then `default_score`.
    """
    scores = assumption_scores or {}
    if not domain:
        domain = fw.get_domain()

    ground_rules: List[Rule] = []
    for r in fw.rules:
        ground_rules.extend(_ground_rule(r, domain))

    ground_asms: List[str] = []
    ground_contr: Dict[str, str] = {}
    ground_tau: Dict[str, float] = {}
    seen: Set[str] = set()
    for asm in fw.assumptions:
        contr_tmpl = fw.contraries.get(asm, f"c_{asm}")
        v = _vars(asm)
        bindings = ([{}] if not v
                    else [dict(zip(sorted(v), combo))
                          for combo in itertools.product(domain, repeat=len(v))])
        for binding in bindings:
            ga = _subst(asm, binding)
            if ga in seen:
                continue
            seen.add(ga)
            gc = _subst(contr_tmpl, binding)
            ground_asms.append(ga)
            ground_contr[ga] = gc
            # Explicit None checks: `or` chaining silently turns a legitimate
            # elicited score of 0.0 into the default.
            tau = scores.get(ga)
            if tau is None:
                tau = scores.get(_pred(ga))
            ground_tau[ga] = default_score if tau is None else tau
    return GroundABAF(ground_rules, ground_asms, ground_contr, ground_tau)


# ──────────────────────────────────────────────────────────────────────────────
# Minimal-support fixpoint:  sentence  ->  family of minimal assumption-sets
# ──────────────────────────────────────────────────────────────────────────────

def _add_minimal(family: Set[FrozenSet[str]], candidate: FrozenSet[str]) -> bool:
    """Insert `candidate` into `family` keeping only subset-minimal sets.

    Returns True if the family changed.
    """
    for existing in family:
        if existing <= candidate:          # candidate is dominated -> skip
            return False
    # candidate is minimal: drop any supersets, then add it
    supersets = {e for e in family if candidate < e}
    family -= supersets
    family.add(candidate)
    return True


def compute_supports(
    g: GroundABAF,
    max_set_size: Optional[int] = None,
    cap_per_atom: int = 256,
    max_iters: int = 1000,
) -> Dict[str, Set[FrozenSet[str]]]:
    """Least fixpoint of  supp : sentence -> {minimal assumption-sets deriving it}.

    This is a MONOTONE Horn computation (assumptions are the only "defeasible
    facts"); it always terminates.  Non-monotonicity lives in the attack
    relation, resolved later by the strength fixpoint, not here.

      * an assumption a always has the trivial support {a}
      * a fact (empty body) has the empty support  (derivable from no assumptions)
      * a rule h <- b1..bk contributes, for every choice of supports
        E_i in supp(b_i), the union E_1 u ... u E_k   (conjunction = union)
      * multiple rules for h = disjunction = several supports
    """
    if max_set_size is None:
        max_set_size = len(g.assumptions)

    asms = set(g.assumptions)
    supp: Dict[str, Set[FrozenSet[str]]] = {}
    for a in g.assumptions:
        supp[a] = {frozenset((a,))}

    # Index rules by head for efficiency.
    rules_by_head: Dict[str, List[Rule]] = {}
    for r in g.rules:
        rules_by_head.setdefault(r.head.strip(), []).append(r)

    changed = True
    iters = 0
    while changed and iters < max_iters:
        changed = False
        iters += 1
        for head, rules in rules_by_head.items():
            fam = supp.setdefault(head, set())
            for rule in rules:
                # collect current supports for each body atom
                per_body: List[List[FrozenSet[str]]] = []
                ok = True
                for b in rule.body:
                    b = b.strip()
                    fb = supp.get(b)
                    if not fb:
                        ok = False
                        break
                    per_body.append(list(fb))
                if not ok:
                    continue
                # cartesian product over body atoms; union each combination
                for combo in itertools.product(*per_body) if per_body else [()]:
                    union: FrozenSet[str] = frozenset().union(*combo) if combo else frozenset()
                    if len(union) > max_set_size:
                        continue
                    # An assumption that is also a rule head (non-flat): keep both.
                    if _add_minimal(fam, union):
                        changed = True
            # cap: keep the smallest supports if the family explodes
            if len(fam) > cap_per_atom:
                smallest = sorted(fam, key=len)[:cap_per_atom]
                supp[head] = set(smallest)
    return supp


# ──────────────────────────────────────────────────────────────────────────────
# BSAF construction + strength-evolution fixpoint
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class BSAF:
    """Bipolar set-argumentation framework (Definition 3.3) over assumptions."""
    assumptions: List[str]
    attacks:  Dict[str, List[FrozenSet[str]]]   # a -> list of set-attackers E
    supports: Dict[str, List[FrozenSet[str]]]   # a -> list of set-supporters E
    base:     Dict[str, float]                  # a -> tau(a)


def build_bsaf(g: GroundABAF, supp: Dict[str, Set[FrozenSet[str]]]) -> BSAF:
    """Definition 3.4: R_D = supp(contrary(a)),  S_D = supp(a) \\ {{a}}."""
    attacks:  Dict[str, List[FrozenSet[str]]] = {}
    supports: Dict[str, List[FrozenSet[str]]] = {}
    for a in g.assumptions:
        contrary = g.contraries[a]
        attacks[a] = list(supp.get(contrary, set()))
        sup = supp.get(a, set()) - {frozenset((a,))}   # drop the trivial argument
        supports[a] = list(sup)
    return BSAF(list(g.assumptions), attacks, supports, dict(g.base_scores))


@dataclass
class GradedResult:
    """Outcome of running a gradual ABA semantics."""
    assumption_strength: Dict[str, float]
    converged:           bool
    iterations:          int
    kernel:              str


def run_semantics(
    bsaf: BSAF,
    kernel: str = DEFAULT_KERNEL,
    epsilon: float = 1e-4,
    max_iters: int = 500,
) -> GradedResult:
    """Strength-evolution fixpoint (Definition 4.17).

    s(0)_a   = tau(a)
    s(t+1)_a = iota(tau(a), alpha( [zeta(E) : E in Att(a)],
                                   [zeta(E) : E in Sup(a)] ))
    Stops when max_a |s(t+1)_a - s(t)_a| < epsilon (converged) or at max_iters.
    """
    k = KERNELS[kernel]
    s: Dict[str, float] = dict(bsaf.base)

    converged = False
    it = 0
    for it in range(1, max_iters + 1):
        nxt: Dict[str, float] = {}
        for a in bsaf.assumptions:
            att_scalars = [k.zeta([s[b] for b in E]) for E in bsaf.attacks[a]]
            sup_scalars = [k.zeta([s[b] for b in E]) for E in bsaf.supports[a]]
            w = k.alpha(att_scalars, sup_scalars)
            nxt[a] = k.iota(bsaf.base[a], w)
        delta = max((abs(nxt[a] - s[a]) for a in bsaf.assumptions), default=0.0)
        s = nxt
        if delta < epsilon:
            converged = True
            break
    return GradedResult(s, converged, it, k.name)


# ──────────────────────────────────────────────────────────────────────────────
# Claim strength  (brave reading via the argument base-score beta_Pi)
# ──────────────────────────────────────────────────────────────────────────────

def _arg_strength(E: FrozenSet[str], sigma: Dict[str, float]) -> float:
    """Argument base score beta_Pi(E) = Prod_{b in E} sigma(b)  (Prop 5.5).

    Empty support (derivable from facts) -> product over empty set = 1.0.
    """
    p = 1.0
    for b in E:
        p *= sigma.get(b, 0.0)
    return p


def claim_strength(
    claim: str,
    sigma: Dict[str, float],
    supp: Dict[str, Set[FrozenSet[str]]],
    mode: str = "max",
) -> float:
    """Strength of a (non-assumption) claim from the assumption strengths.

    The paper computes assumption strengths; a claim is derived by one or more
    arguments E in supp(claim), each scored by beta_Pi(E) = Prod sigma(b).  The
    `mode` selects how to combine multiple arguments for the same claim — these
    mirror the sigma* extraction functions of Section 5.2:

      "max"      sigma*_top : credulous. The FAITHFUL reading of BRAVE
                 entailment ("exists an accepted argument").  DEFAULT.
      "min"      sigma*_bot : sceptical (weakest argument).
      "avg"      sigma*_avg : average over arguments.
      "noisy_or" accrual: 1 - Prod_E (1 - beta_Pi(E)).  NOT brave entailment;
                 treats alternative derivations as independent accruing evidence
                 (the DF-QuAD-F behaviour of the old argument-tree module).

    An underivable claim has no support -> 0.0.
    """
    claim = claim.strip()
    fam = supp.get(claim)
    if not fam:
        return 0.0
    scores = [_arg_strength(E, sigma) for E in fam]
    if mode == "max":
        return max(scores)
    if mode == "min":
        return min(scores)
    if mode == "avg":
        return sum(scores) / len(scores)
    if mode == "noisy_or":
        prod = 1.0
        for v in scores:
            prod *= (1.0 - v)
        return 1.0 - prod
    raise ValueError(f"unknown claim mode {mode!r}")


# ──────────────────────────────────────────────────────────────────────────────
# High-level driver  (mirrors aba_graded.GradedABA, but the correct semantics)
# ──────────────────────────────────────────────────────────────────────────────

class GradualABA:
    """Correct, assumption-based gradual ABA semantics over a learned framework.

    Usage:
        g = GradualABA(framework, domain, assumption_scores=scores)
        sigma = g.assumption_strengths()          # dict ground-asm -> [0,1]
        s     = g.query_strength("pacifist(a)")   # claim strength in [0,1]
    """

    def __init__(
        self,
        framework: ABAFramework,
        domain: List[str],
        assumption_scores: Optional[Dict[str, float]] = None,
        default_score: float = 0.5,
        kernel: str = DEFAULT_KERNEL,
        claim_mode: str = "max",
        max_set_size: Optional[int] = None,
        epsilon: float = 1e-4,
        max_iters: int = 500,
    ):
        self.kernel = kernel
        self.claim_mode = claim_mode
        self.epsilon = epsilon
        self.max_iters = max_iters
        self.ground = ground_framework(framework, domain, assumption_scores,
                                       default_score)
        self.supp = compute_supports(self.ground, max_set_size=max_set_size)
        self.bsaf = build_bsaf(self.ground, self.supp)
        self.result = run_semantics(self.bsaf, kernel, epsilon, max_iters)

    def assumption_strengths(self) -> Dict[str, float]:
        return self.result.assumption_strength

    def query_strength(self, claim: str, mode: Optional[str] = None) -> float:
        return claim_strength(claim, self.result.assumption_strength, self.supp,
                              mode=mode or self.claim_mode)

    @property
    def converged(self) -> bool:
        return self.result.converged

    @property
    def iterations(self) -> int:
        return self.result.iterations


# ──────────────────────────────────────────────────────────────────────────────
# Crisp-vs-graded comparison  (same shape as aba_graded.compare_crisp_vs_graded)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class BSAFReport:
    query:           str
    crisp_entailed:  bool
    graded_strength: float
    agree:           bool
    converged:       bool


def compare_crisp_vs_graded_bsaf(
    framework: ABAFramework,
    domain: List[str],
    queries: List[str],
    assumption_scores: Optional[Dict[str, float]] = None,
    threshold: float = 0.5,
    kernel: str = DEFAULT_KERNEL,
    claim_mode: str = "max",
) -> List[BSAFReport]:
    """For each query, the crisp brave verdict vs the BSAF graded strength.

    Crisp is delegated to Clingo (aba_validator); graded uses the correct
    assumption-based fixpoint semantics of this module.
    """
    from src.aba_validator import check_brave_entailment

    g = GradualABA(framework, domain, assumption_scores,
                   kernel=kernel, claim_mode=claim_mode)
    out: List[BSAFReport] = []
    for q in queries:
        crisp, _, _ = check_brave_entailment(framework, [q], [], domain)
        strength = g.query_strength(q)
        out.append(BSAFReport(
            query=q,
            crisp_entailed=crisp,
            graded_strength=round(strength, 4),
            agree=(crisp == (strength > threshold)),
            converged=g.converged,
        ))
    return out
