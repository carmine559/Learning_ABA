#!/bin/bash
# Build the venv on giano. Venv and model cache live in scratch (home quota 400 MB):
#   git clone https://github.com/carmine559/Learning_ABA.git /scratch.hpc/$USER/Learning_aba
#   cd /scratch.hpc/$USER/Learning_aba && bash cluster/setup_env.sh
# An existing venv is moved to venv.old; delete it once the new one works.
set -euo pipefail
cd "/scratch.hpc/$USER/Learning_aba"

if [ -d venv ]; then
    rm -rf venv.old
    mv venv venv.old
fi
python3 -m venv venv
source venv/bin/activate
pip3 install --no-cache-dir --upgrade pip
# one resolve with the pins, so no extra can move the pinned stack
pip3 install --no-cache-dir -r requirements-train.txt \
    bitsandbytes sentencepiece numpy matplotlib scikit-learn networkx pytest

# On giano torch sees no GPU; the GPU appears only inside a SLURM job.
python3 - <<'PY'
import importlib.metadata as md
import platform
import torch
want = {"torch": "2.7.1+cu118", "transformers": "5.17.0", "tokenizers": "0.23.2",
        "accelerate": "1.15.0", "peft": "0.21.0", "clingo": "5.8.2"}
got = {p: md.version(p) for p in want}
assert got == want, f"not the pinned stack: {got}"
print(f"pinned stack ok on Python {platform.python_version()}, CUDA runtime {torch.version.cuda}")
PY
