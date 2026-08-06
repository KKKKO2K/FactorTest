from __future__ import annotations

import importlib.util
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_off_engine_results"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("idx", HERE / "index_core_satellite_test.py")
idx = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(idx)

enh = idx.enh
START, SPLIT, END, STEP = idx.START, idx.SPLIT, idx.END, idx.STEP
INDEX_ASSET = idx.INDEX_ASSET
COSTS = (30, 60, 100)


def rank01(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").rank(pct=True, method="average")


def benchmark_weights(g0: pd.DataFrame, basic: pd.DataFrame) -> pd.Series:
    codes = g0.index.get_level_values("code")
    mcap = pd.to_numeric(basic.reindex(codes)["mcap"], errors="coerce").clip(lower=0.0)
    return enh.cap_weights(mcap, max_abs=1.0)


def satellite(benchmark: pd.Series, score: pd.Series, kappa: float, top_n: int, cap: float) -> pd.Series:
    s = rank01(score.reindex(benchmark.index)).dropna()
    if s.empty:
        return benchmark.copy()
    keep = s.nlargest(min(top_n, len(s))).index
    raw = benchmark.reindex(keep).fillna(0.0) * np.exp(kappa * (2.0 * s.reindex(keep) - 1.0))
    return enh.cap_weights(raw, max_abs=cap)


def mix(index_weight: float, sat: pd.Series) -> pd.Series:
    out = sat * (1.0 - index_weight)
    out.loc[INDEX_ASSET] = index_weight
    return out[out > 1e-12]


def candidate_scores(g0: pd.DataFrame, z: pd.DataFrame) -> dict[str, pd.Series]:
    codes = g0.index.get_level_values("code")
    g = g0.copy(); g.index = codes
    z = z.reindex(codes)
    low_vol = 1.0 - g["vol20_rank"]
    scores = {
        "VALUE_REV": 0.35*g["VALUE"] + 0.25*g["REVISION"] + 0.25*g["VALUE_UNLOCK"] + 0.15*g["PRIVATE"],
        "REV_BREADTH": 0.30*g["REVISION"] + 0.30*g["EARNINGS_BREADTH"] + 0.20*g["LONG_MOM"] + 0.20*g["PRIVATE"],
        "ABSORPTION": 0.35*g["OWNERSHIP_TRANSFER"] + 0.25*g["SHORT_REVERSAL"] + 0.20*g["VALUE_UNLOCK"] + 0.20*low_vol,
        "LOWVOL_VALUE": 0.35*low_vol + 0.30*g["VALUE"] + 0.20*g["REVISION"] + 0.15*g["SHORT_REVERSAL"],
        "QUALITY_TREND": 0.30*g["REVISION"] + 0.25*g["EARNINGS_BREADTH"] + 0.25*g["LONG_MOM"] + 0.20*low_vol,
        "QUIET_ACCUM": 0.35*g["NEGLECTED_VALUE"] + 0.25*g["PRIVATE"] + 0.20*g["quiet_price"] + 0.20*g["VALUE"],
        "CONTRARIAN": 0.35*g["VALUE"] + 0.30*g["SHORT_REVERSAL"] + 0.20*g["PRIVATE"] + 0.15*g["REVISION"],
        "BALANCED": 0.22*g["VALUE"] + 0.22*g["REVISION"] + 0.18*g["PRIVATE"] + 0.16*g["SHORT_REVERSAL"] + 0.12*low_vol + 0.10*z["HYBRID_ROTATION"],
        "EVENT_META": 0.55*z["EVENT_PLUS_META"] + 0.25*g["VALUE_UNLOCK"] + 0.20*low_vol,
    }
    return {k: rank01(v) for k, v in scores.items()}


def targets_for_date(g0: pd.DataFrame, z: pd.DataFrame, basic: pd.DataFrame) -> dict[str, pd.Series]:
    benchmark = benchmark_weights(g0, basic)
    scores = candidate_scores(g0, z)
    out = {"INDEX_ONLY": pd.Series({INDEX_ASSET: 1.0})}
    for name, score in scores.items():
        top_n = 30 if name in {"LOWVOL_VALUE", "VALUE_REV", "BALANCED"} else 20
        cap = 0.25 if name in {"LOWVOL_VALUE", "BALANCED"} else 0.35
        kappa = 1.8 if name in {"LOWVOL_VALUE", "BALANCED"} else 2.2
        sat = satellite(benchmark, score, kappa=kappa, top_n=top_n, cap=cap)
        for active in (30, 50, 70):
            out[f"{name}_{active}"] = mix(1.0-active/100.0, sat)
    # Existing transparent satellites retained as controls.
    stock_targets = enh.strategy_targets(pd.Timestamp(g0.index.get_level_values("date")[0]), g0, z, basic)
    sats = idx.recover_satellites(stock_targets)
    out["PYRAMID_50"] = mix(0.50, sats["PYRAMID"])
    out["EVENT_30"] = mix(0.70, sats["EVENT"])
    out["MODERATE_50"] = mix(0.50, sats["MODERATE"])
    out["LEADER5_80"] = mix(0.20, sats["LEADER5"])
    out["LEADER5_100"] = mix(0.00, sats["LEADER5"])
    return out


def run_all(panel, scores, returns, basic_panels, k200_period, cost_bps):
    fwd10 = enh.lab.forward_return(returns, STEP)
    current_end: dict[str, pd.Series] = {}
    rows, weight_rows = [], []
    for dt, g0 in panel.groupby(level="date"):
        if dt not in scores or dt not in fwd10.index or dt not in k200_period.index or pd.isna(k200_period.loc[dt]):
            continue
        codes = g0.index.get_level_values("code")
        stock_future = fwd10.loc[dt].reindex(codes).fillna(0.0)
        asset_returns = stock_future.copy(); asset_returns.loc[INDEX_ASSET] = float(k200_period.loc[dt])
        targets = targets_for_date(g0, scores[dt], basic_panels[dt])
        state = str(g0["state"].iloc[0])
        for strategy, new_w in targets.items():
            old = current_end.get(strategy, pd.Series(dtype=float))
            turn = idx.turnover(old, new_w)
            r = asset_returns.reindex(new_w.index).fillna(0.0)
            gross = float((new_w*r).sum())
            net = gross - turn*cost_bps/10000.0
            denom = 1.0 + gross
            end_w = new_w*(1.0+r)/denom if denom > 0 else new_w.copy()
            current_end[strategy] = end_w[end_w.abs() > 1e-12]
            rows.append({
                "date":dt,"strategy":strategy,"cost_bps":cost_bps,"state":state,
                "gross":gross,"net":net,"k200_return":float(k200_period.loc[dt]),
                "active_return":net-float(k200_period.loc[dt]),"turnover":turn,
                "index_weight":float(new_w.get(INDEX_ASSET,0.0)),
                "stock_weight":float(new_w.drop(INDEX_ASSET,errors="ignore").sum()),
            })
            for asset, weight in new_w.items():
                weight_rows.append({"date":dt,"strategy":strategy,"cost_bps":cost_bps,"asset":asset,"weight":float(weight),"state":state})
    return pd.DataFrame(rows), pd.DataFrame(weight_rows)


def trailing_compound(x: pd.Series, n: int) -> pd.Series:
    return (1.0+x).rolling(n,min_periods=n).apply(np.prod,raw=True).sub(1.0).shift(1)


def year_floor_on(detail60: pd.DataFrame) -> pd.Series:
    p = detail60.pivot(index="date",columns="strategy",values="net").sort_index()
    b = detail60[detail60.strategy=="INDEX_ONLY"].set_index("date")["k200_return"].sort_index()
    state = detail60[detail60.strategy=="INDEX_ONLY"].set_index("date")["state"].sort_index()
    leader = p["LEADER5_80"]
    rel = (1.0+leader)/(1.0+b)-1.0
    trail9 = trailing_compound(rel,9)
    bench3 = trailing_compound(b,3)
    rel_wealth = (1.0+leader).cumprod()/(1.0+b).cumprod()
    dd12 = rel_wealth.shift(1)/rel_wealth.shift(1).rolling(12,min_periods=12).max()-1.0
    return state.isin({"BROAD_RISK_ON","NARROW_RISK_ON","RISK_OFF"}) & (trail9>0.05) & (bench3>0.0) & (dd12>-0.10)


def perf(returns: pd.Series, benchmark: pd.Series) -> dict[str,float]:
    x = pd.concat([returns.rename("r"),benchmark.rename("b")],axis=1).dropna()
    if len(x)<10: return {}
    periods=252/STEP; years=len(x)/periods
    active=(1+x.r)/(1+x.b)-1
    sw=(1+x.r).cumprod(); bw=(1+x.b).cumprod(); rw=sw/bw
    annual=[]
    for _,g in x.groupby(x.index.year): annual.append(float((1+g.r).prod()/(1+g.b).prod()-1))
    roll=(1+active).rolling(25,min_periods=25).apply(np.prod,raw=True).sub(1)
    return {
        "n":len(x),"strategy_cagr":float(sw.iloc[-1]**(1/years)-1),"k200_cagr":float(bw.iloc[-1]**(1/years)-1),
        "relative_cagr":float(rw.iloc[-1]**(1/years)-1),
        "information_ratio":float(active.mean()/active.std(ddof=1)*math.sqrt(periods)) if active.std(ddof=1)>0 else np.nan,
        "relative_mdd":float((rw/rw.cummax()-1).min()),"worst_calendar_year":min(annual),
        "worst_rolling_12m":float(roll.min()),"positive_periods":float((active>0).mean()),
    }


def off_metrics(detail60: pd.DataFrame, on: pd.Series) -> pd.DataFrame:
    pivot=detail60.pivot(index="date",columns="strategy",values="net").sort_index()
    b=detail60[detail60.strategy=="INDEX_ONLY"].set_index("date")["k200_return"].sort_index()
    rows=[]
    for strategy in pivot.columns:
        for sample,mask in (("train",(pivot.index<SPLIT)&(~on.reindex(pivot.index,fill_value=False))),
                            ("test",(pivot.index>=SPLIT)&(~on.reindex(pivot.index,fill_value=False)))):
            m=perf(pivot.loc[mask,strategy],b.loc[mask]);
            if m: rows.append({"strategy":strategy,"sample":sample,**m})
    return pd.DataFrame(rows)


def choose_train_robust(off: pd.DataFrame) -> list[str]:
    t=off[off.sample=="train"].copy()
    t=t[(t.strategy!="INDEX_ONLY")&(t.n>=40)]
    t["score"]=t.relative_cagr+0.25*t.information_ratio+0.50*np.minimum(t.worst_calendar_year+0.03,0)-0.25*np.maximum(-t.relative_mdd-0.12,0)
    return t.sort_values("score",ascending=False).head(8).strategy.tolist()


def make_routers(detail60: pd.DataFrame,on:pd.Series,candidates:list[str]) -> pd.DataFrame:
    p=detail60.pivot(index="date",columns="strategy",values="net").sort_index()
    gross=detail60.pivot(index="date",columns="strategy",values="gross").sort_index()
    turn=detail60.pivot(index="date",columns="strategy",values="turnover").sort_index()
    b=detail60[detail60.strategy=="INDEX_ONLY"].set_index("date")["k200_return"].sort_index()
    state=detail60[detail60.strategy=="INDEX_ONLY"].set_index("date")["state"].sort_index()
    active=(1+p[candidates]).div(1+b,axis=0)-1
    trail6=(1+active).rolling(6,min_periods=6).apply(np.prod,raw=True).sub(1).shift(1)
    trail12=(1+active).rolling(12,min_periods=12).apply(np.prod,raw=True).sub(1).shift(1)
    # Frozen train mapping by observable market state, OFF dates only.
    train_mask=(p.index<SPLIT)&(~on.reindex(p.index,fill_value=False))
    state_map={}
    for st in state.unique():
        m=train_mask&(state==st)
        if m.sum()<8: continue
        stats={c:active.loc[m,c].mean()/active.loc[m,c].std(ddof=1) if active.loc[m,c].std(ddof=1)>0 else -np.inf for c in candidates}
        state_map[st]=max(stats,key=stats.get)
    rows=[]
    for dt in p.index:
        if on.get(dt,False):
            choice="LEADER5_80"; router="ON_LEADER_OFF_STATE"
            rows.append((dt,router,choice)); rows.append((dt,"ON_LEADER_OFF_TRAILING","LEADER5_80")); rows.append((dt,"ON_LEADER_OFF_DUAL","LEADER5_80"));
            continue
        choice_state=state_map.get(state.loc[dt],"INDEX_ONLY")
        rows.append((dt,"ON_LEADER_OFF_STATE",choice_state))
        s6=trail6.loc[dt].dropna(); choice6=str(s6.idxmax()) if not s6.empty and s6.max()>0 else "INDEX_ONLY"
        rows.append((dt,"ON_LEADER_OFF_TRAILING",choice6))
        both=pd.concat([trail6.loc[dt],trail12.loc[dt]],axis=1).dropna(); both=both[(both.iloc[:,0]>0)&(both.iloc[:,1]>0)]
        choice_dual=str((both.iloc[:,0]+both.iloc[:,1]).idxmax()) if not both.empty else "INDEX_ONLY"
        rows.append((dt,"ON_LEADER_OFF_DUAL",choice_dual))
    choices=pd.DataFrame(rows,columns=["date","router","choice"])
    out=[]
    for router,g in choices.groupby("router"):
        g=g.set_index("date").sort_index(); rets=[]
        prev=None
        for dt,choice in g.choice.items():
            r=float(p.at[dt,choice])
            # Add a conservative switch surcharge beyond each component's own turnover.
            if prev is not None and choice!=prev: r-=0.003
            rets.append(r); prev=choice
        s=pd.Series(rets,index=g.index)
        for sample,mask in (("train",s.index<SPLIT),("test",s.index>=SPLIT)):
            m=perf(s.loc[mask],b.loc[mask]); out.append({"strategy":router,"sample":sample,**m})
        g.assign(return_=s.values).reset_index().to_csv(OUT/f"{router.lower()}_history.csv",index=False,encoding="utf-8-sig")
    return pd.DataFrame(out)


def main():
    returns,basic_panels=enh.base.load_basic(); returns=returns.loc[:END]
    panel=enh.lab.build_panel("K200",returns,basic_panels)
    fwd20=enh.lab.forward_return(returns,enh.lab.HORIZON)
    ic=enh.lab.ic_detail(panel,fwd20,"K200")
    static,mapping,_=enh.lab.factor_maps(ic,"K200")
    scores,_=enh.lab.score_history(panel,ic,"K200",static,mapping)
    dates=sorted(panel.index.get_level_values("date").unique())
    close=enh.download_kospi200(); k200=enh.forward_index_returns(close,dates,STEP)
    details=[]; weights=[]
    for cost in COSTS:
        d,w=run_all(panel,scores,returns,basic_panels,k200,cost); details.append(d); weights.append(w)
    detail=pd.concat(details,ignore_index=True); weight=pd.concat(weights,ignore_index=True)
    detail.to_csv(OUT/"candidate_period_returns.csv",index=False,encoding="utf-8-sig")
    weight.to_csv(OUT/"candidate_target_weights.csv",index=False,encoding="utf-8-sig")
    d60=detail[detail.cost_bps==60].copy(); on=year_floor_on(d60)
    on.rename("on_signal").to_csv(OUT/"concentration_on_signal.csv",encoding="utf-8-sig")
    off=off_metrics(d60,on); off.to_csv(OUT/"off_engine_metrics.csv",index=False,encoding="utf-8-sig")
    candidates=choose_train_robust(off)
    pd.Series(candidates,name="candidate").to_csv(OUT/"train_robust_candidates.csv",index=False,encoding="utf-8-sig")
    routers=make_routers(d60,on,candidates); routers.to_csv(OUT/"router_metrics.csv",index=False,encoding="utf-8-sig")
    paired=off.pivot(index="strategy",columns="sample",values=["relative_cagr","information_ratio","relative_mdd","worst_calendar_year","worst_rolling_12m"]).reset_index()
    paired.columns=["strategy"]+[f"{a}_{b}" for a,b in paired.columns[1:]]
    paired.to_csv(OUT/"off_engine_train_test_comparison.csv",index=False,encoding="utf-8-sig")
    print("ROBUST CANDIDATES",candidates)
    print(paired.sort_values("relative_cagr_test",ascending=False).head(20).to_string(index=False))
    print("ROUTERS")
    print(routers.to_string(index=False))

if __name__=="__main__":
    main()
