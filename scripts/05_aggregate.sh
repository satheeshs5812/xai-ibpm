#!/usr/bin/env bash
# Step 5: collect per-task outputs into ALL_*.csv, cross-task statistics (Friedman/Nemenyi/Wilcoxon-Holm),
# runtime/environment report, results summary, figures and paper tables.
source "$(dirname "$0")/_env.sh"
$PY src/aggregate.py
$PY src/runtime_env.py
cp -n results/figures_list.md "$XAI_IBPM_RESULTS/" 2>/dev/null || true
$PY src/build_summary.py
$PY src/figures.py
$PY src/make_tables.py
