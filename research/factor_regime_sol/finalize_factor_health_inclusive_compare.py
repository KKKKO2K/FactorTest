from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
OUT=HERE/'results_factor_health_inclusive_compare'
PANEL=OUT/'inclusive_health_panel.csv'
SELF=OUT/'own_state_incremental.csv'
TRAIN_END=pd.Timestamp('2023-01-01')
SAMPLES={
'TRAIN_2017_2022':(pd.Timestamp('2017-01-01'),pd.Timestamp('2022-12-31')),
'POST_2023_PLUS':(pd.Timestamp('2023-01-01'),pd.Timestamp('2099-12-31')),
'POST_2023_2024':(pd.Timestamp('2023-01-01'),pd.Timestamp('2024-12-31')),
'BULL_2025':(pd.Timestamp('2025-01-01'),pd.Timestamp('2025-12-31')),
'YTD_2026':(pd.Timestamp('2026-01-01'),pd.Timestamp('2026-12-31'))}
PAIRS=[('FH_A_HEALTHY_BREADTH','FH_A_INCLUSIVE','A'),('FH_B_NET_BREADTH','FH_B_INCLUSIVE','B'),('FH_C_CONTINUOUS','FH_C_INCLUSIVE','C')]

def nw(y,d,lag=3):
 y=np.asarray(y,float);d=np.asarray(d,float);m=np.isfinite(y)&np.isfinite(d);y=y[m];d=d[m]
 if len(y)<12 or len(np.unique(d))<2:return np.nan
 X=np.c_[np.ones(len(y)),d]
 try:inv=np.linalg.inv(X.T@X)
 except:return np.nan
 b=inv@X.T@y;e=y-X@b;S=np.zeros((2,2))
 for i in range(len(y)):S+=e[i]**2*np.outer(X[i],X[i])
 for L in range(1,lag+1):
  w=1-L/(lag+1);G=np.zeros((2,2))
  for i in range(L,len(y)):G+=e[i]*e[i-L]*np.outer(X[i],X[i-L])
  S+=w*(G+G.T)
 V=inv@S@inv;se=math.sqrt(max(V[1,1],0))
 return b[1]/se if se>0 else np.nan

def c_cuts(x):
 cuts={}
 tr=x[x.date<TRAIN_END]
 for (u,t),g in tr.groupby(['universe','target']):
  for m in ['FH_C_CONTINUOUS','FH_C_INCLUSIVE']:
   v=g[m].dropna()
   if len(v)>=30:
    q1,q2=v.quantile([1/3,2/3]).tolist()
    if np.isfinite(q1) and np.isfinite(q2) and q1<q2:cuts[(u,t,m)]=(q1,q2)
 return cuts

def bins(z,m,u,t,cuts):
 if m=='FH_A_HEALTHY_BREADTH':return np.where(z[m]<=1/3,'LOW',np.where(z[m]>=2/3,'HIGH','MID'))
 if m=='FH_A_INCLUSIVE':return np.where(z[m]<=0.25,'LOW',np.where(z[m]>=0.75,'HIGH','MID'))
 if m in ('FH_B_NET_BREADTH','FH_B_INCLUSIVE'):return np.where(z[m]<0,'LOW',np.where(z[m]>0,'HIGH','MID'))
 if (u,t,m) not in cuts:return np.array(['MID']*len(z))
 q1,q2=cuts[(u,t,m)];return np.where(z[m]<=q1,'LOW',np.where(z[m]>=q2,'HIGH','MID'))

def highlow(x):
 cuts=c_cuts(x);rows=[]
 for sample,(lo,hi) in SAMPLES.items():
  z0=x[(x.date>=lo)&(x.date<=hi)]
  for (u,t),g in z0.groupby(['universe','target']):
   g=g.sort_values('date')
   for ex,inc,label in PAIRS:
    for m in [ex,inc]:
     for h in [5,20]:
      for outcome in ['top','spread']:
       ycol=f'{outcome}_fwd{h}';z=g[[m,ycol]].dropna().copy();b=bins(z,m,u,t,cuts)
       keep=np.isin(b,['LOW','HIGH']);z=z.loc[keep];b=np.asarray(b)[keep]
       hy=z.loc[b=='HIGH',ycol];ly=z.loc[b=='LOW',ycol]
       if len(hy)<5 or len(ly)<5:continue
       rows.append({'sample':sample,'universe':u,'target':t,'definition':label,'metric':m,'horizon':h,'outcome':outcome,
       'n_high':len(hy),'n_low':len(ly),'high_mean':hy.mean(),'low_mean':ly.mean(),'high_minus_low':hy.mean()-ly.mean(),'nw_t':nw(z[ycol],(b=='HIGH').astype(float),3 if h==20 else 0)})
 return pd.DataFrame(rows)

def aggregate(hl):
 rows=[]
 for ex,inc,label in PAIRS:
  for sample in SAMPLES:
   a=hl[(hl.metric==ex)&(hl['sample']==sample)&(hl.horizon==20)&(hl.outcome=='top')]
   b=hl[(hl.metric==inc)&(hl['sample']==sample)&(hl.horizon==20)&(hl.outcome=='top')]
   m=a.merge(b,on=['sample','universe','target','horizon','outcome','definition'],suffixes=('_ex','_inc'))
   if m.empty:continue
   rows.append({'definition':label,'sample':sample,'n_pairs':len(m),'ex_median_hl':m.high_minus_low_ex.median(),'inc_median_hl':m.high_minus_low_inc.median(),
   'delta_median':(m.high_minus_low_inc-m.high_minus_low_ex).median(),'ex_positive_share':(m.high_minus_low_ex>0).mean(),'inc_positive_share':(m.high_minus_low_inc>0).mean(),'inc_better_share':(m.high_minus_low_inc>m.high_minus_low_ex).mean()})
 return pd.DataFrame(rows)

def bytarget(hl):
 rows=[]
 for ex,inc,label in PAIRS:
  for sample in SAMPLES:
   for target in sorted(hl.target.unique()):
    a=hl[(hl.metric==ex)&(hl['sample']==sample)&(hl.target==target)&(hl.horizon==20)&(hl.outcome=='top')]
    b=hl[(hl.metric==inc)&(hl['sample']==sample)&(hl.target==target)&(hl.horizon==20)&(hl.outcome=='top')]
    m=a.merge(b,on=['sample','universe','target','horizon','outcome','definition'],suffixes=('_ex','_inc'))
    if m.empty:continue
    rows.append({'definition':label,'sample':sample,'target':target,'n':len(m),'ex_median_hl':m.high_minus_low_ex.median(),'inc_median_hl':m.high_minus_low_inc.median(),'delta':(m.high_minus_low_inc-m.high_minus_low_ex).median()})
 return pd.DataFrame(rows)

def summary(agg,bt,ps):
 L=['# Factor Health: ex-target vs target-inclusive comparison','', 'A/B use discrete-safe breadth thresholds; C uses TRAIN-frozen terciles. Primary lens is future +20D preferred-leg return.','',
 'Inclusive adds the target own state by construction, so any improvement must be interpreted as self-confirmation, not purely cross-factor information.','', '## Aggregate','',
 '| Def | Sample | Ex H-L | Inclusive H-L | Δ | Ex + | Inc + | Inc better |','|---|---|---:|---:|---:|---:|---:|---:|']
 for _,r in agg.iterrows():L.append(f"| {r.definition} | {r['sample']} | {r.ex_median_hl:+.2%} | {r.inc_median_hl:+.2%} | {r.delta_median:+.2%} | {r.ex_positive_share:.0%} | {r.inc_positive_share:.0%} | {r.inc_better_share:.0%} |")
 L+=['','## By target','','| Def | Sample | Target | Ex | Inclusive | Δ |','|---|---|---|---:|---:|---:|']
 for _,r in bt.iterrows():L.append(f"| {r.definition} | {r['sample']} | {r.target} | {r.ex_median_hl:+.2%} | {r.inc_median_hl:+.2%} | {r.delta:+.2%} |")
 L+=['','## Own-state incremental regression','','future top20 ~ standardized ex-target health + standardized own component','', '| Def | Sample | Ex beta | Own beta | Own positive share |','|---|---|---:|---:|---:|']
 for (fam,s),g in ps.groupby(['family','sample']):L.append(f"| {fam} | {s} | {g.ex_beta_per_1sd.median():+.2%} | {g.self_beta_per_1sd.median():+.2%} | {(g.self_beta_per_1sd>0).mean():.0%} |")
 return '\n'.join(L)+'\n'

def main():
 x=pd.read_csv(PANEL);x.date=pd.to_datetime(x.date);ps=pd.read_csv(SELF)
 hl=highlow(x);agg=aggregate(hl);bt=bytarget(hl)
 hl.to_csv(OUT/'high_low_comparison.csv',index=False,encoding='utf-8-sig');agg.to_csv(OUT/'aggregate_comparison.csv',index=False,encoding='utf-8-sig');bt.to_csv(OUT/'by_target_comparison.csv',index=False,encoding='utf-8-sig')
 (OUT/'RESEARCH_SUMMARY.md').write_text(summary(agg,bt,ps),encoding='utf-8')
 print(f'done hl={len(hl)} agg={len(agg)} bt={len(bt)}')
if __name__=='__main__':main()
