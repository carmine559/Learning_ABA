"""Tests for the step-wise supervision of arm S2 (`src/aba_steps.py`, corpus/v1-step).

What must hold for the step rows to be supervision for Algorithm 1:

  1. The prompts are frozen: `tests/golden/step_prompts.txt` pins one prompt and
     target per kind, and the committed corpus's prompt_sha256 is what the builder
     rebuilds. Any edit to the text is a new STEP_PROMPT_VERSION.
  2. Every target says what the reference did: it parses back to the reference's own
     answer, a lines-16/18 witness is empty exactly when the verdict is yes, and gold
     answers fed to the controller reproduce the trace target byte for byte.
  3. Model answers are read leniently but never wrongly: bare facts and duplicates
     are normalised, illegal items are dropped and counted, and an unusable answer
     stops the run with a code instead of guessing.

Regenerate the golden file (only with a version bump): set REGEN_STEP_GOLDEN=1.
Run with:  python -m pytest tests/test_steps.py -q
"""
from __future__ import annotations

import collections
import hashlib
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.aba_algorithm import ORACLE_KINDS
from src.aba_corpus import problem_from_dict
from src.aba_steps import (
    STEP_PROMPT_VERSION, WITNESSED, ModelOracle, StepStop, chained_run, gold_backend,
    harvest, parse_answer, same_answer, step_prompt,
)

GOLDEN = ROOT / "tests/golden/step_prompts.txt"
GOLDEN_PROBLEM = "t4_nested_0080"                  # train; all seven kinds and extra rows
REGEN = os.environ.get("REGEN_STEP_GOLDEN") == "1"


def _rows(path):
    return [json.loads(x) for x in open(path, encoding="utf-8")]


@pytest.fixture(scope="module")
def corpus():
    probs = {r["problem_id"]: r for r in _rows(ROOT / "corpus/v1/problems.jsonl")}
    gold = {r["problem_id"]: r["target"] for r in _rows(ROOT / "corpus/v1/sft_trace.jsonl")}
    gold.update({r["problem_id"]: r["trace_target"] for r in _rows(ROOT / "corpus/v1/eval.jsonl")})
    return probs, gold


@pytest.fixture(scope="module")
def sample(corpus):
    """Two problems per tier and split."""
    probs, gold = corpus
    per, out = collections.Counter(), []
    for pid, r in probs.items():
        if per[(r["tier"], r["split"])] < 2:
            per[(r["tier"], r["split"])] += 1
            p = problem_from_dict(r["problem"])
            out.append((p, r["split"], gold[pid]) + harvest(p))
    return out


def _golden_text(corpus):
    probs, _ = corpus
    p = problem_from_dict(probs[GOLDEN_PROBLEM]["problem"])
    rows, _ = harvest(p)
    first = {}
    for r in rows:
        first.setdefault((r["kind"], r["extra"]), r)
    blocks = [f"### {STEP_PROMPT_VERSION} {GOLDEN_PROBLEM}"]
    for (kind, extra), r in sorted(first.items()):
        blocks += [f"### kind {kind}{' (extra)' if extra else ''}",
                   step_prompt(p, kind, r["state"]), "### target", r["target"]]
    return "\n".join(blocks) + "\n"


def test_prompts_are_frozen(corpus):
    text = _golden_text(corpus)
    if REGEN:
        GOLDEN.write_text(text, encoding="utf-8")
    assert GOLDEN.read_text(encoding="utf-8") == text, "prompt text changed: bump STEP_PROMPT_VERSION"


def test_committed_corpus_matches_the_builder(corpus):
    probs, _ = corpus
    m = json.loads((ROOT / "corpus/v1-step/MANIFEST.json").read_text(encoding="utf-8"))
    assert m["prompt_version"] == STEP_PROMPT_VERSION
    data = (ROOT / "corpus/v1-step/steps.jsonl").read_bytes()
    assert hashlib.sha256(data).hexdigest() == m["sha256"]["steps.jsonl"]
    h = collections.defaultdict(hashlib.sha256)
    cache = {}
    for line in data.decode("utf-8").splitlines():
        r = json.loads(line)
        p = cache.get(r["problem_id"]) or cache.setdefault(
            r["problem_id"], problem_from_dict(probs[r["problem_id"]]["problem"]))
        h[f"{r['split']}/{r['kind']}"].update(
            step_prompt(p, r["kind"], r["state"]).encode("utf-8") + b"\x00")
    assert {k: v.hexdigest() for k, v in h.items()} == m["prompt_sha256"]


def test_targets_parse_back_to_the_reference(sample):
    for p, _, _, rows, _ in sample:
        for r in rows:
            ans, _ = parse_answer(r["kind"], r["target"], p, r["answer"], r["payload"])
            assert same_answer(r["kind"], ans, r["answer"]), (p.problem_id, r["k"])


def test_witnesses_are_unique_and_agree_with_the_verdict(sample):
    for p, _, _, rows, _ in sample:
        for r in rows:
            if r["kind"] in WITNESSED:
                assert r["n_models"] == 1, (p.problem_id, r["k"])
                assert (r["witness"] == []) == r["verdict"], (p.problem_id, r["k"])
                _, notes = parse_answer(r["kind"], r["target"], p, r["answer"], r["payload"])
                assert notes["witness"] == ([] if r["verdict"] else r["witness"])


def test_gold_answers_reproduce_the_trace(sample):
    seen = set()
    for p, _, gold, rows, _ in sample:
        out = chained_run(p, ModelOracle(p, gold_backend(rows, p)))
        assert out["error"] is None and out["text"] == gold, p.problem_id
        seen |= {r["kind"] for r in rows}
    assert seen == set(ORACLE_KINDS)


def test_extra_rows_are_unvisited_non_dom_checks(sample):
    for p, split, _, rows, _ in sample:
        visited = {(r["event"], r["state"]["fold"]) for r in rows
                   if r["kind"] == "check" and not r["extra"]}
        for r in rows:
            if r["extra"]:
                assert r["kind"] == "check" and r["cell"] == "extra_check"
                assert (r["event"], r["state"]["fold"]) not in visited
                assert "dom(" not in r["state"]["fold"]


# ─────────────────────────────────────────────────────────────────────────────
# Reading model answers
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def golden_rows(corpus):
    probs, _ = corpus
    p = problem_from_dict(probs[GOLDEN_PROBLEM]["problem"])
    rows, _ = harvest(p)
    return p, {r["kind"]: r for r in rows if not r["extra"]}


def test_facts_are_normalised(golden_rows):
    p, by = golden_rows
    r = by["role"]
    facts = r["answer"][0]
    const = lambda f: f.body[0].split("= ")[1]
    text = "\n".join([f"R1 {facts[-1].head.split('(')[0]}({const(facts[-1])})."]   # bare, out of order
                     + [f"R1 {f.to_prolog()}" for f in facts] + ["R1 zz(X) :- X = a."])
    ans, notes = parse_answer("role", text, p, r["answer"], r["payload"])
    assert same_answer("role", ans, r["answer"])               # sorted, duplicate dropped
    assert notes["illegal"] == 1                               # zz is not in T


def test_decisions_are_read_from_the_verdict(golden_rows):
    p, by = golden_rows
    r = by["check"]
    assert parse_answer("check", "FAILS: none. YES", p, r["answer"], r["payload"])[0] is True
    assert parse_answer("reuse_check", "no.", p, False, by["reuse_check"]["payload"])[0] is False
    with pytest.raises(StepStop, match="unparseable:check"):
        parse_answer("check", "maybe", p, r["answer"], r["payload"])


def test_folds_must_be_offered_by_applyFolding(golden_rows):
    p, by = golden_rows
    r = by["fold_candidates"]
    legal = r["answer"]
    text = "R2 candidates: [w(X) :- zz(X).] " + " ".join(f"[{f.to_prolog()}]" for f, _ in legal)
    ans, notes = parse_answer("fold_candidates", text, p, legal, r["payload"])
    assert same_answer("fold_candidates", ans, legal) and notes["illegal"] == 1
    for bad in ("R2 candidates: none.", "R2 candidates: [w(X) :- zz(X).]"):
        with pytest.raises(StepStop, match="empty:fold_candidates"):
            parse_answer("fold_candidates", bad, p, legal, r["payload"])


def test_scan_names_assumptions_of_A(golden_rows):
    p, by = golden_rows
    r = by["reuse_scan"]
    assert parse_answer("reuse_scan", "R3 reuse: none.", p, r["answer"], r["payload"])[0] == []
    with pytest.raises(StepStop, match="empty:reuse_scan"):
        parse_answer("reuse_scan", "R3 reuse: [zz(X)].", p, r["answer"], r["payload"])
