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
# export HF_TOKEN=hf_xxx        # only for gated models (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate

MODEL="${MODEL:-qwen2.5-7b}"     # single model OR space-separated list
BENCH_N="${BENCH_N:-20}"         # problems PER TIER (5 tiers)
N_SAMPLES="${N_SAMPLES:-3}"      # LLM samples per problem (pass@k)
MODES="${MODES:-direct cot guided algorithm}"   # subset, for per-mode jobs
EXTRA="${EXTRA:-}"               # e.g. --load-4bit   (needed for 32B on an L40)
PROBES="${PROBES:-0}"            # 1 = probes instead of the modes
                                 # both = the modes AND then the probes

# Per-mode jobs write into the SAME results/bench_<model>/ directory, one
# results_<mode>.jsonl each. Required for 32B: the full four-mode run is 25-42 h
# in 4-bit against a 24 h wall limit, while one mode is 4-14 h.
#
# NOTE: each job also writes summary.json covering ONLY its own mode, so the
# last job in the chain leaves a single-mode summary behind. Rebuild the merged
# one afterwards, on CPU, in seconds:
#     python3 rescore.py results/bench_<model> --benchmark 20

python3 -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"

for m in $MODEL; do
    OUT="results/bench_${m}"
    echo "[job $SLURM_JOB_ID] model=$m bench_n=$BENCH_N samples=$N_SAMPLES" \
         "modes='$MODES' extra='$EXTRA' probes=$PROBES"

    if [ "$PROBES" = "1" ]; then
        # Step probes: one ASP-ABAlearnB decision per prompt, each with a
        # Clingo or syntactic oracle. Short answers, so --max-tokens is small
        # and k=1 (power comes from the ~780 probe items, not repeated draws).
        CMD=(python3 main.py --backend local --model "$m"
             --benchmark "$BENCH_N" --probes --max-tokens 512
             --output "$OUT")
    else
        # PROBES=both appends the probes to the SAME process, so the weights are
        # loaded once for both halves of the run.
        WITH_PROBES=""
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

# Optional Task-2 pass on the same suite (adds graded BSAF/BAF columns):
#   append   --graded   (uniform base scores, no extra LLM calls)
