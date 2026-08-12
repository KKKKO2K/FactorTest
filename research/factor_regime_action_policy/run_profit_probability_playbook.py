from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/factor_regime_action_policy/results'
AR=OUT/'action_returns_long.csv'
FAMS=['MOMENTUM','REVISION','VALUE','FLOW']


def loadwide():
    x=pd.read_csv(AR);x.date=pd.to_datetime(x.date);x=x[x.horizon.eq(5)]
    idx=['date','universe','period','base_state','factor_substate','state_cell']
    return x.pivot_table(index=idx,columns='action',values='ret',aggfunc='first').reset_index()


def state_hit_table(w):
    rows=[]
    for (u,p,cell),g in w.groupby(['universe','period','state_cell']):
        r=g.WPLUS
        rows.append(dict(universe=u,period=p,state_cell=cell,n=len(r),win_rate=(r>0).mean(),mean5=r.mean(),median5=r.median(),p10=r.quantile(.1)))
    return pd.DataFrame(rows)


def stable_high_prob(hit):
    rows=[]
    for (u,cell),g in hit.groupby(['universe','state_cell']):
        tr=g[g.period.eq('TRAIN_2016_2022')];va=g[g.period.eq('VALID_2023_2024')];s25=g[g.period.eq('STRESS_2025')]
        if tr.empty or va.empty:continue
        t=tr.iloc[0];v=va.iloc[0]
        if t.n<20 or v.n<8:continue
        rows.append(dict(universe=u,state_cell=cell,train_n=t.n,valid_n=v.n,train_win=t.win_rate,valid_win=v.win_rate,train_mean=t.mean5,valid_mean=v.mean5,
                         stress25_n=(s25.iloc[0].n if len(s25) else 0),stress25_win=(s25.iloc[0].win_rate if len(s25) else np.nan),stress25_mean=(s25.iloc[0].mean5 if len(s25) else np.nan)))
    return pd.DataFrame(rows).sort_values(['valid_win','valid_mean'],ascending=False)


def fit_hitrate_choices(w,min_edge):
    tr=w[w.period.eq('TRAIN_2016_2022')];rows=[]
    for (u,cell),g in tr.groupby(['universe','state_cell']):
        if len(g)<20:continue
        basewin=(g.WPLUS>0).mean();basemean=g.WPLUS.mean();best=None
        for fam in FAMS:
            win=(g[fam]>0).mean();mean=g[fam].mean();edge=win-basewin
            # require higher hit rate and no meaningful sacrifice in TRAIN expected return
            if edge>=min_edge and mean>=basemean-0.0005:
                cand=(edge,mean-basemean,win,fam)
                if best is None or cand>best:best=cand
        rows.append(dict(universe=u,state_cell=cell,action=(best[3] if best else 'WPLUS'),train_hit_edge=(best[0] if best else 0),train_mean_edge=(best[1] if best else 0),train_n=len(g)))
    return pd.DataFrame(rows)


def eval_hitrate(w,choices,label):
    C={(r.universe,r.state_cell):r.action for _,r in choices.iterrows()};rows=[]
    z=w.copy();z['action']=[C.get((r.universe,r.state_cell),'WPLUS') for _,r in z.iterrows()];z['ret']=[r[r.action] for _,r in z.iterrows()];z['edge']=z.ret-z.WPLUS;z['switched']=z.action.ne('WPLUS')
    for (u,p),g in z.groupby(['universe','period']):
        r=g.ret;eq=(1+r).cumprod();yrs=max((g.date.max()-g.date.min()).days/365.25,len(r)*5/252);q=g[g.switched]
        rows.append(dict(universe=u,period=p,policy=label,n=len(g),switch_share=g.switched.mean(),win_rate=(r>0).mean(),wplus_win=(g.WPLUS>0).mean(),mean5=r.mean(),mean_edge=g.edge.mean(),
                         switched_n=len(q),switched_win=(q.ret>0).mean() if len(q) else np.nan,switched_wplus_win=(q.WPLUS>0).mean() if len(q) else np.nan,
                         switched_edge=q.edge.mean() if len(q) else np.nan,cagr=eq.iloc[-1]**(1/yrs)-1,mdd=(eq/eq.cummax()-1).min()))
    return z,pd.DataFrame(rows)


def fit_sizing(hit,hi_cut):
    # TRAIN-only confidence map; high states receive 1.25x, others 0.75x. A stronger 1.5/0.5 variant is evaluated separately.
    tr=hit[hit.period.eq('TRAIN_2016_2022')]
    return {(r.universe,r.state_cell):(r.win_rate>=hi_cut and r.mean5>0) for _,r in tr.iterrows() if r.n>=20}


def eval_sizing(w,hit):
    rows=[];paths=[]
    for cut in [0.55,0.60]:
        H=fit_sizing(hit,cut)
        for hi,lo,tag in [(1.25,.75,'125_75'),(1.5,.5,'150_50')]:
            z=w.copy();z['mult']=[hi if H.get((r.universe,r.state_cell),False) else lo for _,r in z.iterrows()];z['ret']=z.WPLUS*z.mult;z['policy']=f'SIZE_HIT{int(cut*100)}_{tag}'
            paths.append(z[['date','universe','period','state_cell','policy','mult','ret','WPLUS','MARKET']])
            for (u,p),g in z.groupby(['universe','period']):
                r=g.ret;eq=(1+r).cumprod();yrs=max((g.date.max()-g.date.min()).days/365.25,len(r)*5/252)
                rows.append(dict(universe=u,period=p,policy=z.policy.iloc[0],avg_mult=g.mult.mean(),win_rate=(r>0).mean(),mean5=r.mean(),cagr=eq.iloc[-1]**(1/yrs)-1,mdd=(eq/eq.cummax()-1).min(),worst5=r.min()))
    return pd.concat(paths,ignore_index=True),pd.DataFrame(rows)


def summary(stable,h5,h10,size):
    lines=['# Profit-Probability and Position-Sizing Research','',
           'Objective is explicitly P(5D return > 0), not only average return. Family switches and sizing maps are fit on 2016-2022 only; 2023-2024/2025 are frozen evaluation.','',
           '## W+ states with adequate TRAIN and VALID samples','']
    for _,r in stable.iterrows():
        s='NA' if pd.isna(r.stress25_win) else f"{r.stress25_win:.0%}/{r.stress25_mean:+.2%} n={int(r.stress25_n)}"
        lines.append(f"- {r.universe} {r.state_cell}: TRAIN win {r.train_win:.0%}, mean {r.train_mean:+.2%} n={int(r.train_n)} -> VALID win {r.valid_win:.0%}, mean {r.valid_mean:+.2%} n={int(r.valid_n)} -> 2025 {s}")
    lines+=['','## TRAIN-only hit-rate family switching','']
    for label,tab in [('5PP',h5),('10PP',h10)]:
        lines.append(f'### Require +{label} TRAIN hit-rate edge')
        for p in ['VALID_2023_2024','STRESS_2025']:
            q=tab[tab.period.eq(p)];lines.append(f'#### {p}')
            for _,r in q.iterrows():
                lines.append(f"- {r.universe}: switch {r.switch_share:.0%}; win {r.win_rate:.0%} vs W+ {r.wplus_win:.0%}; mean edge {r.mean_edge:+.2%}; switched n={int(r.switched_n)}, switched win {r.switched_win:.0%} vs W+ {r.switched_wplus_win:.0%}; CAGR {r.cagr:+.1%}, MDD {r.mdd:+.1%}")
    lines+=['','## TRAIN-only probability sizing of W+','']
    for p in ['VALID_2023_2024','STRESS_2025']:
        lines.append(f'### {p}')
        q=size[size.period.eq(p)]
        for u,g in q.groupby('universe'):
            lines.append(f'#### {u}')
            for _,r in g.iterrows():lines.append(f"- {r.policy}: avg exposure {r.avg_mult:.2f}x, win {r.win_rate:.0%}, mean5 {r.mean5:+.2%}, CAGR {r.cagr:+.1%}, MDD {r.mdd:+.1%}, worst5 {r.worst5:+.1%}")
    lines+=['','## Interpretation','',
            '- Sizing changes return magnitude, not the sign of a nonzero W+ period; therefore its role is expectancy/risk concentration, while family switching is the only tested mechanism aimed directly at increasing hit rate.',
            '- High-probability states are actionable only when TRAIN and VALID both show elevated hit rate with adequate n; 2025 provides an additional stress check.', '']
    return '\n'.join(lines)+'\n'


def main():
    w=loadwide();hit=state_hit_table(w);stable=stable_high_prob(hit)
    c5=fit_hitrate_choices(w,.05);p5,h5=eval_hitrate(w,c5,'HIT_TILT_5PP')
    c10=fit_hitrate_choices(w,.10);p10,h10=eval_hitrate(w,c10,'HIT_TILT_10PP')
    sp,ss=eval_sizing(w,hit)
    hit.to_csv(OUT/'wplus_state_profit_probability.csv',index=False);stable.to_csv(OUT/'wplus_stable_profit_states.csv',index=False)
    c5.to_csv(OUT/'hitrate_family_choices_5pp.csv',index=False);c10.to_csv(OUT/'hitrate_family_choices_10pp.csv',index=False)
    h5.to_csv(OUT/'hitrate_policy_performance_5pp.csv',index=False);h10.to_csv(OUT/'hitrate_policy_performance_10pp.csv',index=False)
    sp.to_csv(OUT/'probability_sizing_paths.csv',index=False);ss.to_csv(OUT/'probability_sizing_performance.csv',index=False)
    (OUT/'PROFIT_PROBABILITY_PLAYBOOK_SUMMARY.md').write_text(summary(stable,h5,h10,ss),encoding='utf-8')
    print(f'stable states={len(stable)}, hit choices={len(c5)}, sizing stats={len(ss)}')

if __name__=='__main__':main()
