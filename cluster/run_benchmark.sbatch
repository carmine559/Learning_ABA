#!/bin/bash
# The stratified benchmark suite (anonymised) for one model, or several in sequence.
#   sbatch --export=ALL,MODEL=qwen2.5-7b cluster/run_benchmark.sbatch
#   sbatch --export=ALL,MODEL="qwen2.5-3b qwen2.5-7b" cluster/run_benchmark.sbatch
# One job per model, chained: bash cluster/submit_benchmarks.sh.
# Output in results/bench_<model>/. Jobs split by mode each leave a one-mode
# summary.json; merge them with: python3 rescore.py results/bench_<model> --benchmark 20
#SBATCH --job-name=aba-bench
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=carmine.santella@studio.unibo.it
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=l40
#SBATCH --gres=gpu:1
#SBATCH --output=slurm-%x-%j.out

set -euo pipefail
export HF_HOME="/scratch.hpc/$USER/hf_cache"
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# export HF_TOKEN=hf_xxx                 # gated models only (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate

MODEL="${MODEL:-qwen2.5-7b}"             # one alias, or a space-separated list
BENCH_N="${BENCH_N:-20}"                 # problems per tier
N_SAMPLES="${N_SAMPLES:-3}"              # samples per problem
MODES="${MODES:-direct cot guided algorithm}"
EXTRA="${EXTRA:-}"                       # e.g. --load-4bit (32B)
PROBES="${PROBES:-0}"                    # 1: step probes only; both: modes, then probes

python3 -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"

for m in $MODEL; do
    OUT="results/bench_${m}"
    echo "[job $SLURM_JOB_ID] model=$m bench_n=$BENCH_N samples=$N_SAMPLES" \
         "modes='$MODES' extra='$EXTRA' probes=$PROBES"
    if [ "$PROBES" = "1" ]; then
        CMD=(python3 main.py --backend local --model "$m"
             --benchmark "$BENCH_N" --probes --max-tokens 512
             --output "$OUT")
    else
        WITH_PROBES=""                   # both: one weight load for modes and probes
        [ "$PROBES" = "both" ] && WITH_PROBES="--with-probes"
        CMD=(python3 main.py --backend local --model "$m"
             --benchmark "$BENCH_N" --modes $MODES
             --n-samples "$N_SAMPLES" --max-tokens 1536 --export
             $WITH_PROBES --output "$OUT")
    fi
    # shellcheck disable=SC2086
    if "${CMD[@]}" $EXTRA; then
        echo "DONE $m -> $OUT"
    else
        echo "FAILED $m (exit $?) - continuing with the next model"
    fi
done
