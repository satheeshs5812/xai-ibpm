"""Directory configuration.

All paths default to locations inside the repository and can be overridden with environment variables:

  XAI_IBPM_PARSED   parsed event logs (parquet, output of parse_logs.py)   default: <repo>/data/parsed
  XAI_IBPM_WORK     encoded datasets, trained models, raw predictions       default: <repo>/work
  XAI_IBPM_RESULTS  result tables (CSV/JSON), per-task outputs, figures     default: <repo>/results
  XAI_IBPM_FIGURES  figure output directory                                 default: $XAI_IBPM_RESULTS/figures
"""
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _p(var, default):
    return os.path.abspath(os.environ.get(var, default))


PARSED = _p('XAI_IBPM_PARSED', os.path.join(REPO_ROOT, 'data', 'parsed'))
WORK = _p('XAI_IBPM_WORK', os.path.join(REPO_ROOT, 'work'))
RES = _p('XAI_IBPM_RESULTS', os.path.join(REPO_ROOT, 'results'))
FIG = _p('XAI_IBPM_FIGURES', os.path.join(RES, 'figures'))
