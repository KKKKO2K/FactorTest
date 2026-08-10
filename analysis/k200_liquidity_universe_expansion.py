from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

import k200_nearby_universe_ladder as lad

ADD_N = int(os.environ.get("ADD_N", "50"))
LOOKBACK = int(os.environ.get("TA_LOOKBACK", "20"))
LABEL = f"K200_LIQ20_PLUS_{ADD_N}"
ROOT = Path(__file__).resolve().parents[1]
TA_DIR = ROOT / "source" / "factor_all_values" / "reference_snapshots" / "trading_amount"
OUT = Path(__file__).resolve().parent / "k200_liquidity_universe_expansion_results" / f"PLUS_{ADD_N}"
OUT.mkdir(parents=True, exist_ok=True)

# Reuse the exact production-control / router / engine simulation and metrics from
# the nearby-universe ladder. Only universe eligibility changes here.
lad.ADD_N = ADD_N
lad.LABEL = LABEL
lad.OUT = OUT

_BP_DATE_BY_ID: dict[int, pd.Timestamp] = {}
_TRADING_INDEX = pd.DatetimeIndex([])
_TA_FILE_CACHE: dict[pd.Timestamp, pd.Series] = {}
_TA20_CACHE: dict[pd.Timestamp, pd.Series] = {}
_ELIGIBILITY_ROWS: list[dict] = []
_SEEN_EFFECTIVE: set[pd.Timestamp] = set()


def _read_trading_amount_csv(path: Path) -> pd.DataFrame:
    last_error = None
    for enc in ("utf-8-sig", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, dtype={"Code": str}, encoding=enc)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return pd.read_csv(path, dtype={"Code": str})


def load_ta_day(dt: pd.Timestamp) -> pd.Series:
    dt = pd.Timestamp(dt)
    if dt in _TA_FILE_CACHE:
        return _TA_FILE_CACHE[dt]
    path = TA_DIR / f"{dt:%Y-%m-%d}.csv"
    if not path.exists():
        s = pd.Series(dtype=float)
    else:
        f = _read_trading_amount_csv(path)
        if "Code" not in f.columns or "거래대금(십억원)" not in f.columns:
            raise KeyError(f"Unexpected trading amount schema: {path}; columns={list(f.columns)}")
        s = pd.to_numeric(f["거래대금(십억원)"], errors="coerce")
        s.index = f["Code"].astype(str)
        s = s[~s.index.duplicated(keep="last")]
    _TA_FILE_CACHE[dt] = s
    return s


def trailing_avg_ta(eff: pd.Timestamp) -> pd.Series:
    eff = pd.Timestamp(eff)
    if eff in _TA20_CACHE:
        return _TA20_CACHE[eff]
    dates = _TRADING_INDEX[_TRADING_INDEX <= eff]
    dates = dates[-LOOKBACK:]
    frames = []
    for dt in dates:
        s = load_ta_day(pd.Timestamp(dt))
        if not s.empty:
            frames.append(s.rename(pd.Timestamp(dt)))
    if not frames:
        out = pd.Series(dtype=float)
    else:
        out = pd.concat(frames, axis=1).mean(axis=1, skipna=True)
    _TA20_CACHE[eff] = out
    return out


def liquidity_universe_codes(bp: pd.DataFrame, universe: str) -> pd.Index:
    if universe != LABEL:
        return lad.up._ORIGINAL_UC(bp, universe) if hasattr(lad.up, "_ORIGINAL_UC") else lad.up.universe_codes_ext(bp, universe)

    eff = _BP_DATE_BY_ID.get(id(bp))
    if eff is None:
        raise KeyError("Could not resolve effective basic_info snapshot date")

    market = bp["market"].astype(str).str.upper()
    k200 = pd.Index(bp.index[bp["k200"] == 1])
    ex_mask = market.str.contains("KOSPI", na=False) & (bp["k200"] == 0)
    ex_codes = pd.Index(bp.index[ex_mask])
    ta20 = trailing_avg_ta(eff).reindex(ex_codes)
    valid = ta20.dropna().sort_values(ascending=False)
    extra = valid.head(min(ADD_N, len(valid))).index

    if eff not in _SEEN_EFFECTIVE:
        selected = valid.reindex(extra).dropna()
        _ELIGIBILITY_ROWS.append({
            "effective_snapshot_date": eff,
            "lookback_days": LOOKBACK,
            "requested_extra_n": ADD_N,
            "available_ex_k200_with_ta": int(len(valid)),
            "selected_extra_n": int(len(extra)),
            "ta20_min_selected_billion": float(selected.min()) if len(selected) else np.nan,
            "ta20_median_selected_billion": float(selected.median()) if len(selected) else np.nan,
            "ta20_mean_selected_billion": float(selected.mean()) if len(selected) else np.nan,
        })
        _SEEN_EFFECTIVE.add(eff)

    return k200.union(pd.Index(extra))


def build_liquidity_expanded(returns, basic_panels):
    global _BP_DATE_BY_ID, _TRADING_INDEX
    _BP_DATE_BY_ID = {id(bp): pd.Timestamp(dt) for dt, bp in basic_panels.items()}
    _TRADING_INDEX = pd.DatetimeIndex(returns.index).sort_values()

    original = lad.up.universe_codes_ext
    lad.up._ORIGINAL_UC = original
    lad.up.universe_codes_ext = liquidity_universe_codes
    try:
        return lad.up.build_true_calendar_panel_universe(returns, basic_panels, LABEL)
    finally:
        lad.up.universe_codes_ext = original
        if hasattr(lad.up, "_ORIGINAL_UC"):
            delattr(lad.up, "_ORIGINAL_UC")


lad.build_expanded = build_liquidity_expanded


if __name__ == "__main__":
    print(
        f"Liquidity universe: K200 + top {ADD_N} KOSPI ex-K200 by trailing {LOOKBACK}D avg trading amount; "
        "trading amount is eligibility only, not an alpha score.",
        flush=True,
    )
    lad.main()
    pd.DataFrame(_ELIGIBILITY_ROWS).sort_values("effective_snapshot_date").to_csv(
        OUT / "liquidity_eligibility_diagnostics.csv", index=False, encoding="utf-8-sig"
    )
