from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import run_cross_factor_liquidity as base

OUT = Path(__file__).resolve().parent / "results"
KEEP = ("BASE", "RAW_TA_W10", "TURNOVER_W10", "ACT1_W10", "ACT5_W10", "ACT5_KEEP_TOP70", "ACT5_KEEP_TOP50")


def main() -> None:
    returns, mcap, k200_by_date = base.load_basic()
    ta = base.load_trading_amount()
    fwd = base.forward_returns(returns, base.HORIZON)
    liq_frames = base.build_liquidity_features(ta, mcap)
    common_dates = sorted(set(returns.index) & set(ta.index) & set(k200_by_date))
    dates = [d for d in common_dates if d >= base.START][::base.STEP]
    factor_files = {name: base.dated_files(folder) for name, folder in base.FACTORS.items()}

    rows = []
    current = {}
    for dt in dates:
        if dt not in fwd.index or dt not in k200_by_date:
            continue
        k = k200_by_date[dt]
        codes = k.index[k == 1]
        y = fwd.loc[dt].reindex(codes)
        if y.notna().sum() < 50:
            continue
        liq = {name: frame.loc[dt].reindex(codes) if dt in frame.index else pd.Series(index=codes, dtype=float)
               for name, frame in liq_frames.items()}
        for factor, files in factor_files.items():
            if dt not in files:
                continue
            raw = base.load_factor(files[dt]).reindex(codes)
            for direction, high_good in (("HIGH", True), ("LOW", False)):
                factor_score = base.pct_rank(raw, high_good=high_good)
                scores = base.overlay_scores(factor_score, liq)
                for overlay in KEEP:
                    score = scores[overlay]
                    for n in base.TOP_NS:
                        names = base.select_top(score, n)
                        if len(names) < n:
                            continue
                        gross = float(y.reindex(names).mean())
                        for cost in base.COSTS_BPS:
                            key = (factor, direction, overlay, n, cost)
                            turn = base.overlap_turnover(current.get(key, []), names, n)
                            net = gross - turn * cost / 10000.0
                            rows.append({"date": dt, "factor": factor, "direction": direction, "overlay": overlay,
                                         "top_n": n, "cost_bps": cost, "net": net, "turnover": turn})
                            current[key] = names

    periods = pd.DataFrame(rows)
    periods["date"] = pd.to_datetime(periods.date)
    periods.to_csv(OUT / "sign_robustness_periods.csv", index=False, encoding="utf-8-sig")

    summaries=[]
    for (factor,direction,overlay,n,cost),g in periods.groupby(["factor","direction","overlay","top_n","cost_bps"]):
        for sample,mask in (("FULL", pd.Series(True,index=g.index)),
                            ("OOS_2023_PLUS", g.date >= base.OOS_START)):
            x=g[mask]
            if len(x)<3: continue
            summaries.append({"sample":sample,"factor":factor,"direction":direction,"overlay":overlay,
                              "top_n":n,"cost_bps":cost,"n_periods":len(x),
                              "annualized_return":base.ann_return(x.net),"sharpe":base.sharpe(x.net),
                              "mdd":base.max_drawdown(x.net),"avg_turnover":float(x.turnover.mean())})
    summary=pd.DataFrame(summaries)
    summary.to_csv(OUT / "sign_robustness_summary.csv", index=False, encoding="utf-8-sig")

    comps=[]
    for (sample,factor,direction,n,cost),g in summary.groupby(["sample","factor","direction","top_n","cost_bps"]):
        b=g[g.overlay=="BASE"]
        if b.empty: continue
        b=b.iloc[0]
        for _,r in g[g.overlay!="BASE"].iterrows():
            comps.append({"sample":sample,"factor":factor,"direction":direction,"overlay":r.overlay,
                          "top_n":n,"cost_bps":cost,
                          "return_delta":r.annualized_return-b.annualized_return,
                          "sharpe_delta":r.sharpe-b.sharpe,"mdd_delta":r.mdd-b.mdd,
                          "turnover_delta":r.avg_turnover-b.avg_turnover})
    comp=pd.DataFrame(comps)
    comp.to_csv(OUT / "sign_robustness_vs_base.csv", index=False, encoding="utf-8-sig")

    agg=[]
    for (sample,overlay),g in comp.groupby(["sample","overlay"]):
        agg.append({"sample":sample,"overlay":overlay,"n_configs":len(g),
                    "return_improve_share":float((g.return_delta>0).mean()),
                    "sharpe_improve_share":float((g.sharpe_delta>0).mean()),
                    "mdd_improve_share":float((g.mdd_delta>0).mean()),
                    "median_return_delta":float(g.return_delta.median()),
                    "median_sharpe_delta":float(g.sharpe_delta.median()),
                    "median_turnover_delta":float(g.turnover_delta.median())})
    agg=pd.DataFrame(agg)
    agg.to_csv(OUT / "sign_robustness_aggregate.csv", index=False, encoding="utf-8-sig")

    lines=["# Trading-value overlay sign robustness","",
           "Each raw factor is tested in both HIGH-good and LOW-good directions; overlay uplift is always measured versus the same-direction BASE.",""]
    oos=agg[agg["sample"]=="OOS_2023_PLUS"].sort_values(["return_improve_share","median_return_delta"],ascending=False)
    for _,r in oos.iterrows():
        lines.append(f"- {r.overlay}: return improve {r.return_improve_share:.0%}, Sharpe improve {r.sharpe_improve_share:.0%}, MDD improve {r.mdd_improve_share:.0%}, median return delta {r.median_return_delta:.2%}, turnover delta {r.median_turnover_delta:.2f}")
    (OUT / "SIGN_ROBUSTNESS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print((OUT / "SIGN_ROBUSTNESS.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
