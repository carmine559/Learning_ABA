"""
Regression tests for the defects found in the July 2026 audit.

Each test names the defect it locks down, because several of them changed
published numbers rather than crashing anything — they are exactly the kind of
bug a test suite exists to prevent from coming back silently.

Run with:  python -m pytest tests -q
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import clingo
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.aba_types import Rule, ABAFramework
from src.aba_dataset import make_nixon_diamond, make_flies_problem
from src.aba_algorithm import solve_aba_learning
from src.aba_anonymize import verify_invariance
from src.aba_generalization import (
    is_intensional_strict, rule_contains_constant, wellformed_violations,
    split_problem_examples, evaluate_generalization,
)
from src.aba_prompts import parse_llm_output, problem_to_prompt, _split_body
from src.aba_validator import _build_asp, conditioned_status, witness_extension


# ─────────────────────────────────────────────────────────────────────────────
# B5 — #minimize tuples must not collide across learnable predicates
# ─────────────────────────────────────────────────────────────────────────────

def _optimal_cost(program: str):
    ctl = clingo.Control(["--models=0", "--opt-mode=optN"], logger=lambda c, m: None)
    ctl.add("base", [], program)
    ctl.ground([("base", [])])
    costs = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            costs.append(model.cost)
    return costs[-1] if costs else None


def test_minimize_counts_each_learnt_fact_separately():
    """Learning p(a) AND q(a) must cost 2, not 1.

    #minimize aggregates over the SET of tuples, so a bare {1,X} makes two
    facts about the same constant cost one between them and RoLe stops being
    minimal as soon as |T| > 1 — which is every tier but t5.
    """
    fw = ABAFramework(rules=[])
    prog = _build_asp(fw, ["p(a)", "q(a)"], [], ["a", "b"],
                      learnable=["p", "q"], minimize=True)
    assert _optimal_cost(prog) == [2]


def test_minimize_line_mentions_the_predicate():
    fw = ABAFramework(rules=[])
    prog = _build_asp(fw, [], [], ["a"], learnable=["p"], minimize=True)
    assert "#minimize{1,X,p : p_prime(X)}." in prog


# ─────────────────────────────────────────────────────────────────────────────
# B3 — the parser must not silently discard what the model wrote
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def background():
    return ABAFramework(
        rules=[Rule("q(a)", []), Rule("r(b)", []), Rule("t(X)", ["q(X)"])],
        assumptions=["u(X)"],
        contraries={"u(X)": "t(X)"},
    )


def test_rules_written_under_new_assumptions_are_recovered(background):
    """46.2% of benchmark samples put a rule under NEW ASSUMPTIONS."""
    text = (
        "NEW RULES:\n"
        "v(X) :- t(X).\n"
        "NEW ASSUMPTIONS:\n"
        "c_alpha(X) :- r(X).\n"
    )
    repairs = []
    fw = parse_llm_output(text, background, repairs=repairs)
    assert "c_alpha(X) :- r(X)." in [r.to_prolog() for r in fw.new_rules]
    assert any("recovered" in m for m in repairs)


def test_defeated_by_inside_a_rule_keeps_both_readings(background):
    """'v(X) :- t(X), u(X) defeated_by c_u(X).' is a rule AND a declaration."""
    text = ("NEW RULES:\nNONE\n"
            "NEW ASSUMPTIONS:\n"
            "v(X) :- t(X), u(X) defeated_by c_u(X).\n")
    fw = parse_llm_output(text, background)
    assert "v(X) :- t(X), u(X)." in [r.to_prolog() for r in fw.new_rules]
    assert fw.contraries["u(X)"] == "c_u(X)"      # visible to the (iv) check


def test_last_answer_block_wins_not_the_draft(background):
    """17.9% of samples emit more than one NEW RULES: header."""
    text = (
        "Draft:\nNEW RULES:\nv(X) :- q(X).\nNEW ASSUMPTIONS:\nNONE\n\n"
        "Final answer:\nNEW RULES:\nv(X) :- r(X).\nNEW ASSUMPTIONS:\nNONE\n"
    )
    fw = parse_llm_output(text, background)
    assert [r.to_prolog() for r in fw.new_rules] == ["v(X) :- r(X)."]


def test_echoed_problem_statement_is_truncated(background):
    text = (
        "NEW RULES:\nv(X) :- q(X).\nNEW ASSUMPTIONS:\nNONE\n\n"
        "=== BACKGROUND KNOWLEDGE ===\nRules:\n  - q(a) is always true.\n"
    )
    repairs = []
    fw = parse_llm_output(text, background, repairs=repairs)
    assert [r.to_prolog() for r in fw.new_rules] == ["v(X) :- q(X)."]
    assert any("echoed" in m for m in repairs)


def test_none_none_is_an_empty_answer_not_a_parse_error(background):
    """"The background already suffices" is a claim, not unreadable output."""
    fw = parse_llm_output("NEW RULES:\nNONE\n\nNEW ASSUMPTIONS:\nNONE",
                          background)
    assert fw is not None and fw.new_rules == [] and fw.new_assumptions == []


def test_unstructured_output_still_fails_to_parse(background):
    assert parse_llm_output("I am not sure how to answer this.", background) is None


def test_binary_predicates_survive_body_splitting():
    assert _split_body("edge(X, Y), q(Y)") == ["edge(X, Y)", "q(Y)"]


def test_reused_background_assumption_is_not_reported_as_new(background):
    text = "NEW RULES:\nv(X) :- q(X), u(X).\nNEW ASSUMPTIONS:\nu(X) defeated_by t(X)"
    fw = parse_llm_output(text, background)
    assert fw.new_assumptions == []
    assert fw.assumptions.count("u(X)") == 1


# ─────────────────────────────────────────────────────────────────────────────
# B1 / B2 — Definition-1 side conditions
# ─────────────────────────────────────────────────────────────────────────────

def test_reusing_a_background_assumption_is_legal(background):
    """Definition 4 / Algorithm 1 line 36. This false positive marked 71.8%
    of the v3 benchmark ill-formed."""
    text = "NEW RULES:\nv(X) :- q(X), u(X).\nNEW ASSUMPTIONS:\nu(X) defeated_by t(X)"
    fw = parse_llm_output(text, background)
    assert wellformed_violations(fw, background, ["v"]) == []


def test_changing_the_contrary_of_a_background_assumption_is_a_violation(background):
    text = "NEW RULES:\nv(X) :- q(X), u(X).\nNEW ASSUMPTIONS:\nu(X) defeated_by c_u(X)"
    fw = parse_llm_output(text, background)
    viol = wellformed_violations(fw, background, ["v"])
    assert any("(iv)" in m for m in viol)


def test_contrary_of_a_background_assumption_still_needs_to_be_in_T(background):
    """Condition (ii) applies to a contrary like any other background predicate
    — the paper's Example 3 puts abnormal_quaker in T for exactly this reason."""
    text = "NEW RULES:\nt(X) :- r(X).\nNEW ASSUMPTIONS:\nNONE"
    fw = parse_llm_output(text, background)
    assert any("(ii)" in m for m in wellformed_violations(fw, background, ["v"]))
    assert wellformed_violations(fw, background, ["v", "t"]) == []


def test_assumption_as_a_rule_head_breaks_flatness(background):
    text = "NEW RULES:\nu(X) :- q(X).\nNEW ASSUMPTIONS:\nNONE"
    fw = parse_llm_output(text, background)
    assert any("flatness" in m for m in wellformed_violations(fw, background, ["u"]))


# ─────────────────────────────────────────────────────────────────────────────
# m1 / m2 — constants, domains and intensionality
# ─────────────────────────────────────────────────────────────────────────────

def test_predicate_symbols_are_not_domain_constants():
    """get_constants used to match every lowercase token, so `quaker` and
    `pacifist` were grounded as if they were individuals."""
    r = Rule("pacifist(X)", ["quaker(X)", "normal_quaker(X)"])
    assert r.get_constants() == []
    fw = ABAFramework(rules=[r, Rule("quaker(a)", [])])
    assert fw.get_domain() == ["a"]


def test_bare_ground_fact_is_not_intensional():
    assert not Rule("p(c)", []).is_intensional()
    assert rule_contains_constant(Rule("p(c)", []))
    assert not Rule("p(X)", ["X = c"]).is_intensional()
    assert Rule("p(X)", ["q(X)"]).is_intensional()


def test_propositional_assumption_gets_no_dom_guard():
    """dom/1 is unary; a 0-ary assumption must not be existentially guarded."""
    fw = ABAFramework(rules=[], assumptions=["r"], contraries={"r": "p"})
    prog = _build_asp(fw, [], [], ["a"])
    assert "r :- not p." in prog


# ─────────────────────────────────────────────────────────────────────────────
# M2 — determinacy: brave success is not evidence of learning
# ─────────────────────────────────────────────────────────────────────────────

def test_free_choice_framework_is_caught_by_determinacy():
    """The reference Nixon solution leaves pacifist(e) FREE once e is held out:
    some extension consistent with the training examples accepts it and another
    rejects it, so a brave check scores a coin flip as a success."""
    problem, _ = make_nixon_diamond()
    solution, trace = solve_aba_learning(problem)
    assert trace.success
    status = conditioned_status(
        solution, ["pacifist(a)"], ["pacifist(b)"],
        [f"pacifist({c})" for c in problem.get_domain()],
        problem.get_domain(),
    )
    assert status["pacifist(e)"] == "FREE"
    assert status["pacifist(a)"] == "ALWAYS"
    assert status["pacifist(d)"] == "NEVER"


def test_witness_extension_is_a_real_extension():
    problem, _ = make_nixon_diamond()
    solution, _ = solve_aba_learning(problem)
    w = witness_extension(solution, problem.positive, problem.negative,
                          problem.get_domain())
    assert w is not None
    assert all(e.replace(" ", "") in w for e in problem.positive)
    assert all(e.replace(" ", "") not in w for e in problem.negative)


def test_determined_generalisation_implies_brave_generalisation():
    problem = make_flies_problem()
    split = split_problem_examples(problem)
    solution, trace = solve_aba_learning(split.train)
    assert trace.success
    g = evaluate_generalization(solution, split, domain=problem.get_domain())
    assert not g.gen_determined or g.gen_valid


# ─────────────────────────────────────────────────────────────────────────────
# End-to-end sanity
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("factory", [make_nixon_diamond, make_flies_problem])
def test_symbolic_solver_returns_an_intensional_solution(factory):
    result = factory()
    problem = result[0] if isinstance(result, tuple) else result
    solution, trace = solve_aba_learning(problem)
    assert trace.success and solution is not None
    assert is_intensional_strict(solution)


def test_anonymisation_preserves_solvability():
    problem, _ = make_nixon_diamond()
    assert verify_invariance(problem)


def test_problem_is_serialised_in_the_notation_the_answer_must_use():
    """The prompt used to show the problem as prose while demanding Prolog."""
    problem, _ = make_nixon_diamond()
    prompt = problem_to_prompt(problem, mode="direct")
    assert "pacifist(X) :- quaker(X), normal_quaker(X)." in prompt
    assert "normal_quaker(X) defeated_by abnormal_quaker(X)" in prompt
    assert "dom(a)." in prompt
    assert "is always true" not in prompt      # the old prose rendering
