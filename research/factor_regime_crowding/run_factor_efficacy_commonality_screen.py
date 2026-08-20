from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / 'results_factor_efficacy_commonality'
OUT.mkdir(parents=True, exist_ok=True)
PANEL_PATH = HERE / 'results/crowding_feature_panel.csv'
FACTOR_PATH = ROOT / 'research/factor_regime_v1/results/factor_5d_returns.csv'
MIXED = 'KOSDAQ_PLUS_KOSPI_EX_K200'

FACTORS = ['OP12_REV','OPFY1_REV','PBR12MF','PER12MF','MOM1M','MOM12_1','PRIVATE_FLOW','FOREIGN_FLOW']
FAMILIES = {
    'REVISION': ['OP12_REV','OPFY1_REV'],
    'VALUE': ['PBR12MF','PER12MF'],
    'MOMENTUM': ['MOM1M','MOM12_1'],
    'FLOW': ['PRIVATE_FLOW','FOREIGN_FLOW'],
}
FEATURE_DIRECTION = {
    'OPFY1_LS20': 'LOW_BAD',
    'OPFY1_LS_RANK20': 'LOW_BAD',
    'OPFY1_MINUS_FACTOR_MEDIAN20': 'LOW_BAD',
    'REVISION_FAMILY_RANK20': 'LOW_BAD',
    'REVISION_MINUS_MOMENTUM20': 'LOW_BAD',
    'OPFY1_SPREAD_SHARE20': 'LOW_BAD',
    'OPFY1_LS_ACCEL20': 'LOW_BAD',
    'AVG_PAIR_CORR_120D': 'HIGH_BAD',
    'PC1_SHARE_120D': 'HIGH_BAD',
    'REV_MOM_CORR_120D': 'HIGH_BAD',
}


def sample_of(dt: pd.Timestamp) -> str:
    if dt.year <= 2019: return 'EARLY_2016_2019'
    if dt.year <= 2022: return 'LATE_2020_2022'
    if dt.year <= 2024: return 'OOS_2023_2024'
    if dt.year == 2025: return 'BULL_2025'
    return 'YTD_2026'


def rolling_compound(x: pd.DataFrame, periods: int) -> pd.DataFrame:
    return (1.0 + x).rolling(periods, min_periods=periods).apply(np.prod, raw=True) - 1.0


def build_panel() -> pd.DataFrame:
    base = pd.read_csv(PANEL_PATH)
    base['date'] = pd.to_datetime(base['date'])
    base = base.sort_values('date').drop_duplicates('date')

    f = pd.read_csv(FACTOR_PATH)
    f['date'] = pd.to_datetime(f['date'])
    f = f[f['universe'].eq(MIXED) & f['factor'].isin(FACTORS)].copy()
    ls5 = f.pivot(index='date', columns='factor', values='ls_return').sort_index().reindex(columns=FACTORS)
    top5 = f.pivot(index='date', columns='factor', values='top_abs_return').sort_index().reindex(columns=FACTORS)
    ls20 = rolling_compound(ls5, 4)
    top20 = rolling_compound(top5, 4)
    prior20 = rolling_compound(ls5.shift(4), 4)

    rows = []
    all_dates = ls5.index.tolist()
    pos = {d: i for i, d in enumerate(all_dates)}
    for dt in base['date']:
        if dt not in ls20.index:
            continue
        r = ls20.loc[dt]
        top = top20.loc[dt]
        if r.notna().sum() < 5:
            continue
        op = float(r['OPFY1_REV']) if pd.notna(r['OPFY1_REV']) else np.nan
        med = float(r.median())
        rank = float(r.rank(pct=True, method='average')['OPFY1_REV']) if pd.notna(op) else np.nan
        fam = {name: float(r[members].mean()) for name, members in FAMILIES.items()}
        fam_s = pd.Series(fam)
        fam_rank = float(fam_s.rank(pct=True, method='average')['REVISION'])
        rev_minus_mom = fam['REVISION'] - fam['MOMENTUM']

        op_top = float(top['OPFY1_REV']) if pd.notna(top['OPFY1_REV']) else np.nan
        op_bottom = op_top - op if np.isfinite(op_top) and np.isfinite(op) else np.nan
        denom = abs(op_top) + abs(op_bottom) if np.isfinite(op_bottom) else np.nan
        spread_share = abs(op) / denom if np.isfinite(denom) and denom > 1e-8 else np.nan
        accel = op - float(prior20.loc[dt, 'OPFY1_REV']) if dt in prior20.index and pd.notna(prior20.loc[dt, 'OPFY1_REV']) and np.isfinite(op) else np.nan

        avg_corr = pc1 = rev_mom_corr = np.nan
        i = pos.get(dt)
        if i is not None and i >= 23:
            w = ls5.iloc[i-23:i+1].dropna(axis=1, thresh=18)
            if w.shape[1] >= 5:
                corr = w.corr().to_numpy(float)
                mask = ~np.eye(corr.shape[0], dtype=bool)
                vals = corr[mask]
                vals = vals[np.isfinite(vals)]
                avg_corr = float(vals.mean()) if len(vals) else np.nan
                eig = np.linalg.eigvalsh(np.nan_to_num(corr, nan=0.0))
                pc1 = float(eig[-1] / eig.sum()) if eig.sum() > 0 else np.nan
            rev = ls5[['OP12_REV','OPFY1_REV']].mean(axis=1).iloc[i-23:i+1]
            mom = ls5[['MOM1M','MOM12_1']].mean(axis=1).iloc[i-23:i+1]
            z = pd.concat([rev.rename('r'), mom.rename('m')], axis=1).dropna()
            if len(z) >= 18:
                rev_mom_corr = float(z.r.corr(z.m))

        rows.append({
            'date': dt,
            'OPFY1_LS20': op,
            'OPFY1_LS_RANK20': rank,
            'OPFY1_MINUS_FACTOR_MEDIAN20': op - med if np.isfinite(op) else np.nan,
            'REVISION_FAMILY_RANK20': fam_rank,
            'REVISION_MINUS_MOMENTUM20': rev_minus_mom,
            'OPFY1_SPREAD_SHARE20': spread_share,
            'OPFY1_LS_ACCEL20': accel,
            'AVG_PAIR_CORR_120D': avg_corr,
            'PC1_SHARE_120D': pc1,
            'REV_MOM_CORR_120D': rev_mom_corr,
        })

    x = base.merge(pd.DataFrame(rows), on='date', how='left')
    x['sample'] = x['date'].map(sample_of)
    x.to_csv(OUT / 'factor_efficacy_commonality_panel.csv', index=False, encoding='utf-8-sig')
    return x


def group_stats(x: pd.DataFrame, flag: pd.Series) -> dict:
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
    }


def run_screen(p: pd.DataFrame) -> pd.DataFrame:
    high = p[p['is_high'].astype(bool)].copy()
    train = high[high['date'] < pd.Timestamp('2023-01-01')]
    rows = []
    for feature, direction in FEATURE_DIRECTION.items():
        tr = train[feature].dropna()
        if len(tr) < 60:
            continue
        q1, q2 = tr.quantile([1/3, 2/3]).tolist()
        cutoff = float(q1 if direction == 'LOW_BAD' else q2)
        rec = {'feature': feature, 'direction': direction, 'train_q1': float(q1), 'train_q2': float(q2), 'train_cutoff': cutoff}
        for sample in ('EARLY_2016_2019','LATE_2020_2022','OOS_2023_2024','BULL_2025','YTD_2026'):
            x = high[high['sample'].eq(sample)].copy()
            flag = x[feature].notna() & ((x[feature] <= cutoff + 1e-12) if direction == 'LOW_BAD' else (x[feature] >= cutoff - 1e-12))
            st = group_stats(x, flag)
            for k,v in st.items(): rec[f'{sample}_{k}'] = v
            if sample == 'YTD_2026':
                neg = x['NET60_FWD20'].notna() & (x['NET60_FWD20'] < 0)
                rec['YTD_2026_negative_n'] = int(neg.sum())
                rec['YTD_2026_negative_capture'] = float(flag[neg].mean()) if neg.any() else np.nan
        rec['pass_early'] = bool(rec.get('EARLY_2016_2019_n_bad',0) >= 8 and rec.get('EARLY_2016_2019_bad_minus_rest',np.nan) < 0)
        rec['pass_late'] = bool(rec.get('LATE_2020_2022_n_bad',0) >= 8 and rec.get('LATE_2020_2022_bad_minus_rest',np.nan) < 0)
        rec['pass_oos'] = bool(rec.get('OOS_2023_2024_n_bad',0) >= 6 and rec.get('OOS_2023_2024_bad_minus_rest',np.nan) < 0)
        rec['pass_2025_control'] = bool(rec.get('BULL_2025_flag_rate',1.0) <= 0.40)
        rec['pass_2026_capture'] = bool(rec.get('YTD_2026_negative_capture',0.0) >= 0.50 and rec.get('YTD_2026_bad_mean',np.nan) < 0)
        rec['SCREEN_PASS'] = all(rec[k] for k in ('pass_early','pass_late','pass_oos','pass_2025_control','pass_2026_capture'))
        rows.append(rec)
    s = pd.DataFrame(rows).sort_values(['SCREEN_PASS','YTD_2026_negative_capture','BULL_2025_flag_rate'], ascending=[False,False,True])
    s.to_csv(OUT / 'factor_efficacy_commonality_screen.csv', index=False, encoding='utf-8-sig')
    return s


def pct(x): return 'NA' if pd.isna(x) else f'{x:+.2%}'


def make_report(p: pd.DataFrame, s: pd.DataFrame) -> str:
    lines = [
        '# Factor Efficacy / Commonality Screen — Mixed OPFY1+CF20', '',
        '- Purpose: distinguish healthy broad factor strength from a state where FACTOR_20D is HIGH but the target OPFY1 factor is weak/lagging or factor returns have collapsed into a common mode.',
        '- All factor-strength metrics use only canonical 5D factor returns through the signal date. 20D metrics compound four 5D observations; correlation/commonality uses the trailing 24 5D observations (~120D).',
        '- Adverse direction is pre-specified: weak OPFY1 / weak Revision-vs-Momentum is bad; high factor-return correlation/commonality is bad.',
        '- Cutoffs are TRAIN 2016-22 HIGH-state terciles only and frozen later.', '', '## Screen results', ''
    ]
    for r in s.itertuples(index=False):
        lines.append(
            f"- {r.feature} ({r.direction}, cutoff={r.train_cutoff:.4f}): early d={pct(r.EARLY_2016_2019_bad_minus_rest)}, "
            f"late d={pct(r.LATE_2020_2022_bad_minus_rest)}, OOS d={pct(r.OOS_2023_2024_bad_minus_rest)}, "
            f"2025 flag={r.BULL_2025_flag_rate:.0%}, 2026 negative capture={r.YTD_2026_negative_capture:.0%}, "
            f"2026 bad mean={pct(r.YTD_2026_bad_mean)}; PASS={bool(r.SCREEN_PASS)}"
        )
    passed = s[s['SCREEN_PASS']]
    lines += ['', '## Passed features', '']
    lines += ['- None.'] if passed.empty else [f'- {x}' for x in passed['feature']]

    lines += ['', '## 2026 HIGH chronology — candidate-specific factor quality', '']
    q = p[p['is_high'].astype(bool) & p['date'].between('2026-01-01','2026-07-31')]
    for r in q.itertuples(index=False):
        lines.append(
            f"- {r.date.date()}: FB={r.value:.3f}; OPFY1_LS20={pct(r.OPFY1_LS20)}; rank={r.OPFY1_LS_RANK20:.2f}; "
            f"Rev-Mom={pct(r.REVISION_MINUS_MOMENTUM20)}; spread_share={r.OPFY1_SPREAD_SHARE20:.2f}; "
            f"avg_corr120={r.AVG_PAIR_CORR_120D:+.2f}; pc1={r.PC1_SHARE_120D:.2f}; fwd20={pct(r.NET60_FWD20)}"
        )
    lines += ['', '## Guardrails', '',
        '- No feature weights or cutoffs are optimized on 2025/2026.',
        '- A passing single feature goes directly to unchanged exact daily-NAV Gross/Net30/Net60 testing; near-miss combinations are not allowed.',
        '- 2023+ is robustness/stress evidence rather than pristine untouched OOS.',
    ]
    return '\n'.join(lines)


def main():
    p = build_panel()
    s = run_screen(p)
    report = make_report(p,s)
    (OUT/'RESEARCH_SUMMARY.md').write_text(report, encoding='utf-8')
    print(report)


if __name__ == '__main__':
    main()
