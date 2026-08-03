from __future__ import annotations

import itertools
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "source" / "factor_all_values"
BASIC = DATA / "reference_snapshots" / "basic_info"
OUT = ROOT / "analysis" / "methodology_results_fast"
OUT.mkdir(parents=True, exist_ok=True)

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
FACTOR_DIRS = {
    "op12": DATA / "OP(12MF_1M_CHG)",
    "opfy1": DATA / "OP(FY1_1M_CHG)",
    "pbr": DATA / "PBR(12MF)",
    "per": DATA / "PER(12MF)",
}
SPLIT_DATE = pd.Timestamp("2023-05-26")
START_DATE = pd.Timestamp("2016-04-01")
COSTS_BPS = (10, 30, 60, 100)
INTERVALS = (5, 10, 20, 40)
TARGET_NS = (10, 20, 30)
WEIGHT_METHODS = ("equal", "rank_linear", "inverse_vol", "rank_inverse_vol", "sqrt_mcap")
CAP_MULTS = (2.0,)


def read_csv(path: Path) -> pd.DataFrame:
    last = None
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Could not read {path}: {last}")


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out = {}
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def find_code_col(df: pd.DataFrame) -> str:
    for c in df.columns:
        if str(c).strip().lower() in {"code", "종목코드", "ticker", "stockcode"}:
            return c
    raise KeyError(f"Code column missing: {list(df.columns)}")


def normalize_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return x.where(x.str.startswith("A"), "A" + x.str.zfill(6))


def find_col(df: pd.DataFrame, exact: list[str] | None = None, contains: list[str] | None = None) -> str | None:
    exact = exact or []
    contains = contains or []
    for c in df.columns:
        s = str(c).strip()
        if s in exact:
            return c
    for c in df.columns:
        s = str(c).strip().lower()
        if any(k.lower() in s for k in contains):
            return c
    return None


def load_basic() -> tuple[pd.DataFrame, pd.DataFrame, dict[pd.Timestamp, pd.DataFrame]]:
    ret_rows = []
    cap_rows = []
    panels = {}
    for dt, path in dated_files(BASIC).items():
        df = read_csv(path)
        code_col = find_code_col(df)
        ret_col = find_col(df, exact=["수정주가수익률"], contains=["수정주가수익률", "daily_return"])
        cap_col = find_col(df, exact=["시가총액"], contains=["시가총액"])
        market_col = find_col(df, exact=["상장된 시장"], contains=["상장된 시장", "market"])
        k200_col = find_col(df, contains=["코스피200", "k200"])
        if ret_col is None or cap_col is None:
            continue
        code = normalize_code(df[code_col])
        ret = pd.to_numeric(df[ret_col], errors="coerce") / 100.0
        cap = pd.to_numeric(df[cap_col], errors="coerce")
        market = df[market_col].astype(str).str.upper().str.strip() if market_col else ""
        k200 = pd.to_numeric(df[k200_col], errors="coerce").fillna(0).astype(int) if k200_col else 0
        panel = pd.DataFrame({
            "code": code,
            "ret": ret,
            "mcap": cap,
            "market": market,
            "k200": k200,
        }).drop_duplicates("code", keep="last").set_index("code")
        panels[dt] = panel
        ret_rows.append(pd.DataFrame({"date": dt, "code": panel.index, "ret": panel["ret"].to_numpy()}))
        cap_rows.append(pd.DataFrame({"date": dt, "code": panel.index, "mcap": panel["mcap"].to_numpy()}))
    returns = pd.concat(ret_rows, ignore_index=True).pivot(index="date", columns="code", values="ret").sort_index()
    c = pd.concat(cap_rows, ignore_index=True).pivot(index="date", columns="code", values="mcap").sort_index()
    return returns, c, panels


def load_factor_on_date(folder: Path, dt: pd.Timestamp) -> pd.Series:
    path = folder / f"{dt.date().isoformat()}.csv"
    if not path.exists():
        return pd.Series(dtype=float)
    df = read_csv(path)
    code_col = find_code_col(df)
    val_col = find_col(df, exact=["FactorValue"], contains=["factorvalue"])
    if val_col is None:
        numeric = []
        for c in df.columns:
            if c == code_col:
                continue
            s = pd.to_numeric(df[c], errors="coerce")
            if s.notna().sum() >= 20 and s.nunique(dropna=True) >= 5:
                numeric.append((c, s.notna().sum()))
        if not numeric:
            return pd.Series(dtype=float)
        val_col = max(numeric, key=lambda x: x[1])[0]
    codes = normalize_code(df[code_col])
    vals = pd.to_numeric(df[val_col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return pd.Series(vals.to_numpy(), index=codes).groupby(level=0).last()


def rank_pct(s: pd.Series, high_is_good: bool) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    return s.rank(pct=True, method="average", ascending=high_is_good)


def build_signal_panel(
    dt: pd.Timestamp,
    basic_panel: pd.DataFrame,
    factor_cache: dict[tuple[str, pd.Timestamp], pd.Series],
    returns: pd.DataFrame,
) -> pd.DataFrame:
    p = basic_panel.copy()
    for name, folder in FACTOR_DIRS.items():
        key = (name, dt)
        if key not in factor_cache:
            factor_cache[key] = load_factor_on_date(folder, dt)
        p[name] = factor_cache[key].reindex(p.index)
    p["cheap_per"] = rank_pct(-p["per"], high_is_good=True)
    p["cheap_pbr"] = rank_pct(-p["pbr"], high_is_good=True)
    p["value"] = p[["cheap_per", "cheap_pbr"]].mean(axis=1)
    p["rev_fy1"] = rank_pct(p["opfy1"], high_is_good=True)
    p["rev_12"] = rank_pct(p["op12"], high_is_good=True)
    p["global_mcap_rank"] = p["mcap"].rank(pct=True, method="average")
    hist = returns.loc[:dt].tail(60)
    p["vol60"] = hist.std(ddof=1).reindex(p.index)
    return p


def universe_panel(panel: pd.DataFrame, strategy: str) -> pd.DataFrame:
    if strategy == "K200_VETO":
        u = panel[panel["k200"] == 1].copy()
    elif strategy == "KOSDAQ_REV_FIRST":
        u = panel[panel["market"].str.contains("KOSDAQ", na=False)].copy()
    else:
        raise ValueError(strategy)
    u["cheap_per"] = rank_pct(-u["per"], True)
    u["cheap_pbr"] = rank_pct(-u["pbr"], True)
    u["value"] = u[["cheap_per", "cheap_pbr"]].mean(axis=1)
    u["rev_fy1"] = rank_pct(u["opfy1"], True)
    u["rev_12"] = rank_pct(u["op12"], True)
    if strategy == "K200_VETO":
        u["score"] = 0.75 * u["value"] + 0.15 * u["rev_fy1"].fillna(0.5) + 0.10 * u["rev_12"].fillna(0.5)
    else:
        u["score"] = 0.70 * u["rev_fy1"] + 0.30 * u["value"]
    return u


def candidate_masks(u: pd.DataFrame, strategy: str) -> tuple[pd.Series, pd.Series, pd.Series]:
    if strategy == "K200_VETO":
        required = u[["per", "pbr", "opfy1", "op12"]].notna().all(axis=1)
        entry = required & (u["value"] >= 0.80) & (u["rev_fy1"] >= 0.20) & (u["rev_12"] >= 0.20)
        retain = required & (u["value"] >= 0.70) & (u["rev_fy1"] >= 0.15) & (u["rev_12"] >= 0.15)
    else:
        required = u[["per", "pbr", "opfy1"]].notna().all(axis=1)
        entry = required & (u["rev_fy1"] >= 0.80) & (u["value"] >= 0.40)
        retain = required & (u["rev_fy1"] >= 0.70) & (u["value"] >= 0.30)
    return required, entry, retain


def select_names(u: pd.DataFrame, strategy: str, n_target: int, current: list[str], buffer: bool) -> tuple[list[str], list[str]]:
    required, entry, retain = candidate_masks(u, strategy)
    eligible = u.index[required].tolist()
    entrants = u.loc[entry].sort_values("score", ascending=False).index.tolist()
    if not buffer:
        return entrants[:n_target], eligible
    keep = [c for c in current if c in u.index and bool(retain.reindex([c]).fillna(False).iloc[0])]
    keep = sorted(keep, key=lambda c: float(u.at[c, "score"]), reverse=True)[:n_target]
    fill = [c for c in entrants if c not in keep]
    return keep + fill[: max(0, n_target - len(keep))], eligible


def cap_weights(raw: pd.Series, cap: float) -> pd.Series:
    w = raw.clip(lower=0).astype(float)
    if not np.isfinite(w).all() or w.sum() <= 0:
        w = pd.Series(1.0, index=raw.index)
    w /= w.sum()
    cap = max(cap, 1.0 / len(w))
    for _ in range(20):
        over = w > cap + 1e-12
        if not over.any():
            break
        excess = float((w[over] - cap).sum())
        w.loc[over] = cap
        under = ~over
        if not under.any() or w.loc[under].sum() <= 0:
            break
        w.loc[under] += excess * w.loc[under] / w.loc[under].sum()
    return w / w.sum()


def target_weights(u: pd.DataFrame, names: list[str], method: str, cap_mult: float) -> pd.Series:
    if not names:
        return pd.Series(dtype=float)
    x = u.loc[names].sort_values("score", ascending=False)
    n = len(x)
    if method == "equal":
        raw = pd.Series(1.0, index=x.index)
        cap_mult = 1.0
    elif method == "rank_linear":
        raw = pd.Series(np.arange(n, 0, -1, dtype=float), index=x.index)
    elif method == "inverse_vol":
        v = x["vol60"].clip(lower=x["vol60"].quantile(0.10), upper=x["vol60"].quantile(0.90))
        raw = 1.0 / v.replace(0, np.nan)
    elif method == "rank_inverse_vol":
        rank = pd.Series(np.arange(n, 0, -1, dtype=float), index=x.index)
        v = x["vol60"].clip(lower=x["vol60"].quantile(0.10), upper=x["vol60"].quantile(0.90))
        raw = rank / v.replace(0, np.nan)
    elif method == "sqrt_mcap":
        raw = np.sqrt(x["mcap"].clip(lower=0))
    else:
        raise ValueError(method)
    return cap_weights(raw.replace([np.inf, -np.inf], np.nan).fillna(0), cap_mult / n)


def make_rebalance_dates(dates: pd.DatetimeIndex, interval: int) -> pd.DatetimeIndex:
    return dates[dates >= START_DATE][::interval]


def drift_weights(weights: pd.Series, returns_row: pd.Series, port_ret: float) -> pd.Series:
    if weights.empty:
        return weights
    rr = returns_row.reindex(weights.index).fillna(0.0)
    denom = 1.0 + port_ret
    if denom <= 0:
        return pd.Series(dtype=float)
    w = weights * (1.0 + rr) / denom
    return w[w.abs() > 1e-14]


def turnover_to_target(current: pd.Series, target: pd.Series) -> float:
    idx = current.index.union(target.index)
    delta = target.reindex(idx, fill_value=0.0) - current.reindex(idx, fill_value=0.0)
    current_cash = 1.0 - float(current.sum())
    target_cash = 1.0 - float(target.sum())
    return 0.5 * (float(delta.abs().sum()) + abs(target_cash - current_cash))


def simulate_config(returns: pd.DataFrame, prepared: dict[str, dict[pd.Timestamp, pd.DataFrame]], strategy: str, interval: int, n_target: int, method: str, buffer: bool, cap_mult: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    dates = returns.index[returns.index >= START_DATE]
    rebalance_dates = set(make_rebalance_dates(dates, interval))
    weights = pd.Series(dtype=float)
    bench_w = pd.Series(dtype=float)
    current_names: list[str] = []
    pending_turnover = 0.0
    records = []
    rebalances = []
    for dt in dates:
        rr = returns.loc[dt]
        gross = float((weights * rr.reindex(weights.index).fillna(0.0)).sum()) if not weights.empty else 0.0
        bench = float((bench_w * rr.reindex(bench_w.index).fillna(0.0)).sum()) if not bench_w.empty else 0.0
        records.append({"date": dt, "gross_ret": gross, "bench_ret": bench, "turnover_event": pending_turnover, "n_names": len(weights)})
        pending_turnover = 0.0
        weights = drift_weights(weights, rr, gross)
        bench_w = drift_weights(bench_w, rr, bench)
        if dt in rebalance_dates and dt in prepared[strategy]:
            u = prepared[strategy][dt]
            names, eligible = select_names(u, strategy, n_target, current_names, buffer)
            target = target_weights(u, names, method, cap_mult)
            pending_turnover = turnover_to_target(weights, target)
            bench_w = pd.Series(1.0 / len(eligible), index=eligible) if eligible else pd.Series(dtype=float)
            rebalances.append({"date": dt, "turnover": pending_turnover, "n_selected": len(names), "n_eligible": len(eligible), "max_weight": float(target.max()) if not target.empty else np.nan, "hhi": float((target ** 2).sum()) if not target.empty else np.nan})
            weights = target
            current_names = names
    return pd.DataFrame(records).set_index("date"), pd.DataFrame(rebalances)


def max_drawdown(r: pd.Series) -> float:
    wealth = (1.0 + r.fillna(0.0)).cumprod()
    return float((wealth / wealth.cummax() - 1.0).min())


def metrics(r: pd.Series) -> dict[str, float]:
    r = r.dropna()
    if len(r) < 20:
        return {k: np.nan for k in ("cagr", "vol", "sharpe", "mdd", "hit")}
    years = len(r) / 252.0
    wealth = float((1 + r).prod())
    cagr = wealth ** (1 / years) - 1 if wealth > 0 and years > 0 else np.nan
    vol = float(r.std(ddof=1) * math.sqrt(252))
    sharpe = float(r.mean() / r.std(ddof=1) * math.sqrt(252)) if r.std(ddof=1) > 0 else np.nan
    return {"cagr": cagr, "vol": vol, "sharpe": sharpe, "mdd": max_drawdown(r), "hit": float((r > 0).mean())}


def summarize_run(daily: pd.DataFrame, rebal: pd.DataFrame, cfg: dict, cost_bps: int, period_name: str, mask: pd.Series) -> dict:
    d = daily.loc[mask].copy()
    net = d["gross_ret"] - d["turnover_event"] * cost_bps / 10000.0
    excess = net - d["bench_ret"]
    gross_m, net_m, ex_m = metrics(d["gross_ret"]), metrics(net), metrics(excess)
    rdates = rebal[(rebal["date"] >= d.index.min()) & (rebal["date"] <= d.index.max())] if not rebal.empty else rebal
    out = dict(cfg)
    out.update({
        "cost_bps": cost_bps,
        "period": period_name,
        "start": d.index.min().date().isoformat(),
        "end": d.index.max().date().isoformat(),
        "n_days": len(d),
        "gross_cagr": gross_m["cagr"],
        "net_cagr": net_m["cagr"],
        "net_vol": net_m["vol"],
        "net_sharpe": net_m["sharpe"],
        "net_mdd": net_m["mdd"],
        "excess_cagr": ex_m["cagr"],
        "excess_vol": ex_m["vol"],
        "excess_sharpe": ex_m["sharpe"],
        "excess_mdd": ex_m["mdd"],
        "avg_turnover_rebal": rdates["turnover"].mean() if not rdates.empty else np.nan,
        "annual_turnover": rdates["turnover"].sum() / max(len(d) / 252.0, 1e-9) if not rdates.empty else np.nan,
        "avg_names": rdates["n_selected"].mean() if not rdates.empty else np.nan,
        "avg_eligible": rdates["n_eligible"].mean() if not rdates.empty else np.nan,
        "avg_max_weight": rdates["max_weight"].mean() if not rdates.empty else np.nan,
        "avg_effective_names": (1.0 / rdates["hhi"]).mean() if not rdates.empty else np.nan,
    })
    return out


def main():
    returns, _mcaps, panels = load_basic()
    base_dates = make_rebalance_dates(returns.index, min(INTERVALS))
    cache: dict[tuple[str, pd.Timestamp], pd.Series] = {}
    prepared = {"K200_VETO": {}, "KOSDAQ_REV_FIRST": {}}
    for j, dt in enumerate(base_dates, 1):
        if dt not in panels:
            continue
        full = build_signal_panel(dt, panels[dt], cache, returns)
        for strategy in prepared:
            prepared[strategy][dt] = universe_panel(full, strategy)
        if j % 50 == 0:
            print(f"prepared {j}/{len(base_dates)} rebalance panels")

    configs = []
    for strategy in ("K200_VETO", "KOSDAQ_REV_FIRST"):
        for interval, n_target, method, buffer in itertools.product(INTERVALS, TARGET_NS, WEIGHT_METHODS, (False, True)):
            caps = (1.0,) if method == "equal" else CAP_MULTS
            for cap_mult in caps:
                configs.append({"strategy": strategy, "interval": interval, "n_target": n_target, "weighting": method, "buffer": buffer, "cap_mult": cap_mult})

    rows = []
    yearly = []
    for i, cfg in enumerate(configs, 1):
        daily, rebal = simulate_config(returns, prepared, cfg["strategy"], cfg["interval"], cfg["n_target"], cfg["weighting"], cfg["buffer"], cfg["cap_mult"])
        train_mask = daily.index < SPLIT_DATE
        test_mask = daily.index >= SPLIT_DATE
        for cost in COSTS_BPS:
            rows.append(summarize_run(daily, rebal, cfg, cost, "TRAIN", train_mask))
            rows.append(summarize_run(daily, rebal, cfg, cost, "TEST", test_mask))
        d = daily.loc[test_mask].copy()
        d["net"] = d["gross_ret"] - d["turnover_event"] * 30 / 10000.0
        d["excess"] = d["net"] - d["bench_ret"]
        for year, g in d.groupby(d.index.year):
            yearly.append({**cfg, "year": int(year), "net_return": float((1 + g["net"]).prod() - 1), "bench_return": float((1 + g["bench_ret"]).prod() - 1), "excess_return": float((1 + g["excess"]).prod() - 1), "turnover": float(g["turnover_event"].sum())})
        if i % 20 == 0:
            print(f"completed {i}/{len(configs)} configurations")

    results = pd.DataFrame(rows)
    results.to_csv(OUT / "methodology_results.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(yearly).to_csv(OUT / "methodology_yearly_results.csv", index=False, encoding="utf-8-sig")
    keys = ["strategy", "interval", "n_target", "weighting", "buffer", "cap_mult"]
    test30 = results[(results["period"] == "TEST") & (results["cost_bps"] == 30)].copy()
    train30 = results[(results["period"] == "TRAIN") & (results["cost_bps"] == 30)].copy()
    merged = test30.merge(train30[keys + ["excess_cagr", "excess_sharpe", "net_cagr", "net_sharpe"]], on=keys, suffixes=("_test", "_train"))
    robust = merged[(merged["excess_cagr_train"] > 0) & (merged["excess_cagr_test"] > 0)].copy()
    robust["robust_score"] = np.minimum(robust["excess_sharpe_train"], robust["excess_sharpe_test"])
    robust = robust.sort_values(["strategy", "robust_score", "excess_cagr_test"], ascending=[True, False, False])
    robust.groupby("strategy").head(20).to_csv(OUT / "robust_top_configs.csv", index=False, encoding="utf-8-sig")

    agg_rows = []
    for strategy in test30["strategy"].unique():
        s = test30[test30["strategy"] == strategy]
        for dim in ("interval", "n_target", "weighting", "buffer", "cap_mult"):
            a = s.groupby(dim).agg(median_excess_cagr=("excess_cagr", "median"), median_excess_sharpe=("excess_sharpe", "median"), median_net_cagr=("net_cagr", "median"), median_turnover=("annual_turnover", "median"), n_configs=("excess_cagr", "size")).reset_index().rename(columns={dim: "level"})
            a["strategy"] = strategy
            a["dimension"] = dim
            agg_rows.append(a)
    pd.concat(agg_rows, ignore_index=True).to_csv(OUT / "parameter_medians.csv", index=False, encoding="utf-8-sig")

    lines = ["# Methodology backtest", "", f"- Data: {returns.index.min().date()} to {returns.index.max().date()}", f"- Split: {SPLIT_DATE.date()}", f"- Configurations: {len(configs)}", "- Signal at t close; target applies t+1; daily weight drift and transaction costs included.", ""]
    for strategy in prepared:
        lines += [f"## {strategy}", "", robust[robust.strategy == strategy].head(10)[keys + ["excess_cagr_train", "excess_sharpe_train", "excess_cagr_test", "excess_sharpe_test", "net_cagr_test", "net_sharpe_test", "annual_turnover", "avg_names", "avg_max_weight"]].to_markdown(index=False), ""]
    (OUT / "methodology_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
