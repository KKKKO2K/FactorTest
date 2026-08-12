from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ASSIGN = ROOT / "research/factor_regime_contemporaneous_states/results/nested_state_assignments.csv"
PRIM = ROOT / "research/factor_regime_full_state_map/results/family_primitives.csv"
FSTATE = ROOT / "research/factor_regime_full_state_map/results/family_states_static.csv"
OUT = ROOT / "research/factor_regime_action_policy/results"
OUT.mkdir(parents=True, exist_ok=True)

DYNAMIC_ACTIONS = ["MARKET", "EW4", "WPLUS", "POSABS", "LEADER", "LEADER_OR_ROTATE"]
ALPHA_ACTIONS = ["EW4", "WPLUS", "POSABS", "LEADER", "LEADER_OR_ROTATE"]
FAMILIES = ["MOMENTUM", "REVISION", "VALUE", "FLOW"]


def period_of(d: pd.Timestamp) -> str:
    y = d.year
    if y <= 2022: return "TRAIN_2016_2022"
    if y <= 2024: return "VALID_2023_2024"
    if y == 2025: return "STRESS_2025"
    return "STRESS_2026"


def load_panel() -> pd.DataFrame:
    s = pd.read_csv(ASSIGN)
    p = pd.read_csv(PRIM)
    fs = pd.read_csv(FSTATE)
    for x in (s, p, fs): x["date"] = pd.to_datetime(x["date"])
    fs = fs[fs["cut_name"].eq("Q33")].copy()
    if fs.empty:
        raise RuntimeError("Q33 family states missing")
    keep_s = ["date","universe","base_state","factor_substate","MKT_FWD_5D","MKT_FWD_20D","LEADER_FAMILY","LEADER_STATE"]
    s = s[keep_s].drop_duplicates(["date","universe"])
    p = p.merge(fs[["date","universe","family","state6"]], on=["date","universe","family"], how="left")
    rows=[]
    for (dt,u), g in p.groupby(["date","universe"], sort=False):
        if g["family"].nunique() < 4: continue
        rec={"date":dt,"universe":u}
        for _, r in g.iterrows():
            fam=r["family"]
            rec[f"{fam}_state"] = r["state6"]
            rec[f"{fam}_top20"] = r["top_20d"]
            rec[f"{fam}_fwd5"] = r["top_fwd_5d"]
            rec[f"{fam}_fwd20"] = r["top_fwd_20d"]
        rows.append(rec)
    w=pd.DataFrame(rows)
    x=s.merge(w,on=["date","universe"],how="inner")
    x["period"] = x["date"].map(period_of)
    x["state_cell"] = x["base_state"].astype(str)+"|"+x["factor_substate"].astype(str)
    return x.sort_values(["universe","date"]).reset_index(drop=True)


def fam_ret(r, fam, h): return float(r[f"{fam}_fwd{h}"])


def action_returns(r: pd.Series, h: int) -> dict[str,float]:
    vals={f:fam_ret(r,f,h) for f in FAMILIES}
    states={f:r.get(f"{f}_state",np.nan) for f in FAMILIES}
    top20={f:r.get(f"{f}_top20",np.nan) for f in FAMILIES}
    ew=float(np.nanmean(list(vals.values())))
    wplus=[f for f in FAMILIES if states[f]=="W+"]
    posabs=[f for f in FAMILIES if pd.notna(top20[f]) and top20[f]>0]
    leader=r.get("LEADER_FAMILY",np.nan)
    leader_ret=vals.get(leader, ew)
    wplus_ret=float(np.nanmean([vals[f] for f in wplus])) if wplus else ew
    posabs_ret=float(np.nanmean([vals[f] for f in posabs])) if posabs else ew
    rotate_ret=leader_ret
    if r.get("LEADER_STATE",np.nan)=="R-":
        alts=[f for f in wplus if f!=leader]
        if alts: rotate_ret=float(np.nanmean([vals[f] for f in alts]))
    out={
        "MARKET": float(r[f"MKT_FWD_{h}D"]),
        "EW4": ew,
        "WPLUS": wplus_ret,
        "POSABS": posabs_ret,
        "LEADER": leader_ret,
        "LEADER_OR_ROTATE": rotate_ret,
    }
    out.update(vals)
    return out


def make_long(x: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for _,r in x.iterrows():
        for h in (5,20):
            ar=action_returns(r,h)
            mkt=ar["MARKET"]
            for a,v in ar.items():
                rows.append({"date":r.date,"universe":r.universe,"period":r.period,"base_state":r.base_state,
                             "factor_substate":r.factor_substate,"state_cell":r.state_cell,"horizon":h,
                             "action":a,"ret":v,"mkt_ret":mkt,"excess":v-mkt})
    return pd.DataFrame(rows)


def summarize_actions(long: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    keys=["universe","period","base_state","factor_substate","state_cell","horizon","action"]
    for key,g in long.groupby(keys):
        r=g["ret"].dropna(); ex=g.loc[r.index,"excess"]
        if len(r)<5: continue
        rows.append({**dict(zip(keys,key)),"n":len(r),"mean":r.mean(),"median":r.median(),"win_rate":(r>0).mean(),
                     "beat_mkt_rate":(ex>0).mean(),"mean_excess":ex.mean(),"p10":r.quantile(.10),
                     "avg_loss":r[r<0].mean() if (r<0).any() else 0.0})
    return pd.DataFrame(rows)


def choose_actions(action_summary: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    tr=action_summary[(action_summary.period=="TRAIN_2016_2022") & (action_summary.horizon==5)].copy()
    choice=[]; uncond=[]
    for u,g0 in tr.groupby("universe"):
        # unconditional fallbacks
        q=g0[g0.action.isin(DYNAMIC_ACTIONS)].groupby("action",as_index=False).agg(n=("n","sum"), win_rate=("win_rate","mean"), mean=("mean","mean"), beat_mkt_rate=("beat_mkt_rate","mean"), mean_excess=("mean_excess","mean"))
        q=q.sort_values(["win_rate","mean","beat_mkt_rate"],ascending=False)
        abs_u=q.iloc[0]
        qa=q[q.action.isin(ALPHA_ACTIONS)].sort_values(["beat_mkt_rate","mean_excess","mean"],ascending=False)
        alpha_u=qa.iloc[0]
        uncond += [
            {"universe":u,"policy":"ABS_UNCOND","action":abs_u.action,"train_win":abs_u.win_rate,"train_mean":abs_u["mean"]},
            {"universe":u,"policy":"ALPHA_UNCOND","action":alpha_u.action,"train_beat":alpha_u.beat_mkt_rate,"train_excess":alpha_u.mean_excess},
        ]
        for cell,g in g0.groupby("state_cell"):
            base,fsub=cell.split("|")
            z=g[(g.action.isin(DYNAMIC_ACTIONS)) & (g.n>=20)].copy()
            if z.empty:
                abs_a=abs_u.action; abs_win=abs_u.win_rate; abs_mean=abs_u["mean"]
            else:
                best=z.sort_values(["win_rate","mean","beat_mkt_rate"],ascending=False).iloc[0]
                abs_a=best.action; abs_win=best.win_rate; abs_mean=best["mean"]
            if abs_win<=0.50 or abs_mean<=0:
                abs_a="CASH"
            za=g[(g.action.isin(ALPHA_ACTIONS)) & (g.n>=20)].copy()
            if za.empty:
                alpha_a=alpha_u.action
            else:
                alpha_a=za.sort_values(["beat_mkt_rate","mean_excess","mean"],ascending=False).iloc[0].action
            choice += [
                {"universe":u,"state_cell":cell,"base_state":base,"factor_substate":fsub,"policy":"ABS_STATE","action":abs_a,"train_score":abs_win},
                {"universe":u,"state_cell":cell,"base_state":base,"factor_substate":fsub,"policy":"ALPHA_STATE","action":alpha_a,"train_score":np.nan},
            ]
    return pd.DataFrame(choice), pd.DataFrame(uncond)


def backtest(x: pd.DataFrame, choices: pd.DataFrame, uncond: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    c={(r.universe,r.state_cell,r.policy):r.action for _,r in choices.iterrows()}
    u={(r.universe,r.policy):r.action for _,r in uncond.iterrows()}
    rows=[]
    for _,r in x.iterrows():
        ar=action_returns(r,5); mkt=ar["MARKET"]
        policies={
            "MARKET":"MARKET","EW4":"EW4","WPLUS":"WPLUS","LEADER":"LEADER","LEADER_OR_ROTATE":"LEADER_OR_ROTATE",
            "ABS_STATE":c.get((r.universe,r.state_cell,"ABS_STATE"),"CASH"),
            "ALPHA_STATE":c.get((r.universe,r.state_cell,"ALPHA_STATE"),"EW4"),
            "ABS_UNCOND":u.get((r.universe,"ABS_UNCOND"),"EW4"),
            "ALPHA_UNCOND":u.get((r.universe,"ALPHA_UNCOND"),"EW4"),
        }
        for pol,a in policies.items():
            ret=0.0 if a=="CASH" else ar[a]
            rows.append({"date":r.date,"universe":r.universe,"period":r.period,"state_cell":r.state_cell,
                         "base_state":r.base_state,"factor_substate":r.factor_substate,"policy":pol,"action":a,
                         "ret":ret,"mkt_ret":mkt,"excess":ret-mkt,
                         "ret_net10":ret-(0.001 if a!="CASH" else 0.0),
                         "ret_net30":ret-(0.003 if a!="CASH" else 0.0)})
    path=pd.DataFrame(rows).sort_values(["universe","policy","date"])
    stats=[]
    for (univ,period,pol),g in path.groupby(["universe","period","policy"]):
        g=g.sort_values("date"); rr=g.ret.dropna()
        if len(rr)<5: continue
        eq=(1+rr).cumprod(); peak=eq.cummax(); mdd=(eq/peak-1).min()
        years=max((g.date.max()-g.date.min()).days/365.25, len(rr)*5/252)
        cagr=eq.iloc[-1]**(1/years)-1 if years>0 and eq.iloc[-1]>0 else np.nan
        vol=rr.std(ddof=1)*np.sqrt(252/5)
        sharpe=rr.mean()/rr.std(ddof=1)*np.sqrt(252/5) if rr.std(ddof=1)>0 else np.nan
        action_switch=(g.action!=g.action.shift()).mean()
        stats.append({"universe":univ,"period":period,"policy":pol,"n":len(rr),"win_rate":(rr>0).mean(),"mean_5d":rr.mean(),
                      "median_5d":rr.median(),"beat_mkt_rate":(g.excess>0).mean(),"mean_excess":g.excess.mean(),
                      "cagr_gross":cagr,"vol_ann":vol,"sharpe_gross":sharpe,"mdd_gross":mdd,"worst_5d":rr.min(),
                      "action_switch_rate":action_switch,
                      "compound_net10":(1+g.ret_net10).prod()-1,"compound_net30":(1+g.ret_net30).prod()-1})
    return path,pd.DataFrame(stats)


def state_policy_diagnostics(path: pd.DataFrame) -> pd.DataFrame:
    q=path[path.policy.isin(["ABS_STATE","ALPHA_STATE"])].copy()
    return q.groupby(["universe","period","base_state","factor_substate","policy","action"],as_index=False).agg(
        n=("ret","size"), win_rate=("ret",lambda s:(s>0).mean()), mean_5d=("ret","mean"),
        beat_mkt_rate=("excess",lambda s:(s>0).mean()), mean_excess=("excess","mean"))


def write_summary(stats: pd.DataFrame, choices: pd.DataFrame, diag: pd.DataFrame, action_summary: pd.DataFrame) -> str:
    lines=["# Regime-Conditioned Investment Action Research","",
           "Goal: identify what to hold, not merely name the regime. State definitions are contemporaneous and fixed before future returns are attached.",
           "Weekly/non-overlap-style 5D forward returns are used for executable policy backtests; 20D is descriptive only. Policies are selected on 2016-2022 and frozen for 2023 onward.","",
           "## Policy definitions","",
           "- ABS_STATE: within each BASE x factor-health state, choose the TRAIN action with the highest positive-5D probability; go to cash if TRAIN win rate <=50% or mean <=0.",
           "- ALPHA_STATE: within each state, choose the TRAIN factor action with the highest probability of beating the same-universe market.",
           "- ABS_UNCOND / ALPHA_UNCOND: same selection without regime conditioning; these are the key controls.",
           "- Dynamic actions: MARKET, equal-weight four family top portfolios (EW4), W+ family basket, positive-absolute family basket, current leader, and leader-or-rotate when leader is R- and an alternative W+ exists.","",
           "## 2023-2024 frozen-policy results","" ]
    v=stats[stats.period.eq("VALID_2023_2024")]
    for u,g in v.groupby("universe"):
        lines.append(f"### {u}")
        for pol in ["MARKET","EW4","WPLUS","LEADER","LEADER_OR_ROTATE","ABS_UNCOND","ABS_STATE","ALPHA_UNCOND","ALPHA_STATE"]:
            z=g[g.policy.eq(pol)]
            if z.empty: continue
            r=z.iloc[0]
            lines.append(f"- {pol}: win {r.win_rate:.0%}, mean5 {r.mean_5d:+.2%}, beat-mkt {r.beat_mkt_rate:.0%}, excess {r.mean_excess:+.2%}, CAGR {r.cagr_gross:+.1%}, MDD {r.mdd_gross:+.1%}")
    lines += ["","## 2025 stress","" ]
    v=stats[stats.period.eq("STRESS_2025")]
    for u,g in v.groupby("universe"):
        lines.append(f"### {u}")
        for pol in ["MARKET","ABS_UNCOND","ABS_STATE","ALPHA_UNCOND","ALPHA_STATE"]:
            z=g[g.policy.eq(pol)]
            if z.empty: continue
            r=z.iloc[0]
            lines.append(f"- {pol}: win {r.win_rate:.0%}, mean5 {r.mean_5d:+.2%}, beat-mkt {r.beat_mkt_rate:.0%}, excess {r.mean_excess:+.2%}, CAGR {r.cagr_gross:+.1%}, MDD {r.mdd_gross:+.1%}")
    lines += ["","## Frozen state -> action map","" ]
    for u,g in choices.groupby("universe"):
        lines.append(f"### {u}")
        for _,r in g.sort_values(["state_cell","policy"]).iterrows():
            lines.append(f"- {r.state_cell} {r.policy}: {r.action}")
    lines += ["","## Guardrails","",
              "- Gross factor-family top-portfolio returns do not contain exact constituent-level implementation costs. net10/net30 outputs subtract 10/30bp every active 5D rebalance as blunt stress tests, not precise cost estimates.",
              "- Choosing among several actions within a state creates model-selection risk. The decisive comparison is state-conditioned policy vs its unconditional counterpart in 2023-2024 and 2025, not the best individual cell.",
              "- 20D observations overlap and are descriptive. Policy performance is evaluated on 5D forward blocks.",
              "- 2023+ has informed the broader research design, so it is post-discovery validation rather than pristine OOS.",""]
    return "\n".join(lines)+"\n"


def main():
    x=load_panel(); long=make_long(x); summary=summarize_actions(long)
    choices,uncond=choose_actions(summary)
    path,stats=backtest(x,choices,uncond)
    diag=state_policy_diagnostics(path)
    x.to_csv(OUT/"action_state_panel.csv",index=False)
    long.to_csv(OUT/"action_returns_long.csv",index=False)
    summary.to_csv(OUT/"state_action_matrix.csv",index=False)
    choices.to_csv(OUT/"frozen_state_action_choices.csv",index=False)
    uncond.to_csv(OUT/"unconditional_action_choices.csv",index=False)
    path.to_csv(OUT/"policy_path_5d.csv",index=False)
    stats.to_csv(OUT/"policy_performance.csv",index=False)
    diag.to_csv(OUT/"state_policy_diagnostics.csv",index=False)
    (OUT/"RESEARCH_SUMMARY.md").write_text(write_summary(stats,choices,diag,summary),encoding="utf-8")
    print(f"panel={len(x):,} long={len(long):,} policy rows={len(path):,}")

if __name__=="__main__": main()
