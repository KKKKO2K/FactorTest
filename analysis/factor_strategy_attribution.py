from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "factor_strategy_attribution_results"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("lab", HERE / "factor_rotation_event_lab.py")
lab = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(lab)
base = lab.base

COST_BPS = 60
TARGETS = (
    ("K200", "EVENT_STATE_MACHINE", "1_K200_EVENT_STATE_MACHINE"),
    ("KOSPI_EX_K200", "EVENT_STATE_MACHINE", "2_KOSPI_EX_K200_EVENT_STATE_MACHINE"),
    ("K200", "REGIME_HYSTERESIS", "3_K200_REGIME_HYSTERESIS"),
)


def name_map() -> dict[str, str]:
    result: dict[str, str] = {}
    for _, path in sorted(base.dated_files(base.BASIC).items()):
        df = base.read_csv(path)
        cc = base.code_col(df)
        nc = base.find_col(df, exact=("종목명", "Name", "StockName"), contains=("종목명", "stockname"))
        if nc is None:
            continue
        codes = base.norm_code(df[cc])
        names = df[nc].astype(str).str.strip()
        result.update(dict(zip(codes, names)))
    return result


def make_weights(strategy: str, z: pd.DataFrame, current: pd.Series, ages: dict[str, int]):
    if strategy == "REGIME_HYSTERESIS":
        score = z["HYBRID_ROTATION"].dropna().sort_values(ascending=False)
        retain = set(score.head(max(40, int(len(score) * 0.35))).index)
        keep = [c for c in current.index if c in retain]
        fill = [c for c in score.index if c not in keep]
        names = (keep + fill)[:25]
        new_w = pd.Series(1.0 / len(names), index=names) if len(names) >= 10 else pd.Series(dtype=float)
        return new_w, []

    old_names = list(current.index)
    survivors = []
    exits = []
    for code in old_names:
        ages[code] = ages.get(code, 0) + lab.STEP
        if code not in z.index:
            exits.append((code, "OUT_OF_UNIVERSE"))
            ages.pop(code, None)
            continue
        meta_rank = z["HYBRID_ROTATION"].rank(pct=True).get(code, np.nan)
        age_exit = ages[code] >= 80
        score_exit = pd.notna(meta_rank) and meta_rank <= 0.25
        crowd_exit = z.at[code, "crowding_exit"] >= 0.80
        if not (age_exit or score_exit or crowd_exit):
            survivors.append(code)
        else:
            reason = "MAX_AGE" if age_exit else ("SCORE_DECAY" if score_exit else "CROWDING")
            exits.append((code, reason))
            ages.pop(code, None)
    candidates = z.loc[z.event_any].sort_values("event_score", ascending=False).index.tolist()
    additions = [c for c in candidates if c not in survivors]
    names = (survivors + additions)[:25]
    for code in names:
        if code not in ages:
            ages[code] = 0
    new_w = pd.Series(1.0 / len(names), index=names) if names else pd.Series(dtype=float)
    return new_w, exits


def run_one(universe: str, strategy: str, label: str, returns, basic_panels, names):
    fwd10 = lab.forward_return(returns, lab.STEP)
    panel = lab.build_panel(universe, returns, basic_panels)
    ic = lab.ic_detail(panel, lab.forward_return(returns, lab.HORIZON), universe)
    static, mapping, _ = lab.factor_maps(ic, universe)
    scores, _ = lab.score_history(panel, ic, universe, static, mapping)

    current = pd.Series(dtype=float)
    ages: dict[str, int] = {}
    period_rows = []
    stock_period_rows = []
    trade_rows = []
    wealth = 1.0
    bench_wealth = 1.0
    excess_wealth = 1.0

    for dt in sorted(scores):
        if dt not in fwd10.index:
            continue
        z = scores[dt]
        future = fwd10.loc[dt]
        universe_valid = future.reindex(z.index).dropna()
        benchmark = float(universe_valid.mean()) if len(universe_valid) else 0.0
        old_w = current.copy()
        new_w, exits = make_weights(strategy, z, current, ages)
        turn = lab.turnover(old_w, new_w)
        gross_contrib = new_w * future.reindex(new_w.index).fillna(0.0)
        gross = float(gross_contrib.sum())
        total_cost = turn * COST_BPS / 10000.0
        delta = (new_w.reindex(old_w.index.union(new_w.index), fill_value=0.0) - old_w.reindex(old_w.index.union(new_w.index), fill_value=0.0)).abs()
        if delta.sum() > 0:
            stock_cost = delta / delta.sum() * total_cost
        else:
            stock_cost = pd.Series(0.0, index=delta.index)
        net_contrib = gross_contrib.reindex(delta.index, fill_value=0.0) - stock_cost
        net = float(net_contrib.sum())
        exposure = float(new_w.sum())
        bench_ret = benchmark * exposure
        excess = net - bench_ret

        if dt >= lab.SPLIT:
            start_wealth = wealth
            for code, c in net_contrib.items():
                if abs(c) < 1e-18 and code not in new_w.index and code not in old_w.index:
                    continue
                stock_period_rows.append({
                    "label": label, "universe": universe, "strategy": strategy,
                    "date": dt, "code": code, "name": names.get(code, code),
                    "old_weight": float(old_w.get(code, 0.0)), "new_weight": float(new_w.get(code, 0.0)),
                    "forward10": float(future.get(code, 0.0)) if pd.notna(future.get(code, np.nan)) else 0.0,
                    "gross_contribution": float(gross_contrib.get(code, 0.0)),
                    "cost_contribution": float(stock_cost.get(code, 0.0)),
                    "net_contribution": float(c),
                    "wealth_contribution": float(start_wealth * c),
                    "event_type": z.at[code, "event_type"] if code in z.index and pd.notna(z.at[code, "event_type"]) else "",
                    "event_score": float(z.at[code, "event_score"]) if code in z.index and pd.notna(z.at[code, "event_score"]) else np.nan,
                })
            period_rows.append({
                "label": label, "universe": universe, "strategy": strategy, "date": dt,
                "gross": gross, "net": net, "benchmark": bench_ret, "excess": excess,
                "turnover": turn, "n_holdings": len(new_w),
                "wealth_before": wealth,
                "strategy_wealth": wealth * (1.0 + net),
                "benchmark_wealth": bench_wealth * (1.0 + bench_ret),
                "excess_wealth": excess_wealth * (1.0 + excess),
            })
            wealth *= 1.0 + net
            bench_wealth *= 1.0 + bench_ret
            excess_wealth *= 1.0 + excess

            union = old_w.index.union(new_w.index)
            for code in union:
                dw = float(new_w.get(code, 0.0) - old_w.get(code, 0.0))
                if abs(dw) > 1e-12:
                    trade_rows.append({
                        "label": label, "date": dt, "code": code, "name": names.get(code, code),
                        "weight_change": dw, "action": "BUY" if dw > 0 else "SELL",
                        "event_type": z.at[code, "event_type"] if code in z.index and pd.notna(z.at[code, "event_type"]) else "",
                    })
            for code, reason in exits:
                if dt >= lab.SPLIT:
                    trade_rows.append({
                        "label": label, "date": dt, "code": code, "name": names.get(code, code),
                        "weight_change": 0.0, "action": f"EXIT_{reason}", "event_type": "",
                    })
        current = new_w

    return pd.DataFrame(period_rows), pd.DataFrame(stock_period_rows), pd.DataFrame(trade_rows)


def diagnostics(periods: pd.DataFrame, stock_periods: pd.DataFrame):
    rows = []
    contributions = []
    yearly = []
    for label, g in periods.groupby("label"):
        g = g.sort_values("date").copy()
        s = stock_periods[stock_periods.label == label].copy()
        by_stock = s.groupby(["code", "name"], as_index=False).agg(
            wealth_contribution=("wealth_contribution", "sum"),
            gross_contribution=("gross_contribution", "sum"),
            cost_contribution=("cost_contribution", "sum"),
            holding_periods=("new_weight", lambda x: int((x > 0).sum())),
            avg_weight=("new_weight", lambda x: float(x[x > 0].mean()) if (x > 0).any() else 0.0),
        ).sort_values("wealth_contribution", ascending=False)
        by_stock["label"] = label
        contributions.append(by_stock)
        top_codes = by_stock.code.tolist()
        base_return = float(g.strategy_wealth.iloc[-1] - 1.0)
        bench_return = float(g.benchmark_wealth.iloc[-1] - 1.0)
        excess_comp = float(g.excess_wealth.iloc[-1] - 1.0)
        net_series = g.set_index("date").net
        ex_series = g.set_index("date").excess

        row = {
            "label": label, "strategy_return": base_return, "benchmark_return": bench_return,
            "compounded_excess": excess_comp, "best_period": float(net_series.max()),
            "worst_period": float(net_series.min()), "top1_positive_share": np.nan,
            "top5_positive_share": np.nan, "top10_positive_share": np.nan,
        }
        positives = by_stock[by_stock.wealth_contribution > 0].wealth_contribution
        pos_sum = positives.sum()
        for n in (1, 5, 10):
            row[f"top{n}_positive_share"] = float(positives.head(n).sum() / pos_sum) if pos_sum > 0 else np.nan
            remove = set(top_codes[:n])
            removed = s[s.code.isin(remove)].groupby("date").net_contribution.sum()
            cf = g.set_index("date").net.sub(removed, fill_value=0.0)
            row[f"return_without_top{n}_cash"] = float((1.0 + cf).prod() - 1.0)
        for n in (1, 3, 5):
            trimmed = net_series.drop(net_series.nlargest(n).index)
            row[f"return_without_best{n}_periods"] = float((1.0 + trimmed).prod() - 1.0)
            trimmed_ex = ex_series.drop(ex_series.nlargest(n).index)
            row[f"excess_without_best{n}_periods"] = float((1.0 + trimmed_ex).prod() - 1.0)
        lo, hi = net_series.quantile([0.025, 0.975])
        wins = net_series.clip(lo, hi)
        row["winsorized_return_2_5pct"] = float((1.0 + wins).prod() - 1.0)
        rows.append(row)

        gy = g.copy()
        gy["year"] = gy.date.dt.year
        for year, y in gy.groupby("year"):
            yearly.append({
                "label": label, "year": year,
                "strategy_return": float((1.0 + y.net).prod() - 1.0),
                "benchmark_return": float((1.0 + y.benchmark).prod() - 1.0),
                "excess_return": float((1.0 + y.excess).prod() - 1.0),
                "sharpe": float(y.net.mean() / y.net.std(ddof=1) * math.sqrt(252 / lab.STEP)) if len(y) > 2 and y.net.std(ddof=1) > 0 else np.nan,
                "n_periods": len(y),
            })
    return pd.DataFrame(rows), pd.concat(contributions, ignore_index=True), pd.DataFrame(yearly)


def main():
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:lab.END]
    names = name_map()
    all_p, all_s, all_t = [], [], []
    for universe, strategy, label in TARGETS:
        print(f"Running {label}", flush=True)
        p, s, t = run_one(universe, strategy, label, returns, basic_panels, names)
        all_p.append(p); all_s.append(s); all_t.append(t)
    periods = pd.concat(all_p, ignore_index=True)
    stock_periods = pd.concat(all_s, ignore_index=True)
    trades = pd.concat(all_t, ignore_index=True)
    diag, contrib, yearly = diagnostics(periods, stock_periods)
    periods.to_csv(OUT / "period_returns_and_wealth.csv", index=False, encoding="utf-8-sig")
    stock_periods.to_csv(OUT / "stock_period_contributions.csv", index=False, encoding="utf-8-sig")
    trades.to_csv(OUT / "trades_and_exits.csv", index=False, encoding="utf-8-sig")
    contrib.to_csv(OUT / "stock_total_contributions.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(OUT / "yearly_absolute_and_excess.csv", index=False, encoding="utf-8-sig")
    diag.to_csv(OUT / "outlier_sensitivity.csv", index=False, encoding="utf-8-sig")
    print(diag.to_string(index=False))
    print(yearly.to_string(index=False))
    print(contrib.groupby("label", group_keys=False).head(10).to_string(index=False))

if __name__ == "__main__":
    main()
