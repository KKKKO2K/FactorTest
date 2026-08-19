from __future__ import annotations

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
import audit_cf20_portfolio_tieout as audit
from chunked_csv import write_chunked_csv

OUT = Path(__file__).resolve().parent / 'results_factor_level_finalists'
OUT.mkdir(parents=True, exist_ok=True)
CONNECTOR_EXPORT_DIR = OUT / 'daily_returns_text'

H = audit.H
TOPN = audit.TOPN
PERIODS = audit.PERIODS
COSTS_BPS = (0, 30, 60)

MIXED = 'KOSDAQ_PLUS_KOSPI_EX_K200'

# Include BASE/CF20 pairs where the overlay itself is under evaluation.
VARIANTS = (
    {'variant': 'KOSPI_ALL_PER_BASE', 'universe': 'KOSPI_ALL', 'strategy': 'PRIMARY8', 'factor': 'PER12MF'},
    {'variant': 'KOSPI_ALL_PER_CF20', 'universe': 'KOSPI_ALL', 'strategy': 'CF20', 'factor': 'PER12MF'},
    {'variant': 'KOSPI_ALL_PRIVATE_FLOW_BASE', 'universe': 'KOSPI_ALL', 'strategy': 'PRIMARY8', 'factor': 'PRIVATE_FLOW'},
    {'variant': 'MIXED_PER_BASE', 'universe': MIXED, 'strategy': 'PRIMARY8', 'factor': 'PER12MF'},
    {'variant': 'MIXED_PER_CF20', 'universe': MIXED, 'strategy': 'CF20', 'factor': 'PER12MF'},
    {'variant': 'MIXED_OPFY1_BASE', 'universe': MIXED, 'strategy': 'PRIMARY8', 'factor': 'OPFY1_REV'},
    {'variant': 'MIXED_OPFY1_CF20', 'universe': MIXED, 'strategy': 'CF20', 'factor': 'OPFY1_REV'},
)

PAIR_MAP = (
    ('KOSPI_ALL_PER', 'KOSPI_ALL_PER_BASE', 'KOSPI_ALL_PER_CF20'),
    ('MIXED_PER', 'MIXED_PER_BASE', 'MIXED_PER_CF20'),
    ('MIXED_OPFY1', 'MIXED_OPFY1_BASE', 'MIXED_OPFY1_CF20'),
)


def equal_weight_target(names: list[str]) -> pd.Series:
    if len(names) != TOPN:
        raise ValueError(f'Expected {TOPN} names, got {len(names)}')
    return pd.Series(1.0 / TOPN, index=pd.Index(names), dtype=float).sort_index()


def extract_factor_targets(sleeve_store, universe: str, strategy: str, factor: str) -> dict[pd.Timestamp, pd.Series]:
    out: dict[pd.Timestamp, pd.Series] = {}
    for dt, by_factor in sleeve_store[universe][strategy].items():
        names = by_factor.get(factor)
        if names is None or len(names) != TOPN:
            continue
        out[dt] = equal_weight_target(names)
    return out


def simulate_factor_one(returns, targets, phase, phase_map, meta):
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
                turnover = float(
                    0.5 * (
                        current.reindex(union, fill_value=0.0)
                        - target.reindex(union, fill_value=0.0)
                    ).abs().sum()
                )
            else:
                turnover = 1.0
            current = target.copy()
            rebalanced = 1

        rec = {
            'date': dt,
            'variant': meta['variant'],
            'universe': meta['universe'],
            'strategy': meta['strategy'],
            'factor': meta['factor'],
            'phase': phase,
            'gross_ret': gross,
            'turnover': turnover,
            'rebalanced': rebalanced,
            'missing_weight': missing_weight,
        }
        for bps in (30, 60):
            cost = turnover * bps / 10000.0
            rec[f'net{bps}_ret'] = (1.0 + gross) * (1.0 - cost) - 1.0
        rows.append(rec)
    return pd.DataFrame(rows)


def write_connector_friendly_daily_exports(daily: pd.DataFrame) -> pd.DataFrame:
    """Write small, plain UTF-8 CSV slices alongside the archival gzip output."""
    CONNECTOR_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    for meta in VARIANTS:
        variant = meta['variant']
        x = daily[daily['variant'].eq(variant)].sort_values(['date', 'phase']).copy()
        if x.empty:
            raise RuntimeError(f'No daily rows for connector export: {variant}')
        path = CONNECTOR_EXPORT_DIR / f'{variant}.csv'
        x.to_csv(path, index=False, encoding='utf-8', lineterminator='\n')
        manifest_rows.append({
            'variant': variant,
            'file': path.name,
            'rows': len(x),
            'date_start': x['date'].min().date().isoformat(),
            'date_end': x['date'].max().date().isoformat(),
            'phases': int(x['phase'].nunique()),
        })

    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(
        CONNECTOR_EXPORT_DIR / 'manifest.csv',
        index=False,
        encoding='utf-8',
        lineterminator='\n',
    )
    return manifest


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


def performance_stats(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    ret_cols = [('gross_ret', 'GROSS'), ('net30_ret', 'NET30'), ('net60_ret', 'NET60')]
    for (variant, phase), g0 in daily.groupby(['variant', 'phase']):
        g0 = g0.sort_values('date')
        meta = g0.iloc[0]
        for period, (lo, hi) in PERIODS.items():
            g = g0[(g0.date >= lo) & (g0.date <= hi)]
            if len(g) < 40:
                continue
            years = len(g) / 252.0
            annual_turnover = float(g.turnover.sum() / years) if years > 0 else np.nan
            for col, label in ret_cols:
                r = g[col].dropna()
                rows.append({
                    'variant': variant,
                    'universe': meta.universe,
                    'strategy': meta.strategy,
                    'factor': meta.factor,
                    'phase': phase,
                    'period': period,
                    'return_type': label,
                    'n_days': len(r),
                    'cagr': cagr(r),
                    'sharpe': sharpe(r),
                    'mdd': mdd(r),
                    'calmar': cagr(r) / abs(mdd(r)) if mdd(r) < 0 else np.nan,
                    'annual_turnover': annual_turnover,
                    'avg_missing_weight': float(g.missing_weight.mean()),
                    'n_rebalances': int(g.rebalanced.sum()),
                })
    return pd.DataFrame(rows)


def summarize(perf: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = ['variant', 'universe', 'strategy', 'factor', 'period', 'return_type']
    for key, g in perf.groupby(keys):
        rec = dict(zip(keys, key))
        rec.update({
            'median_cagr': float(g.cagr.median()),
            'median_sharpe': float(g.sharpe.median()),
            'median_mdd': float(g.mdd.median()),
            'median_calmar': float(g.calmar.median()),
            'median_annual_turnover': float(g.annual_turnover.median()),
            'min_cagr': float(g.cagr.min()),
            'max_cagr': float(g.cagr.max()),
            'positive_cagr_phases': int((g.cagr > 0).sum()),
            'n_phases': int(g.phase.nunique()),
        })
        rows.append(rec)
    return pd.DataFrame(rows)


def overlay_comparison(perf: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    detail = []
    summary = []
    idx = ['phase', 'period', 'return_type']
    for pair, base_name, cf_name in PAIR_MAP:
        b = perf[perf.variant == base_name].set_index(idx)
        c = perf[perf.variant == cf_name].set_index(idx)
        common = b.index.intersection(c.index)
        for k in common:
            rb = b.loc[k]
            rc = c.loc[k]
            detail.append({
                'pair': pair,
                'phase': k[0],
                'period': k[1],
                'return_type': k[2],
                'base_cagr': rb.cagr,
                'cf20_cagr': rc.cagr,
                'delta_cagr': rc.cagr - rb.cagr,
                'base_sharpe': rb.sharpe,
                'cf20_sharpe': rc.sharpe,
                'delta_sharpe': rc.sharpe - rb.sharpe,
                'base_mdd': rb.mdd,
                'cf20_mdd': rc.mdd,
                'delta_mdd': rc.mdd - rb.mdd,
                'base_turnover': rb.annual_turnover,
                'cf20_turnover': rc.annual_turnover,
                'delta_turnover': rc.annual_turnover - rb.annual_turnover,
            })
    d = pd.DataFrame(detail)
    for (pair, period, return_type), g in d.groupby(['pair', 'period', 'return_type']):
        summary.append({
            'pair': pair,
            'period': period,
            'return_type': return_type,
            'median_delta_cagr': float(g.delta_cagr.median()),
            'median_delta_sharpe': float(g.delta_sharpe.median()),
            'median_delta_mdd': float(g.delta_mdd.median()),
            'median_delta_turnover': float(g.delta_turnover.median()),
            'better_cagr_phases': int((g.delta_cagr > 0).sum()),
            'better_sharpe_phases': int((g.delta_sharpe > 0).sum()),
            'better_mdd_phases': int((g.delta_mdd > 0).sum()),
            'n_phases': int(g.phase.nunique()),
        })
    return d, pd.DataFrame(summary)


def fmt_pct(x):
    return 'NA' if pd.isna(x) else f'{x:+.2%}'


def fmt_num(x):
    return 'NA' if pd.isna(x) else f'{x:.2f}'


def make_report(summary: pd.DataFrame, overlay: pd.DataFrame) -> str:
    lines = [
        '# Factor-Level Finalist Daily-NAV Audit',
        '',
        'Daily implementation matches the existing CF20 audit convention: positions selected on rebalance date are held from the next trading day; missing stock returns are zero-filled while the position remains held; one-way turnover is 0.5 * sum(abs(current-target)); costs are charged on rebalance turnover.',
        '',
        'Finalist variants include BASE/CF20 pairs for PER and OPFY1 so overlay attribution remains explicit. PRIVATE_FLOW is tested as BASE only.',
        '',
        '## 2016-2024 median across 10 phases',
        '',
    ]
    q = summary[summary.period == 'PRE_STRESS_2016_2024']
    for variant in [v['variant'] for v in VARIANTS]:
        lines.append(f'### {variant}')
        for rt in ('GROSS', 'NET30', 'NET60'):
            x = q[(q.variant == variant) & (q.return_type == rt)]
            if x.empty:
                continue
            r = x.iloc[0]
            lines.append(
                f"- {rt}: CAGR {fmt_pct(r.median_cagr)}; Sharpe {fmt_num(r.median_sharpe)}; "
                f"MDD {fmt_pct(r.median_mdd)}; Calmar {fmt_num(r.median_calmar)}; "
                f"annual turnover {r.median_annual_turnover:.2f}x; positive phases {int(r.positive_cagr_phases)}/{int(r.n_phases)}"
            )
        lines.append('')

    lines += ['## CF20 incremental — 2016-2024', '']
    z = overlay[overlay.period == 'PRE_STRESS_2016_2024']
    for pair in [p[0] for p in PAIR_MAP]:
        lines.append(f'### {pair}')
        for rt in ('GROSS', 'NET30', 'NET60'):
            x = z[(z.pair == pair) & (z.return_type == rt)]
            if x.empty:
                continue
            r = x.iloc[0]
            lines.append(
                f"- {rt}: median dCAGR {fmt_pct(r.median_delta_cagr)}; dSharpe {r.median_delta_sharpe:+.2f}; "
                f"dMDD {fmt_pct(r.median_delta_mdd)}; dTurnover {r.median_delta_turnover:+.2f}x; "
                f"better CAGR phases {int(r.better_cagr_phases)}/{int(r.n_phases)}"
            )
        lines.append('')

    lines += ['## 2026 YTD stress diagnostic — NET60', '']
    y = summary[(summary.period == 'YTD_2026') & (summary.return_type == 'NET60')]
    for variant in [v['variant'] for v in VARIANTS]:
        x = y[y.variant == variant]
        if x.empty:
            continue
        r = x.iloc[0]
        lines.append(
            f"- {variant}: CAGR {fmt_pct(r.median_cagr)}; Sharpe {fmt_num(r.median_sharpe)}; "
            f"MDD {fmt_pct(r.median_mdd)}; positive phases {int(r.positive_cagr_phases)}/{int(r.n_phases)}"
        )
    lines += [
        '',
        '## Guardrails',
        '',
        '- 2023+ is a robustness/stress slice, not a clean untouched OOS confirmation, because later data informed earlier research iterations.',
        '- NET30/NET60 are turnover-proportional implementation-cost scenarios, not a full market-impact model.',
        '- MDD here is true daily-NAV MDD for each factor sleeve, not the prior aggregate 8-sleeve portfolio MDD.',
        '- Final production confirmation should still use frozen-rule/walk-forward logic per RESEARCH_ARCHITECTURE_V2.md.',
        '',
    ]
    return '\n'.join(lines)


def main():
    returns, _mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}

    _store, sleeve_store, _common, phase_map, _common_pos = audit.build_targets(
        returns, k200, markets, files
    )

    frames = []
    for meta in VARIANTS:
        targets = extract_factor_targets(
            sleeve_store, meta['universe'], meta['strategy'], meta['factor']
        )
        if not targets:
            raise RuntimeError(f"No targets for {meta['variant']}")
        for phase in range(H):
            x = simulate_factor_one(returns, targets, phase, phase_map, meta)
            if len(x):
                frames.append(x)

    daily = pd.concat(frames, ignore_index=True)
    daily['date'] = pd.to_datetime(daily['date'])
    write_chunked_csv(daily, OUT / 'finalist_daily_returns.csv', index=False, target_mb=40)
    connector_manifest = write_connector_friendly_daily_exports(daily)

    perf = performance_stats(daily)
    perf.to_csv(OUT / 'finalist_phase_performance.csv', index=False)
    summary = summarize(perf)
    summary.to_csv(OUT / 'finalist_summary.csv', index=False)

    overlay_detail, overlay_summary = overlay_comparison(perf)
    overlay_detail.to_csv(OUT / 'cf20_overlay_phase_detail.csv', index=False)
    overlay_summary.to_csv(OUT / 'cf20_overlay_summary.csv', index=False)

    report = make_report(summary, overlay_summary)
    (OUT / 'FINALIST_SUMMARY.md').write_text(report, encoding='utf-8')
    print(report)
    print(
        f'daily_rows={len(daily):,}; connector_files={len(connector_manifest):,}; '
        f'perf_rows={len(perf):,}; summary_rows={len(summary):,}; '
        f'overlay_rows={len(overlay_summary):,}'
    )


if __name__ == '__main__':
    main()
