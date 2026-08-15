from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import run_alt_liquidity_veto_sensitivity as m

m.OUT = Path(__file__).resolve().parent / 'results_alt_liquidity_veto_h10_fast'
m.OUT.mkdir(parents=True, exist_ok=True)
m.HORIZONS = (10,)
m.block_boot = lambda *args, **kwargs: np.array([])

# The main sensitivity only needs aggregate/family summaries. Suppress two very
# large diagnostic CSVs so the confirmatory run stays GitHub-friendly.
_orig_to_csv = pd.DataFrame.to_csv

def _compact_to_csv(self, path_or_buf=None, *args, **kwargs):
    if path_or_buf is not None and Path(str(path_or_buf)).name in {'paths.csv', 'matched.csv'}:
        return None
    return _orig_to_csv(self, path_or_buf, *args, **kwargs)

pd.DataFrame.to_csv = _compact_to_csv

if __name__ == '__main__':
    p = m.run()
    stats, fam = m.evaluate(p)
    summary = m.report(stats, fam)
    (m.OUT / 'RESEARCH_SUMMARY.md').write_text(summary, encoding='utf-8')
    print(summary)
    print(f'paths_in_memory={len(p):,}; specs={len(stats):,}')
