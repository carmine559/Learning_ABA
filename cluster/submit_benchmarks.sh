#!/bin/bash
# ---------------------------------------------------------------------------
# Submit benchmark jobs on a cluster that allows only ONE running L40 job per
# user: jobs are CHAINED with SLURM dependencies (afterany), so they execute
# strictly one-after-another, each with its own full --time budget. Only the
# first runs immediately; the rest sit PENDING (Dependency) until their turn.
#
# Run on giano.cs.unibo.it:
#     cd /scratch.hpc/$USER/Learning_aba
#     bash cluster/submit_benchmarks.sh              # end-to-end modes
#     SPLIT_MODES=1 bash cluster/submit_benchmarks.sh   # one job PER MODE
#     PROBES=1 bash cluster/submit_benchmarks.sh     # step probes
#
# WHY SPLIT_MODES EXISTS
#   Measured GPU time for the full 1236 calls: 3B 1.1 h, 7B 3.7 h, 14B 7.3 h —
#   roughly linear in parameters. 32B extrapolates to ~17 h in bf16, and bnb
#   nf4 runs 1.5-2.5x slower, so a four-mode 32B job is 25-42 h against a 24 h
#   wall limit. One job per mode is 4-14 h and fits. The per-mode jobs write
#   into the same results/bench_<model>/ directory, so the result is identical
#   to a single job's output.
#
# MODELS / MODES / EXTRA can all be overridden from the environment, e.g.
#     MODELS="qwen2.5-32b" EXTRA="--load-4bit" SPLIT_MODES=1 \
#         bash cluster/submit_benchmarks.sh
# ---------------------------------------------------------------------------
set -euo pipefail

read -r -a MODELS <<< "${MODELS:-qwen2.5-3b qwen2.5-7b mistral-7b qwen2.5-14b}"
read -r -a MODES  <<< "${MODES:-direct cot guided algorithm}"
EXTRA="${EXTRA:-}"                 # e.g. --load-4bit  (required for 32B)
SPLIT_MODES="${SPLIT_MODES:-0}"
PROBES="${PROBES:-0}"

submit() {   # $1 = job name, $2 = extra --export assignments
    local name="$1" exports="$2" jid
    if [ -z "${prev:-}" ]; then
        jid=$(sbatch --parsable --job-name="$name" \
                     --export="ALL,${exports}" cluster/run_benchmark.sbatch)
    else
        # afterany: start when the previous job ENDS, even if it failed, so one
        # bad model never blocks the rest of the chain.
        jid=$(sbatch --parsable --job-name="$name" \
                     --dependency="afterany:${prev}" \
                     --export="ALL,${exports}" cluster/run_benchmark.sbatch)
    fi
    prev="$jid"
    echo "submitted ${name} as job ${jid}"
    n_jobs=$((n_jobs + 1))
}

prev=""
n_jobs=0
for m in "${MODELS[@]}"; do
    if [ "$PROBES" = "1" ]; then
        submit "probe-${m}" "MODEL=${m},PROBES=1,EXTRA=${EXTRA}"
    elif [ "$PROBES" = "both" ]; then
        # One job per model covering the modes AND the probes, on a single load
        # of the weights. Incompatible with SPLIT_MODES, which would re-run the
        # probes once per mode.
        submit "bench-${m}" "MODEL=${m},MODES=${MODES[*]},PROBES=both,EXTRA=${EXTRA}"
    elif [ "$SPLIT_MODES" = "1" ]; then
        for mode in "${MODES[@]}"; do
            submit "bench-${m}-${mode}" "MODEL=${m},MODES=${mode},EXTRA=${EXTRA}"
        done
    else
        submit "bench-${m}" "MODEL=${m},MODES=${MODES[*]},EXTRA=${EXTRA}"
    fi
done

echo "Chain submitted (${n_jobs} jobs, one runs at a time)."
echo "Monitor with: squeue -u \$USER   (PENDING/Dependency = waiting its turn)"
if [ "$SPLIT_MODES" = "1" ]; then
    echo
    echo "Per-mode chain: each job leaves a summary.json for its own mode only."
    echo "Rebuild the merged summary when the chain finishes (CPU, seconds):"
    for m in "${MODELS[@]}"; do
        echo "    python3 rescore.py results/bench_${m} --benchmark 20"
    done
fi
