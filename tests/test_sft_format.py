"""Tests for the two SFT serialisations and the replay that verifies them.

A training target is only supervision if it determines the algorithm's answer,
and only a fair fidelity target if the scorer can read it. These tests pin both,
plus one property of the checker itself: that it can fail. A verifier that
passes everything is indistinguishable from one that checks nothing.

Run with:  python -m pytest tests/test_sft_format.py -q
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.aba_dataset import ABADataset
from src.aba_sft import sft_example, gold_self_score
from src.aba_replay import check_example
from src.aba_trace import score_trace


@pytest.fixture(scope="module")
def examples():
    ds = ABADataset()
    ds.load_builtin_benchmarks(solve=False)   # the only problems that reuse
    ds.add_benchmark_suite(n_per_tier=3, seed=42, solve=False)
    ds.anonymize(scheme="letters", anonymize_constants=True)
    return [(e.problem, sft_example(e.problem)) for e in ds]


def _by_id(examples, pid):
    return next((p, ex) for p, ex in examples if p.problem_id == pid)


def test_every_target_is_sound_supervision(examples):
    """Algorithm, record replay, text replay and parser all agree; zero parser
    repairs; the replayed framework is still a solution."""
    for problem, ex in examples:
        assert check_example(ex, problem) is None, problem.problem_id


def test_the_reuse_branch_is_serialised(examples):
    """Only the hand-written benchmarks reuse an assumption (no synthetic tier
    does), so this is the one place line 36's reuse is exercised end to end."""
    problem, ex = _by_id(examples, "nixon_diamond_anon")
    assert "R3 reuse? [w(X)] yes." in ex["trace_target"]
    assert check_example(ex, problem) is None


@pytest.mark.parametrize("corrupt", [
    # minting on the fold whose reuse failed: the step line 40 forbids
    lambda t: t.replace("R2 p1(X) :- r(X).\nR3 p1(X) :- r(X), alpha_0(X).",
                        "R2 p1(X) :- p(X).\nR3 p1(X) :- p(X), alpha_0(X)."),
    # losing the declaration of a minted assumption
    lambda t: t.replace("alpha_0(X) defeated_by c_alpha_0(X)\nR1", "R1"),
    # a draft answer block ahead of the real one
    lambda t: "NEW RULES:\nv(X) :- q(X).\n\n" + t,
])
def test_the_check_can_fail(examples, corrupt):
    problem, ex = _by_id(examples, "nixon_diamond_anon")
    bad = dict(ex, trace_target=corrupt(ex["trace_target"]))
    assert bad["trace_target"] != ex["trace_target"], "corruption did not apply"
    assert check_example(bad, problem) is not None


def test_rejected_candidates_are_invisible_to_the_scorer(examples):
    """The reason for the [bracket] convention. Unbracketed, a candidate the
    algorithm rejected reads as an R2 it took, and a perfectly faithful model
    loses precision for having recorded its own search."""
    problem, ex = _by_id(examples, "t2_defeas_0000_anon")
    args = (ex["trace"], problem.background, problem.learnable)
    bare = re.sub(r"R2\? \[([^\]]+)\] no\.", r"R2? \1 no.", ex["trace_target"])
    assert bare != ex["trace_target"]
    assert score_trace(ex["trace_target"], *args).precision == 1.0
    assert score_trace(bare, *args).precision < 1.0


def test_endpoint_target_is_excluded_not_scored_zero(examples):
    """`has_trace` False puts the endpoint arm outside fidelity averages, the
    same denominator hygiene applied to answer-only samples elsewhere."""
    for problem, ex in examples:
        s = score_trace(ex["endpoint_target"], ex["trace"],
                        problem.background, problem.learnable)
        assert not s.has_trace, problem.problem_id


def test_gold_trace_gets_full_recall_wherever_recall_is_defined(examples):
    """R1-R3 recall must be exactly 1.0 on a perfect copy wherever gold has that
    step. R4 is exempt: the scorer infers it at the end of the trace and can
    charge it to the wrong fact (see `gold_self_score`)."""
    for problem, ex in examples:
        ceil = gold_self_score(ex, problem)
        for attr in ("r1_recall", "r2_recall", "r3_recall"):
            assert ceil[attr] in (None, 1.0), (problem.problem_id, attr, ceil[attr])
