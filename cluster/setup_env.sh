#!/bin/bash
# ---------------------------------------------------------------------------
# ONE-TIME environment setup. Run ON giano.cs.unibo.it (the login node),
# AFTER copying the project into scratch, e.g. from your laptop:
#     rsync -av --exclude .venv --exclude results \
#           Learning_aba/ giano.cs.unibo.it:/scratch.hpc/$USER/Learning_aba/
# then on giano:
#     cd /scratch.hpc/$USER/Learning_aba && bash cluster/setup_env.sh
#
# Everything (venv + model cache) goes in /scratch.hpc because the home quota
# is only 400 MB and PyTorch + the models are several GB.
# ---------------------------------------------------------------------------
set -euo pipefail

SCRATCH="/scratch.hpc/$USER"
PROJ="$SCRATCH/Learning_aba"
mkdir -p "$SCRATCH/hf_cache"
cd "$PROJ"

python3 -m venv venv
source venv/bin/activate
pip3 install --no-cache-dir --upgrade pip

# PyTorch built for the cluster's CUDA 11.8 (rif. https://pytorch.org/)
pip3 install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu118

# Local on-GPU inference + the project's own dependencies.
# (No API libs, no fine-tuning libs — not needed for local runs.)
pip3 install --no-cache-dir \
    transformers accelerate bitsandbytes sentencepiece \
    clingo numpy matplotlib scikit-learn networkx

echo "----------------------------------------------------------------------"
python3 -c "import torch, transformers, clingo; \
print('torch', torch.__version__, '| transformers', transformers.__version__, \
'| cuda build', torch.version.cuda)"
echo "Setup OK. Model cache -> $SCRATCH/hf_cache"
echo "(torch.cuda.is_available() is False here on the login node - that is normal;"
echo " the GPU only appears inside a SLURM job.)"
