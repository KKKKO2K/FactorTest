from __future__ import annotations

from pathlib import Path
import pandas as pd

import run_weighted_momentum_filter_exact as exact

m = exact.m
HERE = Path(__file__).resolve().parent
m.OUT = HERE / "results_threshold"
m.OUT.mkdir(parents=True, exist_ok=True)

# Exact neighboring cutoffs around the pre-specified 0% gate.
m.THRESHOLDS_PCT = (-10.0, -5.0, 0.0, 5.0, 10.0)


def write_threshold_decision_tables() -> None:
    paired = pd.read_csv(m.OUT / "paired_summary.csv", encoding="utf-8-sig")
    summary = pd.read_csv(m.OUT / "summary.csv", encoding="utf-8-sig")

    # Main decision surface: incremental value vs unfiltered weighted momentum.
    z = paired[paired["cost_bp"].eq(30)].copy()
    z["threshold_pct"] = z["strategy"].str.extract(r"_GE_([PM]\d+)$")[0].map(
        lambda x: float(x[1:]) if isinstance(x, str) and x.startswith("P") else (-float(x[1:]) if isinstance(x, str) and x.startswith("M") else None)
    )
    z = z.dropna(subset=["threshold_pct"])
    cols = [
        "universe", "period", "threshold_pct", "n_phases",
        "median_delta_cagr", "median_delta_excess_cagr", "median_delta_sharpe",
        "median_delta_mdd", "cagr_better_phases", "excess_better_phases",
    ]
    z[cols].sort_values(["period", "universe", "threshold_pct"]).to_csv(
        m.OUT / "threshold_incremental_net30.csv", index=False, encoding="utf-8-sig"
    )

    # Absolute strategy performance at NET30.
    s = summary[summary["cost_bp"].eq(30)].copy()
    s["threshold_pct"] = s["strategy"].str.extract(r"_GE_([PM]\d+)$")[0].map(
        lambda x: float(x[1:]) if isinstance(x, str) and x.startswith("P") else (-float(x[1:]) if isinstance(x, str) and x.startswith("M") else None)
    )
    s = s.dropna(subset=["threshold_pct"])
    perf_cols = [
        "universe", "period", "threshold_pct", "median_cagr", "median_mdd",
        "median_sharpe", "median_excess_cagr", "median_turnover",
        "positive_cagr_phases", "positive_excess_phases",
    ]
    s[perf_cols].sort_values(["period", "universe", "threshold_pct"]).to_csv(
        m.OUT / "threshold_absolute_net30.csv", index=False, encoding="utf-8-sig"
    )

    # Compact markdown for the most decision-relevant periods.
    focus = ["PRE_STRESS_2017_2024", "EARLY_2017_2019", "LATE_2020_2022", "NORMAL_2023_2024", "BULL_2025", "YTD_2026"]
    lines = [
        "# Weighted Momentum 1M Threshold Sensitivity",
        "",
        "Exact legacy signal and portfolio construction are unchanged. Only the 1M gate changes:",
        "`R1M >= {-10%, -5%, 0%, +5%, +10%}`.",
        "All values below are NET30 paired median delta CAGR versus unfiltered WEIGHTED_MOM, with phase win count in parentheses.",
        "",
    ]
    for period in focus:
        q = z[z["period"].eq(period)]
        if q.empty:
            continue
        lines.append(f"## {period}")
        lines.append("")
        lines.append("| Universe | -10% | -5% | 0% | +5% | +10% |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for u in m.UNIVERSES:
            qu = q[q["universe"].eq(u)].set_index("threshold_pct")
            vals = []
            for t in (-10.0, -5.0, 0.0, 5.0, 10.0):
                if t in qu.index:
                    r = qu.loc[t]
                    vals.append(f"{r.median_delta_cagr:+.2%} ({int(r.cagr_better_phases)}/{int(r.n_phases)})")
                else:
                    vals.append("NA")
            lines.append("| " + u + " | " + " | ".join(vals) + " |")
        lines.append("")

    (m.OUT / "THRESHOLD_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    exact.main()
    write_threshold_decision_tables()
