# Set 07 — End-to-end modes v4, problems posed whole, five models at 4-bit

Each model is asked for a whole answer (the new rules and assumptions) to each benchmark
problem, in four prompting modes. The answer is scored against the algorithm's run on the
same problem. This set repeats set 05's end-to-end design with every problem posed whole:
every example is in the prompt and in the scoring, as Definition 1 poses it. The instrument,
the floors and the reading were fixed before the run
([METHOD_HISTORY.md](../../docs/METHOD_HISTORY.md), Phases 13 and 14). The outcome, and two
defects of the scorer found after the run, are in Phase 15.

| Field | Value |
| --- | --- |
| Date | 2026-10-28 (generation), 2026-10-29 (analysis) |
| Models | Qwen2.5 3B / 7B / 14B / 32B and Mistral-7B, all `--load-4bit`; each model's revision is in its `summary.json` |
| Backend | `local` (L40, DISI cluster), jobs 73997–74001 |
| Code | `80ad57f` (3B, 7B) and `1eec742-dirty` (Mistral, 14B, 32B): the same code, see Provenance |
| Dataset | 103 problems, 5 tiers, anonymised, `--benchmark 20`, seed 42 (as sets 05 and 06) |
| Modes | `direct cot guided algorithm`, 309 rows each (`--n-samples 3`) |
| Decoding | temperature 0.7, top-p 0.95, `--max-tokens 1536`; each sample's seed derived from `--sampling-seed 0` |
| **Mode-prompt version** | **v4**, as set 05; each mode's prompt hash is in `summary.json` |
| Scorer | `src.aba_score.score_output`, step audit off, with Phases 12 and 14 |
| Reference | after METHOD_HISTORY Phase 8; `references.jsonl` in each model's folder |
| Status | done; 20 rows per model read by hand before any aggregate |

## Command

```bash
OUT_ROOT=results/e2e_whole_v4 \
    MODELS="qwen2.5-3b qwen2.5-7b mistral-7b qwen2.5-14b qwen2.5-32b" \
    EXTRA="--load-4bit" bash cluster/submit_benchmarks.sh
```

Each job ran `python main.py --backend local --model <model> --benchmark 20 --modes direct
cot guided algorithm --n-samples 3 --max-tokens 1536 --export --output
results/e2e_whole_v4/bench_<model> --load-4bit`, as its `run` block records. The outputs were
then moved here.

- **Generation time:** 19.8 h over the five models, summed from the rows'
  `llm_latency_s`: 3B 0.6 h, 7B 4.1 h, Mistral 5.7 h, 14B 7.0 h, 32B 2.4 h.
- **Logs:** `logs/` holds the SLURM logs.
- **Smoke jobs:** two ran first (73982–73983: 3B, `--benchmark 1`, k = 2). Reading their
  rows by hand found the hole that Phase 14 closed. They are in the history at `097ffb3` and
  were removed in `de1822b`.

## What changed since set 05

1. **Problems are posed whole.** Set 05 hid 30% of each problem's examples and scored the
   answers on them. Here the prompt shows every example and the scoring uses every example
   (Phase 13).
2. **One scorer.** The answers are scored by the fine-tuning scorer:
   - valid and clean (Definition 1 on the posed examples);
   - exact (the algorithm's answer, up to assumption names and body order);
   - agreement off the examples, R2 bodies and R3.

   The step audit is off: it misfires on free prose.
3. **Grammar and side conditions.** The rule grammar of Phase 12, and Phase 14's check that
   no learnable predicate is an assumption.
4. **A run record.** Samples are seeded, and the `run` block of `summary.json` records the
   prompt hashes, the code, model and package versions, the decoding, the dataset and the
   references' hash. `rescore.py` rebuilds the run from it.
5. **Floors and reading registered first.** The floors were measured and the reading
   registered before the run (Phase 13).

## Results against the no-reasoning floors

`python analysis/null_baselines.py --end-to-end --set experiments/07_e2e_whole_v4`. A cell is
*above* iff its 95% Wilson lower bound exceeds the floor (Phase 13, rule 1). The floors are:

- clean@k: **0.777**, the positional rule;
- exact@k: **0.388**, one answer for all.

A 0/103 cell has the interval [0.00, 0.04].

clean@k (floor 0.777):

| model | direct | cot | guided | algorithm |
| --- | --- | --- | --- | --- |
| Qwen2.5-3B | 0 | 0 | 0 | 0 |
| Qwen2.5-7B | 0.252 [0.18, 0.34] | 0.155 [0.10, 0.24] | 0.029 [0.01, 0.08] | 0.068 [0.03, 0.13] † |
| Mistral-7B | 0.175 [0.11, 0.26] | 0.058 [0.03, 0.12] | 0.039 [0.01, 0.10] | 0.019 [0.01, 0.07] † |
| Qwen2.5-14B | 0.641 [0.55, 0.73] | 0.330 [0.25, 0.43] | 0.204 [0.14, 0.29] | 0.136 [0.08, 0.21] |
| Qwen2.5-32B | 0.757 [0.67, 0.83] | 0.680 [0.58, 0.76] | 0.650 [0.55, 0.74] | 0.631 [0.54, 0.72] |

exact@k (floor 0.388):

| model | direct | cot | guided | algorithm |
| --- | --- | --- | --- | --- |
| Qwen2.5-3B | 0 | 0 | 0 | 0 |
| Qwen2.5-7B | 0 | 0 | 0 | 0.010 [0.00, 0.05] † |
| Mistral-7B | 0 | 0 | 0 | 0 † |
| Qwen2.5-14B | 0 | 0.136 [0.08, 0.21] | 0.155 [0.10, 0.24] ‡ | 0.068 [0.03, 0.13] |
| Qwen2.5-32B | 0 | 0.058 [0.03, 0.12] | 0.019 [0.01, 0.07] | 0 |

† **Token cap:** more than 10% of the cell's samples reached it (7B 46 of 309, Mistral 68),
so the cell is a lower bound (rule 3). No other cell has more than 14 (3B algorithm).

‡ **Credited by ill-formed answers:** three of these 16 problems are credited only by an
ill-formed answer that is not a solution (caveat 1). With exact requiring clean, the cell is
13/103 = 0.126 [0.07, 0.20].

**No model × mode cell is above its floor, on either primary metric** (rule 10). Without t5
(83 problems; floors 0.964 and 0.482), the same holds. The highest cells are then:

- 32B direct clean@k, 0.807 [0.71, 0.88];
- 14B guided exact@k, 0.193 [0.12, 0.29], or 0.157 with exact requiring clean.

The secondary metrics show nothing either (rule 2):

- **valid@1:** at most 0.515 (32B direct), against RoLe's facts' 1.000.
- **agreement:** at most 0.517 (32B direct), against the positional rule's 1.000.
- **R3 balanced:** between 0.340 (Mistral guided) and 0.592 (14B guided), against 0.500.
  14B guided gets its figure by writing monotonic answers: 141 of its 249 answers to
  problems whose algorithm answer is defeasible are monotonic.

Per tier (`by_tier` in each `summary.json`), clean@k / exact@k for the two models with
clean answers in number. The 3 built-in problems are left out: 14B guided is exact on one,
and 32B cot clean on one.

| model | mode | t1 | t2 | t3 | t4 | t5 |
| --- | --- | --- | --- | --- | --- | --- |
| 14B | direct | 0.60 / 0 | 0.85 / 0 | 0.55 / 0 | 0.85 / 0 | 0.45 / 0 |
| 14B | cot | 0.75 / 0.15 | 0.25 / 0.20 | 0.60 / 0.30 | 0.05 / 0.05 | 0.05 / 0 |
| 14B | guided | 0.95 / 0.60 | 0 / 0 | 0.05 / 0.15 ‡ | 0 / 0 | 0 / 0 |
| 14B | algorithm | 0.50 / 0.35 | 0 / 0 | 0.15 / 0 | 0 / 0 | 0.05 / 0 |
| 32B | direct | 0.70 / 0 | 0.95 / 0 | 0.95 / 0 | 0.75 / 0 | 0.55 / 0 |
| 32B | cot | 0.45 / 0 | 0.85 / 0.10 | 0.85 / 0 | 0.90 / 0.20 | 0.40 / 0 |
| 32B | guided | 0.45 / 0 | 0.70 / 0.05 | 0.95 / 0 | 0.35 / 0.05 | 0.90 / 0 |
| 32B | algorithm | 0.25 / 0 | 0.85 / 0 | 0.75 / 0 | 0.40 / 0 | 1.00 / 0 |

## Checks

1. **Hand-reading** (rule 4). 20 rows per model from `sample.md` were read beside the posed
   problem and the algorithm's answer, before any aggregate. Every verdict follows from what
   the parser read. In one row the parser reads too much (caveat 2): 14B algorithm,
   `t1_mono_0013` #0.
2. **Rescoring.** `rescore.py` at `9a076dc` reproduces every row and every summary field of
   all five runs.
3. **Seeds.** Every sample's seed matches its derivation.
4. **Phase 14's check** changes one cell only: 3B guided, whose clean@k would be 0.20
   without it.
5. **The echo detector** misses a bare `===` line. Such a line occurs in 2 answers (7B) and
   changes no valid, clean or exact value in any run.

## Provenance

- **The code.** 3B and 7B recorded `80ad57f`; Mistral, 14B and 32B recorded
  `1eec742-dirty`.
  - `1eec742` adds only result files to `80ad57f`: 7B's partial rows, committed at 18:21
    while job 73998 was still appending to them.
  - A tracked file that differs from the revision marks the tree dirty, so the later jobs
    read `-dirty`.
  - All five runs record the same prompt hashes, references' hash, decoding and package
    versions, and the rescore at `9a076dc` reproduces each of them exactly.
- **4-bit kernels are not bitwise deterministic:** the seed fixes the draw, not the output.

## What the answers show

Clean answers (samples) by the learnt rules' bodies:

- *plain*: no assumption in any body;
- *reuses*: a background assumption in some body, and no new one;
- *mints*: a new assumption in some body.

In brackets, how many are exact.

| model | mode | t1 plain | t1 reuses | t1 mints | t2–t4 reuses | t2–t4 mints | t5 reuses |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 14B | direct | 1 | 18 | 1 | 88 | 0 | 16 |
| 14B | cot | 7 (3) | 14 | 5 | 3 | 19 (14) | 1 |
| 14B | guided | 32 (18) | 0 | 3 | 0 | 1 | 0 |
| 14B | algorithm | 11 (7) | 2 | 2 | 3 | 1 | 1 |
| 32B | direct | 0 | 21 | 0 | 121 | 0 | 16 |
| 32B | cot | 0 | 6 | 6 | 62 | 28 (6) | 10 |
| 32B | guided | 0 | 10 | 1 | 82 | 4 (2) | 34 |
| 32B | algorithm | 0 | 6 | 0 | 67 | 0 | 40 |

One clean plain answer on t2–t4 (14B cot) is not shown; no clean answer mints on t5.

- **32B writes the positional rule's shape.**
  - 332 of its 364 clean answers on t2–t4 reuse the background assumption, as in
    `v(X) :- p(X), u(X).` with the background's `u(X) defeated_by t(X)`.
  - That answer is clean but never the algorithm's. Here no assumption is relative to the
    body (Definition 4), so line 41 introduces a new one.
  - It never writes the plain fold on t1, where that is the algorithm's answer. On the 60
    samples of the 20 t1 problems, its answer guards a rule with an assumption on 60, 60,
    60 and 59 (direct, cot, guided, algorithm; the R3 confusion in `summary.json`).
  - Set 06 measured the same habit at lines 36 and 41: 32B "reuses a background assumption
    that is not relative where line 41 introduces one".
- **Why 14B outranks 32B on exact@k** in cot, guided and algorithm modes (rule 5). This is
  the mechanism:
  - 14B writes the plain fold on t1 in guided and algorithm modes (18 and 7 exact samples);
  - in cot, it introduces a new assumption with the algorithm's contrary on t2–t4 (14
    exact);
  - 32B does neither.

  The same mechanism gives 14B the higher R3 balanced (0.54–0.59 against 0.48–0.50): 32B's
  answers are defeasible on 301–309 of the 309 samples per mode, whatever the problem.
- **A further fold.** When 32B introduces an assumption (cot), its commonest non-exact
  answer folds the contrary one step past the algorithm's:
  - `c_alpha(X) :- v(X)` on t3 (10 samples), where the background has `v(X) :- q(X)`;
  - `c_alpha(X) :- t(X)` on t2 and t4 (6), where it has `t(X) :- q(X)`.

  14B writes the first on 5 samples. The algorithm folds the contrary's fact once, to
  `c_alpha(X) :- q(X)`. These answers mean the same and are clean, but exact does not
  credit them (caveat 3).
- **Algorithm mode does not run the algorithm.** Its prompt asks for the steps, then the
  final answer. The table counts the answers that come first: the output's first non-blank
  line is the `NEW RULES:` heading.

  | model | direct | cot | guided | algorithm |
  | --- | --- | --- | --- | --- |
  | 3B | 309 | 309 | 216 | 307 |
  | 7B | 309 | 309 | 309 | 309 |
  | Mistral | 308 | 309 | 309 | 309 |
  | 14B | 309 | 199 | 309 | 264 |
  | 32B | 309 | 21 | 309 | 309 |

  - 32B's median algorithm answer is 41 tokens: the answer alone.
  - In algorithm mode, where steps are written, they mostly follow the answer. `trace_f1`
    averages over the answers that contain a trace: 31 of 32B's 309 algorithm answers, and
    293 of 14B's.
  - Only cot gets 32B to reason before answering (288 of 309).
- **The more procedural the prompt, the fewer clean answers.** For 14B and 32B, clean@k
  falls from direct to cot to guided to algorithm.

## Caveats

1. **Exact credits a name that is not fresh.** `same_answer` renames every assumption an
   answer declares new as if its name were fresh.
   - Three 14B guided answers on t3 declare `v(X) defeated_by c_v(X)` and otherwise match
     the algorithm's answer. But `v` is a background predicate (`v(X) :- q(X)`).
   - They score exact, although they are ill-formed and not solutions.
   - They are the only such rows in this set. No fine-tuning row and no floor policy has
     one.
   - With exact requiring clean, 14B guided is 13/103 (0.126 [0.07, 0.20]); no verdict
     changes.
2. **The parser reads past the answer.** Rules written under `NEW ASSUMPTIONS:` are
   recovered from that heading to the end of the block, so a rule quoted in an explanation
   after the answer joins the answer.
   - In 14B algorithm `t1_mono_0013` #0, the RoLe facts quoted in the explanation made a
     non-solution "valid but degenerate".
   - Ending the section at its first line of prose changes these cells:
     - 14B, which moves the most: algorithm clean@k 14 → 20 and guided exact@k 16 → 19;
     - Mistral, by at most one problem;
     - 32B, by one problem (algorithm clean@k);
     - 3B and 7B, not at all.
   - No verdict changes.
3. **Exact credits one run of a nondeterministic algorithm.** The paper (p. 3450) leaves
   these choices open:
   - the order of the learnt facts: Gen "considers any non-intensional rule ρ ∈ Rl";
   - `applyFolding`: "We do not provide a concrete definition of the function
     applyFolding";
   - line 36: "the choice of the assumption α(X) ∈ A at line 36 is nondeterministic";
   - which optimal answer set `getAS` returns at lines 8 and 44.

   The reference fixes one resolution of each, so another run of Algorithm 1 may return an
   answer that exact does not credit. The further-fold answers above are one instance if
   `applyFolding` may fold an intensional rule again. The positional rule is not one: line
   36 reuses only an assumption relative to the body.
4. **The intervals treat problems as independent.** They are not: t2–t4 have one answer
   string each, and t5's 20 problems one structure (rule 7).
5. **@k favours the model** (rule 8). Each floor is one deterministic answer per problem,
   against the model's k = 3 samples.
6. **4-bit for every model.** The set is comparable within itself, not with bf16 runs, and
   with no earlier end-to-end set (rule 9).
