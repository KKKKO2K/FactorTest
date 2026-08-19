from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DAILY_PATH = ROOT / 'research' / 'stock_level_factor_interaction' / 'results_factor_level_finalists' / 'daily_returns_text' / 'MIXED_OPFY1_CF20.csv'
EVENT_PATH = ROOT / 'research' / 'factor_regime_action_policy' / 'results' / 'finalist_regime_overlay' / 'overlay_signal_events.csv'
OUT = ROOT / 'research' / 'factor_regime_action_policy' / 'results' / 'finalist_regime_execution'
OUT.mkdir(parents=True, exist_ok=True)

PERIODS = {
    'TRAIN_2016_2022': ('2016-01-01', '2022-12-31'),
    'OOS_2023_2024': ('2023-01-01', '2024-12-31'),
    'PRE_STRESS_2016_2024': ('2016-01-01', '2024-12-31'),
    'BULL_2025': ('2025-01-01', '2025-12-31'),
    'YTD_2026': ('2026-01-01', '2099-12-31'),
}

POLICIES = (
    'ALWAYS_100',
    'F_LOW_HALF_REBAL10',
    'FB20_HIGH_HALF_REBAL10',
    'CRASH_GUARD_REBAL10',
    'FB20_HALF_REBAL10_CRASH_IMMEDIATE',
)


def cagr(r: pd.Series) -> float:
    r = r.dropna()
    if len(r) < 2:
        return np.nan
    total = float((1.0 + r).prod())
    years = len(r) / 252.0
    return total ** (1.0 / years) - 1.0 if total > 0 else np.nan


def sharpe(r: pd.Series) -> float:
    r = r.dropna()
    if len(r) < 3:
        return np.nan
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(252.0)) if pd.notna(sd) and sd > 0 else np.nan


def mdd(r: pd.Series) -> float:
    r = r.dropna()
    if r.empty:
        return np.nan
    nav = (1.0 + r).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    d = pd.read_csv(DAILY_PATH)
    d['date'] = pd.to_datetime(d['date'])
    d = d.sort_values(['phase', 'date'])
    e = pd.read_csv(EVENT_PATH)
    e['date'] = pd.to_datetime(e['date'])
    e = e.sort_values('date').drop_duplicates('date', keep='last')
    e['F_LOW_TARGET'] = np.where(e['factor_substate'].eq('F_LOW'), 0.5, 1.0)
    e['FB20_TARGET'] = np.where(e['breadth_high'].eq(1), 0.5, 1.0)
    e['CRASH_TARGET'] = np.where(e['crash_guard'].eq(1), 0.0, 1.0)
    return d, e


def simulate_rebal10(g: pd.DataFrame, e: pd.DataFrame, target_col: str, ret_col: str, bps: int, policy: str) -> pd.DataFrame:
    g = g.sort_values('date')
    ev_dates = e['date'].tolist()
    target_map = e.set_index('date')[target_col].to_dict()
    event_idx = 0
    desired = 1.0
    risky, cash = 1.0, 0.0
    target_exposure = 1.0
    rows = []

    for row in g.itertuples(index=False):
        dt = row.date
        nav_start = risky + cash
        risky_weight_start = risky / nav_start if nav_start > 0 else 0.0
        risky *= 1.0 + float(getattr(row, ret_col))
        nav_pre = risky + cash

        while event_idx < len(ev_dates) and ev_dates[event_idx] <= dt:
            desired = float(target_map[ev_dates[event_idx]])
            event_idx += 1

        internal_turnover = risky_weight_start * float(row.turnover)
        alloc_turnover = 0.0
        if int(row.rebalanced) == 1:
            current_weight = risky / nav_pre if nav_pre > 0 else 0.0
            alloc_turnover = abs(desired - current_weight)
            nav_after = nav_pre * (1.0 - alloc_turnover * bps / 10000.0)
            risky = desired * nav_after
            cash = (1.0 - desired) * nav_after
            target_exposure = desired

        nav_end = risky + cash
        rows.append({
            'date': dt,
            'phase': int(row.phase),
            'policy': policy,
            'return_type': 'GROSS' if ret_col == 'gross_ret' else f'NET{bps}',
            'daily_ret': nav_end / nav_start - 1.0,
            'target_exposure': target_exposure,
            'internal_turnover': internal_turnover,
            'allocation_turnover': alloc_turnover,
            'total_turnover': internal_turnover + alloc_turnover,
        })
    return pd.DataFrame(rows)


def simulate_hybrid(g: pd.DataFrame, e: pd.DataFrame, ret_col: str, bps: int) -> pd.DataFrame:
    g = g.sort_values('date')
    ev_dates = e['date'].tolist()
    ev = e.set_index('date')
    event_idx = 0
    breadth_desired = 1.0
    crash_on = False
    risky, cash = 1.0, 0.0
    target_exposure = 1.0
    rows = []

    for row in g.itertuples(index=False):
        dt = row.date
        nav_start = risky + cash
        risky_weight_start = risky / nav_start if nav_start > 0 else 0.0
        risky *= 1.0 + float(getattr(row, ret_col))
        nav_pre = risky + cash

        new_crash = crash_on
        saw_event = False
        while event_idx < len(ev_dates) and ev_dates[event_idx] <= dt:
            z = ev.loc[ev_dates[event_idx]]
            breadth_desired = float(z.FB20_TARGET)
            new_crash = bool(z.crash_guard == 1)
            saw_event = True
            event_idx += 1

        desired = target_exposure
        immediate_crash = saw_event and new_crash and not crash_on
        crash_on = new_crash
        if crash_on:
            desired = 0.0
        elif int(row.rebalanced) == 1:
            desired = breadth_desired

        internal_turnover = risky_weight_start * float(row.turnover)
        alloc_turnover = 0.0
        if immediate_crash or (int(row.rebalanced) == 1 and desired != target_exposure):
            current_weight = risky / nav_pre if nav_pre > 0 else 0.0
            alloc_turnover = abs(desired - current_weight)
            nav_after = nav_pre * (1.0 - alloc_turnover * bps / 10000.0)
            risky = desired * nav_after
            cash = (1.0 - desired) * nav_after
            target_exposure = desired
        elif int(row.rebalanced) == 1 and not crash_on:
            # Refresh the intended risky/cash weight on the existing stock rebalance day.
            current_weight = risky / nav_pre if nav_pre > 0 else 0.0
            alloc_turnover = abs(desired - current_weight)
            nav_after = nav_pre * (1.0 - alloc_turnover * bps / 10000.0)
            risky = desired * nav_after
            cash = (1.0 - desired) * nav_after
            target_exposure = desired

        nav_end = risky + cash
        rows.append({
            'date': dt,
            'phase': int(row.phase),
            'policy': 'FB20_HALF_REBAL10_CRASH_IMMEDIATE',
            'return_type': 'GROSS' if ret_col == 'gross_ret' else f'NET{bps}',
            'daily_ret': nav_end / nav_start - 1.0,
            'target_exposure': target_exposure,
            'internal_turnover': internal_turnover,
            'allocation_turnover': alloc_turnover,
            'total_turnover': internal_turnover + alloc_turnover,
        })
    return pd.DataFrame(rows)


def always_path(g: pd.DataFrame, ret_col: str, bps: int) -> pd.DataFrame:
    return pd.DataFrame({
        'date': g['date'].values,
        'phase': g['phase'].values,
        'policy': 'ALWAYS_100',
        'return_type': 'GROSS' if ret_col == 'gross_ret' else f'NET{bps}',
        'daily_ret': g[ret_col].values,
        'target_exposure': 1.0,
        'internal_turnover': g['turnover'].values,
        'allocation_turnover': 0.0,
        'total_turnover': g['turnover'].values,
    })


def build_paths(d: pd.DataFrame, e: pd.DataFrame) -> pd.DataFrame:
    frames = []
    specs = [('gross_ret', 0), ('net30_ret', 30), ('net60_ret', 60)]
    for _, g in d.groupby('phase'):
        for ret_col, bps in specs:
            frames.append(always_path(g, ret_col, bps))
            frames.append(simulate_rebal10(g, e, 'F_LOW_TARGET', ret_col, bps, 'F_LOW_HALF_REBAL10'))
            frames.append(simulate_rebal10(g, e, 'FB20_TARGET', ret_col, bps, 'FB20_HIGH_HALF_REBAL10'))
            frames.append(simulate_rebal10(g, e, 'CRASH_TARGET', ret_col, bps, 'CRASH_GUARD_REBAL10'))
            frames.append(simulate_hybrid(g, e, ret_col, bps))
    return pd.concat(frames, ignore_index=True)


def performance(paths: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (policy, phase, rt), g0 in paths.groupby(['policy', 'phase', 'return_type']):
        g0 = g0.sort_values('date')
        for period, (lo, hi) in PERIODS.items():
            g = g0[(g0.date >= lo) & (g0.date <= hi)]
            if len(g) < 40:
                continue
            years = len(g) / 252.0
            rows.append({
                'policy': policy,
                'phase': phase,
                'return_type': rt,
                'period': period,
                'cagr': cagr(g.daily_ret),
                'sharpe': sharpe(g.daily_ret),
                'mdd': mdd(g.daily_ret),
                'annual_turnover': float(g.total_turnover.sum() / years),
                'annual_allocation_turnover': float(g.allocation_turnover.sum() / years),
                'avg_target_exposure': float(g.target_exposure.mean()),
            })
    return pd.DataFrame(rows)


def summary(perf: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for key, g in perf.groupby(['policy', 'return_type', 'period']):
        rows.append({
            'policy': key[0],
            'return_type': key[1],
            'period': key[2],
            'median_cagr': float(g.cagr.median()),
            'median_sharpe': float(g.sharpe.median()),
            'median_mdd': float(g.mdd.median()),
            'median_annual_turnover': float(g.annual_turnover.median()),
            'median_annual_allocation_turnover': float(g.annual_allocation_turnover.median()),
            'median_avg_target_exposure': float(g.avg_target_exposure.median()),
            'positive_cagr_phases': int((g.cagr > 0).sum()),
            'n_phases': int(g.phase.nunique()),
        })
    return pd.DataFrame(rows)


def compare(perf: pd.DataFrame) -> pd.DataFrame:
    b = perf[perf.policy.eq('ALWAYS_100')].set_index(['phase', 'return_type', 'period'])
    rows = []
    for policy in POLICIES:
        if policy == 'ALWAYS_100':
            continue
        x = perf[perf.policy.eq(policy)].set_index(['phase', 'return_type', 'period'])
        detail = []
        for idx in b.index.intersection(x.index):
            rb, rx = b.loc[idx], x.loc[idx]
            detail.append({
                'phase': idx[0], 'return_type': idx[1], 'period': idx[2],
                'dcagr': rx.cagr - rb.cagr,
                'dsharpe': rx.sharpe - rb.sharpe,
                'dmdd': rx.mdd - rb.mdd,
                'dturn': rx.annual_turnover - rb.annual_turnover,
            })
        z = pd.DataFrame(detail)
        for (rt, period), g in z.groupby(['return_type', 'period']):
            rows.append({
                'policy': policy, 'return_type': rt, 'period': period,
                'median_delta_cagr': float(g.dcagr.median()),
                'median_delta_sharpe': float(g.dsharpe.median()),
                'median_delta_mdd': float(g.dmdd.median()),
                'median_delta_turnover': float(g.dturn.median()),
                'better_cagr_phases': int((g.dcagr > 0).sum()),
                'better_mdd_phases': int((g.dmdd > 0).sum()),
                'n_phases': int(g.phase.nunique()),
            })
    return pd.DataFrame(rows)


def pct(x: float) -> str:
    return 'NA' if pd.isna(x) else f'{x:+.2%}'


def report(s: pd.DataFrame, c: pd.DataFrame) -> str:
    lines = [
        '# Mixed OPFY1+CF20 — Rebalance-Aligned Regime Execution Audit', '',
        'This test keeps the regime signal definitions frozen and changes only execution timing.',
        'REBAL10 policies update exposure only on the sleeve own H=10 stock-rebalance dates, using the latest signal available by that close.',
        'The hybrid applies the crash transition to 0% immediately, but applies normal Breadth 100/50 changes only on stock-rebalance dates.',
        'Allocator costs are still charged conservatively at the same 30/60 bps rate on exposure turnover.', '',
    ]
    for period in ('TRAIN_2016_2022', 'OOS_2023_2024', 'BULL_2025', 'YTD_2026'):
        lines += [f'## {period} — NET60', '']
        z = s[(s.period.eq(period)) & (s.return_type.eq('NET60'))]
        for policy in POLICIES:
            x = z[z.policy.eq(policy)]
            if x.empty:
                continue
            r = x.iloc[0]
            lines.append(
                f"- {policy}: CAGR {pct(r.median_cagr)}; Sharpe {r.median_sharpe:.2f}; MDD {pct(r.median_mdd)}; "
                f"turn {r.median_annual_turnover:.2f}x (allocator {r.median_annual_allocation_turnover:.2f}x); "
                f"avg target {r.median_avg_target_exposure:.1%}; pos phases {int(r.positive_cagr_phases)}/{int(r.n_phases)}"
            )
        lines.append('')

    lines += ['## Incremental vs ALWAYS_100 — NET60', '']
    for period in ('TRAIN_2016_2022', 'OOS_2023_2024', 'BULL_2025', 'YTD_2026'):
        lines.append(f'### {period}')
        z = c[(c.period.eq(period)) & (c.return_type.eq('NET60'))]
        for policy in POLICIES:
            if policy == 'ALWAYS_100':
                continue
            x = z[z.policy.eq(policy)]
            if x.empty:
                continue
            r = x.iloc[0]
            lines.append(
                f"- {policy}: dCAGR {pct(r.median_delta_cagr)}, dSharpe {r.median_delta_sharpe:+.2f}, "
                f"dMDD {pct(r.median_delta_mdd)}, dTurn {r.median_delta_turnover:+.2f}x; "
                f"better CAGR {int(r.better_cagr_phases)}/{int(r.n_phases)}, better MDD {int(r.better_mdd_phases)}/{int(r.n_phases)}"
            )
        lines.append('')
    return '\n'.join(lines)


def main() -> None:
    d, e = load()
    paths = build_paths(d, e)
    perf = performance(paths)
    s = summary(perf)
    c = compare(perf)
    perf.to_csv(OUT / 'execution_phase_performance.csv', index=False, encoding='utf-8', lineterminator='\n')
    s.to_csv(OUT / 'execution_summary.csv', index=False, encoding='utf-8', lineterminator='\n')
    c.to_csv(OUT / 'execution_vs_always.csv', index=False, encoding='utf-8', lineterminator='\n')
    text = report(s, c)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
