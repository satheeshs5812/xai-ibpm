"""Publication figures (300 dpi PNG + PDF) from <results>/ALL_*.csv and per-task SHAP samples."""
import sys, os, json, glob, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.ticker
from common import *

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.titlesize': 9, 'axes.labelsize': 8.5,
                     'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5, 'legend.fontsize': 7.5, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.grid': True, 'grid.color': '#e6e6e3', 'grid.linewidth': 0.6,
                     'axes.edgecolor': '#52514e', 'axes.linewidth': 0.7, 'savefig.bbox': 'tight', 'figure.dpi': 100,
                     'lines.linewidth': 1.6, 'legend.frameon': False})
# validated categorical order (dataviz reference palette, light mode), fixed per entity
PAL = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#6250d6', '#e34948']
MAIN = ['LR', 'RF', 'XGB', 'LGBM', 'CatBoost', 'LSTM', 'Transformer', 'Stack (proposed)']
COL = {'Stack (proposed)': '#2a78d6', 'LGBM': '#eb6834', 'XGB': '#1baf7a', 'CatBoost': '#eda100', 'LR': '#e87ba4',
       'RF': '#008300', 'Transformer': '#6250d6', 'LSTM': '#e34948'}
INK, INK2 = '#0b0b0b', '#52514e'
REP = ['bpic2012_accepted', 'bpic2017_accepted', 'sepsis_cases_2', 'traffic_fines_1']
def R(f): return pd.read_csv(f'{RES}/{f}')
def save(fig, name):
    fig.savefig(f'{FIG}/{name}.png', dpi=300); fig.savefig(f'{FIG}/{name}.pdf'); plt.close(fig); print('saved', name)

summ = R('ALL_model_results_summary.csv')
ranks = R('ALL_stats_avg_ranks.csv'); fried = R('ALL_stats_friedman_nemenyi.csv')

# 1. Critical-difference diagram
for proto in fried.protocol.unique():
    rk = ranks[ranks.protocol == proto].sort_values('avg_rank'); fr = fried[fried.protocol == proto].iloc[0]
    k = len(rk); cd = fr.nemenyi_CD
    fig, ax = plt.subplots(figsize=(7.2, 2.9)); ax.grid(False)
    for s in ['left', 'bottom', 'right']: ax.spines[s].set_visible(False)
    ax.set_xlim(k + 0.2, 0.8); ax.set_ylim(0, 1); ax.set_yticks([]); ax.xaxis.set_ticks_position('top')
    ax.spines['top'].set_visible(True); ax.set_xticks(range(1, k + 1))
    names = list(rk.model); avgs = list(rk.avg_rank)
    half = (k + 1) // 2
    # cliques (groups whose rank range is within CD) drawn just below the axis
    cl = []
    for i in range(k):
        j = max([j for j in range(i, k) if avgs[j] - avgs[i] <= cd])
        if j > i and not any(c[0] <= i and c[1] >= j for c in cl): cl.append((i, j))
    for t, (i, j) in enumerate(cl):
        yy = 0.92 - t * 0.05
        ax.plot([avgs[i] - 0.04, avgs[j] + 0.04], [yy, yy], color=INK2, lw=2.4, solid_capstyle='round', zorder=3)
    y0 = 0.92 - len(cl) * 0.05 - 0.06
    for i, (n, a) in enumerate(zip(names, avgs)):
        best_side = i < half        # best-ranked models to the right (rank 1 side)
        row = i if best_side else (k - 1 - i)
        y = y0 - row * 0.12
        xe = 0.8 if best_side else k + 0.2
        ax.plot([a, a, xe], [1.0, y, y], color=COL[n], lw=1.2, clip_on=False)
        ax.text(xe - 0.06 if best_side else xe + 0.06, y, f'{n} ({a:.2f})', ha='left' if best_side else 'right', va='center',
                fontsize=7.5, color=INK, fontweight='bold' if 'proposed' in n else 'normal', clip_on=False)
    ax.plot([k, k - cd], [0.05, 0.05], color=INK, lw=1.4)
    ax.text(k - cd / 2, 0.08, f'critical difference CD = {cd:.2f}', ha='center', va='bottom', fontsize=7.2)
    ax.set_title(f'{proto.upper()} protocol: average AUC rank over {int(fr.n_tasks)} tasks (Friedman p = {fr.friedman_p:.2g}; Nemenyi α = 0.05)', fontsize=8.5, pad=18)
    save(fig, f'fig01_cd_diagram_{proto}')

# 2. Heatmap AUC models x tasks
for proto in ['benchmark', 'strict']:
    A = summ[(summ.protocol == proto) & summ.model.isin(MAIN)].pivot(index='model', columns='task', values='auc_mean').reindex(MAIN)
    if A.empty: continue
    order = [t for t in BENCH_TASKS if t in A.columns]; A = A[order]
    fig, ax = plt.subplots(figsize=(0.62 * len(order) + 2.2, 3.3)); ax.grid(False)
    im = ax.imshow(A.values, cmap='Blues', vmin=0.5, vmax=1.0, aspect='auto')
    best = A.values.argmax(0)
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            v = A.values[i, j]
            ax.text(j, i, f'{v:.3f}', ha='center', va='center', fontsize=6.6, color='white' if v > 0.8 else INK,
                    fontweight='bold' if best[j] == i else 'normal')
    ax.set_xticks(range(len(order))); ax.set_xticklabels([t.replace('_', ' ') for t in order], rotation=40, ha='right')
    ax.set_yticks(range(len(MAIN))); ax.set_yticklabels(MAIN)
    for s in ax.spines.values(): s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02); cb.set_label('test AUC (mean of 5 seeds)'); cb.outline.set_visible(False)
    ax.set_title(f'{proto.upper()} protocol: test AUC (bold = best per task)')
    save(fig, f'fig02_auc_heatmap_{proto}')

# 3. AUC vs prefix length small multiples
plb = R('ALL_prefix_auc_bootstrap.csv')
for proto in ['benchmark', 'strict']:
    tasks = [t for t in BENCH_TASKS if ((plb.protocol == proto) & (plb.task == t)).any()]
    if not tasks: continue
    nc = 5 if len(tasks) > 4 else 4; nr = int(np.ceil(len(tasks) / nc))
    fig, axs = plt.subplots(nr, nc, figsize=(1.9 * nc, 1.75 * nr + 0.4), squeeze=False)
    for ax, t in zip(axs.flat, tasks):
        d = plb[(plb.protocol == proto) & (plb.task == t)]
        d = d[d.n >= 30]
        for mdl in d.model.unique():
            e = d[d.model == mdl].sort_values('prefix_len')
            ax.fill_between(e.prefix_len, e.ci_lo, e.ci_hi, color=COL[mdl], alpha=0.15, lw=0)
            ax.plot(e.prefix_len, e.auc, color=COL[mdl], lw=1.9 if 'proposed' in mdl else 1.1, label=mdl)
        ax.set_title(t.replace('_', ' '), fontsize=7.8); ax.set_ylim(0.1, 1.0); ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    for ax in axs.flat[len(tasks):]: ax.axis('off')
    for ax in axs[:, 0]: ax.set_ylabel('AUC')
    for ax in axs[-1]: ax.set_xlabel('prefix length')
    hs = {}
    for ax in axs.flat:
        for h, l in zip(*ax.get_legend_handles_labels()): hs[l] = h
    fig.legend(hs.values(), hs.keys(), loc='lower center', ncol=len(hs), bbox_to_anchor=(0.5, -0.04))
    fig.suptitle(f'{proto.upper()}: AUC by prefix length, proposed vs 3 best baselines per task (seed 0, 95% case-bootstrap bands; n≥30 prefixes)', fontsize=8.5)
    fig.tight_layout(rect=(0, 0.03, 1, 0.97))
    save(fig, f'fig03_auc_vs_prefix_{proto}')

# 4. Reliability diagrams
rel = R('ALL_reliability.csv')
fig, axs = plt.subplots(1, 4, figsize=(9, 2.5))
rc = {'LGBM (raw)': '#eb6834', 'Stack: meta-LR output': '#6250d6', 'Stack (proposed, calibrated)': '#2a78d6'}
cal = R('ALL_calibration_comparison.csv')
for ax, t in zip(axs, REP):
    ax.plot([0, 1], [0, 1], color=INK2, lw=0.8, ls='--')
    for mdl, c in rc.items():
        e = rel[(rel.protocol == 'benchmark') & (rel.task == t) & (rel.model == mdl)]
        ax.plot(e.mean_pred, e.frac_pos, marker='o', ms=3.5, color=c, label=mdl)
    ece_raw = summ[(summ.protocol == 'benchmark') & (summ.task == t) & (summ.model == 'LGBM')].ece_mean.values
    ece_st = summ[(summ.protocol == 'benchmark') & (summ.task == t) & (summ.model == 'Stack (proposed)')].ece_mean.values
    if len(ece_raw) and len(ece_st):
        ax.text(0.03, 0.97, f'ECE LGBM {ece_raw[0]:.3f}\nECE proposed {ece_st[0]:.3f}', transform=ax.transAxes, va='top', fontsize=6.8, color=INK2)
    ax.set_title(t.replace('_', ' ')); ax.set_xlabel('mean predicted probability'); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
axs[0].set_ylabel('observed positive fraction')
axs[0].legend(loc='lower right', fontsize=6.5)
fig.suptitle('Reliability diagrams (BENCHMARK, seed 0, 10 equal-width bins with ≥20 prefixes)', fontsize=8.5); fig.tight_layout()
save(fig, 'fig04_reliability')

# 5. SHAP beeswarm, dependence, waterfall
import shap
def pretty(c): return c.replace('cnt_', '#').replace('Activity=', '').replace('Resource=', 'res ').replace('static_', '')
fig = plt.figure(figsize=(11, 8.5))
for i, t in enumerate(REP):
    p = f'{RES}/per_task/benchmark/{t}/shap_sample.npz'
    if not os.path.exists(p): continue
    z = np.load(p, allow_pickle=True)
    ax = fig.add_subplot(2, 2, i + 1); plt.sca(ax)
    shap.summary_plot(z['phi'], z['X'], feature_names=[pretty(c) for c in z['cols']], max_display=10, show=False, plot_size=None, color_bar=(i % 2 == 1))
    ax.set_title(t.replace('_', ' ') + ' (ensemble TreeSHAP, log-odds)', fontsize=8.5); ax.tick_params(labelsize=7); ax.xaxis.label.set_size(7.5)
fig.tight_layout(); save(fig, 'fig05a_shap_beeswarm')
z = np.load(f'{RES}/per_task/strict/bpic2017_accepted/shap_sample.npz', allow_pickle=True)
cols = list(z['cols']); top = np.argsort(-np.abs(z['phi']).mean(0))[0]
fig, ax = plt.subplots(figsize=(4.2, 3.0))
x = z['X'][:, top]; ok = ~np.isnan(x)
ax.scatter(x[ok], z['phi'][ok, top], s=6, color=COL['Stack (proposed)'], alpha=0.5, lw=0)
ax.set_xlabel(pretty(cols[top]) + ' (feature value)'); ax.set_ylabel('SHAP value (log-odds)'); ax.axhline(0, color=INK2, lw=0.7)
ax.set_title('STRICT bpic2017 accepted: dependence of top ensemble-SHAP feature', fontsize=8.5)
save(fig, 'fig05b_shap_dependence')
w = pd.read_csv(f'{RES}/per_task/strict/bpic2017_accepted/waterfall_deferred_case.csv')
w = w.reindex(w.shap.abs().sort_values(ascending=False).index)
top = w.head(10); rest = w.shap.iloc[10:].sum()
labels = [f'{pretty(f)} = {v:.4g}' for f, v in zip(top.feature, top.value)] + ['other features (sum)', 'Transformer term']
vals = list(top.shap) + [rest, top.transformer_term.iloc[0]]
start = top.base_tree.iloc[0] + top.intercept.iloc[0]
fig, ax = plt.subplots(figsize=(6.2, 3.8)); ax.grid(axis='y', visible=False)
cur = start
for i, v in enumerate(vals):
    ax.barh(len(vals) - 1 - i, v, left=cur, color='#e34948' if v > 0 else '#2a78d6', height=0.65)
    ax.text(cur + v + (0.01 if v > 0 else -0.01), len(vals) - 1 - i, f'{v:+.3f}', va='center', ha='left' if v > 0 else 'right', fontsize=6.8, color=INK)
    cur += v
ax.set_yticks(range(len(vals))); ax.set_yticklabels(labels[::-1], fontsize=7)
ax.axvline(start, color=INK2, lw=0.7, ls='--'); ax.axvline(cur, color=INK, lw=0.9)
cum = start + np.cumsum([0] + vals); lo, hi = cum.min(), cum.max(); pad = 0.25 * (hi - lo); ax.set_xlim(lo - pad, hi + pad)
r0 = w.iloc[0]
ax.set_xlabel('ensemble log-odds (meta-learner scale)')
ax.set_title(f'STRICT bpic2017 accepted, deferred case (conformal set {{{"0" if r0.set_contains_0 else ""}{"," if r0.set_contains_0 and r0.set_contains_1 else ""}{"1" if r0.set_contains_1 else ""}}} at α=0.1), '
             f'prefix {int(r0.prefix_len)}, calibrated p={r0.p_calibrated:.2f}, true label={int(r0.label)}', fontsize=7.8)
save(fig, 'fig05c_waterfall_deferred_case')

# 6. Explanation quality
if os.path.exists(f'{RES}/ALL_xai_stability_shap_per_instance.csv'):
    ss = R('ALL_xai_stability_shap_per_instance.csv'); sl = R('ALL_xai_stability_lime_per_instance.csv'); dl = R('ALL_xai_deletion.csv')
    tasks = [t for t in REP if t in ss.task.unique()]
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.0), gridspec_kw={'width_ratios': [1.5, 1]})
    ax = axs[0]; pos = 0; ticks = []
    mc = {'SHAP perturb.': '#2a78d6', 'SHAP train seeds': '#1baf7a', 'LIME perturb.': '#eb6834', 'LIME sampling seeds': '#e34948'}
    for t in tasks:
        a = ss[ss.task == t]; b = sl[sl.task == t]
        data = [a.stab_shap_perturb, a.stab_shap_seeds, b.stab_lime_perturb, b.stab_lime_seed]
        bp = ax.boxplot(data, positions=pos + np.arange(4) * 0.8, widths=0.6, patch_artist=True, showfliers=False, medianprops=dict(color=INK, lw=1))
        for patch, c in zip(bp['boxes'], mc.values()): patch.set_facecolor(c); patch.set_alpha(0.75); patch.set_edgecolor(INK2)
        ticks.append(pos + 1.2); pos += 4
    ax.set_xticks(ticks); ax.set_xticklabels([t.replace('_', ' ') for t in tasks]); ax.set_ylabel('Jaccard of top-5 features')
    ax.legend([plt.Rectangle((0, 0), 1, 1, fc=c, alpha=0.75) for c in mc.values()], mc.keys(), ncol=2, loc='lower left', fontsize=6.8)
    ax.set_title('Explanation stability (higher = more stable)')
    ax = axs[1]
    dc = {'SHAP': '#2a78d6', 'LIME': '#eb6834', 'LIME (no discretization)': '#eda100', 'random': INK2}
    agg = dl[dl.task.isin(tasks)].groupby(['method', 'k']).mean_drop_pred_class_prob.mean().reset_index()
    for meth, c in dc.items():
        e = agg[agg.method == meth]; ax.plot(e.k, e.mean_drop_pred_class_prob, marker='o', ms=3.5, color=c, label=meth)
    ax.set_xlabel('k features removed'); ax.set_ylabel('drop in predicted-class probability'); ax.legend(fontsize=6.8)
    ax.set_title(f'Deletion fidelity (mean over {len(tasks)} tasks)')
    fig.tight_layout(); save(fig, 'fig06_explanation_quality')

# 7. Risk-coverage + conformal coverage
rcv = R('ALL_risk_coverage.csv'); cc = R('ALL_conformal_curve.csv')
fig, axs = plt.subplots(1, 5, figsize=(12, 2.6))
for ax, t in zip(axs[:4], REP):
    for mdl in ['Stack (proposed)', 'LGBM', 'LR', 'Transformer']:
        e = rcv[(rcv.protocol == 'benchmark') & (rcv.task == t) & (rcv.model == mdl)]
        ax.fill_between(e.coverage, e.ci_lo, e.ci_hi, color=COL[mdl], alpha=0.15, lw=0)
        ax.plot(e.coverage, e.risk, color=COL[mdl], lw=1.8 if 'proposed' in mdl else 1.1, label=mdl if t == REP[0] else None)
    ax.set_title(t.replace('_', ' ')); ax.set_xlabel('coverage (automated share)')
axs[0].set_ylabel('error rate on automated'); axs[0].legend(fontsize=6.5)
ax = axs[4]
for i, t in enumerate(BENCH_TASKS):
    e = cc[(cc.protocol == 'benchmark') & (cc.task == t) & (cc.method == 'Mondrian')]
    ax.plot(1 - e.alpha, e.empirical_coverage, color='#2a78d6', alpha=0.45, lw=0.9)
ax.plot([0.6, 1], [0.6, 1], color=INK, ls='--', lw=0.8, label='nominal')
ax.plot([], [], color='#2a78d6', label='Mondrian conformal (10 tasks)')
ax.set_xlabel('nominal coverage 1−α'); ax.set_ylabel('empirical test coverage'); ax.legend(fontsize=6.5); ax.set_title('Conformal coverage')
fig.suptitle('Risk–coverage curves with 95% case-bootstrap bands (BENCHMARK, seed 0) and conformal coverage', fontsize=8.5)
fig.tight_layout(); save(fig, 'fig07_risk_coverage_conformal')

# 8. Net benefit curves
cs = R('ALL_cost_summary.csv')
pc = {'Stack (proposed) q>r': '#2a78d6', 'LGBM raw q>r': '#eb6834', 'LR q>r': '#e87ba4', 'Transformer q>r': '#6250d6',
      'Stack (proposed) fixed 0.5 threshold': '#1baf7a', 'always intervene': INK2, 'never intervene': '#9b9a95', 'oracle': INK}
fig, axs = plt.subplots(1, 4, figsize=(11, 2.8))
for ax, t in zip(axs, REP):
    for pol, c in pc.items():
        e = cs[(cs.protocol == 'benchmark') & (cs.task == t) & (cs.policy == pol)].sort_values('cost_ratio')
        ls = ':' if pol in ('always intervene', 'never intervene', 'oracle') else '-'
        ax.plot(e.cost_ratio, e.nb_mean, color=c, ls=ls, lw=1.8 if 'proposed) q' in pol else 1.0, label=pol if t == REP[0] else None)
    ymax = cs[(cs.protocol == 'benchmark') & (cs.task == t) & (cs.policy == 'oracle')].nb_mean.max()
    ax.set_ylim(-0.1, (ymax if ymax == ymax else 0.5) * 1.05); ax.set_title(t.replace('_', ' ')); ax.set_xlabel('cost ratio r = C/B')
axs[0].set_ylabel('net benefit per case (units of B)')
fig.legend(loc='lower center', ncol=4, bbox_to_anchor=(0.5, -0.1)); fig.suptitle('Decision curves: intervene iff P(adverse) > r (BENCHMARK, mean of 5 seeds)', fontsize=8.5)
fig.tight_layout(rect=(0, 0.06, 1, 1)); save(fig, 'fig08_net_benefit')

# 9. Ablation
ab = R('ALL_ablation_summary.csv'); ab = ab[ab.protocol == 'benchmark']
var = ['Stack (proposed)', 'Stack w/o Transformer', 'Stack w/o post-calibration', 'Best tuned GBM + isotonic', 'Stack of default GBMs (untuned)', 'LGBM', 'Transformer']
lab = ['Proposed', 'w/o Transformer', 'w/o post-calib.', 'single GBM+iso', 'untuned stack', 'LGBM (raw)', 'Transformer']
fig, axs = plt.subplots(1, 3, figsize=(10.5, 2.9))
for ax, (mcol, title) in zip(axs, [('auc_mean', 'test AUC'), ('ece_mean', 'ECE (lower is better)'), ('singleton_rate_a0_1_mean', 'automation rate (conformal α=0.1)')]):
    P = ab.pivot(index='task', columns='variant', values=mcol).reindex(columns=var)
    mu = P.mean(); se = P.std() / np.sqrt(P.notna().sum())
    ax.bar(range(len(var)), mu, yerr=1.96 * se, color=['#2a78d6'] + ['#9b9a95'] * (len(var) - 1), width=0.65, error_kw=dict(lw=0.8, ecolor=INK2, capsize=2))
    for j, v in enumerate(var):
        ax.scatter(np.full(len(P), j) + np.random.RandomState(j).uniform(-0.18, 0.18, len(P)), P[v], s=5, color=INK, alpha=0.5, zorder=3, lw=0)
    ax.set_xticks(range(len(var))); ax.set_xticklabels(lab, rotation=40, ha='right'); ax.set_title(title)
    if mcol == 'auc_mean': ax.set_ylim(0.4, 1.0)
fig.suptitle('Ablation (BENCHMARK, mean over 10 tasks ± 95% CI across tasks; dots = tasks)', fontsize=8.5)
fig.tight_layout(); save(fig, 'fig09_ablation')
