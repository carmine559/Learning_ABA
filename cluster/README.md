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

## 4. Monitor

```bash
squeue -u $USER                 # queued / running jobs
tail -f slurm-aba-learn-*.out   # live log
sacct -j <jobid> --format=JobID,State,Elapsed,MaxRSS   # after it finishes
scancel <jobid>                 # cancel
```

## Model ↔ GPU fit (one GPU per job)

| Partition | GPU | VRAM | Fits in bf16 | With `--load-4bit` |
| --- | --- | --- | --- | --- |
| `l40` | Nvidia L40 | 48 GB | 7B–14B | up to ~32B |
| `rtx2080` | RTX 2080 Ti | 11 GB | — | 7B (nf4) only |

On `rtx2080`, add `--load-4bit` **and** set `#SBATCH --cpus-per-task=4` (quad-core
nodes). Model aliases (`qwen2.5-7b/14b/32b`, `llama3-8b`, `mistral-7b`,
`gemma2-9b`, `phi3-mini`) are defined in `src/aba_model.py` (`LOCAL_MODELS`); any
full HF id also works.

## Gated models (Llama, Gemma)

These require accepting the licence on HuggingFace and a token. Add to the sbatch
before the `python3` call:

```bash
export HF_TOKEN=hf_xxxxxxxx      # or run `huggingface-cli login` once on giano
```

Qwen and Mistral are ungated — easiest to start with `--model qwen2.5-7b`.

## How the flags map to the experiments

| Experiment | Flags (added to `--backend local --model …`) |
| --- | --- |
| Task 1 — LLM learning | `--modes direct cot guided algorithm --n-samples 5` (anonymised by default) |
| Task 2 — gradual semantics | add `--graded --graded-source llm_elicited` |
| Reporting | add `--export` (frameworks + figures + narratives) |

Drop `--graded-source llm_elicited` (→ default `uniform`) for a faster Task 2 with
no extra LLM calls. Use `--no-anonymize` only for a future Task 3 (RAG) run.
