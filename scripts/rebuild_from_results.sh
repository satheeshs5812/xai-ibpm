#!/usr/bin/env bash
# Rebuild every result table and figure of the paper from the shipped result files in results/ (no data, no
# training; a few minutes on a laptop). Regenerates in place: results/ALL_*.csv (aggregation + statistics),
# results/results_summary.md, results/figures/*, results/tables/*.
# Inputs: results/per_task/**, results/run_metadata/** (dataset statistics, tuning summaries, Optuna trials).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$REPO_ROOT"
PY="${PYTHON:-python3}"
export XAI_IBPM_RESULTS="${XAI_IBPM_RESULTS:-$REPO_ROOT/results}"
export XAI_IBPM_WORK="${XAI_IBPM_WORK:-$REPO_ROOT/results/run_metadata}"
$PY src/aggregate.py
$PY src/build_summary.py
$PY src/figures.py
$PY src/make_tables.py
echo "Tables: $XAI_IBPM_RESULTS/tables/   Figures: $XAI_IBPM_RESULTS/figures/"
