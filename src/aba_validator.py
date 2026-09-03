"""
aba_validator.py  (refactored)
Clingo Python-API based validation and the RoLe phase.
Implements the ASP encoding from Definition 2 of De Angelis et al. 2024.
"""
from __future__ import annotations
import re
import time
from typing import List, Tuple, Optional, Dict

import clingo

from src.aba_types import Rule, ABAFramework, LearningProblem


# ──────────────────────────────────────────────────────────────────────────────
# ASP program builder  (Definition 2)
# ──────────────────────────────────────────────────────────────────────────────

def _build_asp(
    framework: ABAFramework,
    positive: List[str],
    negative: List[str],
    domain: List[str],
    learnable: Optional[List[str]] = None,
    minimize: bool = False,
) -> str:
    lines: List[str] = []

    # (a) domain facts
    for c in domain:
        lines.append(f"dom({c}).")

    # (a) rules
    for rule in framework.rules:
        lines.append(rule.to_prolog())

    # (b) assumptions  α :- dom(X), not c_α.
    # dom/1 is unary, so an n-ary assumption needs one guard per argument;
    # a propositional assumption needs no guard at all (a dom(X) with X
    # unbound elsewhere would existentially quantify over the whole domain).
    for asm in framework.assumptions:
        contrary = framework.contraries.get(asm, f"c_{asm}")
        m = re.search(r'\((.+)\)', asm)
        args = [a.strip() for a in m.group(1).split(',')] if m else []
        guards = "".join(f"dom({a}), " for a in args if a and a[:1].isupper())
        lines.append(f"{asm} :- {guards}not {contrary}.")

    # (c) positive constraints
    for e in positive:
        lines.append(f":- not {e}.")

    # (d) negative constraints
    for e in negative:
        lines.append(f":- {e}.")

    # (e) learnable choice rules
    if learnable:
        for pred in learnable:
            prime = f"{pred}_prime"
            lines.append(f"{pred}(X) :- {prime}(X).")
            lines.append(f"{{{prime}(X)}} :- dom(X).")
            if minimize:
                # The predicate MUST be part of the tuple: #minimize aggregates
                # over the SET of tuples, so a bare {1,X} makes p(c) and q(c)
                # cost 1 between them instead of 2, and RoLe stops being minimal
                # as soon as |T| > 1.
                lines.append(f"#minimize{{1,X,{pred} : {prime}(X)}}.")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────────
# Internal: run clingo and return (satisfiable, list_of_atom_sets, elapsed)
# ──────────────────────────────────────────────────────────────────────────────

def _silent_logger(code, message: str) -> None:
    """Drop all Clingo diagnostic messages (info, warning, error).
    We handle errors via RuntimeError exceptions instead."""
    pass


def _solve(
    program: str,
    n_models: int = 1,
    opt_mode: bool = False,
    timeout: int = 30,
) -> Tuple[bool, List[List[str]], float]:
    """
    Run clingo on *program*.
    Returns (satisfiable, answer_sets, elapsed_s).
    Each answer_set is a list of atom strings.

    Returns (False, [], elapsed) on any parse or runtime error so that
    callers never crash — an invalid ASP program is treated as unsatisfiable.
    """
    t0 = time.time()
    # Clingo's C->Python logger bridge decodes diagnostic messages as UTF-8 and
    # crashes on stray non-UTF-8 bytes that can appear in mangled LLM output.
    # Force the program to clean ASCII before it ever reaches Clingo. Any rule
    # containing a non-ASCII byte was malformed anyway, so this only affects
    # text that would have been rejected.
    program = program.encode("ascii", "ignore").decode("ascii")
    flags = ["--models=0", "--opt-mode=optN"] if opt_mode else [f"--models={n_models}"]
    try:
        ctl = clingo.Control(flags, logger=_silent_logger)
        # ── parse phase ── most likely to fail when LLM output leaks into program
        ctl.add("base", [], program)
        # ── ground phase ──
        ctl.ground([("base", [])])
    except RuntimeError:
        # Clingo could not parse or ground the program.
        # Treat as unsatisfiable rather than crashing the evaluation loop.
        return False, [], time.time() - t0

    models: List[List[str]] = []
    try:
        # Asynchronous solve so the timeout is actually enforced.
        with ctl.solve(yield_=True, async_=True) as handle:
            while True:
                handle.resume()
                finished = handle.wait(timeout)
                if not finished:
                    handle.cancel()
                    # Partial results (if any) are still usable for opt mode.
                    break
                model = handle.model()
                if model is None:
                    break
                models.append([str(s) for s in model.symbols(shown=True)])
            sat = handle.get().satisfiable
    except RuntimeError:
        sat = False

    return sat, models, time.time() - t0


# ──────────────────────────────────────────────────────────────────────────────
# Public validation API
# ──────────────────────────────────────────────────────────────────────────────

def check_brave_entailment(
    framework: ABAFramework,
    positive: List[str],
    negative: List[str],
    domain: Optional[List[str]] = None,
    timeout: int = 30,
) -> Tuple[bool, str, float]:
    """
    Returns (valid, message, clingo_elapsed_s).
    valid = True  iff the framework bravely entails every e in E+
                       and does not bravely entail any e in E-.
    """
    dom = domain or framework.get_domain()
    prog = _build_asp(framework, positive, negative, dom)
    sat, _, elapsed = _solve(prog, n_models=1, timeout=timeout)
    msg = "Valid." if sat else "Invalid: brave entailment not satisfied."
    return sat, msg, elapsed


def check_has_stable_extension(
    framework: ABAFramework,
    domain: Optional[List[str]] = None,
    timeout: int = 30,
) -> bool:
    """True iff the framework admits at least one stable extension."""
    dom = domain or framework.get_domain()
    prog = _build_asp(framework, [], [], dom)
    sat, _, _ = _solve(prog, n_models=1, timeout=timeout)
    return sat


def _norm(atom: str) -> str:
    """Canonical spelling of a ground atom, so 'p(a, b)' == clingo's 'p(a,b)'."""
    return re.sub(r'\s+', '', atom)


def witness_extension(
    framework: ABAFramework,
    positive: List[str],
    negative: List[str],
    domain: Optional[List[str]] = None,
    timeout: int = 30,
) -> Optional[set]:
    """One stable extension Δ satisfying the given examples, as a set of atoms.

    Definition 1 asks for a SINGLE Δ accepting all of E+ and none of E-. This
    returns a witness for that Δ so held-out examples can be read off inside
    it, instead of being probed one at a time (which asks a different, much
    weaker question on multi-extension frameworks).

    Returns None when no such extension exists.
    """
    dom = domain or framework.get_domain()
    prog = _build_asp(framework, positive, negative, dom)
    sat, models, _ = _solve(prog, n_models=1, timeout=timeout)
    if not sat or not models:
        return None
    return {_norm(a) for a in models[-1]}


def conditioned_status(
    framework: ABAFramework,
    condition_positive: List[str],
    condition_negative: List[str],
    atoms: List[str],
    domain: Optional[List[str]] = None,
    timeout: int = 30,
) -> Dict[str, str]:
    """Status of each atom across ALL extensions satisfying the conditions.

    For every atom, one of:
      ``ALWAYS``       accepted in every extension that satisfies the conditions
      ``NEVER``        accepted in none of them
      ``FREE``         accepted in some and rejected in others — the framework
                       makes no prediction about this atom; a brave check would
                       score it as a success anyway
      ``NO_EXTENSION`` the conditions themselves are unsatisfiable

    Conditioning on the TRAINING examples and asking about the HELD-OUT ones is
    the honest generalisation test under brave semantics: brave ABA Learning
    admits mutually-attacking assumptions that let a framework realise any
    labelling of the unseen atoms, so "some extension gets it right" is not
    evidence of having learnt anything.
    """
    dom = domain or framework.get_domain()
    base = _build_asp(framework, condition_positive, condition_negative, dom)
    out: Dict[str, str] = {}
    for atom in atoms:
        accepts, _, _ = _solve(f"{base}\n:- not {atom}.", n_models=1, timeout=timeout)
        rejects, _, _ = _solve(f"{base}\n:- {atom}.", n_models=1, timeout=timeout)
        if accepts and rejects:
            out[atom] = "FREE"
        elif accepts:
            out[atom] = "ALWAYS"
        elif rejects:
            out[atom] = "NEVER"
        else:
            out[atom] = "NO_EXTENSION"
    return out


# ──────────────────────────────────────────────────────────────────────────────
# RoLe phase
# ──────────────────────────────────────────────────────────────────────────────

_PRIME_RE = re.compile(r'^([a-z][a-z0-9_]*)_prime\(([^)]+)\)$')


def run_rote_learning(
    problem: LearningProblem,
    timeout: int = 30,
) -> Tuple[List[Rule], bool, str]:
    """
    RoLe phase: find the *minimal* set of ground facts to add.

    Returns (new_ground_facts, success, message).
    """
    dom = problem.get_domain()
    prog = _build_asp(
        problem.background,
        problem.positive,
        problem.negative,
        dom,
        learnable=problem.learnable,
        minimize=True,
    )

    sat, models, _ = _solve(prog, opt_mode=True, timeout=timeout)
    if not sat or not models:
        return [], False, (
            "RoLe: no solution exists. "
            "Verify that T (learnable predicates) is large enough and "
            "that the background knowledge is consistent."
        )

    # Last model = optimal (lowest cost under #minimize)
    optimal_atoms = models[-1]

    new_facts: List[Rule] = []
    seen: set = set()
    for atom in optimal_atoms:
        m = _PRIME_RE.match(atom)
        if m:
            pred, const = m.group(1), m.group(2)
            rule = Rule(head=f"{pred}(X)", body=[f"X = {const}"])
            key = rule.to_prolog()
            if key not in seen:
                seen.add(key)
                new_facts.append(rule)

    return new_facts, True, f"RoLe: found {len(new_facts)} ground facts."


# ──────────────────────────────────────────────────────────────────────────────
# Full solution validator
# ──────────────────────────────────────────────────────────────────────────────

def validate_llm_solution(
    background: ABAFramework,
    candidate: ABAFramework,
    positive: List[str],
    negative: List[str],
    domain: Optional[List[str]] = None,
    timeout: int = 30,
) -> Dict:
    """
    Full validation of a candidate framework produced by an LLM.

    Returns a dict with keys:
        valid, has_extension, intensional,
        n_new_rules, n_new_assumptions, clingo_time, message.
    """
    dom = domain or candidate.get_domain()
    has_ext = check_has_stable_extension(candidate, dom, timeout)
    valid, msg, elapsed = check_brave_entailment(
        candidate, positive, negative, dom, timeout
    )
    return {
        "valid": valid,
        "has_extension": has_ext,
        "intensional": candidate.is_intensional(),
        "n_new_rules": len(candidate.new_rules),
        "n_new_assumptions": len(candidate.new_assumptions),
        "clingo_time": elapsed,
        "message": msg,
    }