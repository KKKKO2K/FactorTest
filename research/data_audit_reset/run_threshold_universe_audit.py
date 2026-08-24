from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'source' / 'factor_all_values'
BASIC = DATA / 'reference_snapshots' / 'basic_info'
FACTOR = DATA / '단기모멘텀'
OUT = Path(__file__).resolve().parent / 'results_threshold_universe'
OUT.mkdir(parents=True, exist_ok=True)
CUTOFF_BN = 200.0
STEP = 5


def read_csv(p):
    for enc in ('utf-8-sig','utf-8','cp949','euc-kr'):
        try:
            return pd.read_csv(p, encoding=enc, low_memory=False)
        except Exception:
            pass
    raise RuntimeError(p)


def norm_code(s):
    x=s.astype(str).str.strip().str.replace(r'\.0$','',regex=True)
    return x.where(x.str.startswith('A'),'A'+x.str.zfill(6))


def dated(folder):
    return sorted([p for p in folder.glob('*.csv') if p.stem[:4].isdigit()])

files=dated(BASIC)
sample=files[::STEP]
if files[-1] not in sample: sample.append(files[-1])
rows=[]
for bp in sample:
    dt=bp.stem
    fp=FACTOR/f'{dt}.csv'
    if not fp.exists():
        continue
    b=read_csv(bp)
    f=read_csv(fp)
    b['code']=norm_code(b['Code'])
    b['mcap']=pd.to_numeric(b['시가총액'],errors='coerce')
    b['market']=b['상장된 시장'].astype(str).str.upper().str.strip()
    f_codes=set(norm_code(f['StockCode']))
    # researchable listed common universe proxy = KOSPI/KOSDAQ + PIT mcap cutoff
    eligible=set(b.loc[b['market'].isin(['KOSPI','KOSDAQ']) & b['mcap'].ge(CUTOFF_BN),'code'])
    inter=f_codes & eligible
    union=f_codes | eligible
    factor_only=f_codes-eligible
    elig_only=eligible-f_codes
    rows.append({
        'date':dt,'factor_rows':len(f_codes),'eligible_mcap200':len(eligible),
        'intersection':len(inter),'jaccard':len(inter)/len(union) if union else np.nan,
        'factor_precision_vs_cutoff':len(inter)/len(f_codes) if f_codes else np.nan,
        'cutoff_recall_in_factor':len(inter)/len(eligible) if eligible else np.nan,
        'factor_only':len(factor_only),'eligible_only':len(elig_only),
        'factor_only_examples':';'.join(sorted(factor_only)[:10]),
        'eligible_only_examples':';'.join(sorted(elig_only)[:10]),
    })

df=pd.DataFrame(rows)
df.to_csv(OUT/'threshold_match_by_date.csv',index=False,encoding='utf-8-sig')

summary=[]
for c in ['factor_rows','eligible_mcap200','jaccard','factor_precision_vs_cutoff','cutoff_recall_in_factor','factor_only','eligible_only']:
    s=pd.to_numeric(df[c],errors='coerce')
    summary.append({'metric':c,'mean':s.mean(),'median':s.median(),'p10':s.quantile(.1),'p90':s.quantile(.9),'min':s.min(),'max':s.max()})
pd.DataFrame(summary).to_csv(OUT/'threshold_match_summary.csv',index=False,encoding='utf-8-sig')

# inspect mismatch mcap relative to cutoff
mismatch=[]
for bp in sample:
    dt=bp.stem; fp=FACTOR/f'{dt}.csv'
    if not fp.exists(): continue
    b=read_csv(bp); f=read_csv(fp)
    b['code']=norm_code(b['Code']); b['mcap']=pd.to_numeric(b['시가총액'],errors='coerce'); b['market']=b['상장된 시장'].astype(str).str.upper().str.strip()
    f_codes=set(norm_code(f['StockCode']))
    listed=b[b['market'].isin(['KOSPI','KOSDAQ'])].set_index('code')
    for code in f_codes-set(listed.index[listed.mcap.ge(CUTOFF_BN)]):
        if code in listed.index:
            mismatch.append({'date':dt,'side':'factor_below_cutoff','code':code,'mcap':listed.at[code,'mcap'],'market':listed.at[code,'market']})
    for code in set(listed.index[listed.mcap.ge(CUTOFF_BN)])-f_codes:
        mismatch.append({'date':dt,'side':'eligible_missing_factor','code':code,'mcap':listed.at[code,'mcap'],'market':listed.at[code,'market']})
mm=pd.DataFrame(mismatch)
mm.to_csv(OUT/'threshold_mismatch_rows.csv',index=False,encoding='utf-8-sig')

md=['# PIT Market-Cap Cutoff Audit','',f'User-specified intended universe: KOSPI/KOSDAQ stocks with PIT market cap >= {CUTOFF_BN:.0f} KRW bn.','',f'- Sampled dates: {len(df)} (every {STEP} basic-info dates + endpoint)',f'- Median factor rows: {df.factor_rows.median():.0f}',f'- Median PIT cutoff-eligible rows: {df.eligible_mcap200.median():.0f}',f'- Median Jaccard: {df.jaccard.median():.4f}',f'- Median factor precision vs cutoff: {df.factor_precision_vs_cutoff.median():.2%}',f'- Median cutoff recall in factor rows: {df.cutoff_recall_in_factor.median():.2%}',f'- Median factor-only mismatch: {df.factor_only.median():.0f}',f'- Median cutoff-eligible missing factor: {df.eligible_only.median():.0f}','','Interpretation: a near-1.0 match validates the factor row universe as a point-in-time market-cap-threshold universe, not a top-N/current-survivor universe. Remaining mismatches should be understood from security-type or boundary timing rules before being treated as data defects.']
(OUT/'THRESHOLD_UNIVERSE_AUDIT.md').write_text('\n'.join(md),encoding='utf-8')
print('\n'.join(md))
