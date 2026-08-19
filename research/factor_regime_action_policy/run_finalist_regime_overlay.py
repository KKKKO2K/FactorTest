from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FINALIST_DIR = ROOT / 'research' / 'stock_level_factor_interaction' / 'results_factor_level_finalists'
REGIME_V1_DIR = ROOT / 'research' / 'factor_regime_v1' / 'results'
ACTION_DIR = ROOT / 'research' / 'factor_regime_action_policy' / 'results'
OUT = ACTION_DIR / 'finalist_regime_overlay'
OUT.mkdir(parents=True, exist_ok=True)

MIXED = 'KOSDAQ_PLUS_KOSPI_EX_K200'
VARIANT = 'MIXED_OPFY1_CF20'
TRAIN_END = pd.Timestamp('2023-01-01')

PERIODS = {
    'TRAIN_2016_2022': (pd.Timestamp('2016-01-01'), pd.Timestamp('2022-12-31')),
    'OOS_2023_2024': (pd.Timestamp('2023-01-01'), pd.Timestamp('2024-12-31')),
    'PRE_STRESS_2016_2024': (pd.Timestamp('2016-01-01'), pd.Timestamp('2024-12-31')),
    'BULL_2025': (pd.Timestamp('2025-01-01'), pd.Timestamp('2025-12-31')),
    'YTD_2026': (pd.Timestamp('2026-01-01'), pd.Timestamp('2099-12-31')),
}

POLICIES = (
    'ALWAYS_100',
    'F_LOW_HALF',
    'FB20_HIGH_HALF',
    'CRASH_GUARD_ONLY',
    'FB20_HALF_PLUS_CRASH0',
)


def cagr(r: pd.Series) -> float:
    r = pd.Series(r).dropna()
    if len(r) < 2:
        return np.nan
    total = float((1.0 + r).prod())
    years = len(r) / 252.0
    return total ** (1.0 / years) - 1.0 if total > 0 and years > 0 else np.nan


def sharpe(r: pd.Series) -> float:
    r = pd.Series(r).dropna()
    if len(r) < 3:
        return np.nan
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(252.0)) if pd.notna(sd) and sd > 0 else np.nan


def mdd(r: pd.Series) -> float:
    r = pd.Series(r).dropna()
    if r.empty:
        return np.nan
    nav = (1.0 + r).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def robust_thresholds(x: pd.Series) -> tuple[float, float]:
    x = x.dropna()
    uniq = np.sort(x.unique())
    if len(x) < 30 or len(uniq) < 3:
        raise RuntimeError('Insufficient TRAIN observations for factor-breadth thresholds')
    q1, q2 = x.quantile([1 / 3, 2 / 3]).tolist()
    if np.isfinite(q1) and np.isfinite(q2) and q1 < q2:
        return float(q1), float(q2)
    i1 = min(len(uniq) - 2, max(0, int(math.floor((len(uniq) - 1) / 3))))
    i2 = max(i1 + 1, min(len(uniq) - 1, int(math.ceil(2 * (len(uniq) - 1) / 3))))
    if uniq[i1] >= uniq[i2]:
        raise RuntimeError('Unable to create distinct factor-breadth thresholds')
    return float(uniq[i1]), float(uniq[i2])


def load_factor_breadth() -> tuple[pd.DataFrame, float, float]:
    f = pd.read_csv(REGIME_V1_DIR / 'factor_5d_returns.csv')
    f['date'] = pd.to_datetime(f['date'])
    f = f[f['universe'].eq(MIXED)].copy()
    ls = f.pivot(index='date', columns='factor', values='ls_return').sort_index()
    comp = (1.0 + ls).rolling(4, min_periods=4).apply(np.prod, raw=True) - 1.0
    valid = comp.notna().sum(axis=1)
    breadth = (comp > 0).sum(axis=1) / valid.replace(0, np.nan)
    z = pd.DataFrame({'date': breadth.index, 'factor_breadth_20d': breadth.values, 'n_factors_20d': valid.values})
    z = z[(z['n_factors_20d'] >= 5) & z['factor_breadth_20d'].notna()].copy()
    q1, q2 = robust_thresholds(z.loc[z['date'] < TRAIN_END, 'factor_breadth_20d'])
    z['breadth_bin'] = np.where(
        z['factor_breadth_20d'] <= q1,
        'LOW',
        np.where(z['factor_breadth_20d'] >= q2, 'HIGH', 'MID'),
    )
    return z, q1, q2


def load_action_states() -> pd.DataFrame:
    s = pd.read_csv(ACTION_DIR / 'action_state_panel.csv')
    s['date'] = pd.to_datetime(s['date'])
    s = s[s['universe'].eq(MIXED)][
        ['date', 'base_state', 'factor_substate', 'REVISION_state']
    ].sort_values('date').drop_duplicates('date', keep='last')
    return s


def build_events() -> tuple[pd.DataFrame, float, float]:
    b, q1, q2 = load_factor_breadth()
    s = load_action_states()
    dates = pd.DataFrame({'date': sorted(set(b['date']).union(set(s['date'])))})
    events = pd.merge_asof(dates, b.sort_values('date'), on='date', direction='backward')
    events = pd.merge_asof(events, s.sort_values('date'), on='date', direction='backward')

    high = events['factor_breadth_20d'].ge(q2).fillna(False)
    flow = events['factor_substate'].eq('F_LOW').fillna(False)
    crash = (
        events['base_state'].isin(['B1', 'B2'])
        & events['REVISION_state'].isin(['W-', 'R-'])
    )

    events['ALWAYS_100'] = 1.0
    events['F_LOW_HALF'] = np.where(flow, 0.5, 1.0)
    events['FB20_HIGH_HALF'] = np.where(high, 0.5, 1.0)
    events['CRASH_GUARD_ONLY'] = np.where(crash, 0.0, 1.0)
    events['FB20_HALF_PLUS_CRASH0'] = np.where(crash, 0.0, np.where(high, 0.5, 1.0))
    events['breadth_high'] = high.astype(int)
    events['crash_guard'] = crash.astype(int)
    return events, q1, q2


def load_daily() -> pd.DataFrame:
    path = FINALIST_DIR / 'daily_returns_text' / f'{VARIANT}.csv'
    if not path.exists():
        raise FileNotFoundError(f'Missing connector-friendly daily export: {path}')
    d = pd.read_csv(path)
    d['date'] = pd.to_datetime(d['date'])
    return d.sort_values(['phase', 'date']).reset_index(drop=True)


def simulate_allocator(g: pd.DataFrame, events: pd.DataFrame, policy: str, return_col: str, bps: int) -> pd.DataFrame:
    g = g.sort_values('date').copy()
    ev = events[['date', policy]].sort_values('date').copy()
    event_dates = set(ev['date'])
    target_map = ev.set_index('date')[policy].to_dict()

    risky = 1.0
    cash = 0.0
    current_target = 1.0
    event_idx = 0
    ev_dates = ev['date'].tolist()
    rows = []

    for row in g.itertuples(index=False):
        dt = row.date
        nav_start = risky + cash
        risky_weight_start = risky / nav_start if nav_start > 0 else 0.0
        sleeve_ret = float(getattr(row, return_col))

        # The risky sleeve realizes today's return first. Signals dated today are
        # contemporaneous and only change the allocation after today's close,
        # therefore affecting the next trading day's return.
        risky *= 1.0 + sleeve_ret
        nav_pre_alloc = risky + cash

        internal_turnover = risky_weight_start * float(row.turnover)
        alloc_turnover = 0.0
        signal_rebalance = 0

        # Apply every signal event up through this trading date. Normally dates
        # coincide; the while-loop also handles a signal falling between rows.
        latest_target = current_target
        saw_event = False
        while event_idx < len(ev_dates) and ev_dates[event_idx] <= dt:
            latest_target = float(target_map[ev_dates[event_idx]])
            saw_event = True
            event_idx += 1

        if saw_event:
            current_weight = risky / nav_pre_alloc if nav_pre_alloc > 0 else 0.0
            alloc_turnover = abs(latest_target - current_weight)
            cost_rate = alloc_turnover * bps / 10000.0
            nav_after_cost = nav_pre_alloc * (1.0 - cost_rate)
            risky = latest_target * nav_after_cost
            cash = (1.0 - latest_target) * nav_after_cost
            current_target = latest_target
            signal_rebalance = 1

        nav_end = risky + cash
        rows.append({
            'date': dt,
            'policy': policy,
            'phase': int(row.phase),
            'return_type': 'GROSS' if return_col == 'gross_ret' else f'NET{bps}',
            'daily_ret': nav_end / nav_start - 1.0 if nav_start > 0 else np.nan,
            'nav': nav_end,
            'target_exposure': current_target,
            'risky_weight_start': risky_weight_start,
            'internal_turnover': internal_turnover,
            'allocation_turnover': alloc_turnover,
            'total_turnover': internal_turnover + alloc_turnover,
            'signal_rebalance': signal_rebalance,
        })
    return pd.DataFrame(rows)


def run_paths(daily: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    frames = []
    specs = [('gross_ret', 0), ('net30_ret', 30), ('net60_ret', 60)]
    for phase, g in daily.groupby('phase'):
        for policy in POLICIES:
            for col, bps in specs:
                frames.append(simulate_allocator(g, events, policy, col, bps))
    return pd.concat(frames, ignore_index=True)


def performance(paths: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (policy, phase, rt), g0 in paths.groupby(['policy', 'phase', 'return_type']):
        g0 = g0.sort_values('date')
        for period, (lo, hi) in PERIODS.items():
            g = g0[(g0['date'] >= lo) & (g0['date'] <= hi)].copy()
            if len(g) < 40:
                continue
            r = g['daily_ret']
            years = len(g) / 252.0
            rows.append({
                'policy': policy,
                'phase': phase,
                'return_type': rt,
                'period': period,
                'n_days': len(g),
                'cagr': cagr(r),
                'sharpe': sharpe(r),
                'mdd': mdd(r),
                'annual_turnover': float(g['total_turnover'].sum() / years),
                'annual_allocation_turnover': float(g['allocation_turnover'].sum() / years),
                'avg_target_exposure': float(g['target_exposure'].mean()),
                'share_half_or_less': float((g['target_exposure'] <= 0.5).mean()),
                'share_zero': float((g['target_exposure'] == 0.0).mean()),
            })
    return pd.DataFrame(rows)


def summarize(perf: pd.DataFrame) -> pd.DataFrame:
    keys = ['policy', 'return_type', 'period']
    rows = []
    for key, g in perf.groupby(keys):
        rec = dict(zip(keys, key))
        rec.update({
            'median_cagr': float(g['cagr'].median()),
            'median_sharpe': float(g['sharpe'].median()),
            'median_mdd': float(g['mdd'].median()),
            'median_annual_turnover': float(g['annual_turnover'].median()),
            'median_annual_allocation_turnover': float(g['annual_allocation_turnover'].median()),
            'median_avg_target_exposure': float(g['avg_target_exposure'].median()),
            'median_share_half_or_less': float(g['share_half_or_less'].median()),
            'median_share_zero': float(g['share_zero'].median()),
            'positive_cagr_phases': int((g['cagr'] > 0).sum()),
            'n_phases': int(g['phase'].nunique()),
        })
        rows.append(rec)
    return pd.DataFrame(rows)


def comparisons(perf: pd.DataFrame) -> pd.DataFrame:
    base = perf[perf['policy'].eq('ALWAYS_100')].set_index(['phase', 'return_type', 'period'])
    rows = []
    for policy in POLICIES:
        if policy == 'ALWAYS_100':
            continue
        x = perf[perf['policy'].eq(policy)].set_index(['phase', 'return_type', 'period'])
        common = base.index.intersection(x.index)
        detail = []
        for idx in common:
            b = base.loc[idx]
            p = x.loc[idx]
            detail.append({
                'phase': idx[0],
                'return_type': idx[1],
                'period': idx[2],
                'delta_cagr': p.cagr - b.cagr,
                'delta_sharpe': p.sharpe - b.sharpe,
                'delta_mdd': p.mdd - b.mdd,
                'delta_turnover': p.annual_turnover - b.annual_turnover,
            })
        z = pd.DataFrame(detail)
        for (rt, period), g in z.groupby(['return_type', 'period']):
            rows.append({
                'policy': policy,
                'return_type': rt,
                'period': period,
                'median_delta_cagr': float(g.delta_cagr.median()),
                'median_delta_sharpe': float(g.delta_sharpe.median()),
                'median_delta_mdd': float(g.delta_mdd.median()),
                'median_delta_turnover': float(g.delta_turnover.median()),
                'better_cagr_phases': int((g.delta_cagr > 0).sum()),
                'better_mdd_phases': int((g.delta_mdd > 0).sum()),
                'n_phases': int(g.phase.nunique()),
            })
    return pd.DataFrame(rows)


def pct(x: float) -> str:
    return 'NA' if pd.isna(x) else f'{x:+.2%}'


def num(x: float) -> str:
    return 'NA' if pd.isna(x) else f'{x:.2f}'


def make_report(summary: pd.DataFrame, comp: pd.DataFrame, events: pd.DataFrame, q1: float, q2: float) -> str:
    lines = [
        '# Mixed OPFY1+CF20 — Exact Daily-NAV Regime Overlay Audit',
        '',
        f'- Frozen TRAIN factor-breadth thresholds: q1={q1:.3f}, q2={q2:.3f}.',
        '- FACTOR_20D is the fraction of available canonical factor long-short sleeves with positive compounded return over four 5D periods; at least five factors are required.',
        '- A signal dated t is applied after the close of t, so it affects portfolio returns from the next trading day. No forward outcome enters the rule.',
        '- Net30/Net60 use the finalist sleeve net returns and additionally charge the same bps on allocator turnover between the risky sleeve and cash.',
        '- While a target is active, allocation is refreshed on regime signal dates; between signal dates the risky/cash weights are allowed to drift.',
        '',
        'Policies:',
        '- ALWAYS_100: finalist sleeve fully invested.',
        '- F_LOW_HALF: legacy benchmark; 50% when nested factor_substate is F_LOW.',
        '- FB20_HIGH_HALF: 50% when FACTOR_20D >= frozen TRAIN q2.',
        '- CRASH_GUARD_ONLY: 0% only when base state is B1/B2 and Revision family state is W-/R-.',
        '- FB20_HALF_PLUS_CRASH0: Breadth HIGH -> 50%; crash guard overrides to 0%; otherwise 100%.',
        '',
    ]

    for period in ('TRAIN_2016_2022', 'OOS_2023_2024', 'PRE_STRESS_2016_2024', 'BULL_2025', 'YTD_2026'):
        lines += [f'## {period} — median across 10 phases', '']
        z = summary[(summary['period'].eq(period)) & (summary['return_type'].eq('NET60'))]
        for policy in POLICIES:
            x = z[z['policy'].eq(policy)]
            if x.empty:
                continue
            r = x.iloc[0]
            lines.append(
                f"- {policy}: CAGR {pct(r.median_cagr)}; Sharpe {num(r.median_sharpe)}; "
                f"MDD {pct(r.median_mdd)}; turnover {r.median_annual_turnover:.2f}x; "
                f"avg target {r.median_avg_target_exposure:.1%}; positive phases {int(r.positive_cagr_phases)}/{int(r.n_phases)}"
            )
        lines.append('')

    lines += ['## Incremental vs ALWAYS_100 — NET60', '']
    for period in ('TRAIN_2016_2022', 'OOS_2023_2024', 'PRE_STRESS_2016_2024', 'BULL_2025', 'YTD_2026'):
        lines.append(f'### {period}')
        z = comp[(comp['period'].eq(period)) & (comp['return_type'].eq('NET60'))]
        for policy in POLICIES:
            if policy == 'ALWAYS_100':
                continue
            x = z[z['policy'].eq(policy)]
            if x.empty:
                continue
            r = x.iloc[0]
            lines.append(
                f"- {policy}: dCAGR {pct(r.median_delta_cagr)}; dSharpe {r.median_delta_sharpe:+.2f}; "
                f"dMDD {pct(r.median_delta_mdd)}; dTurnover {r.median_delta_turnover:+.2f}x; "
                f"better CAGR {int(r.better_cagr_phases)}/{int(r.n_phases)}, better MDD {int(r.better_mdd_phases)}/{int(r.n_phases)}"
            )
        lines.append('')

    e26 = events[(events['date'] >= '2026-04-01') & (events['date'] <= '2026-06-30')].copy()
    lines += ['## 2026 signal chronology', '']
    for _, r in e26.iterrows():
        if pd.isna(r.factor_breadth_20d):
            continue
        lines.append(
            f"- {r.date.date()}: breadth {r.factor_breadth_20d:.1%} ({r.breadth_bin}); "
            f"B={r.base_state}; Revision={r.REVISION_state}; F={r.factor_substate}; "
            f"FB-half target={r.FB20_HIGH_HALF:.1f}; combined target={r.FB20_HALF_PLUS_CRASH0:.1f}"
        )

    lines += [
        '',
        '## Guardrails',
        '',
        '- 2023+ is robustness/stress evidence rather than pristine untouched OOS because later observations informed prior research iterations.',
        '- The crash guard uses the Revision family state from the frozen nested/action-state panel, not an OPFY1-only state.',
        '- This audit tests the frozen 62.5%-style breadth rule without optimizing persistence, alternative cutoffs, or exposure levels on 2026.',
        '- A production PASS requires improvement that is not concentrated solely in 2026 and that survives Net30/Net60 and phase consistency checks.',
        '',
    ]
    return '\n'.join(lines)


def main() -> None:
    daily = load_daily()
    events, q1, q2 = build_events()
    if not np.isclose(q2, 0.625):
        print(f'WARNING: expected Mixed TRAIN q2 near 0.625, got {q2:.6f}')

    paths = run_paths(daily, events)
    perf = performance(paths)
    summary = summarize(perf)
    comp = comparisons(perf)

    # Keep the full path output connector-friendly but limited to this single finalist.
    paths.to_csv(OUT / 'overlay_daily_paths.csv', index=False, encoding='utf-8', lineterminator='\n')
    perf.to_csv(OUT / 'overlay_phase_performance.csv', index=False, encoding='utf-8', lineterminator='\n')
    summary.to_csv(OUT / 'overlay_summary.csv', index=False, encoding='utf-8', lineterminator='\n')
    comp.to_csv(OUT / 'overlay_vs_always.csv', index=False, encoding='utf-8', lineterminator='\n')
    events.to_csv(OUT / 'overlay_signal_events.csv', index=False, encoding='utf-8', lineterminator='\n')
    events[(events['date'] >= '2026-04-01') & (events['date'] <= '2026-06-30')].to_csv(
        OUT / 'overlay_signal_2026_q2.csv', index=False, encoding='utf-8', lineterminator='\n'
    )

    report = make_report(summary, comp, events, q1, q2)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(report, encoding='utf-8')
    print(report)
    print(
        f'daily_rows={len(daily):,}; event_rows={len(events):,}; path_rows={len(paths):,}; '
        f'perf_rows={len(perf):,}; q1={q1:.6f}; q2={q2:.6f}'
    )


if __name__ == '__main__':
    main()
