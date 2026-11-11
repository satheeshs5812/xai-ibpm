"""Encoding selection + Optuna (TPE) tuning + 5-seed final fits for LightGBM / XGBoost / CatBoost,
plus LR and RF baselines and default-parameter GBMs (ablation "no tuning").
Usage: python3 train_gbm.py <protocol> <task>"""
import sys, os, json, time, pickle, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from common import *
import lightgbm as lgb, xgboost as xgb, catboost as cb, optuna
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
optuna.logging.set_verbosity(optuna.logging.WARNING)

PROTO, TASK = sys.argv[1], sys.argv[2]
N_TRIALS = {'LGBM': int(os.environ.get('NT_LGBM', 30)), 'XGB': int(os.environ.get('NT_XGB', 30)), 'CatBoost': int(os.environ.get('NT_CAT', 20))}
NJ = 1
TUNE_TIMEOUT = float(os.environ.get('TUNE_TIMEOUT', 480))  # wall-clock cap per family study (s)
summary_tt = TUNE_TIMEOUT
OUT = f'{WORK}/{PROTO}/runs/{TASK}'; os.makedirs(OUT, exist_ok=True)
T0 = time.time()


def log(*a):
    print(f'[{PROTO}/{TASK} {time.strftime("%H:%M:%S")} +{time.time() - T0:.0f}s]', *a, flush=True)


def load(protocol, task):
    g = group_of(protocol, task); gd = f'{WORK}/{protocol}/{g}'
    info = json.load(open(f'{gd}/info.json')); K = info['K'][task]
    Xz = np.load(f'{gd}/X.npz')
    D = {}
    for s in ['fit', 'val', 'test']:
        M = pd.read_parquet(f'{gd}/meta_{s}.parquet'); m = (M.prefix_len <= K).values
        X = Xz[s][m]; M = M[m].reset_index(drop=True)
        y = M['label__' + task].values.astype(int)
        D[s] = (X, y, M)
    return info, K, D


info, K, D = load(PROTO, TASK)
nagg = info['n_agg_cols']; cols = info['columns']
Xf, yf, Mf = D['fit']; Xv, yv, Mv = D['val']; Xt, yt, Mt = D['test']
log('fit', Xf.shape, 'val', Xv.shape, 'test', Xt.shape, 'pos rate fit/val/test', yf.mean().round(3), yv.mean().round(3), yt.mean().round(3))
# tuning subsample of the fit split (whole cases)
rng = np.random.RandomState(0)
cases = Mf.case.unique(); rng.shuffle(cases)
cnt = Mf.groupby('case').size().reindex(cases).cumsum()
tune_m = Mf.case.isin(set(cnt[cnt <= TUNE_CAP].index)).values
log('tuning subsample', tune_m.sum())
ENC = {'agg': slice(0, nagg), 'agg+index': slice(0, len(cols))}


def make(fam, params, seed, n_est=600):
    if fam == 'LGBM':
        return lgb.LGBMClassifier(n_estimators=n_est, subsample_freq=1, n_jobs=NJ, random_state=seed, verbose=-1, **params)
    if fam == 'XGB':
        return xgb.XGBClassifier(n_estimators=n_est, tree_method='hist', n_jobs=NJ, random_state=seed, eval_metric='auc',
                                 early_stopping_rounds=30 if n_est <= 600 else 50, **params)
    if fam == 'CatBoost':
        return cb.CatBoostClassifier(iterations=n_est, thread_count=NJ, random_seed=seed, verbose=0, border_count=64,
                                     eval_metric='AUC', od_type='Iter', od_wait=30 if n_est <= 600 else 50, **params)


def fit_es(fam, m, Xa, ya, Xb, yb, es=30):
    if fam == 'LGBM':
        m.fit(Xa, ya, eval_set=[(Xb, yb)], eval_metric='auc', callbacks=[lgb.early_stopping(es, verbose=False)])
        return m, m.best_iteration_
    if fam == 'XGB':
        m.fit(Xa, ya, eval_set=[(Xb, yb)], verbose=False); return m, m.best_iteration + 1
    m.fit(Xa, ya, eval_set=(Xb, yb), use_best_model=True); return m, m.get_best_iteration() + 1


DEFAULTS = {'LGBM': dict(learning_rate=0.05, num_leaves=31, subsample=0.8, colsample_bytree=0.8),
            'XGB': dict(learning_rate=0.05, max_depth=6, subsample=0.8, colsample_bytree=0.8),
            'CatBoost': dict(learning_rate=0.05, depth=6)}


def space(fam, tr):
    if fam == 'LGBM':
        return dict(learning_rate=tr.suggest_float('learning_rate', 0.02, 0.3, log=True),
                    num_leaves=tr.suggest_int('num_leaves', 15, 255, log=True),
                    min_child_samples=tr.suggest_int('min_child_samples', 5, 200, log=True),
                    subsample=tr.suggest_float('subsample', 0.5, 1.0),
                    colsample_bytree=tr.suggest_float('colsample_bytree', 0.3, 1.0),
                    reg_alpha=tr.suggest_float('reg_alpha', 1e-3, 10, log=True),
                    reg_lambda=tr.suggest_float('reg_lambda', 1e-3, 10, log=True))
    if fam == 'XGB':
        return dict(learning_rate=tr.suggest_float('learning_rate', 0.02, 0.3, log=True),
                    max_depth=tr.suggest_int('max_depth', 3, 10),
                    min_child_weight=tr.suggest_float('min_child_weight', 1, 50, log=True),
                    subsample=tr.suggest_float('subsample', 0.5, 1.0),
                    colsample_bytree=tr.suggest_float('colsample_bytree', 0.3, 1.0),
                    gamma=tr.suggest_float('gamma', 1e-3, 5, log=True),
                    reg_alpha=tr.suggest_float('reg_alpha', 1e-3, 10, log=True),
                    reg_lambda=tr.suggest_float('reg_lambda', 1e-3, 10, log=True))
    return dict(learning_rate=tr.suggest_float('learning_rate', 0.03, 0.3, log=True),
                depth=tr.suggest_int('depth', 4, 8),
                l2_leaf_reg=tr.suggest_float('l2_leaf_reg', 1, 30, log=True),
                bagging_temperature=tr.suggest_float('bagging_temperature', 0.0, 1.0),
                random_strength=tr.suggest_float('random_strength', 1e-3, 10, log=True))


def auc(y, p):
    return roc_auc_score(y, p) if len(np.unique(y)) > 1 else np.nan


preds = {}   # (model, seed) -> dict(va, vb, test)
partv = Mv.part.values
def store(name, seed, pv, pt):
    preds[(name, seed)] = dict(val=pv.astype(np.float32), test=pt.astype(np.float32))

summary = dict(protocol=PROTO, task=TASK, tune_timeout_s=summary_tt, K=K, n_fit=len(yf), n_val=len(yv), n_test=len(yt), n_tune=int(tune_m.sum()))
trials_rows = []
models_dir = f'{OUT}/models'; os.makedirs(models_dir, exist_ok=True)
for fam in ['LGBM', 'XGB', 'CatBoost']:
    # 1) encoding selection with default params on the tuning subsample
    enc_auc = {}
    for e, sl in ENC.items():
        t = time.time()
        m, it = fit_es(fam, make(fam, DEFAULTS[fam], 0), Xf[tune_m][:, sl], yf[tune_m], Xv[:, sl], yv)
        enc_auc[e] = auc(yv, m.predict_proba(Xv[:, sl])[:, 1])
        log(fam, 'encoding', e, round(enc_auc[e], 4), f'{time.time() - t:.1f}s')
    best_enc = max(enc_auc, key=enc_auc.get); sl = ENC[best_enc]
    summary[f'{fam}_enc_val_auc'] = enc_auc; summary[f'{fam}_encoding'] = best_enc

    # 2) Optuna TPE on the tuning subsample, objective = validation AUC (temporal validation split)
    def objective(tr):
        p = space(fam, tr)
        m, it = fit_es(fam, make(fam, p, 0), Xf[tune_m][:, sl], yf[tune_m], Xv[:, sl], yv)
        tr.set_user_attr('n_iter', int(it))
        return auc(yv, m.predict_proba(Xv[:, sl])[:, 1])
    t = time.time()
    st = optuna.create_study(direction='maximize', sampler=optuna.samplers.TPESampler(seed=0))
    st.enqueue_trial({k: v for k, v in DEFAULTS[fam].items() if k in ('learning_rate', 'num_leaves', 'subsample', 'colsample_bytree', 'max_depth', 'depth')} | (
        {'min_child_samples': 20, 'reg_alpha': 1e-3, 'reg_lambda': 1e-3} if fam == 'LGBM' else
        {'min_child_weight': 1, 'gamma': 1e-3, 'reg_alpha': 1e-3, 'reg_lambda': 1.0} if fam == 'XGB' else
        {'l2_leaf_reg': 3, 'bagging_temperature': 1.0, 'random_strength': 1.0}))
    st.optimize(objective, n_trials=N_TRIALS[fam], timeout=TUNE_TIMEOUT)
    summary[f'{fam}_n_trials_completed'] = len(st.trials)
    for tr in st.trials:
        trials_rows.append(dict(protocol=PROTO, task=TASK, family=fam, trial=tr.number, value=tr.value, n_iter=tr.user_attrs.get('n_iter'), **tr.params))
    bp = st.best_params
    summary[f'{fam}_best_params'] = bp; summary[f'{fam}_best_val_auc_tuning'] = st.best_value
    summary[f'{fam}_tuning_time_s'] = time.time() - t
    log(fam, 'tuned', round(st.best_value, 4), bp, f'{time.time() - t:.0f}s')

    # 3) final fits on the full fit split, 5 seeds, early stopping on validation
    its = []
    for s in SEEDS:
        t = time.time()
        m, it = fit_es(fam, make(fam, bp, s, n_est=1000), Xf[:, sl], yf, Xv[:, sl], yv, es=50)
        tt = time.time() - t; its.append(int(it))
        t = time.time(); pt = m.predict_proba(Xt[:, sl])[:, 1]; it_ = time.time() - t
        store(fam, s, m.predict_proba(Xv[:, sl])[:, 1], pt)
        summary.setdefault(f'{fam}_train_s', []).append(tt); summary.setdefault(f'{fam}_infer_ms_per_1000', []).append(it_ / len(yt) * 1e6)
        pickle.dump(m, open(f'{models_dir}/{fam}_seed{s}.pkl', 'wb'))
        log(fam, 'seed', s, 'test auc', round(auc(yt, pt), 4), 'iters', it, f'{tt:.0f}s')
    summary[f'{fam}_final_iters'] = its

    # 4) untuned (default-parameter) model on the agg encoding, seed 0 (ablation: no tuning)
    m, it = fit_es(fam, make(fam, DEFAULTS[fam], 0, n_est=1000), Xf[:, :nagg], yf, Xv[:, :nagg], yv, es=50)
    store(fam + '-default', 0, m.predict_proba(Xv[:, :nagg])[:, 1], m.predict_proba(Xt[:, :nagg])[:, 1])
    log(fam, 'default test auc', round(auc(yt, preds[(fam + '-default', 0)]['test']), 4))

# LR baseline (agg encoding; C chosen on validation from a small grid)
best = None
for C in [0.01, 0.1, 1.0]:
    t = time.time()
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=C)).fit(Xf[:, :nagg], yf)
    a = auc(yv, m.predict_proba(Xv[:, :nagg])[:, 1])
    if best is None or a > best[0]: best = (a, C, m, time.time() - t)
summary['LR_C'] = best[1]; m = best[2]
t = time.time(); pt = m.predict_proba(Xt[:, :nagg])[:, 1]
summary['LR_train_s'] = [best[3]]; summary['LR_infer_ms_per_1000'] = [(time.time() - t) / len(yt) * 1e6]
store('LR', 0, m.predict_proba(Xv[:, :nagg])[:, 1], pt)
log('LR C', best[1], 'test auc', round(auc(yt, pt), 4))
# RF baseline (agg encoding)
for s in SEEDS:
    t = time.time()
    m = RandomForestClassifier(n_estimators=150, min_samples_leaf=5, max_features='sqrt', max_samples=0.5, n_jobs=NJ, random_state=s).fit(Xf[:, :nagg], yf)
    tt = time.time() - t; t = time.time(); pt = m.predict_proba(Xt[:, :nagg])[:, 1]
    summary.setdefault('RF_train_s', []).append(tt); summary.setdefault('RF_infer_ms_per_1000', []).append((time.time() - t) / len(yt) * 1e6)
    store('RF', s, m.predict_proba(Xv[:, :nagg])[:, 1], pt)
    log('RF seed', s, round(auc(yt, pt), 4), f'{tt:.0f}s')

pickle.dump(preds, open(f'{OUT}/preds_tab.pkl', 'wb'))
pd.DataFrame(trials_rows).to_csv(f'{OUT}/optuna_trials.csv', index=False)
summary['runtime_s'] = time.time() - T0
json.dump(summary, open(f'{OUT}/gbm_summary.json', 'w'), indent=1, default=float)
log('DONE')
