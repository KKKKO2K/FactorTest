from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/liquidity_cross_factor'))
sys.path.insert(0, str(ROOT / 'research/stock_level_factor_interaction'))

import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as multi
import audit_cf20_portfolio_tieout as audit
import run_factor_level_finalists as finalists

OUT = Path(__file__).resolve().parent / 'results_opfy1_regime_gate'
OUT.mkdir(parents=True, exist_ok=True)

MIXED = 'KOSDAQ_PLUS_KOSPI_EX_K200'
ALLOWED_REVISION_CELLS = {'B3|F_LOW', 'B4|F_HIGH'}

# Pre-declared rules. All state variables are observed as-of the rebalance date.
RULES = (
    'ALWAYS_OPFY1',
    'ALWAYS_PER',
    'STATIC_50_50',
    'B2_SWITCH',
    'B2_PERSIST_SWITCH',
    'TRAIN_CELL_SWITCH',
    'TRAIN_CELL_HEALTH_SWITCH',
    'B2_OR_NEG_SWITCH',
)


def blend(a: pd.Series, b: pd.Series, wa: float) -> pd.Series:
    idx = a.index.union(b.index)
    out = wa * a.reindex(idx, fill_value=0.0) + (1.0 - wa) * b.reindex(idx, fill_value=0.0)
    out = out[out > 0]
    return out / out.sum()


def load_states() -> pd.DataFrame:
    p = Path(__file__).resolve().parent / 'results' / 'action_state_panel.csv'
    s = pd.read_csv(p, parse_dates=['date'])
    s = s[s.universe == MIXED].sort_values('date').reset_index(drop=True)
    if s.empty:
        raise RuntimeError('No mixed-universe state panel')
    return s


def asof_state(states: pd.DataFrame, dt: pd.Timestamp):
    i = states.date.searchsorted(dt, side='right') - 1
    if i < 0:
        return None, None
    cur = states.iloc[int(i)]
    prev = states.iloc[int(i - 1)] if i > 0 else None
    return cur, prev


def choose_target(rule: str, op: pd.Series, per: pd.Series, cur, prev) -> tuple[pd.Series, str]:
    if rule == 'ALWAYS_OPFY1':
        return op, 'OPFY1'
    if rule == 'ALWAYS_PER':
        return per, 'PER'
    if rule == 'STATIC_50_50':
        return blend(op, per, 0.5), '50_50'

    b2 = str(cur.base_state) == 'B2'
    prev_b2 = prev is not None and str(prev.base_state) == 'B2'
    approved = str(cur.state_cell) in ALLOWED_REVISION_CELLS
    rev_top = float(cur.REVISION_top20) if pd.notna(cur.REVISION_top20) else np.nan
    rev_negative = np.isfinite(rev_top) and rev_top < 0

    if rule == 'B2_SWITCH':
        use_op = not b2
    elif rule == 'B2_PERSIST_SWITCH':
        use_op = not (b2 and prev_b2)
    elif rule == 'TRAIN_CELL_SWITCH':
        use_op = approved
    elif rule == 'TRAIN_CELL_HEALTH_SWITCH':
        use_op = approved and not rev_negative
    elif rule == 'B2_OR_NEG_SWITCH':
        use_op = not (b2 or rev_negative)
    else:
        raise KeyError(rule)
    return (op, 'OPFY1') if use_op else (per, 'PER')


def build_rule_targets(op_targets, per_targets, states):
    common = sorted(set(op_targets) & set(per_targets))
    first_state = states.date.min()
    rows = []
    stores = {r: {} for r in RULES}
    for dt in common:
        if dt < first_state:
            continue
        cur, prev = asof_state(states, dt)
        if cur is None:
            continue
        for rule in RULES:
            target, action = choose_target(rule, op_targets[dt], per_targets[dt], cur, prev)
            stores[rule][dt] = target
            rows.append({
                'date': dt, 'rule': rule, 'action': action,
                'state_date': cur.date, 'base_state': cur.base_state,
                'factor_substate': cur.factor_substate, 'state_cell': cur.state_cell,
                'revision_state': cur.REVISION_state, 'revision_top20': cur.REVISION_top20,
            })
    return stores, pd.DataFrame(rows)


def simulate(returns, stores, phase_map):
    frames = []
    for rule, targets in stores.items():
        meta = {'variant': rule, 'universe': MIXED, 'strategy': 'REGIME_GATE', 'factor': 'OPFY1_REV'}
        for phase in range(audit.H):
            x = finalists.simulate_factor_one(returns, targets, phase, phase_map, meta)
            if len(x):
                frames.append(x)
    return pd.concat(frames, ignore_index=True)


def comparisons(summary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for period in audit.PERIODS:
        for rt in ('GROSS', 'NET30', 'NET60'):
            q = summary[(summary.period == period) & (summary.return_type == rt)].set_index('variant')
            if 'ALWAYS_OPFY1' not in q.index or 'ALWAYS_PER' not in q.index:
                continue
            op = q.loc['ALWAYS_OPFY1']
            per = q.loc['ALWAYS_PER']
            for rule in RULES:
                if rule not in q.index:
                    continue
                r = q.loc[rule]
                rows.append({
                    'period': period, 'return_type': rt, 'rule': rule,
                    'cagr': r.median_cagr, 'sharpe': r.median_sharpe, 'mdd': r.median_mdd,
                    'annual_turnover': r.median_annual_turnover,
                    'delta_cagr_vs_opfy1': r.median_cagr - op.median_cagr,
                    'delta_mdd_vs_opfy1': r.median_mdd - op.median_mdd,
                    'delta_cagr_vs_per': r.median_cagr - per.median_cagr,
                    'positive_phases': r.positive_cagr_phases,
                })
    return pd.DataFrame(rows)


def action_stats(actions: pd.DataFrame) -> pd.DataFrame:
    x = actions.copy()
    x['period'] = np.select(
        [x.date.dt.year <= 2022, x.date.dt.year <= 2024, x.date.dt.year == 2025],
        ['TRAIN_2016_2022', 'VALID_2023_2024', 'STRESS_2025'],
        default='STRESS_2026',
    )
    out = (x.groupby(['rule', 'period'])
             .agg(n=('date', 'size'), op_share=('action', lambda z: float((z == 'OPFY1').mean())),
                  b2_share=('base_state', lambda z: float((z == 'B2').mean())))
             .reset_index())
    return out


def pct(x):
    return 'NA' if pd.isna(x) else f'{x:+.2%}'


def report(comp: pd.DataFrame, acts: pd.DataFrame) -> str:
    L = [
        '# Mixed OPFY1 + CF20 Regime Gate — Daily NAV', '',
        'Purpose: test whether ex-ante regime permissioning improves the actual Mixed OPFY1+CF20 factor sleeve, using Mixed PER+CF20 as the investable fallback rather than cash.', '',
        'State cells are observed as-of each rebalance date. The TRAIN_CELL rules only permit Revision in the two cells selected from 2016-2022 training evidence: B3|F_LOW and B4|F_HIGH. No future state or forward return is used in target selection.', '',
        'Rules: ALWAYS_OPFY1; ALWAYS_PER; STATIC_50_50; B2_SWITCH; B2_PERSIST_SWITCH; TRAIN_CELL_SWITCH; TRAIN_CELL_HEALTH_SWITCH (training-cell permission plus lagged Revision top20 >= 0); B2_OR_NEG_SWITCH.', '',
        '## NET60 median across 10 phases', ''
    ]
    for period in ('TRAIN_2016_2022', 'VALID_2023_2024', 'STRESS_2025', 'STRESS_2026'):
        # audit periods use different labels
        amap = {'TRAIN_2016_2022': 'EARLY_2016_2019', 'VALID_2023_2024': 'NORMAL_2023_2024',
                'STRESS_2025': 'BULL_2025', 'STRESS_2026': 'YTD_2026'}
        # TRAIN is better represented by full pre-stress below; retained here only for readable slices.
        p = amap[period]
        q = comp[(comp.period == p) & (comp.return_type == 'NET60')]
        if q.empty:
            continue
        L.append(f'### {p}')
        for rule in RULES:
            z = q[q.rule == rule]
            if z.empty:
                continue
            r = z.iloc[0]
            L.append(f"- {rule}: CAGR {pct(r.cagr)}; Sharpe {r.sharpe:.2f}; MDD {pct(r.mdd)}; turnover {r.annual_turnover:.2f}x; dCAGR vs OPFY1 {pct(r.delta_cagr_vs_opfy1)}; dCAGR vs PER {pct(r.delta_cagr_vs_per)}")
        L.append('')
    L += ['## 2016-2024 NET60', '']
    q = comp[(comp.period == 'PRE_STRESS_2016_2024') & (comp.return_type == 'NET60')]
    for rule in RULES:
        z = q[q.rule == rule]
        if z.empty: continue
        r = z.iloc[0]
        L.append(f"- {rule}: CAGR {pct(r.cagr)}; Sharpe {r.sharpe:.2f}; MDD {pct(r.mdd)}; turnover {r.annual_turnover:.2f}x; dCAGR vs OPFY1 {pct(r.delta_cagr_vs_opfy1)}")
    L += ['', '## Guardrails', '',
          '- 2023+ remains robustness/stress evidence, not untouched OOS.',
          '- TRAIN_CELL_HEALTH_SWITCH and B2_OR_NEG_SWITCH combine already-observed components but the composite rules are new hypotheses; treat their results as exploratory until re-frozen/walk-forward tested.',
          '- A switch rule must beat both ALWAYS_OPFY1 and the simple ALWAYS_PER / STATIC_50_50 alternatives to justify regime complexity.',
          '- NET60 is turnover-proportional cost, not a full market-impact model.', '']
    return '\n'.join(L)


def main():
    returns, _mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}
    _store, sleeves, _common, phase_map, _common_pos = audit.build_targets(returns, k200, markets, files)

    op = finalists.extract_factor_targets(sleeves, MIXED, 'CF20', 'OPFY1_REV')
    per = finalists.extract_factor_targets(sleeves, MIXED, 'CF20', 'PER12MF')
    states = load_states()
    stores, actions = build_rule_targets(op, per, states)
    daily = simulate(returns, stores, phase_map)
    daily['date'] = pd.to_datetime(daily.date)

    perf = finalists.performance_stats(daily)
    summ = finalists.summarize(perf)
    comp = comparisons(summ)
    ast = action_stats(actions)

    perf.to_csv(OUT / 'phase_performance.csv', index=False)
    summ.to_csv(OUT / 'summary.csv', index=False)
    comp.to_csv(OUT / 'comparisons.csv', index=False)
    actions.to_csv(OUT / 'rebalance_actions.csv', index=False)
    ast.to_csv(OUT / 'action_stats.csv', index=False)
    (OUT / 'SUMMARY.md').write_text(report(comp, ast), encoding='utf-8')
    print((OUT / 'SUMMARY.md').read_text(encoding='utf-8'))


if __name__ == '__main__':
    main()
