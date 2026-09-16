#!/bin/sh
set -eu
# Run from this study root. Downloads and environments remain ignored by Git.
if [ ! -d downloads/earm/.git ]; then
  git clone --filter=blob:none https://github.com/FengQi-HITSZ/earm.git downloads/earm
fi
git -C downloads/earm checkout ea06cb9059e9ebf7ebd9bf036ff08e188c18f6e0
if [ ! -d downloads/tau2-bench/.git ]; then
  git clone --filter=blob:none https://github.com/sierra-research/tau2-bench.git downloads/tau2-bench
fi
git -C downloads/tau2-bench checkout 2174a603f6d014ef94473ffa95957f6ce27100db
uv sync --frozen
uv run python scripts/check_workload.py
# Model path and verified hashes are in evidence/calibration-v1/model.json.
# No model download is triggered by this script. Final commands appear in FINDINGS.md.
