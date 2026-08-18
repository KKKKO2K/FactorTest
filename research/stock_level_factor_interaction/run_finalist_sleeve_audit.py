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

OUT = Path(__file__).resolve().parent / 'results_finalist_sleeve_audit'
OUT.mkdir(parents=True, exist_ok=True)

H = 10
TOPN = 20
COSTS_BP = (0, 30, 60)
PERIODS = {
    'FULL_2016_2026': (pd.Timestamp('2016-01-01'), pd.Timestamp('2099-12-31')),
    'PRE_STRESS_2016_2024': (pd.Timestamp('2016-01-01'), pd.Timestamp('2024-12-31')),
    'EARLY_2016_2019': (pd.Timestamp('2016-01-01'), pd.Timestamp('2019-12-31')),
    'LATE_2020_2022': (pd.Timestamp('2020-01-01'), pd.Timestamp('2022-12-31')),
    'NORMAL_2023_2024': (pd.Timestamp('2023-01-01'), pd.Timestamp('2024-12-31')),
    'BULL_2025': (pd.Timestamp('2025-01-01'), pd.Timestamp('2025-12-31')),
    'YTD_2026': (pd.Timestamp('2026-01-01'), pd.Timestamp('2099-12-31')),
}

FINALISTS = (
    ('KOSPI_ALL', 'PER12MF'),
    ('KOSPI_ALL', 'PRIVATE_FLOW'),
    ('KOSDAQ_PLUS_KOSPI_EX_K200', 'PER12MF'),
    ('KOSDAQ_PLUS_KOSPI_EX_K200', 'OPFY1_REV'),
)
STRATEGIES = ('BASE', 'CF20')


def ew_target(names: list[str]) -> pd.Series:
    if len(names) != TOPN:
        return pd.Series(dtype=float)
    return pd.Series(1.0 / TOPN, index=pd.Index(names), dtype=float).sort_index()


def build_targets(returns, k200, markets, files):
    common = sorted(set(returns.index) & set(k200) & set(markets))
    common = [d for d in common if d >= base.START]
    phase_map = {d: i % H for i, d in enumerate(common)}
    targets = {(u, f, s): {} for u, f in FINALISTS for s in STRATEGIES}
    rows = []

    needed_universes = sorted({u for u, _ in FINALISTS})
    factors_by_u = defaultdict(set)
    for u, f in FINALISTS:
        factors_by_u[u].add(f)

    for dt in common:
        k = k200[dt]
        market = markets[dt]
        for universe in needed_universes:
            codes = multi.universe_codes(universe, k, market)
            minobs = 70 if universe == 'K200' else 120
            if len(codes) < minobs:
                continue
            scores, others = core.build_scores(dt, codes, files)
            if not scores:
                continue
            for factor in factors_by_u[universe]:
                if factor not in scores or factor not in others:
                    continue
                primary = scores[factor]
                cf20 = 0.8 * primary + 0.2 * others[factor]
                by_s = {
                    'BASE': core.top_names(primary, TOPN),
                    'CF20': core.top_names(cf20, TOPN),
                }
                for strategy, names in by_s.items():
                    target = ew_target(names)
                    if len(target) != TOPN:
                        continue
                    targets[(universe, factor, strategy)][dt] = target
                    rows.append({
                        'date': dt, 'phase': phase_map[dt], 'universe': universe,
                        'factor': factor, 'strategy': strategy, 'codes': '|'.join(names),
                    })
    pd.DataFrame(rows).to_csv(OUT / 'holdings.csv', index=False)
    return targets, phase_map


def simulate_one(returns, targets, phase, phase_map, universe, factor, strategy):
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
                turnover = float(0.5 * (
                    current.reindex(union, fill_value=0.0)
                    - target.reindex(union, fill_value=0.0)
                ).abs().sum())
            else:
                turnover = 1.0
            current = target.copy()
            rebalanced = 1

        row = {
            'date': dt, 'universe': universe, 'factor': factor,
            'strategy': strategy, 'phase': phase,
            'gross_ret': gross, 'turnover': turnover,
            'rebalanced': rebalanced, 'missing_weight': missing_weight,
        }
        for bp in (30, 60):
            cost = turnover * bp / 10000.0
            row[f'net{bp}_ret'] = (1.0 + gross) * (1.0 - cost) - 1.0
        rows.append(row)
    return pd.DataFrame(rows)


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


def performance(daily):
    rows = []
    mapping = [('gross_ret', 'GROSS'), ('net30_ret', 'NET30'), ('net60_ret', 'NET60')]
    for (u, f, s, phase), g0 in daily.groupby(['universe', 'factor', 'strategy', 'phase']):
        g0 = g0.sort_values('date')
        for period, (lo, hi) in PERIODS.items():
            g = g0[(g0.date >= lo) & (g0.date <= hi)]
            if len(g) < 40:
                continue
            annual_turnover = float(g.turnover.sum() / (len(g) / 252.0))
            for col, label in mapping:
                r = g[col]
                md = mdd(r)
                cg = cagr(r)
                rows.append({
                    'universe': u, 'factor': f, 'strategy': s, 'phase': phase,
                    'period': period, 'return_type': label, 'n_days': len(g),
                    'cagr': cg, 'sharpe': sharpe(r), 'mdd': md,
                    'calmar': cg / abs(md) if pd.notna(md) and md < 0 else np.nan,
                    'annual_turnover': annual_turnover,
                    'avg_missing_weight': float(g.missing_weight.mean()),
                })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'phase_performance.csv', index=False)
    return out


def summarize(perf):
    keys = ['universe', 'factor', 'strategy', 'period', 'return_type']
    agg = perf.groupby(keys, as_index=False).agg(
        median_cagr=('cagr', 'median'),
        median_sharpe=('sharpe', 'median'),
        median_mdd=('mdd', 'median'),
        worst_phase_mdd=('mdd', 'min'),
        median_calmar=('calmar', 'median'),
        median_annual_turnover=('annual_turnover', 'median'),
        min_cagr=('cagr', 'min'),
        max_cagr=('cagr', 'max'),
        positive_phases=('cagr', lambda x: int((x > 0).sum())),
        n_phases=('cagr', 'size'),
    )
    agg.to_csv(OUT / 'summary_median.csv', index=False)

    deltas = []
    for (u, f, period, rt), g in perf.groupby(['universe', 'factor', 'period', 'return_type']):
        p = g[g.strategy == 'BASE'].set_index('phase')
        c = g[g.strategy == 'CF20'].set_index('phase')
        phases = sorted(set(p.index) & set(c.index))
        if not phases:
            continue
        dc = c.loc[phases, 'cagr'] - p.loc[phases, 'cagr']
        ds = c.loc[phases, 'sharpe'] - p.loc[phases, 'sharpe']
        dm = c.loc[phases, 'mdd'] - p.loc[phases, 'mdd']
        deltas.append({
            'universe': u, 'factor': f, 'period': period, 'return_type': rt,
            'median_delta_cagr': float(dc.median()),
            'median_delta_sharpe': float(ds.median()),
            'median_delta_mdd': float(dm.median()),
            'cagr_win_phases': int((dc > 0).sum()),
            'sharpe_win_phases': int((ds > 0).sum()),
            'mdd_improve_phases': int((dm > 0).sum()),
            'n_phases': len(phases),
        })
    pd.DataFrame(deltas).to_csv(OUT / 'cf20_incremental.csv', index=False)
    return agg, pd.DataFrame(deltas)


def make_report(summary, deltas):
    L = ['# Finalist Factor-Sleeve Daily NAV Audit', '',
         'Exact daily-NAV simulation for the four finalist factor/universe pairs. Each sleeve holds 20 equal-weight names and rebalances every 10 trading days, with 10 staggered phases. Costs are charged on one-way turnover as turnover × 30bp or 60bp.', '',
         '## 2016-2024 median across 10 phases', '']
    q = summary[summary.period == 'PRE_STRESS_2016_2024']
    for u, f in FINALISTS:
        L.append(f'### {u} × {f}')
        for s in STRATEGIES:
            for rt in ('GROSS', 'NET30', 'NET60'):
                x = q[(q.universe == u) & (q.factor == f) & (q.strategy == s) & (q.return_type == rt)]
                if x.empty:
                    continue
                r = x.iloc[0]
                L.append(f"- {s} {rt}: CAGR {r.median_cagr:+.2%}; Sharpe {r.median_sharpe:.2f}; MDD {r.median_mdd:+.1%}; worst-phase MDD {r.worst_phase_mdd:+.1%}; turnover {r.median_annual_turnover:.2f}x/yr")
        d = deltas[(deltas.universe == u) & (deltas.factor == f) & (deltas.period == 'PRE_STRESS_2016_2024')]
        for rt in ('GROSS', 'NET30', 'NET60'):
            x = d[d.return_type == rt]
            if x.empty:
                continue
            r = x.iloc[0]
            L.append(f"- CF20 incremental {rt}: median dCAGR {r.median_delta_cagr:+.2%}; CAGR wins {int(r.cagr_win_phases)}/{int(r.n_phases)}; dSharpe {r.median_delta_sharpe:+.2f}; MDD improves {int(r.mdd_improve_phases)}/{int(r.n_phases)}")
        L.append('')

    L += ['## Recent diagnostics', '']
    for period in ('NORMAL_2023_2024', 'BULL_2025', 'YTD_2026'):
        L.append(f'### {period}')
        z = summary[(summary.period == period) & (summary.return_type == 'NET30')]
        for u, f in FINALISTS:
            for s in STRATEGIES:
                x = z[(z.universe == u) & (z.factor == f) & (z.strategy == s)]
                if x.empty:
                    continue
                r = x.iloc[0]
                L.append(f"- {u} × {f} {s}: CAGR {r.median_cagr:+.2%}; Sharpe {r.median_sharpe:.2f}; MDD {r.median_mdd:+.1%}; positive phases {int(r.positive_phases)}/{int(r.n_phases)}")
        L.append('')
    return '\n'.join(L)


def main():
    returns, mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}

    targets, phase_map = build_targets(returns, k200, markets, files)
    frames = []
    for (u, f, s), by_date in targets.items():
        for phase in range(H):
            x = simulate_one(returns, by_date, phase, phase_map, u, f, s)
            if len(x):
                frames.append(x)
    daily = pd.concat(frames, ignore_index=True)
    daily.to_csv(OUT / 'daily_returns.csv', index=False)
    perf = performance(daily)
    summary, deltas = summarize(perf)
    report = make_report(summary, deltas)
    (OUT / 'FINALIST_AUDIT.md').write_text(report, encoding='utf-8')
    print(report)
    print(f'daily_rows={len(daily):,}; perf_rows={len(perf):,}')


if __name__ == '__main__':
    main()
