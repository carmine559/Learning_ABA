#!/bin/bash
# Download a model into the scratch HF cache on giano, before the GPU job:
# inside a job the download is slow, rate-limited and spends wall time.
#   bash cluster/prefetch_model.sh qwen2.5-7b
set -euo pipefail

ALIAS="${1:?usage: bash cluster/prefetch_model.sh <alias or HF id>}"
export HF_HOME="/scratch.hpc/$USER/hf_cache"
mkdir -p "$HF_HOME"
# export HF_TOKEN=hf_xxx                 # gated models only (Llama, Gemma)

cd "/scratch.hpc/$USER/Learning_aba"
source venv/bin/activate
df -h "/scratch.hpc/$USER" | tail -1

python3 - "$ALIAS" <<'PY'
import sys
from huggingface_hub import snapshot_download
from src.aba_model import LOCAL_MODELS

repo = LOCAL_MODELS.get(sys.argv[1], sys.argv[1])
print(f"Fetching {sys.argv[1]} -> {repo}")
path = snapshot_download(repo_id=repo,       # safetensors only
                         ignore_patterns=["*.pth", "*.msgpack", "*.h5", "*.onnx*"])
print("Cached at:", path)
PY
