# Running the experiments on the DISI GPU cluster

This runs the project **locally on a GPU** (`--backend local`): the chosen
HuggingFace model is downloaded onto the L40/RTX card and inference happens
on-device, no API. Scheduling is via SLURM from `giano.cs.unibo.it`.

## 0. Why everything goes in `/scratch.hpc`

The home quota is **400 MB**, but PyTorch (~2–3 GB) and the models (7B ≈ 15 GB in
bf16) are far larger. So the **venv and the model cache live in
`/scratch.hpc/$USER/`**, never in home. (Scratch files are deleted only if not
accessed for 40 days.)

## 1. One-time setup (on `giano`)

```bash
# from your laptop: copy the project into scratch
rsync -av --exclude .venv --exclude results \
      Learning_aba/ giano.cs.unibo.it:/scratch.hpc/$USER/Learning_aba/

# on giano: build the venv + install deps (torch cu118, transformers, clingo…)
ssh giano.cs.unibo.it
cd /scratch.hpc/$USER/Learning_aba
bash cluster/setup_env.sh
```

If a script reports `bad interpreter` / `\r` errors (Windows line endings), run:
`sed -i 's/\r$//' cluster/*.sh cluster/*.sbatch`.

## 2. Submit a run

Edit the `--mail-user` line in `cluster/run.sbatch`, then:

```bash
cd /scratch.hpc/$USER/Learning_aba
sbatch cluster/run.sbatch
```

This one job runs **Task 1** (LLM learning, all four modes, anonymised) +
**Task 2** (gradual semantics) + export, and writes everything under
`results/<model>/`. You get e-mails at start/end/error; logs stream to
`slurm-<job>-<id>.out`.

## 3. Run several models at once (4× L40)

```bash
sbatch cluster/run_sweep.sbatch     # a job array: qwen2.5-7b, llama3-8b, mistral-7b, gemma2-9b
```

Each array task takes one GPU, so with four L40s the four models run in parallel.

## 3b. MASSIVE testing — the stratified benchmark suite

```bash
sbatch cluster/run_benchmark.sbatch   # 4 models x 103 anonymised problems x 4 modes
```

This is the headline Task-1 experiment: `--benchmark N` generates **N problems
per tier**, where each tier isolates one capability of the ASP-ABAlearnB
algorithm (all anonymised, so the LLM cannot use world knowledge):

| Tier | Isolates | Structure |
| --- | --- | --- |
| `t1_mono` | Folding only | no exceptions, monotonic rule suffices |
| `t2_defeas` | Assumption introduction | one exception to defeat |
| `t3_noise` | Distractor robustness | extra irrelevant predicates |
| `t4_domain` | Domain-size scaling | 12 constants |
| `t5_twopath` | Multiple derivation paths | two defeasible rules needed |

`summary.json` then contains a **per-tier gen@k breakdown** (also printed as a
table), so the result is not "the LLM scores 40%" but "*it can fold but fails
at assumption introduction*" — the explainable answer to whether it replicates
the algorithm. Per-problem narratives are in `explanations.md`, every learned
framework (mechanism-tagged, de-anonymisable via `name_maps.json`) in
`frameworks.md`. Every generated problem is validated at generation time:
symbolically solvable, ≥2 examples per side, no E+/E− overlap, no duplicates.

Runtime scales as `5·N + 3` problems × modes × samples; with `BENCH_N=20`,
`--n-samples 3`, 4 modes → ~1236 calls ≈ 6–10 h per model on an L40 (7B). Trim
`BENCH_N` or the mode list for a faster pass.

## 4. Monitor

```bash
squeue -u $USER                 # queued / running jobs
tail -f slurm-aba-learn-*.out   # live log
sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS   # after it finishes
scancel <jobid>                 # cancel
```

## Model ↔ GPU fit (one GPU per job)

| Partition | GPU | VRAM | Recommended model | `--load-4bit` |
| --- | --- | --- | --- | --- |
| `l40` | Nvidia L40 | 48 GB | 7B–14B (bf16); 32B in 4-bit | for ≥32B |
| `rtx2080` | RTX 2080 Ti | 11 GB | **≤ 3B** (`qwen2.5-3b`, `1.5b`, `phi3-mini`) | yes |

> A **7B does NOT fit the rtx2080**, even in 4-bit: the 4-bit weights (~5.5 GB) +
> CUDA context (~1.5 GB) + the long `algorithm` prompt + KV cache leave no room,
> and a transient ~1 GB copy of the embedding tips it into **CUDA OutOfMemory**.
> Use a ≤3B model on `rtx2080`, or run 7B+ on `l40`.

On `rtx2080` use `#SBATCH --cpus-per-task=4` (quad-core nodes); on `l40` use 8.
Model aliases (`qwen2.5-0.5b/1.5b/3b/7b/14b/32b`, `phi3-mini`, `llama3-8b`,
`mistral-7b`, `gemma2-9b`) are in `src/aba_model.py` (`LOCAL_MODELS`); any full HF
id also works.

### CUDA out of memory?

1. Smaller model (`qwen2.5-3b` → `1.5b` → `0.5b`) or move to `l40`.
2. Lower `--max-tokens` (e.g. 768) — KV cache scales with prompt + output length.
3. Lower `--n-samples`.
4. Keep `--load-4bit` on `rtx2080`. The loader already sets
   `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` and pins the model to one
   GPU (no `device_map="auto"` hooks) to minimise fragmentation and avoid the
   parameter deepcopy.

## Gated models (Llama, Gemma)

These require accepting the licence on HuggingFace and a token. Add to the sbatch
before the `python3` call:

```bash
export HF_TOKEN=hf_xxxxxxxx      # or run `huggingface-cli login` once on giano
```

Qwen, Mistral and Phi are ungated — easiest to start with `--model qwen2.5-3b`
(rtx2080) or `--model qwen2.5-7b` (l40).

## How the flags map to the experiments

| Experiment | Flags (added to `--backend local --model …`) |
| --- | --- |
| Task 1 — LLM learning | `--modes direct cot guided algorithm --n-samples 5` (anonymised by default) |
| Task 2 — gradual semantics | add `--graded --graded-source llm_elicited` |
| Reporting | add `--export` (frameworks + figures + narratives) |

Drop `--graded-source llm_elicited` (→ default `uniform`) for a faster Task 2 with
no extra LLM calls. Use `--no-anonymize` only for a future Task 3 (RAG) run.
