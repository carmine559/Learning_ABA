# Experiment registry

Curated, immutable result sets live in [`experiments/`](../experiments/), one
folder per set, each with a `MANIFEST.md` (date, model, prompt version, exact
command, key metrics, caveats). The `results/` folder is a **gitignored working
directory**: `main.py` writes there; finished runs worth keeping are *promoted*
into `experiments/` together with a manifest.

| Set | Date | Models | Backend | Prompts | Dataset | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [`00_preliminary_api`](../experiments/00_preliminary_api/MANIFEST.md) | May–Jun 2026 | Llama-3.3-70B, Llama-3.1-8B | Groq API | v0 (evolving) | 3 builtin ± early synthetics | done (exploratory) |
| [`01_bench_prompts_v1`](../experiments/01_bench_prompts_v1/MANIFEST.md) | Jul 2026 | Qwen2.5-7B | local (L40) | v1 | 103 problems, 5 tiers, anonymised | done |
| [`02_bench_prompts_v2`](../experiments/02_bench_prompts_v2/MANIFEST.md) | Jul 2026 | Qwen2.5-3B/7B/14B, Mistral-7B | local (L40) | v2 | 103 problems, 5 tiers, anonymised | done |

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
| 1. parse | `parse_success` | the output yields a non-empty framework in the required format |
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

**Diagnostics (not validity):** `generalization_score` = fraction of held-out
examples individually correct (per-example brave checks; localises errors);
`overfit_gap` = fit(1/0) − generalization_score; `intensional_rate` (strict:
no constants anywhere in new rules); `semantic_agreement` = per-constant
agreement of the candidate with the symbolic reference on the target
predicate.

> **Metrics revision 3** (with prompts v3): stage 2 added, and stage 5 changed
> from per-example held-out checks to the joint full-problem check. The old
> per-example version could accept held-out positives in *different*
> extensions and its negative test (":- e" alone) was near-vacuous on
> multi-extension frameworks — the source of "80% gen@k with 0% fit"
> anomalies in sets 01–02. Numbers from sets 01–02 use the old stage 5 and
> are therefore *optimistic* on `gen@k`; `fit` and `clean`'s fit-component
> were always Definition-1-exact.

`summary.json` contains every aggregate, overall and per tier (`by_tier`).

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
