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

OUT = Path(__file__).resolve().parent / 'results_cf20_portfolio_audit'
OUT.mkdir(parents=True, exist_ok=True)

H = 10
TOPN = 20
COST_BP = 30
UNIVERSES = core.UNIVERSES
FACTORS = tuple(core.FACTOR_FAMILY)
STRATEGIES = ('PRIMARY8', 'CF20')
PERIODS = {
    'FULL_2016_2026': (pd.Timestamp('2016-01-01'), pd.Timestamp('2099-12-31')),
    'PRE_STRESS_2016_2024': (pd.Timestamp('2016-01-01'), pd.Timestamp('2024-12-31')),
    'EARLY_2016_2019': (pd.Timestamp('2016-01-01'), pd.Timestamp('2019-12-31')),
    'LATE_2020_2022': (pd.Timestamp('2020-01-01'), pd.Timestamp('2022-12-31')),
    'NORMAL_2023_2024': (pd.Timestamp('2023-01-01'), pd.Timestamp('2024-12-31')),
    'BULL_2025': (pd.Timestamp('2025-01-01'), pd.Timestamp('2025-12-31')),
    'YTD_2026': (pd.Timestamp('2026-01-01'), pd.Timestamp('2099-12-31')),
}


def aggregate_sleeves(sleeves: dict[str, list[str]]) -> pd.Series | None:
    if set(sleeves) != set(FACTORS):
        return None
    w = defaultdict(float)
    unit = 1.0 / len(FACTORS) / TOPN
    for factor in FACTORS:
        names = sleeves[factor]
        if len(names) != TOPN:
            return None
        for code in names:
            w[code] += unit
    s = pd.Series(w, dtype=float).sort_index()
    if not np.isclose(s.sum(), 1.0, atol=1e-10):
        raise RuntimeError(f'weights sum to {s.sum()}')
    return s


def build_targets(returns, k200, markets, files):
    common = sorted(set(returns.index) & set(k200) & set(markets))
    common = [d for d in common if d >= base.START]
    phase_map = {d: i % H for i, d in enumerate(common)}
    ret_pos = {d: i for i, d in enumerate(returns.index)}
    common_pos = {d: ret_pos[d] for d in common if d in ret_pos}

    store = {u: {s: {} for s in STRATEGIES} for u in UNIVERSES}
    sleeve_store = {u: {s: {} for s in STRATEGIES} for u in UNIVERSES}
    compact = []

    for dt in common:
        k = k200[dt]
        market = markets[dt]
        for universe in UNIVERSES:
            codes = multi.universe_codes(universe, k, market)
            minobs = 70 if universe == 'K200' else 120
            if len(codes) < minobs:
                continue
            scores, others = core.build_scores(dt, codes, files)
            if set(scores) != set(FACTORS):
                continue
            by_strategy = {s: {} for s in STRATEGIES}
            failed = False
            for factor in FACTORS:
                primary = scores[factor]
                cf20 = 0.8 * primary + 0.2 * others[factor]
                pnames = core.top_names(primary, TOPN)
                cnames = core.top_names(cf20, TOPN)
                if len(pnames) != TOPN or len(cnames) != TOPN:
                    failed = True
                    break
                by_strategy['PRIMARY8'][factor] = pnames
                by_strategy['CF20'][factor] = cnames
            if failed:
                continue
            for strategy in STRATEGIES:
                target = aggregate_sleeves(by_strategy[strategy])
                if target is None:
                    continue
                store[universe][strategy][dt] = target
                sleeve_store[universe][strategy][dt] = by_strategy[strategy]
                for factor, names in by_strategy[strategy].items():
                    compact.append({
                        'date': dt, 'phase': phase_map[dt], 'universe': universe,
                        'strategy': strategy, 'factor': factor,
                        'family': core.FACTOR_FAMILY[factor], 'codes': '|'.join(names),
                    })

    compact_df = pd.DataFrame(compact)
    write_chunked_csv(compact_df, OUT / 'sleeve_holdings_compact.csv', index=False, target_mb=40)
    return store, sleeve_store, common, phase_map, common_pos


def zero_fill_stock_cum(returns: pd.DataFrame, dt: pd.Timestamp, names: pd.Index | list[str]) -> pd.Series:
    loc = returns.index.get_loc(dt)
    w = returns.iloc[loc + 1:loc + 1 + H].reindex(columns=list(names))
    if len(w) != H:
        return pd.Series(index=list(names), dtype=float)
    w = w.clip(lower=-0.999999).fillna(0.0)
    return (1.0 + w).prod(axis=0) - 1.0


def tieout_windows(returns, store, sleeves, common, phase_map, common_pos):
    fwd = base.forward_returns(returns, H)
    rows = []
    factor_rows = []
    for universe in UNIVERSES:
        for strategy in STRATEGIES:
            by_date = store[universe][strategy]
            for dt, target in by_date.items():
                if dt not in fwd.index:
                    continue
                stock_zero = zero_fill_stock_cum(returns, dt, target.index)
                if stock_zero.isna().all():
                    continue
                direct_zero = float((target * stock_zero.reindex(target.index).fillna(0.0)).sum())
                legacy_factor = []
                complete_factor_n = []
                direct_factor = []
                for factor, names in sleeves[universe][strategy][dt].items():
                    y = fwd.loc[dt].reindex(names)
                    legacy = float(y.mean())
                    z = zero_fill_stock_cum(returns, dt, names)
                    direct = float(z.mean())
                    legacy_factor.append(legacy)
                    direct_factor.append(direct)
                    complete_factor_n.append(int(y.notna().sum()))
                    factor_rows.append({
                        'date': dt, 'phase': phase_map[dt], 'universe': universe,
                        'strategy': strategy, 'factor': factor,
                        'family': core.FACTOR_FAMILY[factor],
                        'legacy_forward': legacy, 'zero_fill_forward': direct,
                        'legacy_minus_zero': legacy - direct,
                        'complete_names': int(y.notna().sum()), 'topn': TOPN,
                    })
                legacy_agg = float(np.nanmean(legacy_factor))
                pos = common_pos.get(dt)
                gap = np.nan
                if pos is not None:
                    later = [x for x in common if x > dt and phase_map[x] == phase_map[dt]]
                    if later:
                        gap = common_pos[later[0]] - pos
                rows.append({
                    'date': dt, 'phase': phase_map[dt], 'universe': universe,
                    'strategy': strategy, 'legacy_forward': legacy_agg,
                    'zero_fill_forward': direct_zero,
                    'legacy_minus_zero': legacy_agg - direct_zero,
                    'min_complete_names_per_sleeve': int(min(complete_factor_n)),
                    'mean_complete_names_per_sleeve': float(np.mean(complete_factor_n)),
                    'next_same_phase_return_index_gap': gap,
                })
    out = pd.DataFrame(rows)
    factors = pd.DataFrame(factor_rows)
    out.to_csv(OUT / 'window_tieout_pre_sim.csv', index=False)
    factors.to_csv(OUT / 'factor_window_returns.csv', index=False)
    return out, factors


def simulate_one(returns, targets, phase, phase_map, universe, strategy):
    scheduled = sorted(d for d in targets if phase_map.get(d) == phase)
    if not scheduled:
        return pd.DataFrame()
    first = scheduled[0]
    scheduled_set = set(scheduled)
    current = pd.Series(dtype=float)
    rows = []
    for dt in returns.index[returns.index >= first]:
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
        cost = turnover * COST_BP / 10000.0
        net = (1.0 + gross) * (1.0 - cost) - 1.0
        rows.append({
            'date': dt, 'universe': universe, 'strategy': strategy, 'phase': phase,
            'gross_ret': gross, 'net30_ret': net, 'turnover': turnover,
            'rebalanced': rebalanced, 'missing_weight': missing_weight,
        })
    return pd.DataFrame(rows)


def simulate_all(returns, store, phase_map):
    frames = []
    for universe in UNIVERSES:
        for strategy in STRATEGIES:
            for phase in range(H):
                x = simulate_one(returns, store[universe][strategy], phase, phase_map, universe, strategy)
                if len(x):
                    frames.append(x)
    daily = pd.concat(frames, ignore_index=True)
    write_chunked_csv(daily, OUT / 'daily_strategy_returns.csv', index=False, target_mb=40)
    return daily


def add_sim_tieout(pre: pd.DataFrame, daily: pd.DataFrame, returns_index: pd.Index):
    pos = {d: i for i, d in enumerate(returns_index)}
    lookup = {}
    for key, g in daily.groupby(['universe', 'strategy', 'phase']):
        lookup[key] = g.set_index('date').sort_index()
    simvals = []
    for r in pre.itertuples(index=False):
        key = (r.universe, r.strategy, r.phase)
        g = lookup.get(key)
        if g is None or r.date not in pos:
            simvals.append(np.nan)
            continue
        i = pos[r.date]
        dates = returns_index[i + 1:i + 1 + H]
        if len(dates) != H or not set(dates).issubset(g.index):
            simvals.append(np.nan)
            continue
        rr = g.loc[dates, 'gross_ret']
        simvals.append(float((1.0 + rr).prod() - 1.0))
    out = pre.copy()
    out['simulated_10d_gross'] = simvals
    out['sim_minus_zero'] = out.simulated_10d_gross - out.zero_fill_forward
    out.to_csv(OUT / 'window_tieout.csv', index=False)
    return out


def build_benchmarks(returns, mcap, k200, markets):
    rows = []
    dates = list(returns.index)
    for i in range(1, len(dates)):
        dt = dates[i]
        prev = dates[i - 1]
        if prev not in k200 or prev not in markets or prev not in mcap.index:
            continue
        k = k200[prev]
        market = markets[prev]
        rr_all = returns.loc[dt]
        mc_all = mcap.loc[prev]
        for universe in UNIVERSES:
            codes = multi.universe_codes(universe, k, market)
            mc = pd.to_numeric(mc_all.reindex(codes), errors='coerce')
            valid_mc = mc[(mc > 0) & mc.notna()]
            if len(valid_mc) < (50 if universe == 'K200' else 100):
                continue
            w = valid_mc / valid_mc.sum()
            rr = rr_all.reindex(w.index)
            miss = float(w[rr.isna()].sum())
            cap_ret = float((w * rr.clip(lower=-0.999999).fillna(0.0)).sum())
            ew = rr.clip(lower=-0.999999).fillna(0.0)
            rows.append({'date': dt, 'universe': universe, 'cap_proxy_ret': cap_ret,
                         'ew_proxy_ret': float(ew.mean()), 'cap_missing_weight': miss,
                         'n_benchmark_names': len(w)})
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
    return float(r.mean() / sd * math.sqrt(252.0)) if len(r) >= 3 and pd.notna(sd) and sd > 0 else np.nan


def mdd(r):
    r = pd.Series(r).dropna()
    if not len(r):
        return np.nan
    nav = (1.0 + r).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def relative_mdd(port, bench):
    q = pd.concat([pd.Series(port).rename('p'), pd.Series(bench).rename('b')], axis=1).dropna()
    if not len(q):
        return np.nan
    rel = (1.0 + q.p) / (1.0 + q.b) - 1.0
    return mdd(rel)


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
    return ex_cagr, te, ir, relative_mdd(q.p, q.b), beta, alpha, corr


def performance_stats(daily, bench):
    b = bench[['date', 'universe', 'cap_proxy_ret']]
    x = daily.merge(b, on=['date', 'universe'], how='left')
    rows = []
    for (universe, strategy, phase), g0 in x.groupby(['universe', 'strategy', 'phase']):
        g0 = g0.sort_values('date')
        for period, (lo, hi) in PERIODS.items():
            g = g0[(g0.date >= lo) & (g0.date <= hi)]
            if len(g) < 40:
                continue
            for ret_col, label in [('gross_ret', 'GROSS'), ('net30_ret', 'NET30')]:
                q = g[[ret_col, 'cap_proxy_ret']].dropna()
                ex_cagr, te, ir, rmdd, beta, alpha, corr = active_stats(q[ret_col], q.cap_proxy_ret)
                rows.append({
                    'universe': universe, 'strategy': strategy, 'phase': phase,
                    'period': period, 'return_type': label, 'n_days': len(q),
                    'cagr': cagr(q[ret_col]), 'mdd': mdd(q[ret_col]), 'sharpe': sharpe(q[ret_col]),
                    'calmar': cagr(q[ret_col]) / abs(mdd(q[ret_col])) if mdd(q[ret_col]) < 0 else np.nan,
                    'benchmark_cagr': cagr(q.cap_proxy_ret), 'benchmark_mdd': mdd(q.cap_proxy_ret),
                    'benchmark_sharpe': sharpe(q.cap_proxy_ret), 'geometric_excess_cagr': ex_cagr,
                    'tracking_error': te, 'information_ratio': ir, 'relative_mdd': rmdd,
                    'beta': beta, 'jensen_alpha_annual': alpha, 'corr': corr,
                    'annual_turnover': float(g.turnover.sum() / (len(g) / 252.0)),
                    'avg_missing_weight': float(g.missing_weight.mean()),
                })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'phase_performance.csv', index=False)
    return out


def factor_period_stats(factors: pd.DataFrame):
    rows = []
    for (universe, strategy, factor, phase), g0 in factors.groupby(['universe', 'strategy', 'factor', 'phase']):
        g0 = g0.sort_values('date')
        for period, (lo, hi) in PERIODS.items():
            g = g0[(g0.date >= lo) & (g0.date <= hi)]
            if len(g) < 8:
                continue
            r = g.zero_fill_forward.dropna()
            legacy = g.legacy_forward.dropna()
            ppy = 252.0 / H
            def pcagr(s):
                if len(s) < 2: return np.nan
                total = float((1.0 + s).prod())
                return total ** (ppy / len(s)) - 1.0 if total > 0 else np.nan
            def psh(s):
                sd = s.std(ddof=1)
                return float(s.mean() / sd * math.sqrt(ppy)) if len(s) >= 3 and sd > 0 else np.nan
            rows.append({
                'universe': universe, 'strategy': strategy, 'factor': factor,
                'family': core.FACTOR_FAMILY[factor], 'phase': phase, 'period': period,
                'zero_fill_cagr': pcagr(r), 'zero_fill_sharpe': psh(r),
                'legacy_cagr': pcagr(legacy), 'legacy_sharpe': psh(legacy),
                'mean_legacy_minus_zero': float(g.legacy_minus_zero.mean()),
                'mean_complete_names': float(g.complete_names.mean()), 'n_periods': len(g),
            })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'factor_phase_performance.csv', index=False)
    return out


def summarize_tieout(tie):
    rows = []
    for (u, s), g in tie.groupby(['universe', 'strategy']):
        z = g.sim_minus_zero.dropna().abs()
        l = g.legacy_minus_zero.dropna()
        rows.append({
            'universe': u, 'strategy': s, 'n_windows': len(g),
            'sim_vs_zero_mean_abs': float(z.mean()) if len(z) else np.nan,
            'sim_vs_zero_p99_abs': float(z.quantile(.99)) if len(z) else np.nan,
            'sim_vs_zero_max_abs': float(z.max()) if len(z) else np.nan,
            'legacy_minus_zero_mean': float(l.mean()) if len(l) else np.nan,
            'legacy_vs_zero_mean_abs': float(l.abs().mean()) if len(l) else np.nan,
            'legacy_vs_zero_p99_abs': float(l.abs().quantile(.99)) if len(l) else np.nan,
            'mean_min_complete_names': float(g.min_complete_names_per_sleeve.mean()),
            'share_gap_exact_h': float((g.next_same_phase_return_index_gap == H).mean()),
        })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'tieout_summary.csv', index=False)
    return out


def make_report(tie_sum, perf, fperf):
    L = ['# CF20 Portfolio Audit', '',
         'Purpose: reconcile legacy non-overlapping forward-return tests with the daily-NAV implementation before making any strategy-quality claim.', '',
         'Legacy forward returns use the original implementation, where a stock with any missing daily return in the next 10 days has a NaN 10D return and is skipped by the cross-sectional mean. The audit zero-fill path instead matches the daily NAV convention: missing daily stock returns are treated as 0 while the position remains held.', '',
         'Benchmarks below are lagged-membership / lagged-total-market-cap universe proxies constructed from the same stock return panel. They are sanity-check benchmarks, not official KOSPI/KOSDAQ/K200 index series; K200 in particular is not free-float weighted here.', '',
         '## Exact tie-out: simulated daily NAV vs direct 10D holding return', '']
    for r in tie_sum.itertuples(index=False):
        status = 'PASS' if pd.notna(r.sim_vs_zero_max_abs) and r.sim_vs_zero_max_abs < 1e-10 and r.share_gap_exact_h > .999 else 'CHECK'
        L.append(f'- {r.universe} {r.strategy}: {status}; sim-vs-direct max abs {r.sim_vs_zero_max_abs:.3e}; legacy-minus-direct mean {r.legacy_minus_zero_mean:+.3%}; legacy/direct mean abs gap {r.legacy_vs_zero_mean_abs:.3%}; same-phase gap exactly 10 returns {r.share_gap_exact_h:.1%}')

    L += ['', '## Absolute and benchmark-relative results — 2016-2024, NET30, median across 10 phases', '']
    z = perf[(perf.period == 'PRE_STRESS_2016_2024') & (perf.return_type == 'NET30')]
    for u in UNIVERSES:
        q = z[z.universe == u]
        if q.empty: continue
        L.append(f'### {u}')
        for s in STRATEGIES:
            x = q[q.strategy == s]
            if x.empty: continue
            L.append(f"- {s}: CAGR {x.cagr.median():+.2%}; MDD {x.mdd.median():+.1%}; Sharpe {x.sharpe.median():.2f}; Calmar {x.calmar.median():.2f}; BM CAGR {x.benchmark_cagr.median():+.2%}; geometric excess CAGR {x.geometric_excess_cagr.median():+.2%}; IR {x.information_ratio.median():.2f}; relative MDD {x.relative_mdd.median():+.1%}")
        p = q[q.strategy == 'PRIMARY8'].set_index('phase')
        c = q[q.strategy == 'CF20'].set_index('phase')
        phases = sorted(set(p.index) & set(c.index))
        if phases:
            dc = c.loc[phases, 'cagr'] - p.loc[phases, 'cagr']
            de = c.loc[phases, 'geometric_excess_cagr'] - p.loc[phases, 'geometric_excess_cagr']
            L.append(f'- CF20 incremental: median dCAGR {dc.median():+.2%}; better CAGR phases {(dc>0).sum()}/{len(dc)}; median dExcessCAGR {de.median():+.2%}')
        L.append('')

    L += ['## Factor-sleeve diagnosis — 2016-2024 zero-fill gross CAGR, median across phases', '']
    q = fperf[fperf.period == 'PRE_STRESS_2016_2024']
    for u in UNIVERSES:
        L.append(f'### {u}')
        for f in FACTORS:
            p = q[(q.universe == u) & (q.strategy == 'PRIMARY8') & (q.factor == f)]
            c = q[(q.universe == u) & (q.strategy == 'CF20') & (q.factor == f)]
            if p.empty or c.empty: continue
            L.append(f'- {f}: Primary {p.zero_fill_cagr.median():+.2%} / Sharpe {p.zero_fill_sharpe.median():.2f}; CF20 {c.zero_fill_cagr.median():+.2%} / Sharpe {c.zero_fill_sharpe.median():.2f}')
        L.append('')

    L += ['## Audit guardrails', '',
          '- If simulated daily NAV does not match the direct zero-fill 10D holding return, the portfolio implementation is invalid and must be fixed before interpretation.',
          '- If simulated/direct tie but legacy differs materially, prior forward-return summaries and daily NAV are answering slightly different missing-data questions; both should be restated consistently.',
          '- CF20 was originally validated as an incremental overlay versus each primary-factor sleeve. A weak equal-notional 8-sleeve aggregate does not contradict a positive incremental overlay, but it does invalidate any claim that the aggregate CF20 portfolio itself was previously proven to be a strong standalone strategy.',
          '- Benchmark-relative results use internal cap-weighted proxies only; official index data should replace them before production-level attribution.', '']
    return '\n'.join(L)


def main():
    returns, mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}

    store, sleeves, common, phase_map, common_pos = build_targets(returns, k200, markets, files)
    pre, factor_windows = tieout_windows(returns, store, sleeves, common, phase_map, common_pos)
    daily = simulate_all(returns, store, phase_map)
    tie = add_sim_tieout(pre, daily, returns.index)
    bench = build_benchmarks(returns, mcap, k200, markets)
    perf = performance_stats(daily, bench)
    fperf = factor_period_stats(factor_windows)
    tie_sum = summarize_tieout(tie)
    report = make_report(tie_sum, perf, fperf)
    (OUT / 'AUDIT_SUMMARY.md').write_text(report, encoding='utf-8')
    print(report)
    print(f'tie_windows={len(tie):,}; daily_rows={len(daily):,}; perf_rows={len(perf):,}; factor_stats={len(fperf):,}')


if __name__ == '__main__':
    main()
