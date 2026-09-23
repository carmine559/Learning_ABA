"""Rebuild the algorithm's framework from what was logged.

A training target is only supervision if it actually determines the answer.
This module proves that, two ways:

  replay_record(record, problem)
      Walk the RunRecord's FactEvents, applying each recorded outcome to a
      learnt-rule list, and rebuild the framework. Proves the RECORD is
      complete — nothing the algorithm did is missing from it.

  replay_text(text, problem)
      Rebuild the framework from the TRACE TARGET TEXT ALONE, reading only the
      lines that apply a transformation. Proves the SERIALISATION is lossless:
      a model that reproduces the trace has, in doing so, written down the
      algorithm's answer. This is also the natural basis for an
      execution-fidelity reward later — replay what the model wrote and compare.

`check_example` asserts both agree with the algorithm's own final framework AND
with `parse_llm_output` reading the answer block, and that the result is still a
brave-entailment solution. The Day-2 corpus builder drops any problem that fails
it, with the reason, rather than training on it.

Only APPLIED transformations change state during a text replay:

    R1 <rule>.                append (RoLe facts and contrary facts alike)
    fact <rule>.              move the cursor to that learnt rule
    R4? yes, removed.         remove the rule under the cursor
    R2 <rule>. / R3 <rule>.   replace the rule under the cursor
    <a> defeated_by <c>       register a freshly minted assumption
    R3 reuse? [<a>] yes.      register a reused assumption (a no-op on the
                              final framework, mirrored for exactness)

Everything else — candidates, verdicts, the bracketed considerations — is
decision record, not state change, and is skipped.

CLI:  python -m src.aba_replay [--benchmark 20]
"""
from __future__ import annotations

import argparse
import re
import sys
from typing import Dict, List, Optional

from src.aba_types import ABAFramework, LearningProblem, Rule
from src.aba_algorithm import _current_framework
from src.aba_prompts import (
    _parse_rule_line, parse_llm_output, _RULES_HDR_RE,
)
from src.aba_validator import check_brave_entailment
from src.aba_tracelog import RunRecord


class ReplayError(AssertionError):
    """A logged step does not apply to the state the replay has reached."""


def _rule(text: str) -> Rule:
    r = _parse_rule_line(text)
    if r is None:
        raise ReplayError(f"unparseable rule: {text!r}")
    return r


# ─────────────────────────────────────────────────────────────────────────────
# From the record
# ─────────────────────────────────────────────────────────────────────────────

def replay_record(record: RunRecord, problem: LearningProblem) -> ABAFramework:
    learnt: List[Rule] = [_rule(f) for f in record.role_facts]
    new_asms: Dict[str, str] = {}

    for ev in record.events:
        if not (0 <= ev.idx < len(learnt)):
            raise ReplayError(f"event idx {ev.idx} out of range ({len(learnt)})")
        # The recorded idx must point at the rule the event says it processed.
        # This is what catches a record whose events drifted out of step.
        if learnt[ev.idx].to_prolog() != ev.input_rule:
            raise ReplayError(
                f"idx {ev.idx} holds {learnt[ev.idx].to_prolog()!r}, "
                f"event says {ev.input_rule!r}")

        if ev.outcome == "subsumed":
            learnt.pop(ev.idx)
        elif ev.outcome == "folded":
            learnt[ev.idx] = _rule(ev.chosen_fold)
        elif ev.outcome == "folded_with_assumption":
            learnt[ev.idx] = _rule(ev.guarded_rule)
            new_asms[ev.new_assumption] = ev.contrary
            learnt.extend(_rule(cf) for cf in ev.contrary_facts)
        elif ev.outcome in ("already_intensional", "kept_ground"):
            pass
        else:
            raise ReplayError(f"unknown outcome {ev.outcome!r}")

    return _current_framework(problem.background, learnt, new_asms)


# ─────────────────────────────────────────────────────────────────────────────
# From the text
# ─────────────────────────────────────────────────────────────────────────────

_APPLIED_RE  = re.compile(r'^(R1|R2|R3)\s+([a-z]\w*\(.*)$')
_FACT_RE     = re.compile(r'^fact\s+([a-z]\w*\(.*)$')
_R4_YES_RE   = re.compile(r'^R4\?\s+yes\b')
_REUSE_YES_RE = re.compile(r'^R3\s+reuse\?\s+\[([^\]]+)\]\s+yes\b')
_DECL_RE     = re.compile(
    r'^([a-z]\w*\([^()]*\))\s+defeated_by\s+([a-z]\w*\([^()]*\))\s*$')


def trace_lines(text: str) -> List[str]:
    """The lines before the final `NEW RULES:` header — the working."""
    starts = [m.start() for m in _RULES_HDR_RE.finditer(text)]
    body = text[:starts[-1]] if starts else text
    return [ln.strip() for ln in body.split("\n")]


def replay_text(text: str, problem: LearningProblem) -> ABAFramework:
    bg = problem.background
    learnt: List[Rule] = []
    new_asms: Dict[str, str] = {}
    cur: Optional[int] = None

    for n, ln in enumerate(trace_lines(text), 1):
        m = _FACT_RE.match(ln)
        if m:
            want = _rule(m.group(1)).to_prolog()
            cur = next((i for i, r in enumerate(learnt)
                        if r.to_prolog() == want), None)
            if cur is None:
                raise ReplayError(f"line {n}: 'fact' names a rule not learnt: {want}")
            continue

        if _R4_YES_RE.match(ln):
            if cur is None:
                raise ReplayError(f"line {n}: removal with no current fact")
            learnt.pop(cur)
            cur = None
            continue

        m = _APPLIED_RE.match(ln)
        if m:
            sym, rule = m.group(1), _rule(m.group(2))
            if sym == "R1":
                learnt.append(rule)
            else:
                if cur is None:
                    raise ReplayError(f"line {n}: {sym} with no current fact")
                learnt[cur] = rule
            continue

        m = _DECL_RE.match(ln)
        if m:
            new_asms[m.group(1)] = m.group(2)
            continue

        m = _REUSE_YES_RE.match(ln)
        if m:
            # Mirrors `current.contraries.get(asm, f"c_{asm}")` in
            # assumption_introduction, where current = bg + everything learnt,
            # so an assumption minted earlier in this run is reusable too.
            asm = m.group(1)
            new_asms[asm] = new_asms.get(asm, bg.contraries.get(asm, f"c_{asm}"))
            continue

    return _current_framework(bg, learnt, new_asms)


# ─────────────────────────────────────────────────────────────────────────────
# The check a training example must pass
# ─────────────────────────────────────────────────────────────────────────────

def _signature(fw: ABAFramework) -> Dict:
    return {
        "new_rules": [r.to_prolog() for r in fw.new_rules],
        "assumptions": list(fw.assumptions),
        "contraries": dict(fw.contraries),
    }


def check_example(example: Dict, problem: LearningProblem) -> Optional[str]:
    """None if the example is sound supervision, else the reason it is not.

    Four frameworks must coincide: the algorithm's own, the record replay, the
    trace-text replay, and what `parse_llm_output` reads from the answer block
    of either target. And the result must still be a solution.
    """
    truth = _signature(example["solution"])

    try:
        from_record = _signature(replay_record(example["record"], problem))
    except ReplayError as e:
        return f"record_replay_error: {e}"
    if from_record != truth:
        return "record_replay_mismatch"

    try:
        from_text = replay_text(example["trace_target"], problem)
    except ReplayError as e:
        return f"text_replay_error: {e}"
    if _signature(from_text) != truth:
        return "text_replay_mismatch"

    for arm in ("trace_target", "endpoint_target"):
        repairs: List[str] = []
        parsed = parse_llm_output(example[arm], problem.background, repairs)
        if parsed is None:
            return f"{arm}_unparseable"
        if repairs:
            return f"{arm}_needed_repairs: {repairs}"
        if [r.to_prolog() for r in parsed.new_rules] != truth["new_rules"]:
            return f"{arm}_parse_mismatch"
        if dict(parsed.contraries) != truth["contraries"]:
            return f"{arm}_contrary_mismatch"

    sat, _, _ = check_brave_entailment(from_text, problem.positive,
                                       problem.negative, problem.get_domain())
    if not sat:
        return "replayed_framework_not_a_solution"
    return None


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--benchmark", type=int, default=20,
                    help="problems per tier to regenerate (default 20)")
    args = ap.parse_args(argv)

    from main import build_dataset
    from src.aba_sft import sft_example, Untrainable

    ds = build_dataset(benchmark_per_tier=args.benchmark, solve_symbolic=False,
                       anonymize=True, anonymize_scheme="letters")
    ok, failed = 0, []
    for entry in ds:
        p = entry.problem
        try:
            reason = check_example(sft_example(p), p)
        except Untrainable as e:
            reason = f"untrainable: {e}"
        if reason is None:
            ok += 1
        else:
            failed.append((p.problem_id, reason))

    print(f"\nreplay check: {ok}/{len(ds)} examples are sound supervision")
    for pid, reason in failed:
        print(f"  FAIL {pid}: {reason}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
