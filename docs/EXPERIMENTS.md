# Experiment registry

Curated, immutable result sets live in [`experiments/`](../experiments/), one
folder per set, each with a `MANIFEST.md` (date, model, prompt version, metric
revision, exact command, key metrics, caveats). The `results/` folder is a
gitignored working directory: `main.py` writes there; finished runs worth
keeping are *promoted* into `experiments/` together with a manifest.

| Set | Date | Models | Backend | Prompts | Metrics | Dataset | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [`00_preliminary_api`](../experiments/00_preliminary_api/MANIFEST.md) | May–Jun 2026 | Llama-3.3-70B, Llama-3.1-8B | Groq API | v0 (evolving) | rev 1 | 3 builtin ± early synthetics | done (exploratory) |
| [`01_bench_prompts_v1`](../experiments/01_bench_prompts_v1/MANIFEST.md) | Jul 2026 | Qwen2.5-7B | local (L40) | v1 | rev 2 | 103 problems, 5 tiers, anonymised | done |
| [`02_bench_prompts_v2`](../experiments/02_bench_prompts_v2/MANIFEST.md) | Jul 2026 | Qwen2.5-3B/7B/14B, Mistral-7B | local (L40) | v2 | rev 2 | 103 problems, 5 tiers, anonymised | done |
| [`03_bench_prompts_v3`](../experiments/03_bench_prompts_v3/MANIFEST.md) | Jul 2026 | Qwen2.5-3B/7B/14B, Mistral-7B | local (L40) | v3 | **rev 4** (re-scored offline) | 103 problems, 5 tiers, anonymised | done |
| [`04_step_probes`](../experiments/04_step_probes/MANIFEST.md) | Sep 2026 | Qwen2.5-3B/7B/14B/**32B**, 4-bit | local (L40) | probes **v1** | probe **rev 3** (re-scored offline) | 780 probes/model over the same 103 problems | done; `role` superseded |

Sets are comparable only when **both** the prompt version and the metric
revision match. Set 03 was generated under rev-3 scoring and re-scored to rev 4
with `rescore.py` from its stored raw answers; nothing about the model outputs
changed.

Probe sets carry their **own** prompt version, independent of the mode prompts:
`PROBE_PROMPT_VERSION` in [`src/aba_probes.py`](../src/aba_probes.py), stamped
into every `probe_summary.json`. Re-scoring carries the generating version
through rather than restamping it, so a v1 run re-scored today still reads v1.

## The benchmark at a glance

`--benchmark N` builds a stratified suite of `5·N` synthetic problems (plus the
3 builtin ones), each tier isolating one capability of the ASP-ABAlearnB
algorithm; everything is anonymised so the LLM cannot lean on world knowledge:

| Tier | Isolates |
| --- | --- |
| `t1_mono` | Folding only (monotonic rule suffices) |
| `t2_defeas` | Assumption introduction (one exception to defeat) |
| `t3_noise` | Distractor robustness (irrelevant predicates) |
| `t4_domain` | Domain-size scaling (12 constants) |
| `t5_twopath` | Two independent defeasible derivation paths |

## Metrics — precise definitions

All entailment checks are performed by Clingo on the ASP encoding of
Definition 2 (De Angelis et al., ECAI 2024); "a solution" always means
Definition 1: the framework is satisfiable and admits **one stable extension Δ**
accepting all the given positives and none of the given negatives (**the same
Δ for both conditions**).

**Per-sample outcome chain** (each stage must pass before the next; the first
failure names the `error_type`):

| Stage | Field | Definition |
| --- | --- | --- |
| 1. parse | `parse_success` | the output yields a framework. An explicit `NONE` / `NONE` answer is a legitimate empty framework, not a parse failure *(rev. 4)*. Every repair the parser applied is listed in `parse_repairs` |
| 2. well-formed | `wellformed_violations = []` | Definition-1 side conditions hold: (ii) every new-rule head with a background predicate is learnable; (iv) contraries of existing assumptions unchanged; flatness (no assumption as rule head); new-assumption predicates fresh. *(added in metrics rev. 3)* |
| 3. stability | `has_extension` | the candidate admits at least one stable extension |
| 4. fit | `fit_valid` | the candidate **is a solution of the TRAIN problem** (one joint check) |
| 5. generalisation | `gen_valid` | the candidate **is a solution of the FULL problem** (train + held-out examples, one joint check — *not* per-example; rev. 3) |
| 6. non-degenerate | `not is_degenerate` | at least one new rule mentions no individual constant |

**Per-problem aggregates over k samples:** `X@1` = mean of X across samples;
`X@k` = X holds for **at least one** sample. Reported for `fit`, `gen`, and
`clean` (= stages 1–6 all pass, `error_type == "none"`). **`clean@k` is the
headline metric**: "the LLM produced, at least once, a legal, stable,
fitting, generalising, non-degenerate solution — i.e. it did the algorithm's
job".

### The determinacy metric (`det@k`) — rev. 4

`gen_valid` is faithful to Definition 1 but cannot, on its own, distinguish
learning from guessing. Brave ABA Learning admits frameworks with mutually
attacking assumptions under which an unseen atom is **free**: accepted in one
stable extension and rejected in another. Brave entailment then reports success
for a framework that predicts nothing. The paper itself notes this of its own
Nixon solution (p. 3451, "cautious reasoning would not work"), and the effect is
reproducible here — hold out `pacifist(e)` and the reference solution leaves it
free.

So each held-out atom is also classified *conditioned on the training examples*:

| Status | Meaning |
| --- | --- |
| `ALWAYS` | accepted in **every** extension consistent with the training examples |
| `NEVER` | accepted in none of them |
| `FREE` | accepted in some, rejected in others — no prediction |

- `gen_determined` (`det@1` / `det@k`): fit holds **and** every held-out example
  is `ALWAYS`/`NEVER` in agreement with its label.
- `determinacy_score`: the fraction of held-out atoms determined and correct.
- `n_free_heldout`: how many the framework leaves open.

`gen@k − det@k` is the share of apparent generalisation that is free choice.
Implemented by `conditioned_status` in [`src/aba_validator.py`](../src/aba_validator.py).

**Diagnostics (not validity):** `generalization_score` = fraction of held-out
examples correct **inside one witness extension of the training problem**
(rev. 4; previously independent per-example brave queries, which made this score
routinely exceed fit); `overfit_gap` = fit(1/0) − generalization_score;
`intensional_rate` (strict: no constant anywhere in a new rule; reported as
`null` when no sample fitted, rather than as a measured 0%);
`semantic_agreement` = per-constant agreement with the symbolic reference on the
target predicate.

**Two symbolic rows.** `symbolic_full_problem` is the algorithm with every
example in view — not comparable with the LLM rows. `symbolic_train_only` runs
ASP-ABAlearnB on the same training split and scores it with the same function
used for LLM samples; that is the comparable ceiling (53.8% on the current
benchmark, not 100%).

> **Metrics revision 3** (prompts v3): stage 2 added; stage 5 changed from
> per-example held-out checks to the joint full-problem check. The old
> per-example version could accept held-out positives in *different* extensions
> and its negative test (`:- e` alone) was near-vacuous — the source of the
> "80% gen@k with 0% fit" anomalies in sets 01–02.
>
> **Metrics revision 4** (current). Four corrections, all of which change
> reported numbers without any new model output:
> 1. Stage 2 no longer rejects the legal **reuse** of a background assumption
>    (Definition 4 / Algorithm 1 line 36). This alone accounted for 4 262 of
>    ~6 100 violations, marking 71.8% of set-03 samples ill-formed.
> 2. Stage 2 applies condition (ii) to the contrary of a background assumption
>    like any other background predicate — it must be in T.
> 3. The parser no longer discards rules filed under `NEW ASSUMPTIONS:` or
>    prefers a draft answer block over the final one (~40% more rules
>    recovered), and `NONE`/`NONE` is no longer a parse error.
> 4. `det@*` added; `generalization_score` moved to a witness extension.
>
> Re-scoring an old set to the current revision costs minutes:
> `python rescore.py <run_dir> --benchmark 20`.

`summary.json` contains every aggregate, overall and per tier (`by_tier`), with
95% Wilson intervals for the `@k` rates under `ci95`.

## Step probes — measuring the algorithm, not just the answer

Every metric above is an **outcome** metric: did a Definition-1 solution come
out? None of them says whether the model *executed* ASP-ABAlearnB. Step probes
do, by supplying the state instead of inferring it: each probe presents one
decision point taken from the real symbolic execution (via the `observer` hook
in `gen_phase`, so the states are exactly those the algorithm visits) and asks
for that one decision.

Each probe is keyed to a line of Algorithm 1, which is what fixes its
granularity:

| probe | Algorithm 1 | question | oracle | chance |
| --- | --- | --- | --- | --- |
| `role` | lines 3–12, **RoLe** | which ground facts make this a solution? | `run_rote_learning`'s minimal set | ~0 |
| `subsume` | line 16, **R4** | can this fact be dropped? | `fact_subsumption` | 0.50 |
| `fold` | line 17, **applyFolding** | generalise `p(X) :- X = c` | `apply_folding` — the **set** of legal results | ~0 |
| `check` | line 18 | still a solution? if not, which examples fail? | `check_brave_entailment` | 0.50 / ~0 |
| `introduce` | lines 19, 34–46, **R3** | which rule to guard, with which assumption? | RoLe on the contrary must complete it | ~0 |

`role` tests the **RoLe procedure**, not R1: R1 alone adds a single fact
(`p(X) ← X = t`), and minimality comes from the `#minimize` directive of
Definition 2(e). Likewise `fold` tests `applyFolding` — a bounded *sequence* of
R2 applications returning an intensional rule (Prop. 3) — not one R2 step.

Design points that matter when reading the numbers:

- **`fold` and `introduce` accept any legal answer**, not the one the solver
  happened to pick, so the nondeterminism of `applyFolding`/`applyAsmIntro`
  costs the model nothing. This is not a convenience: the paper's own
  conclusion names Folding's nondeterminism as *"the most critical issue"* and
  reports work in progress on controlling it, which is precisely what `fold`
  measures.
- **`fold` accepts folds that break solution-hood.** Example 6 folds ρ12/ρ13 to
  ρ14/ρ15 and the result "is no longer a solution"; R3 then repairs it.
  Legality (line 17) and solution-preservation (line 18) are separate steps and
  so separate probes.
- **`check` and `subsume` are binary and must be read as `balanced_accuracy`
  against a 0.50 floor** — a model that always answers YES scores exactly 0.50,
  where raw accuracy would flatter it. `check` additionally asks *which*
  examples fail, and that half has a ~0 chance floor.
- **`introduce` asks for two things only**: which rule to guard and which
  assumption to use. `applyAsmIntro` returns `⟨ρ, α(X), S⟩`, but **S is not
  chosen by the algorithm** — it is computed by ASP at line 44 and rote-learnt
  at lines 23–25, with Prop. 2 guaranteeing it exists. So the oracle runs that
  same RoLe (T = {c_α}) rather than asking the model for it. Demanding a
  contrary would require more of the model than of the reference.
- **`introduce` credits the reuse → fresh fallback.** Line 36 prefers an
  existing assumption; if it fails, line 39 backtracks and line 41 mints a new
  one. A model gets one shot, so scoring the literal answer penalises it for
  obeying REUSE FIRST — measured, that inverted the scale trend, with all 24 of
  32B's failed reuses rescued by the fallback.

`reuse_rate` is reported alongside, **descriptively, not as an accuracy**. An
assumption relative to the body (Definition 4) exists in only 2.9% of these
probes, so the algorithm mints a fresh assumption almost always; agreement with
line 36 would therefore be a degenerate 97/3 class split. It is still worth
reading, because it shows *process* divergence behind identical outcomes: 32B
reuses on 99% of probes where the algorithm would reuse on 3%, and reaches a
legal result anyway.

Validation: feeding the reference algorithm's *own* decisions back through every
probe scores 328/328 (`tests/test_probes.py::test_solver_own_decisions_score_correct`).
A probe that rejects the algorithm's own answer is mis-specified, and two were
found that way during development.

Run with `--probes`; results land in `probes.jsonl` and `probe_summary.json`.

### Trace fidelity (secondary, descriptive)

`rescore.py --trace` additionally reports how much of the symbolic execution the
model's free-text reasoning reproduces: `has_trace_rate`, rule-keyed `f1`, and
`r2_recall` / `r3_recall`. All measures are keyed to a **canonical rule**, whose
chance rate is ~0.

> An earlier version aligned the R1/R2/R3/R4 **symbol sequence** against the
> symbolic trace. It was dropped: random sequences of the same length score
> 0.28–0.49 on it, i.e. at or above every cell it was meant to measure. A
> four-symbol alphabet over length-4–8 sequences cannot discriminate.

Two cautions. `direct` mode is excluded — it asks for an answer, not a
derivation, so it has no trace and any hits are echo artefacts. And the
aggregate `f1` is weighted towards R1 (44.8% of gold steps here); R1 is not
merely "copy the examples" — RoLe adds a *minimal* set and 23.2% of its facts
are contraries of assumptions that appear in no example list — but it is still
the step overlapping most with given text. Report `r2_recall`/`r3_recall` as the
discriminating figures.

## Reproducing

```bash
# quick local demo (no API key, no GPU)
python main.py --backend mock --benchmark 2 --modes direct --n-samples 1

# full benchmark for one model on a GPU
python main.py --backend local --model qwen2.5-7b \
    --benchmark 20 --modes direct cot guided algorithm \
    --n-samples 3 --max-tokens 1536 --export --output results/bench_qwen2.5-7b
```

On the DISI SLURM cluster see [`cluster/README.md`](../cluster/README.md)
(`bash cluster/submit_benchmarks.sh` chains one job per model).

Problem generation is seeded: the same `--benchmark N` reproduces byte-identical
problem sets, and `verify_invariance` (in `src/aba_anonymize.py`) guarantees
anonymisation preserves symbolic solvability.
