from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ASSIGN = ROOT / 'research/factor_regime_contemporaneous_states/results/nested_state_assignments.csv'
PRIM = ROOT / 'research/factor_regime_full_state_map/results/family_primitives.csv'
FSTATE = ROOT / 'research/factor_regime_full_state_map/results/family_states_static.csv'
OUT = ROOT / 'research/factor_payoff_surface/results'
OUT.mkdir(parents=True, exist_ok=True)

FAMILIES = ['MOMENTUM','REVISION','VALUE','FLOW']
ACTIONS = ['WPLUS','EW4','MARKET'] + FAMILIES
MARKET_FEATURES = ['MKT_RET_20D','MKT_RET_60D','MKT_VOL_20D','MKT_DD_60D','LIQ_5D_20D','LIQ_1D_20D']
GLOBAL_FACTOR_FEATURES = [
    'RELATIVE_WORKING_BREADTH','ABS_CONFIRMED_BREADTH','DEFENSIVE_WORKING_BREADTH',
    'REVERSE_BREADTH','BEARISH_REVERSE_BREADTH','POSITIVE_ABS_BREADTH',
    'WPLUS_FAMILY_SHARE','WMINUS_FAMILY_SHARE','RMINUS_FAMILY_SHARE',
    'WPLUS_PAIR_SHARE','CONFLICT_PAIR_SHARE','LEADER_STRENGTH_60D',
    'SPREAD_DISPERSION_20D','FAMILY_MEMBER_AGREEMENT'
]
RIDGE_ALPHAS = [0.1,1.0,10.0,100.0]
MIN_TRAIN = 120
MIN_UNIVAR = 12


def period_of(d: pd.Timestamp) -> str:
    y=d.year
    if y<=2022: return 'DISCOVERY_2016_2022'
    if y<=2024: return 'NORMAL_2023_2024'
    if y==2025: return 'BULL_2025'
    return 'YTD_2026'


def load_panel() -> tuple[pd.DataFrame,list[str],list[str]]:
    s=pd.read_csv(ASSIGN)
    p=pd.read_csv(PRIM)
    fs=pd.read_csv(FSTATE)
    for z in (s,p,fs): z['date']=pd.to_datetime(z['date'])
    # State labels are used ONLY to construct the W+ control action, not as predictors.
    fs=fs[fs['cut_name'].eq('Q33')][['date','universe','family','state6']]
    p=p.merge(fs,on=['date','universe','family'],how='left')
    rows=[]
    for (dt,u),g in p.groupby(['date','universe'],sort=False):
        if g['family'].nunique()<4: continue
        rec={'date':dt,'universe':u}
        for _,r in g.iterrows():
            f=r['family']
            for c in ['top_20d','spread_20d','top_60d','spread_60d','member_positive_spread_share_20d','member_same_sign_20d','top_fwd_5d','top_fwd_20d']:
                if c in r.index: rec[f'{f}_{c}']=r[c]
            rec[f'{f}_state6']=r.get('state6',np.nan)
        rows.append(rec)
    w=pd.DataFrame(rows)
    # Keep only contemporaneous predictors from the state file. Future fields and discrete regime labels are excluded.
    keep=['date','universe'] + [c for c in MARKET_FEATURES+GLOBAL_FACTOR_FEATURES if c in s.columns]
    x=s[keep].drop_duplicates(['date','universe']).merge(w,on=['date','universe'],how='inner')
    # market future returns are outcomes, not predictors
    mf=s[['date','universe','MKT_FWD_5D','MKT_FWD_20D']].drop_duplicates(['date','universe'])
    x=x.merge(mf,on=['date','universe'],how='left')
    # actions
    fam5=[f'{f}_top_fwd_5d' for f in FAMILIES]
    fam20=[f'{f}_top_fwd_20d' for f in FAMILIES]
    x['EW4_fwd5']=x[fam5].mean(axis=1)
    x['EW4_fwd20']=x[fam20].mean(axis=1)
    for h in [5,20]:
        vals=[]
        for _,r in x.iterrows():
            ws=[f for f in FAMILIES if r.get(f'{f}_state6')=='W+']
            cols=[f'{f}_top_fwd_{h}d' for f in ws]
            vals.append(float(r[cols].mean()) if cols else float(r[[f'{f}_top_fwd_{h}d' for f in FAMILIES]].mean()))
        x[f'WPLUS_fwd{h}']=vals
    x['MARKET_fwd5']=x['MKT_FWD_5D']; x['MARKET_fwd20']=x['MKT_FWD_20D']
    for f in FAMILIES:
        x[f'{f}_fwd5']=x[f'{f}_top_fwd_5d']; x[f'{f}_fwd20']=x[f'{f}_top_fwd_20d']
    x['period']=x.date.map(period_of)
    family_features=[]
    for f in FAMILIES:
        family_features += [c for c in [
            f'{f}_top_20d',f'{f}_spread_20d',f'{f}_top_60d',f'{f}_spread_60d',
            f'{f}_member_positive_spread_share_20d',f'{f}_member_same_sign_20d'
        ] if c in x.columns]
    market=[c for c in MARKET_FEATURES if c in x.columns]
    factor=[c for c in GLOBAL_FACTOR_FEATURES if c in x.columns] + family_features
    return x.sort_values(['universe','date']).reset_index(drop=True),market,factor


def winsor_standardize(train: pd.DataFrame, test: pd.DataFrame, cols:list[str]):
    a=train[cols].astype(float).copy(); b=test[cols].astype(float).copy()
    lo=a.quantile(.01); hi=a.quantile(.99)
    a=a.clip(lo,hi,axis=1); b=b.clip(lo,hi,axis=1)
    med=a.median(); a=a.fillna(med); b=b.fillna(med)
    mu=a.mean(); sd=a.std(ddof=0).replace(0,1.0)
    return ((a-mu)/sd).to_numpy(),((b-mu)/sd).to_numpy(),mu,sd


def ridge_fit(X:np.ndarray,y:np.ndarray,alpha:float)->np.ndarray:
    Xi=np.c_[np.ones(len(X)),X]
    pen=np.eye(Xi.shape[1])*alpha; pen[0,0]=0.0
    return np.linalg.pinv(Xi.T@Xi+pen)@(Xi.T@y)


def ridge_predict(X:np.ndarray,b:np.ndarray)->np.ndarray:
    return np.c_[np.ones(len(X)),X]@b


def choose_alpha(train:pd.DataFrame,features:list[str],target:str)->float:
    z=train.dropna(subset=[target]).sort_values('date')
    if len(z)<MIN_TRAIN: return 10.0
    cut=int(len(z)*.75)
    a=z.iloc[:cut]; b=z.iloc[cut:]
    if len(b)<20: return 10.0
    Xa,Xb,_,_=winsor_standardize(a,b,features); ya=a[target].to_numpy(); yb=b[target].to_numpy()
    scores=[]
    for al in RIDGE_ALPHAS:
        bh=ridge_fit(Xa,ya,al); pred=ridge_predict(Xb,bh)
        scores.append((float(np.mean((yb-pred)**2)),al))
    return min(scores)[1]


def model_predictions(panel:pd.DataFrame,market_features:list[str],factor_features:list[str])->tuple[pd.DataFrame,pd.DataFrame]:
    specs={'MARKET_ONLY':market_features,'FACTOR_ONLY':factor_features,'FULL':market_features+factor_features}
    pred_rows=[]; coef_rows=[]
    for u,g in panel.groupby('universe'):
        g=g.sort_values('date')
        min_year=max(2020,int(g.date.dt.year.min())+3)
        for y in range(min_year,int(g.date.dt.year.max())+1):
            tr=g[g.date < pd.Timestamp(f'{y}-01-01')].copy(); te=g[g.date.dt.year.eq(y)].copy()
            if len(tr)<MIN_TRAIN or te.empty: continue
            # Target each action's excess over W+ directly.
            for action in ['MARKET','EW4']+FAMILIES:
                target=f'Y_{action}_minus_WPLUS'
                tr[target]=tr[f'{action}_fwd5']-tr['WPLUS_fwd5']
                for spec,features in specs.items():
                    if not features: continue
                    z=tr.dropna(subset=[target]);
                    if len(z)<MIN_TRAIN: continue
                    alpha=choose_alpha(z,features,target)
                    Xtr,Xte,_,_=winsor_standardize(z,te,features); yy=z[target].to_numpy()
                    bh=ridge_fit(Xtr,yy,alpha); pp=ridge_predict(Xte,bh)
                    for i,(_,r) in enumerate(te.iterrows()):
                        pred_rows.append({'date':r.date,'universe':u,'eval_year':y,'model':spec,'action':action,
                                          'pred_excess_vs_wplus':pp[i],'realized_excess_vs_wplus':r[f'{action}_fwd5']-r['WPLUS_fwd5'],
                                          'action_ret':r[f'{action}_fwd5'],'wplus_ret':r['WPLUS_fwd5'],'market_ret':r['MARKET_fwd5']})
                    for j,c in enumerate(features):
                        coef_rows.append({'universe':u,'eval_year':y,'model':spec,'action':action,'feature':c,'coef_std':bh[j+1],'alpha':alpha})
    return pd.DataFrame(pred_rows),pd.DataFrame(coef_rows)


def policy_from_predictions(pred:pd.DataFrame,panel:pd.DataFrame)->tuple[pd.DataFrame,pd.DataFrame]:
    # W+ is the baseline. Switch only when model predicts positive incremental payoff.
    base=panel[['date','universe','period','WPLUS_fwd5']].copy()
    rows=[]
    for (dt,u,m),g in pred.groupby(['date','universe','model']):
        g=g.dropna(subset=['pred_excess_vs_wplus'])
        if g.empty: continue
        best=g.sort_values('pred_excess_vs_wplus',ascending=False).iloc[0]
        use='WPLUS' if best.pred_excess_vs_wplus<=0 else best.action
        realized=float(best.wplus_ret if use=='WPLUS' else best.action_ret)
        rows.append({'date':dt,'universe':u,'model':m,'chosen_action':use,'pred_edge':max(float(best.pred_excess_vs_wplus),0.0),
                     'ret':realized,'wplus_ret':float(best.wplus_ret),'edge':realized-float(best.wplus_ret),'market_ret':float(best.market_ret)})
    path=pd.DataFrame(rows).merge(base[['date','universe','period']],on=['date','universe'],how='left').sort_values(['universe','model','date'])
    stats=[]
    for (u,m,p),g in path.groupby(['universe','model','period']):
        r=g.ret.dropna(); w=g.wplus_ret.loc[r.index]
        if len(r)<8: continue
        eq=(1+r).cumprod(); eqw=(1+w).cumprod()
        stats.append({'universe':u,'model':m,'period':p,'n':len(r),'switch_rate':(g.chosen_action!='WPLUS').mean(),
                      'mean5':r.mean(),'win_rate':(r>0).mean(),'mean_edge_vs_wplus':(r-w).mean(),'beat_wplus_rate':(r>w).mean(),
                      'compound':eq.iloc[-1]-1,'compound_wplus':eqw.iloc[-1]-1,'mdd':(eq/eq.cummax()-1).min(),
                      'wplus_mdd':(eqw/eqw.cummax()-1).min()})
    return path,pd.DataFrame(stats)


def prediction_diagnostics(pred:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for (u,m,a,y),g in pred.groupby(['universe','model','action','eval_year']):
        z=g.dropna(subset=['pred_excess_vs_wplus','realized_excess_vs_wplus'])
        if len(z)<8: continue
        pear=z.pred_excess_vs_wplus.corr(z.realized_excess_vs_wplus)
        spear=z.pred_excess_vs_wplus.rank().corr(z.realized_excess_vs_wplus.rank())
        hi=z[z.pred_excess_vs_wplus>=z.pred_excess_vs_wplus.quantile(.67)]
        lo=z[z.pred_excess_vs_wplus<=z.pred_excess_vs_wplus.quantile(.33)]
        rows.append({'universe':u,'model':m,'action':a,'eval_year':y,'n':len(z),'pearson':pear,'spearman':spear,
                     'top_bottom_realized':hi.realized_excess_vs_wplus.mean()-lo.realized_excess_vs_wplus.mean(),
                     'positive_pred_realized':z.loc[z.pred_excess_vs_wplus>0,'realized_excess_vs_wplus'].mean(),
                     'positive_pred_n':int((z.pred_excess_vs_wplus>0).sum())})
    return pd.DataFrame(rows)


def univariate_surface(panel:pd.DataFrame,features:list[str])->pd.DataFrame:
    rows=[]
    # Descriptive, with fixed chronological samples to expose instability. No cell is promoted from this table alone.
    samples={'DISCOVERY_2016_2022':lambda d:d.dt.year<=2022,'NORMAL_2023_2024':lambda d:d.dt.year.between(2023,2024),
             'BULL_2025':lambda d:d.dt.year.eq(2025),'YTD_2026':lambda d:d.dt.year.eq(2026)}
    for u,g in panel.groupby('universe'):
        for feat in features:
            if feat not in g: continue
            for action in ['MARKET','EW4']+FAMILIES:
                target=g[f'{action}_fwd5']-g['WPLUS_fwd5']
                for sample,maskfn in samples.items():
                    z=g.loc[maskfn(g.date),[feat]].copy(); z['y']=target.loc[z.index]; z=z.dropna()
                    if len(z)<MIN_UNIVAR*3: continue
                    # thresholds fit within the displayed sample; table is descriptive, not a trading backtest.
                    q1,q2=z[feat].quantile([.33,.67])
                    lo=z[z[feat]<=q1].y; hi=z[z[feat]>=q2].y
                    if len(lo)<MIN_UNIVAR or len(hi)<MIN_UNIVAR: continue
                    rows.append({'universe':u,'feature':feat,'action':action,'sample':sample,'n':len(z),
                                 'low_n':len(lo),'high_n':len(hi),'high_minus_low_payoff':hi.mean()-lo.mean(),
                                 'high_payoff':hi.mean(),'low_payoff':lo.mean(),'high_beat_wplus':(hi>0).mean(),'low_beat_wplus':(lo>0).mean()})
    return pd.DataFrame(rows)


def stable_surface(surface:pd.DataFrame)->pd.DataFrame:
    rows=[]
    for key,g in surface.groupby(['universe','feature','action']):
        mp={r.sample:r for _,r in g.iterrows()}
        if 'DISCOVERY_2016_2022' not in mp or 'NORMAL_2023_2024' not in mp: continue
        a=mp['DISCOVERY_2016_2022']; b=mp['NORMAL_2023_2024']
        same=np.sign(a.high_minus_low_payoff)==np.sign(b.high_minus_low_payoff) and np.sign(a.high_minus_low_payoff)!=0
        if not same: continue
        rows.append({'universe':key[0],'feature':key[1],'action':key[2],
                     'discovery_hl':a.high_minus_low_payoff,'normal_hl':b.high_minus_low_payoff,
                     'discovery_high_payoff':a.high_payoff,'normal_high_payoff':b.high_payoff,
                     'min_abs_hl':min(abs(a.high_minus_low_payoff),abs(b.high_minus_low_payoff)),
                     'sign':int(np.sign(a.high_minus_low_payoff))})
    return pd.DataFrame(rows).sort_values('min_abs_hl',ascending=False) if rows else pd.DataFrame()


def summarize(panel,pred,diag,stats,surface,stable,coefs)->str:
    L=['# Continuous Factor Payoff-Surface Research','',
       'Primary question: given only information observable at date t, which investable action has the better conditional payoff? Hard B2/B3/B4 and F_HIGH/F_LOW labels are excluded from predictors. Q33 family states are retained only to construct the W+ control basket.','',
       '## Data / design','',
       f'- Panel rows: {len(panel):,}; date range {panel.date.min().date()} to {panel.date.max().date()}.',
       '- Actions: W+, EW4, market, Momentum, Revision, Value, Flow family top portfolios.',
       '- Models: MARKET_ONLY, FACTOR_ONLY, FULL. Each universe is estimated separately with expanding yearly walk-forward. Ridge penalty is selected using the tail 25% of the then-available training history only.',
       '- Objective for action models: predict each action minus W+ next-5D payoff. W+ remains the fallback unless predicted incremental payoff is positive.','',
       '## Walk-forward policy performance by historical sample','']
    if not stats.empty:
        for (u,p),g in stats.groupby(['universe','period']):
            L.append(f'### {u} — {p}')
            for _,r in g.sort_values('model').iterrows():
                L.append(f"- {r.model}: n={int(r.n)}, switch {r.switch_rate:.0%}, mean5 {r.mean5:+.2%}, win {r.win_rate:.0%}, edge vs W+ {r.mean_edge_vs_wplus:+.2%}, beat W+ {r.beat_wplus_rate:.0%}, MDD {r.mdd:+.1%} (W+ {r.wplus_mdd:+.1%})")
    L += ['','## Incremental factor information test','']
    if not diag.empty:
        q=diag.groupby(['model','eval_year']).agg(n=('n','sum'),median_spearman=('spearman','median'),median_tb=('top_bottom_realized','median')).reset_index()
        for _,r in q.iterrows():
            L.append(f"- {int(r.eval_year)} {r.model}: median rank IC {r.median_spearman:+.3f}; median predicted-top vs bottom realized spread {r.median_tb:+.2%}")
    L += ['','## Strongest stable univariate payoff surfaces','']
    if stable.empty:
        L.append('- None passed same-sign DISCOVERY and 2023-24 screen.')
    else:
        for _,r in stable.head(25).iterrows():
            L.append(f"- {r.universe} | {r.feature} -> {r.action}-W+: H-L {r.discovery_hl:+.2%} (2016-22) -> {r.normal_hl:+.2%} (2023-24); sign {'positive' if r.sign>0 else 'negative'}")
    L += ['','## Interpretation guardrails','',
          '- 2023-2024 has already informed the broader research program, so it is historical validation rather than pristine untouched OOS.',
          '- 2025 and 2026 are reported separately because their market regimes are exceptional and should not be pooled into a generic recent sample.',
          '- A useful finding requires either incremental FULL/FACTOR_ONLY walk-forward value over MARKET_ONLY, or a simple payoff surface whose sign and economic size persist across samples.',
          '- This stage intentionally does not create a new discrete regime taxonomy.','']
    return '\n'.join(L)+'\n'


def main():
    panel,mkt,fact=load_panel(); allfeat=mkt+fact
    pred,coefs=model_predictions(panel,mkt,fact)
    path,stats=policy_from_predictions(pred,panel)
    diag=prediction_diagnostics(pred)
    surface=univariate_surface(panel,allfeat)
    stable=stable_surface(surface)
    panel.to_csv(OUT/'state_feature_action_matrix.csv',index=False)
    pred.to_csv(OUT/'walkforward_action_predictions.csv',index=False)
    coefs.to_csv(OUT/'walkforward_standardized_coefficients.csv',index=False)
    path.to_csv(OUT/'walkforward_action_policy_path.csv',index=False)
    stats.to_csv(OUT/'walkforward_action_policy_performance.csv',index=False)
    diag.to_csv(OUT/'walkforward_prediction_diagnostics.csv',index=False)
    surface.to_csv(OUT/'univariate_payoff_surfaces.csv',index=False)
    stable.to_csv(OUT/'stable_payoff_surfaces.csv',index=False)
    (OUT/'RESEARCH_SUMMARY.md').write_text(summarize(panel,pred,diag,stats,surface,stable,coefs),encoding='utf-8')
    print(f'panel={len(panel):,}; pred={len(pred):,}; policy={len(path):,}; stable={len(stable):,}')

if __name__=='__main__': main()
