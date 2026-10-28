# Command-line reference

Everything is driven by `main.py`; there is no config file. Two auxiliary
entry points exist: `rescore.py` (recompute metrics offline) and the SLURM
scripts in [`cluster/`](../cluster/README.md).

```bash
python main.py [dataset flags] [LLM flags] [task flags] [output flags]
```

---

## Dataset

| Argument | Default | Description |
| --- | --- | --- |
| `--benchmark N` | `0` | **The main flag for a real run.** Adds the stratified benchmark suite with N problems per tier (`t1_mono`, `t2_defeas`, `t3_noise`, `t4_domain`, `t5_twopath`), so `--benchmark 20` gives 5×20 + 3 built-ins = 103 problems. The per-tier breakdown in the report shows *which* part of the algorithm the model can replicate. |
| `--dataset-seed N` | `42` | Seed of the benchmark and synthetic generators. Every committed set used 42. |
| `--n-synthetic N` | `0` | N extra single-path synthetic problems. |
| `--n-complex N` | `0` | N extra two-path synthetic problems (richer QBAFs → intermediate σ under Task 2). |
| `--anonymize` / `--no-anonymize` | **on** | Rename every predicate and constant to an abstract symbol before the model sees the problem. On by default; `--no-anonymize` keeps real names (human inspection, or Task 3 / RAG where retrieval needs them). |
| `--anonymize-scheme {letters,indexed}` | `letters` | `p,q,r,… / a,b,c,…` or `p0,p1,… / c0,c1,…`. |

The three built-in problems (`nixon_diamond`, `flies`, `tax_law`) are always
included. Problem generation is seeded, so the same `--benchmark N` reproduces
a byte-identical problem set.

---

## LLM backend

| Argument | Default | Description |
| --- | --- | --- |
| `--backend {mock,groq,hf_api,google_ai,local}` | `mock` | See the table below. |
| `--model NAME` | per backend | Model id or alias. |
| `--n-samples N` | `5` | Samples per problem: the `k` in @k (any of k samples). The committed benchmark runs used `3`. |
| `--temperature F` | `0.7` | Set `0` for greedy decoding. The `local` backend samples with top-p 0.95. |
| `--max-tokens N` | `1024` | Cap on the answer. `algorithm` mode emits a long trace before the answer — the cluster runs use `1536`. A sample that hits the cap has `finish: length` and is scored `truncated`. |
| `--sampling-seed N` | `0` | Run seed. Each sample's seed is derived from it, the problem, the mode and the sample index, so a resumed run draws the same samples. 4-bit kernels are not bitwise deterministic: the seed fixes the draw, not the output. |
| `--thinking` | off | Gemini thinking mode (`google_ai`, `gemini-2.5-*`). Thinking tokens do not count against `--max-tokens`. |
| `--load-4bit` | off | **`local` only.** Load in 4-bit nf4 — needed to fit a 32B model on an L40, or any 7B on an 11 GB RTX 2080 Ti. |
| `--min-interval F` | `0.0` | Minimum seconds between API requests. Try `2`–`4` on free tiers, `6`–`12` for a 10 RPM Gemini model. |

### Backends

| Backend | Credential | Default model | Install |
| --- | --- | --- | --- |
| `local` | `HF_TOKEN` (gated repos only) | `Qwen/Qwen2.5-7B-Instruct` | `torch` + `transformers` — see [`cluster/setup_env.sh`](../cluster/setup_env.sh) |
| `groq` | `GROQ_API_KEY` | `llama-3.3-70b-versatile` | `pip install groq` |
| `google_ai` | `GOOGLE_API_KEY` | `gemini-2.5-flash` | `pip install google-genai` |
| `hf_api` | `HF_TOKEN` | `Qwen/Qwen2.5-7B-Instruct` | `pip install huggingface_hub` |
| `mock` | — | hard-coded answers | — |

**`local` is the backend every committed experiment used** — it runs the model
on the GPU with no network and no rate limit, which is what makes a 103-problem
× 4-mode × k=3 run feasible.

Aliases are defined in [`src/aba_model.py`](../src/aba_model.py):
`LOCAL_MODELS` (`qwen2.5-0.5b/1.5b/3b/7b/14b/32b`, `mistral-7b`, `llama3-8b`,
`gemma2-9b`, `phi3-mini`), `GROQ_MODELS`, `HF_MODELS`, `GOOGLE_MODELS`. Any
full model id can be passed directly instead of an alias.

GPU fit, single card: L40 (48 GB) takes 7B–14B in bf16 and up to ~32B with
`--load-4bit`; RTX 2080 Ti (11 GB) takes a 7B only with `--load-4bit`.

---

## Task 1 — LLM learning

| Argument | Default | Description |
| --- | --- | --- |
| `--modes MODE …` | all four | `direct`, `cot`, `guided`, `algorithm` — increasing guidance. |
| `--symbolic-only` | off | Run only the ASP-ABAlearnB reference; no LLM calls. Also writes `symbolic_traces.jsonl`. |

Every problem is **posed whole**: the prompt shows every example, and the answer is
scored on every example by `score_output` in [`src/aba_score.py`](../src/aba_score.py),
against the algorithm's run on the same problem (valid, clean, exact, agreement; see
[EXPERIMENTS.md](EXPERIMENTS.md#metrics--precise-definitions)). Before any model call
the run builds that reference for every problem and checks the instrument: the
algorithm's answer must score clean and exact, and RoLe's facts valid but not clean;
otherwise it stops. `guided` mode hands the model the RoLe facts of that same run.

---

## Task 1b — step probes

Instead of asking for a whole framework and scoring the outcome, ask for **one
transformation at a time** and score each against a Clingo or syntactic oracle.
See [EXPERIMENTS.md](EXPERIMENTS.md#step-probes--measuring-the-algorithm-not-just-the-answer).

| Argument | Default | Description |
| --- | --- | --- |
| `--probes` | off | Run step probes *instead of* the end-to-end modes. Five kinds: `role` (RoLe), `fold` (R2), `check` (the solution test), `introduce` (R3), `subsume` (R4). |
| `--with-probes` | off | Run the probes *after* the end-to-end modes, in the same process and on the same loaded model. |
| `--probes-per-kind N` | `2` | Max probes of each kind per problem. The default gives 845 over the 103-problem suite under probe prompts v3. |
| `--probe-samples K` | `1` | Samples per probe. Power comes from the number of items, not from repeated draws of one item; probes run greedy (temperature 0). |

Outputs `probes.jsonl` (one row per probe, with the model's answer, the oracle's
answer and the verdict) and `probe_summary.json`.

Read every probe against its measured no-reasoning floor
(`python analysis/null_baselines.py`). `check` and `subsume` are binary and read as
`balanced_accuracy`: a constant YES scores 0.50, but a single surface cue scores
more (v3: `check` 0.633, `subsume` 0.762).

```bash
# 845 probes, short answers; roughly a third of one mode's GPU time
python main.py --backend local --model qwen2.5-14b --benchmark 20 \
    --probes --output results/bench_qwen2.5-14b
```

---

## Task 2 — gradual semantics

| Argument | Default | Description |
| --- | --- | --- |
| `--graded` | off | Run the graded analysis: BSAF (headline) and the BAF baseline side by side. |
| `--graded-source {uniform,sample_freq,llm_elicited}` | `uniform` | Where assumption base scores come from — see [GRADED.md](GRADED.md). |
| `--graded-kernel {dfquad_prod,dfquad_min,qe_prod,qe_min}` | `dfquad_prod` | BSAF modular kernel. `dfquad_prod` is the most robust. |
| `--graded-claim-mode {max,min,avg,noisy_or}` | `max` | How a claim's strength is read from the assumption strengths. `max` is the faithful brave reading. |

---

## Output

| Argument | Default | Description |
| --- | --- | --- |
| `--output PATH` | `./results` | Directory for results and figures. |
| `--export` | off | Also write `frameworks.jsonl`, `frameworks.md`, `defeasibility.csv`. |
| `--verbose` | off | Per-step trace of the symbolic solver. |

### What a run writes

```text
<output>/
├── summary.json           the run block (provenance), metrics per mode and per tier (by_tier)
├── results_<mode>.jsonl   one row per sample: seed, prompt and problem hashes, finish,
│                          raw output and the score card; appended as scored, so a rerun
│                          into the same --output resumes
├── references.jsonl       the algorithm's answer, RoLe facts and atom statuses per problem
├── sample.md              20 seeded rows (5 per mode), each beside the algorithm's answer:
│                          read by hand before any aggregate
├── explanations.md        per-problem narrative of one answer beside the algorithm's
├── symbolic_traces.jsonl  the algorithm's trace on every problem
├── name_maps.json         anonymisation maps, for reading results back
├── frameworks.{jsonl,md}  every learned framework, mechanism-tagged        (--export)
├── defeasibility.csv      flat per-sample table                            (--export)
├── graded_results.json    BSAF vs BAF                                      (--graded)
└── figures/               valid/clean/exact by mode, error labels, clean@k heatmap,
                           complexity (PDF)
```

`results/` is a scratch directory. Runs worth keeping are promoted into
[`experiments/`](../experiments/) with a `MANIFEST.md` — see the
[experiment registry](EXPERIMENTS.md).

---

## `rescore.py` — recompute metrics without re-running the models

Every sample stores its full `raw_output`, and the benchmark is seeded, so a
finished run can be scored again offline. Use it whenever the parser, the
well-formedness check or a metric definition changes.

```bash
# rescore one run in place
python rescore.py results/bench_qwen2.5-7b

# rescore several, writing to a separate tree
python rescore.py "results/bench_*" --out rescored/
```

An end-to-end run is rebuilt from the `run` block of its `summary.json`: the dataset
is regenerated from it, and the references are recomputed. A row whose problem no
longer matches its stored hash stops the rescore. A changed prompt or changed
references are reported, and the new `run.rescored` records them. Runs that hid
examples (sets 00–03 and set 05's end-to-end half) have no `run` block and are
refused as superseded.

`--probes` rescores `probes.jsonl` instead of the end-to-end modes. Probe
generation is deterministic, so the regenerated probes are the exact items the
run was given and each stored answer can be scored again offline. Probe runs record
no dataset, so the dataset flags (`--benchmark`, `--seed`, `--anonymize`) must match
the run's; add `--probes-per-kind N` if the run did not use the default 2.

```bash
python rescore.py "results/bench_qwen2.5-*" --benchmark 20 --probes --out rescored/
```

---

## Recipes

```bash
# no API key, no GPU — smoke test the whole pipeline
python main.py --backend mock --benchmark 2 --modes direct --n-samples 1

# the symbolic reference alone, with the per-problem trace
python main.py --symbolic-only --benchmark 20 --verbose

# the full benchmark for one model on a GPU (what the cluster jobs run)
python main.py --backend local --model qwen2.5-7b --load-4bit \
    --benchmark 20 --modes direct cot guided algorithm \
    --n-samples 3 --max-tokens 1536 --export --output results/bench_qwen2.5-7b

# free API, spaced out to stay under the rate limit
python main.py --backend groq --model llama3-70b --min-interval 3 \
    --benchmark 5 --modes guided --n-samples 3

# the end-to-end floors, and a set read against them
python analysis/null_baselines.py --end-to-end --set experiments/07_e2e_whole_v4

# Task 1 + Task 2 in one pass
python main.py --backend local --model qwen2.5-7b --benchmark 10 \
    --graded --graded-source llm_elicited --export
```

On the DISI SLURM cluster, `bash cluster/submit_benchmarks.sh` chains one job
per model — see [`cluster/README.md`](../cluster/README.md).
