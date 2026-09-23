"""Rich sidecar record of what ASP-ABAlearnB actually decided.

`LearningTrace` records the steps the algorithm ACCEPTED. That is enough to
reconstruct the answer, and it is what `symbolic_traces.jsonl` has always held,
but it throws away everything that distinguishes EXECUTING the algorithm from
arriving at its answer:

  * every satisfiability verdict — including the negative ones, i.e. the
    decision to KEEP a fact rather than subsume it, which left no record at all;
  * the fold candidates that were tried and REJECTED before the accepted one,
    and the background rule each was folded from (the paper's rho2);
  * whether an assumption was REUSED (Definition 4, line 37) or freshly
    MINTED (line 42), and the line-40 FAILURE when every reusable one is
    rejected. The accepted step looks identical whether reused or minted, so no
    stored result could tell the branches apart;
  * Gen's BACKTRACKING: a choice whose continuation failed is retracted and the
    fact's next option tried, possibly after later facts were already
    processed. Those later events are kept, marked `abandoned`.

Those are exactly the semantic decisions the prompted models were found NOT to
replicate, so they have to be in the supervision if trace training is to be
tested against them at all.

DESIGN. This is a SIDECAR. It adds no field to `TransformStep`/`LearningTrace`
and changes no algorithm behaviour: it rides the existing spectator `observer`
hook, and `RunRecord` embeds `LearningTrace.to_dict()` verbatim under
`symbolic_trace`, so `aba_trace`, `rescore.py` and `analysis/*` keep working
unchanged and the sidecar diffs against the committed 103 for free.
`tests/test_golden_traces.py` pins the no-behaviour-change property.

Usage:
    solution, trace, record = solve_and_log(problem)
"""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

from src.aba_types import ABAFramework, LearningProblem, LearningTrace, Rule
from src.aba_algorithm import solve_aba_learning


def _git_rev() -> str:
    """Short HEAD, with a dirty flag. Provenance for a generated corpus."""
    try:
        rev = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=10)
        if rev.returncode != 0:
            return "unknown"
        head = rev.stdout.strip()
        st = subprocess.run(["git", "status", "--porcelain"],
                            capture_output=True, text=True, timeout=10)
        return head + ("-dirty" if st.stdout.strip() else "")
    except Exception:
        return "unknown"


def _p(rule: Optional[Rule]) -> Optional[str]:
    return rule.to_prolog() if rule is not None else None


@dataclass
class FoldCandidate:
    """One candidate from `apply_folding`, in the order the algorithm saw it."""
    rule: str
    via: List[str]                  # background rule(s) folded in, in order
    depth: int                      # len(via); >1 is a multi-step fold
    rank: int                       # position in the candidate list
    sat: Optional[bool] = None      # the line-18 verdict, None if never checked
    accepted: bool = False
    # Pass 2 (assumption introduction) on this candidate. `reuse_scan` is None
    # when pass 2 never reached it — distinct from [] ("reached, but no
    # background assumption fits the body").
    reuse_scan: Optional[List[str]] = None
    asm_ok: Optional[bool] = None   # did applyAsmIntro succeed on it

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class AsmAttempt:
    """One pass through applyAsmIntro's reuse loop, or the mint that follows."""
    asm: Optional[str]
    mode: str                       # "reuse" | "mint"
    sat: Optional[bool] = None      # reuse: did the framework become a solution
    rote_ok: Optional[bool] = None  # mint: did RoLe find the contrary facts
    contrary: Optional[str] = None
    accepted: bool = False
    # The fold candidate this attempt guards. Pass 2 walks the candidates in
    # order and runs a full reuse-then-mint on each until one succeeds, so
    # without this an attempt cannot be attributed once two candidates reach it.
    for_fold: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class FactEvent:
    """One iteration of the Gen while-queue: everything done to one fact."""
    idx: int
    input_rule: str
    subsume_sat: Optional[bool] = None       # R4 verdict (False = kept)
    candidates: List[FoldCandidate] = field(default_factory=list)
    chosen_fold: Optional[str] = None
    chosen_rank: Optional[int] = None
    asm_attempts: List[AsmAttempt] = field(default_factory=list)
    guarded_rule: Optional[str] = None       # the R3 output, chosen_fold + asm
    new_assumption: Optional[str] = None
    contrary: Optional[str] = None
    contrary_facts: List[str] = field(default_factory=list)
    outcome: str = "unknown"
    # subsumed | already_intensional | folded | folded_with_assumption
    # | failed (no option left; the search backtracked out of this fact)
    # Choices made for this fact and later RETRACTED because their
    # continuation failed, oldest first.
    retracted: List[Dict[str, Any]] = field(default_factory=list)
    # True when this event lies on a branch the search abandoned: it happened,
    # but it is not part of the derivation that produced the answer.
    abandoned: bool = False

    @property
    def backtracked(self) -> bool:
        """True when the algorithm tried something and had to retreat.

        Four ways: a fold candidate was rejected before the accepted one, the
        accepted fold was not the first candidate, a reuse attempt failed, or a
        choice was retracted after its continuation failed.
        """
        rejected_fold = any(c.sat is False for c in self.candidates)
        late_choice = self.chosen_rank is not None and self.chosen_rank > 0
        failed_reuse = any(a.mode == "reuse" and a.sat is False
                           for a in self.asm_attempts)
        return bool(rejected_fold or late_choice or failed_reuse
                    or self.retracted)

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["candidates"] = [c.to_dict() for c in self.candidates]
        d["asm_attempts"] = [a.to_dict() for a in self.asm_attempts]
        d["backtracked"] = self.backtracked
        return d


@dataclass
class RunRecord:
    problem_id: str
    role_facts: List[str] = field(default_factory=list)
    events: List[FactEvent] = field(default_factory=list)
    symbolic_trace: Dict = field(default_factory=dict)   # to_dict(), verbatim
    final_new_rules: List[str] = field(default_factory=list)
    final_assumptions: List[str] = field(default_factory=list)
    final_contraries: Dict[str, str] = field(default_factory=dict)
    success: bool = False
    intensional: bool = False
    n_clingo_calls: int = 0
    wall_s: float = 0.0
    code_rev: str = "unknown"
    budget_exceeded: bool = False

    @property
    def n_backtracks(self) -> int:
        return sum(1 for e in self.events if e.backtracked)

    @property
    def n_retractions(self) -> int:
        """Choices undone because a LATER fact failed (cross-fact backtracks)."""
        return sum(len(e.retracted) for e in self.events)

    @property
    def path(self) -> List[FactEvent]:
        """The events of the derivation that produced the answer."""
        return [e for e in self.events if not e.abandoned]

    def to_dict(self) -> Dict:
        return {
            "problem_id": self.problem_id,
            "role_facts": list(self.role_facts),
            "events": [e.to_dict() for e in self.events],
            "n_backtracks": self.n_backtracks,
            "n_retractions": self.n_retractions,
            "budget_exceeded": self.budget_exceeded,
            "symbolic_trace": self.symbolic_trace,
            "final_new_rules": list(self.final_new_rules),
            "final_assumptions": list(self.final_assumptions),
            "final_contraries": dict(self.final_contraries),
            "success": self.success,
            "intensional": self.intensional,
            "n_clingo_calls": self.n_clingo_calls,
            "wall_s": round(self.wall_s, 3),
            "code_rev": self.code_rev,
        }


class TraceRecorder:
    """Observer that assembles the flat notification stream into FactEvents.

    The stream is sequential and single-threaded, so "the currently open event"
    is well defined. Per fact the algorithm emits:

        subsume -> [fold -> check* -> (asm_reuse_scan -> asm_reuse_try*
                                       -> asm_decision -> asm_intro)*]
                -> fact_done | fact_failed

    `asm_*` notifications arrive from inside `asm_intro_options` with idx=-1,
    so they are attached to the open event rather than matched by index. Their
    `rule` argument is the fold CANDIDATE being guarded, which is how an
    attempt is attributed when pass 2 works through more than one candidate.

    BACKTRACKING. After a fact's `fact_done`, later facts may fail; the search
    then sends `backtrack` for the fact whose choice it is undoing. That fact's
    most recent live event is REOPENED — its choice is moved to `retracted` —
    and every event after it is marked `abandoned`. The fact's remaining
    options then stream in as usual, onto the reopened event.
    """

    @staticmethod
    def _candidate(ev: FactEvent, rule: Optional[str]) -> Optional[FoldCandidate]:
        return next((c for c in ev.candidates if c.rule == rule), None)

    def __init__(self) -> None:
        self.role_facts: List[str] = []
        self.events: List[FactEvent] = []
        self.n_clingo_calls = 0
        self.budget_exceeded = False
        self._cur: Optional[FactEvent] = None

    def _open(self, idx: int, rule: Rule) -> FactEvent:
        ev = FactEvent(idx=idx, input_rule=_p(rule))
        self.events.append(ev)
        self._cur = ev
        return ev

    def _reopen(self, idx: int, rule_text: Optional[str]) -> None:
        """Undo the fact's current choice: its continuation failed."""
        k = next((i for i in range(len(self.events) - 1, -1, -1)
                  if not self.events[i].abandoned
                  and self.events[i].idx == idx
                  and self.events[i].input_rule == rule_text), None)
        if k is None:                       # defensive: stream out of order
            return
        ev = self.events[k]
        for later in self.events[k + 1:]:
            later.abandoned = True
        ev.retracted.append({
            "outcome": ev.outcome,
            "fold": ev.chosen_fold,
            "guarded_rule": ev.guarded_rule,
            "assumption": ev.new_assumption,
            "contrary_facts": list(ev.contrary_facts),
        })
        retracted_fold = ev.chosen_fold
        ev.outcome = "unknown"
        ev.chosen_fold = ev.chosen_rank = None
        ev.guarded_rule = ev.new_assumption = ev.contrary = None
        ev.contrary_facts = []
        for c in ev.candidates:
            c.accepted = False
            if c.rule == retracted_fold and c.asm_ok:
                c.asm_ok = False            # it offered an option; that failed
        for a in ev.asm_attempts:
            a.accepted = False
        self._cur = ev

    def __call__(self, kind, learnt, new_asms, idx, rule, extra) -> None:
        if kind == "role":
            self.role_facts = [_p(f) for f in extra["facts"]]
            self.n_clingo_calls += 1
            return

        if kind == "subsume":
            ev = self._open(idx, rule)
            ev.subsume_sat = bool(extra["answer"])
            self.n_clingo_calls += 1
            return

        # The search notifications can arrive with no event open.
        if kind == "backtrack":
            self._reopen(idx, _p(rule))
            return
        if kind == "fact_failed":
            if self._cur is not None:
                self._cur.outcome = "failed"
            self._cur = None
            return
        if kind == "search_budget_exceeded":
            self.budget_exceeded = True
            return

        ev = self._cur
        if ev is None:                      # defensive: stream out of order
            return

        if kind == "fold":
            vias = extra.get("via") or [[] for _ in extra["candidates"]]
            for rank, (cand, via) in enumerate(zip(extra["candidates"], vias)):
                ev.candidates.append(FoldCandidate(
                    rule=_p(cand), via=[_p(v) for v in via],
                    depth=len(via), rank=rank))

        elif kind == "check":
            self.n_clingo_calls += 1
            folded = _p(extra["folded"])
            sat = bool(extra["answer"])
            for c in ev.candidates:
                if c.rule == folded and c.sat is None:
                    c.sat = sat
                    break
            if sat:
                ev.chosen_fold = folded
                ev.chosen_rank = next(
                    (c.rank for c in ev.candidates if c.rule == folded), None)
                for c in ev.candidates:
                    if c.rule == folded:
                        c.accepted = True

        elif kind == "asm_reuse_scan":
            cand = self._candidate(ev, _p(rule))
            if cand is not None:
                cand.reuse_scan = list(extra["candidates"])

        elif kind == "asm_reuse_try":
            self.n_clingo_calls += 1
            ev.asm_attempts.append(AsmAttempt(
                asm=extra["asm"], mode="reuse", sat=bool(extra["answer"]),
                for_fold=_p(rule)))

        elif kind == "asm_decision":
            if extra["mode"] == "reuse":
                # The last reuse attempt is the one that succeeded.
                for a in reversed(ev.asm_attempts):
                    if (a.mode == "reuse" and a.asm == extra["asm"]
                            and a.for_fold == _p(rule)):
                        a.accepted = True
                        a.contrary = extra.get("contrary")
                        break
            elif extra["mode"] == "mint":
                # ("fail" — line 40 — adds no attempt: the rejected reuses are
                # already recorded, and `asm_ok` goes False via `asm_intro`.)
                self.n_clingo_calls += 1      # the RoLe call for the contrary
                ev.asm_attempts.append(AsmAttempt(
                    asm=extra["asm"], mode="mint",
                    rote_ok=bool(extra.get("rote_ok")),
                    contrary=extra.get("contrary"),
                    accepted=bool(extra.get("rote_ok")),
                    for_fold=_p(rule)))

        elif kind == "asm_intro":
            result = extra.get("answer")
            cand = self._candidate(ev, _p(extra["folded"]))
            if cand is not None:
                cand.asm_ok = result is not None
            if result is not None:
                defeasible, asm, contrary, contra_facts = result
                ev.chosen_fold = _p(extra["folded"])
                ev.chosen_rank = cand.rank if cand is not None else None
                # NOT cand.accepted: that records the fold passing line 18 on
                # its own, which every pass-2 candidate already failed. Pass-2
                # success is `asm_ok`.
                ev.guarded_rule = _p(defeasible)
                ev.new_assumption = asm
                ev.contrary = contrary
                ev.contrary_facts = [_p(r) for r in contra_facts]

        elif kind == "fact_done":
            ev.outcome = extra["outcome"]
            self._cur = None


def solve_and_log(
    problem: LearningProblem,
    verbose: bool = False,
) -> Tuple[Optional[ABAFramework], LearningTrace, RunRecord]:
    """`solve_aba_learning` with a recorder attached. Same answer, plus the why."""
    rec = TraceRecorder()
    t0 = time.time()
    solution, trace = solve_aba_learning(problem, verbose=verbose, observer=rec)
    wall = time.time() - t0

    record = RunRecord(
        problem_id=problem.problem_id,
        role_facts=rec.role_facts,
        events=rec.events,
        symbolic_trace=trace.to_dict(),
        success=trace.success,
        n_clingo_calls=rec.n_clingo_calls,
        wall_s=wall,
        code_rev=_git_rev(),
        budget_exceeded=rec.budget_exceeded,
    )
    if solution is not None:
        record.final_new_rules = [r.to_prolog() for r in solution.new_rules]
        record.final_assumptions = list(solution.assumptions)
        record.final_contraries = dict(solution.contraries)
        record.intensional = all(r.is_intensional() for r in solution.new_rules)
    return solution, trace, record
