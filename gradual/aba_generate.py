"""
aba_generate.py
Random ABA framework generator + a convergence experiment for the gradual
ABA semantics, reproducing the methodology of:

  * Lehtonen, Rapberger, Toni, Ulbricht & Wallner, "Instantiations and
    Computational Aspects of Non-Flat Assumption-based Argumentation"
    (IJCAI 2024) — the benchmark-generation procedure, and
  * Rapberger, Russo, Rago & Toni, "On Gradual Semantics for ABA" (KR 2025)
    — the BSAF convergence experiment (their Figure 3),
    code: https://github.com/briziorusso/GradualABA  (data_generation/).

GENERATION PROCEDURE  (cycle_bengen_asp.py : create_framework)
--------------------------------------------------------------
Parameters:
    n_sentences      total number of atoms
    n_assumptions    number of those atoms that are assumptions
    n_rules_per_head candidate counts of rules deriving each head atom
    size_of_bodies   candidate rule-body sizes
    cycle_prob       probability of adding a "later" atom to a body (-> cycles)
    nonflat_coef     fraction of assumptions allowed to be rule heads
                     (0.0 -> flat ABAF; >0 -> non-flat)

Algorithm:
    1. create assumptions  a0..a{k-1}  and sentences  s0..s{m-1}
    2. contrary(a_i) = a random atom (sentence or assumption)
    3. head pool = all sentences + a nonflat_coef fraction of assumptions
    4. impose an ordering on atoms; rule bodies draw from assumptions and
       EARLIER sentences (acyclic by default), except with prob cycle_prob a
       body atom may come from later/equal positions, deliberately closing a cycle
    5. for each head: pick #rules from n_rules_per_head; each rule a body whose
       size is drawn from size_of_bodies

Reference parameter ranges (Lehtonen 2024, benchmark set 1):
    n_sentences in {80,120,160,200}; assumption ratio in {0.2,0.4};
    fraction of assumptions as heads in {0.2,0.5};
    #rules-per-head and body-size from [1,n], n in {1,2,5}.
Reference defaults (GradualABA generate_atomic):
    atoms in {20,40,60}; assumption ratio 0.5; rules/atom 2-8; body 2-16;
    nonflat coef in {0.01,0.05,0.1,0.2}; 10 iterations per config.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

from src.aba_types import Rule, ABAFramework
from gradual.aba_bsaf import GradualABA, KERNELS


# ──────────────────────────────────────────────────────────────────────────────
# Generator
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class QuantitativeABAF:
    """A generated ABAF together with its base scores (tau)."""
    framework:   ABAFramework
    base_scores: Dict[str, float]            # ground assumption atom -> tau
    flat:        bool
    meta:        Dict[str, object] = field(default_factory=dict)


def generate_random_abaf(
    n_sentences: int = 40,
    n_assumptions: Optional[int] = None,
    assumption_ratio: float = 0.5,
    n_rules_per_head: Tuple[int, ...] = (2, 3, 4, 5, 6, 7, 8),
    size_of_bodies: Tuple[int, ...] = tuple(range(2, 17)),
    cycle_prob: float = 0.05,
    nonflat_coef: float = 0.0,
    base_score_init: str = "constant",       # "constant" (0.5) | "random" U(0,1)
    seed: int = 0,
) -> QuantitativeABAF:
    """Generate one random (quantitative) ABA framework.

    Atoms are propositional: assumptions  a0..  and sentences  s0..  .
    Contraries map each assumption to a random other atom.  With nonflat_coef>0
    some assumptions may appear as rule heads, yielding a non-flat ABAF (with
    genuine BSAF supports).
    """
    rng = random.Random(seed)

    if n_assumptions is None:
        n_assumptions = max(1, round(assumption_ratio * n_sentences))
    n_assumptions = min(n_assumptions, n_sentences)
    n_plain = n_sentences - n_assumptions

    assumptions = [f"a{i}" for i in range(n_assumptions)]
    sentences   = [f"s{i}" for i in range(n_plain)]
    all_atoms   = assumptions + sentences

    # (2) contraries: each assumption -> a random atom (not itself)
    contraries: Dict[str, str] = {}
    for a in assumptions:
        choices = [x for x in all_atoms if x != a]
        contraries[a] = rng.choice(choices) if choices else a

    # (3) head pool: all plain sentences + a nonflat fraction of assumptions
    n_nonflat_heads = round(nonflat_coef * n_assumptions)
    nonflat_heads = rng.sample(assumptions, n_nonflat_heads) if n_nonflat_heads else []
    head_pool = sentences + nonflat_heads
    flat = len(nonflat_heads) == 0

    # (4) ordering on atoms — position[atom] used to keep bodies acyclic
    #     (assumptions first so they are always available as leaves)
    order = assumptions + sentences
    position = {atom: i for i, atom in enumerate(order)}

    rules: List[Rule] = []
    for head in head_pool:
        h_pos = position[head]
        # candidate body atoms that respect the ordering (strictly earlier),
        # always including ALL assumptions as available leaves
        earlier = [x for x in order if position[x] < h_pos]
        later   = [x for x in order if position[x] >= h_pos and x != head]
        # sorted(), not list(set(...)): set iteration order over strings varies
        # with PYTHONHASHSEED, which would make rng.sample below differ between
        # processes and silently break the seeded reproducibility claim.
        base_candidates = sorted(set(earlier) | set(assumptions))
        base_candidates = [x for x in base_candidates if x != head]
        if not base_candidates:
            continue

        n_rules = rng.choice(n_rules_per_head)
        for _ in range(n_rules):
            size = rng.choice(size_of_bodies)
            size = max(1, min(size, len(base_candidates)))
            body = rng.sample(base_candidates, size)
            # (4 cont.) with prob cycle_prob, swap in a "later" atom -> cycle
            if later and rng.random() < cycle_prob:
                body[rng.randrange(len(body))] = rng.choice(later)
            rules.append(Rule(head=head, body=sorted(set(body))))

    # also emit a few ground facts so some sentences are unconditionally derivable
    # (otherwise many atoms are vacuously underivable and the BSAF is empty)
    n_facts = max(1, n_plain // 5)
    for s in rng.sample(sentences, min(n_facts, len(sentences))):
        rules.append(Rule(head=s, body=[]))

    fw = ABAFramework(rules=rules, assumptions=list(assumptions),
                      contraries=dict(contraries))

    # base scores
    if base_score_init == "random":
        base = {a: rng.random() for a in assumptions}
    else:
        base = {a: 0.5 for a in assumptions}

    return QuantitativeABAF(
        framework=fw,
        base_scores=base,
        flat=flat,
        meta={
            "n_sentences": n_sentences,
            "n_assumptions": n_assumptions,
            "nonflat_coef": nonflat_coef,
            "cycle_prob": cycle_prob,
            "n_rules": len(rules),
            "base_score_init": base_score_init,
            "seed": seed,
        },
    )


def generate_batch(
    n: int,
    seed: int = 0,
    **kwargs,
) -> List[QuantitativeABAF]:
    """Generate n random quantitative ABAFs with distinct seeds."""
    return [generate_random_abaf(seed=seed + i, **kwargs) for i in range(n)]


# ──────────────────────────────────────────────────────────────────────────────
# Convergence experiment  (reproduces the BSAF side of the paper's Figure 3)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ConvergenceStats:
    kernel:              str
    base_score_init:     str
    n_frameworks:        int
    n_converged:         int
    global_conv_rate:    float            # fraction that converged
    avg_steps:           float            # mean iterations over converged runs

    def __str__(self) -> str:
        return (f"  {self.kernel:<14} init={self.base_score_init:<8} "
                f"conv={self.global_conv_rate:5.1%} "
                f"({self.n_converged}/{self.n_frameworks})  "
                f"avg_steps={self.avg_steps:5.1f}")


def convergence_experiment(
    n_frameworks: int = 50,
    kernels: Tuple[str, ...] = ("dfquad_prod", "dfquad_min", "qe_prod", "qe_min"),
    base_inits: Tuple[str, ...] = ("constant", "random"),
    epsilon: float = 1e-3,
    max_iters: int = 500,
    seed: int = 0,
    verbose: bool = True,
    **gen_kwargs,
) -> List[ConvergenceStats]:
    """Run the strength-evolution fixpoint over many random ABAFs and report,
    per (kernel, base-score init), the global convergence rate and average steps
    to converge — the BSAF metrics of the paper's Figure 3.

    The paper finds DF-QuAD converges in >=90% of scenarios; QE is faster under
    Product but degrades on larger / cyclic instances.
    """
    stats: List[ConvergenceStats] = []
    if verbose:
        print(f"\n=== BSAF gradual-semantics convergence "
              f"({n_frameworks} random ABAFs) ===")
    for init in base_inits:
        # generate ONE shared suite per init so kernels are compared on equal footing
        suite = generate_batch(n_frameworks, seed=seed,
                               base_score_init=init, **gen_kwargs)
        for kernel in kernels:
            n_conv = 0
            steps: List[int] = []
            for q in suite:
                g = GradualABA(
                    q.framework, q.framework.get_domain() or ["x"],
                    assumption_scores=q.base_scores,
                    kernel=kernel, epsilon=epsilon, max_iters=max_iters,
                )
                if g.converged:
                    n_conv += 1
                    steps.append(g.iterations)
            st = ConvergenceStats(
                kernel=KERNELS[kernel].name,
                base_score_init=init,
                n_frameworks=len(suite),
                n_converged=n_conv,
                global_conv_rate=n_conv / len(suite) if suite else 0.0,
                avg_steps=sum(steps) / len(steps) if steps else 0.0,
            )
            stats.append(st)
            if verbose:
                print(st)
    return stats
