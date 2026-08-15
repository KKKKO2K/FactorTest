from __future__ import annotations

from pathlib import Path
import sys
import numpy as np
import pandas as pd
import run_alt_liquidity_veto_sensitivity as m

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/common'))
from chunked_csv import write_chunked_csv

m.OUT = Path(__file__).resolve().parent / 'results_alt_liquidity_veto_h10_fast'
m.OUT.mkdir(parents=True, exist_ok=True)
m.HORIZONS = (10,)
m.block_boot = lambda *args, **kwargs: np.array([])

# Preserve large diagnostics for later reuse without violating GitHub's 100 MB
# per-file limit. Logical paths.csv / matched.csv become ordered gzip chunks
# plus a manifest that can be reconstructed with research/common/chunked_csv.py.
_orig_to_csv = pd.DataFrame.to_csv


def _chunk_large_outputs(self, path_or_buf=None, *args, **kwargs):
    if path_or_buf is not None:
        path = Path(str(path_or_buf))
        if path.name in {'paths.csv', 'matched.csv'}:
            index = bool(kwargs.pop('index', False))
            write_chunked_csv(self, path, index=index, target_mb=40)
            return None
    return _orig_to_csv(self, path_or_buf, *args, **kwargs)


pd.DataFrame.to_csv = _chunk_large_outputs

if __name__ == '__main__':
    p = m.run()
    stats, fam = m.evaluate(p)
    summary = m.report(stats, fam)
    (m.OUT / 'RESEARCH_SUMMARY.md').write_text(summary, encoding='utf-8')
    print(summary)
    print(f'paths_in_memory={len(p):,}; specs={len(stats):,}')
