from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor, export_text

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "source" / "factor_all_values"
BASIC = DATA / "reference_snapshots" / "basic_info"
OUT = ROOT / "analysis" / "results_nonlinear"
OUT.mkdir(parents=True, exist_ok=True)

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
FACTOR_DIRS = {
    "per": DATA / "PER(12MF)",
    "pbr": DATA / "PBR(12MF)",
    "rev_fy1": DATA / "OP(FY1_1M_CHG)",
    "rev_12mf": DATA / "OP(12MF_1M_CHG)",
}
FEATURES = ["cheap_per", "cheap_pbr", "rev_fy1", "rev_12mf", "log_mcap_rank"]
HORIZON = 20
REB_FREQ = 20
ONE_WAY_COST = 0.003
MIN_NAMES = 15


def read_csv(path: Path) -> pd.DataFrame:
    errors = []
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as exc:
            errors.append(f"{enc}: {exc}")
    raise RuntimeError(f"Could not read {path}: {' | '.join(errors)}")


def normalize_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    x = x.where(x.str.startswith("A"), "A" + x.str.zfill(6))
    return x


def find_col(df: pd.DataFrame, predicates) -> str | None:
    for c in df.columns:
        cs = str(c).strip()
        if any(p(cs) for p in predicates):
            return c
    return None


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out = {}
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def parse_basic(path: Path, dt: pd.Timestamp) -> pd.DataFrame:
    df = read_csv(path)
    code_col = find_col(df, [lambda x: x.lower() == "code", lambda x: "종목코드" in x])
    ret_col = find_col(df, [lambda x: "수정주가수익률" in x, lambda x: x.lower() in {"ret", "return"}])
    cap_col = find_col(df, [lambda x: x == "시가총액"])
    market_col = find_col(df, [lambda x: "상장된 시장" in x, lambda x: x.lower() == "market"])
    k200_col = find_col(df, [lambda x: "코스피200" in x])
    name_col = find_col(df, [lambda x: x.lower() == "name", lambda x: x == "종목명"])
    if code_col is None or ret_col is None:
        raise KeyError(f"basic columns missing: {list(df.columns)}")
    out = pd.DataFrame({
        "date": dt,
        "code": normalize_code(df[code_col]),
        "name": df[name_col].astype(str) if name_col is not None else "",
        "ret": pd.to_numeric(df[ret_col], errors="coerce") / 100.0,
        "mcap": pd.to_numeric(df[cap_col], errors="coerce") if cap_col is not None else np.nan,
        "market": df[market_col].astype(str).str.upper().str.strip() if market_col is not None else "",
        "k200": pd.to_numeric(df[k200_col], errors="coerce").fillna(0).astype(int) if k200_col is not None else 0,
    })
    return out.drop_duplicates("code", keep="last")


def parse_factor(path: Path, key: str) -> pd.DataFrame:
    df = read_csv(path)
    code_col = find_col(df, [lambda x: x.lower() in {"code", "stockcode", "ticker"}, lambda x: "종목코드" in x])
    value_col = find_col(df, [lambda x: x.lower() == "factorvalue"])
    if value_col is None:
        candidates = []
        for c in df.columns:
            if c == code_col:
                continue
            vals = pd.to_numeric(df[c], errors="coerce")
            if vals.notna().sum() >= 20 and "sourcerow" not in str(c).lower():
                candidates.append((vals.notna().sum(), c))
        value_col = max(candidates)[1] if candidates else None
    if code_col is None or value_col is None:
        return pd.DataFrame(columns=["code", key])
    if "Universe" in df.columns and (df["Universe"].astype(str) == "ALL").any():
        df = df[df["Universe"].astype(str) == "ALL"].copy()
    status_col = find_col(df, [lambda x: x.lower() == "valuestatus"])
    vals = pd.to_numeric(df[value_col], errors="coerce")
    if status_col is not None:
        vals = vals.where(df[status_col].astype(str).str.upper().eq("OK"))
    out = pd.DataFrame({"code": normalize_code(df[code_col]), key: vals})
    return out.groupby("code", as_index=False).last()


def load_daily_panel() -> tuple[pd.DataFrame, dict[pd.Timestamp, pd.DataFrame]]:
    basic_files = dated_files(BASIC)
    rows = []
    meta = {}
    for i, (dt, p) in enumerate(basic_files.items(), 1):
        b = parse_basic(p, dt)
        rows.append(b[["date", "code", "ret"]])
        meta[dt] = b.drop(columns=["ret"])
        if i % 500 == 0:
            print(f"loaded basic {i}/{len(basic_files)}")
    long = pd.concat(rows, ignore_index=True)
    ret = long.pivot(index="date", columns="code", values="ret").sort_index()
    return ret, meta


def forward_returns(daily: pd.DataFrame, h: int) -> pd.DataFrame:
    logret = np.log1p(daily.clip(lower=-0.999999))
    target = sum(logret.shift(-i) for i in range(1, h + 1))
    return np.expm1(target)


def common_dates() -> list[pd.Timestamp]:
    sets = [set(dated_files(BASIC))]
    sets.extend(set(dated_files(p)) for p in FACTOR_DIRS.values())
    return sorted(set.intersection(*sets))


def make_snapshot(dt: pd.Timestamp, meta: dict[pd.Timestamp, pd.DataFrame], target: pd.DataFrame) -> pd.DataFrame:
    if dt not in meta or dt not in target.index:
        return pd.DataFrame()
    df = meta[dt].copy()
    df["y"] = target.loc[dt].reindex(df["code"]).to_numpy()
    for key, folder in FACTOR_DIRS.items():
        p = folder / f"{dt.date().isoformat()}.csv"
        if not p.exists():
            df[key] = np.nan
        else:
            df = df.merge(parse_factor(p, key), on="code", how="left")
    df["market"] = df["market"].replace({"KOSPI ": "KOSPI", "KOSDAQ ": "KOSDAQ"})
    df["log_mcap"] = np.log(df["mcap"].where(df["mcap"] > 0))
    return df


def percentile(s: pd.Series, ascending: bool = True) -> pd.Series:
    return s.rank(pct=True, ascending=ascending, method="average")


def add_local_features(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["cheap_per"] = percentile(x["per"], ascending=False)
    x["cheap_pbr"] = percentile(x["pbr"], ascending=False)
    x["rev_fy1"] = percentile(x["rev_fy1"], ascending=True)
    x["rev_12mf"] = percentile(x["rev_12mf"], ascending=True)
    x["log_mcap_rank"] = percentile(x["log_mcap"], ascending=True)
    x["value"] = x[["cheap_per", "cheap_pbr"]].mean(axis=1)
    return x


def universe_masks(df: pd.DataFrame) -> dict[str, pd.Series]:
    cap_rank = percentile(df["log_mcap"], ascending=True)
    return {
        "ALL": pd.Series(True, index=df.index),
        "KOSPI": df["market"].eq("KOSPI"),
        "KOSDAQ": df["market"].eq("KOSDAQ"),
        "K200": df["k200"].eq(1),
        "KOSPI_EX_K200": df["market"].eq("KOSPI") & df["k200"].ne(1),
        "LARGE_TOP30": cap_rank.ge(0.70),
        "MID_30_70": cap_rank.ge(0.30) & cap_rank.lt(0.70),
        "SMALL_BOTTOM30": cap_rank.lt(0.30),
    }


def build_dataset(ret: pd.DataFrame, meta: dict[pd.Timestamp, pd.DataFrame]) -> tuple[dict[pd.Timestamp, pd.DataFrame], pd.Timestamp]:
    target = forward_returns(ret, HORIZON)
    dates = [d for d in common_dates() if d in target.index][::REB_FREQ]
    panels = {}
    for i, dt in enumerate(dates, 1):
        p = make_snapshot(dt, meta, target)
        if not p.empty:
            p = p[p["y"].notna() & p["mcap"].notna()].copy()
            p["target_rank"] = p["y"].rank(pct=True)
            panels[dt] = p
        if i % 25 == 0:
            print(f"built panels {i}/{len(dates)}")
    valid_dates = sorted(panels)
    split_idx = max(10, int(len(valid_dates) * 0.70))
    return panels, valid_dates[split_idx]


def training_frame(panels: dict[pd.Timestamp, pd.DataFrame], split_date: pd.Timestamp) -> pd.DataFrame:
    rows = []
    for dt, p in panels.items():
        if dt >= split_date:
            continue
        q = add_local_features(p)
        q["date"] = dt
        rows.append(q)
    train = pd.concat(rows, ignore_index=True).dropna(subset=["target_rank"])
    for f in FEATURES:
        train[f + "_missing"] = train[f].isna().astype(int)
        train[f] = train[f].fillna(0.5)
    return train


def fit_models(train: pd.DataFrame):
    feature_cols = FEATURES + [f + "_missing" for f in FEATURES[:4]]
    sample = train.sample(min(len(train), 350_000), random_state=42)
    X, y = sample[feature_cols], sample["target_rank"]
    tree = DecisionTreeRegressor(max_depth=4, min_samples_leaf=2500, random_state=42)
    tree.fit(X, y)
    hgb = HistGradientBoostingRegressor(
        max_depth=3, max_iter=160, learning_rate=0.05,
        min_samples_leaf=300, l2_regularization=1.0, random_state=42,
    )
    hgb.fit(X, y)
    return feature_cols, tree, hgb


def apply_scores(df: pd.DataFrame, feature_cols, tree, hgb) -> pd.DataFrame:
    x = add_local_features(df)
    model_x = x.copy()
    for f in FEATURES:
        model_x[f + "_missing"] = model_x[f].isna().astype(int)
        model_x[f] = model_x[f].fillna(0.5)
    x["score_linear_value"] = x["value"]
    x["score_double_cheap"] = x["value"].where((x["cheap_per"] >= 0.70) & (x["cheap_pbr"] >= 0.70))
    x["score_value_revision_gate"] = (0.7*x["value"] + 0.3*x["rev_fy1"]).where(
        (x["value"] >= 0.70) & (x["rev_fy1"] >= 0.50)
    )
    x["score_revision_veto"] = x["value"].where(
        (x["value"] >= 0.80) & (x["rev_fy1"] >= 0.20) & (x["rev_12mf"] >= 0.20)
    )
    x["score_deep_value_turnaround"] = (0.5*x["value"] + 0.5*x["rev_fy1"]).where(
        (x["value"] >= 0.75) & (x["rev_fy1"] >= 0.70)
    )
    x["score_revision_first_floor"] = x["rev_fy1"].where(
        (x["rev_fy1"] >= 0.80) & (x["value"] >= 0.40)
    )
    x["score_tree"] = tree.predict(model_x[feature_cols])
    x["score_hgb"] = hgb.predict(model_x[feature_cols])
    return x


STRATEGIES = {
    "LINEAR_VALUE": "score_linear_value",
    "DOUBLE_CHEAP_AND": "score_double_cheap",
    "VALUE_REVISION_GATE": "score_value_revision_gate",
    "VALUE_REVISION_VETO": "score_revision_veto",
    "DEEP_VALUE_TURNAROUND": "score_deep_value_turnaround",
    "REVISION_FIRST_FLOOR": "score_revision_first_floor",
    "SHALLOW_TREE": "score_tree",
    "GRADIENT_BOOSTING": "score_hgb",
}


def choose_holdings(df: pd.DataFrame, score_col: str) -> pd.DataFrame:
    eligible = df.dropna(subset=[score_col, "y"]).copy()
    if len(eligible) < MIN_NAMES:
        return eligible.iloc[0:0]
    n = max(MIN_NAMES, int(math.ceil(len(df) * 0.20)))
    return eligible.nlargest(min(n, len(eligible)), score_col)


def equal_weight_turnover(prev: set[str], cur: set[str]) -> float:
    if not prev:
        return 1.0
    union = prev | cur
    wp, wc = 1.0 / len(prev), 1.0 / len(cur)
    return 0.5 * sum(abs((wc if c in cur else 0.0) - (wp if c in prev else 0.0)) for c in union)


def max_drawdown(returns: pd.Series) -> float:
    wealth = (1.0 + returns.fillna(0)).cumprod()
    return float((wealth / wealth.cummax() - 1.0).min())


def summarize_periods(periods: pd.DataFrame) -> pd.DataFrame:
    rows = []
    scale = 252 / HORIZON
    for (univ, strat), g in periods.groupby(["universe", "strategy"]):
        g = g.sort_values("date")
        ex, gross = g["excess_net"], g["excess_gross"]
        sd = ex.std(ddof=1)
        rows.append({
            "universe": univ, "strategy": strat, "n_periods": len(g),
            "first_test_date": g["date"].min().date().isoformat(),
            "last_test_date": g["date"].max().date().isoformat(),
            "avg_universe_names": g["universe_n"].mean(),
            "avg_selected_names": g["selected_n"].mean(),
            "avg_turnover": g["turnover"].mean(),
            "avg_20d_port_return": g["portfolio_return"].mean(),
            "avg_20d_benchmark_return": g["benchmark_return"].mean(),
            "avg_20d_excess_gross": gross.mean(),
            "avg_20d_excess_net30bp": ex.mean(),
            "annualized_excess_net30bp": ex.mean() * scale,
            "sharpe_excess_net30bp": ex.mean() / sd * math.sqrt(scale) if sd > 0 else np.nan,
            "tstat_excess_net30bp": ex.mean() / (sd / math.sqrt(len(ex))) if sd > 0 else np.nan,
            "win_rate_excess_net30bp": (ex > 0).mean(),
            "max_drawdown_excess_net30bp": max_drawdown(ex),
        })
    return pd.DataFrame(rows)


def bucket_surface(test_panels: dict[pd.Timestamp, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for dt, raw in test_panels.items():
        for univ, mask in universe_masks(raw).items():
            d = add_local_features(raw[mask].copy()).dropna(subset=["value", "rev_fy1", "y"])
            if len(d) < 50:
                continue
            d["value_bin"] = pd.qcut(d["value"].rank(method="first"), 5, labels=False) + 1
            d["revision_bin"] = pd.qcut(d["rev_fy1"].rank(method="first"), 5, labels=False) + 1
            benchmark = d["y"].mean()
            for (vb, rb), g in d.groupby(["value_bin", "revision_bin"]):
                rows.append({"date": dt, "universe": univ, "value_bin": int(vb),
                    "revision_bin": int(rb), "n": len(g), "return": g["y"].mean(),
                    "excess": g["y"].mean() - benchmark})
    raw = pd.DataFrame(rows)
    raw.to_csv(OUT / "bucket_surface_timeseries.csv", index=False, encoding="utf-8-sig")
    return raw.groupby(["universe", "value_bin", "revision_bin"]).agg(
        n_dates=("date", "nunique"), avg_names=("n", "mean"),
        avg_20d_return=("return", "mean"), avg_20d_excess=("excess", "mean"),
    ).reset_index()


def main():
    ret, meta = load_daily_panel()
    panels, split_date = build_dataset(ret, meta)
    train = training_frame(panels, split_date)
    feature_cols, tree, hgb = fit_models(train)
    (OUT / "tree_rules.txt").write_text(export_text(tree, feature_names=feature_cols, decimals=3), encoding="utf-8")
    pd.DataFrame({"feature": feature_cols, "tree_importance": tree.feature_importances_}).sort_values(
        "tree_importance", ascending=False).to_csv(OUT / "tree_feature_importance.csv", index=False, encoding="utf-8-sig")

    periods, prev_holdings = [], {}
    test_panels = {dt: p for dt, p in panels.items() if dt >= split_date}
    for dt, raw in test_panels.items():
        for univ, mask in universe_masks(raw).items():
            base = raw[mask].copy()
            if len(base) < 30:
                continue
            scored = apply_scores(base, feature_cols, tree, hgb)
            benchmark = scored["y"].dropna().mean()
            for strat, score_col in STRATEGIES.items():
                held = choose_holdings(scored, score_col)
                if len(held) < MIN_NAMES:
                    continue
                key, cur = (univ, strat), set(held["code"])
                turnover = equal_weight_turnover(prev_holdings.get(key, set()), cur)
                prev_holdings[key] = cur
                port_ret = held["y"].mean()
                excess = port_ret - benchmark
                periods.append({"date": dt, "universe": univ, "strategy": strat,
                    "universe_n": len(scored), "selected_n": len(held), "turnover": turnover,
                    "portfolio_return": port_ret, "benchmark_return": benchmark,
                    "excess_gross": excess, "cost": turnover * ONE_WAY_COST,
                    "excess_net": excess - turnover * ONE_WAY_COST})
    periods = pd.DataFrame(periods).sort_values(["universe", "strategy", "date"])
    periods.to_csv(OUT / "strategy_period_returns.csv", index=False, encoding="utf-8-sig")
    summary = summarize_periods(periods)
    summary.to_csv(OUT / "strategy_universe_results.csv", index=False, encoding="utf-8-sig")
    surface = bucket_surface(test_panels)
    surface.to_csv(OUT / "value_revision_bucket_surface.csv", index=False, encoding="utf-8-sig")

    top = summary.sort_values(["universe", "sharpe_excess_net30bp"], ascending=[True, False])
    lines = ["# Nonlinear and conditional factor strategy backtest", "",
        f"- Data dates: {ret.index.min().date()} to {ret.index.max().date()}",
        f"- Rebalance/holding interval: every {REB_FREQ} trading days / {HORIZON}-day forward return",
        f"- Chronological OOS split date: {split_date.date()}", f"- Train rows: {len(train):,}",
        f"- Test rebalance periods: {len(test_panels)}", "- Factor timing: t-close signal, return begins t+1",
        "- Local percentile ranks recalculated inside each tested universe",
        "- Cost assumption: 30 bp per one-way turnover, deducted from strategy excess",
        "- Rules/thresholds specified before this run's test results; tree/HGB fit on train only", "",
        "## Best strategies by universe", ""]
    for univ in sorted(top["universe"].unique()):
        lines += [f"### {univ}", "", top[top["universe"] == univ].head(8).to_markdown(index=False), ""]
    lines += ["## Learned shallow tree", "", "```", (OUT / "tree_rules.txt").read_text(encoding="utf-8"), "```", ""]
    (OUT / "summary_nonlinear.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
