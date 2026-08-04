from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "index_core_satellite_results"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("enh", HERE / "enhanced_k200_allocation_test.py")
enh = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(enh)

START = enh.START
SPLIT = enh.SPLIT
END = enh.END
STEP = enh.STEP
COSTS = enh.COSTS
INDEX_ASSET = "__KOSPI200_INDEX__"


def recover_satellites(targets: dict[str, pd.Series]) -> dict[str, pd.Series]:
    b = targets["CAP_WEIGHT_PROXY"]

    def recover(name: str, active: float) -> pd.Series:
        idx = b.index.union(targets[name].index)
        x = (targets[name].reindex(idx, fill_value=0.0) - (1.0 - active) * b.reindex(idx, fill_value=0.0)) / active
        x = x.clip(lower=0.0)
        return x / x.sum() if x.sum() > 0 else b

    return {
        "EVENT": recover("CORE90_EVENT10", 0.10),
        "MODERATE": recover("ENHANCED_MODERATE", 0.45),
        "LEADER10": recover("LEADER_TOP10_50", 0.50),
        "LEADER5": recover("LEADER_TOP5_65", 0.65),
        "PYRAMID": recover("PYRAMID_CONCENTRATED", 0.65),
    }


def mix_index_satellite(index_weight: float, satellite: pd.Series, stock_weight: float | None = None) -> pd.Series:
    if stock_weight is None:
        stock_weight = 1.0 - index_weight
    out = satellite * stock_weight
    out.loc[INDEX_ASSET] = index_weight
    return out[out > 1e-12]


def targets_for_state(state: str, sats: dict[str, pd.Series]) -> dict[str, pd.Series]:
    if state == "NARROW_RISK_ON":
        adaptive = mix_index_satellite(0.35, sats["LEADER5"], 0.65)
        defensive = adaptive.copy()
    elif state == "BROAD_RISK_ON":
        adaptive = mix_index_satellite(0.50, sats["LEADER10"], 0.50)
        defensive = adaptive.copy()
    elif state == "HIGH_DISPERSION":
        adaptive = mix_index_satellite(0.50, sats["PYRAMID"], 0.50)
        defensive = adaptive.copy()
    elif state == "HIGH_VOL_CHOP":
        adaptive = mix_index_satellite(0.80, sats["EVENT"], 0.20)
        defensive = mix_index_satellite(0.65, sats["EVENT"], 0.20)  # 15% cash
    elif state == "RISK_OFF":
        adaptive = mix_index_satellite(0.70, sats["EVENT"], 0.30)
        defensive = mix_index_satellite(0.50, sats["EVENT"], 0.20)  # 30% cash
    else:
        adaptive = mix_index_satellite(0.70, sats["MODERATE"], 0.30)
        defensive = adaptive.copy()

    return {
        "INDEX_ONLY": pd.Series({INDEX_ASSET: 1.0}),
        "INDEX90_EVENT10": mix_index_satellite(0.90, sats["EVENT"]),
        "INDEX70_EVENT30": mix_index_satellite(0.70, sats["EVENT"]),
        "INDEX70_LEADER30": mix_index_satellite(0.70, sats["LEADER10"]),
        "INDEX50_LEADER50": mix_index_satellite(0.50, sats["LEADER10"]),
        "INDEX35_LEADER65": mix_index_satellite(0.35, sats["LEADER5"]),
        "INDEX50_PYRAMID50": mix_index_satellite(0.50, sats["PYRAMID"]),
        "INDEX35_PYRAMID65": mix_index_satellite(0.35, sats["PYRAMID"]),
        "INDEX_ADAPTIVE_FULL": adaptive,
        "INDEX_ADAPTIVE_DEFENSIVE": defensive,
    }


def turnover(old_end: pd.Series, new: pd.Series) -> float:
    idx = old_end.index.union(new.index)
    old = old_end.reindex(idx, fill_value=0.0)
    target = new.reindex(idx, fill_value=0.0)
    old_cash = 1.0 - float(old.sum())
    new_cash = 1.0 - float(target.sum())
    return 0.5 * (float((target - old).abs().sum()) + abs(new_cash - old_cash))


def run(
    panel: pd.DataFrame,
    scores: dict[pd.Timestamp, pd.DataFrame],
    returns: pd.DataFrame,
    basic_panels: dict[pd.Timestamp, pd.DataFrame],
    k200_period: pd.Series,
    cost_bps: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fwd10 = enh.lab.forward_return(returns, STEP)
    current_end: dict[str, pd.Series] = {}
    rows: list[dict] = []
    weights: list[dict] = []

    for dt, g0 in panel.groupby(level="date"):
        if dt not in scores or dt not in fwd10.index or dt not in k200_period.index or pd.isna(k200_period.loc[dt]):
            continue
        codes = g0.index.get_level_values("code")
        stock_future = fwd10.loc[dt].reindex(codes).fillna(0.0)
        stock_targets = enh.strategy_targets(dt, g0, scores[dt], basic_panels[dt])
        sats = recover_satellites(stock_targets)
        state = str(g0["state"].iloc[0])
        targets = targets_for_state(state, sats)
        asset_returns = stock_future.copy()
        asset_returns.loc[INDEX_ASSET] = float(k200_period.loc[dt])

        for strategy, new_w in targets.items():
            old = current_end.get(strategy, pd.Series(dtype=float))
            turn = turnover(old, new_w)
            r = asset_returns.reindex(new_w.index).fillna(0.0)
            gross = float((new_w * r).sum())
            net = gross - turn * cost_bps / 10000.0
            denom = 1.0 + gross
            end_w = new_w * (1.0 + r) / denom if denom > 0 else new_w.copy()
            current_end[strategy] = end_w[end_w.abs() > 1e-12]
            stock_only = new_w.drop(INDEX_ASSET, errors="ignore")
            rows.append({
                "date": dt,
                "strategy": strategy,
                "cost_bps": cost_bps,
                "state": state,
                "gross": gross,
                "net": net,
                "k200_return": float(k200_period.loc[dt]),
                "active_return": net - float(k200_period.loc[dt]),
                "turnover": turn,
                "exposure": float(new_w.sum()),
                "index_weight": float(new_w.get(INDEX_ASSET, 0.0)),
                "stock_weight": float(stock_only.sum()),
                "cash_weight": float(1.0 - new_w.sum()),
                "top1_stock_weight": float(stock_only.nlargest(1).sum()),
                "top5_stock_weight": float(stock_only.nlargest(5).sum()),
                "n_stocks": int((stock_only > 1e-8).sum()),
            })
            for asset, weight in new_w.sort_values(ascending=False).items():
                weights.append({
                    "date": dt,
                    "strategy": strategy,
                    "cost_bps": cost_bps,
                    "asset": asset,
                    "weight": float(weight),
                    "state": state,
                })
    return pd.DataFrame(rows), pd.DataFrame(weights)


def metrics(g: pd.DataFrame) -> dict[str, float]:
    g = g.sort_values("date")
    periods = 252 / STEP
    years = len(g) / periods
    s, b = g.net, g.k200_return
    a = s - b
    sw, bw = (1+s).cumprod(), (1+b).cumprod()
    rel = sw / bw
    te = a.std(ddof=1) * math.sqrt(periods)
    beta = np.cov(s, b, ddof=1)[0, 1] / np.var(b, ddof=1) if np.var(b, ddof=1) > 0 else np.nan
    top = b >= b.quantile(0.80)
    return {
        "n_periods": len(g),
        "strategy_total_return": float(sw.iloc[-1]-1),
        "k200_total_return": float(bw.iloc[-1]-1),
        "strategy_cagr": float(sw.iloc[-1]**(1/years)-1),
        "k200_cagr": float(bw.iloc[-1]**(1/years)-1),
        "relative_cagr": float(rel.iloc[-1]**(1/years)-1),
        "information_ratio": float(a.mean()/a.std(ddof=1)*math.sqrt(periods)) if a.std(ddof=1)>0 else np.nan,
        "tracking_error": float(te),
        "beta_to_k200": float(beta),
        "capm_alpha_ann": float((s.mean()-beta*b.mean())*periods) if pd.notna(beta) else np.nan,
        "strategy_mdd": float((sw/sw.cummax()-1).min()),
        "relative_mdd": float((rel/rel.cummax()-1).min()),
        "up_capture": float(s[b>0].mean()/b[b>0].mean()),
        "down_capture": float(s[b<0].mean()/b[b<0].mean()),
        "top20_rally_capture": float(s[top].mean()/b[top].mean()),
        "annual_turnover": float(g.turnover.mean()*periods),
        "avg_index_weight": float(g.index_weight.mean()),
        "avg_stock_weight": float(g.stock_weight.mean()),
        "avg_cash_weight": float(g.cash_weight.mean()),
        "avg_top1_stock_weight": float(g.top1_stock_weight.mean()),
        "avg_top5_stock_weight": float(g.top5_stock_weight.mean()),
    }


def summarize(detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, yearly = [], []
    for (strategy, cost), g0 in detail.groupby(["strategy", "cost_bps"]):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, END+pd.Timedelta(days=1))):
            g = g0[(g0.date>=lo)&(g0.date<hi)]
            if len(g)<20:
                continue
            row={"strategy":strategy,"cost_bps":cost,"sample":sample}
            row.update(metrics(g)); rows.append(row)
        test=g0[g0.date>=SPLIT].copy(); test["year"]=test.date.dt.year
        for year, gy in test.groupby("year"):
            yearly.append({
                "strategy":strategy,"cost_bps":cost,"year":year,
                "strategy_return":float((1+gy.net).prod()-1),
                "k200_return":float((1+gy.k200_return).prod()-1),
                "relative_return":float((1+gy.net).prod()/(1+gy.k200_return).prod()-1),
                "n_periods":len(gy),
            })
    return pd.DataFrame(rows),pd.DataFrame(yearly)


def main() -> None:
    returns,basic_panels=enh.base.load_basic(); returns=returns.loc[:END]
    panel=enh.lab.build_panel("K200",returns,basic_panels)
    fwd20=enh.lab.forward_return(returns,enh.lab.HORIZON)
    ic=enh.lab.ic_detail(panel,fwd20,"K200")
    static,mapping,_=enh.lab.factor_maps(ic,"K200")
    scores,selections=enh.lab.score_history(panel,ic,"K200",static,mapping)
    dates=sorted(panel.index.get_level_values("date").unique())
    close=enh.download_kospi200(); k200=enh.forward_index_returns(close,dates,STEP)

    details=[]; weights=[]
    for cost in COSTS:
        d,w=run(panel,scores,returns,basic_panels,k200,cost)
        details.append(d); weights.append(w)
    detail=pd.concat(details,ignore_index=True); weight=pd.concat(weights,ignore_index=True)
    summary,yearly=summarize(detail)
    detail.to_csv(OUT/"period_returns.csv",index=False,encoding="utf-8-sig")
    weight.to_csv(OUT/"target_weights.csv",index=False,encoding="utf-8-sig")
    summary.to_csv(OUT/"strategy_summary.csv",index=False,encoding="utf-8-sig")
    yearly.to_csv(OUT/"yearly_returns.csv",index=False,encoding="utf-8-sig")
    key=summary[(summary["sample"]=="test")&(summary.cost_bps==60)].sort_values("relative_cagr",ascending=False)
    train=summary[(summary["sample"]=="train")&(summary.cost_bps==60)][["strategy","relative_cagr","information_ratio","strategy_cagr"]].rename(columns={"relative_cagr":"train_relative_cagr","information_ratio":"train_ir","strategy_cagr":"train_strategy_cagr"})
    key=key.merge(train,on="strategy",how="left")
    key.to_csv(OUT/"key_comparison_60bps.csv",index=False,encoding="utf-8-sig")
    (OUT/"summary.md").write_text("# Actual KOSPI200 Core + Stock Satellite\n\n"+key.to_markdown(index=False),encoding="utf-8")
    print(key.to_string(index=False))

if __name__=="__main__":
    main()
