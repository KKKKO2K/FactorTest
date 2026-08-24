from __future__ import annotations

from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd

import run_pairwise_abstention as pa

nsfs = pa.nsfs
FACTORS = pa.FACTORS
UNIVERSES = pa.UNIVERSES
PERIODS = pa.PERIODS
N = len(FACTORS)
OUT = Path(__file__).resolve().parent / "results_epistemic"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 20260824
N_MODELS = 100
BLOCK = 8


def discovery_state_training(common):
    feats = nsfs.common_features(common)
    arr = common.to_numpy(dtype=float)
    states = []
    for i, feat in feats:
        if i + 1 >= len(common) or common.index[i + 1].year > 2019:
            continue
        nxt = arr[i + 1]
        X, y = [], []
        for a, b in combinations(range(N), 2):
            X.append(feat[a] - feat[b])
            y.append(float(nxt[a] > nxt[b]))
        states.append((common.index[i + 1], np.asarray(X), np.asarray(y)))
    return states, feats


def moving_block_sample(n, rng):
    chosen = []
    max_start = max(n - BLOCK + 1, 1)
    while len(chosen) < n:
        start = int(rng.integers(0, max_start))
        chosen.extend(range(start, min(start + BLOCK, n)))
    return chosen[:n]


def fit_ensemble(common):
    states, feats = discovery_state_training(common)
    rng = np.random.default_rng(SEED)
    models = []
    n = len(states)
    for _ in range(N_MODELS):
        idx = moving_block_sample(n, rng)
        X = np.vstack([states[j][1] for j in idx])
        y = np.concatenate([states[j][2] for j in idx])
        beta, mean, std = nsfs.fit_logistic(X, y)
        models.append((beta, mean, std))
    return models, feats


def model_scores(feat, model):
    beta, mean, std = model
    score = np.zeros(N)
    votes = np.zeros((N, N), dtype=bool)
    for a, b in combinations(range(N), 2):
        z = np.r_[1.0, (feat[a] - feat[b] - mean) / std]
        p = float(1 / (1 + np.exp(-np.clip(z @ beta, -30, 30))))
        score[a] += p
        score[b] += 1 - p
        votes[a, b] = p > 0.5
        votes[b, a] = p < 0.5
    return score / (N - 1), votes


def jaccard(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if (a | b) else 1.0


def build_epistemic_panel(common):
    models, feats = fit_ensemble(common)
    rows = []
    qdf = pd.DataFrame(np.ones((len(common), N)) / N, index=common.index, columns=FACTORS)

    for i, feat in feats:
        if i + 1 >= len(common):
            continue
        ti = i + 1
        dt = common.index[ti]
        qs = []
        vote_cube = []
        top3_sets = []
        top1s = []
        for model in models:
            q, votes = model_scores(feat, model)
            qs.append(q)
            vote_cube.append(votes)
            top3_sets.append(tuple(np.argsort(q)[-3:]))
            top1s.append(int(np.argmax(q)))
        Q = np.vstack(qs)
        mean_q = Q.mean(axis=0)
        qdf.iloc[ti] = mean_q
        ens_top3 = tuple(np.argsort(mean_q)[-3:])
        ens_top1 = int(np.argmax(mean_q))

        vote_agreements = []
        V = np.stack(vote_cube, axis=0)
        for a, b in combinations(range(N), 2):
            share = float(V[:, a, b].mean())
            vote_agreements.append(2 * abs(share - 0.5))

        rows.append({
            "date": dt,
            "pair_vote_agreement": float(np.mean(vote_agreements)),
            "top3_jaccard": float(np.mean([jaccard(s, ens_top3) for s in top3_sets])),
            "top1_vote_share": float(np.mean(np.asarray(top1s) == ens_top1)),
            "score_model_sd": float(np.mean(np.std(Q, axis=0, ddof=1))),
            **{f"q_{fac}": float(mean_q[j]) for j, fac in enumerate(FACTORS)},
        })

    panel = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    metrics = ["pair_vote_agreement", "top3_jaccard", "top1_vote_share", "score_model_sd"]
    disc = panel[panel.date.dt.year <= 2019].copy()
    calib_rows = []
    for col in metrics:
        mu = float(disc[col].mean())
        sd = float(disc[col].std(ddof=1))
        if not np.isfinite(sd) or sd <= 1e-12:
            sd = 1.0
        sign = -1.0 if col == "score_model_sd" else 1.0
        panel[f"z_{col}"] = sign * (panel[col] - mu) / sd
        calib_rows.append({"metric": col, "discovery_mean": mu, "discovery_std": sd})
    panel["epi_conf"] = panel[[f"z_{c}" for c in metrics]].mean(axis=1)

    disc_vals = panel.loc[panel.date.dt.year <= 2019, "epi_conf"].dropna().to_numpy(dtype=float)
    sorted_disc = np.sort(disc_vals)
    q80 = float(np.quantile(disc_vals, 0.80))
    cuts = np.quantile(disc_vals, [0.20, 0.40, 0.60, 0.80])
    panel["disc_percentile"] = panel.epi_conf.map(lambda v: float(np.searchsorted(sorted_disc, v, side="right") / len(sorted_disc)))
    panel["intensity"] = np.clip(2 * panel.disc_percentile - 1, 0, 1)
    panel["high_confidence"] = panel.epi_conf > q80
    panel["confidence_quintile"] = panel.epi_conf.map(lambda v: int(np.searchsorted(cuts, v, side="right") + 1))
    panel["period"] = panel.date.map(nsfs.period_of_date)

    calib = pd.DataFrame(calib_rows)
    calib["epi_conf_q80"] = q80
    calib["epi_conf_q20"] = float(cuts[0])
    calib["epi_conf_q40"] = float(cuts[1])
    calib["epi_conf_q60"] = float(cuts[2])
    calib["epi_conf_q80_quintile"] = float(cuts[3])
    return panel, qdf, calib


def construct_weights(common, panel, qdf):
    ew = np.ones(N) / N
    by_date = panel.set_index("date")
    names = [
        "EW8", "ENS_SOFT", "ENS_TOP3", "ENS_BOTTOM2_VETO",
        "EPI_CONF_SOFT", "EPI_CONF_HALF_TOP3", "EPI_CONT_HALF_TOP3", "EPI_CONF_BOTTOM2_VETO",
    ]
    frames = {n: nsfs.empty_weights(common.index) for n in names}

    for i, dt in enumerate(common.index):
        q = qdf.loc[dt].to_numpy(dtype=float)
        soft = q / q.sum() if q.sum() > 0 else ew.copy()
        top3_idx = np.argsort(q)[-3:]
        top3 = np.zeros(N); top3[top3_idx] = 1 / 3
        half = ew + 0.5 * (top3 - ew)
        bottom2 = set(np.argsort(q)[:2].tolist())
        keep = [j for j in range(N) if j not in bottom2]
        veto = np.zeros(N); veto[keep] = 1 / 6
        if dt in by_date.index:
            r = by_date.loc[dt]
            high = bool(r.high_confidence)
            intensity = float(r.intensity)
        else:
            high = False
            intensity = 0.0
        vals = {
            "EW8": ew,
            "ENS_SOFT": soft,
            "ENS_TOP3": top3,
            "ENS_BOTTOM2_VETO": veto,
            "EPI_CONF_SOFT": soft if high else ew,
            "EPI_CONF_HALF_TOP3": half if high else ew,
            "EPI_CONT_HALF_TOP3": ew + 0.5 * intensity * (top3 - ew),
            "EPI_CONF_BOTTOM2_VETO": veto if high else ew,
        }
        for name, value in vals.items():
            frames[name].iloc[i] = value

    weights = {}
    for u in UNIVERSES:
        for name, frame in frames.items():
            weights[(name, u)] = frame.copy()
    return weights


def confidence_diagnostics(mats, panel):
    rows = []
    for u in UNIVERSES:
        w = mats[u]
        for r in panel.itertuples(index=False):
            if r.period not in PERIODS or r.date not in w.index:
                continue
            q = np.array([getattr(r, f"q_{fac}") for fac in FACTORS], dtype=float)
            realized = w.loc[r.date].to_numpy(dtype=float)
            ewret = float(realized.mean())
            top3 = np.argsort(q)[-3:]
            bottom2 = set(np.argsort(q)[:2].tolist())
            keep = [j for j in range(N) if j not in bottom2]
            rows.append({
                "date": r.date, "period": r.period, "universe": u,
                "confidence_quintile": int(r.confidence_quintile),
                "rank_ic": pa.spearman(q, realized),
                "top3_minus_ew8": float(realized[top3].mean() - ewret),
                "bottom2_veto_minus_ew8": float(realized[keep].mean() - ewret),
            })
    raw = pd.DataFrame(rows)
    agg = raw.groupby(["period", "confidence_quintile"], as_index=False).agg(
        n=("rank_ic", "size"), median_rank_ic=("rank_ic", "median"), mean_rank_ic=("rank_ic", "mean"),
        mean_top3_minus_ew8=("top3_minus_ew8", "mean"), median_top3_minus_ew8=("top3_minus_ew8", "median"),
        mean_bottom2_veto_minus_ew8=("bottom2_veto_minus_ew8", "mean"), median_bottom2_veto_minus_ew8=("bottom2_veto_minus_ew8", "median"),
    )
    comps = []
    for p in PERIODS:
        q = raw[raw.period.eq(p)]
        hi, lo = q[q.confidence_quintile.eq(5)], q[q.confidence_quintile.le(4)]
        comps.append({
            "period": p,
            "q5_median_rank_ic": float(hi.rank_ic.median()) if len(hi) else np.nan,
            "q1_4_median_rank_ic": float(lo.rank_ic.median()) if len(lo) else np.nan,
            "q5_mean_top3_minus_ew8": float(hi.top3_minus_ew8.mean()) if len(hi) else np.nan,
            "q1_4_mean_top3_minus_ew8": float(lo.top3_minus_ew8.mean()) if len(lo) else np.nan,
            "q5_mean_bottom2_veto_minus_ew8": float(hi.bottom2_veto_minus_ew8.mean()) if len(hi) else np.nan,
            "q1_4_mean_bottom2_veto_minus_ew8": float(lo.bottom2_veto_minus_ew8.mean()) if len(lo) else np.nan,
        })
    return raw, agg, pd.DataFrame(comps)


def diag_gate(comp):
    out = []
    for p in ["VAL_2020_2022", "CONF_2023_2024"]:
        r = comp[comp.period.eq(p)].iloc[0]
        rank_better = r.q5_median_rank_ic > r.q1_4_median_rank_ic
        top_better = r.q5_mean_top3_minus_ew8 > 0 and r.q5_mean_top3_minus_ew8 > r.q1_4_mean_top3_minus_ew8
        veto_better = r.q5_mean_bottom2_veto_minus_ew8 > 0 and r.q5_mean_bottom2_veto_minus_ew8 > r.q1_4_mean_bottom2_veto_minus_ew8
        out.append(bool(rank_better and (top_better or veto_better)))
    return bool(all(out))


def activation(panel):
    rows = []
    for p in PERIODS:
        q = panel[panel.period.eq(p)]
        rows.append({
            "period": p,
            "high_confidence_share": float(q.high_confidence.mean()) if len(q) else np.nan,
            "mean_continuous_intensity": float(q.intensity.mean()) if len(q) else np.nan,
            "median_epi_conf": float(q.epi_conf.median()) if len(q) else np.nan,
        })
    return pd.DataFrame(rows)


def report(econ, comp, act, diag_ok):
    strategies = ["EPI_CONF_SOFT", "EPI_CONF_HALF_TOP3", "EPI_CONT_HALF_TOP3", "EPI_CONF_BOTTOM2_VETO"]
    passers = [s for s in strategies if bool(econ[econ.strategy.eq(s)].primary_style_gate.iloc[0])]
    if diag_ok and passers:
        cls = "EPISTEMIC_CONFIDENCE_VALID"
    elif diag_ok:
        cls = "DIAGNOSTIC_ONLY"
    elif passers:
        cls = "IMPLEMENTATION_ONLY"
    else:
        cls = "REJECT"

    def rr(s, p):
        return econ[(econ.strategy.eq(s)) & (econ.period.eq(p))].iloc[0]

    lines = [
        "# Stage 2 — Bootstrap Epistemic Confidence", "",
        "This stage is post-hoc exploratory. All model fitting, bootstrap resampling, and confidence calibration use Discovery 2016–19 only.", "",
        f"## Classification: **{cls}**", "",
        f"- Diagnostic gate: {diag_ok}",
        f"- Economic passers: {', '.join(passers) if passers else 'None'}", "",
        "## Q5 epistemic confidence versus lower-confidence dates", "",
    ]
    for r in comp.itertuples(index=False):
        lines.append(
            f"- {r.period}: rank IC Q5 {r.q5_median_rank_ic:+.3f} vs Q1-4 {r.q1_4_median_rank_ic:+.3f}; "
            f"top3-EW8 {r.q5_mean_top3_minus_ew8:+.3%} vs {r.q1_4_mean_top3_minus_ew8:+.3%}; "
            f"bottom2-veto-EW8 {r.q5_mean_bottom2_veto_minus_ew8:+.3%} vs {r.q1_4_mean_bottom2_veto_minus_ew8:+.3%}"
        )
    lines += ["", "## Activation", ""]
    for r in act.itertuples(index=False):
        lines.append(f"- {r.period}: high-confidence {r.high_confidence_share:.1%}; mean intensity {r.mean_continuous_intensity:.3f}; median EPI_CONF {r.median_epi_conf:+.3f}")
    lines += ["", "## Economic results at 10 bps", ""]
    for s in ["ENS_SOFT", "ENS_TOP3", "ENS_BOTTOM2_VETO"] + strategies:
        v, c, y25, y26 = rr(s, "VAL_2020_2022"), rr(s, "CONF_2023_2024"), rr(s, "STRESS_2025"), rr(s, "STRESS_2026")
        lines.append(
            f"- **{s}** — gate={bool(v.primary_style_gate)}; VAL ΔSharpe {v.median_delta_sharpe_vs_ew8:+.3f} ({int(v.positive_universes_vs_ew8)}/6), "
            f"CONF {c.median_delta_sharpe_vs_ew8:+.3f} ({int(c.positive_universes_vs_ew8)}/6), 2025 {y25.median_delta_sharpe_vs_ew8:+.3f}, 2026 {y26.median_delta_sharpe_vs_ew8:+.3f}"
        )
    lines += ["", "## Decision", ""]
    if cls == "REJECT":
        lines.append("Bootstrap model agreement also fails to identify reliably better ranking periods or rescue active factor selection. Per protocol, stop confidence engineering on this historical sample rather than changing bootstrap/block/threshold choices.")
    else:
        lines.append("Epistemic model stability contains some useful information. Because the experiment is post-hoc, any survivor remains a candidate for future untouched validation rather than a production rule.")
    return "\n".join(lines)


def main():
    _, mats, common = nsfs.load_data()
    panel, qdf, calib = build_epistemic_panel(common)
    weights = construct_weights(common, panel, qdf)
    raw, bins, comp = confidence_diagnostics(mats, panel)
    ret, perf = pa.evaluate(mats, weights)
    econ = pa.summarize_economic(perf)
    act = activation(panel)
    dg = diag_gate(comp)
    text = report(econ, comp, act, dg)

    panel.to_csv(OUT / "epistemic_confidence_panel.csv", index=False, encoding="utf-8-sig")
    calib.to_csv(OUT / "discovery_epistemic_calibration.csv", index=False, encoding="utf-8-sig")
    raw.to_csv(OUT / "diagnostics_raw.csv", index=False, encoding="utf-8-sig")
    bins.to_csv(OUT / "confidence_quintile_diagnostics.csv", index=False, encoding="utf-8-sig")
    comp.to_csv(OUT / "q5_vs_lower_confidence.csv", index=False, encoding="utf-8-sig")
    act.to_csv(OUT / "activation_summary.csv", index=False, encoding="utf-8-sig")
    ret.to_csv(OUT / "strategy_return_panel.csv", index=False, encoding="utf-8-sig")
    perf.to_csv(OUT / "performance_by_universe.csv", index=False, encoding="utf-8-sig")
    econ.to_csv(OUT / "economic_gate_summary.csv", index=False, encoding="utf-8-sig")
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
