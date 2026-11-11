#!/usr/bin/env bash
# Full pipeline from raw XES logs to tables and figures (about 2 h on 2 vCPU / 7 GB RAM with JOBS=3).
# Outputs: work/ (encoded data, models, predictions; large) and outputs/results/ (same layout as results/).
set -euo pipefail
D="$(cd "$(dirname "$0")" && pwd)"
bash "$D/01_parse_logs.sh"
bash "$D/02_prepare.sh"
bash "$D/03_train.sh"
bash "$D/04_evaluate_explain.sh"
bash "$D/05_aggregate.sh"
