"""
aba_trace.py
Trace fidelity: does the LLM *execute* ASP-ABAlearnB, or just land on an answer?

WHY THIS EXISTS
---------------
Every other metric in this repo is an OUTCOME metric — is the final framework a
Definition-1 solution? The thesis question is narrower: does the model replicate
the *algorithm*? Those come apart. Qwen2.5-14B scores 56.3% clean@k in `direct`
mode (168 tokens, no algorithmic process at all) but only 21.4% in `algorithm`
mode, where its intensionality collapses from 1.00 to 0.47 — the signature of
performing RoLe and then abandoning Gen.

WHY EXTRACTION IS LABEL-FREE
----------------------------
The obvious approach — count "Fold", "Remove", "STEP 2" markers — measures
instruction-following literalism, not reasoning. Measured over the v3 corpus:
mistral-7b writes the requested `Remove ... (solution preserved)` template 10x
more often than Qwen2.5-14B (35.3% vs 3.6%) and `Alternative path found` 6.5x
more often, while being far the weaker reasoner. `algorithm` mode has 0% template
compliance because _TASK_ALGORITHM never asks for one. A marker-counting metric
would rank mistral above 14B.

So this module ignores prose entirely. It reads the RULES the model writes, in
the order it writes them, and infers which transformation each one represents
from the rule's own shape and its relation to what came before:

    a ground fact appears                      -> R1  (Rote Learning)
    an intensional rule that folds a prior fact -> R2  (Folding)
    a prior rule reappears + an assumption atom -> R3  (Assumption Introduction)
    a ground fact present in the trace but not
      in the final answer                       -> R4  (Fact Subsumption)

R2 is verified against `_candidate_folds`, so a claimed generalisation only
counts if it really is one application of the Folding rule against the
background. That makes the signal semantic rather than lexical.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any

from src.aba_types import Rule, ABAFramework, LearningTrace
from src.aba_algorithm import _candidate_folds, _extract_eq
from src.aba_prompts import (
    _clean_llm_output, _parse_rule_line, _parse_assumption_line,
)

# R1..R4, matching TransformStep.RULE_SYMBOL.
SYMBOLS = ("R1", "R2", "R3", "R4")

_HEAD_ARG_RE = re.compile(r'^([a-z]\w*)\(([^)]*)\)$')
_EQ_ATOM_RE  = re.compile(r'^([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)$')
_ALPHA_RE    = re.compile(r'^(c_)?alpha')
_RULES_HDR   = re.compile(r'^[ \t]*NEW[ \t]+RULES[ \t]*:', re.IGNORECASE)
_ASMS_HDR    = re.compile(r'^[ \t]*NEW[ \t]+ASSUMPTIONS[ \t]*:', re.IGNORECASE)
# Models frequently echo the prompt's problem statement back after the answer.
# Its example lines ("+ t(a)", "- v(b)") look exactly like rote-learnt ground
# facts, and would otherwise be scored as R1 steps the model never took — plus
# spurious R4s when they fail to reappear in the answer. The outcome parser
# already truncates on this marker; the trace extractor must do the same.
_ECHO_HDR    = re.compile(r'^[ \t]*===[ \t]')
_EXAMPLE_RE  = re.compile(r'^[ \t]*[+-][ \t]+[a-z]\w*\([^()]*\)[ \t]*$')


# ──────────────────────────────────────────────────────────────────────────────
# Canonical rule forms
# ──────────────────────────────────────────────────────────────────────────────

def ground_fact_of(rule: Rule) -> Optional[Tuple[str, str]]:
    """Return (predicate, constant) if `rule` denotes a ground fact.

    The same fact is spelled three different ways in this corpus, and all three
    must compare equal or every R1 mismatches:

        p(a).            bare fact           (models)
        p(a) :- a = a.   pseudo-normalised   (models)
        p(X) :- X = a.   normalised          (the solver, aba_validator.py:286)
    """
    m = _HEAD_ARG_RE.match(rule.head.strip())
    if not m:
        return None
    pred, arg = m.group(1), m.group(2).strip()

    if arg[:1].islower():                      # p(a).  /  p(a) :- a = a.
        # Any body must be vacuous (no atom beyond a trivial equality).
        for atom in rule.body:
            eq = _EQ_ATOM_RE.match(atom.strip())
            if not eq or eq.group(1) != eq.group(2):
                return None
        return pred, arg

    # p(X) :- X = a.   — exactly one binding equality, nothing else.
    if len(rule.body) != 1:
        return None
    eq = _EQ_ATOM_RE.match(rule.body[0].strip())
    if eq and eq.group(1) == arg and eq.group(2)[:1].islower():
        return pred, eq.group(2)
    return None


def normalised(rule: Rule) -> Rule:
    """Rewrite a ground fact into the solver's normalised form `p(X) :- X = c`.

    `_candidate_folds` finds the binding equality with `_EQ_RE`, which requires
    an uppercase variable (aba_algorithm.py:31). A model writing `v(a) :- a = a`
    therefore yields no fold candidates at all unless it is normalised first.
    """
    gf = ground_fact_of(rule)
    if gf is None:
        return rule
    return Rule(head=f"{gf[0]}(X)", body=[f"X = {gf[1]}"])


def _alpha_canon(text: str, mapping: Dict[str, str]) -> str:
    """Rename assumption predicates to positional names.

    The solver names new assumptions `alpha_0(X)` / `c_alpha_0(X)`
    (`_new_assumption_name`, aba_algorithm.py:230); models write `alpha(X)`,
    `alpha1(X)`, `alpha_q(X)`. Without renaming, exact matching is ~0 by
    artefact. Names are assigned in order of first appearance on each side, and
    a contrary `c_<asm>` inherits its assumption's index.
    """
    def repl(m: re.Match) -> str:
        name = m.group(0)
        if name not in mapping:
            base = name[2:] if name.startswith("c_") else name
            if base not in mapping:
                idx = len({v for v in mapping.values()
                           if not v.startswith("c_")})
                mapping[base] = f"alpha#{idx}"
            mapping[name] = (f"c_{mapping[base]}" if name.startswith("c_")
                             else mapping[base])
        return mapping[name]

    return re.sub(r'\b(c_)?alpha\w*', repl, text)


def canon(rule: Rule, mapping: Optional[Dict[str, str]] = None) -> str:
    """Canonical comparison key for a rule.

    Ground facts collapse to their normalised spelling; body atoms are sorted
    (`Rule.__eq__` is order-sensitive on the body, aba_types.py:78, but the
    order two systems happen to write a body in is not meaningful); assumption
    names are canonicalised.
    """
    mapping = {} if mapping is None else mapping
    gf = ground_fact_of(rule)
    if gf:
        text = f"{gf[0]}(X) :- X = {gf[1]}."
    else:
        body = sorted(re.sub(r'\s+', '', a) for a in rule.body)
        text = f"{re.sub(r'[ ]+', '', rule.head)} :- {', '.join(body)}."
    return _alpha_canon(text, mapping)


def _is_assumption_atom(atom: str, background: ABAFramework) -> bool:
    """True if `atom` is a declared background assumption or alpha-like."""
    a = re.sub(r'\s+', '', atom)
    if _ALPHA_RE.match(a):
        return True
    for asm in background.assumptions:
        if re.sub(r'\s+', '', asm) == a:
            return True
        # Compare on predicate symbol: background lists alpha(X) but the model
        # may instantiate a different variable name.
        m1, m2 = _HEAD_ARG_RE.match(a), _HEAD_ARG_RE.match(re.sub(r'\s+', '', asm))
        if m1 and m2 and m1.group(1) == m2.group(1):
            return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
# Gold trace normalisation
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Step:
    """One transformation, on either side of the comparison."""
    symbol: str                       # R1 | R2 | R3 | R4
    rule:   Optional[Rule] = None     # the rule produced (removed, for R4)
    source: str = ""                  # provenance, for the hand-audit
    key:    str = ""                  # canonical comparison key

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["rule"] = self.rule.to_prolog() if self.rule else None
        return d


def normalise_gold(trace: LearningTrace,
                   background: ABAFramework) -> List[Step]:
    """Turn a symbolic LearningTrace into a comparable step list.

    Repairs two defects of the recorded trace, both of which would otherwise be
    charged to the model:

    1. `folding_rule` (rho2) is declared but never populated at any append site
       in aba_algorithm.py, so it is re-derived here from `_candidate_folds`.
    2. The `assumption_introduction` step records `input_rule` as the *pre-fold*
       ground fact (aba_algorithm.py:404-411), collapsing R2 and R3 into one
       step. It is expanded back into the (R2, R3) pair it really is, so a model
       that correctly writes fold-then-introduce is not charged an extra step.
    """
    mapping: Dict[str, str] = {}
    steps: List[Step] = []

    for st in trace.steps:
        if st.step_type == "rote_learning":
            steps.append(Step("R1", st.output_rule, "gold:rote",
                              canon(st.output_rule, mapping)))

        elif st.step_type == "folding":
            steps.append(Step("R2", st.output_rule, "gold:fold",
                              canon(st.output_rule, mapping)))

        elif st.step_type == "assumption_introduction":
            folded = _implicit_folded_rule(st.input_rule, st.output_rule,
                                           background)
            if folded is not None:
                steps.append(Step("R2", folded, "gold:fold(implicit)",
                                  canon(folded, mapping)))
            steps.append(Step("R3", st.output_rule, "gold:asm_intro",
                              canon(st.output_rule, mapping)))
            # Contrary facts are rote-learnt (Algorithm 1 lines 23-25).
            for cf in st.new_contrary_facts:
                steps.append(Step("R1", cf, "gold:rote(contrary)",
                                  canon(cf, mapping)))

        elif st.step_type == "fact_subsumption":
            steps.append(Step("R4", st.input_rule, "gold:subsumption",
                              canon(st.input_rule, mapping)))

    return steps


def _implicit_folded_rule(input_rule: Optional[Rule],
                          output_rule: Optional[Rule],
                          background: ABAFramework) -> Optional[Rule]:
    """Recover the folded rule hidden inside a gold R3 step.

    The gold step goes straight from `p(X) :- X = c` to `p(X) :- q(X), alpha(X)`.
    The intermediate `p(X) :- q(X)` is the R2 result; reconstruct it by dropping
    the assumption atom from the output and confirming the remainder really is a
    legal fold of the input.
    """
    if input_rule is None or output_rule is None:
        return None
    if _extract_eq(input_rule.body) is None:
        return None                       # input already intensional: no fold
    stripped = [a for a in output_rule.body
                if not _is_assumption_atom(a, background)]
    if not stripped or len(stripped) == len(output_rule.body):
        return None
    candidate = Rule(head=output_rule.head, body=stripped)
    legal = {canon(c) for c in _candidate_folds(input_rule, background)}
    return candidate if canon(candidate) in legal else candidate


# ──────────────────────────────────────────────────────────────────────────────
# Label-free extraction from LLM text
# ──────────────────────────────────────────────────────────────────────────────

def _answer_span(lines: List[str]) -> Optional[Tuple[int, int]]:
    """Locate the FINAL answer block as a [start, end) line range.

    Bounded properly rather than run to end-of-text: mistral-7b and Qwen2.5-3B
    routinely emit the answer FIRST and the trace after it, so a block that ran
    to the end would swallow the whole trace.
    """
    starts = [i for i, ln in enumerate(lines) if _RULES_HDR.match(ln)]
    if not starts:
        return None
    start = starts[-1]
    i = start + 1
    while i < len(lines):
        ln = lines[i].strip()
        if (not ln or _ASMS_HDR.match(lines[i]) or ln.upper() == "NONE"
                or _parse_rule_line(ln) is not None
                or _parse_assumption_line(ln)[0] is not None):
            i += 1
            continue
        break
    return start, i


# Segment separators that cannot occur inside a rule. Splitting on them is
# syntactic bracketing, not semantic labelling: the step TYPE is still inferred
# from rule shape, never from the word that happened to precede the rule.
_SEG_SPLIT_RE = re.compile(r'\s+->\s+|\s+using\s+|(?<=\.)\s+')
_BRACKET_RE   = re.compile(r'\[[^\]]*\]')


def _rule_exprs(line: str) -> List[str]:
    """Rule-shaped substrings inside one line.

    Models embed rules in prose — `Add: v(a) :- a = a.` and
    `Fold v(a) :- a = a using p(a) is always true -> v(X) :- p(X).` (which
    carries two). Requiring the whole line to parse loses nearly all of them.
    """
    line = _BRACKET_RE.sub(" ", line)          # 'violates [v(e)]' is not a rule
    out: List[str] = []
    for seg in _SEG_SPLIT_RE.split(line):
        seg = seg.strip().lstrip("-*+#> \t").strip()
        m = re.search(r'[a-z]\w*\s*\(', seg)
        if not m:
            continue
        seg = seg[m.start():].strip().rstrip(".").strip()
        if not seg:
            continue
        if ":-" in seg:
            out.append(seg)
            continue
        # A bare fact only counts if nothing trails it; 'v(e) becomes accepted'
        # is a claim about an example, not a rule.
        if re.fullmatch(r'[a-z]\w*\([^()]*\)', seg):
            out.append(seg)
    return out


_HEADING_RE = re.compile(r'^\s*(#{1,6}\s|-{3,}\s*$|\*\*)')


def _strip_echo(lines: List[str]) -> List[str]:
    """Remove echoed problem-statement regions, keeping everything else.

    Truncating from the first "=== " to the end would be wrong: Qwen2.5-7B and
    mistral-7B routinely emit the ANSWER first, then echo the whole problem,
    then reason — so a truncation deletes the entire trace and silently scores
    the model 0. The echo is a bounded region instead: it starts at a "=== "
    header and ends when the model's own text resumes (a markdown heading, a
    horizontal rule, or an answer header).
    """
    out: List[str] = []
    in_echo = False
    for ln in lines:
        if _ECHO_HDR.match(ln):
            in_echo = True
            continue
        if in_echo:
            if (_HEADING_RE.match(ln) or _RULES_HDR.match(ln)
                    or _ASMS_HDR.match(ln)):
                in_echo = False
            else:
                continue
        out.append(ln)
    return out


def _head_pred(rule: Rule) -> Optional[str]:
    m = _HEAD_ARG_RE.match(rule.head.strip())
    return m.group(1) if m else None


def _is_learnt_head(rule: Rule, learnable: List[str],
                    background: ABAFramework) -> bool:
    """Definition 1(ii): a learnt rule's head is a learnable predicate or an
    entirely new one (typically the contrary of a new assumption).

    Without this filter, background facts quoted in prose — `Alternative path
    found using r(a) -> ...` — are counted as rote-learnt facts.
    """
    pred = _head_pred(rule)
    if pred is None:
        return False
    if pred in learnable or _ALPHA_RE.match(pred):
        return True
    bg_preds = {_head_pred(r) for r in background.rules}
    bg_preds |= {_head_pred(Rule(head=a)) for a in background.assumptions}
    bg_preds |= {_head_pred(Rule(head=c)) for c in background.contraries.values()}
    return pred not in bg_preds            # a genuinely new predicate


def extract_llm_steps(raw_output: str,
                      background: ABAFramework,
                      learnable: Optional[List[str]] = None) -> Tuple[List[Step], Dict]:
    """Infer the transformation sequence from the rules an LLM wrote.

    Returns (steps, info). `info["has_trace"]` is False when the output carries
    no reasoning at all — Qwen2.5-3B's `algorithm` mode has a median output of
    73 characters, i.e. the answer block alone. Such samples must be excluded
    from fidelity averages rather than scored as 0, the same denominator hygiene
    already applied to `intensional_rate`.
    """
    learnable = list(learnable or [])
    text = _clean_llm_output(raw_output or "")
    lines = text.split("\n")
    span = _answer_span(lines)

    trace_lines = (lines[:span[0]] + lines[span[1]:]) if span else lines
    answer_lines = lines[span[0]:span[1]] if span else []

    trace_lines = _strip_echo(trace_lines)
    trace_lines = [ln for ln in trace_lines if not _EXAMPLE_RE.match(ln)]

    mapping: Dict[str, str] = {}
    steps: List[Step] = []
    learnt: Dict[str, Rule] = {}          # canonical key -> rule, in order
    n_rule_lines = 0

    for raw_line in trace_lines:
        if _RULES_HDR.match(raw_line) or _ASMS_HDR.match(raw_line):
            continue
        for expr in _rule_exprs(raw_line):
            rule = _parse_rule_line(expr)
            if rule is None or not _HEAD_ARG_RE.match(rule.head.strip()):
                continue
            if not _is_learnt_head(rule, learnable, background):
                continue
            n_rule_lines += 1
            key = canon(rule, mapping)
            if key in learnt:
                continue                   # restatement, not a new step

            if ground_fact_of(rule) is not None:
                steps.append(Step("R1", rule, expr, key))
                learnt[key] = normalised(rule)
                continue

            folded_from = _folds_from(rule, learnt, background, mapping)
            if folded_from is not None:
                steps.append(Step("R2", rule, expr, key))
                learnt.pop(folded_from, None)   # fact replaced by the rule
                learnt[key] = rule
                continue

            guarded_from = _guards(rule, learnt, background, mapping)
            if guarded_from is not None:
                steps.append(Step("R3", rule, expr, key))
                learnt.pop(guarded_from, None)
                learnt[key] = rule
                continue

            learnt[key] = rule             # written, but no transformation
                                           # inferable — deliberately unscored

    # R4: a ground fact built during the trace that does not survive into the
    # final answer has been subsumed away.
    answer_keys = set()
    for ln in answer_lines:
        for expr in _rule_exprs(ln):
            r = _parse_rule_line(expr)
            if r is not None:
                answer_keys.add(canon(r, mapping))
    if answer_lines:
        for key, rule in learnt.items():
            if ground_fact_of(rule) is not None and key not in answer_keys:
                steps.append(Step("R4", rule, "absent from final answer", key))

    info = {
        "has_trace":     bool(trace_lines) and n_rule_lines > 0,
        "n_rule_lines":  n_rule_lines,
        "n_answer_rules": len(answer_keys),
        "answer_first":  bool(span and span[0] == 0 and span[1] < len(lines) - 1),
    }
    return steps, info


def _folds_from(rule: Rule, learnt: Dict[str, Rule], background: ABAFramework,
                mapping: Dict[str, str]) -> Optional[str]:
    """Key of the learnt ground fact that `rule` is a legal fold of, if any."""
    target = canon(rule, mapping)
    for key, prior in learnt.items():
        if ground_fact_of(prior) is None:
            continue
        for cand in _candidate_folds(prior, background):
            if canon(cand, dict(mapping)) == target:
                return key
    return None


def _guards(rule: Rule, learnt: Dict[str, Rule], background: ABAFramework,
            mapping: Dict[str, str]) -> Optional[str]:
    """Key of the learnt rule that `rule` extends with an assumption atom."""
    asm_atoms = [a for a in rule.body if _is_assumption_atom(a, background)]
    if not asm_atoms:
        return None
    stripped = Rule(head=rule.head,
                    body=[a for a in rule.body
                          if not _is_assumption_atom(a, background)])
    if not stripped.body:
        return None
    target = canon(stripped, dict(mapping))
    for key, prior in learnt.items():
        if canon(prior, dict(mapping)) == target:
            return key
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Alignment
# ──────────────────────────────────────────────────────────────────────────────

def _align(a: List[Step], b: List[Step], exact: bool = True) -> int:
    """Needleman-Wunsch; returns the number of matched positions.

    Gap and mismatch both score 0, a match scores 1, so the result is the
    length of the longest common subsequence under the chosen equality — an
    alignment that tolerates extra or missing steps on either side.
    """
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            same = (a[i - 1].symbol == b[j - 1].symbol
                    and (not exact or a[i - 1].key == b[j - 1].key))
            dp[i][j] = max(dp[i - 1][j], dp[i][j - 1],
                           dp[i - 1][j - 1] + (1 if same else 0))
    return dp[n][m]


@dataclass
class TraceScore:
    """Rule-keyed only, deliberately.

    An earlier version scored alignment over the R1/R2/R3/R4 SYMBOL sequence.
    Random sequences of the same lengths score 0.28-0.49 on that measure, i.e.
    at or above everything it was meant to detect — a four-symbol alphabet over
    length-4-8 sequences cannot discriminate. Every field below instead requires
    matching a canonical RULE, whose chance rate is ~0.
    """
    has_trace:   bool  = False
    n_steps_gold: int  = 0
    n_steps_llm:  int  = 0
    align_exact: float = 0.0     # order-sensitive LCS on (symbol, rule)
    # CAUTION when reporting the aggregate. Gold traces on this benchmark are
    # 44.8% R1 / 23.5% R2 / 10.4% R3 / 21.3% R4, so f1 is weighted towards R1.
    # R1 is not merely "copy the examples" — RoLe adds a MINIMAL set over the
    # learnable predicates, and 23.2% of its facts are contraries of assumptions
    # that occur in no example list — but it is still the step whose output
    # overlaps most with text the model was given (76.8% of R1 facts coincide
    # with a listed positive here). Consistent with that, mistral-7B edges
    # Qwen2.5-14B on cot f1 (0.352 vs 0.307) while losing every per-rule recall
    # (r2 0.126 vs 0.183, r3 0.000 vs 0.069). Report r2_recall/r3_recall as the
    # discriminating figures; f1 is a summary, not a headline.
    precision:   float = 0.0     # of the steps written, how many the solver took
    recall:      float = 0.0     # of the solver's steps, how many were written
    f1:          float = 0.0
    r1_recall:   float = 0.0
    r2_recall:   float = 0.0
    r3_recall:   float = 0.0
    r4_recall:   float = 0.0
    phase_order_ok: bool = False
    llm_symbols: List[str] = field(default_factory=list)
    gold_symbols: List[str] = field(default_factory=list)
    answer_first: bool = False
    n_rule_lines: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def score_trace(raw_output: str, gold: LearningTrace,
                background: ABAFramework,
                learnable: Optional[List[str]] = None) -> TraceScore:
    """Score one LLM answer against the symbolic execution of the same problem."""
    gold_steps = normalise_gold(gold, background)
    llm_steps, info = extract_llm_steps(raw_output, background, learnable)

    res = TraceScore(
        has_trace=info["has_trace"],
        n_steps_gold=len(gold_steps),
        n_steps_llm=len(llm_steps),
        llm_symbols=[s.symbol for s in llm_steps],
        gold_symbols=[s.symbol for s in gold_steps],
        answer_first=info["answer_first"],
        n_rule_lines=info["n_rule_lines"],
    )
    denom = max(len(gold_steps), len(llm_steps))
    res.align_exact = (_align(gold_steps, llm_steps, exact=True) / denom
                       if denom else 1.0)

    # Set-based precision/recall on (rule symbol, canonical rule). Order-free,
    # so a model that reaches the same transformations in a different order —
    # which `applyFolding`'s nondeterminism permits — is not penalised.
    gold_keys = {(s.symbol, s.key) for s in gold_steps}
    llm_keys  = {(s.symbol, s.key) for s in llm_steps}
    tp = len(gold_keys & llm_keys)
    res.precision = tp / len(llm_keys) if llm_keys else 0.0
    res.recall    = tp / len(gold_keys) if gold_keys else 0.0
    res.f1 = (2 * res.precision * res.recall / (res.precision + res.recall)
              if (res.precision + res.recall) else 0.0)

    for sym, attr in zip(SYMBOLS, ("r1_recall", "r2_recall",
                                   "r3_recall", "r4_recall")):
        g = [s for s in gold_steps if s.symbol == sym]
        if not g:
            continue
        keys = {s.key for s in llm_steps if s.symbol == sym}
        setattr(res, attr, sum(1 for s in g if s.key in keys) / len(g))

    # Gen never precedes RoLe: no R2/R3/R4 may appear before the first R1.
    first_r1 = next((i for i, s in enumerate(llm_steps)
                     if s.symbol == "R1"), None)
    later = next((i for i, s in enumerate(llm_steps)
                  if s.symbol in ("R2", "R3", "R4")), None)
    res.phase_order_ok = (later is None
                          or (first_r1 is not None and first_r1 < later))
    return res
