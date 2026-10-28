# Experiment registry

Curated, immutable result sets live in [`experiments/`](../experiments/), one
folder per set, each with a `MANIFEST.md` (date, model, prompt version, metric
revision, exact command, key metrics, caveats). The `results/` folder is the
working directory `main.py` and the SFT scripts write to; it is tracked, so runs
on the cluster come back with `git push`. Finished prompting runs worth keeping
are *promoted* into `experiments/` together with a manifest.

| Set | Date | Models | Backend | Prompts | Metrics | Dataset | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [`00_preliminary_api`](../experiments/00_preliminary_api/MANIFEST.md) | May–Jun 2026 | Llama-3.3-70B, Llama-3.1-8B | Groq API | v0 (evolving) | rev 1 | 3 builtin ± early synthetics | superseded (examples held out) |
| [`01_bench_prompts_v1`](../experiments/01_bench_prompts_v1/MANIFEST.md) | Jul 2026 | Qwen2.5-7B | local (L40) | v1 | rev 2 | 103 problems, 5 tiers, anonymised | superseded (examples held out) |
| [`02_bench_prompts_v2`](../experiments/02_bench_prompts_v2/MANIFEST.md) | Jul 2026 | Qwen2.5-3B/7B/14B, Mistral-7B | local (L40) | v2 | rev 2 | 103 problems, 5 tiers, anonymised | superseded (examples held out) |
| [`03_bench_prompts_v3`](../experiments/03_bench_prompts_v3/MANIFEST.md) | Jul 2026 | Qwen2.5-3B/7B/14B, Mistral-7B | local (L40) | v3 | rev 4 (re-scored offline) | 103 problems, 5 tiers, anonymised | superseded (examples held out) |
| [`04_step_probes`](../experiments/04_step_probes/MANIFEST.md) | Sep 2026 | Qwen2.5-3B/7B/14B/**32B**, 4-bit | local (L40) | probes **v1** | probe rev 3 (re-scored offline) | 780 probes/model over the same 103 problems | done; `role` superseded |
| [`05_scale_4bit_probes_v2`](../experiments/05_scale_4bit_probes_v2/MANIFEST.md) | Sep 2026 | Qwen2.5-3B/7B/14B/32B, Mistral-7B, 4-bit | local (L40) | modes **v4**, probes **v2** | rev 4; probe rev 3 | the same 103 problems; 780 probes/model | probes done; end-to-end superseded (examples held out) |
| [`06_probes_v3`](../experiments/06_probes_v3/MANIFEST.md) | Oct 2026 | Qwen2.5-3B/7B/14B/32B, Mistral-7B, 4-bit | local (L40) | probes **v3** | probe floors measured | 845 probes/model over the same 103 problems | done |
| `07_e2e_whole_v4` | Oct 2026 | Qwen2.5-3B/7B/14B/32B, Mistral-7B, 4-bit | local (L40) | modes **v4** | score card, posed whole | the same 103 problems, k = 3 | registered ([METHOD_HISTORY.md](METHOD_HISTORY.md), Phase 13) |

**Sets 00–03 and set 05's end-to-end half are superseded.** They hid part of each
problem's examples from the prompt and scored the answers on the hidden ones, so they
posed a different problem from Definition 1's and are comparable with no set that
poses problems whole ([METHOD_HISTORY.md](METHOD_HISTORY.md), Phase 13). They are
kept as the as-run record, and `rescore.py` refuses them.

Otherwise, sets are comparable only when **both** the prompt version and the metric
match. Probe sets carry their **own** prompt version, independent of the mode prompts:
`PROBE_PROMPT_VERSION` in [`src/aba_probes.py`](../src/aba_probes.py), stamped
into every `probe_summary.json`. Re-scoring carries the generating version
through rather than restamping it, so a v1 run re-scored today still reads v1.
End-to-end runs record the mode prompts' version (`MODE_PROMPT_VERSION`) and each
mode's prompt hash in the `run` block of `summary.json`.

## Training corpora

Data sets for the SFT ablation (trace target vs endpoint target). They are
not result sets: no model output lives here. Each is built by
`sft/build_corpus.py` and committed with its MANIFEST, which carries the sha256
of every file; the data rebuilds byte for byte. Full description in
[CORPUS.md](CORPUS.md).

| Corpus | Date | Tier spec | Prompt | Contents | Status |
| --- | --- | --- | --- | --- | --- |
| [`corpus/v1`](../corpus/v1/MANIFEST.md) | Sep 2026 | **v2** (`t1_base`–`t5_twopath`, held-out `t8_decoy`, `t9_reuse`) | **v4-sft** | 1500 train / 200 val / 200 test / 100 held-out, each training tier 50/50 defeasible | built, all gates pass |

**Not comparable with the benchmark below.** Tier spec v2 replaces the
benchmark's tiers: every problem carries exception facts, every tier is balanced by
class, and `t5_twopath` was rewritten because the legacy generator produced one
problem in 20 surface forms (set 05, caveat 5). Problems are posed whole, as in
the end-to-end study from set 07. Fidelity is scored against the reference's gold
trace, which since Phase 8 of [METHOD_HISTORY.md](METHOD_HISTORY.md) follows
Algorithm 1 at lines 17–19 and 36–39.

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

At `--benchmark 20` (103 problems), the algorithm has only **9 distinct answers**.
Anonymisation names predicates by first appearance, so t2, t3 and t4 each have one
answer string across their 20 problems. t5's 20 problems have one structure
(set 05, caveat 5). This sets what exact agreement can mean here; the floors below
account for it.

## Metrics — precise definitions

All entailment checks are performed by Clingo on the ASP encoding of
Definition 2 (De Angelis et al., ECAI 2024); "a solution" always means
Definition 1: the framework is satisfiable and admits **one stable extension Δ**
accepting all the given positives and none of the given negatives (**the same
Δ for both conditions**).

Every answer, prompted or fine-tuned, is scored by `score_output` in
[`src/aba_score.py`](../src/aba_score.py) against the algorithm's run on the same
problem, **posed whole**: the prompt shows every example and the scoring uses every
example. The fields of its score card:

| Field | Definition |
| --- | --- |
| `parse_ok` | the output yields a framework. An explicit `NONE` / `NONE` answer is an empty framework, not a parse failure. A rule's head must be an atom and each body element an atom, a `not` atom or a comparison; anything else is not a rule ([METHOD_HISTORY.md](METHOD_HISTORY.md), Phase 12). Every repair the parser applied is listed in `repairs` |
| `illformed` | the Definition-1 side conditions it violates: (ii) every new-rule head with a background predicate is learnable; (iv) contraries of existing assumptions unchanged; flatness (no assumption as a rule head); new-assumption predicates fresh, and never learnable, since Definition 1 keeps T and the assumptions disjoint ([METHOD_HISTORY.md](METHOD_HISTORY.md), Phase 14) |
| `valid` | the answer **is a solution**: one stable extension accepts every posed positive and no posed negative (one joint check) |
| `clean` | valid, intensional (no constant in any new rule), not ill-formed, and not self-defeating |
| `exact` | the algorithm's answer, up to assumption names and body order |
| `agreement` | over the example predicate's atoms outside E+ and E-, the share whose status given E+/E- (`ALWAYS` / `NEVER` / `FREE`) matches the algorithm's framework; undefined when there are no such atoms |
| `r2_bodies` | R2: each learnt rule's body against the algorithm's, for the same head |
| `defeasible` | R3: whether the answer guards a rule with an assumption, read against `ref_defeasible` as balanced accuracy |
| `error` | the first failure: `parse_error`, `illformed`, `not_a_solution`, `valid_but_degenerate`, `self_defeating`, `illegal_transformation` (only when the step audit runs), else `ok` |

**Per-problem aggregates over k samples:** `X@1` = mean of X across samples;
`X@k` = X holds for **at least one** sample. `summary.json` reports valid, clean
and exact at @1 and @k, with 95% Wilson intervals for the `@k` rates under `ci95`,
overall and per tier (`by_tier`, with the number of distinct structures).

**Free choice.** Brave ABA Learning admits frameworks with mutually attacking
assumptions under which an atom is **free**: accepted in one stable extension and
rejected in another. The paper notes this of its own Nixon solution (p. 3451,
"cautious reasoning would not work"). `agreement` therefore classifies each atom
*conditioned on the posed examples* (`conditioned_status` in
[`src/aba_validator.py`](../src/aba_validator.py)), and a `FREE` atom matches only
a `FREE` atom.

**Floors.** Every metric is read against measured no-reasoning floors
(`analysis/null_baselines.py --end-to-end`): answers that see only the problem as
posed, or answer every problem alike, scored by the same function. On the
103-problem benchmark the floors are clean@k **0.777** (a positional rule) and
exact@k **0.388** (one answer for all). Valid@1 and agreement both have floors of
1.000, so neither can show reasoning on this benchmark. The registered reading of
set 07 is in [METHOD_HISTORY.md](METHOD_HISTORY.md), Phase 13.

> **Superseded: the fit / gen / det chain (sets 00–03, set 05's end-to-end half).**
> Those runs hid part of each problem's examples (`test_ratio` 0.34) and scored
> `fit_valid` (a solution of the shown examples), `gen_valid` (of all of them),
> `gen_determined`, `generalization_score` and the overfit gap. Two symbolic rows
> accompanied them (the algorithm on the full problem, and on the shown examples).
> Metric revisions 1–4 belong to that chain:
>
> - rev 3 made generalisation one joint check and added the side conditions;
> - rev 4 legalised the reuse of a background assumption (Definition 4), recovered
>   rules filed under `NEW ASSUMPTIONS:`, and added det@k.
>
> The definitions are in each set's MANIFEST and in the history of this file.

## Step probes — measuring the algorithm, not just the answer

Every metric above is an **outcome** metric: what did the answer come out as? None
of them says whether the model *executed* ASP-ABAlearnB. Step probes do, by
supplying the state instead of inferring it: each probe presents one decision point
taken from the real symbolic execution (via the `observer` hook in `gen_phase`, so
the states are exactly those the algorithm visits) and asks for that one decision.

Each probe is keyed to a line of Algorithm 1, which is what fixes its
granularity. The floors are measured on probe prompts v3, each the best of several
no-reasoning policies (`analysis/null_baselines.py`):

| probe | Algorithm 1 | question | oracle | floor (v3) |
| --- | --- | --- | --- | --- |
| `role` | lines 3–12, **RoLe** | which ground facts make this a solution? | `run_rote_learning`'s minimal set | 0.994 (score) |
| `subsume` | line 16, **R4** | can this fact be dropped? | `fact_subsumption` | 0.762 (balanced) |
| `fold` | line 17, **applyFolding** | generalise `p(X) :- X = c` | `apply_folding` — the **set** of legal results | 1.000 |
| `check` | line 18 | still a solution? if not, which examples fail? | `check_brave_entailment` | 0.633 (balanced) |
| `introduce` | lines 19, 34–46, **R3** | which rule to guard, with which assumption? | lines 36–44 as Algorithm 1 prints them | 0.855 (balanced) |

`role` and `fold` cannot discriminate on this benchmark: RoLe's answer is the
positive examples on 102 of 103 problems, and dom(X) is a legal fold at every state.

`role` tests the **RoLe procedure**, not R1: R1 alone adds a single fact
(`p(X) ← X = t`), and minimality comes from the `#minimize` directive of
Definition 2(e). Likewise `fold` tests `applyFolding` — a bounded *sequence* of
R2 applications returning an intensional rule (Prop. 3) — not one R2 step.

Design points that matter when reading the numbers:

- **`fold` accepts any legal answer**, not the one the solver happened to pick, so
  the nondeterminism of `applyFolding` costs the model nothing. This is not a
  convenience: the paper's own conclusion names Folding's nondeterminism as *"the
  most critical issue"* and reports work in progress on controlling it, which is
  precisely what `fold` measures.
- **`fold` accepts folds that break solution-hood.** Example 6 folds ρ12/ρ13 to
  ρ14/ρ15 and the result "is no longer a solution"; R3 then repairs it.
  Legality (line 17) and solution-preservation (line 18) are separate steps and
  so separate probes.
- **`check` and `subsume` are binary and are read as `balanced_accuracy`**. A model
  that always answers YES scores exactly 0.50, but a single surface cue scores
  more, so they are read against the measured floors above. `check` additionally
  asks *which* examples fail.
- **`introduce` asks for two things only**: which rule to guard and which
  assumption to use. `applyAsmIntro` returns `⟨ρ, α(X), S⟩`, but **S is not
  chosen by the algorithm** — it is computed by ASP at line 44 and rote-learnt
  at lines 23–25, with Prop. 2 guaranteeing it exists. So the oracle runs that
  same RoLe (T = {c_α}) rather than asking the model for it. Demanding a
  contrary would require more of the model than of the reference.
- **`introduce` is scored as Algorithm 1 prints lines 36–44** from probe prompts
  v3 on. Line 36 reuses an assumption relative to the body (Definition 4) if there
  is one; if that fails, line 39 backtracks, with no fallback to line 41. Sets 04
  and 05 credited a reuse → mint fallback that is not in the paper, so their
  `introduce` scores are not comparable ([METHOD_HISTORY.md](METHOD_HISTORY.md),
  Phases 8 and 10). In v3 the probe is balanced over line 36's two branches.

Validation: feeding the reference algorithm's *own* decisions back through every
probe scores every probe correct
(`tests/test_probes.py::test_solver_own_decisions_score_correct`). A probe that
rejects the algorithm's own answer is mis-specified, and two were found that way
during development.

Run with `--probes`; results land in `probes.jsonl` and `probe_summary.json`.

### Trace fidelity (secondary, descriptive)

The score card's `trace_fidelity` (the frozen scorer of
[`src/aba_trace.py`](../src/aba_trace.py)) reports how much of the symbolic
execution the model's free-text reasoning reproduces: `has_trace`, rule-keyed
`f1`, and `r2_recall` / `r3_recall`. `summary.json` reports the mean f1 as
`trace_f1`. All measures are keyed to a **canonical rule**, whose chance rate is ~0.

> An earlier version aligned the R1/R2/R3/R4 **symbol sequence** against the
> symbolic trace. It was dropped: random sequences of the same length score
> 0.28–0.49 on it, i.e. at or above every cell it was meant to measure. A
> four-symbol alphabet over length-4–8 sequences cannot discriminate.

Two cautions. `direct` mode is excluded — it asks for an answer, not a
derivation, so it has no trace and any hits are echo artefacts. And the
aggregate `f1` is weighted towards R1, the step that overlaps most with the given
text. Report `r2_recall`/`r3_recall` as the discriminating figures.

## Reproducing

```bash
# quick local demo (no API key, no GPU)
python main.py --backend mock --benchmark 2 --modes direct --n-samples 1

# full benchmark for one model on a GPU
python main.py --backend local --model qwen2.5-7b --load-4bit \
    --benchmark 20 --modes direct cot guided algorithm \
    --n-samples 3 --max-tokens 1536 --export --output results/bench_qwen2.5-7b

# re-score a finished run offline, from its own run record
python rescore.py results/bench_qwen2.5-7b

# the end-to-end floors, and a set read against them
python analysis/null_baselines.py --end-to-end --set experiments/07_e2e_whole_v4
```

On the DISI SLURM cluster see [`cluster/README.md`](../cluster/README.md)
(`bash cluster/submit_benchmarks.sh` chains one job per model).

Before any model call, `main.py` builds the algorithm's answer for every problem
(`references.jsonl`) and checks the instrument: the algorithm's answer must score
clean and exact, RoLe's facts valid but not clean, and the positive examples declared
assumptions not clean. Each sample's seed is derived
from `--sampling-seed`, the problem, the mode and the sample index, and rows are
appended as they are scored, so a run killed and restarted into the same `--output`
resumes with the same samples. 4-bit kernels are not bitwise deterministic: the
seed fixes the draw, not the output.

Problem generation is seeded: the same `--benchmark N` reproduces byte-identical
problem sets, and `verify_invariance` (in `src/aba_anonymize.py`) guarantees
anonymisation preserves symbolic solvability.
