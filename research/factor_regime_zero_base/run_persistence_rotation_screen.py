from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'research/factor_regime_v1/results/factor_5d_returns.csv'
OUT = Path(__file__).resolve().parent / 'results_persistence_rotation'
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    'MOM1M', 'MOM12_1', 'OP12_REV', 'OPFY1_REV',
    'PBR12MF', 'PER12MF', 'PRIVATE_FLOW', 'FOREIGN_FLOW'
]
EVAL_START_YEAR = 2020
MIN_TRAIN = 80
MIN_TEST = 12

PREDICTORS = [
    'BREADTH_20', 'BREADTH_60', 'DISPERSION_20', 'DISPERSION_60',
    'ABS_OPPORTUNITY_20', 'RANGE_20', 'LEADER_STRENGTH_20',
    'LOSER_WEAKNESS_20', 'WINNER_GAP_20', 'CROSS_HORIZON_RANK_CORR',
    'PREV_RANK_CORR_20', 'RANK_TURNOVER_20', 'BREADTH_CHANGE_20',
    'DISPERSION_CHANGE_20', 'AVG_PAIR_CORR_60', 'PC1_SHARE_60',
    'FACTOR_VOL_MEDIAN_60', 'SIGN_ALIGNMENT_20_60'
]
TARGETS = [
    'TARGET_RANK_CORR_20', 'TARGET_RANK_CORR_60',
    'TARGET_TOP2_SURVIVAL_20', 'TARGET_TOP2_SAME_20',
    'TARGET_FACTOR_MOM_20'
]


def period_of(year: int) -> str:
    if year <= 2022:
        return 'DEV_2020_2022'
    if year <= 2024:
        return 'CONFIRM_2023_2024'
    if year == 2025:
        return 'BULL_2025'
    return 'YTD_2026'


def compound_block(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    if a.ndim != 2 or np.isnan(a).any():
        return np.full(a.shape[1] if a.ndim == 2 else len(FACTORS), np.nan)
    if np.any(a <= -0.999999):
        return np.sum(a, axis=0)
    return np.prod(1.0 + a, axis=0) - 1.0


def rank_corr(a: np.ndarray, b: np.ndarray) -> float:
    x = pd.Series(a, dtype=float)
    y = pd.Series(b, dtype=float)
    if x.notna().sum() < 3 or y.notna().sum() < 3:
        return np.nan
    return float(x.rank(method='average').corr(y.rank(method='average')))


def avg_pair_corr(a: np.ndarray) -> float:
    c = pd.DataFrame(a).corr().to_numpy(dtype=float)
    if c.shape[0] < 2:
        return np.nan
    vals = c[np.triu_indices_from(c, k=1)]
    vals = vals[np.isfinite(vals)]
    return float(vals.mean()) if len(vals) else np.nan


def pc1_share(a: np.ndarray) -> float:
    c = pd.DataFrame(a).corr().to_numpy(dtype=float)
    if c.shape[0] < 2 or not np.isfinite(c).all():
        return np.nan
    eig = np.linalg.eigvalsh(c)
    eig = np.clip(eig, 0, None)
    den = eig.sum()
    return float(eig[-1] / den) if den > 0 else np.nan


def build_panel() -> pd.DataFrame:
    f = pd.read_csv(SRC)
    f['date'] = pd.to_datetime(f['date'])
    req = {'date', 'universe', 'factor', 'ls_return'}
    miss = req - set(f.columns)
    if miss:
        raise ValueError(f'missing required columns: {sorted(miss)}')
    f = f[f['factor'].isin(FACTORS)].copy()
    rows = []
    for u, g in f.groupby('universe'):
        w = g.pivot(index='date', columns='factor', values='ls_return').sort_index()
        if not set(FACTORS).issubset(w.columns):
            continue
        w = w[FACTORS]
        dates = w.index.to_list()
        arr = w.to_numpy(dtype=float)
        # 60D lookback + prior non-overlapping 20D needs at least 12 observations.
        # 60D forward target needs 12 observations after t.
        for i in range(11, len(w) - 12):
            cur20 = compound_block(arr[i-3:i+1])
            prev20 = compound_block(arr[i-7:i-3])
            cur60 = compound_block(arr[i-11:i+1])
            fwd20 = compound_block(arr[i+1:i+5])
            fwd60 = compound_block(arr[i+1:i+13])
            if not all(np.isfinite(x).all() for x in [cur20, prev20, cur60, fwd20, fwd60]):
                continue

            order = np.argsort(cur20)
            bottom2 = order[:2]
            top2 = order[-2:]
            future_order = np.argsort(fwd20)
            future_top2 = set(future_order[-2:])
            future_top4 = set(future_order[-4:])
            top2_set = set(top2)

            disp20 = float(np.std(cur20, ddof=1))
            prev_disp20 = float(np.std(prev20, ddof=1))
            med20 = float(np.median(cur20))
            sorted20 = np.sort(cur20)
            ret60_window = arr[i-11:i+1]

            rec = {
                'date': dates[i], 'universe': u,
                'BREADTH_20': float(np.mean(cur20 > 0)),
                'BREADTH_60': float(np.mean(cur60 > 0)),
                'DISPERSION_20': disp20,
                'DISPERSION_60': float(np.std(cur60, ddof=1)),
                'ABS_OPPORTUNITY_20': float(np.mean(np.abs(cur20))),
                'RANGE_20': float(cur20.max() - cur20.min()),
                'LEADER_STRENGTH_20': float(cur20.max() - med20),
                'LOSER_WEAKNESS_20': float(med20 - cur20.min()),
                'WINNER_GAP_20': float(sorted20[-1] - sorted20[-2]),
                'CROSS_HORIZON_RANK_CORR': rank_corr(cur20, cur60),
                'PREV_RANK_CORR_20': rank_corr(prev20, cur20),
                'RANK_TURNOVER_20': 1.0 - rank_corr(prev20, cur20),
                'BREADTH_CHANGE_20': float(np.mean(cur20 > 0) - np.mean(prev20 > 0)),
                'DISPERSION_CHANGE_20': disp20 - prev_disp20,
                'AVG_PAIR_CORR_60': avg_pair_corr(ret60_window),
                'PC1_SHARE_60': pc1_share(ret60_window),
                'FACTOR_VOL_MEDIAN_60': float(np.median(np.std(ret60_window, axis=0, ddof=1))),
                'SIGN_ALIGNMENT_20_60': float(np.mean(np.sign(cur20) == np.sign(cur60))),
                'TARGET_RANK_CORR_20': rank_corr(cur20, fwd20),
                'TARGET_RANK_CORR_60': rank_corr(cur60, fwd60),
                'TARGET_TOP2_SURVIVAL_20': len(top2_set & future_top4) / 2.0,
                'TARGET_TOP2_SAME_20': len(top2_set & future_top2) / 2.0,
                'TARGET_FACTOR_MOM_20': float(np.mean(fwd20[top2]) - np.mean(fwd20[bottom2])),
            }
            for j, fac in enumerate(FACTORS):
                rec[f'CUR20_{fac}'] = float(cur20[j])
                rec[f'FWD20_{fac}'] = float(fwd20[j])
            rows.append(rec)
    out = pd.DataFrame(rows).sort_values(['universe', 'date']).reset_index(drop=True)
    return out


def spearman(x: pd.Series, y: pd.Series) -> float:
    z = pd.concat([x, y], axis=1).dropna()
    if len(z) < 3 or z.iloc[:, 0].nunique() < 2 or z.iloc[:, 1].nunique() < 2:
        return np.nan
    return float(z.iloc[:, 0].rank().corr(z.iloc[:, 1].rank()))


def walkforward_screen(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    max_year = int(panel['date'].dt.year.max())
    for u, gu in panel.groupby('universe'):
        gu = gu.sort_values('date')
        for year in range(EVAL_START_YEAR, max_year + 1):
            train = gu[gu['date'] < pd.Timestamp(f'{year}-01-01')]
            test = gu[gu['date'].dt.year.eq(year)]
            if len(train) < MIN_TRAIN or len(test) < MIN_TEST:
                continue
            for target in TARGETS:
                for feat in PREDICTORS:
                    tr = train[[feat, target]].dropna()
                    te = test[[feat, target]].dropna()
                    if len(tr) < MIN_TRAIN or len(te) < MIN_TEST:
                        continue
                    tr_ic = spearman(tr[feat], tr[target])
                    if not np.isfinite(tr_ic) or tr_ic == 0:
                        continue
                    direction = 1.0 if tr_ic > 0 else -1.0
                    oos_ic = spearman(te[feat], te[target])
                    q33, q67 = tr[feat].quantile([1/3, 2/3])
                    lo = te.loc[te[feat] <= q33, target]
                    hi = te.loc[te[feat] >= q67, target]
                    raw_hl = float(hi.mean() - lo.mean()) if len(lo) >= 3 and len(hi) >= 3 else np.nan
                    rows.append({
                        'universe': u, 'eval_year': year, 'period': period_of(year),
                        'feature': feat, 'target': target,
                        'train_n': len(tr), 'test_n': len(te), 'train_spearman': tr_ic,
                        'direction': int(direction), 'oos_spearman': oos_ic,
                        'directed_oos_spearman': direction * oos_ic if np.isfinite(oos_ic) else np.nan,
                        'train_q33': q33, 'train_q67': q67,
                        'low_n': len(lo), 'high_n': len(hi), 'raw_high_minus_low': raw_hl,
                        'directed_high_minus_low': direction * raw_hl if np.isfinite(raw_hl) else np.nan,
                    })
    return pd.DataFrame(rows)


def summarize_screen(wf: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if wf.empty:
        return pd.DataFrame()
    for (feat, target), g in wf.groupby(['feature', 'target']):
        rec = {'feature': feat, 'target': target, 'n_universe_years': len(g)}
        for p in ['DEV_2020_2022', 'CONFIRM_2023_2024', 'BULL_2025', 'YTD_2026']:
            q = g[g['period'].eq(p)]
            rec[f'{p}_median_dic'] = float(q['directed_oos_spearman'].median()) if len(q) else np.nan
            rec[f'{p}_positive_dic_share'] = float((q['directed_oos_spearman'] > 0).mean()) if len(q) else np.nan
            rec[f'{p}_median_dhl'] = float(q['directed_high_minus_low'].median()) if len(q) else np.nan
        q = g[g['period'].eq('CONFIRM_2023_2024')]
        byu = q.groupby('universe')['directed_oos_spearman'].median() if len(q) else pd.Series(dtype=float)
        rec['CONFIRM_positive_universes'] = int((byu > 0).sum())
        rec['CONFIRM_universe_count'] = int(len(byu))
        rec['PASS'] = bool(
            rec['DEV_2020_2022_median_dic'] > 0 and
            rec['CONFIRM_2023_2024_median_dic'] > 0 and
            rec['CONFIRM_positive_universes'] >= 4 and
            rec['CONFIRM_2023_2024_median_dhl'] > 0
        )
        rows.append(rec)
    z = pd.DataFrame(rows)
    return z.sort_values(
        ['PASS', 'CONFIRM_2023_2024_median_dic', 'DEV_2020_2022_median_dic'],
        ascending=[False, False, False]
    ).reset_index(drop=True)


def unconditional(panel: pd.DataFrame) -> pd.DataFrame:
    z = panel.copy()
    z['year'] = z['date'].dt.year
    z['period'] = z['year'].map(period_of)
    rows = []
    for (u, p), g in z[z.year >= EVAL_START_YEAR].groupby(['universe', 'period']):
        rec = {'universe': u, 'period': p, 'n': len(g)}
        for t in TARGETS:
            rec[f'{t}_mean'] = float(g[t].mean())
            rec[f'{t}_median'] = float(g[t].median())
        rows.append(rec)
    return pd.DataFrame(rows)


def fmt(x: float, n: int = 3) -> str:
    return 'NA' if not np.isfinite(x) else f'{x:+.{n}f}'


def report(panel: pd.DataFrame, wf: pd.DataFrame, summary: pd.DataFrame, unc: pd.DataFrame) -> str:
    factors = [c.removeprefix('CUR20_') for c in panel.columns if c.startswith('CUR20_')]
    universes = sorted(panel['universe'].unique())
    lines = [
        '# Zero-Base Factor Persistence / Rotation — Stage 1', '',
        'This screen uses the canonical factor long-short payoff panel directly. No B/F regime labels, KMeans states, previously selected regime thresholds, or future-derived labels are predictors.', '',
        f'- Panel: {panel.date.min().date()} to {panel.date.max().date()}, {len(panel):,} state observations, {len(universes)} universes.',
        f'- Factors: {", ".join(factors)}.',
        '- Annual expanding walk-forward starts in 2020. Predictor direction and tercile thresholds are fitted only on observations before each evaluation year.',
        '- 2025/2026 are stress slices, not pristine untouched OOS.', '',
        '## Predeclared PASS gate', '',
        'A feature-target relation passes only if train-learned direction has positive median OOS Spearman in 2020-22 and again in 2023-24, 2023-24 universe-median directed Spearman is positive in at least 4/6 universes, and the 2023-24 train-threshold high-vs-low target spread has the same directed sign.', ''
    ]
    passes = summary[summary['PASS']]
    lines += [f'## Result: {len(passes)} PASS relations out of {len(summary)} screened', '']
    if len(passes):
        for r in passes.head(20).itertuples(index=False):
            lines.append(
                f'- {r.target} <- {r.feature}: DEV IC {fmt(r.DEV_2020_2022_median_dic)}, '
                f'CONFIRM IC {fmt(r.CONFIRM_2023_2024_median_dic)}, '
                f'CONFIRM H-L {fmt(r.CONFIRM_2023_2024_median_dhl)}, '
                f'positive universes {r.CONFIRM_positive_universes}/{r.CONFIRM_universe_count}, '
                f'2025 IC {fmt(r.BULL_2025_median_dic)}, 2026 IC {fmt(r.YTD_2026_median_dic)}'
            )
    else:
        lines.append('- No relation clears the predeclared gate. Do not build a composite from near-misses.')
    lines += ['', '## Best relations by target', '']
    for target in TARGETS:
        q = summary[summary['target'].eq(target)].sort_values('CONFIRM_2023_2024_median_dic', ascending=False).head(5)
        lines.append(f'### {target}')
        for r in q.itertuples(index=False):
            lines.append(
                f'- {r.feature}: PASS={r.PASS}; DEV {fmt(r.DEV_2020_2022_median_dic)}, '
                f'CONFIRM {fmt(r.CONFIRM_2023_2024_median_dic)}, '
                f'CONFIRM H-L {fmt(r.CONFIRM_2023_2024_median_dhl)}, '
                f'universes {r.CONFIRM_positive_universes}/{r.CONFIRM_universe_count}, '
                f'2025 {fmt(r.BULL_2025_median_dic)}, 2026 {fmt(r.YTD_2026_median_dic)}'
            )
        lines.append('')
    lines += ['## Unconditional target context', '']
    for p in ['DEV_2020_2022', 'CONFIRM_2023_2024', 'BULL_2025', 'YTD_2026']:
        q = unc[unc['period'].eq(p)]
        if q.empty:
            continue
        lines.append(
            f'- {p}: rank-persistence20 median across universes {fmt(q.TARGET_RANK_CORR_20_median.median())}; '
            f'top2-same mean {q.TARGET_TOP2_SAME_20_mean.mean():.1%}; '
            f'factor-momentum20 mean {q.TARGET_FACTOR_MOM_20_mean.mean():+.2%}'
        )
    lines += ['', '## Next step rule', '',
              '- If robust PASS relations exist, Stage 1b should combine only those predeclared survivors in a simple expanding ridge/logistic model and test a non-overlapping 20D factor-momentum-vs-rotation policy.',
              '- If Stage 1 has no robust relation, move to Factor Opportunity rather than tuning thresholds on 2025/2026.']
    return '\n'.join(lines)


def main() -> None:
    panel = build_panel()
    wf = walkforward_screen(panel)
    summary = summarize_screen(wf)
    unc = unconditional(panel)
    panel.to_csv(OUT / 'persistence_rotation_panel.csv', index=False, encoding='utf-8-sig')
    wf.to_csv(OUT / 'univariate_walkforward.csv', index=False, encoding='utf-8-sig')
    summary.to_csv(OUT / 'univariate_summary.csv', index=False, encoding='utf-8-sig')
    unc.to_csv(OUT / 'unconditional_targets.csv', index=False, encoding='utf-8-sig')
    text = report(panel, wf, summary, unc)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
