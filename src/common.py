"""Shared configuration and utilities for the experiments."""
import os, sys, numpy as np, pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PARSED, WORK, RES, FIG  # directories (repository-relative defaults, overridable via env vars)

for d in (WORK, RES, FIG):
    os.makedirs(d, exist_ok=True)

TIME_NUM = ['hour', 'weekday', 'month', 'timesincemidnight', 'timesincelastevent', 'timesincecasestart', 'event_nr']

# Feature column sets follow irhete/predictive-monitoring-benchmark experiments/dataset_confs.py
COLS = {
    'bpic2012': dict(dyn_cat=['Activity', 'Resource'], static_cat=[], dyn_num=TIME_NUM + ['open_cases'],
                     static_num=['AMOUNT_REQ']),
    'bpic2017': dict(dyn_cat=['Activity', 'Resource', 'Action', 'EventOrigin', 'lifecycle', 'Accepted', 'Selected'],
                     static_cat=['ApplicationType', 'LoanGoal'],
                     dyn_num=['FirstWithdrawalAmount', 'MonthlyCost', 'NumberOfTerms', 'OfferedAmount', 'CreditScore']
                     + TIME_NUM + ['open_cases'], static_num=['RequestedAmount']),
    'sepsis': dict(dyn_cat=['Activity', 'Resource'],
                   static_cat=['Diagnose', 'DiagnosticArtAstrup', 'DiagnosticBlood', 'DiagnosticECG', 'DiagnosticIC',
                               'DiagnosticLacticAcid', 'DiagnosticLiquor', 'DiagnosticOther', 'DiagnosticSputum',
                               'DiagnosticUrinaryCulture', 'DiagnosticUrinarySediment', 'DiagnosticXthorax', 'DisfuncOrg',
                               'Hypotensie', 'Hypoxie', 'InfectionSuspected', 'Infusion', 'Oligurie', 'SIRSCritHeartRate',
                               'SIRSCritLeucos', 'SIRSCritTachypnea', 'SIRSCritTemperature', 'SIRSCriteria2OrMore'],
                   dyn_num=['CRP', 'LacticAcid', 'Leucocytes'] + TIME_NUM + ['open_cases'], static_num=['Age']),
    'traffic': dict(dyn_cat=['Activity', 'Resource', 'lastSent', 'notificationType', 'dismissal'],
                    static_cat=['article', 'vehicleClass'], dyn_num=['expense'] + TIME_NUM + ['open_cases'],
                    static_num=['amount', 'points']),
}

# task -> (log, description, adverse label value [label=1 is always the benchmark "deviant"/positive class])
TASKS = {
    'bpic2012_accepted': ('bpic2012', 'BPIC2012: last offer event is O_ACCEPTED', 0),
    'bpic2012_declined': ('bpic2012', 'BPIC2012: last offer event is O_DECLINED', 1),
    'bpic2012_cancelled': ('bpic2012', 'BPIC2012: last offer event is O_CANCELLED', 1),
    'bpic2017_accepted': ('bpic2017', 'BPIC2017: last Offer-origin event is O_Accepted', 0),
    'bpic2017_refused': ('bpic2017', 'BPIC2017: last Offer-origin event is O_Refused', 1),
    'bpic2017_cancelled': ('bpic2017', 'BPIC2017: last Offer-origin event is O_Cancelled', 1),
    'sepsis_cases_1': ('sepsis', 'Sepsis: Return ER within 28 days of previous event', 1),
    'sepsis_cases_2': ('sepsis', 'Sepsis: Admission IC occurs', 1),
    'sepsis_cases_3': ('sepsis', 'Sepsis: Release A occurs (benchmark script output sepsis_cases_4.csv)', 0),
    'traffic_fines_1': ('traffic', 'Traffic fines: Send for Credit Collection occurs', 1),
}
BENCH_TASKS = list(TASKS)
STRICT_TASKS = ['bpic2012_accepted', 'bpic2017_accepted', 'sepsis_cases_1', 'traffic_fines_1']
# decision prefix length for cost-based decisioning (one decision per case)
DECISION_PREFIX = {'bpic2012': 5, 'bpic2017': 5, 'sepsis': 5, 'traffic': 2}

FIT_CAP = 80_000      # max fit prefixes (whole cases subsampled)
VAL_CAP = 50_000      # max validation prefixes
TUNE_CAP = 30_000     # max fit prefixes used inside Optuna trials

SEEDS = [0, 1, 2, 3, 4]


def group_of(protocol, task):
    """Data group (shared encoding) for a task."""
    log = TASKS[task][0]
    if protocol == 'benchmark' and log in ('bpic2012', 'bpic2017'):
        return log
    return task


def ece_score(y, p, n_bins=15):
    bins = np.linspace(0, 1, n_bins + 1)
    idx = np.clip(np.digitize(p, bins[1:-1]), 0, n_bins - 1)
    e = 0.0
    for b in range(n_bins):
        m = idx == b
        if m.any():
            e += m.mean() * abs(y[m].mean() - p[m].mean())
    return e


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def weighted_auc_fast(order_vals, y, W):
    """AUC for many weight vectors at once.
    order_vals: predictions; y: labels (0/1); W: (B, n) nonneg weights (bootstrap counts). Ties counted 1/2."""
    o = np.argsort(order_vals, kind='mergesort')
    v = order_vals[o]; yy = y[o]; Wo = W[:, o]
    # group ties
    _, start = np.unique(v, return_index=True)
    grp = np.zeros(len(v), int); grp[start[1:]] = 1; grp = np.cumsum(grp)
    ng = grp.max() + 1
    out = np.empty(W.shape[0])
    for b in range(W.shape[0]):
        wpos = np.bincount(grp, weights=Wo[b] * yy, minlength=ng)
        wneg = np.bincount(grp, weights=Wo[b] * (1 - yy), minlength=ng)
        cneg = np.cumsum(wneg) - wneg  # negatives strictly below
        num = np.sum(wpos * (cneg + 0.5 * wneg))
        den = wpos.sum() * wneg.sum()
        out[b] = num / den if den > 0 else np.nan
    return out


def case_bootstrap_weights(case_codes, B, rng):
    """Case-cluster bootstrap: returns (B, n) weights = multiplicity of each prefix's case."""
    ncase = case_codes.max() + 1
    W = np.empty((B, len(case_codes)), np.float32)
    for b in range(B):
        cnt = np.bincount(rng.randint(0, ncase, ncase), minlength=ncase).astype(np.float32)
        W[b] = cnt[case_codes]
    return W


def delong(y, p1, p2):
    """Paired DeLong test (Sun & Xu fast version). Returns auc1, auc2, z, p (two-sided)."""
    from scipy.stats import norm, rankdata
    pos = y == 1; neg = ~pos
    m, n = pos.sum(), neg.sum()
    def comps(p):
        tx = rankdata(p[pos]); ty = rankdata(p[neg]); tz = rankdata(np.r_[p[pos], p[neg]])
        auc = (tz[:m].sum() - m * (m + 1) / 2) / (m * n)
        v01 = (tz[:m] - tx) / n
        v10 = 1 - (tz[m:] - ty) / m
        return auc, v01, v10
    a1, v01a, v10a = comps(p1); a2, v01b, v10b = comps(p2)
    sx = np.cov(np.vstack([v01a, v01b])); sy = np.cov(np.vstack([v10a, v10b]))
    s = sx / m + sy / n
    var = s[0, 0] + s[1, 1] - 2 * s[0, 1]
    z = (a1 - a2) / np.sqrt(var) if var > 0 else 0.0
    return a1, a2, z, 2 * norm.sf(abs(z))
