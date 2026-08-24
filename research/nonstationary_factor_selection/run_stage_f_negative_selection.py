from pathlib import Path
import math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'research/factor_regime_v1/results/factor_5d_returns.csv'
BASE=Path(__file__).resolve().parent/'results'
OUT=Path(__file__).resolve().parent/'results_stage_f_negative_selection'
OUT.mkdir(parents=True,exist_ok=True)
FACTORS=['MOM1M','MOM12_1','OP12_REV','OPFY1_REV','PBR12MF','PER12MF','PRIVATE_FLOW','FOREIGN_FLOW']
UNIVERSES=['K200','KOSDAQ','KOSPI_EX_K200','KOSPI_ALL','KOSPI_KOSDAQ_ALL','KOSDAQ_PLUS_KOSPI_EX_K200']
PERIODS=['VAL_2020_2022','CONF_2023_2024','STRESS_2025','STRESS_2026']

def period(dt):
    y=pd.Timestamp(dt).year
    if 2020<=y<=2022:return 'VAL_2020_2022'
    if 2023<=y<=2024:return 'CONF_2023_2024'
    if y==2025:return 'STRESS_2025'
    if y==2026:return 'STRESS_2026'
    return None

def sharpe(x):
    x=pd.Series(x).dropna()
    return float(x.mean()/x.std(ddof=1)*math.sqrt(252/5)) if len(x)>3 and x.std(ddof=1)>0 else np.nan

def cagr(x):
    x=pd.Series(x).dropna()
    if len(x)<2 or (x<=-1).any():return np.nan
    nav=float(np.prod(1+x)); years=len(x)*5/252
    return nav**(1/years)-1 if nav>0 else np.nan

f=pd.read_csv(SRC); f['date']=pd.to_datetime(f['date']); f=f[f.factor.isin(FACTORS)&f.universe.isin(UNIVERSES)].copy(); f['ls_return']=pd.to_numeric(f['ls_return'],errors='coerce')
q=pd.read_csv(BASE/'pairwise_quality_scores.csv'); q['date']=pd.to_datetime(q['date']); q=q.set_index('date')[FACTORS]
rows=[]
for u in UNIVERSES:
    r=f[f.universe.eq(u)].pivot(index='date',columns='factor',values='ls_return').sort_index().reindex(columns=FACTORS).dropna(how='any')
    idx=r.index.intersection(q.index); r=r.loc[idx]; qq=q.loc[idx]
    w=pd.DataFrame(0.0,index=idx,columns=FACTORS)
    for i,dt in enumerate(idx):
        bottom=np.argsort(qq.loc[dt].to_numpy(dtype=float))[:2]
        ww=np.ones(8)/6; ww[bottom]=0; w.iloc[i]=ww
    gross=pd.Series((w.to_numpy()*r.to_numpy()).sum(axis=1),index=idx)
    turn=.5*w.diff().abs().sum(axis=1); turn.iloc[0]=0
    ew=r.mean(axis=1)
    for cost in [0,10,30]:
        net=gross-(cost/10000)*turn
        for p in PERIODS:
            m=np.array([period(d)==p for d in idx]); x=net[m]; b=ew[m]
            rows.append({'universe':u,'period':p,'cost_bps':cost,'strategy':'PAIRWISE_BOTTOM2_VETO','sharpe':sharpe(x),'ew8_sharpe':sharpe(b),'delta_sharpe_vs_ew8':sharpe(x)-sharpe(b),'cagr':cagr(x),'ew8_cagr':cagr(b),'delta_cagr_vs_ew8':cagr(x)-cagr(b),'annualized_weight_turnover':float(turn[m].mean()*252/5)})
res=pd.DataFrame(rows); res.to_csv(OUT/'performance.csv',index=False,encoding='utf-8-sig')
p10=res[res.cost_bps.eq(10)]; summary=[]
for p in PERIODS:
    z=p10[p10.period.eq(p)]; summary.append({'period':p,'median_delta_sharpe_vs_ew8':float(z.delta_sharpe_vs_ew8.median()),'positive_universes':int((z.delta_sharpe_vs_ew8>0).sum()),'median_delta_cagr_vs_ew8':float(z.delta_cagr_vs_ew8.median())})
s=pd.DataFrame(summary); s.to_csv(OUT/'summary.csv',index=False,encoding='utf-8-sig')
v=s[s.period.eq('VAL_2020_2022')].iloc[0]; c=s[s.period.eq('CONF_2023_2024')].iloc[0]
passed=bool(v.median_delta_sharpe_vs_ew8>0 and v.positive_universes>=4 and c.median_delta_sharpe_vs_ew8>0 and c.positive_universes>=4)
lines=['# Stage F — Pairwise Negative Selection (Post-hoc Exploratory)','', 'This stage was added only after Stage D showed positive rank IC across all eras but concentrated TOP3 selection failed. It is therefore exploratory, not an independent confirmatory test.','',f'- Primary-style gate (diagnostic only): **{passed}**']
for x in s.itertuples(index=False):lines.append(f'- {x.period}: median ΔSharpe vs EW8 {x.median_delta_sharpe_vs_ew8:+.3f} ({x.positive_universes}/6); median ΔCAGR {x.median_delta_cagr_vs_ew8:+.2%}')
(OUT/'RESEARCH_SUMMARY.md').write_text('\n'.join(lines),encoding='utf-8')
print('\n'.join(lines))
