"""The two SFT serialisations: trace-then-answer, and answer only.

The core ablation asks whether training on algorithm TRACES makes a model
execute ASP-ABAlearnB, or only produce outputs that pass the checker. Its two
arms differ in exactly one thing, the target:

  endpoint  the final framework, in the `NEW RULES:` / `NEW ASSUMPTIONS:`
            format — `solution_to_output_format`, the parser's exact inverse.
  trace     the algorithm's decisions, one per line, followed by the SAME
            endpoint block, byte for byte.

Both arms share one prompt, `problem_to_prompt(problem, mode="sft")` (v4-sft),
so a difference between them can only come from supervision.

THE TRACE GRAMMAR. Line-oriented, one decision per line, in the order the
algorithm made them:

    RoLe.
    R1 <fact>.                          a rote-learnt fact
    Gen.
    fact <rule>.                        start processing a learnt rule
    R4? yes, removed.                   subsumption check: removable -> removed
    R4? no.                             subsumption check: kept
    already intensional.                nothing to fold
    R2 candidates: [<r>] [<r>] ...      the fold candidates, in order
    R2 candidates: none.
    R2? [<r>] no.                       line 18 on one candidate: not a solution
    R2? [<r>] yes.                      ... and on the one that is
    R2 <rule>.                          fold APPLIED
    R3 needed.                          no fold is a solution on its own
    R3 on [<r>]                         try assumption introduction on <r>
    R3 reuse: [<a>] [<a>].              background assumptions fitting the body
    R3 reuse: none.
    R3 reuse? [<a>] no. / yes.          line 18 with that assumption reused
    R3 mint [<a>]: no contrary facts.   fresh assumption, RoLe found no facts
    R3 <rule>.                          assumption introduction APPLIED
    <a>(X) defeated_by <c>(X)           the freshly minted assumption
    kept ground.                        nothing succeeded; the fact stays
    Done.

Two conventions carry all the weight, and both exist to fit the FROZEN scorer
`aba_trace.extract_llm_steps`, which reads rule shapes and ignores prose:

  * Only APPLIED transformations are written as bare rules (`R1/R2/R3 <rule>`).
    Everything merely considered — candidates, rejected folds, assumptions
    tried — is in [square brackets], which `_rule_exprs` strips before looking
    for rules. Unbracketed, a rejected candidate would be scored as an R2 the
    algorithm never took, and a perfectly faithful model would lose precision.
  * The fold under an assumption introduction is written explicitly
    (`R2 <fold>.` then `R3 <fold + asm>.`). The recorded trace collapses the two
    into one R3 step, and `aba_trace.normalise_gold` expands it back into R2+R3;
    writing both is what lets the scorer recognise the R3 at all.

Parser hazards avoided: exactly one `NEW RULES:` header, at the very end, and no
line begins with `=` (which `parse_llm_output` treats as an echoed problem).

These targets are VERIFIED, not assumed: `src/aba_replay.py` rebuilds the
algorithm's framework from the trace text alone, and `tests/test_sft_format.py`
checks every target against the parser and the scorer.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from src.aba_types import ABAFramework, LearningProblem
from src.aba_prompts import (
    problem_to_prompt, solution_to_output_format, SFT_PROMPT_VERSION,
)
from src.aba_tracelog import FactEvent, RunRecord, solve_and_log


class Untrainable(ValueError):
    """A problem whose symbolic run cannot become a training target.

    The message is the reason, suitable for a `rejects.jsonl` row.
    """


def _b(text: str) -> str:
    """Bracket: considered, not applied. Invisible to the fidelity scorer."""
    return f"[{text}]"


# ─────────────────────────────────────────────────────────────────────────────
# Prompt
# ─────────────────────────────────────────────────────────────────────────────

def build_prompt(problem: LearningProblem) -> str:
    """The v4-sft prompt. Identical for both arms by construction."""
    return problem_to_prompt(problem, mode="sft")


# ─────────────────────────────────────────────────────────────────────────────
# Targets
# ─────────────────────────────────────────────────────────────────────────────

def render_endpoint_target(solution: ABAFramework,
                           problem: LearningProblem) -> str:
    return solution_to_output_format(solution, problem.background)


def _render_event(ev: FactEvent) -> List[str]:
    out = [f"fact {ev.input_rule}"]

    if ev.outcome == "subsumed":
        out.append("R4? yes, removed.")
        return out
    out.append("R4? no.")

    if ev.outcome == "already_intensional":
        out.append("already intensional.")
        return out

    # ── pass 1: every fold candidate, in order, until one is a solution ──
    if ev.candidates:
        out.append("R2 candidates: "
                   + " ".join(_b(c.rule) for c in ev.candidates))
    else:
        out.append("R2 candidates: none.")
    for c in ev.candidates:
        if c.sat is None:
            break                          # never checked: the loop had stopped
        out.append(f"R2? {_b(c.rule)} {'yes' if c.sat else 'no'}.")
        if c.sat:
            out.append(f"R2 {c.rule}")
            return out

    # ── pass 2: assumption introduction, candidate by candidate ──
    tried = [c for c in ev.candidates if c.reuse_scan is not None]
    if tried:
        out.append("R3 needed.")
    for c in tried:
        out.append(f"R3 on {_b(c.rule)}")
        out.append("R3 reuse: " + (" ".join(_b(a) for a in c.reuse_scan) + "."
                                   if c.reuse_scan else "none."))
        mine = [a for a in ev.asm_attempts if a.for_fold == c.rule]
        for a in mine:
            if a.mode == "reuse":
                out.append(f"R3 reuse? {_b(a.asm)} {'yes' if a.sat else 'no'}.")
            elif not a.rote_ok:
                out.append(f"R3 mint {_b(a.asm)}: no contrary facts.")
        if c.asm_ok:
            out.append(f"R2 {c.rule}")
            out.append(f"R3 {ev.guarded_rule}")
            minted = any(a.mode == "mint" and a.accepted for a in mine)
            if minted:
                out.append(f"{ev.new_assumption} defeated_by {ev.contrary}")
            out.extend(f"R1 {cf}" for cf in ev.contrary_facts)
            return out

    out.append("kept ground.")
    return out


def render_trace_body(record: RunRecord) -> str:
    """The working: every decision, no answer block."""
    lines = ["RoLe."]
    lines.extend(f"R1 {f}" for f in record.role_facts)
    lines.append("Gen.")
    for ev in record.events:
        lines.extend(_render_event(ev))
    lines.append("Done.")
    return "\n".join(lines)


def render_trace_target(record: RunRecord, solution: ABAFramework,
                        problem: LearningProblem) -> str:
    """Trace body, a blank line, then the endpoint target verbatim."""
    return (render_trace_body(record) + "\n\n"
            + render_endpoint_target(solution, problem))


# ─────────────────────────────────────────────────────────────────────────────
# Scorer ceiling
# ─────────────────────────────────────────────────────────────────────────────

_RECALLS = (("R1", "r1_recall"), ("R2", "r2_recall"),
            ("R3", "r3_recall"), ("R4", "r4_recall"))


def gold_self_score(example: Dict, problem: LearningProblem) -> Dict:
    """What the frozen fidelity scorer awards a PERFECT copy of the trace.

    Every model's fidelity must be read against this, not against 1.0, because
    `aba_trace.score_trace` does not give the gold trace full marks. Measured on
    the 103-problem set, three reasons:

      * `rK_recall` is left at 0.0 when the gold trace has no RK step at all.
        Averaged naively that is "not applicable" scored as failure: a perfect
        model gets r3_recall 0.786 (= 81/103, the defeasible share) instead of
        1.0. Here n/a is None, so it drops out of any mean.
      * R4 is inferred only at the END of the trace, from ground facts that do
        not reach the answer, and `_folds_from` pops the FIRST ground fact that
        folds to a rule. When a subsumed fact precedes one that is later folded
        to the same rule, the scorer removes the wrong fact and charges R4 to
        the survivor (e.g. t2_defeas_0006: precision/recall 0.889). No trace
        text can avoid this — the scorer has no mid-trace removal.
      * `align_exact` is order-sensitive and those end-inferred R4s sit last, so
        it is < 1.0 whenever a gold R4 does not.
    """
    from src.aba_trace import normalise_gold, score_trace
    s = score_trace(example["trace_target"], example["trace"],
                    problem.background, problem.learnable)
    present = {st.symbol for st in normalise_gold(example["trace"],
                                                   problem.background)}
    out = {k: getattr(s, k) for k in ("precision", "recall", "f1", "align_exact")}
    for sym, attr in _RECALLS:
        out[attr] = getattr(s, attr) if sym in present else None
    return out


# ─────────────────────────────────────────────────────────────────────────────
# One training example
# ─────────────────────────────────────────────────────────────────────────────

def sft_example(problem: LearningProblem) -> Dict:
    """Solve, log, and render both arms for one problem.

    The caller decides WHICH problem: for a training corpus it must be the
    TRAIN SPLIT (`split_problem_examples(...).train`), so that neither the
    prompt nor the gold trace ever sees a held-out example. The dead
    `ABADataset.to_sft_records` got exactly this wrong.

    Raises `Untrainable` when the symbolic run cannot supply a target: only a
    successful, intensional run is supervision.
    """
    solution, trace, record = solve_and_log(problem)
    if solution is None or not record.success:
        raise Untrainable("gen_failed")
    if not record.intensional:
        raise Untrainable("not_intensional")
    return {
        "problem_id": problem.problem_id,
        "prompt_version": SFT_PROMPT_VERSION,
        "prompt": build_prompt(problem),
        "trace_target": render_trace_target(record, solution, problem),
        "endpoint_target": render_endpoint_target(solution, problem),
        "record": record,
        "solution": solution,
        "trace": trace,
    }
