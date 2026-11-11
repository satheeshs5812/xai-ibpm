#!/usr/bin/env bash
# Step 1: parse the four raw XES logs (data/raw/*.xes.gz) into parquet event tables (data/parsed/).
source "$(dirname "$0")/_env.sh"
RAW="${RAW_DIR:-$REPO_ROOT/data/raw}"
( cd "$RAW" && sha256sum -c "$REPO_ROOT/data/SHA256SUMS" ) || { echo "checksum mismatch: see data/README.md"; exit 1; }
$PY src/parse_logs.py "$RAW" "$XAI_IBPM_PARSED"
