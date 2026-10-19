"""Step-wise supervision (arm S2): each computed step of Algorithm 1 as one question.

The model answers ONE step at a time, at the state the reference has reached:

    role             line 8      the facts RoLe learns            R1 <fact> lines
    subsume          line 16     sat without the fact rho?        fails: <examples>. yes.|no.
    fold_candidates  line 17     the folds of rho, in order       R2 candidates: [<r>] ...
    check            line 18     sat with the fold rho_f?         fails: <examples>. yes.|no.
    reuse_scan       line 36     assumptions relative to rho_f    R3 reuse: [<a>] ... .
    reuse_check      line 38     sat with rho_f guarded by alpha? yes.|no.
    contrary_facts   lines 41-44 the facts for the new contrary   R1 <fact> lines

The reference's own search keeps the control flow (fact order, choice points, line-39
backtracking, mint naming) and asks each step through its oracle (`aba_algorithm._ask`),
so harvesting the gold and running a model use the same code: `step_prompt` builds the
question from the oracle's state at both times, and `parse_answer` reads the gold target
back to the reference's own answer (asserted by the corpus gates).

The lines-16/18 targets first name the examples that fail in the unique answer set of
ASP(F, <{}, {}>, {}) (E+ atoms missing, then E- atoms present), then give the verdict:
an explanation of the test, which the controller does not read. Line 38 stays bare: most
of its frameworks have no stable extension.

`harvest` also asks line 18 at every non-dom fold candidate the search does not reach
(`extra` rows, training only): the same test at more states. dom(X) folds are left out
because they always fail.
"""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.aba_algorithm import ORACLE_KINDS, _current_framework, solve_aba_learning
from src.aba_prompts import _clean_llm_output, _format_problem, _parse_rule_line
from src.aba_score import _BRACKETS, _as_fact, _key, _norm
from src.aba_sft import render_trace_target
from src.aba_tracelog import RunRecord, TraceRecorder
from src.aba_types import ABAFramework, LearningProblem, Rule
from src.aba_validator import _build_asp, _norm as _norm_atom, _solve, check_brave_entailment

# Frozen: a change to any text below is a new prompt version, not a refactor.
STEP_PROMPT_VERSION = "v1-step"

_STEP_TASK = """YOUR TASK: execute ONE step of ASP-ABAlearnB (Algorithm 1, De Angelis,
Proietti & Toni) on the problem below, at the state shown, and answer that step only.
The state lists Rl, the rules learnt so far, without the fact rho being processed;
with the background rules R it forms Rt (line 15). Facts are listed in the order of
T, then of the domain. applyFolding (line 17, Definition 3) replaces the equality
X = t of rho by the head of each background rule that holds for t by an equality
(a fact p(t). or a rule p(X) :- X = t, ...), in the order R lists them, and last by
dom(X); never by learnt rules. An assumption alpha(X) is relative to a body B
(Definition 4) if a rule H :- B, alpha(X) is in Rt. The tests at lines 16 and 18
are answered with the examples that fail in the framework's stable extension
(positive examples not accepted, negative examples accepted), then yes if none
fails, else no."""

DECISIONS = ("subsume", "check", "reuse_check")
WITNESSED = ("subsume", "check")
CAP_CALLS, CAP_LEARNT = 200, 64


class StepStop(Exception):
    """A chained run stops: the answer was unusable, or a cap was hit."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


# ─────────────────────────────────────────────────────────────────────────────
# State and prompt
# ─────────────────────────────────────────────────────────────────────────────

def step_state(kind: str, s: Dict[str, Any], background: ABAFramework) -> Dict[str, Any]:
    """The oracle's payload as JSON: Rl without rho (or without rho_f), new assumptions, subject."""
    if kind == "role":
        return {}
    asms = {a: c for a, c in s["new_asms"].items() if a not in background.assumptions}
    if kind in ("subsume", "fold_candidates", "check"):
        rl = [r for i, r in enumerate(s["learnt"]) if i != s["idx"]]
        out = {"rl": [r.to_prolog() for r in rl], "asms": asms, "rule": s["rule"].to_prolog()}
        if kind == "check":
            out["fold"] = s["folded"].to_prolog()
        return out
    fold = s["folded"].to_prolog()
    # the learnt list the reference tests at lines 38 and 43 (aba_algorithm, asm_intro_options)
    rl = [r.to_prolog() for r in s["learnt"] if r.to_prolog() != fold]
    out = {"rl": rl, "asms": asms, "fold": fold}
    if kind in ("reuse_check", "contrary_facts"):
        out.update(asm=s["asm"], guarded=s["guarded"].to_prolog())
    if kind == "contrary_facts":
        out["contrary"] = s["contrary"]
    return out


def render_state(state: Dict[str, Any]) -> str:
    lines = ["=== RULES LEARNT SO FAR (Rl, without rho) ==="]
    lines += [f"  {r}" for r in state["rl"]] or ["  (none)"]
    if state["asms"]:
        lines += ["", "=== ASSUMPTIONS INTRODUCED SO FAR ==="]
        lines += [f"  {a} defeated_by {c}" for a, c in state["asms"].items()]
    return "\n".join(lines)


def _pred(atom: str) -> str:
    return re.match(r"\s*([a-z]\w*)", atom).group(1)


def question(kind: str, state: Dict[str, Any]) -> str:
    if kind == "role":
        return ("STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set\n"
                "of facts p(X) :- X = t, with p in T, that makes the framework a solution.\n"
                "One per line: R1 p(X) :- X = t.   or: none.")
    if kind == "subsume":
        return (f"STEP: Fact Subsumption (line 16) on rho: {state['rule']}\n"
                "Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?\n"
                "Answer: fails: <examples, or none>. yes.   or   ... no.")
    if kind == "fold_candidates":
        return (f"STEP: applyFolding (line 17) on rho: {state['rule']}\n"
                "List every fold of rho, in order.\n"
                "Answer: R2 candidates: [<rule>] [<rule>] ...")
    if kind == "check":
        return (f"STEP: the test at line 18 on rho: {state['rule']}\n"
                f"with rho_f: {state['fold']}\n"
                "Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?\n"
                "Answer: fails: <examples, or none>. yes.   or   ... no.")
    if kind == "reuse_scan":
        return (f"STEP: applyAsmIntro (line 36) on rho_f: {state['fold']}\n"
                "List the assumptions in A relative to the body of rho_f.\n"
                "Answer: R3 reuse: [<assumption>] ... .   or: R3 reuse: none.")
    if kind == "reuse_check":
        return (f"STEP: the test at line 38 with the relative assumption {state['asm']}\n"
                f"rho_d: {state['guarded']}\n"
                "Is ASP(<Rt u {rho_d}, A, C>, <E+, E->, {}) satisfiable?\n"
                "Answer: yes.   or: no.")
    c = _pred(state["contrary"])
    return (f"STEP: lines 41-44 on rho_f: {state['fold']}\n"
            f"A new assumption {state['asm']}, with contrary {state['contrary']}, gives\n"
            f"rho_d: {state['guarded']}\n"
            f"List the facts for {c} in S := getAS(ASP(F, <E+, E->, {{{c}}})), where\n"
            f"F = <Rt u {{rho_d}}, A u {{{state['asm']}}}, C u {{{state['asm']} -> "
            f"{state['contrary']}}}>; lines 23-25 learn them.\n"
            f"One per line: R1 {c}(X) :- X = t.   or: none.")


def step_prompt(problem: LearningProblem, kind: str, state: Dict[str, Any]) -> str:
    """The one prompt for a step, at harvest and at inference."""
    parts = [_STEP_TASK, "", _format_problem(problem), ""]
    if kind != "role":
        parts += [render_state(state), ""]
    parts.append(question(kind, state))
    return "\n".join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# Targets
# ─────────────────────────────────────────────────────────────────────────────

def failing_examples(fw: ABAFramework, problem: LearningProblem) -> Tuple[int, Optional[List[str]]]:
    """(number of answer sets of ASP(fw, <{}, {}>, {}), failing examples if exactly one)."""
    _, models, _ = _solve(_build_asp(fw, [], [], problem.get_domain()), n_models=0)
    if len(models) != 1:
        return len(models), None
    m = {_norm_atom(a) for a in models[0]}
    return 1, ([e for e in problem.positive if _norm_atom(e) not in m]
               + [e for e in problem.negative if _norm_atom(e) in m])


def _facts(rules: List[Rule]) -> str:
    return "\n".join(f"R1 {r.to_prolog()}" for r in rules) or "none."


def render_answer(kind: str, answer: Any, witness: Optional[List[str]] = None) -> str:
    """The target text for the reference's answer to a step."""
    if kind in ("role", "contrary_facts"):
        facts, ok, _ = answer
        assert ok, "line 8 / 44 unsatisfiable: no target"    # Theorem 2, Proposition 2
        return _facts(facts)
    if kind == "fold_candidates":
        return ("R2 candidates: " + " ".join(f"[{r.to_prolog()}]" for r, _ in answer)
                if answer else "R2 candidates: none.")
    if kind == "reuse_scan":
        return "R3 reuse: " + (" ".join(f"[{a}]" for a in answer) + "." if answer else "none.")
    verdict = "yes." if answer else "no."
    if kind == "reuse_check":
        return verdict
    if answer:
        return f"fails: none. {verdict}"
    return f"fails: {', '.join(witness) if witness else 'unknown'}. {verdict}"


# ─────────────────────────────────────────────────────────────────────────────
# Parsing an answer back into the reference's terms
# ─────────────────────────────────────────────────────────────────────────────

_FACT = re.compile(r"^([a-z]\w*)\(X\) :- X = ([a-z0-9]\w*)\.$")
_ATOM = re.compile(r"[a-z]\w*(?:\([^()]*\))?")
_ENDS = re.compile(r"(?:^|[\s.:])(yes|no)\s*\.?\s*$", re.I)


def _lines(text: str) -> List[str]:
    return [ln for ln in map(_norm, _clean_llm_output(text).split("\n")) if ln]


def _read_facts(lines: List[str], preds: List[str], problem: LearningProblem,
                kind: str) -> Tuple[List[Rule], int]:
    """Legal facts p(X) :- X = t (p in preds, t in the domain), in (preds, domain) order."""
    dom, seen, out, bad = problem.get_domain(), set(), [], 0
    for ln in lines:
        m = re.match(r"^R1\s+(.+)$", ln)
        r = _as_fact(_parse_rule_line(m.group(1))) if m else None
        f = r and _FACT.match(r.to_prolog())
        if not f or f.group(1) not in preds or f.group(2) not in dom:
            bad += 1
            continue
        if r.to_prolog() not in seen:
            seen.add(r.to_prolog())
            out.append(r)
    if not out and bad:
        raise StepStop(f"empty:{kind}")
    order = lambda r: (preds.index(_FACT.match(r.to_prolog()).group(1)),
                       dom.index(_FACT.match(r.to_prolog()).group(2)))
    return sorted(out, key=order), bad


def parse_answer(kind: str, text: str, problem: LearningProblem, gold: Any = None,
                 state: Optional[Dict[str, Any]] = None) -> Tuple[Any, Dict[str, Any]]:
    """(answer in the type the reference returns, notes). Raises StepStop if unusable.

    `gold` is the reference's answer at this state, used only to map a legal fold onto the
    reference's object (folds are legal iff applyFolding offers them); `state` is the
    oracle's payload, for the assumptions in A.
    """
    lines = _lines(text)
    notes: Dict[str, Any] = {"illegal": 0}
    if not lines:
        raise StepStop(f"unparseable:{kind}")
    if kind in DECISIONS:
        m = _ENDS.search(lines[-1])
        if not m:
            raise StepStop(f"unparseable:{kind}")
        if kind in WITNESSED:
            w = re.match(r"^fails:\s*(.*?)\s*\.?\s*(?:yes|no)\s*\.?\s*$", " ".join(lines), re.I)
            body = w.group(1).strip().rstrip(".") if w else None
            notes["witness"] = (None if body is None or body.lower() == "unknown" else
                                [] if body.lower() == "none" else _ATOM.findall(body))
        return m.group(1).lower() == "yes", notes
    if kind == "role":
        if lines == ["none."] or lines == ["none"]:
            return ([], True, "none"), notes
        facts, notes["illegal"] = _read_facts(lines, list(problem.learnable), problem, kind)
        return (facts, True, "model"), notes
    if kind == "contrary_facts":
        if lines == ["none."] or lines == ["none"]:
            return ([], True, "none"), notes
        facts, notes["illegal"] = _read_facts(lines, [_pred(state["contrary"])], problem, kind)
        return (facts, True, "model"), notes
    if kind == "fold_candidates":
        m = re.match(r"^R2 candidates:\s*(.*)$", lines[0])
        if not m:
            raise StepStop(f"unparseable:{kind}")
        if m.group(1).strip().rstrip(".").lower() == "none":
            raise StepStop(f"empty:{kind}")                  # Definition 3, F1: dom always folds
        legal = {_key(r): (r, via) for r, via in gold}
        out, seen = [], set()
        for txt in _BRACKETS.findall(m.group(1)):
            r = _parse_rule_line(txt)
            k = r is not None and _key(r)
            if k not in legal:
                notes["illegal"] += 1
            elif k not in seen:
                seen.add(k)
                out.append(legal[k])
        if not out:
            raise StepStop(f"empty:{kind}")
        return out, notes
    # reuse_scan
    m = re.match(r"^R3 reuse:\s*(.*)$", lines[0])
    if not m:
        raise StepStop(f"unparseable:{kind}")
    if m.group(1).strip().rstrip(".").lower() == "none":
        return [], notes
    A = set(problem.background.assumptions) | set(state["new_asms"])
    named = [a.strip() for a in _BRACKETS.findall(m.group(1))]
    out = list(dict.fromkeys(a for a in named if a in A))
    notes["illegal"] = len(named) - sum(a in A for a in named)
    if named and not out:
        raise StepStop(f"empty:{kind}")
    return out, notes


def same_answer(kind: str, a: Any, b: Any) -> bool:
    """Equality of two answers to the same step, in the reference's terms."""
    if kind in ("role", "contrary_facts"):
        return ([r.to_prolog() for r in a[0]], a[1]) == ([r.to_prolog() for r in b[0]], b[1])
    if kind == "fold_candidates":
        return [r.to_prolog() for r, _ in a] == [r.to_prolog() for r, _ in b]
    return a == b


# ─────────────────────────────────────────────────────────────────────────────
# Oracles
# ─────────────────────────────────────────────────────────────────────────────

class RecordingOracle:
    """Answers with the reference and records (kind, payload, answer) in call order."""

    def __init__(self) -> None:
        self.calls: List[Tuple[str, Dict[str, Any], Any]] = []

    def __call__(self, kind: str, state: Dict[str, Any], compute: Callable[[], Any]) -> Any:
        answer = compute()
        self.calls.append((kind, state, answer))
        return answer


class ModelOracle:
    """Answers the steps in `kinds` with `generate(prompt, kind) -> text`; the rest, and a
    shadow of every step, with the reference. Every model call is logged."""

    def __init__(self, problem: LearningProblem, generate: Callable[[str, str], str],
                 kinds=ORACLE_KINDS) -> None:
        self.p, self.generate, self.kinds = problem, generate, set(kinds)
        self.log: List[Dict[str, Any]] = []

    def __call__(self, kind: str, state: Dict[str, Any], compute: Callable[[], Any]) -> Any:
        gold = compute()                        # now: the closures move with the search loops
        if kind not in self.kinds:
            return gold
        if len(self.log) >= CAP_CALLS:
            raise StepStop("cap:calls")
        if len(state.get("learnt", ())) > CAP_LEARNT:
            raise StepStop("cap:learnt")
        st = step_state(kind, state, self.p.background)
        text = self.generate(step_prompt(self.p, kind, st), kind)
        entry = {"kind": kind, "raw": text, "state": st}
        self.log.append(entry)
        try:
            answer, notes = parse_answer(kind, text, self.p, gold, state)
        except StepStop as e:
            entry["error"] = e.code
            raise
        entry.update(notes, correct=same_answer(kind, answer, gold))
        return answer


def chained_run(problem: LearningProblem, oracle) -> Dict[str, Any]:
    """Algorithm 1 on the oracle's answers, rendered in the trace grammar plus answer block."""
    rec = TraceRecorder()
    error, trace = None, None
    try:
        _, trace = solve_aba_learning(problem, observer=rec, oracle=oracle)
    except StepStop as e:
        error = e.code
    except RecursionError:
        error = "recursion"
    record = RunRecord(problem_id=problem.problem_id, role_facts=rec.role_facts,
                       events=rec.events)
    final = trace.final_framework if trace is not None else None
    text = "" if error or final is None else render_trace_target(record, final, problem)
    return {"text": text, "error": error or ("role_failed" if final is None else None),
            "record": record, "retractions": record.n_retractions}


# ─────────────────────────────────────────────────────────────────────────────
# Harvest
# ─────────────────────────────────────────────────────────────────────────────

def _line18(problem: LearningProblem, learnt: List[Rule], new_asms: Dict[str, str],
            idx: int, fold: Rule) -> Tuple[bool, ABAFramework]:
    """Line 18's test on `fold`, built as `gen_phase` builds it."""
    fw = _current_framework(problem.background, learnt[:idx] + [fold] + learnt[idx + 1:], new_asms)
    return check_brave_entailment(fw, problem.positive, problem.negative,
                                  problem.get_domain())[0], fw


def harvest(problem: LearningProblem, extra: bool = True) -> Tuple[List[Dict[str, Any]], RunRecord]:
    """One row per step the reference takes (plus `extra` line-18 rows), and its record.

    Each row: k, kind, state, target, answer (the reference's, for gates), verdict and
    witness for decisions, n_models for witnessed tests, facets (event, src, rank,
    first) and extra.
    """
    bg = problem.background
    rec, orc = TraceRecorder(), RecordingOracle()
    solve_aba_learning(problem, observer=rec, oracle=orc)
    record = RunRecord(problem_id=problem.problem_id, role_facts=rec.role_facts, events=rec.events)

    rows: List[Dict[str, Any]] = []
    role_facts, event, src, rho, folds, checks = set(), -1, "role", None, [], 0
    checked = {}                                 # (event, fold) -> the visited row
    for kind, s, answer in orc.calls:
        st = step_state(kind, s, bg)
        row = {"kind": kind, "state": st, "answer": answer, "extra": False}
        if kind == "role":
            role_facts = {r.to_prolog() for r in answer[0]}
        if kind == "subsume":
            event, rho = event + 1, s["rule"].to_prolog()
            src = "role" if rho in role_facts else "contrary"
            fw = _current_framework(bg, s["learnt"][:s["idx"]] + s["learnt"][s["idx"] + 1:],
                                    s["new_asms"])
            row["n_models"], row["witness"] = failing_examples(fw, problem)
        if kind == "fold_candidates":
            folds = [r.to_prolog() for r, _ in answer]
        if kind == "check":
            fw = _current_framework(bg, s["learnt"][:s["idx"]] + [s["folded"]]
                                    + s["learnt"][s["idx"] + 1:], s["new_asms"])
            row["n_models"], row["witness"] = failing_examples(fw, problem)
            row["rank"] = folds.index(s["folded"].to_prolog())
            row["first"], checks = checks == 0, checks + 1
            checked[(event, st["fold"])] = row
        if kind in DECISIONS:
            row["verdict"] = answer
        row["target"] = render_answer(kind, answer, row.get("witness"))
        row.update(event=event, src=src)
        row["payload"] = s
        rows.append(row)

    if extra:                                    # line 18 at the candidates the search skips
        out = []
        for row in rows:
            out.append(row)
            if row["kind"] != "fold_candidates":
                continue
            s = row["payload"]
            for rank, (fold, _) in enumerate(row["answer"]):
                f = fold.to_prolog()
                if (row["event"], f) in checked or any(b.startswith("dom(") for b in fold.body):
                    continue
                sat, fw = _line18(problem, s["learnt"], s["new_asms"], s["idx"], fold)
                n, wit = failing_examples(fw, problem)
                st = {**step_state("fold_candidates", s, bg), "fold": f}
                out.append({"kind": "check", "state": st, "answer": sat, "verdict": sat,
                            "n_models": n, "witness": wit, "target": render_answer("check", sat, wit),
                            "rank": rank, "first": False, "extra": True,
                            "event": row["event"], "src": row["src"],
                            "payload": {**s, "folded": fold}})
        rows = out
    for k, row in enumerate(rows):
        row["k"] = k
        row["cell"] = signal_cell(row)
    return rows, record


def signal_cell(row: Dict[str, Any]) -> str:
    """The decisions a position-only rule cannot predict (corpus statistics, 19 Oct)."""
    kind, src = row["kind"], row["src"]
    if kind == "check":
        if row["extra"]:
            return "extra_check"
        if row["first"]:
            return "first_check"
        if src == "role":
            return "second_path_check" if row["rank"] == 0 else "after_l39_check"
    if kind == "subsume" and src == "role" and row["event"] > 0:
        return "later_role_subsume"
    if kind == "reuse_check" and src == "role":
        return "role_reuse_check"
    return "other"


def gold_backend(rows: List[Dict[str, Any]], problem: LearningProblem) -> Callable[[str, str], str]:
    """generate(prompt, kind) answering with the harvested gold target; a prompt the
    harvest never built is an error (training and inference prompts must coincide)."""
    table = {step_prompt(problem, r["kind"], r["state"]): r["target"]
             for r in rows if not r["extra"]}
    return lambda prompt, kind: table[prompt]
