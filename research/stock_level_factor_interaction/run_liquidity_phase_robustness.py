from __future__ import annotations

from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/liquidity_cross_factor'))
sys.path.insert(0, str(ROOT / 'research/stock_level_factor_interaction'))
sys.path.insert(0, str(ROOT / 'research/common'))
import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as multi
import run_cf20_decomposition_liquidity_ranges as core
import run_alt_liquidity_veto_sensitivity as alt
from chunked_csv import write_chunked_csv

OUT = Path(__file__).resolve().parent / 'results_liquidity_phase_robustness'
OUT.mkdir(parents=True, exist_ok=True)
H = 10
TOPN = 20
COST_BP = 30

# Frozen after the H10 metric screen; no new cutoff search here.
CANDIDATES = {
    'KOSPI_EX_K200': [
        ('ACT5','LOW10'),
        ('ADV20','LOW10'),
        ('TURNOVER20','TOP01'),
        ('TURNOVER20','TOP01_LOW10'),
        ('AMIHUD20','TOP05'),
    ],
    'KOSDAQ': [
        ('ACT5','LOW30'),
        ('TURNOVER20','LOW30'),
        ('TURNOVER20','TOP01_LOW30'),
        ('ACT1','LOW05'),
        ('AMIHUD20','TOP05'),
    ],
}


def apply_strategy(cf20: pd.Series, rank: pd.Series, strategy: str) -> pd.Series:
    if strategy == 'CF20':
        return cf20
    mask = pd.Series(True, index=cf20.index)
    for token in strategy.split('_'):
        if token.startswith('TOP'):
            cut = int(token[3:]) / 100
            mask &= rank <= 1 - cut
        elif token.startswith('LOW'):
            cut = int(token[3:]) / 100
            mask &= rank >= cut
        else:
            raise ValueError(strategy)
    return cf20.where(mask)


def run() -> pd.DataFrame:
    returns, mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    ta = base.load_trading_amount()
    liq = alt.build_alt_liquidity(ta, mcap, returns)
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}
    fwd = base.forward_returns(returns, H)
    common = sorted(set(returns.index) & set(ta.index) & set(k200) & set(markets) & set(fwd.index))
    dates = [d for d in common if d >= base.START]

    holdings: dict[tuple, list[str]] = {}
    rows=[]
    for i,dt in enumerate(dates):
        phase = i % H
        k = k200[dt]
        market = markets[dt]
        for u, candidates in CANDIDATES.items():
            codes = multi.universe_codes(u, k, market)
            y = fwd.loc[dt].reindex(codes)
            if y.notna().sum() < 120:
                continue
            scores, others = core.build_scores(dt, codes, files)
            if len(scores) < 8:
                continue
            needed_metrics = sorted({m for m,_ in candidates})
            ranks={}
            for metric in needed_metrics:
                v = liq[metric].loc[dt].reindex(codes) if dt in liq[metric].index else pd.Series(index=codes,dtype=float)
                ranks[metric] = pd.to_numeric(v,errors='coerce').rank(pct=True,method='average')
            for f,primary in scores.items():
                cf20 = 0.8*primary + 0.2*others[f]
                specs=[('BASE','CF20',None)] + [(metric,strategy,ranks[metric]) for metric,strategy in candidates]
                for metric,strategy,rank in specs:
                    score = cf20 if strategy=='CF20' else apply_strategy(cf20,rank,strategy)
                    names = core.top_names(score,TOPN)
                    if len(names)<TOPN:
                        continue
                    key=(phase,u,f,metric,strategy)
                    old=holdings.get(key,[])
                    turn=1-len(set(old)&set(names))/TOPN if old else 1.0
                    rows.append({
                        'date':dt,'phase':phase,'sample':core.sample_of(dt),'universe':u,
                        'factor':f,'family':core.FACTOR_FAMILY[f],'metric':metric,'strategy':strategy,
                        'gross':float(y.reindex(names).mean()),'turnover':turn,
                    })
                    holdings[key]=names
    p=pd.DataFrame(rows)
    write_chunked_csv(p,OUT/'paths.csv',index=False,target_mb=40)
    return p


def evaluate(p: pd.DataFrame):
    b=p[(p.metric=='BASE')&(p.strategy=='CF20')][['date','phase','sample','universe','factor','family','gross','turnover']].rename(columns={'gross':'base_gross','turnover':'base_turnover'})
    x=p[~((p.metric=='BASE')&(p.strategy=='CF20'))].merge(b,on=['date','phase','sample','universe','factor','family'],how='inner')
    x['gross_delta']=x.gross-x.base_gross
    x['turnover_delta']=x.turnover-x.base_turnover
    x['net_delta_30']=x.gross_delta-x.turnover_delta*COST_BP/10000
    write_chunked_csv(x,OUT/'matched.csv',index=False,target_mb=40)

    phase=[]; family=[]
    for key,g in x.groupby(['universe','metric','strategy','sample','phase']):
        d=g.groupby('date').net_delta_30.mean()
        phase.append(dict(zip(['universe','metric','strategy','sample','phase'],key))|{'n_dates':len(d),'net_delta_30':d.mean()})
    for key,g in x.groupby(['universe','metric','strategy','sample','phase','family']):
        d=g.groupby('date').net_delta_30.mean()
        family.append(dict(zip(['universe','metric','strategy','sample','phase','family'],key))|{'n_dates':len(d),'net_delta_30':d.mean()})
    phase=pd.DataFrame(phase); family=pd.DataFrame(family)
    phase.to_csv(OUT/'phase.csv',index=False); family.to_csv(OUT/'family_phase.csv',index=False)

    rows=[]
    for key,g in phase.groupby(['universe','metric','strategy','sample']):
        vals=g.net_delta_30.to_numpy(float)
        rows.append(dict(zip(['universe','metric','strategy','sample'],key))|{
            'n_phases':len(vals),'mean_phase_edge':np.mean(vals),'median_phase_edge':np.median(vals),
            'min_phase_edge':np.min(vals),'max_phase_edge':np.max(vals),'std_phase_edge':np.std(vals,ddof=1) if len(vals)>1 else np.nan,
            'positive_phases':int((vals>0).sum()),'positive_phase_share':float((vals>0).mean()),
        })
    summary=pd.DataFrame(rows)
    summary.to_csv(OUT/'summary.csv',index=False)
    return summary,family


def report(summary: pd.DataFrame,family: pd.DataFrame)->str:
    lines=['# H10 Liquidity Rebalance-Phase Robustness','',
           'Each candidate is frozen from the prior H10 screen. All 10 possible non-overlapping 10-trading-day rebalance offsets are evaluated.','',
           'Headline fields are mean edge across phases, worst phase, and positive phase count. 30bp turnover cost is included.','']
    samples = tuple(core.CORE) + ('BULL_2025','YTD_2026')
    for u,candidates in CANDIDATES.items():
        lines += [f'## {u}','']
        for metric,strategy in candidates:
            lines.append(f'### {metric} {strategy}')
            z=summary[(summary.universe==u)&(summary.metric==metric)&(summary.strategy==strategy)]
            for sample in samples:
                q=z[z['sample']==sample]
                if len(q):
                    r=q.iloc[0]
                    lines.append(f"- {sample}: mean {r.mean_phase_edge:+.2%}; median {r.median_phase_edge:+.2%}; worst {r.min_phase_edge:+.2%}; +phases {int(r.positive_phases)}/{int(r.n_phases)}")
            lines.append('')
    lines += ['## Guardrails','',
              '- Phase robustness is diagnostic; no candidate/cutoff is changed based on the best phase.',
              '- A production-worthy veto should not depend on one arbitrary rebalance offset. Mean and worst-phase behavior matter more than the best phase.',
              '- Large intermediates are retained as GitHub-safe chunked gzip CSVs with manifests.','']
    return '\n'.join(lines)


if __name__=='__main__':
    p=run(); summary,family=evaluate(p)
    text=report(summary,family)
    (OUT/'RESEARCH_SUMMARY.md').write_text(text,encoding='utf-8')
    print(text)
    print(f'paths={len(p):,}; phase_rows={len(summary):,}')
