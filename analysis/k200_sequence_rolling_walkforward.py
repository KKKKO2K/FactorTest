from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
IN = HERE / "k200_sequence_attribution_results" / "variant_period_returns.csv"
OUT = HERE / "k200_sequence_rolling_walkforward_results"
OUT.mkdir(parents=True, exist_ok=True)

STEP = 10
SPLIT = pd.Timestamp("2023-05-26")
VARIANTS = ["FLOW_ONLY", "THREE_ONLY", "FLOW_THREE"]


def overlay_stats(p: pd.DataFrame, dates, variant: str) -> dict:
    x = pd.DataFrame({"base": p.loc[dates, "BASE"], "variant": p.loc[dates, variant]}).dropna()
    if x.empty:
        return {}
    delta = x["variant"] - x["base"]
    rel = (1.0 + x["variant"]) / (1.0 + x["base"]) - 1.0
    n = len(x)
    years = n / (252 / STEP)
    sd = float(delta.std(ddof=1)) if n > 1 else np.nan
    t_stat = float(delta.mean() / sd * math.sqrt(n)) if n > 1 and sd > 0 else np.nan
    active = delta.abs() > 1e-12
    return {
        "n_periods": n,
        "mean_delta_bp": float(delta.mean() * 1e4),
        "median_delta_bp": float(delta.median() * 1e4),
        "hit_rate_all": float((delta > 0).mean()),
        "active_periods": int(active.sum()),
        "hit_rate_active": float((delta[active] > 0).mean()) if active.any() else np.nan,
        "t_stat": t_stat,
        "overlay_relative_cagr": float((1.0 + rel).prod() ** (1 / years) - 1.0),
        "simple_delta_sum": float(delta.sum()),
    }


def era_table(p: pd.DataFrame) -> pd.DataFrame:
    eras = {
        "2017-2019": p.index[p.index < pd.Timestamp("2020-01-01")],
        "2020-2022": p.index[(p.index >= pd.Timestamp("2020-01-01")) & (p.index < pd.Timestamp("2023-01-01"))],
        "2023-2024": p.index[(p.index >= pd.Timestamp("2023-01-01")) & (p.index < pd.Timestamp("2025-01-01"))],
        "2025-2026": p.index[p.index >= pd.Timestamp("2025-01-01")],
        "TRAIN": p.index[p.index < SPLIT],
        "OOS": p.index[p.index >= SPLIT],
    }
    rows = []
    for era, dates in eras.items():
        for variant in VARIANTS:
            rows.append({"era": era, "variant": variant, **overlay_stats(p, dates, variant)})
    return pd.DataFrame(rows)


def calendar_year_table(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for year in sorted(p.index.year.unique()):
        dates = p.index[p.index.year == year]
        for variant in VARIANTS:
            rows.append({"year": int(year), "variant": variant, **overlay_stats(p, dates, variant)})
    return pd.DataFrame(rows)


def rolling_table(p: pd.DataFrame, windows=(30, 50), step=10) -> pd.DataFrame:
    idx = p.index
    rows = []
    for window in windows:
        end_positions = list(range(window - 1, len(idx), step))
        if end_positions[-1] != len(idx) - 1:
            end_positions.append(len(idx) - 1)
        for end_i in end_positions:
            dates = idx[end_i - window + 1 : end_i + 1]
            if len(dates) != window:
                continue
            for variant in VARIANTS:
                rows.append({
                    "window_periods": window,
                    "start": dates[0],
                    "end": dates[-1],
                    "variant": variant,
                    **overlay_stats(p, dates, variant),
                })
    return pd.DataFrame(rows)


def rolling_sign_summary(rolling: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (window, variant), g in rolling.groupby(["window_periods", "variant"]):
        rows.append({
            "window_periods": int(window),
            "variant": variant,
            "n_windows": len(g),
            "positive_mean_fraction": float((g["mean_delta_bp"] > 0).mean()),
            "positive_overlay_fraction": float((g["overlay_relative_cagr"] > 0).mean()),
            "median_window_mean_bp": float(g["mean_delta_bp"].median()),
            "min_window_mean_bp": float(g["mean_delta_bp"].min()),
            "max_window_mean_bp": float(g["mean_delta_bp"].max()),
        })
    return pd.DataFrame(rows)


def expanding_walkforward(p: pd.DataFrame) -> pd.DataFrame:
    """No tuning/selection: compare expanding pre-year evidence with the next calendar year's realized overlay."""
    rows = []
    years = sorted(p.index.year.unique())
    for test_year in years[2:]:
        prior_dates = p.index[p.index.year < test_year]
        test_dates = p.index[p.index.year == test_year]
        for variant in VARIANTS:
            prior = overlay_stats(p, prior_dates, variant)
            test = overlay_stats(p, test_dates, variant)
            if not prior or not test:
                continue
            prior_mean = prior["mean_delta_bp"]
            test_mean = test["mean_delta_bp"]
            rows.append({
                "test_year": int(test_year),
                "variant": variant,
                "prior_n_periods": prior["n_periods"],
                "prior_mean_delta_bp": prior_mean,
                "prior_overlay_relative_cagr": prior["overlay_relative_cagr"],
                "test_n_periods": test["n_periods"],
                "test_mean_delta_bp": test_mean,
                "test_overlay_relative_cagr": test["overlay_relative_cagr"],
                "same_sign": bool(np.sign(prior_mean) == np.sign(test_mean)),
            })
    return pd.DataFrame(rows)


def rolling_predictiveness(p: pd.DataFrame, windows=(20, 30, 50, 75)) -> pd.DataFrame:
    """Diagnostic only: does past rolling sequence efficacy predict the next period's sequence delta?"""
    delta = pd.DataFrame(index=p.index)
    for variant in VARIANTS:
        delta[variant] = p[variant] - p["BASE"]

    rows = []
    for window in windows:
        for variant in VARIANTS:
            hist = delta[variant].rolling(window, min_periods=window).mean().shift(1)
            z = pd.DataFrame({"hist_mean": hist, "next_delta": delta[variant]}).dropna()
            if z.empty:
                continue
            corr = float(z["hist_mean"].corr(z["next_delta"]))
            pos = z[z["hist_mean"] > 0]
            nonpos = z[z["hist_mean"] <= 0]
            rows.append({
                "window_periods": window,
                "variant": variant,
                "n_observations": len(z),
                "past_vs_next_corr": corr,
                "past_positive_n": len(pos),
                "next_mean_bp_if_past_positive": float(pos["next_delta"].mean() * 1e4) if len(pos) else np.nan,
                "next_positive_rate_if_past_positive": float((pos["next_delta"] > 0).mean()) if len(pos) else np.nan,
                "past_nonpositive_n": len(nonpos),
                "next_mean_bp_if_past_nonpositive": float(nonpos["next_delta"].mean() * 1e4) if len(nonpos) else np.nan,
            })
    return pd.DataFrame(rows)


def interaction_table(detail: pd.DataFrame, p: pd.DataFrame) -> pd.DataFrame:
    ft = detail[detail["variant"] == "FLOW_THREE"].copy().set_index("date")
    ft["delta_flow_three"] = p["FLOW_THREE"] - p["BASE"]
    ft["delta_flow"] = p["FLOW_ONLY"] - p["BASE"]
    ft["delta_three"] = p["THREE_ONLY"] - p["BASE"]
    # Exact period-return interaction after each independently simulated turnover path.
    ft["interaction"] = ft["delta_flow_three"] - ft["delta_flow"] - ft["delta_three"]
    ft["event_presence"] = np.select(
        [
            (ft["flow_names"] > 0) & (ft["three_names"] > 0),
            (ft["flow_names"] > 0) & (ft["three_names"] == 0),
            (ft["flow_names"] == 0) & (ft["three_names"] > 0),
        ],
        ["BOTH", "FLOW_ONLY_PRESENT", "THREE_ONLY_PRESENT"],
        default="NONE",
    )

    rows = []
    samples = {
        "TRAIN": ft.index < SPLIT,
        "OOS": ft.index >= SPLIT,
        "ALL": pd.Series(True, index=ft.index),
    }
    for sample, mask in samples.items():
        sub = ft.loc[mask]
        for bucket, g in sub.groupby("event_presence"):
            rows.append({
                "sample": sample,
                "event_presence": bucket,
                "n_periods": len(g),
                "flow_three_mean_delta_bp": float(g["delta_flow_three"].mean() * 1e4),
                "flow_mean_delta_bp": float(g["delta_flow"].mean() * 1e4),
                "three_mean_delta_bp": float(g["delta_three"].mean() * 1e4),
                "interaction_mean_bp": float(g["interaction"].mean() * 1e4),
                "flow_three_positive_rate": float((g["delta_flow_three"] > 0).mean()),
                "interaction_positive_rate": float((g["interaction"] > 0).mean()),
                "avg_flow_names": float(g["flow_names"].mean()),
                "avg_three_names": float(g["three_names"].mean()),
            })
    return pd.DataFrame(rows)


def main():
    detail = pd.read_csv(IN, parse_dates=["date"])
    p = detail.pivot(index="date", columns="variant", values="net").sort_index()

    required = {"BASE", *VARIANTS}
    missing = required.difference(p.columns)
    if missing:
        raise RuntimeError(f"Missing variants: {sorted(missing)}")

    era = era_table(p)
    yearly = calendar_year_table(p)
    rolling = rolling_table(p)
    rolling_summary = rolling_sign_summary(rolling)
    walkforward = expanding_walkforward(p)
    predictiveness = rolling_predictiveness(p)
    interaction = interaction_table(detail, p)

    era.to_csv(OUT / "era_stability.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(OUT / "calendar_year_stability.csv", index=False, encoding="utf-8-sig")
    rolling.to_csv(OUT / "rolling_windows.csv", index=False, encoding="utf-8-sig")
    rolling_summary.to_csv(OUT / "rolling_sign_summary.csv", index=False, encoding="utf-8-sig")
    walkforward.to_csv(OUT / "expanding_walkforward_years.csv", index=False, encoding="utf-8-sig")
    predictiveness.to_csv(OUT / "rolling_predictiveness.csv", index=False, encoding="utf-8-sig")
    interaction.to_csv(OUT / "flow_three_interaction.csv", index=False, encoding="utf-8-sig")

    print("=== ERA STABILITY ===")
    print(era.to_string(index=False))
    print("\n=== CALENDAR YEAR MEAN DELTA BP ===")
    print(yearly.pivot(index="year", columns="variant", values="mean_delta_bp").to_string())
    print("\n=== ROLLING SIGN SUMMARY ===")
    print(rolling_summary.to_string(index=False))
    print("\n=== EXPANDING WALK-FORWARD ===")
    print(walkforward.to_string(index=False))
    print("\n=== ROLLING EFFICACY PREDICTIVENESS ===")
    print(predictiveness.to_string(index=False))
    print("\n=== FLOW x THREE INTERACTION ===")
    print(interaction.to_string(index=False))


if __name__ == "__main__":
    main()
