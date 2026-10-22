#!/bin/bash
# Arm S2: train step by step, then evaluate it chained (v1, permuted) and at gold states.
#   sbatch cluster/stepwise_sft.sbatch
#   sbatch --export=ALL,SEED=1 cluster/stepwise_sft.sbatch   # a replicate: runs/sft_step_s1, s2_s1/
# Resubmitted, it skips a finished adapter or evaluation, resumes training from the last
# checkpoint and continues an evaluation where it stopped. Check first, on the login node:
#   python3 sft/train_step.py --out runs/sft_step --dry-run        # with SEED: add --seed
#   python3 sft/eval_stepwise.py --protocol chained --dry-run --out /tmp/s2
# sft/compare_step.py is run after the job, once sample.md and calls_sample.md are read.
#SBATCH --job-name=sft-step
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

SEED=${SEED:-0}
RUN=runs/sft_step NAME=s2                # seed 0: the registered run
if [ "$SEED" != 0 ]; then
    RUN=runs/sft_step_s$SEED NAME=s2_s$SEED
fi
echo "[job $SLURM_JOB_ID] arm s2, seed $SEED, run $RUN"
if [ ! -f "$RUN/adapter/adapter_model.safetensors" ]; then
    RESUME=""
    compgen -G "$RUN/checkpoint-*" > /dev/null && RESUME="--resume"
    python3 sft/train_step.py --out "$RUN" --seed "$SEED" $RESUME
fi

evaluate() {                             # protocol, out, then extra arguments
    local protocol=$1 out=$2
    shift 2
    if [ -f "$out/step_summary.json" ]; then
        echo "$out done"
        return
    fi
    python3 sft/eval_stepwise.py --protocol "$protocol" --adapter "$RUN/adapter" --out "$out" "$@"
}
evaluate chained "results/sft-step/$NAME/chained"
evaluate chained "results/sft-step-permuted/$NAME" --corpus corpus/v1-permuted
evaluate gold "results/sft-step/$NAME/gold"
