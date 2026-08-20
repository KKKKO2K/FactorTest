from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/liquidity_cross_factor'))

import run_cross_factor_liquidity as base

HERE = Path(__file__).resolve().parent
OUT = HERE / 'results_raw_revision_diffusion'
OUT.mkdir(parents=True, exist_ok=True)
PANEL_PATH = HERE / 'results/crowding_feature_panel.csv'
HOLD_DIR = ROOT / 'research/stock_level_factor_interaction/results_cf20_portfolio_audit/sleeve_holdings_compact_parts'
MIXED = 'KOSDAQ_PLUS_KOSPI_EX_K200'

FEATURE_DIRECTION = {
    'OPFY1_POS_BREADTH': 'LOW_BAD',
    'OPFY1_MEDIAN_RAW': 'LOW_BAD',
    'OPFY1_P75_RAW': 'LOW_BAD',
    'OP12_POS_BREADTH': 'LOW_BAD',
    'DUAL_UPGRADE_BREADTH': 'LOW_BAD',
    'SELECTED_OPFY1_POS_SHARE': 'LOW_BAD',
    'SELECTED_OPFY1_MEDIAN_RAW': 'LOW_BAD',
    'SELECTED_DUAL_UPGRADE_SHARE': 'LOW_BAD',
    'OPFY1_POS_BREADTH_ACCEL_4STATE': 'LOW_BAD',
    'SELECTED_OPFY1_MEDIAN_ACCEL_4STATE': 'LOW_BAD',
}


def sample_of(dt: pd.Timestamp) -> str:
    if dt.year <= 2019: return 'EARLY_2016_2019'
    if dt.year <= 2022: return 'LATE_2020_2022'
    if dt.year <= 2024: return 'OOS_2023_2024'
    if dt.year == 2025: return 'BULL_2025'
    return 'YTD_2026'


def load_holdings() -> dict[pd.Timestamp, list[str]]:
    parts = sorted(HOLD_DIR.glob('*.csv.gz'))
    if not parts:
        raise FileNotFoundError(HOLD_DIR)
    h = pd.concat([pd.read_csv(p) for p in parts], ignore_index=True)
    h['date'] = pd.to_datetime(h['date'])
    q = h[
        h['universe'].eq(MIXED)
        & h['strategy'].eq('CF20')
        & h['factor'].eq('OPFY1_REV')
    ][['date','codes']].drop_duplicates('date')
    return {r.date: str(r.codes).split('|') for r in q.itertuples(index=False)}


def load_mixed_codes(dt: pd.Timestamp) -> pd.Index:
    p = base.BASIC / f'{dt.date().isoformat()}.csv'
    if not p.exists():
        return pd.Index([])
    df = base.read_csv(p)
    cc = base.code_col(df)
    kc = base.find_col(df, contains=('코스피200','k200'))
    mc = base.find_col(df, exact=('상장된 시장',), contains=('상장된 시장','market'))
    if kc is None or mc is None:
        return pd.Index([])
    codes = base.norm_code(df[cc])
    k = pd.to_numeric(df[kc], errors='coerce').fillna(0).astype(int)
    market = df[mc].astype(str).str.upper().str.strip()
    mask = market.isin(['KOSPI','KOSDAQ']) & k.eq(0)
    return pd.Index(codes[mask].dropna().unique())


def load_raw(factor: str, dt: pd.Timestamp) -> pd.Series:
    p = base.FACTORS[factor] / f'{dt.date().isoformat()}.csv'
    if not p.exists():
        return pd.Series(dtype=float)
    return base.load_factor(p)


def build_panel() -> pd.DataFrame:
    p = pd.read_csv(PANEL_PATH)
    p['date'] = pd.to_datetime(p['date'])
    p = p.sort_values('date').drop_duplicates('date').reset_index(drop=True)
    holdings = load_holdings()
    rows = []
    for dt in p['date']:
        codes = load_mixed_codes(dt)
        selected = holdings.get(dt, [])
        if len(codes) < 100 or len(selected) != 20:
            continue
        fy1 = pd.to_numeric(load_raw('OPFY1_REV', dt).reindex(codes), errors='coerce')
        op12 = pd.to_numeric(load_raw('OP12_REV', dt).reindex(codes), errors='coerce')
        z = pd.concat([fy1.rename('fy1'), op12.rename('op12')], axis=1)
        if z.fy1.notna().sum() < 80:
            continue
        sel = z.reindex(selected)
        rows.append({
            'date': dt,
            'OPFY1_POS_BREADTH': float((z.fy1.dropna() > 0).mean()),
            'OPFY1_MEDIAN_RAW': float(z.fy1.median()),
            'OPFY1_P75_RAW': float(z.fy1.quantile(.75)),
            'OP12_POS_BREADTH': float((z.op12.dropna() > 0).mean()) if z.op12.notna().sum() >= 80 else np.nan,
            'DUAL_UPGRADE_BREADTH': float(((z.fy1 > 0) & (z.op12 > 0)).mean()) if z.op12.notna().sum() >= 80 else np.nan,
            'SELECTED_OPFY1_POS_SHARE': float((sel.fy1.dropna() > 0).mean()) if sel.fy1.notna().sum() >= 15 else np.nan,
            'SELECTED_OPFY1_MEDIAN_RAW': float(sel.fy1.median()) if sel.fy1.notna().sum() >= 15 else np.nan,
            'SELECTED_DUAL_UPGRADE_SHARE': float(((sel.fy1 > 0) & (sel.op12 > 0)).mean()) if sel[['fy1','op12']].notna().all(axis=1).sum() >= 15 else np.nan,
        })
    r = pd.DataFrame(rows).sort_values('date')
    for c in ('OPFY1_POS_BREADTH','SELECTED_OPFY1_MEDIAN_RAW'):
        r[f'{c}_ACCEL_4STATE'] = r[c] - r[c].shift(4)
    r = r.rename(columns={
        'OPFY1_POS_BREADTH_ACCEL_4STATE': 'OPFY1_POS_BREADTH_ACCEL_4STATE',
        'SELECTED_OPFY1_MEDIAN_RAW_ACCEL_4STATE': 'SELECTED_OPFY1_MEDIAN_ACCEL_4STATE',
    })
    x = p.merge(r, on='date', how='left')
    x['sample'] = x['date'].map(sample_of)
    x.to_csv(OUT/'raw_revision_diffusion_panel.csv', index=False, encoding='utf-8-sig')
    return x


def group_stats(x: pd.DataFrame, flag: pd.Series) -> dict:
    good = x['NET60_FWD20'].notna()
    bad = x.loc[good & flag, 'NET60_FWD20']
    rest = x.loc[good & ~flag, 'NET60_FWD20']
    return {
        'n': int(good.sum()), 'flag_rate': float(flag[good].mean()) if good.any() else np.nan,
        'n_bad': len(bad), 'n_rest': len(rest),
        'bad_mean': float(bad.mean()) if len(bad) else np.nan,
        'rest_mean': float(rest.mean()) if len(rest) else np.nan,
        'bad_minus_rest': float(bad.mean()-rest.mean()) if len(bad) and len(rest) else np.nan,
    }


def run_screen(p: pd.DataFrame) -> pd.DataFrame:
    high = p[p['is_high'].astype(bool)].copy()
    train = high[high['date'] < pd.Timestamp('2023-01-01')]
    rows=[]
    for feature,direction in FEATURE_DIRECTION.items():
        if feature not in p.columns:
            continue
        tr=train[feature].dropna()
        if len(tr)<60:
            continue
        q1,q2=tr.quantile([1/3,2/3]).tolist()
        cutoff=float(q1 if direction=='LOW_BAD' else q2)
        rec={'feature':feature,'direction':direction,'train_q1':float(q1),'train_q2':float(q2),'train_cutoff':cutoff}
        for sample in ('EARLY_2016_2019','LATE_2020_2022','OOS_2023_2024','BULL_2025','YTD_2026'):
            x=high[high['sample'].eq(sample)].copy()
            flag=x[feature].notna() & ((x[feature]<=cutoff+1e-12) if direction=='LOW_BAD' else (x[feature]>=cutoff-1e-12))
            st=group_stats(x,flag)
            for k,v in st.items(): rec[f'{sample}_{k}']=v
            if sample=='YTD_2026':
                neg=x['NET60_FWD20'].notna() & (x['NET60_FWD20']<0)
                rec['YTD_2026_negative_n']=int(neg.sum())
                rec['YTD_2026_negative_capture']=float(flag[neg].mean()) if neg.any() else np.nan
        rec['pass_early']=bool(rec.get('EARLY_2016_2019_n_bad',0)>=8 and rec.get('EARLY_2016_2019_bad_minus_rest',np.nan)<0)
        rec['pass_late']=bool(rec.get('LATE_2020_2022_n_bad',0)>=8 and rec.get('LATE_2020_2022_bad_minus_rest',np.nan)<0)
        rec['pass_oos']=bool(rec.get('OOS_2023_2024_n_bad',0)>=6 and rec.get('OOS_2023_2024_bad_minus_rest',np.nan)<0)
        rec['pass_2025_control']=bool(rec.get('BULL_2025_flag_rate',1.0)<=.40)
        rec['pass_2026_capture']=bool(rec.get('YTD_2026_negative_capture',0.0)>=.50 and rec.get('YTD_2026_bad_mean',np.nan)<0)
        rec['SCREEN_PASS']=all(rec[k] for k in ('pass_early','pass_late','pass_oos','pass_2025_control','pass_2026_capture'))
        rows.append(rec)
    s=pd.DataFrame(rows).sort_values(['SCREEN_PASS','YTD_2026_negative_capture','BULL_2025_flag_rate'],ascending=[False,False,True])
    s.to_csv(OUT/'raw_revision_diffusion_screen.csv',index=False,encoding='utf-8-sig')
    return s


def pct(x): return 'NA' if pd.isna(x) else f'{x:+.2%}'


def make_report(p,s):
    lines=['# Raw Revision Diffusion Screen — Mixed OPFY1+CF20','',
        '- This is the final early-warning screen using the factor input itself rather than realized factor returns or later stock participation.',
        '- Raw OPFY1/OP12 FactorValue is read at the signal close. Positive breadth means the share of Mixed stocks with positive revision; selected metrics use the actual OPFY1+CF20 top20 from the precomputed holdings audit.',
        '- Adverse direction is pre-specified: narrow/weaker revision diffusion or deterioration versus four state observations earlier is bad.',
        '- Cutoffs are TRAIN 2016-22 HIGH-state terciles only and frozen later. Same strict split/OOS/2025-control/2026-capture gate is used.','','## Screen results','']
    for r in s.itertuples(index=False):
        lines.append(f'- {r.feature} cutoff={r.train_cutoff:.4f}: early d={pct(r.EARLY_2016_2019_bad_minus_rest)}, late d={pct(r.LATE_2020_2022_bad_minus_rest)}, OOS d={pct(r.OOS_2023_2024_bad_minus_rest)}, 2025 flag={r.BULL_2025_flag_rate:.0%}, 2026 negative capture={r.YTD_2026_negative_capture:.0%}, 2026 bad mean={pct(r.YTD_2026_bad_mean)}; PASS={bool(r.SCREEN_PASS)}')
    passed=s[s.SCREEN_PASS]
    lines+=['','## Passed features','']+(['- None.'] if passed.empty else [f'- {f}' for f in passed.feature])
    lines+=['','## 2026 HIGH chronology — raw revision diffusion','']
    q=p[p.is_high.astype(bool)&p.date.between('2026-01-01','2026-07-31')]
    for r in q.itertuples(index=False):
        lines.append(f'- {r.date.date()}: FB={r.value:.3f}; FY1 breadth={r.OPFY1_POS_BREADTH:.2f}; FY1 median={r.OPFY1_MEDIAN_RAW:+.3f}; dual breadth={r.DUAL_UPGRADE_BREADTH:.2f}; selected FY1+={r.SELECTED_OPFY1_POS_SHARE:.2f}; selected median={r.SELECTED_OPFY1_MEDIAN_RAW:+.3f}; selected dual={r.SELECTED_DUAL_UPGRADE_SHARE:.2f}; breadth accel={r.OPFY1_POS_BREADTH_ACCEL_4STATE:+.2f}; fwd20={pct(r.NET60_FWD20)}')
    lines+=['','## Guardrails','',
        '- Do not combine near-misses if none passes. Failure here means the current data stack does not support a robust ex-ante OPFY1 breakdown timer.',
        '- Any single passing feature must be tested unchanged on exact daily NAV before production use.',
    ]
    return '\n'.join(lines)


def main():
    p=build_panel(); s=run_screen(p); report=make_report(p,s)
    (OUT/'RESEARCH_SUMMARY.md').write_text(report,encoding='utf-8'); print(report)

if __name__=='__main__': main()
