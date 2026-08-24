from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
INP=HERE/'results_persistence_rotation/persistence_rotation_panel.csv'
OUT=HERE/'results_crash_crowding'
OUT.mkdir(parents=True,exist_ok=True)

FACTORS=['MOM1M','MOM12_1','OP12_REV','OPFY1_REV','PBR12MF','PER12MF','PRIVATE_FLOW','FOREIGN_FLOW']
BASE_FEATURES=[
 'BREADTH_20','BREADTH_60','DISPERSION_20','DISPERSION_60','ABS_OPPORTUNITY_20','RANGE_20',
 'LEADER_STRENGTH_20','LOSER_WEAKNESS_20','WINNER_GAP_20','CROSS_HORIZON_RANK_CORR',
 'PREV_RANK_CORR_20','RANK_TURNOVER_20','BREADTH_CHANGE_20','DISPERSION_CHANGE_20',
 'AVG_PAIR_CORR_60','PC1_SHARE_60','FACTOR_VOL_MEDIAN_60','SIGN_ALIGNMENT_20_60'
]
CROWD_FEATURES=[
 'LEADER_ABS_SHARE_20','TOP2_ABS_SHARE_20','LEADER_Z_20','TOP2_PREMIUM_20','EXTREME_RANGE_RATIO_20'
]
FEATURES=BASE_FEATURES+CROWD_FEATURES
TARGETS=[
 'TARGET_TOP2_RELATIVE_LOSS_20',
 'TARGET_TOP2_DROP_SHARE_20',
 'TARGET_WORST_LEADER_LOSS_20',
 'TARGET_REVERSAL_GAP_20'
]
MIN_TRAIN=80;MIN_TEST=12


def period_of(y):
 if y<=2022:return 'DEV_2020_2022'
 if y<=2024:return 'CONFIRM_2023_2024'
 if y==2025:return 'BULL_2025'
 return 'YTD_2026'


def spearman(x,y):
 z=pd.concat([x,y],axis=1).dropna()
 if len(z)<3 or z.iloc[:,0].nunique()<2 or z.iloc[:,1].nunique()<2:return np.nan
 return float(z.iloc[:,0].rank().corr(z.iloc[:,1].rank()))


def add_features_targets(p):
 z=p.copy(); cur=z[[f'CUR20_{f}' for f in FACTORS]].to_numpy(float); fwd=z[[f'FWD20_{f}' for f in FACTORS]].to_numpy(float)
 vals=[]
 for i in range(len(z)):
  c=cur[i];y=fwd[i];order=np.argsort(c);bot=order[:2];top=order[-2:]
  med=float(np.median(c));sd=float(np.std(c,ddof=1));abs_sum=float(np.abs(c).sum());abs_mean=float(np.mean(np.abs(c)))
  future_order=np.argsort(y);future_bottom4=set(future_order[:4]);topset=set(top)
  ew=float(np.mean(y));topret=float(np.mean(y[top]));botret=float(np.mean(y[bot]))
  vals.append({
   'LEADER_ABS_SHARE_20':float(abs(c[order[-1]])/abs_sum) if abs_sum>0 else np.nan,
   'TOP2_ABS_SHARE_20':float(np.abs(c[top]).sum()/abs_sum) if abs_sum>0 else np.nan,
   'LEADER_Z_20':float((c.max()-med)/sd) if sd>0 else np.nan,
   'TOP2_PREMIUM_20':float(np.mean(c[top])-med),
   'EXTREME_RANGE_RATIO_20':float((c.max()-c.min())/abs_mean) if abs_mean>0 else np.nan,
   'TARGET_TOP2_RELATIVE_LOSS_20':ew-topret,
   'TARGET_TOP2_DROP_SHARE_20':len(topset & future_bottom4)/2.0,
   'TARGET_WORST_LEADER_LOSS_20':-float(np.min(y[top])),
   'TARGET_REVERSAL_GAP_20':botret-topret,
  })
 return pd.concat([z.reset_index(drop=True),pd.DataFrame(vals)],axis=1)


def walkforward(p):
 rows=[]
 for u,g in p.groupby('universe'):
  g=g.sort_values('date')
  for year in range(2020,int(g.date.dt.year.max())+1):
   tr=g[g.date<pd.Timestamp(f'{year}-01-01')];te=g[g.date.dt.year.eq(year)]
   if len(tr)<MIN_TRAIN or len(te)<MIN_TEST:continue
   for t in TARGETS:
    for f in FEATURES:
     a=tr[[f,t]].dropna();b=te[[f,t]].dropna()
     if len(a)<MIN_TRAIN or len(b)<MIN_TEST:continue
     tic=spearman(a[f],a[t])
     if not np.isfinite(tic) or tic==0:continue
     direction=1 if tic>0 else -1;oic=spearman(b[f],b[t])
     q33,q67=a[f].quantile([1/3,2/3]);lo=b.loc[b[f]<=q33,t];hi=b.loc[b[f]>=q67,t]
     hl=float(hi.mean()-lo.mean()) if len(lo)>=3 and len(hi)>=3 else np.nan
     rows.append({'universe':u,'eval_year':year,'period':period_of(year),'feature':f,'target':t,
      'train_n':len(a),'test_n':len(b),'train_spearman':tic,'direction':direction,'oos_spearman':oic,
      'directed_oos_spearman':direction*oic if np.isfinite(oic) else np.nan,
      'raw_high_minus_low':hl,'directed_high_minus_low':direction*hl if np.isfinite(hl) else np.nan})
 return pd.DataFrame(rows)


def summarize(wf):
 rows=[]
 for (f,t),g in wf.groupby(['feature','target']):
  r={'feature':f,'target':t,'n_universe_years':len(g),'train_direction_median':float(g.direction.median())}
  for p in ['DEV_2020_2022','CONFIRM_2023_2024','BULL_2025','YTD_2026']:
   q=g[g.period.eq(p)];r[f'{p}_median_dic']=float(q.directed_oos_spearman.median()) if len(q) else np.nan
   r[f'{p}_positive_dic_share']=float((q.directed_oos_spearman>0).mean()) if len(q) else np.nan
   r[f'{p}_median_dhl']=float(q.directed_high_minus_low.median()) if len(q) else np.nan
  q=g[g.period.eq('CONFIRM_2023_2024')];byu=q.groupby('universe').directed_oos_spearman.median() if len(q) else pd.Series(dtype=float)
  r['CONFIRM_positive_universes']=int((byu>0).sum());r['CONFIRM_universe_count']=len(byu)
  r['PASS']=bool(r['DEV_2020_2022_median_dic']>0 and r['CONFIRM_2023_2024_median_dic']>0 and r['CONFIRM_2023_2024_median_dhl']>0 and r['CONFIRM_positive_universes']>=4)
  rows.append(r)
 return pd.DataFrame(rows).sort_values(['PASS','CONFIRM_2023_2024_median_dic','DEV_2020_2022_median_dic'],ascending=[False,False,False]).reset_index(drop=True)


def fmt(x):return 'NA' if not np.isfinite(x) else f'{x:+.3f}'
def pct(x):return 'NA' if not np.isfinite(x) else f'{x:+.2%}'


def report(s):
 L=['# Zero-Base Factor Crash / Crowding Risk — Stage 3','',
 '- Targets are explicitly adverse: current top-2 future underperformance vs EW8, current top-2 dropping into the future bottom half, worst current-leader forward loss, and current-bottom2 minus current-top2 reversal gap.',
 '- The 18 prior structural predictors are augmented by five factor-level crowding/concentration measures declared before this run: leader absolute-payoff share, top2 absolute-payoff share, leader z-score, top2 premium, and normalized extreme range.',
 '- Direction and tercile thresholds are trained only on dates before each evaluation year. A positive directed result means the train-learned risk direction continues to separate future crash/reversal risk.',
 '- PASS gate is unchanged: positive directed median IC in 2020-22 and 2023-24, positive 2023-24 directed H-L, and >=4/6 positive universe-median IC.','',
 f'## Result: {int(s.PASS.sum())} PASS relations out of {len(s)} screened','']
 for r in s[s.PASS].head(30).itertuples(index=False):
  sign='HIGH_BAD' if r.train_direction_median>0 else 'LOW_BAD'
  L.append(f'- {r.target} <- {r.feature} ({sign}): DEV IC {fmt(r.DEV_2020_2022_median_dic)}, CONFIRM IC {fmt(r.CONFIRM_2023_2024_median_dic)}, CONFIRM H-L {pct(r.CONFIRM_2023_2024_median_dhl)}, universes {r.CONFIRM_positive_universes}/{r.CONFIRM_universe_count}, 2025 {fmt(r.BULL_2025_median_dic)}, 2026 {fmt(r.YTD_2026_median_dic)}')
 L += ['','## Best relations by target','']
 for t in TARGETS:
  L.append(f'### {t}')
  for r in s[s.target.eq(t)].sort_values('CONFIRM_2023_2024_median_dic',ascending=False).head(7).itertuples(index=False):
   sign='HIGH_BAD' if r.train_direction_median>0 else 'LOW_BAD'
   L.append(f'- {r.feature} ({sign}): PASS={r.PASS}; DEV {fmt(r.DEV_2020_2022_median_dic)}, CONFIRM {fmt(r.CONFIRM_2023_2024_median_dic)}, H-L {pct(r.CONFIRM_2023_2024_median_dhl)}, universes {r.CONFIRM_positive_universes}/{r.CONFIRM_universe_count}, 2025 {fmt(r.BULL_2025_median_dic)}, 2026 {fmt(r.YTD_2026_median_dic)}')
  L.append('')
 L += ['## Next-step rule','',
 '- Only if a small coherent set of crash predictors survives across multiple adverse targets should a crash-risk cap be tested economically.',
 '- Do not combine one-off near-misses or tune 2025/2026 thresholds.',
 '- If factor-level crowding is weak, the next extension should add stock-level participation/turnover/ADV/holdings-overlap variables rather than further transforming the same factor returns.']
 return '\n'.join(L)


def main():
 p=pd.read_csv(INP);p['date']=pd.to_datetime(p.date);p=add_features_targets(p)
 wf=walkforward(p);s=summarize(wf)
 p.to_csv(OUT/'crash_crowding_panel.csv',index=False,encoding='utf-8-sig');wf.to_csv(OUT/'crash_crowding_walkforward.csv',index=False,encoding='utf-8-sig');s.to_csv(OUT/'crash_crowding_summary.csv',index=False,encoding='utf-8-sig')
 text=report(s);(OUT/'RESEARCH_SUMMARY.md').write_text(text,encoding='utf-8');print(text)

if __name__=='__main__':main()
