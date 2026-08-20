from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results_participation_divergence'
OUT.mkdir(parents=True, exist_ok=True)
PANEL_PATH = HERE / 'results/crowding_feature_panel.csv'

BASE_FEATURES = {
    'UNIVERSE_POS20_BREADTH': 'LOW_BAD',
    'SELECTED_POS20_BREADTH': 'LOW_BAD',
    'SELECTED_RET20_DISPERSION': 'HIGH_BAD',
    'SELECTED_TOP5_POS_CONC': 'HIGH_BAD',
}
CANDIDATES = (
    'PARTICIPATION_STRESS_LEVEL',
    'PARTICIPATION_STRESS_ACCEL_4STATE',
    'ADVERSE_CHANGE_COUNT_4STATE',
    'FACTOR_UNIVERSE_BREADTH_DIVERGENCE',
)


def ecdf_score(values: pd.Series, ref: pd.Series) -> pd.Series:
    ref = np.sort(pd.to_numeric(ref, errors='coerce').dropna().to_numpy(float))
    x = pd.to_numeric(values, errors='coerce').to_numpy(float)
    out = np.full(len(x), np.nan)
    if len(ref) == 0:
        return pd.Series(out, index=values.index)
    good = np.isfinite(x)
    out[good] = np.searchsorted(ref, x[good], side='right') / len(ref)
    return pd.Series(out, index=values.index)


def sample_of(dt: pd.Timestamp) -> str:
    if dt.year <= 2019:
        return 'EARLY_2016_2019'
    if dt.year <= 2022:
        return 'LATE_2020_2022'
    if dt.year <= 2024:
        return 'OOS_2023_2024'
    if dt.year == 2025:
        return 'BULL_2025'
    return 'YTD_2026'


def build_candidates() -> pd.DataFrame:
    p = pd.read_csv(PANEL_PATH)
    p['date'] = pd.to_datetime(p['date'])
    p = p.sort_values('date').drop_duplicates('date').reset_index(drop=True)
    p['sample'] = p['date'].map(sample_of)
    train_high = p[p['is_high'].astype(bool) & (p['date'] < pd.Timestamp('2023-01-01'))]

    risk_cols = []
    for feature, direction in BASE_FEATURES.items():
        cdf = ecdf_score(p[feature], train_high[feature])
        risk = 1.0 - cdf if direction == 'LOW_BAD' else cdf
        col = f'RISK_{feature}'
        p[col] = risk
        risk_cols.append(col)

    p['PARTICIPATION_STRESS_LEVEL'] = p[risk_cols].mean(axis=1, skipna=False)
    lagged = p[risk_cols].shift(4)
    deltas = p[risk_cols] - lagged
    p['PARTICIPATION_STRESS_ACCEL_4STATE'] = deltas.mean(axis=1, skipna=False)
    p['ADVERSE_CHANGE_COUNT_4STATE'] = (deltas > 0).sum(axis=1).where(deltas.notna().all(axis=1))
    p['FACTOR_UNIVERSE_BREADTH_DIVERGENCE'] = p['value'] - p['UNIVERSE_POS20_BREADTH']

    p.to_csv(OUT / 'participation_divergence_panel.csv', index=False, encoding='utf-8-sig')
    return p


def stats(x: pd.DataFrame, flag: pd.Series) -> dict:
    good = x['NET60_FWD20'].notna()
    bad = x.loc[good & flag, 'NET60_FWD20']
    rest = x.loc[good & ~flag, 'NET60_FWD20']
    return {
        'n': int(good.sum()),
        'flag_rate': float(flag[good].mean()) if good.any() else np.nan,
        'n_bad': len(bad),
        'n_rest': len(rest),
        'bad_mean': float(bad.mean()) if len(bad) else np.nan,
        'rest_mean': float(rest.mean()) if len(rest) else np.nan,
        'bad_minus_rest': float(bad.mean() - rest.mean()) if len(bad) and len(rest) else np.nan,
        'bad_positive_share': float((bad > 0).mean()) if len(bad) else np.nan,
    }


def run_screen(p: pd.DataFrame) -> pd.DataFrame:
    high = p[p['is_high'].astype(bool)].copy()
    train = high[high['date'] < pd.Timestamp('2023-01-01')]
    rows = []
    for feature in CANDIDATES:
        tr = train[feature].dropna()
        if len(tr) < 60:
            continue
        q1, q2 = tr.quantile([1 / 3, 2 / 3]).tolist()
        cutoff = float(q2)
        rec = {'feature': feature, 'direction': 'HIGH_BAD', 'train_q1': float(q1), 'train_q2': float(q2), 'train_cutoff': cutoff}
        for sample in ('EARLY_2016_2019', 'LATE_2020_2022', 'OOS_2023_2024', 'BULL_2025', 'YTD_2026'):
            x = high[high['sample'].eq(sample)].copy()
            flag = x[feature].notna() & (x[feature] >= cutoff - 1e-12)
            st = stats(x, flag)
            for k, v in st.items():
                rec[f'{sample}_{k}'] = v
            if sample == 'YTD_2026':
                neg = x['NET60_FWD20'].notna() & (x['NET60_FWD20'] < 0)
                rec['YTD_2026_negative_n'] = int(neg.sum())
                rec['YTD_2026_negative_capture'] = float(flag[neg].mean()) if neg.any() else np.nan

        rec['pass_early'] = bool(rec.get('EARLY_2016_2019_n_bad', 0) >= 8 and rec.get('EARLY_2016_2019_bad_minus_rest', np.nan) < 0)
        rec['pass_late'] = bool(rec.get('LATE_2020_2022_n_bad', 0) >= 8 and rec.get('LATE_2020_2022_bad_minus_rest', np.nan) < 0)
        rec['pass_oos'] = bool(rec.get('OOS_2023_2024_n_bad', 0) >= 6 and rec.get('OOS_2023_2024_bad_minus_rest', np.nan) < 0)
        rec['pass_2025_control'] = bool(rec.get('BULL_2025_flag_rate', 1.0) <= 0.40)
        rec['pass_2026_capture'] = bool(rec.get('YTD_2026_negative_capture', 0.0) >= 0.50 and rec.get('YTD_2026_bad_mean', np.nan) < 0)
        rec['SCREEN_PASS'] = all(rec[k] for k in ('pass_early', 'pass_late', 'pass_oos', 'pass_2025_control', 'pass_2026_capture'))
        rows.append(rec)

    s = pd.DataFrame(rows).sort_values(['SCREEN_PASS', 'YTD_2026_negative_capture', 'BULL_2025_flag_rate'], ascending=[False, False, True])
    s.to_csv(OUT / 'participation_divergence_screen.csv', index=False, encoding='utf-8-sig')
    return s


def pct(x):
    return 'NA' if pd.isna(x) else f'{x:+.2%}'


def make_report(p: pd.DataFrame, s: pd.DataFrame) -> str:
    lines = [
        '# Participation Divergence Screen — Mixed OPFY1+CF20', '',
        '- Stage 2 is explicitly post-discovery: Stage 1 showed 2025 vs 2026 separation in stock-level participation/dispersion/concentration, so these results are hypothesis refinement rather than pristine OOS.',
        '- The composite is still mechanically defined: four pre-specified participation-quality features, equal weights, TRAIN-HIGH empirical-CDF scaling only; no return-fitted weights.',
        '- Stress acceleration is the four-state change in that equal-weight risk score. Adverse-change count is the number of the four components deteriorating versus four state observations earlier.',
        '- FACTOR_UNIVERSE_BREADTH_DIVERGENCE is FACTOR_20D breadth minus Mixed-universe trailing-20D positive-stock breadth.',
        '- All cutoffs are 2016-22 HIGH-state 2/3 quantiles and are frozen for later periods.', '',
        '## Screen results', '',
    ]
    for r in s.itertuples(index=False):
        lines.append(
            f"- {r.feature} cutoff={r.train_cutoff:.4f}: early d={pct(r.EARLY_2016_2019_bad_minus_rest)}, "
            f"late d={pct(r.LATE_2020_2022_bad_minus_rest)}, OOS d={pct(r.OOS_2023_2024_bad_minus_rest)}, "
            f"2025 flag={r.BULL_2025_flag_rate:.0%}, 2026 negative capture={r.YTD_2026_negative_capture:.0%}, "
            f"2026 bad mean={pct(r.YTD_2026_bad_mean)}; PASS={bool(r.SCREEN_PASS)}"
        )

    passed = s[s['SCREEN_PASS']]
    lines += ['', '## Passed features', '']
    if passed.empty:
        lines.append('- None.')
    else:
        for f in passed['feature']:
            lines.append(f'- {f}')

    lines += ['', '## 2026 HIGH chronology', '']
    q = p[p['is_high'].astype(bool) & p['date'].between('2026-01-01', '2026-07-31')].copy()
    for r in q.itertuples(index=False):
        fwd = getattr(r, 'NET60_FWD20')
        lines.append(
            f"- {r.date.date()}: FB={r.value:.3f}; stress={r.PARTICIPATION_STRESS_LEVEL:.3f}; "
            f"accel={r.PARTICIPATION_STRESS_ACCEL_4STATE:+.3f}; adverse_count={r.ADVERSE_CHANGE_COUNT_4STATE:.0f}; "
            f"divergence={r.FACTOR_UNIVERSE_BREADTH_DIVERGENCE:+.3f}; fwd20={pct(fwd)}"
        )

    lines += ['', '## Guardrails', '',
        '- Because Stage 2 feature construction was motivated by the observed 2025/2026 contrast, a PASS here is candidate evidence, not final confirmation.',
        '- Do not optimize weights, lag length, or cutoff after seeing this table. A passing specification should go directly to exact daily-NAV testing unchanged.',
    ]
    return '\n'.join(lines)


def main() -> None:
    p = build_candidates()
    s = run_screen(p)
    report = make_report(p, s)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(report, encoding='utf-8')
    print(report)


if __name__ == '__main__':
    main()
