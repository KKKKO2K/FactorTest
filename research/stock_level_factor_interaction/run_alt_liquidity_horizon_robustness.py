from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import run_alt_liquidity_veto_sensitivity as m

m.OUT = Path(__file__).resolve().parent / 'results_alt_liquidity_horizon_robustness'
m.OUT.mkdir(parents=True, exist_ok=True)
m.HORIZONS = (5, 20)
m.block_boot = lambda *args, **kwargs: np.array([])

# Confirm the mechanism without opening another combined-cutoff search: only
# one-sided tail vetoes are carried to H5/H20. For ACT5/ADV20/TURNOVER20/ACT1,
# LOWxx removes the least-liquid/least-active tail; for AMIHUD20, TOPxx removes
# the most illiquid/high-price-impact tail.
def one_sided_score_map(cf20: pd.Series, rank: pd.Series):
    out = {'CF20': cf20}
    for t in (0.01, 0.05):
        out[f'TOP{int(t*100):02d}'] = cf20.where(rank <= 1 - t)
    for l in (0.05, 0.10, 0.20, 0.30):
        out[f'LOW{int(l*100):02d}'] = cf20.where(rank >= l)
    return out

m.score_map = one_sided_score_map


def _vals(stats: pd.DataFrame, metric: str, strategy: str, universe: str, horizon: int):
    z = stats[(stats.metric == metric) & (stats.strategy == strategy) &
              (stats.universe == universe) & (stats.horizon == horizon)]
    mp = {r['sample']: r for _, r in z.iterrows()}
    if not all(s in mp for s in m.CORE):
        return None
    return [float(mp[s].net_delta_30) for s in m.CORE]


def report(stats: pd.DataFrame, fam: pd.DataFrame) -> str:
    lines = [
        '# Alternative Liquidity Horizon Robustness', '',
        'CF20 remains frozen. This stage carries only one-sided tail vetoes to H5/H20, after the H10 alternative-metric screen.', '',
        'Economic-direction candidates: LOW tail for ACT5/ADV20/TURNOVER20/ACT1; TOP tail for AMIHUD20 because higher Amihud means more illiquid.', '',
    ]
    candidates = {
        'ACT5': ['LOW05','LOW10','LOW20','LOW30'],
        'ADV20': ['LOW05','LOW10','LOW20','LOW30'],
        'TURNOVER20': ['LOW05','LOW10','LOW20','LOW30'],
        'ACT1': ['LOW05','LOW10','LOW20','LOW30'],
        'AMIHUD20': ['TOP01','TOP05'],
    }
    for h in (5,20):
        lines += [f'## H{h} stable core-block one-sided vetoes', '']
        for metric, strategies in candidates.items():
            hits=[]
            for strategy in strategies:
                for u in m.UNIVERSES:
                    v=_vals(stats, metric, strategy, u, h)
                    if v is not None and all(x>0 for x in v):
                        z=fam[(fam.metric==metric)&(fam.strategy==strategy)&(fam.universe==u)&(fam.horizon==h)&fam['sample'].isin(m.CORE)]
                        pos=z.groupby('sample').apply(lambda q:int((q.gross_delta>0).sum()),include_groups=False).to_dict() if len(z) else {}
                        hits.append(f'- {metric} {u} {strategy}: {v[0]:+.2%}->{v[1]:+.2%}->{v[2]:+.2%}; family+ {pos}')
            if hits:
                lines.extend(hits)
        lines.append('')

    lines += ['## H10-screen candidates: H5/H20 direction table', '']
    screen = [
        ('KOSPI_EX_K200','ADV20','LOW05'), ('KOSPI_EX_K200','ADV20','LOW10'),
        ('KOSPI_EX_K200','TURNOVER20','LOW05'), ('KOSPI_EX_K200','TURNOVER20','LOW10'),
        ('KOSPI_EX_K200','AMIHUD20','TOP01'), ('KOSPI_EX_K200','AMIHUD20','TOP05'),
        ('KOSDAQ','ACT5','LOW20'), ('KOSDAQ','ACT5','LOW30'),
        ('KOSDAQ','ADV20','LOW20'), ('KOSDAQ','ADV20','LOW30'),
        ('KOSDAQ','TURNOVER20','LOW20'), ('KOSDAQ','TURNOVER20','LOW30'),
        ('KOSDAQ','ACT1','LOW05'), ('KOSDAQ','ACT1','LOW10'),
        ('KOSDAQ','AMIHUD20','TOP01'), ('KOSDAQ','AMIHUD20','TOP05'),
    ]
    for u,metric,strategy in screen:
        vals=[]
        for h in (5,20):
            v=_vals(stats,metric,strategy,u,h)
            vals.append('NA' if v is None else '/'.join(f'{x:+.2%}' for x in v))
        lines.append(f'- {u} {metric} {strategy}: H5 {vals[0]} | H20 {vals[1]}')

    lines += ['', '## Guardrails', '',
              '- No new cutoff is selected from H5/H20; these horizons only test whether the H10 economic mechanism survives.',
              '- 2025/2026 are retained in summary.csv as stress observations but do not determine candidates.',
              '- Large intermediates are stored through the common chunked CSV helper for later bootstrap/post-processing.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    p = m.run()
    stats, fam = m.evaluate(p)
    text = report(stats, fam)
    (m.OUT / 'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)
    print(f'paths={len(p):,}; specs={len(stats):,}')
