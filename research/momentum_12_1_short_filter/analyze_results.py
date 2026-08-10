from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
OOS_START = pd.Timestamp("2023-01-01")
PERIODS_PER_YEAR = 252.0 / 10.0
BASE = "MOM12_1_BASE"


def max_drawdown(r: pd.Series) -> float:
    if r.empty:
        return np.nan
    nav = (1.0 + r.fillna(0.0)).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def ann_return(r: pd.Series) -> float:
    if r.empty:
        return np.nan
    return float((1.0 + r).prod() ** (PERIODS_PER_YEAR / len(r)) - 1.0)


def sharpe(r: pd.Series) -> float:
    if len(r) < 3 or r.std(ddof=1) <= 0:
        return np.nan
    return float(r.mean() / r.std(ddof=1) * math.sqrt(PERIODS_PER_YEAR))


def summarize_split(periods: pd.DataFrame) -> pd.DataFrame:
    x = periods.copy()
    x["date"] = pd.to_datetime(x["date"])
    x["sample"] = np.where(x["date"] < OOS_START, "IS_PRE_2023", "OOS_2023_PLUS")
    x = pd.concat([x, x.assign(sample="FULL")], ignore_index=True)

    rows: list[dict] = []
    keys = ["sample", "variant", "top_n", "weighting", "cost_bps"]
    for k, g in x.groupby(keys, dropna=False):
        g = g.sort_values("date")
        rows.append(
            {
                "sample": k[0],
                "variant": k[1],
                "top_n": k[2],
                "weighting": k[3],
                "cost_bps": k[4],
                "n_periods": len(g),
                "annualized_return": ann_return(g["net"]),
                "annualized_excess": ann_return(g["excess_net"]),
                "sharpe": sharpe(g["net"]),
                "excess_sharpe": sharpe(g["excess_net"]),
                "mdd": max_drawdown(g["net"]),
                "avg_turnover": float(g["turnover"].mean()),
                "hit_rate": float((g["net"] > 0).mean()),
                "excess_hit_rate": float((g["excess_net"] > 0).mean()),
                "avg_rank_ic": float(g["rank_ic"].mean()),
            }
        )
    return pd.DataFrame(rows)


def paired_vs_base(periods: pd.DataFrame) -> pd.DataFrame:
    x = periods.copy()
    x["date"] = pd.to_datetime(x["date"])
    x["sample"] = np.where(x["date"] < OOS_START, "IS_PRE_2023", "OOS_2023_PLUS")
    x = pd.concat([x, x.assign(sample="FULL")], ignore_index=True)

    rows: list[dict] = []
    group = ["sample", "top_n", "weighting", "cost_bps"]
    for keys, g in x.groupby(group, dropna=False):
        base = g[g["variant"] == BASE][["date", "net", "turnover"]].rename(
            columns={"net": "base_net", "turnover": "base_turnover"}
        )
        if base.empty:
            continue
        for variant, v in g[g["variant"] != BASE].groupby("variant"):
            p = v[["date", "net", "turnover"]].merge(base, on="date", how="inner")
            if len(p) < 3:
                continue
            delta = p["net"] - p["base_net"]
            sd = delta.std(ddof=1)
            tstat = float(delta.mean() / sd * math.sqrt(len(delta))) if sd > 0 else np.nan
            relative_ann = float(
                ((1.0 + p["net"]).prod() / (1.0 + p["base_net"]).prod())
                ** (PERIODS_PER_YEAR / len(p))
                - 1.0
            )
            rows.append(
                {
                    "sample": keys[0],
                    "variant": variant,
                    "top_n": keys[1],
                    "weighting": keys[2],
                    "cost_bps": keys[3],
                    "n_periods": len(p),
                    "mean_period_uplift": float(delta.mean()),
                    "paired_tstat": tstat,
                    "positive_uplift_rate": float((delta > 0).mean()),
                    "relative_annualized_return": relative_ann,
                    "avg_turnover_delta": float((p["turnover"] - p["base_turnover"]).mean()),
                }
            )
    return pd.DataFrame(rows)


def robustness_table(split: pd.DataFrame, paired: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for sample in ("FULL", "OOS_2023_PLUS"):
        s = split[split["sample"] == sample]
        p = paired[paired["sample"] == sample]
        base = s[s["variant"] == BASE][
            ["top_n", "weighting", "cost_bps", "annualized_return", "sharpe", "mdd"]
        ].rename(
            columns={
                "annualized_return": "base_ann_return",
                "sharpe": "base_sharpe",
                "mdd": "base_mdd",
            }
        )
        for variant in sorted(v for v in s["variant"].unique() if v != BASE):
            v = s[s["variant"] == variant].merge(
                base, on=["top_n", "weighting", "cost_bps"], how="inner"
            )
            pv = p[p["variant"] == variant]
            n = len(v)
            if n == 0:
                continue
            rows.append(
                {
                    "sample": sample,
                    "variant": variant,
                    "n_configs": n,
                    "beat_base_return_share": float((v["annualized_return"] > v["base_ann_return"]).mean()),
                    "beat_base_sharpe_share": float((v["sharpe"] > v["base_sharpe"]).mean()),
                    "improve_mdd_share": float((v["mdd"] > v["base_mdd"]).mean()),
                    "paired_positive_share": float((pv["mean_period_uplift"] > 0).mean()) if len(pv) else np.nan,
                    "paired_tstat_gt_1_96_share": float((pv["paired_tstat"] > 1.96).mean()) if len(pv) else np.nan,
                    "median_relative_ann_return": float(pv["relative_annualized_return"].median()) if len(pv) else np.nan,
                }
            )
    return pd.DataFrame(rows)


def write_note(split: pd.DataFrame, paired: pd.DataFrame, robust: pd.DataFrame) -> None:
    key_filter = (
        (split["top_n"] == 10)
        & (split["weighting"] == "equal")
        & (split["cost_bps"] == 30)
    )
    key = split[key_filter].copy()
    key_pair = paired[
        (paired["top_n"] == 10)
        & (paired["weighting"] == "equal")
        & (paired["cost_bps"] == 30)
    ].copy()

    lines = [
        "# MOM12-1 × 1M Filter: automated result note",
        "",
        f"Fixed OOS split: `{OOS_START.date()}`. This cutoff is declared in code, not selected from results.",
        "Key construction: Top10 / equal-weight / 30 bps one-way turnover cost.",
        "",
    ]

    for sample in ("FULL", "OOS_2023_PLUS"):
        lines += [f"## {sample}", ""]
        ks = key[key["sample"] == sample].sort_values("annualized_return", ascending=False)
        for _, r in ks.iterrows():
            lines.append(
                f"- {r['variant']}: ann {r['annualized_return']:.2%}, "
                f"Sharpe {r['sharpe']:.2f}, MDD {r['mdd']:.2%}, "
                f"turnover {r['avg_turnover']:.2f}"
            )
        lines.append("")
        kp = key_pair[key_pair["sample"] == sample].sort_values(
            "relative_annualized_return", ascending=False
        )
        lines.append("Paired uplift vs baseline:")
        for _, r in kp.iterrows():
            lines.append(
                f"- {r['variant']}: relative ann {r['relative_annualized_return']:.2%}, "
                f"paired t {r['paired_tstat']:.2f}, win {r['positive_uplift_rate']:.1%}"
            )
        lines.append("")

    lines += ["## Robustness across 24 portfolio/cost configurations", ""]
    for _, r in robust.sort_values(["sample", "beat_base_return_share"], ascending=[True, False]).iterrows():
        lines.append(
            f"- {r['sample']} / {r['variant']}: return beat {r['beat_base_return_share']:.0%}, "
            f"Sharpe beat {r['beat_base_sharpe_share']:.0%}, "
            f"MDD improve {r['improve_mdd_share']:.0%}, "
            f"median relative ann {r['median_relative_ann_return']:.2%}"
        )

    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    periods = pd.read_csv(OUT / "period_returns.csv", encoding="utf-8-sig")
    split = summarize_split(periods)
    paired = paired_vs_base(periods)
    robust = robustness_table(split, paired)

    split.to_csv(OUT / "is_oos_summary.csv", index=False, encoding="utf-8-sig")
    paired.to_csv(OUT / "paired_vs_base.csv", index=False, encoding="utf-8-sig")
    robust.to_csv(OUT / "robustness_vs_base.csv", index=False, encoding="utf-8-sig")
    write_note(split, paired, robust)


if __name__ == "__main__":
    main()
