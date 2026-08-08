from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
OUT = HERE / "k200_aug7_refresh_results"
OUT.mkdir(parents=True, exist_ok=True)

# Research branch code was frozen at 2026-07-31. Extend the local checkout only;
# no production code is changed or merged.
for filename in ("factor_rotation_event_lab.py", "enhanced_k200_allocation_test.py"):
    path = HERE / filename
    text = path.read_text(encoding="utf-8")
    text = text.replace('pd.Timestamp("2026-07-31")', 'pd.Timestamp("2026-08-07")')
    path.write_text(text, encoding="utf-8")

spec = importlib.util.spec_from_file_location("off", HERE / "k200_off_engine_lab.py")
off = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(off)

enh = off.enh
base = enh.base
INDEX_ASSET = off.INDEX_ASSET
STEP = off.STEP
COST_BPS = 60
OLD_DATE = pd.Timestamp("2026-07-22")
HEADERS = {"User-Agent": "Mozilla/5.0"}

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


def num(value):
    if value is None:
        return np.nan
    return float(str(value).replace(",", ""))


def fetch_naver_index(page_size: int = 300) -> pd.DataFrame:
    url = f"https://m.stock.naver.com/api/index/KPI200/price?pageSize={page_size}&page=1"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    f = pd.DataFrame(r.json())
    f["date"] = pd.to_datetime(f["localTradedAt"])
    f["open"] = f["openPrice"].map(num)
    f["close"] = f["closePrice"].map(num)
    return f.set_index("date")[["open", "close"]].sort_index()


def fetch_naver_stock(code: str, page_size: int = 80) -> pd.DataFrame:
    url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize={page_size}&page=1"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    f = pd.DataFrame(r.json())
    f["date"] = pd.to_datetime(f["localTradedAt"])
    f["open"] = f["openPrice"].map(num)
    f["close"] = f["closePrice"].map(num)
    return f.set_index("date")[["open", "close"]].sort_index()


def index_forward_returns(close: pd.Series, dates: list[pd.Timestamp], horizon: int) -> pd.Series:
    idx = close.index
    out = {}
    for dt in dates:
        pos = int(idx.searchsorted(dt, side="right"))
        if pos == 0 or pos + horizon - 1 >= len(idx):
            out[dt] = np.nan
            continue
        start_px = float(close.iloc[pos - 1])
        end_px = float(close.iloc[pos + horizon - 1])
        out[dt] = end_px / start_px - 1.0
    return pd.Series(out, name="k200_return")


def compound(s: pd.Series) -> float:
    s = pd.to_numeric(s, errors="coerce").dropna()
    return float((1.0 + s).prod() - 1.0) if len(s) else np.nan


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
    names = df[name_col].astype(str).str.strip() if name_col is not None else codes
    return pd.Series(names.values, index=codes.values).groupby(level=0).last()


def target_frame(weights: pd.Series, names: pd.Series, engine: str, dt: pd.Timestamp) -> pd.DataFrame:
    f = weights.rename("weight").reset_index().rename(columns={"index": "asset"})
    f["name"] = f["asset"].map(names)
    f.loc[f.asset == INDEX_ASSET, "name"] = "KOSPI200 지수"
    f["name"] = f["name"].fillna(f["asset"])
    f["weight_pct"] = f["weight"] * 100.0
    f["engine"] = engine
    f["date"] = dt
    return f.sort_values("weight", ascending=False)


def prices_for_assets(assets: set[str], index_prices: pd.DataFrame) -> dict[str, pd.DataFrame]:
    out = {INDEX_ASSET: index_prices}
    for asset in sorted(a for a in assets if a != INDEX_ASSET):
        out[asset] = fetch_naver_stock(asset)
    return out


def portfolio_return(weights: pd.Series, prices: dict[str, pd.DataFrame], start: pd.Timestamp, end: pd.Timestamp, start_field: str = "close"):
    rows = []
    total = 0.0
    for asset, w in weights.items():
        p = prices[asset]
        if start not in p.index or end not in p.index:
            raise RuntimeError(f"Missing price date for {asset}: {start} -> {end}")
        s = float(p.loc[start, start_field])
        e = float(p.loc[end, "close"])
        r = e / s - 1.0
        contrib = float(w) * r
        total += contrib
        rows.append({"asset": asset, "weight": float(w), "start": start, "end": end, "start_field": start_field, "start_px": s, "end_px": e, "return": r, "contribution": contrib})
    return float(total), pd.DataFrame(rows)


def drift_weights(weights: pd.Series, returns_by_asset: pd.Series) -> pd.Series:
    vals = weights * (1.0 + returns_by_asset.reindex(weights.index).fillna(0.0))
    return vals / vals.sum()


def turnover(old: pd.Series, new: pd.Series) -> float:
    idx = old.index.union(new.index)
    return 0.5 * float((old.reindex(idx, fill_value=0.0) - new.reindex(idx, fill_value=0.0)).abs().sum())


def main():
    returns, basic_panels = base.load_basic()
    returns = returns.loc[: pd.Timestamp("2026-08-07")]
    panel = enh.lab.build_panel("K200", returns, basic_panels)
    fwd20 = enh.lab.forward_return(returns, enh.lab.HORIZON)
    ic = enh.lab.ic_detail(panel, fwd20, "K200")
    static, mapping, _ = enh.lab.factor_maps(ic, "K200")
    scores, _ = enh.lab.score_history(panel, ic, "K200", static, mapping)

    dates = sorted(panel.index.get_level_values("date").unique())
    latest_dt = max(dates)
    if OLD_DATE not in dates:
        raise RuntimeError(f"Old signal date {OLD_DATE.date()} is not a scheduled panel date")

    index_prices = fetch_naver_index(300)
    k200_period = index_forward_returns(index_prices["close"], dates, STEP)
    detail, _ = off.run_all(panel, scores, returns, basic_panels, k200_period, cost_bps=COST_BPS)
    detail = detail.sort_values("date")

    # Current ON/OFF diagnostics use only completed 10-day periods available at latest_dt.
    pivot = detail.pivot(index="date", columns="strategy", values="net").sort_index()
    benchmark = detail[detail.strategy == "INDEX_ONLY"].set_index("date")["k200_return"].sort_index()
    completed_dates = pivot.index[pivot.index < latest_dt]
    rel = (1.0 + pivot.loc[completed_dates, "LEADER5_80"]) / (1.0 + benchmark.loc[completed_dates]) - 1.0
    leader_relative_90d = compound(rel.tail(9))
    k200_return_30d = compound(benchmark.loc[completed_dates].tail(3))
    rw = (1.0 + rel).cumprod()
    leader_relative_drawdown_120d = float(rw.iloc[-1] / rw.tail(12).max() - 1.0)

    p_latest = panel.xs(latest_dt, level="date")
    state = str(p_latest["state"].iloc[0])
    size_state = str(p_latest["size_state"].iloc[0])
    eligible = state in {"BROAD_RISK_ON", "NARROW_RISK_ON", "RISK_OFF"}
    on_signal = bool(eligible and leader_relative_90d > 0.05 and k200_return_30d > 0.0 and leader_relative_drawdown_120d > -0.10)
    engine = current_engine(state, size_state, on_signal)

    latest_targets = off.targets_for_date(p_latest, scores[latest_dt], basic_panels[latest_dt])
    new_w = latest_targets[engine].sort_values(ascending=False)
    fallback_engine = current_engine(state, size_state, False)
    fallback_w = latest_targets[fallback_engine].sort_values(ascending=False)

    # Reconstruct old 2026-07-22 portfolio under the same rules used previously.
    p_old = panel.xs(OLD_DATE, level="date")
    old_targets = off.targets_for_date(p_old, scores[OLD_DATE], basic_panels[OLD_DATE])
    old_w = old_targets["LEADER5_80"].sort_values(ascending=False)

    old_names = load_name_map(OLD_DATE)
    latest_names = load_name_map(latest_dt)
    old_frame = target_frame(old_w, old_names, "LEADER5_80", OLD_DATE)
    new_frame = target_frame(new_w, latest_names, engine, latest_dt)
    fallback_frame = target_frame(fallback_w, latest_names, fallback_engine, latest_dt)

    # Factor and sequence detail at the new rebalance date.
    z = scores[latest_dt]
    codes = p_latest.index
    factor = pd.DataFrame(index=codes)
    factor["name"] = latest_names.reindex(codes)
    factor["leader_score"] = (
        0.30 * p_latest["long_up"]
        + 0.20 * p_latest["short_up"]
        + 0.25 * p_latest["revision"]
        + 0.15 * p_latest["private_persist"]
        + 0.10 * p_latest["size_rank"]
    )
    factor["long_momentum"] = p_latest["long_up"]
    factor["short_momentum"] = p_latest["short_up"]
    factor["revision"] = p_latest["revision"]
    factor["private_persist"] = p_latest["private_persist"]
    factor["size_rank"] = p_latest["size_rank"]
    factor["event_any"] = p_latest["event_any"]
    factor["event_type"] = p_latest["event_type"]
    factor["flow_revision"] = p_latest["event_flow_revision"]
    factor["three_stage"] = p_latest["event_three_stage"]
    factor["dual_revision"] = p_latest["event_dual_revision"]
    factor["value_unlock"] = p_latest["event_value_unlock"]
    factor["pullback"] = p_latest["event_pullback"]
    factor["sequence_count"] = factor[["flow_revision", "three_stage", "dual_revision"]].sum(axis=1)
    factor["leader_rank"] = factor["leader_score"].rank(pct=True)
    factor.index.name = "asset"
    factor = factor.reset_index()
    selected_factor = new_frame.merge(factor, on="asset", how="left", suffixes=("", "_factor"))

    # Realized performance of old portfolio, and partial performance of new portfolio.
    latest_price_date = pd.Timestamp("2026-08-07")
    assets = set(old_w.index).union(new_w.index)
    prices = prices_for_assets(assets, index_prices)
    old_10d, old_10d_assets = portfolio_return(old_w, prices, OLD_DATE, latest_dt, "close")
    old_to_aug7, old_aug7_assets = portfolio_return(old_w, prices, OLD_DATE, latest_price_date, "close")
    new_partial, new_partial_assets = portfolio_return(new_w, prices, latest_dt, latest_price_date, "close")

    post_latest = index_prices.index[index_prices.index > latest_dt]
    next_trade = post_latest[0]
    new_next_open, new_next_open_assets = portfolio_return(new_w, prices, next_trade, latest_price_date, "open")

    k200_10d = float(index_prices.loc[latest_dt, "close"] / index_prices.loc[OLD_DATE, "close"] - 1.0)
    k200_to_aug7 = float(index_prices.loc[latest_price_date, "close"] / index_prices.loc[OLD_DATE, "close"] - 1.0)
    k200_new_partial = float(index_prices.loc[latest_price_date, "close"] / index_prices.loc[latest_dt, "close"] - 1.0)
    k200_next_open = float(index_prices.loc[latest_price_date, "close"] / index_prices.loc[next_trade, "open"] - 1.0)

    old_asset_returns = old_10d_assets.set_index("asset")["return"]
    old_drift = drift_weights(old_w, old_asset_returns)
    rebalance_turnover = turnover(old_drift, new_w)
    rebalance_cost = rebalance_turnover * COST_BPS / 10000.0
    chained_gross = (1.0 + old_10d) * (1.0 + new_partial) - 1.0
    chained_net_rebal_cost = (1.0 + old_10d) * (1.0 + new_partial - rebalance_cost) - 1.0
    chained_net_full_entry = (1.0 + old_10d - COST_BPS / 10000.0) * (1.0 + new_partial - rebalance_cost) - 1.0

    status = {
        "latest_factor_data_available": "2026-08-07",
        "latest_scheduled_rebalance_date": str(latest_dt.date()),
        "market_state": state,
        "size_state": size_state,
        "market60": float(p_latest["market60"].iloc[0]),
        "breadth60": float(p_latest["breadth60"].iloc[0]),
        "market_vol20": float(p_latest["market_vol20"].iloc[0]),
        "dispersion20": float(p_latest["dispersion20"].iloc[0]),
        "size_lead60": float(p_latest["size_lead60"].iloc[0]),
        "leader_relative_90d": leader_relative_90d,
        "k200_return_30d": k200_return_30d,
        "leader_relative_drawdown_120d": leader_relative_drawdown_120d,
        "concentration_on": on_signal,
        "selected_engine": engine,
        "selected_engine_ko": ENGINE_KO[engine],
        "off_engine_if_concentration_off": fallback_engine,
        "off_engine_ko": ENGINE_KO[fallback_engine],
        "old_portfolio_7_22_to_rebalance": old_10d,
        "k200_7_22_to_rebalance": k200_10d,
        "old_active_7_22_to_rebalance": (1.0 + old_10d) / (1.0 + k200_10d) - 1.0,
        "old_portfolio_7_22_to_8_7_hold": old_to_aug7,
        "k200_7_22_to_8_7": k200_to_aug7,
        "old_hold_active_to_8_7": (1.0 + old_to_aug7) / (1.0 + k200_to_aug7) - 1.0,
        "new_portfolio_rebalance_close_to_8_7": new_partial,
        "k200_rebalance_close_to_8_7": k200_new_partial,
        "new_active_rebalance_close_to_8_7": (1.0 + new_partial) / (1.0 + k200_new_partial) - 1.0,
        "new_portfolio_next_open_to_8_7": new_next_open,
        "k200_next_open_to_8_7": k200_next_open,
        "new_active_next_open_to_8_7": (1.0 + new_next_open) / (1.0 + k200_next_open) - 1.0,
        "rebalance_turnover": rebalance_turnover,
        "rebalance_cost_60bps": rebalance_cost,
        "chained_gross_7_22_to_8_7": chained_gross,
        "chained_net_rebalance_cost_7_22_to_8_7": chained_net_rebal_cost,
        "chained_net_full_entry_cost_7_22_to_8_7": chained_net_full_entry,
        "chained_active_gross_vs_k200": (1.0 + chained_gross) / (1.0 + k200_to_aug7) - 1.0,
    }

    pd.DataFrame([status]).to_csv(OUT / "status_and_performance.csv", index=False, encoding="utf-8-sig")
    old_frame.to_csv(OUT / "old_2026_07_22_target.csv", index=False, encoding="utf-8-sig")
    new_frame.to_csv(OUT / "new_rebalance_target.csv", index=False, encoding="utf-8-sig")
    fallback_frame.to_csv(OUT / "off_engine_target_if_off.csv", index=False, encoding="utf-8-sig")
    selected_factor.to_csv(OUT / "new_target_factor_sequence_detail.csv", index=False, encoding="utf-8-sig")
    old_10d_assets.to_csv(OUT / "old_portfolio_10d_asset_contributions.csv", index=False, encoding="utf-8-sig")
    old_aug7_assets.to_csv(OUT / "old_portfolio_hold_to_aug7_asset_contributions.csv", index=False, encoding="utf-8-sig")
    new_partial_assets.to_csv(OUT / "new_portfolio_partial_asset_contributions.csv", index=False, encoding="utf-8-sig")
    new_next_open_assets.to_csv(OUT / "new_portfolio_next_open_asset_contributions.csv", index=False, encoding="utf-8-sig")
    (OUT / "summary.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    print("=== STATUS ===")
    print(json.dumps(status, ensure_ascii=False, indent=2))
    print("\n=== OLD TARGET ===")
    print(old_frame[["asset", "name", "weight_pct"]].to_string(index=False))
    print("\n=== NEW TARGET ===")
    print(new_frame[["asset", "name", "weight_pct"]].to_string(index=False))
    print("\n=== NEW TARGET FACTOR/SEQUENCE ===")
    cols = ["asset", "name", "weight_pct", "leader_score", "leader_rank", "revision", "long_momentum", "short_momentum", "private_persist", "event_type", "sequence_count"]
    print(selected_factor[[c for c in cols if c in selected_factor.columns]].to_string(index=False))


if __name__ == "__main__":
    main()
