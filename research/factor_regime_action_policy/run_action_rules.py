from __future__ import annotations
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
IN=ROOT/'research/factor_regime_action_policy/results/action_returns_long.csv'
OUT=ROOT/'research/factor_regime_action_policy/results'
FAMS=['MOMENTUM','REVISION','VALUE','FLOW']


def path_stats(g, retcol='ret'):
    g=g.sort_values('date'); r=g[retcol].dropna()
    if len(r)<5:return None
    eq=(1+r).cumprod(); years=max((g.date.max()-g.date.min()).days/365.25,len(r)*5/252)
    return dict(n=len(r),win_rate=(r>0).mean(),mean5=r.mean(),median5=r.median(),cagr=eq.iloc[-1]**(1/years)-1,
                mdd=(eq/eq.cummax()-1).min(),worst5=r.min(),mean_excess=(r-g.loc[r.index,'MARKET']).mean(),beat_mkt=((r-g.loc[r.index,'MARKET'])>0).mean())


def load():
    x=pd.read_csv(IN); x['date']=pd.to_datetime(x.date)
    x=x[x.horizon.eq(5)].copy()
    idx=['date','universe','period','base_state','factor_substate','state_cell']
    w=x.pivot_table(index=idx,columns='action',values='ret',aggfunc='first').reset_index()
    return w


def contrast_table(w):
    pairs=[('WPLUS','MARKET'),('WPLUS','EW4')]+[(f,'WPLUS') for f in FAMS]
    rows=[]
    for (u,p,bs,fs,cell),g in w.groupby(['universe','period','base_state','factor_substate','state_cell']):
        for a,b in pairs:
            if a not in g or b not in g: continue
            d=g[a]-g[b]
            rows.append(dict(universe=u,period=p,base_state=bs,factor_substate=fs,state_cell=cell,a=a,b=b,n=len(d),
                             mean_diff=d.mean(),median_diff=d.median(),win_vs_b=(d>0).mean()))
    return pd.DataFrame(rows)


def stability(c):
    keys=['universe','state_cell','a','b']; rows=[]
    for key,g in c.groupby(keys):
        tr=g[g.period.eq('TRAIN_2016_2022')]; va=g[g.period.eq('VALID_2023_2024')]
        if tr.empty or va.empty:continue
        t=tr.iloc[0];v=va.iloc[0]
        if min(t.n,v.n)<8:continue
        rows.append({**dict(zip(keys,key)),'train_n':t.n,'valid_n':v.n,'train_diff':t.mean_diff,'valid_diff':v.mean_diff,
                     'same_sign':float(np.sign(t.mean_diff)==np.sign(v.mean_diff)),'train_win_vs_b':t.win_vs_b,'valid_win_vs_b':v.win_vs_b})
    return pd.DataFrame(rows)


def rule_return(r,rule):
    wp=r.WPLUS; m=r.MARKET; bs=r.base_state; fh=r.factor_substate
    if rule=='ALWAYS_WPLUS':return wp
    if rule=='ALWAYS_EW4':return r.EW4
    if rule=='F_LOW_MARKET':return wp if fh=='F_HIGH' else m
    if rule=='REPAIR_F_LOW_MARKET':return m if (bs in ['B2','B3'] and fh=='F_LOW') else wp
    if rule=='B2_F_LOW_MARKET':return m if (bs=='B2' and fh=='F_LOW') else wp
    if rule=='F_LOW_HALF':return wp*(1.0 if fh=='F_HIGH' else .5)
    if rule=='REPAIR_F_LOW_HALF':return wp*(.5 if (bs in ['B2','B3'] and fh=='F_LOW') else 1.0)
    if rule=='B2_F_LOW_HALF':return wp*(.5 if (bs=='B2' and fh=='F_LOW') else 1.0)
    if rule=='REPAIR_F_LOW_CASH':return 0.0 if (bs in ['B2','B3'] and fh=='F_LOW') else wp
    if rule=='B2_F_LOW_CASH':return 0.0 if (bs=='B2' and fh=='F_LOW') else wp
    if rule=='B4_F_HIGH_HALF':return wp*(.5 if (bs=='B4' and fh=='F_HIGH') else 1.0)
    if rule=='B4_MARKET':return m if bs=='B4' else wp
    raise KeyError(rule)

RULES=['ALWAYS_WPLUS','ALWAYS_EW4','F_LOW_MARKET','REPAIR_F_LOW_MARKET','B2_F_LOW_MARKET','F_LOW_HALF','REPAIR_F_LOW_HALF','B2_F_LOW_HALF','REPAIR_F_LOW_CASH','B2_F_LOW_CASH','B4_F_HIGH_HALF','B4_MARKET']


def test_rules(w):
    rows=[]; paths=[]
    for rule in RULES:
        z=w.copy();z['rule']=rule;z['ret']=[rule_return(r,rule) for _,r in z.iterrows()]
        paths.append(z[['date','universe','period','base_state','factor_substate','state_cell','rule','ret','MARKET','WPLUS','EW4']])
        for (u,p),g in z.groupby(['universe','period']):
            s=path_stats(g)
            if s: rows.append(dict(universe=u,period=p,rule=rule,**s))
    return pd.concat(paths,ignore_index=True),pd.DataFrame(rows)


def family_candidates(stab):
    q=stab[(stab.b=='WPLUS') & (stab.a.isin(FAMS)) & (stab.same_sign==1)].copy()
    q=q[(q.train_diff>0)&(q.valid_diff>0)]
    return q.sort_values(['valid_diff','train_diff'],ascending=False)


def write_summary(rules,stab,fam):
    lines=['# Simple Investment Rules from Factor Regimes','',
           'Core question: keep W+ stock selection fixed and use the contemporaneous regime only for exposure/switching/family tilts. No validation outcome enters rule definitions.','',
           '## 2023-2024 rule results','']
    v=rules[rules.period.eq('VALID_2023_2024')]
    for u,g in v.groupby('universe'):
        lines.append(f'### {u}')
        for rule in RULES:
            z=g[g.rule.eq(rule)]
            if z.empty:continue
            r=z.iloc[0];lines.append(f'- {rule}: win {r.win_rate:.0%}, mean5 {r.mean5:+.2%}, excess {r.mean_excess:+.2%}, CAGR {r.cagr:+.1%}, MDD {r.mdd:+.1%}')
    lines+=['','## 2025 stress: selected simple controls','']
    v=rules[rules.period.eq('STRESS_2025')]
    for u,g in v.groupby('universe'):
        lines.append(f'### {u}')
        for rule in ['ALWAYS_WPLUS','REPAIR_F_LOW_MARKET','REPAIR_F_LOW_HALF','B2_F_LOW_MARKET','B4_F_HIGH_HALF']:
            z=g[g.rule.eq(rule)]
            if z.empty:continue
            r=z.iloc[0];lines.append(f'- {rule}: win {r.win_rate:.0%}, mean5 {r.mean5:+.2%}, excess {r.mean_excess:+.2%}, CAGR {r.cagr:+.1%}, MDD {r.mdd:+.1%}')
    lines+=['','## Stable state-specific family tilts over WPLUS','']
    if fam.empty:lines.append('- None with n>=8 in both TRAIN and 2023-2024.')
    else:
        for _,r in fam.head(30).iterrows():lines.append(f'- {r.universe} {r.state_cell}: {r.a} - WPLUS {r.train_diff:+.2%} TRAIN -> {r.valid_diff:+.2%} VALID; win-vs-W+ {r.train_win_vs_b:.0%}->{r.valid_win_vs_b:.0%}; n {int(r.train_n)}/{int(r.valid_n)}')
    lines+=['','## Interpretation discipline','',
            '- Promotion requires improvement versus ALWAYS_WPLUS, not merely versus the market.',
            '- A rule that helps 2023-2024 but reverses in 2025 is regime-contingent, not a permanent allocation rule.',
            '- Family tilts are candidates only when the same state/action contrast has the same positive sign in TRAIN and VALID with adequate n.','']
    return '\n'.join(lines)+'\n'


def main():
    w=load();c=contrast_table(w);s=stability(c);fam=family_candidates(s);paths,rules=test_rules(w)
    c.to_csv(OUT/'state_action_contrasts.csv',index=False);s.to_csv(OUT/'state_action_contrast_stability.csv',index=False);fam.to_csv(OUT/'stable_family_tilts.csv',index=False)
    paths.to_csv(OUT/'simple_rule_paths_5d.csv',index=False);rules.to_csv(OUT/'simple_rule_performance.csv',index=False)
    (OUT/'SIMPLE_RULES_SUMMARY.md').write_text(write_summary(rules,s,fam),encoding='utf-8')
    print(f'wide={len(w):,}; stable contrasts={len(s):,}; family candidates={len(fam):,}')

if __name__=='__main__':main()
