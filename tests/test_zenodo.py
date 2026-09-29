"""The Table 1 import (src/aba_zenodo.py), on the real Zenodo archive.

Skipped until the archive is downloaded (`python build_corpus.py` does it).
"""
from pathlib import Path

import pytest

from src.aba_algorithm import solve_aba_learning
from src.aba_zenodo import load_table1

ZIP = (Path(__file__).resolve().parents[1]
       / "corpus" / "zenodo" / "aba_asp-ASP-ABAlearn_B.zip")
pytestmark = pytest.mark.skipif(not ZIP.exists(),
                                reason="Zenodo archive not downloaded")


@pytest.fixture(scope="module")
def table1():
    return dict(load_table1(ZIP))       # sizes are asserted against Table 1


def test_read_as_the_released_tool_reads(table1):
    p = table1["nixon_diamond_2"]
    # The file writes contrary(votes_rep(A), democrat(A)); the assumption uses X.
    assert p.background.contraries["votes_rep(X)"] == "democrat(X)"
    assert p.learnable == ["pacifist", "republican", "democrat", "abnormal_quaker"]
    # dom holds every constant, examples included (lines 211-212).
    assert "n75" in table1["acute"].domain


def test_nixon_diamond_2_gives_the_papers_solution(table1):
    """R'_2 (PDF lines 247-255), which Example 10 reaches with Algorithm 1."""
    _, trace = solve_aba_learning(table1["nixon_diamond_2"])
    assert sorted(r.to_prolog() for r in trace.final_framework.new_rules) == [
        "abnormal_quaker(X) :- republican(X), alpha_0(X).",
        "c_alpha_0(X) :- quaker(X), normal_quaker(X).",
        "pacifist(X) :- democrat(X).",
    ]
