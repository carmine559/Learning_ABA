#!/bin/bash
# ---------------------------------------------------------------------------
# MASSIVE TESTING: can an LLM replicate the ABA-learning algorithm?
#
# CLUSTER CONSTRAINT: no job arrays AND only ONE running L40 job per user.
# Two ways to cover several models:
#
#   (a) CHAINED JOBS (preferred) - one job per model, linked with SLURM
#       dependencies so they run strictly one-after-another, each with its
#       own 24 h budget:        bash cluster/submit_benchmarks.sh
#
#   (b) ONE SEQUENTIAL JOB - MODEL may be a space-separated list; the models
#       run in a loop INSIDE this single job (all must fit in --time):
#       sbatch --export=ALL,MODEL="qwen2.5-3b qwen2.5-7b" cluster/run_benchmark.sbatch
#
# With no MODEL given, defaults to qwen2.5-7b.
#
# Each job runs the full stratified benchmark suite, anonymised (default):
#   t1_mono / t2_defeas / t3_noise / t4_domain / t5_twopath
# Explainable outputs land in results/bench_<model>/ :
#   summary.json (with per-tier breakdown), results_<mode>.jsonl,
#   explanations.md, frameworks.{md,jsonl}, defeasibility.csv, name_maps.json
# ---------------------------------------------------------------------------
#SBATCH --job-name=aba-bench
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=carmine.santella@studio.unibo.it
#SBATCH --time=24:00:00
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
# export HF_TOKEN=hf_xxx        # only for gated models (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate

MODEL="${MODEL:-qwen2.5-7b}"     # single model OR space-separated list
BENCH_N="${BENCH_N:-20}"         # problems PER TIER (5 tiers)
N_SAMPLES="${N_SAMPLES:-3}"      # LLM samples per problem (pass@k)

python3 -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"

for m in $MODEL; do
    OUT="results/bench_${m}"
    echo "[job $SLURM_JOB_ID] model=$m bench_n=$BENCH_N samples=$N_SAMPLES"

    # A failure on one model must not kill the remaining ones (set -e).
    if python3 main.py \
        --backend local --model "$m" \
        --benchmark "$BENCH_N" \
        --modes direct cot guided algorithm \
        --n-samples "$N_SAMPLES" --max-tokens 1536 \
        --export \
        --output "$OUT"
    then
        echo "DONE $m -> $OUT"
    else
        echo "FAILED $m (exit $?) - continuing with the next model"
    fi
done

# Optional Task-2 pass on the same suite (adds graded BSAF/BAF columns):
#   append   --graded   (uniform base scores, no extra LLM calls)
