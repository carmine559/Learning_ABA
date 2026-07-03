#!/bin/bash
# ---------------------------------------------------------------------------
# MASSIVE TESTING: can an LLM replicate the ABA-learning algorithm?
#
# Job array: one model per GPU (4x L40 -> all four run in parallel).
# Each task runs the full stratified benchmark suite, anonymised (default):
#   t1_mono     folding only (monotonic rule suffices)
#   t2_defeas   assumption introduction (one exception)
#   t3_noise    distractor robustness (extra noise predicates)
#   t4_domain   domain-size scaling (12 constants)
#   t5_twopath  two independent defeasible derivation paths
#
# With BENCH_N=20: 5x20 + 3 builtin = 103 problems x 4 modes x 3 samples
# = ~1236 LLM calls per model  (~6-10 h on an L40 with a 7B model).
#
# Explainable outputs per model, under results/bench_<model>/:
#   summary.json       overall + per-mode metrics AND per-tier breakdown
#   results_<mode>.jsonl   every sample: raw LLM output + error class
#   explanations.md    per-problem narrative of HOW the model generalised
#   frameworks.{md,jsonl}  every learned framework, mechanism-tagged
#   defeasibility.csv  flat table for stats
#   name_maps.json     anonymisation maps (de-anonymise for reading)
#
# Submit from giano.cs.unibo.it:
#     cd /scratch.hpc/$USER/Learning_aba
#     sbatch cluster/run_benchmark.sbatch
# ---------------------------------------------------------------------------
#SBATCH --job-name=aba-bench
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=carmine.santella@studio.unibo.it     # <-- EDIT
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=l40
#SBATCH --gres=gpu:1
#SBATCH --array=0-3
#SBATCH --output=slurm-%x-%a-%j.out

set -euo pipefail

export HF_HOME="/scratch.hpc/$USER/hf_cache"
export TOKENIZERS_PARALLELISM=false
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
# export HF_TOKEN=hf_xxx        # only for gated models (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate

# Ungated models spanning a size axis (does capability scale with size?).
MODELS=(qwen2.5-3b qwen2.5-7b mistral-7b qwen2.5-14b)
MODEL="${MODELS[$SLURM_ARRAY_TASK_ID]}"

BENCH_N=20            # problems PER TIER (5 tiers). Lower for a faster pass.
N_SAMPLES=3           # LLM samples per problem (pass@k)
OUT="results/bench_${MODEL}"

echo "[array $SLURM_ARRAY_TASK_ID] model=$MODEL bench_n=$BENCH_N samples=$N_SAMPLES"
python3 -c "import torch; print('GPU:', torch.cuda.get_device_name(0))"

python3 main.py \
    --backend local --model "$MODEL" \
    --benchmark "$BENCH_N" \
    --modes direct cot guided algorithm \
    --n-samples "$N_SAMPLES" --max-tokens 1536 \
    --export \
    --output "$OUT"

# Optional Task-2 pass on the same suite (adds graded BSAF/BAF columns):
#   append   --graded   (uniform base scores, no extra LLM calls)

echo "DONE $MODEL -> $OUT"
