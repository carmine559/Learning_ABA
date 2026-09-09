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
    _is_ground_fact,
)
from src.aba_validator import run_rote_learning, check_brave_entailment
from src.aba_prompts import SYSTEM_PROMPT, _format_problem, _clean_llm_output

KINDS = ("role", "fold", "check", "introduce", "subsume")
BINARY_KINDS = ("check", "subsume")


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


def _head(problem: LearningProblem) -> str:
    return SYSTEM_PROMPT + "\n\n" + _format_problem(problem) + "\n"


_P1 = """TASK — apply ONLY the Rote Learning transformation (R1).

Add the MINIMAL set of ground facts that makes the framework a solution: one
stable extension accepting every positive example and no negative example.
Do not generalise, do not fold, do not introduce assumptions.

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
adding an assumption to its body, so that the framework becomes a solution again.

You may REUSE an assumption already declared in the background — if you do, its
contrary is already fixed and you must not redefine it, so write no CONTRARY
line. Otherwise introduce a new assumption and give rules for its contrary.

Output these lines, in this form and nothing else:
RULE: <head> :- <body>, <assumption>.
ASSUMPTION: <assumption> defeated_by <contrary>
CONTRARY: <contrary> :- <body>.
Repeat the CONTRARY line if more than one is needed; omit it when reusing an
existing assumption."""

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
    text = _clean_llm_output(raw_output or "")

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


def _declared_assumption(atom: str, background: ABAFramework) -> bool:
    """True if `atom` is an assumption already declared in the background.

    Compared on the predicate symbol: the background lists `u(X)` but a model
    may instantiate a different variable name for the same assumption.
    """
    a = re.sub(r'\s+', '', atom).split("(")[0]
    return any(re.sub(r'\s+', '', x).split("(")[0] == a
               for x in background.assumptions)


_ASM_LINE = re.compile(
    r'ASSUMPTION\s*:\s*(.+?)\s+defeated_by\s+(.+?)\s*$',
    re.IGNORECASE | re.MULTILINE)


def _score_introduce(probe: Probe, text: str,
                     problem: LearningProblem) -> Tuple[bool, float, str]:
    """Semantic oracle: does the model's own proposal yield a Definition-1
    solution? Any correct answer passes, not only the solver's."""
    rules = [r for r in (_rule_from(seg) for seg in _split_labelled(text))
             if r is not None]
    m = _ASM_LINE.search(text)
    # Only the defeasible rule and the assumption declaration are mandatory:
    # when an existing assumption is reused there is no contrary rule to write.
    if not rules or m is None:
        return False, 0.0, "<incomplete>"
    defeasible, contraries = rules[0], rules[1:]
    asm, contra = m.group(1).strip(), m.group(2).strip()

    learnt = [r for r in (_p(x) for x in probe.state.get("learnt", [])) if r]
    idx = probe.state.get("idx", 0)
    new_learnt = learnt[:idx] + [defeasible] + contraries + learnt[idx + 1:]
    new_asms = dict(probe.state.get("new_asms", {}))
    # Reusing an EXISTING assumption is the algorithm's preferred move
    # (Algorithm 1 line 36, which then sets S := empty — no contrary is learnt
    # at all). Its contrary is fixed by the background and must not be
    # redefined, per Definition 1(iv).
    if not _declared_assumption(asm, problem.background):
        new_asms[asm] = contra

    try:
        fw = _current_framework(problem.background, new_learnt, new_asms)
        sat, _, _ = check_brave_entailment(
            fw, problem.positive, problem.negative, problem.get_domain())
    except Exception:
        return False, 0.0, "<solver error>"

    # Correctness is the Definition-1 check ALONE. Algorithm 1 applies R3 and
    # then ROTE-LEARNS the contrary as ground facts (lines 23-25); only a later
    # Gen iteration folds it intensional — exactly the paper's Example 10, where
    # rho17 `c_alpha(X) <- X = a` becomes rho19 only on the next pass. Demanding
    # an intensional contrary here would mark the reference algorithm itself
    # wrong. Intensionality of the contrary is reported separately, and the
    # folding of the contrary is already covered by the P2 probes.
    intensional = all(not c.contains_constant() for c in contraries)
    parsed = " | ".join([defeasible.to_prolog()]
                        + [c.to_prolog() for c in contraries]
                        + [f"intensional={intensional}"])
    return bool(sat), 1.0 if sat else 0.0, parsed


def _split_labelled(text: str) -> List[str]:
    """RULE:/CONTRARY: lines first; fall back to every line."""
    labelled = [ln for ln in text.split("\n")
                if re.match(r'^\s*(RULE|CONTRARY)\s*:', ln, re.IGNORECASE)]
    return labelled if len(labelled) >= 2 else text.split("\n")


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


def aggregate_probes(results: List[ProbeResult]) -> Dict[str, Any]:
    out: Dict[str, Any] = {"n": len(results)}
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
        out[kind] = entry
    return out
