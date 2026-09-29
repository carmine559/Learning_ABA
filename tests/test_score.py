"""Hand-built cases the scorer must catch; `--control` covers the gold side.

Run with:  python -m pytest tests/test_score.py -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.aba_algorithm import _current_framework
from src.aba_dataset import (
    CORPUS_TIERS, HELDOUT_TIERS, generate_corpus_problem, generate_heldout_problem,
)
from src.aba_prompts import solution_to_output_format
from src.aba_replay import trace_lines
from src.aba_score import (
    degenerate_answer, gold_failures, reference, reward, score_output,
)
from src.aba_types import Rule


@pytest.fixture(scope="module")
def ref():
    return reference(generate_corpus_problem(CORPUS_TIERS[0], True, "test")[0])


def _answer(ref, rules, asms):
    return solution_to_output_format(
        _current_framework(ref.problem.background, rules, asms), ref.problem.background)


def test_gold_targets_score_the_maximum(ref):
    for arm in ("trace_target", "endpoint_target"):
        assert gold_failures(score_output(getattr(ref, arm), ref), arm, {}) == []


def test_degenerate_answer_is_valid_but_rewarded_less(ref):
    card = score_output(degenerate_answer(ref), ref)
    assert card.valid and not card.intensional and card.n_ground > 0
    assert card.error == "valid_but_degenerate"
    assert reward(card) < reward(score_output(ref.endpoint_target, ref))


def test_self_defeating_rule(ref):
    sol = ref.solution
    guarded = next(r for r in sol.new_rules if "alpha_0(X)" in r.body)
    body = [b for b in guarded.body if b != "alpha_0(X)"]
    inert = [Rule(guarded.head, body + ["alpha_9(X)"]), Rule("c_alpha_9(X)", body)]
    asms = {**{a: sol.contraries[a] for a in sol.new_assumptions},
            "alpha_9(X)": "c_alpha_9(X)"}
    card = score_output(_answer(ref, sol.new_rules + inert, asms), ref)
    assert card.valid and card.self_defeating == [inert[0].to_prolog()]
    assert card.error == "self_defeating" and not card.clean
    assert reward(card) < reward(score_output(ref.endpoint_target, ref))


def test_parse_failure_scores_zero(ref):
    card = score_output("I cannot solve this problem.", ref)
    assert card.error == "parse_error" and reward(card) == 0.0


def test_changed_background_contrary_is_illformed(ref):
    a = ref.problem.background.assumptions[0]
    card = score_output(f"{ref.endpoint_target}\n{a} defeated_by changed(X)", ref)
    assert card.illformed and card.error == "illformed" and reward(card) == 0.0


def test_renamed_assumption_is_still_the_algorithms_answer(ref):
    card = score_output(ref.endpoint_target.replace("alpha_0", "abnormal"), ref)
    assert card.exact and card.clean


def test_wrong_branch_of_a_decoy_problem():
    problem, meta = generate_heldout_problem(HELDOUT_TIERS[0], True,
                                             "corpus-v1:t8_decoy:v1:0")
    stored = {"expected": meta["expected"], "forbidden": meta["forbidden"],
              "answers": {n: {"new_rules": [r.to_prolog() for r in rules],
                              "contraries": c}
                          for n, (rules, c) in meta["answers"].items()}}
    r = reference(problem)
    other = next(n for n in meta["answers"] if n != meta["expected"])
    card = score_output(_answer(r, *meta["answers"][other]), r, stored)
    assert card.valid and card.choice == other
    assert card.algorithm_choice is False and not card.exact


def test_one_flipped_check_is_localised(ref):
    lines = [ln for ln in trace_lines(ref.trace_target) if ln]
    i = next(k for k, ln in enumerate(lines) if ln.startswith("R2? [") and ln.endswith("no."))
    flipped = ref.trace_target.replace(lines[i], lines[i][:-3] + "yes.", 1)
    audit = score_output(flipped, ref).audit
    assert audit["first_error"] == i + 1
    right, total = audit["by_kind"]["check"]
    assert right == total - 1 and audit["accuracy"] < 1.0
