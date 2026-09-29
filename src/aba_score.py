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
answer set the reference happened to get.
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
    _clean_llm_output, _parse_rule_line, parse_llm_output,
    solution_to_output_format,
)
from src.aba_replay import _DECL_RE, _FACT_RE, trace_lines
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


def _renamed(fw: ABAFramework, order) -> collections.Counter:
    """Learnt rules with fresh assumption i written @a<order[i]>, its contrary @c."""
    ren = {}
    for a, i in zip(fw.new_assumptions, order):
        ren[_pred_of(a)] = f"@a{i}"
        if a in fw.contraries:
            ren[_pred_of(fw.contraries[a])] = f"@c{i}"
    def sub(atom: str) -> str:
        p = _pred_of(atom)
        return ren[p] + atom.strip()[len(p):] if p in ren else atom
    return collections.Counter(_rule_key(sub(r.head), [sub(b) for b in r.body])
                               for r in fw.new_rules)


def same_answer(a: ABAFramework, b: ABAFramework) -> bool:
    """Same learnt rules, up to the names of fresh assumptions and body order."""
    n = len(b.new_assumptions)
    if len(a.new_assumptions) != n or len(a.new_rules) != len(b.new_rules):
        return False
    target = _renamed(b, range(n))
    return any(_renamed(a, perm) == target
               for perm in itertools.permutations(range(n)))


def _defeasible(fw: ABAFramework) -> bool:
    asm = {_pred_of(a) for a in fw.assumptions}
    return any(_pred_of(b) in asm for r in fw.new_rules for b in r.body)


def _r2_bodies(cand: ABAFramework, ref: ABAFramework) -> Dict[str, int]:
    """Per head with one learnt rule on each side: its non-assumption body."""
    def bodies(fw):
        asm = {_pred_of(a) for a in fw.assumptions}
        by = collections.defaultdict(list)
        for r in fw.new_rules:
            by[_pred_of(r.head)].append({_pred_of(b) for b in r.body} - asm - {None})
        return {h: bs[0] for h, bs in by.items() if len(bs) == 1}
    mine, algo = bodies(cand), bodies(ref)
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

_BRACKETS = re.compile(r"\[([^\[\]]+)\]")
_LINES = [
    ("role", re.compile(r"^RoLe\.$")),
    ("gen", re.compile(r"^Gen\.$")),
    ("r1", re.compile(r"^R1\s+(.+)$")),
    ("fact", _FACT_RE),
    ("r4", re.compile(r"^R4\?\s+(yes|no)\b")),
    ("intensional", re.compile(r"^already intensional")),
    ("candidates", re.compile(r"^R2 candidates:\s*(.*)$")),
    ("check", re.compile(r"^R2\?\s+\[([^\[\]]+)\]\s+(yes|no)\b")),
    ("r2", re.compile(r"^R2\s+(.+)$")),
    ("r3_on", re.compile(r"^R3 on\s+\[([^\[\]]+)\]")),
    ("scan", re.compile(r"^R3 reuse:\s*(.*)$")),
    ("reuse", re.compile(r"^R3 reuse\?\s+\[([^\[\]]+)\]\s+(yes|no)\b")),
    ("failed", re.compile(r"^R3 failed\b")),
    ("mint_none", re.compile(r"^R3 mint\s+\[([^\[\]]+)\]:\s*no contrary facts")),
    ("r3", re.compile(r"^R3\s+(.+)$")),
    ("decl", _DECL_RE),
    ("gave_up", re.compile(r"^no option works")),
    ("done", re.compile(r"^Done\.?$")),
]
_NEEDS_FACT = {"r4", "intensional", "candidates", "check", "r3_on", "scan",
               "reuse", "mint_none", "r2", "r3"}
_NEEDS_FOLD = {"scan", "reuse", "mint_none"}


class _Audit:
    """The state a written trace has reached, and a verdict on each decision.

    State changes follow what the model wrote, right or wrong; each decision is
    judged against the reference functions `gen_phase` itself calls.
    """

    def __init__(self, p: LearningProblem):
        self.p, self.bg, self.dom = p, p.background, p.get_domain()
        self.learnt: List[Rule] = []
        self.asms: Dict[str, str] = {}
        self.cur: Optional[int] = None      # the fact being processed
        self.fold: Optional[Rule] = None    # the fold taken (line 17)
        self.kept = False                   # applied as it stands (line 18)
        self.scan: Optional[List[str]] = None
        self.minted: Optional[str] = None   # fresh assumption awaiting declaration
        self.minted_test: List[Rule] = []   # the learnt rules line 43 builds F from
        self.role: Optional[List[Rule]] = None
        self.contra: Optional[Tuple[str, List[Rule], ABAFramework]] = None
        self.acc = {k: [0, 0] for k in KINDS}
        self.conf = {k: collections.Counter() for k in YES_NO}
        self.illegal: List[str] = []
        self.first_error: Optional[int] = None
        self.gave_up = 0

    # verdicts
    def judge(self, n: int, kind: str, ok: bool, truth: Optional[bool] = None,
              said: Optional[bool] = None) -> None:
        self.acc[kind][0] += ok
        self.acc[kind][1] += 1
        if truth is not None:
            self.conf[kind][f"{'yes' if truth else 'no'}/{'yes' if said else 'no'}"] += 1
        if not ok and self.first_error is None:
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

    def guarded(self, rule: Rule) -> List[Rule]:
        # asm_intro_options drops every copy of the fold, then appends
        return [r for r in self.with_cur(self.fold)
                if r.to_prolog() != self.fold.to_prolog()] + [rule]

    def is_fold(self, rule: Optional[Rule]) -> bool:
        return rule is not None and _key(rule) in {
            _key(r) for r in apply_folding(self.learnt[self.cur], self.bg)}

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
        if self.cur is not None and self.kept:
            test = self.with_cur(self.fold)
            if not self.sat(self.fw(test)):
                self.bad(n, "fold kept without passing line 18")
            self.learnt = test
        if self.minted:
            self.bad(n, f"assumption {self.minted} never declared")
        self.cur = self.fold = self.scan = self.minted = None
        self.kept = False

    # one line
    def line(self, n: int, kind: str, m: re.Match) -> None:
        if kind != "r1":
            self.end_contrary(n)
        if kind in ("gen", "fact", "done"):
            self.end_role(n)
            self.end_fact(n)
        if kind in _NEEDS_FACT and self.cur is None:
            self.bad(n, f"'{kind}' with no current fact")
            return
        if kind in _NEEDS_FOLD and self.fold is None:
            self.bad(n, f"'{kind}' with no fold under line 19")
            return
        getattr(self, f"on_{kind}")(n, m)

    def on_role(self, n, m):
        self.role = []

    def on_gen(self, n, m):
        pass

    def on_r1(self, n, m):
        rule = _parse_rule_line(m.group(1))
        if rule is None:
            self.bad(n, "unreadable R1")
        elif self.role is not None:
            self.role.append(rule)
        elif self.contra is not None:
            self.contra[1].append(rule)
            self.learnt.append(rule)
        else:
            self.bad(n, "R1 outside RoLe and contrary rote learning")

    def on_fact(self, n, m):
        rule = _parse_rule_line(m.group(1))
        keys = [_key(r) for r in self.learnt]
        if rule is None or _key(rule) not in keys:
            self.bad(n, "'fact' names no learnt rule")
        else:
            self.cur = keys.index(_key(rule))

    def on_done(self, n, m):
        left = sum(_is_ground_fact(r) for r in self.learnt)
        if left:
            self.bad(n, f"{left} ground facts never generalised")

    def on_gave_up(self, n, m):
        self.gave_up += 1

    def on_r4(self, n, m):
        said = m.group(1) == "yes"
        others = self.learnt[:self.cur] + self.learnt[self.cur + 1:]
        truth = fact_subsumption(self.learnt[self.cur], self.bg, others,
                                 self.asms, self.p)
        self.judge(n, "subsume", said == truth, truth, said)
        if said:
            self.learnt, self.cur = others, None

    def on_intensional(self, n, m):
        if _is_ground_fact(self.learnt[self.cur]):
            self.bad(n, "a ground fact called intensional")

    def on_candidates(self, n, m):
        written = {_key(r) for r in map(_parse_rule_line,
                                        _BRACKETS.findall(m.group(1))) if r}
        truth = {_key(r) for r in apply_folding(self.learnt[self.cur], self.bg)}
        self.judge(n, "fold_candidates", written == truth)

    def on_check(self, n, m):
        fold, said = _parse_rule_line(m.group(1)), m.group(2) == "yes"
        if not self.is_fold(fold):
            self.bad(n, "line 18 on a rule that is not a fold")
            return
        truth = self.sat(self.fw(self.with_cur(fold)))
        self.judge(n, "check", said == truth, truth, said)

    def on_r3_on(self, n, m):
        fold = _parse_rule_line(m.group(1))
        if not self.is_fold(fold):
            self.bad(n, "line 19 on a rule that is not a fold")
            return
        self.fold = fold
        self.scan = _assumptions_relative_to(fold.body, self.fw(self.learnt))

    def on_scan(self, n, m):
        self.judge(n, "reuse_scan", set(_BRACKETS.findall(m.group(1))) == set(self.scan))

    def on_reuse(self, n, m):
        asm, said = m.group(1).strip(), m.group(2) == "yes"
        if asm not in self.scan:
            self.bad(n, "reuse of an assumption not relative to the body")
            return
        rule = Rule(self.fold.head, self.fold.body + [asm])
        truth = self.sat(self.fw(self.guarded(rule)))
        self.judge(n, "reuse_check", said == truth, truth, said)

    def on_failed(self, n, m):
        self.fold = self.scan = None

    def on_mint_none(self, n, m):
        asm = m.group(1).strip()
        con = f"c_{asm}"
        rule = Rule(self.fold.head, self.fold.body + [asm])
        tmp = self.fw(self.guarded(rule), {**self.asms, asm: con})
        _, ok, _ = run_rote_learning(LearningProblem(
            background=tmp, positive=self.p.positive, negative=self.p.negative,
            learnable=[_pred_of(con)], domain=self.dom))
        self.judge(n, "contrary_facts", not ok and not self.scan)
        self.fold = self.scan = None

    def on_r2(self, n, m):
        fold = _parse_rule_line(m.group(1))
        if not self.is_fold(fold):
            self.bad(n, "R2 applied to a rule that is not a fold")
            return
        self.fold, self.kept = fold, True

    def on_r3(self, n, m):
        rule = _parse_rule_line(m.group(1))
        extra = [b for b in rule.body if b not in self.fold.body] if rule and self.fold else []
        if (not rule or not self.fold or rule.head != self.fold.head
                or len(extra) != 1 or len(rule.body) != len(self.fold.body) + 1):
            self.bad(n, "R3 is not the fold plus one assumption")
            return
        asm = extra[0]
        scan = (self.scan if self.scan is not None
                else _assumptions_relative_to(self.fold.body, self.fw(self.learnt)))
        test = self.guarded(rule)
        if asm in self.bg.assumptions or asm in self.asms:        # line 36
            self.judge(n, "introduce", asm in scan and self.sat(self.fw(test)))
            self.asms.setdefault(asm, self.bg.contraries.get(asm, f"c_{asm}"))
        else:                                                     # line 41
            self.judge(n, "introduce", not scan)
            self.minted, self.minted_test = asm, test
        self.learnt, self.kept = self.with_cur(rule), False

    def on_decl(self, n, m):
        asm, con = m.group(1), m.group(2)
        if asm != self.minted:
            self.bad(n, "declaration without a fresh R3")
            return
        self.asms[asm] = con
        self.contra = (_pred_of(con), [], self.fw(self.minted_test))
        self.minted = None


def audit_trace(text: str, problem: LearningProblem,
                gold_text: Optional[str] = None) -> Optional[Dict]:
    """Judge every decision line; None when the text writes no trace at all."""
    lines = [ln for ln in trace_lines(_clean_llm_output(text)) if ln]
    a = _Audit(problem)
    seen = 0
    for n, ln in enumerate(lines, 1):
        for kind, rx in _LINES:
            m = rx.match(ln)
            if m:
                break
        else:
            continue                            # prose: not a decision
        seen += 1
        try:
            a.line(n, kind, m)
        except Exception as e:                  # model text never crashes scoring
            a.bad(n, f"unscorable: {type(e).__name__}")
    if not seen:
        return None
    try:
        a.end_contrary(len(lines))
        a.end_role(len(lines))
        a.end_fact(len(lines))
    except Exception as e:
        a.bad(len(lines), f"unscorable: {type(e).__name__}")

    parsed = parse_llm_output(text, problem.background)
    n = sum(t for _, t in a.acc.values())
    out = {
        "n_decisions": n,
        "accuracy": sum(c for c, _ in a.acc.values()) / n if n else 0.0,
        "by_kind": {k: v for k, v in a.acc.items() if v[1]},
        "confusion": {k: dict(v) for k, v in a.conf.items() if v},
        "illegal": a.illegal,
        "first_error": a.first_error,
        "gave_up": a.gave_up,
        "answer_matches_trace": parsed is not None and same_answer(parsed, a.fw(a.learnt)),
    }
    if gold_text is not None:
        gold = [ln for ln in trace_lines(gold_text) if ln]
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

    card.audit = audit_trace(raw, p, ref.trace_target)
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
        r += w["process"] * card.audit["accuracy"]
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
