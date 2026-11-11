"""Per-task evaluation: proposed calibrated stacked ensemble, calibration comparison, metrics, bootstrap CIs,
DeLong / paired bootstrap tests, prefix-length AUC, reliability, conformal governance, confidence deferral,
risk-coverage, cost-based decisioning, ablation.
Usage: python3 evaluate.py <protocol> <task>"""
import sys, os, json, time, pickle, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd
from common import *
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss, accuracy_score, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.model_selection import GroupKFold

PROTO, TASK = sys.argv[1], sys.argv[2]
RUN = f'{WORK}/{PROTO}/runs/{TASK}'
OUT = f'{RES}/per_task/{PROTO}/{TASK}'; os.makedirs(OUT, exist_ok=True)
T0 = time.time()
def log(*a): print(f'[eval {PROTO}/{TASK} {time.strftime("%H:%M:%S")} +{time.time() - T0:.0f}s]', *a, flush=True)

g = group_of(PROTO, TASK); gd = f'{WORK}/{PROTO}/{g}'
info = json.load(open(f'{gd}/info.json')); K = info['K'][TASK]; LOG_ = TASKS[TASK][0]; ADV = TASKS[TASK][2]
Mv = pd.read_parquet(f'{gd}/meta_val.parquet'); Mv = Mv[Mv.prefix_len <= K].reset_index(drop=True)
Mt = pd.read_parquet(f'{gd}/meta_test.parquet'); Mt = Mt[Mt.prefix_len <= K].reset_index(drop=True)
yv = Mv['label__' + TASK].values.astype(int); yt = Mt['label__' + TASK].values.astype(int)
va = (Mv.part == 'va').values; vb = ~va
P = pickle.load(open(f'{RUN}/preds_tab.pkl', 'rb')); P.update(pickle.load(open(f'{RUN}/preds_deep.pkl', 'rb')))
P = {k: {kk: np.clip(vv.astype(np.float64), 0.0, 1.0) for kk, vv in v.items()} for k, v in P.items()}  # float32 round-off
gs = json.load(open(f'{RUN}/gbm_summary.json')); ds = json.load(open(f'{RUN}/deep_summary.json'))
case_codes = pd.factorize(Mt.case)[0]


# ------------------------------------------------------------------ calibrators
class Ident:
    def fit(s, p, y): return s
    def predict(s, p): return p
class Platt:  # constrained to be non-decreasing: a negative slope would invert the ranking -> identity
    def fit(s, p, y):
        s.m = LogisticRegression(C=1e6).fit(logit(p)[:, None], y); s.ok = s.m.coef_[0, 0] > 0; return s
    def predict(s, p): return s.m.predict_proba(logit(p)[:, None])[:, 1] if s.ok else p
class Iso:
    def fit(s, p, y): s.m = IsotonicRegression(out_of_bounds='clip', y_min=0, y_max=1).fit(p, y); return s
    def predict(s, p): return s.m.predict(p)
class Beta:  # Kull et al. 2017, 3-parameter beta calibration via logistic regression on (ln p, -ln(1-p))
    def _f(s, p): p = np.clip(p, 1e-6, 1 - 1e-6); return np.c_[np.log(p), -np.log(1 - p)]
    def fit(s, p, y):  # Kull et al. require a, b >= 0 for a monotone map; otherwise fall back to identity
        s.m = LogisticRegression(C=1e6).fit(s._f(p), y); s.ok = bool(np.all(s.m.coef_[0] >= 0)); return s
    def predict(s, p): return s.m.predict_proba(s._f(p))[:, 1] if s.ok else p
class VennAbers:  # inductive Venn-Abers predictor (Vovk & Petej 2014), merged p1/(1-p0+p1); scores evaluated on a grid
    def fit(s, p, y, ngrid=51):
        s.grid = np.unique(np.quantile(p, np.linspace(0, 1, ngrid)))
        p0, p1 = [], []
        for gv in s.grid:
            for lab, store in ((0, p0), (1, p1)):
                ir = IsotonicRegression(out_of_bounds='clip', y_min=0, y_max=1).fit(np.r_[p, gv], np.r_[y, lab])
                store.append(ir.predict([gv])[0])
        p0, p1 = np.array(p0), np.array(p1)
        s.pm = p1 / (1 - p0 + p1); s.width = np.mean(p1 - p0); return s
    def predict(s, p): return np.interp(p, s.grid, s.pm)
CALS = {'none': Ident, 'platt': Platt, 'isotonic': Iso, 'beta': Beta, 'venn-abers': VennAbers}


def mets(y, p):
    yh = (p >= 0.5).astype(int)
    return dict(auc=roc_auc_score(y, p), brier=brier_score_loss(y, p), ece=ece_score(y, p),
                logloss=log_loss(y, np.clip(p, 1e-6, 1 - 1e-6)), accuracy=accuracy_score(y, yh), f1_macro=f1_score(y, yh, average='macro'))


# ------------------------------------------------------------------ stacking
groups_va = pd.factorize(Mv.case[va])[0]
def stack(base_names, seed, cal_choice=None, post_cal=True):
    """Meta logistic regression on base-model logits, fit on validation part A; calibrator chosen by grouped 5-fold
    cross-validated log-loss on out-of-fold meta predictions (part A). Returns val & test predictions + chosen cal."""
    Zv = np.column_stack([logit(P[(b, seed)]['val']) for b in base_names]); Zt = np.column_stack([logit(P[(b, seed)]['test']) for b in base_names])
    ya = yv[va]; Za = Zv[va]
    meta = LogisticRegression(C=1.0, max_iter=1000).fit(Za, ya)
    oof = np.zeros(len(ya)); gkf = GroupKFold(5)
    folds = list(gkf.split(Za, ya, groups_va))
    for tr, te in folds:
        oof[te] = LogisticRegression(C=1.0, max_iter=1000).fit(Za[tr], ya[tr]).predict_proba(Za[te])[:, 1]
    cv_ll = {}
    if post_cal and cal_choice is None:
        for cn, C in CALS.items():
            ll = []
            for tr, te in folds:
                pr = C().fit(oof[tr], ya[tr]).predict(oof[te]); ll.append(log_loss(ya[te], np.clip(pr, 1e-6, 1 - 1e-6), labels=[0, 1]))
            cv_ll[cn] = float(np.mean(ll))
        cal_choice = min(cv_ll, key=cv_ll.get)
    elif not post_cal:
        cal_choice = 'none'
    cal = CALS[cal_choice]().fit(oof, ya)
    pv_raw = meta.predict_proba(Zv)[:, 1]; pt_raw = meta.predict_proba(Zt)[:, 1]
    return dict(val=cal.predict(pv_raw), test=cal.predict(pt_raw), val_raw=pv_raw, test_raw=pt_raw, cal=cal_choice,
                cv_logloss=cv_ll, weights=dict(zip(base_names, meta.coef_[0])), intercept=float(meta.intercept_[0]))


BASE = ['LGBM', 'XGB', 'CatBoost', 'Transformer']
ST = {}
for s in SEEDS:
    ST[('Stack (proposed)', s)] = stack(BASE, s)
    ST[('Stack w/o Transformer', s)] = stack(BASE[:3], s)
    ST[('Stack w/o post-calibration', s)] = stack(BASE, s, post_cal=False)
    # single best tuned GBM (by validation-A AUC) + isotonic on validation-A
    best = max(['LGBM', 'XGB', 'CatBoost'], key=lambda b: roc_auc_score(yv[va], P[(b, s)]['val'][va]))
    iso = Iso().fit(P[(best, s)]['val'][va], yv[va])
    ST[('Best tuned GBM + isotonic', s)] = dict(val=iso.predict(P[(best, s)]['val']), test=iso.predict(P[(best, s)]['test']), cal='isotonic', best=best)
ST[('Stack of default GBMs (untuned)', 0)] = stack(['LGBM-default', 'XGB-default', 'CatBoost-default'], 0)
for k, v in ST.items():
    P[k] = v
stack_info = [dict(protocol=PROTO, task=TASK, seed=s, chosen_calibrator=ST[('Stack (proposed)', s)]['cal'],
                   **{f'cv_logloss_{c}': v for c, v in ST[('Stack (proposed)', s)]['cv_logloss'].items()},
                   **{f'meta_w_{b}': w for b, w in ST[('Stack (proposed)', s)]['weights'].items()},
                   meta_intercept=ST[('Stack (proposed)', s)]['intercept']) for s in SEEDS]
pd.DataFrame(stack_info).to_csv(f'{OUT}/stack_meta.csv', index=False)
log('stack calibrators', [d['chosen_calibrator'] for d in stack_info])

MAIN = ['LR', 'RF', 'XGB', 'LGBM', 'CatBoost', 'LSTM', 'Transformer', 'Stack (proposed)']
ABL = ['Stack w/o Transformer', 'Stack w/o post-calibration', 'Best tuned GBM + isotonic', 'Stack of default GBMs (untuned)',
       'LGBM-default', 'XGB-default', 'CatBoost-default']
def seeds_of(m): return [s for s in SEEDS if (m, s) in P]

# ------------------------------------------------------------------ metrics per model/seed
rows, pl_rows = [], []
times = {'LR': gs.get('LR_train_s'), 'RF': gs.get('RF_train_s'), 'XGB': gs.get('XGB_train_s'), 'LGBM': gs.get('LGBM_train_s'),
         'CatBoost': gs.get('CatBoost_train_s'), 'LSTM': ds.get('LSTM_train_s'), 'Transformer': ds.get('Transformer_train_s')}
inf = {'LR': gs.get('LR_infer_ms_per_1000'), 'RF': gs.get('RF_infer_ms_per_1000'), 'XGB': gs.get('XGB_infer_ms_per_1000'), 'LGBM': gs.get('LGBM_infer_ms_per_1000'),
       'CatBoost': gs.get('CatBoost_infer_ms_per_1000'), 'LSTM': ds.get('LSTM_infer_ms_per_1000'), 'Transformer': ds.get('Transformer_infer_ms_per_1000')}
for m in MAIN + ABL:
    for s in seeds_of(m):
        p = P[(m, s)]['test']
        r = dict(protocol=PROTO, task=TASK, model=m, seed=s, **mets(yt, p))
        if m in times and times[m]: r['train_s'] = times[m][s if len(times[m]) > s else 0]; r['infer_ms_per_1000'] = inf[m][s if len(inf[m]) > s else 0]
        if m == 'Stack (proposed)':
            r['train_s'] = sum(times[b][s] for b in BASE); r['infer_ms_per_1000'] = sum(inf[b][s] for b in BASE)
        rows.append(r)
        if m in MAIN:
            for L, gidx in Mt.groupby('prefix_len').indices.items():
                yy = yt[gidx]
                pl_rows.append(dict(protocol=PROTO, task=TASK, model=m, seed=s, prefix_len=L, n=len(gidx),
                                    auc=roc_auc_score(yy, p[gidx]) if len(np.unique(yy)) > 1 else np.nan))
res = pd.DataFrame(rows); res.to_csv(f'{OUT}/metrics_per_seed.csv', index=False)
pd.DataFrame(pl_rows).to_csv(f'{OUT}/prefix_auc_per_seed.csv', index=False)
mean_auc = res.groupby('model').auc.mean()
log('mean test AUC', mean_auc.round(4).to_dict())

# ------------------------------------------------------------------ calibration comparison (each base model, seed 0..4, calibrator fit on val part A)
calrows = []
for m in ['LGBM', 'XGB', 'CatBoost', 'RF', 'LSTM', 'Transformer']:
    for s in seeds_of(m):
        for cn, C in CALS.items():
            c = C().fit(P[(m, s)]['val'][va], yv[va]); p = c.predict(P[(m, s)]['test'])
            calrows.append(dict(protocol=PROTO, task=TASK, model=m, seed=s, calibrator=cn, **mets(yt, p)))
for s in SEEDS:
    for k, lab in [('test_raw', 'meta-LR output (no post-calibration)'), ('test', 'chosen post-calibration')]:
        calrows.append(dict(protocol=PROTO, task=TASK, model='Stack (proposed)', seed=s, calibrator=lab + f" [{ST[('Stack (proposed)', s)]['cal']}]" if k == 'test' else lab,
                            **mets(yt, ST[('Stack (proposed)', s)][k])))
pd.DataFrame(calrows).to_csv(f'{OUT}/calibration_comparison.csv', index=False)

# reliability (seed 0): raw LGBM, raw stack meta, calibrated stack, LR, Transformer
rel = []
for name, p in [('LGBM (raw)', P[('LGBM', 0)]['test']), ('Stack: meta-LR output', ST[('Stack (proposed)', 0)]['test_raw']),
                ('Stack (proposed, calibrated)', P[('Stack (proposed)', 0)]['test']), ('LR', P[('LR', 0)]['test']),
                ('Transformer', P[('Transformer', 0)]['test'])]:
    bins = np.linspace(0, 1, 11); idx = np.clip(np.digitize(p, bins[1:-1]), 0, 9)
    for b in range(10):
        mm = idx == b
        if mm.sum() >= 20:
            rel.append(dict(protocol=PROTO, task=TASK, model=name, bin=b, n=int(mm.sum()), mean_pred=p[mm].mean(), frac_pos=yt[mm].mean()))
pd.DataFrame(rel).to_csv(f'{OUT}/reliability.csv', index=False)

# ------------------------------------------------------------------ bootstrap CIs (case-cluster bootstrap, seed-0 predictions)
rng = np.random.RandomState(0); B = 1000
W = case_bootstrap_weights(case_codes, B, rng)
ci_rows, boot = [], {}
for m in MAIN + ABL:
    if (m, 0) not in P: continue
    a = weighted_auc_fast(P[(m, 0)]['test'].astype(np.float64), yt, W); boot[m] = a
    ci_rows.append(dict(protocol=PROTO, task=TASK, model=m, auc_seed0=roc_auc_score(yt, P[(m, 0)]['test']),
                        auc_mean_5seeds=mean_auc.get(m, np.nan), ci_lo=np.nanpercentile(a, 2.5), ci_hi=np.nanpercentile(a, 97.5), n_boot=B))
pd.DataFrame(ci_rows).to_csv(f'{OUT}/auc_bootstrap_ci.csv', index=False)

# DeLong + paired bootstrap: proposed vs every baseline (seed 0)
pt = P[('Stack (proposed)', 0)]['test']
cmp_rows = []
baselines = [m for m in MAIN if m != 'Stack (proposed)']
best_base = max(baselines, key=lambda m: mean_auc[m])
for m in baselines:
    a1, a2, z, pd_ = delong(yt, pt, P[(m, 0)]['test'])
    d = boot['Stack (proposed)'] - boot[m]
    cmp_rows.append(dict(protocol=PROTO, task=TASK, comparison=f'Stack (proposed) vs {m}', is_best_baseline=m == best_base,
                         auc_proposed=a1, auc_baseline=a2, delta=a1 - a2, delong_z=z, delong_p=pd_,
                         boot_delta_ci_lo=np.percentile(d, 2.5), boot_delta_ci_hi=np.percentile(d, 97.5),
                         boot_p_two_sided=min(1.0, 2 * min(np.mean(d <= 0), np.mean(d >= 0)))))
pd.DataFrame(cmp_rows).to_csv(f'{OUT}/pairwise_tests.csv', index=False)
log('best baseline', best_base, 'delta', round(pt.mean() * 0 + roc_auc_score(yt, pt) - roc_auc_score(yt, P[(best_base, 0)]['test']), 4))

# prefix-length AUC bootstrap bands (seed 0, 200 reps) for proposed + top-3 baselines
top_b = list(mean_auc[baselines].sort_values(ascending=False).index[:3])
plb = []
rs = np.random.RandomState(1)
for L, gidx in Mt.groupby('prefix_len').indices.items():
    yy = yt[gidx]
    if len(np.unique(yy)) < 2: continue
    cc = pd.factorize(Mt.case.values[gidx])[0]
    Wl = case_bootstrap_weights(cc, 200, rs)
    for m in ['Stack (proposed)'] + top_b:
        a = weighted_auc_fast(P[(m, 0)]['test'][gidx].astype(np.float64), yy, Wl)
        plb.append(dict(protocol=PROTO, task=TASK, model=m, prefix_len=L, n=len(gidx), auc=roc_auc_score(yy, P[(m, 0)]['test'][gidx]),
                        ci_lo=np.nanpercentile(a, 2.5), ci_hi=np.nanpercentile(a, 97.5)))
pd.DataFrame(plb).to_csv(f'{OUT}/prefix_auc_bootstrap.csv', index=False)

# ------------------------------------------------------------------ governance: conformal (calibration = validation part B)
def conformal(p_cal, y_cal, p_te, alpha, mondrian=True):
    s_cal = np.where(y_cal == 1, 1 - p_cal, p_cal)  # nonconformity = 1 - p_hat(true class)
    def q(sc):
        n = len(sc); k = int(np.ceil((n + 1) * (1 - alpha)))
        return np.inf if k > n else np.sort(sc)[k - 1]
    if mondrian:
        q1, q0 = q(s_cal[y_cal == 1]), q(s_cal[y_cal == 0])
    else:
        q1 = q0 = q(s_cal)
    in1 = (1 - p_te) <= q1; in0 = p_te <= q0
    return in0, in1

conf_rows, conf_curve = [], []
for s in SEEDS:
    pc, pt_ = P[('Stack (proposed)', s)]['val'][vb], P[('Stack (proposed)', s)]['test']
    for mond in [True, False]:
        for alpha in [0.05, 0.1, 0.2]:
            in0, in1 = conformal(pc, yv[vb], pt_, alpha, mond)
            size = in0.astype(int) + in1.astype(int); single = size == 1
            covered = np.where(yt == 1, in1, in0)
            pred_single = np.where(in1, 1, 0)
            conf_rows.append(dict(protocol=PROTO, task=TASK, seed=s, method='Mondrian (class-conditional)' if mond else 'marginal split conformal',
                                  alpha=alpha, nominal_coverage=1 - alpha, empirical_coverage=covered.mean(),
                                  coverage_class1=covered[yt == 1].mean(), coverage_class0=covered[yt == 0].mean(),
                                  singleton_rate=single.mean(), empty_rate=(size == 0).mean(), both_rate=(size == 2).mean(),
                                  accuracy_on_singletons=(pred_single[single] == yt[single]).mean() if single.any() else np.nan,
                                  error_on_singletons=(pred_single[single] != yt[single]).mean() if single.any() else np.nan,
                                  auc_on_singletons=roc_auc_score(yt[single], pt_[single]) if single.any() and len(np.unique(yt[single])) > 1 else np.nan,
                                  n_cal=int(vb.sum())))
        if s == 0:
            for alpha in np.round(np.arange(0.02, 0.41, 0.02), 2):
                in0, in1 = conformal(pc, yv[vb], pt_, alpha, mond)
                covered = np.where(yt == 1, in1, in0); single = (in0.astype(int) + in1) == 1
                conf_curve.append(dict(protocol=PROTO, task=TASK, method='Mondrian' if mond else 'marginal', alpha=alpha,
                                       empirical_coverage=covered.mean(), coverage_class1=covered[yt == 1].mean(),
                                       coverage_class0=covered[yt == 0].mean(), singleton_rate=single.mean()))
pd.DataFrame(conf_rows).to_csv(f'{OUT}/conformal_per_seed.csv', index=False)
pd.DataFrame(conf_curve).to_csv(f'{OUT}/conformal_curve.csv', index=False)

# confidence-threshold deferral (tau on validation part B) for proposed and LGBM raw
def_rows = []
for s in SEEDS:
    for m in ['Stack (proposed)', 'LGBM']:
        pc, pt_ = P[(m, s)]['val'][vb], P[(m, s)]['test']
        cc = np.maximum(pc, 1 - pc); ct = np.maximum(pt_, 1 - pt_)
        for target in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            tau = 0.0 if target == 1.0 else np.quantile(cc, 1 - target)
            keep = ct >= tau
            yk, pk = yt[keep], pt_[keep]
            def_rows.append(dict(protocol=PROTO, task=TASK, model=m + (' (raw)' if m == 'LGBM' else ''), seed=s, target_coverage=target, tau=tau,
                                 realized_coverage=keep.mean(), n_unique_conf_values_test=len(np.unique(ct)),
                                 acc_automated=accuracy_score(yk, pk >= .5), error_automated=1 - accuracy_score(yk, pk >= .5),
                                 auc_automated=roc_auc_score(yk, pk) if len(np.unique(yk)) > 1 else np.nan))
pd.DataFrame(def_rows).to_csv(f'{OUT}/deferral_per_seed.csv', index=False)

# risk-coverage curve with case-bootstrap 95% bands (seed 0)
rc = []
Wr = W[:300]
for m in ['Stack (proposed)', 'LGBM', 'LR', 'Transformer']:
    p = P[(m, 0)]['test']; conf = np.maximum(p, 1 - p); err = ((p >= .5) != yt).astype(float)
    o = np.argsort(-conf, kind='mergesort'); e_o = err[o]
    covs = np.round(np.arange(0.05, 1.0001, 0.05), 2)
    cw = np.cumsum(Wr[:, o], 1); ce = np.cumsum(Wr[:, o] * e_o, 1); tot = cw[:, -1:]
    for cov in covs:
        n = int(round(cov * len(p))); point = e_o[:n].mean()
        idx = np.argmax(cw >= cov * tot, axis=1)
        br = ce[np.arange(len(Wr)), idx] / cw[np.arange(len(Wr)), idx]
        rc.append(dict(protocol=PROTO, task=TASK, model=m, coverage=cov, risk=point, ci_lo=np.percentile(br, 2.5), ci_hi=np.percentile(br, 97.5)))
pd.DataFrame(rc).to_csv(f'{OUT}/risk_coverage.csv', index=False)
aurc = pd.DataFrame(rc).groupby('model').risk.mean().to_dict()

# ------------------------------------------------------------------ cost-based decisioning (one decision per case at prefix DP)
DP = DECISION_PREFIX[LOG_]
dm = (Mt.prefix_len.values == DP)
yadv = (yt[dm] == ADV).astype(int)
cost_rows = []
pols = {'Stack (proposed) q>r': 'Stack (proposed)', 'Best tuned GBM + isotonic q>r': 'Best tuned GBM + isotonic', 'LGBM raw q>r': 'LGBM',
        'LR q>r': 'LR', 'Transformer q>r': 'Transformer', 'LSTM q>r': 'LSTM'}
for r in np.round(np.arange(0.05, 0.951, 0.05), 2):
    nb = lambda intv: float(np.sum(intv * (yadv - r)) / len(yadv))
    for k, v in {'never intervene': np.zeros(len(yadv)), 'always intervene': np.ones(len(yadv)), 'oracle': yadv.astype(float)}.items():
        cost_rows.append(dict(protocol=PROTO, task=TASK, cost_ratio=r, policy=k, seed=0, net_benefit=nb(v), intervention_rate=v.mean()))
    for lab, m in pols.items():
        for s in seeds_of(m):
            p = P[(m, s)]['test'][dm]; q = p if ADV == 1 else 1 - p
            intv = (q > r).astype(float)
            cost_rows.append(dict(protocol=PROTO, task=TASK, cost_ratio=r, policy=lab, seed=s, net_benefit=nb(intv), intervention_rate=intv.mean()))
    for s in SEEDS:  # cost-agnostic 0.5 threshold on the proposed model
        p = P[('Stack (proposed)', s)]['test'][dm]; q = p if ADV == 1 else 1 - p
        intv = (q > 0.5).astype(float)
        cost_rows.append(dict(protocol=PROTO, task=TASK, cost_ratio=r, policy='Stack (proposed) fixed 0.5 threshold', seed=s, net_benefit=nb(intv), intervention_rate=intv.mean()))
cost = pd.DataFrame(cost_rows); cost['decision_prefix_len'] = DP; cost['n_decision_cases'] = int(dm.sum()); cost['adverse_rate'] = yadv.mean()
cost.to_csv(f'{OUT}/cost_per_seed.csv', index=False)

# ------------------------------------------------------------------ ablation summary
abl = []
for m in ['Stack (proposed)'] + ABL[:4] + ['LGBM', 'Transformer']:
    for s in seeds_of(m):
        p = P[(m, s)]['test']; pv = P[(m, s)]['val'][vb]
        in0, in1 = conformal(pv, yv[vb], p, 0.1, True); single = (in0.astype(int) + in1) == 1
        covered = np.where(yt == 1, in1, in0)
        q = p[dm] if ADV == 1 else 1 - p[dm]
        abl.append(dict(protocol=PROTO, task=TASK, variant=m, seed=s, **mets(yt, p), conformal_cov_a0_1=covered.mean(),
                        singleton_rate_a0_1=single.mean(), nb_r0_3=float(np.sum((q > 0.3) * (yadv - 0.3)) / len(yadv)),
                        nb_r0_5=float(np.sum((q > 0.5) * (yadv - 0.5)) / len(yadv))))
pd.DataFrame(abl).to_csv(f'{OUT}/ablation_per_seed.csv', index=False)

# save proposed predictions for XAI / figures
pickle.dump({k: v for k, v in P.items() if k[0] in MAIN + ABL[:4]}, open(f'{RUN}/preds_all.pkl', 'wb'))
json.dump(dict(best_baseline=best_base, top_baselines=top_b, aurc=aurc, runtime_s=time.time() - T0), open(f'{OUT}/eval_info.json', 'w'), indent=1)
log('DONE')
