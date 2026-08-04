from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

import creative_factor_lab as lab

HERE = Path(__file__).resolve().parent
lab.OUT = HERE / "creative_factor_results_v2"
lab.OUT.mkdir(parents=True, exist_ok=True)
lab.UNIVERSES = ("KOSPI_EX_K200",)
lab.STEPS = (5, 10)
lab.COSTS = (30, 60, 100)

_BASE_ADD = lab.add_derived_features


def add_rank_calibrated_features(panel: pd.DataFrame) -> pd.DataFrame:
    panel = _BASE_ADD(panel)
    score_cols = [
        "regime_score",
        "stealth_accum",
        "composite_alpha",
        "residual_private",
        "private_conviction",
        "revision_front_run",
        "capitulation_absorption",
        "flow_price_divergence",
        "crowding_exhaustion",
    ]
    by_date = panel.groupby(level="date", group_keys=False)
    for col in score_cols:
        panel[f"{col}_rank"] = by_date[col].rank(pct=True)
    by_code = panel.groupby(level="code", group_keys=False)
    for col in [
        "regime_score_rank",
        "stealth_accum_rank",
        "composite_alpha_rank",
        "residual_private_rank",
        "private_conviction_rank",
        "revision_front_run_rank",
        "capitulation_absorption_rank",
    ]:
        panel[f"{col}_slow"] = by_code[col].transform(
            lambda s: s.rolling(4, min_periods=2).mean()
        )
        panel[f"{col}_lag1"] = by_code[col].shift(1)
    return panel


lab.add_derived_features = add_rank_calibrated_features
lab.DERIVED_COLS = (
    "regime_score",
    "regime_score_rank_slow",
    "stealth_accum",
    "stealth_accum_rank_slow",
    "composite_alpha",
    "composite_alpha_rank_slow",
    "residual_private",
    "residual_private_rank_slow",
    "private_conviction",
    "revision_front_run",
    "capitulation_absorption",
    "flow_price_divergence",
    "crowding_exhaustion",
)


def derived_ic_rank(
    panel: pd.DataFrame,
    returns: pd.DataFrame,
    universe: str,
    step: int,
    horizon: int = 20,
):
    fwd = lab.base.forward_return(returns, horizon)
    rows = []
    for dt in panel.index.get_level_values("date").unique():
        if dt not in fwd.index:
            continue
        x = panel.xs(dt, level="date")
        y = fwd.loc[dt].reindex(x.index)
        for factor in lab.DERIVED_COLS:
            valid = pd.concat([x[factor], y.rename("future")], axis=1).dropna()
            if len(valid) < 25:
                continue
            ic = valid[factor].rank(method="average").corr(
                valid["future"].rank(method="average")
            )
            rows.append(
                {
                    "date": dt,
                    "universe": universe,
                    "step": step,
                    "factor": factor,
                    "ic": ic,
                    "n": len(valid),
                }
            )
    detail = pd.DataFrame(rows)
    summaries = []
    for factor, g0 in detail.groupby("factor"):
        for sample, lo, hi in (
            ("train", lab.START, lab.SPLIT),
            ("test", lab.SPLIT, None),
        ):
            g = g0[g0["date"] >= lo]
            if hi is not None:
                g = g[g["date"] < hi]
            g = g.dropna(subset=["ic"])
            if len(g) < 8:
                continue
            sd = g["ic"].std(ddof=1)
            summaries.append(
                {
                    "universe": universe,
                    "step": step,
                    "factor": factor,
                    "sample": sample,
                    "mean_ic": g["ic"].mean(),
                    "ic_tstat": g["ic"].mean() / (sd / math.sqrt(len(g)))
                    if sd > 0
                    else np.nan,
                    "ic_hit_rate": (g["ic"] > 0).mean(),
                    "n_dates": len(g),
                    "avg_n": g["n"].mean(),
                }
            )
    return detail, pd.DataFrame(summaries)


lab.derived_ic = derived_ic_rank

R = lab.Rule
ge, le, between = lab.ge, lab.le, lab.between

lab.RULES = (
    R(
        name="REGIME_HYSTERESIS",
        score_col="regime_score_rank",
        entry=lambda r: ge(r, "regime_score_rank", 0.90)
        and ge(r, "regime_score_rank_slow", 0.68),
        exit=lambda r: le(r, "regime_score_rank", 0.43)
        or le(r, "regime_score_rank_slow", 0.52),
        max_hold_days=90,
        cross_only=False,
        profit_take=0.45,
    ),
    R(
        name="STEALTH_HYSTERESIS",
        score_col="stealth_accum_rank",
        entry=lambda r: ge(r, "stealth_accum_rank", 0.90)
        and ge(r, "stealth_accum_rank_slow", 0.65)
        and ge(r, "residual_private_rank", 0.60),
        exit=lambda r: le(r, "stealth_accum_rank", 0.42)
        or ge(r, "crowding_exhaustion_rank", 0.90),
        max_hold_days=90,
        cross_only=False,
        profit_take=0.45,
    ),
    R(
        name="RESIDUAL_HYSTERESIS",
        score_col="residual_private_rank",
        entry=lambda r: ge(r, "residual_private_rank", 0.90)
        and ge(r, "private_persist", 0.52),
        exit=lambda r: le(r, "residual_private_rank", 0.38)
        or le(r, "private_level", 0.32),
        max_hold_days=80,
        cross_only=False,
        profit_take=0.45,
    ),
    R(
        name="COMPOSITE_HYSTERESIS",
        score_col="composite_alpha_rank",
        entry=lambda r: ge(r, "composite_alpha_rank", 0.90)
        and ge(r, "composite_alpha_rank_slow", 0.66),
        exit=lambda r: le(r, "composite_alpha_rank", 0.43)
        or le(r, "composite_alpha_rank_slow", 0.50),
        max_hold_days=90,
        cross_only=False,
        profit_take=0.45,
    ),
    R(
        name="REGIME_CROSS",
        score_col="regime_score_rank",
        entry=lambda r: ge(r, "regime_score_rank", 0.86),
        exit=lambda r: le(r, "regime_score_rank", 0.48),
        max_hold_days=70,
        cross_only=True,
        profit_take=0.45,
    ),
    R(
        name="SLOW_COMPOSITE_CROSS",
        score_col="composite_alpha_rank_slow",
        entry=lambda r: ge(r, "composite_alpha_rank_slow", 0.82)
        and ge(r, "composite_alpha_rank", 0.72),
        exit=lambda r: le(r, "composite_alpha_rank_slow", 0.52),
        max_hold_days=100,
        cross_only=True,
        profit_take=0.50,
    ),
    R(
        name="CONDITIONAL_DUAL_PATH",
        score_col="regime_score_rank",
        entry=lambda r: (
            r.get("regime") == "RISK_ON"
            and ge(r, "revision_front_run_rank", 0.85)
            and ge(r, "private_conviction_rank", 0.65)
        )
        or (
            r.get("regime") == "RISK_OFF"
            and ge(r, "capitulation_absorption_rank", 0.85)
            and ge(r, "residual_private_rank", 0.60)
        )
        or (
            r.get("regime") == "NEUTRAL"
            and ge(r, "stealth_accum_rank", 0.85)
            and ge(r, "residual_private_rank", 0.70)
        ),
        exit=lambda r: le(r, "regime_score_rank", 0.42)
        or ge(r, "crowding_exhaustion_rank", 0.93),
        max_hold_days=80,
        cross_only=True,
        profit_take=0.45,
    ),
    R(
        name="ANTI_CROWDING_COMPOSITE",
        score_col="composite_alpha_rank",
        entry=lambda r: ge(r, "composite_alpha_rank", 0.86)
        and le(r, "crowding_exhaustion_rank", 0.72)
        and ge(r, "private_persist", 0.55),
        exit=lambda r: le(r, "composite_alpha_rank", 0.42)
        or ge(r, "crowding_exhaustion_rank", 0.88),
        max_hold_days=80,
        cross_only=False,
        profit_take=0.45,
    ),
    R(
        name="REGIME_PYRAMID",
        score_col="regime_score_rank",
        entry=lambda r: ge(r, "regime_score_rank", 0.86)
        and ge(r, "regime_score_rank_slow", 0.62),
        add=lambda r: ge(r, "regime_score_rank", 0.95)
        and ge(r, "revision_front_run_rank", 0.80)
        and ge(r, "private_persist", 0.68),
        reduce=lambda r: le(r, "regime_score_rank", 0.58)
        or le(r, "revision_front_run_rank", 0.42),
        exit=lambda r: le(r, "regime_score_rank", 0.38)
        or ge(r, "crowding_exhaustion_rank", 0.92),
        max_hold_days=90,
        cross_only=False,
        profit_take=0.50,
        max_units_per_name=2,
    ),
)

if __name__ == "__main__":
    lab.main()
