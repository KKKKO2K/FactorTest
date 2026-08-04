from __future__ import annotations

import importlib.util
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "creative_factor_results"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location(
    "base_rules", HERE / "test_transparent_new_factor_rules.py"
)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

START = pd.Timestamp("2017-01-02")
SPLIT = pd.Timestamp("2023-05-26")
END = pd.Timestamp("2026-07-31")
UNIVERSES = ("KOSPI_EX_K200", "KOSDAQ", "K200")
STEPS = (5, 10)
COSTS = (30, 60, 100)
MAX_UNITS = 30
COOLDOWN_STEPS = 2
DERIVED_COLS = (
    "private_level",
    "private_accel_rank",
    "private_persist",
    "private_conviction",
    "residual_private",
    "abnormal_private",
    "stealth_accum",
    "capitulation_absorption",
    "revision_front_run",
    "flow_price_divergence",
    "crowding_heat",
    "crowding_exhaustion",
    "composite_alpha",
    "regime_score",
)


def pct_rank(s: pd.Series, high_good: bool = True) -> pd.Series:
    """Cross-sectional percentile, 1 = best."""
    x = pd.to_numeric(s, errors="coerce")
    return x.rank(pct=True, method="average", ascending=high_good)


def safe_mean(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    return frame[cols].mean(axis=1, skipna=True)


def universe_codes(basic_panel: pd.DataFrame, universe: str) -> pd.Index:
    market = basic_panel["market"].astype(str).str.upper()
    if universe == "KOSPI_EX_K200":
        mask = market.str.contains("KOSPI", na=False) & (basic_panel["k200"] == 0)
    elif universe == "KOSDAQ":
        mask = market.str.contains("KOSDAQ", na=False)
    elif universe == "K200":
        mask = basic_panel["k200"] == 1
    else:
        raise KeyError(universe)
    return basic_panel.index[mask]


def trailing_stock_return(returns: pd.DataFrame, dt: pd.Timestamp, codes: pd.Index, days: int) -> pd.Series:
    hist = returns.loc[:dt, codes].tail(days)
    if hist.empty:
        return pd.Series(index=codes, dtype=float)
    return (1.0 + hist.fillna(0.0)).prod(axis=0) - 1.0


def trailing_stock_vol(returns: pd.DataFrame, dt: pd.Timestamp, codes: pd.Index, days: int) -> pd.Series:
    hist = returns.loc[:dt, codes].tail(days)
    return hist.std(axis=0, ddof=1) * math.sqrt(252)


def market_snapshot(returns: pd.DataFrame, dt: pd.Timestamp, codes: pd.Index) -> dict[str, float]:
    hist20 = returns.loc[:dt, codes].tail(20)
    hist60 = returns.loc[:dt, codes].tail(60)
    stock60 = (1.0 + hist60.fillna(0.0)).prod(axis=0) - 1.0
    ew60 = float(stock60.mean()) if len(stock60) else np.nan
    breadth60 = float((stock60 > 0).mean()) if len(stock60) else np.nan
    ew_daily20 = hist20.mean(axis=1, skipna=True)
    ew_vol20 = float(ew_daily20.std(ddof=1) * math.sqrt(252)) if len(ew_daily20) > 2 else np.nan
    dispersion20 = float(hist20.std(axis=1, ddof=1).mean() * math.sqrt(252)) if not hist20.empty else np.nan
    return {
        "market60": ew60,
        "breadth60": breadth60,
        "market_vol20": ew_vol20,
        "dispersion20": dispersion20,
    }


def raw_snapshot(
    dt: pd.Timestamp,
    universe: str,
    returns: pd.DataFrame,
    basic_panels: dict[pd.Timestamp, pd.DataFrame],
    factor_cache: dict[tuple[str, pd.Timestamp], pd.Series],
) -> pd.DataFrame:
    basic_panel = basic_panels[dt]
    codes = universe_codes(basic_panel, universe)
    x = pd.DataFrame(index=codes)
    for key, folder in base.FACTOR_DIRS.items():
        cache_key = (key, dt)
        if cache_key not in factor_cache:
            factor_cache[cache_key] = base.load_factor(folder, dt)
        x[key] = factor_cache[cache_key].reindex(codes)

    x["mcap"] = basic_panel["mcap"].reindex(codes)
    x["size_rank"] = pct_rank(np.log1p(x["mcap"]), True)
    x["private_level"] = pct_rank(x["private"], True)
    x["foreign_buy"] = pct_rank(x["foreign"], True)
    x["foreign_sell"] = pct_rank(x["foreign"], False)
    x["short_up"] = pct_rank(x["short"], True)
    x["short_reversal"] = pct_rank(x["short"], False)
    x["long_up"] = pct_rank(x["long"], True)
    x["long_contrarian"] = pct_rank(x["long"], False)
    x["op12_level"] = pct_rank(x["op12"], True)
    x["opfy1_level"] = pct_rank(x["opfy1"], True)
    x["revision_level"] = safe_mean(x, ["op12_level", "opfy1_level"])
    x["cheap_per"] = pct_rank(x["per"], False)
    x["cheap_pbr"] = pct_rank(x["pbr"], False)
    x["value"] = safe_mean(x, ["cheap_per", "cheap_pbr"])

    r20 = trailing_stock_return(returns, dt, codes, 20)
    r60 = trailing_stock_return(returns, dt, codes, 60)
    vol20 = trailing_stock_vol(returns, dt, codes, 20)
    x["ret20_rank"] = pct_rank(r20, True)
    x["ret20_reversal"] = pct_rank(r20, False)
    x["ret60_rank"] = pct_rank(r60, True)
    x["vol20_rank"] = pct_rank(vol20, True)
    x["quiet_price"] = (1.0 - 2.0 * (x["short_up"] - 0.50).abs()).clip(0.0, 1.0)

    market = market_snapshot(returns, dt, codes)
    for key, value in market.items():
        x[key] = value
    x["date"] = dt
    x["code"] = x.index
    return x.reset_index(drop=True).set_index(["date", "code"])


def cross_sectional_residual(group: pd.DataFrame) -> pd.Series:
    cols = ["size_rank", "short_up", "long_up", "foreign_buy", "revision_level", "value"]
    use = group[["private_level", *cols]].dropna()
    out = pd.Series(index=group.index, dtype=float)
    if len(use) < max(25, len(cols) + 5):
        return out
    y = use["private_level"].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(use)), use[cols].to_numpy(dtype=float)])
    try:
        beta, *_ = np.linalg.lstsq(X, y, rcond=None)
        resid = y - X @ beta
    except np.linalg.LinAlgError:
        return out
    out.loc[use.index] = resid
    return out


def add_derived_features(panel: pd.DataFrame) -> pd.DataFrame:
    panel = panel.sort_index().copy()
    by_code = panel.groupby(level="code", group_keys=False)

    panel["private_lag1"] = by_code["private_level"].shift(1)
    panel["private_lag4"] = by_code["private_level"].shift(4)
    panel["foreign_lag4"] = by_code["foreign_buy"].shift(4)
    panel["revision_lag4"] = by_code["revision_level"].shift(4)
    panel["short_lag4"] = by_code["short_up"].shift(4)
    panel["private_accel_5"] = panel["private_level"] - panel["private_lag1"]
    panel["private_accel_20"] = panel["private_level"] - panel["private_lag4"]
    panel["foreign_accel_20"] = panel["foreign_buy"] - panel["foreign_lag4"]
    panel["revision_accel_20"] = panel["revision_level"] - panel["revision_lag4"]
    panel["short_accel_20"] = panel["short_up"] - panel["short_lag4"]

    panel["private_persist"] = by_code["private_level"].transform(
        lambda s: s.rolling(4, min_periods=2).mean()
    )
    panel["private_rank_std"] = by_code["private_level"].transform(
        lambda s: s.rolling(4, min_periods=2).std(ddof=1)
    )
    panel["private_hist_mean"] = by_code["private_level"].transform(
        lambda s: s.rolling(12, min_periods=6).mean()
    )
    panel["private_hist_std"] = by_code["private_level"].transform(
        lambda s: s.rolling(12, min_periods=6).std(ddof=1)
    )
    panel["private_abnormal_raw"] = (
        (panel["private_level"] - panel["private_hist_mean"])
        / panel["private_hist_std"].replace(0, np.nan)
    ).clip(-5, 5)

    by_date = panel.groupby(level="date", group_keys=False)
    panel["private_accel_rank"] = by_date["private_accel_20"].rank(pct=True)
    panel["private_accel5_rank"] = by_date["private_accel_5"].rank(pct=True)
    panel["foreign_accel_rank"] = by_date["foreign_accel_20"].rank(pct=True)
    panel["revision_accel_rank"] = by_date["revision_accel_20"].rank(pct=True)
    panel["short_accel_rank"] = by_date["short_accel_20"].rank(pct=True)
    panel["private_stability"] = by_date["private_rank_std"].rank(pct=True, ascending=False)
    panel["abnormal_private"] = by_date["private_abnormal_raw"].rank(pct=True)

    residual = panel.groupby(level="date", group_keys=False).apply(cross_sectional_residual)
    if isinstance(residual.index, pd.MultiIndex) and residual.index.nlevels > panel.index.nlevels:
        residual.index = residual.index.droplevel(0)
    panel["private_residual_raw"] = residual.reindex(panel.index)
    panel["residual_private"] = panel.groupby(level="date")["private_residual_raw"].rank(pct=True)

    panel["private_conviction"] = (
        0.30 * panel["private_level"]
        + 0.25 * panel["private_persist"]
        + 0.20 * panel["private_stability"]
        + 0.25 * panel["abnormal_private"]
    )
    panel["flow_price_divergence"] = (
        0.45 * panel["private_level"]
        + 0.30 * panel["private_accel_rank"]
        + 0.25 * panel["short_reversal"]
    )
    panel["capitulation_absorption"] = (
        0.35 * panel["private_level"]
        + 0.25 * panel["foreign_sell"]
        + 0.25 * panel["short_reversal"]
        + 0.15 * panel["ret20_reversal"]
    )
    panel["stealth_accum"] = (
        0.35 * panel["residual_private"]
        + 0.25 * panel["private_persist"]
        + 0.20 * panel["abnormal_private"]
        + 0.20 * panel["quiet_price"]
    )
    panel["revision_front_run"] = (
        0.30 * panel["private_accel_rank"]
        + 0.25 * panel["residual_private"]
        + 0.25 * panel["revision_accel_rank"]
        + 0.20 * (1.0 - panel["revision_level"])
    )
    panel["crowding_heat"] = safe_mean(
        panel, ["private_level", "foreign_buy", "short_up", "long_up"]
    )
    panel["crowding_exhaustion"] = (
        0.55 * panel["crowding_heat"]
        + 0.25 * (1.0 - panel["private_accel_rank"])
        + 0.20 * (1.0 - panel["revision_accel_rank"])
    )
    panel["factor_disagreement"] = panel[
        ["private_level", "foreign_buy", "short_up", "long_up", "revision_level", "value"]
    ].std(axis=1, ddof=1)
    panel["composite_alpha"] = (
        0.23 * panel["private_conviction"]
        + 0.22 * panel["residual_private"]
        + 0.20 * panel["revision_front_run"]
        + 0.20 * panel["capitulation_absorption"]
        + 0.10 * panel["value"]
        + 0.05 * panel["factor_disagreement"].clip(0, 1)
    )

    date_state = (
        panel.reset_index()
        .groupby("date", as_index=True)
        .agg(
            market60=("market60", "first"),
            breadth60=("breadth60", "first"),
            dispersion20=("dispersion20", "first"),
            market_vol20=("market_vol20", "first"),
        )
        .sort_index()
    )
    date_state["dispersion_median"] = (
        date_state["dispersion20"].rolling(52, min_periods=12).median().shift(1)
    )
    date_state["high_dispersion"] = (
        date_state["dispersion20"] > date_state["dispersion_median"]
    )
    date_state["regime"] = "NEUTRAL"
    date_state.loc[
        (date_state["market60"] > 0.03) & (date_state["breadth60"] > 0.55),
        "regime",
    ] = "RISK_ON"
    date_state.loc[
        (date_state["market60"] < -0.03) & (date_state["breadth60"] < 0.45),
        "regime",
    ] = "RISK_OFF"

    panel = panel.join(date_state[["regime", "high_dispersion"]], on="date")
    risk_on = panel["regime"].eq("RISK_ON")
    risk_off = panel["regime"].eq("RISK_OFF")
    neutral = ~(risk_on | risk_off)
    panel["regime_score"] = np.nan
    panel.loc[risk_on, "regime_score"] = (
        0.30 * panel.loc[risk_on, "private_conviction"]
        + 0.30 * panel.loc[risk_on, "revision_front_run"]
        + 0.20 * panel.loc[risk_on, "long_up"]
        + 0.20 * panel.loc[risk_on, "value"]
    )
    panel.loc[risk_off, "regime_score"] = (
        0.38 * panel.loc[risk_off, "capitulation_absorption"]
        + 0.27 * panel.loc[risk_off, "residual_private"]
        + 0.20 * panel.loc[risk_off, "short_reversal"]
        + 0.15 * panel.loc[risk_off, "value"]
    )
    panel.loc[neutral, "regime_score"] = (
        0.32 * panel.loc[neutral, "stealth_accum"]
        + 0.28 * panel.loc[neutral, "residual_private"]
        + 0.22 * panel.loc[neutral, "private_conviction"]
        + 0.18 * panel.loc[neutral, "revision_front_run"]
    )
    high_disp = panel["high_dispersion"].fillna(False)
    panel.loc[high_disp, "regime_score"] = (
        0.75 * panel.loc[high_disp, "regime_score"]
        + 0.25 * panel.loc[high_disp, "capitulation_absorption"]
    )
    return panel


def build_panel(
    returns: pd.DataFrame,
    basic_panels: dict[pd.Timestamp, pd.DataFrame],
    universe: str,
    step: int,
) -> pd.DataFrame:
    dates = [
        dt for dt in returns.index[(returns.index >= START) & (returns.index <= END)][::step]
        if dt in basic_panels
    ]
    factor_cache: dict[tuple[str, pd.Timestamp], pd.Series] = {}
    snapshots = []
    for i, dt in enumerate(dates, 1):
        snapshots.append(raw_snapshot(dt, universe, returns, basic_panels, factor_cache))
        if i % 100 == 0:
            print(f"{universe} step={step}: loaded {i}/{len(dates)} snapshots")
    panel = pd.concat(snapshots).sort_index()
    return add_derived_features(panel)


def derived_ic(
    panel: pd.DataFrame,
    returns: pd.DataFrame,
    universe: str,
    step: int,
    horizon: int = 20,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fwd = base.forward_return(returns, horizon)
    rows = []
    for dt in panel.index.get_level_values("date").unique():
        if dt not in fwd.index:
            continue
        x = panel.xs(dt, level="date")
        y = fwd.loc[dt].reindex(x.index)
        for factor in DERIVED_COLS:
            valid = pd.concat([x[factor], y.rename("future")], axis=1).dropna()
            if len(valid) < 25:
                continue
            ic = valid[factor].corr(valid["future"], method="spearman")
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
    summary_rows = []
    for (factor,), g0 in detail.groupby(["factor"]):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, None)):
            g = g0[g0["date"] >= lo]
            if hi is not None:
                g = g[g["date"] < hi]
            g = g.dropna(subset=["ic"])
            if len(g) < 8:
                continue
            sd = g["ic"].std(ddof=1)
            summary_rows.append(
                {
                    "universe": universe,
                    "step": step,
                    "factor": factor,
                    "sample": sample,
                    "mean_ic": g["ic"].mean(),
                    "ic_tstat": g["ic"].mean() / (sd / math.sqrt(len(g))) if sd > 0 else np.nan,
                    "ic_hit_rate": (g["ic"] > 0).mean(),
                    "n_dates": len(g),
                    "avg_n": g["n"].mean(),
                }
            )
    return detail, pd.DataFrame(summary_rows)


@dataclass(frozen=True)
class Rule:
    name: str
    score_col: str
    entry: Callable[[pd.Series], bool]
    exit: Callable[[pd.Series], bool]
    max_hold_days: int
    cross_only: bool = True
    stop_loss: float = -0.15
    profit_take: float = 0.25
    max_units_per_name: int = 1
    add: Callable[[pd.Series], bool] | None = None
    reduce: Callable[[pd.Series], bool] | None = None


def finite(v: object) -> float:
    try:
        f = float(v)
        return f if math.isfinite(f) else np.nan
    except (TypeError, ValueError):
        return np.nan


def ge(row: pd.Series, col: str, value: float) -> bool:
    v = finite(row.get(col))
    return bool(math.isfinite(v) and v >= value)


def le(row: pd.Series, col: str, value: float) -> bool:
    v = finite(row.get(col))
    return bool(math.isfinite(v) and v <= value)


def between(row: pd.Series, col: str, lo: float, hi: float) -> bool:
    v = finite(row.get(col))
    return bool(math.isfinite(v) and lo <= v <= hi)


RULES = (
    Rule(
        name="PRIVATE_HYSTERESIS",
        score_col="private_conviction",
        entry=lambda r: ge(r, "private_level", 0.90) and ge(r, "private_persist", 0.65),
        exit=lambda r: le(r, "private_level", 0.48) or le(r, "private_accel_rank", 0.18),
        max_hold_days=80,
        cross_only=False,
    ),
    Rule(
        name="FLOW_INFLECTION",
        score_col="flow_price_divergence",
        entry=lambda r: ge(r, "private_accel_rank", 0.90)
        and between(r, "private_level", 0.55, 0.92)
        and ge(r, "private_persist", 0.50)
        and le(r, "crowding_heat", 0.76),
        exit=lambda r: le(r, "private_accel_rank", 0.32)
        or le(r, "private_level", 0.38)
        or ge(r, "crowding_exhaustion", 0.82),
        max_hold_days=40,
    ),
    Rule(
        name="STEALTH_ACCUM",
        score_col="stealth_accum",
        entry=lambda r: ge(r, "stealth_accum", 0.84)
        and ge(r, "residual_private", 0.85)
        and ge(r, "private_persist", 0.60)
        and ge(r, "quiet_price", 0.35)
        and le(r, "crowding_heat", 0.77),
        exit=lambda r: le(r, "stealth_accum", 0.43) or ge(r, "crowding_heat", 0.86),
        max_hold_days=60,
    ),
    Rule(
        name="CAPITULATION_ABSORB",
        score_col="capitulation_absorption",
        entry=lambda r: ge(r, "capitulation_absorption", 0.82)
        and ge(r, "short_reversal", 0.80)
        and ge(r, "private_level", 0.65)
        and ge(r, "foreign_sell", 0.55),
        exit=lambda r: le(r, "short_reversal", 0.36) or le(r, "private_level", 0.38),
        max_hold_days=40,
        stop_loss=-0.12,
        profit_take=0.20,
    ),
    Rule(
        name="REVISION_FRONT_RUN",
        score_col="revision_front_run",
        entry=lambda r: ge(r, "revision_front_run", 0.84)
        and ge(r, "private_accel_rank", 0.70)
        and ge(r, "revision_accel_rank", 0.65)
        and le(r, "revision_level", 0.82),
        exit=lambda r: le(r, "revision_accel_rank", 0.32) or le(r, "private_level", 0.38),
        max_hold_days=60,
    ),
    Rule(
        name="COMPOSITE_CROSS",
        score_col="composite_alpha",
        entry=lambda r: ge(r, "composite_alpha", 0.86) and le(r, "crowding_heat", 0.80),
        exit=lambda r: le(r, "composite_alpha", 0.44) or ge(r, "crowding_heat", 0.90),
        max_hold_days=60,
    ),
    Rule(
        name="REGIME_ROUTER",
        score_col="regime_score",
        entry=lambda r: ge(r, "regime_score", 0.84)
        and (
            (
                r.get("regime") == "RISK_ON"
                and (ge(r, "revision_front_run", 0.72) or ge(r, "private_conviction", 0.84))
            )
            or (
                r.get("regime") == "RISK_OFF"
                and ge(r, "capitulation_absorption", 0.78)
            )
            or (
                r.get("regime") == "NEUTRAL"
                and (ge(r, "stealth_accum", 0.78) or ge(r, "residual_private", 0.88))
            )
        ),
        exit=lambda r: le(r, "regime_score", 0.42) or ge(r, "crowding_exhaustion", 0.88),
        max_hold_days=60,
    ),
    Rule(
        name="CROWDING_AVOIDED_PRIVATE",
        score_col="private_conviction",
        entry=lambda r: ge(r, "private_conviction", 0.82)
        and ge(r, "private_level", 0.78)
        and le(r, "crowding_heat", 0.68)
        and le(r, "crowding_exhaustion", 0.62),
        exit=lambda r: le(r, "private_conviction", 0.40)
        or ge(r, "crowding_heat", 0.82)
        or ge(r, "crowding_exhaustion", 0.80),
        max_hold_days=60,
    ),
    Rule(
        name="PYRAMID_CONFIRM",
        score_col="flow_price_divergence",
        entry=lambda r: ge(r, "private_accel_rank", 0.86)
        and ge(r, "private_level", 0.62)
        and le(r, "crowding_heat", 0.78),
        add=lambda r: ge(r, "revision_front_run", 0.74)
        and ge(r, "private_persist", 0.70)
        and ge(r, "private_level", 0.75),
        reduce=lambda r: le(r, "private_accel_rank", 0.45)
        or le(r, "revision_accel_rank", 0.40),
        exit=lambda r: le(r, "private_level", 0.36) or ge(r, "crowding_heat", 0.90),
        max_hold_days=70,
        max_units_per_name=2,
    ),
)


def stock_trade_return(
    cumlog: pd.DataFrame,
    entry_date: pd.Timestamp,
    current_date: pd.Timestamp,
    code: str,
) -> float:
    if code not in cumlog.columns or entry_date not in cumlog.index or current_date not in cumlog.index:
        return np.nan
    a = cumlog.at[entry_date, code]
    b = cumlog.at[current_date, code]
    if pd.isna(a) or pd.isna(b):
        return np.nan
    return float(np.expm1(b - a))


def rule_condition(rule: Rule, row: pd.Series | None) -> bool:
    if row is None:
        return False
    try:
        return bool(rule.entry(row))
    except Exception:
        return False


def backtest_rule(
    rule: Rule,
    panel: pd.DataFrame,
    returns: pd.DataFrame,
    basic_panels: dict[pd.Timestamp, pd.DataFrame],
    universe: str,
    step: int,
    cost_bps: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    signal_dates = list(panel.index.get_level_values("date").unique())
    all_days = returns.index[(returns.index >= signal_dates[0]) & (returns.index <= END)]
    cumlog = np.log1p(returns.clip(lower=-0.999999)).fillna(0.0).cumsum()

    holdings: dict[str, dict[str, object]] = {}
    cooldown: dict[str, int] = {}
    daily_rows: list[dict[str, object]] = []
    trade_rows: list[dict[str, object]] = []
    previous_x: pd.DataFrame | None = None

    for step_idx, dt in enumerate(signal_dates):
        x = panel.xs(dt, level="date").copy()
        next_dt = signal_dates[step_idx + 1] if step_idx + 1 < len(signal_dates) else END
        exited_units = 0
        entered_units = 0

        for code in list(cooldown):
            cooldown[code] -= 1
            if cooldown[code] <= 0:
                cooldown.pop(code, None)

        for code in list(holdings):
            state = holdings[code]
            row = x.loc[code] if code in x.index else None
            units = int(state["units"])
            held_days = int((dt - pd.Timestamp(state["entry_date"])).days)
            trade_ret = stock_trade_return(cumlog, pd.Timestamp(state["entry_date"]), dt, code)
            reason = None
            if row is None:
                reason = "UNIVERSE_OR_DATA"
            elif held_days >= rule.max_hold_days:
                reason = "MAX_HOLD"
            elif math.isfinite(trade_ret) and trade_ret <= rule.stop_loss:
                reason = "STOP_LOSS"
            elif (
                math.isfinite(trade_ret)
                and trade_ret >= rule.profit_take
                and (ge(row, "crowding_heat", 0.74) or ge(row, "crowding_exhaustion", 0.72))
            ):
                reason = "PROFIT_HARVEST"
            elif rule.exit(row):
                reason = "SIGNAL_EXIT"

            if reason is not None:
                exited_units += units
                trade_rows.append(
                    {
                        "strategy": rule.name,
                        "universe": universe,
                        "step": step,
                        "cost_bps": cost_bps,
                        "code": code,
                        "entry_date": state["entry_date"],
                        "exit_date": dt,
                        "holding_days": held_days,
                        "units_max": state["units_max"],
                        "adds": state["adds"],
                        "entry_regime": state["entry_regime"],
                        "exit_reason": reason,
                        "stock_return": trade_ret,
                    }
                )
                holdings.pop(code)
                cooldown[code] = COOLDOWN_STEPS
                continue

            if rule.reduce is not None and units > 1 and rule.reduce(row):
                holdings[code]["units"] = units - 1
                exited_units += 1

        if rule.add is not None:
            free_units = MAX_UNITS - sum(int(v["units"]) for v in holdings.values())
            if free_units > 0:
                add_candidates = []
                for code, state in holdings.items():
                    row = x.loc[code] if code in x.index else None
                    if (
                        row is not None
                        and int(state["units"]) < rule.max_units_per_name
                        and rule.add(row)
                    ):
                        add_candidates.append((finite(row.get(rule.score_col)), code))
                for _, code in sorted(add_candidates, reverse=True):
                    if free_units <= 0:
                        break
                    holdings[code]["units"] = int(holdings[code]["units"]) + 1
                    holdings[code]["units_max"] = max(
                        int(holdings[code]["units_max"]), int(holdings[code]["units"])
                    )
                    holdings[code]["adds"] = int(holdings[code]["adds"]) + 1
                    entered_units += 1
                    free_units -= 1

        free_units = MAX_UNITS - sum(int(v["units"]) for v in holdings.values())
        candidates = []
        if free_units > 0:
            for code, row in x.iterrows():
                if code in holdings or code in cooldown:
                    continue
                if not rule_condition(rule, row):
                    continue
                if rule.cross_only and previous_x is not None and code in previous_x.index:
                    if rule_condition(rule, previous_x.loc[code]):
                        continue
                score = finite(row.get(rule.score_col))
                if not math.isfinite(score):
                    continue
                candidates.append((score, code, row))

        for score, code, row in sorted(candidates, reverse=True):
            if free_units <= 0:
                break
            holdings[code] = {
                "entry_date": dt,
                "entry_score": score,
                "entry_regime": row.get("regime"),
                "units": 1,
                "units_max": 1,
                "adds": 0,
            }
            entered_units += 1
            free_units -= 1

        active_units = {code: int(state["units"]) for code, state in holdings.items()}
        total_units = sum(active_units.values())
        exposure = total_units / MAX_UNITS
        regime = x["regime"].iloc[0] if len(x) else "UNKNOWN"
        high_dispersion = bool(x["high_dispersion"].iloc[0]) if len(x) else False

        interval_days = all_days[(all_days > dt) & (all_days <= next_dt)]
        for j, day in enumerate(interval_days):
            stock_rets = returns.loc[day].reindex(list(active_units))
            gross_ret = sum(
                active_units[code] * (0.0 if pd.isna(stock_rets.get(code)) else float(stock_rets[code]))
                for code in active_units
            ) / MAX_UNITS

            if dt in basic_panels:
                bench_codes = universe_codes(basic_panels[dt], universe)
                bench_raw = returns.loc[day].reindex(bench_codes).mean()
            else:
                bench_raw = np.nan
            bench_ret = (0.0 if pd.isna(bench_raw) else float(bench_raw)) * exposure
            turnover = (entered_units + exited_units) / MAX_UNITS if j == 0 else 0.0
            cost = turnover * cost_bps / 10000.0
            daily_rows.append(
                {
                    "date": day,
                    "signal_date": dt,
                    "strategy": rule.name,
                    "universe": universe,
                    "step": step,
                    "cost_bps": cost_bps,
                    "gross_return": gross_ret,
                    "benchmark_return": bench_ret,
                    "net_return": gross_ret - cost,
                    "excess_return": gross_ret - bench_ret - cost,
                    "turnover": turnover,
                    "exposure": exposure,
                    "positions": len(active_units),
                    "units": total_units,
                    "entries_units": entered_units if j == 0 else 0,
                    "exits_units": exited_units if j == 0 else 0,
                    "regime": regime,
                    "high_dispersion": high_dispersion,
                }
            )
        previous_x = x

    last_dt = signal_dates[-1]
    for code, state in holdings.items():
        trade_rows.append(
            {
                "strategy": rule.name,
                "universe": universe,
                "step": step,
                "cost_bps": cost_bps,
                "code": code,
                "entry_date": state["entry_date"],
                "exit_date": last_dt,
                "holding_days": int((last_dt - pd.Timestamp(state["entry_date"])).days),
                "units_max": state["units_max"],
                "adds": state["adds"],
                "entry_regime": state["entry_regime"],
                "exit_reason": "END_OF_SAMPLE",
                "stock_return": stock_trade_return(cumlog, pd.Timestamp(state["entry_date"]), last_dt, code),
            }
        )
    return pd.DataFrame(daily_rows), pd.DataFrame(trade_rows)


def perf_metrics(g: pd.DataFrame, return_col: str = "excess_return") -> dict[str, float]:
    x = g[return_col].dropna()
    if len(x) < 20:
        return {}
    nav = (1.0 + x).cumprod()
    years = len(x) / 252.0
    cagr = nav.iloc[-1] ** (1.0 / years) - 1.0 if years > 0 and nav.iloc[-1] > 0 else np.nan
    sd = x.std(ddof=1)
    sharpe = x.mean() / sd * math.sqrt(252) if sd > 0 else np.nan
    mdd = (nav / nav.cummax() - 1.0).min()
    return {
        "n_days": len(x),
        "cagr": cagr,
        "ann_mean": x.mean() * 252,
        "sharpe": sharpe,
        "mdd": mdd,
        "hit_rate": (x > 0).mean(),
    }


def summarize_daily(daily: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    yearly_rows = []
    regime_rows = []
    keys = ["strategy", "universe", "step", "cost_bps"]
    for key, g0 in daily.groupby(keys):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, None)):
            g = g0[g0["date"] >= lo]
            if hi is not None:
                g = g[g["date"] < hi]
            metrics = perf_metrics(g, "excess_return")
            if not metrics:
                continue
            summary_rows.append(
                {
                    **dict(zip(keys, key)),
                    "sample": sample,
                    **metrics,
                    "net_long_cagr": perf_metrics(g, "net_return").get("cagr", np.nan),
                    "avg_exposure": g["exposure"].mean(),
                    "avg_positions": g["positions"].mean(),
                    "annual_turnover": g["turnover"].mean() * 252,
                    "invested_day_ratio": (g["exposure"] > 0).mean(),
                }
            )
        test = g0[g0["date"] >= SPLIT]
        for year, gy in test.groupby(test["date"].dt.year):
            metrics = perf_metrics(gy, "excess_return")
            if metrics:
                yearly_rows.append({**dict(zip(keys, key)), "year": int(year), **metrics})
        for regime, gr in test.groupby("regime"):
            metrics = perf_metrics(gr, "excess_return")
            if metrics:
                regime_rows.append(
                    {
                        **dict(zip(keys, key)),
                        "regime": regime,
                        **metrics,
                        "avg_exposure": gr["exposure"].mean(),
                    }
                )
    return pd.DataFrame(summary_rows), pd.DataFrame(yearly_rows), pd.DataFrame(regime_rows)


def summarize_trades(trades: pd.DataFrame) -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    rows = []
    keys = ["strategy", "universe", "step", "cost_bps"]
    for key, g0 in trades.groupby(keys):
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, None)):
            g = g0[pd.to_datetime(g0["entry_date"]) >= lo]
            if hi is not None:
                g = g[pd.to_datetime(g["entry_date"]) < hi]
            g = g.dropna(subset=["stock_return"])
            if len(g) < 5:
                continue
            rows.append(
                {
                    **dict(zip(keys, key)),
                    "sample": sample,
                    "n_trades": len(g),
                    "avg_trade_return": g["stock_return"].mean(),
                    "median_trade_return": g["stock_return"].median(),
                    "trade_hit_rate": (g["stock_return"] > 0).mean(),
                    "avg_holding_days": g["holding_days"].mean(),
                    "p10_trade_return": g["stock_return"].quantile(0.10),
                    "p90_trade_return": g["stock_return"].quantile(0.90),
                    "avg_adds": g["adds"].mean(),
                }
            )
    return pd.DataFrame(rows)


def robustness_score(summary: pd.DataFrame) -> pd.DataFrame:
    test = summary[summary["sample"] == "test"].copy()
    train = summary[summary["sample"] == "train"][
        ["strategy", "universe", "step", "cost_bps", "cagr", "sharpe"]
    ].rename(columns={"cagr": "train_cagr", "sharpe": "train_sharpe"})
    merged = test.merge(train, on=["strategy", "universe", "step", "cost_bps"], how="left")
    merged["robust"] = (
        (merged["cagr"] > 0)
        & (merged["sharpe"] > 0)
        & (merged["train_cagr"] > 0)
        & (merged["train_sharpe"] > 0)
    )
    grouped = (
        merged.groupby(["strategy", "universe"], as_index=False)
        .agg(
            robust_cells=("robust", "sum"),
            total_cells=("robust", "size"),
            median_test_cagr=("cagr", "median"),
            median_test_sharpe=("sharpe", "median"),
            worst_test_cagr=("cagr", "min"),
            median_train_cagr=("train_cagr", "median"),
            median_exposure=("avg_exposure", "median"),
            median_turnover=("annual_turnover", "median"),
        )
    )
    grouped["robust_ratio"] = grouped["robust_cells"] / grouped["total_cells"]
    grouped["selection_score"] = (
        0.35 * grouped["robust_ratio"]
        + 0.25 * grouped["median_test_sharpe"].clip(-1, 2) / 2
        + 0.20 * grouped["median_test_cagr"].clip(-0.20, 0.30) / 0.30
        + 0.10 * grouped["median_train_cagr"].clip(-0.20, 0.30) / 0.30
        + 0.10 * (1.0 - grouped["median_turnover"].clip(0, 20) / 20)
    )
    return grouped.sort_values("selection_score", ascending=False)


def write_definitions() -> None:
    lines = [
        "# Creative factor lab — strategy definitions",
        "",
        "Signals are evaluated every 5 or 10 trading days, but existing holdings are not mechanically reranked or displaced.",
        "A stock enters only when its own pre-set condition is met; it leaves through signal decay, stop-loss, profit-harvest, or maximum holding period.",
        "Each position uses one of 30 fixed notional slots. PYRAMID_CONFIRM may add a second slot after earnings-revision confirmation.",
        "",
        "## Derived factors",
        "",
        "- **Private acceleration:** change in cross-sectional private-flow rank over roughly 20 trading days.",
        "- **Private persistence:** average private-flow rank over the latest four signal observations.",
        "- **Abnormal private flow:** stock-specific deviation from its own trailing 12-observation flow-rank history.",
        "- **Residual private flow:** cross-sectional regression residual after controlling for size, momentum, foreign flow, revisions, and value.",
        "- **Stealth accumulation:** residual/private persistence/abnormal flow while price momentum remains quiet.",
        "- **Capitulation absorption:** private buying against foreign selling and short-term price weakness.",
        "- **Revision front-run:** accelerating private flow and residual accumulation before revisions become fully crowded.",
        "- **Crowding exhaustion:** high price/flow crowding combined with slowing private flow and revisions.",
        "- **Regime score:** switches between trend-confirmation, capitulation, and stealth-accumulation logic using market breadth and 60-day return.",
        "",
        "## State-machine families",
    ]
    for rule in RULES:
        lines.append(
            f"- **{rule.name}:** score `{rule.score_col}`, max hold {rule.max_hold_days} days, "
            f"cross-only={rule.cross_only}, max units/name={rule.max_units_per_name}."
        )
    (OUT / "strategy_definitions.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:END]
    all_ic_detail = []
    all_ic_summary = []
    all_daily = []
    all_trades = []

    for universe in UNIVERSES:
        for step in STEPS:
            panel = build_panel(returns, basic_panels, universe, step)
            panel.to_pickle(OUT / f"feature_panel_{universe}_{step}d.pkl")
            ic_detail, ic_summary = derived_ic(panel, returns, universe, step)
            all_ic_detail.append(ic_detail)
            all_ic_summary.append(ic_summary)
            for rule in RULES:
                for cost in COSTS:
                    daily, trades = backtest_rule(
                        rule, panel, returns, basic_panels, universe, step, cost
                    )
                    all_daily.append(daily)
                    all_trades.append(trades)
                    print(
                        f"done {universe} step={step} {rule.name} cost={cost}: "
                        f"{len(daily)} days, {len(trades)} trades"
                    )

    ic_detail = pd.concat(all_ic_detail, ignore_index=True)
    ic_summary = pd.concat(all_ic_summary, ignore_index=True)
    daily = pd.concat(all_daily, ignore_index=True)
    trades = pd.concat(all_trades, ignore_index=True)

    summary, yearly, regime = summarize_daily(daily)
    trade_summary = summarize_trades(trades)
    robustness = robustness_score(summary)

    ic_detail.to_csv(OUT / "derived_factor_ic_detail.csv", index=False, encoding="utf-8-sig")
    ic_summary.to_csv(OUT / "derived_factor_ic_summary.csv", index=False, encoding="utf-8-sig")
    daily.to_csv(OUT / "state_machine_daily.csv", index=False, encoding="utf-8-sig")
    trades.to_csv(OUT / "state_machine_trades.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "state_machine_summary.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(OUT / "state_machine_yearly.csv", index=False, encoding="utf-8-sig")
    regime.to_csv(OUT / "state_machine_regime.csv", index=False, encoding="utf-8-sig")
    trade_summary.to_csv(OUT / "trade_summary.csv", index=False, encoding="utf-8-sig")
    robustness.to_csv(OUT / "robustness_ranking.csv", index=False, encoding="utf-8-sig")
    write_definitions()

    key_ic = ic_summary[
        (ic_summary["sample"] == "test") & (ic_summary["universe"] == "KOSPI_EX_K200")
    ].sort_values(["step", "mean_ic"], ascending=[True, False])
    key_perf = summary[
        (summary["sample"] == "test")
        & (summary["universe"] == "KOSPI_EX_K200")
        & (summary["cost_bps"] == 60)
    ].sort_values(["step", "sharpe"], ascending=[True, False])
    report = [
        "# Creative factor lab",
        "",
        "## OOS derived-factor IC — KOSPI ex-K200",
        "",
        key_ic.to_markdown(index=False),
        "",
        "## OOS state-machine performance — KOSPI ex-K200, 60 bps",
        "",
        key_perf.to_markdown(index=False),
        "",
        "## Robustness ranking",
        "",
        robustness.head(30).to_markdown(index=False),
    ]
    (OUT / "summary.md").write_text("\n".join(report), encoding="utf-8")
    print(robustness.head(20).to_string(index=False))


if __name__ == "__main__":
    main()
