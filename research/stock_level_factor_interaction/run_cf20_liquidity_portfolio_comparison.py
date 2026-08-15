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
import run_alt_liquidity_veto_sensitivity as alt
from chunked_csv import write_chunked_csv

OUT = Path(__file__).resolve().parent / 'results_cf20_liquidity_portfolio_comparison'
OUT.mkdir(parents=True, exist_ok=True)

H = 10
TOPN = 20
COSTS_BP = (0, 30, 60)
FACTOR_NAMES = tuple(core.FACTOR_FAMILY)
N_FACTORS = len(FACTOR_NAMES)
UNIVERSES = ('KOSPI_EX_K200', 'KOSDAQ')

# Frozen from the completed stock-level / horizon / phase screens.  No new
# cutoff search is performed in this portfolio stage.
STRATEGIES = {
    'KOSPI_EX_K200': {
        'CF20': None,
        'ACT5_LOW10': ('ACT5', 'LOW10'),
        'ADV20_LOW10': ('ADV20', 'LOW10'),
        'TURNOVER20_TOP01': ('TURNOVER20', 'TOP01'),
        'TURNOVER20_TOP01_LOW10': ('TURNOVER20', 'TOP01_LOW10'),
        'AMIHUD20_TOP05': ('AMIHUD20', 'TOP05'),
    },
    'KOSDAQ': {
        'CF20': None,
        'ACT5_LOW30': ('ACT5', 'LOW30'),
        'TURNOVER20_LOW30': ('TURNOVER20', 'LOW30'),
        'TURNOVER20_TOP01_LOW30': ('TURNOVER20', 'TOP01_LOW30'),
        'ACT1_LOW05': ('ACT1', 'LOW05'),
        'AMIHUD20_TOP05': ('AMIHUD20', 'TOP05'),
    },
}

# Cross-universe 50/50 portfolios.  These are rule families, not ex-post
# optimized combinations.
COMBINED = {
    'CF20_BASE': ('CF20', 'CF20'),
    'ACT5_RULE': ('ACT5_LOW10', 'ACT5_LOW30'),
    'TURNOVER_RULE': ('TURNOVER20_TOP01_LOW10', 'TURNOVER20_TOP01_LOW30'),
    'TURNOVER_SIMPLE_DIAG': ('TURNOVER20_TOP01', 'TURNOVER20_LOW30'),
    'AMIHUD_RULE': ('AMIHUD20_TOP05', 'AMIHUD20_TOP05'),
}

PERIODS = {
    'FULL_2016_2026': (pd.Timestamp('2016-01-01'), pd.Timestamp('2099-12-31')),
    'PRE_STRESS_2016_2024': (pd.Timestamp('2016-01-01'), pd.Timestamp('2024-12-31')),
    'EARLY_2016_2019': (pd.Timestamp('2016-01-01'), pd.Timestamp('2019-12-31')),
    'LATE_2020_2022': (pd.Timestamp('2020-01-01'), pd.Timestamp('2022-12-31')),
    'NORMAL_2023_2024': (pd.Timestamp('2023-01-01'), pd.Timestamp('2024-12-31')),
    'BULL_2025': (pd.Timestamp('2025-01-01'), pd.Timestamp('2025-12-31')),
    'YTD_2026': (pd.Timestamp('2026-01-01'), pd.Timestamp('2099-12-31')),
}


def apply_veto(cf20: pd.Series, rank: pd.Series, rule: str | None) -> pd.Series:
    if rule is None:
        return cf20
    mask = pd.Series(True, index=cf20.index)
    for token in rule.split('_'):
        if token.startswith('TOP'):
            cut = int(token[3:]) / 100.0
            mask &= rank <= 1.0 - cut
        elif token.startswith('LOW'):
            cut = int(token[3:]) / 100.0
            mask &= rank >= cut
        else:
            raise ValueError(rule)
    return cf20.where(mask)


def aggregate_sleeves(sleeve_names: dict[str, list[str]]) -> pd.Series | None:
    if set(sleeve_names) != set(FACTOR_NAMES):
        return None
    w = defaultdict(float)
    sleeve_w = 1.0 / N_FACTORS
    name_w = sleeve_w / TOPN
    for factor in FACTOR_NAMES:
        names = sleeve_names[factor]
        if len(names) != TOPN:
            return None
        for code in names:
            w[code] += name_w
    s = pd.Series(w, dtype=float).sort_index()
    if not np.isclose(s.sum(), 1.0, atol=1e-10):
        raise RuntimeError(f'aggregate target sums to {s.sum()}')
    return s


def build_targets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    returns, mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    ta = base.load_trading_amount()
    liq = alt.build_alt_liquidity(ta, mcap, returns)
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}

    common = sorted(set(returns.index) & set(ta.index) & set(k200) & set(markets))
    common = [d for d in common if d >= base.START]
    phase_map = {d: i % H for i, d in enumerate(common)}

    target_rows: list[dict] = []
    sleeve_rows: list[dict] = []
    quality_rows: list[dict] = []

    for dt in common:
        k = k200[dt]
        market = markets[dt]
        phase = phase_map[dt]

        for universe in UNIVERSES:
            codes = multi.universe_codes(universe, k, market)
            if len(codes) < 120:
                continue
            scores, others = core.build_scores(dt, codes, files)
            if set(scores) != set(FACTOR_NAMES):
                continue

            needed_metrics = sorted({
                spec[0] for spec in STRATEGIES[universe].values() if spec is not None
            })
            ranks: dict[str, pd.Series] = {}
            for metric in needed_metrics:
                v = liq[metric].loc[dt].reindex(codes) if dt in liq[metric].index else pd.Series(index=codes, dtype=float)
                ranks[metric] = pd.to_numeric(v, errors='coerce').rank(pct=True, method='average')

            strat_sleeves: dict[str, dict[str, list[str]]] = {
                s: {} for s in STRATEGIES[universe]
            }
            failed = False
            for factor in FACTOR_NAMES:
                primary = scores[factor]
                cf20 = 0.8 * primary + 0.2 * others[factor]
                for strategy, spec in STRATEGIES[universe].items():
                    if spec is None:
                        score = cf20
                    else:
                        metric, rule = spec
                        score = apply_veto(cf20, ranks[metric], rule)
                    names = core.top_names(score, TOPN)
                    if len(names) != TOPN:
                        failed = True
                        break
                    strat_sleeves[strategy][factor] = names
                if failed:
                    break
            if failed:
                continue

            # Require all frozen candidates to be constructible on the same date,
            # so strategy NAV histories are matched rather than benefiting from
            # different warm-up / missing-data windows.
            aggregate: dict[str, pd.Series] = {}
            for strategy, sleeves in strat_sleeves.items():
                target = aggregate_sleeves(sleeves)
                if target is None:
                    failed = True
                    break
                aggregate[strategy] = target
            if failed:
                continue

            for strategy, target in aggregate.items():
                hhi = float((target ** 2).sum())
                top_weight = float(target.max())
                eff_n = float(1.0 / hhi) if hhi > 0 else np.nan
                quality_rows.append({
                    'date': dt, 'phase': phase, 'universe': universe, 'strategy': strategy,
                    'n_names': int(len(target)), 'hhi': hhi, 'effective_n': eff_n,
                    'top_weight': top_weight,
                })
                for code, weight in target.items():
                    target_rows.append({
                        'date': dt, 'phase': phase, 'universe': universe,
                        'strategy': strategy, 'code': code, 'weight': float(weight),
                    })
                for factor, names in strat_sleeves[strategy].items():
                    for code in names:
                        sleeve_rows.append({
                            'date': dt, 'phase': phase, 'universe': universe,
                            'strategy': strategy, 'factor': factor,
                            'family': core.FACTOR_FAMILY[factor], 'code': code,
                            'sleeve_weight': 1.0 / N_FACTORS / TOPN,
                        })

    targets = pd.DataFrame(target_rows)
    sleeves = pd.DataFrame(sleeve_rows)
    quality = pd.DataFrame(quality_rows)
    write_chunked_csv(targets, OUT / 'targets.csv', index=False, target_mb=40)
    write_chunked_csv(sleeves, OUT / 'sleeve_holdings.csv', index=False, target_mb=40)
    quality.to_csv(OUT / 'target_quality.csv', index=False)
    return targets, returns, quality


def target_dict(targets: pd.DataFrame, universe: str, strategy: str) -> dict[pd.Timestamp, pd.Series]:
    z = targets[(targets.universe == universe) & (targets.strategy == strategy)]
    out: dict[pd.Timestamp, pd.Series] = {}
    for dt, g in z.groupby('date', sort=True):
        s = pd.Series(g.weight.to_numpy(float), index=g.code.astype(str)).groupby(level=0).sum()
        out[pd.Timestamp(dt)] = s / s.sum()
    return out


def combine_target_dicts(
    targets: pd.DataFrame,
    left_strategy: str,
    right_strategy: str,
) -> dict[pd.Timestamp, pd.Series]:
    left = target_dict(targets, 'KOSPI_EX_K200', left_strategy)
    right = target_dict(targets, 'KOSDAQ', right_strategy)
    dates = sorted(set(left) & set(right))
    out: dict[pd.Timestamp, pd.Series] = {}
    for dt in dates:
        s = pd.concat([0.5 * left[dt], 0.5 * right[dt]]).groupby(level=0).sum()
        out[dt] = s / s.sum()
    return out


def simulate_one(
    returns: pd.DataFrame,
    targets_by_date: dict[pd.Timestamp, pd.Series],
    phase: int,
    phase_map: dict[pd.Timestamp, int],
    universe: str,
    strategy: str,
) -> pd.DataFrame:
    scheduled = {d for d in targets_by_date if phase_map.get(d) == phase}
    if not scheduled:
        return pd.DataFrame()
    first = min(scheduled)
    dates = [d for d in returns.index if d >= first]

    current = pd.Series(dtype=float)
    rows: list[dict] = []
    rebal_count = 0

    for dt in dates:
        gross_ret = 0.0
        missing_weight = 0.0
        if len(current):
            rr = returns.loc[dt].reindex(current.index)
            missing_weight = float(current[rr.isna()].sum())
            rr = rr.fillna(0.0).clip(lower=-0.999999)
            gross_ret = float((current * rr).sum())
            grown = current * (1.0 + rr)
            denom = float(grown.sum())
            if denom > 0:
                current = grown / denom

        turnover = 0.0
        rebalanced = False
        n_names = len(current)
        hhi = float((current ** 2).sum()) if len(current) else np.nan
        top_weight = float(current.max()) if len(current) else np.nan

        if dt in scheduled:
            target = targets_by_date[dt]
            if len(current):
                union = current.index.union(target.index)
                turnover = float(0.5 * (current.reindex(union, fill_value=0.0) - target.reindex(union, fill_value=0.0)).abs().sum())
            else:
                turnover = 1.0
            current = target.copy()
            rebalanced = True
            rebal_count += 1
            n_names = len(current)
            hhi = float((current ** 2).sum())
            top_weight = float(current.max())

        rec = {
            'date': dt, 'universe': universe, 'strategy': strategy, 'phase': phase,
            'gross_ret': gross_ret, 'turnover': turnover, 'rebalanced': int(rebalanced),
            'missing_return_weight': missing_weight, 'n_names': n_names,
            'hhi': hhi, 'top_weight': top_weight,
        }
        for cost in COSTS_BP:
            c = turnover * cost / 10000.0
            rec[f'net{cost}_ret'] = (1.0 + gross_ret) * (1.0 - c) - 1.0
        rows.append(rec)

    return pd.DataFrame(rows)


def simulate_all(targets: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    common = sorted(targets.date.drop_duplicates())
    # Keep phase assignment identical to target construction. Every eligible
    # date appears once in targets and preserves the original date modulo.
    phase_lookup = targets[['date', 'phase']].drop_duplicates().set_index('date')['phase'].to_dict()

    frames: list[pd.DataFrame] = []
    for universe in UNIVERSES:
        for strategy in STRATEGIES[universe]:
            td = target_dict(targets, universe, strategy)
            for phase in range(H):
                f = simulate_one(returns, td, phase, phase_lookup, universe, strategy)
                if len(f):
                    frames.append(f)

    for strategy, (left, right) in COMBINED.items():
        td = combine_target_dicts(targets, left, right)
        for phase in range(H):
            f = simulate_one(returns, td, phase, phase_lookup, 'NON_K200_50_50', strategy)
            if len(f):
                frames.append(f)

    daily = pd.concat(frames, ignore_index=True)
    write_chunked_csv(daily, OUT / 'daily_portfolio_returns.csv', index=False, target_mb=40)
    return daily


def ann_cagr(r: pd.Series) -> float:
    r = r.dropna()
    if len(r) < 2:
        return np.nan
    total = float((1.0 + r).prod())
    years = len(r) / 252.0
    return total ** (1.0 / years) - 1.0 if total > 0 and years > 0 else np.nan


def ann_vol(r: pd.Series) -> float:
    r = r.dropna()
    return float(r.std(ddof=1) * math.sqrt(252.0)) if len(r) >= 3 else np.nan


def sharpe(r: pd.Series) -> float:
    r = r.dropna()
    sd = r.std(ddof=1)
    if len(r) < 3 or not np.isfinite(sd) or sd <= 0:
        return np.nan
    return float(r.mean() / sd * math.sqrt(252.0))


def max_dd(r: pd.Series) -> float:
    r = r.dropna()
    if not len(r):
        return np.nan
    nav = (1.0 + r).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def worst_20d(r: pd.Series) -> float:
    r = r.dropna()
    if len(r) < 20:
        return np.nan
    x = (1.0 + r).rolling(20).apply(np.prod, raw=True) - 1.0
    return float(x.min())


def period_stats(daily: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (universe, strategy, phase), g0 in daily.groupby(['universe', 'strategy', 'phase']):
        g0 = g0.sort_values('date')
        for period, (lo, hi) in PERIODS.items():
            g = g0[(g0.date >= lo) & (g0.date <= hi)]
            if len(g) < 40:
                continue
            days = len(g)
            years = days / 252.0
            for cost in COSTS_BP:
                r = g[f'net{cost}_ret']
                cagr = ann_cagr(r)
                mdd = max_dd(r)
                vol = ann_vol(r)
                sh = sharpe(r)
                rows.append({
                    'universe': universe, 'strategy': strategy, 'phase': phase,
                    'period': period, 'cost_bp': cost, 'n_days': days,
                    'cagr': cagr, 'mdd': mdd, 'vol': vol, 'sharpe': sh,
                    'calmar': cagr / abs(mdd) if np.isfinite(cagr) and np.isfinite(mdd) and mdd < 0 else np.nan,
                    'worst_20d': worst_20d(r),
                    'annual_turnover': float(g.turnover.sum() / years) if years > 0 else np.nan,
                    'avg_rebalance_turnover': float(g.loc[g.rebalanced.eq(1), 'turnover'].mean()),
                    'n_rebalances': int(g.rebalanced.sum()),
                    'avg_n_names': float(g.loc[g.rebalanced.eq(1), 'n_names'].mean()),
                    'avg_hhi': float(g.loc[g.rebalanced.eq(1), 'hhi'].mean()),
                    'avg_top_weight': float(g.loc[g.rebalanced.eq(1), 'top_weight'].mean()),
                    'avg_missing_return_weight': float(g.missing_return_weight.mean()),
                })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'phase_period_stats.csv', index=False)
    return out


def baseline_name(universe: str) -> str:
    return 'CF20_BASE' if universe == 'NON_K200_50_50' else 'CF20'


def compare_to_baseline(stats: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (universe, period, cost), g in stats.groupby(['universe', 'period', 'cost_bp']):
        bname = baseline_name(universe)
        b = g[g.strategy.eq(bname)].set_index('phase')
        if not len(b):
            continue
        for strategy, s in g.groupby('strategy'):
            if strategy == bname:
                continue
            s = s.set_index('phase')
            phases = sorted(set(b.index) & set(s.index))
            if not phases:
                continue
            q = s.loc[phases]
            qb = b.loc[phases]
            dcagr = (q.cagr - qb.cagr).to_numpy(float)
            dsh = (q.sharpe - qb.sharpe).to_numpy(float)
            dmdd = (q.mdd - qb.mdd).to_numpy(float)  # positive = less severe drawdown
            dturn = (q.annual_turnover - qb.annual_turnover).to_numpy(float)
            rows.append({
                'universe': universe, 'strategy': strategy, 'period': period, 'cost_bp': cost,
                'n_phases': len(phases),
                'median_delta_cagr': float(np.nanmedian(dcagr)),
                'mean_delta_cagr': float(np.nanmean(dcagr)),
                'min_delta_cagr': float(np.nanmin(dcagr)),
                'cagr_better_phases': int(np.nansum(dcagr > 0)),
                'median_delta_sharpe': float(np.nanmedian(dsh)),
                'sharpe_better_phases': int(np.nansum(dsh > 0)),
                'median_mdd_improvement': float(np.nanmedian(dmdd)),
                'mdd_better_phases': int(np.nansum(dmdd > 0)),
                'median_delta_annual_turnover': float(np.nanmedian(dturn)),
                'median_cagr': float(np.nanmedian(q.cagr)),
                'worst_phase_cagr': float(np.nanmin(q.cagr)),
                'median_mdd': float(np.nanmedian(q.mdd)),
                'worst_phase_mdd': float(np.nanmin(q.mdd)),
                'median_sharpe': float(np.nanmedian(q.sharpe)),
                'worst_phase_sharpe': float(np.nanmin(q.sharpe)),
                'median_annual_turnover': float(np.nanmedian(q.annual_turnover)),
            })
    out = pd.DataFrame(rows)
    out.to_csv(OUT / 'baseline_comparison.csv', index=False)
    return out


def baseline_summary(stats: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for (universe, strategy, period, cost), g in stats.groupby(['universe','strategy','period','cost_bp']):
        rows.append({
            'universe': universe, 'strategy': strategy, 'period': period, 'cost_bp': cost,
            'n_phases': g.phase.nunique(),
            'median_cagr': g.cagr.median(), 'mean_cagr': g.cagr.mean(), 'worst_phase_cagr': g.cagr.min(),
            'median_mdd': g.mdd.median(), 'worst_phase_mdd': g.mdd.min(),
            'median_sharpe': g.sharpe.median(), 'worst_phase_sharpe': g.sharpe.min(),
            'median_turnover': g.annual_turnover.median(),
            'median_n_names': g.avg_n_names.median(), 'median_top_weight': g.avg_top_weight.median(),
        })
    out=pd.DataFrame(rows)
    out.to_csv(OUT/'portfolio_summary.csv',index=False)
    return out


def pct(x: float, digits: int = 1) -> str:
    return 'NA' if not np.isfinite(x) else f'{x*100:+.{digits}f}%'


def num(x: float, digits: int = 2) -> str:
    return 'NA' if not np.isfinite(x) else f'{x:.{digits}f}'


def make_report(summary: pd.DataFrame, comp: pd.DataFrame) -> str:
    L = [
        '# CF20 Liquidity Portfolio Comparison', '',
        'CF20 is frozen. This stage converts the previously tested factor/liquidity rules into actual daily long-only portfolio NAVs.', '',
        'Construction: 8 equal-notional factor sleeves; each sleeve holds Top20 equal-weight names. Duplicate names across sleeves receive proportionally larger aggregate weights. Rebalance every 10 trading days. All 10 possible rebalance phases are simulated.', '',
        'Turnover is measured on the aggregate portfolio as 0.5 * sum(abs(target weight - pre-trade drifted weight)). Costs are charged at each rebalance. Headline comparisons use 30bp per one-way turnover; 0bp and 60bp are also saved.', '',
        'Selection guardrail: liquidity metrics/cutoffs are frozen from prior stock-level, horizon, and phase tests. No portfolio metric is used to retune a cutoff.', '',
    ]

    for universe in ('KOSPI_EX_K200','KOSDAQ','NON_K200_50_50'):
        L += [f'## {universe} — 30bp, median across 10 phases', '']
        for period in ('PRE_STRESS_2016_2024','NORMAL_2023_2024','BULL_2025','YTD_2026','FULL_2016_2026'):
            z = summary[(summary.universe==universe)&(summary.period==period)&(summary.cost_bp==30)]
            if not len(z):
                continue
            L.append(f'### {period}')
            z = z.sort_values(['median_sharpe','median_cagr'],ascending=False)
            for _,r in z.iterrows():
                L.append(
                    f"- {r.strategy}: CAGR {pct(r.median_cagr)}; MDD {pct(r.median_mdd)}; "
                    f"Sharpe {num(r.median_sharpe)}; ann.turn {r.median_turnover:.2f}x; "
                    f"worst-phase CAGR {pct(r.worst_phase_cagr)}"
                )
            L.append('')

        L += ['### Incremental vs CF20 baseline — PRE_STRESS_2016_2024', '']
        z = comp[(comp.universe==universe)&(comp.period=='PRE_STRESS_2016_2024')&(comp.cost_bp==30)]
        if len(z):
            z=z.sort_values(['cagr_better_phases','median_delta_cagr'],ascending=False)
            for _,r in z.iterrows():
                L.append(
                    f"- {r.strategy}: median dCAGR {pct(r.median_delta_cagr)}; "
                    f"CAGR better {int(r.cagr_better_phases)}/{int(r.n_phases)} phases; "
                    f"dSharpe {num(r.median_delta_sharpe)} ({int(r.sharpe_better_phases)}/{int(r.n_phases)} better); "
                    f"MDD improvement {pct(r.median_mdd_improvement)} ({int(r.mdd_better_phases)}/{int(r.n_phases)} better)"
                )
        L.append('')

    L += [
        '## Interpretation guardrails', '',
        '- This is a portfolio implementation test, not another cutoff search. A strategy that wins only in one phase or one stress year should not be promoted.',
        '- Median-across-phase results are more important than the best single phase. Worst-phase CAGR/MDD are retained to expose timing dependence.',
        '- KOSPI_EX_K200 and KOSDAQ results should be read separately before using the 50/50 combined portfolio because their liquidity mechanisms differ.',
        '- Missing held-stock daily returns are treated as 0 for that day; the average missing-return weight is saved as a QA field.',
        '- Large targets, sleeve holdings, and daily NAV intermediates are retained as GitHub-safe chunked gzip CSVs with manifests for later reuse.', '',
    ]
    return '\n'.join(L)


def main() -> None:
    targets, returns, quality = build_targets()
    daily = simulate_all(targets, returns)
    stats = period_stats(daily)
    summary = baseline_summary(stats)
    comp = compare_to_baseline(stats)
    text = make_report(summary, comp)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)
    print(f'target_rows={len(targets):,}; daily_rows={len(daily):,}; stats={len(stats):,}')


if __name__ == '__main__':
    main()
