from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
ASSIGN=ROOT/'research/factor_regime_contemporaneous_states/results/nested_state_assignments.csv'
PRIM=ROOT/'research/factor_regime_full_state_map/results/family_primitives.csv'
FSTATE=ROOT/'research/factor_regime_full_state_map/results/family_states_static.csv'
OUT=ROOT/'research/factor_payoff_surface/results'
OUT.mkdir(parents=True,exist_ok=True)
FAMS=['MOMENTUM','REVISION','VALUE','FLOW']
RIDGE=[0.1,1,10,100]
MIN_TRAIN=300

CONTEXT=['MKT_RET_20D','MKT_RET_60D','MKT_VOL_20D','MKT_DD_60D','LIQ_5D_20D','LIQ_1D_20D',
         'RELATIVE_WORKING_BREADTH','ABS_CONFIRMED_BREADTH','DEFENSIVE_WORKING_BREADTH','REVERSE_BREADTH',
         'POSITIVE_ABS_BREADTH','WPLUS_FAMILY_SHARE','WPLUS_PAIR_SHARE','CONFLICT_PAIR_SHARE','LEADER_STRENGTH_60D','SPREAD_DISPERSION_20D']


def sample(d):
    y=d.year
    if y<=2022:return 'DISCOVERY_2016_2022'
    if y<=2024:return 'NORMAL_2023_2024'
    if y==2025:return 'BULL_2025'
    return 'YTD_2026'


def load():
    s=pd.read_csv(ASSIGN); p=pd.read_csv(PRIM); fs=pd.read_csv(FSTATE)
    for z in (s,p,fs):z['date']=pd.to_datetime(z['date'])
    fs=fs[fs.cut_name.eq('Q33')][['date','universe','family','state6']]
    p=p.merge(fs,on=['date','universe','family'],how='left')
    keep=['date','universe']+[c for c in CONTEXT if c in s.columns]
    p=p.merge(s[keep].drop_duplicates(['date','universe']),on=['date','universe'],how='inner')
    p=p[p.family.isin(FAMS)].copy()
    # Continuous family features.
    for c in ['top_20d','spread_20d','top_60d','spread_60d']:
        p[f'rel_{c}']=p[c]-p.groupby(['date','universe'])[c].transform('mean')
        sd=p.groupby(['date','universe'])[c].transform('std').replace(0,np.nan)
        p[f'z_{c}']=p[f'rel_{c}']/sd
        p[f'rank_{c}']=p.groupby(['date','universe'])[c].rank(pct=True)
    # Approximate short-vs-long acceleration using cross-sectional standardized signals, not raw horizon subtraction.
    p['spread_accel']=p['z_spread_20d']-p['z_spread_60d']
    p['top_accel']=p['z_top_20d']-p['z_top_60d']
    # Relative future family payoff removes same-date market/common factor shock.
    for h in [5,20]:
        c=f'top_fwd_{h}d'
        p[f'y_rel_{h}d']=p[c]-p.groupby(['date','universe'])[c].transform('mean')
    p['sample']=p.date.map(sample)
    # one-hot family fixed effects
    for f in FAMS[1:]: p[f'FAM_{f}']=(p.family==f).astype(float)
    family_feats=['top_20d','spread_20d','top_60d','spread_60d','z_top_20d','z_spread_20d','z_top_60d','z_spread_60d',
                  'rank_top_20d','rank_spread_20d','rank_top_60d','rank_spread_60d','spread_accel','top_accel',
                  'member_positive_spread_share_20d','member_same_sign_20d']+[f'FAM_{f}' for f in FAMS[1:]]
    family_feats=[c for c in family_feats if c in p.columns]
    ctx=[c for c in CONTEXT if c in p.columns]
    # Context must interact with family-relative state to affect within-date ranking.
    inter=[]
    for a in ['z_top_20d','z_spread_20d','spread_accel','top_accel']:
        for b in ['MKT_RET_60D','MKT_VOL_20D','LIQ_5D_20D','ABS_CONFIRMED_BREADTH','CONFLICT_PAIR_SHARE']:
            if a in p and b in p:
                nm=f'INT_{a}__{b}'; p[nm]=p[a]*p[b]; inter.append(nm)
    return p.sort_values(['universe','date','family']).reset_index(drop=True),family_feats,ctx,inter


def prep(tr,te,cols):
    A=tr[cols].astype(float);B=te[cols].astype(float)
    lo=A.quantile(.01);hi=A.quantile(.99);A=A.clip(lo,hi,axis=1);B=B.clip(lo,hi,axis=1)
    med=A.median();A=A.fillna(med);B=B.fillna(med);mu=A.mean();sd=A.std(ddof=0).replace(0,1)
    return ((A-mu)/sd).to_numpy(),((B-mu)/sd).to_numpy()

def fit(X,y,a):
    Z=np.c_[np.ones(len(X)),X];P=np.eye(Z.shape[1])*a;P[0,0]=0
    return np.linalg.pinv(Z.T@Z+P)@(Z.T@y)
def pred(X,b):return np.c_[np.ones(len(X)),X]@b

def tune(tr,cols,target):
    z=tr.dropna(subset=[target]).sort_values('date');dates=np.array(sorted(z.date.unique()))
    if len(z)<MIN_TRAIN or len(dates)<30:return 10
    dcut=dates[int(len(dates)*.75)];a=z[z.date<dcut];b=z[z.date>=dcut]
    if len(a)<150 or len(b)<50:return 10
    Xa,Xb=prep(a,b,cols);ya=a[target].to_numpy();yb=b[target].to_numpy()
    return min((np.mean((yb-pred(Xb,fit(Xa,ya,al)))**2),al) for al in RIDGE)[1]


def walkforward(p,fam,ctx,inter):
    specs={'STATIC_FAMILY':[c for c in fam if c.startswith('FAM_')],
           'FAMILY_STATE':fam,
           'FULL_INTERACTION':fam+inter}
    rows=[];coefs=[]
    for u,g in p.groupby('universe'):
        for y in range(2020,int(g.date.dt.year.max())+1):
            tr=g[g.date<pd.Timestamp(f'{y}-01-01')];te=g[g.date.dt.year.eq(y)]
            if len(tr)<MIN_TRAIN or te.empty:continue
            for h in [5,20]:
                target=f'y_rel_{h}d'
                for model,cols in specs.items():
                    z=tr.dropna(subset=[target]);alpha=tune(z,cols,target)
                    Xtr,Xte=prep(z,te,cols);bh=fit(Xtr,z[target].to_numpy(),alpha);pp=pred(Xte,bh)
                    for i,(_,r) in enumerate(te.iterrows()):
                        rows.append({'date':r.date,'universe':u,'eval_year':y,'horizon':h,'model':model,'family':r.family,
                                     'pred_rel':pp[i],'real_rel':r[target],'family_ret':r[f'top_fwd_{h}d'],'state6':r.state6})
                    for j,c in enumerate(cols):coefs.append({'universe':u,'eval_year':y,'horizon':h,'model':model,'feature':c,'coef':bh[j+1],'alpha':alpha})
    return pd.DataFrame(rows),pd.DataFrame(coefs)


def eval_ranking(pr):
    rows=[];path=[]
    for (dt,u,h,m),g in pr.groupby(['date','universe','horizon','model']):
        if g.family.nunique()<4:continue
        pick=g.sort_values('pred_rel',ascending=False).iloc[0]
        oracle=g.sort_values('real_rel',ascending=False).iloc[0]
        ew=g.family_ret.mean()
        leader20=g.loc[g.pred_rel.idxmax(),'family']
        path.append({'date':dt,'universe':u,'horizon':h,'model':m,'chosen_family':pick.family,'ret':pick.family_ret,
                     'ew4':ew,'edge_vs_ew4':pick.family_ret-ew,'correct_best':float(pick.family==oracle.family)})
    path=pd.DataFrame(path);path['sample']=path.date.map(sample)
    for key,g in path.groupby(['universe','horizon','model','sample']):
        if len(g)<8:continue
        e=g.edge_vs_ew4
        rows.append(dict(zip(['universe','horizon','model','sample'],key))|{'n':len(g),'mean_ret':g.ret.mean(),'win':(g.ret>0).mean(),
                    'edge_vs_ew4':e.mean(),'beat_ew4':(e>0).mean(),'best_family_accuracy':g.correct_best.mean()})
    return path,pd.DataFrame(rows)


def baselines(p):
    rows=[]
    for (dt,u),g in p.groupby(['date','universe']):
        if g.family.nunique()<4:continue
        for h in [5,20]:
            ew=g[f'top_fwd_{h}d'].mean()
            # strongest current signals are deliberately simple controls
            defs={'TOP20_LEADER':g.sort_values('top_20d',ascending=False).iloc[0],
                  'SPREAD20_LEADER':g.sort_values('spread_20d',ascending=False).iloc[0],
                  'SPREAD60_LEADER':g.sort_values('spread_60d',ascending=False).iloc[0]}
            wp=g[g.state6.eq('W+')]
            if not wp.empty:
                wr=wp[f'top_fwd_{h}d'].mean();rows.append({'date':dt,'universe':u,'horizon':h,'strategy':'WPLUS','ret':wr,'ew4':ew,'edge':wr-ew})
            for nm,r in defs.items():rows.append({'date':dt,'universe':u,'horizon':h,'strategy':nm,'ret':r[f'top_fwd_{h}d'],'ew4':ew,'edge':r[f'top_fwd_{h}d']-ew})
    z=pd.DataFrame(rows);z['sample']=z.date.map(sample)
    return z.groupby(['universe','horizon','strategy','sample']).agg(n=('ret','size'),mean_ret=('ret','mean'),edge_vs_ew4=('edge','mean'),beat_ew4=('edge',lambda x:(x>0).mean())).reset_index()


def simple_surfaces(p):
    feats=['z_top_20d','z_spread_20d','z_top_60d','z_spread_60d','spread_accel','top_accel']
    rows=[]
    for (u,fam),g in p.groupby(['universe','family']):
        for ft in feats:
            for h in [5,20]:
                for sm,sg in g.groupby('sample'):
                    z=sg[[ft,f'y_rel_{h}d']].dropna()
                    if len(z)<24:continue
                    q1,q2=z[ft].quantile([.33,.67]);lo=z[z[ft]<=q1][f'y_rel_{h}d'];hi=z[z[ft]>=q2][f'y_rel_{h}d']
                    if len(lo)<8 or len(hi)<8:continue
                    rows.append({'universe':u,'family':fam,'feature':ft,'horizon':h,'sample':sm,'n':len(z),
                                 'hl':hi.mean()-lo.mean(),'high_rel':hi.mean(),'low_rel':lo.mean(),'high_win_rel':(hi>0).mean(),'low_win_rel':(lo>0).mean()})
    surf=pd.DataFrame(rows);stable=[]
    for key,g in surf.groupby(['universe','family','feature','horizon']):
        mp={r.sample:r for _,r in g.iterrows()}
        if 'DISCOVERY_2016_2022' not in mp or 'NORMAL_2023_2024' not in mp:continue
        a=mp['DISCOVERY_2016_2022'];b=mp['NORMAL_2023_2024']
        if np.sign(a.hl)==np.sign(b.hl) and np.sign(a.hl)!=0:
            stable.append(dict(zip(['universe','family','feature','horizon'],key))|{'disc_hl':a.hl,'normal_hl':b.hl,'min_abs':min(abs(a.hl),abs(b.hl)),'sign':np.sign(a.hl)})
    st=pd.DataFrame(stable)
    if not st.empty:st=st.sort_values('min_abs',ascending=False)
    return surf,st


def summary(p,perf,base,surf,st)->str:
    L=['# Cross-Family Conditional Payoff Ranking','',
       'This iteration removes the need to forecast absolute family returns. The target is each family future return minus the same-date four-family average, so common market shocks are removed.','',
       '## Walk-forward ranking vs equal-weight four-family basket','']
    for (u,sm),g in perf[perf.horizon.eq(5)].groupby(['universe','sample']):
        L.append(f'### {u} — {sm}')
        for _,r in g.sort_values('model').iterrows():
            L.append(f"- {r.model}: n={int(r.n)}, edge vs EW4 {r.edge_vs_ew4:+.2%}/5D, beat EW4 {r.beat_ew4:.0%}, best-family accuracy {r.best_family_accuracy:.0%}, absolute win {r.win:.0%}")
    L+=['','## Simple controls','']
    for (u,sm),g in base[(base.horizon==5)&(base['sample'].isin(['DISCOVERY_2016_2022','NORMAL_2023_2024','BULL_2025','YTD_2026']))].groupby(['universe','sample']):
        vals='; '.join(f"{r.strategy} {r.edge_vs_ew4:+.2%}" for _,r in g.iterrows())
        L.append(f'- {u} {sm}: {vals}')
    L+=['','## Stable simple family-level payoff surfaces','']
    if st.empty:L.append('- None')
    else:
        for _,r in st.head(30).iterrows():
            L.append(f"- {r.universe} {r.family} {r.feature} {int(r.horizon)}D: H-L {r.disc_hl:+.2%} -> {r.normal_hl:+.2%}")
    L+=['','## Guardrail','',
        '- A model is economically useful only if FAMILY_STATE or FULL_INTERACTION improves on both STATIC_FAMILY and simple leader controls in sequential walk-forward, not merely in one exceptional year.',
        '- Stable surfaces are descriptive screens; they are not promoted into rules until an expanding threshold test confirms them.','']
    return '\n'.join(L)+'\n'

def main():
    p,fam,ctx,inter=load();pr,coef=walkforward(p,fam,ctx,inter);path,perf=eval_ranking(pr);base=baselines(p);surf,st=simple_surfaces(p)
    p.to_csv(OUT/'family_relative_payoff_panel.csv',index=False);pr.to_csv(OUT/'family_ranking_predictions.csv',index=False);coef.to_csv(OUT/'family_ranking_coefficients.csv',index=False)
    path.to_csv(OUT/'family_ranking_policy_path.csv',index=False);perf.to_csv(OUT/'family_ranking_performance.csv',index=False);base.to_csv(OUT/'family_ranking_baselines.csv',index=False)
    surf.to_csv(OUT/'family_simple_surfaces.csv',index=False);st.to_csv(OUT/'family_stable_surfaces.csv',index=False)
    (OUT/'FAMILY_RANKING_SUMMARY.md').write_text(summary(p,perf,base,surf,st),encoding='utf-8')
    print(f'panel={len(p):,}; predictions={len(pr):,}; stable={len(st):,}')

if __name__=='__main__':main()
