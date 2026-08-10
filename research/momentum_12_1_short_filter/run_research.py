from __future__ import annotations

import argparse
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "source" / "factor_all_values"
BASIC = DATA / "reference_snapshots" / "basic_info"
MOM12 = DATA / "모멘텀(12-1)"
MOM1 = DATA / "단기모멘텀"
OUT = Path(__file__).resolve().parent / "results"

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
DEFAULT_STEP = 10
DEFAULT_HORIZON = 10
TOP_NS = (5, 10, 20)
WEIGHTINGS = ("equal", "rank_linear")
COSTS_BPS = (0, 30, 60, 100)
SHORT_RANK_WEIGHTS = (0.10, 0.20, 0.30)


def read_csv(path: Path) -> pd.DataFrame:
    last = None
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Could not read {path}: {last}")


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out: dict[pd.Timestamp, Path] = {}
    for path in folder.glob("*.csv"):
        m = DATE_RE.match(path.name)
        if m:
            out[pd.Timestamp(m.group(1))] = path
    return dict(sorted(out.items()))


def normalize_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return x.where(x.str.startswith("A"), "A" + x.str.zfill(6))


def find_col(
    df: pd.DataFrame,
    exact: tuple[str, ...] = (),
    contains: tuple[str, ...] = (),
) -> str | None:
    for col in df.columns:
        label = str(col).strip()
        if label in exact:
            return col
    for col in df.columns:
        label = str(col).strip().lower()
        if any(token.lower() in label for token in contains):
            return col
    return None


def load_factor(path: Path) -> pd.Series:
    df = read_csv(path)
    code_col = find_col(df, exact=("StockCode", "Code", "종목코드"))
    value_col = find_col(df, exact=("FactorValue",), contains=("factorvalue",))
    if code_col is None or value_col is None:
        raise KeyError(f"Factor columns missing in {path}: {list(df.columns)}")
    code = normalize_code(df[code_col])
    value = pd.to_numeric(df[value_col], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return pd.Series(value.to_numpy(), index=code).groupby(level=0).last()


def load_basic_panels() -> tuple[pd.DataFrame, dict[pd.Timestamp, pd.DataFrame]]:
    rows: list[pd.DataFrame] = []
    panels: dict[pd.Timestamp, pd.DataFrame] = {}

    for dt, path in dated_files(BASIC).items():
        df = read_csv(path)
        code_col = find_col(df, exact=("Code", "StockCode", "종목코드"))
        ret_col = find_col(df, exact=("수정주가수익률",), contains=("수정주가수익률", "daily_return"))
        k200_col = find_col(df, contains=("코스피200", "k200"))
        if code_col is None or ret_col is None or k200_col is None:
            continue

        code = normalize_code(df[code_col])
        daily_ret = pd.to_numeric(df[ret_col], errors="coerce") / 100.0
        k200 = pd.to_numeric(df[k200_col], errors="coerce").fillna(0).astype(int)

        panel = pd.DataFrame(
            {"ret": daily_ret.to_numpy(), "k200": k200.to_numpy()},
            index=code,
        )
        panel = panel[~panel.index.duplicated(keep="last")]
        panels[dt] = panel

        rows.append(
            pd.DataFrame(
                {"date": dt, "code": panel.index, "ret": panel["ret"].to_numpy()}
            )
        )

    if not rows:
        raise RuntimeError(f"No usable basic-info files found under {BASIC}")

    returns = (
        pd.concat(rows, ignore_index=True)
        .pivot(index="date", columns="code", values="ret")
        .sort_index()
    )
    return returns, panels


def forward_return(returns: pd.DataFrame, dt: pd.Timestamp, horizon: int) -> pd.Series:
    loc = returns.index.get_indexer([dt])[0]
    if loc < 0 or loc + horizon >= len(returns.index):
        return pd.Series(dtype=float)
    block = returns.iloc[loc + 1 : loc + 1 + horizon]
    valid_count = block.notna().sum(axis=0)
    out = (1.0 + block.fillna(0.0)).prod(axis=0) - 1.0
    out[valid_count < horizon] = np.nan
    return out


def pct_rank(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").rank(pct=True, method="average")


def variant_scores(frame: pd.DataFrame) -> dict[str, pd.Series]:
    x = frame[["mom12", "mom1"]].replace([np.inf, -np.inf], np.nan)
    mom_rank = pct_rank(x["mom12"])
    short_rank = pct_rank(x["mom1"])

    variants: dict[str, pd.Series] = {
        "MOM12_1_BASE": x["mom12"],
        "MOM12_1_1M_POS": x["mom12"].where(x["mom1"] > 0),
        "MOM12_1_1M_ABOVE_MEDIAN": x["mom12"].where(
            x["mom1"] >= x["mom1"].median(skipna=True)
        ),
        # "Keep top 70%" means remove the bottom 30% of the cross-section.
        "MOM12_1_1M_KEEP_TOP70PCT": x["mom12"].where(short_rank >= 0.30),
    }
    for w in SHORT_RANK_WEIGHTS:
        key = f"MOM12_1_PLUS_1M_RANK_W{int(round(w * 100)):02d}"
        variants[key] = (1.0 - w) * mom_rank + w * short_rank
    return variants


def portfolio_weights(score: pd.Series, top_n: int, method: str) -> pd.Series:
    ranked = score.dropna().sort_values(ascending=False).head(top_n)
    if len(ranked) < top_n:
        return pd.Series(dtype=float)

    if method == "equal":
        raw = pd.Series(1.0, index=ranked.index)
    elif method == "rank_linear":
        raw = pd.Series(
            np.arange(len(ranked), 0, -1, dtype=float),
            index=ranked.index,
        )
    else:
        raise ValueError(method)
    return raw / raw.sum()


def turnover(old_w: pd.Series, new_w: pd.Series) -> float:
    union = old_w.index.union(new_w.index)
    old = old_w.reindex(union, fill_value=0.0)
    new = new_w.reindex(union, fill_value=0.0)
    return float(0.5 * (new - old).abs().sum())


def rank_ic(score: pd.Series, future: pd.Series) -> float:
    pair = pd.concat([score.rename("score"), future.rename("future")], axis=1).dropna()
    if len(pair) < 20:
        return np.nan
    return float(
        pair["score"].rank(method="average").corr(
            pair["future"].rank(method="average")
        )
    )


def max_drawdown(period_returns: pd.Series) -> float:
    if period_returns.empty:
        return np.nan
    nav = (1.0 + period_returns.fillna(0.0)).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def summarize(periods: pd.DataFrame, horizon: int) -> pd.DataFrame:
    rows: list[dict] = []
    periods_per_year = 252.0 / horizon

    group_cols = ["variant", "top_n", "weighting", "cost_bps"]
    for keys, g in periods.groupby(group_cols, dropna=False):
        g = g.sort_values("date").copy()
        if len(g) < 3:
            continue

        net = g["net"]
        excess = g["excess_net"]
        ann_return = float((1.0 + net).prod() ** (periods_per_year / len(net)) - 1.0)
        ann_excess = float(
            (1.0 + excess).prod() ** (periods_per_year / len(excess)) - 1.0
        )
        sharpe = (
            float(net.mean() / net.std(ddof=1) * math.sqrt(periods_per_year))
            if net.std(ddof=1) > 0
            else np.nan
        )
        excess_sharpe = (
            float(excess.mean() / excess.std(ddof=1) * math.sqrt(periods_per_year))
            if excess.std(ddof=1) > 0
            else np.nan
        )

        rows.append(
            {
                "variant": keys[0],
                "top_n": keys[1],
                "weighting": keys[2],
                "cost_bps": keys[3],
                "n_periods": len(g),
                "annualized_return": ann_return,
                "annualized_excess": ann_excess,
                "sharpe": sharpe,
                "excess_sharpe": excess_sharpe,
                "mdd": max_drawdown(net),
                "excess_mdd": max_drawdown(excess),
                "hit_rate": float((net > 0).mean()),
                "excess_hit_rate": float((excess > 0).mean()),
                "avg_turnover": float(g["turnover"].mean()),
                "annual_turnover": float(g["turnover"].mean() * periods_per_year),
                "avg_eligible": float(g["n_eligible"].mean()),
                "avg_rank_ic": float(g["rank_ic"].mean()),
                "rank_ic_hit_rate": float((g["rank_ic"] > 0).mean()),
            }
        )
    return pd.DataFrame(rows)


def yearly_summary(periods: pd.DataFrame, horizon: int) -> pd.DataFrame:
    rows: list[dict] = []
    periods_per_year = 252.0 / horizon
    x = periods.copy()
    x["year"] = pd.to_datetime(x["date"]).dt.year

    group_cols = ["variant", "top_n", "weighting", "cost_bps", "year"]
    for keys, g in x.groupby(group_cols, dropna=False):
        if len(g) < 2:
            continue
        net = g["net"]
        excess = g["excess_net"]
        rows.append(
            {
                "variant": keys[0],
                "top_n": keys[1],
                "weighting": keys[2],
                "cost_bps": keys[3],
                "year": keys[4],
                "n_periods": len(g),
                "return": float((1.0 + net).prod() - 1.0),
                "excess_return": float((1.0 + excess).prod() - 1.0),
                "sharpe": (
                    float(net.mean() / net.std(ddof=1) * math.sqrt(periods_per_year))
                    if net.std(ddof=1) > 0
                    else np.nan
                ),
                "mdd": max_drawdown(net),
                "avg_turnover": float(g["turnover"].mean()),
                "avg_rank_ic": float(g["rank_ic"].mean()),
            }
        )
    return pd.DataFrame(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="KOSPI200 MOM(12-1) with recent 1M return conditioning."
    )
    parser.add_argument("--start", default=None, help="YYYY-MM-DD")
    parser.add_argument("--end", default=None, help="YYYY-MM-DD")
    parser.add_argument("--step", type=int, default=DEFAULT_STEP)
    parser.add_argument("--horizon", type=int, default=DEFAULT_HORIZON)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    returns, basic_panels = load_basic_panels()
    mom12_files = dated_files(MOM12)
    mom1_files = dated_files(MOM1)

    dates = sorted(set(basic_panels) & set(mom12_files) & set(mom1_files))
    if args.start:
        dates = [d for d in dates if d >= pd.Timestamp(args.start)]
    if args.end:
        dates = [d for d in dates if d <= pd.Timestamp(args.end)]
    dates = dates[:: args.step]
    if not dates:
        raise RuntimeError("No common rebalance dates after filters.")

    current: dict[tuple[str, int, str, int], pd.Series] = {}
    period_rows: list[dict] = []
    diagnostic_rows: list[dict] = []

    for dt in dates:
        future = forward_return(returns, dt, args.horizon)
        if future.empty:
            continue

        basic = basic_panels[dt]
        k200_names = basic.index[basic["k200"] == 1]
        mom12 = load_factor(mom12_files[dt]).reindex(k200_names)
        mom1 = load_factor(mom1_files[dt]).reindex(k200_names)

        frame = pd.DataFrame({"mom12": mom12, "mom1": mom1})
        future_k200 = future.reindex(frame.index)
        benchmark = float(future_k200.dropna().mean()) if future_k200.notna().any() else np.nan

        variants = variant_scores(frame)
        base_score = variants["MOM12_1_BASE"].dropna()
        baseline_top20 = set(base_score.nlargest(min(20, len(base_score))).index)

        for variant, score in variants.items():
            eligible = score.dropna()
            ic = rank_ic(score, future_k200)
            top20 = set(eligible.nlargest(min(20, len(eligible))).index)
            diagnostic_rows.append(
                {
                    "date": dt,
                    "variant": variant,
                    "k200_count": len(k200_names),
                    "n_eligible": len(eligible),
                    "eligible_share": len(eligible) / len(k200_names) if len(k200_names) else np.nan,
                    "baseline_top20_overlap": (
                        len(top20 & baseline_top20) / len(baseline_top20)
                        if baseline_top20
                        else np.nan
                    ),
                    "rank_ic": ic,
                }
            )

            for top_n in TOP_NS:
                for weighting in WEIGHTINGS:
                    new_w = portfolio_weights(score, top_n, weighting)
                    if new_w.empty:
                        continue

                    gross = float(
                        (new_w * future_k200.reindex(new_w.index).fillna(0.0)).sum()
                    )
                    for cost_bps in COSTS_BPS:
                        key = (variant, top_n, weighting, cost_bps)
                        old_w = current.get(key, pd.Series(dtype=float))
                        turn = turnover(old_w, new_w)
                        cost = turn * cost_bps / 10000.0
                        net = gross - cost
                        excess_gross = gross - benchmark
                        excess_net = net - benchmark

                        period_rows.append(
                            {
                                "date": dt,
                                "variant": variant,
                                "top_n": top_n,
                                "weighting": weighting,
                                "cost_bps": cost_bps,
                                "gross": gross,
                                "net": net,
                                "benchmark": benchmark,
                                "excess_gross": excess_gross,
                                "excess_net": excess_net,
                                "turnover": turn,
                                "transaction_cost": cost,
                                "n_eligible": len(eligible),
                                "rank_ic": ic,
                            }
                        )
                        current[key] = new_w

    periods = pd.DataFrame(period_rows)
    diagnostics = pd.DataFrame(diagnostic_rows)
    if periods.empty:
        raise RuntimeError("Backtest produced no periods.")

    summary = summarize(periods, args.horizon)
    yearly = yearly_summary(periods, args.horizon)

    periods.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "summary.csv", index=False, encoding="utf-8-sig")
    yearly.to_csv(OUT / "yearly_summary.csv", index=False, encoding="utf-8-sig")
    diagnostics.to_csv(OUT / "filter_diagnostics.csv", index=False, encoding="utf-8-sig")

    key = summary[
        (summary["top_n"] == 10)
        & (summary["weighting"] == "equal")
        & (summary["cost_bps"] == 30)
    ].sort_values(["excess_sharpe", "annualized_excess"], ascending=False)

    print("\nKey comparison: Top10 equal-weight, 30 bps\n")
    print(key.to_string(index=False))


if __name__ == "__main__":
    main()
