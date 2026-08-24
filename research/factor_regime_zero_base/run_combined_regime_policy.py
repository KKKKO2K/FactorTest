from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
INP = HERE / 'results_persistence_rotation/persistence_rotation_panel.csv'
OUT = HERE / 'results_combined_regime_policy'
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = [
    'MOM1M','MOM12_1','OP12_REV','OPFY1_REV',
    'PBR12MF','PER12MF','PRIVATE_FLOW','FOREIGN_FLOW'
]
PERSIST_FEATURES = [
    'CROSS_HORIZON_RANK_CORR','PC1_SHARE_60','LEADER_STRENGTH_20',
    'SIGN_ALIGNMENT_20_60','DISPERSION_CHANGE_20','BREADTH_20','DISPERSION_20'
]
# Frozen to predictors that passed Stage-2 gate for all three opportunity targets.
OPPORTUNITY_FEATURES = [
    'LEADER_STRENGTH_20','DISPERSION_20','RANGE_20',
    'ABS_OPPORTUNITY_20','WINNER_GAP_20'
]
PERSIST_TARGET = 'TARGET_FACTOR_MOM_20'
OPP_TARGETS = ['TARGET_FWD_DISPERSION_20','TARGET_FWD_ABS_OPPORTUNITY_20','TARGET_FWD_RANGE_20']
COSTS = [0,10,30]
PERIODS = {
    'DEV_2020_2022':(2020,2022),
    'CONFIRM_2023_2024':(2023,2024),
    'BULL_2025':(2025,2025),
    'YTD_2026':(2026,2026),
}


def spearman(x,y):
    z=pd.concat([x,y],axis=1).dropna()
    if len(z)<10 or z.iloc[:,0].nunique()<2 or z.iloc[:,1].nunique()<2:return np.nan
    return float(z.iloc[:,0].rank().corr(z.iloc[:,1].rank()))


def add_opp_targets(p):
    z=p.copy(); a=z[[f'FWD20_{f}' for f in FACTORS]].to_numpy(float)
    z['TARGET_FWD_DISPERSION_20']=np.nanstd(a,axis=1,ddof=1)
    z['TARGET_FWD_ABS_OPPORTUNITY_20']=np.nanmean(np.abs(a),axis=1)
    z['TARGET_FWD_RANGE_20']=np.nanmax(a,axis=1)-np.nanmin(a,axis=1)
    return z


def standardize(train,test,cols):
    a=train[cols].astype(float).copy(); b=test[cols].astype(float).copy()
    lo=a.quantile(.01); hi=a.quantile(.99)
    a=a.clip(lo,hi,axis=1); b=b.clip(lo,hi,axis=1)
    med=a.median(); a=a.fillna(med); b=b.fillna(med)
    mu=a.mean(); sd=a.std(ddof=0).replace(0,1.0)
    return (a-mu)/sd,(b-mu)/sd


def direction_series(train,features,targets):
    d={}
    for f in features:
        vals=[spearman(train[f],train[t]) for t in targets]
        vals=[v for v in vals if np.isfinite(v)]
        m=float(np.mean(vals)) if vals else 0.0
        d[f]=1.0 if m>=0 else -1.0
    return pd.Series(d)


def sleeve_weights(r,mode):
    cur=np.array([r[f'CUR20_{f}'] for f in FACTORS],float)
    order=np.argsort(cur); w=np.zeros(len(FACTORS))
    if mode=='TOP2': w[order[-2:]]=.5
    elif mode=='BOTTOM2': w[order[:2]]=.5
    elif mode=='EW8': w[:]=1/len(FACTORS)
    else: raise ValueError(mode)
    return w


def sleeve_return(r,w):
    fwd=np.array([r[f'FWD20_{f}'] for f in FACTORS],float)
    return float(w@fwd)


def build_decisions(panel):
    rows=[]
    for u,g0 in panel.groupby('universe'):
        g=g0.sort_values('date').reset_index(drop=True)
        # common deterministic non-overlap schedule across all policies
        g['take']=(np.arange(len(g))%4==0)
        for year in range(2020,int(g.date.dt.year.max())+1):
            tr=g[g.date<pd.Timestamp(f'{year}-01-01')].copy()
            te=g[g.date.dt.year.eq(year)].copy()
            if len(tr)<80 or te.empty: continue

            zp_tr,zp_te=standardize(tr,te,PERSIST_FEATURES)
            zo_tr,zo_te=standardize(tr,te,OPPORTUNITY_FEATURES)
            dp=direction_series(tr,PERSIST_FEATURES,[PERSIST_TARGET])
            do=direction_series(tr,OPPORTUNITY_FEATURES,OPP_TARGETS)
            p_tr=(zp_tr*dp).mean(axis=1); p_te=(zp_te*dp).mean(axis=1)
            o_tr=(zo_tr*do).mean(axis=1); o_te=(zo_te*do).mean(axis=1)
            p33,p67=p_tr.quantile([1/3,2/3]); o67=float(o_tr.quantile(2/3))

            for idx,r in te.iterrows():
                if not bool(r['take']): continue
                ps=float(p_te.loc[idx]); os=float(o_te.loc[idx])
                persist_action='TOP2' if ps>=p67 else ('BOTTOM2' if ps<=p33 else 'EW8')
                if os<o67:
                    combined_action='EW8'
                else:
                    combined_action='TOP2' if ps>=p67 else ('BOTTOM2' if ps<=p33 else 'EW8')
                rec={
                    'date':r.date,'universe':u,'eval_year':year,
                    'persist_score':ps,'opportunity_score':os,
                    'train_p33':float(p33),'train_p67':float(p67),'train_o67':o67,
                    'persist_action':persist_action,'combined_action':combined_action,
                    'target_factor_mom_20':float(r[PERSIST_TARGET]),
                    'target_fwd_range_20':float(r['TARGET_FWD_RANGE_20']),
                }
                for mode in ['TOP2','BOTTOM2','EW8']:
                    w=sleeve_weights(r,mode)
                    rec[f'{mode.lower()}_gross']=sleeve_return(r,w)
                    for j,f in enumerate(FACTORS): rec[f'{mode.lower()}_w_{f}']=float(w[j])
                for policy,action in [('PERSIST_ONLY',persist_action),('COMBINED',combined_action)]:
                    w=sleeve_weights(r,action)
                    rec[f'{policy.lower()}_gross']=sleeve_return(r,w)
                    for j,f in enumerate(FACTORS):rec[f'{policy.lower()}_w_{f}']=float(w[j])
                rows.append(rec)
    return pd.DataFrame(rows).sort_values(['universe','date']).reset_index(drop=True)


def add_costs(dec):
    out=[]
    policies=['COMBINED','PERSIST_ONLY','TOP2','EW8']
    for u,g0 in dec.groupby('universe'):
        g=g0.sort_values('date').copy()
        turn={}
        for policy in policies:
            prefix=policy.lower()
            W=g[[f'{prefix}_w_{f}' for f in FACTORS]].to_numpy(float)
            prev=np.zeros(len(FACTORS)); vals=[]
            for w in W:
                vals.append(.5*float(np.abs(w-prev).sum())); prev=w
            turn[policy]=np.array(vals)
        for cost in COSTS:
            z=g.copy(); z['cost_bps']=cost
            for policy in policies:
                prefix=policy.lower(); z[f'{prefix}_turnover']=turn[policy]
                z[f'{prefix}_ret']=z[f'{prefix}_gross']-turn[policy]*cost/10000
            out.append(z)
    return pd.concat(out,ignore_index=True)


def perf(r):
    r=pd.Series(r).dropna().astype(float)
    if len(r)<3:return {'cagr':np.nan,'sharpe':np.nan,'mdd':np.nan}
    nav=(1+r).cumprod(); ppy=252/20; years=len(r)/ppy
    cagr=float(nav.iloc[-1]**(1/years)-1) if years>0 and nav.iloc[-1]>0 else np.nan
    sd=r.std(ddof=1); sh=float(r.mean()/sd*np.sqrt(ppy)) if sd>0 else np.nan
    return {'cagr':cagr,'sharpe':sh,'mdd':float((nav/nav.cummax()-1).min())}


def summarize(path):
    rows=[]
    for cost in COSTS:
      zc=path[path.cost_bps.eq(cost)]
      for period,(a,b) in PERIODS.items():
        zp=zc[zc.eval_year.between(a,b)]
        for u,g in zp.groupby('universe'):
          if len(g)<3:continue
          mets={p:perf(g[f'{p.lower()}_ret']) for p in ['COMBINED','PERSIST_ONLY','TOP2','EW8']}
          r={'universe':u,'cost_bps':cost,'period':period,'n_rebalances':len(g)}
          for p,m in mets.items():
            r[f'{p.lower()}_cagr']=m['cagr'];r[f'{p.lower()}_sharpe']=m['sharpe'];r[f'{p.lower()}_mdd']=m['mdd']
          r['delta_sharpe_vs_ew8']=r['combined_sharpe']-r['ew8_sharpe']
          r['delta_cagr_vs_ew8']=r['combined_cagr']-r['ew8_cagr']
          r['delta_mdd_vs_ew8']=r['combined_mdd']-r['ew8_mdd']
          r['delta_sharpe_vs_persist']=r['combined_sharpe']-r['persist_only_sharpe']
          r['delta_cagr_vs_persist']=r['combined_cagr']-r['persist_only_cagr']
          r['combined_active_share']=float((g.combined_action!='EW8').mean())
          r['persist_active_share']=float((g.persist_action!='EW8').mean())
          r['combined_top2_share']=float((g.combined_action=='TOP2').mean())
          r['combined_bottom2_share']=float((g.combined_action=='BOTTOM2').mean())
          r['combined_annual_turnover']=float(g.combined_turnover.mean()*(252/20))
          r['ew8_annual_turnover']=float(g.ew8_turnover.mean()*(252/20))
          rows.append(r)
    return pd.DataFrame(rows)


def pct(x):return 'NA' if not np.isfinite(x) else f'{x:+.2%}'


def report(stats):
    L=['# Combined Zero-Base Factor Regime Policy','',
       '- Opportunity gate is frozen to five predictors that passed all three Stage-2 opportunity targets: leader strength, dispersion, range, current absolute opportunity, and winner gap.',
       '- Persistence score uses the seven Stage-1 survivors for future top-minus-bottom factor payoff.',
       '- Predeclared mapping: opportunity below train top tercile -> EW8; opportunity high + persistence high -> TOP2; opportunity high + persistence low -> BOTTOM2; otherwise EW8.',
       '- 20D decisions are non-overlapping; costs apply to one-way factor-sleeve turnover.',
       '- This is a historical/pseudo-OOS policy audit. 2023-24 contributed to feature survival and is therefore not a pristine untouched confirmation sample; 2025/26 were also previously inspected as stress slices.','']
    for cost in COSTS:
      L += [f'## Cost {cost} bps','']
      for period in PERIODS:
        q=stats[(stats.cost_bps==cost)&(stats.period==period)]
        if q.empty:continue
        L.append(
          f'- {period}: median ΔSharpe vs EW8 {q.delta_sharpe_vs_ew8.median():+.3f}; '
          f'ΔCAGR {pct(q.delta_cagr_vs_ew8.median())}; ΔMDD {pct(q.delta_mdd_vs_ew8.median())}; '
          f'better Sharpe {(q.delta_sharpe_vs_ew8>0).sum()}/{len(q)} universes; '
          f'ΔSharpe vs persistence-only {q.delta_sharpe_vs_persist.median():+.3f}; '
          f'active share {q.combined_active_share.median():.1%} vs persistence-only {q.persist_active_share.median():.1%}'
        )
      L.append('')
    L += ['## 10 bps universe detail','']
    q=stats[stats.cost_bps.eq(10)]
    for period in PERIODS:
      L.append(f'### {period}')
      for r in q[q.period.eq(period)].sort_values('universe').itertuples(index=False):
        L.append(
          f'- {r.universe}: combined Sharpe {r.combined_sharpe:+.2f} vs EW8 {r.ew8_sharpe:+.2f} '
          f'(Δ {r.delta_sharpe_vs_ew8:+.2f}); ΔCAGR {pct(r.delta_cagr_vs_ew8)}; '
          f'active {r.combined_active_share:.0%}'
        )
      L.append('')
    L += ['## Interpretation','',
          '- A positive result requires the opportunity gate to improve the persistence-only policy and close or reverse the gap to EW8 broadly, not merely in one stress year.',
          '- Do not retune terciles or feature weights after seeing this output. If combined policy still cannot beat EW8 robustly, retain Persistence and Opportunity as monitoring/risk-budget states and proceed to Factor Crash/Crowding.']
    return '\n'.join(L)


def main():
    p=pd.read_csv(INP);p['date']=pd.to_datetime(p.date);p=add_opp_targets(p)
    d=build_decisions(p);path=add_costs(d);s=summarize(path)
    d.to_csv(OUT/'combined_decisions.csv',index=False,encoding='utf-8-sig')
    path.to_csv(OUT/'combined_policy_path.csv',index=False,encoding='utf-8-sig')
    s.to_csv(OUT/'combined_policy_summary.csv',index=False,encoding='utf-8-sig')
    text=report(s);(OUT/'RESEARCH_SUMMARY.md').write_text(text,encoding='utf-8');print(text)

if __name__=='__main__':main()
