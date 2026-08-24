from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/'source'/'factor_all_values'
BASIC=DATA/'reference_snapshots'/'basic_info'
FACTOR=DATA/'단기모멘텀'
OUT=Path(__file__).resolve().parent/'results_threshold_grid'
OUT.mkdir(parents=True,exist_ok=True)
THRESHOLDS=[150,175,200,225,250,275,300,325,350]
STEP=5

def read_csv(p):
    for enc in ('utf-8-sig','utf-8','cp949','euc-kr'):
        try:return pd.read_csv(p,encoding=enc,low_memory=False)
        except Exception:pass
    raise RuntimeError(p)
def norm(s):
    x=s.astype(str).str.strip().str.replace(r'\.0$','',regex=True)
    return x.where(x.str.startswith('A'),'A'+x.str.zfill(6))

files=sorted(BASIC.glob('*.csv'))
sample=files[::STEP]
if files[-1] not in sample:sample.append(files[-1])
rows=[]
for bp in sample:
    fp=FACTOR/f'{bp.stem}.csv'
    if not fp.exists():continue
    b=read_csv(bp); f=read_csv(fp)
    b['code']=norm(b['Code']); b['mcap']=pd.to_numeric(b['시가총액'],errors='coerce'); b['market']=b['상장된 시장'].astype(str).str.upper().str.strip()
    listed=b[b.market.isin(['KOSPI','KOSDAQ'])]
    fs=set(norm(f['StockCode']))
    for th in THRESHOLDS:
        es=set(listed.loc[listed.mcap.ge(th),'code'])
        inter=fs&es; union=fs|es
        rows.append({'date':bp.stem,'threshold_bn':th,'factor_rows':len(fs),'eligible':len(es),'jaccard':len(inter)/len(union) if union else np.nan,'precision':len(inter)/len(fs) if fs else np.nan,'recall':len(inter)/len(es) if es else np.nan,'factor_only':len(fs-es),'eligible_only':len(es-fs)})

df=pd.DataFrame(rows); df.to_csv(OUT/'threshold_grid_by_date.csv',index=False,encoding='utf-8-sig')
s=[]
for th,g in df.groupby('threshold_bn'):
    s.append({'threshold_bn':th,'median_jaccard':g.jaccard.median(),'median_precision':g.precision.median(),'median_recall':g.recall.median(),'median_factor_only':g.factor_only.median(),'median_eligible_only':g.eligible_only.median(),'mean_jaccard':g.jaccard.mean()})
sm=pd.DataFrame(s).sort_values('threshold_bn'); sm.to_csv(OUT/'threshold_grid_summary.csv',index=False,encoding='utf-8-sig')
best=sm.loc[sm.median_jaccard.idxmax()]
lines=['# Market-cap Threshold Grid Audit','',f'- Dates sampled: {len(sample)}',f'- Best median-Jaccard threshold: {best.threshold_bn:.0f} KRW bn',f'- Best median Jaccard: {best.median_jaccard:.4f}',f'- Precision: {best.median_precision:.2%}',f'- Recall: {best.median_recall:.2%}','','| Cutoff (bn KRW) | Median Jaccard | Precision | Recall | Factor-only | Eligible-only |','|---:|---:|---:|---:|---:|---:|']
for _,r in sm.iterrows():
    lines.append(f"| {r.threshold_bn:.0f} | {r.median_jaccard:.4f} | {r.median_precision:.2%} | {r.median_recall:.2%} | {r.median_factor_only:.0f} | {r.median_eligible_only:.0f} |")
(OUT/'THRESHOLD_GRID_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')
print('\n'.join(lines))
