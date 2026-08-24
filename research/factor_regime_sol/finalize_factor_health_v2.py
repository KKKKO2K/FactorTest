from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

HERE=Path(__file__).resolve().parent
OUT=HERE/'results_factor_health_v2'
FAMILIES=('MOMENTUM','REVISION','VALUE','FLOW')
METRICS=('FH_A_HEALTHY_BREADTH','FH_B_NET_BREADTH','FH_C_CONTINUOUS')


def robustness_table(hl: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for metric in METRICS:
        tr=hl[(hl['metric']==metric)&(hl['sample']=='TRAIN_2017_2022')&(hl['horizon']==20)&(hl['outcome']=='top')]
        po=hl[(hl['metric']==metric)&(hl['sample']=='POST_2023_PLUS')&(hl['horizon']==20)&(hl['outcome']=='top')]
        m=tr.merge(po,on=['universe','target','horizon','outcome','metric'],suffixes=('_tr','_po'))
        if m.empty: continue
        rows.append({
            'metric':metric,'n_pairs':len(m),
            'train_median_hl':m.high_minus_low_tr.median(),
            'post_median_hl':m.high_minus_low_po.median(),
            'train_positive_share':(m.high_minus_low_tr>0).mean(),
            'post_positive_share':(m.high_minus_low_po>0).mean(),
            'same_positive_share':((m.high_minus_low_tr>0)&(m.high_minus_low_po>0)).mean(),
            'sign_agreement_share':(np.sign(m.high_minus_low_tr)==np.sign(m.high_minus_low_po)).mean(),
        })
    return pd.DataFrame(rows)


def fmt(x):
    return 'NA' if pd.isna(x) else f'{x:+.2%}'


def write_summary(rob:pd.DataFrame,hl:pd.DataFrame,conflict:pd.DataFrame)->str:
    lines=['# Factor Health 2.0 — generalized ex-target test','',
           'Target family itself is excluded from health. This tests whether the *other* factor families contain useful information about a target factor\'s subsequent preferred-leg performance.','',
           '## Definitions','',
           '- FH-A Healthy Breadth = # W+ among the other 3 families / 3.',
           '- FH-B Net Breadth = (# W+ - # R-) among the other 3 / 3; all other states are neutral.',
           '- FH-C Continuous = mean across the other 3 of 0.5*z(20D spread)+0.5*z(20D preferred-leg absolute return); z parameters fit pre-2023 and frozen.',
           '- Conflict is separate: at least one ex-target W+ and at least one ex-target R-.','',
           'Primary lens is HIGH-minus-LOW future 20D preferred-leg return. 20D points overlap on the 5D grid; NW lag-3 t-stats are descriptive.','',
           '## Aggregate robustness: 6 universes × 4 targets','',
           '| Metric | Pairs | Train median H-L | Post median H-L | Train + | Post + | + in both | Sign agreement |',
           '|---|---:|---:|---:|---:|---:|---:|---:|']
    for _,r in rob.iterrows():
        lines.append(f"| {r.metric} | {int(r.n_pairs)} | {r.train_median_hl:+.2%} | {r.post_median_hl:+.2%} | {r.train_positive_share:.0%} | {r.post_positive_share:.0%} | {r.same_positive_share:.0%} | {r.sign_agreement_share:.0%} |")
    lines += ['', '## Median H-L by target family across universes','',
              '| Metric | Sample | Momentum | Revision | Value | Flow |','|---|---|---:|---:|---:|---:|']
    for metric in METRICS:
        for sample in ('TRAIN_2017_2022','POST_2023_PLUS','POST_2023_2024','BULL_2025','YTD_2026'):
            z=hl[(hl['metric']==metric)&(hl['sample']==sample)&(hl['horizon']==20)&(hl['outcome']=='top')]
            vals={f:(z.loc[z.target==f,'high_minus_low'].median() if (z.target==f).any() else np.nan) for f in FAMILIES}
            lines.append(f"| {metric} | {sample} | {fmt(vals['MOMENTUM'])} | {fmt(vals['REVISION'])} | {fmt(vals['VALUE'])} | {fmt(vals['FLOW'])} |")
    lines += ['', '## Strongest cells positive in both TRAIN and POST','',
              '| Metric | Universe | Target | Train H-L | Post H-L | Train t | Post t |','|---|---|---|---:|---:|---:|---:|']
    tr=hl[(hl['sample']=='TRAIN_2017_2022')&(hl['horizon']==20)&(hl['outcome']=='top')]
    po=hl[(hl['sample']=='POST_2023_PLUS')&(hl['horizon']==20)&(hl['outcome']=='top')]
    m=tr.merge(po,on=['universe','target','horizon','outcome','metric'],suffixes=('_tr','_po'))
    m=m[(m.high_minus_low_tr>0)&(m.high_minus_low_po>0)].copy()
    if not m.empty:
        m['floor']=m[['high_minus_low_tr','high_minus_low_po']].min(axis=1)
        for _,r in m.sort_values('floor',ascending=False).head(24).iterrows():
            lines.append(f"| {r.metric} | {r.universe} | {r.target} | {r.high_minus_low_tr:+.2%} | {r.high_minus_low_po:+.2%} | {r.nw_t_tr:+.2f} | {r.nw_t_po:+.2f} |")
    lines += ['', '## Conflict incremental test','',
              'Regression: future target return ~ FH-B Net Breadth + Conflict. A negative Conflict beta means cross-factor disagreement hurts after controlling for net breadth.','']
    for sample in ('TRAIN_2017_2022','POST_2023_PLUS'):
        z=conflict[(conflict['sample']==sample)&(conflict['horizon']==20)&(conflict['outcome']=='top')]
        if not z.empty:
            lines.append(f"- {sample}: median Conflict beta {z.conflict_beta.median():+.2%}; negative in {(z.conflict_beta<0).mean():.0%} of cells; median NW t {z.conflict_nw_t.median():+.2f}; n={len(z)}")
    lines += ['', '## Selection rule','',
              'Prefer the simplest definition that keeps the same economic sign across TRAIN and POST and works across several target families/universes. FH-C is only worth keeping if it materially improves stability over FH-A/FH-B.','']
    return '\n'.join(lines)+'\n'


def main():
    hl=pd.read_csv(OUT/'health_high_low_results.csv')
    conflict=pd.read_csv(OUT/'conflict_incremental_results.csv')
    rob=robustness_table(hl)
    rob.to_csv(OUT/'metric_robustness.csv',index=False,encoding='utf-8-sig')
    (OUT/'RESEARCH_SUMMARY.md').write_text(write_summary(rob,hl,conflict),encoding='utf-8')
    print(f'finalized robustness={len(rob)} hl={len(hl)} conflict={len(conflict)}')

if __name__=='__main__': main()
