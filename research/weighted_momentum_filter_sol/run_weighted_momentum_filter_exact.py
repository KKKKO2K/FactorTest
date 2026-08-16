from __future__ import annotations

import math
import numpy as np
import pandas as pd
import run_weighted_momentum_filter_ge as ge

m = ge.m

WORKBOOK_SAMPLES = {
    "A000070": {"r1": -6.55, "r3": -18.55, "r6": -7.61, "r12": -3.75, "factor": -10.104117647058825},
    "A000080": {"r1": -6.13, "r3": -5.24, "r6": -16.08, "r12": -20.80, "factor": -8.67529411764706},
    "A000100": {"r1": -8.02, "r3": -20.50, "r6": -30.80, "r12": -24.45, "factor": -15.546470588235294},
    "A000120": {"r1": -8.33, "r3": -25.96, "r6": -11.77, "r12": 1.44, "factor": -13.288235294117648},
    "A000150": {"r1": 0.62, "r3": 46.31, "r6": 93.56, "r12": 165.36, "factor": 32.06823529411765},
}
VALIDATION_DATE = pd.Timestamp("2026-06-17")


def geometric_active_stats(port, bench):
    q = pd.concat([pd.Series(port).rename("p"), pd.Series(bench).rename("b")], axis=1).dropna()
    if len(q) < 40:
        return (np.nan,) * 3
    active = q.p - q.b
    sd = active.std(ddof=1)
    ir = float(active.mean() / sd * math.sqrt(252.0)) if np.isfinite(sd) and sd > 0 else np.nan
    rel = (1.0 + q.p) / (1.0 + q.b) - 1.0
    ex_cagr = m.cagr(rel)
    rel_mdd = m.mdd(rel)
    return ex_cagr, ir, rel_mdd


def phase_stats_exact(daily, benchmark):
    bench_map = benchmark.set_index(["date", "universe"])["benchmark_ret"]
    rows = []
    for u in m.UNIVERSES:
        for strategy in daily[u]:
            for phase, d in daily[u][strategy].items():
                if d.empty:
                    continue
                x = d.copy().sort_values("date")
                x["benchmark_ret"] = [bench_map.get((dt, u), np.nan) for dt in x.date]
                for period, (start, end) in m.PERIODS.items():
                    z = x[(x.date >= start) & (x.date <= end)]
                    if len(z) < 40:
                        continue
                    years = len(z) / 252.0
                    for cost in m.COSTS_BP:
                        r = z[f"net{cost}_ret"]
                        b = z["benchmark_ret"]
                        ex, ir, rdd = geometric_active_stats(r.reset_index(drop=True), b.reset_index(drop=True))
                        rows.append({
                            "universe": u,
                            "strategy": strategy,
                            "phase": phase,
                            "period": period,
                            "cost_bp": cost,
                            "n_days": len(z),
                            "cagr": m.cagr(r),
                            "mdd": m.mdd(r),
                            "sharpe": m.sharpe(r),
                            "benchmark_cagr": m.cagr(b),
                            "excess_cagr": ex,
                            "information_ratio": ir,
                            "relative_mdd": rdd,
                            "turnover_x": float(z.turnover.sum() / years) if years > 0 else np.nan,
                        })
    return pd.DataFrame(rows)


def validate_calendar_source(returns: pd.DataFrame, mcap: pd.DataFrame):
    idx = returns.index
    logs = np.log1p(returns.clip(lower=-0.999999).fillna(0.0))
    cs = logs.cumsum()
    rows = []
    if VALIDATION_DATE not in idx:
        return pd.DataFrame(), pd.DataFrame()
    i = idx.get_loc(VALIDATION_DATE)
    if not isinstance(i, (int, np.integer)):
        return pd.DataFrame(), pd.DataFrame()
    for code, expected in WORKBOOK_SAMPLES.items():
        rec = {"date": VALIDATION_DATE, "code": code}
        weighted_pct = 0.0
        valid_factor = True
        for months, w in m.WMOM_WEIGHTS.items():
            anchor = VALIDATION_DATE - pd.DateOffset(months=months)
            j = int(idx.searchsorted(anchor, side="right") - 1)
            got = np.nan
            if j >= 0 and j < i and code in returns.columns:
                mc_now = mcap.at[VALIDATION_DATE, code] if code in mcap.columns else np.nan
                mc_old = mcap.iloc[j][code] if code in mcap.columns else np.nan
                if np.isfinite(mc_now) and np.isfinite(mc_old) and mc_now > 0 and mc_old > 0:
                    got = float(np.expm1(cs.at[VALIDATION_DATE, code] - cs.iloc[j][code]) * 100.0)
            exp = expected[f"r{months}"]
            rec[f"r{months}_calc_pct"] = got
            rec[f"r{months}_workbook_pct"] = exp
            rec[f"r{months}_error_pp"] = got - exp if np.isfinite(got) else np.nan
            if np.isfinite(got):
                weighted_pct += got * w
            else:
                valid_factor = False
        rec["factor_calc_pct"] = weighted_pct if valid_factor else np.nan
        rec["factor_workbook_pct"] = expected["factor"]
        rec["factor_error_pp"] = weighted_pct - expected["factor"] if valid_factor else np.nan
        rows.append(rec)
    detail = pd.DataFrame(rows)
    raw_errors = []
    for months in (1, 3, 6, 12):
        raw_errors.extend(detail[f"r{months}_error_pp"].dropna().tolist())
    factor_errors = detail.factor_error_pp.dropna().to_numpy(float)
    summary = pd.DataFrame([{
        "method": "CALENDAR_MONTH_ASOF",
        "raw_component_rmse_pp": float(np.sqrt(np.mean(np.square(raw_errors)))) if raw_errors else np.nan,
        "raw_component_mae_pp": float(np.mean(np.abs(raw_errors))) if raw_errors else np.nan,
        "factor_rmse_pp": float(np.sqrt(np.mean(np.square(factor_errors)))) if len(factor_errors) else np.nan,
        "factor_mae_pp": float(np.mean(np.abs(factor_errors))) if len(factor_errors) else np.nan,
        "n_samples": int(len(detail)),
    }])
    detail.to_csv(m.OUT / "source_definition_validation.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(m.OUT / "source_definition_validation_summary.csv", index=False, encoding="utf-8-sig")
    return detail, summary


def baseline_tieout(summary):
    # Legacy primary recheck values from research/factor-lab-v2 PRIMARY_SUMMARY.md, NET30 medians.
    expected = {
        ("K200", "PRE_STRESS_2017_2024"): -0.1005,
        ("KOSPI_EX_K200", "PRE_STRESS_2017_2024"): -0.1268,
        ("KOSPI_ALL", "PRE_STRESS_2017_2024"): -0.1480,
        ("KOSDAQ", "PRE_STRESS_2017_2024"): -0.0474,
        ("KOSPI_KOSDAQ_ALL", "PRE_STRESS_2017_2024"): -0.1000,
        ("KOSDAQ_PLUS_KOSPI_EX_K200", "PRE_STRESS_2017_2024"): -0.0926,
    }
    rows = []
    for (u, period), exp in expected.items():
        q = summary[(summary.universe == u) & (summary.strategy == "WEIGHTED_MOM") & (summary.period == period) & (summary.cost_bp == 30)]
        got = float(q.iloc[0].median_cagr) if not q.empty else np.nan
        rows.append({"universe": u, "period": period, "legacy_primary_cagr_rounded": exp, "independent_cagr": got, "difference_pp_vs_rounded": (got-exp)*100 if np.isfinite(got) else np.nan})
    out = pd.DataFrame(rows)
    out.to_csv(m.OUT / "baseline_tieout.csv", index=False, encoding="utf-8-sig")
    return out


def main():
    returns, mcap, k200_by_date, market_by_date = m.load_basic()
    print(f"returns {returns.shape}; mcap {mcap.shape}", flush=True)
    _, validation_summary = validate_calendar_source(returns, mcap)
    if len(validation_summary):
        print("source validation:", validation_summary.to_dict("records"), flush=True)
    wm, r1m = m.calendar_weighted_momentum(returns, mcap)
    store, phase_map = m.build_targets(returns, mcap, k200_by_date, market_by_date, wm, r1m)
    daily = {u: {s: {} for s in store[u]} for u in m.UNIVERSES}
    for u in m.UNIVERSES:
        for strategy, targets in store[u].items():
            for phase in range(m.H):
                daily[u][strategy][phase] = m.simulate_one(returns, targets, phase, phase_map)
        print(f"simulated {u}", flush=True)
    benchmark = m.build_benchmark(returns, mcap, k200_by_date, market_by_date)
    stats = phase_stats_exact(daily, benchmark)
    summary = m.summarize_phases(stats)
    paired, paired_summary = m.paired_vs_base(stats)
    tieout = baseline_tieout(summary)
    stats.to_csv(m.OUT / "phase_stats.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(m.OUT / "summary.csv", index=False, encoding="utf-8-sig")
    paired.to_csv(m.OUT / "paired_phase_stats.csv", index=False, encoding="utf-8-sig")
    paired_summary.to_csv(m.OUT / "paired_summary.csv", index=False, encoding="utf-8-sig")
    m.write_summary(summary, paired_summary)
    print("baseline tieout:", tieout.to_dict("records"), flush=True)
    print(f"done stats={len(stats):,}; summary={len(summary):,}", flush=True)


if __name__ == "__main__":
    main()
