#!/bin/bash
# ---------------------------------------------------------------------------
# Run SEVERAL models in parallel, one per GPU, via a SLURM job array.
# With 4x L40 the four array tasks run concurrently (one GPU each).
#     cd /scratch.hpc/$USER/Learning_aba
#     sbatch cluster/run_sweep.sbatch
# ---------------------------------------------------------------------------
#SBATCH --job-name=aba-sweep
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=nome.cognome@unibo.it     # <-- EDIT
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=l40
#SBATCH --gres=gpu:1
#SBATCH --array=0-3                            # one task per model below
#SBATCH --output=slurm-%x-%a-%j.out           # %a = array index

set -euo pipefail

export HF_HOME="/scratch.hpc/$USER/hf_cache"
export TOKENIZERS_PARALLELISM=false
# export HF_TOKEN=hf_xxx        # for gated models (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate

# One model per array index. All of these fit an L40 (48 GB) in bf16.
MODELS=(qwen2.5-7b llama3-8b mistral-7b gemma2-9b)
MODEL="${MODELS[$SLURM_ARRAY_TASK_ID]}"
OUT="results/${MODEL}"

echo "[array $SLURM_ARRAY_TASK_ID] model=$MODEL gpu=$(python3 -c 'import torch;print(torch.cuda.get_device_name(0))')"

python3 main.py \
    --backend local --model "$MODEL" \
    --modes direct cot guided algorithm \
    --n-samples 5 --max-tokens 1536 \
    --graded --graded-source llm_elicited \
    --export \
    --output "$OUT"

echo "DONE $MODEL -> $OUT"
