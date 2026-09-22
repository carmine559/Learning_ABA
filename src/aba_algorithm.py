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
from typing import List, Optional, Tuple, Dict, Callable

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


def assumption_introduction(
    folded_rule: Rule,
    background: ABAFramework,
    current: ABAFramework,
    problem: LearningProblem,
    learnt: List[Rule],
    new_asms: Dict[str, str],
    observer: Optional[Callable[..., None]] = None,
) -> Optional[Tuple[Rule, str, str, List[Rule]]]:
    """
    Attempt to recover a valid solution after folding broke brave entailment.

    Strategy (mirrors the paper's applyAsmIntro):
      1. Try using an existing assumption relative to the rule body.
      2. If none works, introduce a fresh assumption.

    `background` is the ORIGINAL background knowledge and `current` the
    framework as it stands (background + everything learnt so far). Keeping
    them apart matters: `learnt` already carries the rules under construction,
    so building the test framework from `current` would append them a second
    time — leaving the un-folded ground fact in place and making every
    satisfiability check below pass for the wrong reason.

    `observer`, when given, is a pure spectator with the same contract as
    `gen_phase`'s: it receives copies and its return value is ignored, so
    passing None (the default) leaves behaviour bit-for-bit unchanged.

    It exists because the fall-through from the reuse loop to the fresh branch
    below IS Algorithm 1's line 39 -> 41 backtrack, and it is otherwise
    invisible: the resulting TransformStep is identical in shape whether the
    assumption was reused or freshly minted, so no trace, scorer or stored
    result can tell the two branches apart. Distinguishing them matters because
    reuse-first (Definition 4) is the step the models were found NOT to take.

    Returns (defeasible_rule, asm_atom, contrary_atom, contrary_facts)
    or None on failure.
    """
    def _notify(kind: str, **extra) -> None:
        if observer is not None:
            observer(kind, list(learnt), dict(new_asms), -1, folded_rule, extra)

    dom = problem.get_domain()

    # ── 1. Try existing assumptions relative to body ──────────────────────────
    reusable = _assumptions_relative_to(folded_rule.body, current)
    _notify("asm_reuse_scan", candidates=list(reusable))
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
            return defeasible, asm, contrary, []

    # ── 2. Introduce a fresh assumption α_i(X) ────────────────────────────────
    # Reaching here is the line 39 -> 41 backtrack: every reusable assumption
    # above was tried and rejected (or there were none).
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
        return None

    _notify("asm_decision", mode="mint", asm=asm, contrary=contrary,
            rote_ok=True, contrary_facts=list(contrary_facts))
    return defeasible, asm, contrary, contrary_facts


# ──────────────────────────────────────────────────────────────────────────────
# Gen phase — orchestration
# ──────────────────────────────────────────────────────────────────────────────

def gen_phase(
    ground_facts: List[Rule],
    problem: LearningProblem,
    verbose: bool = False,
    observer: Optional[Callable[..., None]] = None,
) -> Tuple[ABAFramework, LearningTrace]:
    """
    Apply Fact Subsumption, Folding and Assumption Introduction to
    turn ground facts into an intensional solution.

    Returns (final_framework, trace).

    `observer`, when given, is called at every decision point with
    ``(kind, learnt, new_asms, idx, rule, extra)`` where `kind` is one of
    "subsume" / "fold" / "check" / "asm_intro". It is a pure spectator: it
    receives copies and its return value is ignored, so passing None (the
    default) leaves behaviour bit-for-bit unchanged.

    It exists so that the step probes in `aba_probes.py` can be built from the
    states this loop actually visits. Re-implementing the loop in a separate
    harvester would let the probe states drift away from the reference
    algorithm, which is the one thing that must not happen.
    """
    def _notify(kind: str, learnt, new_asms, idx, rule, **extra) -> None:
        if observer is not None:
            observer(kind, list(learnt), dict(new_asms), idx, rule, extra)

    background = problem.background
    dom = problem.get_domain()
    trace = LearningTrace(problem_id=problem.problem_id)

    # Working state
    learnt: List[Rule] = list(ground_facts)
    new_asms: Dict[str, str] = {}   # asm → contrary

    queue = list(range(len(learnt)))   # indices of facts to process

    while queue:
        idx = queue.pop(0)
        if idx >= len(learnt):
            continue
        rule = learnt[idx]

        if verbose:
            print(f"  Processing: {rule.to_prolog()}")

        # ── R4: Fact Subsumption ─────────────────────────────────────────────
        others = learnt[:idx] + learnt[idx + 1:]
        _subsumable = fact_subsumption(rule, background, others, new_asms, problem)
        _notify("subsume", learnt, new_asms, idx, rule, answer=_subsumable)
        if _subsumable:
            learnt.pop(idx)
            queue = [i - 1 if i > idx else i for i in queue]
            trace.steps.append(TransformStep(
                step_type="fact_subsumption",
                input_rule=rule,
                note="redundant, removed",
            ))
            if verbose:
                print(f"    -> Subsumption: removed.")
            _notify("fact_done", learnt, new_asms, idx, rule, outcome="subsumed")
            continue

        # ── R2: Folding ──────────────────────────────────────────────────────
        if not _is_ground_fact(rule):
            # Already intensional — nothing to fold
            _notify("fact_done", learnt, new_asms, idx, rule,
                    outcome="already_intensional")
            continue

        # Traced variant: same candidates in the same order, plus the
        # background rule(s) folded in to reach each one. The algorithm still
        # runs on the plain list, so this is inert.
        folds_traced = apply_folding_traced(rule, background)
        fold_candidates = [r for r, _ in folds_traced]
        accepted = False
        _notify("fold", learnt, new_asms, idx, rule,
                candidates=list(fold_candidates),
                via=[list(chain) for _, chain in folds_traced])

        # Pass 1: try direct folding (no assumption needed)
        for folded in fold_candidates:
            test_learnt = learnt[:idx] + [folded] + learnt[idx + 1:]
            fw = _current_framework(background, test_learnt, new_asms)
            sat, _, _ = check_brave_entailment(
                fw, problem.positive, problem.negative, dom
            )
            _notify("check", learnt, new_asms, idx, rule, folded=folded, answer=sat)
            if sat:
                trace.steps.append(TransformStep(
                    step_type="folding",
                    input_rule=rule,
                    output_rule=folded,
                    note="valid after folding",
                ))
                learnt[idx] = folded
                if verbose:
                    print(f"    -> Folded: {folded.to_prolog()}")
                accepted = True
                break

        # Pass 2: if no direct fold worked, try assumption introduction
        #         on EACH fold candidate, keeping the best result
        if not accepted:
            fw_now = _current_framework(background, learnt, new_asms)
            for folded in fold_candidates:
                test_learnt = learnt[:idx] + [folded] + learnt[idx + 1:]
                result = assumption_introduction(
                    folded, background, fw_now, problem, test_learnt, new_asms,
                    observer=observer,
                )
                _notify("asm_intro", learnt, new_asms, idx, rule,
                        folded=folded, answer=result)
                if result is not None:
                    defeasible, asm, contrary, contra_facts = result
                    learnt[idx] = defeasible
                    new_asms[asm] = contrary
                    for cf in contra_facts:
                        learnt.append(cf)
                        queue.append(len(learnt) - 1)
                    trace.steps.append(TransformStep(
                        step_type="assumption_introduction",
                        input_rule=rule,
                        output_rule=defeasible,
                        new_assumption=asm,
                        new_contrary_facts=contra_facts,
                        note=f"new assumption {asm} -> {contrary}",
                    ))
                    if verbose:
                        print(f"    -> AsmIntro: {defeasible.to_prolog()}")
                        print(f"       new asm: {asm} -> {contrary}")
                    accepted = True
                    break

        if not accepted and verbose:
            print(f"    -> No successful folding found; kept as ground fact.")

        # The "kept as ground fact" outcome was previously a verbose-only print,
        # so a fact the algorithm failed to generalise left NO record at all —
        # the trace simply lacked an entry for it. Distinguishing that from a
        # successful fold matters for scoring R1 residue end-to-end.
        _notify("fact_done", learnt, new_asms, idx, rule,
                outcome=("folded_with_assumption"
                         if accepted and trace.steps
                         and trace.steps[-1].step_type == "assumption_introduction"
                         else "folded" if accepted else "kept_ground"))

    # Build final framework
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
