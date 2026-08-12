from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd
import run_payoff_surface as base

OUT=Path(__file__).resolve().parent/'results'
OUT.mkdir(exist_ok=True)
RIDGE=[0.1,1,10,100]
MIN_TRAIN=120


def prep(tr,te,cols):
    A=tr[cols].astype(float);B=te[cols].astype(float)
    lo=A.quantile(.01);hi=A.quantile(.99);A=A.clip(lo,hi,axis=1);B=B.clip(lo,hi,axis=1)
    med=A.median();A=A.fillna(med);B=B.fillna(med);mu=A.mean();sd=A.std(ddof=0).replace(0,1)
    return ((A-mu)/sd).to_numpy(),((B-mu)/sd).to_numpy()
def fit(X,y,a):
    Z=np.c_[np.ones(len(X)),X];P=np.eye(Z.shape[1])*a;P[0,0]=0
    return np.linalg.pinv(Z.T@Z+P)@(Z.T@y)
def predict(X,b):return np.c_[np.ones(len(X)),X]@b

def tune(tr,cols,target):
    z=tr.dropna(subset=[target]).sort_values('date')
    if len(z)<MIN_TRAIN:return 10
    dates=np.array(sorted(z.date.unique()));cut=dates[int(len(dates)*.75)]
    a=z[z.date<cut];b=z[z.date>=cut]
    if len(a)<80 or len(b)<20:return 10
    Xa,Xb=prep(a,b,cols);ya=a[target].to_numpy();yb=b[target].to_numpy()
    return min((np.mean((yb-predict(Xb,fit(Xa,ya,al)))**2),al) for al in RIDGE)[1]


def build():
    p,mkt,fact=base.load_panel()
    # Do not use W+ here: its static Q33 state definition is unsuitable for a clean 2020-22 sequential target.
    p['ALPHA5']=p.EW4_fwd5-p.MARKET_fwd5
    p['ALPHA20']=p.EW4_fwd20-p.MARKET_fwd20
    p['RISK5']=p.MARKET_fwd5
    p['RISK20']=p.MARKET_fwd20
    return p,mkt,fact


def walkforward(p,mkt,fact):
    specs={'MARKET_ONLY':mkt,'FACTOR_ONLY':fact,'FULL':mkt+fact}
    rows=[]
    for u,g in p.groupby('universe'):
        for y in range(2020,int(g.date.dt.year.max())+1):
            tr=g[g.date<pd.Timestamp(f'{y}-01-01')];te=g[g.date.dt.year.eq(y)]
            if len(tr)<MIN_TRAIN or te.empty:continue
            for task in ['ALPHA','RISK']:
                for h in [5,20]:
                    target=f'{task}{h}'
                    for model,cols in specs.items():
                        z=tr.dropna(subset=[target]);alpha=tune(z,cols,target);Xtr,Xte=prep(z,te,cols);bh=fit(Xtr,z[target].to_numpy(),alpha);pp=predict(Xte,bh)
                        for i,(_,r) in enumerate(te.iterrows()):
                            if task=='ALPHA':
                                action='EW4' if pp[i]>0 else 'MARKET'
                                ret=float(r[f'EW4_fwd{h}'] if action=='EW4' else r[f'MARKET_fwd{h}'])
                                control=float(r[f'EW4_fwd{h}'])
                                alt=float(r[f'MARKET_fwd{h}'])
                            else:
                                action='MARKET' if pp[i]>0 else 'CASH'
                                ret=float(r[f'MARKET_fwd{h}'] if action=='MARKET' else 0.0)
                                control=float(r[f'MARKET_fwd{h}']);alt=0.0
                            rows.append({'date':r.date,'universe':u,'eval_year':y,'period':r.period,'task':task,'horizon':h,'model':model,
                                         'pred':pp[i],'real_target':r[target],'action':action,'ret':ret,'control':control,'alt':alt})
    return pd.DataFrame(rows)


def metrics(path):
    rows=[]
    for key,g in path.groupby(['universe','task','horizon','model','period']):
        r=g.ret.dropna();c=g.control.loc[r.index]
        if len(r)<8:continue
        eq=(1+r).cumprod();eqc=(1+c).cumprod();
        rows.append(dict(zip(['universe','task','horizon','model','period'],key))|{'n':len(r),'participation':(g.action!='CASH').mean(),
                    'mean':r.mean(),'win':(r>0).mean(),'edge_vs_control':(r-c).mean(),'beat_control':(r>c).mean(),
                    'mdd':(eq/eq.cummax()-1).min(),'control_mdd':(eqc/eqc.cummax()-1).min(),
                    'target_sign_accuracy':((g.pred>0)==(g.real_target>0)).mean(),'rank_ic':g.pred.rank().corr(g.real_target.rank())})
    return pd.DataFrame(rows)


def compare_incremental(stats):
    rows=[]
    for key,g in stats.groupby(['universe','task','horizon','period']):
        mp={r.model:r for _,r in g.iterrows()}
        if 'MARKET_ONLY' not in mp:continue
        b=mp['MARKET_ONLY']
        for m in ['FACTOR_ONLY','FULL']:
            if m not in mp:continue
            r=mp[m]
            rows.append(dict(zip(['universe','task','horizon','period'],key))|{'model':m,
                'delta_edge_vs_control':r.edge_vs_control-b.edge_vs_control,'delta_sign_accuracy':r.target_sign_accuracy-b.target_sign_accuracy,
                'delta_rank_ic':r.rank_ic-b.rank_ic,'delta_mdd':r.mdd-b.mdd})
    return pd.DataFrame(rows)


def summary(stats,inc):
    L=['# Binary Investment Decisions from Continuous Factor State','',
       'Low-dimensional tests only. No hard regime labels. W+ is intentionally excluded from these targets to avoid using a static Q33 definition inside early sequential training years.','',
       'Tasks: RISK = market vs cash; ALPHA = equal-weight four factor-family top portfolios (EW4) vs same-universe market. Models retrain once per year using only prior history.','',
       '## 5D historical walk-forward','']
    z=stats[stats.horizon.eq(5)]
    for (u,t,p),g in z.groupby(['universe','task','period']):
        L.append(f'### {u} — {t} — {p}')
        for _,r in g.sort_values('model').iterrows():
            L.append(f"- {r.model}: mean {r['mean']:+.2%}, win {r.win:.0%}, edge vs {'EW4' if t=='ALPHA' else 'market'} {r.edge_vs_control:+.2%}, sign accuracy {r.target_sign_accuracy:.0%}, rank IC {r.rank_ic:+.2f}, MDD {r.mdd:+.1%} (control {r.control_mdd:+.1%})")
    L+=['','## Incremental factor information over market/liquidity model','']
    q=inc[(inc.horizon==5)&(inc.period.isin(['DISCOVERY_2016_2022','NORMAL_2023_2024','BULL_2025','YTD_2026']))]
    for (t,p,m),g in q.groupby(['task','period','model']):
        L.append(f"- {t} {p} {m}: median delta edge {g.delta_edge_vs_control.median():+.2%}/5D; delta sign accuracy {g.delta_sign_accuracy.median():+.1%}; delta rank IC {g.delta_rank_ic.median():+.3f}; universes={len(g)}")
    L+=['','## Promotion criterion','',
        '- Factor interaction earns a practical role only if FACTOR_ONLY or FULL improves the market/liquidity model across multiple universes in 2023-24 and does not materially reverse in 2025.',
        '- If not, the tactical regime/factor-interaction project should not be forced into an allocation rule; the robust output would instead be the negative result and any unconditional factor edge.','']
    return '\n'.join(L)+'\n'

def main():
    p,m,f=build();path=walkforward(p,m,f);stats=metrics(path);inc=compare_incremental(stats)
    path.to_csv(OUT/'binary_decision_path.csv',index=False);stats.to_csv(OUT/'binary_decision_performance.csv',index=False);inc.to_csv(OUT/'binary_incremental_factor_value.csv',index=False)
    (OUT/'BINARY_DECISION_SUMMARY.md').write_text(summary(stats,inc),encoding='utf-8')
    print(f'path={len(path):,}; stats={len(stats):,}; incremental={len(inc):,}')
if __name__=='__main__':main()
