from __future__ import annotations

from pathlib import Path
import numpy as np
import run_alt_liquidity_veto_sensitivity as m

m.OUT = Path(__file__).resolve().parent / 'results_alt_liquidity_veto_h10_fast'
m.OUT.mkdir(parents=True, exist_ok=True)
m.HORIZONS = (10,)
m.block_boot = lambda *args, **kwargs: np.array([])

if __name__ == '__main__':
    p = m.run()
    stats, fam = m.evaluate(p)
    (m.OUT / 'RESEARCH_SUMMARY.md').write_text(m.report(stats, fam), encoding='utf-8')
    print(f'paths={len(p):,}; specs={len(stats):,}')
