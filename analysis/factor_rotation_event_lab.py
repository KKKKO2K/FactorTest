from __future__ import annotations

import importlib.util
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = HERE / "factor_rotation_event_results"
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
STEP = 10
HORIZON = 20
UNIVERSES = ("K200", "KOSPI_EX_K200", "KOSDAQ")
COSTS = (30, 60, 100)
NAMES = {
    "VALUE": "저평가",
    "REVISION": "이익리비전",
    "PRIVATE": "사모수급",
    "SHORT_REVERSAL": "단기반전",
    "LONG_MOM": "중기모멘텀",
    "FLOW_TO_REVISION": "수급선행→리비전",
    "THREE_STAGE": "수급→리비전→가격 3단계",
    "OWNERSHIP_TRANSFER": "외국인매도·사모흡수",
    "VALUE_UNLOCK": "가치함정 탈출",
    "EARNINGS_BREADTH": "리비전 동시확산",
    "EARLY_REVISION": "초기 리비전 선점",
    "PULLBACK_RELOAD": "추세내 눌림목 매집",
    "BREAKOUT_CONFIRM": "추세·수급·실적 확인",
    "NEGLECTED_VALUE": "소외가치 매집",
    "TENSION_REVERSAL": "팩터충돌 해소",
}
FACTOR_COLS = tuple(NAMES)


def pct_rank(s: pd.Series, high_good: bool = True) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    return x.rank(pct=True, method="average", ascending=high_good)


def gmean(frame: pd.DataFrame, cols: list[str]) -> pd.Series:
    x = frame[cols].clip(lower=1e-6, upper=1.0)
    valid = x.notna().sum(axis=1)
    out = np.exp(np.log(x).sum(axis=1, skipna=True) / valid.replace(0, np.nan))
    return out.where(valid == len(cols))


def universe_codes(basic_panel: pd.DataFrame, universe: str) -> pd.Index:
    market = basic_panel["market"].astype(str).str.upper()
    if universe == "K200":
        mask = basic_panel["k200"] == 1
    elif universe == "KOSPI_EX_K200":
        mask = market.str.contains("KOSPI", na=False) & (basic_panel["k200"] == 0)
    elif universe == "KOSDAQ":
        mask = market.str.contains("KOSDAQ", na=False)
    else:
        raise KeyError(universe)
    return basic_panel.index[mask]


def trailing_return(
    returns: pd.DataFrame, dt: pd.Timestamp, codes: pd.Index, days: int
) -> pd.Series:
    cols = returns.columns.intersection(codes)
    hist = returns.loc[:dt, cols].tail(days)
    out = pd.Series(index=codes, dtype=float)
    if not hist.empty:
        out.loc[cols] = (1.0 + hist.fillna(0.0)).prod(axis=0) - 1.0
    return out


def trailing_vol(
    returns: pd.DataFrame, dt: pd.Timestamp, codes: pd.Index, days: int
) -> pd.Series:
    cols = returns.columns.intersection(codes)
    hist = returns.loc[:dt, cols].tail(days)
    out = pd.Series(index=codes, dtype=float)
    if not hist.empty:
        out.loc[cols] = hist.std(axis=0, ddof=1) * math.sqrt(252)
    return out


def forward_return(daily: pd.DataFrame, horizon: int) -> pd.DataFrame:
    logs = np.log1p(daily.clip(lower=-0.999999))
    acc = sum(logs.shift(-i) for i in range(1, horizon + 1))
    return np.expm1(acc)


def raw_snapshot(
    dt: pd.Timestamp,
    universe: str,
    returns: pd.DataFrame,
    basic_panels: dict[pd.Timestamp, pd.DataFrame],
    factor_cache: dict[tuple[str, pd.Timestamp], pd.Series],
) -> pd.DataFrame:
    bp = basic_panels[dt]
    codes = universe_codes(bp, universe)
    x = pd.DataFrame(index=codes)
    for key, folder in base.FACTOR_DIRS.items():
        cache_key = (key, dt)
        if cache_key not in factor_cache:
            factor_cache[cache_key] = base.load_factor(folder, dt)
        x[key] = factor_cache[cache_key].reindex(codes)

    x["mcap"] = bp["mcap"].reindex(codes)
    x["size_rank"] = pct_rank(np.log1p(x["mcap"]), True)
    x["cheap_per"] = pct_rank(x["per"], False)
    x["cheap_pbr"] = pct_rank(x["pbr"], False)
    x["value"] = x[["cheap_per", "cheap_pbr"]].mean(axis=1)
    x["op12_level"] = pct_rank(x["op12"], True)
    x["opfy1_level"] = pct_rank(x["opfy1"], True)
    x["revision"] = x[["op12_level", "opfy1_level"]].mean(axis=1)
    x["private_buy"] = pct_rank(x["private"], True)
    x["foreign_buy"] = pct_rank(x["foreign"], True)
    x["foreign_sell"] = pct_rank(x["foreign"], False)
    x["short_up"] = pct_rank(x["short"], True)
    x["short_reversal"] = pct_rank(x["short"], False)
    x["long_up"] = pct_rank(x["long"], True)
    x["long_contrarian"] = pct_rank(x["long"], False)

    r20 = trailing_return(returns, dt, codes, 20)
    r60 = trailing_return(returns, dt, codes, 60)
    vol20 = trailing_vol(returns, dt, codes, 20)
    x["ret20"] = r20
    x["ret60"] = r60
    x["ret20_rank"] = pct_rank(r20, True)
    x["ret20_reversal"] = pct_rank(r20, False)
    x["ret60_rank"] = pct_rank(r60, True)
    x["vol20_rank"] = pct_rank(vol20, True)
    x["quiet_price"] = (1.0 - 2.0 * (x["short_up"] - 0.50).abs()).clip(0.0, 1.0)

    valid_cols = returns.columns.intersection(codes)
    hist20 = returns.loc[:dt, valid_cols].tail(20)
    stock60 = r60.reindex(valid_cols)
    x["market60"] = float(stock60.mean())
    x["breadth60"] = float((stock60 > 0).mean())
    ew20 = hist20.mean(axis=1, skipna=True)
    x["market_vol20"] = float(ew20.std(ddof=1) * math.sqrt(252))
    x["dispersion20"] = float(hist20.std(axis=1, ddof=1).mean() * math.sqrt(252))

    high_size = x.index[x["size_rank"] >= 0.70]
    low_size = x.index[x["size_rank"] <= 0.30]
    x["size_lead60"] = float(r60.reindex(high_size).mean() - r60.reindex(low_size).mean())
    x["date"] = dt
    x["code"] = x.index
    return x.reset_index(drop=True).set_index(["date", "code"])


def build_panel(
    universe: str,
    returns: pd.DataFrame,
    basic_panels: dict[pd.Timestamp, pd.DataFrame],
) -> pd.DataFrame:
    dates = [
        dt
        for dt in returns.index
        if START <= dt <= END and dt in basic_panels
    ][::STEP]
    cache: dict[tuple[str, pd.Timestamp], pd.Series] = {}
    frames = []
    for i, dt in enumerate(dates, 1):
        frames.append(raw_snapshot(dt, universe, returns, basic_panels, cache))
        if i % 80 == 0:
            print(f"{universe}: loaded {i}/{len(dates)} snapshots", flush=True)
    p = pd.concat(frames).sort_index()
    by_code = p.groupby(level="code", group_keys=False)

    for col in (
        "private_buy", "revision", "op12_level", "opfy1_level",
        "short_up", "long_up", "foreign_buy", "value"
    ):
        p[f"{col}_lag1"] = by_code[col].shift(1)
        p[f"{col}_lag2"] = by_code[col].shift(2)
        p[f"{col}_lag4"] = by_code[col].shift(4)

    p["private_accel"] = p["private_buy"] - p["private_buy_lag2"]
    p["revision_accel"] = p["revision"] - p["revision_lag2"]
    p["op12_accel"] = p["op12_level"] - p["op12_level_lag2"]
    p["opfy1_accel"] = p["opfy1_level"] - p["opfy1_level_lag2"]
    p["short_accel"] = p["short_up"] - p["short_up_lag1"]
    p["private_persist"] = by_code["private_buy"].transform(
        lambda s: s.rolling(4, min_periods=2).mean()
    )

    by_date = p.groupby(level="date", group_keys=False)
    p["private_accel_rank"] = by_date["private_accel"].rank(pct=True)
    p["revision_accel_rank"] = by_date["revision_accel"].rank(pct=True)
    p["op12_accel_rank"] = by_date["op12_accel"].rank(pct=True)
    p["opfy1_accel_rank"] = by_date["opfy1_accel"].rank(pct=True)
    p["short_accel_rank"] = by_date["short_accel"].rank(pct=True)
    p["private_accel_lag1"] = by_code["private_accel_rank"].shift(1)
    p["private_accel_lag2"] = by_code["private_accel_rank"].shift(2)
    p["revision_accel_lag1"] = by_code["revision_accel_rank"].shift(1)

    p["revision_cross"] = (
        p["revision"] * (1.0 - p["revision_lag1"])
    ).clip(0.0, 1.0)
    p["earnings_agreement"] = (
        1.0 - (p["op12_level"] - p["opfy1_level"]).abs()
    ).clip(0.0, 1.0)
    p["earnings_breadth"] = (
        p[["op12_level", "opfy1_level"]].min(axis=1)
        * p["earnings_agreement"]
    )

    # Original factors, all oriented so a higher number is the long signal.
    p["VALUE"] = p["value"]
    p["REVISION"] = p["revision"]
    p["PRIVATE"] = p["private_buy"]
    p["SHORT_REVERSAL"] = p["short_reversal"]
    p["LONG_MOM"] = p["long_up"]

    # Conditional combinations and explicit event-sequence factors. No residualization.
    p["FLOW_TO_REVISION"] = gmean(
        p, ["private_accel_lag1", "revision_accel_rank", "quiet_price"]
    )
    p["THREE_STAGE"] = gmean(
        p,
        ["private_accel_lag2", "revision_accel_lag1", "short_accel_rank", "quiet_price"],
    )
    p["OWNERSHIP_TRANSFER"] = gmean(
        p, ["private_buy", "foreign_sell", "short_reversal"]
    )
    p["VALUE_UNLOCK"] = gmean(
        p, ["value", "revision_cross", "private_buy"]
    )
    p["EARNINGS_BREADTH"] = p["earnings_breadth"]
    p["EARLY_REVISION"] = gmean(
        p,
        ["private_accel_lag1", "revision_accel_rank", "quiet_price"],
    ) * (1.0 - 0.50 * p["revision"])
    p["PULLBACK_RELOAD"] = gmean(
        p, ["long_up", "short_reversal", "private_persist", "revision"]
    )
    p["BREAKOUT_CONFIRM"] = gmean(
        p, ["long_up", "short_up", "private_persist", "earnings_breadth"]
    )
    p["NEGLECTED_VALUE"] = gmean(
        p, ["value", "private_persist", "quiet_price", "foreign_sell"]
    )
    p["TENSION_REVERSAL"] = gmean(
        p, ["value", "long_contrarian", "revision_accel_rank", "private_buy"]
    )

    p["event_flow_revision"] = (
        (p["private_accel_lag1"] >= 0.80)
        & (p["revision_accel_rank"] >= 0.70)
        & (p["quiet_price"] >= 0.45)
    )
    p["event_three_stage"] = (
        (p["private_accel_lag2"] >= 0.75)
        & (p["revision_accel_lag1"] >= 0.65)
        & (p["short_accel_rank"] >= 0.65)
    )
    p["event_transfer"] = (
        (p["private_buy"] >= 0.80)
        & (p["foreign_sell"] >= 0.80)
        & (p["short_reversal"] >= 0.65)
    )
    p["event_value_unlock"] = (
        (p["value"] >= 0.75)
        & (p["revision_cross"] >= 0.60)
        & (p["private_buy"] >= 0.60)
    )
    p["event_pullback"] = (
        (p["long_up"] >= 0.70)
        & (p["short_reversal"] >= 0.70)
        & (p["private_persist"] >= 0.65)
        & (p["revision"] >= 0.40)
    )
    p["event_dual_revision"] = (
        (p["opfy1_level_lag1"] >= 0.65)
        & (p["op12_level_lag1"] < 0.55)
        & (p["op12_level"] >= 0.65)
    )
    event_map = {
        "FLOW_REVISION": ("event_flow_revision", "FLOW_TO_REVISION"),
        "THREE_STAGE": ("event_three_stage", "THREE_STAGE"),
        "TRANSFER": ("event_transfer", "OWNERSHIP_TRANSFER"),
        "VALUE_UNLOCK": ("event_value_unlock", "VALUE_UNLOCK"),
        "PULLBACK": ("event_pullback", "PULLBACK_RELOAD"),
        "DUAL_REVISION": ("event_dual_revision", "EARNINGS_BREADTH"),
    }
    event_scores = pd.DataFrame(index=p.index)
    for name, (flag, score) in event_map.items():
        event_scores[name] = p[score].where(p[flag])
    p["event_score"] = event_scores.max(axis=1, skipna=True)
    p["event_type"] = event_scores.idxmax(axis=1, skipna=True)
    p["event_any"] = event_scores.notna().any(axis=1)

    # Crowding deterioration is used only as an exit condition.
    p["crowding_exit"] = (
        0.35 * p["short_up"]
        + 0.25 * p["long_up"]
        + 0.20 * p["private_buy"]
        + 0.20 * p["foreign_buy"]
    ) * (
        0.50 * (1.0 - p["private_accel_rank"])
        + 0.50 * (1.0 - p["revision_accel_rank"])
    )

    # Point-in-time market-state classification.
    ds = (
        p.reset_index()
        .groupby("date")
        .agg(
            market60=("market60", "first"),
            breadth60=("breadth60", "first"),
            market_vol20=("market_vol20", "first"),
            dispersion20=("dispersion20", "first"),
            size_lead60=("size_lead60", "first"),
        )
        .sort_index()
    )
    ds["vol_med"] = ds["market_vol20"].rolling(26, min_periods=8).median().shift(1)
    ds["disp_med"] = ds["dispersion20"].rolling(26, min_periods=8).median().shift(1)
    ds["high_vol"] = ds["market_vol20"] > ds["vol_med"]
    ds["high_disp"] = ds["dispersion20"] > ds["disp_med"]
    ds["state"] = "NEUTRAL"
    ds.loc[(ds.market60 > 0.03) & (ds.breadth60 > 0.55), "state"] = "BROAD_RISK_ON"
    ds.loc[(ds.market60 > 0.03) & (ds.breadth60 <= 0.55), "state"] = "NARROW_RISK_ON"
    ds.loc[(ds.market60 < -0.03) & (ds.breadth60 < 0.45), "state"] = "RISK_OFF"
    ds.loc[
        ds.state.eq("NEUTRAL") & ds.high_disp,
        "state",
    ] = "HIGH_DISPERSION"
    ds.loc[
        ds.state.eq("NEUTRAL") & ds.high_vol,
        "state",
    ] = "HIGH_VOL_CHOP"
    ds["size_state"] = np.where(ds.size_lead60 > 0, "LARGE_LEAD", "SMALL_LEAD")
    p = p.join(ds[["state", "size_state", "high_vol", "high_disp"]], on="date")
    return p


def rank_corr(x: pd.Series, y: pd.Series) -> float:
    valid = pd.concat([x, y], axis=1).dropna()
    if len(valid) < 25 or valid.iloc[:, 0].nunique() < 5:
        return np.nan
    return valid.iloc[:, 0].rank().corr(valid.iloc[:, 1].rank())


def ic_detail(
    panel: pd.DataFrame,
    fwd20: pd.DataFrame,
    universe: str,
) -> pd.DataFrame:
    rows = []
    for dt, g in panel.groupby(level="date"):
        if dt not in fwd20.index:
            continue
        codes = g.index.get_level_values("code")
        future = fwd20.loc[dt].reindex(codes)
        state = str(g["state"].iloc[0])
        size_state = str(g["size_state"].iloc[0])
        for factor in FACTOR_COLS:
            s = g[factor].copy()
            s.index = codes
            valid = pd.concat([s.rename("score"), future.rename("future")], axis=1).dropna()
            if len(valid) < 25:
                continue
            ic = rank_corr(valid.score, valid.future)
            q = valid.score.rank(pct=True)
            top = valid.loc[q >= 0.80, "future"].mean()
            bottom = valid.loc[q <= 0.20, "future"].mean()
            rows.append(
                {
                    "universe": universe,
                    "date": dt,
                    "factor": factor,
                    "state": state,
                    "size_state": size_state,
                    "ic": ic,
                    "q5_q1": top - bottom,
                    "n": len(valid),
                }
            )
    return pd.DataFrame(rows)


def summarize_ic(detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = detail.copy()
    d["sample"] = np.where(d.date < SPLIT, "train", "test")
    overall = (
        d.groupby(["universe", "sample", "factor"], as_index=False)
        .agg(
            mean_ic=("ic", "mean"),
            ic_t=("ic", lambda x: x.mean() / (x.std(ddof=1) / math.sqrt(len(x))) if len(x) > 2 and x.std(ddof=1) > 0 else np.nan),
            positive_ic=("ic", lambda x: (x > 0).mean()),
            mean_spread=("q5_q1", "mean"),
            n_dates=("ic", "count"),
        )
    )
    conditional = (
        d.groupby(["universe", "sample", "state", "size_state", "factor"], as_index=False)
        .agg(
            mean_ic=("ic", "mean"),
            positive_ic=("ic", lambda x: (x > 0).mean()),
            mean_spread=("q5_q1", "mean"),
            n_dates=("ic", "count"),
        )
    )
    return overall, conditional


def factor_maps(
    ic: pd.DataFrame,
    universe: str,
) -> tuple[list[str], dict[tuple[str, str], list[str]], pd.DataFrame]:
    train = ic[(ic.universe == universe) & (ic.date < SPLIT)].copy()
    overall = train.groupby("factor").ic.agg(["mean", "count"]).sort_values("mean", ascending=False)
    static = overall[overall["count"] >= 20].head(3).index.tolist()
    mapping: dict[tuple[str, str], list[str]] = {}
    rows = []
    for (state, size_state), g in train.groupby(["state", "size_state"]):
        rank = g.groupby("factor").ic.agg(["mean", "count"]).sort_values("mean", ascending=False)
        chosen = rank[(rank["count"] >= 5) & (rank["mean"] > 0)].head(2).index.tolist()
        if not chosen:
            chosen = static[:2]
        mapping[(state, size_state)] = chosen
        for order, factor in enumerate(chosen, 1):
            rows.append(
                {
                    "universe": universe,
                    "state": state,
                    "size_state": size_state,
                    "rank": order,
                    "factor": factor,
                    "train_conditional_ic": rank.loc[factor, "mean"] if factor in rank.index else np.nan,
                    "n_dates": rank.loc[factor, "count"] if factor in rank.index else 0,
                }
            )
    return static, mapping, pd.DataFrame(rows)


def score_history(
    panel: pd.DataFrame,
    ic: pd.DataFrame,
    universe: str,
    static: list[str],
    mapping: dict[tuple[str, str], list[str]],
) -> tuple[dict[pd.Timestamp, pd.DataFrame], pd.DataFrame]:
    pivot = (
        ic[ic.universe == universe]
        .pivot(index="date", columns="factor", values="ic")
        .sort_index()
    )
    # A 20-day outcome is not known until two 10-day snapshots later.
    trailing = pivot.shift(2).rolling(12, min_periods=5).mean()
    train_cond = (
        ic[(ic.universe == universe) & (ic.date < SPLIT)]
        .groupby(["state", "size_state", "factor"])
        .ic.mean()
    )
    out: dict[pd.Timestamp, pd.DataFrame] = {}
    selection_rows = []
    for dt, g0 in panel.groupby(level="date"):
        g = g0.copy()
        codes = g.index.get_level_values("code")
        state = str(g.state.iloc[0])
        size_state = str(g.size_state.iloc[0])
        static_factors = static
        regime_factors = mapping.get((state, size_state), static[:2])
        available_trailing = trailing.loc[dt] if dt in trailing.index else pd.Series(dtype=float)
        pos = available_trailing.dropna().sort_values(ascending=False)
        pos = pos[pos > 0]
        trailing_factors = pos.head(2).index.tolist() or static[:2]

        regime_expected = pd.Series(
            {f: train_cond.get((state, size_state, f), np.nan) for f in FACTOR_COLS}
        )
        hybrid_strength = regime_expected.fillna(0).clip(lower=0)
        if dt in trailing.index:
            hybrid_strength = hybrid_strength + trailing.loc[dt].fillna(0).clip(lower=0)
        hybrid_factors = hybrid_strength.sort_values(ascending=False).head(2).index.tolist()
        if not hybrid_factors or hybrid_strength.loc[hybrid_factors].sum() <= 0:
            hybrid_factors = static[:2]

        z = pd.DataFrame(index=codes)
        for col in FACTOR_COLS:
            z[col] = g[col].to_numpy()
        z["event_score"] = g["event_score"].to_numpy()
        z["event_any"] = g["event_any"].to_numpy()
        z["event_type"] = g["event_type"].to_numpy()
        z["crowding_exit"] = g["crowding_exit"].to_numpy()
        z["STATIC_BEST3"] = z[static_factors].mean(axis=1)
        z["REGIME_ROTATION"] = z[regime_factors].mean(axis=1)

        if trailing_factors:
            w = available_trailing.reindex(trailing_factors).clip(lower=0)
            if w.notna().sum() and w.sum() > 0:
                w = w / w.sum()
                z["TRAILING_IC_ROTATION"] = sum(z[f] * w[f] for f in trailing_factors)
            else:
                z["TRAILING_IC_ROTATION"] = z[trailing_factors].mean(axis=1)
        else:
            z["TRAILING_IC_ROTATION"] = z["STATIC_BEST3"]

        hw = hybrid_strength.reindex(hybrid_factors).clip(lower=0)
        if hw.sum() > 0:
            hw = hw / hw.sum()
            z["HYBRID_ROTATION"] = sum(z[f] * hw[f] for f in hybrid_factors)
        else:
            z["HYBRID_ROTATION"] = z[hybrid_factors].mean(axis=1)
        z["EVENT_ONLY"] = z["event_score"].where(z["event_any"])
        z["EVENT_PLUS_META"] = np.where(
            z["event_any"],
            0.70 * z["event_score"] + 0.30 * z["HYBRID_ROTATION"],
            z["HYBRID_ROTATION"],
        )
        out[dt] = z
        for strategy, factors in (
            ("STATIC_BEST3", static_factors),
            ("REGIME_ROTATION", regime_factors),
            ("TRAILING_IC_ROTATION", trailing_factors),
            ("HYBRID_ROTATION", hybrid_factors),
        ):
            for order, factor in enumerate(factors, 1):
                selection_rows.append(
                    {
                        "universe": universe,
                        "date": dt,
                        "state": state,
                        "size_state": size_state,
                        "strategy": strategy,
                        "rank": order,
                        "factor": factor,
                        "trailing_ic": available_trailing.get(factor, np.nan),
                        "train_state_ic": regime_expected.get(factor, np.nan),
                    }
                )
    return out, pd.DataFrame(selection_rows)


def turnover(old: pd.Series, new: pd.Series) -> float:
    idx = old.index.union(new.index)
    o = old.reindex(idx, fill_value=0.0)
    n = new.reindex(idx, fill_value=0.0)
    old_cash = 1.0 - o.sum()
    new_cash = 1.0 - n.sum()
    return 0.5 * (float((n - o).abs().sum()) + abs(new_cash - old_cash))


def target_weights(
    scores: pd.Series,
    n: int,
    minimum: int = 10,
) -> pd.Series:
    s = scores.replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)
    if len(s) < minimum:
        return pd.Series(dtype=float)
    names = s.head(n).index
    return pd.Series(1.0 / len(names), index=names)


def backtest(
    universe: str,
    panel: pd.DataFrame,
    scores: dict[pd.Timestamp, pd.DataFrame],
    fwd10: pd.DataFrame,
    cost_bps: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = sorted(scores)
    strategies = (
        "STATIC_BEST3",
        "REGIME_ROTATION",
        "TRAILING_IC_ROTATION",
        "HYBRID_ROTATION",
        "EVENT_ONLY",
        "EVENT_PLUS_META",
        "REGIME_HYSTERESIS",
        "EVENT_STATE_MACHINE",
    )
    current = {s: pd.Series(dtype=float) for s in strategies}
    ages: dict[str, dict[str, int]] = {s: {} for s in strategies}
    rows = []
    event_rows = []
    for dt in dates:
        if dt not in fwd10.index:
            continue
        z = scores[dt]
        future = fwd10.loc[dt]
        universe_valid = future.reindex(z.index).dropna()
        benchmark = float(universe_valid.mean()) if len(universe_valid) else 0.0
        for strategy in strategies:
            if strategy in {
                "STATIC_BEST3", "REGIME_ROTATION", "TRAILING_IC_ROTATION",
                "HYBRID_ROTATION", "EVENT_PLUS_META"
            }:
                new_w = target_weights(z[strategy], 25, 10)
            elif strategy == "EVENT_ONLY":
                new_w = target_weights(z["EVENT_ONLY"], 20, 5)
            elif strategy == "REGIME_HYSTERESIS":
                score = z["HYBRID_ROTATION"].dropna().sort_values(ascending=False)
                retain = set(score.head(max(40, int(len(score) * 0.35))).index)
                keep = [c for c in current[strategy].index if c in retain]
                fill = [c for c in score.index if c not in keep]
                names = (keep + fill)[:25]
                new_w = pd.Series(1.0 / len(names), index=names) if len(names) >= 10 else pd.Series(dtype=float)
            else:
                # Event-driven stock-level entry/exit. Positions are not replaced merely due to rank.
                old_names = list(current[strategy].index)
                survivors = []
                for code in old_names:
                    ages[strategy][code] = ages[strategy].get(code, 0) + STEP
                    if code not in z.index:
                        continue
                    meta_rank = z["HYBRID_ROTATION"].rank(pct=True).get(code, np.nan)
                    exit_now = (
                        ages[strategy][code] >= 80
                        or (pd.notna(meta_rank) and meta_rank <= 0.25)
                        or z.at[code, "crowding_exit"] >= 0.80
                    )
                    if not exit_now:
                        survivors.append(code)
                    else:
                        ages[strategy].pop(code, None)
                candidates = z.loc[z.event_any].sort_values("event_score", ascending=False).index.tolist()
                additions = [c for c in candidates if c not in survivors]
                names = (survivors + additions)[:25]
                for code in additions[: max(0, 25 - len(survivors))]:
                    ages[strategy][code] = 0
                    event_rows.append(
                        {
                            "universe": universe,
                            "date": dt,
                            "code": code,
                            "event_type": z.at[code, "event_type"],
                            "event_score": z.at[code, "event_score"],
                        }
                    )
                new_w = pd.Series(1.0 / len(names), index=names) if names else pd.Series(dtype=float)

            turn = turnover(current[strategy], new_w)
            gross = float((new_w * future.reindex(new_w.index).fillna(0.0)).sum())
            exposure = float(new_w.sum())
            bench_exposure = benchmark * exposure
            net = gross - turn * cost_bps / 10000.0
            rows.append(
                {
                    "universe": universe,
                    "date": dt,
                    "strategy": strategy,
                    "cost_bps": cost_bps,
                    "gross": gross,
                    "net": net,
                    "benchmark": bench_exposure,
                    "excess": net - bench_exposure,
                    "turnover": turn,
                    "exposure": exposure,
                    "n_holdings": len(new_w),
                }
            )
            current[strategy] = new_w
    return pd.DataFrame(rows), pd.DataFrame(event_rows)


def performance(detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    yearly = []
    periods = 252 / STEP
    for keys, g0 in detail.groupby(["universe", "strategy", "cost_bps"]):
        universe, strategy, cost = keys
        g0 = g0.sort_values("date")
        for sample, lo, hi in (("train", START, SPLIT), ("test", SPLIT, END + pd.Timedelta(days=1))):
            g = g0[(g0.date >= lo) & (g0.date < hi)]
            if len(g) < 12:
                continue
            ex = g.excess
            nav = (1.0 + ex).cumprod()
            years = len(g) / periods
            cagr = nav.iloc[-1] ** (1.0 / years) - 1.0 if nav.iloc[-1] > 0 else np.nan
            vol = ex.std(ddof=1) * math.sqrt(periods)
            sharpe = ex.mean() / ex.std(ddof=1) * math.sqrt(periods) if ex.std(ddof=1) > 0 else np.nan
            rows.append(
                {
                    "universe": universe,
                    "strategy": strategy,
                    "cost_bps": cost,
                    "sample": sample,
                    "n_periods": len(g),
                    "excess_cagr": cagr,
                    "excess_ann_mean": ex.mean() * periods,
                    "excess_vol": vol,
                    "excess_sharpe": sharpe,
                    "excess_mdd": float((nav / nav.cummax() - 1.0).min()),
                    "annual_turnover": g.turnover.mean() * periods,
                    "avg_exposure": g.exposure.mean(),
                    "avg_holdings": g.n_holdings.mean(),
                    "positive_periods": (ex > 0).mean(),
                }
            )
        test = g0[g0.date >= SPLIT].copy()
        if not test.empty:
            test["year"] = test.date.dt.year
            for year, gy in test.groupby("year"):
                ex = gy.excess
                yearly.append(
                    {
                        "universe": universe,
                        "strategy": strategy,
                        "cost_bps": cost,
                        "year": year,
                        "excess_return": float((1.0 + ex).prod() - 1.0),
                        "excess_sharpe": ex.mean() / ex.std(ddof=1) * math.sqrt(periods) if len(ex) > 2 and ex.std(ddof=1) > 0 else np.nan,
                        "n_periods": len(ex),
                    }
                )
    return pd.DataFrame(rows), pd.DataFrame(yearly)


def event_summary(
    panel: pd.DataFrame,
    fwd20: pd.DataFrame,
    universe: str,
) -> pd.DataFrame:
    rows = []
    flags = {
        "FLOW_REVISION": "event_flow_revision",
        "THREE_STAGE": "event_three_stage",
        "TRANSFER": "event_transfer",
        "VALUE_UNLOCK": "event_value_unlock",
        "PULLBACK": "event_pullback",
        "DUAL_REVISION": "event_dual_revision",
    }
    for dt, g in panel.groupby(level="date"):
        if dt not in fwd20.index:
            continue
        codes = g.index.get_level_values("code")
        future = fwd20.loc[dt].reindex(codes)
        state = str(g.state.iloc[0])
        for name, flag in flags.items():
            selected = g[flag].to_numpy(dtype=bool)
            r = future[selected]
            base_ret = future.mean()
            if r.notna().sum() < 3:
                continue
            rows.append(
                {
                    "universe": universe,
                    "date": dt,
                    "sample": "train" if dt < SPLIT else "test",
                    "state": state,
                    "event": name,
                    "n": int(r.notna().sum()),
                    "mean_forward20": float(r.mean()),
                    "excess_forward20": float(r.mean() - base_ret),
                    "hit_rate": float((r > base_ret).mean()),
                }
            )
    d = pd.DataFrame(rows)
    if d.empty:
        return d
    return (
        d.groupby(["universe", "sample", "state", "event"], as_index=False)
        .agg(
            n_dates=("date", "count"),
            avg_names=("n", "mean"),
            mean_forward20=("mean_forward20", "mean"),
            excess_forward20=("excess_forward20", "mean"),
            hit_rate=("hit_rate", "mean"),
        )
    )


def main() -> None:
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:END]
    fwd10 = forward_return(returns, STEP)
    fwd20 = forward_return(returns, HORIZON)

    all_ic = []
    all_maps = []
    all_selections = []
    all_bt = []
    all_events = []
    event_entry_rows = []
    panels = {}

    for universe in UNIVERSES:
        panel = build_panel(universe, returns, basic_panels)
        panels[universe] = panel
        ic = ic_detail(panel, fwd20, universe)
        all_ic.append(ic)
        static, mapping, map_df = factor_maps(ic, universe)
        all_maps.append(map_df)
        scores, selections = score_history(panel, ic, universe, static, mapping)
        all_selections.append(selections)
        for cost in COSTS:
            detail, entries = backtest(universe, panel, scores, fwd10, cost)
            all_bt.append(detail)
            if not entries.empty:
                entries["cost_bps"] = cost
                event_entry_rows.append(entries)
        ev = event_summary(panel, fwd20, universe)
        if not ev.empty:
            all_events.append(ev)

    ic = pd.concat(all_ic, ignore_index=True)
    overall_ic, conditional_ic = summarize_ic(ic)
    bt = pd.concat(all_bt, ignore_index=True)
    summary, yearly = performance(bt)
    maps = pd.concat(all_maps, ignore_index=True)
    selections = pd.concat(all_selections, ignore_index=True)
    events = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    entries = pd.concat(event_entry_rows, ignore_index=True) if event_entry_rows else pd.DataFrame()

    ic.to_csv(OUT / "factor_ic_detail.csv", index=False, encoding="utf-8-sig")
    overall_ic.to_csv(OUT / "factor_ic_overall.csv", index=False, encoding="utf-8-sig")
    conditional_ic.to_csv(OUT / "factor_ic_by_state.csv", index=False, encoding="utf-8-sig")
    maps.to_csv(OUT / "train_state_factor_map.csv", index=False, encoding="utf-8-sig")
    selections.to_csv(OUT / "meta_factor_selection_history.csv", index=False, encoding="utf-8-sig")
    bt.to_csv(OUT / "strategy_periods.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "strategy_summary.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(OUT / "strategy_yearly.csv", index=False, encoding="utf-8-sig")
    events.to_csv(OUT / "event_forward_return_summary.csv", index=False, encoding="utf-8-sig")
    entries.to_csv(OUT / "event_state_machine_entries.csv", index=False, encoding="utf-8-sig")

    key = summary[(summary["sample"] == "test") & (summary["cost_bps"] == 60)].sort_values(
        ["universe", "excess_sharpe"], ascending=[True, False]
    )
    factor_key = overall_ic[overall_ic["sample"] == "test"].sort_values(
        ["universe", "mean_ic"], ascending=[True, False]
    )
    event_key = events[events["sample"] == "test"].sort_values(
        ["universe", "excess_forward20"], ascending=[True, False]
    ) if not events.empty else pd.DataFrame()

    definitions = {
        "STATIC_BEST3": "Training-period overall IC top three factors, frozen out of sample.",
        "REGIME_ROTATION": "For each observable market and size-leadership state, use the two factors with the highest training conditional IC.",
        "TRAILING_IC_ROTATION": "Use the two factors with the strongest positive trailing realized 20-day IC, delayed by two snapshots.",
        "HYBRID_ROTATION": "Combine frozen training conditional IC with delayed trailing realized IC.",
        "EVENT_ONLY": "Invest only when a pre-defined factor sequence or conditional event occurs; otherwise hold cash.",
        "EVENT_PLUS_META": "Use event score when an event exists and the hybrid factor-rotation score otherwise.",
        "REGIME_HYSTERESIS": "Hybrid rotation with broad retain bands so names are not replaced solely by small rank changes.",
        "EVENT_STATE_MACHINE": "Stock-level entries on events and exits on age, score decay, or crowding deterioration.",
    }
    (OUT / "strategy_definitions.json").write_text(
        json.dumps(definitions, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md = [
        "# Conditional Factor Rotation & Event Lab",
        "",
        "## OOS strategy ranking at 60 bps one-way cost",
        "",
        key.to_markdown(index=False),
        "",
        "## OOS factor IC ranking",
        "",
        factor_key.to_markdown(index=False),
    ]
    if not event_key.empty:
        md += ["", "## OOS conditional event ranking", "", event_key.to_markdown(index=False)]
    (OUT / "summary.md").write_text("\n".join(md), encoding="utf-8")

    print("\n=== OOS STRATEGY RANKING, 60 BPS ===")
    print(key.to_string(index=False))
    print("\n=== OOS FACTOR IC ===")
    print(factor_key.groupby("universe").head(8).to_string(index=False))
    if not event_key.empty:
        print("\n=== OOS EVENT SUMMARY ===")
        print(event_key.groupby("universe").head(8).to_string(index=False))


if __name__ == "__main__":
    main()
