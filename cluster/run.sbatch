#!/bin/bash
# ---------------------------------------------------------------------------
# Run ONE experiment on the DISI GPU cluster (one model, one GPU).
# Submit from giano.cs.unibo.it:
#     cd /scratch.hpc/$USER/Learning_aba
#     sbatch cluster/run.sbatch
#
# Pick a partition + model that FIT (one GPU per job):
#   rtx2080 (11 GB): small models only -> qwen2.5-3b / 1.5b / phi3-mini (+ --load-4bit)
#   l40     (48 GB): 7B-14B in bf16; 32B with --load-4bit
# A 7B model does NOT fit the rtx2080 even in 4-bit once you add the long prompt
# + KV cache + CUDA context -> CUDA OutOfMemory. Use l40 for 7B+.
# ---------------------------------------------------------------------------
#SBATCH --job-name=tesi
#SBATCH --mail-type=ALL
#SBATCH --mail-user=carmine.santella@studio.unibo.it     # <-- EDIT
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4                      # rtx2080 = 4 cores; for l40 use 8
#SBATCH --mem=16G                              # loading needs headroom; nodes have 44-64 GB
#SBATCH --partition=rtx2080                    # rtx2080 (11 GB) | l40 (48 GB)
#SBATCH --gres=gpu:1                           # MANDATORY, leave as-is (1 GPU/node)
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

# --- environment -----------------------------------------------------------
# Home quota is only 400 MB, so the HF model cache MUST live in scratch.
export HF_HOME="/scratch.hpc/$USER/hf_cache"
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True   # less fragmentation
# export HF_TOKEN=hf_xxx        # ONLY needed for gated models (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate
python3 -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"

# --- experiment ------------------------------------------------------------
# ACTIVE preset: rtx2080 (11 GB) -> small model, 4-bit, shorter outputs.
MODEL=qwen2.5-3b
EXTRA="--load-4bit --max-tokens 1024"

# l40 (48 GB) preset -> comment the two lines above and uncomment these:
# MODEL=qwen2.5-7b
# EXTRA="--max-tokens 1536"

OUT="results/${MODEL}"

# Task 1 (learn, anonymised by default) + Task 2 (gradual) + export, one job:
python3 main.py \
    --backend local --model "$MODEL" $EXTRA \
    --modes direct cot guided algorithm \
    --n-samples 5 \
    --graded --graded-source llm_elicited \
    --export \
    --output "$OUT"

echo "DONE -> $OUT"
