#!/bin/bash
# ---------------------------------------------------------------------------
# SFT ablation on one L40: train an arm, then evaluate it, in one job (one L40
# job per user, and a long queue).
#
#   sbatch cluster/train_sft.sbatch                                  # endpoint
#   sbatch --export=ALL,ARMS="endpoint base" cluster/train_sft.sbatch
#   sbatch --export=ALL,ARMS=trace cluster/train_sft.sbatch
#   sbatch --export=ALL,ARMS=endpoint,MATCH=tokens cluster/train_sft.sbatch
#
# ARMS runs in order: endpoint | trace (train, then evaluate) | base (the model
# without adapter, same decoding). Adapters in runs/<run>/, generations and
# scores in results/sft/<run>/. The job is idempotent: resubmitted, it skips a
# finished adapter, resumes from the last checkpoint, and continues generation.
#
# Once, on giano: pip3 install --no-cache-dir -r requirements-train.txt (in
# venv/); corpus/v1/*.jsonl and TOKENS.json synced; Qwen2.5-7B-Instruct cached.
# ---------------------------------------------------------------------------
#SBATCH --job-name=sft
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=carmine.santella@studio.unibo.it
#SBATCH --time=2-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --partition=l40
#SBATCH --gres=gpu:1
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail

export HF_HOME="/scratch.hpc/$USER/hf_cache"
export HF_HUB_OFFLINE=1                  # the model is cached: never download in a GPU job
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader

ARMS="${ARMS:-endpoint}"
MATCH="${MATCH:-steps}"                  # steps (primary) | tokens (secondary)

for arm in $ARMS; do
    echo "[job $SLURM_JOB_ID] arm=$arm match=$MATCH"
    if [ "$arm" = base ]; then
        python3 eval_sft.py --out results/sft/base
        continue
    fi
    run="sft_${arm}"
    [ "$MATCH" = tokens ] && run="${run}_tokens"
    if [ ! -f "runs/$run/adapter/adapter_model.safetensors" ]; then
        RESUME=""
        compgen -G "runs/$run/checkpoint-*" > /dev/null && RESUME="--resume"
        python3 train_sft.py --arm "$arm" --match "$MATCH" --out "runs/$run" $RESUME
    fi
    python3 eval_sft.py --adapter "runs/$run/adapter" --out "results/sft/$run"
done
