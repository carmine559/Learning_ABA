"""Golden master for the reference algorithm's own output.

The thesis scores the LLM on FIDELITY to ASP-ABAlearnB, so the algorithm is the
measuring instrument. Any change to `src/aba_algorithm.py` that silently moves
the instrument invalidates every number already reported against it — including
the 12 model-mode files in `experiments/05_scale_4bit_probes_v2/`.

This test pins the instrument. It regenerates the exact 103-problem corpus set
05 used and asserts that `solve_aba_learning` still produces byte-identical
`LearningTrace.to_dict()` records for every one of them.

It exists specifically to make the trace-logging work safe: that work adds an
observer to the algorithm, and an observer is only a spectator if the steps it
watches are unchanged. Run this BEFORE and AFTER any edit to the algorithm.

The whole pass takes ~4s (3s of it is `build_dataset`), so it runs by default
rather than hiding behind a marker.

Run with:  python -m pytest tests/test_golden_traces.py -q
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from main import build_dataset
from src.aba_algorithm import solve_aba_learning

# Set 05 is the committed reference run. `symbolic_traces.jsonl` is written per
# bench_* directory but its contents are MODEL-INDEPENDENT (main.py writes the
# symbolic baseline, not the LLM's answer), so any copy will do.
_SET_05 = (Path(__file__).resolve().parents[1]
           / "experiments" / "05_scale_4bit_probes_v2")

# The corpus parameters set 05 ran with. These are what make the regeneration
# reproducible; changing any of them changes which problems are compared.
_BENCHMARK_PER_TIER = 20
_ANONYMIZE_SCHEME = "letters"
_EXPECTED_N = 103

# Traces that changed DELIBERATELY since set 05, and why. Their current records
# are pinned in tests/golden/repinned.jsonl; the other 101 still match set 05.
_REPINNED = {
    "nixon_diamond_anon": "line 40: a failed reuse fails the fold instead of "
                          "minting (paper, Algorithm 1)",
    "tax_law_anon": "line 40 as above, plus the dom(X) fold candidate "
                    "(paper, Definition 3)",
}
_REPINNED_FILE = Path(__file__).resolve().parent / "golden" / "repinned.jsonl"


def _read_jsonl(path: Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            out[rec["problem_id"]] = rec
    return out


def _committed_traces() -> dict:
    paths = sorted(_SET_05.glob("bench_*/symbolic_traces.jsonl"))
    if not paths:
        pytest.skip(f"no committed traces under {_SET_05}")
    out = _read_jsonl(paths[0])
    repinned = _read_jsonl(_REPINNED_FILE)
    assert set(repinned) == set(_REPINNED), "repinned.jsonl out of step with _REPINNED"
    out.update(repinned)
    return out


@pytest.fixture(scope="module")
def committed():
    return _committed_traces()


@pytest.fixture(scope="module")
def regenerated():
    ds = build_dataset(
        benchmark_per_tier=_BENCHMARK_PER_TIER,
        solve_symbolic=False,
        anonymize=True,
        anonymize_scheme=_ANONYMIZE_SCHEME,
    )
    return {e.problem.problem_id: e.problem for e in ds}


def test_corpus_regenerates_to_the_same_problem_set(committed, regenerated):
    """The problem ids must match before any trace comparison is meaningful.

    A mismatch here means the GENERATOR moved, not the algorithm — check
    `src/aba_dataset.py` and the seed, not `src/aba_algorithm.py`.
    """
    assert len(committed) == _EXPECTED_N
    assert set(regenerated) == set(committed), (
        f"corpus drift: {len(set(regenerated) - set(committed))} new, "
        f"{len(set(committed) - set(regenerated))} missing"
    )


def test_traces_are_byte_identical_to_the_committed_reference(
    committed, regenerated
):
    """Every step, symbol, note and final rule, unchanged.

    `to_dict()` carries `symbols`, the full `steps` list and the final
    framework, so this covers the decision SEQUENCE and not merely the answer.
    """
    differing = []
    for pid, problem in sorted(regenerated.items()):
        _, trace = solve_aba_learning(problem)
        if trace.to_dict() != committed[pid]:
            differing.append(pid)
    assert not differing, (
        f"{len(differing)}/{len(regenerated)} traces changed, first few: "
        f"{differing[:5]}"
    )


def test_nixon_reproduces_the_papers_solution():
    """The paper's own worked problem (Examples 1 and 10): our reference must
    learn the paper's rules, up to the name of the minted assumption."""
    from src.aba_dataset import make_nixon_diamond
    problem, paper = make_nixon_diamond()
    solution, trace = solve_aba_learning(problem)
    norm = lambda rules: sorted(r.to_prolog().replace("alpha_0", "alpha")
                                for r in rules)
    assert trace.success
    assert norm(solution.new_rules) == norm(paper.new_rules)


def test_observer_none_is_the_default_path(regenerated):
    """Guards the property the instrumentation work depends on.

    `solve_aba_learning` must stay callable with no observer and must not
    require one. If this ever needs updating, the spectator contract has been
    broken.
    """
    problem = next(iter(regenerated.values()))
    solution, trace = solve_aba_learning(problem)
    assert trace.success
    assert solution is not None
