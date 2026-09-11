"""
Tests for the step probes and the trace scorer.

The load-bearing test here is `test_solver_own_decisions_score_correct`: if
feeding the reference algorithm's own answer back into a probe does not score
correct, the probe is mis-specified and every model number from it is
meaningless. Two probes were found mis-specified exactly that way — one
demanding an intensional contrary that Algorithm 1 only produces on a LATER Gen
iteration (the paper's Example 10, rho17 -> rho19), and one refusing the
assumption-reuse case where line 36 sets S := empty.

Run with:  python -m pytest tests -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.aba_types import Rule, LearningTrace, TransformStep
from src.aba_dataset import ABADataset, make_nixon_diamond
from src.aba_algorithm import (
    solve_aba_learning, gen_phase, assumption_introduction, _current_framework,
)
from src.aba_validator import run_rote_learning
from src.aba_prompts import _parse_rule_line
from src.aba_probes import (
    generate_probes, score_probe, balanced_accuracy, ProbeResult,
    _failing_examples,
)
from src.aba_trace import (
    ground_fact_of, canon, normalise_gold, extract_llm_steps,
)


@pytest.fixture(scope="module")
def problems():
    ds = ABADataset()
    ds.load_builtin_benchmarks(solve=False)
    ds.add_benchmark_suite(n_per_tier=3, seed=42, solve=False)
    ds.anonymize(scheme="letters", anonymize_constants=True)
    return [e.problem for e in ds]


# ─────────────────────────────────────────────────────────────────────────────
# The observer must not perturb the algorithm it observes
# ─────────────────────────────────────────────────────────────────────────────

def test_observer_is_behaviour_neutral(problems):
    for problem in problems:
        facts, ok, _ = run_rote_learning(problem)
        if not ok:
            continue
        _, plain = gen_phase(facts, problem)
        _, watched = gen_phase(facts, problem, observer=lambda *a: None)
        assert [s.to_text() for s in plain.steps] == \
               [s.to_text() for s in watched.steps]
        assert plain.success == watched.success


# ─────────────────────────────────────────────────────────────────────────────
# Probe oracles agree with the algorithm's own decisions
# ─────────────────────────────────────────────────────────────────────────────

def _solver_answer(probe, problem):
    """Render the reference algorithm's own decision in the probe's format."""
    if probe.kind == "role":
        return "\n".join(
            "%s(%s)." % (r.head.split("(")[0], r.body[0].split("=")[1].strip())
            for r in probe.oracle)
    if probe.kind == "fold":
        return probe.oracle[0].to_prolog()
    if probe.kind == "subsume":
        return "YES" if probe.oracle else "NO"
    if probe.kind == "check":
        answer = "YES" if probe.oracle else "NO"
        if not probe.oracle:
            answer += "\n" + "\n".join(sorted(_failing_examples(probe, problem)))
        return answer
    if probe.kind == "introduce":
        learnt = [_parse_rule_line(x) for x in probe.state["learnt"]]
        folded = _parse_rule_line(probe.state["folded"])
        idx = probe.state["idx"]
        fw_now = _current_framework(problem.background, learnt,
                                    probe.state["new_asms"])
        test = learnt[:idx] + [folded] + learnt[idx + 1:]
        res = assumption_introduction(folded, problem.background, fw_now,
                                      problem, test, probe.state["new_asms"])
        if res is None:
            return None
        rule, asm, contra, cfacts = res
        out = "RULE: %s\nASSUMPTION: %s defeated_by %s\n" % (
            rule.to_prolog(), asm, contra)
        return out + "\n".join("CONTRARY: %s" % c.to_prolog() for c in cfacts)
    return None


def test_solver_own_decisions_score_correct(problems):
    checked = {k: 0 for k in ("role", "fold", "check", "introduce", "subsume")}
    for problem in problems:
        for probe in generate_probes(problem, max_per_kind=2):
            answer = _solver_answer(probe, problem)
            if answer is None:
                continue
            correct, score, parsed = score_probe(probe, answer, problem)
            assert correct, (
                f"{probe.probe_id} ({probe.kind}) rejected the algorithm's own "
                f"answer: {answer!r} -> parsed {parsed!r}")
            checked[probe.kind] += 1
    for kind, n in checked.items():
        assert n > 0, f"no {kind} probes were exercised"


def test_introduce_ignores_a_model_supplied_contrary():
    """R3 is two choices; the contrary's extension is not one of them.

    `applyAsmIntro` returns S, but S is computed by ASP (Algorithm 1 line 44)
    and rote-learnt at lines 23-25 — the algorithm never chooses it. Scoring it
    would demand more of the model than of the reference.
    """
    problem, _ = make_nixon_diamond()
    probes = [p for p in generate_probes(problem, max_per_kind=4)
              if p.kind == "introduce"]
    assert probes, "the Nixon problem must produce an R3 probe"
    folded = _parse_rule_line(probes[0].state["folded"])
    two_lines = ("RULE: %s :- %s, alpha(X).\n"
                 "ASSUMPTION: alpha(X) defeated_by c_alpha(X)"
                 % (folded.head, ", ".join(folded.body)))
    with_junk = two_lines + "\nCONTRARY: c_alpha(X) :- X = zzz_nonexistent."
    assert score_probe(probes[0], two_lines, problem)[:2] == \
           score_probe(probes[0], with_junk, problem)[:2]


def test_both_answer_formats_score_identically(problems):
    """`RULE:`/`ASSUMPTION:` and `NEW RULES:`/`NEW ASSUMPTIONS:` are one answer.

    The probe prompt asks for the first, the shared SYSTEM_PROMPT for the
    second, so the corpus contains both: Qwen2.5-14B wrote `RULE:` on 103/103
    introduce probes, 32B on 11/103. Scoring only the labelled form measured
    which instruction a model obeyed, not whether its R3 was legal.
    """
    compared = 0
    for problem in problems:
        for probe in generate_probes(problem, max_per_kind=2):
            if probe.kind != "introduce":
                continue
            labelled = _solver_answer(probe, problem)
            if labelled is None:
                continue
            rules, asms = [], []
            for ln in labelled.split("\n"):
                if ln.startswith(("RULE:", "CONTRARY:")):
                    rules.append(ln.split(":", 1)[1].strip())
                elif ln.startswith("ASSUMPTION:"):
                    asms.append(ln.split(":", 1)[1].strip())
            block = ("NEW RULES:\n" + "\n".join(rules)
                     + "\n\nNEW ASSUMPTIONS:\n" + "\n".join(asms))
            assert score_probe(probe, block, problem)[:2] == \
                   score_probe(probe, labelled, problem)[:2], \
                   f"{probe.probe_id}: formats disagree\n{block!r}"
            compared += 1
    assert compared > 0, "no introduce probes were exercised"


def test_echoed_contraries_are_not_read_as_the_proposal():
    """The echoed problem declares `<asm> defeated_by <contrary>` of its own.

    Qwen2.5-7B echoes the problem after its answer in 415/780 probes. Accepting
    a bare `defeated_by` line without stripping that region first would score
    the BACKGROUND's contraries as the model's proposed assumption.
    """
    problem, _ = make_nixon_diamond()
    probes = [p for p in generate_probes(problem, max_per_kind=4)
              if p.kind == "introduce"]
    assert probes, "the Nixon problem must produce an R3 probe"
    folded = _parse_rule_line(probes[0].state["folded"])
    echo = "\n".join("  %s defeated_by %s" % (a, c)
                     for a, c in problem.background.contraries.items())
    answer = ("NEW RULES:\n%s :- %s, alpha(X).\n\n"
              "NEW ASSUMPTIONS:\nalpha(X) defeated_by c_alpha(X)\n\n"
              "=== BACKGROUND KNOWLEDGE (ABA framework) ===\n"
              "%% Assumptions A, with their contraries\n%s\n"
              % (folded.head, ", ".join(folded.body), echo))
    _, _, parsed = score_probe(probes[0], answer, problem)
    assert "alpha" in parsed, f"read the echoed background instead: {parsed!r}"


def test_assumption_reuse_needs_no_contrary_rule():
    """Algorithm 1 line 36: reusing an existing assumption sets S := empty."""
    problem, _ = make_nixon_diamond()
    probes = [p for p in generate_probes(problem, max_per_kind=4)
              if p.kind == "introduce"]
    assert probes, "the Nixon problem must produce an R3 probe"
    asm = problem.background.assumptions[0]
    contra = problem.background.contraries[asm]
    folded = _parse_rule_line(probes[0].state["folded"])
    answer = ("RULE: %s :- %s, %s.\nASSUMPTION: %s defeated_by %s"
              % (folded.head, ", ".join(folded.body), asm, asm, contra))
    # Must parse and be judged on the solution criterion, never rejected as
    # "incomplete" merely for carrying no CONTRARY line.
    _, _, parsed = score_probe(probes[0], answer, problem)
    assert parsed != "<incomplete>"


# ─────────────────────────────────────────────────────────────────────────────
# Binary probes are read against their 0.50 floor
# ─────────────────────────────────────────────────────────────────────────────

def test_constant_answer_scores_exactly_one_half():
    """A model that always says YES must land on the chance floor, not above."""
    results = []
    for oracle in [True] * 7 + [False] * 3:          # deliberately unbalanced
        results.append(ProbeResult(
            probe_id="x", problem_id="p", kind="check", model_name="const",
            oracle_bool=oracle, correct=(oracle is True),
        ))
    assert balanced_accuracy(results) == pytest.approx(0.5)
    # Raw accuracy would have flattered the same model:
    assert sum(r.correct for r in results) / len(results) == pytest.approx(0.7)


def test_balanced_accuracy_is_undefined_without_both_classes():
    one_class = [ProbeResult(probe_id="x", problem_id="p", kind="subsume",
                             model_name="m", oracle_bool=True, correct=True)]
    assert balanced_accuracy(one_class) is None


def test_binary_probes_carry_both_classes(problems):
    """Balanced accuracy is only estimable if both YES and NO instances occur."""
    for kind in ("check", "subsume"):
        oracles = {p.oracle for problem in problems
                   for p in generate_probes(problem, max_per_kind=2)
                   if p.kind == kind}
        assert oracles == {True, False}, f"{kind} probes are single-class"


# ─────────────────────────────────────────────────────────────────────────────
# Folding probe accepts any LEGAL fold, not only the solver's choice
# ─────────────────────────────────────────────────────────────────────────────

def test_fold_probe_accepts_every_legal_candidate(problems):
    seen_multi = False
    for problem in problems:
        for probe in generate_probes(problem, max_per_kind=4):
            if probe.kind != "fold" or len(probe.oracle) < 2:
                continue
            seen_multi = True
            for candidate in probe.oracle:
                ok, _, _ = score_probe(probe, candidate.to_prolog(), problem)
                assert ok, f"legal fold rejected: {candidate.to_prolog()}"
    assert seen_multi, "no probe with alternative folds was found"


# ─────────────────────────────────────────────────────────────────────────────
# Trace scorer: canonical forms
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("text", ["p(a).", "p(a) :- a = a.", "p(X) :- X = a."])
def test_ground_fact_spellings_are_one_fact(text):
    """Models write the middle form, the solver writes the last."""
    rule = _parse_rule_line(text)
    assert ground_fact_of(rule) == ("p", "a")
    assert canon(rule) == "p(X) :- X = a."


def test_alpha_renaming_makes_model_and_solver_names_match():
    gold = _parse_rule_line("c_alpha_0(X) :- quaker(X).")
    model = _parse_rule_line("c_alpha(X) :- quaker(X).")
    assert canon(gold, {}) == canon(model, {})


def test_gold_r3_step_expands_into_a_fold_and_an_introduction():
    """The recorded R3 step keeps the PRE-FOLD ground fact as its input, which
    would charge a faithful model an extra step."""
    problem, _ = make_nixon_diamond()
    _, trace = solve_aba_learning(problem)
    assert any(s.step_type == "assumption_introduction" for s in trace.steps)
    symbols = [s.symbol for s in normalise_gold(trace, problem.background)]
    for i, sym in enumerate(symbols):
        if sym == "R3":
            assert "R2" in symbols[:i], "R3 must be preceded by its implicit fold"


def test_trace_to_dict_round_trips():
    problem, _ = make_nixon_diamond()
    _, trace = solve_aba_learning(problem)
    d = trace.to_dict()
    assert d["problem_id"] == problem.problem_id
    assert len(d["steps"]) == len(trace.steps)
    assert d["symbols"] == [s.rule_symbol for s in trace.steps]
    assert all(s["rule_symbol"] in ("R1", "R2", "R3", "R4") for s in d["steps"])


def test_echoed_problem_statement_is_not_read_as_rote_learning():
    """Models echo the prompt back; its '+ t(a)' lines are examples, not facts."""
    problem, _ = make_nixon_diamond()
    raw = ("NEW RULES:\npacifist(X) :- democrat(X).\n\n"
           "NEW ASSUMPTIONS:\nNONE\n\n"
           "=== POSITIVE EXAMPLES ===\n  + pacifist(a)\n  + pacifist(c)\n"
           "=== NEGATIVE EXAMPLES ===\n  - pacifist(b)\n")
    steps, _ = extract_llm_steps(raw, problem.background, problem.learnable)
    assert not any(s.symbol == "R1" for s in steps)
