#!/usr/bin/env bash
# Step 2: labelling, BENCHMARK and STRICT preprocessing, temporal splits, encodings (-> work/<protocol>/<group>/).
source "$(dirname "$0")/_env.sh"
{ for g in $BENCH_GROUPS;  do echo "prep_benchmark_$g $PY src/prepare.py benchmark $g"; done
  for g in $STRICT_GROUPS; do echo "prep_strict_$g $PY src/prepare.py strict $g"; done; } | JOBS=1 prun
