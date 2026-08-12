from __future__ import annotations
from pathlib import Path
import itertools
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/factor_regime_action_policy/results'
AR=OUT/'action_returns_long.csv'
TILTS=OUT/'stable_family_tilts.csv'
U3=['K200','KOSPI_EX_K200','KOSDAQ']
FAMS=['MOMENTUM','REVISION','VALUE','FLOW']


def load_wide():
    x=pd.read_csv(AR);x['date']=pd.to_datetime(x.date);x=x[x.horizon.eq(5)].copy()
    idx=['date','universe','period','base_state','factor_substate','state_cell']
    w=x.pivot_table(index=idx,columns='action',values='ret',aggfunc='first').reset_index()
    return w


def cross_section_tests(w):
    q=w[w.universe.isin(U3)].copy();rows=[]
    for (dt,p),g in q.groupby(['date','period']):
        if len(g)<2:continue
        for a,b in itertools.combinations(g.to_dict('records'),2):
            # F_HIGH - F_LOW when status differs
            if a['factor_substate']!=b['factor_substate']:
                hi=a if a['factor_substate']=='F_HIGH' else b
                lo=b if hi is a else a
                rows.append(dict(date=dt,period=p,test='FHIGH_MINUS_FLOW',u_hi=hi['universe'],u_lo=lo['universe'],diff=hi['WPLUS']-lo['WPLUS']))
            # stronger base state - weaker base state, using ordinal rank B4>B3>B2>B1
            ra=int(str(a['base_state']).replace('B','')); rb=int(str(b['base_state']).replace('B',''))
            if ra!=rb:
                hi=a if ra>rb else b;lo=b if hi is a else a
                rows.append(dict(date=dt,period=p,test='STRONGER_BASE_MINUS_WEAKER',u_hi=hi['universe'],u_lo=lo['universe'],diff=hi['WPLUS']-lo['WPLUS']))
    raw=pd.DataFrame(rows)
    summ=[]
    for (p,t),g in raw.groupby(['period','test']):
        summ.append(dict(period=p,test=t,n=len(g),mean_diff=g['diff'].mean(),median_diff=g['diff'].median(),win_rate=(g['diff']>0).mean(),p10=g['diff'].quantile(.1)))
    return raw,pd.DataFrame(summ)


def alloc_rules(w):
    q=w[w.universe.isin(U3)].copy()
    by=[]
    for (dt,p),g in q.groupby(['date','period']):
        if len(g)!=3:continue
        rec={'date':dt,'period':p}
        G={r.universe:r for _,r in g.iterrows()}
        for u in U3: rec[f'{u}_ret']=G[u].WPLUS
        def weighted(weights):
            ws=np.array([weights[u] for u in U3],float);rs=np.array([G[u].WPLUS for u in U3],float)
            return float(np.dot(ws/ws.sum(),rs))
        rec['EW3']=weighted({u:1 for u in U3})
        # Health only: 2x weight to F_HIGH
        rec['HEALTH_2X']=weighted({u:(2 if G[u].factor_substate=='F_HIGH' else 1) for u in U3})
        # Select F_HIGH sleeves only; fallback equal weight if none
        hs=[u for u in U3 if G[u].factor_substate=='F_HIGH']
        rec['FHIGH_ONLY']=weighted({u:(1 if (not hs or u in hs) else 0) for u in U3})
        # Base only ordinal weighting: B2=.75, B3=1, B4=1.25; B1=.5
        bw={'B1':.5,'B2':.75,'B3':1.0,'B4':1.25}
        rec['BASE_WEIGHT']=weighted({u:bw.get(G[u].base_state,1) for u in U3})
        # Combined modest tilt, deliberately not winner-take-all
        rec['HEALTH_BASE']=weighted({u:bw.get(G[u].base_state,1)*(1.5 if G[u].factor_substate=='F_HIGH' else 1) for u in U3})
        by.append(rec)
    path=pd.DataFrame(by).sort_values('date')
    stats=[]
    rules=['EW3','HEALTH_2X','FHIGH_ONLY','BASE_WEIGHT','HEALTH_BASE']
    for (p,),g in path.groupby(['period']):
        for r in rules:
            x=g[r].dropna();eq=(1+x).cumprod();years=max((g.date.max()-g.date.min()).days/365.25,len(x)*5/252)
            stats.append(dict(period=p,rule=r,n=len(x),win_rate=(x>0).mean(),mean5=x.mean(),cagr=eq.iloc[-1]**(1/years)-1,mdd=(eq/eq.cummax()-1).min(),worst5=x.min()))
    return path,pd.DataFrame(stats)


def tilt_stress(w):
    cand=pd.read_csv(TILTS);rows=[]
    for _,c in cand.iterrows():
        g=w[(w.universe==c.universe)&(w.state_cell==c.state_cell)]
        if c.a not in w.columns:continue
        for p in ['TRAIN_2016_2022','VALID_2023_2024','STRESS_2025','STRESS_2026']:
            z=g[g.period==p]
            if len(z)<3:continue
            d=z[c.a]-z.WPLUS
            rows.append(dict(universe=c.universe,state_cell=c.state_cell,family=c.a,period=p,n=len(z),mean_diff=d.mean(),median_diff=d.median(),win_vs_wplus=(d>0).mean()))
    raw=pd.DataFrame(rows)
    keep=[]
    keys=['universe','state_cell','family']
    for key,g in raw.groupby(keys):
        tr=g[g.period=='TRAIN_2016_2022'];va=g[g.period=='VALID_2023_2024'];s25=g[g.period=='STRESS_2025']
        if tr.empty or va.empty:continue
        r={**dict(zip(keys,key)),'train_diff':tr.iloc[0].mean_diff,'valid_diff':va.iloc[0].mean_diff,'train_n':tr.iloc[0].n,'valid_n':va.iloc[0].n}
        if not s25.empty:r.update(stress25_diff=s25.iloc[0].mean_diff,stress25_n=s25.iloc[0].n,stress25_win=s25.iloc[0].win_vs_wplus)
        else:r.update(stress25_diff=np.nan,stress25_n=0,stress25_win=np.nan)
        keep.append(r)
    return raw,pd.DataFrame(keep).sort_values('valid_diff',ascending=False)


def overlay_rules(w,tilt_summary):
    # conservative overlays: only candidates with positive TRAIN and VALID and positive 2025 if >=5 obs
    good=tilt_summary[(tilt_summary.train_diff>0)&(tilt_summary.valid_diff>0)&(((tilt_summary.stress25_n>=5)&(tilt_summary.stress25_diff>0))|(tilt_summary.stress25_n<5))].copy()
    key={(r.universe,r.state_cell):r.family for _,r in good.iterrows()}
    rows=[]
    for _,r in w.iterrows():
        if r.universe not in set(good.universe):continue
        fam=key.get((r.universe,r.state_cell))
        ret=r[fam] if fam in FAMS else r.WPLUS
        rows.append(dict(date=r.date,universe=r.universe,period=r.period,state_cell=r.state_cell,action=fam or 'WPLUS',ret=ret,wplus=r.WPLUS))
    path=pd.DataFrame(rows)
    stats=[]
    for (u,p),g in path.groupby(['universe','period']):
        for label,col in [('WPLUS','wplus'),('STABLE_TILT','ret')]:
            x=g[col];eq=(1+x).cumprod();years=max((g.date.max()-g.date.min()).days/365.25,len(x)*5/252)
            stats.append(dict(universe=u,period=p,policy=label,n=len(x),win_rate=(x>0).mean(),mean5=x.mean(),cagr=eq.iloc[-1]**(1/years)-1,mdd=(eq/eq.cummax()-1).min()))
    return good,path,pd.DataFrame(stats)


def summary(cs,alloc,tilt,good,ov):
    lines=['# Cross-Universe Allocation and Stable Family Overlay','',
           'Disjoint sleeves: K200, KOSPI_EX_K200, KOSDAQ. Each sleeve uses its W+ family basket. Rules are contemporaneous and generic; no validation outcome is used to define the cross-universe weighting rules.','',
           '## Cross-sectional signal tests','']
    for _,r in cs.iterrows():lines.append(f"- {r.period} {r.test}: n={int(r.n)}, mean {r.mean_diff:+.2%}, win {r.win_rate:.0%}, median {r.median_diff:+.2%}")
    lines+=['','## Allocation rule performance','']
    for p,g in alloc.groupby('period'):
        lines.append(f'### {p}')
        for _,r in g.iterrows():lines.append(f"- {r.rule}: win {r.win_rate:.0%}, mean5 {r.mean5:+.2%}, CAGR {r.cagr:+.1%}, MDD {r.mdd:+.1%}")
    lines+=['','## Family tilt stress check','']
    for _,r in tilt.head(20).iterrows():
        s='NA' if pd.isna(r.stress25_diff) else f"{r.stress25_diff:+.2%} (n={int(r.stress25_n)})"
        lines.append(f"- {r.universe} {r.state_cell} {r.family}: TRAIN {r.train_diff:+.2%} (n={int(r.train_n)}) -> VALID {r.valid_diff:+.2%} (n={int(r.valid_n)}) -> 2025 {s}")
    lines+=['','## Conservative overlay candidates','']
    if good.empty:lines.append('- None survive the positive TRAIN + positive VALID + non-negative/adequate 2025 screen.')
    else:
        for _,r in good.iterrows():lines.append(f"- {r.universe} {r.state_cell}: tilt to {r.family}")
    lines+=['','## Overlay performance','']
    for (u,p),g in ov.groupby(['universe','period']):
        if p not in ['VALID_2023_2024','STRESS_2025']:continue
        lines.append(f'### {u} {p}')
        for _,r in g.iterrows():lines.append(f"- {r.policy}: win {r.win_rate:.0%}, mean5 {r.mean5:+.2%}, CAGR {r.cagr:+.1%}, MDD {r.mdd:+.1%}")
    lines+=['','## Promotion rule','',
            '- Cross-universe allocation is useful only if the same generic health/base weighting improves EW3 in both TRAIN and 2023-2024 without a major 2025 reversal.',
            '- A family overlay is useful only if the exact state/family excess over W+ is positive in TRAIN and 2023-2024 and remains positive in 2025 when sample size is adequate.', '']
    return '\n'.join(lines)+'\n'


def main():
    w=load_wide();raw,cs=cross_section_tests(w);ap,ast=alloc_rules(w);traw,ts=tilt_stress(w);good,op,os=overlay_rules(w,ts)
    raw.to_csv(OUT/'cross_universe_signal_raw.csv',index=False);cs.to_csv(OUT/'cross_universe_signal_summary.csv',index=False)
    ap.to_csv(OUT/'cross_universe_allocation_paths.csv',index=False);ast.to_csv(OUT/'cross_universe_allocation_performance.csv',index=False)
    traw.to_csv(OUT/'family_tilt_stress_raw.csv',index=False);ts.to_csv(OUT/'family_tilt_stress_summary.csv',index=False);good.to_csv(OUT/'family_tilt_promoted.csv',index=False)
    op.to_csv(OUT/'family_overlay_paths.csv',index=False);os.to_csv(OUT/'family_overlay_performance.csv',index=False)
    (OUT/'CROSS_UNIVERSE_AND_OVERLAY_SUMMARY.md').write_text(summary(cs,ast,ts,good,os),encoding='utf-8')
    print(f'cross rows={len(raw):,}, tilt candidates={len(ts)}, promoted={len(good)}')

if __name__=='__main__':main()
