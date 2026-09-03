"""
aba_prompts.py
Prompt construction and LLM output parsing for ABA framework learning.
"""
from __future__ import annotations
import re
from typing import Optional, List, Dict
from src.aba_types import Rule, ABAFramework, LearningProblem
from src.aba_validator import run_rote_learning


# ---------------------------------------------------------------------------
# System prompt — shared across all modes
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert in Assumption-Based Argumentation (ABA).
Terminology follows De Angelis, Proietti & Toni, "Learning Brave Assumption-
Based Argumentation Frameworks via ASP" (ECAI 2024).

KEY DEFINITIONS.
- An ABA framework is a tuple (R, A, C) where:
    R is a set of inference rules of the form  s0 :- s1, ..., sm  (m >= 0;
      if m = 0 the rule is a FACT, written  s0. );
    A is a non-empty set of ASSUMPTIONS;
    C is a total mapping assigning to each assumption a in A its CONTRARY,
      a sentence written contrary(a).
  The framework is FLAT: assumptions never occur as heads of rules.
- NORMALISED FORM. Rules are written
      p0(X0) :- eq_1, ..., eq_k, p1(X1), ..., pn(Xn)
  where each eq_i is an equality between terms. In particular a ground fact
  p(t) is represented as the normalised rule  p(X) :- X = t.
- An ARGUMENT for a claim s, supported by a set of assumptions S and a set of
  rules, is a finite proof tree: the root is labelled s; every leaf is labelled
  by an assumption in S or by true; every internal node labelled s' has as
  children exactly the body atoms of a rule in R with head s'.
- An argument A1 with claim s1 ATTACKS an argument A2 iff s1 = contrary(a) for
  some assumption a in the support of A2.
- A set Delta of arguments is a STABLE EXTENSION iff
    (i)  there are NO two arguments a, b in Delta such that a attacks b
         (Delta is conflict-free), and
    (ii) for every argument b NOT in Delta, some argument a in Delta attacks b
         (Delta attacks every argument it does not contain).
- A framework is SATISFIABLE iff it admits at least one stable extension.
- A sentence s is a BRAVE CONSEQUENCE of the framework iff s is the claim of an
  argument belonging to SOME stable extension.

THE LEARNING PROBLEM (Definition 1 of the paper).
Given: a satisfiable background framework (R, A, C); positive examples E+ and
negative examples E- (disjoint sets of ground atoms whose predicates are not
assumptions); a set T of LEARNABLE predicates, disjoint from the assumption
predicates, with every predicate of E+ and E- belonging to T.
Goal: construct a framework (R', A', C') such that
  (i)   R is a subset of R';
  (ii)  every NEW rule head uses either a learnable predicate from T or an
        entirely NEW predicate (e.g. the contrary of a new assumption);
  (iii) A is a subset of A';
  (iv)  C' agrees with C on all old assumptions;
  (v)   (R', A', C') is satisfiable and admits ONE stable extension Delta
        such that:
          1. EVERY e in E+ is the claim of an argument in Delta, and
          2. NO   e in E- is the claim of an argument in Delta.
IMPORTANT: conditions 1 and 2 refer to the SAME single extension Delta. A
negative example may still be accepted in some OTHER stable extension; that
does not violate the definition.
A solution is INTENSIONAL when the new rules R' \\ R are non-ground rule
schemata, i.e. contain no equalities "X = constant" binding variables to
specific individuals.

YOUR TASK: given an ABA Learning problem, construct a solution satisfying
Definition 1. In this task an INTENSIONAL solution is REQUIRED:
- NEVER leave ground facts  <pred>(X) :- X = <const>.  or bare facts
  <pred>(<const>).  in your final answer: they memorise the examples without
  generalising.
- Every new rule must use a variable X and at least one background predicate.
- Defeasibility: if a candidate rule makes the framework violate condition (v)
  - either a positive example is no longer accepted in the chosen extension,
  or a negative example becomes accepted in it - make a rule defeasible by
  Assumption Introduction: add an assumption alpha(X) to its body and learn an
  intensional rule for its contrary c_alpha(X). Schematically:
    <learnable>(X) :- <support>(X), alpha(X).
    c_alpha(X) :- <exception>(X).
  NEW ASSUMPTIONS:  alpha(X) defeated_by c_alpha(X)
  REUSE FIRST: if the background already declares an assumption that fits the
  same body, put THAT assumption in the body instead of inventing alpha. Its
  contrary is already fixed by the background - never redefine it (condition
  (iv)), and only write rules for it if it is in the learnable set T.

PLACEHOLDER RULE - critical:
Angle-bracketed tokens such as <pred>, <support>, <exception>, <learnable> are
PLACEHOLDERS used only to describe rule shapes. In your answer, replace each of
them with a predicate name taken from THE PROBLEM ABOVE. Your answer must
contain NO angle brackets and NO placeholder names - only predicates that occur
in the problem, plus any new assumption names (alpha, c_alpha) you introduce.

CRITICAL FORMATTING RULES - read carefully:
- Do NOT use markdown. No backticks, no code fences, no bold, no bullet symbols.
- Do NOT add any explanation or commentary outside the two sections below.
- Do NOT repeat or echo the problem statement.
- Output ONLY the two sections in this exact plain-text format:

NEW RULES:
<head> :- <body_atom_1>, <body_atom_2>.

NEW ASSUMPTIONS:
<assumption>(X) defeated_by <contrary>(X)

If no new rules or assumptions are needed, write NONE under that section."""


# ---------------------------------------------------------------------------
# Problem serialisation
# ---------------------------------------------------------------------------

def _format_problem(problem: LearningProblem) -> str:
    """Serialise the problem in the SAME notation the answer must use.

    The background used to be rendered as prose ("p(a) is always true.",
    "u(X) [defeated by: t(X)]") while every definition, transformation rule and
    the required output were in ABA/Prolog syntax. That forced the model to
    translate between three notations before it could start reasoning. One
    notation throughout: rules as `h :- b1, b2.`, assumptions as
    `a(X) defeated_by c(X)` — exactly the form required in NEW ASSUMPTIONS.
    """
    bg = problem.background
    domain = problem.get_domain()

    lines = ["=== BACKGROUND KNOWLEDGE (ABA framework) ==="]
    lines.append("% Domain: dom/1 holds for each constant below, and every")
    lines.append("% assumption is instantiated once per constant.")
    lines.append("  " + " ".join(f"dom({c})." for c in domain))
    lines.append("")
    lines.append("% Rules R")
    for r in bg.rules:
        lines.append(f"  {r.to_prolog()}")
    lines.append("")
    lines.append("% Assumptions A, with their contraries")
    if bg.assumptions:
        for asm in bg.assumptions:
            contrary = bg.contraries.get(asm, f"c_{asm}")
            lines.append(f"  {asm} defeated_by {contrary}")
    else:
        lines.append("  (none)")

    lines.append("")
    lines.append("=== POSITIVE EXAMPLES E+ "
                 "(all accepted in ONE common stable extension) ===")
    for e in problem.positive:
        lines.append(f"  + {e}")
    lines.append("")
    lines.append("=== NEGATIVE EXAMPLES E- (none accepted in that same extension) ===")
    for e in problem.negative:
        lines.append(f"  - {e}")
    lines.append("")
    lines.append("=== LEARNABLE PREDICATES T ===")
    lines.append(f"  {', '.join(problem.learnable)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mode-specific task instructions
# ---------------------------------------------------------------------------

_TASK_DIRECT = """
Find a solution directly.
Think about which claims entail the positive examples and not the negatives,
then construct rules that capture this.
"""

_TASK_COT = """
Follow these steps explicitly in your response:

STEP 1 — ROTE LEARNING:
For each positive example, determine the minimal ground facts needed to derive it.
List them as: "Add: <fact>."

STEP 2 — FOLDING (syntactic generalisation):
For each ground fact  <pred>(X) :- X = <const>  from Step 1, look for a rule or
normalised background fact whose body matches the equality (most commonly a
background fact  <support>(<const>), i.e.  <support>(X) :- X = <const>), and
REPLACE the matched sub-body by that rule's HEAD:
    <pred>(X) :- <support>(X).
List as: "Fold <fact> using <rule> -> <generalised_rule>"
CAUTION: folding preserves all existing arguments but can CREATE new arguments
and attacks — after folding, the framework may stop being a solution.

STEP 3 — SOLUTION CHECK + ASSUMPTION INTRODUCTION:
For EACH rule produced in Step 2, check BOTH directions against the single
target extension:
  (a) does some NEGATIVE example now become accepted?
  (b) does some POSITIVE example STOP being accepted? (this can happen when a
      folded contrary rule defeats an assumption that a positive relied on)
  List every violated example.

  Case A — no violation: the rule is safe. Keep it as-is.

  Case B — any violation: make the rule defeasible.
    (i)  Add an assumption alpha(X) to the rule body (new, or reuse an
         existing assumption already used with the same body):
           <learnable>(X) :- <support>(X), alpha(X).
    (ii) Find a background predicate distinguishing exactly the constants
         where the rule must be defeated.
    (iii) Write a GENERAL contrary rule using that predicate:
           c_alpha(X) :- <exception>(X).   [NOT a ground fact]
    List as: "Rule violates [list]. Introduce alpha(X) defeated_by c_alpha(X).
             Contrary rule: c_alpha(X) :- <exception>(X)."
    (<learnable>, <support>, <exception> are placeholders: use predicates from
     the problem, never the placeholder names themselves.)

STEP 3b — MULTIPLE DERIVATION PATHS (search heuristic, NOT part of the
original algorithm):
If some positive examples are still not covered, ask whether they share a
DIFFERENT background predicate usable as alternative support; if so, fold
those facts separately into a second (or third) rule for the same head, and
re-apply Step 3 to each new rule. Multiple rules for the same head are valid —
they represent alternative argument paths.
List as: "Alternative path found using <pred> -> <new_rule>"

STEP 4 — FACT SUBSUMPTION:
Delete a remaining ground fact if and only if the framework WITHOUT it still
satisfies the goal (one stable extension accepting all positives and no
negatives). The criterion is the solution check, not mere derivability.
List as: "Remove <fact> (solution preserved without it)."

After completing all steps, output the final answer in the required format.
"""

_TASK_ALGORITHM = """
Apply the ASP-ABAlearnB algorithm for brave ABA Learning (De Angelis, Proietti
& Toni, ECAI 2024) to the problem above. EXECUTE the algorithm step by step; do
not guess the final answer.

GOAL (Definition 1, restated). Extend the background framework so that the
result is satisfiable and admits ONE stable extension Delta in which EVERY
positive example is the claim of an accepted argument and NO negative example
is. A SOLUTION is checked against this single-extension condition - after
every transformation below, "still a solution" means exactly this check.
A rule is INTENSIONAL if its body contains no equality "X = constant". The
final solution must be intensional.
(All angle-bracketed tokens below are PLACEHOLDERS: substitute predicates and
constants from the problem; never write the placeholder names themselves.)

THE FOUR TRANSFORMATION RULES (as defined in the paper).

  R1 - ROTE LEARNING. Given a ground atom <pred>(<const>), add to R the
       normalised ground fact
           <pred>(X) :- X = <const>.
       Used in two places: to make positive examples derivable, and to add
       facts for the CONTRARIES of assumptions (the exceptions).

  R2 - FOLDING. A SYNTACTIC generalisation step. Given two DISTINCT rules
           rho1:  H :- Eqs1, B1, B2.        (the rule being folded)
           rho2:  K :- Eqs1, Eqs2, B1.      (the rule used for folding, in R)
       where Eqs1, Eqs2 are sets of equalities, B1, B2 are sets of atoms, and
       the variables of Eqs2 do not occur in rho1, REPLACE rho1 by
           rho3:  H :- Eqs2, K, B2.
       That is: the sub-body "Eqs1, B1" of rho1 is replaced by the HEAD K of a
       rule whose body is that same sub-body (up to the residual equalities
       Eqs2, which are carried over into the new body).
       Most common special case here: fold the learnt fact
           <pred>(X) :- X = <const>.
       using a normalised background fact  <support>(X) :- X = <const>.
       (i.e. the background contains the fact <support>(<const>)), obtaining
           <pred>(X) :- <support>(X).
       CAUTION (Proposition 1 of the paper): folding PRESERVES all existing
       arguments but may CREATE NEW arguments and new attacks. Therefore after
       folding the framework may NO LONGER BE A SOLUTION - a positive example
       may stop being accepted, a negative example may become accepted, or all
       stable extensions may disappear. ALWAYS re-check after folding.

  R3 - ASSUMPTION INTRODUCTION. Replace a rule
           rho1:  H :- Eqs, B.
       by the defeasible rule
           rho2:  H :- Eqs, B, alpha(X).
       where X are the variables of the body B, and alpha(X) is an assumption
       with contrary c_alpha(X). Applied when, after folding, the framework is
       no longer a solution - whether the failure is an ACCEPTED NEGATIVE or a
       LOST POSITIVE. There are two cases, and they behave differently:

       (a) REUSE an EXISTING assumption already used with the same body B
           (Definition 4). Try this FIRST: it keeps the framework small and it
           is what makes the algorithm terminate. Its contrary is already
           fixed by the background, so you must NOT invent or redefine it -
           you only check whether the resulting framework is a solution. If it
           is not, try another assumption or another fold.

       (b) Otherwise introduce a NEW assumption alpha(X), whose contrary
           c_alpha(X) is a NEW predicate. Only in this case do you then use R1
           to add ground facts for the contrary,
               c_alpha(X) :- X = <const>.
           for exactly those constants where the rule must be defeated so the
           framework becomes a solution again. These new ground facts are then
           themselves generalised (R2/R3/R4) in later iterations.

       (Learning rules for the contrary of an EXISTING background assumption is
       allowed only when that contrary predicate is itself in T - condition (ii)
       of Definition 1 applies to it like any other background predicate.)

  R4 - FACT SUBSUMPTION. Delete a learnt ground fact
           <pred>(X) :- X = <const>.
       if and only if the framework WITHOUT it is still a solution
       (Definition 1 still holds). The criterion is the solution check, not
       mere derivability of the fact.

THE ALGORITHM: two procedures, RoLe then Gen.

  RoLe: using R1, add a MINIMAL set of ground facts (with learnable-predicate
    heads) such that the framework becomes a - non-intensional - solution.

  Gen: iterate over every learnt ground fact rho still present:
    (a) [R4] if the framework without rho is still a solution, delete rho and
        continue with the next fact;
    (b) [R2] otherwise fold rho (repeatedly if needed) into an intensional
        rule, using rules and normalised facts of the background;
    (c) check: is the framework still a solution?
          - YES -> keep the folded rule; continue;
          - NO  -> [R3] add an assumption alpha(X) to the folded rule's body
            (new, or an existing one fitting the same body), set its contrary
            c_alpha(X), and [R1] add ground facts c_alpha(X) :- X = <const>.
            for the constants where the rule must be defeated so that the
            framework is a solution again. These c_alpha facts join the learnt
            set and are generalised by the SAME procedure in later iterations.
    Repeat until every learnt rule is intensional.

Now EXECUTE both procedures on the problem above: show the facts added by RoLe
and each transformation (R2/R3/R4) applied in Gen, re-checking the solution
condition after each step. Then output ONLY the final framework in the
required format. Every final rule must be INTENSIONAL (no "X = constant") and
must use only predicate names that appear in the problem, plus
alpha(X) / c_alpha(X) (or alpha1, alpha2, ... if several) for new assumptions
and their contraries.
"""

_TASK_GUIDED_TEMPLATE = """
I have already determined that the following ground facts must be added
(this is the output of the Rote Learning phase):

{role_facts}

Your task: generalise EACH of these ground facts into intensional rules
(rules with variables, no explicit constants) using Folding (R2) and
Assumption Introduction (R3) as defined by De Angelis, Proietti & Toni
(ECAI 2024).

For each ground fact of the form  <pred>(X) :- X = <const>
(the <...> tokens are placeholders — always substitute the actual predicate
and constant from the fact you are working on):
  1. FOLD: find a background fact <support>(<const>) (in normalised form,
     <support>(X) :- X = <const>) and replace the matched equality by its
     head, producing   <pred>(X) :- <support>(X).
     Folding preserves existing arguments but can create NEW arguments and
     attacks, so the result must be re-checked.
  2. CHECK the solution condition — ONE stable extension accepting all
     positive examples and no negative example. Check BOTH directions:
     a negative may have become accepted, or a positive may have been LOST.
       If it holds  → keep the folded rule.
       If violated  → ASSUMPTION INTRODUCTION: add an assumption to the body,
                <pred>(X) :- <support>(X), alpha(X).
                and write an INTENSIONAL contrary rule that fires exactly on
                the constants where the rule must be defeated:
                c_alpha(X) :- <exception>(X).   [must use variable X]
  3. Once all ground facts are generalised, delete any remaining learnt ground
     fact if and only if the framework without it still satisfies the solution
     condition (Fact Subsumption, R4).

REMINDER: Your final answer must contain ZERO occurrences of "X = constant",
NO angle brackets, and only predicate names that appear in the problem (plus
alpha / c_alpha for new assumptions).

Output your answer in the required format.
"""

# ---------------------------------------------------------------------------
# Public: build a prompt
# ---------------------------------------------------------------------------

def problem_to_prompt(
    problem: LearningProblem,
    mode: str = "direct",   # "direct" | "cot" | "guided" | "algorithm"
    include_system: bool = True,
    precomputed_role_facts: Optional[List[Rule]] = None,
) -> str:
    """
    Build the full prompt string for a given problem and mode.

    Modes, from least to most guidance:
      direct    — just the problem; raw zero-shot.
      cot       — step-by-step reasoning instructions.
      guided    — the problem plus the precomputed RoLe ground facts to generalise.
      algorithm — the full published ASP-ABAlearnB algorithm (RoLe + Gen, with the
                  four transformation rules R1-R4) for the LLM to EXECUTE. This is
                  the faithful "can the LLM replicate the algorithm?" test.

    For `guided` mode, pass `precomputed_role_facts` (the output of
    run_rote_learning) to avoid an expensive ASP call on every invocation.
    If not provided, RoLe is run once here as a fallback.
    """
    parts = []
    if include_system:
        parts.append(SYSTEM_PROMPT)
        parts.append("")

    parts.append(_format_problem(problem))
    parts.append("")

    if mode == "direct":
        parts.append(_TASK_DIRECT)
    elif mode == "cot":
        parts.append(_TASK_COT)
    elif mode == "algorithm":
        parts.append(_TASK_ALGORITHM)
    elif mode == "guided":
        if precomputed_role_facts is not None:
            new_facts = precomputed_role_facts
        else:
            new_facts, _success, _ = run_rote_learning(problem)
        if new_facts:
            facts_str = "\n".join(f"  {r.to_prolog()}" for r in new_facts)
        else:
            facts_str = "  (none found — background may already be sufficient)"
        parts.append(
            _TASK_GUIDED_TEMPLATE.format(role_facts=facts_str)
        )

    parts.append("\nProvide your answer below:")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Output serialisation (for SFT target)
# ---------------------------------------------------------------------------

def solution_to_output_format(
    solution: ABAFramework,
    background: ABAFramework,
) -> str:
    """
    Serialise the difference between solution and background as the
    expected LLM output format.
    """
    # Determine new rules
    bg_rule_set = set(r.to_prolog() for r in background.rules)
    new_rules = [r for r in solution.rules
                 if r.to_prolog() not in bg_rule_set]

    # Determine new assumptions
    bg_asm_set = set(background.assumptions)
    new_asms = [a for a in solution.assumptions if a not in bg_asm_set]

    lines = ["NEW RULES:"]
    if new_rules:
        for r in new_rules:
            lines.append(r.to_prolog())
    else:
        lines.append("NONE")

    lines.append("")
    lines.append("NEW ASSUMPTIONS:")
    if new_asms:
        for a in new_asms:
            contrary = solution.contraries.get(a, f"c_{a}")
            lines.append(f"{a} defeated_by {contrary}")
    else:
        lines.append("NONE")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output parser
# ---------------------------------------------------------------------------

def _clean_llm_output(text: str) -> str:
    """
    Strip markdown formatting that LLMs commonly add despite being told not to.

    Handles:
    - Fenced code blocks:  ```prolog ... ```  or  ``` ... ```
    - Inline backticks:    `some_atom(X)`
    - Trailing backslashes (Windows escape artefacts or LLM line continuations)
    - Leading/trailing whitespace on each line
    - Unicode dashes that some models use instead of ASCII hyphens
    """
    # Remove opening code fence:  ```prolog  or  ```asp  or just  ```
    text = re.sub(r'```[a-zA-Z]*\s*\n?', '', text)
    # Remove closing code fence
    text = re.sub(r'```', '', text)
    # Remove inline backtick wrappers  `atom(X)`  →  atom(X)
    text = re.sub(r'`([^`\n]+)`', r'\1', text)
    # Remove single stray backticks that survive
    text = text.replace('`', '')
    # Remove trailing backslashes (line-continuation artefacts)
    text = re.sub(r'\\\s*\n', '\n', text)
    text = re.sub(r'\\$', '', text, flags=re.MULTILINE)
    # Replace Unicode em-dash / en-dash with ASCII hyphen
    text = text.replace('\u2014', '-').replace('\u2013', '-')
    # Replace common Unicode quotes/spaces with ASCII equivalents
    text = (text.replace('\u2018', "'").replace('\u2019', "'")
                .replace('\u201c', '"').replace('\u201d', '"')
                .replace('\u00a0', ' '))
    # Drop any remaining non-ASCII bytes (mangled output) to keep Clingo safe
    text = text.encode("ascii", "ignore").decode("ascii")
    # Collapse multiple blank lines to one
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


_RULES_HDR_RE = re.compile(r'^[ \t]*NEW[ \t]+RULES[ \t]*:', re.IGNORECASE | re.MULTILINE)
_ASMS_HDR_RE  = re.compile(r'^[ \t]*NEW[ \t]+ASSUMPTIONS[ \t]*:', re.IGNORECASE | re.MULTILINE)
_ECHO_HDR_RE  = re.compile(r'^[ \t]*===[ \t]', re.MULTILINE)
_DEFEATED_RE  = re.compile(
    r'([a-zA-Z_]\w*\([^)]*\)|[a-zA-Z_]\w*)\s+defeated_by\s+'
    r'([a-zA-Z_]\w*\([^)]*\)|[a-zA-Z_]\w*)'
)


def _split_body(body: str) -> List[str]:
    """Split a rule body on TOP-LEVEL commas only.

    A naive ``body.split(',')`` tears ``p(X, Y)`` into ``p(X`` and ``Y)``.
    """
    atoms: List[str] = []
    depth = 0
    cur: List[str] = []
    for ch in body:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth = max(0, depth - 1)
        if ch == ',' and depth == 0:
            atoms.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    atoms.append(''.join(cur).strip())
    return [a for a in atoms if a]


def _iter_answer_blocks(text: str) -> List[str]:
    """Every ``NEW RULES:`` … block in the output, in order of appearance.

    Models routinely draft an answer inside their reasoning and then restate
    the final one; taking the first block scores the draft.
    """
    starts = [m.start() for m in _RULES_HDR_RE.finditer(text)]
    if not starts:
        return [text]
    bounds = starts + [len(text)]
    return [text[bounds[i]:bounds[i + 1]] for i in range(len(starts))]


def _sections_of(block: str) -> tuple:
    """(rules_text, assumptions_text) for one answer block."""
    mr = re.search(r'NEW[ \t]+RULES[ \t]*:[ \t]*\n?(.*?)'
                   r'(?=^[ \t]*NEW[ \t]+ASSUMPTIONS[ \t]*:|\Z)',
                   block, re.DOTALL | re.IGNORECASE | re.MULTILINE)
    ma = re.search(r'NEW[ \t]+ASSUMPTIONS[ \t]*:[ \t]*\n?(.*)\Z',
                   block, re.DOTALL | re.IGNORECASE)
    # No 'NEW RULES:' heading means no rules section — never fall back to the
    # whole block, or free prose would be parsed as rules.
    return (mr.group(1) if mr else ''), (ma.group(1) if ma else '')


def _iter_content_lines(section: str):
    """Yield the meaningful lines of a section, stripped of list markers."""
    for line in section.split('\n'):
        line = line.strip()
        if not line or line.upper() == 'NONE':
            continue
        yield re.sub(r'^[\-\*\d\.]+\s*', '', line)


def _looks_like_an_answer(rules: List[Rule], asms: Dict[str, str]) -> bool:
    """A block is the real answer if it names at least one concrete symbol.

    Guards against selecting an echoed copy of the prompt's format template,
    whose ``<head> :- <body_atom_1>.`` lines parse but mean nothing.
    """
    for r in rules:
        if '<' not in r.to_prolog() and re.match(r'^[a-z]\w*', r.head):
            return True
    return any('<' not in a for a in asms)


def parse_llm_output(
    text: str,
    background: ABAFramework,
    repairs: Optional[List[str]] = None,
) -> Optional[ABAFramework]:
    """
    Parse the LLM's output into an ABAFramework.
    Returns None if parsing fails entirely.

    The parser repairs three failure modes that are common enough to dominate
    the results if left alone (measured over 4 944 benchmark samples):
      * several ``NEW RULES:`` blocks, only the last of which is the answer
        (17.9% of samples) — the last usable block wins;
      * rules written under ``NEW ASSUMPTIONS:`` (46.2%) — they are routed to
        the rule list instead of being dropped;
      * the problem statement echoed after the answer (23.6%) — truncated.

    Pass a list as `repairs` to receive a note for every repair applied, so a
    sample's score can always be traced back to what the model literally wrote.
    """
    log = repairs if repairs is not None else []

    # Strip markdown and other formatting artefacts before any regex work
    text = _clean_llm_output(text)

    blocks = _iter_answer_blocks(text)
    if len(blocks) > 1:
        log.append(f"output contained {len(blocks)} 'NEW RULES:' blocks")

    best: Optional[tuple] = None
    # Later blocks first: the final restatement is the model's actual answer.
    for offset, block in enumerate(reversed(blocks)):
        echo = _ECHO_HDR_RE.search(block)
        if echo:
            block = block[:echo.start()]
        rules, asms, block_log = _parse_answer_block(block)
        if best is None:
            best = (rules, asms, block_log, offset, bool(echo))
        if _looks_like_an_answer(rules, asms):
            best = (rules, asms, block_log, offset, bool(echo))
            break

    if best is None:
        return None
    new_rules, new_asms, block_log, offset, echoed = best
    if echoed:
        log.append("truncated an echoed problem statement")
    if offset > 0:
        log.append(f"used answer block {len(blocks) - offset} of {len(blocks)}")
    log.extend(block_log)

    if not new_rules and not new_asms:
        # An answer of NONE/NONE is a legitimate claim ("the background already
        # suffices"), not a parse failure — scoring it as parse_error would
        # conflate "unreadable output" with "model said nothing is needed".
        # Only genuinely unstructured output fails to parse.
        if not (_RULES_HDR_RE.search(text) or _ASMS_HDR_RE.search(text)):
            return None
        log.append("empty answer (NONE / NONE)")

    # An assumption the background already declares is legal REUSE
    # (Definition 4), not a new assumption — but keep the contrary the model
    # wrote so that a changed contrary is still visible to the Definition-1(iv)
    # check rather than being silently repaired away.
    genuinely_new = [a for a in new_asms if a not in background.assumptions]
    reused = [a for a in new_asms if a in background.assumptions]
    if reused:
        log.append(f"re-listed existing assumption(s): {', '.join(reused)}")

    merged = background.copy()
    merged.rules = background.rules + new_rules
    merged.assumptions = background.assumptions + genuinely_new
    merged.contraries = {**background.contraries, **new_asms}
    merged.new_rules = new_rules
    merged.new_assumptions = genuinely_new
    return merged


def _parse_answer_block(block: str) -> tuple:
    """Parse one answer block into (rules, assumptions, repair_log)."""
    log: List[str] = []
    rules_text, asms_text = _sections_of(block)

    new_rules: List[Rule] = []
    for line in _iter_content_lines(rules_text):
        rule = _parse_rule_line(line)
        if rule:
            new_rules.append(rule)

    new_asms: Dict[str, str] = {}
    n_misfiled = 0
    for line in _iter_content_lines(asms_text):
        asm, contrary, remainder = _parse_assumption_line(line)
        if asm:
            new_asms[asm] = contrary
        # Whatever is left is a rule the model filed under the wrong heading.
        if remainder and ':-' in remainder:
            rule = _parse_rule_line(remainder)
            if rule:
                new_rules.append(rule)
                n_misfiled += 1
    if n_misfiled:
        log.append(f"recovered {n_misfiled} rule(s) written under "
                   f"'NEW ASSUMPTIONS:'")
    new_rules = list(dict.fromkeys(new_rules))   # Rule is hashable; keep order
    return new_rules, new_asms, log


def _parse_rule_line(line: str) -> Optional[Rule]:
    """
    Parse a line like 'pacifist(X) :- quaker(X), normal_quaker(X).'
    or 'pacifist(a).'
    """
    line = line.strip().rstrip('.').strip()
    if not line:
        return None
    if ':-' in line:
        head, body = line.split(':-', 1)
        head = head.strip()
        if not head:
            return None
        return Rule(head=head, body=_split_body(body))
    # Fact
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\(.*\))?$', line):
        return Rule(head=line, body=[])
    return None


def _parse_assumption_line(line: str) -> tuple:
    """
    Parse 'normal_quaker(X) defeated_by abnormal_quaker(X)'.

    Returns (assumption, contrary, remainder). `remainder` is whatever text
    surrounded the declaration — models often write a whole defeasible rule and
    its ``defeated_by`` clause on one line, and the rule part must not be lost.
    """
    m = _DEFEATED_RE.search(line)
    if m:
        # Keep the assumption atom in the remainder. A model writing
        #   v(X) :- t(X), u(X) defeated_by c_u(X).
        # means the rule body is 't(X), u(X)' AND u(X) is declared defeasible;
        # deleting the whole span would drop the assumption from the body.
        remainder = (line[:m.start()] + m.group(1) + line[m.end():]).strip()
        return m.group(1).strip(), m.group(2).strip(), remainder
    # Comma/arrow-separated form 'asm, contrary' — only when the line is not a
    # rule, otherwise a two-atom rule body would be read as a declaration.
    if ':-' not in line:
        m2 = re.match(
            r'([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))\s*[,→]\s*'
            r'([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))\s*$',
            line
        )
        if m2:
            return m2.group(1).strip(), m2.group(2).strip(), ""
    return None, None, line