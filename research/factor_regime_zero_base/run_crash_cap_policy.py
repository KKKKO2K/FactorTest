from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
INP=HERE/'results_persistence_rotation/persistence_rotation_panel.csv'
OUT=HERE/'results_crash_cap_policy';OUT.mkdir(parents=True,exist_ok=True)
FACTORS=['MOM1M','MOM12_1','OP12_REV','OPFY1_REV','PBR12MF','PER12MF','PRIVATE_FLOW','FOREIGN_FLOW']
PERSIST_FEATURES=['CROSS_HORIZON_RANK_CORR','PC1_SHARE_60','LEADER_STRENGTH_20','SIGN_ALIGNMENT_20_60','DISPERSION_CHANGE_20','BREADTH_20','DISPERSION_20']
# Frozen from Stage-3 DEV/CONFIRM evidence: each passed current-top2 relative-loss and at least one additional adverse target.
CRASH_FEATURES=['LOSER_WEAKNESS_20','DISPERSION_20','TOP2_PREMIUM_20']
COSTS=[0,10,30]
PERIODS={'DEV_2020_2022':(2020,2022),'CONFIRM_2023_2024':(2023,2024),'BULL_2025':(2025,2025),'YTD_2026':(2026,2026)}


def spearman(x,y):
 z=pd.concat([x,y],axis=1).dropna()
 if len(z)<10 or z.iloc[:,0].nunique()<2 or z.iloc[:,1].nunique()<2:return np.nan
 return float(z.iloc[:,0].rank().corr(z.iloc[:,1].rank()))


def enrich(p):
 z=p.copy();cur=z[[f'CUR20_{f}' for f in FACTORS]].to_numpy(float);fwd=z[[f'FWD20_{f}' for f in FACTORS]].to_numpy(float)
 prem=[];loss=[]
 for c,y in zip(cur,fwd):
  o=np.argsort(c);top=o[-2:];med=np.median(c)
  prem.append(float(np.mean(c[top])-med));loss.append(float(np.mean(y)-np.mean(y[top])))
 z['TOP2_PREMIUM_20']=prem;z['TARGET_TOP2_RELATIVE_LOSS_20']=loss
 return z


def standardize(tr,te,cols):
 a=tr[cols].astype(float).copy();b=te[cols].astype(float).copy();lo=a.quantile(.01);hi=a.quantile(.99)
 a=a.clip(lo,hi,axis=1);b=b.clip(lo,hi,axis=1);med=a.median();a=a.fillna(med);b=b.fillna(med);mu=a.mean();sd=a.std(ddof=0).replace(0,1)
 return (a-mu)/sd,(b-mu)/sd


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
   if len(tr)<80 or te.empty:continue
   zp_tr,zp_te=standardize(tr,te,PERSIST_FEATURES);zc_tr,zc_te=standardize(tr,te,CRASH_FEATURES)
   pdir=dirs(tr,PERSIST_FEATURES,'TARGET_FACTOR_MOM_20');cdir=dirs(tr,CRASH_FEATURES,'TARGET_TOP2_RELATIVE_LOSS_20')
   ps_tr=(zp_tr*pdir).mean(axis=1);ps_te=(zp_te*pdir).mean(axis=1);cs_tr=(zc_tr*cdir).mean(axis=1);cs_te=(zc_te*cdir).mean(axis=1)
   p33,p67=ps_tr.quantile([1/3,2/3]);c67=float(cs_tr.quantile(2/3))
   for idx,r in te.iterrows():
    if not bool(r['take']):continue
    ps=float(ps_te.loc[idx]);cs=float(cs_te.loc[idx]);base='TOP2' if ps>=p67 else ('BOTTOM2' if ps<=p33 else 'EW8')
    capped='EW8' if base=='TOP2' and cs>=c67 else base
    rec={'date':r.date,'universe':u,'eval_year':year,'persist_score':ps,'crash_score':cs,'train_p33':float(p33),'train_p67':float(p67),'train_c67':c67,'persist_action':base,'capped_action':capped,'cap_triggered':base=='TOP2' and cs>=c67}
    for pol,act in [('PERSIST_ONLY',base),('CRASH_CAP',capped),('EW8','EW8'),('TOP2','TOP2')]:
     w=weights(r,act);rec[f'{pol.lower()}_gross']=fwdret(r,w)
     for j,f in enumerate(FACTORS):rec[f'{pol.lower()}_w_{f}']=float(w[j])
    rows.append(rec)
 return pd.DataFrame(rows).sort_values(['universe','date']).reset_index(drop=True)


def cost_path(d):
 out=[];pols=['CRASH_CAP','PERSIST_ONLY','EW8','TOP2']
 for u,g0 in d.groupby('universe'):
  g=g0.sort_values('date').copy();turn={}
  for pol in pols:
   W=g[[f'{pol.lower()}_w_{f}' for f in FACTORS]].to_numpy(float);prev=np.zeros(len(FACTORS));x=[]
   for w in W:x.append(.5*float(np.abs(w-prev).sum()));prev=w
   turn[pol]=np.array(x)
  for cost in COSTS:
   z=g.copy();z['cost_bps']=cost
   for pol in pols:
    z[f'{pol.lower()}_turnover']=turn[pol];z[f'{pol.lower()}_ret']=z[f'{pol.lower()}_gross']-turn[pol]*cost/10000
   out.append(z)
 return pd.concat(out,ignore_index=True)


def perf(r):
 r=pd.Series(r).dropna().astype(float)
 if len(r)<3:return {'cagr':np.nan,'sharpe':np.nan,'mdd':np.nan}
 nav=(1+r).cumprod();ppy=252/20;yrs=len(r)/ppy;cagr=float(nav.iloc[-1]**(1/yrs)-1) if yrs>0 and nav.iloc[-1]>0 else np.nan;sd=r.std(ddof=1);sh=float(r.mean()/sd*np.sqrt(ppy)) if sd>0 else np.nan
 return {'cagr':cagr,'sharpe':sh,'mdd':float((nav/nav.cummax()-1).min())}


def summarize(path):
 rows=[]
 for cost in COSTS:
  zc=path[path.cost_bps.eq(cost)]
  for period,(a,b) in PERIODS.items():
   zp=zc[zc.eval_year.between(a,b)]
   for u,g in zp.groupby('universe'):
    if len(g)<3:continue
    m={p:perf(g[f'{p.lower()}_ret']) for p in ['CRASH_CAP','PERSIST_ONLY','EW8','TOP2']};r={'universe':u,'cost_bps':cost,'period':period,'n_rebalances':len(g)}
    for p,v in m.items():r[f'{p.lower()}_cagr']=v['cagr'];r[f'{p.lower()}_sharpe']=v['sharpe'];r[f'{p.lower()}_mdd']=v['mdd']
    r['delta_sharpe_vs_persist']=r['crash_cap_sharpe']-r['persist_only_sharpe'];r['delta_cagr_vs_persist']=r['crash_cap_cagr']-r['persist_only_cagr'];r['delta_mdd_vs_persist']=r['crash_cap_mdd']-r['persist_only_mdd']
    r['delta_sharpe_vs_ew8']=r['crash_cap_sharpe']-r['ew8_sharpe'];r['delta_cagr_vs_ew8']=r['crash_cap_cagr']-r['ew8_cagr'];r['delta_mdd_vs_ew8']=r['crash_cap_mdd']-r['ew8_mdd']
    r['cap_trigger_share']=float(g.cap_triggered.mean());r['persist_top2_share']=float((g.persist_action=='TOP2').mean());r['annual_cap_turnover']=float(g.crash_cap_turnover.mean()*(252/20));rows.append(r)
 return pd.DataFrame(rows)


def pct(x):return 'NA' if not np.isfinite(x) else f'{x:+.2%}'

def report(s):
 L=['# Factor Crash-Risk Cap — Stage 3b','',
 '- Crash score is frozen to LOSER_WEAKNESS_20, DISPERSION_20, and TOP2_PREMIUM_20, selected because each passed the Stage-3 DEV/CONFIRM gate for current-top2 relative loss and at least one other adverse target.',
 '- Predictor directions and top-tercile crash threshold are estimated only from prior data each year.',
 '- The cap only changes one action: when persistence-only says TOP2 and crash risk is in the train-defined top tercile, use EW8 instead. BOTTOM2 and EW8 decisions are untouched.',
 '- Decisions are non-overlapping 20D; costs apply to one-way factor-sleeve turnover.','']
 for cost in COSTS:
  L += [f'## Cost {cost} bps','']
  for period in PERIODS:
   q=s[(s.cost_bps==cost)&(s.period==period)]
   if q.empty:continue
   L.append(f'- {period}: ΔSharpe vs persistence {q.delta_sharpe_vs_persist.median():+.3f}; ΔCAGR {pct(q.delta_cagr_vs_persist.median())}; ΔMDD {pct(q.delta_mdd_vs_persist.median())}; better Sharpe {(q.delta_sharpe_vs_persist>0).sum()}/{len(q)}; ΔSharpe vs EW8 {q.delta_sharpe_vs_ew8.median():+.3f}; cap-trigger share {q.cap_trigger_share.median():.1%}')
  L.append('')
 L += ['## 10 bps universe detail','']
 q=s[s.cost_bps.eq(10)]
 for period in PERIODS:
  L.append(f'### {period}')
  for r in q[q.period.eq(period)].sort_values('universe').itertuples(index=False):L.append(f'- {r.universe}: cap Sharpe {r.crash_cap_sharpe:+.2f} vs persistence {r.persist_only_sharpe:+.2f} (Δ {r.delta_sharpe_vs_persist:+.2f}) vs EW8 {r.ew8_sharpe:+.2f}; ΔCAGR vs persistence {pct(r.delta_cagr_vs_persist)}; trigger {r.cap_trigger_share:.0%}')
  L.append('')
 L += ['## Interpretation','',
 '- Do not retune the threshold after this run. A useful crash cap should improve persistence-only broadly without depending on 2025 or 2026 alone.',
 '- If it fails, factor-return-only crowding has reached its useful limit; the next crash research should add stock-level participation, turnover/ADV and holdings-overlap data.']
 return '\n'.join(L)


def main():
 p=pd.read_csv(INP);p['date']=pd.to_datetime(p.date);p=enrich(p);d=decisions(p);path=cost_path(d);s=summarize(path)
 d.to_csv(OUT/'crash_cap_decisions.csv',index=False,encoding='utf-8-sig');path.to_csv(OUT/'crash_cap_path.csv',index=False,encoding='utf-8-sig');s.to_csv(OUT/'crash_cap_summary.csv',index=False,encoding='utf-8-sig');text=report(s);(OUT/'RESEARCH_SUMMARY.md').write_text(text,encoding='utf-8');print(text)

if __name__=='__main__':main()
