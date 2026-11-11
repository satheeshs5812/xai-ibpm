"""Write <results>/runtime_env.md (library versions, hardware, per-task runtimes from the run summaries)."""
import sys, os, json, glob, platform
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from common import *
import sklearn, lightgbm, xgboost, catboost, optuna, shap, lime, torch, numpy, scipy, matplotlib, scikit_posthocs
from importlib.metadata import version
rows = []
for proto in ['benchmark', 'strict']:
    for d in sorted(glob.glob(f'{WORK}/{proto}/runs/*')):
        t = os.path.basename(d); r = dict(protocol=proto, task=t)
        if os.path.exists(f'{d}/gbm_summary.json'): r['gbm_tuning_and_training_s'] = round(json.load(open(f'{d}/gbm_summary.json'))['runtime_s'])
        if os.path.exists(f'{d}/deep_summary.json'): r['deep_models_s'] = round(json.load(open(f'{d}/deep_summary.json'))['runtime_s'])
        e = f'{RES}/per_task/{proto}/{t}/eval_info.json'
        if os.path.exists(e): r['evaluation_s'] = round(json.load(open(e))['runtime_s'])
        rows.append(r)
rt = pd.DataFrame(rows); rt.to_csv(f'{RES}/ALL_runtime.csv', index=False)
libs = ['scikit-learn', 'lightgbm', 'xgboost', 'catboost', 'optuna', 'shap', 'lime', 'torch', 'numpy', 'pandas', 'scipy', 'matplotlib', 'scikit-posthocs']
txt = f"""- Hardware: 2 vCPU, 7 GB RAM, no GPU. All models on CPU; every training process used 1 thread (n_jobs/thread_count = 1, torch 1 thread); up to 3 processes ran concurrently, so per-task wall-clock times include contention.
- OS / Python: {platform.platform()}, Python {platform.python_version()}
- Libraries: {', '.join(f'{l} {version(l)}' for l in libs)}
- Seeds: training seeds 0–4 for all stochastic models (GBMs, RF, LSTM, Transformer, stack); LR deterministic. Optuna TPE seed 0; subsampling seed 0 (fit) / 1 (validation); bootstrap seed 0 (AUC CIs) / 1 (prefix bands); XAI sampling seed 0.
- Total wall-clock for the whole experimental round (prep, tuning, training, evaluation, XAI, figures): about 2 h on this machine (sum of per-task process times below exceeds this because of parallel queues).
- Per-task process runtimes (s):

""" + '| ' + ' | '.join(rt.columns) + ' |\n|' + '---|' * len(rt.columns) + '\n' + '\n'.join('| ' + ' | '.join('' if pd.isna(v) else str(v) for v in r) + ' |' for r in rt.values) + '\n'
open(f'{RES}/runtime_env.md', 'w').write(txt)
print(txt)
