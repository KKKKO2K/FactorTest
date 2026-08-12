from __future__ import annotations

import numpy as np
import pandas as pd
import run_action_policy as base

THRESHOLDS=(0.00,0.03,0.05)


def metrics(g: pd.DataFrame) -> dict:
    r=g.ret.dropna(); ex=g.loc[r.index,"excess"]
    return {"n":len(r),"win":float((r>0).mean()),"mean":float(r.mean()),"beat":float((ex>0).mean()),"excess":float(ex.mean())}


def choose(long: pd.DataFrame):
    tr=long[(long.period=="TRAIN_2016_2022") & (long.horizon==5)].copy()
    choices=[]; uncond=[]
    for u,gu in tr.groupby("universe"):
        um={}
        for a,ga in gu[gu.action.isin(base.DYNAMIC_ACTIONS)].groupby("action"):
            um[a]=metrics(ga)
        abs_u=max(um, key=lambda a:(um[a]["win"],um[a]["mean"],um[a]["beat"]))
        alpha_pool={a:m for a,m in um.items() if a in base.ALPHA_ACTIONS}
        alpha_u=max(alpha_pool,key=lambda a:(alpha_pool[a]["beat"],alpha_pool[a]["excess"],alpha_pool[a]["mean"]))
        abs_u_final=abs_u if um[abs_u]["win"]>0.50 and um[abs_u]["mean"]>0 else "CASH"
        uncond += [
            {"universe":u,"policy":"ABS_UNCOND","action":abs_u_final,"raw_action":abs_u,**{f"train_{k}":v for k,v in um[abs_u].items()}},
            {"universe":u,"policy":"ALPHA_UNCOND","action":alpha_u,**{f"train_{k}":v for k,v in alpha_pool[alpha_u].items()}},
        ]
        for cell,gc in gu.groupby("state_cell"):
            base_state,fsub=cell.split("|")
            cm={}
            for a,ga in gc[gc.action.isin(base.DYNAMIC_ACTIONS)].groupby("action"):
                if len(ga)>=20: cm[a]=metrics(ga)
            if not cm: continue
            best_abs=max(cm,key=lambda a:(cm[a]["win"],cm[a]["mean"],cm[a]["beat"]))
            ca={a:m for a,m in cm.items() if a in base.ALPHA_ACTIONS}
            best_alpha=max(ca,key=lambda a:(ca[a]["beat"],ca[a]["excess"],ca[a]["mean"]))
            for th in THRESHOLDS:
                use_abs=best_abs if cm[best_abs]["win"] >= um[abs_u]["win"]+th else abs_u
                ma=cm.get(use_abs,um[use_abs])
                if ma["win"]<=0.50 or ma["mean"]<=0: use_abs="CASH"
                use_alpha=best_alpha if ca[best_alpha]["beat"] >= alpha_pool[alpha_u]["beat"]+th else alpha_u
                tag=int(round(th*100))
                choices += [
                    {"universe":u,"state_cell":cell,"base_state":base_state,"factor_substate":fsub,"policy":f"ABS_STATE_{tag}PP","action":use_abs,"state_best":best_abs,"uncond":abs_u,"state_edge":cm[best_abs]["win"]-um[abs_u]["win"]},
                    {"universe":u,"state_cell":cell,"base_state":base_state,"factor_substate":fsub,"policy":f"ALPHA_STATE_{tag}PP","action":use_alpha,"state_best":best_alpha,"uncond":alpha_u,"state_edge":ca[best_alpha]["beat"]-alpha_pool[alpha_u]["beat"]},
                ]
    return pd.DataFrame(choices),pd.DataFrame(uncond)


def backtest(x,choices,uncond):
    c={(r.universe,r.state_cell,r.policy):r.action for _,r in choices.iterrows()}
    uc={(r.universe,r.policy):r.action for _,r in uncond.iterrows()}
    policy_names=[f"ABS_STATE_{k}PP" for k in (0,3,5)]+[f"ALPHA_STATE_{k}PP" for k in (0,3,5)]
    rows=[]
    for _,r in x.iterrows():
        ar=base.action_returns(r,5); mkt=ar["MARKET"]
        pols={"MARKET":"MARKET","EW4":"EW4","WPLUS":"WPLUS","POSABS":"POSABS","LEADER":"LEADER","LEADER_OR_ROTATE":"LEADER_OR_ROTATE",
              "ABS_UNCOND":uc.get((r.universe,"ABS_UNCOND"),"CASH"),"ALPHA_UNCOND":uc.get((r.universe,"ALPHA_UNCOND"),"EW4")}
        for p in policy_names:
            pols[p]=c.get((r.universe,r.state_cell,p),pols["ABS_UNCOND"] if p.startswith("ABS") else pols["ALPHA_UNCOND"])
        for pol,a in pols.items():
            ret=0.0 if a=="CASH" else ar[a]
            rows.append({"date":r.date,"universe":r.universe,"period":r.period,"state_cell":r.state_cell,"base_state":r.base_state,"factor_substate":r.factor_substate,
                         "policy":pol,"action":a,"ret":ret,"mkt_ret":mkt,"excess":ret-mkt,"active":a!="CASH",
                         "ret_net10":ret-(.001 if a!="CASH" else 0),"ret_net30":ret-(.003 if a!="CASH" else 0)})
    path=pd.DataFrame(rows).sort_values(["universe","policy","date"])
    stats=[]
    for (u,pdname,pol),g in path.groupby(["universe","period","policy"]):
        g=g.sort_values("date"); rr=g.ret.dropna(); active=g[g.active]
        if len(rr)<5: continue
        eq=(1+rr).cumprod(); mdd=(eq/eq.cummax()-1).min(); years=max((g.date.max()-g.date.min()).days/365.25,len(rr)*5/252)
        cagr=eq.iloc[-1]**(1/years)-1 if eq.iloc[-1]>0 else np.nan
        stats.append({"universe":u,"period":pdname,"policy":pol,"n":len(rr),"participation":g.active.mean(),"positive_rate_all":(rr>0).mean(),
                      "active_win_rate":(active.ret>0).mean() if len(active) else np.nan,"mean_5d":rr.mean(),"median_5d":rr.median(),
                      "beat_mkt_rate":(g.excess>0).mean(),"mean_excess":g.excess.mean(),"cagr_gross":cagr,"mdd_gross":mdd,
                      "vol_ann":rr.std()*np.sqrt(252/5),"sharpe_gross":rr.mean()/rr.std()*np.sqrt(252/5) if rr.std()>0 else np.nan,
                      "worst_5d":rr.min(),"action_switch_rate":(g.action!=g.action.shift()).mean(),
                      "compound_net10":(1+g.ret_net10).prod()-1,"compound_net30":(1+g.ret_net30).prod()-1})
    return path,pd.DataFrame(stats)


def write_summary(stats,choices,uncond):
    lines=["# Regime-Conditioned Investment Action Research v2","",
           "Unconditional selection is now computed from raw TRAIN observations (not an unweighted average of state summaries). Cash periods are reported through participation plus active-only win rate.",
           "State policies are regularized: 0/3/5PP means state-specific action is used only when its TRAIN win-rate (ABS) or beat-market-rate (ALPHA) advantage over the unconditional action is at least that threshold.","",
           "## 2023-2024 frozen-policy comparison","" ]
    v=stats[stats.period=="VALID_2023_2024"]
    show=["MARKET","EW4","WPLUS","ABS_UNCOND","ABS_STATE_0PP","ABS_STATE_3PP","ABS_STATE_5PP","ALPHA_UNCOND","ALPHA_STATE_0PP","ALPHA_STATE_3PP","ALPHA_STATE_5PP"]
    for u,g in v.groupby("universe"):
        lines.append(f"### {u}")
        for pol in show:
            z=g[g.policy==pol]
            if z.empty: continue
            r=z.iloc[0]
            lines.append(f"- {pol}: participation {r.participation:.0%}, active win {r.active_win_rate:.0%}, mean5 {r.mean_5d:+.2%}, beat-mkt {r.beat_mkt_rate:.0%}, excess {r.mean_excess:+.2%}, CAGR {r.cagr_gross:+.1%}, MDD {r.mdd_gross:+.1%}")
    lines += ["","## 2025 stress","" ]
    v=stats[stats.period=="STRESS_2025"]
    for u,g in v.groupby("universe"):
        lines.append(f"### {u}")
        for pol in ["MARKET","WPLUS","ABS_UNCOND","ABS_STATE_3PP","ALPHA_UNCOND","ALPHA_STATE_3PP"]:
            z=g[g.policy==pol]
            if z.empty: continue
            r=z.iloc[0]
            lines.append(f"- {pol}: participation {r.participation:.0%}, active win {r.active_win_rate:.0%}, mean5 {r.mean_5d:+.2%}, excess {r.mean_excess:+.2%}, CAGR {r.cagr_gross:+.1%}, MDD {r.mdd_gross:+.1%}")
    lines += ["","## TRAIN-frozen unconditional actions","" ]
    for _,r in uncond.iterrows(): lines.append(f"- {r.universe} {r.policy}: {r.action}")
    lines += ["","## Decision criterion","",
              "- Regime conditioning earns promotion only where a regularized state policy improves 2023-2024 versus its unconditional control and does not catastrophically reverse in 2025.",
              "- WPLUS and EW4 remain important simple controls: a complicated regime policy is not useful if it cannot beat them.",
              "- Exact constituent turnover is still unavailable; net10/net30 are blunt every-rebalance stresses, not implementation-grade costs.",""]
    return "\n".join(lines)+"\n"


def main():
    x=base.load_panel(); long=base.make_long(x); action_summary=base.summarize_actions(long)
    choices,uncond=choose(long); path,stats=backtest(x,choices,uncond)
    x.to_csv(base.OUT/"action_state_panel.csv",index=False); long.to_csv(base.OUT/"action_returns_long.csv",index=False)
    action_summary.to_csv(base.OUT/"state_action_matrix.csv",index=False); choices.to_csv(base.OUT/"frozen_state_action_choices_v2.csv",index=False)
    uncond.to_csv(base.OUT/"unconditional_action_choices_v2.csv",index=False); path.to_csv(base.OUT/"policy_path_5d_v2.csv",index=False); stats.to_csv(base.OUT/"policy_performance_v2.csv",index=False)
    (base.OUT/"RESEARCH_SUMMARY_V2.md").write_text(write_summary(stats,choices,uncond),encoding="utf-8")
    print(f"panel={len(x):,}; choices={len(choices):,}; stats={len(stats):,}")

if __name__=="__main__": main()
