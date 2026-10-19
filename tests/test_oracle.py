"""Tests for the step oracle in `src/aba_algorithm.py`.

The oracle lets someone else (a fine-tuned model) answer the computed steps of
Algorithm 1 while the reference keeps the control flow. Two things must hold:

  1. Without an oracle, or with one that returns the reference computation, the
     run is the reference's, step for step. `tests/test_golden_traces.py` pins
     the no-oracle path; these pin the identity-oracle path.
  2. Every routed answer is actually used: perturbing any one kind changes the
     run somewhere, so no step is computed behind the oracle's back.

Run with:  python -m pytest tests/test_oracle.py -q
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.aba_algorithm import ORACLE_KINDS, solve_aba_learning
from src.aba_corpus import problem_from_dict
from src.aba_dataset import ABADataset
from src.aba_tracelog import TraceRecorder


@pytest.fixture(scope="module")
def problems():
    ds = ABADataset()
    ds.load_builtin_benchmarks(solve=False)
    ds.anonymize(scheme="letters", anonymize_constants=True)
    out = [e.problem for e in ds]
    per_tier = collections.Counter()
    for line in open(ROOT / "corpus/v1/problems.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if per_tier[r["tier"]] < 3:                 # every tier, t4/t9 reuse included
            per_tier[r["tier"]] += 1
            out.append(problem_from_dict(r["problem"]))
    return out


def run(problem, oracle=None):
    """The trace and the decision record of one run."""
    rec = TraceRecorder()
    _, trace = solve_aba_learning(problem, observer=rec, oracle=oracle)
    return trace.to_dict(), rec.role_facts, [e.to_dict() for e in rec.events]


def test_identity_oracle_reproduces_the_reference(problems):
    for p in problems:
        assert run(p, lambda kind, state, compute: compute()) == run(p), p.problem_id


def test_every_kind_is_asked_with_its_state(problems):
    seen = collections.defaultdict(set)

    def spy(kind, state, compute):
        seen[kind].add(tuple(sorted(state)))
        return compute()

    for p in problems:
        solve_aba_learning(p, oracle=spy)
    assert set(seen) == set(ORACLE_KINDS)
    assert seen["role"] == {("problem",)}
    for kind in ("subsume", "fold_candidates", "check"):
        assert all({"learnt", "new_asms", "idx", "rule"} <= set(k) for k in seen[kind])
    for kind in ("reuse_scan", "reuse_check", "contrary_facts"):
        assert all({"learnt", "new_asms", "folded"} <= set(k) for k in seen[kind])


# One perturbation per kind; each must change some run, so its answer is live.
PERTURB = {
    "role": lambda a: (a[0][:-1], a[1], a[2]),
    "subsume": lambda a: not a,
    "fold_candidates": lambda a: list(reversed(a)),
    "check": lambda a: not a,
    "reuse_scan": lambda a: [],
    "reuse_check": lambda a: not a,
    "contrary_facts": lambda a: (a[0][:-1], a[1], a[2]),
}


@pytest.mark.parametrize("kind", ORACLE_KINDS)
def test_perturbing_an_answer_changes_the_run(problems, kind):
    def once(k, state, compute):
        answer = compute()
        if k == kind and not done:
            done.append(True)
            return PERTURB[kind](answer)
        return answer

    changed = 0
    for p in problems:
        done = []
        try:
            changed += run(p, once) != run(p)
        except Exception:                           # a perturbed run may break: also a change
            changed += 1
    assert changed, f"perturbing {kind} never changed a run"
