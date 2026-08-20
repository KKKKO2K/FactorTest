from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
OUT=HERE/'results_transition_allocation'
OUT.mkdir(parents=True,exist_ok=True)
PANEL=HERE/'results/market_incremental_panel.csv'
MARKET=ROOT/'research/factor_regime_v1/results/market_daily_returns.csv'
MIN_CELL=20
COSTS=(0,10,30)

PERIODS={
 'TRAIN_2016_2022':('2016-01-01','2022-12-31'),
 'OOS_2023_2024':('2023-01-01','2024-12-31'),
 'BULL_2025':('2025-01-01','2025-12-31'),
 'YTD_2026':('2026-01-01','2026-12-31'),
}


def fit_probs(g):
    tr=g[g.date<pd.Timestamp('2023-01-01')].dropna(subset=['TARGET_NEXT_B_DOWN','base_state','factor_substate'])
    global_p=float(tr.TARGET_NEXT_B_DOWN.mean())
    b=tr.groupby('base_state').TARGET_NEXT_B_DOWN.agg(['mean','count'])
    bf=tr.groupby(['base_state','factor_substate']).TARGET_NEXT_B_DOWN.agg(['mean','count'])
    def pb(row):
        return float(b.loc[row.base_state,'mean']) if row.base_state in b.index else global_p
    def pbf(row):
        fallback=pb(row)
        key=(row.base_state,row.factor_substate)
        if key in bf.index and int(bf.loc[key,'count'])>=MIN_CELL:
            return float(bf.loc[key,'mean'])
        return fallback
    return pb,pbf,b,bf


def metrics(r):
    r=pd.Series(r).dropna()
    if len(r)<20:return {'cagr':np.nan,'sharpe':np.nan,'mdd':np.nan}
    nav=(1+r).cumprod(); years=len(r)/252
    cagr=float(nav.iloc[-1]**(1/years)-1)
    sd=r.std(ddof=1); sharpe=float(r.mean()/sd*math.sqrt(252)) if sd>0 else np.nan
    mdd=float((nav/nav.cummax()-1).min())
    return {'cagr':cagr,'sharpe':sharpe,'mdd':mdd}


def build():
    x=pd.read_csv(PANEL);x['date']=pd.to_datetime(x.date)
    m=pd.read_csv(MARKET,index_col=0);m.index=pd.to_datetime(m.index);m=m.sort_index()
    rows=[];state_rows=[]
    for u,g0 in x.groupby('universe'):
        g=g0.sort_values('date').copy()
        pb,pbf,b,bf=fit_probs(g)
        g['p_down_b']=g.apply(pb,axis=1)
        g['p_down_bf']=g.apply(pbf,axis=1)
        g['exp_b']=1-g.p_down_b
        g['exp_bf_raw']=1-g.p_down_bf
        # TRAIN-only average exposure normalization isolates information from average risk budget.
        tr=g[g.date<pd.Timestamp('2023-01-01')]
        scale=float(tr.exp_b.mean()/tr.exp_bf_raw.mean()) if tr.exp_bf_raw.mean()>0 else 1.0
        g['exp_bf']=(g.exp_bf_raw*scale).clip(0,1)
        g['bf_minus_b']=g.p_down_bf-g.p_down_b
        state_rows.append(g[['date','universe','base_state','factor_substate','TARGET_NEXT_B_DOWN','p_down_b','p_down_bf','exp_b','exp_bf','bf_minus_b']])
        if u not in m.columns:continue
        d=pd.DataFrame({'date':m.index,'market_ret':pd.to_numeric(m[u],errors='coerce').to_numpy()}).sort_values('date')
        sig=g[['date','exp_b','exp_bf']].dropna().sort_values('date')
        # signal at close t becomes active from next trading day: strictly previous state date only.
        d=pd.merge_asof(d,sig,on='date',direction='backward',allow_exact_matches=False)
        d=d.dropna(subset=['market_ret','exp_b','exp_bf']).copy()
        for policy,col in [('B_ONLY_PROB','exp_b'),('B_FSUB_PROB','exp_bf')]:
            target=d[col].astype(float)
            alloc_turn=target.diff().abs().fillna(0)
            gross=target*d.market_ret
            for cost in COSTS:
                net=gross-alloc_turn*(cost/10000)
                for period,(a,bdate) in PERIODS.items():
                    mask=d.date.between(a,bdate)
                    rr=net[mask]
                    if len(rr)<20:continue
                    met=metrics(rr)
                    rows.append({
                        'universe':u,'policy':policy,'cost_bps':cost,'period':period,
                        **met,
                        'avg_exposure':float(target[mask].mean()),
                        'annual_allocator_turnover':float(alloc_turn[mask].sum()*252/len(rr)),
                        'n_days':len(rr),
                    })
    state=pd.concat(state_rows,ignore_index=True)
    perf=pd.DataFrame(rows)
    state.to_csv(OUT/'transition_probability_states.csv',index=False,encoding='utf-8-sig')
    perf.to_csv(OUT/'transition_allocation_performance.csv',index=False,encoding='utf-8-sig')
    return state,perf


def compare(perf):
    b=perf[perf.policy=='B_ONLY_PROB'].rename(columns={'cagr':'base_cagr','sharpe':'base_sharpe','mdd':'base_mdd','avg_exposure':'base_avg_exposure','annual_allocator_turnover':'base_turn'})
    a=perf[perf.policy=='B_FSUB_PROB']
    keys=['universe','cost_bps','period']
    z=a.merge(b[keys+['base_cagr','base_sharpe','base_mdd','base_avg_exposure','base_turn']],on=keys)
    z['delta_cagr']=z.cagr-z.base_cagr
    z['delta_sharpe']=z.sharpe-z.base_sharpe
    z['delta_mdd']=z.mdd-z.base_mdd
    z['delta_avg_exposure']=z.avg_exposure-z.base_avg_exposure
    z['delta_turn']=z.annual_allocator_turnover-z.base_turn
    z.to_csv(OUT/'transition_allocation_vs_base.csv',index=False,encoding='utf-8-sig')
    return z


def pct(x):return 'NA' if pd.isna(x) else f'{x:+.2%}'

def report(state,perf,z):
    lines=['# Transition-Probability Market Allocation Audit','',
      '- This is a mechanical action test of the one Factor Regime signal that passed the information-value gate: B × F substate for next-B-down probability.',
      '- TRAIN 2016-22 conditional probabilities are frozen. Exposure = 1 - predicted P(next B down). B×F exposure is TRAIN-normalized to the same average exposure as B-only, then clipped to [0,1].',
      '- Signal dated t applies from the next trading day. Market daily returns are the same universe cap-weighted series used in Factor Regime v1.',
      '- Costs of 0/10/30 bps are charged only on absolute allocator exposure changes at state updates. No return-fitted exposure threshold is used.','']
    for cost in COSTS:
      lines += [f'## Cost {cost} bps','']
      for period in ('TRAIN_2016_2022','OOS_2023_2024','BULL_2025','YTD_2026'):
        q=z[(z.cost_bps==cost)&(z.period==period)]
        if q.empty:continue
        lines.append(f'### {period}')
        lines.append(f'- median ΔCAGR {pct(q.delta_cagr.median())}; ΔSharpe {q.delta_sharpe.median():+.3f}; ΔMDD {pct(q.delta_mdd.median())}; Δavg exposure {pct(q.delta_avg_exposure.median())}; CAGR-better {(q.delta_cagr>0).sum()}/{len(q)}, MDD-better {(q.delta_mdd>0).sum()}/{len(q)}')
        lines.append('')
    lines += ['## OOS 2023-24 universe detail — 10 bps','']
    q=z[(z.cost_bps==10)&(z.period=='OOS_2023_2024')]
    for r in q.sort_values('universe').itertuples(index=False):
        lines.append(f'- {r.universe}: ΔCAGR {pct(r.delta_cagr)}, ΔSharpe {r.delta_sharpe:+.3f}, ΔMDD {pct(r.delta_mdd)}, avg exposure {r.avg_exposure:.1%} vs {r.base_avg_exposure:.1%}')
    lines += ['','## Interpretation gate','',
      '- Production evidence requires OOS 2023-24 median Sharpe improvement and non-worse median MDD at 10 bps, with Sharpe improvement in at least 4/6 universes.',
      '- 2025/2026-only success is stress evidence, not confirmation.',
      '- This allocation mapping is intentionally mechanical; if it fails, do not tune probability thresholds on 2025/2026.']
    return '\n'.join(lines)


def main():
    s,p=build();z=compare(p);text=report(s,p,z)
    (OUT/'RESEARCH_SUMMARY.md').write_text(text,encoding='utf-8');print(text)

if __name__=='__main__':main()
