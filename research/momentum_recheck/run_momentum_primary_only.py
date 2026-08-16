from __future__ import annotations

import pandas as pd
import run_momentum_recheck as m

m.STRATEGIES = ('WEIGHTED_MOM',)


def build_targets_primary(returns, mcap, k200, markets, weighted_panel):
    common = sorted(set(returns.index) & set(mcap.index) & set(k200) & set(markets))
    common = [d for d in common if d >= pd.Timestamp('2017-01-01')]
    phase_map = {d: i % m.H for i, d in enumerate(common)}
    store = {u: {'WEIGHTED_MOM': {}} for u in m.UNIVERSES}
    compact = []

    for dt in common:
        if dt not in weighted_panel.index:
            continue
        mc = pd.to_numeric(mcap.loc[dt], errors='coerce')
        for universe in m.UNIVERSES:
            codes = m.multi.universe_codes(universe, k200[dt], markets[dt])
            mc_u = mc.reindex(codes)
            eligible = mc_u.index[(mc_u >= m.MCAP_CUTOFF_BN).fillna(False)]
            if len(eligible) < 40:
                continue
            score = m.core.rank_good(weighted_panel.loc[dt].reindex(eligible), True)
            names = m.core.top_names(score, m.TOPN)
            if len(names) != m.TOPN:
                continue
            store[universe]['WEIGHTED_MOM'][dt] = m.equal_weight_target(names)
            compact.append({
                'date': dt, 'phase': phase_map[dt], 'universe': universe,
                'strategy': 'WEIGHTED_MOM', 'eligible_n': len(eligible), 'codes': '|'.join(names),
            })
    m.write_chunked_csv(pd.DataFrame(compact), m.OUT / 'primary_holdings_compact.csv', index=False, target_mb=40)
    return store, phase_map


def write_summary(chosen, validation_summary, psum):
    lines = [
        '# Weighted Momentum Primary Recheck', '',
        'This is the stage gate before CF20 or liquidity. No other factor is used in portfolio construction.', '',
        '## Recovered definition', '',
        '- `WEIGHTED_MOM = (12*R1M + 4*R3M + 2*R6M + R12M) / 17`',
        '- Descending Top20; market-cap cutoff KRW 250bn.',
        '- Equal-weight Top20 is used here to isolate the stock-selection signal; historical production weighting is not assumed.', '',
        '## Source-value reconstruction', '',
    ]
    for r in validation_summary.itertuples(index=False):
        lines.append(f'- {r.method}: component RMSE {r.raw_component_rmse_pp:.3f}pp; factor RMSE {r.factor_rmse_pp:.3f}pp.')
    lines += [f'- **Chosen convention: {chosen}**, selected only by workbook fidelity.', '',
              '## 2017-2024 NET30 — median across 10 phases', '']
    z = psum[(psum.period == 'PRE_STRESS_2017_2024') & (psum.cost_bp == 30) & (psum.strategy == 'WEIGHTED_MOM')]
    for u in m.UNIVERSES:
        q = z[z.universe == u]
        if q.empty:
            continue
        r = q.iloc[0]
        lines.append(
            f'- {u}: CAGR {r.median_cagr:+.2%}; MDD {r.median_mdd:+.1%}; Sharpe {r.median_sharpe:.2f}; '
            f'Calmar {r.median_calmar:.2f}; BM CAGR {r.median_benchmark_cagr:+.2%}; excess {r.median_excess_cagr:+.2%}; '
            f'IR {r.median_information_ratio:.2f}; relative MDD {r.median_relative_mdd:+.1%}; turnover {r.median_turnover:.2f}x; '
            f'positive CAGR phases {int(r.positive_cagr_phases)}/{int(r.n_phases)}; positive excess phases {int(r.positive_excess_phases)}/{int(r.n_phases)}.'
        )
    lines += ['', '## Historical blocks — NET30', '']
    for period in ('EARLY_2017_2019', 'LATE_2020_2022', 'NORMAL_2023_2024', 'BULL_2025', 'YTD_2026'):
        lines.append(f'### {period}')
        q0 = psum[(psum.period == period) & (psum.cost_bp == 30) & (psum.strategy == 'WEIGHTED_MOM')]
        for u in m.UNIVERSES:
            q = q0[q0.universe == u]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(
                f'- {u}: CAGR {r.median_cagr:+.2%}; MDD {r.median_mdd:+.1%}; Sharpe {r.median_sharpe:.2f}; '
                f'excess {r.median_excess_cagr:+.2%}; IR {r.median_information_ratio:.2f}; '
                f'positive CAGR {int(r.positive_cagr_phases)}/{int(r.n_phases)}, excess {int(r.positive_excess_phases)}/{int(r.n_phases)}.'
            )
        lines.append('')
    lines += [
        '## Stage gate', '',
        '- Only if this primary is independently credible should CF20 be tested on it.',
        '- 2025/2026 are stress diagnostics, not untouched OOS.',
        '- No other factor and no liquidity overlay enter this run.',
        '- Large raw outputs are retained as gzip chunks plus manifests.', '',
    ]
    (m.OUT / 'PRIMARY_SUMMARY.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    returns, mcap, k200 = m.base.load_basic()
    markets = m.multi.load_market_by_date()
    td_panel, td_parts = m.trading_day_momentum(returns, mcap)
    cal_panel, cal_parts = m.calendar_asof_momentum(returns, mcap)
    chosen, _, validation_summary = m.validate_source_definition(td_panel, td_parts, cal_panel, cal_parts)
    weighted = cal_panel if chosen == 'CALENDAR_MONTH_ASOF' else td_panel
    del td_parts, cal_parts

    store, phase_map = build_targets_primary(returns, mcap, k200, markets, weighted)
    daily = m.simulate_all(returns, store, phase_map)
    bench = m.build_benchmarks(returns, mcap, k200, markets)
    stats = m.performance(daily, bench)
    psum = m.summarize_phases(stats)
    write_summary(chosen, validation_summary, psum)
    print(f'primary chosen={chosen}; daily_rows={len(daily):,}; stats={len(stats):,}; summaries={len(psum):,}')


if __name__ == '__main__':
    main()
