#!/bin/bash
# One end-to-end run of one model: Task 1 (four modes) + Task 2 + export.
#   sbatch cluster/run.sbatch
# rtx2080 (11 GB) fits up to 3B in 4-bit; 7B and larger need the l40 preset.
#SBATCH --job-name=tesi
#SBATCH --mail-type=ALL
#SBATCH --mail-user=carmine.santella@studio.unibo.it
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4                # rtx2080 nodes have 4 cores; l40: 8
#SBATCH --mem=16G
#SBATCH --partition=rtx2080              # rtx2080 | l40
#SBATCH --gres=gpu:1                     # required as is: one GPU per node
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail
export HF_HOME="/scratch.hpc/$USER/hf_cache"
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# export HF_TOKEN=hf_xxx                 # gated models only (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate
python3 -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"

# rtx2080 preset
MODEL=qwen2.5-3b
EXTRA="--load-4bit --max-tokens 1024"
# l40 preset
# MODEL=qwen2.5-7b
# EXTRA="--max-tokens 1536"

OUT="results/${MODEL}"
python3 main.py \
    --backend local --model "$MODEL" $EXTRA \
    --modes direct cot guided algorithm \
    --n-samples 5 \
    --graded --graded-source llm_elicited \
    --export \
    --output "$OUT"

echo "DONE -> $OUT"
