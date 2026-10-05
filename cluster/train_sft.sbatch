#!/bin/bash
# SFT: train an arm, then evaluate it, in one job.
#   sbatch cluster/train_sft.sbatch                                     # endpoint
#   sbatch --export=ALL,ARMS="endpoint base" cluster/train_sft.sbatch   # + the base model
#   sbatch --export=ALL,ARMS=trace cluster/train_sft.sbatch
#   sbatch --export=ALL,ARMS=endpoint,MATCH=tokens cluster/train_sft.sbatch
# Resubmitted, it skips a finished adapter, resumes training from the last
# checkpoint and continues generation. Check the corpus before submitting:
#   python3 -c "from pathlib import Path; from src.aba_train import load_audit; load_audit(Path('corpus/v1'), 'qwen2.5-7b'); print('ok')"
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
export HF_HUB_OFFLINE=1                  # cached by cluster/prefetch_model.sh
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate
nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader

ARMS="${ARMS:-endpoint}"                 # endpoint | trace | base, run in order
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
