from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FINALIST = ROOT / 'research' / 'stock_level_factor_interaction' / 'results_factor_level_finalists' / 'daily_returns_text' / 'MIXED_OPFY1_CF20.csv'
EVENTS = ROOT / 'research' / 'factor_regime_action_policy' / 'results' / 'finalist_regime_overlay' / 'overlay_signal_events.csv'
OUT = ROOT / 'research' / 'factor_regime_action_policy' / 'results' / 'finalist_regime_diagnostics'
OUT.mkdir(parents=True, exist_ok=True)

HORIZONS = (5, 10, 20)
RETURNS = {'GROSS': 'gross_ret', 'NET30': 'net30_ret', 'NET60': 'net60_ret'}


def sample_label(dt: pd.Timestamp) -> str:
    if dt < pd.Timestamp('2023-01-01'):
        return 'TRAIN_2016_2022'
    if dt < pd.Timestamp('2025-01-01'):
        return 'OOS_2023_2024'
    if dt < pd.Timestamp('2026-01-01'):
        return 'BULL_2025'
    return 'YTD_2026'


def add_forward_returns(daily: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for phase, g in daily.groupby('phase'):
        g = g.sort_values('date').copy()
        for label, col in RETURNS.items():
            arr = (1.0 + g[col].to_numpy(dtype=float))
            for h in HORIZONS:
                vals = np.full(len(g), np.nan)
                for i in range(len(g) - h):
                    vals[i] = float(np.prod(arr[i + 1:i + 1 + h]) - 1.0)
                g[f'{label}_FWD_{h}D'] = vals
        frames.append(g)
    return pd.concat(frames, ignore_index=True)


def build_state_panel() -> pd.DataFrame:
    e = pd.read_csv(EVENTS)
    e['date'] = pd.to_datetime(e['date'])
    e = e.sort_values('date').drop_duplicates('date', keep='last').copy()

    prev_bin = e['breadth_bin'].shift(1)
    e['breadth_transition'] = np.select(
        [
            e['breadth_bin'].eq('HIGH') & prev_bin.ne('HIGH'),
            e['breadth_bin'].eq('HIGH') & prev_bin.eq('HIGH'),
        ],
        ['HIGH_ENTRY', 'HIGH_PERSIST'],
        default='NON_HIGH',
    )
    e['breadth_delta'] = e['factor_breadth_20d'].diff()
    e['breadth_group'] = np.where(e['breadth_bin'].eq('HIGH'), 'HIGH', 'NON_HIGH')
    e['base_group'] = np.where(e['base_state'].isin(['B1', 'B2']), 'B1_B2', e['base_state'])
    e['high_base_cell'] = np.where(
        e['breadth_bin'].eq('HIGH'),
        'HIGH|' + e['base_group'].astype(str),
        'NON_HIGH',
    )
    e['high_revision_cell'] = np.where(
        e['breadth_bin'].eq('HIGH'),
        'HIGH|' + e['REVISION_state'].astype(str),
        'NON_HIGH',
    )
    e['high_factor_substate_cell'] = np.where(
        e['breadth_bin'].eq('HIGH'),
        'HIGH|' + e['factor_substate'].astype(str),
        'NON_HIGH',
    )
    e['sample'] = e['date'].map(sample_label)
    return e


def date_level_forward() -> pd.DataFrame:
    d = pd.read_csv(FINALIST)
    d['date'] = pd.to_datetime(d['date'])
    d = add_forward_returns(d)
    fwd_cols = [f'{rt}_FWD_{h}D' for rt in RETURNS for h in HORIZONS]
    date_level = d.groupby('date')[fwd_cols].agg(['mean', 'median']).reset_index()
    date_level.columns = [
        c[0] if c[1] == '' else f'{c[0]}_{c[1]}'
        for c in date_level.columns.to_flat_index()
    ]
    return date_level


def long_panel() -> pd.DataFrame:
    states = build_state_panel()
    fwd = date_level_forward()
    p = states.merge(fwd, on='date', how='inner')
    rows = []
    for _, r in p.iterrows():
        for rt in RETURNS:
            for h in HORIZONS:
                rows.append({
                    'date': r.date,
                    'sample': r['sample'],
                    'return_type': rt,
                    'horizon': h,
                    'factor_breadth_20d': r.factor_breadth_20d,
                    'breadth_bin': r.breadth_bin,
                    'breadth_group': r.breadth_group,
                    'breadth_transition': r.breadth_transition,
                    'breadth_delta': r.breadth_delta,
                    'base_state': r.base_state,
                    'factor_substate': r.factor_substate,
                    'REVISION_state': r.REVISION_state,
                    'high_base_cell': r.high_base_cell,
                    'high_revision_cell': r.high_revision_cell,
                    'high_factor_substate_cell': r.high_factor_substate_cell,
                    'fwd_mean_across_phases': r[f'{rt}_FWD_{h}D_mean'],
                    'fwd_median_across_phases': r[f'{rt}_FWD_{h}D_median'],
                })
    return pd.DataFrame(rows)


def summarize_condition(panel: pd.DataFrame, condition_col: str) -> pd.DataFrame:
    rows = []
    keys = ['sample', 'return_type', 'horizon', condition_col]
    for key, g in panel.groupby(keys, dropna=False):
        x = g['fwd_mean_across_phases'].dropna()
        if len(x) == 0:
            continue
        rec = dict(zip(keys, key))
        rec.update({
            'n_dates': len(x),
            'mean_fwd': float(x.mean()),
            'median_fwd': float(x.median()),
            'positive_share': float((x > 0).mean()),
            'mean_abs_fwd': float(x.abs().mean()),
        })
        rows.append(rec)
    return pd.DataFrame(rows)


def high_contrasts(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (sample, rt, h), g in panel.groupby(['sample', 'return_type', 'horizon']):
        high = g.loc[g.breadth_group.eq('HIGH'), 'fwd_mean_across_phases'].dropna()
        non = g.loc[g.breadth_group.eq('NON_HIGH'), 'fwd_mean_across_phases'].dropna()
        entry = g.loc[g.breadth_transition.eq('HIGH_ENTRY'), 'fwd_mean_across_phases'].dropna()
        persist = g.loc[g.breadth_transition.eq('HIGH_PERSIST'), 'fwd_mean_across_phases'].dropna()
        rows.append({
            'sample': sample,
            'return_type': rt,
            'horizon': h,
            'n_high': len(high),
            'n_non_high': len(non),
            'high_mean': float(high.mean()) if len(high) else np.nan,
            'non_high_mean': float(non.mean()) if len(non) else np.nan,
            'high_minus_non_high': float(high.mean() - non.mean()) if len(high) and len(non) else np.nan,
            'high_positive_share': float((high > 0).mean()) if len(high) else np.nan,
            'non_high_positive_share': float((non > 0).mean()) if len(non) else np.nan,
            'n_high_entry': len(entry),
            'high_entry_mean': float(entry.mean()) if len(entry) else np.nan,
            'high_entry_positive_share': float((entry > 0).mean()) if len(entry) else np.nan,
            'n_high_persist': len(persist),
            'high_persist_mean': float(persist.mean()) if len(persist) else np.nan,
            'high_persist_positive_share': float((persist > 0).mean()) if len(persist) else np.nan,
        })
    return pd.DataFrame(rows)


def pct(x: float) -> str:
    return 'NA' if pd.isna(x) else f'{x:+.2%}'


def make_report(contrast: pd.DataFrame, base_cells: pd.DataFrame, transition: pd.DataFrame) -> str:
    lines = [
        '# Mixed OPFY1+CF20 — Candidate-Specific Regime Diagnostics',
        '',
        'Purpose: test whether the frozen Mixed FACTOR_20D signal predicts the exact finalist sleeve itself, rather than market or family-level proxy returns.',
        'Forward sleeve returns start on the trading day after each state date. For each state date, the 10 H=10 phase forward returns are averaged first, so the sample count is state dates rather than treating phases as independent observations.',
        'All results are descriptive; 2023+ is not pristine untouched OOS because prior research used later data for discovery.',
        '',
        '## HIGH vs NON_HIGH — exact finalist forward return',
        '',
    ]
    z = contrast[contrast.return_type.eq('NET60')]
    for sample in ('TRAIN_2016_2022', 'OOS_2023_2024', 'BULL_2025', 'YTD_2026'):
        lines.append(f'### {sample}')
        for h in HORIZONS:
            x = z[(z['sample'].eq(sample)) & (z['horizon'].eq(h))]
            if x.empty:
                continue
            r = x.iloc[0]
            lines.append(
                f"- {h}D: HIGH {pct(r.high_mean)} (n={int(r.n_high)}, pos={r.high_positive_share:.0%}) vs "
                f"NON_HIGH {pct(r.non_high_mean)} (n={int(r.n_non_high)}, pos={r.non_high_positive_share:.0%}); "
                f"H-N {pct(r.high_minus_non_high)}"
            )
        lines.append('')

    lines += ['## HIGH entry vs persistent HIGH — NET60', '']
    for sample in ('TRAIN_2016_2022', 'OOS_2023_2024', 'BULL_2025', 'YTD_2026'):
        lines.append(f'### {sample}')
        for h in HORIZONS:
            x = z[(z['sample'].eq(sample)) & (z['horizon'].eq(h))]
            if x.empty:
                continue
            r = x.iloc[0]
            lines.append(
                f"- {h}D: ENTRY {pct(r.high_entry_mean)} (n={int(r.n_high_entry)}, pos={r.high_entry_positive_share:.0%}); "
                f"PERSIST {pct(r.high_persist_mean)} (n={int(r.n_high_persist)}, pos={r.high_persist_positive_share:.0%})"
            )
        lines.append('')

    lines += ['## HIGH x base-state — NET60 20D', '']
    b = base_cells[(base_cells.return_type.eq('NET60')) & (base_cells.horizon.eq(20))]
    for sample in ('TRAIN_2016_2022', 'OOS_2023_2024', 'BULL_2025', 'YTD_2026'):
        lines.append(f'### {sample}')
        x = b[b['sample'].eq(sample)].sort_values('high_base_cell')
        for _, r in x.iterrows():
            lines.append(
                f"- {r.high_base_cell}: mean {pct(r.mean_fwd)}, median {pct(r.median_fwd)}, "
                f"pos {r.positive_share:.0%}, n={int(r.n_dates)}"
            )
        lines.append('')

    lines += [
        '## Interpretation guardrails',
        '',
        '- If HIGH is negative only in 2026 but not TRAIN / 2023-24 / 2025, treat it as a useful episode warning rather than a production exposure rule.',
        '- If HIGH_ENTRY is more consistently adverse than HIGH_PERSIST across historical samples, a transition/event rule is more defensible than a persistent state throttle.',
        '- If the sign depends strongly on B-state, return to nested conditioning before choosing an action rule.',
        '- Do not tune new cutoffs or hold durations on 2026 in this diagnostic.',
        '',
    ]
    return '\n'.join(lines)


def main() -> None:
    panel = long_panel()
    contrast = high_contrasts(panel)
    transition = summarize_condition(panel, 'breadth_transition')
    base_cells = summarize_condition(panel, 'high_base_cell')
    rev_cells = summarize_condition(panel, 'high_revision_cell')
    f_cells = summarize_condition(panel, 'high_factor_substate_cell')

    panel.to_csv(OUT / 'candidate_state_forward_panel.csv', index=False, encoding='utf-8', lineterminator='\n')
    contrast.to_csv(OUT / 'high_vs_nonhigh.csv', index=False, encoding='utf-8', lineterminator='\n')
    transition.to_csv(OUT / 'transition_summary.csv', index=False, encoding='utf-8', lineterminator='\n')
    base_cells.to_csv(OUT / 'high_base_state_summary.csv', index=False, encoding='utf-8', lineterminator='\n')
    rev_cells.to_csv(OUT / 'high_revision_state_summary.csv', index=False, encoding='utf-8', lineterminator='\n')
    f_cells.to_csv(OUT / 'high_factor_substate_summary.csv', index=False, encoding='utf-8', lineterminator='\n')

    text = make_report(contrast, base_cells, transition)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)
    print(f'panel_rows={len(panel):,}; contrast_rows={len(contrast):,}')


if __name__ == '__main__':
    main()
