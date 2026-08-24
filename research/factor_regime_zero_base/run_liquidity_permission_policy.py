from __future__ import annotations
from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
PANEL=HERE/'results_persistence_rotation/persistence_rotation_panel.csv'
LIQ=HERE.parent/'factor_regime_v1/results/liquidity_states.csv'
OUT=HERE/'results_liquidity_permission_policy';OUT.mkdir(parents=True,exist_ok=True)
FACTORS=['MOM1M','MOM12_1','OP12_REV','OPFY1_REV','PBR12MF','PER12MF','PRIVATE_FLOW','FOREIGN_FLOW']
# Frozen from Stage 4A DEV/CONFIRM only: each passes both TOP2-vs-EW8 alpha and factor-momentum targets.
LIQ_FEATURES=['MKT_ACT1_BREADTH','MKT_ACT1_CHANGE_4','FACTOR_TOP_ACT5_BREADTH_MEAN']
PERSIST_FEATURES=['CROSS_HORIZON_RANK_CORR','PC1_SHARE_60','LEADER_STRENGTH_20','SIGN_ALIGNMENT_20_60','DISPERSION_CHANGE_20','BREADTH_20','DISPERSION_20']
COSTS=[0,10,30]
PERIODS={'DEV_2020_2022':(2020,2022),'CONFIRM_2023_2024':(2023,2024),'BULL_2025':(2025,2025),'YTD_2026':(2026,2026)}

def spearman(x,y):
 z=pd.concat([x,y],axis=1).dropna()
 if len(z)<10 or z.iloc[:,0].nunique()<2 or z.iloc[:,1].nunique()<2:return np.nan
 return float(z.iloc[:,0].rank().corr(z.iloc[:,1].rank()))

def build():
 p=pd.read_csv(PANEL);p['date']=pd.to_datetime(p.date)
 l=pd.read_csv(LIQ);l['date']=pd.to_datetime(l.date);l=l.sort_values(['universe','date']);l['MKT_ACT1_CHANGE_4']=l.groupby('universe').MKT_ACT1_BREADTH.diff(4)
 fwd=p[[f'FWD20_{f}' for f in FACTORS]].to_numpy(float);cur=p[[f'CUR20_{f}' for f in FACTORS]].to_numpy(float);alpha=[]
 for c,y in zip(cur,fwd):
  o=np.argsort(c);top=o[-2:];alpha.append(float(np.mean(y[top])-np.mean(y)))
 p['TARGET_TOP2_ALPHA_VS_EW8_20']=alpha
 return p.merge(l[['date','universe']+LIQ_FEATURES],on=['date','universe'],how='left')

def standardize(tr,te,cols):
 a=tr[cols].astype(float).copy();b=te[cols].astype(float).copy();lo=a.quantile(.01);hi=a.quantile(.99);a=a.clip(lo,hi,axis=1);b=b.clip(lo,hi,axis=1);med=a.median();a=a.fillna(med);b=b.fillna(med);mu=a.mean();sd=a.std(ddof=0).replace(0,1);return (a-mu)/sd,(b-mu)/sd

def dirs(tr,features,target):
 d={}
 for f in features:
  ic=spearman(tr[f],tr[target]);d[f]=1.0 if np.isfinite(ic) and ic>=0 else -1.0
 return pd.Series(d)

def weights(r,mode):
 c=np.array([r[f'CUR20_{f}'] for f in FACTORS],float);o=np.argsort(c);w=np.zeros(len(FACTORS))
 if mode=='TOP2':w[o[-2:]]=.5
 elif mode=='BOTTOM2':w[o[:2]]=.5
 elif mode=='EW8':w[:]=1/len(FACTORS)
 else:raise ValueError(mode)
 return w

def fwdret(r,w):return float(w@np.array([r[f'FWD20_{f}'] for f in FACTORS],float))
def decisions(p):
 rows=[]
 for u,g0 in p.groupby('universe'):
  g=g0.sort_values('date').reset_index(drop=True);g['take']=np.arange(len(g))%4==0
  for year in range(2020,int(g.date.dt.year.max())+1):
   tr=g[g.date<pd.Timestamp(f'{year}-01-01')].copy();te=g[g.date.dt.year.eq(year)].copy()
   tr=tr.dropna(subset=LIQ_FEATURES);te=te.dropna(subset=LIQ_FEATURES)
   if len(tr)<60 or te.empty:continue
   zl_tr,zl_te=standardize(tr,te,LIQ_FEATURES);dl=dirs(tr,LIQ_FEATURES,'TARGET_TOP2_ALPHA_VS_EW8_20');ls_tr=(zl_tr*dl).mean(axis=1);ls_te=(zl_te*dl).mean(axis=1);l67=float(ls_tr.quantile(2/3))
   zp_tr,zp_te=standardize(tr,te,PERSIST_FEATURES);dp=dirs(tr,PERSIST_FEATURES,'TARGET_FACTOR_MOM_20');ps_tr=(zp_tr*dp).mean(axis=1);ps_te=(zp_te*dp).mean(axis=1);p33,p67=ps_tr.quantile([1/3,2/3])
   for idx,r in te.iterrows():
    if not bool(r['take']):continue
    ls=float(ls_te.loc[idx]);ps=float(ps_te.loc[idx]);permission=ls>=l67;persist='TOP2' if ps>=p67 else ('BOTTOM2' if ps<=p33 else 'EW8')
    acts={'LIQ_TOP2_GATE':'TOP2' if permission else 'EW8','PERSIST_LIQ_GATE':persist if permission else 'EW8','PERSIST_ONLY':persist,'TOP2':'TOP2','EW8':'EW8'}
    rec={'date':r.date,'universe':u,'eval_year':year,'liquidity_score':ls,'persist_score':ps,'train_l67':l67,'permission':permission,'persist_action':persist}
    for pol,act in acts.items():
     w=weights(r,act);rec[f'{pol.lower()}_gross']=fwdret(r,w)
     for j,f in enumerate(FACTORS):rec[f'{pol.lower()}_w_{f}']=float(w[j])
    rows.append(rec)
 return pd.DataFrame(rows).sort_values(['universe','date']).reset_index(drop=True)
def cost_path(d):
 out=[];pols=['LIQ_TOP2_GATE','PERSIST_LIQ_GATE','PERSIST_ONLY','TOP2','EW8']
 for u,g0 in d.groupby('universe'):
  g=g0.sort_values('date').copy();turn={}
  for pol in pols:
   W=g[[f'{pol.lower()}_w_{f}' for f in FACTORS]].to_numpy(float);prev=np.zeros(len(FACTORS));v=[]
   for w in W:v.append(.5*float(np.abs(w-prev).sum()));prev=w
   turn[pol]=np.array(v)
  for cost in COSTS:
   z=g.copy();z['cost_bps']=cost
   for pol in pols:z[f'{pol.lower()}_turnover']=turn[pol];z[f'{pol.lower()}_ret']=z[f'{pol.lower()}_gross']-turn[pol]*cost/10000
   out.append(z)
 return pd.concat(out,ignore_index=True)
def perf(r):
 r=pd.Series(r).dropna().astype(float)
 if len(r)<3:return {'cagr':np.nan,'sharpe':np.nan,'mdd':np.nan}
 nav=(1+r).cumprod();ppy=252/20;yrs=len(r)/ppy;c=float(nav.iloc[-1]**(1/yrs)-1) if yrs>0 and nav.iloc[-1]>0 else np.nan;sd=r.std(ddof=1);s=float(r.mean()/sd*np.sqrt(ppy)) if sd>0 else np.nan;return {'cagr':c,'sharpe':s,'mdd':float((nav/nav.cummax()-1).min())}
def summarize(path):
 rows=[];pols=['LIQ_TOP2_GATE','PERSIST_LIQ_GATE','PERSIST_ONLY','TOP2','EW8']
 for cost in COSTS:
  zc=path[path.cost_bps.eq(cost)]
  for per,(a,b) in PERIODS.items():
   for u,g in zc[zc.eval_year.between(a,b)].groupby('universe'):
    if len(g)<3:continue
    r={'universe':u,'cost_bps':cost,'period':per,'n_rebalances':len(g),'permission_share':float(g.permission.mean())}
    for pol in pols:
     m=perf(g[f'{pol.lower()}_ret']);r[f'{pol.lower()}_cagr']=m['cagr'];r[f'{pol.lower()}_sharpe']=m['sharpe'];r[f'{pol.lower()}_mdd']=m['mdd']
    for pol in ['LIQ_TOP2_GATE','PERSIST_LIQ_GATE']:
     x=pol.lower();r[f'{x}_delta_sharpe_vs_ew8']=r[f'{x}_sharpe']-r['ew8_sharpe'];r[f'{x}_delta_cagr_vs_ew8']=r[f'{x}_cagr']-r['ew8_cagr'];r[f'{x}_delta_mdd_vs_ew8']=r[f'{x}_mdd']-r['ew8_mdd'];r[f'{x}_delta_sharpe_vs_persist']=r[f'{x}_sharpe']-r['persist_only_sharpe']
    rows.append(r)
 return pd.DataFrame(rows)
def pct(x):return 'NA' if not np.isfinite(x) else f'{x:+.2%}'
def report(s):
 L=['# Stock-Liquidity Active Permission Policy — Stage 4B','',
 '- Liquidity permission score is frozen to MKT_ACT1_BREADTH, its 4-state change, and FACTOR_TOP_ACT5_BREADTH_MEAN because each passed both Stage-4A TOP2-vs-EW8 alpha and factor-momentum targets in DEV/CONFIRM.',
 '- Directions and the top-tercile permission threshold are estimated only from prior data each year.',
 '- LIQ_TOP2_GATE: TOP2 only when permission is high, otherwise EW8.',
 '- PERSIST_LIQ_GATE: persistence TOP2/BOTTOM2/EW8 action is allowed only when permission is high, otherwise EW8.',
 '- Decisions are non-overlapping 20D and costs apply to one-way factor-sleeve turnover. 2023-24 is feature-selection-contaminated and 2025/26 are previously inspected stress slices.','']
 for cost in COSTS:
  L += [f'## Cost {cost} bps','']
  for per in PERIODS:
   q=s[(s.cost_bps==cost)&(s.period==per)]
   if q.empty:continue
   for pol,label in [('liq_top2_gate','LIQ_TOP2'),('persist_liq_gate','PERSIST×LIQ')]:
    L.append(f'- {per} {label}: median ΔSharpe vs EW8 {q[f"{pol}_delta_sharpe_vs_ew8"].median():+.3f}; ΔCAGR {pct(q[f"{pol}_delta_cagr_vs_ew8"].median())}; ΔMDD {pct(q[f"{pol}_delta_mdd_vs_ew8"].median())}; better Sharpe {(q[f"{pol}_delta_sharpe_vs_ew8"]>0).sum()}/{len(q)}; ΔSharpe vs persistence {q[f"{pol}_delta_sharpe_vs_persist"].median():+.3f}; permission {q.permission_share.median():.1%}')
  L.append('')
 L += ['## 10 bps universe detail — LIQ_TOP2','']
 q=s[s.cost_bps.eq(10)]
 for per in PERIODS:
  L.append(f'### {per}')
  for r in q[q.period.eq(per)].sort_values('universe').itertuples(index=False):L.append(f'- {r.universe}: gate Sharpe {r.liq_top2_gate_sharpe:+.2f} vs EW8 {r.ew8_sharpe:+.2f} (Δ {r.liq_top2_gate_delta_sharpe_vs_ew8:+.2f}); ΔCAGR {pct(r.liq_top2_gate_delta_cagr_vs_ew8)}; permission {r.permission_share:.0%}')
  L.append('')
 L += ['## Interpretation','',
 '- Do not tune the permission threshold after this run. A meaningful result must improve on EW8 broadly and not rely on one calendar slice.',
 '- If the gate fails economically despite Stage-4A IC, the next step is leader-specific raw stock participation/turnover/overlap rather than more aggregate-liquidity transformations.']
 return '\n'.join(L)
def main():
 p=build();d=decisions(p);path=cost_path(d);s=summarize(path);d.to_csv(OUT/'permission_decisions.csv',index=False,encoding='utf-8-sig');path.to_csv(OUT/'permission_path.csv',index=False,encoding='utf-8-sig');s.to_csv(OUT/'permission_summary.csv',index=False,encoding='utf-8-sig');text=report(s);(OUT/'RESEARCH_SUMMARY.md').write_text(text,encoding='utf-8');print(text)
if __name__=='__main__':main()
