"""Deep sequence models: LSTM and a small causal Transformer encoder (ProcessTransformer-style: activity embedding +
positional embedding + time/attribute features). Many-to-many training: one output per prefix position.
Light tuning (3 configs each, seed 0, validation AUC), then 5 seeds of the best config.
Usage: python3 train_deep.py <protocol> <task>"""
import sys, os, json, time, pickle, warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.metrics import roc_auc_score
from common import *
torch.set_num_threads(int(os.environ.get('TORCH_THREADS', 1)))

PROTO, TASK = sys.argv[1], sys.argv[2]
OUT = f'{WORK}/{PROTO}/runs/{TASK}'; os.makedirs(OUT, exist_ok=True)
T0 = time.time()
def log(*a): print(f'[deep {PROTO}/{TASK} {time.strftime("%H:%M:%S")} +{time.time() - T0:.0f}s]', *a, flush=True)

g = group_of(PROTO, TASK); gd = f'{WORK}/{PROTO}/{g}'
info = json.load(open(f'{gd}/info.json')); K = info['K'][TASK]
S = pickle.load(open(f'{gd}/seq.pkl', 'rb'))
def tens(s):
    d = S[s]
    return dict(act=torch.tensor(d['act'][:, :K].astype(np.int64)), res=torch.tensor(d['res'][:, :K].astype(np.int64)),
                num=torch.tensor(d['num'][:, :K]), st=torch.tensor(d['static']),
                y=torch.tensor(d['label__' + TASK]), mask=torch.tensor((np.arange(K)[None] < np.minimum(d['lens'], K)[:, None]).astype(np.float32)),
                cases=d['cases'])
F, V, T = tens('fit'), tens('val'), tens('test')
n_act, n_res = info['n_act'] + 2, info['n_res'] + 2
d_num, d_st = F['num'].shape[2], F['st'].shape[1]
Mv = pd.read_parquet(f'{gd}/meta_val.parquet'); Mv = Mv[Mv.prefix_len <= K].reset_index(drop=True)
Mt = pd.read_parquet(f'{gd}/meta_test.parquet'); Mt = Mt[Mt.prefix_len <= K].reset_index(drop=True)
log('cases fit/val/test', len(F['y']), len(V['y']), len(T['y']), 'K', K)


class Inp(nn.Module):
    def __init__(s, d_out):
        super().__init__()
        s.ea = nn.Embedding(n_act, 16); s.er = nn.Embedding(n_res, 8)
        s.proj = nn.Linear(16 + 8 + d_num + d_st, d_out)
    def forward(s, b):
        st = b['st'][:, None, :].expand(-1, b['act'].shape[1], -1)
        return s.proj(torch.cat([s.ea(b['act']), s.er(b['res']), b['num'], st], -1))


class LSTMNet(nn.Module):
    def __init__(s, h=64, drop=0.2, **kw):
        super().__init__(); s.inp = Inp(h); s.lstm = nn.LSTM(h, h, batch_first=True); s.drop = nn.Dropout(drop); s.out = nn.Linear(h, 1)
    def forward(s, b):
        o, _ = s.lstm(torch.relu(s.inp(b))); return s.out(s.drop(o)).squeeze(-1)


class TransNet(nn.Module):
    def __init__(s, d=64, layers=2, heads=4, drop=0.1, **kw):
        super().__init__(); s.inp = Inp(d); s.pos = nn.Embedding(K, d)
        el = nn.TransformerEncoderLayer(d, heads, 2 * d, drop, batch_first=True)
        s.enc = nn.TransformerEncoder(el, layers); s.out = nn.Linear(d, 1)
        s.register_buffer('causal', torch.triu(torch.full((K, K), float('-inf')), 1))
    def forward(s, b):
        L = b['act'].shape[1]
        x = s.inp(b) + s.pos(torch.arange(L))[None]
        pad = b['act'] == 0
        o = s.enc(x, mask=s.causal[:L, :L], src_key_padding_mask=pad)
        return s.out(o).squeeze(-1)


def batch(D, idx):
    return {k: D[k][idx] for k in ['act', 'res', 'num', 'st', 'y', 'mask']}


def predict(net, D):
    net.eval(); out = []
    with torch.no_grad():
        for i in range(0, len(D['y']), 1024):
            out.append(torch.sigmoid(net(batch(D, slice(i, i + 1024)))))
    return torch.cat(out).numpy()


def prefix_probs(out, D, M):
    cidx = pd.Series(np.arange(len(D['cases'])), index=D['cases'])
    return out[cidx[M.case].values, M.prefix_len.values - 1]


def val_auc(net):
    o = predict(net, V); mk = V['mask'].numpy().astype(bool)
    return roc_auc_score(np.broadcast_to(V['y'].numpy()[:, None], mk.shape)[mk], o[mk])


MAX_EP = 25 if len(F['y']) < 5000 else 12
def train(cls, cfg, seed):
    torch.manual_seed(seed); np.random.seed(seed)
    net = cls(**cfg); opt = torch.optim.Adam(net.parameters(), lr=cfg['lr'], weight_decay=1e-5)
    bce = nn.BCEWithLogitsLoss(reduction='none')
    best, state, bad, ep_used = -1, None, 0, 0
    t = time.time()
    for ep in range(MAX_EP):
        net.train(); perm = torch.randperm(len(F['y']))
        for i in range(0, len(perm), 128):
            b = batch(F, perm[i:i + 128])
            lg = net(b); l = (bce(lg, b['y'][:, None].expand_as(lg)) * b['mask']).sum() / b['mask'].sum()
            opt.zero_grad(); l.backward(); nn.utils.clip_grad_norm_(net.parameters(), 1.0); opt.step()
        a = val_auc(net); ep_used = ep + 1
        if a > best + 1e-4: best, state, bad = a, {k: v.clone() for k, v in net.state_dict().items()}, 0
        else:
            bad += 1
            if bad >= 3: break
    net.load_state_dict(state)
    return net, best, ep_used, time.time() - t


CFGS = {'LSTM': (LSTMNet, [dict(h=64, lr=1e-3), dict(h=128, lr=1e-3), dict(h=64, lr=3e-3)]),
        'Transformer': (TransNet, [dict(d=32, layers=1, lr=1e-3), dict(d=64, layers=2, lr=1e-3), dict(d=64, layers=2, lr=3e-4)])}
preds, summ = {}, dict(protocol=PROTO, task=TASK, K=K)
for name, (cls, cfgs) in CFGS.items():
    res = []
    for cfg in cfgs:
        net, a, ep, tt = train(cls, cfg, 0); res.append((a, cfg, net, ep, tt))
        log(name, cfg, 'val auc', round(a, 4), 'epochs', ep, f'{tt:.0f}s')
    a, cfg, net0, ep0, tt0 = max(res, key=lambda r: r[0])
    summ[f'{name}_tuning'] = [dict(cfg=r[1], val_auc=r[0], epochs=r[3]) for r in res]; summ[f'{name}_best_cfg'] = cfg
    for s in SEEDS:
        if s == 0: net, ep, tt = net0, ep0, tt0
        else: net, _, ep, tt = train(cls, cfg, s)
        t = time.time(); pt = prefix_probs(predict(net, T), T, Mt); it = time.time() - t
        pv = prefix_probs(predict(net, V), V, Mv)
        preds[(name, s)] = dict(val=pv.astype(np.float32), test=pt.astype(np.float32))
        summ.setdefault(f'{name}_epochs', []).append(ep); summ.setdefault(f'{name}_train_s', []).append(tt)
        summ.setdefault(f'{name}_infer_ms_per_1000', []).append(it / len(pt) * 1e6)
        log(name, 'seed', s, 'test auc', round(roc_auc_score(Mt['label__' + TASK], pt), 4), 'epochs', ep)
pickle.dump(preds, open(f'{OUT}/preds_deep.pkl', 'wb'))
summ['runtime_s'] = time.time() - T0
json.dump(summ, open(f'{OUT}/deep_summary.json', 'w'), indent=1, default=float)
log('DONE')
