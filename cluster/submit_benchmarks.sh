#!/bin/bash
# ---------------------------------------------------------------------------
# Submit the benchmark for several models on a cluster that allows only ONE
# running L40 job per user: the jobs are CHAINED with SLURM dependencies
# (afterany), so they execute strictly one-after-another, each with its own
# full --time budget. Only the first job runs immediately; the others sit in
# the queue as PENDING (Dependency) until their predecessor finishes.
#
# Run on giano.cs.unibo.it:
#     cd /scratch.hpc/$USER/Learning_aba
#     bash cluster/submit_benchmarks.sh
#
# If the cluster also limits the number of QUEUED jobs, fall back to one
# sequential job instead (models looped inside a single job, shared 24 h):
#     sbatch --export=ALL,MODEL="qwen2.5-3b qwen2.5-7b mistral-7b" \
#            cluster/run_benchmark.sbatch
# ---------------------------------------------------------------------------
set -euo pipefail

MODELS=(qwen2.5-3b qwen2.5-7b mistral-7b qwen2.5-14b)

prev=""
for m in "${MODELS[@]}"; do
    if [ -z "$prev" ]; then
        prev=$(sbatch --parsable --job-name="bench-${m}" \
                      --export=ALL,MODEL="$m" \
                      cluster/run_benchmark.sbatch)
    else
        # afterany: start when the previous job ENDS (even if it failed),
        # so one bad model never blocks the rest of the chain.
        prev=$(sbatch --parsable --job-name="bench-${m}" \
                      --dependency="afterany:${prev}" \
                      --export=ALL,MODEL="$m" \
                      cluster/run_benchmark.sbatch)
    fi
    echo "submitted bench-${m} as job ${prev}"
done

echo "Chain submitted (${#MODELS[@]} jobs, one runs at a time)."
echo "Monitor with: squeue -u \$USER   (PENDING/Dependency = waiting its turn)"