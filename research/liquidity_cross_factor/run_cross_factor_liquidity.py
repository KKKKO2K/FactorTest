from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "source" / "factor_all_values"
BASIC = DATA / "reference_snapshots" / "basic_info"
TRADING = DATA / "reference_snapshots" / "trading_amount"
OUT = Path(__file__).resolve().parent / "results"

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
START = pd.Timestamp("2016-01-04")
OOS_START = pd.Timestamp("2023-01-01")
HORIZON = 10
STEP = 10
TOP_NS = (10, 20)
COSTS_BPS = (0, 30, 60)

FACTORS = {
    "OP12_REV": DATA / "OP(12MF_1M_CHG)",
    "OPFY1_REV": DATA / "OP(FY1_1M_CHG)",
    "PBR12MF": DATA / "PBR(12MF)",
    "PER12MF": DATA / "PER(12MF)",
    "MOM1M": DATA / "단기모멘텀",
    "MOM12_1": DATA / "모멘텀(12-1)",
    "PRIVATE_FLOW": DATA / "사모수급",
    "FOREIGN_FLOW": DATA / "외국인수급",
}

OVERLAYS = (
    "BASE",
    "RAW_TA_W10",
    "TURNOVER_W10",
    "TURNOVER_W20",
    "ACT1_W10",
    "ACT1_W20",
    "ACT5_W10",
    "ACT5_W20",
    "ACT5_KEEP_TOP70",
    "ACT5_KEEP_TOP50",
    "ACT5_GT1",
    "ACT5_MULTIPLY",
)


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
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def norm_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return x.where(x.str.startswith("A"), "A" + x.str.zfill(6))


def find_col(df: pd.DataFrame, exact=(), contains=()) -> str | None:
    for c in df.columns:
        if str(c).strip() in exact:
            return c
    for c in df.columns:
        label = str(c).strip().lower()
        if any(token.lower() in label for token in contains):
            return c
    return None


def code_col(df: pd.DataFrame) -> str:
    c = find_col(df, exact=("Code", "StockCode", "종목코드", "Ticker"))
    if c is None:
        raise KeyError(f"Code column missing: {list(df.columns)}")
    return c


def load_basic() -> tuple[pd.DataFrame, pd.DataFrame, dict[pd.Timestamp, pd.Series]]:
    ret_rows: list[pd.DataFrame] = []
    mcap_rows: list[pd.DataFrame] = []
    k200_by_date: dict[pd.Timestamp, pd.Series] = {}

    for dt, p in dated_files(BASIC).items():
        if dt < START:
            continue
        df = read_csv(p)
        cc = code_col(df)
        rc = find_col(df, exact=("수정주가수익률",), contains=("수정주가수익률", "daily_return"))
        mc = find_col(df, exact=("시가총액",), contains=("시가총액", "marketcap"))
        kc = find_col(df, contains=("코스피200", "k200"))
        if rc is None or mc is None or kc is None:
            continue
        codes = norm_code(df[cc])
        ret = pd.to_numeric(df[rc], errors="coerce") / 100.0
        mcap = pd.to_numeric(df[mc], errors="coerce")
        k200 = pd.to_numeric(df[kc], errors="coerce").fillna(0).astype(int)

        ret_rows.append(pd.DataFrame({"date": dt, "code": codes, "value": ret}))
        mcap_rows.append(pd.DataFrame({"date": dt, "code": codes, "value": mcap}))
        k = pd.Series(k200.to_numpy(), index=codes).groupby(level=0).last()
        k200_by_date[dt] = k

    returns = pd.concat(ret_rows, ignore_index=True).pivot(index="date", columns="code", values="value").sort_index()
    mcap = pd.concat(mcap_rows, ignore_index=True).pivot(index="date", columns="code", values="value").sort_index()
    return returns, mcap, k200_by_date


def load_trading_amount() -> pd.DataFrame:
    rows: list[pd.DataFrame] = []
    for dt, p in dated_files(TRADING).items():
        if dt < START:
            continue
        df = read_csv(p)
        cc = code_col(df)
        vc = find_col(df, exact=("거래대금(십억원)",), contains=("거래대금", "trading"))
        if vc is None:
            continue
        codes = norm_code(df[cc])
        vals = pd.to_numeric(df[vc], errors="coerce")
        rows.append(pd.DataFrame({"date": dt, "code": codes, "value": vals}))
    if not rows:
        raise RuntimeError(f"No trading amount data under {TRADING}")
    return pd.concat(rows, ignore_index=True).pivot(index="date", columns="code", values="value").sort_index()


def load_factor(path: Path) -> pd.Series:
    df = read_csv(path)
    cc = code_col(df)
    vc = find_col(df, exact=("FactorValue",), contains=("factorvalue",))
    if vc is None:
        raise KeyError(f"FactorValue missing in {path}")
    codes = norm_code(df[cc])
    vals = pd.to_numeric(df[vc], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return pd.Series(vals.to_numpy(), index=codes).groupby(level=0).last()


def forward_returns(daily: pd.DataFrame, horizon: int) -> pd.DataFrame:
    logs = np.log1p(daily.clip(lower=-0.999999))
    acc = sum(logs.shift(-i) for i in range(1, horizon + 1))
    return np.expm1(acc)


def pct_rank(s: pd.Series, high_good: bool = True) -> pd.Series:
    # Score 1 = best.
    return pd.to_numeric(s, errors="coerce").rank(pct=True, method="average", ascending=high_good)


def build_liquidity_features(ta: pd.DataFrame, mcap: pd.DataFrame) -> dict[str, pd.DataFrame]:
    ta = ta.reindex(index=mcap.index, columns=mcap.columns)
    raw = ta.where(ta > 0)
    turnover = raw / mcap.where(mcap > 0)

    # One-day shock vs strictly prior 20 trading days.
    hist20 = raw.shift(1).rolling(20, min_periods=15).mean()
    act1 = raw / hist20

    # Recent 5D average vs preceding 20D average (non-overlapping windows).
    recent5 = raw.rolling(5, min_periods=4).mean()
    prior20 = raw.shift(5).rolling(20, min_periods=15).mean()
    act5 = recent5 / prior20
    return {"raw": raw, "turnover": turnover, "act1": act1, "act5": act5}


def factor_direction(
    files: dict[pd.Timestamp, Path],
    fwd: pd.DataFrame,
    k200_by_date: dict[pd.Timestamp, pd.Series],
    rebalance_dates: list[pd.Timestamp],
) -> tuple[int, float, int]:
    ics: list[float] = []
    for dt in rebalance_dates:
        if dt >= OOS_START or dt not in files or dt not in fwd.index or dt not in k200_by_date:
            continue
        universe = k200_by_date[dt]
        codes = universe.index[universe == 1]
        x = load_factor(files[dt]).reindex(codes)
        y = fwd.loc[dt].reindex(codes)
        pair = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
        if len(pair) < 50:
            continue
        ic = pair.x.rank().corr(pair.y.rank())
        if pd.notna(ic):
            ics.append(float(ic))
    avg = float(np.mean(ics)) if ics else np.nan
    direction = 1 if (pd.notna(avg) and avg >= 0) else -1
    return direction, avg, len(ics)


def overlay_scores(base: pd.Series, liq: dict[str, pd.Series]) -> dict[str, pd.Series]:
    raw_r = pct_rank(liq["raw"], True)
    turn_r = pct_rank(liq["turnover"], True)
    act1_r = pct_rank(liq["act1"], True)
    act5_r = pct_rank(liq["act5"], True)

    out = {
        "BASE": base,
        "RAW_TA_W10": 0.90 * base + 0.10 * raw_r,
        "TURNOVER_W10": 0.90 * base + 0.10 * turn_r,
        "TURNOVER_W20": 0.80 * base + 0.20 * turn_r,
        "ACT1_W10": 0.90 * base + 0.10 * act1_r,
        "ACT1_W20": 0.80 * base + 0.20 * act1_r,
        "ACT5_W10": 0.90 * base + 0.10 * act5_r,
        "ACT5_W20": 0.80 * base + 0.20 * act5_r,
        "ACT5_KEEP_TOP70": base.where(act5_r >= 0.30),
        "ACT5_KEEP_TOP50": base.where(act5_r >= 0.50),
        "ACT5_GT1": base.where(liq["act5"] > 1.0),
        "ACT5_MULTIPLY": base * (0.50 + 0.50 * act5_r),
    }
    return out


def select_top(score: pd.Series, n: int) -> list[str]:
    s = score.replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)
    return s.head(n).index.tolist() if len(s) >= n else []


def overlap_turnover(old: list[str], new: list[str], n: int) -> float:
    if not old:
        return 1.0
    return float(1.0 - len(set(old) & set(new)) / n)


def max_drawdown(r: pd.Series) -> float:
    nav = (1.0 + r.fillna(0.0)).cumprod()
    return float((nav / nav.cummax() - 1.0).min()) if len(nav) else np.nan


def ann_return(r: pd.Series) -> float:
    if len(r) == 0:
        return np.nan
    ppy = 252.0 / HORIZON
    return float((1.0 + r).prod() ** (ppy / len(r)) - 1.0)


def sharpe(r: pd.Series) -> float:
    if len(r) < 3 or r.std(ddof=1) <= 0:
        return np.nan
    return float(r.mean() / r.std(ddof=1) * math.sqrt(252.0 / HORIZON))


def summarize(periods: pd.DataFrame) -> pd.DataFrame:
    x = periods.copy()
    x["date"] = pd.to_datetime(x["date"])
    x["sample"] = np.where(x.date < OOS_START, "IS_PRE_2023", "OOS_2023_PLUS")
    x = pd.concat([x, x.assign(sample="FULL")], ignore_index=True)
    rows: list[dict] = []
    keys = ["sample", "factor", "overlay", "top_n", "cost_bps"]
    for k, g in x.groupby(keys, dropna=False):
        g = g.sort_values("date")
        rows.append({
            "sample": k[0], "factor": k[1], "overlay": k[2], "top_n": k[3], "cost_bps": k[4],
            "n_periods": len(g),
            "annualized_return": ann_return(g.net),
            "annualized_excess": ann_return(g.excess),
            "sharpe": sharpe(g.net),
            "excess_sharpe": sharpe(g.excess),
            "mdd": max_drawdown(g.net),
            "avg_turnover": float(g.turnover.mean()),
            "hit_rate": float((g.net > 0).mean()),
            "avg_eligible": float(g.eligible.mean()),
        })
    return pd.DataFrame(rows)


def compare_to_base(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for sample in ("FULL", "OOS_2023_PLUS"):
        ss = summary[summary.sample == sample]
        for factor, fg in ss.groupby("factor"):
            base = fg[fg.overlay == "BASE"][["top_n", "cost_bps", "annualized_return", "sharpe", "mdd", "avg_turnover"]].rename(columns={
                "annualized_return": "base_return", "sharpe": "base_sharpe", "mdd": "base_mdd", "avg_turnover": "base_turnover"
            })
            for overlay, og in fg[fg.overlay != "BASE"].groupby("overlay"):
                z = og.merge(base, on=["top_n", "cost_bps"], how="inner")
                for _, r in z.iterrows():
                    rows.append({
                        "sample": sample, "factor": factor, "overlay": overlay,
                        "top_n": r.top_n, "cost_bps": r.cost_bps,
                        "return_delta": r.annualized_return - r.base_return,
                        "sharpe_delta": r.sharpe - r.base_sharpe,
                        "mdd_delta": r.mdd - r.base_mdd,
                        "turnover_delta": r.avg_turnover - r.base_turnover,
                    })
    return pd.DataFrame(rows)


def overlay_robustness(comp: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for (sample, overlay), g in comp.groupby(["sample", "overlay"]):
        rows.append({
            "sample": sample,
            "overlay": overlay,
            "n_factor_configs": len(g),
            "return_improve_share": float((g.return_delta > 0).mean()),
            "sharpe_improve_share": float((g.sharpe_delta > 0).mean()),
            "mdd_improve_share": float((g.mdd_delta > 0).mean()),
            "median_return_delta": float(g.return_delta.median()),
            "median_sharpe_delta": float(g.sharpe_delta.median()),
            "median_turnover_delta": float(g.turnover_delta.median()),
        })
    return pd.DataFrame(rows)


def standalone_liquidity(
    fwd: pd.DataFrame,
    k200_by_date: dict[pd.Timestamp, pd.Series],
    liq_frames: dict[str, pd.DataFrame],
    rebalance_dates: list[pd.Timestamp],
) -> pd.DataFrame:
    rows: list[dict] = []
    current: dict[tuple[str, int, int], list[str]] = {}
    signals = {
        "RAW_HIGH": ("raw", True), "RAW_LOW": ("raw", False),
        "TURNOVER_HIGH": ("turnover", True), "TURNOVER_LOW": ("turnover", False),
        "ACT1_HIGH": ("act1", True), "ACT1_LOW": ("act1", False),
        "ACT5_HIGH": ("act5", True), "ACT5_LOW": ("act5", False),
    }
    for dt in rebalance_dates:
        if dt not in fwd.index or dt not in k200_by_date:
            continue
        k = k200_by_date[dt]
        codes = k.index[k == 1]
        y = fwd.loc[dt].reindex(codes)
        if y.notna().sum() < 50:
            continue
        bench = float(y.dropna().mean())
        for name, (feat, high) in signals.items():
            raw = liq_frames[feat].loc[dt].reindex(codes) if dt in liq_frames[feat].index else pd.Series(index=codes, dtype=float)
            score = pct_rank(raw, high_good=high)
            for n in TOP_NS:
                names = select_top(score, n)
                if len(names) < n:
                    continue
                gross = float(y.reindex(names).mean())
                for cost in COSTS_BPS:
                    key = (name, n, cost)
                    turn = overlap_turnover(current.get(key, []), names, n)
                    net = gross - turn * cost / 10000.0
                    rows.append({"date": dt, "signal": name, "top_n": n, "cost_bps": cost,
                                 "gross": gross, "net": net, "benchmark": bench, "excess": net-bench,
                                 "turnover": turn})
                    current[key] = names
    return pd.DataFrame(rows)


def summarize_standalone(periods: pd.DataFrame) -> pd.DataFrame:
    x = periods.copy()
    x["date"] = pd.to_datetime(x.date)
    x["sample"] = np.where(x.date < OOS_START, "IS_PRE_2023", "OOS_2023_PLUS")
    x = pd.concat([x, x.assign(sample="FULL")], ignore_index=True)
    rows=[]
    for k,g in x.groupby(["sample","signal","top_n","cost_bps"]):
        rows.append({"sample":k[0],"signal":k[1],"top_n":k[2],"cost_bps":k[3],"n_periods":len(g),
                     "annualized_return":ann_return(g.net),"annualized_excess":ann_return(g.excess),
                     "sharpe":sharpe(g.net),"excess_sharpe":sharpe(g.excess),"mdd":max_drawdown(g.net),
                     "avg_turnover":float(g.turnover.mean())})
    return pd.DataFrame(rows)


def write_summary(direction_df: pd.DataFrame, robust: pd.DataFrame, summary: pd.DataFrame, standalone: pd.DataFrame) -> None:
    lines = [
        "# Trading Value × Cross-Factor Research",
        "",
        "Universe: point-in-time KOSPI200. Rebalance/holding: 10 trading days. OOS starts 2023-01-01.",
        "Factor direction is chosen using only pre-2023 mean 10D rank IC and then frozen.",
        "Trading activity features use only information available by rebalance-date close.",
        "",
        "## Frozen factor directions",
        "",
    ]
    for _, r in direction_df.iterrows():
        lines.append(f"- {r.factor}: {'HIGH' if r.direction > 0 else 'LOW'} raw value is good; train IC {r.train_ic:.4f} ({int(r.n_train_dates)} dates)")

    lines += ["", "## Overlay robustness — OOS 2023+", ""]
    r = robust[robust.sample == "OOS_2023_PLUS"].sort_values(["return_improve_share", "median_return_delta"], ascending=False)
    for _, x in r.iterrows():
        lines.append(
            f"- {x.overlay}: return improve {x.return_improve_share:.0%}, Sharpe improve {x.sharpe_improve_share:.0%}, "
            f"MDD improve {x.mdd_improve_share:.0%}, median return delta {x.median_return_delta:.2%}, "
            f"median turnover delta {x.median_turnover_delta:.2f}"
        )

    lines += ["", "## Per-factor key view — Top10 / 30 bps / OOS", ""]
    key = summary[(summary.sample == "OOS_2023_PLUS") & (summary.top_n == 10) & (summary.cost_bps == 30)].copy()
    for factor, g in key.groupby("factor"):
        base = g[g.overlay == "BASE"].iloc[0]
        best = g[g.overlay != "BASE"].sort_values("annualized_return", ascending=False).iloc[0]
        lines.append(
            f"- {factor}: BASE {base.annualized_return:.2%} / Sh {base.sharpe:.2f}; "
            f"best {best.overlay} {best.annualized_return:.2%} / Sh {best.sharpe:.2f}; "
            f"delta {(best.annualized_return-base.annualized_return):+.2%}"
        )

    lines += ["", "## Standalone trading-value signals — Top10 / 30 bps / OOS", ""]
    st = standalone[(standalone.sample == "OOS_2023_PLUS") & (standalone.top_n == 10) & (standalone.cost_bps == 30)].sort_values("annualized_return", ascending=False)
    for _, x in st.iterrows():
        lines.append(f"- {x.signal}: ann {x.annualized_return:.2%}, excess {x.annualized_excess:.2%}, Sharpe {x.sharpe:.2f}, MDD {x.mdd:.2%}, turnover {x.avg_turnover:.2f}")

    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    returns, mcap, k200_by_date = load_basic()
    ta = load_trading_amount()
    fwd = forward_returns(returns, HORIZON)
    liq_frames = build_liquidity_features(ta, mcap)

    common_dates = sorted(set(returns.index) & set(ta.index) & set(k200_by_date))
    rebalance_dates = [d for d in common_dates if d >= START][::STEP]

    factor_files = {name: dated_files(folder) for name, folder in FACTORS.items()}
    direction_rows=[]
    directions={}
    for factor, files in factor_files.items():
        direction, train_ic, n_dates = factor_direction(files, fwd, k200_by_date, rebalance_dates)
        directions[factor] = direction
        direction_rows.append({"factor":factor,"direction":direction,"train_ic":train_ic,"n_train_dates":n_dates})
    direction_df = pd.DataFrame(direction_rows)

    rows: list[dict] = []
    current: dict[tuple[str, str, int, int], list[str]] = {}
    for dt in rebalance_dates:
        if dt not in fwd.index or dt not in k200_by_date:
            continue
        k = k200_by_date[dt]
        codes = k.index[k == 1]
        y = fwd.loc[dt].reindex(codes)
        if y.notna().sum() < 50:
            continue
        bench = float(y.dropna().mean())
        liq = {name: frame.loc[dt].reindex(codes) if dt in frame.index else pd.Series(index=codes, dtype=float)
               for name, frame in liq_frames.items()}

        for factor, files in factor_files.items():
            if dt not in files:
                continue
            raw_factor = load_factor(files[dt]).reindex(codes)
            base = pct_rank(raw_factor, high_good=(directions[factor] > 0))
            scores = overlay_scores(base, liq)
            for overlay, score in scores.items():
                eligible = int(score.replace([np.inf, -np.inf], np.nan).notna().sum())
                for n in TOP_NS:
                    names = select_top(score, n)
                    if len(names) < n:
                        continue
                    gross = float(y.reindex(names).mean())
                    for cost in COSTS_BPS:
                        key = (factor, overlay, n, cost)
                        turn = overlap_turnover(current.get(key, []), names, n)
                        net = gross - turn * cost / 10000.0
                        rows.append({"date":dt,"factor":factor,"overlay":overlay,"top_n":n,"cost_bps":cost,
                                     "gross":gross,"net":net,"benchmark":bench,"excess":net-bench,
                                     "turnover":turn,"eligible":eligible})
                        current[key] = names

    periods = pd.DataFrame(rows)
    summary = summarize(periods)
    comp = compare_to_base(summary)
    robust = overlay_robustness(comp)
    standalone_periods = standalone_liquidity(fwd, k200_by_date, liq_frames, rebalance_dates)
    standalone_summary = summarize_standalone(standalone_periods)

    direction_df.to_csv(OUT / "factor_directions.csv", index=False, encoding="utf-8-sig")
    periods.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "summary.csv", index=False, encoding="utf-8-sig")
    comp.to_csv(OUT / "overlay_vs_base.csv", index=False, encoding="utf-8-sig")
    robust.to_csv(OUT / "overlay_robustness.csv", index=False, encoding="utf-8-sig")
    standalone_periods.to_csv(OUT / "standalone_period_returns.csv", index=False, encoding="utf-8-sig")
    standalone_summary.to_csv(OUT / "standalone_summary.csv", index=False, encoding="utf-8-sig")
    write_summary(direction_df, robust, summary, standalone_summary)

    print((OUT / "RESEARCH_SUMMARY.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
