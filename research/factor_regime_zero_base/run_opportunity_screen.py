from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
INP = HERE / 'results_persistence_rotation/persistence_rotation_panel.csv'
OUT = HERE / 'results_opportunity'
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    'MOM1M', 'MOM12_1', 'OP12_REV', 'OPFY1_REV',
    'PBR12MF', 'PER12MF', 'PRIVATE_FLOW', 'FOREIGN_FLOW'
]
PREDICTORS = [
    'BREADTH_20', 'BREADTH_60', 'DISPERSION_20', 'DISPERSION_60',
    'ABS_OPPORTUNITY_20', 'RANGE_20', 'LEADER_STRENGTH_20',
    'LOSER_WEAKNESS_20', 'WINNER_GAP_20', 'CROSS_HORIZON_RANK_CORR',
    'PREV_RANK_CORR_20', 'RANK_TURNOVER_20', 'BREADTH_CHANGE_20',
    'DISPERSION_CHANGE_20', 'AVG_PAIR_CORR_60', 'PC1_SHARE_60',
    'FACTOR_VOL_MEDIAN_60', 'SIGN_ALIGNMENT_20_60'
]
TARGETS = [
    'TARGET_FWD_DISPERSION_20',
    'TARGET_FWD_ABS_OPPORTUNITY_20',
    'TARGET_FWD_RANGE_20',
]
MIN_TRAIN = 80
MIN_TEST = 12


def period_of(year: int) -> str:
    if year <= 2022: return 'DEV_2020_2022'
    if year <= 2024: return 'CONFIRM_2023_2024'
    if year == 2025: return 'BULL_2025'
    return 'YTD_2026'


def spearman(x: pd.Series, y: pd.Series) -> float:
    z = pd.concat([x, y], axis=1).dropna()
    if len(z) < 3 or z.iloc[:, 0].nunique() < 2 or z.iloc[:, 1].nunique() < 2:
        return np.nan
    return float(z.iloc[:, 0].rank().corr(z.iloc[:, 1].rank()))


def add_targets(p: pd.DataFrame) -> pd.DataFrame:
    z = p.copy()
    cols = [f'FWD20_{f}' for f in FACTORS]
    a = z[cols].to_numpy(dtype=float)
    z['TARGET_FWD_DISPERSION_20'] = np.nanstd(a, axis=1, ddof=1)
    z['TARGET_FWD_ABS_OPPORTUNITY_20'] = np.nanmean(np.abs(a), axis=1)
    z['TARGET_FWD_RANGE_20'] = np.nanmax(a, axis=1) - np.nanmin(a, axis=1)
    return z


def walkforward(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for u, g in p.groupby('universe'):
        g = g.sort_values('date')
        for year in range(2020, int(g.date.dt.year.max()) + 1):
            tr = g[g.date < pd.Timestamp(f'{year}-01-01')]
            te = g[g.date.dt.year.eq(year)]
            if len(tr) < MIN_TRAIN or len(te) < MIN_TEST:
                continue
            for target in TARGETS:
                for feat in PREDICTORS:
                    a = tr[[feat, target]].dropna(); b = te[[feat, target]].dropna()
                    if len(a) < MIN_TRAIN or len(b) < MIN_TEST:
                        continue
                    train_ic = spearman(a[feat], a[target])
                    if not np.isfinite(train_ic) or train_ic == 0:
                        continue
                    direction = 1.0 if train_ic > 0 else -1.0
                    oos_ic = spearman(b[feat], b[target])
                    q33, q67 = a[feat].quantile([1/3, 2/3])
                    lo = b.loc[b[feat] <= q33, target]
                    hi = b.loc[b[feat] >= q67, target]
                    raw_hl = float(hi.mean()-lo.mean()) if len(lo) >= 3 and len(hi) >= 3 else np.nan
                    rows.append({
                        'universe': u, 'eval_year': year, 'period': period_of(year),
                        'feature': feat, 'target': target, 'train_n': len(a), 'test_n': len(b),
                        'train_spearman': train_ic, 'direction': int(direction),
                        'oos_spearman': oos_ic,
                        'directed_oos_spearman': direction*oos_ic if np.isfinite(oos_ic) else np.nan,
                        'raw_high_minus_low': raw_hl,
                        'directed_high_minus_low': direction*raw_hl if np.isfinite(raw_hl) else np.nan,
                    })
    return pd.DataFrame(rows)


def summarize(wf: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (feat, target), g in wf.groupby(['feature','target']):
        r = {'feature': feat, 'target': target, 'n_universe_years': len(g)}
        for p in ['DEV_2020_2022','CONFIRM_2023_2024','BULL_2025','YTD_2026']:
            q = g[g.period.eq(p)]
            r[f'{p}_median_dic'] = float(q.directed_oos_spearman.median()) if len(q) else np.nan
            r[f'{p}_positive_dic_share'] = float((q.directed_oos_spearman>0).mean()) if len(q) else np.nan
            r[f'{p}_median_dhl'] = float(q.directed_high_minus_low.median()) if len(q) else np.nan
        qc = g[g.period.eq('CONFIRM_2023_2024')]
        byu = qc.groupby('universe').directed_oos_spearman.median() if len(qc) else pd.Series(dtype=float)
        r['CONFIRM_positive_universes'] = int((byu>0).sum())
        r['CONFIRM_universe_count'] = int(len(byu))
        r['PASS'] = bool(
            r['DEV_2020_2022_median_dic'] > 0 and
            r['CONFIRM_2023_2024_median_dic'] > 0 and
            r['CONFIRM_2023_2024_median_dhl'] > 0 and
            r['CONFIRM_positive_universes'] >= 4
        )
        rows.append(r)
    return pd.DataFrame(rows).sort_values(
        ['PASS','CONFIRM_2023_2024_median_dic','DEV_2020_2022_median_dic'],
        ascending=[False,False,False]
    ).reset_index(drop=True)


def fmt(x: float) -> str:
    return 'NA' if not np.isfinite(x) else f'{x:+.3f}'


def pct(x: float) -> str:
    return 'NA' if not np.isfinite(x) else f'{x:+.2%}'


def report(panel: pd.DataFrame, s: pd.DataFrame) -> str:
    L = [
        '# Zero-Base Factor Opportunity — Stage 2', '',
        'Question: can information observable at t predict how much cross-factor opportunity will exist over the next 20D?', '',
        '- Targets are forward cross-factor dispersion, mean absolute factor payoff, and best-minus-worst range across the same eight canonical factor sleeves.',
        '- Predictors are the same 18 predeclared contemporaneous structural features used in Stage 1.',
        '- Direction and thresholds are re-estimated only from data before each evaluation year.',
        '- PASS gate matches Stage 1: positive directed median IC in 2020-22 and 2023-24, positive 2023-24 directed H-L, and positive universe-median IC in at least 4/6 universes.', '',
        f'## Result: {int(s.PASS.sum())} PASS relations out of {len(s)} screened', ''
    ]
    for r in s[s.PASS].head(25).itertuples(index=False):
        L.append(
            f'- {r.target} <- {r.feature}: DEV IC {fmt(r.DEV_2020_2022_median_dic)}, '
            f'CONFIRM IC {fmt(r.CONFIRM_2023_2024_median_dic)}, '
            f'CONFIRM H-L {pct(r.CONFIRM_2023_2024_median_dhl)}, '
            f'universes {r.CONFIRM_positive_universes}/{r.CONFIRM_universe_count}, '
            f'2025 IC {fmt(r.BULL_2025_median_dic)}, 2026 IC {fmt(r.YTD_2026_median_dic)}'
        )
    L += ['', '## Best relations by target', '']
    for target in TARGETS:
        L.append(f'### {target}')
        q = s[s.target.eq(target)].sort_values('CONFIRM_2023_2024_median_dic', ascending=False).head(6)
        for r in q.itertuples(index=False):
            L.append(
                f'- {r.feature}: PASS={r.PASS}; DEV {fmt(r.DEV_2020_2022_median_dic)}, '
                f'CONFIRM {fmt(r.CONFIRM_2023_2024_median_dic)}, H-L {pct(r.CONFIRM_2023_2024_median_dhl)}, '
                f'universes {r.CONFIRM_positive_universes}/{r.CONFIRM_universe_count}, '
                f'2025 {fmt(r.BULL_2025_median_dic)}, 2026 {fmt(r.YTD_2026_median_dic)}'
            )
        L.append('')
    L += ['## Next-step rule', '',
          '- If opportunity is forecastable, freeze the robust opportunity predictors and use them only as an active-risk gate around the persistence/rotation signal.',
          '- High opportunity + persistence -> top-factor tilt; high opportunity + rotation -> contrarian-factor tilt; low opportunity -> EW8.',
          '- Do not optimize opportunity thresholds on 2025/2026.']
    return '\n'.join(L)


def main():
    p = pd.read_csv(INP)
    p['date'] = pd.to_datetime(p['date'])
    p = add_targets(p)
    wf = walkforward(p)
    s = summarize(wf)
    p.to_csv(OUT/'opportunity_panel.csv', index=False, encoding='utf-8-sig')
    wf.to_csv(OUT/'opportunity_walkforward.csv', index=False, encoding='utf-8-sig')
    s.to_csv(OUT/'opportunity_summary.csv', index=False, encoding='utf-8-sig')
    text = report(p, s)
    (OUT/'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
