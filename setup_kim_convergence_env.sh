#!/usr/bin/env bash
# setup_kim_convergence_env.sh
# -------------------------------------------------
# Creates a Conda environment called `kc-dev`,
# installs NumPy, Matplotlib, OmegaConf, Hydra,
# builds the kim_convergence wheel, and
# installs that wheel with pip.
# -------------------------------------------------

set -e  # exit on first error

ENV_NAME="kc-dev"
PY_VER="3.11"

echo ">>> Creating / activating Conda env: ${ENV_NAME}"
conda create -n "${ENV_NAME}" python="${PY_VER}" -y
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "${ENV_NAME}"

echo ">>> Installing binary packages via conda..."
conda install -y \
    numpy \
    matplotlib \
    omegaconf

echo ">>> Upgrading pip and adding build helpers..."
python -m pip install --upgrade pip
# `build` creates wheels; `wheel` supplies the bdist helper
python -m pip install build wheel
# Hydra is pure‑Python, so we still grab it with pip
pip install hydra-core

echo ">>> Building kim_convergence distribution..."
# Creates dist/<name>-<version>-py3-none-any.whl (and a source tarball)
python -m build --wheel

echo ">>> Installing kim_convergence from the freshly built wheel..."
pip install -e .          # dev mode – live edits
# pip install dist/*.whl    # frozen wheel – production test


echo ">>> Environment ${ENV_NAME} is ready."
echo "    Activate later with:  conda activate ${ENV_NAME}"
