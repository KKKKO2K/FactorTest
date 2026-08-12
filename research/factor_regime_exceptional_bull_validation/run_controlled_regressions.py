from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = ROOT / "research" / "factor_regime_full_state_map" / "results"
ABS = ROOT / "research" / "factor_regime_absolute_states" / "results"
REG = ROOT / "research" / "factor_regime_v1" / "results"
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

FAMILIES = ("MOMENTUM", "REVISION", "VALUE", "FLOW")
PAIRS = list(itertools.combinations(FAMILIES, 2))
MAIN_CUT = "Q33"
POST_START = pd.Timestamp("2023-01-01")
MIN_N = 80


def forward_market(market: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market.clip(lower=-0.999999))
    return np.expm1(sum(logs.shift(-i) for i in range(1, h + 1)))


def trailing_market(market: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market.clip(lower=-0.999999))
    return np.expm1(logs.rolling(h, min_periods=h).sum())


def load():
    states = pd.read_csv(FULL / "family_states_static.csv")
    states["date"] = pd.to_datetime(states.date)
    states = states[(states.cut_name == MAIN_CUT) & (states.date >= POST_START)].copy()
    breadth = pd.read_csv(ABS / "refined_breadth_panel.csv")
    breadth["date"] = pd.to_datetime(breadth.date)
    breadth = breadth[breadth.date >= POST_START].copy()
    market = pd.read_csv(REG / "market_daily_returns.csv", index_col=0)
    market.index = pd.to_datetime(market.index)
    return states, breadth, market.sort_index()


def context(market):
    fwd20 = forward_market(market, 20)
    tr20 = trailing_market(market, 20)
    tr60 = trailing_market(market, 60)
    return fwd20, tr20, tr60


def add_context(z: pd.DataFrame, u: str, fwd20, tr20, tr60):
    x = z.copy()
    x["fwd20"] = x.date.map(fwd20[u])
    x["trail20"] = x.date.map(tr20[u])
    x["trail60"] = x.date.map(tr60[u])
    x["d25"] = (x.date.dt.year == 2025).astype(float)
    x["d26"] = (x.date.dt.year == 2026).astype(float)
    return x


def linear_combo(model, names, weights):
    params = model.params
    cov = model.cov_params()
    w = np.zeros(len(params))
    for name, val in zip(names, weights):
        if name in params.index:
            w[params.index.get_loc(name)] = val
    est = float(w @ params.to_numpy())
    var = float(w @ cov.to_numpy() @ w)
    se = np.sqrt(max(var, 0.0))
    t = est / se if se > 0 else np.nan
    return est, se, t


def fit_hac(y, X):
    q = pd.concat([y.rename("y"), X], axis=1).dropna()
    if len(q) < MIN_N:
        return None, q
    model = sm.OLS(q.y, sm.add_constant(q.drop(columns="y"), has_constant="add")).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    return model, q


def pair_regressions(states, market):
    fwd20, tr20, tr60 = context(market)
    rows = []
    for fa, fb in PAIRS:
        a = states[states.family == fa][["date", "universe", "state6"]].rename(columns={"state6": "state_a"})
        b = states[states.family == fb][["date", "universe", "state6"]].rename(columns={"state6": "state_b"})
        x = a.merge(b, on=["date", "universe"], how="inner")
        for u, g in x.groupby("universe"):
            if u not in market.columns:
                continue
            z = add_context(g, u, fwd20, tr20, tr60)
            z["sig"] = ((z.state_a == "W+") & (z.state_b == "W+")).astype(float)
            z["sig25"] = z.sig * z.d25
            z["sig26"] = z.sig * z.d26
            X = z[["sig", "trail20", "trail60", "d25", "d26", "sig25", "sig26"]]
            model, q = fit_hac(z.fwd20, X)
            if model is None or q.sig.sum() < 8:
                continue
            bnorm, sen, tn = linear_combo(model, ["sig"], [1.0])
            b25, se25, t25 = linear_combo(model, ["sig", "sig25"], [1.0, 1.0])
            b26, se26, t26 = linear_combo(model, ["sig", "sig26"], [1.0, 1.0])
            rows.append({
                "universe": u, "family_pair": f"{fa}_X_{fb}", "n": len(q), "n_signal": int(q.sig.sum()),
                "beta_2023_24": bnorm, "se_2023_24": sen, "t_2023_24": tn,
                "beta_2025": b25, "se_2025": se25, "t_2025": t25,
                "beta_2026": b26, "se_2026": se26, "t_2026": t26,
                "interaction_2025": float(model.params.get("sig25", np.nan)), "interaction_2025_t": float(model.tvalues.get("sig25", np.nan)),
                "interaction_2026": float(model.params.get("sig26", np.nan)), "interaction_2026_t": float(model.tvalues.get("sig26", np.nan)),
                "trail20_beta": float(model.params.get("trail20", np.nan)), "trail60_beta": float(model.params.get("trail60", np.nan)),
                "r2": float(model.rsquared),
            })
    return pd.DataFrame(rows)


def breadth_regressions(breadth, market):
    fwd20, tr20, tr60 = context(market)
    rows = []
    for u, g in breadth.groupby("universe"):
        if u not in market.columns:
            continue
        for v in ["RELATIVE_WORKING_BREADTH", "ABS_CONFIRMED_BREADTH", "DEFENSIVE_WORKING_BREADTH"]:
            if v not in g.columns:
                continue
            z = add_context(g[["date", "universe", v]], u, fwd20, tr20, tr60)
            # Effect is reported per +25 percentage-point breadth, not per full 0->1 change.
            z["b25pp"] = z[v] / 0.25
            z["b25pp_x25"] = z.b25pp * z.d25
            z["b25pp_x26"] = z.b25pp * z.d26
            X = z[["b25pp", "trail20", "trail60", "d25", "d26", "b25pp_x25", "b25pp_x26"]]
            model, q = fit_hac(z.fwd20, X)
            if model is None:
                continue
            bnorm, sen, tn = linear_combo(model, ["b25pp"], [1.0])
            b25, se25, t25 = linear_combo(model, ["b25pp", "b25pp_x25"], [1.0, 1.0])
            b26, se26, t26 = linear_combo(model, ["b25pp", "b25pp_x26"], [1.0, 1.0])
            rows.append({
                "universe": u, "state": v, "n": len(q),
                "beta25pp_2023_24": bnorm, "t_2023_24": tn,
                "beta25pp_2025": b25, "t_2025": t25,
                "beta25pp_2026": b26, "t_2026": t26,
                "interaction_2025": float(model.params.get("b25pp_x25", np.nan)), "interaction_2025_t": float(model.tvalues.get("b25pp_x25", np.nan)),
                "interaction_2026": float(model.params.get("b25pp_x26", np.nan)), "interaction_2026_t": float(model.tvalues.get("b25pp_x26", np.nan)),
                "r2": float(model.rsquared),
            })
    return pd.DataFrame(rows)


def pct(x):
    return "NA" if pd.isna(x) else f"{x:+.2%}"


def write_summary(pair, breadth):
    lines = [
        "# Continuous Market-Strength Controlled Regressions", "",
        "Sample: 2023 onward only. Baseline regime is 2023-2024; 2025 and 2026 have separate level and signal-interaction dummies.",
        "Controls: trailing 20D and trailing 60D same-universe market return. Outcome: next 20D same-universe market return.",
        "Standard errors: HAC/Newey-West with 3 lags, reflecting approximately four overlapping 5D state observations in a 20D forward return.",
        "W+/W+ pair coefficients are incremental versus all other pair states after controls. Breadth coefficients are per +25 percentage points.", "",
        "## W+/W+ pair effect after continuous controls", "",
    ]
    for u in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"]:
        z = pair[pair.universe == u]
        if z.empty:
            continue
        lines.append(
            f"- {u}: median across {len(z)} pairs — 2023-24 {pct(z.beta_2023_24.median())}; "
            f"2025 {pct(z.beta_2025.median())}; 2026 {pct(z.beta_2026.median())}. "
            f"Positive pairs: {(z.beta_2023_24 > 0).sum()}/{len(z)}, {(z.beta_2025 > 0).sum()}/{len(z)}, {(z.beta_2026 > 0).sum()}/{len(z)}."
        )
        for _, r in z.sort_values("family_pair").iterrows():
            lines.append(
                f"  - {r.family_pair}: 23-24 {pct(r.beta_2023_24)} (t={r.t_2023_24:+.2f}); "
                f"2025 {pct(r.beta_2025)} (t={r.t_2025:+.2f}); 2026 {pct(r.beta_2026)} (t={r.t_2026:+.2f})"
            )
    lines += ["", "## Breadth effect after continuous controls", ""]
    for u in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"]:
        z = breadth[breadth.universe == u]
        if z.empty:
            continue
        for _, r in z.iterrows():
            lines.append(
                f"- {u} {r.state} per +25pp: 23-24 {pct(r.beta25pp_2023_24)} (t={r.t_2023_24:+.2f}); "
                f"2025 {pct(r.beta25pp_2025)} (t={r.t_2025:+.2f}); 2026 {pct(r.beta25pp_2026)} (t={r.t_2026:+.2f})"
            )
    lines += ["", "## Guardrails", "",
              "- These are post-discovery controlled diagnostics, not untouched OOS estimates.",
              "- The interaction structure tests regime dependence; it does not prove causality.",
              "- Prefer consistency across pairs, cap tiers, calendar splits, and the earlier stratified same-prior60 comparisons over isolated t-statistics.", ""]
    return "\n".join(lines) + "\n"


def main():
    states, breadth, market = load()
    pair = pair_regressions(states, market)
    br = breadth_regressions(breadth, market)
    pair.to_csv(OUT / "controlled_pair_regressions.csv", index=False, encoding="utf-8-sig")
    br.to_csv(OUT / "controlled_breadth_regressions.csv", index=False, encoding="utf-8-sig")
    (OUT / "CONTROLLED_REGRESSION_SUMMARY.md").write_text(write_summary(pair, br), encoding="utf-8")
    print(f"pair regressions: {len(pair)}")
    print(f"breadth regressions: {len(br)}")


if __name__ == "__main__":
    main()
