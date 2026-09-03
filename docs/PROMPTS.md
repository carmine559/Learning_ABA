# Prompt design and version history

All prompts live in [`src/aba_prompts.py`](../src/aba_prompts.py) (single source
of truth — this document explains the design and records how the prompts evolved,
because **prompt changes split the experimental results into non-comparable
sets**, and one prompt bug turned out to be a finding in its own right).

## Design principles

1. **One system prompt, four task modes.** Every mode shares `SYSTEM_PROMPT`
   (ABA definitions, the learning goal, defeasibility requirement, output
   format) and appends a mode-specific task block.
2. **Machine-parseable output.** The model must answer with exactly two
   sections (`NEW RULES:` / `NEW ASSUMPTIONS:`); the parser
   (`parse_llm_output`) is markdown-robust but ASCII-only — hence e.g. `alpha`
   instead of `α` in the instructions.
3. **Anonymisation-aware.** Problems are anonymised by default (predicates
   `p,q,r,…`, constants `a,b,c,…`), so the instructions must not contain any
   concrete name a model could mistake for (or prefer over) a problem symbol.
   This principle was *learned the hard way* — see v2 below.

## The four modes (increasing guidance)

| Mode | Task block | What it tests |
| --- | --- | --- |
| `direct` | just "extend the background knowledge" | raw zero-shot ability |
| `cot` | step-by-step reasoning: RoLe → Folding → Assumption Introduction (+ multiple-paths check) → Subsumption | algorithm mimicry from a described recipe |
| `guided` | the precomputed **RoLe ground facts** (computed on the TRAIN split only) + instructions to generalise them | the Gen phase in isolation |
| `algorithm` | the **full ASP-ABAlearnB algorithm** (De Angelis et al. 2024): both phases and the four transformation rules R1–R4, to *execute* | can the LLM replicate the published algorithm end-to-end? |

A `fewshot` mode (two worked examples) existed early on and was removed: it
tests format imitation, not the research question.

## Version history

### v0 — exploratory (experiment set `00_preliminary_api`)

Evolving prompts during pipeline development. Notable steps, in order:

- **Defeasibility block added** to the system prompt (ban on ground facts
  `X = const`, requirement to introduce an assumption + contrary rule when a
  generalisation covers a negative) — LLMs otherwise memorise the examples.
- **CoT Step 3b (multiple derivation paths)** added for two-path problems.
- **ASCII `alpha`** replaced `α` in all instruction text: the output sanitiser
  strips non-ASCII, so a model echoing `α(X)` produced corrupt rules `(X)`.
- **`algorithm` mode introduced** (the faithful R1–R4 rendition of
  ASP-ABAlearnB), and `fewshot` removed.

### v1 — first benchmark (experiment set `01_bench_prompts_v1`)

The frozen prompt set used for the first full stratified benchmark
(Qwen2.5-7B, 103 anonymised problems). Schematic rules in the instructions
used **concrete names**, e.g.:

```text
target(X) :- background_prop(X), normal_target(X).
exception_prop(X) :- negative_feature(X).
...
p(X) :- b(X)          (algorithm mode, R2 example)
c_alpha(X) :- e(X)    (algorithm mode, R3 example)
```

### v2 — placeholder-neutralised (experiment set `02_bench_prompts_v2`, current)

Analysis of set 01 found **11.3% of guided-mode samples copied the
instructions' schema names** (`target`, `exception_prop`, …) into their answers
instead of binding to the problem's anonymised predicates — with all problem
symbols semantically empty, the only "meaningful" names available were the ones
in the instructions. A second, subtler bug: the algorithm/guided templates used
schematic letters `p`, `b`, `e`, `t` that **collide with the anonymisation
alphabets** (predicates are drawn from `p…w`, constants from `a…o`), making
instruction schema and problem symbols literally indistinguishable.

Changes (all in `src/aba_prompts.py`):

1. Every concrete schema name → **angle-bracket placeholder**
   (`<learnable>`, `<support>`, `<exception>`, `<pred>`, `<const>`), consistent
   with the output-format section which already used `<head>`/`<body_atom_1>`.
2. A **PLACEHOLDER RULE** added to the system prompt: placeholders describe rule
   *shapes*; the answer must contain no angle brackets and only predicates from
   the problem (plus new `alpha`/`c_alpha` names). If a model still copies a
   placeholder, parsing fails loudly (`parse_error`) instead of producing a
   plausible-looking wrong framework.
3. **"Do not repeat or echo the problem statement"** formatting rule (echoing
   was the second failure signature observed in set 01).
4. `alpha`/`c_alpha` intentionally stay concrete — they are *meant* to be used
   verbatim as fresh assumption names.

**Consequence for analysis:** sets 01 and 02 are not directly comparable; the
template-copy delta is itself an ablation of instruction-induced symbol leakage
under anonymisation.

#### Measured effect (v1 vs v2, same regex over raw outputs)

| Failure signature | v1 (Qwen2.5-7B) | v2 (Qwen2.5-7B) | v2 (all 4 models) |
| --- | --- | --- | --- |
| **Schema-name copying** (`target(`, `exception_prop(`, …) | **11.3%** guided; 4–6% other modes | **0.0%** | **0.0% in all 16 model×mode cells** |
| Placeholder copying (`<support>`, `learnable(`, …) | ≤1.3% (only the format section's `<head>` existed) | ≤0.6% | ≤3.6% except **Mistral-7B: 11.7% guided, 7.8% cot** |

The v1 failure is **eliminated**. Mistral-7B partially shifts the same anchoring
behaviour onto the new placeholder tokens — but, by design, placeholder mentions
are either confined to the reasoning text or rejected loudly by the parser
(angle brackets never parse into rules), instead of silently producing
plausible-looking frameworks with invented predicates as in v1.

### v3 — terminologically exact (current; supervisor feedback)

After review, the prompts were found *terminologically imprecise* with respect
to the source paper (De Angelis, Proietti & Toni, ECAI 2024). v3 rewrites the
system prompt and all task templates to state Definition 1 and the four
transformation rules **exactly as in the paper**. The corrections, each a real
divergence and not mere wording:

1. **Goal statement (Definition 1(v)).** v2 demanded "no negative example is
   bravely entailed" — *stronger than the paper*. Correct: there exists **one
   single stable extension Δ** in which all of E+ are accepted and none of E−
   is; a negative may still be accepted in *other* extensions. (The Clingo
   validator always implemented the correct condition — only the prompt prose
   was wrong.)
2. **Folding (R2) restated syntactically.** v2 said "find a background
   predicate that *holds* for the constant" — a semantic paraphrase of a
   *syntactic* rule. v3 gives the paper's schema: distinct rules
   `rho1: H :- Eqs1, B1, B2` and `rho2: K :- Eqs1, Eqs2, B1` (fresh `Eqs2`
   variables), replace `rho1` by `rho3: H :- Eqs2, K, B2`; plus the special
   case actually used (folding with a normalised background fact), plus the
   Proposition-1 caveat: folding preserves existing arguments but may CREATE
   arguments/attacks — the framework can stop being a solution.
3. **Assumption Introduction (R3) trigger widened.** v2 triggered R3 only when
   "a negative gets through". The paper applies R3 whenever the framework is
   **no longer a solution — including a LOST POSITIVE** (its own running
   example introduces α to *recover* `pacifist(a)`). v3 also restores:
   α new **or existing** (reuse, Definition 4), `X = vars(B)`, and the
   `c_α` exceptions added via **R1 and generalised recursively** in later Gen
   iterations.
4. **Fact Subsumption (R4) criterion.** v2's CoT said "remove facts already
   derivable" — wrong criterion. Correct: remove a learnt fact iff the
   framework **without it is still a solution**.
5. **Conflict-freeness restored.** A pasted PDF fragment had lost the `∄`
   glyph, literally inverting the stable-extension definition ("there exist
   α,β…" instead of "there do NOT exist"). v3 states it in words.
6. **CoT Step 3b explicitly labelled** a search heuristic *outside* the
   original algorithm (it was previously presented as part of it).

Also made exact: flatness, normalised rule form (`p(t)` as `p(X) :- X = t`),
brave consequence, and "intensional" per the paper (non-ground rule schemata).
The problem-serialisation headers now read "all accepted in ONE common stable
extension" / "none accepted in that same extension".

### v4 — one notation (current)

v3 fixed the *terminology* but left a structural problem: the problem itself was
still serialised as English prose by `ABAFramework.to_natural_language()` —

```text
Rules:
  - p(a) is always true.
  - t(X) holds if q(X).
Assumptions (defeasible by default):
  - u(X)  [defeated by: t(X)]
```

— while every definition in the system prompt, all four transformation rules and
the required output format were in ABA/Prolog syntax, and contraries appeared in
a *third* notation (`defeated_by`) in the answer format. The model had to
translate between three notations before it could begin reasoning.

Changes, all in `_format_problem`:

1. Rules are printed as rules (`h :- b1, b2.`, `p(a).`), exactly as they must be
   written back.
2. Assumptions and their contraries are printed as
   `u(X) defeated_by t(X)` — the same line the answer must produce for a new
   assumption. One notation end to end.
3. The domain is stated as `dom(a). dom(b). …` with an explicit note that
   assumptions are instantiated once per constant — previously the model was
   shown a bare list of constants and never told what `dom` meant, although
   `dom` appears in background rule bodies.
4. Section headers name the formal objects: `E+`, `E-`, `T`.

Also in v4, R3 in `algorithm` mode is split into its two cases, matching
Algorithm 1 lines 36–44: **(a)** reusing an existing assumption, whose contrary
is fixed and must not be redefined (and rules for it are legal only if that
contrary is itself in `T`), and **(b)** introducing a new assumption, the only
case in which contrary facts are rote-learned. v3 described only case (b) while
every benchmark tier's intended solution is case (a). The system prompt gained a
matching `REUSE FIRST` line.

`to_natural_language()` is retained, but only for reports
(`explanations.md`, `frameworks.md`).

## Prompt-version ↔ experiment-set matrix

| Experiment set | Prompts | Metrics | Comparable with |
| --- | --- | --- | --- |
| `experiments/00_preliminary_api` | v0 (evolving) | rev 1 | nothing (exploratory) |
| `experiments/01_bench_prompts_v1` | v1 | rev 2 | — |
| `experiments/02_bench_prompts_v2` | v2 | rev 2 | — |
| `experiments/03_bench_prompts_v3` | v3 | rev 4 | — |
| *(next benchmark run)* | **v4** | rev 4 | future v4 runs |

A prompt change and a metric change are independent axes: a metric change can be
applied retroactively with `rescore.py`, a prompt change cannot.
