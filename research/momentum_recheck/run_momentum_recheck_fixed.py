from __future__ import annotations

import pandas as pd
import run_momentum_recheck as m


def compare_cf20_fixed(stats: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (u, period, cost), g in stats.groupby(['universe', 'period', 'cost_bp']):
        b = g[g.strategy.eq('WEIGHTED_MOM')].set_index('phase')
        q = g[g.strategy.eq('WEIGHTED_MOM_CF20')].set_index('phase')
        phases = sorted(set(b.index) & set(q.index))
        if not phases:
            continue
        dcagr = q.loc[phases, 'cagr'].to_numpy(float) - b.loc[phases, 'cagr'].to_numpy(float)
        dsh = q.loc[phases, 'sharpe'].to_numpy(float) - b.loc[phases, 'sharpe'].to_numpy(float)
        dex = q.loc[phases, 'geometric_excess_cagr'].to_numpy(float) - b.loc[phases, 'geometric_excess_cagr'].to_numpy(float)
        dturn = q.loc[phases, 'annual_turnover'].to_numpy(float) - b.loc[phases, 'annual_turnover'].to_numpy(float)
        rows.append({
            'universe': u, 'period': period, 'cost_bp': cost, 'n_phases': len(phases),
            'median_delta_cagr': float(pd.Series(dcagr).median()),
            'cagr_better_phases': int((dcagr > 0).sum()),
            'median_delta_sharpe': float(pd.Series(dsh).median()),
            'sharpe_better_phases': int((dsh > 0).sum()),
            'median_delta_excess_cagr': float(pd.Series(dex).median()),
            'excess_better_phases': int((dex > 0).sum()),
            'median_delta_turnover': float(pd.Series(dturn).median()),
        })
    out = pd.DataFrame(rows)
    out.to_csv(m.OUT / 'cf20_incremental.csv', index=False)
    return out


m.compare_cf20 = compare_cf20_fixed

if __name__ == '__main__':
    m.main()
