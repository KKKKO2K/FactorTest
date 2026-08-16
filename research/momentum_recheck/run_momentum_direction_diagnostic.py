from __future__ import annotations

import math
import pandas as pd
import numpy as np

import run_momentum_recheck as m

PERIODS = {
    'EARLY_2017_2019': (pd.Timestamp('2017-01-01'), pd.Timestamp('2019-12-31')),
    'LATE_2020_2022': (pd.Timestamp('2020-01-01'), pd.Timestamp('2022-12-31')),
    'NORMAL_2023_2024': (pd.Timestamp('2023-01-01'), pd.Timestamp('2024-12-31')),
    'BULL_2025': (pd.Timestamp('2025-01-01'), pd.Timestamp('2025-12-31')),
    'YTD_2026': (pd.Timestamp('2026-01-01'), pd.Timestamp('2099-12-31')),
}


def main():
    returns, mcap, k200 = m.base.load_basic()
    markets = m.multi.load_market_by_date()
    td_panel, td_parts = m.trading_day_momentum(returns, mcap)
    cal_panel, cal_parts = m.calendar_asof_momentum(returns, mcap)
    chosen, _, val = m.validate_source_definition(td_panel, td_parts, cal_panel, cal_parts)
    weighted = cal_panel if chosen == 'CALENDAR_MONTH_ASOF' else td_panel
    del td_parts, cal_parts

    fwd = m.base.forward_returns(returns, m.H)
    common = sorted(set(returns.index) & set(mcap.index) & set(k200) & set(markets) & set(fwd.index))
    common = [d for d in common if d >= pd.Timestamp('2017-01-01')]
    phase_map = {d: i % m.H for i, d in enumerate(common)}
    rows = []

    for dt in common:
        if dt not in weighted.index:
            continue
        mc = pd.to_numeric(mcap.loc[dt], errors='coerce')
        for u in m.UNIVERSES:
            codes = m.multi.universe_codes(u, k200[dt], markets[dt])
            mc_u = mc.reindex(codes)
            eligible = mc_u.index[(mc_u >= m.MCAP_CUTOFF_BN).fillna(False)]
            if len(eligible) < 40:
                continue
            score = pd.to_numeric(weighted.loc[dt].reindex(eligible), errors='coerce')
            y = pd.to_numeric(fwd.loc[dt].reindex(eligible), errors='coerce')
            pair = pd.concat([score.rename('score'), y.rename('fwd')], axis=1).dropna()
            if len(pair) < 40:
                continue
            rank = pair.score.rank(method='average')
            ic = float(rank.corr(pair.fwd.rank(method='average')))
            top = pair.nlargest(m.TOPN, 'score').fwd.mean()
            bottom = pair.nsmallest(m.TOPN, 'score').fwd.mean()
            rows.append({
                'date': dt, 'phase': phase_map[dt], 'universe': u, 'n': len(pair),
                'ic_10d': ic, 'top20_10d': float(top), 'bottom20_10d': float(bottom),
                'top_minus_bottom_10d': float(top - bottom),
            })

    detail = pd.DataFrame(rows)
    m.write_chunked_csv(detail, m.OUT / 'direction_detail.csv', index=False, target_mb=40)
    summary = []
    for u in m.UNIVERSES:
        for period, (lo, hi) in PERIODS.items():
            g0 = detail[(detail.universe == u) & (detail.date >= lo) & (detail.date <= hi)]
            for phase, g in g0.groupby('phase'):
                if len(g) < 8:
                    continue
                summary.append({
                    'universe': u, 'period': period, 'phase': phase, 'n_dates': len(g),
                    'mean_ic': g.ic_10d.mean(),
                    'mean_top20_10d': g.top20_10d.mean(),
                    'mean_bottom20_10d': g.bottom20_10d.mean(),
                    'mean_top_minus_bottom_10d': g.top_minus_bottom_10d.mean(),
                    'top_minus_bottom_positive_rate': (g.top_minus_bottom_10d > 0).mean(),
                })
    ph = pd.DataFrame(summary)
    ph.to_csv(m.OUT / 'direction_phase_summary.csv', index=False)

    agg = []
    for (u, period), g in ph.groupby(['universe', 'period']):
        agg.append({
            'universe': u, 'period': period, 'n_phases': g.phase.nunique(),
            'median_ic': g.mean_ic.median(),
            'positive_ic_phases': int((g.mean_ic > 0).sum()),
            'median_top20_10d': g.mean_top20_10d.median(),
            'median_bottom20_10d': g.mean_bottom20_10d.median(),
            'median_top_minus_bottom_10d': g.mean_top_minus_bottom_10d.median(),
            'positive_top_minus_bottom_phases': int((g.mean_top_minus_bottom_10d > 0).sum()),
        })
    agg = pd.DataFrame(agg)
    agg.to_csv(m.OUT / 'direction_summary.csv', index=False)

    lines = ['# Weighted Momentum Direction Diagnostic', '',
             f'- Reconstruction convention: **{chosen}**.',
             '- This is a sign/mechanism diagnostic only. It does not redefine the production direction.',
             '- Universe and cutoff match the primary recheck: Top/Bottom 20 among names with market cap >= KRW 250bn.', '',
             '## Median across 10 rebalance phases', '']
    for period in PERIODS:
        lines.append(f'### {period}')
        z = agg[agg.period == period]
        for u in m.UNIVERSES:
            q = z[z.universe == u]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f'- {u}: IC {r.median_ic:+.3f} ({int(r.positive_ic_phases)}/{int(r.n_phases)} positive phases); '
                f'Top20 {r.median_top20_10d:+.2%}; Bottom20 {r.median_bottom20_10d:+.2%}; '
                f'Top-Bottom {r.median_top_minus_bottom_10d:+.2%} ({int(r.positive_top_minus_bottom_phases)}/{int(r.n_phases)} positive phases).'
            )
        lines.append('')
    (m.OUT / 'DIRECTION_SUMMARY.md').write_text('\n'.join(lines), encoding='utf-8')
    print(f'chosen={chosen}; detail={len(detail):,}; phase_rows={len(ph):,}; summary_rows={len(agg):,}')


if __name__ == '__main__':
    main()
