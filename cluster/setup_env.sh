#!/bin/bash
# One-time setup on giano. Venv and model cache live in scratch (home quota 400 MB):
#   git clone https://github.com/carmine559/Learning_ABA.git /scratch.hpc/$USER/Learning_aba
#   cd /scratch.hpc/$USER/Learning_aba && bash cluster/setup_env.sh
set -euo pipefail
cd "/scratch.hpc/$USER/Learning_aba"

python3 -m venv venv
source venv/bin/activate
pip3 install --no-cache-dir --upgrade pip
pip3 install --no-cache-dir -r requirements-train.txt     # torch 2.7.1+cu118, transformers, peft
pip3 install --no-cache-dir bitsandbytes sentencepiece numpy matplotlib scikit-learn networkx

# On giano torch sees no GPU; the GPU appears only inside a SLURM job.
python3 -c "import torch, transformers, peft; print('torch', torch.__version__, \
'| transformers', transformers.__version__, '| peft', peft.__version__)"
