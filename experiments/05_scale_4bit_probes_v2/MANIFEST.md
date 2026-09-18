# Set 05 — Scale series at 4-bit, probe prompts v2 + end-to-end modes v3

One run per model covering **both** halves of the evaluation on a single load of
the weights: the four end-to-end modes (mode prompts **v3**, as in set 03) and
the five step probes (probe prompts **v2**, superseding set 04's v1).

| Field | Value |
| --- | --- |
| Date | 2026-09-15 (generation), 2026-09-16 (analysis) |
| Models | Qwen2.5 **3B / 7B / 14B / 32B** + **Mistral-7B**, all `--load-4bit` |
| Backend | `local` (L40, DISI cluster) |
| Dataset | 103 problems, 5 tiers, anonymised, `--benchmark 20`, seed 42 |
| Modes | `direct cot guided algorithm`, 309 rows each (`--n-samples 3`, `--max-tokens 1536`) |
| Probes | 780 per model (`--probes-per-kind 2`, k=1, `temperature=0.0`, `--max-tokens 512`) |
| **Probe-prompt version** | **v2** (stamped in every `probe_summary.json`) |
| Mode-prompt version | **v3** (byte-identical to set 03) |
| Status | done; **three instrument defects found after scoring** — see below |

Quantisation is constant across all five models, so they are comparable with each
other. They are **not** comparable with the bf16 rows of set 03.

## Command

```bash
PROBES=both MODELS="qwen2.5-3b qwen2.5-7b qwen2.5-14b qwen2.5-32b mistral-7b" \
    EXTRA="--load-4bit" bash cluster/submit_benchmarks.sh
```

`PROBES=both` appends the probes to the same process as the modes
(`--with-probes`, `main.py:996-1003`), so 32B's weights load once instead of
twice. `run_probe_experiment` sets `temperature=0.0` and caps probe answers at
`min(--max-tokens, 512)` explicitly, so the modes run cannot leak sampling state
or a longer budget into the probes.

## What changed since set 04

1. **Probe prompts v1 → v2.** The target was `role`: under v1, 3B answered a
   literal `NONE` on all 103 `role` probes and 7B echoed the problem text.
2. **Two models added** — Qwen2.5-32B and Mistral-7B. Set 04 was Qwen 3B–14B.
3. **Uniform 4-bit.** Qwen2.5-32B in bf16 is ~65 GB of weights against one L40's
   48 GB, so bf16 at 32B is not available without splitting layers across two
   GPUs. Mixing precisions would have confounded the 14B → 32B step that carries
   the scale claim, so every model in this set is 4-bit.
4. **Both halves in one job**, where set 04 was probes-only.

## How v2 affected the probe results

Same 103 problems, same scoring code, same 4-bit quantisation — the only
difference is the prompt. Set 04 column is its rev-3 re-scoring
(`rescored_v2/`); Mistral has no v1 column because it was not in set 04.

| probe | metric | 3B v1→v2 | 7B v1→v2 | 14B v1→v2 | 32B v1→v2 |
| --- | --- | --- | --- | --- | --- |
| `role` | F1 | 0.000 → 0.000 | 0.000 → 0.000 | 0.548 → **0.321** | 0.780 → **0.688** |
| `fold` | accuracy | 0.011 → 0.033 | 0.130 → 0.130 | 0.196 → **0.114** | 0.484 → **0.359** |
| `check` | balanced acc | 0.500 → 0.500 | 0.703 → **0.500** | 0.780 → **0.501** | 0.500 → 0.500 |
| `introduce` | accuracy | 0.563 → 0.893 | 0.971 → 0.990 | 1.000 → 0.961 | 1.000 → 1.000 |
| `subsume` | balanced acc | 0.500 → 0.647 | 0.500 → 0.500 | 0.520 → 0.500 | 0.510 → 0.520 |

**v2 fixed what it was aimed at and cost more elsewhere.** It is a different
trade, not a strict improvement:

- **It did fix its target.** 14B's literal `NONE` answers went 46 → 0 and 32B's
  5 → 0, and 7B stopped echoing the problem statement.
- **`role` fell anyway** at both models that had a non-zero score. Precision and
  recall fell together, so this is misdirection rather than over-generation: v2's
  extra clause "in particular for the contrary of an assumption"
  (`src/aba_probes.py:154-156`) points the model at contrary predicates, which
  the oracle wants in a negligible fraction of probes.
- **`fold` and `check` fell from a second cause** — v2's leaner `_PROBE_TASK`
  preamble (`src/aba_probes.py:132-143`) dropped the solution criterion that v1's
  task half carried incidentally. `check` collapses to a near-constant NO for
  every Qwen model, which is why three of the four balanced accuracies sit exactly
  at the constant-responder floor.
- **`role` is still broken below 14B.** 3B answers a literal `NONE` on 103/103;
  7B and Mistral echo the prompt's metavariables (`p(t).`) instead of
  instantiating them. Both score 0.000.

> **Provenance.** Every figure in the tables of this manifest was read directly
> from the committed `summary.json` / `probe_summary.json` files, or measured from
> the committed `.jsonl` rows, when the manifest was written. Four claims come
> instead from the set-05 analysis conversation and were **not re-derived**: the
> `NONE`-answer counts (14B 46 → 0, 32B 5 → 0) and the 7B echo timing; the
> precision/recall decomposition of `role` and the attribution of v2's new wrong
> atoms to contrary predicates; the hand audit of 32B's end-to-end output; and the
> ~52-minute cost of the probe half. Re-derive them before they go into the
> thesis.

## Set 05 probe results, against measured floors

The `chance` field the summaries emit (`src/aba_probes.py:722`) is
`0.5` for the binary probes and `0.0` otherwise. **Both are wrong**, and the
measured floors below are what these numbers have to be read against. The floors
were obtained by running answer policies containing no reasoning at all through
the real `score_probe` on the same 103 problems.

| probe | metric | null floor | 3B | 7B | 14B | 32B | mistral |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `role` | F1 | 0.000 | 0.000 | 0.000 | 0.321 | **0.688** | 0.260 |
| `fold` | accuracy | 0.000 | 0.033 | 0.130 | 0.114 | **0.359** | 0.413 |
| `check` | balanced acc | **0.681** | 0.500 | 0.500 | 0.501 | 0.500 | 0.500 |
| `introduce` | accuracy | **1.000** | 0.893 | 0.990 | 0.961 | 1.000 | 0.874 |
| `subsume` | balanced acc | **0.687** | 0.647 | 0.500 | 0.500 | 0.520 | 0.520 |

The null policies: for `check`/`subsume`, answer YES iff the rendered state block
shows an "ASSUMPTIONS INTRODUCED SO FAR" section — one surface cue, with the
rules and the examples never read. For `introduce`, always guard the folded rule
with a brand-new assumption and a brand-new contrary. For `role`, always `NONE`;
for `fold`, copy the rule back unchanged.

**Reading.** Only `role` and `fold` clear their floor, and only above 7B.

1. **`introduce`'s floor is 1.000, not 0.** The trivial "always fresh" policy
   scores 1.000 over 103 probes with zero failures — this is Proposition 2 (R3 +
   RoLe always recovers a solution), so the oracle *cannot* fail when the
   instruction is followed literally. Every model is at or below the trivial
   baseline, so the probe measures **mistakes only** and must be reported
   inverted, as an error count:

   | rows below 1.000 | 32B | 7B | 14B | 3B | mistral |
   | --- | --- | --- | --- | --- | --- |
   | | **0** | 1 | 4 | 11 | 13 |

   Monotone in scale within Qwen — a real result, but the opposite framing from
   set 04's "introduce saturates above 3B".

2. **`check` and `subsume` have a ~0.68 surface-cue floor, not 0.50.** Against
   it, **nothing in set 04 or set 05 has ever beaten baseline on `subsume`**, and
   only 14B under v1 (`check` 0.780) has ever beaten it on `check`. 3B's
   `subsume` 0.647 is a partial surface cue, not comprehension.

3. Secondary: the generator emits the binary probes in fixed `(True, False)`
   pairs (`check` YES 103 / NO 83, `subsume` YES 101 / NO 103 — the imbalance is
   the tail where a class is unavailable). Harmless, because probe calls are
   independent, but the pairs are constructed, not sampled.

## End-to-end results

`gen@k`, k=3, 103 problems per cell. This half is solid and is the part of set 05
that stands without correction.

| mode | 3B | mistral-7b | 7B | 14B | 32B |
| --- | --- | --- | --- | --- | --- |
| `direct` | 0.010 | 0.272 | 0.291 | 0.194 | **0.728** |
| `cot` | 0.010 | 0.078 | 0.184 | 0.282 | **0.505** |
| `guided` | 0.000 | 0.010 | 0.019 | 0.019 | **0.757** |
| `algorithm` | 0.000 | 0.000 | 0.058 | 0.126 | **0.748** |

Parse rate is 1.000 everywhere except 3B `guided` (0.832) and 14B `algorithm`
(0.997).

**32B is the result of this set.** It is the first model for which the structured
modes (`guided` 0.757, `algorithm` 0.748) do not collapse — below 32B, every model
does *worse* the more procedural structure it is given, which is the finding the
scale series was built to expose. Its output is also genuinely terse rather than
lucky: 28.8 mean output tokens in `direct` against 14B's 310.5, hand-audited, with
valid rows really valid and failures real completeness errors.

**14B falling below 7B on `direct`** triggered the confound rule. Set 03's
four-model quantisation control (same prompts v3, same 103 problems) supplies the
mechanism — the 4-bit penalty grows with size across 7B and 14B (mean gen@k bf16 →
4-bit: 7B 0.202 → 0.138, 14B 0.289 → 0.155), so the inversion is quantisation, not
capability. Two points in one family is a trend, not a law. 32B reaches 0.728
*despite* whatever penalty it paid, so the 32B result is robust in the
conservative direction.

## Caveats

1. **Truncation at `--max-tokens 1536` makes two algorithm-mode scores lower
   bounds.** Rows hitting the cap, counted as `completion_tokens >= 1536`:
   Mistral **21.7%** (67/309) and 7B **12.0%** (37/309) in `algorithm`; 3B 3.6%
   (11/309); 14B and 32B zero; all other modes ≤ 0.3%.
2. **The `chance` field in every `probe_summary.json` in this set is wrong** —
   `0.5` for the binary probes where the measured floor is ~0.68, and `0.0` for
   `introduce` where it is 1.000. The stored files are kept as the as-run record;
   read the floors from the table above, not from the JSON.
3. **`fold` scores remain a lower bound**, unchanged from set 04:
   `apply_folding` folds against the background only, while Algorithm 1 line 17
   passes `R`, which grows at line 20 with each learnt defeasible rule. Solver and
   oracle share the restriction, so the agreement test cannot detect it.
4. **4-bit everywhere** — comparable within this set, not with set 03's bf16 rows.

## Files

- `bench_<model>/results_{direct,cot,guided,algorithm}.jsonl` — 309 rows each,
  every row keeping its `raw_output`.
- `bench_<model>/summary.json` — the end-to-end aggregates above.
- `bench_<model>/probes.jsonl` + `probe_summary.json` — 780 probe answers and
  their aggregates, stamped `probe_prompt_version: "v2"`.
- `bench_<model>/symbolic_traces.jsonl`, `name_maps.json` — reference traces and
  the anonymisation maps needed to read the anonymised answers back.
- `bench_<model>/figures/`, `explanations.md`, `frameworks.*`,
  `defeasibility.csv` — the generated report.

Moved here out of `results/` so that `results/` stays scratch, as every doc
describes it: the next probe run writes to `results/bench_<model>/` and would
otherwise have overwritten this set's raw data in place.

## Consequences for set 04

Two of the three defects are properties of the instrument, not of set 05, so they
also apply to the committed `experiments/04_step_probes/MANIFEST.md`, which is
now wrong where it reports `introduce` as a saturating accuracy and where it
prints a 0.50 chance floor for `check` and `subsume`. **Left uncorrected
deliberately** — pending a decision on the framing.

## Successor

Probe prompts **v3** would drop the contrary clause (`src/aba_probes.py:154-156`),
restore the solution criterion into `_PROBE_TASK` (`:132-143`), and keep v2's echo
suppression, bumping `PROBE_PROMPT_VERSION` (`:60`). Defects 1 and 2 are
*reporting* fixes and need no GPU. The probe half of this run cost ~52 minutes
across all five models, so a probes-only re-run is under an hour; the end-to-end
half does not need re-running.
