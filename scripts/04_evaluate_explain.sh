#!/usr/bin/env bash
# Step 4: per-task evaluation (stacking, calibration, tests, conformal deferral, cost rule, ablation) followed by
# the explanation analysis (ensemble TreeSHAP global/local; full SHAP/LIME quality study on 4 representative tasks).
source "$(dirname "$0")/_env.sh"
one() {  # protocol task
  p=$1; t=$2; mode=global
  case "$p:$t" in benchmark:bpic2012_accepted|benchmark:bpic2017_accepted|benchmark:sepsis_cases_2|benchmark:traffic_fines_1) mode=full;; esac
  echo "eval_${p}_$t sh -c '$PY src/evaluate.py $p $t && $PY src/explain.py $p $t $mode > $LOGDIR/xai_${p}_$t.log 2>&1'"
}
{ for t in $BENCH_TASKS; do one benchmark $t; done; for t in $STRICT_TASKS; do one strict $t; done; } | prun
