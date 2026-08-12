from __future__ import annotations

import math
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'research/liquidity_cross_factor'))
import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as multi

OUT=Path(__file__).resolve().parent/'results_confirmatory'; OUT.mkdir(parents=True,exist_ok=True)
FAMILIES={
    'MOMENTUM':['MOM1M','MOM12_1'],
    'REVISION':['OP12_REV','OPFY1_REV'],
    'VALUE':['PBR12MF','PER12MF'],
    'FLOW':['PRIVATE_FLOW','FOREIGN_FLOW'],
}
FACTOR_FAMILY={f:k for k,v in FAMILIES.items() for f in v}
HIGH_GOOD={'MOM1M':True,'MOM12_1':True,'OP12_REV':True,'OPFY1_REV':True,
           'PBR12MF':False,'PER12MF':False,'PRIVATE_FLOW':True,'FOREIGN_FLOW':True}
UNIVERSES=('K200','KOSPI_EX_K200','KOSPI_ALL','KOSDAQ','KOSPI_KOSDAQ_ALL','KOSDAQ_PLUS_KOSPI_EX_K200')
TOP_NS=(10,20)
HORIZONS=(5,10,20)
COST_BPS=(0,30,60)
RULE='CROSS_FAMILY_W20'  # fixed before this confirmatory grid: 80% primary + 20% other-three-family consensus
RNG=np.random.default_rng(20260813)


def sample_of(d):
    y=d.year
    if y<=2019:return 'EARLY_2016_2019'
    if y<=2022:return 'LATE_2020_2022'
    if y<=2024:return 'NORMAL_2023_2024'
    if y==2025:return 'BULL_2025'
    return 'YTD_2026'

def rank_good(raw,high_good):
    return pd.to_numeric(raw,errors='coerce').rank(pct=True,method='average',ascending=True if high_good else False)

def block_boot(x,block=4,nboot=4000):
    x=np.asarray(x,float);x=x[np.isfinite(x)];n=len(x)
    if n<8:return np.array([])
    nb=int(np.ceil(n/block));starts=RNG.integers(0,n,size=(nboot,nb));idx=(starts[:,:,None]+np.arange(block)[None,None,:])%n
    return x[idx.reshape(nboot,-1)[:,:n]].mean(axis=1)


def run_grid():
    returns,mcap,k200=base.load_basic(); markets=multi.load_market_by_date(); files={f:base.dated_files(path) for f,path in base.FACTORS.items()}
    common=sorted(set(returns.index)&set(k200)&set(markets)); allrows=[]
    for h in HORIZONS:
        fwd=base.forward_returns(returns,h); dates=[d for d in common if d>=base.START and d in fwd.index][::h]
        holdings={}
        for dt in dates:
            k=k200[dt];market=markets[dt];raws={f:base.load_factor(fs[dt]) for f,fs in files.items() if dt in fs}
            if len(raws)<8:continue
            for u in UNIVERSES:
                codes=multi.universe_codes(u,k,market);y=fwd.loc[dt].reindex(codes)
                minobs=70 if u=='K200' else 120
                if y.notna().sum()<minobs:continue
                scores={f:rank_good(raws[f].reindex(codes),HIGH_GOOD[f]) for f in raws}
                fam={name:pd.concat([scores[x] for x in members],axis=1).mean(axis=1) for name,members in FAMILIES.items()}
                for f,primary in scores.items():
                    ff=FACTOR_FAMILY[f];other=pd.concat([v for n,v in fam.items() if n!=ff],axis=1).mean(axis=1)
                    overlay=.8*primary+.2*other
                    for topn in TOP_NS:
                        sb=primary.dropna().sort_values(ascending=False);so=overlay.dropna().sort_values(ascending=False)
                        if len(sb)<topn or len(so)<topn:continue
                        bn=sb.head(topn).index.tolist();on=so.head(topn).index.tolist()
                        bg=float(y.reindex(bn).mean());og=float(y.reindex(on).mean())
                        for label,names,gross in [('BASE',bn,bg),(RULE,on,og)]:
                            key=(h,u,f,topn,label);old=holdings.get(key,[]);turn=1-len(set(old)&set(names))/topn if old else 1.0
                            allrows.append({'date':dt,'universe':u,'factor':f,'family':ff,'horizon':h,'topn':topn,'strategy':label,'gross':gross,'turnover':turn})
                            holdings[key]=names
    p=pd.DataFrame(allrows);p['date']=pd.to_datetime(p.date);p['sample']=p.date.map(sample_of)
    return p


def evaluate(p):
    b=p[p.strategy.eq('BASE')][['date','universe','factor','horizon','topn','gross','turnover']].rename(columns={'gross':'base_gross','turnover':'base_turnover'})
    o=p[p.strategy.eq(RULE)].merge(b,on=['date','universe','factor','horizon','topn'],how='inner')
    o['gross_delta']=o.gross-o.base_gross;o['turnover_delta']=o.turnover-o.base_turnover
    for cost in COST_BPS:
        o[f'net_delta_{cost}']=o.gross_delta-o.turnover_delta*cost/10000
    o.to_csv(OUT/'matched_confirmatory_deltas.csv',index=False)
    stats=[];boots=[];family=[]
    for key,g in o.groupby(['universe','horizon','topn','sample']):
        # equal-weight primary factors within each date first
        da=g.groupby('date').agg(gross_delta=('gross_delta','mean'),turnover_delta=('turnover_delta','mean'),**{f'net_{c}':(f'net_delta_{c}','mean') for c in COST_BPS}).reset_index().sort_values('date')
        rec=dict(zip(['universe','horizon','topn','sample'],key))|{'n_dates':len(da),'gross_delta':da.gross_delta.mean(),'turnover_delta':da.turnover_delta.mean()}
        for c in COST_BPS:rec[f'net_delta_{c}']=da[f'net_{c}'].mean()
        stats.append(rec)
        for metric in ['gross_delta']+[f'net_{c}' for c in COST_BPS]:
            bs=block_boot(da[metric].to_numpy())
            if len(bs):boots.append(dict(zip(['universe','horizon','topn','sample'],key))|{'metric':metric,'mean':da[metric].mean(),'ci025':np.quantile(bs,.025),'ci975':np.quantile(bs,.975),'p_gt0':(bs>0).mean(),'n_dates':len(da)})
    for key,g in o.groupby(['universe','horizon','topn','sample','family']):
        da=g.groupby('date').gross_delta.mean()
        family.append(dict(zip(['universe','horizon','topn','sample','family'],key))|{'n_dates':len(da),'gross_delta':da.mean(),'positive_date_rate':(da>0).mean()})
    return pd.DataFrame(stats),pd.DataFrame(boots),pd.DataFrame(family)


def summarize(stats,boots,fam):
    core=['EARLY_2016_2019','LATE_2020_2022','NORMAL_2023_2024']
    L=['# Confirmatory CROSS_FAMILY_W20 Grid','',
       'Rule is frozen from the prior stock-level result: 80% primary factor stock score + 20% consensus score from the other three factor families. No weight optimization is performed here. Rebalance interval equals the forward horizon, so 5D/10D/20D observations are non-overlapping by construction.','',
       '## Core-block sign robustness by horizon / TopN','']
    robust=[]
    for key,g in stats.groupby(['universe','horizon','topn']):
        mp={r['sample']:r for _,r in g.iterrows()}
        if not all(s in mp for s in core):continue
        gross=[mp[s].gross_delta for s in core];net30=[mp[s].net_delta_30 for s in core]
        posfam=[]
        for s in core:
            z=fam[(fam.universe==key[0])&(fam.horizon==key[1])&(fam.topn==key[2])&(fam['sample']==s)]
            posfam.append(int((z.gross_delta>0).sum()))
        ok=all(v>0 for v in gross) and all(v>0 for v in net30)
        robust.append({'universe':key[0],'horizon':key[1],'topn':key[2],'ok':ok,'gross':gross,'net30':net30,'posfam':posfam})
        L.append(f"- {key[0]} H{key[1]} Top{key[2]}: gross {gross[0]:+.2%}->{gross[1]:+.2%}->{gross[2]:+.2%}; net30 {net30[0]:+.2%}->{net30[1]:+.2%}->{net30[2]:+.2%}; positive families {posfam[0]}/4->{posfam[1]}/4->{posfam[2]}/4; {'PASS' if ok else 'FAIL'}")
    L+=['','## 2023-24 block-bootstrap for passing specifications','']
    for r in robust:
        if not r['ok']:continue
        for metric in ['gross_delta','net_30','net_60']:
            z=boots[(boots.universe==r['universe'])&(boots.horizon==r['horizon'])&(boots.topn==r['topn'])&(boots['sample']=='NORMAL_2023_2024')&(boots.metric==metric)]
            if z.empty:continue
            q=z.iloc[0];L.append(f"- {r['universe']} H{r['horizon']} Top{r['topn']} {metric}: {q['mean']:+.2%}; CI [{q.ci025:+.2%},{q.ci975:+.2%}], P>0 {q.p_gt0:.0%}, n={int(q.n_dates)}")
    L+=['','## Stress behavior of passing 10D Top20 reference spec','']
    for u in stats.universe.unique():
        z=stats[(stats.universe==u)&(stats.horizon==10)&(stats.topn==20)]
        mp={r['sample']:r for _,r in z.iterrows()}
        if not all(s in mp for s in core):continue
        if not (all(mp[s].gross_delta>0 for s in core) and all(mp[s].net_delta_30>0 for s in core)):continue
        b=mp.get('BULL_2025');y=mp.get('YTD_2026')
        L.append(f"- {u}: 2025 net30 {b.net_delta_30:+.2%} gross {b.gross_delta:+.2%}; 2026 net30 {y.net_delta_30:+.2%} gross {y.gross_delta:+.2%}")
    L+=['','## Decision rule','',
       '- Promote the concept, not a precise parameter, only if the same frozen W20 rule remains positive across multiple TopN/horizon settings and the edge survives 30/60 bp costs.',
       '- Top20/H10 remains the reference specification because it predates this confirmatory grid; superior grid cells are robustness evidence, not newly optimized choices.',
       '- 2025/2026 are stress diagnostics only.','']
    return '\n'.join(L)+'\n'


def main():
    p=run_grid();p.to_csv(OUT/'portfolio_paths.csv',index=False);stats,boots,fam=evaluate(p)
    stats.to_csv(OUT/'confirmatory_grid.csv',index=False);boots.to_csv(OUT/'confirmatory_bootstrap.csv',index=False);fam.to_csv(OUT/'confirmatory_family_breadth.csv',index=False)
    (OUT/'CONFIRMATORY_SUMMARY.md').write_text(summarize(stats,boots,fam),encoding='utf-8')
    print(f'rows={len(p):,}, specs={len(stats):,}, bootstrap={len(boots):,}')

if __name__=='__main__':main()
