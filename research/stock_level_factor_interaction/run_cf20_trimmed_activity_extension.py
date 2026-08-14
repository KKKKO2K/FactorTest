from __future__ import annotations

from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/liquidity_cross_factor'))
sys.path.insert(0, str(ROOT / 'research/stock_level_factor_interaction'))
import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as multi
import run_cf20_decomposition_liquidity_ranges as core

OUT = Path(__file__).resolve().parent / 'results_cf20_trimmed_activity'
OUT.mkdir(parents=True, exist_ok=True)

UNIVERSES = core.UNIVERSES
FAMILIES = core.FAMILIES
FACTOR_FAMILY = core.FACTOR_FAMILY
CORE = core.CORE
TOPN = 20
HORIZONS = (5, 10, 20)
COSTS = (0, 30, 60)
RNG = np.random.default_rng(20260814)

STRATEGIES = (
    'CF20',
    'VETO_TOP1_ONLY', 'VETO_TOP5_ONLY',
    'TRIM_TOP1_W10', 'TRIM_TOP5_W10',
    'TRIM_TOP1_W20_DIAG', 'TRIM_TOP5_W20_DIAG',
    'BAND_50_95', 'BAND_70_95',
)


def block_boot(x, block=4, nboot=6000):
    x=np.asarray(x,float); x=x[np.isfinite(x)]; n=len(x)
    if n<8:return np.array([])
    nb=int(np.ceil(n/block)); starts=RNG.integers(0,n,size=(nboot,nb))
    idx=(starts[:,:,None]+np.arange(block)[None,None,:])%n
    return x[idx.reshape(nboot,-1)[:,:n]].mean(axis=1)


def score_map(cf20: pd.Series, ar: pd.Series):
    w10=.9*cf20+.1*ar
    w20=.8*cf20+.2*ar
    return {
        'CF20':cf20,
        'VETO_TOP1_ONLY':cf20.where(ar<=.99),
        'VETO_TOP5_ONLY':cf20.where(ar<=.95),
        'TRIM_TOP1_W10':w10.where(ar<=.99),
        'TRIM_TOP5_W10':w10.where(ar<=.95),
        'TRIM_TOP1_W20_DIAG':w20.where(ar<=.99),
        'TRIM_TOP5_W20_DIAG':w20.where(ar<=.95),
        'BAND_50_95':cf20.where((ar>=.50)&(ar<=.95)),
        'BAND_70_95':cf20.where((ar>=.70)&(ar<=.95)),
    }


def act_zone(x):
    if x<=.20:return 'P00_20'
    if x<=.50:return 'P20_50'
    if x<=.70:return 'P50_70'
    if x<=.90:return 'P70_90'
    if x<=.95:return 'P90_95'
    if x<=.99:return 'P95_99'
    return 'P99_100'


def run():
    returns,mcap,k200=base.load_basic(); markets=multi.load_market_by_date()
    ta=base.load_trading_amount(); liq=base.build_liquidity_features(ta,mcap)
    files={f:base.dated_files(path) for f,path in base.FACTORS.items()}
    rows=[]; surface=[]
    for h in HORIZONS:
        fwd=base.forward_returns(returns,h)
        common=sorted(set(returns.index)&set(ta.index)&set(k200)&set(markets))
        dates=[d for d in common if d>=base.START and d in fwd.index][::h]
        holdings={}
        for dt in dates:
            k=k200[dt]; market=markets[dt]
            act5_full=liq['act5'].loc[dt] if dt in liq['act5'].index else pd.Series(dtype=float)
            for u in UNIVERSES:
                codes=multi.universe_codes(u,k,market); y=fwd.loc[dt].reindex(codes)
                if y.notna().sum() < (70 if u=='K200' else 120):continue
                scores,others=core.build_scores(dt,codes,files)
                if len(scores)<8:continue
                act5=act5_full.reindex(codes)
                ar=pd.to_numeric(act5,errors='coerce').rank(pct=True,method='average')
                for f,primary in scores.items():
                    cf20=.8*primary+.2*others[f]
                    for strat,score in score_map(cf20,ar).items():
                        names=core.top_names(score,TOPN)
                        if len(names)<TOPN:continue
                        key=(h,u,f,strat); old=holdings.get(key,[])
                        turn=1-len(set(old)&set(names))/TOPN if old else 1.0
                        rows.append({'date':dt,'sample':core.sample_of(dt),'horizon':h,'universe':u,
                            'factor':f,'family':FACTOR_FAMILY[f],'strategy':strat,
                            'gross':float(y.reindex(names).mean()),'turnover':turn,
                            'mean_act5_rank':float(ar.reindex(names).mean()),
                            'top1_share':float((ar.reindex(names)>.99).mean()),
                            'top5_share':float((ar.reindex(names)>.95).mean())})
                        holdings[key]=names
                    if h==10:
                        pool=cf20.dropna().sort_values(ascending=False).head(100).index
                        for code in pool:
                            rr=ar.get(code,np.nan); yy=y.get(code,np.nan)
                            if np.isfinite(rr) and np.isfinite(yy):
                                surface.append({'date':dt,'sample':core.sample_of(dt),'universe':u,'factor':f,
                                    'family':FACTOR_FAMILY[f],'code':code,'cf20_rank':float(cf20.rank(ascending=False).get(code,np.nan)),
                                    'act5_rank':float(rr),'zone':act_zone(float(rr)),'fwd10':float(yy)})
    p=pd.DataFrame(rows);s=pd.DataFrame(surface)
    p.to_csv(OUT/'paths.csv',index=False);s.to_csv(OUT/'surface_top100.csv',index=False)
    return p,s


def evaluate(p):
    b=p[p.strategy.eq('CF20')][['date','sample','horizon','universe','factor','family','gross','turnover']].rename(columns={'gross':'base_gross','turnover':'base_turnover'})
    x=p[p.strategy.ne('CF20')].merge(b,on=['date','sample','horizon','universe','factor','family'],how='inner')
    x['gross_delta']=x.gross-x.base_gross;x['turnover_delta']=x.turnover-x.base_turnover
    for c in COSTS:x[f'net_delta_{c}']=x.gross_delta-x.turnover_delta*c/10000
    x.to_csv(OUT/'matched.csv',index=False)
    stats=[];fam=[];boots=[]
    for key,g in x.groupby(['strategy','universe','horizon','sample']):
        d=g.groupby('date').agg(gross_delta=('gross_delta','mean'),turnover_delta=('turnover_delta','mean'),
            **{f'net_{c}':(f'net_delta_{c}','mean') for c in COSTS}).reset_index().sort_values('date')
        rec=dict(zip(['strategy','universe','horizon','sample'],key))|{'n_dates':len(d),'gross_delta':d.gross_delta.mean(),'turnover_delta':d.turnover_delta.mean()}
        for c in COSTS:rec[f'net_delta_{c}']=d[f'net_{c}'].mean()
        stats.append(rec)
        for metric in ['gross_delta','net_30','net_60']:
            bs=block_boot(d[metric].to_numpy())
            if len(bs):boots.append(rec|{'metric':metric,'mean':d[metric].mean(),'ci025':np.quantile(bs,.025),'ci975':np.quantile(bs,.975),'p_gt0':(bs>0).mean()})
    for key,g in x.groupby(['strategy','universe','horizon','sample','family']):
        d=g.groupby('date').gross_delta.mean();fam.append(dict(zip(['strategy','universe','horizon','sample','family'],key))|{'n_dates':len(d),'gross_delta':d.mean()})
    stats=pd.DataFrame(stats);fam=pd.DataFrame(fam);boots=pd.DataFrame(boots)
    stats.to_csv(OUT/'summary.csv',index=False);fam.to_csv(OUT/'family.csv',index=False);boots.to_csv(OUT/'bootstrap.csv',index=False)
    return stats,fam,boots


def surface_summary(s):
    zone=[];con=[]
    for key,g in s.groupby(['universe','sample','zone']):
        d=g.groupby(['date','factor']).fwd10.mean().groupby('date').mean()
        zone.append(dict(zip(['universe','sample','zone'],key))|{'n_dates':len(d),'fwd10':d.mean()})
    # contrasts designed before looking at outcomes
    for key,g in s.groupby(['universe','sample']):
        fd=g.groupby(['date','factor','zone']).fwd10.mean().unstack('zone')
        daily=fd.groupby('date').mean()
        combos=[
            ('P70_90','P99_100'),('P90_95','P99_100'),('P70_90','P00_20'),
            ('P90_95','P00_20'),('P95_99','P99_100'),('P70_90','P95_99'),
        ]
        for a,b in combos:
            if a not in daily or b not in daily:continue
            d=(daily[a]-daily[b]).dropna().sort_index();bs=block_boot(d.to_numpy())
            con.append({'universe':key[0],'sample':key[1],'contrast':f'{a}_MINUS_{b}','n_dates':len(d),'mean':d.mean(),
                'ci025':np.quantile(bs,.025) if len(bs) else np.nan,'ci975':np.quantile(bs,.975) if len(bs) else np.nan,'p_gt0':(bs>0).mean() if len(bs) else np.nan})
    zone=pd.DataFrame(zone);con=pd.DataFrame(con)
    zone.to_csv(OUT/'surface_zones.csv',index=False);con.to_csv(OUT/'surface_contrasts.csv',index=False)
    return zone,con


def core_values(stats,strat,u,h):
    z=stats[(stats.strategy==strat)&(stats.universe==u)&(stats.horizon==h)]
    mp={r['sample']:r for _,r in z.iterrows()}
    if not all(s in mp for s in CORE):return None
    return [float(mp[s].net_delta_30) for s in CORE]


def report(stats,fam,con):
    L=['# CF20 Trimmed Activity Preference Extension','',
       'This extension was predeclared after the broad range/veto test was already launched, and is evaluated separately. CF20 is fixed. ACT5 is used either as an extreme-hot veto, a monotonic preference after that veto, or a moderate-activity eligibility band.','',
       '## Core-block 30bp-net results','']
    for strat in STRATEGIES[1:]:
        L.append(f'### {strat}')
        anyrow=False
        for u in UNIVERSES:
            for h in HORIZONS:
                v=core_values(stats,strat,u,h)
                if v is None:continue
                ok=all(x>0 for x in v); anyrow=True
                L.append(f"- {u} H{h}: {v[0]:+.2%} -> {v[1]:+.2%} -> {v[2]:+.2%}; {'PASS' if ok else 'FAIL'}")
        if not anyrow:L.append('- no complete core blocks')
    L+=['','## Stable passing specifications only','']
    for strat in STRATEGIES[1:]:
        for u in UNIVERSES:
            for h in HORIZONS:
                v=core_values(stats,strat,u,h)
                if v is not None and all(x>0 for x in v):
                    z=fam[(fam.strategy==strat)&(fam.universe==u)&(fam.horizon==h)&(fam['sample'].isin(CORE))]
                    pos=z.groupby('sample').apply(lambda q:int((q.gross_delta>0).sum()),include_groups=False).to_dict() if len(z) else {}
                    L.append(f"- {strat} / {u} / H{h}: {v[0]:+.2%}->{v[1]:+.2%}->{v[2]:+.2%}; positive-family counts {pos}")
    L+=['','## ACT5 shape in frozen CF20 Top100, H10','']
    for u in UNIVERSES:
        for s in CORE:
            z=con[(con.universe==u)&(con['sample']==s)]
            if z.empty:continue
            items=[f"{r.contrast} {r['mean']:+.2%} (P>0 {r.p_gt0:.0%})" for _,r in z.iterrows()]
            L.append(f"- {u} {s}: "+'; '.join(items))
    L+=['','## Interpretation guardrails','',
       '- Main trimmed-preference hypotheses are TRIM_TOP1_W10 and TRIM_TOP5_W10. W20 versions are weight-sensitivity diagnostics.',
       '- BAND_50_95 and BAND_70_95 test whether moderate/high-but-not-extreme activity is better than monotonic activity preference.',
       '- Passing requires positive 30bp-net edge in all three core historical blocks for the same universe and horizon.',
       '- 2025/2026 are retained in CSVs as stress diagnostics but do not determine promotion.','']
    return '\n'.join(L)+'\n'


def main():
    p,s=run();stats,fam,_=evaluate(p);_,con=surface_summary(s)
    (OUT/'RESEARCH_SUMMARY.md').write_text(report(stats,fam,con),encoding='utf-8')
    print(f'paths={len(p):,}; surface={len(s):,}; specs={len(stats):,}')

if __name__=='__main__':main()
