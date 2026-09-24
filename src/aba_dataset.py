"""
aba_dataset.py
Dataset loading (from the paper's Zenodo benchmarks),
synthetic generation, and train/val/test splitting.
"""
from __future__ import annotations
import os
import re
import json
import random
import copy
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Iterator
from pathlib import Path

from src.aba_types import Rule, ABAFramework, LearningProblem, LearningTrace
from src.aba_validator import (
    check_brave_entailment, run_rote_learning,
    check_has_stable_extension
)


# ---------------------------------------------------------------------------
# Prolog file parser
# ---------------------------------------------------------------------------

def _strip_comments(text: str) -> str:
    text = re.sub(r'%.*', '', text)
    return text


def _parse_prolog_rule(line: str) -> Optional[Rule]:
    line = line.strip().rstrip('.')
    if ':-' in line:
        head, body = line.split(':-', 1)
        body_atoms = [b.strip() for b in body.split(',') if b.strip()]
        return Rule(head=head.strip(), body=body_atoms)
    elif line:
        return Rule(head=line.strip(), body=[])
    return None


def parse_framework_from_prolog(text: str) -> ABAFramework:
    """
    Parse an ABA framework from a Prolog-style text file.

    Expected format (as used in the paper's Zenodo archive):
        % Rules
        pacifist(X) :- quaker(X), normal_quaker(X).
        quaker(a).

        % Assumptions
        assumption(normal_quaker(X)).

        % Contraries
        contrary(normal_quaker(X), abnormal_quaker(X)).
    """
    text = _strip_comments(text)
    rules: List[Rule] = []
    assumptions: List[str] = []
    contraries: Dict[str, str] = {}

    for raw_line in text.split('\n'):
        line = raw_line.strip().rstrip('.')
        if not line:
            continue

        # Assumption declaration
        asm_match = re.match(r'assumption\((.+)\)', line)
        if asm_match:
            assumptions.append(asm_match.group(1).strip())
            continue

        # Contrary declaration
        cnt_match = re.match(r'contrary\((.+),\s*(.+)\)', line)
        if cnt_match:
            asm = cnt_match.group(1).strip()
            contrary = cnt_match.group(2).strip()
            contraries[asm] = contrary
            continue

        # Learnable predicate hint (used in dataset files)
        if line.startswith('learnable(') or line.startswith('#learnable'):
            continue

        # Regular rule or fact
        rule = _parse_prolog_rule(line + '.')
        if rule and rule.head:
            rules.append(rule)

    return ABAFramework(rules=rules, assumptions=assumptions,
                        contraries=contraries)


def parse_learning_problem_from_dir(directory: str) -> LearningProblem:
    """
    Load a learning problem from a directory with the structure:
        background.pl   — background ABA framework
        examples.pl     — positive/negative examples
        learnable.txt   — list of learnable predicate names (one per line)
    """
    base = Path(directory)
    problem_id = base.name

    bg_text = (base / 'background.pl').read_text()
    background = parse_framework_from_prolog(bg_text)

    positive, negative, learnable = [], [], []

    ex_path = base / 'examples.pl'
    if ex_path.exists():
        ex_text = _strip_comments(ex_path.read_text())
        for line in ex_text.split('\n'):
            line = line.strip().rstrip('.')
            pos_m = re.match(r'pos\((.+)\)', line)
            neg_m = re.match(r'neg\((.+)\)', line)
            if pos_m:
                positive.append(pos_m.group(1).strip())
            elif neg_m:
                negative.append(neg_m.group(1).strip())

    learn_path = base / 'learnable.txt'
    if learn_path.exists():
        learnable = [
            l.strip() for l in learn_path.read_text().split('\n')
            if l.strip()
        ]

    domain = background.get_domain()

    return LearningProblem(
        background=background,
        positive=positive,
        negative=negative,
        learnable=learnable,
        domain=domain,
        problem_id=problem_id,
    )


# ---------------------------------------------------------------------------
# Built-in benchmark problems (from the paper, hard-coded for convenience)
# ---------------------------------------------------------------------------

def make_nixon_diamond() -> Tuple[LearningProblem, ABAFramework]:
    """
    The Nixon diamond problem from Example 3 of the paper.
    Returns (problem, ground_truth_solution).
    """
    # Background rules
    bg_rules = [
        Rule("quaker(a)", []),
        Rule("quaker(b)", []),
        Rule("quaker(e)", []),
        Rule("democrat(c)", []),
        Rule("republican(a)", []),
        Rule("republican(b)", []),
        Rule("republican(d)", []),
        Rule("democrat(X)", ["person(X)", "votes_dem(X)"]),
        Rule("republican(X)", ["person(X)", "votes_rep(X)"]),
        Rule("pacifist(X)", ["quaker(X)", "normal_quaker(X)"]),
        Rule("person(X)", ["dom(X)"]),
    ]
    bg_assumptions = [
        "votes_dem(X)", "votes_rep(X)", "normal_quaker(X)"
    ]
    bg_contraries = {
        "votes_dem(X)": "republican(X)",
        "votes_rep(X)": "democrat(X)",
        "normal_quaker(X)": "abnormal_quaker(X)",
    }
    background = ABAFramework(
        rules=bg_rules,
        assumptions=bg_assumptions,
        contraries=bg_contraries,
    )

    domain = ['a', 'b', 'c', 'd', 'e']
    problem = LearningProblem(
        background=background,
        positive=["pacifist(a)", "pacifist(c)", "pacifist(e)"],
        negative=["pacifist(b)", "pacifist(d)"],
        learnable=["pacifist", "abnormal_quaker"],
        domain=domain,
        problem_id="nixon_diamond",
    )

    # Ground truth solution (R2 from Example 3)
    new_rules = [
        Rule("abnormal_quaker(X)", ["republican(X)", "alpha(X)"]),
        Rule("c_alpha(X)", ["quaker(X)", "normal_quaker(X)"]),
        Rule("pacifist(X)", ["democrat(X)"]),
    ]
    new_asms = ["alpha(X)"]
    solution = background.copy()
    solution.rules.extend(new_rules)
    solution.assumptions.extend(new_asms)
    solution.contraries["alpha(X)"] = "c_alpha(X)"
    solution.new_rules = new_rules
    solution.new_assumptions = new_asms

    return problem, solution


def make_flies_problem() -> LearningProblem:
    """Classic 'flies' ILP benchmark."""
    bg_rules = [
        Rule("bird(tweety)", []),
        Rule("bird(sam)", []),
        Rule("bird(opus)", []),
        Rule("penguin(sam)", []),
        Rule("penguin(opus)", []),
    ]
    bg_asms = ["normal_bird(X)"]
    bg_contraries = {"normal_bird(X)": "ab_bird(X)"}
    background = ABAFramework(
        rules=bg_rules, assumptions=bg_asms, contraries=bg_contraries
    )
    return LearningProblem(
        background=background,
        positive=["flies(tweety)"],
        negative=["flies(sam)", "flies(opus)"],
        learnable=["flies", "ab_bird"],
        domain=["tweety", "sam", "opus"],
        problem_id="flies",
    )


def make_tax_law_problem() -> LearningProblem:
    """Simplified tax law problem."""
    bg_rules = [
        Rule("employed(alice)", []),
        Rule("employed(bob)", []),
        Rule("self_employed(carol)", []),
        Rule("income(alice)", ["employed(alice)"]),
        Rule("income(bob)", ["employed(bob)"]),
        Rule("income(carol)", ["self_employed(carol)"]),
    ]
    bg_asms = ["normal_taxpayer(X)"]
    bg_contraries = {"normal_taxpayer(X)": "exempt(X)"}
    background = ABAFramework(
        rules=bg_rules, assumptions=bg_asms, contraries=bg_contraries
    )
    return LearningProblem(
        background=background,
        positive=["taxable(alice)", "taxable(carol)"],
        negative=["taxable(bob)"],
        learnable=["taxable", "exempt"],
        domain=["alice", "bob", "carol"],
        problem_id="tax_law",
    )


BUILTIN_PROBLEMS = {
    "nixon_diamond": make_nixon_diamond,
    "flies": make_flies_problem,
    "tax_law": make_tax_law_problem,
}


# ---------------------------------------------------------------------------
# Synthetic problem generator
# ---------------------------------------------------------------------------

# Stratified difficulty tiers for the massive-testing benchmark suite.
# Each tier isolates one capability of the ABA-learning algorithm.
BENCHMARK_TIERS: List[Dict] = [
    {"name": "t1_mono",    "kind": "single",
     "kwargs": dict(n_constants=6, with_exceptions=False),
     "tests": "folding only, monotonic rule suffices"},
    {"name": "t2_defeas",  "kind": "single",
     "kwargs": dict(n_constants=6, with_exceptions=True),
     "tests": "assumption introduction, one exception"},
    {"name": "t3_noise",   "kind": "single",
     "kwargs": dict(n_constants=8, with_exceptions=True, n_predicates=6),
     "tests": "distractor robustness, extra noise predicates"},
    {"name": "t4_domain",  "kind": "single",
     "kwargs": dict(n_constants=12, with_exceptions=True,
                    n_positive=4, n_negative=4),
     "tests": "domain-size scaling, 12 constants"},
    {"name": "t5_twopath", "kind": "complex",
     "kwargs": dict(n_constants=8),
     "tests": "two independent defeasible derivation paths"},
]


_PRED_POOL = (
    "flies", "swims", "runs", "eats", "sleeps",
    "predator", "prey", "domestic", "wild",
    "friendly", "dangerous", "nocturnal", "fast",
)


class SyntheticGenerator:
    """
    Generate random ABA learning problems by:
      1. Sampling a random 'target' ABA framework.
      2. Hiding some of its rules to form background knowledge.
      3. Generating positive/negative examples from what the target entails.
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.pred_names = list(_PRED_POOL)

    @staticmethod
    def _make_constants(n: int) -> List[str]:
        """Constant pool of exactly n symbols (c0..c{n-1}); no hidden cap."""
        return [f"c{i}" for i in range(n)]

    def generate_one(
        self,
        n_predicates: int = 4,
        n_constants: int = 6,
        n_positive: int = 3,
        n_negative: int = 3,
        with_exceptions: bool = True,
        seed: Optional[object] = None,
    ) -> Optional[LearningProblem]:
        """
        Generate a random learning problem.
        Returns None if no valid problem could be built.

        The target predicate holds for a constant iff a chosen support
        predicate holds for it, UNLESS the constant is an exception. We force a
        balanced split by assigning the support predicate to roughly half the
        constants.

        with_exceptions=True (default) makes some support-satisfying constants
        into NEGATIVE examples via an exception predicate that triggers the
        contrary of the assumption. This is what forces the symbolic solver to
        learn a genuinely DEFEASIBLE rule (using the assumption), rather than a
        trivial monotonic rule. Without exceptions the assumption is never used
        and the graded layer collapses to crisp 0/1.

        `seed`, when given, draws this ONE problem from its own
        `random.Random(seed)` instead of the generator's shared stream. That is
        what makes corpora nest: with a shared stream every rejected attempt
        shifts all later problems, so a corpus of 50 is not a prefix of one of
        200. None (the default) is the original shared-stream behaviour, which
        `tests/test_golden_traces.py` pins against set 05.
        """
        rng = random.Random(seed) if seed is not None else self.rng
        n_constants = max(n_constants, 6)          # need room for >=2 each side
        preds = rng.sample(self.pred_names, min(n_predicates, len(self.pred_names)))
        consts = self._make_constants(n_constants)
        target_pred = preds[0]
        support_preds = preds[1:]
        key_support = support_preds[0]
        # A dedicated exception predicate (distinct from the support preds)
        exception_pred = f"exc_{target_pred}"

        # Force a balanced assignment: about half the constants get the key
        # support predicate. Among those, designate one or two as EXCEPTIONS
        # (they satisfy the support but are defeated -> negative).
        shuffled = list(consts)
        rng.shuffle(shuffled)
        half = len(shuffled) // 2
        support_consts = shuffled[:half + 1]        # satisfy key_support
        no_support_consts = shuffled[half + 1:]     # clearly negative

        exception_consts: List[str] = []
        if with_exceptions and len(support_consts) >= 3:
            # Make one constant an exception so it is support-satisfying yet
            # negative, forcing a defeasible solution.
            n_exc = 1
            exception_consts = support_consts[:n_exc]

        base_facts = [Rule(f"{key_support}({c})", []) for c in support_consts]
        base_facts += [Rule(f"{exception_pred}({c})", []) for c in exception_consts]
        # Add some noise facts for the other support predicates.
        for p in support_preds[1:]:
            for c in consts:
                if rng.random() > 0.5:
                    base_facts.append(Rule(f"{p}({c})", []))

        asm_name = f"normal_{target_pred}"
        asm = f"{asm_name}(X)"
        contrary = f"ab_{target_pred}(X)"

        # Target holds if support AND the (defeasible) normal assumption.
        target_rule = Rule(head=f"{target_pred}(X)", body=[f"{key_support}(X)", asm])
        # The exception derives the contrary, defeating the assumption.
        exception_rule = Rule(head=f"ab_{target_pred}(X)",
                              body=[f"{exception_pred}(X)"])

        full_rules = base_facts + [target_rule, exception_rule]
        full_fw = ABAFramework(
            rules=full_rules,
            assumptions=[asm],
            contraries={asm: contrary},
        )

        # Determine which constants satisfy/don't satisfy target_pred.
        positive_candidates, negative_candidates = [], []
        for c in consts:
            atom = f"{target_pred}({c})"
            valid, _, _ = check_brave_entailment(full_fw, [atom], [], consts)
            (positive_candidates if valid else negative_candidates).append(atom)

        if not positive_candidates or not negative_candidates:
            return None

        # Ensure at least one exception lands in the negatives so the learned
        # solution must be defeasible.
        forced_negatives = [f"{target_pred}({c})" for c in exception_consts
                            if f"{target_pred}({c})" in negative_candidates]

        positives = rng.sample(
            positive_candidates, min(n_positive, len(positive_candidates))
        )
        remaining_neg = [n for n in negative_candidates if n not in forced_negatives]
        rng.shuffle(remaining_neg)
        negatives = (forced_negatives +
                     remaining_neg)[:max(n_negative, len(forced_negatives))]

        # Background = remove the target rule (but KEEP the exception facts and
        # the contrary rule, so the structure for defeasibility is available).
        background = ABAFramework(
            rules=base_facts + [exception_rule],
            assumptions=[asm],
            contraries={asm: contrary},
        )

        problem = LearningProblem(
            background=background,
            positive=positives,
            negative=negatives,
            learnable=[target_pred, f"ab_{target_pred}"],
            domain=consts,
            problem_id=f"synthetic_{target_pred}",
        )

        # ── Quality filter (M6) ──────────────────────────────────────────────
        if len(positives) < 2 or len(negatives) < 2:
            return None
        if len(consts) < 3:
            return None
        try:
            from src.aba_validator import run_rote_learning
            _facts, ok, _ = run_rote_learning(problem)
            if not ok:
                return None
        except Exception:
            return None

        return problem

    def generate_batch(
        self,
        n: int,
        max_attempts: int = 5,
        **kwargs,
    ) -> List[LearningProblem]:
        """Generate n valid synthetic problems."""
        problems = []
        attempts = 0
        while len(problems) < n and attempts < n * max_attempts:
            p = self.generate_one(**kwargs)
            if p is not None:
                p.problem_id = f"synthetic_{len(problems):04d}"
                problems.append(p)
            attempts += 1
        return problems

    def generate_complex(
        self,
        n_constants: int = 8,
        n_positive: int = 4,
        n_negative: int = 4,
    ) -> Optional[LearningProblem]:
        """
        Generate a two-path learning problem.

        The target predicate is reachable via two independent background
        predicates (prop_a / prop_b), each gated by its own defeasible
        assumption.  A valid solution therefore requires:

          target(X) :- prop_a(X), normal_a(X).   % path A
          target(X) :- prop_b(X), normal_b(X).   % path B
          ab_a(X)   :- exc_a(X).
          ab_b(X)   :- exc_b(X).

        This gives a richer QBAF: constants reachable via one path score
        differently from those reachable via both paths (DF-QuAD's
        probabilistic-OR over supporters), producing genuinely intermediate
        sigma values rather than a binary 0/1 outcome.
        """
        n_constants = max(n_constants, 8)
        if len(self.pred_names) < 4:
            return None

        preds = self.rng.sample(self.pred_names, min(6, len(self.pred_names)))
        target_pred = preds[0]
        prop_a = preds[1]
        prop_b = preds[2]
        exc_a_pred = f"exc_a_{target_pred[:4]}"
        exc_b_pred = f"exc_b_{target_pred[:4]}"
        asm_a = f"normal_a_{target_pred}(X)"
        asm_b = f"normal_b_{target_pred}(X)"
        contrary_a = f"ab_a_{target_pred}(X)"
        contrary_b = f"ab_b_{target_pred}(X)"

        consts = self._make_constants(n_constants)
        shuffled = list(consts)
        self.rng.shuffle(shuffled)

        # Distribute across four groups so the QBAF has genuinely distinct cases:
        #   a_only  → reachable via path A only
        #   b_only  → reachable via path B only
        #   both    → reachable via both (boosted σ from two supporters)
        #   neither → no path (clearly negative)
        q = max(2, len(shuffled) // 4)
        a_only  = shuffled[:q]
        b_only  = shuffled[q:2 * q]
        both    = shuffled[2 * q: 2 * q + 2]
        # shuffled[2*q+2:] → neither group: no prop facts added → always negative

        exc_a_consts = a_only[:1]   # exception for path A → forced negative
        exc_b_consts = b_only[:1]   # exception for path B → forced negative

        base_facts: List[Rule] = []
        for c in a_only + both:
            base_facts.append(Rule(f"{prop_a}({c})", []))
        for c in b_only + both:
            base_facts.append(Rule(f"{prop_b}({c})", []))
        for c in exc_a_consts:
            base_facts.append(Rule(f"{exc_a_pred}({c})", []))
        for c in exc_b_consts:
            base_facts.append(Rule(f"{exc_b_pred}({c})", []))

        target_rule_a = Rule(head=f"{target_pred}(X)",
                             body=[f"{prop_a}(X)", asm_a])
        target_rule_b = Rule(head=f"{target_pred}(X)",
                             body=[f"{prop_b}(X)", asm_b])
        exc_rule_a = Rule(head=f"ab_a_{target_pred}(X)",
                          body=[f"{exc_a_pred}(X)"])
        exc_rule_b = Rule(head=f"ab_b_{target_pred}(X)",
                          body=[f"{exc_b_pred}(X)"])

        full_rules = (base_facts
                      + [target_rule_a, target_rule_b, exc_rule_a, exc_rule_b])
        full_fw = ABAFramework(
            rules=full_rules,
            assumptions=[asm_a, asm_b],
            contraries={asm_a: contrary_a, asm_b: contrary_b},
        )

        positive_candidates: List[str] = []
        negative_candidates: List[str] = []
        for c in consts:
            atom = f"{target_pred}({c})"
            valid, _, _ = check_brave_entailment(full_fw, [atom], [], consts)
            (positive_candidates if valid else negative_candidates).append(atom)

        if len(positive_candidates) < 2 or len(negative_candidates) < 2:
            return None

        positives = self.rng.sample(
            positive_candidates, min(n_positive, len(positive_candidates))
        )
        negatives = self.rng.sample(
            negative_candidates, min(n_negative, len(negative_candidates))
        )

        background = ABAFramework(
            rules=base_facts + [exc_rule_a, exc_rule_b],
            assumptions=[asm_a, asm_b],
            contraries={asm_a: contrary_a, asm_b: contrary_b},
        )
        # ab_a_* and ab_b_* contrary rules are already in the background;
        # listing them as learnable causes RoLe to add spurious ground facts.
        problem = LearningProblem(
            background=background,
            positive=positives,
            negative=negatives,
            learnable=[target_pred],
            domain=consts,
            problem_id=f"complex_{target_pred}",
        )

        if len(positives) < 2 or len(negatives) < 2:
            return None
        try:
            _facts, ok, _ = run_rote_learning(problem)
            if not ok:
                return None
        except Exception:
            return None

        return problem

    def generate_complex_batch(
        self,
        n: int,
        max_attempts: int = 8,
        **kwargs,
    ) -> List[LearningProblem]:
        """Generate n valid two-path (complex) problems."""
        problems = []
        attempts = 0
        while len(problems) < n and attempts < n * max_attempts:
            p = self.generate_complex(**kwargs)
            if p is not None:
                p.problem_id = f"complex_{len(problems):04d}"
                problems.append(p)
            attempts += 1
        return problems


# ---------------------------------------------------------------------------
# Training-corpus generator (tier spec v2)
# ---------------------------------------------------------------------------

# Every problem carries exception facts, and fact and example counts do not
# depend on the class, so only folding and checking tells whether R3 is needed.
# BENCHMARK_TIERS (spec v1) stays as it was: set 05 regenerates from it.
CORPUS_TIER_SPEC_VERSION = 2
CORPUS_TIERS: List[Dict] = [
    {"name": "t1_base",    "kind": "single",
     "kwargs": dict(n_constants=6, n_noise=2)},
    {"name": "t2_noise",   "kind": "single",
     "kwargs": dict(n_constants=8, n_noise=4)},
    {"name": "t3_domain",  "kind": "single",
     "kwargs": dict(n_constants=12, n_noise=2, n_pos=(4, 5), n_neg=(4, 5))},
    {"name": "t4_nested",  "kind": "single",
     "kwargs": dict(n_constants=8, n_noise=2, nested=True, exc_first=True)},
    {"name": "t5_twopath", "kind": "twopath",
     "kwargs": dict(n_constants=10, n_noise=2)},
]


def _fact_block(rng: random.Random, pred: str, consts: List[str]) -> List[Rule]:
    # Shuffled, so a fact's position says nothing about its constant's role.
    cs = list(consts)
    rng.shuffle(cs)
    return [Rule(f"{pred}({c})", []) for c in cs]


def _noise_facts(rng: random.Random, preds: List[str],
                 consts: List[str]) -> List[Rule]:
    return [Rule(f"{p}({c})", []) for p in preds for c in consts
            if rng.random() < 0.5]


def _finish(rng, facts, exc_rules, target_rules, asms, contr, t, pos_c, neg_c,
            consts, learnable, problem_id) -> Optional[LearningProblem]:
    """The problem, if the hidden target explains its examples and RoLe works."""
    full = ABAFramework(rules=facts + exc_rules + target_rules,
                        assumptions=list(asms), contraries=dict(contr))
    pos = [f"{t}({c})" for c in rng.sample(pos_c, len(pos_c))]
    neg = [f"{t}({c})" for c in rng.sample(neg_c, len(neg_c))]
    if not check_brave_entailment(full, pos, neg, consts)[0]:
        return None
    problem = LearningProblem(
        background=ABAFramework(rules=facts + exc_rules, assumptions=list(asms),
                                contraries=dict(contr)),
        positive=pos, negative=neg, learnable=learnable, domain=list(consts),
        problem_id=problem_id,
    )
    _facts, ok, _ = run_rote_learning(problem)
    return problem if ok else None


def generate_corpus_single(
    seed: object,
    defeasible: bool,
    n_constants: int = 6,
    n_noise: int = 2,
    n_pos: Tuple[int, int] = (2, 3),
    n_neg: Tuple[int, int] = (2, 3),
    nested: bool = False,
    exc_first: bool = False,
) -> Optional[Tuple[LearningProblem, Dict]]:
    """One single-path problem, drawn from Random(seed).

    Hidden target: t(X) :- key(X), normal_t(X), defeated by an exception. One
    key constant s is special, and two exception facts are always present: one
    on a negative, one on an unlisted constant. Defeasible: s is that negative,
    so the fold on key covers it and R3 is needed. Monotonic: s is the unlisted
    one, and the negative lacks key. `nested` adds an exempt positive whose
    exception is itself defeated.
    """
    rng = random.Random(seed)
    names = rng.sample(_PRED_POOL, 2 + n_noise)
    t, key, noise = names[0], names[1], names[2:]
    exc, exempt = f"exc_{t}", f"exempt_{t}"

    sizes = [(p, n) for p in range(n_pos[0], n_pos[1] + 1)
             for n in range(n_neg[0], n_neg[1] + 1) if p + n + 1 <= n_constants]
    npos, nneg = rng.choice(sizes)
    consts = [f"c{i}" for i in range(n_constants)]
    sh = list(consts)
    rng.shuffle(sh)
    s, P, N = sh[0], sh[1:npos + 1], sh[npos + 1:]
    X = P[:1] if nested else []
    if defeasible:
        Ng, exc_on = [s] + N[:nneg - 1], [s, N[nneg - 1]]
    else:
        Ng, exc_on = N[:nneg], [N[0], s]

    key_f = _fact_block(rng, key, [s] + P)
    exc_f = _fact_block(rng, exc, exc_on + X)
    facts = ((exc_f + key_f) if exc_first else (key_f + exc_f)) \
        + _fact_block(rng, exempt, X) + _noise_facts(rng, noise, consts)

    asm_t, ab_t = f"normal_{t}(X)", f"ab_{t}(X)"
    asms, contr = [asm_t], {asm_t: ab_t}
    if nested:
        asm_e, ab_e = f"normal_{exc}(X)", f"ab_{exc}(X)"
        exc_rules = [Rule(ab_t, [f"{exc}(X)", asm_e]),
                     Rule(ab_e, [f"{exempt}(X)"])]
        asms.append(asm_e)
        contr[asm_e] = ab_e
    else:
        exc_rules = [Rule(ab_t, [f"{exc}(X)"])]
    target = Rule(f"{t}(X)", [f"{key}(X)", asm_t])

    problem = _finish(rng, facts, exc_rules, [target], asms, contr, t, P, Ng,
                      consts, [t, f"ab_{t}"], f"corpus_{t}")
    return (problem, {"observed": ["t"] if defeasible else []}) if problem else None


def generate_corpus_twopath(
    seed: object,
    defeasible: bool,
    n_constants: int = 10,
    n_noise: int = 2,
    n_neg: Tuple[int, int] = (2, 3),
) -> Optional[Tuple[LearningProblem, Dict]]:
    """One two-path problem, drawn from Random(seed); t5 spec v2.

    Hidden target: t(X) :- a(X), normal_a(X) and t(X) :- b(X), normal_b(X), each
    with its own exception. Each path has a special constant and two exception
    facts, as in `generate_corpus_single`; defeasible problems observe the
    exception on one path or both. Group sizes vary, so problems are no longer
    isomorphic.
    """
    rng = random.Random(seed)
    names = rng.sample(_PRED_POOL, 3 + n_noise)
    t, pa, pb, noise = names[0], names[1], names[2], names[3:]
    observed = rng.choice([("a",), ("b",), ("a", "b")]) if defeasible else ()

    consts = [f"c{i}" for i in range(n_constants)]
    sh = list(consts)
    rng.shuffle(sh)
    na, nb, nab = rng.randint(2, 3), rng.randint(2, 3), rng.randint(0, 2)
    A, B = sh[:na], sh[na:na + nb]
    AB, N = sh[na + nb:na + nb + nab], sh[na + nb + nab:]
    nneg = rng.choice([n for n in range(n_neg[0], n_neg[1] + 1) if n <= len(N)])
    special = {"a": A[0], "b": B[0]}
    P = A[1:] + B[1:] + AB
    k = nneg - len(observed)
    Ng = [special[p] for p in observed] + N[:k]
    negs, unlisted = iter(N[:k]), iter(N[k:])
    exc_on = {p: [special[p], next(unlisted)] if p in observed
              else [next(negs), special[p]] for p in ("a", "b")}

    exc_a, exc_b = f"exc_a_{t}", f"exc_b_{t}"
    facts = (_fact_block(rng, pa, A + AB) + _fact_block(rng, pb, B + AB)
             + _fact_block(rng, exc_a, exc_on["a"])
             + _fact_block(rng, exc_b, exc_on["b"])
             + _noise_facts(rng, noise, consts))
    asm_a, asm_b = f"normal_a_{t}(X)", f"normal_b_{t}(X)"
    ab_a, ab_b = f"ab_a_{t}(X)", f"ab_b_{t}(X)"
    exc_rules = [Rule(ab_a, [f"{exc_a}(X)"]), Rule(ab_b, [f"{exc_b}(X)"])]
    targets = [Rule(f"{t}(X)", [f"{pa}(X)", asm_a]),
               Rule(f"{t}(X)", [f"{pb}(X)", asm_b])]

    # ab_* already have rules; learnable ones let RoLe add spurious facts.
    problem = _finish(rng, facts, exc_rules, targets, [asm_a, asm_b],
                      {asm_a: ab_a, asm_b: ab_b}, t, P, Ng, consts, [t],
                      f"corpus_{t}")
    return (problem, {"observed": list(observed)}) if problem else None


def generate_corpus_problem(
    tier: Dict, defeasible: bool, seed: object,
) -> Optional[Tuple[LearningProblem, Dict]]:
    fn = (generate_corpus_twopath if tier["kind"] == "twopath"
          else generate_corpus_single)
    return fn(seed, defeasible, **tier["kwargs"])


# ---------------------------------------------------------------------------
# Held-out generator: two solutions the checker cannot tell apart
# ---------------------------------------------------------------------------

# Never trained on. Every problem has two intensional solutions that pass the
# checker, and only following Algorithm 1 gives the reference's. The two halves
# of a tier swap which one that is, so a fixed preference scores 0.5.
HELDOUT_TIERS: List[Dict] = [
    {"name": "t8_decoy", "kind": "decoy",
     "kwargs": dict(n_constants=8, n_noise=1)},
    {"name": "t9_reuse", "kind": "reuse",
     "kwargs": dict(n_constants=8, n_noise=1)},
]


def _heldout_layout(rng, n_constants, n_pos, n_neg):
    sizes = [(p, n) for p in range(n_pos[0], n_pos[1] + 1)
             for n in range(n_neg[0], n_neg[1] + 1) if p + n + 1 <= n_constants]
    npos, nneg = rng.choice(sizes)
    consts = [f"c{i}" for i in range(n_constants)]
    sh = list(consts)
    rng.shuffle(sh)
    s, P, N = sh[0], sh[1:npos + 1], sh[npos + 1:]
    return consts, s, P, [s] + N[:nneg - 1], N[nneg - 1]


def generate_heldout_decoy(
    seed: object,
    decoy_first: bool,
    n_constants: int = 8,
    n_noise: int = 1,
    n_pos: Tuple[int, int] = (2, 3),
    n_neg: Tuple[int, int] = (2, 3),
) -> Optional[Tuple[LearningProblem, Dict]]:
    """t8_decoy, Algorithm 1 lines 17-19.

    key holds for the positives and a negative s (an exception); decoy holds
    for the positives only. Line 17 takes the fold whose facts come first:
    decoy is a solution as it stands (line 18); key is not, so line 19 guards
    it with a fresh alpha. Both answers pass the checker in both halves.
    """
    rng = random.Random(seed)
    names = rng.sample(_PRED_POOL, 3 + n_noise)
    t, key, decoy, noise = names[0], names[1], names[2], names[3:]
    exc = f"exc_{t}"
    consts, s, P, Ng, u = _heldout_layout(rng, n_constants, n_pos, n_neg)

    key_f, decoy_f = _fact_block(rng, key, [s] + P), _fact_block(rng, decoy, P)
    facts = ((decoy_f + key_f) if decoy_first else (key_f + decoy_f)) \
        + _fact_block(rng, exc, [s, u]) + _noise_facts(rng, noise, consts)
    asm_t, ab_t = f"normal_{t}(X)", f"ab_{t}(X)"
    problem = _finish(rng, facts, [Rule(ab_t, [f"{exc}(X)"])],
                      [Rule(f"{t}(X)", [f"{key}(X)", asm_t])], [asm_t],
                      {asm_t: ab_t}, t, P, Ng, consts, [t, f"ab_{t}"],
                      f"heldout_{t}")
    if problem is None:
        return None
    answers = {
        "key": ([Rule(f"{t}(X)", [f"{key}(X)", "alpha_0(X)"]),
                 Rule("c_alpha_0(X)", [f"{exc}(X)"])],
                {"alpha_0(X)": "c_alpha_0(X)"}),
        "decoy": ([Rule(f"{t}(X)", [f"{decoy}(X)"])], {}),
    }
    # Either answer is a run of Algorithm 1 under some fold order (Definition
    # 3 leaves it open), so nothing here is forbidden outright.
    return problem, {"half": "decoy_first" if decoy_first else "key_first",
                     "expected": "decoy" if decoy_first else "key",
                     "forbidden": [], "answers": answers}


def generate_heldout_reuse(
    seed: object,
    reuse_ok: bool,
    n_constants: int = 8,
    n_noise: int = 1,
    n_pos: Tuple[int, int] = (2, 3),
    n_neg: Tuple[int, int] = (2, 3),
) -> Optional[Tuple[LearningProblem, Dict]]:
    """t9_reuse, Algorithm 1 lines 36-39.

    The background rule h(X) :- key(X), beta(X) makes beta relative to key(X)
    (Definition 4), so line 36 must reuse beta on the fold t(X) :- key(X). If
    beta's contrary holds for the negative s, that reuse is the answer. If not,
    line 39 fails and line 17 moves to key2, which has the same facts and no
    relative assumption, so a fresh alpha guards it. Minting on key passes the
    checker in both halves, but Algorithm 1 never does it.
    """
    rng = random.Random(seed)
    names = rng.sample(_PRED_POOL, 5 + n_noise)
    t, key, key2, h, m, noise = (names[0], names[1], names[2], names[3],
                                 names[4], names[5:])
    exc = f"exc_{t}"
    consts, s, P, Ng, u = _heldout_layout(rng, n_constants, n_pos, n_neg)

    facts = (_fact_block(rng, key, [s] + P) + _fact_block(rng, key2, [s] + P)
             + _fact_block(rng, m, [s] if reuse_ok else [u])
             + _fact_block(rng, exc, [s, u]) + _noise_facts(rng, noise, consts))
    beta, ab_h = f"normal_{h}(X)", f"ab_{h}(X)"
    asm_t, ab_t = f"normal_{t}(X)", f"ab_{t}(X)"
    bg_rules = [Rule(f"{h}(X)", [f"{key}(X)", beta]), Rule(ab_h, [f"{m}(X)"]),
                Rule(ab_t, [f"{exc}(X)"])]
    target = (Rule(f"{t}(X)", [f"{key}(X)", beta]) if reuse_ok
              else Rule(f"{t}(X)", [f"{key2}(X)", asm_t]))
    problem = _finish(rng, facts, bg_rules, [target], [beta, asm_t],
                      {beta: ab_h, asm_t: ab_t}, t, P, Ng, consts,
                      [t, f"ab_{t}"], f"heldout_{t}")
    if problem is None:
        return None

    def minted(k):
        return ([Rule(f"{t}(X)", [f"{k}(X)", "alpha_0(X)"]),
                 Rule("c_alpha_0(X)", [f"{exc}(X)"])],
                {"alpha_0(X)": "c_alpha_0(X)"})
    answers = {"mint_on_key": minted(key)}
    if reuse_ok:
        answers["reuse"] = ([Rule(f"{t}(X)", [f"{key}(X)", beta])], {})
    else:
        answers["mint_on_key2"] = minted(key2)
    # Line 36 forbids minting on key under every fold order.
    return problem, {"half": "reuse_ok" if reuse_ok else "reuse_fails",
                     "expected": "reuse" if reuse_ok else "mint_on_key2",
                     "forbidden": ["mint_on_key"], "answers": answers}


def generate_heldout_problem(
    tier: Dict, variant: bool, seed: object,
) -> Optional[Tuple[LearningProblem, Dict]]:
    fn = (generate_heldout_decoy if tier["kind"] == "decoy"
          else generate_heldout_reuse)
    return fn(seed, variant, **tier["kwargs"])


def check_heldout(problem: LearningProblem, meta: Dict) -> Optional[str]:
    """None if every listed answer passes the checker and the reference returns
    the expected one; otherwise the reason."""
    from src.aba_algorithm import solve_aba_learning
    for name, (rules, contr) in meta["answers"].items():
        fw = problem.background.copy()
        fw.rules.extend(rules)
        fw.assumptions.extend(contr)
        fw.contraries.update(contr)
        if not check_brave_entailment(fw, problem.positive, problem.negative,
                                      problem.get_domain())[0]:
            return f"answer_{name}_not_a_solution"
    solution, trace = solve_aba_learning(problem)
    if solution is None or not trace.success:
        return "gen_failed"
    got = sorted(r.to_prolog() for r in solution.new_rules)
    want = sorted(r.to_prolog() for r in meta["answers"][meta["expected"]][0])
    return None if got == want else "reference_disagrees"


# ---------------------------------------------------------------------------
# Dataset class
# ---------------------------------------------------------------------------

@dataclass
class DatasetEntry:
    problem: LearningProblem
    solution: Optional[ABAFramework] = None
    trace: Optional[LearningTrace] = None
    source: str = "unknown"   # "benchmark" | "synthetic" | "zenodo"
    name_map: Optional[object] = None   # NameMap if the problem was anonymised


class ABADataset:
    def __init__(self):
        self.entries: List[DatasetEntry] = []

    def __len__(self) -> int:
        return len(self.entries)

    def __iter__(self) -> Iterator[DatasetEntry]:
        return iter(self.entries)

    def __getitem__(self, idx: int) -> DatasetEntry:
        return self.entries[idx]

    # ---- Loading -----------------------------------------------------------

    def load_builtin_benchmarks(self, solve: bool = True) -> None:
        """Load the hard-coded benchmark problems."""
        # Nixon diamond has a known solution
        problem, solution = make_nixon_diamond()
        self.entries.append(DatasetEntry(
            problem=problem, solution=solution, source="benchmark"
        ))
        # Others — solve with RoLe if requested
        for name, factory in [
            ("flies", make_flies_problem),
            ("tax_law", make_tax_law_problem),
        ]:
            p = factory()
            sol = None
            if solve:
                sol = self._solve_with_role(p)
            self.entries.append(DatasetEntry(
                problem=p, solution=sol, source="benchmark"
            ))

    def load_from_directory(self, base_dir: str, solve: bool = True) -> None:
        """
        Load all problems from subdirectories of base_dir.
        Each subdirectory should have background.pl and examples.pl.
        """
        base = Path(base_dir)
        for subdir in sorted(base.iterdir()):
            if subdir.is_dir():
                try:
                    problem = parse_learning_problem_from_dir(str(subdir))
                    sol = None
                    if solve:
                        sol = self._solve_with_role(problem)
                    self.entries.append(DatasetEntry(
                        problem=problem, solution=sol, source="zenodo"
                    ))
                except Exception as e:
                    print(f"Warning: could not load {subdir.name}: {e}")

    def add_synthetic(
        self,
        n: int = 100,
        seed: int = 42,
        solve: bool = True,
        **gen_kwargs,
    ) -> None:
        """Generate and add synthetic problems."""
        gen = SyntheticGenerator(seed=seed)
        problems = gen.generate_batch(n, **gen_kwargs)
        print(f"Generated {len(problems)} synthetic problems.")
        for p in problems:
            sol = None
            if solve:
                sol = self._solve_with_role(p)
            self.entries.append(DatasetEntry(
                problem=p, solution=sol, source="synthetic"
            ))

    def add_complex_synthetic(
        self,
        n: int = 5,
        seed: int = 99,
        solve: bool = True,
        **gen_kwargs,
    ) -> None:
        """
        Generate and add two-path (complex) synthetic problems.

        Each problem requires the LLM to discover two independent derivation
        rules for the same target predicate, each guarded by a separate
        defeasible assumption.  The richer argument structure causes DF-QuAD to
        produce genuinely intermediate sigma values instead of the binary 0/1
        pattern of single-path problems.
        """
        gen = SyntheticGenerator(seed=seed)
        problems = gen.generate_complex_batch(n, **gen_kwargs)
        print(f"Generated {len(problems)} complex (two-path) synthetic problems.")
        for p in problems:
            sol = None
            if solve:
                sol = self._solve_with_role(p)
            self.entries.append(DatasetEntry(
                problem=p, solution=sol, source="synthetic_complex"
            ))

    def add_benchmark_suite(
        self,
        n_per_tier: int = 10,
        seed: int = 42,
        solve: bool = True,
    ) -> None:
        """
        Generate the stratified benchmark suite for massive Task-1 testing.

        Each tier isolates ONE capability of the ABA-learning algorithm, so the
        per-tier gen@k breakdown tells you *which part* of the algorithm the LLM
        can replicate, not just an overall average:

          t1_mono     folding only — no exceptions, a monotonic rule suffices
          t2_defeas   assumption introduction — one exception must be defeated
          t3_noise    distractor robustness — extra irrelevant predicates
          t4_domain   domain-size scaling — 12 constants instead of 6
          t5_twopath  multiple derivation paths — two defeasible rules needed

        Problem ids carry the tier prefix (e.g. t2_defeas_0003) so results can
        be grouped per tier downstream. Each tier draws from an independently
        seeded generator, so tiers are reproducible in isolation.
        """
        for t_idx, tier in enumerate(BENCHMARK_TIERS):
            gen = SyntheticGenerator(seed=seed + 1000 * t_idx)
            if tier["kind"] == "complex":
                problems = gen.generate_complex_batch(n_per_tier, **tier["kwargs"])
            else:
                problems = gen.generate_batch(n_per_tier, **tier["kwargs"])
            for i, p in enumerate(problems):
                p.problem_id = f"{tier['name']}_{i:04d}"
                sol = None
                if solve:
                    sol = self._solve_with_role(p)
                self.entries.append(DatasetEntry(
                    problem=p, solution=sol, source=f"benchmark_{tier['name']}"
                ))
            print(f"  tier {tier['name']}: {len(problems)}/{n_per_tier} problems "
                  f"({tier['tests']})")

    # ---- Anonymisation -----------------------------------------------------

    def anonymize(
        self,
        scheme: str = "letters",
        anonymize_constants: bool = True,
    ) -> None:
        """Replace every problem with a symbol-anonymised copy, in place.

        Each predicate/constant is consistently renamed to an abstract symbol
        (p, q, ... / a, b, ...), stripping the semantic anchors an LLM might use
        to import external knowledge.  Solutions are cleared and the per-problem
        NameMap is stored on the entry (for later de-anonymised reporting); the
        symbolic baseline re-solves on the anonymised problems.  The rewrite is a
        bijection, so symbolic solvability is preserved.
        """
        from src.aba_anonymize import anonymize_problem
        for entry in self.entries:
            anon, nm = anonymize_problem(
                entry.problem, scheme=scheme,
                anonymize_constants=anonymize_constants,
            )
            entry.problem = anon
            entry.solution = None     # force a fresh symbolic solve downstream
            entry.trace = None
            entry.name_map = nm

    # ---- Solving -----------------------------------------------------------

    def _solve_with_role(
        self, problem: LearningProblem
    ) -> Optional[ABAFramework]:
        """
        Solve a problem using the RoLe phase and return the learned framework.
        Returns None if unsolvable.
        """
        new_facts, success, msg = run_rote_learning(problem)
        if not success:
            return None

        solution = problem.background.copy()
        solution.rules.extend(new_facts)
        solution.new_rules = new_facts
        return solution

    # ---- Filtering ---------------------------------------------------------

    def filter_solved(self) -> 'ABADataset':
        """Return a dataset containing only entries with known solutions."""
        ds = ABADataset()
        ds.entries = [e for e in self.entries if e.solution is not None]
        return ds

    def filter_by_source(self, source: str) -> 'ABADataset':
        ds = ABADataset()
        ds.entries = [e for e in self.entries if e.source == source]
        return ds

    # ---- Splitting ---------------------------------------------------------

    def split(
        self,
        train: float = 0.70,
        val: float = 0.15,
        test: float = 0.15,
        seed: int = 42,
    ) -> Tuple['ABADataset', 'ABADataset', 'ABADataset']:
        assert abs(train + val + test - 1.0) < 1e-6, "Splits must sum to 1."
        indices = list(range(len(self.entries)))
        rng = random.Random(seed)
        rng.shuffle(indices)

        n = len(indices)
        n_train = int(n * train)
        n_val = int(n * val)

        def _subset(idxs: List[int]) -> 'ABADataset':
            ds = ABADataset()
            ds.entries = [self.entries[i] for i in idxs]
            return ds

        return (
            _subset(indices[:n_train]),
            _subset(indices[n_train:n_train + n_val]),
            _subset(indices[n_train + n_val:]),
        )

    # ---- SFT serialisation -------------------------------------------------

    def to_sft_records(
        self,
        mode: str = "full",   # "full" | "guided"
    ) -> List[Dict]:
        """
        Serialise to instruction-following records for SFT.
        Only entries with solutions are included.
        """
        from src.aba_prompts import problem_to_prompt, solution_to_output_format
        records = []
        for entry in self.entries:
            if entry.solution is None:
                continue
            prompt = problem_to_prompt(entry.problem, mode=mode)
            output = solution_to_output_format(
                entry.solution, entry.problem.background
            )
            records.append({
                "problem_id": entry.problem.problem_id,
                "instruction": prompt,
                "output": output,
                "source": entry.source,
            })
        return records

    def save_sft_jsonl(self, path: str, mode: str = "full") -> None:
        records = self.to_sft_records(mode=mode)
        with open(path, 'w', encoding='utf-8') as f:
            for r in records:
                f.write(json.dumps(r) + '\n')
        print(f"Saved {len(records)} SFT records to {path}")

    # ---- Statistics --------------------------------------------------------

    def stats(self) -> Dict:
        n_solved = sum(1 for e in self.entries if e.solution is not None)
        sources = {}
        for e in self.entries:
            sources[e.source] = sources.get(e.source, 0) + 1
        avg_pos = (sum(len(e.problem.positive) for e in self.entries)
                   / max(len(self.entries), 1))
        avg_neg = (sum(len(e.problem.negative) for e in self.entries)
                   / max(len(self.entries), 1))
        avg_rules = (sum(len(e.problem.background.rules) for e in self.entries)
                     / max(len(self.entries), 1))
        return {
            "total": len(self.entries),
            "solved": n_solved,
            "by_source": sources,
            "avg_positive_examples": round(avg_pos, 2),
            "avg_negative_examples": round(avg_neg, 2),
            "avg_background_rules": round(avg_rules, 2),
        }