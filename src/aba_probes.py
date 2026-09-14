"""
aba_probes.py
Step probes: can the model make each individual decision ASP-ABAlearnB makes?

WHY PROBES RATHER THAN TRACE MINING
-----------------------------------
A transformation is only checkable relative to the framework state it was
applied to: R2 is legal only against the current rule set, and R3 is justified
only if the framework had actually stopped being a solution at that moment. A
single free-form answer destroys that state, and recovering it from prose by
position does not work — sequence alignment over the R1..R4 alphabet scores 0.28
to 0.49 on RANDOM input, i.e. at or above everything it was meant to measure.

So the state is supplied rather than inferred. Each probe presents one decision
point taken from the real symbolic execution (via the `observer` hook in
`gen_phase`, so the states are exactly the ones the algorithm visits) and asks
for that one decision. Every oracle below is Clingo or pure syntax — no LLM
judge, no alignment, no gold-path bias.

    P1 role       which ground facts?          oracle: run_rote_learning     ~0
    P2 fold       generalise this fact         oracle: apply_folding (a SET)  ~0
    P3 check      still a solution?            oracle: brave entailment       50%
    P4 introduce  guard it and name a contrary oracle: resulting fw is Def-1  ~0
    P5 subsume    can this fact be dropped?    oracle: fact_subsumption       50%

P2 and P4 accept ANY legal answer, not the one the solver happened to pick, so
the nondeterminism of `applyFolding`/`applyAsmIntro` costs the model nothing.
P3 and P5 are binary: report BALANCED ACCURACY against the explicit 50% floor,
never raw accuracy. P3 also asks which examples fail, and that half has a ~0
chance floor, so it carries most of the probe's discriminating power.
"""
from __future__ import annotations

import random
import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any

from src.aba_types import Rule, ABAFramework, LearningProblem
from src.aba_algorithm import (
    gen_phase, apply_folding, fact_subsumption, _current_framework,
    _is_ground_fact, _assumptions_relative_to, _new_assumption_name,
)
from src.aba_validator import run_rote_learning, check_brave_entailment
from src.aba_prompts import SYSTEM_PROMPT_DEFS, _format_problem, _clean_llm_output
from src.aba_trace import _strip_echo, _RULES_HDR, _ASMS_HDR

KINDS = ("role", "fold", "check", "introduce", "subsume")
BINARY_KINDS = ("check", "subsume")

# Probe prompts version themselves, independently of the end-to-end mode prompts
# (frozen at v3). Probe results are comparable only within one version.
#   v1  the committed Sept-2026 run. Two defects: `_head` prepended the whole
#       SYSTEM_PROMPT, whose format block contradicted every probe's own format,
#       and whose "NEVER leave ground facts" contradicted the RoLe probe.
#   v2  definitions-only preamble; RoLe states that ground facts are expected;
#       R3 asks for the two choices `applyAsmIntro` makes and not for the
#       contrary, which ASP computes at line 44.
# Bump this when any probe prompt changes, and record it in the set MANIFEST.
PROBE_PROMPT_VERSION = "v2"


# ──────────────────────────────────────────────────────────────────────────────
# Probe / result records
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Probe:
    probe_id:   str
    problem_id: str
    kind:       str
    prompt:     str
    oracle:     Any                       # ground truth, kind-dependent
    state:      Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["oracle"] = _repr_oracle(self.oracle)
        return d


@dataclass
class ProbeResult:
    probe_id:   str
    problem_id: str
    kind:       str
    model_name: str
    raw_output: str = ""
    parsed:     str = ""
    oracle_repr: str = ""
    correct:    bool = False
    score:      float = 0.0     # partial credit where the answer is a set
    oracle_bool: Optional[bool] = None   # binary probes, for balanced accuracy
    error:      str = ""
    llm_latency_s: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _repr_oracle(oracle: Any) -> str:
    if isinstance(oracle, bool):
        return "YES" if oracle else "NO"
    if isinstance(oracle, (list, tuple, set)):
        return "; ".join(sorted(r.to_prolog() if isinstance(r, Rule) else str(r)
                                for r in oracle))
    if isinstance(oracle, dict):
        return str({k: _repr_oracle(v) for k, v in oracle.items()})
    return str(oracle)


# ──────────────────────────────────────────────────────────────────────────────
# Rendering the algorithm's state into a prompt
# ──────────────────────────────────────────────────────────────────────────────

def _render_state(learnt: List[Rule], new_asms: Dict[str, str]) -> str:
    lines = ["=== RULES LEARNT SO FAR ==="]
    lines += [f"  {r.to_prolog()}" for r in learnt] or ["  (none)"]
    if new_asms:
        lines.append("")
        lines.append("=== ASSUMPTIONS INTRODUCED SO FAR ===")
        for a, c in new_asms.items():
            lines.append(f"  {a} defeated_by {c}")
    return "\n".join(lines)


# The DEFINITIONS half of the shared prompt only. The task half states the
# end-to-end goal and a fixed output format, both of which contradict the
# probes — see the note beside the split in aba_prompts.py.
_PROBE_TASK = """
YOUR TASK: you will be shown one ABA Learning problem and asked to apply ONE
step of the ASP-ABAlearnB algorithm (De Angelis, Proietti & Toni, Algorithm 1)
to it. Answer only that step. Do not solve the whole learning problem, and do
not carry out any later step. Use exactly the output format given with the task
and write nothing else — no markdown, no commentary, no restatement of the
problem."""


def _head(problem: LearningProblem) -> str:
    return (SYSTEM_PROMPT_DEFS + _PROBE_TASK + "\n\n"
            + _format_problem(problem) + "\n")


_P1 = """TASK — run the RoLe procedure: repeated Rote Learning (R1).

R1 adds one ground fact, written  p(X) :- X = t.  RoLe repeats it until the
framework is a solution, adding a MINIMAL set of such facts.

The expected answer is therefore NON-intensional: ground facts are correct
here, and generalising is not. Do not fold, do not introduce assumptions.

A fact may be needed for a predicate that occurs in NEITHER example list — in
particular for the contrary of an assumption, which is how an exception to a
rule is recorded.

Output one fact per line, in the form
  <predicate>(<constant>).
and nothing else. Write NONE if no fact is needed."""

_P2 = """TASK — apply ONLY the Folding transformation (R2).

{state}

Make this ONE learnt rule intensional by folding it against the background:
  {rule}
Replace the equality in its body by the head of a background rule whose body
that equality satisfies. The result must contain no constant.

Output exactly ONE rule, in the form
  <head> :- <body>.
and nothing else."""

_P3 = """TASK — perform the SOLUTION CHECK that follows a folding step.

Suppose the learnt rules were exactly these:
{state}

Is this framework still a solution? That is: does it admit ONE stable extension
accepting every positive example and no negative example?

Output YES or NO on the first line, and nothing else on that line.
If NO, list on the following lines the examples that fail, one per line, as
  <predicate>(<constant>)"""

_P4 = """TASK — apply the Assumption Introduction transformation (R3).

{state}

Folding produced this rule:
  {folded}
but with it the framework is NO LONGER a solution. Make the rule defeasible by
adding an assumption to its body, so that a solution can be recovered.

R3 replaces a rule  H :- Eqs, B  by  H :- Eqs, B, alpha(X), where alpha(X) is
an assumption with contrary c_alpha(X). You choose exactly two things:
  1. which rule to guard, and
  2. which assumption to put in its body.
REUSE FIRST: if the background already declares an assumption relative to this
body, use that one. Its contrary is fixed by the background and must not be
redefined. Otherwise name a new assumption and its contrary.

Do NOT give rules for the contrary. Those facts are not part of this step: they
are computed afterwards and added by Rote Learning.

Output exactly these two lines and nothing else:
RULE: <head> :- <body>, <assumption>.
ASSUMPTION: <assumption> defeated_by <contrary>"""

_P5 = """TASK — apply the Fact Subsumption transformation (R4).

{state}

Can this rule be REMOVED while the framework remains a solution?
  {rule}

Output YES or NO, and nothing else."""


# ──────────────────────────────────────────────────────────────────────────────
# Probe generation
# ──────────────────────────────────────────────────────────────────────────────

def generate_probes(problem: LearningProblem, max_per_kind: int = 2,
                    seed: int = 42) -> List[Probe]:
    """Build probes from the states the symbolic algorithm actually visits."""
    pid = problem.problem_id
    probes: List[Probe] = []

    facts, ok, _ = run_rote_learning(problem)
    if not ok:
        return probes

    probes.append(Probe(
        probe_id=f"{pid}::role", problem_id=pid, kind="role",
        prompt=_head(problem) + _P1,
        oracle=[r for r in facts],
    ))

    seen: List[Tuple[str, Probe]] = []

    def observe(kind, learnt, new_asms, idx, rule, extra):
        if kind == "subsume":
            seen.append(("subsume", Probe(
                probe_id=f"{pid}::subsume::{len(seen)}", problem_id=pid,
                kind="subsume",
                prompt=_head(problem) + _P5.format(
                    state=_render_state(learnt, new_asms), rule=rule.to_prolog()),
                oracle=bool(extra["answer"]),
                state={"rule": rule.to_prolog()},
            )))
        elif kind == "fold" and _is_ground_fact(rule) and extra["candidates"]:
            seen.append(("fold", Probe(
                probe_id=f"{pid}::fold::{len(seen)}", problem_id=pid, kind="fold",
                prompt=_head(problem) + _P2.format(
                    state=_render_state(learnt, new_asms), rule=rule.to_prolog()),
                oracle=list(extra["candidates"]),
                state={"rule": rule.to_prolog()},
            )))
        elif kind == "check":
            folded = extra["folded"]
            test = learnt[:idx] + [folded] + learnt[idx + 1:]
            seen.append(("check", Probe(
                probe_id=f"{pid}::check::{len(seen)}", problem_id=pid, kind="check",
                prompt=_head(problem) + _P3.format(
                    state=_render_state(test, new_asms)),
                oracle=bool(extra["answer"]),
                state={"learnt": [r.to_prolog() for r in test],
                       "new_asms": dict(new_asms)},
            )))
        elif kind == "asm_intro":
            folded = extra["folded"]
            seen.append(("introduce", Probe(
                probe_id=f"{pid}::introduce::{len(seen)}", problem_id=pid,
                kind="introduce",
                prompt=_head(problem) + _P4.format(
                    state=_render_state(learnt, new_asms),
                    folded=folded.to_prolog()),
                oracle=None,           # semantic: any rule making it a solution
                state={"learnt": [r.to_prolog() for r in learnt],
                       "new_asms": dict(new_asms),
                       "folded": folded.to_prolog(), "idx": idx},
            )))

    try:
        gen_phase(facts, problem, observer=observe)
    except Exception:
        return probes

    rng = random.Random(f"{seed}:{pid}")
    for kind in ("fold", "check", "introduce", "subsume"):
        pool = [p for k, p in seen if k == kind]
        if kind in BINARY_KINDS:
            # Keep both classes so balanced accuracy is estimable per problem.
            yes = [p for p in pool if p.oracle is True]
            no  = [p for p in pool if p.oracle is False]
            take = (rng.sample(yes, min(len(yes), max(1, max_per_kind // 2)))
                    + rng.sample(no, min(len(no), max(1, max_per_kind // 2))))
        else:
            take = rng.sample(pool, min(len(pool), max_per_kind))
        probes.extend(take)
    return probes


# ──────────────────────────────────────────────────────────────────────────────
# Answer parsing + oracles
# ──────────────────────────────────────────────────────────────────────────────

_FACT_RE = re.compile(r'^\s*([a-z]\w*)\s*\(\s*([a-z]\w*)\s*\)\s*\.?\s*$')
_YESNO_RE = re.compile(r'\b(yes|no)\b', re.IGNORECASE)


def _facts_in(text: str) -> set:
    out = set()
    for ln in text.split("\n"):
        m = _FACT_RE.match(ln.strip().lstrip("-*+ \t"))
        if m:
            out.add(f"{m.group(1)}({m.group(2)})")
    return out


def _f1(pred: set, gold: set) -> float:
    if not pred and not gold:
        return 1.0
    if not pred or not gold:
        return 0.0
    tp = len(pred & gold)
    if tp == 0:
        return 0.0
    p, r = tp / len(pred), tp / len(gold)
    return 2 * p * r / (p + r)


def _rule_from(text: str) -> Optional[Rule]:
    from src.aba_prompts import _parse_rule_line
    for ln in text.split("\n"):
        ln = ln.strip().lstrip("-*+ \t")
        ln = re.sub(r'^(RULE|CONTRARY)\s*:\s*', '', ln, flags=re.IGNORECASE)
        if ":-" not in ln:
            continue
        r = _parse_rule_line(ln)
        if r is not None:
            return r
    return None


def score_probe(probe: Probe, raw_output: str,
                problem: LearningProblem) -> Tuple[bool, float, str]:
    """Return (correct, partial_score, parsed_repr)."""
    # Drop echoed problem text BEFORE anything reads the answer. Qwen2.5-7B
    # echoes the whole problem after its answer in 415/780 probes, and both the
    # background facts and its `<asm> defeated_by <contrary>` declarations are
    # otherwise indistinguishable from the model's own output: `role` scored one
    # answer as 12 facts against an oracle of 2, and relaxing the ASSUMPTION:
    # prefix below would read the background's contraries back as the proposal.
    # Region-based, not truncation: the answer often comes FIRST (aba_trace.py).
    text = "\n".join(
        _strip_echo(_clean_llm_output(raw_output or "").split("\n")))

    if probe.kind == "role":
        gold = {f"{r.head.split('(')[0]}({r.body[0].split('=')[1].strip()})"
                for r in probe.oracle if r.body}
        pred = _facts_in(text)
        f1 = _f1(pred, gold)
        return pred == gold, f1, "; ".join(sorted(pred))

    if probe.kind == "fold":
        got = _rule_from(text)
        if got is None:
            return False, 0.0, "<unparseable>"
        legal = {_norm_rule(c) for c in probe.oracle}
        ok = _norm_rule(got) in legal
        return ok, 1.0 if ok else 0.0, got.to_prolog()

    if probe.kind in BINARY_KINDS:
        m = _YESNO_RE.search(text)
        if m is None:
            return False, 0.0, "<no yes/no>"
        said = m.group(1).lower() == "yes"
        ok = (said == bool(probe.oracle))
        parsed = "YES" if said else "NO"
        if probe.kind == "check" and not probe.oracle:
            # The discriminating half: WHICH examples fail (chance ~0).
            gold = _failing_examples(probe, problem)
            f1 = _f1(_facts_in(text), gold)
            return ok, (1.0 if ok else 0.0) * 0.5 + 0.5 * f1, f"{parsed}|{f1:.2f}"
        return ok, 1.0 if ok else 0.0, parsed

    if probe.kind == "introduce":
        return _score_introduce(probe, text, problem)

    return False, 0.0, ""


def _norm_rule(r: Rule) -> str:
    """Whitespace- and body-order-insensitive key (`Rule.__eq__` is neither)."""
    body = sorted(re.sub(r'\s+', '', a) for a in r.body)
    head = re.sub(r'\s+', '', r.head)
    return head + ":-" + ",".join(body)


def _failing_examples(probe: Probe, problem: LearningProblem) -> set:
    """Which train examples the state in this probe gets wrong."""
    learnt = [_p(r) for r in probe.state.get("learnt", [])]
    fw = _current_framework(problem.background, [r for r in learnt if r],
                            probe.state.get("new_asms", {}))
    dom = problem.get_domain()
    bad = set()
    for e in problem.positive:
        if not check_brave_entailment(fw, [e], [], dom)[0]:
            bad.add(re.sub(r'\s+', '', e))
    for e in problem.negative:
        if not check_brave_entailment(fw, [], [e], dom)[0]:
            bad.add(re.sub(r'\s+', '', e))
    return bad


def _p(prolog: str) -> Optional[Rule]:
    from src.aba_prompts import _parse_rule_line
    return _parse_rule_line(prolog)


def _pred_of(atom: str) -> str:
    """Predicate symbol of an atom, ignoring its arguments and spacing."""
    return re.sub(r'\s+', '', atom).split("(")[0]


def _declared_assumption(atom: str, background: ABAFramework) -> bool:
    """True if `atom` is an assumption already declared in the background.

    Compared on the predicate symbol: the background lists `u(X)` but a model
    may instantiate a different variable name for the same assumption.
    """
    a = _pred_of(atom)
    return any(_pred_of(x) == a for x in background.assumptions)


_ASM_LABELLED = re.compile(
    r'ASSUMPTION\s*:\s*(.+?)\s+defeated_by\s+(.+?)\s*$',
    re.IGNORECASE | re.MULTILINE)
_ASM_BARE = re.compile(r'^\s*(.+?)\s+defeated_by\s+(.+?)\s*$', re.IGNORECASE)


def _atom(s: str) -> str:
    """Trim an atom written as a sentence: `c_alpha(X).` -> `c_alpha(X)`.

    The trailing full stop is Prolog punctuation, not part of the atom, but it
    used to be captured into the contrary and then registered AS the contrary,
    so nothing could ever defeat the assumption. Eight 14B answers were scored
    wrong for a full stop.
    """
    return s.strip().rstrip(".").strip()


def _assumption_decl(lines: List[str]) -> Optional[Tuple[str, str]]:
    """(assumption, contrary) from either answer format.

    Two formats are in the corpus because the probe prompt and the shared
    SYSTEM_PROMPT disagree: `_P4` asks for `ASSUMPTION: a defeated_by c`, the
    system prompt for a `NEW ASSUMPTIONS:` block of bare `a defeated_by c`
    lines. Qwen2.5-14B followed the first, 3B/7B/32B the second — and demanding
    the label alone scored 249 answers 0 without the oracle ever running.

    Tried in precedence order, because the bare form also matches the
    background's own declarations: it is reached only when neither the label nor
    the block header is present.
    """
    m = _ASM_LABELLED.search("\n".join(lines))
    if m:
        return _atom(m.group(1)), _atom(m.group(2))
    for i, ln in enumerate(lines):
        if _ASMS_HDR.match(ln):
            for nxt in lines[i + 1:]:
                if _RULES_HDR.match(nxt) or _ASMS_HDR.match(nxt):
                    break
                m = _ASM_BARE.match(nxt)
                if m:
                    return _atom(m.group(1)), _atom(m.group(2))
            break
    for ln in lines:
        m = _ASM_BARE.match(ln)
        if m:
            return _atom(m.group(1)), _atom(m.group(2))
    return None


def _score_introduce(probe: Probe, text: str,
                     problem: LearningProblem) -> Tuple[bool, float, str]:
    """Semantic oracle: does the model's own proposal yield a Definition-1
    solution? Any correct answer passes, not only the solver's."""
    rules = [r for r in (_rule_from(seg) for seg in _split_labelled(text))
             if r is not None]
    decl = _assumption_decl(text.split("\n"))
    # Only the defeasible rule and the assumption declaration are mandatory:
    # when an existing assumption is reused there is no contrary rule to write.
    if not rules or decl is None:
        return False, 0.0, "<incomplete>"
    asm, contra = decl
    # The guarded rule is the one carrying the assumption, not necessarily the
    # first: under the `NEW RULES:` format the contrary's rule may come first.
    i = next((j for j, r in enumerate(rules)
              if any(_pred_of(b) == _pred_of(asm) for b in r.body)), 0)
    defeasible = rules[i]
    # Any further rules the model volunteered are IGNORED. R3 is only the two
    # choices `applyAsmIntro` makes (Algorithm 1 lines 34-46): which rule to
    # guard, and which assumption. The contrary's extension S is not chosen by
    # the algorithm at all — it is computed by the ASP solver at line 44 and
    # rote-learnt at lines 23-25, and Proposition 2 guarantees such an S exists.
    # Scoring a model-supplied contrary would demand more than the reference
    # algorithm decides.

    learnt = [r for r in (_p(x) for x in probe.state.get("learnt", [])) if r]
    idx = probe.state.get("idx", 0)
    new_learnt = learnt[:idx] + [defeasible] + learnt[idx + 1:]
    new_asms = dict(probe.state.get("new_asms", {}))
    reuse = _declared_assumption(asm, problem.background)

    try:
        if reuse:
            # Line 36-38: an assumption already in A, whose contrary is fixed by
            # the background (Definition 1(iv)). S := empty, so the framework
            # must already be a solution — there is nothing left to learn.
            fw = _current_framework(problem.background, new_learnt, new_asms)
            sat, _, _ = check_brave_entailment(
                fw, problem.positive, problem.negative, problem.get_domain())
            if not sat:
                # Line 39: reuse FAILED, so the algorithm backtracks and mints a
                # fresh assumption instead (line 41). Scoring the single forward
                # answer marks that wrong and so penalises the model for obeying
                # REUSE FIRST — which inverted the scale trend when measured:
                # all 24 of Qwen2.5-32B's failed reuses are rescued this way.
                sat = _fresh_assumption_works(
                    defeasible, asm, probe, problem, new_learnt, new_asms)
        else:
            # Lines 41-44: a fresh assumption, then RoLe restricted to T =
            # {c_alpha} supplies the exceptions. Satisfiability of that ASP
            # program IS the criterion (Theorem 2), so run it rather than
            # asking the model for facts the algorithm never chooses.
            new_asms[asm] = contra
            fw = _current_framework(problem.background, new_learnt, new_asms)
            sat = _contrary_is_learnable(fw, contra, problem)
        # Which choice Algorithm 1 line 36 would have made here. Legality
        # saturates above 7B, so this is the discriminating half of the probe.
        expected = _reuse_available(probe, problem)
    except Exception:
        return False, 0.0, "<solver error>"

    parsed = (f"{defeasible.to_prolog()} | {asm} defeated_by {contra} | "
              f"chose={'reuse' if reuse else 'fresh'},"
              f"line36={'reuse' if expected else 'fresh'}")
    return bool(sat), 1.0 if sat else 0.0, parsed


def _reuse_available(probe: Probe, problem: LearningProblem) -> bool:
    """Does an assumption relative to the folded rule's body exist (line 36)?

    When one does, Algorithm 1 reuses it and only mints a fresh assumption on
    backtracking; when none does, minting is the correct move. Comparing the
    model's choice against this is what `reuse_agreement` reports.
    """
    folded = _p(probe.state.get("folded", "")) if probe.state.get("folded") else None
    if folded is None:
        return False
    learnt = [r for r in (_p(x) for x in probe.state.get("learnt", [])) if r]
    fw = _current_framework(problem.background, learnt,
                            probe.state.get("new_asms", {}))
    return bool(_assumptions_relative_to(folded.body, fw))


def _fresh_assumption_works(defeasible: Rule, reused_asm: str, probe: Probe,
                            problem: LearningProblem, new_learnt: List[Rule],
                            new_asms: Dict[str, str]) -> bool:
    """Algorithm 1 line 39 -> 41: retry the same guarded rule with a new alpha."""
    body = [b for b in defeasible.body
            if _pred_of(b) != _pred_of(reused_asm)]
    asm, contra = _new_assumption_name(
        list(problem.background.assumptions) + list(new_asms.keys()))
    fresh = Rule(head=defeasible.head, body=body + [asm])
    idx = probe.state.get("idx", 0)
    learnt = new_learnt[:idx] + [fresh] + new_learnt[idx + 1:]
    asms = {**new_asms, asm: contra}
    fw = _current_framework(problem.background, learnt, asms)
    return _contrary_is_learnable(fw, contra, problem)


def _contrary_is_learnable(fw: ABAFramework, contrary: str,
                           problem: LearningProblem) -> bool:
    """Algorithm 1 line 44: can RoLe complete this R3 into a solution?

    `S := getAS(ASP(F, E+, E-, {c_alpha}))` — rote learning with the contrary
    as the ONLY learnable predicate. By Theorem 2 the program is satisfiable
    exactly when a solution exists, so success here means the model's choice of
    rule and assumption was one the algorithm could have made.
    """
    m = re.match(r'^\s*([a-z]\w*)', contrary)
    if m is None:
        return False
    rote = LearningProblem(
        background=fw,
        positive=problem.positive,
        negative=problem.negative,
        learnable=[m.group(1)],
        domain=problem.get_domain(),
        problem_id=f"{problem.problem_id}_probe_asm_intro",
    )
    _, ok, _ = run_rote_learning(rote)
    return ok


def _split_labelled(text: str) -> List[str]:
    """The answer's rule-bearing lines, under either output format.

    RULE:/CONTRARY: labels first; then the `NEW RULES:` block bounded by the
    next header; then every line. The block must be bounded — unbounded, the
    final fall-back parses whatever follows as further contrary rules.
    """
    lines = text.split("\n")
    labelled = [ln for ln in lines
                if re.match(r'^\s*(RULE|CONTRARY)\s*:', ln, re.IGNORECASE)]
    if len(labelled) >= 2:
        return labelled
    for i, ln in enumerate(lines):
        if _RULES_HDR.match(ln):
            block = []
            for nxt in lines[i + 1:]:
                if _RULES_HDR.match(nxt) or _ASMS_HDR.match(nxt):
                    break
                block.append(nxt)
            if any(":-" in b for b in block):
                return block
            break
    return lines


# ──────────────────────────────────────────────────────────────────────────────
# Aggregation
# ──────────────────────────────────────────────────────────────────────────────

def balanced_accuracy(results: List[ProbeResult]) -> Optional[float]:
    """Mean of per-class recall — the honest score for a binary probe.

    Raw accuracy on an unbalanced YES/NO pool rewards always answering the
    majority class; balanced accuracy puts a constant answer at exactly 0.5,
    which is the floor these probes must be reported against.
    """
    pos = [r for r in results if r.oracle_bool is True]
    neg = [r for r in results if r.oracle_bool is False]
    if not pos or not neg:
        return None
    return 0.5 * (sum(r.correct for r in pos) / len(pos)
                  + sum(r.correct for r in neg) / len(neg))


def run_probes(dataset, backend, max_per_kind: int = 2, n_samples: int = 1,
               temperature: float = 0.0, max_tokens: int = 512,
               seed: int = 42, verbose: bool = True) -> List[ProbeResult]:
    """Generate probes for every problem and put each to the model.

    `temperature=0` by default: a probe asks for ONE decision with a short
    constrained answer, so sampling noise is a confound rather than a signal.
    `n_samples=1` likewise — statistical power here comes from the ~780 probe
    items, not from repeated draws of the same item.
    """
    model_name = getattr(backend, "model", type(backend).__name__)
    results: List[ProbeResult] = []
    entries = list(dataset)
    for i, entry in enumerate(entries):
        problem = entry.problem
        probes = generate_probes(problem, max_per_kind=max_per_kind, seed=seed)
        if verbose:
            print(f"  [{i+1}/{len(entries)}] {problem.problem_id}: "
                  f"{len(probes)} probes ...", end=" ", flush=True)
        n_ok = 0
        for probe in probes:
            for s in range(n_samples):
                r = ProbeResult(
                    probe_id=f"{probe.probe_id}#{s}", problem_id=probe.problem_id,
                    kind=probe.kind, model_name=model_name,
                    oracle_repr=_repr_oracle(probe.oracle),
                    oracle_bool=(probe.oracle
                                 if isinstance(probe.oracle, bool) else None),
                )
                try:
                    resp = backend.generate(probe.prompt, temperature=temperature,
                                            max_tokens=max_tokens)
                except Exception as exc:
                    r.error = f"{type(exc).__name__}: {exc}"
                    results.append(r)
                    continue
                r.raw_output = resp.text
                r.llm_latency_s = resp.latency_s
                r.prompt_tokens = resp.prompt_tokens
                r.completion_tokens = resp.completion_tokens
                try:
                    r.correct, r.score, r.parsed = score_probe(
                        probe, resp.text, problem)
                except Exception as exc:
                    r.error = f"score: {type(exc).__name__}: {exc}"
                n_ok += bool(r.correct)
                results.append(r)
        if verbose:
            total = max(1, len(probes) * n_samples)
            print(f"{n_ok}/{total} correct")
    return results


def aggregate_probes(results: List[ProbeResult],
                     prompt_version: str = PROBE_PROMPT_VERSION) -> Dict[str, Any]:
    # The version belongs to the GENERATION of the answers, not to this scoring
    # pass — re-scoring a v1 run must not stamp it v2. `rescore.py` therefore
    # passes through whatever the original summary recorded.
    out: Dict[str, Any] = {"n": len(results), "probe_prompt_version": prompt_version}
    for kind in KINDS:
        rs = [r for r in results if r.kind == kind]
        if not rs:
            continue
        entry = {
            "n": len(rs),
            "accuracy": round(sum(r.correct for r in rs) / len(rs), 3),
            "score":    round(sum(r.score for r in rs) / len(rs), 3),
            "chance":   0.5 if kind in BINARY_KINDS else 0.0,
        }
        if kind in BINARY_KINDS:
            ba = balanced_accuracy(rs)
            entry["balanced_accuracy"] = round(ba, 3) if ba is not None else None
        if kind == "introduce":
            # `accuracy` credits the reuse->fresh fallback of lines 39-41 and so
            # saturates above 3B: R3 is easy on this benchmark. What still
            # differs is HOW the models get there, so report the process
            # descriptively rather than scoring it.
            #
            # NOT an accuracy. Agreement with line 36 would be degenerate here:
            # an assumption relative to the body (Definition 4) exists in only
            # 2.9% of these probes, so the algorithm mints a fresh assumption
            # almost always and "always answer fresh" would score 0.97 without
            # reasoning — the same trap balanced accuracy guards against on the
            # binary probes. Reusing a non-relative assumption is still a legal
            # R3 (the rule admits "a (possibly new) assumption"); it is simply
            # not the choice Algorithm 1's control flow would make.
            scored = [r for r in rs if "chose=" in r.parsed]
            if scored:
                entry["reuse_rate"] = round(
                    sum(_chose(r.parsed) == "reuse" for r in scored) / len(scored), 3)
                entry["line36_reuse_available"] = round(
                    sum(_line36(r.parsed) == "reuse" for r in scored) / len(scored), 3)
                entry["n_scored"] = len(scored)
        out[kind] = entry
    return out


def _chose(parsed: str) -> str:
    m = re.search(r'chose=(\w+)', parsed)
    return m.group(1) if m else ""


def _line36(parsed: str) -> str:
    m = re.search(r'line36=(\w+)', parsed)
    return m.group(1) if m else ""
