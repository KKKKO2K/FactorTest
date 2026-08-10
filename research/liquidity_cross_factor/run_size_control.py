from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import run_cross_factor_liquidity as base

OUT = Path(__file__).resolve().parent / "results"


def residual_trading_rank(ta: pd.Series, mcap: pd.Series) -> pd.Series:
    pair = pd.concat([ta.rename("ta"), mcap.rename("mcap")], axis=1).dropna()
    pair = pair[(pair.ta > 0) & (pair.mcap > 0)]
    out = pd.Series(index=ta.index, dtype=float)
    if len(pair) < 50:
        return out
    x = np.log(pair.mcap.to_numpy(float))
    y = np.log(pair.ta.to_numpy(float))
    slope, intercept = np.polyfit(x, y, 1)
    resid = y - (slope * x + intercept)
    r = pd.Series(resid, index=pair.index).rank(pct=True, method="average")
    out.loc[r.index] = r
    return out


def main() -> None:
    returns, mcap, k200_by_date = base.load_basic()
    ta = base.load_trading_amount().reindex(index=mcap.index, columns=mcap.columns)
    fwd = base.forward_returns(returns, base.HORIZON)
    common_dates = sorted(set(returns.index) & set(ta.index) & set(k200_by_date))
    dates = [d for d in common_dates if d >= base.START][::base.STEP]
    factor_files = {name: base.dated_files(folder) for name, folder in base.FACTORS.items()}

    rows=[]
    current={}
    for dt in dates:
        if dt not in fwd.index or dt not in k200_by_date or dt not in mcap.index or dt not in ta.index:
            continue
        k=k200_by_date[dt]
        codes=k.index[k==1]
        y=fwd.loc[dt].reindex(codes)
        if y.notna().sum()<50: continue
        ta_now=ta.loc[dt].reindex(codes)
        mc_now=mcap.loc[dt].reindex(codes)
        raw_r=base.pct_rank(ta_now,True)
        mcap_r=base.pct_rank(mc_now,True)
        turn_r=base.pct_rank(ta_now/mc_now.where(mc_now>0),True)
        resid_r=residual_trading_rank(ta_now,mc_now)

        for factor,files in factor_files.items():
            if dt not in files: continue
            raw=base.load_factor(files[dt]).reindex(codes)
            for direction,high_good in (("HIGH",True),("LOW",False)):
                f=base.pct_rank(raw,high_good=high_good)
                scores={
                    "BASE":f,
                    "RAW_TA_W10":0.90*f+0.10*raw_r,
                    "MCAP_W10":0.90*f+0.10*mcap_r,
                    "TURNOVER_W10":0.90*f+0.10*turn_r,
                    "RESID_TA_W10":0.90*f+0.10*resid_r,
                }
                for overlay,score in scores.items():
                    for n in base.TOP_NS:
                        names=base.select_top(score,n)
                        if len(names)<n: continue
                        gross=float(y.reindex(names).mean())
                        for cost in base.COSTS_BPS:
                            key=(factor,direction,overlay,n,cost)
                            turn=base.overlap_turnover(current.get(key,[]),names,n)
                            net=gross-turn*cost/10000.0
                            rows.append({"date":dt,"factor":factor,"direction":direction,"overlay":overlay,
                                         "top_n":n,"cost_bps":cost,"net":net,"turnover":turn})
                            current[key]=names
    p=pd.DataFrame(rows)
    p["date"]=pd.to_datetime(p.date)
    p.to_csv(OUT/"size_control_periods.csv",index=False,encoding="utf-8-sig")

    sums=[]
    for keys,g in p.groupby(["factor","direction","overlay","top_n","cost_bps"]):
        for sample,mask in (("FULL",pd.Series(True,index=g.index)),("OOS_2023_PLUS",g.date>=base.OOS_START)):
            x=g[mask]
            if len(x)<3: continue
            sums.append({"sample":sample,"factor":keys[0],"direction":keys[1],"overlay":keys[2],
                         "top_n":keys[3],"cost_bps":keys[4],"return":base.ann_return(x.net),
                         "sharpe":base.sharpe(x.net),"mdd":base.max_drawdown(x.net),
                         "turnover":float(x.turnover.mean())})
    s=pd.DataFrame(sums)
    s.to_csv(OUT/"size_control_summary.csv",index=False,encoding="utf-8-sig")

    comps=[]
    for keys,g in s.groupby(["sample","factor","direction","top_n","cost_bps"]):
        b=g[g.overlay=="BASE"]
        if b.empty: continue
        b=b.iloc[0]
        for _,r in g[g.overlay!="BASE"].iterrows():
            comps.append({"sample":keys[0],"factor":keys[1],"direction":keys[2],"overlay":r.overlay,
                          "top_n":keys[3],"cost_bps":keys[4],"return_delta":r["return"]-b["return"],
                          "sharpe_delta":r.sharpe-b.sharpe,"mdd_delta":r.mdd-b.mdd,
                          "turnover_delta":r.turnover-b.turnover})
    c=pd.DataFrame(comps)
    c.to_csv(OUT/"size_control_vs_base.csv",index=False,encoding="utf-8-sig")

    agg=[]
    for (sample,overlay),g in c.groupby(["sample","overlay"]):
        agg.append({"sample":sample,"overlay":overlay,"n_configs":len(g),
                    "return_improve_share":float((g.return_delta>0).mean()),
                    "sharpe_improve_share":float((g.sharpe_delta>0).mean()),
                    "mdd_improve_share":float((g.mdd_delta>0).mean()),
                    "median_return_delta":float(g.return_delta.median()),
                    "median_sharpe_delta":float(g.sharpe_delta.median()),
                    "median_turnover_delta":float(g.turnover_delta.median())})
    a=pd.DataFrame(agg)
    a.to_csv(OUT/"size_control_aggregate.csv",index=False,encoding="utf-8-sig")
    lines=["# Raw trading value: size-control test","",
           "Both factor directions; Top10/20; 0/30/60 bps. RESID_TA is log trading value residualized cross-sectionally on log market cap.",""]
    for sample in ("FULL","OOS_2023_PLUS"):
        lines += [f"## {sample}",""]
        z=a[a["sample"]==sample].sort_values(["return_improve_share","median_return_delta"],ascending=False)
        for _,r in z.iterrows():
            lines.append(f"- {r.overlay}: return improve {r.return_improve_share:.0%}, Sharpe improve {r.sharpe_improve_share:.0%}, MDD improve {r.mdd_improve_share:.0%}, median return delta {r.median_return_delta:+.2%}, turnover delta {r.median_turnover_delta:+.2f}")
        lines.append("")
    (OUT/"SIZE_CONTROL.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print((OUT/"SIZE_CONTROL.md").read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
