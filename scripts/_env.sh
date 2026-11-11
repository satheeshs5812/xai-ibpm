# Common environment for all scripts. Source from a script in scripts/.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"
PY="${PYTHON:-python3}"
JOBS="${JOBS:-3}"                       # concurrent single-threaded processes (paper run: 3 on 2 vCPU)
export XAI_IBPM_PARSED="${XAI_IBPM_PARSED:-$REPO_ROOT/data/parsed}"
export XAI_IBPM_WORK="${XAI_IBPM_WORK:-$REPO_ROOT/work}"
# A full re-run writes to outputs/results so that the shipped results/ stay untouched.
export XAI_IBPM_RESULTS="${XAI_IBPM_RESULTS:-$REPO_ROOT/outputs/results}"
export TORCH_THREADS="${TORCH_THREADS:-1}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
LOGDIR="${LOGDIR:-$XAI_IBPM_RESULTS/logs}"; mkdir -p "$LOGDIR"

BENCH_TASKS="bpic2012_accepted bpic2012_cancelled bpic2012_declined bpic2017_accepted bpic2017_cancelled bpic2017_refused sepsis_cases_1 sepsis_cases_2 sepsis_cases_3 traffic_fines_1"
STRICT_TASKS="bpic2012_accepted bpic2017_accepted sepsis_cases_1 traffic_fines_1"
# preprocessing groups (BENCHMARK BPIC tasks of one log share one encoding)
BENCH_GROUPS="bpic2012 bpic2017 sepsis_cases_1 sepsis_cases_2 sepsis_cases_3 traffic_fines_1"
STRICT_GROUPS="bpic2012_accepted bpic2017_accepted sepsis_cases_1 traffic_fines_1"

# run "<cmd args>" lines from stdin in parallel; each line: <logname> <command...>
prun() { xargs -P "${JOBS}" -L 1 sh -c 'n=$0; shift; echo "start $n"; "$@" > "'"$LOGDIR"'/$n.log" 2>&1 && echo "done  $n" || { echo "FAILED $n (see '"$LOGDIR"'/$n.log)"; exit 255; }'; }
