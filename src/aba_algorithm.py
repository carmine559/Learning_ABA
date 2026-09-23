"""
aba_algorithm.py
Symbolic implementation of the Gen phase of ASP-ABAlearnB.

Implements:
  - Fact Subsumption  (R4)
  - Folding           (R2)
  - Assumption Introduction (R3)
  - gen_phase():  orchestrates R2 → R3 → R4 for each learnt ground fact
"""
from __future__ import annotations
import re
import copy
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Callable, Iterator

from src.aba_types import Rule, ABAFramework, LearningProblem, TransformStep, LearningTrace
from src.aba_validator import (
    check_brave_entailment,
    check_has_stable_extension,
    run_rote_learning,
    _build_asp,
    _solve,
)


# ──────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ──────────────────────────────────────────────────────────────────────────────

_EQ_RE   = re.compile(r'^([A-Z]\w*)\s*=\s*([a-z]\w*)$')   # X = const
_HEAD_RE = re.compile(r'^([a-z]\w*)\(([A-Z]\w*)\)$')       # pred(Var)
_FACT_RE = re.compile(r'^([a-z]\w*)\(([a-z]\w*)\)$')       # pred(const)


def _extract_eq(body: List[str]) -> Optional[Tuple[str, str, int]]:
    """
    Find the first equality 'VAR = const' in body.
    Returns (var, const, index) or None.
    """
    for i, atom in enumerate(body):
        m = _EQ_RE.match(atom.strip())
        if m:
            return m.group(1), m.group(2), i
    return None


def _is_ground_fact(rule: Rule) -> bool:
    """True if rule is of the form  p(X) :- X = t."""
    if len(rule.body) != 1:
        return False
    return bool(_EQ_RE.match(rule.body[0].strip()))


def _current_framework(
    background: ABAFramework,
    learnt: List[Rule],
    new_asms: Dict[str, str],
) -> ABAFramework:
    # Reusing an existing assumption (Definition 4) does not introduce a new
    # one — list it once, and report only genuinely fresh assumptions as new,
    # so the symbolic side and the LLM parser agree on what "new" means.
    genuinely_new = [a for a in new_asms if a not in background.assumptions]
    fw = background.copy()
    fw.rules = background.rules + learnt
    fw.assumptions = background.assumptions + genuinely_new
    fw.contraries = {**background.contraries, **new_asms}
    fw.new_rules = learnt
    fw.new_assumptions = genuinely_new
    return fw


# ──────────────────────────────────────────────────────────────────────────────
# R4 — Fact Subsumption
# ──────────────────────────────────────────────────────────────────────────────

def fact_subsumption(
    rule: Rule,
    background: ABAFramework,
    learnt_without_rule: List[Rule],
    new_asms: Dict[str, str],
    problem: LearningProblem,
) -> bool:
    """
    Return True if *rule* can be safely removed (is redundant).
    """
    fw = _current_framework(background, learnt_without_rule, new_asms)
    dom = problem.get_domain()
    sat, _, _ = check_brave_entailment(
        fw, problem.positive, problem.negative, dom
    )
    return sat


# ──────────────────────────────────────────────────────────────────────────────
# R2 — Folding
# ──────────────────────────────────────────────────────────────────────────────

def _candidate_folds_traced(
    rule: Rule,
    background: ABAFramework,
) -> List[Tuple[Rule, Rule]]:
    """
    Given a (possibly non-intensional) rule, return all candidate
    rules obtainable by one application of the Folding transformation,
    each paired with the BACKGROUND RULE that produced it.

    Strategy: for every equality  VAR = const  in the body, find
    background rules whose head  pred(VAR)  would be implied if
    VAR=const — i.e. whose body includes  VAR=const  or whose
    head is the ground fact  pred(const).

    The paired rule is the paper's rho2 — the rule used for folding. It is not
    recorded on `TransformStep.folding_rule`, which stays None: writing it would
    change `LearningTrace.to_dict()` and break the golden master that pins this
    algorithm against the committed set-05 traces. The provenance is carried
    here instead, for the trace log to pick up.

    `_candidate_folds` below is the plain-rule view of this function and is what
    the algorithm itself uses; the two must stay in lockstep, including ORDER,
    because `gen_phase` accepts the first candidate that passes its check.
    """
    eq_info = _extract_eq(rule.body)
    if eq_info is None:
        return []                    # already intensional

    var, const, eq_idx = eq_info
    candidates: List[Tuple[Rule, Rule]] = []
    seen_bodies: set = set()

    for bg in background.rules:
        head_m = _HEAD_RE.match(bg.head.strip())
        fact_m = _FACT_RE.match(bg.head.strip())

        # ── Case A: bg head is  pred(Var)  and body includes  Var = const
        if head_m:
            bg_var = head_m.group(2)
            bg_pred = head_m.group(1)
            bg_eq_atom = f"{bg_var} = {const}"
            if bg_eq_atom in [a.strip() for a in bg.body]:
                # Remaining bg body (minus the equality, normalised to our var).
                # Rename on word boundaries: a bare str.replace would also
                # rewrite 'X' inside 'X1' or any identifier containing it.
                _rename = re.compile(rf'\b{re.escape(bg_var)}\b')
                remaining_bg = [
                    _rename.sub(var, a)
                    for a in bg.body
                    if a.strip() != bg_eq_atom
                ]
                new_body = (
                    [a for a in rule.body if a.strip() != rule.body[eq_idx].strip()]
                    + remaining_bg
                    + [f"{bg_pred}({var})"]
                )
                key = tuple(sorted(new_body))
                if key not in seen_bodies:
                    seen_bodies.add(key)
                    candidates.append((Rule(head=rule.head, body=new_body), bg))

        # ── Case B: bg is a ground fact  pred(const)
        elif fact_m and fact_m.group(2) == const and not bg.body:
            bg_pred = fact_m.group(1)
            new_body = (
                [a for a in rule.body if a.strip() != rule.body[eq_idx].strip()]
                + [f"{bg_pred}({var})"]
            )
            key = tuple(sorted(new_body))
            if key not in seen_bodies:
                seen_bodies.add(key)
                candidates.append((Rule(head=rule.head, body=new_body), bg))

    # dom(X) <- X = c is in R for every constant (paper, Definition 3).
    new_body = ([a for a in rule.body if a.strip() != rule.body[eq_idx].strip()]
                + [f"dom({var})"])
    key = tuple(sorted(new_body))
    if key not in seen_bodies:
        seen_bodies.add(key)
        candidates.append((Rule(head=rule.head, body=new_body),
                           Rule(head=f"dom({const})", body=[])))

    return candidates


def _candidate_folds(rule: Rule, background: ABAFramework) -> List[Rule]:
    """One folding step, candidates only — the view the algorithm runs on."""
    return [c for c, _ in _candidate_folds_traced(rule, background)]


def apply_folding_traced(
    rule: Rule,
    background: ABAFramework,
    max_depth: int = 4,
) -> List[Tuple[Rule, List[Rule]]]:
    """
    Exhaustively fold *rule* (up to max_depth steps) using background rules.
    Returns intensional candidates, shortest first, each paired with the CHAIN
    of background rules folded in to reach it (one entry per step, in order).

    A depth-2 fold therefore reports both rho2's. Note that `gen_phase` records
    such a chain as a SINGLE `TransformStep`, so the chain is the only place the
    intermediate step survives.
    """
    frontier: List[Tuple[Rule, List[Rule]]] = [(rule, [])]
    intensional: List[Tuple[Rule, List[Rule]]] = []
    # Track rules already in the frontier to avoid re-adding, but
    # do NOT pre-mark candidates as visited before we process them.
    queued = {rule.to_prolog()}

    for _ in range(max_depth):
        next_frontier: List[Tuple[Rule, List[Rule]]] = []
        for r, chain in frontier:
            if _extract_eq(r.body) is None:
                # This rule is already intensional — collect it.
                intensional.append((r, chain))
            else:
                for candidate, via in _candidate_folds_traced(r, background):
                    key = candidate.to_prolog()
                    if key not in queued:
                        queued.add(key)
                        next_frontier.append((candidate, chain + [via]))
        frontier = next_frontier
        if not frontier:
            break

    # Deduplicate while preserving order
    seen: set = set()
    result: List[Tuple[Rule, List[Rule]]] = []
    for r, chain in intensional:
        k = r.to_prolog()
        if k not in seen:
            seen.add(k)
            result.append((r, chain))
    return result


def apply_folding(
    rule: Rule,
    background: ABAFramework,
    max_depth: int = 4,
) -> List[Rule]:
    """
    Exhaustively fold *rule* (up to max_depth steps) using background rules.
    Returns a list of intensional candidates, shortest first.
    """
    return [r for r, _ in apply_folding_traced(rule, background, max_depth)]


# ──────────────────────────────────────────────────────────────────────────────
# R3 — Assumption Introduction
# ──────────────────────────────────────────────────────────────────────────────

_ASM_VAR_RE = re.compile(r'^([a-z]\w*)\(([A-Z]\w*)\)$')


def _assumptions_relative_to(
    body: List[str],
    framework: ABAFramework,
) -> List[str]:
    """
    Return assumptions α(X) ∈ A that are *relative to* `body`:
    i.e. there exists a rule  H :- ...body..., α(X)  in R.
    """
    body_set = set(a.strip() for a in body)
    relative = []
    for rule in framework.rules:
        rule_body_set = set(a.strip() for a in rule.body)
        for asm in framework.assumptions:
            if asm in rule_body_set:
                other_atoms = rule_body_set - {asm}
                if other_atoms <= body_set:
                    relative.append(asm)
    return list(dict.fromkeys(relative))   # deduplicated, preserving order


def _new_assumption_name(existing: List[str]) -> Tuple[str, str]:
    """Return (assumption_atom, contrary_atom) with a fresh predicate name."""
    idx = sum(1 for a in existing if re.match(r'^alpha_\d+\(', a))
    asm = f"alpha_{idx}(X)"
    contrary = f"c_alpha_{idx}(X)"
    return asm, contrary


def asm_intro_options(
    folded_rule: Rule,
    background: ABAFramework,
    current: ABAFramework,
    problem: LearningProblem,
    learnt: List[Rule],
    new_asms: Dict[str, str],
    observer: Optional[Callable[..., None]] = None,
) -> Iterator[Tuple[Rule, str, str, List[Rule]]]:
    """
    Every way `applyAsmIntro` can guard `folded_rule`, yielded lazily in order.

    Algorithm 1 (De Angelis, Proietti & Toni, arXiv:2408.10126v2):

        37 if there exists alpha(X) in A relative to B then
        38   rho := H <- B, alpha(X);  S := {}
        39   if not sat(ASP(<R u {rho}, A, ->, <E+, E->, {})) then
        40     fail
        41   end if
        42 else  /* introduce an assumption alpha(X) */
        43-45  rho := H <- B, alpha(X);  S := getAS(...)
        46 end if

    and the paper, on line 40: "If it uses an assumption alpha(X) already
    belonging to A (see line 37 and Definition 4) and it does not obtain a
    solution, then it gets a failure (see line 40) and backtracks to the most
    recent choice point."

    So there are exactly two cases, and they do not fall through into each
    other:
      * Some assumption is relative to the body (Definition 4). The choice of
        WHICH one is a choice point, so each relative assumption that yields a
        solution is one option, in order. If none does, there are NO options —
        that is the line-40 failure, and the caller backtracks to its own
        previous choice (another fold, or an earlier fact).
      * None is relative to the body. Then, and only then, a fresh assumption
        is minted, with its contrary's facts computed by RoLe.

    An earlier version minted a fresh assumption after a failed reuse, calling
    that "the line 39 -> 41 backtrack". The pseudo-code has no such transition.
    On the paper's own Nixon problem (Examples 1 and 10) that version learnt
    `abnormal_quaker(X) :- quaker(X), alpha(X)`, a step Algorithm 1 cannot take
    because `normal_quaker` is relative to `quaker(X)`; the paper learns
    `abnormal_quaker(X) :- republican(X), alpha(X)`.

    `background` is the ORIGINAL background knowledge and `current` the
    framework as it stands (background + everything learnt so far). Keeping
    them apart matters: `learnt` already carries the rules under construction,
    so building the test framework from `current` would append them a second
    time — leaving the un-folded ground fact in place and making every
    satisfiability check below pass for the wrong reason.

    `observer`, when given, is a pure spectator with the same contract as
    `gen_phase`'s: it receives copies and its return value is ignored. It is
    how the branch taken — reuse, mint, or the line-40 failure — becomes
    visible: the resulting TransformStep has the same shape whether the
    assumption was reused or minted.

    Yields (defeasible_rule, asm_atom, contrary_atom, contrary_facts).
    """
    def _notify(kind: str, **extra) -> None:
        if observer is not None:
            observer(kind, list(learnt), dict(new_asms), -1, folded_rule, extra)

    dom = problem.get_domain()

    # ── Lines 37-41: an assumption relative to the body exists ────────────────
    reusable = _assumptions_relative_to(folded_rule.body, current)
    _notify("asm_reuse_scan", candidates=list(reusable))
    if reusable:
        for asm in reusable:
            defeasible = Rule(
                head=folded_rule.head,
                body=folded_rule.body + [asm],
            )
            candidate_asms = dict(new_asms)
            test_learnt = [r for r in learnt
                           if r.to_prolog() != folded_rule.to_prolog()] + [defeasible]
            fw = _current_framework(background, test_learnt, candidate_asms)
            sat, _, _ = check_brave_entailment(
                fw, problem.positive, problem.negative, dom
            )
            _notify("asm_reuse_try", asm=asm, answer=sat)
            if sat:
                contrary = current.contraries.get(asm, f"c_{asm}")
                _notify("asm_decision", mode="reuse", asm=asm, contrary=contrary)
                yield defeasible, asm, contrary, []
        # Line 40. Every relative assumption is exhausted: no R3 on this body.
        _notify("asm_decision", mode="fail", asm=None)
        return

    # ── Lines 42-45: none is relative, so introduce a fresh one ───────────────
    all_asms = list(dict.fromkeys(background.assumptions + list(new_asms.keys())))
    asm, contrary = _new_assumption_name(all_asms)
    defeasible = Rule(
        head=folded_rule.head,
        body=folded_rule.body + [asm],
    )

    # Find minimal contrary facts via clingo
    tmp_new_asms = {**new_asms, asm: contrary}
    test_learnt = [r for r in learnt
                   if r.to_prolog() != folded_rule.to_prolog()] + [defeasible]
    tmp_fw = _current_framework(background, test_learnt, tmp_new_asms)

    contra_pred = re.match(r'^([a-z]\w*)', contrary).group(1)
    rote_problem = LearningProblem(
        background=tmp_fw,
        positive=problem.positive,
        negative=problem.negative,
        learnable=[contra_pred],
        domain=dom,
        problem_id=problem.problem_id + "_asm_intro",
    )
    contrary_facts, ok, _ = run_rote_learning(rote_problem)
    if not ok:
        _notify("asm_decision", mode="mint", asm=asm, contrary=contrary,
                rote_ok=False)
        return

    _notify("asm_decision", mode="mint", asm=asm, contrary=contrary,
            rote_ok=True, contrary_facts=list(contrary_facts))
    yield defeasible, asm, contrary, contrary_facts


def assumption_introduction(
    folded_rule: Rule,
    background: ABAFramework,
    current: ABAFramework,
    problem: LearningProblem,
    learnt: List[Rule],
    new_asms: Dict[str, str],
    observer: Optional[Callable[..., None]] = None,
) -> Optional[Tuple[Rule, str, str, List[Rule]]]:
    """The first option `asm_intro_options` offers, or None if it offers none.

    None now also covers the line-40 failure: an assumption relative to the
    body exists but none yields a solution, so there is no assumption
    introduction on this body at all.
    """
    return next(asm_intro_options(folded_rule, background, current, problem,
                                  learnt, new_asms, observer), None)


# ──────────────────────────────────────────────────────────────────────────────
# Gen phase — orchestration
# ──────────────────────────────────────────────────────────────────────────────

class _SearchBudgetExceeded(Exception):
    """Gen's backtracking search applied more options than it is allowed."""


# Option applications allowed before Gen gives up. The paper's search is
# exponential in the worst case; this only exists so corpus generation cannot
# hang. A problem that hits it FAILS (it is not silently kept), and the
# observer receives "search_budget_exceeded" so a corpus can log the reason.
GEN_SEARCH_BUDGET = 5000


def gen_phase(
    ground_facts: List[Rule],
    problem: LearningProblem,
    verbose: bool = False,
    observer: Optional[Callable[..., None]] = None,
    search_budget: int = GEN_SEARCH_BUDGET,
) -> Tuple[ABAFramework, LearningTrace]:
    """
    Apply Fact Subsumption, Folding and Assumption Introduction to
    turn ground facts into an intensional solution.

    Returns (final_framework, trace).

    SEARCH. Algorithm 1 is nondeterministic: which fold to apply (lines 31-32)
    and which relative assumption to reuse (line 37) are choice points, and a
    failure (line 40) "backtracks to the most recent choice point". This is a
    depth-first search over those choices, fact by fact in queue order. For
    each learnt ground fact the options are tried lazily, in a fixed order:

      pass 1  every fold candidate that is a solution on its own, in order;
      pass 2  assumption introduction on each fold that is not, in order,
              each yielding whatever `asm_intro_options` offers.

    The first option whose continuation succeeds is kept. If none does, the
    fact FAILS and the search backtracks into the previous fact's remaining
    options. That order is one resolution of the paper's nondeterminism: every
    run it completes is a legal execution of Algorithm 1.

    Two behaviours changed when this became a search, both toward the paper:
      * after a failed reuse the old loop minted a fresh assumption on the SAME
        fold; now that fold has no R3 option (line 40), see
        `asm_intro_options`;
      * a fact with no working option used to be "kept as ground fact" and the
        loop moved on; now the fact fails and the search backtracks.
    Neither occurs on 101 of the 103 problems set 05 was scored on, and on
    those the search visits exactly the states the loop did, in the same
    order, with the same Clingo calls. `tests/test_golden_traces.py` pins this.

    TRACE. `trace.steps` is the SUCCESSFUL path only, as in the paper's own
    worked derivations. Abandoned branches reach the observer, never the trace.
    On total failure `trace.success` is False and `trace.steps` is empty.

    `observer`, when given, is called at every decision point with
    ``(kind, learnt, new_asms, idx, rule, extra)``, where `learnt`/`new_asms`
    are the state BEFORE the fact's option is applied (except `fact_done`,
    which gets the state after). Kinds: "subsume", "fold", "check",
    "asm_reuse_scan", "asm_reuse_try", "asm_decision", "asm_intro",
    "fact_done", and, for the search, "backtrack" (an option's continuation
    failed; the fact's remaining options are tried next), "fact_failed" (the
    fact has none left) and "search_budget_exceeded". It is a pure spectator:
    it receives copies and its return value is ignored.

    It exists so that the step probes in `aba_probes.py` can be built from the
    states this search actually visits. Re-implementing the search in a
    separate harvester would let the probe states drift away from the reference
    algorithm, which is the one thing that must not happen.
    """
    def _notify(kind: str, learnt, new_asms, idx, rule, **extra) -> None:
        if observer is not None:
            observer(kind, list(learnt), dict(new_asms), idx, rule, extra)

    background = problem.background
    dom = problem.get_domain()
    applied = [0]

    def _options(learnt: List[Rule], new_asms: Dict[str, str], idx: int,
                 rule: Rule):
        """The fact's choices, lazily, in the order documented above."""
        # Traced variant: same candidates in the same order, plus the
        # background rule(s) folded in to reach each one.
        folds_traced = apply_folding_traced(rule, background)
        fold_candidates = [r for r, _ in folds_traced]
        _notify("fold", learnt, new_asms, idx, rule,
                candidates=list(fold_candidates),
                via=[list(chain) for _, chain in folds_traced])

        # Pass 1: folds that are a solution without an assumption (line 18).
        not_solutions: List[Rule] = []
        for folded in fold_candidates:
            test_learnt = learnt[:idx] + [folded] + learnt[idx + 1:]
            fw = _current_framework(background, test_learnt, new_asms)
            sat, _, _ = check_brave_entailment(
                fw, problem.positive, problem.negative, dom
            )
            _notify("check", learnt, new_asms, idx, rule, folded=folded, answer=sat)
            if sat:
                yield "folding", folded, None
            else:
                not_solutions.append(folded)

        # Pass 2: assumption introduction on each fold that is not (line 19).
        fw_now = _current_framework(background, learnt, new_asms)
        for folded in not_solutions:
            test_learnt = learnt[:idx] + [folded] + learnt[idx + 1:]
            offered = False
            for result in asm_intro_options(folded, background, fw_now, problem,
                                            test_learnt, new_asms,
                                            observer=observer):
                offered = True
                _notify("asm_intro", learnt, new_asms, idx, rule,
                        folded=folded, answer=result)
                yield "assumption_introduction", folded, result
            if not offered:
                _notify("asm_intro", learnt, new_asms, idx, rule,
                        folded=folded, answer=None)

    def _search(learnt: List[Rule], new_asms: Dict[str, str],
                queue: List[int], steps: List[TransformStep]):
        """Process the queue from this state; the successful end state, or None."""
        while queue:
            idx, queue = queue[0], queue[1:]
            if idx >= len(learnt):
                continue
            rule = learnt[idx]

            if verbose:
                print(f"  Processing: {rule.to_prolog()}")

            # ── R4: Fact Subsumption (line 16) — deterministic, no choice ───
            others = learnt[:idx] + learnt[idx + 1:]
            _subsumable = fact_subsumption(rule, background, others, new_asms, problem)
            _notify("subsume", learnt, new_asms, idx, rule, answer=_subsumable)
            if _subsumable:
                learnt = others
                queue = [i - 1 if i > idx else i for i in queue]
                steps = steps + [TransformStep(
                    step_type="fact_subsumption",
                    input_rule=rule,
                    note="redundant, removed",
                )]
                if verbose:
                    print(f"    -> Subsumption: removed.")
                _notify("fact_done", learnt, new_asms, idx, rule, outcome="subsumed")
                continue

            if not _is_ground_fact(rule):
                # Already intensional — nothing to fold
                _notify("fact_done", learnt, new_asms, idx, rule,
                        outcome="already_intensional")
                continue

            # ── R2 / R3: a choice point ─────────────────────────────────────
            for kind, folded, result in _options(learnt, new_asms, idx, rule):
                applied[0] += 1
                if applied[0] > search_budget:
                    _notify("search_budget_exceeded", learnt, new_asms, idx,
                            rule, budget=search_budget)
                    raise _SearchBudgetExceeded()

                if kind == "folding":
                    next_learnt = learnt[:idx] + [folded] + learnt[idx + 1:]
                    next_asms, next_queue = new_asms, queue
                    step = TransformStep(
                        step_type="folding",
                        input_rule=rule,
                        output_rule=folded,
                        note="valid after folding",
                    )
                    outcome = "folded"
                    if verbose:
                        print(f"    -> Folded: {folded.to_prolog()}")
                else:
                    defeasible, asm, contrary, contra_facts = result
                    next_learnt = (learnt[:idx] + [defeasible] + learnt[idx + 1:]
                                   + list(contra_facts))
                    next_asms = {**new_asms, asm: contrary}
                    next_queue = queue + list(range(
                        len(learnt), len(learnt) + len(contra_facts)))
                    step = TransformStep(
                        step_type="assumption_introduction",
                        input_rule=rule,
                        output_rule=defeasible,
                        new_assumption=asm,
                        new_contrary_facts=contra_facts,
                        note=f"new assumption {asm} -> {contrary}",
                    )
                    outcome = "folded_with_assumption"
                    if verbose:
                        print(f"    -> AsmIntro: {defeasible.to_prolog()}")
                        print(f"       new asm: {asm} -> {contrary}")

                _notify("fact_done", next_learnt, next_asms, idx, rule,
                        outcome=outcome)
                found = _search(next_learnt, next_asms, next_queue,
                                steps + [step])
                if found is not None:
                    return found
                _notify("backtrack", learnt, new_asms, idx, rule)
                if verbose:
                    print(f"    <- Backtrack to: {rule.to_prolog()}")

            if verbose:
                print(f"    -> No option works for {rule.to_prolog()}; backtracking.")
            _notify("fact_failed", learnt, new_asms, idx, rule)
            return None

        return learnt, new_asms, steps

    trace = LearningTrace(problem_id=problem.problem_id)
    try:
        found = _search(list(ground_facts), {}, list(range(len(ground_facts))), [])
    except _SearchBudgetExceeded:
        found = None

    if found is None:
        # Algorithm 1 terminates with failure (Theorem 4).
        final = _current_framework(background, list(ground_facts), {})
        trace.final_framework = final
        trace.success = False
        return final, trace

    learnt, new_asms, steps = found
    trace.steps = steps
    final = _current_framework(background, learnt, new_asms)
    trace.final_framework = final
    trace.success = check_brave_entailment(
        final, problem.positive, problem.negative, dom
    )[0]

    return final, trace


# ──────────────────────────────────────────────────────────────────────────────
# Full solver  (RoLe + Gen)
# ──────────────────────────────────────────────────────────────────────────────

def solve_aba_learning(
    problem: LearningProblem,
    verbose: bool = False,
    observer: Optional[Callable[..., None]] = None,
) -> Tuple[Optional[ABAFramework], LearningTrace]:
    """
    Full ASP-ABAlearnB pipeline: RoLe → Gen.
    Returns (solution_or_None, trace).

    `observer` is forwarded to `gen_phase` and to `assumption_introduction`,
    and additionally receives the RoLe facts as a "role" notification so that
    R1 provenance arrives on the same stream as everything else. It is a pure
    spectator: None (the default) is bit-for-bit the original behaviour, which
    `tests/test_golden_traces.py` pins against the committed set-05 traces.

    Before this parameter existed the observer could only be attached to
    `gen_phase` directly, so the code path that writes `symbolic_traces.jsonl`
    never materialised any of the algorithm's decisions.
    """
    trace = LearningTrace(problem_id=problem.problem_id)

    # Phase 1: RoLe
    if verbose:
        print(f"[RoLe] {problem.problem_id}")
    facts, ok, msg = run_rote_learning(problem)
    if not ok:
        trace.success = False
        return None, trace

    for f in facts:
        trace.steps.append(TransformStep(
            step_type="rote_learning", output_rule=f
        ))
    if observer is not None:
        observer("role", list(facts), {}, -1, None, {"facts": list(facts)})
    if verbose:
        print(f"  {msg}")
        for f in facts:
            print(f"  + {f.to_prolog()}")

    # Phase 2: Gen
    if verbose:
        print(f"[Gen]")
    solution, gen_trace = gen_phase(facts, problem, verbose=verbose,
                                    observer=observer)
    trace.steps.extend(gen_trace.steps)
    trace.final_framework = solution
    trace.success = gen_trace.success

    return (solution if gen_trace.success else None), trace
