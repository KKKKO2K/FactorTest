from __future__ import annotations

from functools import lru_cache
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

OUT = Path(__file__).resolve().parent / 'results_alt_liquidity_veto_sensitivity'
OUT.mkdir(parents=True, exist_ok=True)

UNIVERSES = core.UNIVERSES
FAMILIES = core.FAMILIES
FACTOR_FAMILY = core.FACTOR_FAMILY
CORE = core.CORE
TOPN = 20
HORIZONS = (5, 10, 20)
TOP_CUTS = (0.01, 0.05)
LOW_CUTS = (0.05, 0.10, 0.20, 0.30)
COSTS = (0, 30, 60)
RNG = np.random.default_rng(20260815)

METRICS = ('ACT5', 'ADV20', 'TURNOVER20', 'ACT1', 'AMIHUD20')


def block_boot(x, block=4, nboot=4000):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 8:
        return np.array([])
    nb = int(np.ceil(n / block))
    starts = RNG.integers(0, n, size=(nboot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    return x[idx.reshape(nboot, -1)[:, :n]].mean(axis=1)


def build_alt_liquidity(ta: pd.DataFrame, mcap: pd.DataFrame, returns: pd.DataFrame):
    ta = ta.reindex(index=mcap.index, columns=mcap.columns)
    ret = returns.reindex(index=mcap.index, columns=mcap.columns)
    raw = ta.where(ta > 0)
    mc = mcap.where(mcap > 0)
    turnover = raw / mc

    adv20 = raw.rolling(20, min_periods=15).mean()
    turnover20 = turnover.rolling(20, min_periods=15).mean()
    hist20 = raw.shift(1).rolling(20, min_periods=15).mean()
    act1 = raw / hist20
    recent5 = raw.rolling(5, min_periods=4).mean()
    prior20 = raw.shift(5).rolling(20, min_periods=15).mean()
    act5 = recent5 / prior20
    amihud20 = (ret.abs() / raw).replace([np.inf, -np.inf], np.nan).rolling(20, min_periods=15).mean()
    return {'ACT5': act5, 'ADV20': adv20, 'TURNOVER20': turnover20, 'ACT1': act1, 'AMIHUD20': amihud20}


def score_map(cf20: pd.Series, rank: pd.Series):
    out = {'CF20': cf20}
    for t in TOP_CUTS:
        out[f'TOP{int(t*100):02d}'] = cf20.where(rank <= 1-t)
    for l in LOW_CUTS:
        out[f'LOW{int(l*100):02d}'] = cf20.where(rank >= l)
    for t in TOP_CUTS:
        for l in LOW_CUTS:
            out[f'TOP{int(t*100):02d}_LOW{int(l*100):02d}'] = cf20.where((rank <= 1-t) & (rank >= l))
    return out


def run():
    returns, mcap, k200 = base.load_basic()
    markets = multi.load_market_by_date()
    ta = base.load_trading_amount()
    liq = build_alt_liquidity(ta, mcap, returns)
    files = {f: base.dated_files(path) for f, path in base.FACTORS.items()}
    rows = []

    for h in HORIZONS:
        fwd = base.forward_returns(returns, h)
        common = sorted(set(returns.index) & set(ta.index) & set(k200) & set(markets))
        dates = [d for d in common if d >= base.START and d in fwd.index][::h]
        holdings = {}
        for dt in dates:
            k = k200[dt]
            market = markets[dt]
            for u in UNIVERSES:
                codes = multi.universe_codes(u, k, market)
                y = fwd.loc[dt].reindex(codes)
                if y.notna().sum() < (70 if u == 'K200' else 120):
                    continue
                scores, others = core.build_scores(dt, codes, files)
                if len(scores) < 8:
                    continue
                metric_ranks = {}
                for metric in METRICS:
                    v = liq[metric].loc[dt].reindex(codes) if dt in liq[metric].index else pd.Series(index=codes, dtype=float)
                    metric_ranks[metric] = pd.to_numeric(v, errors='coerce').rank(pct=True, method='average')
                for f, primary in scores.items():
                    cf20 = 0.8 * primary + 0.2 * others[f]
                    for metric, rank in metric_ranks.items():
                        for strat, score in score_map(cf20, rank).items():
                            names = core.top_names(score, TOPN)
                            if len(names) < TOPN:
                                continue
                            key = (h, u, f, metric, strat)
                            old = holdings.get(key, [])
                            turn = 1 - len(set(old) & set(names)) / TOPN if old else 1.0
                            rows.append({
                                'date': dt, 'sample': core.sample_of(dt), 'horizon': h,
                                'universe': u, 'factor': f, 'family': FACTOR_FAMILY[f],
                                'metric': metric, 'strategy': strat,
                                'gross': float(y.reindex(names).mean()), 'turnover': turn,
                                'mean_metric_rank': float(rank.reindex(names).mean()),
                            })
                            holdings[key] = names
    p = pd.DataFrame(rows)
    p.to_csv(OUT / 'paths.csv', index=False)
    return p


def evaluate(p: pd.DataFrame):
    b = p[p.strategy.eq('CF20')][['date','sample','horizon','universe','factor','family','metric','gross','turnover']].rename(columns={'gross':'base_gross','turnover':'base_turnover'})
    x = p[p.strategy.ne('CF20')].merge(b, on=['date','sample','horizon','universe','factor','family','metric'], how='inner')
    x['gross_delta'] = x.gross - x.base_gross
    x['turnover_delta'] = x.turnover - x.base_turnover
    for c in COSTS:
        x[f'net_delta_{c}'] = x.gross_delta - x.turnover_delta * c / 10000
    x.to_csv(OUT / 'matched.csv', index=False)

    stats=[]; fam=[]; boots=[]
    for key,g in x.groupby(['metric','strategy','universe','horizon','sample']):
        d = g.groupby('date').agg(gross_delta=('gross_delta','mean'), turnover_delta=('turnover_delta','mean'), **{f'net_{c}':(f'net_delta_{c}','mean') for c in COSTS}).reset_index().sort_values('date')
        rec = dict(zip(['metric','strategy','universe','horizon','sample'],key)) | {'n_dates':len(d), 'gross_delta':d.gross_delta.mean(), 'turnover_delta':d.turnover_delta.mean()}
        for c in COSTS:
            rec[f'net_delta_{c}'] = d[f'net_{c}'].mean()
        stats.append(rec)
        bs = block_boot(d.net_30.to_numpy())
        if len(bs):
            boots.append(rec | {'metric_name':'net_30','ci025':np.quantile(bs,.025),'ci975':np.quantile(bs,.975),'p_gt0':(bs>0).mean()})
    for key,g in x.groupby(['metric','strategy','universe','horizon','sample','family']):
        d=g.groupby('date').gross_delta.mean()
        fam.append(dict(zip(['metric','strategy','universe','horizon','sample','family'],key)) | {'n_dates':len(d),'gross_delta':d.mean()})
    stats=pd.DataFrame(stats); fam=pd.DataFrame(fam); boots=pd.DataFrame(boots)
    stats.to_csv(OUT/'summary.csv',index=False); fam.to_csv(OUT/'family.csv',index=False); boots.to_csv(OUT/'bootstrap.csv',index=False)
    return stats,fam


def core_vals(stats, metric, strat, u, h=10):
    z=stats[(stats.metric==metric)&(stats.strategy==strat)&(stats.universe==u)&(stats.horizon==h)]
    mp={r['sample']:r for _,r in z.iterrows()}
    if not all(s in mp for s in CORE): return None
    return [float(mp[s].net_delta_30) for s in CORE]


def report(stats, fam):
    L=['# Alternative Liquidity Veto Sensitivity','',
       'CF20 is frozen. This test asks whether the ACT5 tail-veto result generalizes to other economically plausible liquidity measures. No outcome-based threshold tuning is used.','',
       'Metrics: ACT5 benchmark; ADV20 = 20D average trading amount; TURNOVER20 = 20D average trading amount / market cap; ACT1 = current trading amount / strictly-prior 20D average; AMIHUD20 = 20D average |return| / trading amount.','',
       '## H10 Top20 stable PASS specifications (30bp net vs CF20)','']
    for metric in METRICS:
        L.append(f'### {metric}')
        found=False
        for u in UNIVERSES:
            for t in TOP_CUTS:
                for l in LOW_CUTS:
                    strat=f'TOP{int(t*100):02d}_LOW{int(l*100):02d}'
                    v=core_vals(stats,metric,strat,u,10)
                    if v is not None and all(x>0 for x in v):
                        found=True
                        z=fam[(fam.metric==metric)&(fam.strategy==strat)&(fam.universe==u)&(fam.horizon==10)&fam['sample'].isin(CORE)]
                        pos=z.groupby('sample').apply(lambda q:int((q.gross_delta>0).sum()),include_groups=False).to_dict() if len(z) else {}
                        L.append(f'- {u} {strat}: {v[0]:+.2%}->{v[1]:+.2%}->{v[2]:+.2%}; positive-family counts {pos}')
        if not found: L.append('- no combined top+bottom veto passes all three core blocks')

    L += ['','## Combination incremental value versus its two component vetoes','']
    for metric in METRICS:
        diffs=[]; pos=0; total=0
        for u in UNIVERSES:
            for s in CORE:
                for t in TOP_CUTS:
                    for l in LOW_CUTS:
                        combo=f'TOP{int(t*100):02d}_LOW{int(l*100):02d}'; top=f'TOP{int(t*100):02d}'; low=f'LOW{int(l*100):02d}'
                        def one(st):
                            z=stats[(stats.metric==metric)&(stats.strategy==st)&(stats.universe==u)&(stats.horizon==10)&(stats['sample']==s)]
                            return float(z.net_delta_30.iloc[0]) if len(z) else np.nan
                        a,b,c=one(combo),one(top),one(low)
                        if np.isfinite(a) and np.isfinite(b) and np.isfinite(c):
                            d=a-max(b,c); diffs.append(d); pos+=int(d>0); total+=1
        if diffs:
            L.append(f'- {metric}: combo-minus-best-component median {np.median(diffs):+.2%}; positive cells {pos}/{total}')

    L += ['','## Metric-level one-sided veto stability, H10','']
    for metric in METRICS:
        L.append(f'### {metric}')
        for strat in [f'TOP{int(t*100):02d}' for t in TOP_CUTS] + [f'LOW{int(l*100):02d}' for l in LOW_CUTS]:
            pass_u=[]
            for u in UNIVERSES:
                v=core_vals(stats,metric,strat,u,10)
                if v is not None and all(x>0 for x in v): pass_u.append(u)
            if pass_u: L.append(f'- {strat}: stable in {", ".join(pass_u)}')

    L += ['','## Guardrails','',
          '- A PASS means positive H10 30bp-net incremental edge in all three historical core blocks for exactly the same metric/cutoff/universe.',
          '- ACT5 is a benchmark, not a selection target. The key question is whether other metric families reproduce the same low-liquidity or extreme-activity quality-control effect.',
          '- ADV20 and TURNOVER20 are liquidity-level measures; ACT1/ACT5 are activity-shock measures; AMIHUD20 is a price-impact illiquidity measure. Similar results across these groups would be stronger evidence of a general liquidity-quality mechanism.',
          '- H5/H20 and 2025/2026 remain robustness/stress diagnostics and do not select cutoffs.','']
    return '\n'.join(L)+'\n'


def main():
    p=run(); stats,fam=evaluate(p)
    (OUT/'RESEARCH_SUMMARY.md').write_text(report(stats,fam),encoding='utf-8')
    print(f'paths={len(p):,}; specs={len(stats):,}')

if __name__=='__main__':
    main()
