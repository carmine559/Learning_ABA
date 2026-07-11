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

## Prompt-version ↔ experiment-set matrix

| Experiment set | Prompts | Comparable with |
| --- | --- | --- |
| `experiments/00_preliminary_api` | v0 (evolving) | nothing (exploratory) |
| `experiments/01_bench_prompts_v1` | v1 | — |
| `experiments/02_bench_prompts_v2` | v2 | future v2 runs |
