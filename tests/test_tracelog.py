"""Tests for the rich sidecar trace log.

Two things have to hold for `src/aba_tracelog.py` to be usable as training
supervision:

  1. It must not change the algorithm. The observer is a spectator; if
     attaching it moves a single step, every number stated against the
     reference becomes unstateable. `tests/test_golden_traces.py` pins the
     no-observer path; these pin the WITH-observer path.
  2. It must be complete. A dropped notification is invisible — the record just
     comes out slightly wrong — so the invariants below are cross-checks
     against the trace the algorithm produced independently.

Run with:  python -m pytest tests/test_tracelog.py -q
"""
from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.aba_dataset import ABADataset
from src.aba_algorithm import (
    solve_aba_learning, apply_folding, apply_folding_traced,
    _candidate_folds, _candidate_folds_traced,
)
from src.aba_tracelog import solve_and_log
from src.aba_validator import run_rote_learning


@pytest.fixture(scope="module")
def problems():
    ds = ABADataset()
    ds.load_builtin_benchmarks(solve=False)
    ds.add_benchmark_suite(n_per_tier=3, seed=42, solve=False)
    ds.anonymize(scheme="letters", anonymize_constants=True)
    return [e.problem for e in ds]


@pytest.fixture(scope="module")
def records(problems):
    return [(p,) + solve_and_log(p)[1:] for p in problems]


# ─────────────────────────────────────────────────────────────────────────────
# The recorder must not perturb the algorithm it records
# ─────────────────────────────────────────────────────────────────────────────

def test_recording_does_not_change_the_trace(problems):
    """Same steps, same symbols, same answer, with and without the recorder.

    This covers the call sites `tests/test_probes.py` does not: the observer
    inside `assumption_introduction` and the per-fact `fact_done`.
    """
    for problem in problems:
        _, plain = solve_aba_learning(problem)
        _, watched, _ = solve_and_log(problem)
        assert plain.to_dict() == watched.to_dict()


# ─────────────────────────────────────────────────────────────────────────────
# Fold provenance is a pure view: same candidates, same ORDER
# ─────────────────────────────────────────────────────────────────────────────

def test_fold_provenance_preserves_candidates_and_order(problems):
    """`gen_phase` accepts the FIRST candidate that checks out.

    So a traced variant that reordered candidates would silently change which
    rule the algorithm learns. List equality, not set equality.
    """
    for problem in problems:
        facts, ok, _ = run_rote_learning(problem)
        if not ok:
            continue
        for fact in facts:
            assert apply_folding(fact, problem.background) == \
                   [r for r, _ in apply_folding_traced(fact, problem.background)]
            assert _candidate_folds(fact, problem.background) == \
                   [r for r, _ in _candidate_folds_traced(fact, problem.background)]


def test_every_fold_candidate_has_provenance(problems):
    """A recorded candidate without its rho2 would be unreplayable."""
    for problem in problems:
        facts, ok, _ = run_rote_learning(problem)
        if not ok:
            continue
        for fact in facts:
            for rule, via in apply_folding_traced(fact, problem.background):
                assert via, f"no provenance for {rule.to_prolog()}"
                assert len(via) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# The record must be complete
# ─────────────────────────────────────────────────────────────────────────────

def test_every_fact_event_is_closed(records):
    """`outcome == "unknown"` means a `fact_done` notification was missed."""
    for problem, trace, record in records:
        for ev in record.events:
            assert ev.outcome != "unknown", (
                f"{problem.problem_id}: unclosed event for {ev.input_rule}")
            assert ev.subsume_sat is not None


def test_outcomes_agree_with_the_symbol_sequence(records):
    """Cross-check against a count the algorithm produced independently.

    Each accepted fold is an R2, each assumption introduction an R3, each
    subsumption an R4. The recorder and `LearningTrace` derive these by
    different routes, so agreement is real evidence rather than a tautology.
    Note an R3 step's implicit fold is NOT counted as R2 by the trace, which is
    why `folded_with_assumption` maps to R3 alone. Nor do the contrary facts an
    R3 obliges emit their own R1 symbols — they ride on the R3 step as
    `new_contrary_facts`, and only `aba_trace.normalise_gold` expands them. So
    R1 counts the RoLe facts and nothing else.
    """
    for problem, trace, record in records:
        symbols = collections.Counter(trace.symbol_sequence())
        outcomes = collections.Counter(ev.outcome for ev in record.events)
        assert outcomes["folded"] == symbols["R2"], problem.problem_id
        assert outcomes["folded_with_assumption"] == symbols["R3"], problem.problem_id
        assert outcomes["subsumed"] == symbols["R4"], problem.problem_id
        assert len(record.role_facts) == symbols["R1"], problem.problem_id


def test_rejected_candidates_are_distinguished_from_unchecked(records):
    """`sat is False` means checked and rejected; `None` means never reached.

    Conflating them would overstate how much search the algorithm did — the
    loop breaks on the first candidate that passes.
    """
    seen_rejected = seen_unchecked = False
    for problem, trace, record in records:
        for ev in record.events:
            accepted = [c for c in ev.candidates if c.accepted]
            assert len(accepted) <= 1, problem.problem_id
            for c in ev.candidates:
                assert c.sat in (True, False, None)
                if c.sat is False:
                    seen_rejected = True
                if c.sat is None:
                    seen_unchecked = True
            # Nothing may be checked after the accepted candidate.
            if accepted:
                rank = accepted[0].rank
                assert all(c.sat is None for c in ev.candidates
                           if c.rank > rank), problem.problem_id
    assert seen_rejected and seen_unchecked, "corpus too small to exercise both"


def test_assumption_branch_is_recorded(records):
    """Reuse vs mint must be distinguishable — the whole point of E2."""
    modes = collections.Counter()
    for problem, trace, record in records:
        for ev in record.events:
            for a in ev.asm_attempts:
                modes[a.mode] += 1
                if a.mode == "reuse":
                    assert a.sat is not None
                else:
                    assert a.rote_ok is not None
            if ev.outcome == "folded_with_assumption":
                assert ev.new_assumption and ev.contrary
    assert modes["mint"], "no assumption introduction exercised"


def test_serialises_to_json(records):
    """The record is only useful if it reaches disk intact."""
    import json
    for problem, trace, record in records:
        d = record.to_dict()
        assert json.loads(json.dumps(d)) == d
        # The old consumers read this key and must keep working.
        assert d["symbolic_trace"] == trace.to_dict()
