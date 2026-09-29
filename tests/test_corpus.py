"""Tests for the persisted corpus: signatures, round-trip, and a tiny build.

Run with:  python -m pytest tests/test_corpus.py -q
"""
from __future__ import annotations

import json
import random
import sys
from dataclasses import replace
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.aba_anonymize import anonymize_problem
from src.aba_corpus import (
    CorpusConfig, build, problem_from_dict, problem_to_dict, structural_signature,
)
from src.aba_dataset import CORPUS_TIERS, generate_corpus_problem
from src.aba_sft import build_prompt
from src.aba_algorithm import solve_aba_learning


def _problem(tier=0, defeasible=True, seed="test"):
    return generate_corpus_problem(CORPUS_TIERS[tier], defeasible, seed)[0]


def test_signature_ignores_names_and_order_but_not_structure():
    p = _problem()
    anon, _ = anonymize_problem(p, scheme="letters")
    rules = list(p.background.rules)
    random.Random(0).shuffle(rules)
    shuffled = replace(p, background=replace(p.background, rules=rules))
    assert structural_signature(p) == structural_signature(anon)
    assert structural_signature(p) == structural_signature(shuffled)
    assert structural_signature(p) != structural_signature(_problem(seed="other"))


def test_problem_round_trips():
    p, _ = anonymize_problem(_problem(tier=3), scheme="letters")
    q = problem_from_dict(json.loads(json.dumps(problem_to_dict(p))))
    assert build_prompt(q) == build_prompt(p)
    assert solve_aba_learning(q)[1].to_dict() == solve_aba_learning(p)[1].to_dict()


def _rows(path):
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]


@pytest.fixture(scope="module")
def tiny(tmp_path_factory):
    out = tmp_path_factory.mktemp("corpus")
    small = CorpusConfig(n_train=2, n_val=1, n_test=1, n_heldout=1)
    manifest = build(small, out / "small")
    build(replace(small, n_train=4), out / "large")
    return manifest, out / "small", out / "large"


def test_gates_pass(tiny):
    manifest, _, _ = tiny
    assert all(manifest["gates"].values()), manifest["gates"]


def test_nothing_evaluated_is_trained_on(tiny):
    _, small, _ = tiny
    evaluated = {r["problem_id"] for r in _rows(small / "eval.jsonl")}
    for arm in ("sft_trace.jsonl", "sft_endpoint.jsonl"):
        trained = _rows(small / arm)
        assert {r["split"] for r in trained} == {"train", "val"}
        assert not evaluated & {r["problem_id"] for r in trained}


def test_growing_train_keeps_the_evaluation_problems(tiny):
    """Splits are filled held-out first, train last, stream by stream."""
    _, small, large = tiny
    fixed = lambda d: {r["problem_id"]: r["signature"]
                       for r in _rows(d / "problems.jsonl")
                       if r["split"] != "train"}
    assert fixed(small) == fixed(large)


def test_heldout_expected_answer_is_the_references(tiny):
    _, small, _ = tiny
    finals = {r["problem_id"]: sorted(r["final_new_rules"])
              for r in _rows(small / "traces.jsonl")}
    for row in _rows(small / "problems.jsonl"):
        if row["split"] == "heldout":
            meta = row["meta"]
            assert finals[row["problem_id"]] == sorted(
                meta["answers"][meta["expected"]]["new_rules"])
