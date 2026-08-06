from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_current_recommendation"
OUT.mkdir(parents=True, exist_ok=True)

spec = importlib.util.spec_from_file_location("cur", HERE / "k200_current_recommendation.py")
cur = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cur)

off, enh, base = cur.off, cur.enh, cur.base
INDEX_ASSET = cur.INDEX_ASSET


def main() -> None:
    returns, basic_panels = base.load_basic()
    returns = returns.loc[:cur.END]
    panel = enh.lab.build_panel("K200", returns, basic_panels)
    fwd20 = enh.lab.forward_return(returns, enh.lab.HORIZON)
    ic = enh.lab.ic_detail(panel, fwd20, "K200")
    static, mapping, _ = enh.lab.factor_maps(ic, "K200")
    scores, _ = enh.lab.score_history(panel, ic, "K200", static, mapping)

    signal_dates = sorted(panel.index.get_level_values("date").unique())
    close = enh.download_kospi200()
    k200_period = enh.forward_index_returns(close, signal_dates, cur.STEP)
    detail, _ = off.run_all(panel, scores, returns, basic_panels, k200_period, cost_bps=60)
    diagnostics = cur.on_diagnostics(detail)

    latest_dt = panel.index.get_level_values("date").max()
    g0 = panel.loc[[latest_dt]]
    panel_latest = panel.xs(latest_dt, level="date")
    score_latest = scores[latest_dt].copy()
    state = str(panel_latest["state"].iloc[0])
    size_state = str(panel_latest["size_state"].iloc[0])

    valid_diag = diagnostics.dropna(
        subset=["leader_relative_90d", "k200_return_30d", "leader_relative_drawdown_120d"]
    )
    if valid_diag.empty:
        raise RuntimeError("No complete concentration diagnostics available")
    signal_input_date = valid_diag.index.max()
    diag = valid_diag.loc[signal_input_date]
    state_eligible = state in {"BROAD_RISK_ON", "NARROW_RISK_ON", "RISK_OFF"}
    on_signal = bool(
        state_eligible
        and diag.leader_relative_90d > 0.05
        and diag.k200_return_30d > 0.0
        and diag.leader_relative_drawdown_120d > -0.10
    )
    selected = cur.current_engine(state, size_state, on_signal)

    all_targets = off.targets_for_date(g0, score_latest, basic_panels[latest_dt])
    selected_weights = all_targets[selected].sort_values(ascending=False)
    current_weights = selected_weights.rename("weight").reset_index()
    current_weights.columns = ["asset", "weight"]
    current_weights["date"] = latest_dt
    current_weights["strategy"] = selected
    current_weights["cost_bps"] = 60

    name_map = cur.load_name_map(latest_dt)
    current_weights["name"] = current_weights.asset.map(name_map)
    current_weights.loc[current_weights.asset == INDEX_ASSET, "name"] = "KOSPI200 지수"
    current_weights["name"] = current_weights["name"].fillna(current_weights.asset)
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
    component.index.name = "code"
    component = component.reset_index()

    holding_detail = current_weights.merge(
        component, left_on="asset", right_on="code", how="left"
    )

    status = pd.DataFrame([{
        "data_date": latest_dt,
        "signal_input_date": signal_input_date,
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
        "selected_engine_ko": cur.ENGINE_KO[selected],
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
