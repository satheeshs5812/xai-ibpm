"""Build the result tables of the paper (Tables 3, 6-16) and the in-text numbers from <results>/ALL_*.csv.

Usage: python3 src/make_tables.py
Output: <results>/tables/table_NN_<name>.md (one Markdown table per paper table), <results>/tables/paper_tables.md
(all tables in paper order) and <results>/tables/in_text_numbers.json (numbers quoted in the text of Sections 5-6).
Only reads CSV files; no model is retrained. Tables 1, 2, 4, 5 and 17 of the paper are literature/design tables
written by hand (Table 5 corresponds to the search spaces in train_gbm.py / train_deep.py; Table 17 quotes values
from Tables 6, 7, 12, 14 and 15).
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from config import RES

OUT = os.path.join(RES, 'tables'); os.makedirs(OUT, exist_ok=True)
R = lambda f: pd.read_csv(os.path.join(RES, f + '.csv'))
TN = {'bpic2012_accepted': 'BPIC12-acc', 'bpic2012_cancelled': 'BPIC12-can', 'bpic2012_declined': 'BPIC12-dec',
      'bpic2017_accepted': 'BPIC17-acc', 'bpic2017_cancelled': 'BPIC17-can', 'bpic2017_refused': 'BPIC17-ref',
      'sepsis_cases_1': 'Sepsis-1', 'sepsis_cases_2': 'Sepsis-2', 'sepsis_cases_3': 'Sepsis-3', 'traffic_fines_1': 'Traffic'}
MODELS = ['LR', 'RF', 'XGB', 'LGBM', 'CatBoost', 'LSTM', 'Transformer', 'Stack (proposed)']
MN = {m: m for m in MODELS}; MN['Stack (proposed)'] = '**Stack (proposed)**'
REP = ['bpic2012_accepted', 'bpic2017_accepted', 'sepsis_cases_2', 'traffic_fines_1']
T = {}   # number -> (title, markdown)

# ---------------------------------------------------------------- Table 3: dataset statistics
d = R('ALL_dataset_stats')
o = ['| Protocol | Task | Cases | Events | Activities | Variants | Mean length | Positive ratio | K | Train / test cases | Test prefixes | Features |', '|' + '---|' * 12]
for _, r in d.iterrows():
    o.append(f"| {r.protocol.upper()} | {TN[r.task]} | {r.cases:,} | {r.events:,} | {r.activities} | {r.variants:,} | {r.mean_case_length:.1f} | {r.positive_case_ratio:.3f} | {r.max_prefix_len_K} | {r.train_cases:,} / {r.test_cases:,} | {r.test_prefixes:,} | {r.n_features_agg} |")
T[3] = ('Prediction tasks and event-log statistics', '\n'.join(o))

# ---------------------------------------------------------------- Tables 6 / 7: AUC
m = R('ALL_model_results_summary')
for num, prot in [(6, 'benchmark'), (7, 'strict')]:
    tasks = [t for t in TN if ((m.protocol == prot) & (m.task == t)).any()]
    o = ['| Task | ' + ' | '.join(MN[x] for x in MODELS) + ' |', '|' + '---|' * (len(MODELS) + 1)]
    for t in tasks:
        e = m[(m.protocol == prot) & (m.task == t)].set_index('model')
        best = e.loc[MODELS, 'auc_mean'].max()
        cells = []
        for x in MODELS:
            a = e.loc[x, 'auc_mean']; s = e.loc[x, 'auc_sd']
            c = f"{a:.3f}" + (f" ± {s:.3f}" if s == s and x != 'LR' else '')
            if abs(a - best) < 5e-4: c = f"**{c}**"
            cells.append(c)
        o.append(f'| {TN[t]} | ' + ' | '.join(cells) + ' |')
    mean = [m[(m.protocol == prot) & (m.model == x)].auc_mean.mean() for x in MODELS]
    o.append('| Mean | ' + ' | '.join(f'{v:.3f}' for v in mean) + ' |')
    T[num] = (f'Test AUC, {prot.upper()} protocol (mean ± SD over 5 seeds)', '\n'.join(o))

# ---------------------------------------------------------------- Table 8: ranks + Wilcoxon-Holm
rk = R('ALL_stats_avg_ranks'); w = R('ALL_stats_wilcoxon_holm')
o = ['| Model | Avg rank (B) | Wins (B) | Mean AUC (B) | Δ AUC stack − model (B) | Wilcoxon p, Holm (B) | Avg rank (S) | Mean AUC (S) | Δ AUC stack − model (S) |', '|' + '---|' * 9]
for x in MODELS:
    rb = rk[(rk.protocol == 'benchmark') & (rk.model == x)].iloc[0]; rs = rk[(rk.protocol == 'strict') & (rk.model == x)].iloc[0]
    if x != 'Stack (proposed)':
        wb = w[(w.protocol == 'benchmark') & (w.comparison == f'Stack (proposed) vs {x}')].iloc[0]
        ws = w[(w.protocol == 'strict') & (w.comparison == f'Stack (proposed) vs {x}')].iloc[0]
        o.append(f"| {MN[x]} | {rb.avg_rank:.2f} | {rb.wins} | {rb.mean_auc:.3f} | {wb.mean_auc_diff:+.4f} | {wb.p_holm:.3f}{'*' if wb.p_holm < 0.05 else ''} | {rs.avg_rank:.2f} | {rs.mean_auc:.3f} | {ws.mean_auc_diff:+.4f} |")
    else:
        o.append(f"| {MN[x]} | **{rb.avg_rank:.2f}** | **{rb.wins}** | **{rb.mean_auc:.3f}** | — | — | **{rs.avg_rank:.2f}** | {rs.mean_auc:.3f} | — |")
fr = R('ALL_stats_friedman_nemenyi')
o.append('')
for _, r in fr.iterrows():
    o.append(f"Friedman ({r.protocol.upper()}): χ² = {r.friedman_chi2:.2f}, p = {r.friedman_p:.3f}; Nemenyi CD = {r.nemenyi_CD:.2f}  ")
T[8] = ('Average ranks, mean AUC and pairwise tests of the stack vs each baseline', '\n'.join(o))

# ---------------------------------------------------------------- Table 9: per-task stack vs best baseline
pw = R('ALL_pairwise_tests'); b = pw[pw.is_best_baseline]
o = ['| Protocol | Task | Best baseline | AUC stack | AUC baseline | Δ AUC | 95% case-bootstrap CI of Δ | Bootstrap p |', '|' + '---|' * 8]
for _, r in b.iterrows():
    o.append(f"| {r.protocol.upper()} | {TN[r.task]} | {r.comparison.split(' vs ')[1]} | {r.auc_proposed:.3f} | {r.auc_baseline:.3f} | {r.delta:+.4f} | [{r.boot_delta_ci_lo:+.4f}, {r.boot_delta_ci_hi:+.4f}] | {'<0.001' if r.boot_p_two_sided < 0.001 else f'{r.boot_p_two_sided:.3f}'} |")
T[9] = ('Per-task comparison of the stack with the best baseline (seed 0; 1,000 case-level bootstrap resamples)', '\n'.join(o))

# ---------------------------------------------------------------- Table 10: leakage (protocol effect + top SHAP features)
st = m[m.model == 'Stack (proposed)'].set_index(['protocol', 'task'])
sh = R('ALL_shap_global_top20')
def top(prot, t, n=4):
    e = sh[(sh.protocol == prot) & (sh.task == t)].sort_values('rank').head(n)
    pr = lambda f: f.replace('cnt_Activity=', '#').replace('cnt_Resource=', '#res ').replace('cnt_', '#').replace('static_', '')
    return '; '.join(f"{pr(f)} ({v:.2f})" for f, v in zip(e.feature, e.mean_abs_shap))
o = ['| Task | AUC BENCHMARK | AUC STRICT | Δ AUC | Top features BENCHMARK | Top features STRICT |', '|' + '---|' * 6]
for t in ['bpic2012_accepted', 'bpic2017_accepted', 'sepsis_cases_1', 'traffic_fines_1']:
    ab = st.loc[('benchmark', t), 'auc_mean']; as_ = st.loc[('strict', t), 'auc_mean']
    o.append(f"| {TN[t]} | {ab:.3f} | {as_:.3f} | {as_ - ab:+.3f} | {top('benchmark', t)} | {top('strict', t)} |")
T[10] = ('Effect of the evaluation protocol on the stack and top ensemble-SHAP features', '\n'.join(o))

# ---------------------------------------------------------------- Table 11: calibration
CM = ['LGBM', 'XGB', 'CatBoost', 'LSTM', 'Transformer', 'Stack (proposed)']
o = ['| Protocol | Task | ' + ' | '.join(CM) + ' |', '|' + '---|' * (len(CM) + 2)]
for prot in ['benchmark', 'strict']:
    tasks = [t for t in TN if ((m.protocol == prot) & (m.task == t)).any()]
    for t in tasks:
        e = m[(m.protocol == prot) & (m.task == t)].set_index('model')
        bb = e.loc[CM, 'brier_mean'].min(); be = e.loc[CM, 'ece_mean'].min()
        cells = []
        for x in CM:
            br = e.loc[x, 'brier_mean']; ec = e.loc[x, 'ece_mean']
            sb = f"**{br:.3f}**" if abs(br - bb) < 5e-4 else f"{br:.3f}"; se = f"**{ec:.3f}**" if abs(ec - be) < 5e-4 else f"{ec:.3f}"
            cells.append(f"{sb} / {se}")
        o.append(f'| {prot.upper()} | {TN[t]} | ' + ' | '.join(cells) + ' |')
    o.append(f'| {prot.upper()} | Mean | ' + ' | '.join(f"{m[(m.protocol == prot) & (m.model == x)].brier_mean.mean():.3f} / {m[(m.protocol == prot) & (m.model == x)].ece_mean.mean():.3f}" for x in CM) + ' |')
T[11] = ('Calibration on the test set: Brier score / ECE (mean over 5 seeds)', '\n'.join(o))

# ---------------------------------------------------------------- Table 12: explanation quality
q = R('ALL_xai_quality'); pv = q.pivot_table(index='metric', columns='task', values='mean'); sd = q.pivot_table(index='metric', columns='task', values='sd')
rows = [('SHAP stability: input perturbation', 'Stability SHAP: Jaccard top-5 under perturbation (10 reps)'),
        ('SHAP stability: across 5 training seeds', 'Stability SHAP: Jaccard top-5 across 5 training seeds (pairwise)'),
        ('LIME stability: input perturbation', 'Stability LIME: Jaccard top-5 under perturbation (3 reps)'),
        ('LIME stability: across sampling seeds', 'Stability LIME: Jaccard top-5 across LIME sampling seeds (3)'),
        ('SHAP–LIME agreement: top-5 Jaccard', 'SHAP-LIME agreement: Jaccard top-5'),
        ('SHAP–LIME (no discretisation): top-5 Jaccard', 'SHAP-LIME(no discretization) agreement: Jaccard top-5'),
        ("SHAP–LIME agreement: Kendall's τ", 'SHAP-LIME agreement: Kendall tau on |attr| of LIME top-10'),
        ('SHAP–LIME sign agreement on shared features', 'SHAP-LIME sign agreement on shared top-5'),
        ('Runtime ensemble TreeSHAP (ms / instance)', 'Runtime ensemble TreeSHAP (s/instance)'),
        ('Runtime LIME, 1,000 samples (ms / instance)', 'Runtime LIME 1000 samples (s/instance)')]
o = ['| Criterion | ' + ' | '.join(TN[t] for t in REP) + ' |', '|' + '---|' * 5]
for lab, k in rows:
    cells = [f"{pv.loc[k, t] * 1000:.0f}" for t in REP] if 'Runtime' in k else [f"{pv.loc[k, t]:.2f} ± {sd.loc[k, t]:.2f}" for t in REP]
    o.append(f'| {lab} | ' + ' | '.join(cells) + ' |')
T[12] = ('Explanation quality of the proposed ensemble (BENCHMARK, 100 stratified test prefixes; LIME stability on 30)', '\n'.join(o))

# ---------------------------------------------------------------- Table 13: deletion fidelity
dl = R('ALL_xai_deletion'); p = dl.pivot_table(index=['method', 'k'], columns='task', values='mean_drop_pred_class_prob')
o = ['| Method | k | ' + ' | '.join(TN[t] for t in REP) + ' | Mean |', '|' + '---|' * 7]
for mth in ['SHAP', 'LIME', 'LIME (no discretization)', 'random']:
    for k in [1, 3, 5, 10]:
        v = [p.loc[(mth, k), t] for t in REP]; mean = sum(v) / 4
        name = {'LIME (no discretization)': 'LIME (no discretisation)', 'random': 'Random'}.get(mth, mth)
        f = (lambda x: f"**{x:.3f}**") if mth == 'SHAP' else (lambda x: f"{x:.3f}")
        o.append(f'| {name} | {k} | ' + ' | '.join(f(x) for x in v) + f' | {f(mean)} |')
T[13] = ('Deletion fidelity: mean drop in predicted-class probability when the top-k features are removed', '\n'.join(o).replace('| -0.000 |', '| 0.000 |'))

# ---------------------------------------------------------------- Table 14: Mondrian conformal deferral
c = R('ALL_conformal_summary'); cm = c[c.method.str.startswith('Mondrian') & (c.alpha == 0.1)]
o = ['| Protocol | Task | Coverage | Coverage class 0 | Coverage class 1 | Automation rate | Accuracy (all) | Accuracy (automated) | AUC (all) | AUC (automated) |', '|' + '---|' * 10]
for _, r in cm.iterrows():
    s_ = st.loc[(r.protocol, r.task)]
    o.append(f"| {r.protocol.upper()} | {TN[r.task]} | {r.empirical_coverage_mean:.3f} | {r.coverage_class0_mean:.3f} | {r.coverage_class1_mean:.3f} | {r.singleton_rate_mean:.3f} | {s_.acc_mean:.3f} | {r.accuracy_on_singletons_mean:.3f} | {s_.auc_mean:.3f} | {r.auc_on_singletons_mean:.3f} |")
T[14] = ('Mondrian conformal deferral at α = 0.1 (nominal coverage 0.90)', '\n'.join(o))

# ---------------------------------------------------------------- Table 15: cost-based decisioning
ch = R('ALL_cost_headline')
o = ['| Protocol | Task | r | Stack q > r | Stack, fixed 0.5 | LGBM raw q > r | Always intervene | Oracle | Gap closed |', '|' + '---|' * 9]
for _, r in ch[ch.cost_ratio.round(2).isin([0.3, 0.5, 0.7])].iterrows():
    o.append(f"| {r.protocol.upper()} | {TN[r.task]} | {r.cost_ratio:.1f} | {r['Stack (proposed) q>r']:+.3f} | {r['Stack (proposed) fixed 0.5 threshold']:+.3f} | {r['LGBM raw q>r']:+.3f} | {r['always intervene']:+.3f} | {r.oracle:.3f} | {r.frac_of_oracle_gap * 100:.0f}% |")
T[15] = ('Net benefit per case (units of b) at cost ratios r = c/b (mean over 5 seeds)', '\n'.join(o).replace('-0%', '0%').replace('| -0.000 |', '| 0.000 |'))

# ---------------------------------------------------------------- Table 16: ablation
a = R('ALL_ablation_summary'); g = a.groupby(['protocol', 'variant'])[['auc_mean', 'brier_mean', 'ece_mean', 'logloss_mean', 'singleton_rate_a0_1_mean']].mean()
VN = [('Stack (proposed)', '**Full model (tuned stack + monotone calibrator selection)**'), ('Stack w/o post-calibration', 'Without post-hoc calibrator'),
      ('Stack w/o Transformer', 'Without Transformer base model'), ('Stack of default GBMs (untuned)', 'Without hyper-parameter tuning (default GBMs, 1 seed)'),
      ('Best tuned GBM + isotonic', 'Single best tuned GBM + isotonic (no stacking)'), ('LGBM', 'Single tuned LightGBM, uncalibrated'), ('Transformer', 'Single Transformer')]
o = ['| Variant | AUC (B) | Brier (B) | ECE (B) | Log-loss (B) | Automation (B) | AUC (S) | ECE (S) | Automation (S) |', '|' + '---|' * 9]
for k, lab in VN:
    b_ = g.loc[('benchmark', k)]; s_ = g.loc[('strict', k)]
    o.append(f"| {lab} | {b_.auc_mean:.3f} | {b_.brier_mean:.3f} | {b_.ece_mean:.3f} | {b_.logloss_mean:.3f} | {b_.singleton_rate_a0_1_mean:.3f} | {s_.auc_mean:.3f} | {s_.ece_mean:.3f} | {s_.singleton_rate_a0_1_mean:.3f} |")
T[16] = ('Ablation of the proposed model (mean over tasks; B = BENCHMARK, S = STRICT)', '\n'.join(o))

# ---------------------------------------------------------------- in-text numbers (Sections 5-6)
K = {}
rki = rk.set_index(['protocol', 'model']); fri = fr.set_index('protocol')
K['avg_rank_stack_benchmark'] = round(rki.loc[('benchmark', 'Stack (proposed)'), 'avg_rank'], 2)
K['avg_rank_stack_strict'] = round(rki.loc[('strict', 'Stack (proposed)'), 'avg_rank'], 2)
K['mean_auc_stack_benchmark'] = round(rki.loc[('benchmark', 'Stack (proposed)'), 'mean_auc'], 4)
K['mean_auc_stack_strict'] = round(rki.loc[('strict', 'Stack (proposed)'), 'mean_auc'], 4)
K['wins_stack_benchmark'] = int(rki.loc[('benchmark', 'Stack (proposed)'), 'wins'])
K['friedman_benchmark'] = dict(chi2=round(fri.loc['benchmark', 'friedman_chi2'], 2), p=round(fri.loc['benchmark', 'friedman_p'], 3), nemenyi_CD=round(fri.loc['benchmark', 'nemenyi_CD'], 2))
mb = m[(m.protocol == 'benchmark') & m.model.isin(MODELS)].pivot(index='task', columns='model', values='auc_mean')
K['benchmark_tasks_within_0.01_of_best'] = int(((mb.max(1) - mb['Stack (proposed)']) <= 0.01).sum())
for p_, kk in [('benchmark', 'benchmark'), ('strict', 'strict')]:
    e = m[(m.protocol == p_) & (m.model == 'Stack (proposed)')]
    K[f'mean_brier_stack_{kk}'] = round(e.brier_mean.mean(), 3); K[f'mean_ece_stack_{kk}'] = round(e.ece_mean.mean(), 3)
bw = m[(m.protocol == 'benchmark') & m.model.isin(MODELS)].pivot(index='task', columns='model', values='brier_mean')
K['benchmark_tasks_stack_lowest_brier'] = int((bw.idxmin(1) == 'Stack (proposed)').sum())
sm = R('ALL_stack_meta'); K['stack_calibrator_counts'] = sm.chosen_calibrator.value_counts().to_dict()
K['stack_meta_weights_mean'] = sm.groupby('protocol')[['meta_w_LGBM', 'meta_w_XGB', 'meta_w_CatBoost', 'meta_w_Transformer']].mean().round(3).to_dict('index')
for p_ in ['benchmark', 'strict']:
    e = cm[cm.protocol == p_]
    K[f'conformal_a0.1_mean_coverage_{p_}'] = round(e.empirical_coverage_mean.mean(), 3)
    K[f'conformal_a0.1_mean_automation_{p_}'] = round(e.singleton_rate_mean.mean(), 3)
K['conformal_benchmark_tasks_within_0.02'] = int(((0.9 - cm[cm.protocol == 'benchmark'].empirical_coverage_mean) <= 0.02).sum())
for p_ in ['benchmark', 'strict']:
    e = ch[ch.protocol == p_]
    K[f'cost_share_at_least_best_trivial_{p_}'] = round((e.gain_vs_trivial >= -1e-9).mean(), 3)
    K[f'cost_share_strictly_better_{p_}'] = round((e.gain_vs_trivial > 1e-9).mean(), 3)
    K[f'cost_mean_gain_vs_trivial_{p_}'] = round(e.gain_vs_trivial.mean(), 4)
G = lambda p_, v, col: g.loc[(p_, v), col]
K['ablation_auc_gain_vs_single_gbm'] = {p_: round(G(p_, 'Stack (proposed)', 'auc_mean') - G(p_, 'Best tuned GBM + isotonic', 'auc_mean'), 4) for p_ in ['benchmark', 'strict']}
K['ablation_auc_gain_vs_no_transformer'] = {p_: round(G(p_, 'Stack (proposed)', 'auc_mean') - G(p_, 'Stack w/o Transformer', 'auc_mean'), 4) for p_ in ['benchmark', 'strict']}
K['ablation_auc_gain_vs_untuned'] = {p_: round(G(p_, 'Stack (proposed)', 'auc_mean') - G(p_, 'Stack of default GBMs (untuned)', 'auc_mean'), 4) for p_ in ['benchmark', 'strict']}

allmd = []
for n in sorted(T):
    title, body = T[n]
    slug = title.split(':')[0].split('(')[0].strip().lower().replace(' ', '_').replace(',', '').replace('/', '_')[:40].strip('_')
    txt = f'## Table {n}. {title}\n\n{body}\n'
    open(os.path.join(OUT, f'table_{n:02d}_{slug}.md'), 'w').write(txt)
    allmd.append(txt)
open(os.path.join(OUT, 'paper_tables.md'), 'w').write('# Result tables of the paper (generated by src/make_tables.py)\n\n' + '\n'.join(allmd))
json.dump(K, open(os.path.join(OUT, 'in_text_numbers.json'), 'w'), indent=1, ensure_ascii=False, default=float)
print('wrote', len(T), 'tables to', OUT)
