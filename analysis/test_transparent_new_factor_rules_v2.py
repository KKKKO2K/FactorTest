from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("base_rules", HERE / "test_transparent_new_factor_rules.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
OUT = HERE / "transparent_rule_results_v2"
OUT.mkdir(parents=True, exist_ok=True)


def strategies(x):
    p = x.private_good
    s = x.short_reversal
    r = x.op12_good
    v = x.value
    out = {
        "PRIVATE_ONLY": p,
        "SHORT_REVERSAL_ONLY": s,
        "OLD4_LINEAR": x[["value", "revision"]].mean(axis=1),
        "NEW4_LINEAR": x[["short_reversal", "long_contrarian", "private_good", "foreign_good"]].mean(axis=1),
        "PRIVATE_REVERSAL_LINEAR": 0.55*p + 0.45*s,
        "PRIVATE_REVISION": 0.70*p + 0.30*r,
        "PRIVATE_VALUE": 0.70*p + 0.30*v,
        "PRIVATE_REVERSAL_INTERACTION": 0.45*p + 0.30*s + 0.25*(p*s),
        "PRIVATE_REVERSAL_SOFT_VETO": 0.45*p + 0.30*s + 0.15*r + 0.10*v - 0.35*(r < 0.10).astype(float),
        "PRIVATE_OR_REVERSAL": pd.concat([p, s], axis=1).max(axis=1),
        "PRIVATE_AND_REVERSAL": pd.concat([p, s], axis=1).min(axis=1),
    }
    return out


def period_test(returns, basic, h=20, n=25, cost_bps=30, buffer=False):
    fwd = base.forward_return(returns, h)
    dates = returns.index[returns.index >= base.START][::h]
    cache = {}
    records = []
    current = {name: [] for name in strategies(pd.DataFrame({
        "private_good": pd.Series(dtype=float), "short_reversal": pd.Series(dtype=float),
        "op12_good": pd.Series(dtype=float), "value": pd.Series(dtype=float),
        "revision": pd.Series(dtype=float), "long_contrarian": pd.Series(dtype=float),
        "foreign_good": pd.Series(dtype=float),
    })).keys()}
    for dt in dates:
        if dt not in basic or dt not in fwd.index:
            continue
        x = base.feature_frame(dt, basic, cache)
        y = fwd.loc[dt].reindex(x.index)
        for name, score in strategies(x).items():
            sc = score.replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)
            if len(sc) < n:
                continue
            if buffer and current[name]:
                retain = set(sc.head(min(len(sc), int(n*1.5))).index)
                keep = [c for c in current[name] if c in retain]
                fill = [c for c in sc.index if c not in keep]
                names = (keep + fill)[:n]
            else:
                names = sc.head(n).index.tolist()
            old, new = set(current[name]), set(names)
            turn = 1.0 if not old else 1 - len(old & new) / n
            current[name] = names
            port = y.reindex(names).mean()
            bench = y.reindex(sc.index).mean()
            records.append({"date": dt, "strategy": name, "gross": port, "bench": bench,
                            "excess_gross": port-bench, "turnover": turn,
                            "net": port-turn*cost_bps/10000,
                            "excess": port-bench-turn*cost_bps/10000,
                            "n": len(names), "eligible": len(sc)})
    return pd.DataFrame(records)


def summarize(df, h=20):
    rows=[]
    periods=252/h
    for name,g0 in df.groupby("strategy"):
        for label,lo,hi in (("train",base.START,base.SPLIT),("test",base.SPLIT,None)):
            g=g0[g0.date>=lo]
            if hi is not None: g=g[g.date<hi]
            if len(g)<10: continue
            ex=g.excess
            nav=(1+ex).cumprod()
            rows.append({"strategy":name,"sample":label,"n_periods":len(g),
                         "excess_ann":ex.mean()*periods,
                         "excess_sharpe":ex.mean()/ex.std(ddof=1)*math.sqrt(periods) if ex.std(ddof=1)>0 else np.nan,
                         "excess_mdd":(nav/nav.cummax()-1).min(),
                         "avg_turnover":g.turnover.mean(),"annual_turnover":g.turnover.mean()*periods,
                         "avg_eligible":g.eligible.mean()})
    return pd.DataFrame(rows)


def main():
    returns,basic=base.load_basic()
    details=[]
    for buffer in (False,True):
        for cost in (30,60,100):
            d=period_test(returns,basic,cost_bps=cost,buffer=buffer)
            d["buffer"]=buffer; d["cost_bps"]=cost; details.append(d)
    detail=pd.concat(details,ignore_index=True)
    detail.to_csv(OUT/"periods.csv",index=False,encoding="utf-8-sig")
    sums=[]
    for (buffer,cost),g in detail.groupby(["buffer","cost_bps"]):
        s=summarize(g); s["buffer"]=buffer; s["cost_bps"]=cost; sums.append(s)
    summary=pd.concat(sums,ignore_index=True)
    summary.to_csv(OUT/"summary.csv",index=False,encoding="utf-8-sig")
    key=summary[(summary["sample"]=="test")&(summary.cost_bps==30)&(summary.buffer==False)].sort_values("excess_sharpe",ascending=False)
    (OUT/"summary.md").write_text("# Milder transparent interactions\n\n"+key.to_markdown(index=False),encoding="utf-8")
    print(key.to_string(index=False))

if __name__ == "__main__":
    main()
