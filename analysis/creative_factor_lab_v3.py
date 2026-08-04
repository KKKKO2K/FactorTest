from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

import creative_factor_lab_v2 as calibrated

lab = calibrated.lab
HERE = Path(__file__).resolve().parent
lab.OUT = HERE / "creative_factor_results_v3"
lab.OUT.mkdir(parents=True, exist_ok=True)
lab.UNIVERSES = ("KOSPI_EX_K200",)
lab.STEPS = (10,)
lab.COSTS = (30, 60, 100)

# The v2 module already patches add_derived_features to create cross-sectional
# ranks and slow four-observation averages. Add a second state layer that asks:
# has this factor actually worked in the recent, fully observable past?
_ORIGINAL_BUILD_PANEL = lab.build_panel


def _rank_ic(x: pd.Series, y: pd.Series) -> float:
    valid = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
    if len(valid) < 25:
        return np.nan
    return valid["x"].rank(method="average").corr(
        valid["y"].rank(method="average")
    )


def add_factor_efficacy(
    panel: pd.DataFrame,
    returns: pd.DataFrame,
    step: int,
    horizon: int = 20,
) -> pd.DataFrame:
    fwd = lab.base.forward_return(returns, horizon)
    dates = list(panel.index.get_level_values("date").unique())
    factor_map = {
        "regime": "regime_score_rank_slow",
        "composite": "composite_alpha_rank_slow",
        "residual": "residual_private_rank_slow",
        "stealth": "stealth_accum_rank_slow",
    }
    date_state = pd.DataFrame(index=pd.Index(dates, name="date"))
    lag = int(math.ceil(horizon / step))
    window = max(8, int(round(126 / step)))  # about six months
    min_periods = max(6, window // 2)

    for label, factor in factor_map.items():
        ics = []
        for dt in dates:
            if dt not in fwd.index:
                ics.append(np.nan)
                continue
            x = panel.xs(dt, level="date")[factor]
            y = fwd.loc[dt].reindex(x.index)
            ics.append(_rank_ic(x, y))
        raw_ic = pd.Series(ics, index=date_state.index, dtype=float)
        known_ic = raw_ic.shift(lag)  # only use IC after its 20-day return is known
        eff_mean = known_ic.rolling(window, min_periods=min_periods).mean()
        eff_hit = (known_ic > 0).rolling(window, min_periods=min_periods).mean()
        date_state[f"{label}_eff_ic"] = eff_mean
        date_state[f"{label}_eff_hit"] = eff_hit
        date_state[f"{label}_eff_on"] = (
            (eff_mean > 0.0) & (eff_hit >= 0.50)
        )

    return panel.join(date_state, on="date")


def build_panel_v3(
    returns: pd.DataFrame,
    basic_panels: dict[pd.Timestamp, pd.DataFrame],
    universe: str,
    step: int,
) -> pd.DataFrame:
    panel = _ORIGINAL_BUILD_PANEL(returns, basic_panels, universe, step)
    return add_factor_efficacy(panel, returns, step)


lab.build_panel = build_panel_v3

# Keep the artifact compact. All signal and trade outputs remain CSVs.
pd.DataFrame.to_pickle = lambda self, *args, **kwargs: None

R = lab.Rule
ge, le = lab.ge, lab.le

lab.RULES = (
    R(
        name="BROAD_REGIME_HYST",
        score_col="regime_score_rank",
        entry=lambda r: ge(r, "regime_score_rank", 0.80)
        and ge(r, "regime_score_rank_slow", 0.55),
        exit=lambda r: le(r, "regime_score_rank", 0.30)
        or le(r, "regime_score_rank_slow", 0.42),
        max_hold_days=120,
        cross_only=False,
        stop_loss=-0.20,
        profit_take=0.60,
    ),
    R(
        name="EFFICACY_REGIME_HYST",
        score_col="regime_score_rank",
        entry=lambda r: bool(r.get("regime_eff_on", False))
        and ge(r, "regime_score_rank", 0.80)
        and ge(r, "regime_score_rank_slow", 0.55),
        exit=lambda r: not bool(r.get("regime_eff_on", False))
        or le(r, "regime_score_rank", 0.30)
        or le(r, "regime_score_rank_slow", 0.42),
        max_hold_days=120,
        cross_only=False,
        stop_loss=-0.20,
        profit_take=0.60,
    ),
    R(
        name="EFFICACY_REGIME_PATIENT",
        score_col="regime_score_rank_slow",
        entry=lambda r: bool(r.get("regime_eff_on", False))
        and ge(r, "regime_score_rank", 0.75)
        and ge(r, "regime_score_rank_slow", 0.55),
        exit=lambda r: not bool(r.get("regime_eff_on", False))
        or le(r, "regime_score_rank", 0.25)
        or le(r, "regime_score_rank_slow", 0.38),
        max_hold_days=160,
        cross_only=False,
        stop_loss=-0.22,
        profit_take=0.65,
    ),
    R(
        name="BROAD_COMPOSITE_HYST",
        score_col="composite_alpha_rank",
        entry=lambda r: ge(r, "composite_alpha_rank", 0.80)
        and ge(r, "composite_alpha_rank_slow", 0.55),
        exit=lambda r: le(r, "composite_alpha_rank", 0.30)
        or le(r, "composite_alpha_rank_slow", 0.42),
        max_hold_days=120,
        cross_only=False,
        stop_loss=-0.20,
        profit_take=0.60,
    ),
    R(
        name="EFFICACY_COMPOSITE_HYST",
        score_col="composite_alpha_rank",
        entry=lambda r: bool(r.get("composite_eff_on", False))
        and ge(r, "composite_alpha_rank", 0.80)
        and ge(r, "composite_alpha_rank_slow", 0.55),
        exit=lambda r: not bool(r.get("composite_eff_on", False))
        or le(r, "composite_alpha_rank", 0.30)
        or le(r, "composite_alpha_rank_slow", 0.42),
        max_hold_days=120,
        cross_only=False,
        stop_loss=-0.20,
        profit_take=0.60,
    ),
    R(
        name="EFFICACY_RESIDUAL_HYST",
        score_col="residual_private_rank",
        entry=lambda r: bool(r.get("residual_eff_on", False))
        and ge(r, "residual_private_rank", 0.80)
        and ge(r, "residual_private_rank_slow", 0.55),
        exit=lambda r: not bool(r.get("residual_eff_on", False))
        or le(r, "residual_private_rank", 0.28)
        or le(r, "residual_private_rank_slow", 0.40),
        max_hold_days=120,
        cross_only=False,
        stop_loss=-0.20,
        profit_take=0.60,
    ),
    R(
        name="EFFICACY_CONDITIONAL_PATH",
        score_col="regime_score_rank",
        entry=lambda r: (
            r.get("regime") == "RISK_ON"
            and bool(r.get("regime_eff_on", False))
            and ge(r, "revision_front_run_rank", 0.70)
            and ge(r, "private_conviction_rank", 0.60)
        )
        or (
            r.get("regime") == "RISK_OFF"
            and bool(r.get("regime_eff_on", False))
            and ge(r, "capitulation_absorption_rank", 0.80)
            and ge(r, "residual_private_rank", 0.55)
        )
        or (
            r.get("regime") == "NEUTRAL"
            and bool(r.get("stealth_eff_on", False))
            and ge(r, "stealth_accum_rank", 0.78)
            and ge(r, "residual_private_rank", 0.60)
        ),
        exit=lambda r: (
            r.get("regime") == "RISK_ON"
            and (
                not bool(r.get("regime_eff_on", False))
                or le(r, "regime_score_rank", 0.30)
            )
        )
        or (
            r.get("regime") == "RISK_OFF"
            and (
                not bool(r.get("regime_eff_on", False))
                or le(r, "capitulation_absorption_rank", 0.35)
            )
        )
        or (
            r.get("regime") == "NEUTRAL"
            and (
                not bool(r.get("stealth_eff_on", False))
                or le(r, "stealth_accum_rank", 0.35)
            )
        ),
        max_hold_days=120,
        cross_only=False,
        stop_loss=-0.20,
        profit_take=0.60,
    ),
    R(
        name="EFFICACY_REGIME_PYRAMID",
        score_col="regime_score_rank",
        entry=lambda r: bool(r.get("regime_eff_on", False))
        and ge(r, "regime_score_rank", 0.78)
        and ge(r, "regime_score_rank_slow", 0.52),
        add=lambda r: bool(r.get("regime_eff_on", False))
        and ge(r, "regime_score_rank", 0.92)
        and ge(r, "revision_front_run_rank", 0.80)
        and ge(r, "private_persist", 0.65),
        reduce=lambda r: le(r, "regime_score_rank", 0.50)
        or le(r, "revision_front_run_rank", 0.40),
        exit=lambda r: not bool(r.get("regime_eff_on", False))
        or le(r, "regime_score_rank", 0.25)
        or le(r, "regime_score_rank_slow", 0.36),
        max_hold_days=150,
        cross_only=False,
        stop_loss=-0.22,
        profit_take=0.65,
        max_units_per_name=2,
    ),
)

if __name__ == "__main__":
    lab.main()
