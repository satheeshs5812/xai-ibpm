"""Data preparation: labelling (Teinemaa et al. 2019 benchmark scripts re-implemented), the two evaluation
protocols (BENCHMARK and STRICT), temporal splits, aggregation + lagged-index encodings and sequence tensors.
Usage: python3 prepare.py <protocol> <group>
  benchmark groups: bpic2012, bpic2017, sepsis_cases_1, sepsis_cases_2, sepsis_cases_3, traffic_fines_1
  strict groups:    bpic2012_accepted, bpic2017_accepted, sepsis_cases_1, traffic_fines_1
"""
import sys, os, json, time, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, pandas as pd
from common import *

CASE, TS = 'case', 'ts'
N_LAG = 10  # lagged index encoding: last 10 events


def log_(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def load_base(log):
    df = pd.read_parquet(f'{PARSED}/{log}.parquet')
    df = df.rename(columns={'case:concept:name': CASE, 'time:timestamp': TS})
    if log == 'bpic2012':
        df['Activity'] = df['concept:name'] + '-' + df['lifecycle:transition']
        df['Resource'] = df['org:resource']; df['AMOUNT_REQ'] = df['case:AMOUNT_REQ']
    elif log == 'bpic2017':
        df['Activity'] = df['concept:name']; df['Resource'] = df['org:resource']; df['lifecycle'] = df['lifecycle:transition']
        for c in ['LoanGoal', 'ApplicationType', 'RequestedAmount']:
            df[c] = df['case:' + c]
    elif log == 'sepsis':
        df['Activity'] = df['concept:name']; df['Resource'] = df['org:group']
    else:
        df['Activity'] = df['concept:name']; df['Resource'] = df['org:resource']
    df = df.sort_values([CASE, TS], kind='mergesort').reset_index(drop=True)
    cf = COLS[log]
    for c in cf['dyn_cat'] + cf['static_cat'] + cf['static_num'] + cf['dyn_num']:
        if c not in df.columns:
            df[c] = np.nan
    # benchmark imputation: forward-fill within case; categoricals -> 'missing', numerics -> 0
    attr = [c for c in cf['dyn_cat'] + cf['static_cat'] + cf['static_num'] + cf['dyn_num'] if c not in TIME_NUM + ['open_cases']]
    df[attr] = df.groupby(CASE)[attr].ffill()
    for c in cf['dyn_cat'] + cf['static_cat']:
        df[c] = df[c].astype(str).where(df[c].notna(), 'missing')
    for c in cf['static_num'] + [c for c in cf['dyn_num'] if c not in TIME_NUM + ['open_cases']]:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(float)
    # timestamp features (minutes), local time
    g = df.groupby(CASE)
    df['event_nr'] = g.cumcount() + 1
    df['timesincecasestart'] = (df[TS] - g[TS].transform('min')).dt.total_seconds() / 60
    df['timesincelastevent'] = g[TS].diff().dt.total_seconds().fillna(0) / 60
    loc = df[TS].dt.tz_convert('Europe/Amsterdam')
    df['hour'] = loc.dt.hour; df['weekday'] = loc.dt.weekday; df['month'] = loc.dt.month
    df['timesincemidnight'] = loc.dt.hour * 60 + loc.dt.minute
    return df[[CASE, TS] + list(dict.fromkeys(cf['dyn_cat'] + cf['static_cat'] + cf['static_num'] +
                                               [c for c in cf['dyn_num'] if c != 'open_cases']))]


def add_open_cases(df):
    """Benchmark inter-case feature: #cases with start <= t < end (start/end over the given log)."""
    se = df.groupby(CASE)[TS].agg(['min', 'max'])
    s = np.sort(se['min'].values.astype('int64')); e = np.sort(se['max'].values.astype('int64'))
    t = df[TS].values.astype('int64')
    df['open_cases'] = (np.searchsorted(s, t, 'right') - np.searchsorted(e, t, 'right')).astype(float)
    return df


def recompute_event_nr(df):
    df['event_nr'] = df.groupby(CASE).cumcount() + 1
    return df


def label_bpic(df, log, protocol, tasks):
    if log == 'bpic2012':
        o = df[df['Activity'].str.startswith('O')]
        rel = {'O_ACCEPTED-COMPLETE': 'accepted', 'O_DECLINED-COMPLETE': 'declined', 'O_CANCELLED-COMPLETE': 'cancelled'}
        reveal = ['O_ACCEPTED-COMPLETE', 'O_DECLINED-COMPLETE', 'O_CANCELLED-COMPLETE', 'A_APPROVED-COMPLETE',
                  'A_REGISTERED-COMPLETE', 'A_ACTIVATED-COMPLETE', 'A_DECLINED-COMPLETE', 'A_CANCELLED-COMPLETE']
    else:
        o = df[df['EventOrigin'] == 'Offer']
        rel = {'O_Accepted': 'accepted', 'O_Refused': 'refused', 'O_Cancelled': 'cancelled'}
        reveal = ['O_Accepted', 'O_Refused', 'O_Cancelled', 'A_Pending', 'A_Denied', 'A_Cancelled']
    last_o = o.groupby(CASE)['Activity'].last()
    last_o = last_o[last_o.isin(rel.keys())].map(rel)
    df = df[df[CASE].isin(last_o.index)].copy()
    lab = df[CASE].map(last_o)
    for t in tasks:
        df['label__' + t] = (lab == t.split('_')[1]).astype(int)
    if protocol == 'strict':
        r = df['Activity'].isin(reveal).astype(int).groupby(df[CASE]).cumsum()
        df = df[r == 0].copy()
    return df


def cut_before(df, act):
    hit = (df['Activity'] == act).astype(int).groupby(df[CASE]).cumsum()
    return df[hit == 0].copy()


def label_task(protocol, task):
    log = TASKS[task][0]
    df = load_base(log)
    if log in ('bpic2012', 'bpic2017'):
        df = add_open_cases(df)  # benchmark: computed on the full log before label filtering
        tasks = [t for t in TASKS if TASKS[t][0] == log] if protocol == 'benchmark' else [task]
        df = label_bpic(df, log, protocol, tasks)
    elif log == 'sepsis':
        has_rel = df.groupby(CASE)['Activity'].apply(lambda s: s.isin(['Release A', 'Release B', 'Release C', 'Release D', 'Release E']).any())
        df = df[df[CASE].isin(has_rel[has_rel].index)].copy()
        df = add_open_cases(df)
        tasks = [task]
        if task == 'sepsis_cases_1':
            r = df[df['Activity'] == 'Return ER'].groupby(CASE)['timesincelastevent'].first()
            pos = r[r <= 28 * 1440].index
            df['label__' + task] = df[CASE].isin(pos).astype(int)
            df = cut_before(df, 'Return ER')
        else:
            act = 'Admission IC' if task == 'sepsis_cases_2' else 'Release A'
            pos = df.loc[df['Activity'] == act, CASE].unique()
            df['label__' + task] = df[CASE].isin(pos).astype(int)
            df = cut_before(df, act)
    else:  # traffic
        if protocol == 'benchmark':
            last = df.groupby(CASE)['Activity'].last()
            df = df[~df[CASE].isin(last[last == 'Send Fine'].index)].copy()
        df = add_open_cases(df)
        tasks = [task]
        pos = df.loc[df['Activity'] == 'Send for Credit Collection', CASE].unique()
        df['label__' + task] = df[CASE].isin(pos).astype(int)
        df = cut_before(df, 'Send for Credit Collection')
    df = df.reset_index(drop=True)
    return log, df, tasks


def prefix_cap(protocol, log, df, task):
    if protocol == 'strict':
        return 10 if log == 'traffic' else 20
    if log == 'traffic':
        return 10
    lens = df[df['label__' + task] == 1].groupby(CASE).size()
    q = int(np.ceil(lens.quantile(0.90)))
    return min(20, q) if log == 'bpic2017' else min(40, q)


def temporal_split_strict(df, ratio=0.8):
    starts = df.groupby(CASE)[TS].min().sort_values(kind='mergesort')
    n = int(ratio * len(starts))
    a_ids, b_ids = starts.index[:n], starts.index[n:]
    split_ts = df.loc[df[CASE].isin(b_ids), TS].min()
    a = df[df[CASE].isin(a_ids) & (df[TS] < split_ts)]
    b = df[df[CASE].isin(b_ids)]
    return a, b, split_ts


def subsample_cases(d, K, cap, seed=0):
    n_pref = d.groupby(CASE).size().clip(upper=K)
    if n_pref.sum() <= cap:
        return d
    cases = np.array(n_pref.index.tolist(), dtype=object); np.random.RandomState(seed).shuffle(cases)
    assert len(set(cases)) == len(cases)
    cs = n_pref.reindex(cases).cumsum()
    keep = set(cs[cs <= cap].index)
    return d[d[CASE].isin(keep)]


class AggEncoder:
    """Teinemaa et al. 'static + agg' encoding (counts of dynamic categorical levels; mean/max/min/sum/std of dynamic
    numerics; static one-hot / numeric) + lagged index encoding of the last N_LAG events (activity code, resource code,
    log time since previous event). Vocabularies are fitted on the fit split only."""

    def __init__(self, log, use_open_cases=True):
        cf = COLS[log]
        self.dyn_cat = cf['dyn_cat']; self.static_cat = cf['static_cat']; self.static_num = cf['static_num']
        self.dyn_num = [c for c in cf['dyn_num'] if use_open_cases or c != 'open_cases']
        self.log = log
        if log == 'bpic2017' and not use_open_cases:
            # STRICT: offer attributes Selected / Accepted / CreditScore are stored on O_Create Offer but their values
            # reflect later outcomes (Selected=False never co-occurs with acceptance) -> excluded as leakage
            self.dyn_cat = [c for c in self.dyn_cat if c not in ('Selected', 'Accepted')]
            self.dyn_num = [c for c in self.dyn_num if c != 'CreditScore']

    def fit(self, d):
        self.levels = {}
        for c in self.dyn_cat + self.static_cat:
            vc = d[c].astype(str).value_counts()
            if c == 'Activity':
                lv = list(vc.index)
            else:
                lv = list(vc[vc >= 10].index)
                if c != 'Resource':
                    lv = lv[:10] if self.log == 'bpic2017' else lv[:30]
            self.levels[c] = lv
        self.act_code = {a: i + 1 for i, a in enumerate(self.levels['Activity'])}
        self.res_code = {a: i + 1 for i, a in enumerate(self.levels['Resource'])}
        return self

    def _onehot(self, s, c):
        lv = self.levels[c]
        s = s.astype(str); s = s.where(s.isin(lv), 'other')
        oh = pd.get_dummies(pd.Categorical(s, categories=lv + ['other'])).astype(np.float32)
        oh.columns = [f'{c}={x}' for x in oh.columns]
        return oh

    def transform(self, d, K):
        """one row per prefix (event_nr <= K). d sorted by case, ts."""
        d = d[d['event_nr'] <= K]
        key = d[CASE].values
        parts, agg_cols = [], []
        for c in self.dyn_cat:
            oh = self._onehot(d[c], c); oh.index = d.index
            cnt = oh.groupby(key).cumsum(); cnt.columns = [f'cnt_{x}' for x in oh.columns]
            parts.append(cnt)
        num = {}
        n = d['event_nr'].values.astype(np.float64)
        for c in self.dyn_num:
            v = d[c].values.astype(np.float64)
            s1 = pd.Series(v, index=d.index).groupby(key).cumsum().values
            s2 = pd.Series(v * v, index=d.index).groupby(key).cumsum().values
            num[f'{c}_mean'] = s1 / n
            num[f'{c}_max'] = pd.Series(v, index=d.index).groupby(key).cummax().values
            num[f'{c}_min'] = pd.Series(v, index=d.index).groupby(key).cummin().values
            num[f'{c}_sum'] = s1
            var = np.where(n > 1, (s2 - s1 * s1 / n) / np.maximum(n - 1, 1), 0)
            num[f'{c}_std'] = np.sqrt(np.clip(var, 0, None))
        for c in self.static_num:
            num[f'static_{c}'] = d[c].values.astype(np.float64)
        parts.append(pd.DataFrame(num, index=d.index).astype(np.float32))
        for c in self.static_cat:
            # static attributes: value at the first event of the case (benchmark 'static' encoder)
            first = d.groupby(key)[c].transform('first')
            oh = self._onehot(first, c); oh.index = d.index; oh.columns = [f'static_{x}' for x in oh.columns]
            parts.append(oh)
        for p in parts:
            p.index = d.index
        A = pd.concat(parts, axis=1).astype(np.float32)
        agg_cols = list(A.columns)
        # lagged index encoding
        ac = d['Activity'].astype(str).map(self.act_code).fillna(len(self.act_code) + 1).astype(np.float32).values
        rc = d['Resource'].astype(str).map(self.res_code).fillna(len(self.res_code) + 1).astype(np.float32).values
        tl = np.log1p(d['timesincelastevent'].values.astype(np.float32))
        I = {}
        g = pd.DataFrame({'a': ac, 'r': rc, 't': tl}, index=d.index).groupby(key)
        for j in range(N_LAG):
            sh = g.shift(j) if j > 0 else pd.DataFrame({'a': ac, 'r': rc, 't': tl}, index=d.index)
            I[f'idx_act_lag{j + 1}'] = sh['a'].values; I[f'idx_res_lag{j + 1}'] = sh['r'].values; I[f'idx_tsl_lag{j + 1}'] = sh['t'].values
        Idf = pd.DataFrame(I, index=d.index).astype(np.float32)  # NaN where position does not exist
        X = pd.concat([A, Idf], axis=1)
        X.columns = [str(c).replace('[', '(').replace(']', ')').replace('<', 'lt').replace(',', ';').replace(':', '_').replace('"', '') for c in X.columns]
        meta = pd.DataFrame({'case': d[CASE].values, 'prefix_len': d['event_nr'].values}, index=d.index)
        return X, meta, len(agg_cols)


def seq_tensors(d, enc, K, num_stats=None):
    """Sequence representation for deep models: activity id, resource id, numeric dynamic features, static vector."""
    d = d[d['event_nr'] <= K]
    cases = d[CASE].unique(); cidx = pd.Series(np.arange(len(cases)), index=cases)
    ci = cidx[d[CASE]].values; ti = d['event_nr'].values - 1
    act = np.zeros((len(cases), K), np.int16); res = np.zeros((len(cases), K), np.int16)
    act[ci, ti] = d['Activity'].astype(str).map(enc.act_code).fillna(len(enc.act_code) + 1).astype(int).values
    res[ci, ti] = d['Resource'].astype(str).map(enc.res_code).fillna(len(enc.res_code) + 1).astype(int).values
    nn_cols = [c for c in enc.dyn_num if c != 'event_nr']
    V = d[nn_cols].values.astype(np.float64); V = np.sign(V) * np.log1p(np.abs(V))
    if num_stats is None:
        num_stats = (V.mean(0), V.std(0) + 1e-6)
    V = ((V - num_stats[0]) / num_stats[1]).astype(np.float32)
    num = np.zeros((len(cases), K, len(nn_cols)), np.float32); num[ci, ti] = V
    first = d.groupby(CASE).first().reindex(cases)
    st = []
    for c in enc.static_cat:
        oh = enc._onehot(first[c], c).values; st.append(oh)
    for c in enc.static_num:
        v = np.sign(first[c].values.astype(float)) * np.log1p(np.abs(first[c].values.astype(float))); st.append(v[:, None])
    S = np.hstack(st).astype(np.float32) if st else np.zeros((len(cases), 1), np.float32)
    lens = d.groupby(CASE).size().reindex(cases).values
    return dict(act=act, res=res, num=num, static=S, lens=lens, cases=np.array(cases, dtype=object)), num_stats


def main(protocol, group):
    t0 = time.time()
    task0 = group if group in TASKS else [t for t in TASKS if TASKS[t][0] == group][0]
    log, df, tasks = label_task(protocol, task0)
    use_oc = protocol == 'benchmark'
    Ks = {t: prefix_cap(protocol, log, df, t) for t in tasks}
    K = max(Ks.values())
    log_(protocol, group, 'tasks', tasks, 'K', Ks, 'events', len(df), 'cases', df[CASE].nunique())
    df = recompute_event_nr(df)
    train, test, split_ts = temporal_split_strict(df, 0.8)
    fit, val, val_ts = temporal_split_strict(train, 0.8)
    n_fit_pref_full = int(fit.groupby(CASE).size().clip(upper=K).sum())
    n_val_pref_full = int(val.groupby(CASE).size().clip(upper=K).sum())
    fit = subsample_cases(fit, K, FIT_CAP, 0); val = subsample_cases(val, K, VAL_CAP, 1)
    vstarts = val.groupby(CASE)[TS].min().sort_values(kind='mergesort')
    va_ids = set(vstarts.index[:len(vstarts) // 2])
    enc = AggEncoder(log, use_oc).fit(fit)
    out = {}
    for name, d in [('fit', fit), ('val', val), ('test', test)]:
        X, M, n_agg = enc.transform(d, K)
        lab = d.loc[X.index, ['label__' + t for t in tasks]].reset_index(drop=True)
        M = pd.concat([M.reset_index(drop=True), lab], axis=1)
        if name == 'val':
            M['part'] = np.where(M['case'].isin(va_ids), 'va', 'vb')
        else:
            M['part'] = name
        out[name] = (X.reset_index(drop=True), M)
        log_(name, X.shape)
    cols = list(out['fit'][0].columns)
    gdir = f'{WORK}/{protocol}/{group}'; os.makedirs(gdir, exist_ok=True)
    np.savez(f'{gdir}/X.npz', **{k: v[0].values.astype(np.float32) for k, v in out.items()})
    for k, v in out.items():
        v[1].to_parquet(f'{gdir}/meta_{k}.parquet', index=False)
    S = {}; stats = None
    for name, d in [('fit', fit), ('val', val), ('test', test)]:
        S[name], stats = seq_tensors(d, enc, K, stats)
        lab = d.groupby(CASE)[['label__' + t for t in tasks]].first().reindex(S[name]['cases'])
        for t in tasks:
            S[name]['label__' + t] = lab['label__' + t].values.astype(np.float32)
        if name == 'val':
            S[name]['part'] = np.where(pd.Series(S[name]['cases']).isin(va_ids), 'va', 'vb')
    pickle.dump(S, open(f'{gdir}/seq.pkl', 'wb'))
    info = dict(protocol=protocol, group=group, log=log, tasks=tasks, K=Ks, K_group=K, columns=cols, n_agg_cols=n_agg,
                split_ts=str(split_ts), val_split_ts=str(val_ts), n_act=len(enc.act_code), n_res=len(enc.res_code),
                time_cols=[c for c in cols[:n_agg] if any(c.startswith(x + '_') for x in TIME_NUM + ['open_cases'])],
                res_cols=[c for c in cols[:n_agg] if c.startswith('cnt_Resource=')],
                n_fit_prefixes_before_subsample=n_fit_pref_full, n_val_prefixes_before_subsample=n_val_pref_full)
    # dataset statistics per task
    full_stats = []
    for t in tasks:
        sub = df
        cl = sub.groupby(CASE).size()
        variants = sub.groupby(CASE)['Activity'].agg(tuple).nunique()
        Mte = out['test'][1]; mte = Mte.prefix_len <= Ks[t]
        Mf = out['fit'][1]; Mv = out['val'][1]
        full_stats.append(dict(protocol=protocol, task=t, log=log, label_definition=TASKS[t][1], cases=sub[CASE].nunique(),
                               events=len(sub), activities=sub['Activity'].nunique(), variants=variants,
                               mean_case_length=round(cl.mean(), 2), max_case_length=int(cl.max()),
                               positive_case_ratio=round(sub.groupby(CASE)['label__' + t].first().mean(), 4),
                               max_prefix_len_K=Ks[t], train_cases=train[CASE].nunique(), test_cases=test[CASE].nunique(),
                               fit_cases_used=fit[CASE].nunique(), val_cases_used=val[CASE].nunique(),
                               fit_prefixes_before_subsample=n_fit_pref_full, fit_prefixes_used=int((Mf.prefix_len <= Ks[t]).sum()),
                               val_prefixes_used=int((Mv.prefix_len <= Ks[t]).sum()), test_prefixes=int(mte.sum()),
                               test_positive_prefix_ratio=round(Mte.loc[mte, 'label__' + t].mean(), 4),
                               n_features_agg=n_agg, n_features_agg_index=len(cols), split_timestamp=str(split_ts)))
    info['stats'] = full_stats
    json.dump(info, open(f'{gdir}/info.json', 'w'), indent=1, default=str)
    log_('done', group, f'{time.time() - t0:.0f}s')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
