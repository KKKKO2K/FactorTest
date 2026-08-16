from __future__ import annotations

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
OUT.mkdir(parents=True, exist_ok=True)

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
START = pd.Timestamp("2016-04-01")
POST_START = pd.Timestamp("2023-01-01")
STEP = 10
HORIZON = 10
TOP_NS = (10, 20, 30)
WEIGHTINGS = ("rank_linear", "equal")
COSTS_BPS = (0, 30, 60, 100)
ABS_THRESHOLDS = (-10.0, -5.0, 0.0, 5.0, 10.0)
PCTL_CUTOFFS = (0.10, 0.20, 0.30, 0.40, 0.50)
BLEND_WEIGHTS = (0.10, 0.20, 0.30)
UNIVERSES = (
    "KOSPI200",
    "KOSPI_EX_K200",
    "KOSPI",
    "KOSDAQ",
    "KOSPI_KOSDAQ",
    "KOSDAQ_PLUS_KOSPI_EX_K200",
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
    if not folder.exists():
        return out
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def find_col(df: pd.DataFrame, exact=(), contains=()) -> str | None:
    for c in df.columns:
        s = str(c).strip()
        if s in exact:
            return c
    for c in df.columns:
        s = str(c).strip().lower()
        if any(str(k).lower() in s for k in contains):
            return c
    return None


def normalize_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return x.where(x.str.startswith("A"), "A" + x.str.zfill(6))


def load_factor(folder: Path, dt: pd.Timestamp) -> pd.Series:
    path = folder / f"{dt.date().isoformat()}.csv"
    if not path.exists():
        return pd.Series(dtype=float)
    df = read_csv(path)
    cc = find_col(df, exact=("StockCode", "Code", "종목코드"))
    vc = find_col(df, exact=("FactorValue",), contains=("factorvalue",))
    if cc is None or vc is None:
        return pd.Series(dtype=float)
    codes = normalize_code(df[cc])
    vals = pd.to_numeric(df[vc], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return pd.Series(vals.to_numpy(), index=codes).groupby(level=0).last()


def load_basic() -> tuple[pd.DataFrame, dict[pd.Timestamp, pd.DataFrame]]:
    rows = []
    panels: dict[pd.Timestamp, pd.DataFrame] = {}
    for dt, path in dated_files(BASIC).items():
        df = read_csv(path)
        cc = find_col(df, exact=("Code", "StockCode", "종목코드"))
        rc = find_col(df, exact=("수정주가수익률",), contains=("수정주가수익률", "daily_return"))
        mc = find_col(df, exact=("상장된 시장",), contains=("상장된 시장", "market"))
        kc = find_col(df, contains=("코스피200", "k200"))
        if cc is None or rc is None:
            continue
        code = normalize_code(df[cc])
        ret = pd.to_numeric(df[rc], errors="coerce") / 100.0
        market = df[mc].astype(str).str.upper().str.strip() if mc is not None else pd.Series("", index=df.index)
        k200 = pd.to_numeric(df[kc], errors="coerce").fillna(0).astype(int) if kc is not None else pd.Series(0, index=df.index)
        p = pd.DataFrame({"ret": ret.to_numpy(), "market": market.to_numpy(), "k200": k200.to_numpy()}, index=code)
        p = p[~p.index.duplicated(keep="last")]
        panels[dt] = p
        rows.append(pd.DataFrame({"date": dt, "code": p.index, "ret": p.ret.to_numpy()}))
    if not rows:
        raise RuntimeError("No basic_info panels found")
    returns = pd.concat(rows, ignore_index=True).pivot(index="date", columns="code", values="ret").sort_index()
    return returns, panels


def universe_mask(p: pd.DataFrame, name: str) -> pd.Series:
    kospi = p.market.str.contains("KOSPI", na=False)
    kosdaq = p.market.str.contains("KOSDAQ", na=False)
    k200 = p.k200.eq(1)
    if name == "KOSPI200":
        return k200
    if name == "KOSPI_EX_K200":
        return kospi & ~k200
    if name == "KOSPI":
        return kospi
    if name == "KOSDAQ":
        return kosdaq
    if name == "KOSPI_KOSDAQ":
        return kospi | kosdaq
    if name == "KOSDAQ_PLUS_KOSPI_EX_K200":
        return kosdaq | (kospi & ~k200)
    raise ValueError(name)


def forward_return(returns: pd.DataFrame, dt: pd.Timestamp) -> pd.Series:
    if dt not in returns.index:
        return pd.Series(dtype=float)
    loc = returns.index.get_loc(dt)
    if not isinstance(loc, (int, np.integer)) or loc + HORIZON >= len(returns):
        return pd.Series(dtype=float)
    block = returns.iloc[loc + 1: loc + 1 + HORIZON]
    valid = block.notna().sum(axis=0)
    out = (1.0 + block.fillna(0.0)).prod(axis=0) - 1.0
    out[valid < HORIZON] = np.nan
    return out


def pct_rank(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").rank(pct=True, method="average")


def variant_scores(mom12: pd.Series, mom1: pd.Series) -> dict[str, pd.Series]:
    x = pd.concat([mom12.rename("mom12"), mom1.rename("mom1")], axis=1)
    x = x.replace([np.inf, -np.inf], np.nan)
    m12_rank = pct_rank(x.mom12)
    m1_rank = pct_rank(x.mom1)
    out: dict[str, pd.Series] = {"BASE": x.mom12}
    for threshold in ABS_THRESHOLDS:
        tag = f"{threshold:+.0f}".replace("+", "P").replace("-", "M")
        out[f"ABS_{tag}"] = x.mom12.where(x.mom1 > threshold)
    for cutoff in PCTL_CUTOFFS:
        keep = int(round((1.0 - cutoff) * 100))
        out[f"PCTL_KEEP_TOP{keep}"] = x.mom12.where(m1_rank >= cutoff)
    for w in BLEND_WEIGHTS:
        out[f"BLEND_M1_W{int(w*100):02d}"] = (1.0 - w) * m12_rank + w * m1_rank
    return out


def make_weights(score: pd.Series, top_n: int, weighting: str) -> pd.Series:
    names = score.dropna().sort_values(ascending=False).head(top_n)
    if len(names) < top_n:
        return pd.Series(dtype=float)
    if weighting == "equal":
        raw = pd.Series(1.0, index=names.index)
    elif weighting == "rank_linear":
        raw = pd.Series(np.arange(top_n, 0, -1, dtype=float), index=names.index)
    else:
        raise ValueError(weighting)
    return raw / raw.sum()


def rank_ic(score: pd.Series, future: pd.Series) -> float:
    pair = pd.concat([score.rename("x"), future.rename("y")], axis=1).dropna()
    if len(pair) < 30 or pair.x.nunique() < 5:
        return np.nan
    return float(pair.x.rank().corr(pair.y.rank()))


def turnover(current: pd.Series, target: pd.Series) -> float:
    idx = current.index.union(target.index)
    return float(0.5 * (target.reindex(idx, fill_value=0.0) - current.reindex(idx, fill_value=0.0)).abs().sum())


def drift_weights(w: pd.Series, future: pd.Series, gross: float) -> pd.Series:
    if w.empty or 1.0 + gross <= 0:
        return pd.Series(dtype=float)
    rr = future.reindex(w.index).fillna(0.0)
    out = w * (1.0 + rr) / (1.0 + gross)
    return out[out.abs() > 1e-14]


def annualized_return(r: pd.Series) -> float:
    if len(r) == 0:
        return np.nan
    ppy = 252.0 / STEP
    return float((1.0 + r).prod() ** (ppy / len(r)) - 1.0)


def sharpe(r: pd.Series) -> float:
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(252.0 / STEP)) if len(r) > 2 and sd > 0 else np.nan


def mdd(r: pd.Series) -> float:
    if r.empty:
        return np.nan
    nav = (1.0 + r.fillna(0.0)).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def summarize(periods: pd.DataFrame) -> pd.DataFrame:
    rows = []
    keys = ["universe", "variant", "top_n", "weighting", "cost_bps", "sample"]
    for k, g in periods.groupby(keys, dropna=False):
        if len(g) < 5:
            continue
        r = g.net_return
        ex = g.excess_return
        rows.append({
            "universe": k[0], "variant": k[1], "top_n": k[2], "weighting": k[3], "cost_bps": k[4], "sample": k[5],
            "n_periods": len(g),
            "ann_return": annualized_return(r),
            "ann_excess": annualized_return(ex),
            "sharpe": sharpe(r),
            "excess_sharpe": sharpe(ex),
            "mdd": mdd(r),
            "excess_mdd": mdd(ex),
            "hit_rate": float((r > 0).mean()),
            "excess_hit_rate": float((ex > 0).mean()),
            "avg_turnover": float(g.turnover.mean()),
            "avg_eligible": float(g.n_eligible.mean()),
            "avg_rank_ic": float(g.rank_ic.mean()),
        })
    return pd.DataFrame(rows)


def main() -> None:
    returns, panels = load_basic()
    signal_dates = sorted(set(dated_files(MOM12)) & set(dated_files(MOM1)) & set(panels))
    rebalance_dates = [d for d in signal_dates if d >= START][::STEP]
    print(f"basic dates={len(returns)}, signal dates={len(signal_dates)}, rebalance dates={len(rebalance_dates)}", flush=True)

    # Cache the cross-sectional signal frames and forward returns once per date/universe.
    prepared: dict[tuple[pd.Timestamp, str], tuple[dict[str, pd.Series], pd.Series, float]] = {}
    for i, dt in enumerate(rebalance_dates, 1):
        future_all = forward_return(returns, dt)
        if future_all.empty:
            continue
        p = panels[dt]
        mom12_all = load_factor(MOM12, dt)
        mom1_all = load_factor(MOM1, dt)
        for uni in UNIVERSES:
            idx = p.index[universe_mask(p, uni)]
            mom12 = mom12_all.reindex(idx)
            mom1 = mom1_all.reindex(idx)
            future = future_all.reindex(idx)
            bench = float(future.dropna().mean()) if future.notna().sum() else np.nan
            prepared[(dt, uni)] = (variant_scores(mom12, mom1), future, bench)
        if i % 50 == 0:
            print(f"prepared {i}/{len(rebalance_dates)} dates", flush=True)

    period_rows = []
    variants = ["BASE"] + [f"ABS_{f'{t:+.0f}'.replace('+','P').replace('-','M')}" for t in ABS_THRESHOLDS]
    variants += [f"PCTL_KEEP_TOP{int(round((1-c)*100))}" for c in PCTL_CUTOFFS]
    variants += [f"BLEND_M1_W{int(w*100):02d}" for w in BLEND_WEIGHTS]

    for uni in UNIVERSES:
        for variant in variants:
            for top_n in TOP_NS:
                for weighting in WEIGHTINGS:
                    current = pd.Series(dtype=float)
                    gross_rows = []
                    for dt in rebalance_dates:
                        item = prepared.get((dt, uni))
                        if item is None:
                            continue
                        scores, future, bench = item
                        score = scores[variant]
                        target = make_weights(score, top_n, weighting)
                        if target.empty or not np.isfinite(bench):
                            continue
                        turn = turnover(current, target)
                        gross = float((target * future.reindex(target.index).fillna(0.0)).sum())
                        ic = rank_ic(score, future)
                        eligible = int(score.notna().sum())
                        gross_rows.append((dt, gross, bench, turn, eligible, ic))
                        current = drift_weights(target, future, gross)
                    if not gross_rows:
                        continue
                    for cost_bps in COSTS_BPS:
                        for dt, gross, bench, turn, eligible, ic in gross_rows:
                            net = gross - turn * cost_bps / 10000.0
                            period_rows.append({
                                "date": dt, "universe": uni, "variant": variant, "top_n": top_n,
                                "weighting": weighting, "cost_bps": cost_bps, "gross_return": gross,
                                "net_return": net, "benchmark_return": bench, "excess_return": net - bench,
                                "turnover": turn, "n_eligible": eligible, "rank_ic": ic,
                                "sample": "POST_2023" if dt >= POST_START else "TRAIN_2016_2022",
                            })

    periods = pd.DataFrame(period_rows).sort_values(["universe", "variant", "top_n", "weighting", "cost_bps", "date"])
    periods.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    summary = summarize(periods)
    summary.to_csv(OUT / "summary_train_post.csv", index=False, encoding="utf-8-sig")

    # Paired delta versus BASE for the operational weighted-momentum baseline.
    key = ["date", "universe", "top_n", "weighting", "cost_bps", "sample"]
    base = periods[periods.variant == "BASE"][key + ["net_return", "excess_return"]].rename(columns={"net_return":"base_net", "excess_return":"base_excess"})
    paired = periods.merge(base, on=key, how="left")
    paired["delta_net"] = paired.net_return - paired.base_net
    paired["delta_excess"] = paired.excess_return - paired.base_excess
    paired.to_csv(OUT / "paired_vs_base.csv", index=False, encoding="utf-8-sig")

    paired_summary = paired.groupby(["universe", "variant", "top_n", "weighting", "cost_bps", "sample"], as_index=False).agg(
        n_periods=("delta_net", "count"), mean_delta_net=("delta_net", "mean"), mean_delta_excess=("delta_excess", "mean"),
        delta_hit_rate=("delta_net", lambda x: float((x > 0).mean())),
    )
    paired_summary.to_csv(OUT / "paired_summary.csv", index=False, encoding="utf-8-sig")

    # Compact decision table: rank-linear, Top20, 60bps is the primary weighted-momentum implementation.
    decision = summary[(summary.top_n == 20) & (summary.weighting == "rank_linear") & (summary.cost_bps == 60)].copy()
    decision.to_csv(OUT / "decision_table_top20_ranklinear_60bps.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Momentum 12-1 × recent 1M filter — independent branch",
        "",
        "Primary operational baseline: Top20 MOM(12-1), linear rank weights, 10-trading-day rebalance/holding, 60 bps one-way turnover cost.",
        "Equal weighting, Top10/20/30 and 0/30/60/100 bps are robustness checks.",
        "TRAIN_2016_2022 and POST_2023 are descriptive subperiod labels; POST is not claimed as untouched OOS.",
        "",
        "## Primary decision table",
        "",
        decision.sort_values(["universe", "sample", "variant"]).to_markdown(index=False) if not decision.empty else "No results",
    ]
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    print("done", flush=True)


if __name__ == "__main__":
    main()
