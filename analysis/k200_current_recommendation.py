from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_current_recommendation"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("off", HERE / "k200_off_engine_lab.py")
off = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(off)

enh = off.enh
idx = off.idx
base = enh.base
STEP = off.STEP
END = off.END
INDEX_ASSET = off.INDEX_ASSET

ENGINE_KO = {
    "INDEX_ONLY": "KOSPI200 100%",
    "LEADER5_80": "KOSPI200 20% + Top-5 Leader 80%",
    "VALUE_REV_30": "KOSPI200 70% + Value & Revision 30%",
    "REV_BREADTH_70": "KOSPI200 30% + Revision Breadth 70%",
    "CONTRARIAN_70": "KOSPI200 30% + Contrarian 70%",
    "PYRAMID_50": "KOSPI200 50% + Pyramid 50%",
}


def current_engine(state: str, size_state: str, on_signal: bool) -> str:
    if on_signal:
        return "LEADER5_80"
    if size_state != "LARGE_LEAD":
        return "INDEX_ONLY"
    return {
        "BROAD_RISK_ON": "VALUE_REV_30",
        "HIGH_DISPERSION": "REV_BREADTH_70",
        "RISK_OFF": "CONTRARIAN_70",
        "NEUTRAL": "PYRAMID_50",
    }.get(state, "INDEX_ONLY")


def load_name_map(dt: pd.Timestamp) -> pd.Series:
    path = base.BASIC / f"{dt.date().isoformat()}.csv"
    df = base.read_csv(path)
    code_col = base.code_col(df)
    name_col = base.find_col(
        df,
        exact=("종목명", "기업명", "한글종목명"),
        contains=("종목명", "기업명", "회사명", "name"),
    )
    codes = base.norm_code(df[code_col])
    if name_col is None:
        return pd.Series(codes.values, index=codes.values)
    names = df[name_col].astype(str).str.strip()
    return pd.Series(names.values, index=codes.values).groupby(level=0).last()


def on_diagnostics(detail: pd.DataFrame) -> pd.DataFrame:
    p = detail.pivot(index="date", columns="strategy", values="net").sort_index()
    benchmark = detail[detail.strategy == "INDEX_ONLY"].set_index("date")["k200_return"].sort_index()
    state = detail[detail.strategy == "INDEX_ONLY"].set_index("date")["state"].sort_index()
    leader = p["LEADER5_80"]
    rel = (1.0 + leader) / (1.0 + benchmark) - 1.0
    trail9 = off.trailing_compound(rel, 9)
    bench3 = off.trailing_compound(benchmark, 3)
    rel_wealth = (1.0 + leader).cumprod() / (1.0 + benchmark).cumprod()
    dd12 = rel_wealth.shift(1) / rel_wealth.shift(1).rolling(12, min_periods=12).max() - 1.0
    eligible = state.isin({"BROAD_RISK_ON", "NARROW_RISK_ON", "RISK_OFF"})
    out = pd.DataFrame({
        "state": state,
        "leader_relative_90d": trail9,
        "k200_return_30d": bench3,
        "leader_relative_drawdown_120d": dd12,
        "state_eligible": eligible,
    })
    out["on_signal"] = (
        out.state_eligible
        & (out.leader_relative_90d > 0.05)
        & (out.k200_return_30d > 0.0)
        & (out.leader_relative_drawdown_120d > -0.10)
    )
    return out


def main() -> None:
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:END]
    panel = enh.lab.build_panel("K200", returns, basic_panels)
    fwd20 = enh.lab.forward_return(returns, enh.lab.HORIZON)
    ic = enh.lab.ic_detail(panel, fwd20, "K200")
    static, mapping, _ = enh.lab.factor_maps(ic, "K200")
    scores, _ = enh.lab.score_history(panel, ic, "K200", static, mapping)

    signal_dates = sorted(panel.index.get_level_values("date").unique())
    close = enh.download_kospi200()
    k200_period = enh.forward_index_returns(close, signal_dates, STEP)
    detail, target_weights = off.run_all(
        panel, scores, returns, basic_panels, k200_period, cost_bps=60
    )
    diagnostics = on_diagnostics(detail)

    latest_dt = min(panel.index.get_level_values("date").max(), detail.date.max())
    panel_latest = panel.xs(latest_dt, level="date")
    score_latest = scores[latest_dt].copy()
    state = str(panel_latest["state"].iloc[0])
    size_state = str(panel_latest["size_state"].iloc[0])
    on_signal = bool(diagnostics.loc[latest_dt, "on_signal"])
    selected = current_engine(state, size_state, on_signal)

    current_weights = target_weights[
        (target_weights.date == latest_dt)
        & (target_weights.strategy == selected)
        & (target_weights.cost_bps == 60)
    ].copy()
    if current_weights.empty:
        raise RuntimeError(f"No target weights for {latest_dt=} {selected=}")

    name_map = load_name_map(latest_dt)
    current_weights["name"] = current_weights.asset.map(name_map)
    current_weights.loc[current_weights.asset == INDEX_ASSET, "name"] = "KOSPI200 지수"
    current_weights["name"] = current_weights["name"].fillna(current_weights.asset)
    current_weights = current_weights.sort_values("weight", ascending=False)
    current_weights["weight_pct"] = current_weights.weight * 100.0

    codes = panel_latest.index
    component = pd.DataFrame(index=codes)
    component["name"] = name_map.reindex(codes)
    component["mcap"] = panel_latest["mcap"]
    component["size_rank"] = panel_latest["size_rank"]
    component["value"] = panel_latest["VALUE"]
    component["revision"] = panel_latest["REVISION"]
    component["private"] = panel_latest["PRIVATE"]
    component["short_reversal"] = panel_latest["SHORT_REVERSAL"]
    component["long_momentum"] = panel_latest["LONG_MOM"]
    component["value_unlock"] = panel_latest["VALUE_UNLOCK"]
    component["earnings_breadth"] = panel_latest["EARNINGS_BREADTH"]
    component["ownership_transfer"] = panel_latest["OWNERSHIP_TRANSFER"]
    component["private_persist"] = panel_latest["private_persist"]
    component["vol20_rank"] = panel_latest["vol20_rank"]
    component["meta_score"] = score_latest["EVENT_PLUS_META"].reindex(codes)
    component["event_any"] = score_latest["event_any"].reindex(codes)
    component["event_type"] = score_latest["event_type"].reindex(codes)

    low_vol = 1.0 - component["vol20_rank"]
    component["value_revision_score"] = (
        0.35 * component.value
        + 0.25 * component.revision
        + 0.25 * component.value_unlock
        + 0.15 * component.private
    )
    component["revision_breadth_score"] = (
        0.30 * component.revision
        + 0.30 * component.earnings_breadth
        + 0.20 * component.long_momentum
        + 0.20 * component.private
    )
    component["contrarian_score"] = (
        0.35 * component.value
        + 0.30 * component.short_reversal
        + 0.20 * component.private
        + 0.15 * component.revision
    )
    component["leader_score"] = (
        0.30 * panel_latest["long_up"]
        + 0.20 * panel_latest["short_up"]
        + 0.25 * panel_latest["revision"]
        + 0.15 * panel_latest["private_persist"]
        + 0.10 * panel_latest["size_rank"]
    )
    component["low_vol_score"] = low_vol
    component.index.name = "code"
    component = component.reset_index()

    held_codes = current_weights.loc[current_weights.asset != INDEX_ASSET, "asset"]
    holding_detail = current_weights.merge(
        component,
        left_on="asset",
        right_on="code",
        how="left",
        suffixes=("", "_factor"),
    )

    diag = diagnostics.loc[latest_dt]
    status = pd.DataFrame([{
        "data_date": latest_dt,
        "market_state": state,
        "size_state": size_state,
        "market60": float(panel_latest["market60"].iloc[0]),
        "breadth60": float(panel_latest["breadth60"].iloc[0]),
        "market_vol20": float(panel_latest["market_vol20"].iloc[0]),
        "dispersion20": float(panel_latest["dispersion20"].iloc[0]),
        "high_vol": bool(panel_latest["high_vol"].iloc[0]),
        "high_dispersion": bool(panel_latest["high_disp"].iloc[0]),
        "size_lead60": float(panel_latest["size_lead60"].iloc[0]),
        "leader_relative_90d": float(diag.leader_relative_90d),
        "k200_return_30d": float(diag.k200_return_30d),
        "leader_relative_drawdown_120d": float(diag.leader_relative_drawdown_120d),
        "concentration_on": on_signal,
        "selected_engine": selected,
        "selected_engine_ko": ENGINE_KO[selected],
        "number_of_stock_positions": int((current_weights.asset != INDEX_ASSET).sum()),
        "index_weight": float(current_weights.loc[current_weights.asset == INDEX_ASSET, "weight"].sum()),
        "stock_weight": float(current_weights.loc[current_weights.asset != INDEX_ASSET, "weight"].sum()),
    }])

    status.to_csv(OUT / "current_status.csv", index=False, encoding="utf-8-sig")
    current_weights.to_csv(OUT / "current_target_weights.csv", index=False, encoding="utf-8-sig")
    holding_detail.to_csv(OUT / "current_holding_factor_details.csv", index=False, encoding="utf-8-sig")
    component.sort_values("contrarian_score", ascending=False).to_csv(
        OUT / "latest_all_stock_scores.csv", index=False, encoding="utf-8-sig"
    )
    diagnostics.to_csv(OUT / "concentration_signal_diagnostics.csv", encoding="utf-8-sig")

    print(status.to_string(index=False))
    print(current_weights[["asset", "name", "weight_pct"]].head(30).to_string(index=False))


if __name__ == "__main__":
    main()
