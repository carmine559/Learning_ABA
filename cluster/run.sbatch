#!/bin/bash
# ---------------------------------------------------------------------------
# Run ONE experiment on the DISI GPU cluster (one model, one GPU).
# Submit from giano.cs.unibo.it:
#     cd /scratch.hpc/$USER/Learning_aba
#     sbatch cluster/run.sbatch
# ---------------------------------------------------------------------------
#SBATCH --job-name=tesi
#SBATCH --mail-type=ALL
#SBATCH --mail-user=carmine.santella@studio.unibo.it     # <-- EDIT
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4                      # l40 = 8 cores; for rtx2080 use 4
#SBATCH --mem=10G
#SBATCH --partition=rtx2080                      # or: rtx2080 (then add --load-4bit)
#SBATCH --gres=gpu:1                           # MANDATORY, leave as-is (1 GPU/node)
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

# --- environment -----------------------------------------------------------
# Home quota is only 400 MB, so the HF model cache MUST live in scratch.
export HF_HOME="/scratch.hpc/$USER/hf_cache"
export TOKENIZERS_PARALLELISM=false
# export HF_TOKEN=hf_xxx        # ONLY needed for gated models (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate
python3 -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"

# --- experiment ------------------------------------------------------------
MODEL=qwen2.5-7b                 # fits an L40 in bf16; aliases in src/aba_model.py
OUT="results/${MODEL}"

# Task 1 (learn, anonymised by default) + Task 2 (gradual) + export, one job:
python3 main.py \
    --backend local --model "$MODEL" \
    --modes direct cot guided algorithm \
    --n-samples 5 --max-tokens 1536 \
    --graded --graded-source llm_elicited \
    --load-4bit \
    --export \
    --output "$OUT"

# Big model on one L40? add 4-bit, e.g.:
#     MODEL=qwen2.5-32b ; python3 main.py --backend local --model $MODEL --load-4bit ...
# On the rtx2080 partition (11 GB) any 7B needs --load-4bit.
echo "DONE -> $OUT"
