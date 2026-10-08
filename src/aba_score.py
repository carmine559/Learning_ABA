"""Score one model output against ASP-ABAlearnB: correctness, fidelity, reward.

The single scorer of the SFT ablation and the source of the RL reward. Every
figure is read against the algorithm's own run on the same problem
(`reference`), and no model output is scored until every gold target scores the
maximum on every field (`python -m src.aba_score --control corpus/v1`).

Instrument per arm:

    field                                   prompted   endpoint   trace
    correctness: valid, clean               yes        yes        yes
    agreement off the examples              yes        yes        yes
    final answer: exact, R2 bodies, R3      yes        yes        yes
    held-out choice (t8/t9)                 yes        yes        yes
    on-policy audit of the written steps    if any     n/a        yes

Correctness is Definition 1 on the posed examples. Problems are posed whole, so
generalisation is measured on unseen problems (test split, held-out tiers,
Table 1) and by `agreement`: over the example predicate's atoms outside E+ and
E-, the share whose status given E+/E- (ALWAYS / NEVER / FREE) matches the
algorithm's framework.

The on-policy audit judges each decision line of the model's own trace by the
algorithm's decision procedure at the state that trace has reached, so one
early slip is not charged to every later step. What the paper leaves open is
not judged: the order of facts (line 14) and of folds (Definition 3). RoLe and
the contrary facts (lines 8, 44) are judged by optimality, not against the one
answer set the reference happened to get. A decision Algorithm 1 takes on the
trace's own path (lines 8, 16, 18, 36, 38, 44) and the trace never writes is an
error: `accuracy` is over the decisions required, written or not, and
`written_accuracy` over those written. The candidate list (line 17) and the
choice of assumption (lines 36/41) are judged when written.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.aba_algorithm import (
    _assumptions_relative_to, _current_framework, _is_ground_fact,
    apply_folding, fact_subsumption,
)
from src.aba_generalization import (
    _pred_of, is_intensional_strict, wellformed_violations,
)
from src.aba_prompts import (
    _RULES_HDR_RE, _clean_llm_output, _parse_rule_line, parse_llm_output,
    solution_to_output_format,
)
from src.aba_replay import _DECL_RE, trace_lines
from src.aba_sft import sft_example
from src.aba_trace import score_trace
from src.aba_tracelog import RunRecord
from src.aba_types import ABAFramework, LearningProblem, LearningTrace, Rule
from src.aba_validator import (
    _build_asp, _solve, check_brave_entailment, check_has_stable_extension,
    conditioned_status, run_rote_learning,
)


# ─────────────────────────────────────────────────────────────────────────────
# The algorithm's answer
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class Reference:
    problem: LearningProblem
    solution: ABAFramework
    trace: LearningTrace
    record: RunRecord
    trace_target: str
    endpoint_target: str
    status: Dict[str, str]        # off-example atom -> ALWAYS / NEVER / FREE


def _off_example_atoms(p: LearningProblem) -> List[str]:
    posed = set(p.positive) | set(p.negative)
    preds = dict.fromkeys(_pred_of(e) for e in p.positive + p.negative)
    return [f"{q}({c})" for q in preds for c in p.get_domain()
            if f"{q}({c})" not in posed]


def reference(problem: LearningProblem) -> Reference:
    ex = sft_example(problem)
    status = conditioned_status(ex["solution"], problem.positive, problem.negative,
                                _off_example_atoms(problem), problem.get_domain())
    return Reference(problem, ex["solution"], ex["trace"], ex["record"],
                     ex["trace_target"], ex["endpoint_target"], status)


# ─────────────────────────────────────────────────────────────────────────────
# Answer-level checks
# ─────────────────────────────────────────────────────────────────────────────

def self_defeating(fw: ABAFramework, dom: List[str]) -> List[str]:
    """Assumption-guarded learnt rules that fire in no stable extension.

    Meaningful only on a framework that has a stable extension.
    """
    asm = {_pred_of(a) for a in fw.assumptions}
    base = _build_asp(fw, [], [], dom)
    return [r.to_prolog() for r in fw.new_rules
            if any(_pred_of(b) in asm for b in r.body)
            and not _solve(f"{base}\n__fires :- {', '.join(r.body)}.\n"
                           f":- not __fires.")[0]]


_VAR = re.compile(r"\b[A-Z_]\w*\b")


def _rule_key(head: str, body: List[str]) -> str:
    """Body sorted, variables renamed by first appearance, spaces dropped."""
    body = sorted(body, key=lambda b: _VAR.sub("_", b))
    names: Dict[str, str] = {}
    text = f"{head}:-{','.join(body)}".replace(" ", "")
    return _VAR.sub(lambda m: names.setdefault(m.group(), f"V{len(names)}"), text)


def _key(r: Rule) -> str:
    return _rule_key(r.head, r.body)


def _relabel(fw: ABAFramework, tags) -> collections.Counter:
    """Learnt rules with fresh assumption k and its contrary written tags(k)."""
    name = lambda atom: _pred_of(atom) or atom.strip()   # unreadable names keyed whole
    ren = {}
    for k, a in enumerate(fw.new_assumptions):
        ren[name(a)], con = tags(k)
        if a in fw.contraries:
            ren[name(fw.contraries[a])] = con
    def sub(atom: str) -> str:
        p = _pred_of(atom)
        if p is None:
            return ren.get(atom.strip(), atom)
        return ren[p] + atom.strip()[len(p):] if p in ren else atom
    return collections.Counter(_rule_key(sub(r.head), [sub(b) for b in r.body])
                               for r in fw.new_rules)


def _renamed(fw: ABAFramework, order) -> collections.Counter:
    """Learnt rules with fresh assumption i written @a<order[i]>, its contrary @c."""
    order = list(order)
    return _relabel(fw, lambda k: (f"@a{order[k]}", f"@c{order[k]}"))


def _alpha_order(a: ABAFramework, b: ABAFramework) -> Optional[Tuple[int, ...]]:
    """The renaming of a's fresh assumptions onto b's that makes them one answer.

    Each assumption is matched only to those with the same role in the rules,
    so the search stays small however many a model mints.
    """
    n = len(b.new_assumptions)
    if len(a.new_assumptions) != n or len(a.new_rules) != len(b.new_rules):
        return None
    target = _renamed(b, range(n))
    sig = lambda fw, i: frozenset(_relabel(fw, lambda k: ("@a", "@c") if k == i
                                           else ("@x", "@y")).items())
    sb = [sig(b, j) for j in range(n)]
    options = [[j for j in range(n) if sb[j] == sig(a, i)] for i in range(n)]
    budget = [5040]

    def search(perm: List[int]) -> Optional[Tuple[int, ...]]:
        if len(perm) == n:
            budget[0] -= 1
            return tuple(perm) if _renamed(a, perm) == target else None
        for j in options[len(perm)]:
            if j not in perm and budget[0] > 0:
                found = search(perm + [j])
                if found:
                    return found
        return None
    return search([])


def same_answer(a: ABAFramework, b: ABAFramework) -> bool:
    """Same learnt rules, up to the names of fresh assumptions and body order."""
    return _alpha_order(a, b) is not None


def _defeasible(fw: ABAFramework) -> bool:
    asm = {_pred_of(a) for a in fw.assumptions}
    return any(_pred_of(b) in asm for r in fw.new_rules for b in r.body)


def _r2_bodies(cand: ABAFramework, ref: ABAFramework) -> Dict[str, int]:
    """Per head with one learnt rule on each side: its non-assumption body.

    Fresh contraries are renamed only by the order `same_answer` finds; any
    other pairing could match an exception to the wrong guarded rule.
    """
    def bodies(fw, ren):
        asm = {_pred_of(a) for a in fw.assumptions}
        by = collections.defaultdict(list)
        for r in fw.new_rules:
            h = _pred_of(r.head)
            by[ren.get(h, h)].append({_pred_of(b) for b in r.body} - asm - {None})
        return {h: bs[0] for h, bs in by.items() if len(bs) == 1}
    order = _alpha_order(cand, ref) or ()
    ren = {_pred_of(cand.contraries[a]): _pred_of(ref.contraries[ref.new_assumptions[i]])
           for a, i in zip(cand.new_assumptions, order) if a in cand.contraries}
    mine, algo = bodies(cand, ren), bodies(ref, {})
    out = collections.Counter(n=0)
    for h, want in algo.items():
        if h in mine:
            got = mine[h]
            out["n"] += 1
            out["exact" if got == want else "over" if got > want
                else "under" if got < want else "other"] += 1
    return dict(out)


def _optimal(facts: List[Rule], fw: ABAFramework, p: LearningProblem,
             learnable: List[str]) -> bool:
    """`facts` are an optimal answer of RoLe's ASP program over `learnable`."""
    oracle, ok, _ = run_rote_learning(LearningProblem(
        background=fw, positive=p.positive, negative=p.negative,
        learnable=learnable, domain=p.get_domain(), problem_id=p.problem_id))
    keys = {_key(f) for f in facts}
    if not ok or len(keys) != len(facts) or len(keys) != len(oracle):
        return False
    if not all(_is_ground_fact(f) and _pred_of(f.head) in learnable for f in facts):
        return False
    with_facts = fw.copy()
    with_facts.rules = fw.rules + facts
    return check_brave_entailment(with_facts, p.positive, p.negative,
                                  p.get_domain())[0]


# ─────────────────────────────────────────────────────────────────────────────
# On-policy audit of a written trace (grammar: src/aba_sft.py)
# ─────────────────────────────────────────────────────────────────────────────

KINDS = ("role", "subsume", "fold_candidates", "check", "reuse_scan",
         "reuse_check", "introduce", "contrary_facts")
YES_NO = ("subsume", "check", "reuse_check")
# Taken on every path that reaches them (lines 8, 16, 18, 36, 38, 44), so a trace
# that skips one is charged; the candidate list and the assumption chosen are not.
REQUIRED = ("role", "subsume", "check", "reuse_scan", "reuse_check", "contrary_facts")

_BRACKETS = re.compile(r"\[([^\[\]]+)\]")
# Keywords as the grammar writes them: `r1` is also a predicate name (t5, t9).
_LINES = [
    ("role", re.compile(r"^RoLe\s*[.:]?$", re.I)),
    ("gen", re.compile(r"^Gen\s*[.:]?$", re.I)),
    ("r1", re.compile(r"^R1\s+(.+)$")),
    ("fact", re.compile(r"^fact\s+([a-z]\w*\(.*)$")),
    ("r4", re.compile(r"^R4\?\s+(?i:(yes|no))\b")),
    ("intensional", re.compile(r"^already intensional")),
    ("candidates", re.compile(r"^R2 candidates:\s*(.*)$")),
    ("check", re.compile(r"^R2\?\s+\[([^\[\]]+)\]\s+(?i:(yes|no))\b")),
    ("r2", re.compile(r"^R2\s+(.+)$")),
    ("r3_on", re.compile(r"^R3 on\s+\[([^\[\]]+)\]")),
    ("scan", re.compile(r"^R3 reuse:\s*(.*)$")),
    ("reuse", re.compile(r"^R3 reuse\?\s+\[([^\[\]]+)\]\s+(?i:(yes|no))\b")),
    ("failed", re.compile(r"^R3 failed\b")),
    ("mint_none", re.compile(r"^R3 mint\s+\[([^\[\]]+)\]:\s*no contrary facts")),
    ("r3", re.compile(r"^R3\s+(.+)$")),
    ("decl", _DECL_RE),
    ("gave_up", re.compile(r"^no option works")),
    ("done", re.compile(r"^Done\s*[.:]?$", re.I)),
]
_NEEDS_FACT = {"r4", "intensional", "candidates", "check", "r3_on", "scan",
               "reuse", "failed", "mint_none", "r2", "r3"}
_NEEDS_FOLD = {"scan", "reuse", "failed", "mint_none"}
_AFTER_R4 = _NEEDS_FACT - {"r4"} | {"gave_up"}
_ROLE_LINES = ("role", "r1", "decl")         # any other line belongs to Gen
_MARKUP = re.compile(r"^(?:(?:step\s*)?\d+\s*[.):]\s+|[-*+]\s+)", re.I)
_BARE_FACT = re.compile(r"^([a-z]\w*)\(\s*([a-z0-9]\w*)\s*\)$")


def _norm(ln: str) -> str:
    """A trace line without list markers, bold or doubled spaces."""
    ln = _MARKUP.sub("", ln.replace("**", "").strip(), count=1)
    return re.sub(r"\s+", " ", ln).strip()


def _as_fact(rule: Optional[Rule]) -> Optional[Rule]:
    """`p(c).` read as the fact `p(X) <- X = c` RoLe learns (line 10)."""
    m = rule is not None and not rule.body and _BARE_FACT.match(rule.head.strip())
    return Rule(f"{m.group(1)}(X)", [f"X = {m.group(2)}"]) if m else rule


def _extends(rule: Optional[Rule], fold: Rule) -> bool:
    """`rule` is `fold` plus one body atom, as lines 37 and 42 build it."""
    return (rule is not None and rule.head == fold.head
            and len(rule.body) == len(fold.body) + 1
            and all(b in rule.body for b in fold.body))


@dataclass
class _Attempt:
    """A fold taken at line 17, and what the trace wrote on it."""
    fold: Rule
    relative: List[str]                     # Definition 4, at this state
    checked: bool = False                   # line 18 written, or charged
    said: Optional[bool] = None             # line 18 as written
    on_l19: bool = False
    scanned: bool = False                   # line 36 written, or charged
    scan: Optional[List[str]] = None        # line 36 as written
    reuse: Dict[str, Optional[bool]] = field(default_factory=dict)  # line 38
    applied: bool = False                   # kept (line 18) or guarded (line 20)
    failed: bool = False                    # line 39, or line 44 found nothing


class _Audit:
    """The state a written trace has reached, and a verdict on each decision.

    State changes follow what the model wrote, right or wrong; each decision is
    judged against the reference functions `gen_phase` itself calls. A required
    decision the trace skips is charged once, where the trace moves past it.
    """

    def __init__(self, p: LearningProblem):
        self.p, self.bg, self.dom = p, p.background, p.get_domain()
        self.learnt: List[Rule] = []
        self.asms: Dict[str, str] = {}
        self.role: Optional[List[Rule]] = None
        self.role_seen = False              # RoLe written, or charged (line 8)
        self.adopt = False                  # RoLe skipped: 'fact' lines name its facts
        self.adopted = 0
        self.gen = False
        self.visited: set = set()           # learnt rules a 'fact' line named
        self.contra: Optional[Tuple[str, List[Rule], ABAFramework]] = None
        self.minted: Optional[str] = None   # fresh assumption awaiting declaration
        self.minted_test: List[Rule] = []   # the learnt rules line 43 builds F from
        self.acc = {k: [0, 0] for k in KINDS}
        self.omit = collections.Counter()
        self.conf = {k: collections.Counter() for k in YES_NO}
        self.illegal: List[str] = []
        self.omissions: List[str] = []
        self.log: List[list] = []           # [line, kind, ok, truth, said, subject]
        self.first_error: Optional[int] = None
        self.gave_up = 0
        self.fresh_fact()

    def fresh_fact(self) -> None:
        self.cur: Optional[int] = None      # the fact under line 14
        self.fact: Optional[Rule] = None    # that fact as named, before any R2/R3
        self.r4: Optional[bool] = None      # line 16 as written; False once charged
        self.att: Optional[_Attempt] = None
        self.tried: List[str] = []          # folds taken for this fact
        self.kept: Optional[Rule] = None    # fold applied as it stands (line 18)
        self.settled = False                # guarded, intensional, or given up

    # verdicts
    def judge(self, n: int, kind: str, ok: bool, truth: Optional[bool] = None,
              said: Optional[bool] = None, subject: str = "") -> None:
        self.acc[kind][0] += ok
        self.acc[kind][1] += 1
        if truth is not None:
            self.conf[kind][f"{'yes' if truth else 'no'}/{'yes' if said else 'no'}"] += 1
        self.log.append([n, kind, bool(ok), truth, said, subject])
        if not ok and self.first_error is None:
            self.first_error = n

    def omitted(self, n: int, kind: str, why: str,
                truth: Optional[bool] = None, subject: str = "") -> None:
        assert kind in REQUIRED, kind
        self.acc[kind][1] += 1
        self.omit[kind] += 1
        if truth is not None:
            self.conf[kind][f"{'yes' if truth else 'no'}/omitted"] += 1
        self.omissions.append(f"line {n}: {kind}, {why}")
        self.log.append([n, kind, False, truth, "omitted", subject])
        if self.first_error is None:
            self.first_error = n

    def bad(self, n: int, why: str) -> None:
        self.illegal.append(f"line {n}: {why}")
        if self.first_error is None:
            self.first_error = n

    # state, as gen_phase and asm_intro_options build it
    def fw(self, learnt: List[Rule], asms: Optional[Dict[str, str]] = None):
        return _current_framework(self.bg, learnt, self.asms if asms is None else asms)

    def sat(self, fw: ABAFramework) -> bool:
        return check_brave_entailment(fw, self.p.positive, self.p.negative, self.dom)[0]

    def with_cur(self, rule: Rule) -> List[Rule]:
        return self.learnt[:self.cur] + [rule] + self.learnt[self.cur + 1:]

    def guarded(self, fold: Rule, rule: Rule) -> List[Rule]:
        # asm_intro_options drops every copy of the fold, then appends
        return [r for r in self.with_cur(fold)
                if r.to_prolog() != fold.to_prolog()] + [rule]

    def folds(self) -> List[Rule]:
        return apply_folding(self.fact or self.learnt[self.cur], self.bg)

    def is_fold(self, rule: Optional[Rule]) -> bool:
        return rule is not None and _key(rule) in {_key(r) for r in self.folds()}

    def untried(self) -> bool:
        return any(_key(r) not in self.tried for r in self.folds())

    def subsumable(self, i: int) -> bool:
        others = self.learnt[:i] + self.learnt[i + 1:]
        return fact_subsumption(self.learnt[i], self.bg, others, self.asms, self.p)

    # required decisions
    def need_r4(self, n: int) -> None:
        if self.r4 is None and _is_ground_fact(self.learnt[self.cur]):
            self.omitted(n, "subsume", "acted on a fact without R4",
                         self.subsumable(self.cur), self.learnt[self.cur].to_prolog())
        self.r4 = bool(self.r4)

    def take(self, n: int, fold: Rule) -> _Attempt:
        """Line 17 takes `fold`; moving to another fold closes the open attempt."""
        if self.att is not None and _key(self.att.fold) == _key(fold):
            return self.att
        self.close(n)
        self.att = _Attempt(fold, _assumptions_relative_to(fold.body, self.fw(self.learnt)))
        self.tried.append(_key(fold))
        return self.att

    def need_check(self, n: int, att: _Attempt) -> None:
        if not att.checked:
            self.omitted(n, "check", "fold acted on without R2?",
                         self.sat(self.fw(self.with_cur(att.fold))), att.fold.to_prolog())
            att.checked = True

    def line19(self, n: int, att: _Attempt) -> None:
        self.need_check(n, att)
        if not att.on_l19:
            att.on_l19 = True
            if att.said:
                self.bad(n, "line 19 after R2? yes")

    def need_scan(self, n: int, att: _Attempt) -> None:
        self.line19(n, att)
        if not att.scanned:
            self.omitted(n, "reuse_scan", "assumption reused or minted without R3 reuse:")
            att.scanned = True

    def need_reuse(self, n: int, att: _Attempt, asm: str) -> None:
        if asm not in att.reuse:
            rule = Rule(att.fold.head, att.fold.body + [asm])
            self.omitted(n, "reuse_check", f"{asm} reused without R3 reuse?",
                         self.sat(self.fw(self.guarded(att.fold, rule))), asm)
            att.reuse[asm] = None

    def need_any_reuse(self, n: int, att: _Attempt, why: str) -> None:
        """A written scan listing a relative assumption owes one line-38 check
        before the reuse branch is left; one listing none sends line 36 to 41."""
        asm = next((a for a in att.relative if a.replace(" ", "") in (att.scan or [])), None)
        if asm is not None and not att.reuse:
            truth = self.sat(self.fw(self.guarded(
                att.fold, Rule(att.fold.head, att.fold.body + [asm]))))
            self.omitted(n, "reuse_check", why, truth, asm)
            att.reuse[asm] = None

    def close(self, n: int) -> Optional[_Attempt]:
        """The trace leaves the attempt: charge what line 18 or 19 still owed.

        A line-19 branch left without an R3 counts as failed, whatever was
        written, so leaving the fact then owes the line-39 backtrack.
        """
        att, self.att = self.att, None
        if att is None or att.applied or att.failed:
            return att
        if (att.said is False and not att.on_l19 and self.kept is not None
                and _key(self.kept) == _key(att.fold)):
            self.bad(n, "fold kept after R2? no")
        elif att.on_l19 or att.said is False:
            if not att.scanned:
                self.omitted(n, "reuse_scan", "line 19 left before R3 reuse:")
            elif att.scan == []:
                self.omitted(n, "contrary_facts", "R3 reuse: none, then nothing minted")
            else:
                self.need_any_reuse(n, att, "relative assumption never checked")
            if any(att.reuse.values()):
                self.bad(n, "reuse passing line 38 never applied")
            else:
                att.failed = True
        elif att.said:
            self.bad(n, "fold passing line 18 never applied")
        return att

    # closing a phase
    def end_role(self, n: int) -> None:
        if self.role is not None:
            self.judge(n, "role", _optimal(self.role, self.bg, self.p, self.p.learnable))
            self.learnt, self.role = list(self.role), None

    def end_contrary(self, n: int) -> None:
        if self.contra is not None:
            con, facts, tmp = self.contra
            self.judge(n, "contrary_facts", _optimal(facts, tmp, self.p, [con]))
            self.contra = None

    def end_fact(self, n: int) -> None:
        if self.cur is not None:
            ground = _is_ground_fact(self.learnt[self.cur])
            if self.r4 is None:                     # named, then left alone
                removable = self.subsumable(self.cur) if ground else None
                if ground:
                    self.omitted(n, "subsume", "fact named, R4 never written", removable,
                                 self.learnt[self.cur].to_prolog())
                if ground and not removable:
                    self.omitted(n, "check", "kept fact never folded")
            else:
                last = self.close(n)
                if self.kept is not None:
                    test = self.with_cur(self.kept)
                    if not self.sat(self.fw(test)):
                        self.bad(n, "fold kept without passing line 18")
                    self.learnt = test
                elif ground and not self.settled:
                    if not self.tried:
                        self.omitted(n, "check", "kept fact never folded")
                    elif last is not None and last.failed and self.untried():
                        self.omitted(n, "check", "line 39 failed, next fold never taken")
        if self.minted:
            self.bad(n, f"assumption {self.minted} never declared")
        self.minted = None
        self.fresh_fact()

    def finish(self, n: int) -> None:
        self.end_contrary(n)
        self.end_role(n)
        self.end_fact(n)
        if self.gave_up:                            # Gen halted with failure: nothing after is owed
            return
        for i, r in enumerate(self.learnt):         # line 14 processes every fact
            if _is_ground_fact(r) and _key(r) not in self.visited:
                removable = self.subsumable(i)
                self.omitted(n, "subsume", f"{r.to_prolog()} never processed", removable,
                             r.to_prolog())
                if not removable:
                    self.omitted(n, "check", f"{r.to_prolog()} never folded")
        if self.adopt:                              # facts line 8 learns and no line named
            facts, ok, _ = run_rote_learning(self.p)
            for _ in range(len(facts) - self.adopted if ok else 0):
                self.omitted(n, "subsume", "a RoLe fact never processed (RoLe skipped)")

    # one line
    def declares(self, m: re.Match) -> bool:
        """Declares the assumption just minted; any other declaration is prose."""
        return (self.minted is not None
                and m.group(1).replace(" ", "") == self.minted.replace(" ", ""))

    def line(self, n: int, kind: str, m: re.Match) -> None:
        if kind not in ("r1", "decl"):
            self.end_contrary(n)
        if kind == "r1" and self.role is None and self.contra is None and not self.gen:
            self.role, self.role_seen = [], True    # RoLe without its header
        if kind not in _ROLE_LINES:
            if not self.role_seen:
                self.omitted(n, "role", "Gen without RoLe")
                self.role_seen = self.adopt = True
            self.gen = True
        if kind == "fact" and self.repeats_fact(m):
            return                                  # the header written twice
        if kind in ("role", "gen", "fact", "done"):
            self.end_fact(n)                        # on the state the fact was processed in
            self.end_role(n)
        if kind in _NEEDS_FACT and self.cur is None:
            self.bad(n, f"'{kind}' with no current fact")
            return
        if kind in _NEEDS_FOLD and self.att is None:
            self.bad(n, f"'{kind}' with no fold under line 19")
            return
        if kind in _AFTER_R4 and self.cur is not None:
            self.need_r4(n)
        getattr(self, f"on_{kind}")(n, m)

    def on_role(self, n, m):
        self.role, self.role_seen = [], True

    def on_gen(self, n, m):
        pass

    def on_r1(self, n, m):
        rule = _as_fact(_parse_rule_line(m.group(1)))
        if rule is None:
            self.bad(n, "unreadable R1")
        elif self.role is not None:
            self.role.append(rule)
        elif self.contra is not None:
            self.contra[1].append(rule)
            self.learnt.append(rule)
        else:
            self.bad(n, "R1 outside RoLe and contrary rote learning")

    def repeats_fact(self, m: re.Match) -> bool:
        rule = _as_fact(_parse_rule_line(m.group(1)))
        return (rule is not None and self.cur is not None and self.r4 is None
                and self.att is None and not self.tried
                and _key(rule) == _key(self.learnt[self.cur]))

    def on_fact(self, n, m):
        rule = _as_fact(_parse_rule_line(m.group(1)))
        keys = [_key(r) for r in self.learnt]
        if (self.adopt and rule is not None and _key(rule) not in keys
                and _is_ground_fact(rule) and _pred_of(rule.head) in self.p.learnable):
            self.learnt.append(rule)                # the fact RoLe left unwritten
            keys.append(_key(rule))
            self.adopted += 1
        if rule is None or _key(rule) not in keys:
            self.bad(n, "'fact' names no learnt rule")
        else:
            self.cur = keys.index(_key(rule))
            self.fact = self.learnt[self.cur]
            self.visited.add(_key(rule))

    def on_done(self, n, m):
        left = sum(_is_ground_fact(r) for r in self.learnt)
        if left and not self.gave_up:
            self.bad(n, f"{left} ground facts never generalised")

    def on_gave_up(self, n, m):
        """Algorithm 1 halts on a fact whose every fold failed (p. 3450); elsewhere
        the line is a false claim and what follows stays owed."""
        if (self.cur is None or self.settled or self.kept is not None
                or not _is_ground_fact(self.learnt[self.cur])):
            self.bad(n, "'no option works' with no failing fact")
            return
        self.close(n)
        if self.untried():
            self.omitted(n, "check", "gave up with a fold untried")
            self.bad(n, "'no option works' with a fold untried")
        else:
            self.gave_up += 1
        self.settled = True

    def on_r4(self, n, m):
        if self.r4 is not None:
            self.bad(n, "line 16 twice for one fact")
            return
        said = m.group(1).lower() == "yes"
        truth = self.subsumable(self.cur)
        self.judge(n, "subsume", said == truth, truth, said, self.learnt[self.cur].to_prolog())
        self.r4 = said
        if said:
            self.learnt = self.learnt[:self.cur] + self.learnt[self.cur + 1:]
            self.cur = None

    def on_intensional(self, n, m):
        if _is_ground_fact(self.learnt[self.cur]):
            self.bad(n, "a ground fact called intensional")
        else:
            self.settled = True

    def on_candidates(self, n, m):
        written = {_key(r) for r in map(_parse_rule_line,
                                        _BRACKETS.findall(m.group(1))) if r}
        self.judge(n, "fold_candidates", written == {_key(r) for r in self.folds()})

    def on_check(self, n, m):
        fold, said = _parse_rule_line(m.group(1)), m.group(2).lower() == "yes"
        if not self.is_fold(fold):
            self.bad(n, "line 18 on a rule that is not a fold")
            return
        att = self.take(n, fold)
        if att.checked:
            self.bad(n, "line 18 twice on one fold")
            return
        truth = self.sat(self.fw(self.with_cur(fold)))
        self.judge(n, "check", said == truth, truth, said, fold.to_prolog())
        att.checked, att.said = True, said

    def on_r2(self, n, m):
        fold = _parse_rule_line(m.group(1))
        if not self.is_fold(fold):
            self.bad(n, "R2 applied to a rule that is not a fold")
            return
        att = self.take(n, fold)
        self.need_check(n, att)
        self.kept = fold
        # under line 19 this is the fold written before its R3 (src/aba_sft.py)
        att.applied = att.applied or not (att.on_l19 or att.said is False)

    def on_r3_on(self, n, m):
        fold = _parse_rule_line(m.group(1))
        if not self.is_fold(fold):
            self.bad(n, "line 19 on a rule that is not a fold")
            return
        self.line19(n, self.take(n, fold))

    def on_scan(self, n, m):
        att = self.att
        self.line19(n, att)
        written = [a.replace(" ", "") for a in _BRACKETS.findall(m.group(1))]
        self.judge(n, "reuse_scan",
                   set(written) == {a.replace(" ", "") for a in att.relative})
        att.scanned, att.scan = True, written

    def on_reuse(self, n, m):
        att = self.att
        asm, said = m.group(1).strip(), m.group(2).lower() == "yes"
        self.need_scan(n, att)
        if asm in att.reuse:
            self.bad(n, "line 38 twice on one assumption")
            return
        if asm not in att.relative:
            if asm.replace(" ", "") in (att.scan or []):
                att.reuse[asm] = said               # its own scan listed it: the scan was the slip
            else:
                self.bad(n, "reuse of an assumption not relative to the body")
            return
        rule = Rule(att.fold.head, att.fold.body + [asm])
        truth = self.sat(self.fw(self.guarded(att.fold, rule)))
        self.judge(n, "reuse_check", said == truth, truth, said, asm)
        att.reuse[asm] = said

    def on_failed(self, n, m):
        att = self.att
        self.need_scan(n, att)
        if any(att.reuse.values()):
            self.bad(n, "line 39 after R3 reuse? yes")
        if att.scan == []:
            self.omitted(n, "contrary_facts", "line 39 where line 41 mints")
        self.need_any_reuse(n, att, "line 39 without a line-38 check")
        att.failed = True

    def on_mint_none(self, n, m):
        att = self.att
        self.need_scan(n, att)
        self.need_any_reuse(n, att, "line 41 after a scan listing assumptions")
        asm = m.group(1).strip()
        con = f"c_{asm}"
        rule = Rule(att.fold.head, att.fold.body + [asm])
        tmp = self.fw(self.guarded(att.fold, rule), {**self.asms, asm: con})
        _, ok, _ = run_rote_learning(LearningProblem(
            background=tmp, positive=self.p.positive, negative=self.p.negative,
            learnable=[_pred_of(con)], domain=self.dom))
        self.judge(n, "contrary_facts", not ok and not att.relative)
        att.failed = True

    def on_r3(self, n, m):
        rule = _parse_rule_line(m.group(1))
        att = self.att
        if att is None or not _extends(rule, att.fold):
            fold = next((f for f in self.folds() if _extends(rule, f)), None)
            if fold is None:
                self.bad(n, "R3 is not a fold plus one assumption")
                return
            att = self.take(n, fold)
        asm = next(b for b in rule.body if b not in att.fold.body)
        test = self.guarded(att.fold, rule)
        self.need_scan(n, att)
        if asm in self.bg.assumptions or asm in self.asms:        # line 36
            if asm in att.relative:                 # else the choice alone is the slip
                self.need_reuse(n, att, asm)
            self.judge(n, "introduce", asm in att.relative)
            if not self.sat(self.fw(test)):
                self.bad(n, "R3 applied without passing line 38")
            self.asms.setdefault(asm, self.bg.contraries.get(asm, f"c_{asm}"))
        else:                                                     # line 41
            self.need_any_reuse(n, att, "line 41 after a scan listing assumptions")
            self.judge(n, "introduce", not att.relative)
            self.asms[asm] = f"c_{asm}"             # until a declaration names it
            self.minted, self.minted_test = asm, test
            self.contra = (_pred_of(self.asms[asm]), [], self.fw(test))
        self.learnt, self.kept = self.with_cur(rule), None
        att.applied = self.settled = True

    def on_decl(self, n, m):
        con = m.group(2)
        self.asms[self.minted] = con
        if self.contra is not None:
            self.contra = (_pred_of(con), self.contra[1], self.fw(self.minted_test))
        self.minted = None


def audit_trace(text: str, problem: LearningProblem, gold_text: Optional[str] = None,
                truncated: bool = False) -> Optional[Dict]:
    """Judge the decisions the trace's own path requires; None when it writes no trace."""
    lines = [ln for ln in map(_norm, trace_lines(_clean_llm_output(text))) if ln]
    if truncated and lines and not text.endswith("\n") and not _RULES_HDR_RE.search(text):
        lines = lines[:-1]                      # cut by the budget, not written
    a = _Audit(problem)
    seen = 0
    for n, ln in enumerate(lines, 1):
        for kind, rx in _LINES:
            m = rx.match(ln)
            if m:
                break
        else:
            continue                            # prose: not a decision
        if kind == "decl" and not a.declares(m):
            continue                            # a declaration in the prose
        seen += kind not in ("gen", "done")
        try:
            a.line(n, kind, m)
        except Exception as e:                  # model text never crashes scoring
            a.bad(n, f"unscorable: {type(e).__name__}")
            a.fresh_fact()
    if not seen:
        return None
    try:
        a.finish(len(lines))
    except Exception as e:
        a.bad(len(lines), f"unscorable: {type(e).__name__}")
    try:
        parsed = parse_llm_output(text, problem.background)
        matches = parsed is not None and same_answer(parsed, a.fw(a.learnt))
    except Exception as e:
        a.bad(len(lines), f"unscorable answer: {type(e).__name__}")
        matches = False

    n = sum(t for _, t in a.acc.values())
    right = sum(c for c, _ in a.acc.values())
    omitted = sum(a.omit.values())
    out = {
        "n_decisions": n,
        "accuracy": right / n if n else None,
        "n_omitted": omitted,
        "written_accuracy": right / (n - omitted) if n > omitted else None,
        "by_kind": {k: v for k, v in a.acc.items() if v[1]},
        "omitted": dict(a.omit),
        "confusion": {k: dict(v) for k, v in a.conf.items() if v},
        # omitted yes/no decisions with no truth (a fold never taken): in accuracy, not in balanced
        "omitted_no_truth": dict(collections.Counter(
            k for _, k, _, truth, said, _ in a.log
            if said == "omitted" and truth is None and k in YES_NO)),
        "illegal": a.illegal,
        "omissions": a.omissions,
        "log": a.log,
        "first_error": a.first_error,
        "gave_up": a.gave_up,
        "answer_matches_trace": matches,
    }
    if gold_text is not None:
        gold = [ln for ln in map(_norm, trace_lines(gold_text)) if ln]
        k = next((i for i, (x, y) in enumerate(zip(lines, gold)) if x != y),
                 min(len(lines), len(gold)))
        out["gold_prefix"] = k / len(gold) if gold else 1.0
    return out


# ─────────────────────────────────────────────────────────────────────────────
# The score card
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ScoreCard:
    parse_ok: bool = False
    repairs: List[str] = field(default_factory=list)
    truncated: bool = False
    illformed: List[str] = field(default_factory=list)
    valid: bool = False
    stable: bool = False
    intensional: bool = False
    n_ground: int = 0
    self_defeating: List[str] = field(default_factory=list)
    clean: bool = False
    agreement: Optional[float] = None
    exact: bool = False
    defeasible: Optional[bool] = None
    ref_defeasible: bool = False
    r2_bodies: Dict[str, int] = field(default_factory=dict)
    choice: Optional[str] = None           # t8/t9: which listed answer, if any
    algorithm_choice: Optional[bool] = None
    forbidden_choice: Optional[bool] = None
    audit: Optional[Dict] = None
    trace_fidelity: Optional[Dict] = None  # the frozen scorer; read against `ceiling`
    error: str = "ok"

    def to_dict(self) -> Dict:
        return asdict(self)


_TRACE_FIELDS = ("has_trace", "precision", "recall", "f1", "align_exact",
                 "r1_recall", "r2_recall", "r3_recall", "r4_recall")


def score_output(raw: str, ref: Reference, meta: Optional[Dict] = None,
                 truncated: bool = False) -> ScoreCard:
    p = ref.problem
    bg, dom = p.background, p.get_domain()
    card = ScoreCard(truncated=truncated, ref_defeasible=_defeasible(ref.solution))
    cand = parse_llm_output(raw, bg, card.repairs)
    card.parse_ok = cand is not None
    card.audit = audit_trace(raw, p, ref.trace_target, truncated)   # even without its answer
    if cand is None:
        card.error = "parse_error"
        return card

    card.illformed = wellformed_violations(cand, bg, p.learnable)
    card.valid = check_brave_entailment(cand, p.positive, p.negative, dom)[0]
    card.stable = card.valid or check_has_stable_extension(cand, dom)
    card.intensional = is_intensional_strict(cand)
    card.n_ground = sum(r.contains_constant() for r in cand.new_rules)
    card.self_defeating = self_defeating(cand, dom) if card.stable else []
    card.clean = (card.valid and card.intensional and not card.illformed
                  and not card.self_defeating)

    if ref.status:
        status = conditioned_status(cand, p.positive, p.negative, list(ref.status), dom)
        card.agreement = sum(status[x] == s for x, s in ref.status.items()) / len(ref.status)
    card.exact = same_answer(cand, ref.solution)
    card.defeasible = _defeasible(cand)
    card.r2_bodies = _r2_bodies(cand, ref.solution)
    if meta and meta.get("answers"):
        card.choice = next((name for name, ans in meta["answers"].items()
                            if same_answer(cand, _current_framework(
                                bg, [_parse_rule_line(r) for r in ans["new_rules"]],
                                ans["contraries"]))), None)
        card.algorithm_choice = card.choice == meta["expected"]
        card.forbidden_choice = card.choice in meta.get("forbidden", [])

    s = score_trace(raw, ref.trace, bg, p.learnable).to_dict()
    card.trace_fidelity = {k: s[k] for k in _TRACE_FIELDS}

    card.error = ("illformed" if card.illformed
                  else "not_a_solution" if not card.valid
                  else "valid_but_degenerate" if not card.intensional
                  else "self_defeating" if card.self_defeating
                  else "illegal_transformation" if card.audit and card.audit["illegal"]
                  else "ok")
    return card


# ─────────────────────────────────────────────────────────────────────────────
# Reward. Weights fixed here, before any run.
# ─────────────────────────────────────────────────────────────────────────────

REWARD_WEIGHTS = {"valid": 1.0, "intensional": 0.5, "ground": 0.1,
                  "ground_cap": 5, "self_defeating": 0.5, "process": 0.0}


def reward(card: ScoreCard, w: Dict = REWARD_WEIGHTS) -> float:
    """Entailment dominates; a valid answer earns more only by being intensional."""
    if not card.parse_ok or card.illformed:
        return 0.0
    r = w["valid"] * card.valid + w["intensional"] * (card.valid and card.intensional)
    r -= w["ground"] * min(card.n_ground, w["ground_cap"])
    r -= w["self_defeating"] * len(card.self_defeating)
    if w["process"] and card.audit:
        r += w["process"] * (card.audit["accuracy"] or 0.0)
    return r


# ─────────────────────────────────────────────────────────────────────────────
# Corpus rows, and the control: every gold target at the maximum
# ─────────────────────────────────────────────────────────────────────────────

def load_eval(corpus: Path) -> List[Tuple[Dict, LearningProblem, Dict]]:
    """(eval row, problem, meta) for eval.jsonl and table1_eval.jsonl."""
    from src.aba_corpus import problem_from_dict
    out = []
    for prefix in ("", "table1_"):
        if not (corpus / f"{prefix}eval.jsonl").exists():
            continue
        rows = {}
        for line in open(corpus / f"{prefix}problems.jsonl", encoding="utf-8"):
            r = json.loads(line)
            rows[r["problem_id"]] = r
        for line in open(corpus / f"{prefix}eval.jsonl", encoding="utf-8"):
            ev = json.loads(line)
            r = rows[ev["problem_id"]]
            out.append((ev, problem_from_dict(r["problem"]), r.get("meta") or {}))
    return out


def degenerate_answer(ref: Reference) -> str:
    """RoLe's facts as the whole answer: a solution by Theorem 2, and worthless."""
    bg = ref.problem.background
    facts = [_parse_rule_line(f) for f in ref.record.role_facts]
    return solution_to_output_format(_current_framework(bg, facts, {}), bg)


def gold_failures(card: ScoreCard, arm: str, meta: Dict) -> List[str]:
    """Every field a gold target must max out; empty when it does."""
    want = {"parse_ok": True, "illformed": [], "valid": True, "intensional": True,
            "n_ground": 0, "self_defeating": [], "clean": True, "exact": True,
            "error": "ok"}
    bad = [k for k, v in want.items() if getattr(card, k) != v]
    if card.agreement not in (None, 1.0):
        bad.append(f"agreement {card.agreement}")
    if card.defeasible != card.ref_defeasible:
        bad.append("defeasible")
    if card.r2_bodies.get("exact", 0) != card.r2_bodies["n"]:
        bad.append(f"r2 {card.r2_bodies}")
    if meta.get("answers") and not card.algorithm_choice:
        bad.append(f"choice {card.choice}")
    a = card.audit
    if arm == "endpoint_target":
        if a is not None:
            bad.append("audit on an endpoint target")
    elif (a is None or a["accuracy"] != 1.0 or a["illegal"] or a["gave_up"]
          or not a["answer_matches_trace"] or a["gold_prefix"] != 1.0):
        bad.append(f"audit {a}")
    return bad


def control(corpus: Path, limit: Optional[int] = None) -> int:
    rows = load_eval(corpus)[:limit]
    failures: List[Tuple[str, str]] = []
    conf = {k: collections.Counter() for k in YES_NO}
    for i, (row, problem, meta) in enumerate(rows, 1):
        ref = reference(problem)
        if (ref.trace_target, ref.endpoint_target) != (row["trace_target"],
                                                       row["endpoint_target"]):
            failures.append((row["problem_id"], "reference changed since the build"))
            continue
        cards = {arm: score_output(row[arm], ref, meta)
                 for arm in ("trace_target", "endpoint_target")}
        for arm, card in cards.items():
            bad = gold_failures(card, arm, meta)
            if bad:
                failures.append((row["problem_id"], f"{arm}: {bad}"))
        tf = cards["trace_target"].trace_fidelity
        if any(v is not None and tf[k] != v for k, v in row["ceiling"].items()):
            failures.append((row["problem_id"], "stored ceiling no longer reproduced"))
        for k, v in cards["trace_target"].audit["confusion"].items():
            conf[k].update(v)
        deg = score_output(degenerate_answer(ref), ref, meta)
        if not deg.valid or reward(deg) >= reward(cards["endpoint_target"]):
            failures.append((row["problem_id"], "degenerate answer invalid or not "
                                                "rewarded less"))
        if i % 50 == 0:
            print(f"  {i}/{len(rows)}", flush=True)

    ok = len(rows) - len({pid for pid, _ in failures})
    print(f"\ncontrol: {ok}/{len(rows)} problems with every gold target at the maximum")
    for pid, why in failures[:20]:
        print(f"  FAIL {pid}: {why}")
    print("\nnull floors of the yes/no decisions (truths on the gold traces):")
    for k, c in conf.items():
        n = sum(c.values())
        if n:
            yes = (c["yes/yes"] + c["yes/no"]) / n
            print(f"  {k:12s} n={n:5d}  truth yes {yes:.3f}  constant responder: "
                  f"raw {max(yes, 1 - yes):.3f}, balanced 0.500")
    return 0 if not failures else 1


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--control", type=Path, required=True,
                    help="corpus directory, e.g. corpus/v1")
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args(argv)
    return control(args.control, args.limit)


if __name__ == "__main__":
    sys.exit(main())
