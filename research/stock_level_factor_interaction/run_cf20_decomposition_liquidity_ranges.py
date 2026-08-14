from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/liquidity_cross_factor'))
import run_cross_factor_liquidity as base
import run_multi_universe_liquidity as multi

OUT = Path(__file__).resolve().parent / 'results_cf20_decomp_liq_ranges'
OUT.mkdir(parents=True, exist_ok=True)

FAMILIES = {
    'MOMENTUM': ['MOM1M', 'MOM12_1'],
    'REVISION': ['OP12_REV', 'OPFY1_REV'],
    'VALUE': ['PBR12MF', 'PER12MF'],
    'FLOW': ['PRIVATE_FLOW', 'FOREIGN_FLOW'],
}
FACTOR_FAMILY = {f: fam for fam, members in FAMILIES.items() for f in members}
HIGH_GOOD = {
    'MOM1M': True, 'MOM12_1': True,
    'OP12_REV': True, 'OPFY1_REV': True,
    'PBR12MF': False, 'PER12MF': False,
    'PRIVATE_FLOW': True, 'FOREIGN_FLOW': True,
}
UNIVERSES = (
    'K200', 'KOSPI_EX_K200', 'KOSPI_ALL', 'KOSDAQ',
    'KOSPI_KOSDAQ_ALL', 'KOSDAQ_PLUS_KOSPI_EX_K200',
)
CORE = ('EARLY_2016_2019', 'LATE_2020_2022', 'NORMAL_2023_2024')
TOPN = 20
PROMOTE_N = 4  # fixed 20% surgery for decomposition
DECOMP_H = 10
LIQ_HORIZONS = (5, 10, 20)
COSTS = (0, 30, 60)
RNG = np.random.default_rng(20260814)

DECOMP_STRATS = ('BASE', 'VETO20', 'PROMOTE20', 'VETO_PROMOTE20', 'CF20')
LIQ_STRATS = (
    'CF20',
    'VETO_LOW10', 'VETO_LOW20',
    'VETO_HIGH10', 'VETO_HIGH20',
    'VETO_BOTH10', 'VETO_BOTH20',
    'NEGLECT_LOW50', 'NEGLECT_LOW30',
    'HOT_HIGH30_DIAG',
)


def sample_of(dt: pd.Timestamp) -> str:
    if dt.year <= 2019: return 'EARLY_2016_2019'
    if dt.year <= 2022: return 'LATE_2020_2022'
    if dt.year <= 2024: return 'NORMAL_2023_2024'
    if dt.year == 2025: return 'BULL_2025'
    return 'YTD_2026'


def rank_good(raw: pd.Series, high_good: bool) -> pd.Series:
    return pd.to_numeric(raw, errors='coerce').rank(
        pct=True, method='average', ascending=True if high_good else False
    )


def block_boot(x, block=4, nboot=6000):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 8:
        return np.array([])
    nb = int(np.ceil(n / block))
    starts = RNG.integers(0, n, size=(nboot, nb))
    idx = (starts[:, :, None] + np.arange(block)[None, None, :]) % n
    return x[idx.reshape(nboot, -1)[:, :n]].mean(axis=1)


@lru_cache(maxsize=4096)
def load_factor_cached(path_str: str) -> pd.Series:
    return base.load_factor(Path(path_str))


def build_scores(dt, codes, files):
    raws = {
        f: load_factor_cached(str(fs[dt]))
        for f, fs in files.items() if dt in fs
    }
    if len(raws) < 8:
        return {}, {}
    scores = {f: rank_good(raws[f].reindex(codes), HIGH_GOOD[f]) for f in raws}
    fam = {
        name: pd.concat([scores[x] for x in members], axis=1).mean(axis=1)
        for name, members in FAMILIES.items()
    }
    others = {}
    for f in scores:
        ff = FACTOR_FAMILY[f]
        others[f] = pd.concat([v for n, v in fam.items() if n != ff], axis=1).mean(axis=1)
    return scores, others


def top_names(score: pd.Series, n=TOPN):
    s = score.replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)
    return s.head(n).index.tolist() if len(s) >= n else []


def decomp_names(primary: pd.Series, other: pd.Series):
    ranked = primary.replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)
    if len(ranked) < 40:
        return {}
    base20 = ranked.head(20).index.tolist()
    rank21_40 = ranked.iloc[20:40].index.tolist()

    # VETO20: use consensus only to identify four weak confirmations inside primary Top20.
    # Replacements are the next four primary names, with no consensus used for admission.
    veto = other.reindex(base20).dropna().sort_values().head(PROMOTE_N).index.tolist()
    fill = rank21_40[:PROMOTE_N]
    veto20 = [x for x in base20 if x not in set(veto)] + fill

    # PROMOTE20: use consensus only to find four overlooked candidates in primary ranks 21-40.
    # Victims are mechanically primary ranks 17-20, with no consensus used for exclusion.
    promote = other.reindex(rank21_40).dropna().sort_values(ascending=False).head(PROMOTE_N).index.tolist()
    promote20 = base20[:TOPN-PROMOTE_N] + promote

    # VETO_PROMOTE20: consensus chooses both four vetoes and four promotions.
    both20 = [x for x in base20 if x not in set(veto)] + promote

    cf20 = top_names(0.8 * primary + 0.2 * other, TOPN)
    if any(len(x) != TOPN for x in (veto20, promote20, both20, cf20)):
        return {}
    return {
        'BASE': base20,
        'VETO20': veto20,
        'PROMOTE20': promote20,
        'VETO_PROMOTE20': both20,
        'CF20': cf20,
    }


def run_decomposition(returns, k200, markets, files):
    fwd = base.forward_returns(returns, DECOMP_H)
    common = sorted(set(returns.index) & set(k200) & set(markets))
    dates = [d for d in common if d >= base.START and d in fwd.index][::DECOMP_H]
    holdings = {}
    rows = []
    for dt in dates:
        k = k200[dt]; market = markets[dt]
        for u in UNIVERSES:
            codes = multi.universe_codes(u, k, market)
            y = fwd.loc[dt].reindex(codes)
            if y.notna().sum() < (70 if u == 'K200' else 120):
                continue
            scores, others = build_scores(dt, codes, files)
            if len(scores) < 8: continue
            for f, primary in scores.items():
                names_map = decomp_names(primary, others[f])
                if len(names_map) != len(DECOMP_STRATS): continue
                for strat, names in names_map.items():
                    key = (u, f, strat)
                    old = holdings.get(key, [])
                    turn = 1.0 - len(set(old) & set(names)) / TOPN if old else 1.0
                    gross = float(y.reindex(names).mean())
                    rows.append({
                        'date': dt, 'sample': sample_of(dt), 'universe': u,
                        'factor': f, 'family': FACTOR_FAMILY[f], 'strategy': strat,
                        'gross': gross, 'turnover': turn,
                    })
                    holdings[key] = names
    p = pd.DataFrame(rows)
    p.to_csv(OUT/'decomposition_paths.csv', index=False)
    return p


def matched_summary(p, baseline, prefix):
    b = p[p.strategy.eq(baseline)][['date','sample','universe','factor','family','gross','turnover']].rename(
        columns={'gross':'base_gross','turnover':'base_turnover'}
    )
    x = p[p.strategy.ne(baseline)].merge(
        b, on=['date','sample','universe','factor','family'], how='inner'
    )
    x['gross_delta'] = x.gross - x.base_gross
    x['turnover_delta'] = x.turnover - x.base_turnover
    for c in COSTS:
        x[f'net_delta_{c}'] = x.gross_delta - x.turnover_delta * c / 10000
    x.to_csv(OUT/f'{prefix}_matched.csv', index=False)

    stats=[]; fam=[]; boots=[]
    for key,g in x.groupby(['strategy','universe','sample']):
        d=g.groupby('date').agg(
            gross_delta=('gross_delta','mean'), turnover_delta=('turnover_delta','mean'),
            **{f'net_{c}':(f'net_delta_{c}','mean') for c in COSTS},
        ).reset_index().sort_values('date')
        rec=dict(zip(['strategy','universe','sample'],key)) | {
            'n_dates':len(d),'gross_delta':d.gross_delta.mean(),
            'turnover_delta':d.turnover_delta.mean(),
        }
        for c in COSTS: rec[f'net_delta_{c}']=d[f'net_{c}'].mean()
        stats.append(rec)
        for metric in ['gross_delta','net_30','net_60']:
            bs=block_boot(d[metric].to_numpy())
            if len(bs):
                boots.append(rec | {'metric':metric,'mean':d[metric].mean(),
                    'ci025':np.quantile(bs,.025),'ci975':np.quantile(bs,.975),'p_gt0':(bs>0).mean()})
    for key,g in x.groupby(['strategy','universe','sample','family']):
        d=g.groupby('date').gross_delta.mean()
        fam.append(dict(zip(['strategy','universe','sample','family'],key)) | {
            'n_dates':len(d),'gross_delta':d.mean(),'positive_date_rate':(d>0).mean()
        })
    stats=pd.DataFrame(stats); fam=pd.DataFrame(fam); boots=pd.DataFrame(boots)
    stats.to_csv(OUT/f'{prefix}_summary.csv',index=False)
    fam.to_csv(OUT/f'{prefix}_family.csv',index=False)
    boots.to_csv(OUT/f'{prefix}_bootstrap.csv',index=False)
    return stats,fam,boots


def liquidity_score_map(cf20: pd.Series, act5_rank: pd.Series):
    # Percentile boundaries are fixed ex ante, within each point-in-time universe.
    masks = {
        'CF20': pd.Series(True, index=cf20.index),
        'VETO_LOW10': act5_rank >= .10,
        'VETO_LOW20': act5_rank >= .20,
        'VETO_HIGH10': act5_rank <= .90,
        'VETO_HIGH20': act5_rank <= .80,
        'VETO_BOTH10': (act5_rank >= .10) & (act5_rank <= .90),
        'VETO_BOTH20': (act5_rank >= .20) & (act5_rank <= .80),
        'NEGLECT_LOW50': act5_rank <= .50,
        'NEGLECT_LOW30': act5_rank <= .30,
        'HOT_HIGH30_DIAG': act5_rank >= .70,
    }
    return {k: cf20.where(m) for k,m in masks.items()}


def run_liquidity_ranges(returns, k200, markets, ta, liq_frames, files):
    rows=[]; surface=[]
    for h in LIQ_HORIZONS:
        fwd=base.forward_returns(returns,h)
        common=sorted(set(returns.index)&set(ta.index)&set(k200)&set(markets))
        dates=[d for d in common if d>=base.START and d in fwd.index][::h]
        holdings={}
        for dt in dates:
            k=k200[dt]; market=markets[dt]
            act5_full=liq_frames['act5'].loc[dt] if dt in liq_frames['act5'].index else pd.Series(dtype=float)
            for u in UNIVERSES:
                codes=multi.universe_codes(u,k,market)
                y=fwd.loc[dt].reindex(codes)
                if y.notna().sum() < (70 if u=='K200' else 120): continue
                scores,others=build_scores(dt,codes,files)
                if len(scores)<8: continue
                act5=act5_full.reindex(codes)
                act5_rank=pd.to_numeric(act5,errors='coerce').rank(pct=True,method='average')
                for f,primary in scores.items():
                    cf20=.8*primary+.2*others[f]
                    smap=liquidity_score_map(cf20,act5_rank)
                    for strat,score in smap.items():
                        names=top_names(score,TOPN)
                        if len(names)<TOPN: continue
                        key=(h,u,f,strat); old=holdings.get(key,[])
                        turn=1-len(set(old)&set(names))/TOPN if old else 1.0
                        rows.append({'date':dt,'sample':sample_of(dt),'horizon':h,'universe':u,
                            'factor':f,'family':FACTOR_FAMILY[f],'strategy':strat,
                            'gross':float(y.reindex(names).mean()),'turnover':turn,
                            'mean_act5_rank':float(act5_rank.reindex(names).mean())})
                        holdings[key]=names

                    # Surface diagnostic only at H10: fixed CF20 Top40 candidate pool, no cutoff selection.
                    if h==10:
                        pool=cf20.dropna().sort_values(ascending=False).head(40).index
                        for code in pool:
                            ar=act5_rank.get(code,np.nan); yy=y.get(code,np.nan)
                            if not (np.isfinite(ar) and np.isfinite(yy)): continue
                            dec=int(min(10,max(1,np.ceil(ar*10))))
                            surface.append({'date':dt,'sample':sample_of(dt),'universe':u,
                                'factor':f,'family':FACTOR_FAMILY[f],'code':code,
                                'act5_rank':float(ar),'act5_decile':dec,'fwd10':float(yy)})
    p=pd.DataFrame(rows); s=pd.DataFrame(surface)
    p.to_csv(OUT/'liquidity_range_paths.csv',index=False)
    s.to_csv(OUT/'liquidity_act5_surface_pool.csv',index=False)
    return p,s


def summarize_liquidity(p):
    b=p[p.strategy.eq('CF20')][['date','sample','horizon','universe','factor','family','gross','turnover']].rename(
        columns={'gross':'base_gross','turnover':'base_turnover'})
    x=p[p.strategy.ne('CF20')].merge(b,on=['date','sample','horizon','universe','factor','family'],how='inner')
    x['gross_delta']=x.gross-x.base_gross; x['turnover_delta']=x.turnover-x.base_turnover
    for c in COSTS: x[f'net_delta_{c}']=x.gross_delta-x.turnover_delta*c/10000
    x.to_csv(OUT/'liquidity_range_matched.csv',index=False)
    stats=[];fam=[];boots=[]
    for key,g in x.groupby(['strategy','universe','horizon','sample']):
        d=g.groupby('date').agg(gross_delta=('gross_delta','mean'),turnover_delta=('turnover_delta','mean'),
            **{f'net_{c}':(f'net_delta_{c}','mean') for c in COSTS}).reset_index().sort_values('date')
        rec=dict(zip(['strategy','universe','horizon','sample'],key))|{'n_dates':len(d),
            'gross_delta':d.gross_delta.mean(),'turnover_delta':d.turnover_delta.mean()}
        for c in COSTS: rec[f'net_delta_{c}']=d[f'net_{c}'].mean()
        stats.append(rec)
        for metric in ['gross_delta','net_30','net_60']:
            bs=block_boot(d[metric].to_numpy())
            if len(bs): boots.append(rec|{'metric':metric,'mean':d[metric].mean(),
                'ci025':np.quantile(bs,.025),'ci975':np.quantile(bs,.975),'p_gt0':(bs>0).mean()})
    for key,g in x.groupby(['strategy','universe','horizon','sample','family']):
        d=g.groupby('date').gross_delta.mean()
        fam.append(dict(zip(['strategy','universe','horizon','sample','family'],key))|{
            'n_dates':len(d),'gross_delta':d.mean(),'positive_date_rate':(d>0).mean()})
    stats=pd.DataFrame(stats);fam=pd.DataFrame(fam);boots=pd.DataFrame(boots)
    stats.to_csv(OUT/'liquidity_range_summary.csv',index=False)
    fam.to_csv(OUT/'liquidity_range_family.csv',index=False)
    boots.to_csv(OUT/'liquidity_range_bootstrap.csv',index=False)
    return stats,fam,boots


def summarize_surface(s):
    dec=[]; contrasts=[]
    for key,g in s.groupby(['universe','sample','act5_decile']):
        d=g.groupby(['date','factor']).fwd10.mean().groupby('date').mean()
        dec.append(dict(zip(['universe','sample','act5_decile'],key))|{'n_dates':len(d),'fwd10':d.mean()})
    for key,g in s.groupby(['universe','sample']):
        # Average within factor-date first, preserving equal factor weight.
        z=g.copy()
        z['zone']=np.select([z.act5_decile<=2,z.act5_decile>=9],['LOW20','HIGH20'],default='MID60')
        fd=z.groupby(['date','factor','zone']).fwd10.mean().unstack('zone')
        daily=fd.groupby('date').mean()
        for a,b in [('MID60','LOW20'),('MID60','HIGH20'),('LOW20','HIGH20')]:
            if a not in daily or b not in daily: continue
            d=(daily[a]-daily[b]).dropna().sort_index()
            bs=block_boot(d.to_numpy())
            contrasts.append({'universe':key[0],'sample':key[1],'contrast':f'{a}_MINUS_{b}',
                'n_dates':len(d),'mean':d.mean(),
                'ci025':np.quantile(bs,.025) if len(bs) else np.nan,
                'ci975':np.quantile(bs,.975) if len(bs) else np.nan,
                'p_gt0':(bs>0).mean() if len(bs) else np.nan})
    dec=pd.DataFrame(dec); con=pd.DataFrame(contrasts)
    dec.to_csv(OUT/'act5_surface_deciles.csv',index=False)
    con.to_csv(OUT/'act5_surface_contrasts.csv',index=False)
    return dec,con


def robust_core(stats, strategy, universe, horizon, metric='net_delta_30'):
    z=stats[(stats.strategy==strategy)&(stats.universe==universe)&(stats.horizon==horizon)]
    mp={r['sample']:r for _,r in z.iterrows()}
    if not all(s in mp for s in CORE): return None
    vals=[float(mp[s][metric]) for s in CORE]
    return vals, all(v>0 for v in vals)


def make_summary(dec_base, dec_cf, liq_stats, liq_fam, surface_con):
    L=['# CF20 Decomposition + ACT5 Range/Veto Tests','',
       'All rules are predeclared. CF20 remains 80% primary + 20% other-family consensus. Decomposition uses a fixed 20% (4-of-20) surgery. Liquidity cutoffs use point-in-time cross-sectional ACT5 percentiles; no cutoff is selected from outcomes.','',
       '## 1) CF20 mechanism decomposition — net 30bp edge vs BASE, H10 Top20','']
    for u in UNIVERSES:
        for strat in ('VETO20','PROMOTE20','VETO_PROMOTE20','CF20'):
            z=dec_base[(dec_base.strategy==strat)&(dec_base.universe==u)]
            mp={r['sample']:r for _,r in z.iterrows()}
            if not all(s in mp for s in CORE): continue
            vals=[mp[s].net_delta_30 for s in CORE]
            L.append(f"- {u} {strat}: {vals[0]:+.2%} -> {vals[1]:+.2%} -> {vals[2]:+.2%}; {'PASS' if all(v>0 for v in vals) else 'FAIL'}")
    L+=['','## Decomposition relative to full CF20 — net 30bp','']
    for u in UNIVERSES:
        for strat in ('BASE','VETO20','PROMOTE20','VETO_PROMOTE20'):
            z=dec_cf[(dec_cf.strategy==strat)&(dec_cf.universe==u)]
            mp={r['sample']:r for _,r in z.iterrows()}
            if not all(s in mp for s in CORE): continue
            vals=[mp[s].net_delta_30 for s in CORE]
            L.append(f"- {u} {strat} minus CF20: {vals[0]:+.2%} -> {vals[1]:+.2%} -> {vals[2]:+.2%}")

    L+=['','## 2) ACT5 range/veto rules on top of CF20','',
        'PASS requires positive 30bp-net incremental edge in 2016-19, 2020-22, and 2023-24 for the same rule/universe/horizon.','']
    for strat in [x for x in LIQ_STRATS if x!='CF20']:
        passes=[]
        for u in UNIVERSES:
            for h in LIQ_HORIZONS:
                r=robust_core(liq_stats,strat,u,h)
                if r and r[1]: passes.append((u,h,r[0]))
        if passes:
            L.append(f'### {strat}')
            for u,h,v in passes:
                L.append(f"- {u} H{h}: {v[0]:+.2%} -> {v[1]:+.2%} -> {v[2]:+.2%}")
    L+=['','## All H10 Top20 ACT5 rules — 30bp net, for reference','']
    for u in UNIVERSES:
        L.append(f'### {u}')
        for strat in [x for x in LIQ_STRATS if x!='CF20']:
            r=robust_core(liq_stats,strat,u,10)
            if r:
                v,ok=r; L.append(f"- {strat}: {v[0]:+.2%} -> {v[1]:+.2%} -> {v[2]:+.2%}; {'PASS' if ok else 'FAIL'}")

    L+=['','## 3) ACT5 shape inside frozen CF20 Top40 candidate pool','',
        'Contrasts are future 10D returns; LOW20=ACT5 bottom 20%, MID60=20-80%, HIGH20=top 20%.','']
    for u in UNIVERSES:
        for s in CORE:
            z=surface_con[(surface_con.universe==u)&(surface_con['sample']==s)]
            if z.empty: continue
            txt=[]
            for _,r in z.iterrows(): txt.append(f"{r.contrast} {r['mean']:+.2%} (P>0 {r.p_gt0:.0%})")
            L.append(f"- {u} {s}: "+'; '.join(txt))
    L+=['','## Guardrails','',
        '- VETO20 and PROMOTE20 are mechanism tests, not newly optimized production rules.',
        '- HOT_HIGH30_DIAG is diagnostic; do not promote it even if it wins.',
        '- 2025 and 2026 remain stress diagnostics only and are not used for rule selection.',
        '- Range-veto promotion requires same-sign net edge across all three core historical blocks; isolated horizon/universe wins are hypotheses only.','']
    return '\n'.join(L)+'\n'


def main():
    returns,mcap,k200=base.load_basic()
    markets=multi.load_market_by_date()
    ta=base.load_trading_amount()
    liq_frames=base.build_liquidity_features(ta,mcap)
    files={f:base.dated_files(path) for f,path in base.FACTORS.items()}

    dp=run_decomposition(returns,k200,markets,files)
    dec_base,_,_=matched_summary(dp,'BASE','decomp_vs_base')
    dec_cf,_,_=matched_summary(dp,'CF20','decomp_vs_cf20')

    lp,surf=run_liquidity_ranges(returns,k200,markets,ta,liq_frames,files)
    liq_stats,liq_fam,_=summarize_liquidity(lp)
    _,surface_con=summarize_surface(surf)

    (OUT/'RESEARCH_SUMMARY.md').write_text(
        make_summary(dec_base,dec_cf,liq_stats,liq_fam,surface_con),encoding='utf-8')
    print(f'decomp rows={len(dp):,}; liquidity rows={len(lp):,}; surface rows={len(surf):,}')

if __name__=='__main__':
    main()
