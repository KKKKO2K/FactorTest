from __future__ import annotations

from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
SPLIT = pd.Timestamp("2023-01-01")


def annualized_return(r: pd.Series, periods_per_year: float = 25.2) -> float:
    if len(r) == 0:
        return float("nan")
    return float((1.0 + r).prod() ** (periods_per_year / len(r)) - 1.0)


def sharpe(r: pd.Series, periods_per_year: float = 25.2) -> float:
    sd = r.std(ddof=1)
    if len(r) < 3 or pd.isna(sd) or sd <= 0:
        return float("nan")
    return float(r.mean() / sd * periods_per_year ** 0.5)


def max_drawdown(r: pd.Series) -> float:
    nav = (1.0 + r.fillna(0.0)).cumprod()
    return float((nav / nav.cummax() - 1.0).min()) if len(nav) else float("nan")


def main() -> None:
    p = pd.read_csv(OUT / "sign_robustness_periods.csv", encoding="utf-8-sig")
    p["date"] = pd.to_datetime(p["date"])
    p["sample"] = p["date"].map(lambda d: "TRAIN_PRE_2023" if d < SPLIT else "OOS_2023_PLUS")

    rows = []
    keys = ["sample", "factor", "direction", "overlay", "top_n", "cost_bps"]
    for k, g in p.groupby(keys):
        g = g.sort_values("date")
        rows.append({
            "sample": k[0], "factor": k[1], "direction": k[2], "overlay": k[3],
            "top_n": k[4], "cost_bps": k[5], "n_periods": len(g),
            "annualized_return": annualized_return(g["net"]),
            "sharpe": sharpe(g["net"]), "mdd": max_drawdown(g["net"]),
            "avg_turnover": float(g["turnover"].mean()),
        })
    s = pd.DataFrame(rows)
    s.to_csv(OUT / "train_oos_summary.csv", index=False, encoding="utf-8-sig")

    comps = []
    group = ["sample", "factor", "direction", "top_n", "cost_bps"]
    for k, g in s.groupby(group):
        b = g[g["overlay"] == "BASE"]
        if b.empty:
            continue
        b = b.iloc[0]
        for _, r in g[g["overlay"] != "BASE"].iterrows():
            comps.append({
                "sample": k[0], "factor": k[1], "direction": k[2],
                "top_n": k[3], "cost_bps": k[4], "overlay": r["overlay"],
                "return_delta": r["annualized_return"] - b["annualized_return"],
                "sharpe_delta": r["sharpe"] - b["sharpe"],
                "mdd_delta": r["mdd"] - b["mdd"],
                "turnover_delta": r["avg_turnover"] - b["avg_turnover"],
            })
    c = pd.DataFrame(comps)
    c.to_csv(OUT / "train_oos_vs_base.csv", index=False, encoding="utf-8-sig")

    agg = []
    for (sample, overlay), g in c.groupby(["sample", "overlay"]):
        agg.append({
            "sample": sample, "overlay": overlay, "n_configs": len(g),
            "return_improve_share": float((g["return_delta"] > 0).mean()),
            "sharpe_improve_share": float((g["sharpe_delta"] > 0).mean()),
            "mdd_improve_share": float((g["mdd_delta"] > 0).mean()),
            "median_return_delta": float(g["return_delta"].median()),
            "median_sharpe_delta": float(g["sharpe_delta"].median()),
            "median_turnover_delta": float(g["turnover_delta"].median()),
        })
    a = pd.DataFrame(agg)
    a.to_csv(OUT / "train_oos_aggregate.csv", index=False, encoding="utf-8-sig")

    pivot = a.pivot(index="overlay", columns="sample", values=[
        "return_improve_share", "sharpe_improve_share", "mdd_improve_share", "median_return_delta"
    ])
    rows2 = []
    for overlay in sorted(a["overlay"].unique()):
        tr = a[(a["overlay"] == overlay) & (a["sample"] == "TRAIN_PRE_2023")]
        oo = a[(a["overlay"] == overlay) & (a["sample"] == "OOS_2023_PLUS")]
        if tr.empty or oo.empty:
            continue
        tr, oo = tr.iloc[0], oo.iloc[0]
        rows2.append({
            "overlay": overlay,
            "train_return_improve_share": tr["return_improve_share"],
            "oos_return_improve_share": oo["return_improve_share"],
            "train_median_return_delta": tr["median_return_delta"],
            "oos_median_return_delta": oo["median_return_delta"],
            "delta_oos_minus_train": oo["median_return_delta"] - tr["median_return_delta"],
            "train_sharpe_improve_share": tr["sharpe_improve_share"],
            "oos_sharpe_improve_share": oo["sharpe_improve_share"],
            "train_mdd_improve_share": tr["mdd_improve_share"],
            "oos_mdd_improve_share": oo["mdd_improve_share"],
        })
    d = pd.DataFrame(rows2).sort_values("delta_oos_minus_train")
    d.to_csv(OUT / "train_oos_decay.csv", index=False, encoding="utf-8-sig")

    lines = ["# K200 trading-value overlays: train vs OOS", "",
             "Same-direction BASE comparison across 8 factors × HIGH/LOW × Top10/20 × 0/30/60 bps.", ""]
    lines.append("## Train-strong / OOS-weaker candidates")
    lines.append("")
    for _, r in d.head(10).iterrows():
        lines.append(
            f"- {r.overlay}: train improve {r.train_return_improve_share:.0%}, median {r.train_median_return_delta:+.2%}; "
            f"OOS improve {r.oos_return_improve_share:.0%}, median {r.oos_median_return_delta:+.2%}; "
            f"change {r.delta_oos_minus_train:+.2%}"
        )
    lines += ["", "## OOS-stronger candidates", ""]
    for _, r in d.sort_values("delta_oos_minus_train", ascending=False).head(10).iterrows():
        lines.append(
            f"- {r.overlay}: train improve {r.train_return_improve_share:.0%}, median {r.train_median_return_delta:+.2%}; "
            f"OOS improve {r.oos_return_improve_share:.0%}, median {r.oos_median_return_delta:+.2%}; "
            f"change {r.delta_oos_minus_train:+.2%}"
        )
    (OUT / "TRAIN_OOS_COMPARISON.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
