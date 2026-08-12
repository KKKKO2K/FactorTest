from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
OUT=HERE/'results'
BLOCK=4
NBOOT=5000
RNG=np.random.default_rng(20260813)
CORE_SAMPLES=['EARLY_2016_2019','LATE_2020_2022','NORMAL_2023_2024']


def moving_block_means(x:np.ndarray,block:int=BLOCK,nboot:int=NBOOT)->np.ndarray:
    x=np.asarray(x,float);x=x[np.isfinite(x)];n=len(x)
    if n<8:return np.array([])
    starts=np.arange(n);out=np.empty(nboot)
    nblocks=int(np.ceil(n/block))
    for b in range(nboot):
        chosen=[]
        for _ in range(nblocks):
            s=int(RNG.integers(0,n)); chosen.extend(x[(s+np.arange(block))%n].tolist())
        out[b]=np.mean(chosen[:n])
    return out


def main():
    x=pd.read_csv(OUT/'matched_overlay_deltas.csv');x['date']=pd.to_datetime(x.date)
    x=x[x.overlay.ne('BASE')].copy()
    # Date-level aggregate gives each rebalance date equal weight, after averaging the eight primary factors.
    dateagg=x.groupby(['universe','overlay','sample','date']).agg(net_delta=('delta','mean'),gross_delta=('gross_delta','mean'),turnover_delta=('turnover_delta','mean')).reset_index()
    dateagg.to_csv(OUT/'date_level_overlay_decomposition.csv',index=False)
    dec=[];boot=[]
    for key,g in dateagg.groupby(['universe','overlay','sample']):
        n=len(g);net=g.net_delta.mean();gross=g.gross_delta.mean();turn=g.turnover_delta.mean()
        dec.append(dict(zip(['universe','overlay','sample'],key))|{'n_dates':n,'net_delta':net,'gross_delta':gross,'turnover_delta':turn,
                    'implied_cost_component':net-gross,'positive_gross_date_rate':(g.gross_delta>0).mean(),'positive_net_date_rate':(g.net_delta>0).mean()})
        for metric in ['net_delta','gross_delta']:
            bs=moving_block_means(g.sort_values('date')[metric].to_numpy())
            if len(bs):
                boot.append(dict(zip(['universe','overlay','sample'],key))|{'metric':metric,'n_dates':n,'mean':g[metric].mean(),
                            'ci025':np.quantile(bs,.025),'ci975':np.quantile(bs,.975),'p_gt0':(bs>0).mean()})
    dec=pd.DataFrame(dec);bt=pd.DataFrame(boot);dec.to_csv(OUT/'overlay_decomposition.csv',index=False);bt.to_csv(OUT/'overlay_block_bootstrap.csv',index=False)

    # Family breadth: effect should not be just one economic family.
    fd=x.groupby(['universe','overlay','sample','family','date']).agg(net_delta=('delta','mean'),gross_delta=('gross_delta','mean')).reset_index()
    fa=fd.groupby(['universe','overlay','sample','family']).agg(n_dates=('date','nunique'),net_delta=('net_delta','mean'),gross_delta=('gross_delta','mean'),positive_date_rate=('net_delta',lambda s:(s>0).mean())).reset_index()
    fa.to_csv(OUT/'family_level_overlay_edge.csv',index=False)

    cand=[]
    for (u,ov),g in dec.groupby(['universe','overlay']):
        mp={r['sample']:r for _,r in g.iterrows()}
        if not all(s in mp for s in CORE_SAMPLES):continue
        net=[mp[s].net_delta for s in CORE_SAMPLES];gross=[mp[s].gross_delta for s in CORE_SAMPLES]
        fsub=fa[(fa.universe==u)&(fa.overlay==ov)&(fa['sample'].isin(CORE_SAMPLES))]
        fampos=fsub.groupby('sample').apply(lambda z:(z.gross_delta>0).sum(),include_groups=False).to_dict() if len(fsub) else {}
        cand.append({'universe':u,'overlay':ov,'net_all3_pos':all(v>0 for v in net),'gross_all3_pos':all(v>0 for v in gross),
                     'early_net':net[0],'late_net':net[1],'normal_net':net[2],'early_gross':gross[0],'late_gross':gross[1],'normal_gross':gross[2],
                     'early_pos_families':fampos.get(CORE_SAMPLES[0],0),'late_pos_families':fampos.get(CORE_SAMPLES[1],0),'normal_pos_families':fampos.get(CORE_SAMPLES[2],0),
                     'bull2025_net':mp['BULL_2025'].net_delta if 'BULL_2025' in mp else np.nan,'ytd2026_net':mp['YTD_2026'].net_delta if 'YTD_2026' in mp else np.nan})
    cand=pd.DataFrame(cand);cand.to_csv(OUT/'validated_candidates.csv',index=False)

    L=['# Stock-Level Factor Interaction — Robustness Validation','',
       'This validation decomposes the previously matched 30-bps-net edge into gross stock-selection alpha and turnover/cost contribution. Inference uses 4-rebalance-date moving-block bootstrap on date-level factor-averaged deltas.','',
       '## Candidates with positive NET and GROSS edge in all three core blocks','']
    q=cand[(cand.net_all3_pos)&(cand.gross_all3_pos)].copy()
    if q.empty:L.append('- None')
    else:
        for _,r in q.sort_values('normal_net',ascending=False).iterrows():
            L.append(f"- {r.universe} {r.overlay}: net {r.early_net:+.2%} -> {r.late_net:+.2%} -> {r.normal_net:+.2%}; gross {r.early_gross:+.2%} -> {r.late_gross:+.2%} -> {r.normal_gross:+.2%}; positive families {int(r.early_pos_families)}/4 -> {int(r.late_pos_families)}/4 -> {int(r.normal_pos_families)}/4; 2025 net {r.bull2025_net:+.2%}; 2026 net {r.ytd2026_net:+.2%}")
    L+=['','## Block-bootstrap — core candidate overlays','']
    focus=bt[(bt.overlay.isin(['CROSS_FAMILY_W10','CROSS_FAMILY_W20','SIBLING_W20']))&(bt['sample'].isin(CORE_SAMPLES))]
    for (u,ov),g in focus.groupby(['universe','overlay']):
        # only show candidates whose net sign is positive in all core samples
        d=dec[(dec.universe==u)&(dec.overlay==ov)&(dec['sample'].isin(CORE_SAMPLES))]
        if len(d)!=3 or not (d.net_delta>0).all():continue
        L.append(f'### {u} {ov}')
        for _,r in g[g.metric.eq('net_delta')].sort_values('sample').iterrows():
            L.append(f"- {r['sample']}: {r['mean']:+.2%}/10D; 95% CI [{r.ci025:+.2%}, {r.ci975:+.2%}], P(edge>0) {r.p_gt0:.0%}, n={int(r.n_dates)}")
    L+=['','## Cost decomposition for CROSS_FAMILY_W20','']
    for _,r in dec[dec.overlay.eq('CROSS_FAMILY_W20')].sort_values(['universe','sample']).iterrows():
        L.append(f"- {r.universe} {r['sample']}: gross {r.gross_delta:+.2%}, net {r.net_delta:+.2%}, turnover change {r.turnover_delta:+.1%}; cost contribution {r.implied_cost_component:+.2%}")
    L+=['','## Decision rule','',
       '- Do not call the overlay structural if net edge is produced only by lower turnover; gross edge must also be positive in 2016-19, 2020-22, and 2023-24.',
       '- Prefer effects spread across multiple primary factor families. A single-family result is hypothesis-generating only.',
       '- 2025/2026 remain stress diagnostics and are not used to select candidates.','']
    (OUT/'ROBUSTNESS_SUMMARY.md').write_text('\n'.join(L)+'\n',encoding='utf-8')
    print(f'decomp={len(dec)}, bootstrap={len(bt)}, validated={len(q)}')

if __name__=='__main__':main()
