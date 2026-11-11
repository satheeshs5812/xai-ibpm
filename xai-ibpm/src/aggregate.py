"""Collect per-task outputs into tidy ALL_*.csv files and run cross-task statistics."""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import *
from scipy.stats import friedmanchisquare, wilcoxon, studentized_range

MAIN = ['LR', 'RF', 'XGB', 'LGBM', 'CatBoost', 'LSTM', 'Transformer', 'Stack (proposed)']
FILES = ['metrics_per_seed', 'prefix_auc_per_seed', 'calibration_comparison', 'reliability', 'auc_bootstrap_ci', 'pairwise_tests',
         'prefix_auc_bootstrap', 'conformal_per_seed', 'conformal_curve', 'deferral_per_seed', 'risk_coverage', 'cost_per_seed',
         'ablation_per_seed', 'stack_meta', 'shap_global_top20', 'xai_quality', 'xai_deletion', 'xai_stability_shap_per_instance',
         'xai_stability_lime_per_instance', 'xai_agreement_per_instance']
for f in FILES:
    parts = [pd.read_csv(p) for p in sorted(glob.glob(f'{RES}/per_task/*/*/{f}.csv'))]
    if parts:
        pd.concat(parts).to_csv(f'{RES}/ALL_{f}.csv', index=False)

# dataset stats
st = []
for proto in ['benchmark', 'strict']:
    for info_p in glob.glob(f'{WORK}/{proto}/*/info.json'):
        info = json.load(open(info_p))
        for s in info['stats']:
            st.append(s)
pd.DataFrame(st).sort_values(['protocol', 'task']).to_csv(f'{RES}/ALL_dataset_stats.csv', index=False)

# best params / search
bp = []
for proto in ['benchmark', 'strict']:
    for p in glob.glob(f'{WORK}/{proto}/runs/*/gbm_summary.json'):
        s = json.load(open(p))
        for fam in ['LGBM', 'XGB', 'CatBoost']:
            if f'{fam}_best_params' not in s: continue
            bp.append(dict(protocol=proto, task=s['task'], family=fam, encoding=s[f'{fam}_encoding'],
                           enc_val_auc_agg=s[f'{fam}_enc_val_auc']['agg'], enc_val_auc_agg_index=s[f'{fam}_enc_val_auc']['agg+index'],
                           best_val_auc_tuning=s[f'{fam}_best_val_auc_tuning'], tuning_time_s=s[f'{fam}_tuning_time_s'],
                           final_iters=str(s[f'{fam}_final_iters']), best_params=json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in s[f'{fam}_best_params'].items()}),
                           LR_C=s.get('LR_C'), gbm_script_runtime_s=s['runtime_s']))
    for p in glob.glob(f'{WORK}/{proto}/runs/*/deep_summary.json'):
        s = json.load(open(p))
        for fam in ['LSTM', 'Transformer']:
            bp.append(dict(protocol=proto, task=s['task'], family=fam, encoding='sequence', best_params=json.dumps(s[f'{fam}_best_cfg']),
                           tuning=json.dumps([(t['cfg'], round(t['val_auc'], 4)) for t in s[f'{fam}_tuning']]),
                           final_iters='epochs ' + str(s[f'{fam}_epochs']), gbm_script_runtime_s=s['runtime_s']))
pd.DataFrame(bp).sort_values(['protocol', 'task', 'family']).to_csv(f'{RES}/ALL_best_params.csv', index=False)
tr = pd.concat([pd.read_csv(p) for p in glob.glob(f'{WORK}/*/runs/*/optuna_trials.csv')])
tr.to_csv(f'{RES}/ALL_optuna_trials.csv', index=False)
nt = tr.groupby(['protocol', 'task', 'family']).size().rename('n_trials_completed').reset_index()
bpd = pd.read_csv(f'{RES}/ALL_best_params.csv').merge(nt, on=['protocol', 'task', 'family'], how='left')
# default-config (first, enqueued) trial vs best trial on validation
first = tr[tr.trial == 0][['protocol', 'task', 'family', 'value']].rename(columns={'value': 'val_auc_default_trial'})
bpd = bpd.merge(first, on=['protocol', 'task', 'family'], how='left')
bpd.to_csv(f'{RES}/ALL_best_params.csv', index=False)

# model summary (mean ± sd over seeds)
m = pd.read_csv(f'{RES}/ALL_metrics_per_seed.csv')
summ = m.groupby(['protocol', 'task', 'model']).agg(n_seeds=('seed', 'count'), auc_mean=('auc', 'mean'), auc_sd=('auc', 'std'),
                                                     brier_mean=('brier', 'mean'), brier_sd=('brier', 'std'), ece_mean=('ece', 'mean'), ece_sd=('ece', 'std'),
                                                     logloss_mean=('logloss', 'mean'), acc_mean=('accuracy', 'mean'), f1_macro_mean=('f1_macro', 'mean'),
                                                     train_s_mean=('train_s', 'mean'), infer_ms_per_1000_mean=('infer_ms_per_1000', 'mean')).reset_index()
ci = pd.read_csv(f'{RES}/ALL_auc_bootstrap_ci.csv')[['protocol', 'task', 'model', 'auc_seed0', 'ci_lo', 'ci_hi']]
summ = summ.merge(ci, on=['protocol', 'task', 'model'], how='left')
summ.to_csv(f'{RES}/ALL_model_results_summary.csv', index=False)

# ------------------------------------------------------------------ cross-task statistics
stat_rows, rank_rows, wil_rows = [], [], []
def cd_nemenyi(k, N, alpha=0.05):
    q = studentized_range.ppf(1 - alpha, k, np.inf) / np.sqrt(2)
    return q * np.sqrt(k * (k + 1) / (6 * N)), q
for proto, tasks in [('benchmark', BENCH_TASKS), ('strict', STRICT_TASKS)]:
    A = summ[(summ.protocol == proto) & summ.model.isin(MAIN)].pivot(index='task', columns='model', values='auc_mean').reindex(columns=MAIN)
    A = A.dropna()
    if len(A) < 2: continue
    R = A.rank(axis=1, ascending=False)
    avg = R.mean()
    for mdl in MAIN:
        rank_rows.append(dict(protocol=proto, model=mdl, avg_rank=avg[mdl], wins=int((R[mdl] == 1).sum()), n_tasks=len(A), mean_auc=A[mdl].mean()))
    fr = friedmanchisquare(*[A[c].values for c in MAIN])
    N, k = len(A), len(MAIN)
    chi2 = 12 * N / (k * (k + 1)) * (np.sum(avg ** 2) - k * (k + 1) ** 2 / 4)
    ff = (N - 1) * chi2 / (N * (k - 1) - chi2) if N * (k - 1) - chi2 > 0 else np.inf
    cd, q = cd_nemenyi(k, N)
    stat_rows.append(dict(protocol=proto, n_tasks=N, k_models=k, friedman_chi2=fr.statistic, friedman_p=fr.pvalue, iman_davenport_F=ff,
                          nemenyi_q_alpha=q, nemenyi_CD=cd))
    raw = []
    for mdl in MAIN[:-1]:
        d = A['Stack (proposed)'] - A[mdl]
        try:
            w = wilcoxon(A['Stack (proposed)'], A[mdl], zero_method='wilcox', alternative='two-sided')
            p = w.pvalue; sstat = w.statistic
        except ValueError:
            p, sstat = np.nan, np.nan
        raw.append((mdl, p, sstat, d.mean(), int((d > 0).sum()), int((d < 0).sum()), N,
                    abs(avg['Stack (proposed)'] - avg[mdl]) > cd))
    ps = np.array([r[1] for r in raw]); order = np.argsort(ps); holm = np.empty(len(ps)); mx = 0
    for i, j in enumerate(order):
        mx = max(mx, min(1, (len(ps) - i) * ps[j])); holm[j] = mx
    for (mdl, p, sstat, dm, wins, losses, n, nem), h in zip(raw, holm):
        wil_rows.append(dict(protocol=proto, comparison=f'Stack (proposed) vs {mdl}', n_tasks=n, mean_auc_diff=dm, proposed_better=wins,
                             proposed_worse=losses, wilcoxon_W=sstat, p_raw=p, p_holm=h, nemenyi_significant=nem))
pd.DataFrame(stat_rows).to_csv(f'{RES}/ALL_stats_friedman_nemenyi.csv', index=False)
pd.DataFrame(rank_rows).to_csv(f'{RES}/ALL_stats_avg_ranks.csv', index=False)
pd.DataFrame(wil_rows).to_csv(f'{RES}/ALL_stats_wilcoxon_holm.csv', index=False)
# Nemenyi pairwise matrix (benchmark) via scikit-posthocs
try:
    import scikit_posthocs as sp
    A = summ[(summ.protocol == 'benchmark') & summ.model.isin(MAIN)].pivot(index='task', columns='model', values='auc_mean').reindex(columns=MAIN).dropna()
    sp.posthoc_nemenyi_friedman(A.values).set_axis(MAIN, axis=0).set_axis(MAIN, axis=1).to_csv(f'{RES}/ALL_stats_nemenyi_pairwise_p_benchmark.csv')
except Exception as e:
    print('posthoc failed', e)

# summaries of governance / cost / ablation / calibration
c = pd.read_csv(f'{RES}/ALL_conformal_per_seed.csv')
c.groupby(['protocol', 'task', 'method', 'alpha']).agg(['mean', 'std']).drop(columns=['seed', 'n_cal'], level=0).pipe(
    lambda d: d.set_axis([f'{a}_{b}' for a, b in d.columns], axis=1)).reset_index().to_csv(f'{RES}/ALL_conformal_summary.csv', index=False)
d = pd.read_csv(f'{RES}/ALL_deferral_per_seed.csv')
d.groupby(['protocol', 'task', 'model', 'target_coverage']).agg(['mean', 'std']).drop(columns=['seed'], level=0).pipe(
    lambda x: x.set_axis([f'{a}_{b}' for a, b in x.columns], axis=1)).reset_index().to_csv(f'{RES}/ALL_deferral_summary.csv', index=False)
co = pd.read_csv(f'{RES}/ALL_cost_per_seed.csv')
co.groupby(['protocol', 'task', 'cost_ratio', 'policy']).agg(nb_mean=('net_benefit', 'mean'), nb_sd=('net_benefit', 'std'),
                                                             intervention_rate=('intervention_rate', 'mean'), n_seeds=('seed', 'count'),
                                                             decision_prefix_len=('decision_prefix_len', 'first'), n_decision_cases=('n_decision_cases', 'first'),
                                                             adverse_rate=('adverse_rate', 'first')).reset_index().to_csv(f'{RES}/ALL_cost_summary.csv', index=False)
ab = pd.read_csv(f'{RES}/ALL_ablation_per_seed.csv')
ab.groupby(['protocol', 'task', 'variant']).agg(['mean', 'std']).drop(columns=['seed'], level=0).pipe(
    lambda x: x.set_axis([f'{a}_{b}' for a, b in x.columns], axis=1)).reset_index().to_csv(f'{RES}/ALL_ablation_summary.csv', index=False)
cc = pd.read_csv(f'{RES}/ALL_calibration_comparison.csv')
cc.groupby(['protocol', 'task', 'model', 'calibrator']).agg(auc=('auc', 'mean'), brier=('brier', 'mean'), ece=('ece', 'mean'), logloss=('logloss', 'mean'),
                                                             n=('seed', 'count')).reset_index().to_csv(f'{RES}/ALL_calibration_summary.csv', index=False)
print('aggregate done')
