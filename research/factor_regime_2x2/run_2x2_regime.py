from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HORIZON_DIR = ROOT / "research" / "factor_regime_horizon_robustness"
REGIME_DIR = ROOT / "research" / "factor_regime_v1"
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

SPLIT = pd.Timestamp("2023-01-01")
FWD_HORIZONS = (1, 5, 20)
STATE_STEP_DAYS = 5

SPECS = {
    "MAIN_F20_L5_20": ("FACTOR_20D", "LIQ_5D_VS_20D"),
    "ROBUST_F10_L5_20": ("FACTOR_10D", "LIQ_5D_VS_20D"),
    "ROBUST_F20_L1_20": ("FACTOR_20D", "LIQ_1D_VS_20D"),
}
SPLIT_RULES = ("MEDIAN", "EXTREME_TERCILE")
PRIMARY_UNIVERSES = ("KOSPI_ALL", "KOSDAQ")
STATE_ORDER = (
    "A_FHIGH_LHIGH",
    "B_FHIGH_LLOW",
    "C_FLOW_LHIGH",
    "D_FLOW_LLOW",
)


def forward_market(market_returns: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market_returns.clip(lower=-0.999999))
    acc = sum(logs.shift(-i) for i in range(1, h + 1))
    return np.expm1(acc)


def trailing_market(market_returns: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market_returns.clip(lower=-0.999999))
    return np.expm1(logs.rolling(h, min_periods=h).sum())


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    states = pd.read_csv(HORIZON_DIR / "results" / "horizon_state_values.csv")
    states["date"] = pd.to_datetime(states["date"])
    states = states.sort_values(["universe", "date", "predictor_type", "definition"])
    wide = (
        states.pivot_table(
            index=["date", "universe"], columns="definition", values="value", aggfunc="last"
        )
        .reset_index()
        .sort_values(["universe", "date"])
    )
    wide.columns.name = None
    market = pd.read_csv(REGIME_DIR / "results" / "market_daily_returns.csv", index_col=0)
    market.index = pd.to_datetime(market.index)
    return wide, market.sort_index()


def factor_cut_median(x: pd.Series) -> float | None:
    x = x.dropna()
    return None if len(x) < 30 or x.nunique() < 2 else float(x.median())


def tercile_cuts(x: pd.Series) -> tuple[float, float] | None:
    x = x.dropna()
    if len(x) < 30 or x.nunique() < 3:
        return None
    q1, q2 = x.quantile([1 / 3, 2 / 3]).tolist()
    if not (np.isfinite(q1) and np.isfinite(q2)):
        return None
    if q1 < q2:
        return float(q1), float(q2)
    uniq = np.sort(x.unique())
    i1 = min(len(uniq) - 2, max(0, int(math.floor((len(uniq) - 1) / 3))))
    i2 = max(i1 + 1, min(len(uniq) - 1, int(math.ceil(2 * (len(uniq) - 1) / 3))))
    return None if uniq[i1] >= uniq[i2] else (float(uniq[i1]), float(uniq[i2]))


def label_state(f_high: bool, l_high: bool) -> str:
    if f_high and l_high:
        return "A_FHIGH_LHIGH"
    if f_high:
        return "B_FHIGH_LLOW"
    if l_high:
        return "C_FLOW_LHIGH"
    return "D_FLOW_LLOW"


def assign_states(g0: pd.DataFrame, factor_def: str, liq_def: str, split_rule: str):
    g = g0[["date", "universe", factor_def, liq_def]].dropna().sort_values("date").copy()
    train = g[g.date < SPLIT]
    if len(train) < 40:
        return None
    if split_rule == "MEDIAN":
        fc, lc = factor_cut_median(train[factor_def]), factor_cut_median(train[liq_def])
        if fc is None or lc is None:
            return None
        g["factor_high"] = g[factor_def] >= fc
        g["liq_high"] = g[liq_def] >= lc
        g["state"] = [label_state(bool(fh), bool(lh)) for fh, lh in zip(g.factor_high, g.liq_high)]
        return g, {"factor_low_cut": np.nan, "factor_high_cut": fc, "liq_low_cut": np.nan, "liq_high_cut": lc}
    if split_rule == "EXTREME_TERCILE":
        ft, lt = tercile_cuts(train[factor_def]), tercile_cuts(train[liq_def])
        if ft is None or lt is None:
            return None
        fq1, fq2 = ft
        lq1, lq2 = lt
        g["factor_side"] = np.where(g[factor_def] <= fq1, "LOW", np.where(g[factor_def] >= fq2, "HIGH", "MID"))
        g["liq_side"] = np.where(g[liq_def] <= lq1, "LOW", np.where(g[liq_def] >= lq2, "HIGH", "MID"))
        g = g[(g.factor_side != "MID") & (g.liq_side != "MID")].copy()
        g["factor_high"] = g.factor_side.eq("HIGH")
        g["liq_high"] = g.liq_side.eq("HIGH")
        g["state"] = [label_state(bool(fh), bool(lh)) for fh, lh in zip(g.factor_high, g.liq_high)]
        return g, {"factor_low_cut": fq1, "factor_high_cut": fq2, "liq_low_cut": lq1, "liq_high_cut": lq2}
    raise KeyError(split_rule)


def state_rows(assigned, thresholds, spec, split_rule, universe, factor_def, liq_def, market_fwd, market_tr20):
    rows = []
    for h in FWD_HORIZONS:
        if universe not in market_fwd[h].columns:
            continue
        x = assigned.copy()
        x["fwd"] = x.date.map(market_fwd[h][universe])
        x["trailing20"] = x.date.map(market_tr20[universe]) if universe in market_tr20.columns else np.nan
        for sample, mask in (("TRAIN", x.date < SPLIT), ("OOS", x.date >= SPLIT)):
            z = x[mask & x.fwd.notna()]
            for state in STATE_ORDER:
                s = z[z.state == state]
                if len(s) < 5:
                    continue
                rows.append({
                    "sample": sample, "spec": spec, "split_rule": split_rule, "universe": universe,
                    "forward_horizon": h, "state": state, "n": len(s),
                    "mean_fwd_return": float(s.fwd.mean()), "median_fwd_return": float(s.fwd.median()),
                    "positive_share": float((s.fwd > 0).mean()),
                    "mean_trailing20_return": float(s.trailing20.mean()),
                    "median_trailing20_return": float(s.trailing20.median()),
                    "mean_factor_breadth": float(s[factor_def].mean()),
                    "mean_liquidity_breadth": float(s[liq_def].mean()), **thresholds,
                })
    return rows


def contrast_rows(quads: pd.DataFrame):
    rows = []
    keys = ["sample", "spec", "split_rule", "universe", "forward_horizon"]
    for key, g in quads.groupby(keys):
        means = g.set_index("state").mean_fwd_return.to_dict()
        ns = g.set_index("state").n.to_dict()
        if not all(s in means for s in STATE_ORDER):
            continue
        A, B, C, D = [means[s] for s in STATE_ORDER]
        contrasts = {
            "A_MINUS_D": A - D,
            "C_MINUS_B": C - B,
            "LIQ_EFFECT_WHEN_FACTOR_HIGH_A_MINUS_B": A - B,
            "LIQ_EFFECT_WHEN_FACTOR_LOW_C_MINUS_D": C - D,
            "FACTOR_EFFECT_WHEN_LIQ_HIGH_A_MINUS_C": A - C,
            "FACTOR_EFFECT_WHEN_LIQ_LOW_B_MINUS_D": B - D,
            "INTERACTION_DID": (A - B) - (C - D),
        }
        base = dict(zip(keys, key))
        for name, value in contrasts.items():
            rows.append({**base, "contrast": name, "value": float(value), "min_state_n": int(min(ns[s] for s in STATE_ORDER))})
    return rows


def transition_rows(assigned: pd.DataFrame, spec: str, universe: str):
    rows = []
    x = assigned.sort_values("date").copy()
    for sample, mask in (("TRAIN", x.date < SPLIT), ("OOS", x.date >= SPLIT)):
        z = x[mask].copy().reset_index(drop=True)
        for lag_steps in (1, 4):
            z["to_state"] = z.state.shift(-lag_steps)
            zz = z.dropna(subset=["to_state"])
            for from_state in STATE_ORDER:
                s = zz[zz.state == from_state]
                if len(s) < 5:
                    continue
                counts = s.to_state.value_counts()
                for to_state in STATE_ORDER:
                    cnt = int(counts.get(to_state, 0))
                    rows.append({
                        "sample": sample, "spec": spec, "universe": universe, "lag_steps": lag_steps,
                        "approx_trading_days": lag_steps * STATE_STEP_DAYS, "from_state": from_state,
                        "to_state": to_state, "n_from": len(s), "count": cnt, "probability": float(cnt / len(s)),
                    })
    return rows


def fmt_pct(x: float) -> str:
    return "nan" if pd.isna(x) else f"{x:+.2%}"


def order_string(g: pd.DataFrame) -> str:
    return " > ".join(g.sort_values("mean_fwd_return", ascending=False).state.str.slice(0, 1).tolist())


def get_contrast(c, sample, spec, split_rule, universe, h, name):
    z = c[(c["sample"] == sample) & (c.spec == spec) & (c.split_rule == split_rule) &
          (c.universe == universe) & (c.forward_horizon == h) & (c.contrast == name)]
    return float(z.iloc[0].value) if len(z) else np.nan


def get_transition(t, sample, spec, universe, lag, from_state, to_state):
    z = t[(t["sample"] == sample) & (t.spec == spec) & (t.universe == universe) &
          (t.lag_steps == lag) & (t.from_state == from_state) & (t.to_state == to_state)]
    return float(z.iloc[0].probability) if len(z) else np.nan


def summarize(quads, contrasts, transitions):
    lines = [
        "# Factor Breadth x Liquidity Breadth 2x2", "",
        "Primary specification: Factor breadth = trailing 20D canonical factor-spread breadth; Liquidity breadth = share of stocks whose recent 5D average trading amount exceeds the strictly preceding 20D average.",
        "Primary quadrant split: TRAIN (2016-2022) median thresholds, frozen for 2023+ OOS. Extreme-tercile corners are a robustness check.",
        "State labels: A = Factor HIGH / Liquidity HIGH; B = Factor HIGH / Liquidity LOW; C = Factor LOW / Liquidity HIGH; D = Factor LOW / Liquidity LOW.",
        "Forward market returns are same-universe cap-weighted returns over +1D/+5D/+20D. 20D forward windows overlap across 5D state dates, so inference is descriptive.",
        "Because the horizons were selected after inspecting 2023+ data, this is post-discovery validation, not untouched OOS.", "",
        "## Primary median-split results", "",
    ]
    for u in PRIMARY_UNIVERSES:
        lines += [f"### {u}", ""]
        for sample in ("TRAIN", "OOS"):
            lines.append(f"{sample}:")
            for h in FWD_HORIZONS:
                z = quads[(quads["sample"] == sample) & (quads.spec == "MAIN_F20_L5_20") &
                          (quads.split_rule == "MEDIAN") & (quads.universe == u) & (quads.forward_horizon == h)].copy()
                if z.empty:
                    continue
                m = z.set_index("state")
                vals = []
                for st in STATE_ORDER:
                    if st in m.index:
                        r = m.loc[st]
                        vals.append(f"{st[0]} {fmt_pct(r.mean_fwd_return)} (med {fmt_pct(r.median_fwd_return)}, +share {r.positive_share:.0%}, n={int(r.n)})")
                lines.append(f"- +{h}D: " + "; ".join(vals) + f"; order {order_string(z)}")
            lines.append("")
        zo = quads[(quads["sample"] == "OOS") & (quads.spec == "MAIN_F20_L5_20") &
                   (quads.split_rule == "MEDIAN") & (quads.universe == u) & (quads.forward_horizon == 20)].copy()
        if not zo.empty:
            lines.append("OOS stage context (trailing 20D -> next 20D):")
            mm = zo.set_index("state")
            for st in STATE_ORDER:
                if st in mm.index:
                    r = mm.loc[st]
                    lines.append(f"- {st[0]}: trailing {fmt_pct(r.mean_trailing20_return)} -> next {fmt_pct(r.mean_fwd_return)}")
            lines.append("")
        lines.append("Key contrasts (TRAIN -> OOS):")
        for h in (5, 20):
            ad_tr = get_contrast(contrasts, "TRAIN", "MAIN_F20_L5_20", "MEDIAN", u, h, "A_MINUS_D")
            ad_oo = get_contrast(contrasts, "OOS", "MAIN_F20_L5_20", "MEDIAN", u, h, "A_MINUS_D")
            cb_tr = get_contrast(contrasts, "TRAIN", "MAIN_F20_L5_20", "MEDIAN", u, h, "C_MINUS_B")
            cb_oo = get_contrast(contrasts, "OOS", "MAIN_F20_L5_20", "MEDIAN", u, h, "C_MINUS_B")
            di_tr = get_contrast(contrasts, "TRAIN", "MAIN_F20_L5_20", "MEDIAN", u, h, "INTERACTION_DID")
            di_oo = get_contrast(contrasts, "OOS", "MAIN_F20_L5_20", "MEDIAN", u, h, "INTERACTION_DID")
            lines.append(f"- +{h}D A-D {fmt_pct(ad_tr)} -> {fmt_pct(ad_oo)}; C-B {fmt_pct(cb_tr)} -> {fmt_pct(cb_oo)}; interaction DiD {fmt_pct(di_tr)} -> {fmt_pct(di_oo)}")
        lines.append("")
        lines.append("Transition checks for the stage interpretation (median split):")
        for lag in (1, 4):
            ca_tr = get_transition(transitions, "TRAIN", "MAIN_F20_L5_20", u, lag, "C_FLOW_LHIGH", "A_FHIGH_LHIGH")
            ca_oo = get_transition(transitions, "OOS", "MAIN_F20_L5_20", u, lag, "C_FLOW_LHIGH", "A_FHIGH_LHIGH")
            bd_tr = get_transition(transitions, "TRAIN", "MAIN_F20_L5_20", u, lag, "B_FHIGH_LLOW", "D_FLOW_LLOW")
            bd_oo = get_transition(transitions, "OOS", "MAIN_F20_L5_20", u, lag, "B_FHIGH_LLOW", "D_FLOW_LLOW")
            aa_tr = get_transition(transitions, "TRAIN", "MAIN_F20_L5_20", u, lag, "A_FHIGH_LHIGH", "A_FHIGH_LHIGH")
            aa_oo = get_transition(transitions, "OOS", "MAIN_F20_L5_20", u, lag, "A_FHIGH_LHIGH", "A_FHIGH_LHIGH")
            dd_tr = get_transition(transitions, "TRAIN", "MAIN_F20_L5_20", u, lag, "D_FLOW_LLOW", "D_FLOW_LLOW")
            dd_oo = get_transition(transitions, "OOS", "MAIN_F20_L5_20", u, lag, "D_FLOW_LLOW", "D_FLOW_LLOW")
            lines.append(f"- ~{lag * STATE_STEP_DAYS}D: C->A {ca_tr:.0%}->{ca_oo:.0%}; B->D {bd_tr:.0%}->{bd_oo:.0%}; A->A {aa_tr:.0%}->{aa_oo:.0%}; D->D {dd_tr:.0%}->{dd_oo:.0%}")
        lines.append("")
    lines += ["## Horizon-neighbor robustness: OOS +20D median split", ""]
    for u in PRIMARY_UNIVERSES:
        lines.append(f"### {u}")
        for spec in SPECS:
            z = quads[(quads["sample"] == "OOS") & (quads.spec == spec) & (quads.split_rule == "MEDIAN") &
                      (quads.universe == u) & (quads.forward_horizon == 20)].copy()
            if z.empty:
                continue
            m = z.set_index("state")
            cell = ", ".join(f"{st[0]}={fmt_pct(float(m.loc[st].mean_fwd_return))}" for st in STATE_ORDER if st in m.index)
            ad = get_contrast(contrasts, "OOS", spec, "MEDIAN", u, 20, "A_MINUS_D")
            cb = get_contrast(contrasts, "OOS", spec, "MEDIAN", u, 20, "C_MINUS_B")
            lines.append(f"- {spec}: {cell}; order {order_string(z)}; A-D {fmt_pct(ad)}, C-B {fmt_pct(cb)}")
        lines.append("")
    lines += ["## Extreme-tercile robustness: MAIN specification, +20D", ""]
    for u in PRIMARY_UNIVERSES:
        lines.append(f"### {u}")
        for sample in ("TRAIN", "OOS"):
            z = quads[(quads["sample"] == sample) & (quads.spec == "MAIN_F20_L5_20") &
                      (quads.split_rule == "EXTREME_TERCILE") & (quads.universe == u) &
                      (quads.forward_horizon == 20)].copy()
            if z.empty:
                continue
            m = z.set_index("state")
            cell = ", ".join(f"{st[0]}={fmt_pct(float(m.loc[st].mean_fwd_return))}(n={int(m.loc[st].n)})" for st in STATE_ORDER if st in m.index)
            lines.append(f"- {sample}: {cell}; order {order_string(z)}")
        lines.append("")
    lines += [
        "## Interpretation guardrails", "",
        "- A high future return in C does not by itself prove 'early-cycle'; the C->A transition rate and trailing-return context are the direct stage checks.",
        "- A weak future return in B does not by itself prove 'late-stage/crowding'; B->D transition and prior-return context are needed to support that label.",
        "- A positive interaction DiD means the two breadth signals are complementary; a negative DiD means their information is more substitutive/rotation-like.",
        "- Median quadrants are the primary exhaustive state map. Extreme-tercile corners are cleaner but use fewer observations.",
        "- This is a regime-screening layer, not yet a production allocation rule.", "",
    ]
    return "\n".join(lines)


def main() -> None:
    wide, market = load_inputs()
    market_fwd = {h: forward_market(market, h) for h in FWD_HORIZONS}
    market_tr20 = trailing_market(market, 20)
    quad_rows, trans_rows = [], []
    for spec, (factor_def, liq_def) in SPECS.items():
        if factor_def not in wide.columns or liq_def not in wide.columns:
            raise KeyError(f"Missing state columns for {spec}: {factor_def}, {liq_def}")
        for u in sorted(wide.universe.dropna().unique()):
            gu = wide[wide.universe == u].copy()
            for split_rule in SPLIT_RULES:
                pack = assign_states(gu, factor_def, liq_def, split_rule)
                if pack is None:
                    continue
                assigned, thresholds = pack
                quad_rows.extend(state_rows(assigned, thresholds, spec, split_rule, u, factor_def, liq_def, market_fwd, market_tr20))
                if split_rule == "MEDIAN":
                    trans_rows.extend(transition_rows(assigned, spec, u))
    quads = pd.DataFrame(quad_rows)
    contrasts = pd.DataFrame(contrast_rows(quads))
    transitions = pd.DataFrame(trans_rows)
    quads.to_csv(OUT / "quadrant_results.csv", index=False, encoding="utf-8-sig")
    contrasts.to_csv(OUT / "contrast_results.csv", index=False, encoding="utf-8-sig")
    transitions.to_csv(OUT / "transition_results.csv", index=False, encoding="utf-8-sig")
    text = summarize(quads, contrasts, transitions)
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
