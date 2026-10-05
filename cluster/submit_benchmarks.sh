#!/bin/bash
# Chain one benchmark job per model: one L40 job per user runs at a time.
#   bash cluster/submit_benchmarks.sh                  # the four modes
#   PROBES=1 bash cluster/submit_benchmarks.sh         # step probes
#   MODELS="qwen2.5-32b" EXTRA="--load-4bit" SPLIT_MODES=1 bash cluster/submit_benchmarks.sh
# SPLIT_MODES=1 submits one job per mode (32B in 4-bit takes 25-42 h for all four).
set -euo pipefail

read -r -a MODELS <<< "${MODELS:-qwen2.5-3b qwen2.5-7b mistral-7b qwen2.5-14b}"
read -r -a MODES  <<< "${MODES:-direct cot guided algorithm}"
EXTRA="${EXTRA:-}"
SPLIT_MODES="${SPLIT_MODES:-0}"
PROBES="${PROBES:-0}"                    # 1: probes only; both: modes, then probes

submit() {   # $1 = job name, $2 = extra --export assignments
    local name="$1" exports="$2" jid
    if [ -z "${prev:-}" ]; then
        jid=$(sbatch --parsable --job-name="$name" \
                     --export="ALL,${exports}" cluster/run_benchmark.sbatch)
    else
        # afterany: the next job starts even if this one failed
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
        # not with SPLIT_MODES, which would rerun the probes once per mode
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
    echo "When the chain ends, merge each model's summary (CPU, seconds):"
    for m in "${MODELS[@]}"; do
        echo "    python3 rescore.py results/bench_${m} --benchmark 20"
    done
fi
