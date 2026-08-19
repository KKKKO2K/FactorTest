from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
NESTED = ROOT / 'research' / 'factor_regime_contemporaneous_states' / 'results' / 'nested_state_assignments.csv'
PANEL = ROOT / 'research' / 'factor_regime_action_policy' / 'results' / 'finalist_regime_diagnostics' / 'candidate_state_forward_panel.csv'
OUT = ROOT / 'research' / 'factor_regime_action_policy' / 'results' / 'high_breadth_feature_diagnostics'
OUT.mkdir(parents=True, exist_ok=True)

MIXED = 'KOSDAQ_PLUS_KOSPI_EX_K200'
FEATURES = [
    'MKT_RET_20D',
    'MKT_RET_60D',
    'MKT_VOL_20D',
    'MKT_DD_60D',
    'LIQ_5D_20D',
    'RELATIVE_WORKING_BREADTH',
    'ABS_CONFIRMED_BREADTH',
    'DEFENSIVE_WORKING_BREADTH',
    'WPLUS_PAIR_SHARE',
    'CONFLICT_PAIR_SHARE',
    'LEADER_STRENGTH_60D',
    'SPREAD_DISPERSION_20D',
    'FAMILY_MEMBER_AGREEMENT',
    'MKT_MOM_ACCEL',
]
SAMPLES = ('TRAIN_2016_2022', 'OOS_2023_2024', 'BULL_2025', 'YTD_2026')


def spearman(a: pd.Series, b: pd.Series) -> float:
    x = pd.concat([a, b], axis=1).dropna()
    if len(x) < 8 or x.iloc[:, 0].nunique() < 3 or x.iloc[:, 1].nunique() < 3:
        return np.nan
    return float(x.iloc[:, 0].rank().corr(x.iloc[:, 1].rank()))


def load_high_panel() -> pd.DataFrame:
    p = pd.read_csv(PANEL)
    p['date'] = pd.to_datetime(p['date'])
    p = p[(p['return_type'].eq('NET60')) & (p['horizon'].eq(20))].copy()

    n = pd.read_csv(NESTED, encoding='utf-8-sig')
    n['date'] = pd.to_datetime(n['date'])
    n = n[n['universe'].eq(MIXED)].copy()
    n['MKT_MOM_ACCEL'] = n['MKT_RET_20D'] - n['MKT_RET_60D'] / 3.0

    cols = ['date'] + [x for x in FEATURES if x in n.columns]
    x = p.merge(n[cols], on='date', how='left')
    x = x[x['breadth_bin'].eq('HIGH')].copy()
    return x


def diagnostics(x: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    threshold_rows = []
    sample_rows = []
    train = x[x['sample'].eq('TRAIN_2016_2022')]

    for feature in FEATURES:
        t = train[[feature, 'fwd_mean_across_phases']].dropna()
        if len(t) < 30 or t[feature].nunique() < 3:
            continue
        q1, q2 = t[feature].quantile([1 / 3, 2 / 3]).tolist()
        rho = spearman(t[feature], t['fwd_mean_across_phases'])
        if pd.isna(rho):
            continue
        bad_direction = 'HIGH_BAD' if rho < 0 else 'LOW_BAD'
        threshold = q2 if bad_direction == 'HIGH_BAD' else q1
        threshold_rows.append({
            'feature': feature,
            'train_n': len(t),
            'train_spearman': rho,
            'q1': q1,
            'q2': q2,
            'bad_direction': bad_direction,
            'frozen_threshold': threshold,
        })

        for sample in SAMPLES:
            g = x[x['sample'].eq(sample)][[feature, 'fwd_mean_across_phases']].dropna().copy()
            if g.empty:
                continue
            bad = g[feature].ge(threshold) if bad_direction == 'HIGH_BAD' else g[feature].le(threshold)
            gb = g[bad]
            gr = g[~bad]
            sample_rows.append({
                'feature': feature,
                'sample': sample,
                'bad_direction': bad_direction,
                'frozen_threshold': threshold,
                'n_high_dates': len(g),
                'n_bad': len(gb),
                'bad_share': len(gb) / len(g),
                'bad_mean_fwd20': float(gb.fwd_mean_across_phases.mean()) if len(gb) else np.nan,
                'bad_median_fwd20': float(gb.fwd_mean_across_phases.median()) if len(gb) else np.nan,
                'bad_positive_share': float((gb.fwd_mean_across_phases > 0).mean()) if len(gb) else np.nan,
                'rest_mean_fwd20': float(gr.fwd_mean_across_phases.mean()) if len(gr) else np.nan,
                'rest_positive_share': float((gr.fwd_mean_across_phases > 0).mean()) if len(gr) else np.nan,
                'bad_minus_rest': float(gb.fwd_mean_across_phases.mean() - gr.fwd_mean_across_phases.mean()) if len(gb) and len(gr) else np.nan,
                'feature_median_all_high': float(g[feature].median()),
            })
    return pd.DataFrame(threshold_rows), pd.DataFrame(sample_rows)


def score_candidates(th: pd.DataFrame, sm: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in th.iterrows():
        f = r.feature
        z = sm[sm.feature.eq(f)].set_index('sample')
        rec = {
            'feature': f,
            'train_spearman': r.train_spearman,
            'bad_direction': r.bad_direction,
            'frozen_threshold': r.frozen_threshold,
        }
        for s in SAMPLES:
            if s in z.index:
                q = z.loc[s]
                rec[f'{s}_bad_share'] = q.bad_share
                rec[f'{s}_bad_mean'] = q.bad_mean_fwd20
                rec[f'{s}_rest_mean'] = q.rest_mean_fwd20
                rec[f'{s}_delta'] = q.bad_minus_rest
            else:
                rec[f'{s}_bad_share'] = np.nan
                rec[f'{s}_bad_mean'] = np.nan
                rec[f'{s}_rest_mean'] = np.nan
                rec[f'{s}_delta'] = np.nan
        rec['train_oos_same_bad_sign'] = bool(
            rec.get('TRAIN_2016_2022_delta', np.nan) < 0
            and rec.get('OOS_2023_2024_delta', np.nan) < 0
        )
        rec['healthy_2025_filter'] = bool(rec.get('BULL_2025_bad_share', 1.0) <= 0.35)
        rec['captures_2026'] = bool(
            rec.get('YTD_2026_bad_share', 0.0) >= 0.50
            and rec.get('YTD_2026_bad_mean', np.nan) < 0
        )
        rec['screen_pass'] = bool(rec['train_oos_same_bad_sign'] and rec['healthy_2025_filter'] and rec['captures_2026'])
        rows.append(rec)
    return pd.DataFrame(rows)


def pct(v: float) -> str:
    return 'NA' if pd.isna(v) else f'{v:+.2%}'


def report(score: pd.DataFrame, sm: pd.DataFrame) -> str:
    lines = [
        '# HIGH-Breadth Feature Diagnostics — Mixed OPFY1+CF20',
        '',
        'Universe is restricted to dates where frozen FACTOR_20D is HIGH. For each existing regime feature, the adverse direction and 1/3 or 2/3 cutoff are chosen using TRAIN 2016-22 only.',
        'The screen then asks whether that frozen adverse extreme remains worse in 2023-24, avoids flagging most healthy 2025 HIGH dates, and captures at least half of 2026 HIGH dates with negative forward 20D finalist return.',
        'This is exploratory feature screening, not a production rule; multiple-testing risk remains.',
        '',
        '## Screen results',
        '',
    ]
    z = score.sort_values(['screen_pass', 'captures_2026', 'train_oos_same_bad_sign'], ascending=False)
    for _, r in z.iterrows():
        lines.append(
            f"- {r.feature}: TRAIN rho {r.train_spearman:+.2f}, {r.bad_direction}, cutoff {r.frozen_threshold:.4f}; "
            f"TRAIN bad-rest {pct(r.TRAIN_2016_2022_delta)}, OOS {pct(r.OOS_2023_2024_delta)}, "
            f"2025 flagged {r.BULL_2025_bad_share:.0%}, 2026 flagged {r.YTD_2026_bad_share:.0%}, "
            f"2026 bad mean {pct(r.YTD_2026_bad_mean)}; SCREEN={'PASS' if r.screen_pass else 'NO'}"
        )

    passed = z[z.screen_pass]
    lines += ['', '## Passed features', '']
    if passed.empty:
        lines.append('- None. Existing continuous regime features do not cleanly separate healthy 2025 HIGH from 2026 breakdown under this frozen screen.')
    else:
        for _, r in passed.iterrows():
            lines.append(f"- {r.feature}: candidate for confirmatory interaction testing.")

    lines += [
        '',
        '## Guardrails',
        '',
        '- Do not combine multiple features merely because they look good here; that would compound selection bias.',
        '- A passed feature must next be tested as a single pre-specified interaction on full daily NAV with the same 10 phase and Net30/Net60 framework.',
        '- 2025 is used here specifically as a healthy-bull false-positive control, not as optimization target.',
        '',
    ]
    return '\n'.join(lines)


def main() -> None:
    x = load_high_panel()
    th, sm = diagnostics(x)
    score = score_candidates(th, sm)
    x.to_csv(OUT / 'high_feature_panel.csv', index=False, encoding='utf-8', lineterminator='\n')
    th.to_csv(OUT / 'train_frozen_thresholds.csv', index=False, encoding='utf-8', lineterminator='\n')
    sm.to_csv(OUT / 'feature_sample_diagnostics.csv', index=False, encoding='utf-8', lineterminator='\n')
    score.to_csv(OUT / 'feature_screen.csv', index=False, encoding='utf-8', lineterminator='\n')
    text = report(score, sm)
    (OUT / 'RESEARCH_SUMMARY.md').write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
