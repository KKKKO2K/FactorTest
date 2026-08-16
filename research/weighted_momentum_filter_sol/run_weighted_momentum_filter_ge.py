from __future__ import annotations

import numpy as np
import pandas as pd
import run_weighted_momentum_filter as m


def variant_name(threshold):
    if threshold is None:
        return "WEIGHTED_MOM"
    tag = f"{threshold:+.0f}".replace("+", "P").replace("-", "M")
    return f"WEIGHTED_MOM_R1M_GE_{tag}"


def build_targets(returns, mcap, k200_by_date, market_by_date, wm, r1m):
    common = sorted(set(returns.index) & set(mcap.index) & set(k200_by_date) & set(market_by_date))
    common = [d for d in common if d >= pd.Timestamp("2017-01-01")]
    phase_map = {d: i % m.H for i, d in enumerate(common)}
    variants = [None] + list(m.THRESHOLDS_PCT)
    store = {u: {variant_name(t): {} for t in variants} for u in m.UNIVERSES}
    diagnostics = []

    for i, dt in enumerate(common, 1):
        if dt not in wm.index or dt not in r1m.index:
            continue
        mc = pd.to_numeric(mcap.loc[dt], errors="coerce")
        for u in m.UNIVERSES:
            codes = m.universe_codes(u, dt, k200_by_date, market_by_date)
            mc_u = mc.reindex(codes)
            eligible = mc_u.index[(mc_u >= m.MCAP_CUTOFF_BN).fillna(False)]
            if len(eligible) < 40:
                continue

            base_score = pd.to_numeric(wm.loc[dt].reindex(eligible), errors="coerce")
            recent = pd.to_numeric(r1m.loc[dt].reindex(eligible), errors="coerce")
            base_top = base_score.dropna().sort_values(ascending=False).head(m.TOPN).index

            for threshold in variants:
                name = variant_name(threshold)
                # User rule: exclude only negative 1M returns. Therefore the pre-specified 0% rule is R1M >= 0.
                score = base_score if threshold is None else base_score.where(recent >= threshold / 100.0)
                names = score.dropna().sort_values(ascending=False).head(m.TOPN).index
                if len(names) == m.TOPN:
                    store[u][name][dt] = pd.Series(1.0 / m.TOPN, index=names, dtype=float)
                if threshold is not None:
                    overlap = len(set(base_top) & set(names)) if len(base_top) == m.TOPN and len(names) == m.TOPN else np.nan
                    diagnostics.append({
                        "date": dt,
                        "universe": u,
                        "variant": name,
                        "base_eligible": int(base_score.notna().sum()),
                        "filtered_eligible": int(score.notna().sum()),
                        "base_top20_valid": int(len(base_top) == m.TOPN),
                        "filtered_top20_valid": int(len(names) == m.TOPN),
                        "top20_overlap": overlap,
                    })
        if i % 250 == 0:
            print(f"built targets {i}/{len(common)}", flush=True)

    pd.DataFrame(diagnostics).to_csv(m.OUT / "filter_diagnostics.csv", index=False, encoding="utf-8-sig")
    return store, phase_map


def paired_vs_base(stats):
    key = ["universe", "phase", "period", "cost_bp"]
    base = stats[stats.strategy == "WEIGHTED_MOM"][key + ["cagr", "mdd", "sharpe", "excess_cagr"]].rename(columns={
        "cagr": "base_cagr",
        "mdd": "base_mdd",
        "sharpe": "base_sharpe",
        "excess_cagr": "base_excess_cagr",
    })
    x = stats[stats.strategy != "WEIGHTED_MOM"].merge(base, on=key, how="left")
    x["delta_cagr"] = x.cagr - x.base_cagr
    x["delta_excess_cagr"] = x.excess_cagr - x.base_excess_cagr
    x["delta_sharpe"] = x.sharpe - x.base_sharpe
    x["delta_mdd"] = x.mdd - x.base_mdd
    summary = x.groupby(["universe", "strategy", "period", "cost_bp"], as_index=False).agg(
        n_phases=("delta_cagr", "count"),
        median_delta_cagr=("delta_cagr", "median"),
        median_delta_excess_cagr=("delta_excess_cagr", "median"),
        median_delta_sharpe=("delta_sharpe", "median"),
        median_delta_mdd=("delta_mdd", "median"),
        cagr_better_phases=("delta_cagr", lambda s: int((s > 0).sum())),
        excess_better_phases=("delta_excess_cagr", lambda s: int((s > 0).sum())),
        sharpe_better_phases=("delta_sharpe", lambda s: int((s > 0).sum())),
        mdd_better_phases=("delta_mdd", lambda s: int((s > 0).sum())),
    )
    return x, summary


def write_summary(summary, paired_summary):
    focus_periods = ["PRE_STRESS_2017_2024", "EARLY_2017_2019", "LATE_2020_2022", "NORMAL_2023_2024", "BULL_2025", "YTD_2026"]
    target = "WEIGHTED_MOM_R1M_GE_P0"
    lines = [
        "# Exact weighted momentum × nonnegative 1M filter",
        "",
        "Exact recovered signal:",
        "`WEIGHTED_MOM = (12*R1M + 4*R3M + 2*R6M + R12M) / 17`",
        "",
        "Calendar-month as-of horizons; market-cap >= KRW 250bn; descending Top20; equal-weight; 10 staggered 10-trading-day rebalance phases.",
        "Pre-specified hypothesis: exclude only names with R1M < 0, i.e. retain R1M >= 0.",
        "",
        "## NET30 comparison",
        "",
    ]
    for period in focus_periods:
        lines.append(f"### {period}")
        s0 = summary[(summary.period == period) & (summary.cost_bp == 30)]
        p0 = paired_summary[(paired_summary.period == period) & (paired_summary.cost_bp == 30)]
        for u in m.UNIVERSES:
            base = s0[(s0.universe == u) & (s0.strategy == "WEIGHTED_MOM")]
            filt = s0[(s0.universe == u) & (s0.strategy == target)]
            pair = p0[(p0.universe == u) & (p0.strategy == target)]
            if base.empty or filt.empty or pair.empty:
                continue
            b, f, p = base.iloc[0], filt.iloc[0], pair.iloc[0]
            lines.append(
                f"- {u}: BASE CAGR {b.median_cagr:+.2%}, FILTER {f.median_cagr:+.2%}, median Δ {p.median_delta_cagr:+.2%}; "
                f"Sharpe {b.median_sharpe:.2f}->{f.median_sharpe:.2f}; MDD {b.median_mdd:+.1%}->{f.median_mdd:+.1%}; "
                f"CAGR better {int(p.cagr_better_phases)}/{int(p.n_phases)} phases; excess better {int(p.excess_better_phases)}/{int(p.n_phases)}."
            )
        lines.append("")
    lines += [
        "## Threshold sensitivity",
        "",
        "Neighboring thresholds -10%, -5%, 0%, +5%, +10% use >= consistently. The 0% rule is pre-specified; neighbors test whether zero is special or part of a broader recent-momentum confirmation effect.",
        "",
    ]
    (m.OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


# Patch only the filter semantics and labels; all signal reconstruction, simulation, benchmark, and statistics stay in the independent base implementation.
m.variant_name = variant_name
m.build_targets = build_targets
m.paired_vs_base = paired_vs_base
m.write_summary = write_summary

if __name__ == "__main__":
    m.main()
