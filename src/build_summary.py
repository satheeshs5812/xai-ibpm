"""Build <results>/results_summary.md from ALL_*.csv (all numbers read from files)."""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import *

MAIN = ['LR', 'RF', 'XGB', 'LGBM', 'CatBoost', 'LSTM', 'Transformer', 'Stack (proposed)']
def R(f): return pd.read_csv(f'{RES}/{f}')
def md(df, fl=4):
    df = df.copy()
    for c in df.columns:
        if df[c].dtype.kind == 'f': df[c] = df[c].map(lambda v: '' if pd.isna(v) else f'{v:.{fl}f}')
    return '| ' + ' | '.join(map(str, df.columns)) + ' |\n|' + '---|' * len(df.columns) + '\n' + '\n'.join('| ' + ' | '.join(map(str, r)) + ' |' for r in df.values) + '\n'
def pm(m, s, f=4): return f'{m:.{f}f} ± {s:.{f}f}' if not pd.isna(s) else f'{m:.{f}f}'
L = []
A = L.append
summ = R('ALL_model_results_summary.csv'); stats = R('ALL_dataset_stats.csv')
A('# Results summary: tuned, state-of-the-art models, two evaluation protocols, statistics and governance\n')
A('All numbers in this file are read from the CSV files in `results/` produced by the scripts in `src/` on the original 4TU.ResearchData event logs '
  '(SHA-256 checksums in `data/README.md`). Nothing was synthesised, adjusted or copied from the literature. '
  'mean ± sd is over 5 training seeds (0–4) unless stated otherwise; LR is deterministic (1 run).\n')

A('## 1. Prediction tasks and dataset statistics\n')
A('Labels re-implement the preprocessing scripts of irhete/predictive-monitoring-benchmark (Teinemaa et al., TKDD 2019), '
  'downloaded from raw.githubusercontent.com and kept in `teinemaa_ref/` for reference. label = 1 is always the benchmark "deviant" class. '
  '`sepsis_cases_3` (Release A) is written by the benchmark script as `sepsis_cases_4.csv`; we use the paper\'s name.\n')
A('Sanity check against the benchmark: our labelled logs give BPIC2012 4,685 cases (K = 40), BPIC2017 31,413 cases (K = 20), '
  'Sepsis 782 cases (K = 29 / 13 / 22 for tasks 1 / 2 / 3), Traffic fines 129,615 cases after removing incomplete cases (K = 10); '
  'these are the case counts and prefix caps produced by the benchmark rules.\n')
cols = ['protocol', 'task', 'label_definition', 'cases', 'events', 'activities', 'variants', 'mean_case_length', 'max_case_length', 'positive_case_ratio',
        'max_prefix_len_K', 'train_cases', 'test_cases', 'fit_prefixes_before_subsample', 'fit_prefixes_used', 'val_prefixes_used', 'test_prefixes',
        'test_positive_prefix_ratio', 'n_features_agg', 'n_features_agg_index', 'split_timestamp']
A(md(stats[cols]))
A('\n"events"/"cases" refer to the labelled log after case filtering and after the protocol\'s truncation. fit/val prefixes are after whole-case subsampling '
  f'(caps: {FIT_CAP:,} fit prefixes, {VAL_CAP:,} validation prefixes); test prefixes are never subsampled.\n')

A('## 2. The two evaluation protocols\n')
A('''| aspect | BENCHMARK (literature-comparable) | STRICT (leakage-free) |
|---|---|---|
| tasks | all 10 tasks | bpic2012_accepted, bpic2017_accepted, sepsis_cases_1, traffic_fines_1 |
| BPIC2012 truncation | none (as in the benchmark script; outcome events O_ACCEPTED/O_DECLINED/O_CANCELLED and A_* decision events stay in the prefixes if they occur within K events) | cut before first O_ACCEPTED/O_DECLINED/O_CANCELLED or A_APPROVED/A_REGISTERED/A_ACTIVATED/A_DECLINED/A_CANCELLED (COMPLETE) |
| BPIC2017 truncation | none (as in the benchmark script) | cut before first O_Accepted/O_Refused/O_Cancelled/A_Pending/A_Denied/A_Cancelled |
| Sepsis truncation | cut before the label activity (Return ER / Admission IC / Release A), as in the script | same (sepsis_cases_1 only) |
| Traffic | cases whose last event is "Send Fine" removed (incomplete); cut before Send for Credit Collection | no incomplete-case removal; cut before Send for Credit Collection |
| prefix cap K | traffic 10; BPIC2017 min(20, q90 of positive case length); others min(40, q90 positive length) → 40 / 20 / 29 / 13 / 22 / 10 | fixed 20 (traffic 10) |
| inter-case feature open_cases | included (benchmark; note it uses each case's end time, i.e. future information) | excluded (not observable at prediction time) |
| everything else | identical: temporal 80/20 split with train events after the first test start discarded; train split again 80/20 temporally into fit / validation; validation split by case start into part A (first half) and part B (second half); same encoders and models | identical |
''')
A('Deviations from the benchmark code that apply to both protocols: categorical vocabularies are fitted on the fit split only (benchmark: whole log); '
  'hyper-parameters are tuned on a temporal validation split (benchmark: random 3-fold CV inside train); one model for all prefix lengths (no bucketing); '
  'BPIC2012/2017 benchmark tasks are encoded once per log (labels differ only).\n')

A('## 3. Models, encodings and tuning\n')
A('''- **Encodings.** (a) `agg`: Teinemaa static+aggregation encoding — counts of every dynamic categorical level (activity, resource, and log-specific attributes), mean/max/min/sum/std of every dynamic numeric attribute (incl. time features hour, weekday, month, time since midnight, time since last event, time since case start, event number, and open_cases in BENCHMARK), static categorical one-hot and static numeric values. (b) `agg+index`: `agg` plus a lagged index encoding of the last 10 events (activity code, resource code, log time since previous event at lags 1..10; missing = NaN). Integer codes are frequency ranks on the fit split. For each GBM family the encoding was selected on the validation split with default hyper-parameters (table below), then tuned. LR and RF use `agg`. Prefix-length bucketing was not used (one model over all prefix lengths, prefix length is a feature).
- **Tuning.** Optuna 5.0 TPE sampler (seed 0), objective = AUC on the temporal validation split (never the test set), training on a ≤30,000-prefix whole-case subsample of the fit split, early stopping on validation (30 rounds, ≤600 trees). Trials: LightGBM 30, XGBoost 30, CatBoost 20 (CatBoost fewer for CPU budget); the first trial is the default configuration. Because XGBoost with the agg+index encoding was ~10× slower than expected on BPIC2017/traffic (28 min for 30 trials on bpic2017_refused), a wall-clock cap of 480 s per family study was added for the four tasks tuned last (benchmark traffic_fines_1 and bpic2017_cancelled, strict bpic2017_accepted and traffic_fines_1); the number of trials actually completed per task/family is given in the table (`n_trials_completed`). Final models: best parameters, full fit split, ≤1000 trees, early stopping (50) on validation, seeds 0–4.
  - LightGBM: learning_rate [0.02, 0.3] log; num_leaves [15, 255] log; min_child_samples [5, 200] log; subsample [0.5, 1]; colsample_bytree [0.3, 1]; reg_alpha, reg_lambda [1e-3, 10] log.
  - XGBoost (hist): learning_rate [0.02, 0.3] log; max_depth [3, 10]; min_child_weight [1, 50] log; subsample [0.5, 1]; colsample_bytree [0.3, 1]; gamma [1e-3, 5] log; reg_alpha, reg_lambda [1e-3, 10] log.
  - CatBoost (border_count 64): learning_rate [0.03, 0.3] log; depth [4, 8]; l2_leaf_reg [1, 30] log; bagging_temperature [0, 1]; random_strength [1e-3, 10] log.
- **Baselines.** LR (standardised, L2, C ∈ {0.01, 0.1, 1} chosen on validation); RF (150 trees, min_samples_leaf 5, max_features sqrt, max_samples 0.5).
- **Deep sequence models** (PyTorch, CPU). Input per event: activity embedding (16), resource embedding (8), standardised signed-log dynamic numeric attributes, static attributes repeated per step, linearly projected. Many-to-many training (one output per prefix position; BCE averaged over valid positions), Adam, batch 128 cases, gradient clipping 1.0, early stopping (patience 3) on validation prefix AUC, max 12 epochs (25 for logs with < 5,000 fit cases). LSTM: 1 layer, configs {h=64, lr 1e-3}, {h=128, lr 1e-3}, {h=64, lr 3e-3}. Transformer (ProcessTransformer-style, causal mask, learned positional embeddings, 4 heads, FF = 2d): {d=32, 1 layer, lr 1e-3}, {d=64, 2 layers, lr 1e-3}, {d=64, 2 layers, lr 3e-4}. Light tuning = best config on validation at seed 0, then seeds 0–4.
- **Proposed model ("Stack (proposed)").** Logistic-regression meta-learner (C = 1) on the log-odds of tuned LightGBM, XGBoost, CatBoost and Transformer, fitted on validation part A (base models never saw part A in training; part A was used for their early stopping/tuning). Post-hoc calibrator chosen per seed among none / Platt / isotonic / beta (Kull et al. 2017) / inductive Venn–Abers (merged p1/(1−p0+p1), evaluated on a 51-point score grid with linear interpolation) by grouped (by case) 5-fold cross-validated log-loss on out-of-fold meta predictions within part A. Validation part B is reserved for conformal calibration and deferral thresholds.
''')
bp = R('ALL_best_params.csv')
A('### Encoding selection, best hyper-parameters and validation AUC\n')
A(md(bp[bp.family.isin(['LGBM', 'XGB', 'CatBoost'])][['protocol', 'task', 'family', 'encoding', 'enc_val_auc_agg', 'enc_val_auc_agg_index', 'n_trials_completed', 'val_auc_default_trial', 'best_val_auc_tuning', 'final_iters', 'best_params', 'tuning_time_s']], 4))
A('\n### Deep models: configuration search (validation AUC, seed 0) and epochs used per seed\n')
A(md(bp[bp.family.isin(['LSTM', 'Transformer'])][['protocol', 'task', 'family', 'best_params', 'tuning', 'final_iters']]))
lrc = bp[bp.family == 'LGBM'][['protocol', 'task', 'LR_C']]
A('\nLR regularisation chosen: ' + '; '.join(f'{r.protocol}/{r.task}: C={r.LR_C}' for r in lrc.itertuples()) + '\n')

A('## 4. Predictive performance (test set, all prefixes pooled)\n')
for proto in ['benchmark', 'strict']:
    s = summ[(summ.protocol == proto) & summ.model.isin(MAIN)]
    tbl = s.assign(v=[pm(a, b) for a, b in zip(s.auc_mean, s.auc_sd)]).pivot(index='task', columns='model', values='v')[MAIN]
    A(f'### {proto.upper()}: AUC mean ± sd over seeds\n'); A(md(tbl.reset_index()))
    ci = s.assign(v=[f'{a:.4f} [{l:.4f}, {h:.4f}]' for a, l, h in zip(s.auc_seed0, s.ci_lo, s.ci_hi)]).pivot(index='task', columns='model', values='v')[MAIN]
    A(f'\n{proto.upper()}: seed-0 AUC with 95% case-cluster bootstrap CI (1,000 resamples of test cases)\n'); A(md(ci.reset_index()))
    for met in ['brier', 'ece']:
        t2 = s.assign(v=[pm(a, b) for a, b in zip(s[f'{met}_mean'], s[f'{met}_sd'])]).pivot(index='task', columns='model', values='v')[MAIN]
        A(f'\n{proto.upper()}: {met.upper()} mean ± sd\n'); A(md(t2.reset_index()))
    oth = s[['task', 'model', 'logloss_mean', 'acc_mean', 'f1_macro_mean', 'train_s_mean', 'infer_ms_per_1000_mean']]
    A(f'\n{proto.upper()}: log-loss, accuracy, macro-F1 (threshold 0.5), training time (s, per seed; Stack = sum of its 4 base models) and inference time (ms per 1,000 prefixes)\n')
    A(md(oth, 3))

A('## 5. Statistical comparison\n')
fr = R('ALL_stats_friedman_nemenyi.csv'); rk = R('ALL_stats_avg_ranks.csv'); wl = R('ALL_stats_wilcoxon_holm.csv')
A('Friedman test over tasks on the seed-averaged test AUC of the 8 main models; Iman–Davenport F; Nemenyi critical difference (α = 0.05, q from the studentised range / √2). '
  'Wilcoxon signed-rank (two-sided) of the proposed model against each baseline across tasks, Holm-corrected over the 7 comparisons. '
  'With 4 STRICT tasks the smallest attainable two-sided Wilcoxon p is 0.125, so STRICT tests cannot reach significance by construction.\n')
A(md(fr)); A('\nAverage ranks (1 = best) and wins\n'); A(md(rk.sort_values(['protocol', 'avg_rank'])))
A('\nWilcoxon signed-rank, proposed vs each baseline\n'); A(md(wl))
if os.path.exists(f'{RES}/ALL_stats_nemenyi_pairwise_p_benchmark.csv'):
    A('\nNemenyi pairwise p-values (BENCHMARK)\n'); A(md(pd.read_csv(f'{RES}/ALL_stats_nemenyi_pairwise_p_benchmark.csv').rename(columns={'Unnamed: 0': 'model'})))
pw = R('ALL_pairwise_tests.csv')
A('\n### Per-task paired tests: proposed vs best baseline (best = highest mean test AUC among the 7 baselines; seed-0 predictions)\n')
A('DeLong assumes independent prefixes (prefixes of the same case are correlated, so DeLong p-values are optimistic); the paired case-cluster bootstrap (1,000 resamples of cases, same resample for both models) respects the clustering.\n')
A(md(pw[pw.is_best_baseline][['protocol', 'task', 'comparison', 'auc_proposed', 'auc_baseline', 'delta', 'delong_z', 'delong_p', 'boot_delta_ci_lo', 'boot_delta_ci_hi', 'boot_p_two_sided']]))
A('\nAll pairwise per-task tests are in `ALL_pairwise_tests.csv`.\n')

A('## 6. Calibration\n')
sm = R('ALL_stack_meta.csv')
ch = sm.groupby(['protocol', 'task']).chosen_calibrator.agg(lambda s: ', '.join(s)).reset_index()
A('Calibrator chosen for the stack (per seed 0..4) by cross-validated log-loss on validation part A:\n'); A(md(ch))
A('\nMeta-learner weights on base-model log-odds (mean over seeds):\n')
A(md(sm.groupby(['protocol', 'task'])[[c for c in sm.columns if c.startswith('meta_w_')]].mean().reset_index(), 3))
cs = R('ALL_calibration_summary.csv')
A('\nCalibrator comparison (fit on validation part A, evaluated on test; mean over seeds). ECE uses 15 equal-width bins.\n')
for proto in ['benchmark', 'strict']:
    c = cs[(cs.protocol == proto)]
    t = c.pivot_table(index=['task', 'model'], columns='calibrator', values='ece').reset_index()
    A(f'\n{proto.upper()} ECE by calibrator\n'); A(md(t))
    t = c.pivot_table(index=['task', 'model'], columns='calibrator', values='brier').reset_index()
    A(f'\n{proto.upper()} Brier by calibrator\n'); A(md(t))

A('## 7. Governance: conformal deferral\n')
A('Split conformal prediction with calibration set = validation part B (temporally later than part A, earlier than test); nonconformity 1 − p̂(true class) on the calibrated stack. '
  'Mondrian = class-conditional quantiles (one per label). A case is automated when the prediction set is a singleton, deferred otherwise (empty or {0,1}). '
  'Coverage guarantees assume exchangeability, which temporal drift and within-case dependence of prefixes violate; empirical coverage is therefore reported, not assumed.\n')
cf = R('ALL_conformal_summary.csv')
for meth in ['Mondrian (class-conditional)', 'marginal split conformal']:
    c = cf[cf.method == meth]
    t = c.assign(cov=[pm(a, b, 3) for a, b in zip(c.empirical_coverage_mean, c.empirical_coverage_std)],
                 cov1=c.coverage_class1_mean.round(3), cov0=c.coverage_class0_mean.round(3),
                 single=[pm(a, b, 3) for a, b in zip(c.singleton_rate_mean, c.singleton_rate_std)],
                 empty=c.empty_rate_mean.round(3), both=c.both_rate_mean.round(3),
                 acc_single=[pm(a, b, 3) for a, b in zip(c.accuracy_on_singletons_mean, c.accuracy_on_singletons_std)])
    A(f'\n### {meth}\n'); A(md(t[['protocol', 'task', 'alpha', 'cov', 'cov1', 'cov0', 'single', 'empty', 'both', 'acc_single']].rename(columns={
        'cov': 'empirical coverage', 'cov1': 'cov. class 1', 'cov0': 'cov. class 0', 'single': 'singleton (automation) rate', 'acc_single': 'accuracy on singletons'})))
A('\n## 8. Governance: confidence-threshold deferral and risk–coverage\n')
A('τ on confidence max(p, 1 − p) is set on validation part B to reach the target coverage and applied to test. `n_unique_conf_values_test` shows how many distinct confidence values exist (isotonic/Venn–Abers plateaus make exact coverage targets unreachable).\n')
dfs = R('ALL_deferral_summary.csv')
A(md(dfs[dfs.target_coverage.isin([0.7, 0.8, 0.9])][['protocol', 'task', 'model', 'target_coverage', 'realized_coverage_mean', 'acc_automated_mean', 'auc_automated_mean', 'n_unique_conf_values_test_mean']], 3))
rcv = R('ALL_risk_coverage.csv')
A('\nArea under the risk–coverage curve (mean error rate over coverage 0.05..1.00; lower is better; seed 0):\n')
A(md(rcv.groupby(['protocol', 'task', 'model']).risk.mean().unstack().reset_index(), 4))

A('\n## 9. Cost-based decisioning\n')
A('One decision per test case at a fixed prefix length (BPIC 5, Sepsis 5, Traffic 2). Intervene iff q = P(adverse) > r, r = C/B. Net benefit per case (units of B) = Σ_intervened (1[adverse] − r) / n; assumes the intervention fully prevents the adverse outcome (stylised). Adverse outcome: accepted tasks → not accepted; declined/cancelled/refused → that outcome; sepsis 1/2 → return ER / ICU admission; sepsis 3 → NOT released with type A; traffic → credit collection. Mean over 5 seeds.\n')
co = R('ALL_cost_summary.csv')
for r in [0.2, 0.5, 0.8]:
    c = co[np.isclose(co.cost_ratio, r)]
    t = c.pivot_table(index=['protocol', 'task'], columns='policy', values='nb_mean').reset_index()
    A(f'\n### r = {r}\n'); A(md(t))
# headline: share of task-ratios where proposed >= max(always, never)
c = co.pivot_table(index=['protocol', 'task', 'cost_ratio'], columns='policy', values='nb_mean').reset_index()
c['best_trivial'] = c[['always intervene', 'never intervene']].max(1)
c['gain_vs_trivial'] = c['Stack (proposed) q>r'] - c['best_trivial']
c['frac_of_oracle_gap'] = c['gain_vs_trivial'] / (c['oracle'] - c['best_trivial'])
c['proposed_minus_fixed05'] = c['Stack (proposed) q>r'] - c['Stack (proposed) fixed 0.5 threshold']
c['proposed_minus_LGBMraw'] = c['Stack (proposed) q>r'] - c['LGBM raw q>r']
c.to_csv(f'{RES}/ALL_cost_headline.csv', index=False)
h = c.groupby('protocol').agg(n=('gain_vs_trivial', 'size'), share_proposed_ge_best_trivial=('gain_vs_trivial', lambda v: (v >= -1e-12).mean()),
                              mean_gain_vs_trivial=('gain_vs_trivial', 'mean'), median_frac_of_oracle_gap=('frac_of_oracle_gap', 'median'),
                              share_proposed_ge_fixed05=('proposed_minus_fixed05', lambda v: (v >= -1e-12).mean()),
                              mean_gain_vs_fixed05=('proposed_minus_fixed05', 'mean'),
                              share_proposed_ge_LGBMraw=('proposed_minus_LGBMraw', lambda v: (v >= -1e-12).mean())).reset_index()
A('\nHeadline over all tasks × cost ratios r ∈ {0.05, …, 0.95} (19 values):\n'); A(md(h))

A('\n## 10. Explanation quality (proposed ensemble, tree part)\n')
A('SHAP: exact additive attribution of the stack log-odds tree part, φ_j = Σ_m w_m φ_mj (TreeSHAP of LightGBM, XGBoost, CatBoost in log-odds; w_m = meta weights), '
  'Transformer term held fixed per instance; additivity error reported in `per_task/*/*/xai_info.json`. LIME (1,000 samples, top-10) explains the same function. '
  '100 stratified test prefixes per task (BENCHMARK representative tasks), LIME stability on 30. Deletion: features supporting the predicted class are removed '
  '(aggregation features → training mean, index features → missing).\n')
if os.path.exists(f'{RES}/ALL_xai_quality.csv'):
    q = R('ALL_xai_quality.csv')
    A(md(q.assign(v=[pm(a, b) for a, b in zip(q['mean'], q['sd'])]).pivot(index='metric', columns='task', values='v').reset_index()))
    d = R('ALL_xai_deletion.csv')
    A('\nDeletion: mean drop in predicted-class probability\n'); A(md(d.pivot_table(index=['task', 'k'], columns='method', values='mean_drop_pred_class_prob').reset_index()))
add = []
for p in glob.glob(f'{RES}/per_task/*/*/xai_info.json'):
    j = json.load(open(p)); add.append(dict(protocol=p.split('/')[-3], task=p.split('/')[-2], additivity_max_abs_err=j['additivity_max_abs_err'], **{f'enc_{k}': v for k, v in j['encodings'].items()}))
A('\nSHAP additivity check (max |Σφ + base − tree-part log-odds| over 2,000 test prefixes):\n'); A(md(pd.DataFrame(add).sort_values(['protocol', 'task']), 8))
sh = R('ALL_shap_global_top20.csv')
A('\nGlobal ensemble SHAP top-10 features (mean |φ|, 2,000 test prefixes, seed 0):\n')
for (p, t), g in sh.groupby(['protocol', 'task']):
    A(f'- **{p}/{t}**: ' + '; '.join(f'{r.feature} ({r.mean_abs_shap:.3f})' for r in g.head(10).itertuples()))
A('')

A('\n## 11. Ablation (mean ± sd over seeds; "untuned stack" uses 1 seed)\n')
ab = R('ALL_ablation_summary.csv')
t = ab.assign(AUC=[pm(a, b) for a, b in zip(ab.auc_mean, ab.auc_std)], ECE=[pm(a, b) for a, b in zip(ab.ece_mean, ab.ece_std)],
              Brier=ab.brier_mean.round(4), conf_cov=ab.conformal_cov_a0_1_mean.round(3), automation=ab.singleton_rate_a0_1_mean.round(3),
              nb_r03=ab.nb_r0_3_mean.round(4), nb_r05=ab.nb_r0_5_mean.round(4))
A(md(t[['protocol', 'task', 'variant', 'AUC', 'ECE', 'Brier', 'conf_cov', 'automation', 'nb_r03', 'nb_r05']]))
abm = ab[ab.protocol == 'benchmark'].groupby('variant')[['auc_mean', 'ece_mean', 'brier_mean', 'singleton_rate_a0_1_mean', 'nb_r0_3_mean']].mean().reset_index()
A('\nBENCHMARK averages over the 10 tasks:\n'); A(md(abm))

if os.path.exists(f'{RES}/caveats.md'):
    A('\n## 12. Caveats and observations\n'); A(open(f'{RES}/caveats.md').read())
if os.path.exists(f'{RES}/runtime_env.md'):
    A('\n## 13. Environment and runtime\n'); A(open(f'{RES}/runtime_env.md').read())
A('\n## 14. Files\n')
A('`results/ALL_*.csv`: tidy tables behind every table and figure (per-seed metrics, summaries, bootstrap CIs, pairwise tests, Friedman/Nemenyi/Wilcoxon, '
  'calibration, reliability, conformal, deferral, risk–coverage, cost, ablation, XAI, best params, Optuna trials, dataset stats). '
  '`results/per_task/<protocol>/<task>/`: the same per task, plus SHAP samples (`shap_sample.npz`) and the deferred-case waterfall data. '
  '`results/figures/`: PNG (300 dpi) + PDF. Code: `src/` (parse_logs.py, prepare.py, train_gbm.py, train_deep.py, evaluate.py, explain.py, aggregate.py, figures.py, make_tables.py, build_summary.py).\n')
A(open(f'{RES}/figures_list.md').read() if os.path.exists(f'{RES}/figures_list.md') else '')
open(f'{RES}/results_summary.md', 'w').write('\n'.join(L))
print('summary written', sum(len(x) for x in L))
