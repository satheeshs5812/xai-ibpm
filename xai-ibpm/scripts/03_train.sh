#!/usr/bin/env bash
# Step 3: encoding selection + Optuna tuning + 5-seed fits of LR/RF/LightGBM/XGBoost/CatBoost (train_gbm.py) and
# light tuning + 5-seed fits of LSTM/Transformer (train_deep.py) -> work/<protocol>/runs/<task>/.
#
# Tuning wall-clock cap (TUNE_TIMEOUT, seconds per model-family study): in the paper run the 480 s cap was only
# active for the four tasks tuned last (benchmark bpic2017_cancelled, benchmark traffic_fines_1, strict
# bpic2017_accepted, strict traffic_fines_1); the other ten tasks ran all trials without a cap. This script
# reproduces that setting. Set TUNE_TIMEOUT_ALL=480 (or any value) to use one cap for every task instead.
source "$(dirname "$0")/_env.sh"
capped() { case "$1:$2" in benchmark:bpic2017_cancelled|benchmark:traffic_fines_1|strict:bpic2017_accepted|strict:traffic_fines_1) return 0;; esac; return 1; }
{ for p in benchmark strict; do
    [ $p = benchmark ] && T="$BENCH_TASKS" || T="$STRICT_TASKS"
    for t in $T; do
      if [ -n "${TUNE_TIMEOUT_ALL:-}" ]; then tt=$TUNE_TIMEOUT_ALL; elif capped $p $t; then tt=480; else tt=inf; fi
      echo "gbm_${p}_$t env TUNE_TIMEOUT=$tt $PY src/train_gbm.py $p $t"
      echo "deep_${p}_$t $PY src/train_deep.py $p $t"
    done
  done; } | prun
