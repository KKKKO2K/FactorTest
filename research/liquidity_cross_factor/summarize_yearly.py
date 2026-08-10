from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"


def main() -> None:
    p = pd.read_csv(OUT / "sign_robustness_periods.csv", encoding="utf-8-sig")
    p["date"] = pd.to_datetime(p["date"])
    p["year"] = p["date"].dt.year

    rows=[]
    for keys,g in p.groupby(["year","factor","direction","overlay","top_n","cost_bps"]):
        if len(g)<3: continue
        ret=float((1+g["net"]).prod()-1)
        rows.append({"year":keys[0],"factor":keys[1],"direction":keys[2],"overlay":keys[3],
                     "top_n":keys[4],"cost_bps":keys[5],"n_periods":len(g),"return":ret,
                     "avg_turnover":float(g["turnover"].mean())})
    annual=pd.DataFrame(rows)
    annual.to_csv(OUT / "sign_robustness_yearly.csv",index=False,encoding="utf-8-sig")

    comps=[]
    for keys,g in annual.groupby(["year","factor","direction","top_n","cost_bps"]):
        b=g[g.overlay=="BASE"]
        if b.empty: continue
        b=b.iloc[0]
        for _,r in g[g.overlay!="BASE"].iterrows():
            comps.append({"year":keys[0],"factor":keys[1],"direction":keys[2],"overlay":r.overlay,
                          "top_n":keys[3],"cost_bps":keys[4],"return_delta":r["return"]-b["return"],
                          "turnover_delta":r.avg_turnover-b.avg_turnover})
    comp=pd.DataFrame(comps)
    comp.to_csv(OUT / "sign_robustness_yearly_vs_base.csv",index=False,encoding="utf-8-sig")

    agg=[]
    for (year,overlay),g in comp.groupby(["year","overlay"]):
        agg.append({"year":year,"overlay":overlay,"n_configs":len(g),
                    "return_improve_share":float((g.return_delta>0).mean()),
                    "median_return_delta":float(g.return_delta.median()),
                    "median_turnover_delta":float(g.turnover_delta.median())})
    agg=pd.DataFrame(agg)
    agg.to_csv(OUT / "sign_robustness_yearly_aggregate.csv",index=False,encoding="utf-8-sig")

    target=agg[agg.overlay=="ACT5_KEEP_TOP70"].sort_values("year")
    lines=["# ACT5 bottom-30% filter: yearly sign robustness","",
           "Across both HIGH/LOW directions, Top10/20 and 0/30/60 bps configurations.",""]
    for _,r in target.iterrows():
        lines.append(f"- {int(r.year)}: improve {r.return_improve_share:.0%} of {int(r.n_configs)} configs; median yearly return delta {r.median_return_delta:+.2%}; turnover delta {r.median_turnover_delta:+.2f}")
    (OUT/"YEARLY_ACT5_TOP70.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print((OUT/"YEARLY_ACT5_TOP70.md").read_text(encoding="utf-8"))


if __name__=="__main__":
    main()
