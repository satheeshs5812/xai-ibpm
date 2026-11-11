"""Parse raw XES event logs (untrusted input) into flat event tables (parquet).
Uses defusedxml for safe XML parsing. Run with: python3 src/parse_logs.py <raw_dir> <out_dir>   (e.g. data/raw data/parsed)
"""
import sys, gzip, os
import pandas as pd
from defusedxml.ElementTree import iterparse

def strip(tag):
    return tag.split('}')[-1]

def conv(tag, val):
    if tag in ('int',):
        try: return int(val)
        except: return None
    if tag in ('float',):
        try: return float(val)
        except: return None
    if tag == 'boolean':
        return val.lower() == 'true'
    return val

def parse_xes(path):
    opener = gzip.open if path.endswith('.gz') else open
    rows = []
    depth_stack = []
    trace_attrs = None
    ev = None
    with opener(path, 'rb') as f:
        for event, elem in iterparse(f, events=('start', 'end')):
            t = strip(elem.tag)
            if event == 'start':
                depth_stack.append(t)
                if t == 'trace':
                    trace_attrs = {}
                elif t == 'event':
                    ev = {}
                continue
            # end
            depth_stack.pop()
            parent = depth_stack[-1] if depth_stack else None
            if t in ('string', 'date', 'int', 'float', 'boolean', 'id'):
                k = elem.get('key'); v = conv(t, elem.get('value'))
                if parent == 'event' and ev is not None:
                    ev[k] = v
                elif parent == 'trace' and trace_attrs is not None:
                    trace_attrs['case:' + k] = v
            elif t == 'event':
                if trace_attrs is not None:
                    ev.update(trace_attrs)  # trace attrs appear before events in XES
                    rows.append(ev)
                ev = None
                elem.clear()
            elif t == 'trace':
                # back-fill trace attrs that appeared after events (rare)
                trace_attrs = None
                elem.clear()
    return pd.DataFrame(rows)

if __name__ == '__main__':
    raw, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for fn, name in [('BPI_Challenge_2012.xes.gz', 'bpic2012'), ('BPI_Challenge_2017.xes.gz', 'bpic2017'),
                     ('Sepsis_Cases.xes.gz', 'sepsis'), ('Road_Traffic_Fine_Management_Process.xes.gz', 'traffic')]:
        df = parse_xes(os.path.join(raw, fn))
        df['time:timestamp'] = pd.to_datetime(df['time:timestamp'], utc=True, format='ISO8601')
        for c in df.columns:
            if df[c].dtype == object:
                df[c] = df[c].astype(str).where(df[c].notna(), None)
        df.to_parquet(os.path.join(out, name + '.parquet'), index=False)
        print(name, df.shape, list(df.columns)[:40], flush=True)
