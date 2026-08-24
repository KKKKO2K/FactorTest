from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
PANEL=HERE/'results_persistence_rotation/persistence_rotation_panel.csv'
LIQ=HERE.parent/'factor_regime_v1/results/liquidity_states.csv'
OUT=HERE/'results_stock_liquidity_state';OUT.mkdir(parents=True,exist_ok=True)
FACTORS=['MOM1M','MOM12_1','OP12_REV','OPFY1_REV','PBR12MF','PER12MF','PRIVATE_FLOW','FOREIGN_FLOW']
FEATURES=['MKT_ACT5_BREADTH','MKT_ACT1_BREADTH','KOSDAQ_TA_SHARE','FACTOR_TOP_ACT5_BREADTH_MEAN','FACTOR_TOP_MINUS_MKT_ACT5','MKT_ACT5_CHANGE_4','MKT_ACT1_CHANGE_4','KOSDAQ_TA_SHARE_CHANGE_4','FACTOR_TOP_ACT5_CHANGE_4','FACTOR_TOP_MINUS_MKT_ACT5_CHANGE_4']
TARGETS=['TARGET_TOP2_ALPHA_VS_EW8_20','TARGET_FACTOR_MOM_20','TARGET_FWD_RANGE_20','TARGET_TOP2_RELATIVE_LOSS_20']
MIN_TRAIN=60;MIN_TEST=10

def period(y):
 if y<=2022:return 'DEV_2020_2022'
 if y<=2024:return 'CONFIRM_2023_2024'
 if y==2025:return 'BULL_2025'
 return 'YTD_2026'

def spearman(x,y):
 z=pd.concat([x,y],axis=1).dropna()
 if len(z)<3 or z.iloc[:,0].nunique()<2 or z.iloc[:,1].nunique()<2:return np.nan
 return float(z.iloc[:,0].rank().corr(z.iloc[:,1].rank()))

def build():
 p=pd.read_csv(PANEL);p['date']=pd.to_datetime(p.date)
 l=pd.read_csv(LIQ);l['date']=pd.to_datetime(l.date);l=l.sort_values(['universe','date'])
 l['FACTOR_TOP_MINUS_MKT_ACT5']=l.FACTOR_TOP_ACT5_BREADTH_MEAN-l.MKT_ACT5_BREADTH
 change_map={
  'MKT_ACT5_BREADTH':'MKT_ACT5_CHANGE_4',
  'MKT_ACT1_BREADTH':'MKT_ACT1_CHANGE_4',
  'KOSDAQ_TA_SHARE':'KOSDAQ_TA_SHARE_CHANGE_4',
  'FACTOR_TOP_ACT5_BREADTH_MEAN':'FACTOR_TOP_ACT5_CHANGE_4',
  'FACTOR_TOP_MINUS_MKT_ACT5':'FACTOR_TOP_MINUS_MKT_ACT5_CHANGE_4',
 }
 for src,dst in change_map.items():l[dst]=l.groupby('universe')[src].diff(4)
 fwd=p[[f'FWD20_{f}' for f in FACTORS]].to_numpy(float);cur=p[[f'CUR20_{f}' for f in FACTORS]].to_numpy(float)
 top_alpha=[];rng=[];rel_loss=[]
 for c,y in zip(cur,fwd):
  o=np.argsort(c);top=o[-2:];ew=float(np.mean(y));ta=float(np.mean(y[top])-ew)
  top_alpha.append(ta);rel_loss.append(-ta);rng.append(float(y.max()-y.min()))
 p['TARGET_TOP2_ALPHA_VS_EW8_20']=top_alpha;p['TARGET_TOP2_RELATIVE_LOSS_20']=rel_loss;p['TARGET_FWD_RANGE_20']=rng
 return p.merge(l[['date','universe']+FEATURES],on=['date','universe'],how='left')

def screen(z):
 rows=[]
 for u,g in z.groupby('universe'):
  g=g.sort_values('date')
  for year in range(2020,int(g.date.dt.year.max())+1):
   tr=g[g.date<pd.Timestamp(f'{year}-01-01')];te=g[g.date.dt.year.eq(year)]
   for t in TARGETS:
    for f in FEATURES:
     a=tr[[f,t]].dropna();b=te[[f,t]].dropna()
     if len(a)<MIN_TRAIN or len(b)<MIN_TEST:continue
     tic=spearman(a[f],a[t])
     if not np.isfinite(tic) or tic==0:continue
     d=1 if tic>0 else -1;oic=spearman(b[f],b[t]);q33,q67=a[f].quantile([1/3,2/3]);lo=b.loc[b[f]<=q33,t];hi=b.loc[b[f]>=q67,t]
     hl=float(hi.mean()-lo.mean()) if len(lo)>=3 and len(hi)>=3 else np.nan
     rows.append({'universe':u,'eval_year':year,'period':period(year),'feature':f,'target':t,'train_n':len(a),'test_n':len(b),'train_spearman':tic,'direction':d,'oos_spearman':oic,'directed_oos_spearman':d*oic if np.isfinite(oic) else np.nan,'raw_high_minus_low':hl,'directed_high_minus_low':d*hl if np.isfinite(hl) else np.nan})
 return pd.DataFrame(rows)

def summarize(w):
 rows=[]
 for (f,t),g in w.groupby(['feature','target']):
  r={'feature':f,'target':t,'train_direction_median':float(g.direction.median()),'n_universe_years':len(g)}
  for p in ['DEV_2020_2022','CONFIRM_2023_2024','BULL_2025','YTD_2026']:
   q=g[g.period.eq(p)];r[f'{p}_median_dic']=float(q.directed_oos_spearman.median()) if len(q) else np.nan;r[f'{p}_median_dhl']=float(q.directed_high_minus_low.median()) if len(q) else np.nan
  q=g[g.period.eq('CONFIRM_2023_2024')];byu=q.groupby('universe').directed_oos_spearman.median() if len(q) else pd.Series(dtype=float);r['CONFIRM_positive_universes']=int((byu>0).sum());r['CONFIRM_universe_count']=len(byu)
  r['PASS']=bool(r['DEV_2020_2022_median_dic']>0 and r['CONFIRM_2023_2024_median_dic']>0 and r['CONFIRM_2023_2024_median_dhl']>0 and r['CONFIRM_positive_universes']>=4);rows.append(r)
 return pd.DataFrame(rows).sort_values(['PASS','CONFIRM_2023_2024_median_dic'],ascending=[False,False]).reset_index(drop=True)

def fmt(x):return 'NA' if not np.isfinite(x) else f'{x:+.3f}'
def pct(x):return 'NA' if not np.isfinite(x) else f'{x:+.2%}'
def report(z,s):
 L=['# Stock-Level Liquidity State Screen — Zero Base Stage 4A','',
 '- Inputs are point-in-time stock/liquidity aggregates already produced by Factor Regime v1: market ACT5/ACT1 breadth, KOSDAQ trading-amount share, and mean ACT5 support among factor-top stocks. No old regime labels or thresholds are used.',
 '- Added features are factor-top minus market ACT5 support and four-state changes in each liquidity/participation measure.',
 '- Primary economic target is future current-top2-factor alpha vs EW8. Factor momentum, future factor range and top2 relative loss are secondary diagnostics.',
 '- Annual expanding walk-forward; feature direction and tercile thresholds use only prior data. PASS gate matches prior zero-base screens.','',f'## Coverage: {z.date.min().date()} to {z.date.max().date()}','',f'## Result: {int(s.PASS.sum())} PASS relations out of {len(s)} screened','']
 for r in s[s.PASS].head(30).itertuples(index=False):
  sign='HIGH_TARGET' if r.train_direction_median>0 else 'LOW_TARGET'
  L.append(f'- {r.target} <- {r.feature} ({sign}): DEV {fmt(r.DEV_2020_2022_median_dic)}, CONFIRM {fmt(r.CONFIRM_2023_2024_median_dic)}, H-L {pct(r.CONFIRM_2023_2024_median_dhl)}, universes {r.CONFIRM_positive_universes}/{r.CONFIRM_universe_count}, 2025 {fmt(r.BULL_2025_median_dic)}, 2026 {fmt(r.YTD_2026_median_dic)}')
 L += ['','## Best relations for TOP2 alpha vs EW8','']
 for r in s[s.target.eq('TARGET_TOP2_ALPHA_VS_EW8_20')].sort_values('CONFIRM_2023_2024_median_dic',ascending=False).head(10).itertuples(index=False):
  sign='HIGH_GOOD' if r.train_direction_median>0 else 'LOW_GOOD';L.append(f'- {r.feature} ({sign}): PASS={r.PASS}; DEV {fmt(r.DEV_2020_2022_median_dic)}, CONFIRM {fmt(r.CONFIRM_2023_2024_median_dic)}, H-L {pct(r.CONFIRM_2023_2024_median_dhl)}, universes {r.CONFIRM_positive_universes}/{r.CONFIRM_universe_count}, 2025 {fmt(r.BULL_2025_median_dic)}, 2026 {fmt(r.YTD_2026_median_dic)}')
 L += ['','## Next step','',
 '- If liquidity-state predictors add stable TOP2-vs-EW8 information, combine only those survivors with the persistence score as an active-risk permission signal.',
 '- If these aggregate liquidity states fail, reconstruct leader-specific stock participation/turnover/overlap from raw point-in-time factor holdings; do not tune the existing factor-return thresholds.']
 return '\n'.join(L)
def main():
 z=build();w=screen(z);s=summarize(w);z.to_csv(OUT/'stock_liquidity_panel.csv',index=False,encoding='utf-8-sig');w.to_csv(OUT/'stock_liquidity_walkforward.csv',index=False,encoding='utf-8-sig');s.to_csv(OUT/'stock_liquidity_summary.csv',index=False,encoding='utf-8-sig');text=report(z,s);(OUT/'RESEARCH_SUMMARY.md').write_text(text,encoding='utf-8');print(text)
if __name__=='__main__':main()
