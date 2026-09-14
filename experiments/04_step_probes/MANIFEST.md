# Set 04 — Step probes (Qwen2.5 scale series)

First experiment set that measures **whether the model executes ASP-ABAlearnB's
transformations**, rather than whether a Definition-1 solution comes out. Sets
00–03 are outcome metrics and are not comparable with this one.

| Field | Value |
| --- | --- |
| Date | 2026-09-10 / 11 (generation), 2026-09-14 (scoring) |
| Models | Qwen2.5 **3B / 7B / 14B / 32B**, all `--load-4bit` |
| Backend | `local` (L40, DISI cluster) |
| Dataset | 103 problems, 5 tiers, anonymised, `--benchmark 20`, seed 42 |
| Probes | 780 per model (`--probes-per-kind 2`, k=1, greedy, `--max-tokens 512`) |
| **Probe-prompt version** | **v1** — see the caveat below |
| Mode-prompt version | n/a (no end-to-end modes in this set) |
| Scoring revision | probe scoring **rev 3** (see below) |
| Status | done, but **`role` superseded** by the pending v2 run |

Quantisation is constant across the series (4-bit everywhere), so the models are
comparable with each other. They are **not** comparable with the bf16 14B rows of
set 03.

## Command

```bash
PROBES=1 MODELS="qwen2.5-3b qwen2.5-7b qwen2.5-14b qwen2.5-32b" \
    EXTRA="--load-4bit" bash cluster/submit_benchmarks.sh
```

## Results

Re-scored offline from stored answers with
`python rescore.py "results/bench_qwen2.5-*" --benchmark 20 --probes --out rescored_v2/`.

| probe (Algorithm 1 line) | chance | 3B | 7B | 14B | 32B |
| --- | --- | --- | --- | --- | --- |
| `role` — RoLe (3–12) | ~0 | 0.000 | 0.000 | 0.534 | **0.777** |
| `fold` — applyFolding (17) | ~0 | 0.011 | 0.130 | 0.196 | **0.484** |
| `introduce` — R3 (19, 34–46) | ~0 | 0.563 | 0.971 | **1.000** | **1.000** |
| `check` — (18), balanced acc | 0.50 | 0.500 | 0.703 | **0.780** | 0.500 |
| `subsume` — R4 (16), balanced acc | 0.50 | 0.500 | 0.500 | 0.520 | 0.510 |
| `reuse_rate` (descriptive, not an accuracy) | — | 0.39 | 0.69 | 0.60 | 0.99 |

**Reading.** Scale buys the rule-rewriting steps and buys nothing on evaluating
the framework state those rewritings act on. `check` peaks at **14B**: 32B
answers a constant "no longer a solution" on 186/186 and 3B a constant YES, both
of which balanced accuracy correctly floors at 0.50 where raw accuracy would have
reported 0.446 and 0.554. `subsume` is at the floor for every model — all four
are constant responders, so **no model performs Fact Subsumption anywhere in
3B–32B**. `introduce` saturates above 3B and no longer discriminates here.

`reuse_rate` is reported descriptively: 32B reuses an existing assumption on 99%
of probes where Algorithm 1 would reuse on 3% (an assumption relative to the body,
Definition 4, exists in only 2.9% of these probes). Identical outcomes reached by
a different process — which is this thesis's question in miniature.

## Scoring revisions

Three defects were found after generation and corrected offline; every raw answer
is stored, so none of this required GPU time.

> **rev 1** (as generated). Contained two harness defects, both ours:
> the shared `SYSTEM_PROMPT` mandated `NEW RULES:`/`NEW ASSUMPTIONS:` while the
> R3 probe asked for `RULE:`/`ASSUMPTION:`, so the oracle **never ran** on 87/103
> (3B), 70/103 (7B) and 92/103 (32B); and 7B's echoed problem text was scored as
> its answer in 80/103 `role` items.
>
> **rev 2.** Echo stripped before scoring; the R3 parser accepts both formats.
> 32B's R3 went 0.029 → 0.757 and **14B changed zero rows** — the regression
> guard. 7B's `role` partial credit fell 0.272 → 0.000: it had been credited for
> reciting the background.
>
> **rev 3** (current). Definitional corrections from re-reading §5–6 of the paper:
> 1. `introduce` asks only for the two choices `applyAsmIntro` makes. The
>    contrary's extension S is computed by ASP at line 44, not chosen by the
>    algorithm (Prop. 2), so the oracle runs that RoLe itself.
> 2. `introduce` credits the reuse → fresh fallback of lines 39–41. Scoring the
>    literal one-shot answer penalised 32B for obeying line 36's REUSE FIRST and
>    inverted the scale trend; all 24 of its failed reuses are rescued by the
>    fallback.
> 3. A trailing full stop on the `ASSUMPTION:` line was being captured into the
>    contrary and registered as the contrary atom, so nothing could defeat the
>    assumption. 8 false negatives, all 14B: `introduce` 0.922 → 1.000.
>    **Found by hand audit, not by a test.**

## Hand audit

37 rows read by hand before these figures were accepted — stratified over all
five probes and all four models, sampling one correct and one incorrect row per
cell so that both false accepts and false rejects were exposed. This is the gate
that found defect 3 above.

Verdicts were otherwise sound: `fold` rejections were genuinely different rules
from the legal set; `role` rejections were real (`NONE`, or an intensional rule
where ground facts were asked for); the reuse/fresh classification was right in
every row inspected.

One judgement call worth recording: a model that answers `YES` and then lists
failing examples is self-contradictory (seen at 3B). The scorer takes the
explicit YES/NO token and scores the example list separately. Defensible, but it
is a convention, not a fact about the answer.

## Caveats

1. **Probe prompts v1 carried the two rev-1 conflicts.** They affected scoring,
   which was corrected, but they also affected **generation**, which cannot be.
   `role` is the row that suffers most: 3B answered a literal `NONE` on all 103
   `role` probes under a system prompt that forbade ground facts. Treat `role`
   for 3B and 7B as unreliable until the v2 re-run.
2. **`fold` scores are a lower bound.** `apply_folding` folds against the
   background only, while Algorithm 1 line 17 passes `R`, which grows at line 20
   with each learnt defeasible rule. Solver and oracle share the restriction, so
   the 328/328 agreement test cannot detect it. (The paper is itself ambiguous:
   §6's prose says "rules in `Rl \ {ρ}`" while line 17 passes `R`.)
3. `introduce` no longer discriminates above 3B on this benchmark.

## Files

Not copied into this folder — they are already committed in the tree, and a third
copy of 4 × 780 rows is not worth it:

- `results/bench_qwen2.5-{3b,7b,14b,32b}/probes.jsonl` — as generated (rev 1)
- `rescored/` — rev 2
- `rescored_v2/` — **rev 3, the table above**; `probe_summary.json` there carries
  `probe_prompt_version: v1`

## Successor

Set **05** will be the same matrix under probe prompts **v2**
(`PROBE_PROMPT_VERSION` in `src/aba_probes.py`), whose summaries stamp themselves
`v2`. Compare `role` first.
