from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import math
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/liquidity_cross_factor'))
sys.path.insert(0, str(ROOT / 'research/stock_level_factor_interaction'))
sys.path.insert(0, str(ROOT / 'research/common'))

import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as multi
import run_cf20_decomposition_liquidity_ranges as core
from chunked_csv import write_chunked_csv

OUT = Path(__file__).resolve().parent / 'results'
OUT.mkdir(parents=True, exist_ok=True)

H = 10
TOPN = 20
MCAP_CUTOFF_BN = 250.0
COSTS_BP = (0, 30, 60)
UNIVERSES = core.UNIVERSES
STRATEGIES = ('MOM1M_SOURCE', 'MOM12_1_SOURCE', 'WEIGHTED_MOM', 'WEIGHTED_MOM_CF20')
PERIODS = {
    'FULL_2017_2026': (pd.Timestamp('2017-01-01'), pd.Timestamp('2099-12-31')),
    'PRE_STRESS_2017_2024': (pd.Timestamp('2017-01-01'), pd.Timestamp('2024-12-31')),
    'EARLY_2017_2019': (pd.Timestamp('2017-01-01'), pd.Timestamp('2019-12-31')),
    'LATE_2020_2022': (pd.Timestamp('2020-01-01'), pd.Timestamp('2022-12-31')),
    'NORMAL_2023_2024': (pd.Timestamp('2023-01-01'), pd.Timestamp('2024-12-31')),
    'BULL_2025': (pd.Timestamp('2025-01-01'), pd.Timestamp('2025-12-31')),
    'YTD_2026': (pd.Timestamp('2026-01-01'), pd.Timestamp('2099-12-31')),
}

# Exact legacy workbook definition recovered from the factor-tracking workbook.
WMOM_COMPONENT_WEIGHTS = {1: 12.0 / 17.0, 3: 4.0 / 17.0, 6: 2.0 / 17.0, 12: 1.0 / 17.0}
TD_LOOKBACK = {1: 21, 3: 63, 6: 126, 12: 252}

# Workbook snapshot values on 2026-06-17. Values are percentage returns.
# These are used ONLY to choose the return-horizon convention that best reproduces
# the source definition, never to optimize portfolio returns.
WORKBOOK_SAMPLES = {
    'A000070': {'r1': -6.55, 'r3': -18.55, 'r6': -7.61, 'r12': -3.75, 'factor': -10.104117647058825},
    'A000080': {'r1': -6.13, 'r3': -5.24, 'r6': -16.08, 'r12': -20.80, 'factor': -8.67529411764706},
    'A000100': {'r1': -8.02, 'r3': -20.50, 'r6': -30.80, 'r12': -24.45, 'factor': -15.546470588235294},
    'A000120': {'r1': -8.33, 'r3': -25.96, 'r6': -11.77, 'r12': 1.44, 'factor': -13.288235294117648},
    'A000150': {'r1': 0.62, 'r3': 46.31, 'r6': 93.56, 'r12': 165.36, 'factor': 32.06823529411765},
}
VALIDATION_DATE = pd.Timestamp('2026-06-17')


def wmom_from_components(parts: dict[int, pd.DataFrame]) -> pd.DataFrame:
    out = None
    for months, w in WMOM_COMPONENT_WEIGHTS.items():
        x = parts[months] * w
        out = x if out is None else out + x
    return out


def trading_day_momentum(returns: pd.DataFrame, mcap: pd.DataFrame):
    logs = np.log1p(returns.clip(lower=-0.999999).fillna(0.0))
    cs = logs.cumsum()
    parts = {}
    for months, n in TD_LOOKBACK.items():
        r = np.expm1(cs - cs.shift(n))
        valid = mcap.notna() & mcap.shift(n).notna() & mcap.gt(0) & mcap.shift(n).gt(0)
        parts[months] = r.where(valid)
    return wmom_from_components(parts), parts


def calendar_asof_momentum(returns: pd.DataFrame, mcap: pd.DataFrame):
    idx = returns.index
    cols = returns.columns
    logs = np.log1p(returns.clip(lower=-0.999999).fillna(0.0))
    cs = logs.cumsum().to_numpy(float)
    mc = mcap.reindex(index=idx, columns=cols).to_numpy(float)
    nrow, ncol = cs.shape
    out = np.full((nrow, ncol), np.nan, dtype=float)
    part_arrays = {m: np.full((nrow, ncol), np.nan, dtype=float) for m in WMOM_COMPONENT_WEIGHTS}

    for i, dt in enumerate(idx):
        acc = np.zeros(ncol, dtype=float)
        valid_all = np.ones(ncol, dtype=bool)
        ok = True
        for months, w in WMOM_COMPONENT_WEIGHTS.items():
            anchor = dt - pd.DateOffset(months=months)
            j = int(idx.searchsorted(anchor, side='right') - 1)
            if j < 0 or j >= i:
                ok = False
                break
            raw = np.expm1(cs[i] - cs[j])
            valid = np.isfinite(mc[i]) & np.isfinite(mc[j]) & (mc[i] > 0) & (mc[j] > 0)
            raw[~valid] = np.nan
            part_arrays[months][i] = raw
            acc += np.nan_to_num(raw, nan=0.0) * w
            valid_all &= valid
        if ok:
            acc[~valid_all] = np.nan
            out[i] = acc

    panel = pd.DataFrame(out, index=idx, columns=cols)
    parts = {m: pd.DataFrame(v, index=idx, columns=cols) for m, v in part_arrays.items()}
    return panel, parts


def validate_source_definition(td_panel, td_parts, cal_panel, cal_parts):
    rows = []
    for method, panel, parts in (
        ('TRADING_DAYS_21_63_126_252', td_panel, td_parts),
        ('CALENDAR_MONTH_ASOF', cal_panel, cal_parts),
    ):
        for code, expected in WORKBOOK_SAMPLES.items():
            rec = {'method': method, 'date': VALIDATION_DATE, 'code': code}
            for months in (1, 3, 6, 12):
                got = float(parts[months].at[VALIDATION_DATE, code] * 100.0) if VALIDATION_DATE in parts[months].index and code in parts[months].columns else np.nan
                exp = expected[f'r{months}']
                rec[f'r{months}_calc_pct'] = got
                rec[f'r{months}_workbook_pct'] = exp
                rec[f'r{months}_error_pp'] = got - exp if np.isfinite(got) else np.nan
            got_factor = float(panel.at[VALIDATION_DATE, code] * 100.0) if VALIDATION_DATE in panel.index and code in panel.columns else np.nan
            rec['factor_calc_pct'] = got_factor
            rec['factor_workbook_pct'] = expected['factor']
            rec['factor_error_pp'] = got_factor - expected['factor'] if np.isfinite(got_factor) else np.nan
            rows.append(rec)
    detail = pd.DataFrame(rows)
    agg = []
    for method, g in detail.groupby('method'):
        raw_errors = []
        for m in (1, 3, 6, 12):
            raw_errors.extend(g[f'r{m}_error_pp'].dropna().tolist())
        factor_errors = g.factor_error_pp.dropna().to_numpy(float)
        agg.append({
            'method': method,
            'raw_component_rmse_pp': float(np.sqrt(np.mean(np.square(raw_errors)))) if raw_errors else np.nan,
            'raw_component_mae_pp': float(np.mean(np.abs(raw_errors))) if raw_errors else np.nan,
            'factor_rmse_pp': float(np.sqrt(np.mean(np.square(factor_errors)))) if len(factor_errors) else np.nan,
            'factor_mae_pp': float(np.mean(np.abs(factor_errors))) if len(factor_errors) else np.nan,
            'n_samples': int(len(g)),
        })
    summary = pd.DataFrame(agg).sort_values(['raw_component_rmse_pp', 'factor_rmse_pp'])
    chosen = summary.iloc[0].method
    detail.to_csv(OUT / 'source_definition_validation.csv', index=False)
    summary.to_csv(OUT / 'source_definition_validation_summary.csv', index=False)
    return chosen, detail, summary


def equal_weight_target(names: list[str]) -> pd.Series:
    return pd.Series(1.0 / len(names), index=pd.Index(names), dtype=float) if names else pd.Series(dtype=float)


def build_targets(returns, mcap, k200, markets, weighted_panel):
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}
    common = sorted(set(returns.index) & set(mcap.index) & set(k200) & set(markets))
    common = [d for d in common if d >= pd.Timestamp('2017-01-01')]
    phase_map = {d: i % H for i, d in enumerate(common)}
    store = {u: {s: {} for s in STRATEGIES} for u in UNIVERSES}
    compact = []

    for dt in common:
        if dt not in weighted_panel.index:
            continue
        k = k200[dt]
        market = markets[dt]
        mc = mcap.loc[dt]
        for universe in UNIVERSES:
            codes = multi.universe_codes(universe, k, market)
            eligible = codes[(pd.to_numeric(mc.reindex(codes), errors='coerce') >= MCAP_CUTOFF_BN).fillna(False)]
            if len(eligible) < 40:
                continue
            scores, others = core.build_scores(dt, eligible, files)
            if set(scores) != set(core.FACTOR_FAMILY):
                continue
            raw_wmom = pd.to_numeric(weighted_panel.loc[dt].reindex(eligible), errors='coerce')
            wm_score = core.rank_good(raw_wmom, True)
            other_consensus = others.get('MOM12_1')
            if other_consensus is None:
                continue
            score_map = {
                'MOM1M_SOURCE': scores['MOM1M'],
                'MOM12_1_SOURCE': scores['MOM12_1'],
                'WEIGHTED_MOM': wm_score,
                'WEIGHTED_MOM_CF20': 0.8 * wm_score + 0.2 * other_consensus,
            }
            for strategy, score in score_map.items():
                names = core.top_names(score, TOPN)
                if len(names) != TOPN:
                    continue
                store[universe][strategy][dt] = equal_weight_target(names)
                compact.append({
                    'date': dt, 'phase': phase_map[dt], 'universe': universe,
                    'strategy': strategy, 'eligible_n': len(eligible), 'codes': '|'.join(names),
                })
    write_chunked_csv(pd.DataFrame(compact), OUT / 'holdings_compact.csv', index=False, target_mb=40)
    return store, phase_map


def simulate_one(returns, targets, phase, phase_map, universe, strategy):
    scheduled = sorted(d for d in targets if phase_map.get(d) == phase)
    if not scheduled:
        return pd.DataFrame()
    scheduled_set = set(scheduled)
    current = pd.Series(dtype=float)
    rows = []
    for dt in returns.index[returns.index >= scheduled[0]]:
        gross = 0.0
        missing_weight = 0.0
        if len(current):
            rr = returns.loc[dt].reindex(current.index)
            missing_weight = float(current[rr.isna()].sum())
            rr = rr.clip(lower=-0.999999).fillna(0.0)
            gross = float((current * rr).sum())
            grown = current * (1.0 + rr)
            denom = float(grown.sum())
            if denom > 0:
                current = grown / denom
        turnover = 0.0
        rebalanced = 0
        if dt in scheduled_set:
            target = targets[dt]
            if len(current):
                union = current.index.union(target.index)
                turnover = float(0.5 * (current.reindex(union, fill_value=0.0) - target.reindex(union, fill_value=0.0)).abs().sum())
            else:
                turnover = 1.0
            current = target.copy()
            rebalanced = 1
        rec = {
            'date': dt, 'universe': universe, 'strategy': strategy, 'phase': phase,
            'gross_ret': gross, 'turnover': turnover, 'rebalanced': rebalanced,
            'missing_weight': missing_weight,
        }
        for cost in COSTS_BP:
            c = turnover * cost / 10000.0
            rec[f'net{cost}_ret'] = (1.0 + gross) * (1.0 - c) - 1.0
        rows.append(rec)
    return pd.DataFrame(rows)


def simulate_all(returns, store, phase_map):
    frames = []
    for universe in UNIVERSES:
        for strategy in STRATEGIES:
            for phase in range(H):
                x = simulate_one(returns, store[universe][strategy], phase, phase_map, universe, strategy)
                if len(x):
                    frames.append(x)
    out = pd.concat(frames, ignore_index=True)
    write_chunked_csv(out, OUT / 'daily_strategy_returns.csv', index=False, target_mb=40)
    return out


def build_benchmarks(returns, mcap, k200, markets):
    rows = []
    dates = list(returns.index)
    for i in range(1, len(dates)):
        dt, prev = dates[i], dates[i - 1]
        if prev not in k200 or prev not in markets or prev not in mcap.index:
            continue
        for universe in UNIVERSES:
            codes = multi.universe_codes(universe, k200[prev], markets[prev])
            mc = pd.to_numeric(mcap.loc[prev].reindex(codes), errors='coerce')
            mc = mc[(mc > 0) & mc.notna()]
            if len(mc) < (50 if universe == 'K200' else 100):
                continue
            w = mc / mc.sum()
            rr = returns.loc[dt].reindex(w.index).clip(lower=-0.999999).fillna(0.0)
            rows.append({'date': dt, 'universe': universe, 'benchmark_ret': float((w * rr).sum())})
    out = pd.DataFrame(rows)
    write_chunked_csv(out, OUT / 'daily_benchmark_proxy.csv', index=False, target_mb=40)
    return out


def cagr(r):
    r = pd.Series(r).dropna()
    if len(r) < 2:
        return np.nan
    total = float((1.0 + r).prod())
    years = len(r) / 252.0
    return total ** (1.0 / years) - 1.0 if total > 0 and years > 0 else np.nan


def sharpe(r):
    r = pd.Series(r).dropna()
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(252.0)) if len(r) >= 3 and np.isfinite(sd) and sd > 0 else np.nan


def mdd(r):
    r = pd.Series(r).dropna()
    if not len(r):
        return np.nan
    nav = (1.0 + r).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def active_stats(port, bench):
    q = pd.concat([pd.Series(port).rename('p'), pd.Series(bench).rename('b')], axis=1).dropna()
    if len(q) < 40:
        return (np.nan,) * 7
    active = q.p - q.b
    te = float(active.std(ddof=1) * math.sqrt(252.0))
    ir = float(active.mean() / active.std(ddof=1) * math.sqrt(252.0)) if active.std(ddof=1) > 0 else np.nan
    rel = (1.0 + q.p) / (1.0 + q.b) - 1.0
    ex_cagr = cagr(rel)
    beta = float(q.p.cov(q.b) / q.b.var()) if q.b.var() > 0 else np.nan
    alpha = float((q.p - beta * q.b).mean() * 252.0) if np.isfinite(beta) else np.nan
    corr = float(q.p.corr(q.b))
    rel_mdd = mdd(rel)
    return ex_cagr, te, ir, rel_mdd, beta, alpha, corr


def performance(daily, bench):
    x = daily.merge(bench, on=['date', 'universe'], how='left')
    rows = []
    for (universe, strategy, phase), g0 in x.groupby(['universe', 'strategy', 'phase']):
        g0 = g0.sort_values('date')
        for period, (lo, hi) in PERIODS.items():
            g = g0[(g0.date >= lo) & (g0.date <= hi)]
            if len(g) < 40:
                continue
            years = len(g) / 252.0
            for cost in COSTS_BP:
                r = g[f'net{cost}_ret']
                bm = g.benchmark_ret
                cg, dd, sh = cagr(r), mdd(r), sharpe(r)
                ex, te, ir, rdd, beta, alpha, corr = active_stats(r.reset_index(drop=True), bm.reset_index(drop=True))
                rows.append({
                    'universe': universe, 'strategy': strategy, 'phase': phase, 'period': period,
                    'cost_bp': cost, 'n_days': len(g), 'cagr': cg, 'mdd': dd, 'sharpe': sh,
                    'calmar': cg / abs(dd) if np.isfinite(cg) and np.isfinite(dd) and dd < 0 else np.nan,
                    'benchmark_cagr': cagr(bm), 'benchmark_mdd': mdd(bm), 'benchmark_sharpe': sharpe(bm),
                    'geometric_excess_cagr': ex, 'tracking_error': te, 'information_ratio': ir,
                    'relative_mdd': rdd, 'beta': beta, 'jensen_alpha_annual': alpha, 'corr': corr,
                    'annual_turnover': float(g.turnover.sum() / years) if years > 0 else np.nan,
                    'avg_missing_weight': float(g.missing_weight.mean()),
                })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'phase_performance.csv', index=False)
    return out


def summarize_phases(stats):
    rows = []
    for key, g in stats.groupby(['universe', 'strategy', 'period', 'cost_bp']):
        rows.append({
            'universe': key[0], 'strategy': key[1], 'period': key[2], 'cost_bp': key[3],
            'n_phases': g.phase.nunique(), 'median_cagr': g.cagr.median(), 'worst_phase_cagr': g.cagr.min(),
            'positive_cagr_phases': int((g.cagr > 0).sum()), 'median_mdd': g.mdd.median(),
            'median_sharpe': g.sharpe.median(), 'worst_phase_sharpe': g.sharpe.min(),
            'median_calmar': g.calmar.median(), 'median_benchmark_cagr': g.benchmark_cagr.median(),
            'median_excess_cagr': g.geometric_excess_cagr.median(), 'positive_excess_phases': int((g.geometric_excess_cagr > 0).sum()),
            'median_information_ratio': g.information_ratio.median(), 'median_relative_mdd': g.relative_mdd.median(),
            'median_turnover': g.annual_turnover.median(),
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'portfolio_summary.csv', index=False)
    return out


def compare_cf20(stats):
    rows = []
    for (u, period, cost), g in stats.groupby(['universe', 'period', 'cost_bp']):
        b = g[g.strategy.eq('WEIGHTED_MOM')].set_index('phase')
        q = g[g.strategy.eq('WEIGHTED_MOM_CF20')].set_index('phase')
        phases = sorted(set(b.index) & set(q.index))
        if not phases:
            continue
        d = q.loc[phases] - b.loc[phases]
        rows.append({
            'universe': u, 'period': period, 'cost_bp': cost, 'n_phases': len(phases),
            'median_delta_cagr': float(d.cagr.median()), 'cagr_better_phases': int((d.cagr > 0).sum()),
            'median_delta_sharpe': float(d.sharpe.median()), 'sharpe_better_phases': int((d.sharpe > 0).sum()),
            'median_delta_excess_cagr': float(d.geometric_excess_cagr.median()),
            'excess_better_phases': int((d.geometric_excess_cagr > 0).sum()),
            'median_delta_turnover': float(d.annual_turnover.median()),
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'cf20_incremental.csv', index=False)
    return out


def make_summary(chosen, validation_summary, psum, inc):
    lines = [
        '# Legacy Weighted Momentum Recheck', '',
        'Research framing: independently validate the historical weighted-momentum primary first; CF20 is an enhancement, not a standalone eight-factor strategy.', '',
        '## Recovered legacy definition', '',
        '- Score = `(12*R1M + 4*R3M + 2*R6M + R12M) / 17`.',
        '- Descending rank, Top20, market-cap cutoff KRW 250bn.',
        '- `MOM1M` and `MOM12_1` remain separate comparison signals.', '',
        '## Source-definition validation', '',
    ]
    for r in validation_summary.itertuples(index=False):
        lines.append(f'- {r.method}: raw-component RMSE {r.raw_component_rmse_pp:.3f}pp; factor RMSE {r.factor_rmse_pp:.3f}pp.')
    lines += [f'- **Chosen reconstruction convention: {chosen}** (chosen only by source-value fidelity, never by future performance).', '',
              '## 2017-2024 NET30 portfolio results — median across 10 rebalance phases', '']
    z = psum[(psum.period == 'PRE_STRESS_2017_2024') & (psum.cost_bp == 30)]
    for u in UNIVERSES:
        lines += [f'### {u}']
        for s in STRATEGIES:
            q = z[(z.universe == u) & (z.strategy == s)]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(f'- {s}: CAGR {r.median_cagr:+.2%}; MDD {r.median_mdd:+.1%}; Sharpe {r.median_sharpe:.2f}; Calmar {r.median_calmar:.2f}; BM excess {r.median_excess_cagr:+.2%}; IR {r.median_information_ratio:.2f}; turnover {r.median_turnover:.2f}x; positive CAGR phases {int(r.positive_cagr_phases)}/{int(r.n_phases)}.')
        lines.append('')
    lines += ['## CF20 incremental on weighted momentum — NET30', '']
    for period in ('EARLY_2017_2019', 'LATE_2020_2022', 'NORMAL_2023_2024', 'BULL_2025', 'YTD_2026'):
        lines.append(f'### {period}')
        z2 = inc[(inc.period == period) & (inc.cost_bp == 30)]
        for u in UNIVERSES:
            q = z2[z2.universe == u]
            if q.empty:
                continue
            r = q.iloc[0]
            lines.append(f'- {u}: dCAGR {r.median_delta_cagr:+.2%} ({int(r.cagr_better_phases)}/{int(r.n_phases)} phases); dSharpe {r.median_delta_sharpe:+.2f}; dExcessCAGR {r.median_delta_excess_cagr:+.2%}; dTurnover {r.median_delta_turnover:+.2f}x.')
        lines.append('')
    lines += ['## Interpretation guardrails', '',
              '- The reconstruction method is selected by matching workbook raw 1/3/6/12M values, not by backtest returns.',
              '- The score definition is exact; the research portfolio uses an equal-weight Top20 sleeve so stock-selection quality is isolated. Do not infer this is the historical production weighting unless separately verified.',
              '- Only if WEIGHTED_MOM itself has credible absolute and benchmark-relative results should the CF20 incremental result be considered for production research.',
              '- Liquidity overlays are intentionally excluded from this run.',
              '- 2025/2026 are stress diagnostics, not untouched OOS.',
              '- Large raw outputs are preserved as gzip chunks plus manifests.', '']
    text = '\n'.join(lines)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')


def main():
    returns, mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    td_panel, td_parts = trading_day_momentum(returns, mcap)
    cal_panel, cal_parts = calendar_asof_momentum(returns, mcap)
    chosen, _, validation_summary = validate_source_definition(td_panel, td_parts, cal_panel, cal_parts)
    weighted = cal_panel if chosen == 'CALENDAR_MONTH_ASOF' else td_panel
    del td_parts, cal_parts

    store, phase_map = build_targets(returns, mcap, k200, markets, weighted)
    daily = simulate_all(returns, store, phase_map)
    bench = build_benchmarks(returns, mcap, k200, markets)
    stats = performance(daily, bench)
    psum = summarize_phases(stats)
    inc = compare_cf20(stats)
    make_summary(chosen, validation_summary, psum, inc)
    print(f'chosen={chosen}; daily_rows={len(daily):,}; stats={len(stats):,}; summaries={len(psum):,}')


if __name__ == '__main__':
    main()
