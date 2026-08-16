from __future__ import annotations

from pathlib import Path
import math
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
BASIC = ROOT / "source" / "factor_all_values" / "reference_snapshots" / "basic_info"
OUT = Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
H = 10
TOPN = 20
MCAP_CUTOFF_BN = 250.0
COSTS_BP = (0, 30, 60)
THRESHOLDS_PCT = (-10.0, -5.0, 0.0, 5.0, 10.0)
UNIVERSES = (
    "K200",
    "KOSPI_EX_K200",
    "KOSPI_ALL",
    "KOSDAQ",
    "KOSPI_KOSDAQ_ALL",
    "KOSDAQ_PLUS_KOSPI_EX_K200",
)
PERIODS = {
    "PRE_STRESS_2017_2024": (pd.Timestamp("2017-01-01"), pd.Timestamp("2024-12-31")),
    "EARLY_2017_2019": (pd.Timestamp("2017-01-01"), pd.Timestamp("2019-12-31")),
    "LATE_2020_2022": (pd.Timestamp("2020-01-01"), pd.Timestamp("2022-12-31")),
    "NORMAL_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2024-12-31")),
    "BULL_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    "YTD_2026": (pd.Timestamp("2026-01-01"), pd.Timestamp("2099-12-31")),
}
WMOM_WEIGHTS = {1: 12.0 / 17.0, 3: 4.0 / 17.0, 6: 2.0 / 17.0, 12: 1.0 / 17.0}


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


def find_col(df: pd.DataFrame, exact=(), contains=()) -> str | None:
    for c in df.columns:
        if str(c).strip() in exact:
            return c
    for c in df.columns:
        s = str(c).strip().lower()
        if any(str(k).lower() in s for k in contains):
            return c
    return None


def normalize_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return x.where(x.str.startswith("A"), "A" + x.str.zfill(6))


def load_basic():
    ret_rows, mcap_rows = [], []
    k200_by_date, market_by_date = {}, {}
    for i, (dt, path) in enumerate(dated_files(BASIC).items(), 1):
        df = read_csv(path)
        cc = find_col(df, exact=("Code", "StockCode", "종목코드"))
        rc = find_col(df, exact=("수정주가수익률",), contains=("수정주가수익률",))
        mc = find_col(df, exact=("시가총액",), contains=("시가총액",))
        kc = find_col(df, contains=("코스피200", "k200"))
        mk = find_col(df, exact=("상장된 시장",), contains=("상장된 시장",))
        if None in (cc, rc, mc, kc, mk):
            continue
        code = normalize_code(df[cc])
        ret = pd.to_numeric(df[rc], errors="coerce") / 100.0
        mcap = pd.to_numeric(df[mc], errors="coerce")
        k200 = pd.to_numeric(df[kc], errors="coerce").fillna(0).astype(int)
        market = df[mk].astype(str).str.upper().str.strip()
        p = pd.DataFrame({"code": code, "ret": ret, "mcap": mcap, "k200": k200, "market": market}).drop_duplicates("code", keep="last")
        ret_rows.append(pd.DataFrame({"date": dt, "code": p.code, "value": p.ret}))
        mcap_rows.append(pd.DataFrame({"date": dt, "code": p.code, "value": p.mcap}))
        k200_by_date[dt] = pd.Series(p.k200.to_numpy(), index=p.code)
        market_by_date[dt] = pd.Series(p.market.to_numpy(), index=p.code)
        if i % 500 == 0:
            print(f"loaded basic {i}", flush=True)
    returns = pd.concat(ret_rows, ignore_index=True).pivot(index="date", columns="code", values="value").sort_index()
    mcap = pd.concat(mcap_rows, ignore_index=True).pivot(index="date", columns="code", values="value").sort_index()
    return returns, mcap, k200_by_date, market_by_date


def calendar_weighted_momentum(returns: pd.DataFrame, mcap: pd.DataFrame):
    idx = returns.index
    cols = returns.columns
    logs = np.log1p(returns.clip(lower=-0.999999).fillna(0.0))
    cs = logs.cumsum().to_numpy(float)
    mc = mcap.reindex(index=idx, columns=cols).to_numpy(float)
    nrow, ncol = cs.shape
    weighted = np.full((nrow, ncol), np.nan, dtype=float)
    r1 = np.full((nrow, ncol), np.nan, dtype=float)
    for i, dt in enumerate(idx):
        acc = np.zeros(ncol, dtype=float)
        valid_all = np.ones(ncol, dtype=bool)
        ok = True
        for months, w in WMOM_WEIGHTS.items():
            anchor = dt - pd.DateOffset(months=months)
            j = int(idx.searchsorted(anchor, side="right") - 1)
            if j < 0 or j >= i:
                ok = False
                break
            raw = np.expm1(cs[i] - cs[j])
            valid = np.isfinite(mc[i]) & np.isfinite(mc[j]) & (mc[i] > 0) & (mc[j] > 0)
            raw[~valid] = np.nan
            if months == 1:
                r1[i] = raw
            acc += np.nan_to_num(raw, nan=0.0) * w
            valid_all &= valid
        if ok:
            acc[~valid_all] = np.nan
            weighted[i] = acc
        if i % 500 == 0 and i:
            print(f"built weighted momentum {i}/{nrow}", flush=True)
    return pd.DataFrame(weighted, index=idx, columns=cols), pd.DataFrame(r1, index=idx, columns=cols)


def universe_codes(name, dt, k200_by_date, market_by_date):
    k = k200_by_date[dt]
    mk = market_by_date[dt]
    idx = k.index.intersection(mk.index)
    k = k.reindex(idx).fillna(0).astype(int)
    mk = mk.reindex(idx).fillna("").astype(str).str.upper()
    kospi = mk.str.contains("KOSPI", na=False)
    kosdaq = mk.str.contains("KOSDAQ", na=False)
    k200 = k.eq(1)
    if name == "K200":
        mask = k200
    elif name == "KOSPI_EX_K200":
        mask = kospi & ~k200
    elif name == "KOSPI_ALL":
        mask = kospi
    elif name == "KOSDAQ":
        mask = kosdaq
    elif name == "KOSPI_KOSDAQ_ALL":
        mask = kospi | kosdaq
    elif name == "KOSDAQ_PLUS_KOSPI_EX_K200":
        mask = kosdaq | (kospi & ~k200)
    else:
        raise ValueError(name)
    return idx[mask.to_numpy()]


def variant_name(threshold):
    if threshold is None:
        return "WEIGHTED_MOM"
    tag = f"{threshold:+.0f}".replace("+", "P").replace("-", "M")
    return f"WEIGHTED_MOM_R1M_GT_{tag}"


def build_targets(returns, mcap, k200_by_date, market_by_date, wm, r1m):
    common = sorted(set(returns.index) & set(mcap.index) & set(k200_by_date) & set(market_by_date))
    common = [d for d in common if d >= pd.Timestamp("2017-01-01")]
    phase_map = {d: i % H for i, d in enumerate(common)}
    variants = [None] + list(THRESHOLDS_PCT)
    store = {u: {variant_name(t): {} for t in variants} for u in UNIVERSES}
    diagnostics = []
    for i, dt in enumerate(common, 1):
        if dt not in wm.index or dt not in r1m.index:
            continue
        mc = pd.to_numeric(mcap.loc[dt], errors="coerce")
        for u in UNIVERSES:
            codes = universe_codes(u, dt, k200_by_date, market_by_date)
            mc_u = mc.reindex(codes)
            eligible = mc_u.index[(mc_u >= MCAP_CUTOFF_BN).fillna(False)]
            if len(eligible) < 40:
                continue
            base_score = pd.to_numeric(wm.loc[dt].reindex(eligible), errors="coerce")
            recent = pd.to_numeric(r1m.loc[dt].reindex(eligible), errors="coerce")
            base_top = base_score.dropna().sort_values(ascending=False).head(TOPN).index
            for threshold in variants:
                name = variant_name(threshold)
                score = base_score if threshold is None else base_score.where(recent > threshold / 100.0)
                names = score.dropna().sort_values(ascending=False).head(TOPN).index
                if len(names) == TOPN:
                    store[u][name][dt] = pd.Series(1.0 / TOPN, index=names, dtype=float)
                if threshold is not None:
                    overlap = len(set(base_top) & set(names)) if len(base_top) == TOPN and len(names) == TOPN else np.nan
                    diagnostics.append({"date": dt, "universe": u, "variant": name, "base_eligible": int(base_score.notna().sum()), "filtered_eligible": int(score.notna().sum()), "base_top20_valid": int(len(base_top) == TOPN), "filtered_top20_valid": int(len(names) == TOPN), "top20_overlap": overlap})
        if i % 250 == 0:
            print(f"built targets {i}/{len(common)}", flush=True)
    pd.DataFrame(diagnostics).to_csv(OUT / "filter_diagnostics.csv", index=False, encoding="utf-8-sig")
    return store, phase_map


def simulate_one(returns, targets, phase, phase_map):
    scheduled = sorted(d for d in targets if phase_map.get(d) == phase)
    if not scheduled:
        return pd.DataFrame()
    scheduled_set = set(scheduled)
    current = pd.Series(dtype=float)
    rows = []
    for dt in returns.index[returns.index >= scheduled[0]]:
        gross = 0.0
        if len(current):
            rr = returns.loc[dt].reindex(current.index).clip(lower=-0.999999).fillna(0.0)
            gross = float((current * rr).sum())
            grown = current * (1.0 + rr)
            denom = float(grown.sum())
            if denom > 0:
                current = grown / denom
        turnover = 0.0
        if dt in scheduled_set:
            target = targets[dt]
            if len(current):
                union = current.index.union(target.index)
                turnover = float(0.5 * (current.reindex(union, fill_value=0.0) - target.reindex(union, fill_value=0.0)).abs().sum())
            else:
                turnover = 1.0
            current = target.copy()
        rec = {"date": dt, "gross_ret": gross, "turnover": turnover}
        for cost in COSTS_BP:
            c = turnover * cost / 10000.0
            rec[f"net{cost}_ret"] = (1.0 + gross) * (1.0 - c) - 1.0
        rows.append(rec)
    return pd.DataFrame(rows)


def build_benchmark(returns, mcap, k200_by_date, market_by_date):
    rows = []
    dates = list(returns.index)
    for i in range(1, len(dates)):
        dt, prev = dates[i], dates[i - 1]
        if prev not in k200_by_date or prev not in market_by_date or prev not in mcap.index:
            continue
        for u in UNIVERSES:
            codes = universe_codes(u, prev, k200_by_date, market_by_date)
            mc = pd.to_numeric(mcap.loc[prev].reindex(codes), errors="coerce")
            mc = mc[(mc > 0) & mc.notna()]
            if len(mc) < (50 if u == "K200" else 100):
                continue
            w = mc / mc.sum()
            rr = returns.loc[dt].reindex(w.index).clip(lower=-0.999999).fillna(0.0)
            rows.append({"date": dt, "universe": u, "benchmark_ret": float((w * rr).sum())})
    return pd.DataFrame(rows)


def cagr(r):
    r = pd.Series(r).dropna()
    if len(r) < 2:
        return np.nan
    total = float((1.0 + r).prod())
    years = len(r) / 252.0
    return total ** (1.0 / years) - 1.0 if total > 0 and years > 0 else np.nan


def sharpe(r):
    r = pd.Series(r).dropna()
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(252.0)) if len(r) >= 3 and np.isfinite(sd) and sd > 0 else np.nan


def mdd(r):
    r = pd.Series(r).dropna()
    if not len(r):
        return np.nan
    nav = (1.0 + r).cumprod()
    return float((nav / nav.cummax() - 1.0).min())


def information_ratio(active):
    a = pd.Series(active).dropna()
    sd = a.std(ddof=1)
    return float(a.mean() / sd * math.sqrt(252.0)) if len(a) >= 3 and np.isfinite(sd) and sd > 0 else np.nan


def phase_stats(daily, benchmark):
    bench_map = benchmark.set_index(["date", "universe"])["benchmark_ret"]
    rows = []
    for u in UNIVERSES:
        for strategy in daily[u]:
            for phase, d in daily[u][strategy].items():
                if d.empty:
                    continue
                x = d.copy()
                x["benchmark_ret"] = [bench_map.get((dt, u), np.nan) for dt in x.date]
                for period, (start, end) in PERIODS.items():
                    z = x[(x.date >= start) & (x.date <= end)].dropna(subset=["benchmark_ret"])
                    if len(z) < 40:
                        continue
                    for cost in COSTS_BP:
                        r = z[f"net{cost}_ret"]
                        b = z["benchmark_ret"]
                        active = r - b
                        rows.append({"universe": u, "strategy": strategy, "phase": phase, "period": period, "cost_bp": cost, "n_days": len(z), "cagr": cagr(r), "mdd": mdd(r), "sharpe": sharpe(r), "benchmark_cagr": cagr(b), "excess_cagr": cagr(r) - cagr(b), "information_ratio": information_ratio(active), "relative_mdd": mdd(active), "turnover_x": float(z.turnover.sum() / (len(z) / 252.0))})
    return pd.DataFrame(rows)


def summarize_phases(stats):
    rows = []
    for keys, g in stats.groupby(["universe", "strategy", "period", "cost_bp"]):
        rows.append({"universe": keys[0], "strategy": keys[1], "period": keys[2], "cost_bp": keys[3], "n_phases": len(g), "median_cagr": g.cagr.median(), "median_mdd": g.mdd.median(), "median_sharpe": g.sharpe.median(), "median_benchmark_cagr": g.benchmark_cagr.median(), "median_excess_cagr": g.excess_cagr.median(), "median_information_ratio": g.information_ratio.median(), "median_relative_mdd": g.relative_mdd.median(), "median_turnover": g.turnover_x.median(), "positive_cagr_phases": int((g.cagr > 0).sum()), "positive_excess_phases": int((g.excess_cagr > 0).sum())})
    return pd.DataFrame(rows)


def paired_vs_base(stats):
    key = ["universe", "phase", "period", "cost_bp"]
    base = stats[stats.strategy == "WEIGHTED_MOM"][key + ["cagr", "mdd", "sharpe", "excess_cagr"]].rename(columns={"cagr": "base_cagr", "mdd": "base_mdd", "sharpe": "base_sharpe", "excess_cagr": "base_excess_cagr"})
    x = stats[stats.strategy != "WEIGHTED_MOM"].merge(base, on=key, how="left")
    x["delta_cagr"] = x.cagr - x.base_cagr
    x["delta_excess_cagr"] = x.excess_cagr - x.base_excess_cagr
    x["delta_sharpe"] = x.sharpe - x.base_sharpe
    x["delta_mdd"] = x.mdd - x.base_mdd
    summary = x.groupby(["universe", "strategy", "period", "cost_bp"], as_index=False).agg(n_phases=("delta_cagr", "count"), median_delta_cagr=("delta_cagr", "median"), median_delta_excess_cagr=("delta_excess_cagr", "median"), median_delta_sharpe=("delta_sharpe", "median"), median_delta_mdd=("delta_mdd", "median"), cagr_better_phases=("delta_cagr", lambda s: int((s > 0).sum())), excess_better_phases=("delta_excess_cagr", lambda s: int((s > 0).sum())), sharpe_better_phases=("delta_sharpe", lambda s: int((s > 0).sum())), mdd_better_phases=("delta_mdd", lambda s: int((s > 0).sum())))
    return x, summary


def write_summary(summary, paired_summary):
    focus_periods = ["PRE_STRESS_2017_2024", "NORMAL_2023_2024", "BULL_2025", "YTD_2026"]
    lines = ["# Exact weighted momentum × 1M filter", "", "Exact recovered signal:", "`WEIGHTED_MOM = (12*R1M + 4*R3M + 2*R6M + R12M) / 17`", "", "Calendar-month as-of horizons; market-cap >= KRW 250bn; descending Top20; equal-weight; 10 staggered 10-trading-day rebalance phases.", "The intended test is `WEIGHTED_MOM_R1M_GT_P0`: same weighted-momentum ranking after excluding names with R1M <= 0.", "", "## NET30 comparison", ""]
    for period in focus_periods:
        lines.append(f"### {period}")
        s0 = summary[(summary.period == period) & (summary.cost_bp == 30)]
        p0 = paired_summary[(paired_summary.period == period) & (paired_summary.cost_bp == 30)]
        for u in UNIVERSES:
            base = s0[(s0.universe == u) & (s0.strategy == "WEIGHTED_MOM")]
            filt = s0[(s0.universe == u) & (s0.strategy == "WEIGHTED_MOM_R1M_GT_P0")]
            pair = p0[(p0.universe == u) & (p0.strategy == "WEIGHTED_MOM_R1M_GT_P0")]
            if base.empty or filt.empty or pair.empty:
                continue
            b, f, p = base.iloc[0], filt.iloc[0], pair.iloc[0]
            lines.append(f"- {u}: BASE CAGR {b.median_cagr:+.2%}, FILTER {f.median_cagr:+.2%}, median Δ {p.median_delta_cagr:+.2%}; Sharpe {b.median_sharpe:.2f}->{f.median_sharpe:.2f}; MDD {b.median_mdd:+.1%}->{f.median_mdd:+.1%}; CAGR better {int(p.cagr_better_phases)}/{int(p.n_phases)} phases.")
        lines.append("")
    lines += ["## Threshold sensitivity", "", "Thresholds -10%, -5%, 0%, +5%, +10% are diagnostics. The 0% rule is the pre-specified hypothesis; neighboring thresholds test whether zero is special or merely part of a broader recent-momentum confirmation effect.", ""]
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    returns, mcap, k200_by_date, market_by_date = load_basic()
    print(f"returns {returns.shape}; mcap {mcap.shape}", flush=True)
    wm, r1m = calendar_weighted_momentum(returns, mcap)
    store, phase_map = build_targets(returns, mcap, k200_by_date, market_by_date, wm, r1m)
    daily = {u: {s: {} for s in store[u]} for u in UNIVERSES}
    for u in UNIVERSES:
        for strategy, targets in store[u].items():
            for phase in range(H):
                daily[u][strategy][phase] = simulate_one(returns, targets, phase, phase_map)
        print(f"simulated {u}", flush=True)
    benchmark = build_benchmark(returns, mcap, k200_by_date, market_by_date)
    stats = phase_stats(daily, benchmark)
    summary = summarize_phases(stats)
    paired, paired_summary = paired_vs_base(stats)
    stats.to_csv(OUT / "phase_stats.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "summary.csv", index=False, encoding="utf-8-sig")
    paired.to_csv(OUT / "paired_phase_stats.csv", index=False, encoding="utf-8-sig")
    paired_summary.to_csv(OUT / "paired_summary.csv", index=False, encoding="utf-8-sig")
    write_summary(summary, paired_summary)
    print(f"done stats={len(stats):,}; summary={len(summary):,}", flush=True)


if __name__ == "__main__":
    main()
