from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import pandas as pd
import numpy as np

import run_momentum_recheck as m

STAGE1_STRATEGIES = ('MOM1M_SOURCE', 'MOM12_1_SOURCE', 'WEIGHTED_MOM')
m.STRATEGIES = STAGE1_STRATEGIES


@lru_cache(maxsize=8192)
def load_factor_cached(path_str: str) -> pd.Series:
    return m.base.load_factor(Path(path_str))


def build_targets_stage1(returns, mcap, k200, markets, weighted_panel):
    mom_files = {
        'MOM1M_SOURCE': m.base.dated_files(m.base.FACTORS['MOM1M']),
        'MOM12_1_SOURCE': m.base.dated_files(m.base.FACTORS['MOM12_1']),
    }
    common = sorted(set(returns.index) & set(mcap.index) & set(k200) & set(markets))
    common = [d for d in common if d >= pd.Timestamp('2017-01-01')]
    phase_map = {d: i % m.H for i, d in enumerate(common)}
    store = {u: {s: {} for s in STAGE1_STRATEGIES} for u in m.UNIVERSES}
    compact = []

    for dt in common:
        if dt not in weighted_panel.index:
            continue
        raw_source = {}
        for strategy, files in mom_files.items():
            if dt in files:
                raw_source[strategy] = load_factor_cached(str(files[dt]))
        if len(raw_source) != 2:
            continue
        mc = mcap.loc[dt]
        for universe in m.UNIVERSES:
            codes = m.multi.universe_codes(universe, k200[dt], markets[dt])
            mc_u = pd.to_numeric(mc.reindex(codes), errors='coerce')
            eligible = mc_u.index[(mc_u >= m.MCAP_CUTOFF_BN).fillna(False)]
            if len(eligible) < 40:
                continue
            scores = {
                'MOM1M_SOURCE': m.core.rank_good(raw_source['MOM1M_SOURCE'].reindex(eligible), True),
                'MOM12_1_SOURCE': m.core.rank_good(raw_source['MOM12_1_SOURCE'].reindex(eligible), True),
                'WEIGHTED_MOM': m.core.rank_good(weighted_panel.loc[dt].reindex(eligible), True),
            }
            for strategy, score in scores.items():
                names = m.core.top_names(score, m.TOPN)
                if len(names) != m.TOPN:
                    continue
                store[universe][strategy][dt] = m.equal_weight_target(names)
                compact.append({
                    'date': dt, 'phase': phase_map[dt], 'universe': universe,
                    'strategy': strategy, 'eligible_n': len(eligible), 'codes': '|'.join(names),
                })
    m.write_chunked_csv(pd.DataFrame(compact), m.OUT / 'stage1_holdings_compact.csv', index=False, target_mb=40)
    return store, phase_map


def write_stage1_summary(chosen, validation_summary, psum):
    lines = [
        '# Weighted Momentum Recheck — Stage 1', '',
        'Stage 1 intentionally tests the primary factor before any CF20 or liquidity overlay.', '',
        '## Recovered historical signal', '',
        '- `WEIGHTED_MOM = (12*R1M + 4*R3M + 2*R6M + R12M) / 17`',
        '- Descending Top20, market-cap cutoff KRW 250bn.',
        '- Research sleeve is equal-weight Top20 to isolate stock-selection quality; historical production weighting is not assumed.', '',
        '## Source reconstruction validation', '',
    ]
    for r in validation_summary.itertuples(index=False):
        lines.append(f'- {r.method}: component RMSE {r.raw_component_rmse_pp:.3f}pp; factor RMSE {r.factor_rmse_pp:.3f}pp.')
    lines += [f'- **Chosen convention: {chosen}**, selected only by fidelity to workbook source values.', '',
              '## 2017-2024 NET30 — median across 10 rebalance phases', '']
    z = psum[(psum.period == 'PRE_STRESS_2017_2024') & (psum.cost_bp == 30)]
    for u in m.UNIVERSES:
        lines.append(f'### {u}')
        for s in STAGE1_STRATEGIES:
            q = z[(z.universe == u) & (z.strategy == s)]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f'- {s}: CAGR {r.median_cagr:+.2%}; MDD {r.median_mdd:+.1%}; Sharpe {r.median_sharpe:.2f}; '
                f'Calmar {r.median_calmar:.2f}; BM excess {r.median_excess_cagr:+.2%}; IR {r.median_information_ratio:.2f}; '
                f'turnover {r.median_turnover:.2f}x; positive CAGR phases {int(r.positive_cagr_phases)}/{int(r.n_phases)}; '
                f'positive excess phases {int(r.positive_excess_phases)}/{int(r.n_phases)}.'
            )
        lines.append('')
    lines += ['## Historical blocks — WEIGHTED_MOM NET30', '']
    for period in ('EARLY_2017_2019', 'LATE_2020_2022', 'NORMAL_2023_2024', 'BULL_2025', 'YTD_2026'):
        lines.append(f'### {period}')
        q0 = psum[(psum.period == period) & (psum.cost_bp == 30) & (psum.strategy == 'WEIGHTED_MOM')]
        for u in m.UNIVERSES:
            q = q0[q0.universe == u]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f'- {u}: CAGR {r.median_cagr:+.2%}; Sharpe {r.median_sharpe:.2f}; BM excess {r.median_excess_cagr:+.2%}; '
                f'IR {r.median_information_ratio:.2f}; positive CAGR {int(r.positive_cagr_phases)}/{int(r.n_phases)}.'
            )
        lines.append('')
    lines += [
        '## Stage-gate interpretation', '',
        '- Do not promote CF20 unless the weighted-momentum primary itself shows credible absolute and benchmark-relative behavior.',
        '- 2025/2026 are stress diagnostics, not untouched OOS.',
        '- No liquidity overlay is tested in Stage 1.',
        '- Large daily/holding outputs are preserved as GitHub-safe gzip chunks plus manifests.', '',
    ]
    (m.OUT / 'STAGE1_SUMMARY.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    returns, mcap, k200 = m.base.load_basic()
    markets = m.multi.load_market_by_date()
    td_panel, td_parts = m.trading_day_momentum(returns, mcap)
    cal_panel, cal_parts = m.calendar_asof_momentum(returns, mcap)
    chosen, _, validation_summary = m.validate_source_definition(td_panel, td_parts, cal_panel, cal_parts)
    weighted = cal_panel if chosen == 'CALENDAR_MONTH_ASOF' else td_panel
    if chosen == 'CALENDAR_MONTH_ASOF':
        del td_panel
    else:
        del cal_panel
    del td_parts, cal_parts

    store, phase_map = build_targets_stage1(returns, mcap, k200, markets, weighted)
    daily = m.simulate_all(returns, store, phase_map)
    bench = m.build_benchmarks(returns, mcap, k200, markets)
    stats = m.performance(daily, bench)
    psum = m.summarize_phases(stats)
    write_stage1_summary(chosen, validation_summary, psum)
    print(f'stage1 chosen={chosen}; daily_rows={len(daily):,}; stats={len(stats):,}; summaries={len(psum):,}')


if __name__ == '__main__':
    main()
