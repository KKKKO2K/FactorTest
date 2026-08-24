from __future__ import annotations

from itertools import combinations
from pathlib import Path
import importlib.util
import math

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

BASE_SCRIPT = ROOT / "research/nonstationary_factor_selection/run_all_selection_methods.py"
spec = importlib.util.spec_from_file_location("nsfs", BASE_SCRIPT)
nsfs = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(nsfs)

FACTORS = nsfs.FACTORS
UNIVERSES = nsfs.UNIVERSES
PERIODS = nsfs.PERIODS
N = len(FACTORS)
COSTS = [0, 10, 30]


def spearman(a, b):
    x = pd.Series(np.asarray(a, dtype=float))
    y = pd.Series(np.asarray(b, dtype=float))
    ok = x.notna() & y.notna()
    x, y = x[ok], y[ok]
    if len(x) < 4 or x.nunique() < 2 or y.nunique() < 2:
        return np.nan
    return float(x.rank(method="average").corr(y.rank(method="average")))


def fit_frozen_pairwise(common):
    feats = nsfs.common_features(common)
    arr = common.to_numpy(dtype=float)
    X, y = [], []
    for i, feat in feats:
        if i + 1 >= len(common) or common.index[i + 1].year > 2019:
            continue
        nxt = arr[i + 1]
        for a, b in combinations(range(N), 2):
            X.append(feat[a] - feat[b])
            y.append(float(nxt[a] > nxt[b]))
    beta, mean, std = nsfs.fit_logistic(np.asarray(X), np.asarray(y))
    return beta, mean, std, feats


def cycle_rate(prob):
    cycles = 0
    total = 0
    for a, b, c in combinations(range(N), 3):
        ab = prob[a, b] > 0.5
        bc = prob[b, c] > 0.5
        ca = prob[c, a] > 0.5
        # Directed 3-cycle: a>b, b>c, c>a, or exact reverse.
        is_cycle = (ab and bc and ca) or ((not ab) and (not bc) and (not ca))
        cycles += int(is_cycle)
        total += 1
    return float(cycles / total) if total else np.nan


def build_confidence_panel(common):
    beta, mean, std, feats = fit_frozen_pairwise(common)
    rows = []
    pair_q = pd.DataFrame(np.ones((len(common), N)) / N, index=common.index, columns=FACTORS)

    for i, feat in feats:
        if i + 1 >= len(common):
            continue
        target_i = i + 1
        dt = common.index[target_i]
        score = np.zeros(N)
        prob = np.full((N, N), 0.5, dtype=float)
        margins = []
        for a, b in combinations(range(N), 2):
            z = np.r_[1.0, (feat[a] - feat[b] - mean) / std]
            p = float(1 / (1 + np.exp(-np.clip(z @ beta, -30, 30))))
            prob[a, b] = p
            prob[b, a] = 1 - p
            score[a] += p
            score[b] += 1 - p
            margins.append(2 * abs(p - 0.5))
        q = score / (N - 1)
        pair_q.iloc[target_i] = q
        sq = np.sort(q)
        rows.append({
            "date": dt,
            "pair_margin": float(np.mean(margins)),
            "score_sd": float(np.std(q, ddof=1)),
            "top_gap": float(sq[-1] - sq[-2]),
            "cycle_rate": cycle_rate(prob),
            **{f"q_{fac}": float(q[j]) for j, fac in enumerate(FACTORS)},
        })

    conf = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    disc = conf[conf.date.dt.year <= 2019].copy()
    metrics = ["pair_margin", "score_sd", "top_gap", "cycle_rate"]
    stats = {}
    for col in metrics:
        mu = float(disc[col].mean())
        sd = float(disc[col].std(ddof=1))
        if not np.isfinite(sd) or sd <= 1e-12:
            sd = 1.0
        stats[col] = (mu, sd)
        sign = -1.0 if col == "cycle_rate" else 1.0
        conf[f"z_{col}"] = sign * (conf[col] - mu) / sd
    zcols = [f"z_{c}" for c in metrics]
    conf["combined_conf"] = conf[zcols].mean(axis=1)

    disc_comb = conf.loc[conf.date.dt.year <= 2019, "combined_conf"].dropna().to_numpy(dtype=float)
    disc_sorted = np.sort(disc_comb)
    q80 = float(np.quantile(disc_comb, 0.80))
    quintile_cuts = np.quantile(disc_comb, [0.20, 0.40, 0.60, 0.80])

    def disc_percentile(v):
        return float(np.searchsorted(disc_sorted, v, side="right") / len(disc_sorted)) if len(disc_sorted) else np.nan

    conf["disc_percentile"] = conf.combined_conf.map(disc_percentile)
    conf["intensity"] = np.clip(2 * conf.disc_percentile - 1, 0, 1)
    conf["high_confidence"] = conf.combined_conf > q80
    conf["confidence_quintile"] = conf.combined_conf.map(lambda v: int(np.searchsorted(quintile_cuts, v, side="right") + 1))
    conf["period"] = conf.date.map(nsfs.period_of_date)

    calibration = pd.DataFrame([
        {"metric": col, "discovery_mean": stats[col][0], "discovery_std": stats[col][1]}
        for col in metrics
    ])
    calibration["combined_conf_q80"] = q80
    calibration["combined_conf_q20"] = float(quintile_cuts[0])
    calibration["combined_conf_q40"] = float(quintile_cuts[1])
    calibration["combined_conf_q60"] = float(quintile_cuts[2])
    calibration["combined_conf_q80_quintile"] = float(quintile_cuts[3])
    return conf, pair_q, calibration


def construct_weights(common, conf, pair_q):
    ew = np.ones(N) / N
    conf_by_date = conf.set_index("date")
    names = [
        "EW8", "PAIRWISE_SOFT", "PAIRWISE_TOP3", "PAIRWISE_BOTTOM2_VETO",
        "CONF_SOFT", "CONF_HALF_TOP3", "CONT_HALF_TOP3", "CONF_BOTTOM2_VETO",
    ]
    frames = {name: nsfs.empty_weights(common.index) for name in names}

    for i, dt in enumerate(common.index):
        q = pair_q.loc[dt].to_numpy(dtype=float)
        pair_soft = q / q.sum() if q.sum() > 0 else ew.copy()
        top3_idx = np.argsort(q)[-3:]
        top3 = np.zeros(N)
        top3[top3_idx] = 1 / 3
        half_top3 = ew + 0.5 * (top3 - ew)
        bottom2 = np.argsort(q)[:2]
        veto = np.zeros(N)
        keep = [j for j in range(N) if j not in set(bottom2)]
        veto[keep] = 1 / 6

        if dt in conf_by_date.index:
            row = conf_by_date.loc[dt]
            high = bool(row.high_confidence)
            intensity = float(row.intensity)
        else:
            high = False
            intensity = 0.0

        vals = {
            "EW8": ew,
            "PAIRWISE_SOFT": pair_soft,
            "PAIRWISE_TOP3": top3,
            "PAIRWISE_BOTTOM2_VETO": veto,
            "CONF_SOFT": pair_soft if high else ew,
            "CONF_HALF_TOP3": half_top3 if high else ew,
            "CONT_HALF_TOP3": ew + 0.5 * intensity * (top3 - ew),
            "CONF_BOTTOM2_VETO": veto if high else ew,
        }
        for name, w in vals.items():
            frames[name].iloc[i] = w

    weights = {}
    for u in UNIVERSES:
        for name, frame in frames.items():
            weights[(name, u)] = frame.copy()
    return weights


def confidence_diagnostics(mats, conf):
    rows = []
    for u in UNIVERSES:
        w = mats[u]
        for r in conf.itertuples(index=False):
            if r.period not in PERIODS or r.date not in w.index:
                continue
            q = np.array([getattr(r, f"q_{fac}") for fac in FACTORS], dtype=float)
            realized = w.loc[r.date].to_numpy(dtype=float)
            ew_ret = float(realized.mean())
            top3 = np.argsort(q)[-3:]
            bottom2 = set(np.argsort(q)[:2].tolist())
            keep = [j for j in range(N) if j not in bottom2]
            rows.append({
                "date": r.date,
                "period": r.period,
                "universe": u,
                "confidence_quintile": int(r.confidence_quintile),
                "combined_conf": float(r.combined_conf),
                "rank_ic": spearman(q, realized),
                "top3_minus_ew8": float(realized[top3].mean() - ew_ret),
                "bottom2_veto_minus_ew8": float(realized[keep].mean() - ew_ret),
            })
    raw = pd.DataFrame(rows)
    agg = raw.groupby(["period", "confidence_quintile"], as_index=False).agg(
        n=("rank_ic", "size"),
        median_rank_ic=("rank_ic", "median"),
        mean_rank_ic=("rank_ic", "mean"),
        mean_top3_minus_ew8=("top3_minus_ew8", "mean"),
        median_top3_minus_ew8=("top3_minus_ew8", "median"),
        mean_bottom2_veto_minus_ew8=("bottom2_veto_minus_ew8", "mean"),
        median_bottom2_veto_minus_ew8=("bottom2_veto_minus_ew8", "median"),
    )
    comp_rows = []
    for p in PERIODS:
        q = raw[raw.period.eq(p)]
        hi = q[q.confidence_quintile.eq(5)]
        lo = q[q.confidence_quintile.le(4)]
        comp_rows.append({
            "period": p,
            "q5_median_rank_ic": float(hi.rank_ic.median()) if len(hi) else np.nan,
            "q1_4_median_rank_ic": float(lo.rank_ic.median()) if len(lo) else np.nan,
            "q5_mean_top3_minus_ew8": float(hi.top3_minus_ew8.mean()) if len(hi) else np.nan,
            "q1_4_mean_top3_minus_ew8": float(lo.top3_minus_ew8.mean()) if len(lo) else np.nan,
            "q5_mean_bottom2_veto_minus_ew8": float(hi.bottom2_veto_minus_ew8.mean()) if len(hi) else np.nan,
            "q1_4_mean_bottom2_veto_minus_ew8": float(lo.bottom2_veto_minus_ew8.mean()) if len(lo) else np.nan,
        })
    comp = pd.DataFrame(comp_rows)
    return raw, agg, comp


def evaluate(mats, weights):
    ret_rows, perf_rows = [], []
    for (strategy, u), ww in weights.items():
        r = mats[u].reindex(ww.index)
        gross = pd.Series(np.sum(ww.to_numpy(dtype=float) * r.to_numpy(dtype=float), axis=1), index=ww.index)
        turnover = 0.5 * ww.diff().abs().sum(axis=1)
        turnover.iloc[0] = 0.0
        for cost in COSTS:
            net = gross - (cost / 10000) * turnover
            for dt in ww.index:
                p = nsfs.period_of_date(dt)
                if p is not None:
                    ret_rows.append({
                        "date": dt, "period": p, "universe": u, "strategy": strategy,
                        "cost_bps": cost, "gross_return": gross.loc[dt], "net_return": net.loc[dt],
                        "turnover": turnover.loc[dt],
                    })
            for p in PERIODS:
                mask = np.array([nsfs.period_of_date(d) == p for d in ww.index])
                x = net[mask]
                t = turnover[mask]
                perf_rows.append({
                    "period": p, "universe": u, "strategy": strategy, "cost_bps": cost,
                    "n_5d": len(x), "sharpe": nsfs.ann_sharpe(x), "cagr": nsfs.cagr_5d(x),
                    "max_drawdown": nsfs.max_drawdown(x),
                    "annualized_weight_turnover": float(t.mean() * 252 / 5) if len(t) else np.nan,
                })
    return pd.DataFrame(ret_rows), pd.DataFrame(perf_rows)


def summarize_economic(perf):
    p10 = perf[perf.cost_bps.eq(10)].copy()
    ew = p10[p10.strategy.eq("EW8")][["period", "universe", "sharpe", "cagr", "max_drawdown"]].rename(
        columns={"sharpe": "ew_sharpe", "cagr": "ew_cagr", "max_drawdown": "ew_mdd"}
    )
    z = p10.merge(ew, on=["period", "universe"], how="left")
    z["delta_sharpe_vs_ew8"] = z.sharpe - z.ew_sharpe
    z["delta_cagr_vs_ew8"] = z.cagr - z.ew_cagr
    z["delta_mdd_vs_ew8"] = z.max_drawdown - z.ew_mdd
    rows = []
    for strategy in sorted(z.strategy.unique()):
        if strategy == "EW8":
            continue
        for p in PERIODS:
            q = z[(z.strategy.eq(strategy)) & (z.period.eq(p))]
            rows.append({
                "strategy": strategy, "period": p,
                "median_delta_sharpe_vs_ew8": float(q.delta_sharpe_vs_ew8.median()),
                "positive_universes_vs_ew8": int((q.delta_sharpe_vs_ew8 > 0).sum()),
                "median_delta_cagr_vs_ew8": float(q.delta_cagr_vs_ew8.median()),
                "median_delta_mdd_vs_ew8": float(q.delta_mdd_vs_ew8.median()),
                "median_annualized_turnover": float(q.annualized_weight_turnover.median()),
            })
    out = pd.DataFrame(rows)
    gates = []
    for strategy in sorted(out.strategy.unique()):
        a = out[(out.strategy.eq(strategy)) & (out.period.eq("VAL_2020_2022"))].iloc[0]
        b = out[(out.strategy.eq(strategy)) & (out.period.eq("CONF_2023_2024"))].iloc[0]
        passed = bool(
            a.median_delta_sharpe_vs_ew8 > 0 and a.positive_universes_vs_ew8 >= 4
            and b.median_delta_sharpe_vs_ew8 > 0 and b.positive_universes_vs_ew8 >= 4
        )
        gates.append({"strategy": strategy, "primary_style_gate": passed})
    return out.merge(pd.DataFrame(gates), on="strategy", how="left")


def activation_summary(conf):
    rows = []
    for p in PERIODS:
        q = conf[conf.period.eq(p)]
        rows.append({
            "period": p,
            "n_dates": len(q),
            "high_confidence_share": float(q.high_confidence.mean()) if len(q) else np.nan,
            "mean_continuous_intensity": float(q.intensity.mean()) if len(q) else np.nan,
            "median_combined_conf": float(q.combined_conf.median()) if len(q) else np.nan,
        })
    return pd.DataFrame(rows)


def diagnostic_gate(comp):
    checks = []
    for p in ["VAL_2020_2022", "CONF_2023_2024"]:
        r = comp[comp.period.eq(p)].iloc[0]
        rank_better = bool(r.q5_median_rank_ic > r.q1_4_median_rank_ic)
        top3_better = bool(r.q5_mean_top3_minus_ew8 > r.q1_4_mean_top3_minus_ew8 and r.q5_mean_top3_minus_ew8 > 0)
        veto_better = bool(r.q5_mean_bottom2_veto_minus_ew8 > r.q1_4_mean_bottom2_veto_minus_ew8 and r.q5_mean_bottom2_veto_minus_ew8 > 0)
        checks.append(rank_better and (top3_better or veto_better))
    return bool(all(checks))


def make_report(econ, comp, activation, diag_ok):
    abstention = ["CONF_SOFT", "CONF_HALF_TOP3", "CONT_HALF_TOP3", "CONF_BOTTOM2_VETO"]
    econ_passers = [s for s in abstention if bool(econ[econ.strategy.eq(s)].primary_style_gate.iloc[0])]
    if diag_ok and econ_passers:
        classification = "CONFIDENCE_VALID"
    elif diag_ok:
        classification = "DIAGNOSTIC_ONLY"
    elif econ_passers:
        classification = "IMPLEMENTATION_ONLY"
    else:
        classification = "REJECT"

    def er(s, p):
        return econ[(econ.strategy.eq(s)) & (econ.period.eq(p))].iloc[0]

    lines = [
        "# Pairwise Ranking + Abstention / Confidence Sizing", "",
        "This follow-up is explicitly post-hoc exploratory. The ranking model remains frozen from Discovery 2016–19, and confidence thresholds are calibrated only from Discovery confidence distributions.", "",
        f"## Classification: **{classification}**", "",
        f"- Confidence diagnostic gate: {diag_ok}",
        f"- Abstention strategies passing the primary-style economic gate: {', '.join(econ_passers) if econ_passers else 'None'}", "",
        "## Does confidence identify better ranking periods?", "",
    ]
    for r in comp.itertuples(index=False):
        lines.append(
            f"- {r.period}: Q5 rank IC {r.q5_median_rank_ic:+.3f} vs Q1-4 {r.q1_4_median_rank_ic:+.3f}; "
            f"Q5 top3-EW8 {r.q5_mean_top3_minus_ew8:+.3%} vs {r.q1_4_mean_top3_minus_ew8:+.3%}; "
            f"Q5 bottom2-veto-EW8 {r.q5_mean_bottom2_veto_minus_ew8:+.3%} vs {r.q1_4_mean_bottom2_veto_minus_ew8:+.3%}"
        )

    lines += ["", "## Confidence activation", ""]
    for r in activation.itertuples(index=False):
        lines.append(
            f"- {r.period}: high-confidence dates {r.high_confidence_share:.1%}; mean continuous intensity {r.mean_continuous_intensity:.3f}; median combined confidence {r.median_combined_conf:+.3f}"
        )

    lines += ["", "## Economic results at 10 bps", ""]
    for s in ["PAIRWISE_SOFT", "PAIRWISE_TOP3", "PAIRWISE_BOTTOM2_VETO"] + abstention:
        v, c, y25, y26 = er(s, "VAL_2020_2022"), er(s, "CONF_2023_2024"), er(s, "STRESS_2025"), er(s, "STRESS_2026")
        lines.append(
            f"- **{s}** — gate={bool(v.primary_style_gate)}; VAL ΔSharpe {v.median_delta_sharpe_vs_ew8:+.3f} ({int(v.positive_universes_vs_ew8)}/6), "
            f"CONF {c.median_delta_sharpe_vs_ew8:+.3f} ({int(c.positive_universes_vs_ew8)}/6), 2025 {y25.median_delta_sharpe_vs_ew8:+.3f}, 2026 {y26.median_delta_sharpe_vs_ew8:+.3f}; "
            f"median annualized turnover VAL/CONF {v.median_annualized_turnover:.2f}/{c.median_annualized_turnover:.2f}"
        )

    lines += ["", "## Interpretation", ""]
    if classification == "CONFIDENCE_VALID":
        lines.append("The ex-ante pairwise probability geometry identifies periods when ranking quality is materially better, and abstention converts that diagnostic into a more robust economic implementation. Because this experiment was motivated by already-inspected 2020–24 results, treat it as a strong exploratory lead requiring future untouched validation.")
    elif classification == "DIAGNOSTIC_ONLY":
        lines.append("Confidence is informative about ranking quality, but the signal remains too weak to justify economically meaningful active factor risk. Keep confidence as a monitoring variable rather than a selector.")
    elif classification == "IMPLEMENTATION_ONLY":
        lines.append("At least one abstention rule improves economics, but confidence does not cleanly identify better ranking periods. Treat the gain as path-dependent implementation evidence rather than validated signal confidence.")
    else:
        lines.append("The frozen pairwise model's internal confidence geometry does not reliably separate good ranking periods from bad ones, and abstention does not rescue the economic selection problem. Do not tune thresholds or add confidence features on the same sample.")
    return "\n".join(lines)


def main():
    f, mats, common = nsfs.load_data()
    conf, pair_q, calibration = build_confidence_panel(common)
    weights = construct_weights(common, conf, pair_q)
    raw_diag, bin_diag, comp = confidence_diagnostics(mats, conf)
    ret_panel, perf = evaluate(mats, weights)
    econ = summarize_economic(perf)
    activation = activation_summary(conf)
    diag_ok = diagnostic_gate(comp)
    report = make_report(econ, comp, activation, diag_ok)

    conf.to_csv(OUT / "confidence_panel.csv", index=False, encoding="utf-8-sig")
    calibration.to_csv(OUT / "discovery_confidence_calibration.csv", index=False, encoding="utf-8-sig")
    raw_diag.to_csv(OUT / "confidence_diagnostics_raw.csv", index=False, encoding="utf-8-sig")
    bin_diag.to_csv(OUT / "confidence_quintile_diagnostics.csv", index=False, encoding="utf-8-sig")
    comp.to_csv(OUT / "q5_vs_lower_confidence.csv", index=False, encoding="utf-8-sig")
    activation.to_csv(OUT / "activation_summary.csv", index=False, encoding="utf-8-sig")
    ret_panel.to_csv(OUT / "strategy_return_panel.csv", index=False, encoding="utf-8-sig")
    perf.to_csv(OUT / "performance_by_universe.csv", index=False, encoding="utf-8-sig")
    econ.to_csv(OUT / "economic_gate_summary.csv", index=False, encoding="utf-8-sig")
    (OUT / "RESEARCH_SUMMARY.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
