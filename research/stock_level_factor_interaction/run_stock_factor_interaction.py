from __future__ import annotations

import math
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0,str(ROOT/'research/liquidity_cross_factor'))
import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as multi

OUT=Path(__file__).resolve().parent/'results'; OUT.mkdir(parents=True,exist_ok=True)
FAMILIES={
    'MOMENTUM':['MOM1M','MOM12_1'],
    'REVISION':['OP12_REV','OPFY1_REV'],
    'VALUE':['PBR12MF','PER12MF'],
    'FLOW':['PRIVATE_FLOW','FOREIGN_FLOW'],
}
FACTOR_FAMILY={f:k for k,v in FAMILIES.items() for f in v}
# Canonical preferred directions; score 1 = preferred/best.
HIGH_GOOD={'MOM1M':True,'MOM12_1':True,'OP12_REV':True,'OPFY1_REV':True,
           'PBR12MF':False,'PER12MF':False,'PRIVATE_FLOW':True,'FOREIGN_FLOW':True}
UNIVERSES=('K200','KOSPI_EX_K200','KOSPI_ALL','KOSDAQ','KOSPI_KOSDAQ_ALL','KOSDAQ_PLUS_KOSPI_EX_K200')
TOP_N=20; H=10; STEP=10; COST_BPS=30
OVERLAYS=('BASE','SIBLING_W20','CROSS_FAMILY_W10','CROSS_FAMILY_W20','FOUR_FAMILY_EW')


def sample_of(d):
    y=d.year
    if y<=2019:return 'EARLY_2016_2019'
    if y<=2022:return 'LATE_2020_2022'
    if y<=2024:return 'NORMAL_2023_2024'
    if y==2025:return 'BULL_2025'
    return 'YTD_2026'

def ann(r):
    if len(r)<2:return np.nan
    return float((1+r).prod()**((252/H)/len(r))-1)
def sharpe(r):
    sd=r.std(ddof=1)
    return float(r.mean()/sd*math.sqrt(252/H)) if len(r)>2 and sd>0 else np.nan
def mdd(r):
    nav=(1+r.fillna(0)).cumprod();return float((nav/nav.cummax()-1).min()) if len(nav) else np.nan

def rank_good(raw,high_good):
    # pandas ascending=True gives the largest percentile to largest values.
    return pd.to_numeric(raw,errors='coerce').rank(pct=True,method='average',ascending=True if high_good else False)

def main():
    returns,mcap,k200=base.load_basic(); markets=multi.load_market_by_date();fwd=base.forward_returns(returns,H)
    files={f:base.dated_files(path) for f,path in base.FACTORS.items()}
    common=sorted(set(returns.index)&set(k200)&set(markets)); dates=[d for d in common if d>=base.START][::STEP]
    holdings={};rows=[];ics=[]
    for dt in dates:
        if dt not in fwd.index:continue
        k=k200[dt]; market=markets[dt]
        raws={f:base.load_factor(fs[dt]) for f,fs in files.items() if dt in fs}
        if len(raws)<8:continue
        for u in UNIVERSES:
            codes=multi.universe_codes(u,k,market); y=fwd.loc[dt].reindex(codes)
            minobs=70 if u=='K200' else 120
            if y.notna().sum()<minobs:continue
            scores={f:rank_good(raws[f].reindex(codes),HIGH_GOOD[f]) for f in raws}
            fam={name:pd.concat([scores[x] for x in members],axis=1).mean(axis=1) for name,members in FAMILIES.items()}
            fam_all=pd.concat(fam,axis=1).mean(axis=1)
            # record stock-level IC diagnostics for the generic overlay ingredients.
            for f,s in scores.items():
                pair=pd.concat([s.rename('x'),y.rename('y')],axis=1).dropna()
                if len(pair)>=50:
                    ics.append({'date':dt,'universe':u,'factor':f,'family':FACTOR_FAMILY[f],'base_ic':pair.x.corr(pair.y)})
            for f,primary in scores.items():
                ff=FACTOR_FAMILY[f]; sib=[x for x in FAMILIES[ff] if x!=f][0]
                otherfam=pd.concat([v for n,v in fam.items() if n!=ff],axis=1).mean(axis=1)
                overlays={
                    'BASE':primary,
                    'SIBLING_W20':.8*primary+.2*scores[sib],
                    'CROSS_FAMILY_W10':.9*primary+.1*otherfam,
                    'CROSS_FAMILY_W20':.8*primary+.2*otherfam,
                    'FOUR_FAMILY_EW':fam_all,
                }
                for ov,score in overlays.items():
                    s=score.dropna().sort_values(ascending=False)
                    if len(s)<TOP_N:continue
                    names=s.head(TOP_N).index.tolist(); gross=float(y.reindex(names).mean())
                    key=(u,f,ov); old=holdings.get(key,[]);turn=1-len(set(old)&set(names))/TOP_N if old else 1.0
                    net=gross-turn*COST_BPS/10000
                    rows.append({'date':dt,'universe':u,'factor':f,'family':ff,'overlay':ov,'gross':gross,'net':net,'turnover':turn,
                                 'n_universe':len(codes),'eligible':len(s)})
                    holdings[key]=names
    p=pd.DataFrame(rows);p['date']=pd.to_datetime(p.date);p['sample']=p.date.map(sample_of)
    p.to_csv(OUT/'period_returns.csv',index=False)
    pd.DataFrame(ics).to_csv(OUT/'base_factor_ic.csv',index=False)
    # exact date/factor matched deltas vs BASE
    b=p[p.overlay.eq('BASE')][['date','universe','factor','net','gross','turnover']].rename(columns={'net':'base_net','gross':'base_gross','turnover':'base_turnover'})
    c=p.merge(b,on=['date','universe','factor'],how='left');c['delta']=c.net-c.base_net;c['gross_delta']=c.gross-c.base_gross;c['turnover_delta']=c.turnover-c.base_turnover
    c.to_csv(OUT/'matched_overlay_deltas.csv',index=False)
    stats=[]
    for key,g in c.groupby(['universe','factor','family','overlay','sample']):
        if len(g)<8:continue
        stats.append(dict(zip(['universe','factor','family','overlay','sample'],key))|{
            'n':len(g),'ann_return':ann(g.net),'sharpe':sharpe(g.net),'mdd':mdd(g.net),'hit_rate':(g.net>0).mean(),'avg_turnover':g.turnover.mean(),
            'mean_delta_vs_base':g.delta.mean(),'beat_base_rate':(g.delta>0).mean(),'median_delta_vs_base':g.delta.median()})
    st=pd.DataFrame(stats);st.to_csv(OUT/'factor_overlay_performance.csv',index=False)
    # Aggregate across factors without letting one factor dominate by number of dates.
    ag=[]
    for key,g in c.groupby(['universe','overlay','sample']):
        if key[1]=='BASE':continue
        # first average matched delta across 8 primary factors per date, then across dates
        d=g.groupby('date').agg(delta=('delta','mean'),beat=('delta',lambda x:(x>0).mean())).reset_index()
        ag.append(dict(zip(['universe','overlay','sample'],key))|{'n_dates':len(d),'mean_delta':d.delta.mean(),'median_delta':d.delta.median(),
                    'positive_date_rate':(d.delta>0).mean(),'mean_factor_beat_rate':d.beat.mean()})
    agg=pd.DataFrame(ag);agg.to_csv(OUT/'aggregate_overlay_edge.csv',index=False)
    # Strict robustness: same sign in early, late, normal; 2025 is stress only.
    rob=[]
    for key,g in agg.groupby(['universe','overlay']):
        mp={r['sample']:r for _,r in g.iterrows()}
        req=['EARLY_2016_2019','LATE_2020_2022','NORMAL_2023_2024']
        if not all(x in mp for x in req):continue
        vals=[mp[x].mean_delta for x in req];same=all(v>0 for v in vals) or all(v<0 for v in vals)
        rob.append({'universe':key[0],'overlay':key[1],'early':vals[0],'late':vals[1],'normal':vals[2],
                    'same_sign':same,'min_abs':min(abs(v) for v in vals),'bull_2025':mp.get('BULL_2025',{}).get('mean_delta',np.nan) if isinstance(mp.get('BULL_2025'),dict) else (mp['BULL_2025'].mean_delta if 'BULL_2025' in mp else np.nan),
                    'ytd_2026':mp['YTD_2026'].mean_delta if 'YTD_2026' in mp else np.nan})
    rb=pd.DataFrame(rob);rb.to_csv(OUT/'overlay_robustness.csv',index=False)
    L=['# Stock-Level Cross-Factor Interaction','',
       'No learned thresholds or state buckets. Every overlay is fixed ex ante. Top-20 portfolios rebalance every 10 trading days; 30 bps one-way turnover cost is applied.','',
       '## Aggregate matched edge vs each factor BASE','']
    for (u,sm),g in agg.groupby(['universe','sample']):
        L.append(f'### {u} — {sm}')
        for _,r in g.sort_values('mean_delta',ascending=False).iterrows():
            L.append(f"- {r.overlay}: {r.mean_delta:+.2%}/10D; positive dates {r.positive_date_rate:.0%}; mean factor beat-rate {r.mean_factor_beat_rate:.0%}")
    L+=['','## Same-sign robustness across 2016-19 / 2020-22 / 2023-24','']
    if rb.empty:L.append('- None')
    else:
        for _,r in rb[rb.same_sign].sort_values('min_abs',ascending=False).iterrows():
            L.append(f"- {r.universe} {r.overlay}: {r.early:+.2%} -> {r.late:+.2%} -> {r.normal:+.2%}; 2025 {r.bull_2025:+.2%}; 2026 {r.ytd_2026:+.2%}")
    L+=['','## Interpretation','',
       '- SIBLING_W20 tests confirmation inside the same economic factor family.',
       '- CROSS_FAMILY_W10/W20 tests whether broad agreement from the other three families improves a primary factor selection.',
       '- FOUR_FAMILY_EW is a generic multifactor benchmark, not a conditional regime rule.',
       '- Promotion requires positive matched edge in all three historical blocks; 2025/2026 are stress diagnostics, not used to select the rule.','']
    (OUT/'RESEARCH_SUMMARY.md').write_text('\n'.join(L)+'\n',encoding='utf-8')
    print(f'rows={len(p):,}; aggregate={len(agg):,}; robust={int(rb.same_sign.sum()) if not rb.empty else 0}')

if __name__=='__main__':main()
