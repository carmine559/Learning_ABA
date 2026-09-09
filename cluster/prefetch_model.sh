#!/bin/bash
# ---------------------------------------------------------------------------
# Download model weights into the scratch HF cache BEFORE submitting a GPU job.
#
# WHY: nothing in the pipeline pre-fetches, so weights are pulled from the Hub
# INSIDE the GPU job, unauthenticated and rate-limited (see
# slurm-bench-qwen2.5-14b-68599.out:3), spending the job's 24 h wall clock on a
# download. For Qwen2.5-32B that is ~65 GB — enough to lose a whole job.
#
# Run on giano.cs.unibo.it (login node, no GPU needed):
#     cd /scratch.hpc/$USER/Learning_aba
#     bash cluster/prefetch_model.sh qwen2.5-32b
#
# Home quota is 400 MB, so the cache MUST live in scratch.
# ---------------------------------------------------------------------------
set -euo pipefail

ALIAS="${1:-qwen2.5-32b}"

export HF_HOME="/scratch.hpc/$USER/hf_cache"
mkdir -p "$HF_HOME"
# export HF_TOKEN=hf_xxx        # only for gated models (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate

echo "Cache: $HF_HOME"
df -h "/scratch.hpc/$USER" | tail -1

python3 - "$ALIAS" <<'PY'
import sys
from huggingface_hub import snapshot_download
from src.aba_model import LOCAL_MODELS

alias = sys.argv[1]
repo = LOCAL_MODELS.get(alias, alias)     # a full HF id also works
print(f"Fetching {alias} -> {repo}")
path = snapshot_download(
    repo_id=repo,
    # Skip duplicate formats: the loader uses safetensors.
    ignore_patterns=["*.pth", "*.msgpack", "*.h5", "*.onnx*"],
)
print("Cached at:", path)
PY

echo "Done. The GPU job will now load from cache instead of downloading."
