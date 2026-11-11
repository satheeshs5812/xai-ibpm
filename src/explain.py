"""Explanations for the proposed stacked ensemble.
The meta-learner is logistic regression on base-model log-odds, so the ensemble log-odds is
  b + sum_m w_m * logit_m(x) + w_T * logit_Transformer(sequence).
TreeSHAP values of each tree model (log-odds space) combined with weights w_m are an exact additive attribution of the
tree part; the Transformer term is held fixed per instance (sequence input, not tabular). The post-hoc calibrator is
monotone, so rankings are unchanged. LIME is applied to the same function (tabular features, Transformer term fixed).
Usage: python3 explain.py <protocol> <task> <full|global>"""
import sys, os, json, time, pickle, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, shap
from common import *
from scipy.stats import kendalltau
from lime.lime_tabular import LimeTabularExplainer

PROTO, TASK, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
RUN = f'{WORK}/{PROTO}/runs/{TASK}'; OUT = f'{RES}/per_task/{PROTO}/{TASK}'
T0 = time.time()
def log(*a): print(f'[xai {PROTO}/{TASK} {time.strftime("%H:%M:%S")} +{time.time() - T0:.0f}s]', *a, flush=True)
g = group_of(PROTO, TASK); gd = f'{WORK}/{PROTO}/{g}'
info = json.load(open(f'{gd}/info.json')); K = info['K'][TASK]; cols = info['columns']; nagg = info['n_agg_cols']
Xz = np.load(f'{gd}/X.npz')
Mt = pd.read_parquet(f'{gd}/meta_test.parquet'); mt = (Mt.prefix_len <= K).values; Xt = Xz['test'][mt]; Mt = Mt[mt].reset_index(drop=True)
Mf = pd.read_parquet(f'{gd}/meta_fit.parquet'); mf = (Mf.prefix_len <= K).values; Xf = Xz['fit'][mf]
Mv = pd.read_parquet(f'{gd}/meta_val.parquet'); Mv = Mv[Mv.prefix_len <= K].reset_index(drop=True)
yt = Mt['label__' + TASK].values.astype(int); yv = Mv['label__' + TASK].values.astype(int); vb = (Mv.part == 'vb').values
gs = json.load(open(f'{RUN}/gbm_summary.json'))
SM = pd.read_csv(f'{OUT}/stack_meta.csv')
PA = pickle.load(open(f'{RUN}/preds_all.pkl', 'rb'))
FAM = ['LGBM', 'XGB', 'CatBoost']
ncol = {f: (nagg if gs[f'{f}_encoding'] == 'agg' else len(cols)) for f in FAM}
idx_cols = np.arange(nagg, len(cols))


def load_seed(s):
    ms = {f: pickle.load(open(f'{RUN}/models/{f}_seed{s}.pkl', 'rb')) for f in FAM}
    row = SM[SM.seed == s].iloc[0]
    w = {f: row[f'meta_w_{f}'] for f in FAM}; wT = row['meta_w_Transformer']; b = row['meta_intercept']
    return ms, w, wT, b


def ens_logit_tree(ms, w, X):
    return sum(w[f] * logit(ms[f].predict_proba(X[:, :ncol[f]])[:, 1]) for f in FAM)


def ens_shap(exps, w, X):
    phi = np.zeros((len(X), len(cols)))
    base = 0.0
    for f in FAM:
        sv = exps[f].shap_values(X[:, :ncol[f]])
        sv = sv[1] if isinstance(sv, list) else sv
        phi[:, :ncol[f]] += w[f] * sv
        ev = exps[f].expected_value; ev = ev[1] if np.ndim(ev) else ev
        base += w[f] * float(ev)
    return phi, base


ms0, w0, wT0, b0 = load_seed(0)
exps0 = {f: shap.TreeExplainer(ms0[f]) for f in FAM}
pT = PA[('Transformer', 0)]['test']; zT = logit(pT)  # fixed per instance
rng = np.random.RandomState(0)

# ---------------- global SHAP (2000 test prefixes) + additivity check
gi = rng.choice(len(Xt), min(2000, len(Xt)), replace=False)
phi, base = ens_shap(exps0, w0, Xt[gi])
recon = phi.sum(1) + base
direct = ens_logit_tree(ms0, w0, Xt[gi])
add_err = float(np.max(np.abs(recon - direct)))
imp = pd.DataFrame({'feature': cols, 'mean_abs_shap': np.abs(phi).mean(0)}).sort_values('mean_abs_shap', ascending=False)
imp.insert(0, 'task', TASK); imp.insert(0, 'protocol', PROTO); imp['rank'] = range(1, len(imp) + 1)
imp.head(20).to_csv(f'{OUT}/shap_global_top20.csv', index=False)
np.savez_compressed(f'{OUT}/shap_sample.npz', phi=phi.astype(np.float32), X=Xt[gi], cols=np.array(cols), idx=gi, base=base)
log('global shap done; max additivity error', add_err)
json.dump(dict(additivity_max_abs_err=add_err, meta_weights=w0, w_transformer=wT0, intercept=b0, encodings={f: gs[f'{f}_encoding'] for f in FAM}),
          open(f'{OUT}/xai_info.json', 'w'), indent=1, default=float)

# ---------------- local waterfall of a deferred case (Mondrian conformal alpha=0.1 not singleton), seed 0
pc = PA[('Stack (proposed)', 0)]['val'][vb]; ptest = PA[('Stack (proposed)', 0)]['test']
s_cal = np.where(yv[vb] == 1, 1 - pc, pc)
def q(sc, a=0.1):
    n = len(sc); k = int(np.ceil((n + 1) * (1 - a))); return np.inf if k > n else np.sort(sc)[k - 1]
q1, q0 = q(s_cal[yv[vb] == 1]), q(s_cal[yv[vb] == 0])
in1 = (1 - ptest) <= q1; in0 = ptest <= q0; deferred = (in0.astype(int) + in1) != 1
cand = np.where(deferred & (Mt.prefix_len.values == min(5, K)))[0]
if len(cand) == 0: cand = np.where(deferred)[0]
if len(cand):
    i = cand[np.argmin(np.abs(ptest[cand] - 0.5))]
    ph, bs = ens_shap(exps0, w0, Xt[i:i + 1])
    pd.DataFrame({'feature': cols, 'value': Xt[i], 'shap': ph[0]}).assign(
        base_tree=bs, transformer_term=wT0 * zT[i], intercept=b0, p_calibrated=ptest[i], label=yt[i], prefix_len=Mt.prefix_len[i],
        set_contains_0=bool(in0[i]), set_contains_1=bool(in1[i]), test_row=int(i)).to_csv(f'{OUT}/waterfall_deferred_case.csv', index=False)
    log('waterfall case', i, 'p', round(float(ptest[i]), 3), 'label', yt[i])
if MODE != 'full':
    log('DONE (global)'); sys.exit(0)

# ---------------- explanation quality on N stratified test prefixes
N = 100; NL = 30
pos = np.where(yt == 1)[0]; neg = np.where(yt == 0)[0]
npos = max(1, int(round(N * yt.mean())))
xi = np.concatenate([rng.choice(pos, npos, replace=False), rng.choice(neg, N - npos, replace=False)])
Xs = Xt[xi]; zTs = zT[xi]
def f_prob(X, zt):  # ensemble probability (pre post-calibration), Transformer term fixed
    return sigmoid(b0 + wT0 * zt + ens_logit_tree(ms0, w0, X))
t = time.time(); S_shap = np.vstack([ens_shap(exps0, w0, Xs[i:i + 1])[0] for i in range(N)]); shap_rt = (time.time() - t) / N
# LIME works on a NaN-free representation: index columns use -1 for "position absent"
def to_lime(X): X = X.copy(); X[np.isnan(X)] = -1; return X
def from_lime(X): X = X.copy(); X[:, idx_cols] = np.where(X[:, idx_cols] < 0, np.nan, X[:, idx_cols]); return X
bg = to_lime(Xf[rng.choice(len(Xf), min(5000, len(Xf)), replace=False)])
lime_d = LimeTabularExplainer(bg, feature_names=cols, class_names=['0', '1'], discretize_continuous=True, random_state=0)
lime_c = LimeTabularExplainer(bg, feature_names=cols, class_names=['0', '1'], discretize_continuous=False, random_state=0)
def run_lime(ex, x, zt, rs=0, nf=10):
    ex.random_state = np.random.RandomState(rs)
    e = ex.explain_instance(to_lime(x[None])[0], lambda Z: np.c_[1 - f_prob(from_lime(Z), zt), f_prob(from_lime(Z), zt)],
                            num_features=nf, num_samples=1000, labels=(1,))
    w = np.zeros(len(cols))
    for fi, v in e.as_map()[1]: w[fi] = v
    return w
t = time.time(); L_d = np.vstack([run_lime(lime_d, Xs[i], zTs[i]) for i in range(N)]); lime_rt = (time.time() - t) / N
L_c = np.vstack([run_lime(lime_c, Xs[i], zTs[i]) for i in range(N)])
log('LIME done', f'{lime_rt:.3f}s/inst; SHAP {shap_rt:.4f}s/inst')
def topk(w, k): return set(np.argsort(-np.abs(w))[:k])
def jac(a, b): return len(a & b) / len(a | b) if (a | b) else 1.0

agr = []
for i in range(N):
    lf = np.where(L_d[i] != 0)[0]
    shared = list(topk(S_shap[i], 5) & topk(L_d[i], 5))
    agr.append(dict(jac_shap_lime=jac(topk(S_shap[i], 5), topk(L_d[i], 5)), jac_shap_lime_nodisc=jac(topk(S_shap[i], 5), topk(L_c[i], 5)),
                    kendall=kendalltau(np.abs(S_shap[i][lf]), np.abs(L_d[i][lf]))[0] if len(lf) > 2 else np.nan,
                    sign_agree=np.mean(np.sign(S_shap[i][shared]) == np.sign(L_d[i][shared])) if shared else np.nan))
agr = pd.DataFrame(agr)

# deletion curve: remove top-k features supporting the predicted class (agg cols -> training mean; index cols -> missing)
fill = np.nanmean(Xf, 0); fill[idx_cols] = np.nan
p0 = f_prob(Xs, zTs); predcls = p0 >= 0.5
del_rows = []
for k in [1, 2, 3, 5, 7, 10, 15, 20]:
    for meth, Wm in [('SHAP', S_shap), ('LIME', L_d), ('LIME (no discretization)', L_c), ('random', None)]:
        drops = []
        for r in range(10 if meth == 'random' else 1):
            Xm = Xs.copy(); rr = np.random.RandomState(100 + r)
            for i in range(N):
                if Wm is None:
                    idx = rr.choice(len(cols), k, replace=False)
                else:
                    c = (1 if predcls[i] else -1) * Wm[i]; idx = np.argsort(-c)[:k]; idx = idx[c[idx] > 0]
                Xm[i, idx] = fill[idx]
            p1 = f_prob(Xm, zTs)
            drops.append(np.where(predcls, p0 - p1, p1 - p0))
        d = np.mean(drops, 0)
        del_rows.append(dict(protocol=PROTO, task=TASK, method=meth, k=k, mean_drop_pred_class_prob=d.mean(), sd=d.std(), n=N))
pd.DataFrame(del_rows).to_csv(f'{OUT}/xai_deletion.csv', index=False)

# stability: perturbation (5% SD Gaussian noise on continuous agg features) and across training seeds
cont = np.array([j < nagg and not np.allclose(Xf[:2000, j], np.round(Xf[:2000, j])) for j in range(len(cols))])
sd = np.nanstd(Xf, 0)
def perturb(X, rs):
    r = np.random.RandomState(rs); Xp = X.copy(); Xp[:, cont] += r.normal(0, 1, (len(X), cont.sum())) * 0.05 * sd[cont]; return Xp
st_shap = np.mean([[jac(topk(S_shap[i], 5), topk(Sp, 5)) for i, Sp in enumerate(ens_shap(exps0, w0, perturb(Xs, rep))[0])] for rep in range(10)], 0)
st_lime_p, st_lime_s = [], []
for i in range(NL):
    b5 = topk(L_d[i], 5)
    st_lime_p.append(np.mean([jac(b5, topk(run_lime(lime_d, perturb(Xs[i:i + 1], rep)[0], zTs[i]), 5)) for rep in range(3)]))
    st_lime_s.append(np.mean([jac(b5, topk(run_lime(lime_d, Xs[i], zTs[i], rs=s), 5)) for s in [1, 2, 3]]))
seed_phis = [S_shap]
for s in SEEDS[1:]:
    ms, w, wT, b = load_seed(s); ex = {f: shap.TreeExplainer(ms[f]) for f in FAM}
    seed_phis.append(ens_shap(ex, w, Xs)[0])
seed_j = [np.mean([jac(topk(seed_phis[a][i], 5), topk(seed_phis[c][i], 5)) for a in range(5) for c in range(a + 1, 5)]) for i in range(N)]
per_inst = pd.DataFrame({'stab_shap_perturb': st_shap, 'stab_shap_seeds': seed_j})
per_inst_l = pd.DataFrame({'stab_lime_perturb': st_lime_p, 'stab_lime_seed': st_lime_s})
per_inst.assign(protocol=PROTO, task=TASK).to_csv(f'{OUT}/xai_stability_shap_per_instance.csv', index=False)
per_inst_l.assign(protocol=PROTO, task=TASK).to_csv(f'{OUT}/xai_stability_lime_per_instance.csv', index=False)
agr.assign(protocol=PROTO, task=TASK).to_csv(f'{OUT}/xai_agreement_per_instance.csv', index=False)
q_rows = [('SHAP-LIME agreement: Jaccard top-5', agr.jac_shap_lime, N), ('SHAP-LIME(no discretization) agreement: Jaccard top-5', agr.jac_shap_lime_nodisc, N),
          ('SHAP-LIME agreement: Kendall tau on |attr| of LIME top-10', agr.kendall, N), ('SHAP-LIME sign agreement on shared top-5', agr.sign_agree, N),
          ('Stability SHAP: Jaccard top-5 under perturbation (10 reps)', per_inst.stab_shap_perturb, N),
          ('Stability SHAP: Jaccard top-5 across 5 training seeds (pairwise)', per_inst.stab_shap_seeds, N),
          ('Stability LIME: Jaccard top-5 under perturbation (3 reps)', per_inst_l.stab_lime_perturb, NL),
          ('Stability LIME: Jaccard top-5 across LIME sampling seeds (3)', per_inst_l.stab_lime_seed, NL)]
qs = pd.DataFrame([dict(protocol=PROTO, task=TASK, metric=m, mean=np.nanmean(v), sd=np.nanstd(v), n=n) for m, v, n in q_rows] +
                  [dict(protocol=PROTO, task=TASK, metric='Runtime ensemble TreeSHAP (s/instance)', mean=shap_rt, sd=np.nan, n=N),
                   dict(protocol=PROTO, task=TASK, metric='Runtime LIME 1000 samples (s/instance)', mean=lime_rt, sd=np.nan, n=N),
                   dict(protocol=PROTO, task=TASK, metric='Perturbed continuous features (count)', mean=int(cont.sum()), sd=np.nan, n=len(cols))])
qs.to_csv(f'{OUT}/xai_quality.csv', index=False)
log('DONE (full)')
