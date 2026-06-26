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

KEY DEFINITIONS:
- An ABA framework has: (1) inference rules of the form "head :- body", \
(2) defeasible assumptions, (3) a mapping from each assumption to its contrary.
- An argument for claim s is a proof tree: root=s, leaves=assumptions or facts, \
  internal nodes derived by rules.
- An argument A attacks B if A's claim is the contrary of an assumption in B's support.
- A stable extension Δ is a conflict-free set of arguments that attacks \
  every argument outside it.
- Brave entailment: s is bravely entailed if some argument for s is in \
  some stable extension.

YOUR TASK: Extend a background ABA framework so that:
  (1) All positive examples are bravely entailed.
  (2) No negative example is bravely entailed.
  (3) New rule heads use only predicates listed as learnable.

DEFEASIBILITY REQUIREMENT — this is the hardest and most important part:
- NEVER output ground facts such as  p(X) :- X = t.  or bare facts  p(t).
  Ground facts only memorise training examples; they do not generalise.
- Every new rule MUST use a variable X and at least one background predicate.
- If a generalised rule would also derive a NEGATIVE example, you MUST make
  it defeasible: add a new assumption alpha(X) to its body, then add a contrary
  rule  c_alpha(X) :- <background_predicate_distinguishing_exceptions>(X).
  The contrary rule must also use a variable — not a ground fact.
- A defeasible solution looks like:
    target(X) :- background_prop(X), normal_target(X).
    exception_prop(X) :- negative_feature(X).   [contrary rule]
  NEW ASSUMPTIONS:  normal_target(X) defeated_by exception_prop(X)

CRITICAL FORMATTING RULES — read carefully:
- Do NOT use markdown. No backticks, no code fences, no bold, no bullet symbols.
- Do NOT add any explanation or commentary outside the two sections below.
- Output ONLY the two sections in this exact plain-text format:

NEW RULES:
<head> :- <body_atom_1>, <body_atom_2>.
(or simply <head>. for a ground fact)

NEW ASSUMPTIONS:
<assumption(X)> defeated_by <contrary(X)>

If no new rules or assumptions are needed, write NONE under that section."""


# ---------------------------------------------------------------------------
# Problem serialisation
# ---------------------------------------------------------------------------

def _format_problem(problem: LearningProblem) -> str:
    lines = ["=== BACKGROUND KNOWLEDGE ==="]
    lines.append(problem.background.to_natural_language())
    lines.append("")
    lines.append("=== POSITIVE EXAMPLES (must be bravely entailed) ===")
    for e in problem.positive:
        lines.append(f"  + {e}")
    lines.append("")
    lines.append("=== NEGATIVE EXAMPLES (must NOT be bravely entailed) ===")
    for e in problem.negative:
        lines.append(f"  - {e}")
    lines.append("")
    lines.append(f"=== LEARNABLE PREDICATES ===")
    lines.append(f"  {', '.join(problem.learnable)}")
    lines.append(f"=== DOMAIN (known constants) ===")
    lines.append(f"  {', '.join(problem.get_domain())}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Mode-specific task instructions
# ---------------------------------------------------------------------------

_TASK_DIRECT = """
Extend the background knowledge directly.
Think about which constants satisfy the positive examples and not the negatives,
then construct rules that capture this.
"""

_TASK_COT = """
Follow these steps explicitly in your response:

STEP 1 — ROTE LEARNING:
For each positive example, determine the minimal ground facts needed to derive it.
Also determine ground facts needed to block each negative example.
List them as: "Add: <fact>."

STEP 2 — FOLDING:
For each ground fact from Step 1, check if a rule in the background has a head
that matches after substituting the constant. If yes, replace the constant-binding
equality with that rule's head.
List as: "Fold <fact> using <rule> → <generalised_rule>"

STEP 3 — ASSUMPTION INTRODUCTION (overgeneralisation check):
For EACH rule produced in Step 2, explicitly check:
  "If I apply this rule to every domain constant, does it derive any NEGATIVE example?"
  List the negatives it would incorrectly derive (if any).

  Case A — no negative derived: the rule is safe. Keep it as-is.

  Case B — some negatives derived: the rule overgeneralises.
    (i)  Add a new defeasible assumption alpha(X) to the rule body:
           target(X) :- background_prop(X), alpha(X).
    (ii) Find a background predicate that distinguishes the exceptions
         (the constants where the negative result should be blocked).
    (iii) Write a GENERAL contrary rule using that predicate:
           c_alpha(X) :- exception_predicate(X).   [NOT a ground fact]
    List as: "Rule overgeneralises for [list]. Introduce alpha(X) defeated_by c_alpha(X).
             Contrary rule: c_alpha(X) :- <exception_predicate>(X)."

STEP 3b — MULTIPLE DERIVATION PATHS:
After Step 3, look at the remaining positive examples that are NOT yet covered
by the rules produced so far.  Ask: "Do any of these positives share a DIFFERENT
background predicate that could serve as an alternative support?"

  If YES: fold those facts separately using that background predicate to produce
           a second (or third) rule for the same target predicate.  Each new rule
           may also need its own assumption if it overgeneralises (repeat Step 3).
  If NO:  skip this step.

Multiple rules for the same head are valid and desirable — they represent
alternative argument paths. A constant reachable via two independent rules
receives stronger graded support than one reachable via only one.
List as: "Alternative path found using <pred> → <new_rule>"

STEP 4 — FACT SUBSUMPTION:
Check if any added ground fact is now redundant (already derivable without it).
Remove redundant facts.
List as: "Remove <fact> (redundant)."

After completing all steps, output the final answer in the required format.
"""

_TASK_ALGORITHM = """
Apply the ASP-ABAlearnB algorithm for brave ABA Learning (De Angelis, Proietti
& Toni, ECAI 2024) to the problem above. EXECUTE the algorithm step by step; do
not guess the final answer.

GOAL. Build a set of rules R' extending the background rules R so that:
  * every POSITIVE example is bravely entailed (it is the claim of an argument
    accepted in some stable extension), and
  * no NEGATIVE example is bravely entailed.
New rule heads must be learnable predicates (or the contrary of a new assumption).
A rule is written  head :- body.  A ground fact p(t) is written  p(X) :- X = t.
A rule is INTENSIONAL if its body contains no equality "X = constant"; intensional
rules are the goal, because they generalise beyond the listed constants.

THE FOUR TRANSFORMATION RULES.
  R1 - Rote Learning. To force an atom p(t) to hold, add the ground fact
       p(X) :- X = t.  (Used both for positive examples and for the contraries
       of assumptions.)
  R2 - Folding (generalisation). Given a ground fact  p(X) :- X = t,  find a
       background atom b(X) that holds for t (i.e. b(t) is derivable) and replace
       the equality with it:   p(X) :- b(X).   More generally, replace a set of
       body atoms by the head of a background rule whose body those atoms match.
  R3 - Assumption Introduction (defeasibility). If a rule  H :- B  is too general
       and lets a NEGATIVE example through, add a fresh assumption to its body to
       make it defeasible:
            H :- B, alpha(X).      with contrary  c_alpha(X)
       Then, by R1+R2, learn an INTENSIONAL rule for the contrary that fires
       exactly on the exceptions to be blocked:   c_alpha(X) :- e(X).
  R4 - Fact Subsumption. Delete any ground fact  p(X) :- X = t  if E+ and E- are
       still correctly entailed without it.

THE ALGORITHM (two phases).
  PHASE 1 - RoLe (Rote Learning): using R1, add the MINIMAL set of ground facts
    that makes every E+ entailed and every E- blocked. This is a correct but
    non-general (memorised) solution.
  PHASE 2 - Gen (Generalisation): turn each learnt ground fact into an
    intensional rule. For each learnt fact  p(X) :- X = t:
      (a) [R4] If the fact can be dropped with E+/E- still correct, drop it.
      (b) [R2] Otherwise fold it into  p(X) :- b(X)  using a background predicate
          b that holds for t.
      (c) Check the folded rule against ALL constants: does it now derive any
          negative example?
            - No  -> keep the intensional rule.
            - Yes -> [R3] add an assumption:  p(X) :- b(X), alpha(X);  then learn
              an intensional contrary rule  c_alpha(X) :- e(X)  using a background
              predicate e that holds exactly on the constants to block (fold that
              contrary rule too, recursively).
      (d) Repeat until the rule is intensional.

Now EXECUTE both phases on the problem above: show the facts added in RoLe and
each transformation (R2/R3/R4) applied in Gen. Then output ONLY the final
framework in the required format. Every final rule must be INTENSIONAL (no
"X = constant") and use only the predicates listed above. Use ASCII names such as
alpha(X) and c_alpha(X) for any new assumptions and their contraries.
"""

_TASK_GUIDED_TEMPLATE = """
I have already determined that the following ground facts must be added
(this is the output of the Rote Learning phase):

{role_facts}

Your task: generalise EACH of these ground facts into intensional rules
(rules with variables, no explicit constants) using Folding and
Assumption Introduction.

For each ground fact p(X) :- X = t:
  1. Find a background predicate B such that B(t) holds.
  2. Replace "X = t" with "B(X)" to produce the folded rule  p(X) :- B(X).
  3. Check: does  p(X) :- B(X)  derive any NEGATIVE example?
       If NO  → keep the rule as-is.
       If YES → add a defeasible assumption:  p(X) :- B(X), alpha(X).
                Find a background predicate E that holds for the exceptions.
                Write the contrary rule:  c_alpha(X) :- E(X).   [must use variable X]
  4. Once all ground facts are generalised, remove any that are now redundant
     (already covered by the intensional rules).

REMINDER: Your final answer must contain ZERO occurrences of "X = <constant>".
If any rule still has "X = t" after folding, you have not generalised enough.

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


def parse_llm_output(
    text: str,
    background: ABAFramework,
) -> Optional[ABAFramework]:
    """
    Parse the LLM's output into an ABAFramework.
    Returns None if parsing fails entirely.
    """
    # Strip markdown and other formatting artefacts before any regex work
    text = _clean_llm_output(text)

    # --- Extract NEW RULES section ---
    rules_match = re.search(
        r'NEW RULES:\s*\n(.*?)(?=\nNEW ASSUMPTIONS:|\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    new_rules: List[Rule] = []
    if rules_match:
        rules_text = rules_match.group(1).strip()
        if rules_text.upper() != 'NONE':
            for line in rules_text.split('\n'):
                line = line.strip()
                if not line or line.upper() == 'NONE':
                    continue
                # Remove leading bullet/dash/number
                line = re.sub(r'^[\-\*\d\.]+\s*', '', line)
                rule = _parse_rule_line(line)
                if rule:
                    new_rules.append(rule)

    # --- Extract NEW ASSUMPTIONS section ---
    asms_match = re.search(
        r'NEW ASSUMPTIONS:\s*\n(.*?)(?=\Z)',
        text, re.DOTALL | re.IGNORECASE
    )
    new_asms: Dict[str, str] = {}
    if asms_match:
        asms_text = asms_match.group(1).strip()
        if asms_text.upper() != 'NONE':
            for line in asms_text.split('\n'):
                line = line.strip()
                if not line or line.upper() == 'NONE':
                    continue
                line = re.sub(r'^[\-\*\d\.]+\s*', '', line)
                asm, contrary = _parse_assumption_line(line)
                if asm:
                    new_asms[asm] = contrary

    if not new_rules and not new_asms:
        return None

    # Merge with background
    merged = background.copy()
    merged.rules = background.rules + new_rules
    merged.assumptions = background.assumptions + list(new_asms.keys())
    merged.contraries = {**background.contraries, **new_asms}
    merged.new_rules = new_rules
    merged.new_assumptions = list(new_asms.keys())
    return merged


def _parse_rule_line(line: str) -> Optional[Rule]:
    """
    Parse a line like 'pacifist(X) :- quaker(X), normal_quaker(X).'
    or 'pacifist(a).'
    """
    line = line.rstrip('.')
    if not line:
        return None
    if ':-' in line:
        head, body = line.split(':-', 1)
        body_atoms = [b.strip() for b in body.split(',') if b.strip()]
        return Rule(head=head.strip(), body=body_atoms)
    # Fact
    if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*(\(.*\))?$', line.strip()):
        return Rule(head=line.strip(), body=[])
    return None


def _parse_assumption_line(line: str) -> tuple:
    """
    Parse 'normal_quaker(X) defeated_by abnormal_quaker(X)'
    Returns (assumption, contrary) or (None, None) on failure.
    """
    # Format: asm defeated_by contrary
    m = re.match(
        r'([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))\s+defeated_by\s+'
        r'([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))',
        line
    )
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # Also try comma-separated format: asm, contrary
    m2 = re.match(
        r'([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))\s*[,→]\s*'
        r'([a-zA-Z_][a-zA-Z0-9_]*\([^)]*\))',
        line
    )
    if m2:
        return m2.group(1).strip(), m2.group(2).strip()
    return None, None