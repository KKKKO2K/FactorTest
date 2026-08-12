from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/factor_regime_action_policy/results'
AR=OUT/'action_returns_long.csv'
ALLOC=OUT/'cross_universe_allocation_paths.csv'
FAMS=['MOMENTUM','REVISION','VALUE','FLOW']
SPECS=[('TILT_0BP_W50',0.0000,0.50),('TILT_10BP_W55',0.0010,0.55),('TILT_20BP_W55',0.0020,0.55),('TILT_20BP_W60',0.0020,0.60)]


def loadwide():
    x=pd.read_csv(AR);x.date=pd.to_datetime(x.date);x=x[x.horizon.eq(5)]
    idx=['date','universe','period','base_state','factor_substate','state_cell']
    return x.pivot_table(index=idx,columns='action',values='ret',aggfunc='first').reset_index()


def fit_choices(w):
    tr=w[w.period.eq('TRAIN_2016_2022')];rows=[]
    for (u,cell),g in tr.groupby(['universe','state_cell']):
        if len(g)<20:continue
        candidates=[]
        for fam in FAMS:
            d=g[fam]-g.WPLUS
            candidates.append(dict(family=fam,n=len(d),mean_edge=d.mean(),median_edge=d.median(),win_vs_wplus=(d>0).mean()))
        c=pd.DataFrame(candidates).sort_values(['mean_edge','win_vs_wplus'],ascending=False)
        for spec,minedge,minwin in SPECS:
            q=c[(c.mean_edge>=minedge)&(c.win_vs_wplus>=minwin)]
            fam=q.iloc[0].family if len(q) else 'WPLUS'
            r=q.iloc[0] if len(q) else None
            rows.append(dict(universe=u,state_cell=cell,spec=spec,action=fam,
                             train_edge=(r.mean_edge if r is not None else 0.0),train_win_vs_wplus=(r.win_vs_wplus if r is not None else 0.5),train_n=len(g)))
    return pd.DataFrame(rows)


def evaluate(w,choices):
    C={(r.universe,r.state_cell,r.spec):r.action for _,r in choices.iterrows()};paths=[]
    for spec,_,_ in SPECS:
        z=w.copy();z['spec']=spec;z['action']=[C.get((r.universe,r.state_cell,spec),'WPLUS') for _,r in z.iterrows()]
        z['ret']=[r[r.action] for _,r in z.iterrows()];z['edge']=z.ret-z.WPLUS;z['switched']=z.action.ne('WPLUS')
        paths.append(z[['date','universe','period','base_state','factor_substate','state_cell','spec','action','ret','WPLUS','MARKET','edge','switched']])
    path=pd.concat(paths,ignore_index=True);stats=[];switch=[]
    for (u,p,s),g in path.groupby(['universe','period','spec']):
        g=g.sort_values('date');r=g.ret;eq=(1+r).cumprod();yrs=max((g.date.max()-g.date.min()).days/365.25,len(r)*5/252)
        stats.append(dict(universe=u,period=p,spec=s,n=len(r),switch_share=g.switched.mean(),win_rate=(r>0).mean(),mean5=r.mean(),
                          beat_wplus=(g.edge>0).mean(),mean_edge=g.edge.mean(),beat_market=((r-g.MARKET)>0).mean(),
                          cagr=eq.iloc[-1]**(1/yrs)-1,mdd=(eq/eq.cummax()-1).min(),worst5=r.min()))
        q=g[g.switched]
        if len(q)>=3:switch.append(dict(universe=u,period=p,spec=s,n=len(q),mean_edge=q.edge.mean(),median_edge=q.edge.median(),win_vs_wplus=(q.edge>0).mean(),abs_win=(q.ret>0).mean()))
    return path,pd.DataFrame(stats),pd.DataFrame(switch)


def alloc_bootstrap():
    x=pd.read_csv(ALLOC);x.date=pd.to_datetime(x.date);rows=[];rng=np.random.default_rng(20260812)
    for period in ['TRAIN_2016_2022','VALID_2023_2024','STRESS_2025','STRESS_2026']:
        g=x[x.period.eq(period)].sort_values('date')
        if len(g)<8:continue
        for rule in ['HEALTH_2X','FHIGH_ONLY','BASE_WEIGHT','HEALTH_BASE']:
            d=(g[rule]-g.EW3).to_numpy();n=len(d);B=4000;L=min(4,n);vals=[]
            for _ in range(B):
                samp=[]
                while len(samp)<n:
                    st=int(rng.integers(0,n));samp.extend([d[(st+j)%n] for j in range(L)])
                vals.append(np.mean(samp[:n]))
            vals=np.array(vals)
            rows.append(dict(period=period,rule=rule,n=n,mean_edge=d.mean(),win_vs_ew3=(d>0).mean(),ci_lo=np.quantile(vals,.025),ci_hi=np.quantile(vals,.975),p_gt0=(vals>0).mean()))
    return pd.DataFrame(rows)


def summary(choices,stats,switch,boot):
    lines=['# Train-Only Investment Playbook Validation','',
           'All state->family choices below are fit only on 2016-2022. 2023-2024 and 2025 are untouched by the choice rule. This replaces the exploratory look-ahead overlay.','',
           '## Frozen family-tilt choices','']
    for spec,g in choices.groupby('spec'):
        lines.append(f'### {spec}')
        for _,r in g[g.action.ne('WPLUS')].sort_values(['universe','state_cell']).iterrows():
            lines.append(f"- {r.universe} {r.state_cell}: {r.action}; TRAIN edge {r.train_edge:+.2%}, pair-win {r.train_win_vs_wplus:.0%}, n={int(r.train_n)}")
    lines+=['','## 2023-2024 overall performance vs WPLUS','']
    v=stats[stats.period.eq('VALID_2023_2024')]
    for u,g in v.groupby('universe'):
        lines.append(f'### {u}')
        for _,r in g.iterrows():lines.append(f"- {r.spec}: switch {r.switch_share:.0%}, mean5 {r.mean5:+.2%}, edge {r.mean_edge:+.2%}, beat-W+ {r.beat_wplus:.0%}, CAGR {r.cagr:+.1%}, MDD {r.mdd:+.1%}")
    lines+=['','## Switched-state edge only','']
    for p in ['VALID_2023_2024','STRESS_2025']:
        lines.append(f'### {p}')
        q=switch[switch.period.eq(p)]
        for _,r in q.sort_values('mean_edge',ascending=False).iterrows():lines.append(f"- {r.universe} {r.spec}: n={int(r.n)}, family-vs-W+ mean {r.mean_edge:+.2%}, win {r.win_vs_wplus:.0%}, absolute win {r.abs_win:.0%}")
    lines+=['','## Cross-universe allocation edge vs EW3: moving-block bootstrap','']
    for _,r in boot.iterrows():lines.append(f"- {r.period} {r.rule}: edge {r.mean_edge:+.2%}/5D, win {r.win_vs_ew3:.0%}, 95% CI [{r.ci_lo:+.2%},{r.ci_hi:+.2%}], P(edge>0) {r.p_gt0:.0%}, n={int(r.n)}")
    lines+=['','## Decision rules','',
            '- Promote a family tilt only if TRAIN-only selection produces positive overall edge in 2023-2024 and switched-state edge remains positive; 2025 should not materially reverse.',
            '- Promote cross-universe weighting only if edge vs EW3 is positive in TRAIN and VALID with reasonable bootstrap support; 2025/2026 are stress confirmation, not discovery.', '']
    return '\n'.join(lines)+'\n'


def main():
    w=loadwide();c=fit_choices(w);p,s,sw=evaluate(w,c);b=alloc_bootstrap()
    c.to_csv(OUT/'train_only_family_choices.csv',index=False);p.to_csv(OUT/'train_only_family_paths.csv',index=False);s.to_csv(OUT/'train_only_family_performance.csv',index=False);sw.to_csv(OUT/'train_only_family_switch_diagnostics.csv',index=False);b.to_csv(OUT/'cross_universe_allocation_bootstrap.csv',index=False)
    (OUT/'TRAIN_ONLY_PLAYBOOK_SUMMARY.md').write_text(summary(c,s,sw,b),encoding='utf-8')
    print(f'choices={len(c)}, stats={len(s)}, bootstrap={len(b)}')

if __name__=='__main__':main()
