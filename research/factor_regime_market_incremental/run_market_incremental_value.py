from __future__ import annotations

from pathlib import Path
import math
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / 'results'
OUT.mkdir(parents=True, exist_ok=True)

NESTED = ROOT / 'research/factor_regime_contemporaneous_states/results/nested_state_assignments.csv'
HSTATE = ROOT / 'research/factor_regime_horizon_robustness/results/horizon_state_values.csv'
HTEST = ROOT / 'research/factor_regime_horizon_robustness/results/horizon_tests.csv'
MIN_CELL = 20
EPS = 1e-6

MODELS = {
    'B_ONLY': ['base_state'],
    'B_FSUB': ['base_state','factor_substate'],
    'B_FB20': ['base_state','fb20_bin'],
    'B_FSUB_FB20': ['base_state','factor_substate','fb20_bin'],
}


def sample_of(dt: pd.Timestamp) -> str:
    if dt < pd.Timestamp('2023-01-01'): return 'TRAIN_2016_2022'
    if dt < pd.Timestamp('2025-01-01'): return 'OOS_2023_2024'
    if dt < pd.Timestamp('2026-01-01'): return 'BULL_2025'
    return 'YTD_2026'


def load_panel() -> pd.DataFrame:
    n = pd.read_csv(NESTED)
    n['date'] = pd.to_datetime(n['date'])
    hs = pd.read_csv(HSTATE)
    hs['date'] = pd.to_datetime(hs['date'])
    hs = hs[(hs.predictor_type=='FACTOR_BREADTH') & (hs.definition=='FACTOR_20D')][['date','universe','value']].rename(columns={'value':'fb20'})
    ht = pd.read_csv(HTEST)
    ht = ht[(ht.predictor_type=='FACTOR_BREADTH') & (ht.definition=='FACTOR_20D') & (ht['sample']=='TRAIN')]
    th = ht.groupby('universe')[['train_q1','train_q2']].first().reset_index()
    x = n.merge(hs,on=['date','universe'],how='left').merge(th,on='universe',how='left')
    x['fb20_bin'] = np.where(x.fb20<=x.train_q1,'LOW',np.where(x.fb20>=x.train_q2,'HIGH','MID'))
    x.loc[x.fb20.isna(),'fb20_bin'] = np.nan
    x['sample'] = x.date.map(sample_of)
    x['TARGET_NEXT_B_DOWN'] = pd.to_numeric(x['NEXT_BASE_DOWN'],errors='coerce')
    x['TARGET_MKT_NEG20'] = np.where(x['MKT_FWD_20D'].notna(),(x['MKT_FWD_20D']<0).astype(float),np.nan)
    x['TARGET_DD5_20'] = np.where(x['MKT_FWD_DD20'].notna(),(x['MKT_FWD_DD20']<=-0.05).astype(float),np.nan)
    x.to_csv(OUT/'market_incremental_panel.csv',index=False,encoding='utf-8-sig')
    return x


def fit_lookup(train: pd.DataFrame, target: str, cols: list[str]):
    z = train.dropna(subset=[target]+cols).copy()
    # Baseline by B-state is always retained as fallback.
    b = z.groupby('base_state')[target].agg(['mean','count'])
    global_p = float(z[target].mean())
    lookup = z.groupby(cols)[target].agg(['mean','count']) if cols else pd.DataFrame()
    return lookup,b,global_p


def predict(df: pd.DataFrame, target: str, cols: list[str], lookup, b, global_p) -> pd.Series:
    out=[]
    for r in df.itertuples(index=False):
        bstate=getattr(r,'base_state')
        fallback=float(b.loc[bstate,'mean']) if bstate in b.index else global_p
        if cols==['base_state']:
            out.append(fallback); continue
        vals=tuple(getattr(r,c) for c in cols)
        if any(pd.isna(v) for v in vals):
            out.append(fallback); continue
        key=vals if len(vals)>1 else vals[0]
        try:
            row=lookup.loc[key]
            if isinstance(row,pd.DataFrame): row=row.iloc[0]
            out.append(float(row['mean']) if int(row['count'])>=MIN_CELL else fallback)
        except KeyError:
            out.append(fallback)
    return pd.Series(out,index=df.index,dtype=float).clip(EPS,1-EPS)


def auc(y: pd.Series,p: pd.Series) -> float:
    z=pd.DataFrame({'y':y,'p':p}).dropna()
    pos=z[z.y==1]; neg=z[z.y==0]
    if len(pos)==0 or len(neg)==0: return np.nan
    ranks=z.p.rank(method='average')
    sum_pos=float(ranks[z.y==1].sum())
    return (sum_pos-len(pos)*(len(pos)+1)/2)/(len(pos)*len(neg))


def metrics(y: pd.Series,p: pd.Series) -> dict:
    z=pd.DataFrame({'y':y,'p':p}).dropna()
    if len(z)==0: return {'n':0,'event_rate':np.nan,'brier':np.nan,'logloss':np.nan,'auc':np.nan}
    pp=z.p.clip(EPS,1-EPS)
    return {
        'n':len(z),'event_rate':float(z.y.mean()),
        'brier':float(((z.y-pp)**2).mean()),
        'logloss':float(-(z.y*np.log(pp)+(1-z.y)*np.log(1-pp)).mean()),
        'auc':auc(z.y,pp),
    }


def run_models(x: pd.DataFrame) -> pd.DataFrame:
    targets=['TARGET_NEXT_B_DOWN','TARGET_MKT_NEG20','TARGET_DD5_20']
    rows=[]
    for u,g in x.groupby('universe'):
        train=g[g['sample']=='TRAIN_2016_2022'].copy()
        for target in targets:
            for model,cols in MODELS.items():
                lookup,b,gp=fit_lookup(train,target,cols)
                for sample in ('TRAIN_2016_2022','OOS_2023_2024','BULL_2025','YTD_2026'):
                    s=g[g['sample']==sample].copy()
                    if s.empty: continue
                    p=predict(s,target,cols,lookup,b,gp)
                    m=metrics(s[target],p)
                    rows.append({'universe':u,'target':target,'model':model,'sample':sample,**m})
    r=pd.DataFrame(rows)
    r.to_csv(OUT/'market_incremental_metrics.csv',index=False,encoding='utf-8-sig')
    return r


def compare(r: pd.DataFrame) -> pd.DataFrame:
    b=r[r.model=='B_ONLY'][['universe','target','sample','brier','logloss','auc']].rename(columns={'brier':'base_brier','logloss':'base_logloss','auc':'base_auc'})
    z=r[r.model!='B_ONLY'].merge(b,on=['universe','target','sample'],how='left')
    z['delta_brier']=z.brier-z.base_brier
    z['delta_logloss']=z.logloss-z.base_logloss
    z['delta_auc']=z.auc-z.base_auc
    z.to_csv(OUT/'market_incremental_vs_base.csv',index=False,encoding='utf-8-sig')
    return z


def fmt(x): return 'NA' if pd.isna(x) else f'{x:+.4f}'


def report(r,z):
    lines=['# Factor Regime — Incremental Market-State Value','',
        '- Question: does frozen factor-state information improve market-state/downside prediction beyond the frozen B-state alone?',
        '- Models are non-parametric TRAIN 2016-22 conditional event rates. Augmented cells with <20 TRAIN observations fall back to the B-state probability; no 2023+ fitting is allowed.',
        '- Predictors: B_ONLY; B_FSUB = B × frozen F_HIGH/F_LOW; B_FB20 = B × frozen FACTOR_20D LOW/MID/HIGH; B_FSUB_FB20 = all three.',
        '- Targets: next B-state down-transition; negative 20D market return; >=5% forward-20D drawdown.',
        '- Lower Brier/log-loss is better; higher AUC is better. Primary confirmation sample is 2023-24; 2025/2026 are stress descriptions.','']
    for target in ('TARGET_NEXT_B_DOWN','TARGET_MKT_NEG20','TARGET_DD5_20'):
        lines += [f'## {target}','']
        for sample in ('OOS_2023_2024','BULL_2025','YTD_2026'):
            lines.append(f'### {sample}')
            zz=z[(z.target==target)&(z['sample']==sample)]
            for model in ('B_FSUB','B_FB20','B_FSUB_FB20'):
                q=zz[zz.model==model]
                if q.empty: continue
                lines.append(f'- {model}: median ΔBrier {fmt(q.delta_brier.median())}; median Δlogloss {fmt(q.delta_logloss.median())}; median ΔAUC {fmt(q.delta_auc.median())}; Brier-better universes {(q.delta_brier<0).sum()}/{len(q)}')
            lines.append('')
    lines += ['## Universe detail — OOS 2023-24 next-B-down','']
    zz=z[(z.target=='TARGET_NEXT_B_DOWN')&(z['sample']=='OOS_2023_2024')]
    for u in sorted(zz.universe.unique()):
        q=zz[zz.universe==u]
        bits=[]
        for model in ('B_FSUB','B_FB20','B_FSUB_FB20'):
            a=q[q.model==model]
            if not a.empty: bits.append(f'{model} ΔBrier={a.delta_brier.iloc[0]:+.4f}, ΔAUC={a.delta_auc.iloc[0]:+.3f}')
        lines.append(f'- {u}: '+'; '.join(bits))
    lines += ['','## Interpretation gate','',
        '- PASS as market-regime information only if an augmented model improves 2023-24 median Brier and does so in at least 4/6 universes for the same target.',
        '- A 2025/2026-only improvement is not confirmation.',
        '- This test evaluates information value, not a trading strategy; any market allocation rule would require a separate pre-specified mapping and exact NAV test.']
    return '\n'.join(lines)


def main():
    x=load_panel(); r=run_models(x); z=compare(r); text=report(r,z)
    (OUT/'RESEARCH_SUMMARY.md').write_text(text,encoding='utf-8'); print(text)

if __name__=='__main__': main()
