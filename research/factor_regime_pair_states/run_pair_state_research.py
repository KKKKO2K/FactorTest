from __future__ import annotations

import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REGIME_DIR = ROOT / "research" / "factor_regime_v1"
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

SPLIT = pd.Timestamp("2023-01-01")
FWD_MARKET_HORIZONS = (1, 5, 20)
FWD_FACTOR_PERIODS = {"FWD_FACTOR_5D": 1, "FWD_FACTOR_20D": 4}
CUT_QUANTILES = {"Q25": 0.25, "Q33": 1 / 3, "Q50": 0.50}
MAIN_CUT = "Q33"
MIN_CELL_N = 8

FACTOR_FAMILY = {
    "MOM1M": "MOMENTUM",
    "MOM12_1": "MOMENTUM",
    "OP12_REV": "REVISION",
    "OPFY1_REV": "REVISION",
    "PBR12MF": "VALUE",
    "PER12MF": "VALUE",
    "PRIVATE_FLOW": "FLOW",
    "FOREIGN_FLOW": "FLOW",
}

MOMENTUM_FACTORS = ("MOM1M", "MOM12_1")
OTHER_FAMILIES = {
    "REVISION": ("OP12_REV", "OPFY1_REV"),
    "VALUE": ("PBR12MF", "PER12MF"),
    "FLOW": ("PRIVATE_FLOW", "FOREIGN_FLOW"),
}

PRIMARY_PAIRS = [
    (mom, other, fam)
    for mom in MOMENTUM_FACTORS
    for fam, members in OTHER_FAMILIES.items()
    for other in members
]

STATE_ORDER = ("REVERSE", "NEUTRAL", "WORKING")


def compound_rows(df: pd.DataFrame, periods: int) -> pd.DataFrame:
    if periods == 1:
        return df.copy()
    return (1.0 + df).rolling(periods, min_periods=periods).apply(np.prod, raw=True) - 1.0


def future_factor_returns(ls: pd.DataFrame, periods: int) -> pd.DataFrame:
    if periods == 1:
        return ls.shift(-1)
    parts = [1.0 + ls.shift(-i) for i in range(1, periods + 1)]
    out = parts[0].copy()
    for p in parts[1:]:
        out = out * p
    return out - 1.0


def forward_market(market_returns: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market_returns.clip(lower=-0.999999))
    acc = sum(logs.shift(-i) for i in range(1, h + 1))
    return np.expm1(acc)


def mean_tstat(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 3:
        return np.nan
    sd = x.std(ddof=1)
    return float(x.mean() / (sd / math.sqrt(len(x)))) if sd > 0 else np.nan


def diff_tstat(a: pd.Series, b: pd.Series) -> float:
    a, b = a.dropna(), b.dropna()
    if len(a) < 3 or len(b) < 3:
        return np.nan
    se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    return float((a.mean() - b.mean()) / se) if se > 0 else np.nan


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    f = pd.read_csv(REGIME_DIR / "results" / "factor_5d_returns.csv")
    f["date"] = pd.to_datetime(f["date"])
    market = pd.read_csv(REGIME_DIR / "results" / "market_daily_returns.csv", index_col=0)
    market.index = pd.to_datetime(market.index)
    market = market.sort_index()
    return f, market


def build_state_panel(f: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    state_rows: list[dict] = []
    threshold_rows: list[dict] = []

    for universe, gu in f.groupby("universe"):
        ls = gu.pivot(index="date", columns="factor", values="ls_return").sort_index()
        ls20 = compound_rows(ls, 4)

        available = [f for f in FACTOR_FAMILY if f in ls20.columns]
        for factor in available:
            train = ls20.loc[ls20.index < SPLIT, factor].dropna()
            if len(train) < 40:
                continue
            abs_train = train.abs()
            for cut_name, q in CUT_QUANTILES.items():
                cut = float(abs_train.quantile(q))
                if not np.isfinite(cut) or cut <= 0:
                    continue
                threshold_rows.append({
                    "universe": universe,
                    "factor": factor,
                    "family": FACTOR_FAMILY[factor],
                    "cut_name": cut_name,
                    "abs_spread_cut": cut,
                    "train_n": len(train),
                })
                x = ls20[factor].dropna()
                for dt, val in x.items():
                    state = "WORKING" if val >= cut else ("REVERSE" if val <= -cut else "NEUTRAL")
                    state_rows.append({
                        "date": dt,
                        "universe": universe,
                        "factor": factor,
                        "family": FACTOR_FAMILY[factor],
                        "cut_name": cut_name,
                        "spread_20d": float(val),
                        "strength_vs_cut": float(val / cut),
                        "state": state,
                    })

    return pd.DataFrame(state_rows), pd.DataFrame(threshold_rows)


def build_pair_results(
    f: pd.DataFrame,
    states: pd.DataFrame,
    market: pd.DataFrame,
) -> pd.DataFrame:
    market_fwd = {h: forward_market(market, h) for h in FWD_MARKET_HORIZONS}
    rows: list[dict] = []

    for universe, gu in f.groupby("universe"):
        ls = gu.pivot(index="date", columns="factor", values="ls_return").sort_index()
        future_factor = {label: future_factor_returns(ls, n) for label, n in FWD_FACTOR_PERIODS.items()}
        su = states[states.universe == universe]

        for mom, other, family_pair in PRIMARY_PAIRS:
            if mom not in ls.columns or other not in ls.columns:
                continue
            for cut_name in CUT_QUANTILES:
                a = su[(su.factor == mom) & (su.cut_name == cut_name)][
                    ["date", "state", "spread_20d", "strength_vs_cut"]
                ].rename(columns={
                    "state": "state_a", "spread_20d": "spread20_a", "strength_vs_cut": "strength_a"
                })
                b = su[(su.factor == other) & (su.cut_name == cut_name)][
                    ["date", "state", "spread_20d", "strength_vs_cut"]
                ].rename(columns={
                    "state": "state_b", "spread_20d": "spread20_b", "strength_vs_cut": "strength_b"
                })
                p = a.merge(b, on="date", how="inner").sort_values("date")
                if p.empty:
                    continue

                for h in FWD_MARKET_HORIZONS:
                    if universe in market_fwd[h].columns:
                        p[f"mkt_{h}"] = p.date.map(market_fwd[h][universe])
                for label, frame in future_factor.items():
                    p[f"a_{label}"] = p.date.map(frame[mom])
                    p[f"b_{label}"] = p.date.map(frame[other])

                for sample, mask in (("TRAIN", p.date < SPLIT), ("OOS", p.date >= SPLIT)):
                    ps = p.loc[mask].copy()
                    for state_a, state_b in itertools.product(STATE_ORDER, STATE_ORDER):
                        z = ps[(ps.state_a == state_a) & (ps.state_b == state_b)]
                        if len(z) < MIN_CELL_N:
                            continue
                        base = {
                            "sample": sample,
                            "universe": universe,
                            "cut_name": cut_name,
                            "factor_a": mom,
                            "factor_b": other,
                            "family_pair": f"MOMENTUM_X_{family_pair}",
                            "state_a": state_a,
                            "state_b": state_b,
                            "cell": f"{state_a[:1]}_{state_b[:1]}",
                            "n": len(z),
                            "mean_spread20_a": float(z.spread20_a.mean()),
                            "mean_spread20_b": float(z.spread20_b.mean()),
                        }
                        for h in FWD_MARKET_HORIZONS:
                            x = z[f"mkt_{h}"].dropna()
                            if len(x):
                                base[f"mkt_{h}d_mean"] = float(x.mean())
                                base[f"mkt_{h}d_median"] = float(x.median())
                                base[f"mkt_{h}d_positive_share"] = float((x > 0).mean())
                                base[f"mkt_{h}d_tstat"] = mean_tstat(x)
                        for label in FWD_FACTOR_PERIODS:
                            xa = z[f"a_{label}"].dropna()
                            xb = z[f"b_{label}"].dropna()
                            suffix = "5d" if label.endswith("5D") else "20d"
                            if len(xa):
                                base[f"a_fwd_{suffix}_mean"] = float(xa.mean())
                                base[f"a_fwd_{suffix}_positive_share"] = float((xa > 0).mean())
                            if len(xb):
                                base[f"b_fwd_{suffix}_mean"] = float(xb.mean())
                                base[f"b_fwd_{suffix}_positive_share"] = float((xb > 0).mean())
                        rows.append(base)

    return pd.DataFrame(rows)


PREDEFINED_CONTRASTS = {
    # Holding momentum WORKING fixed: does the other factor being REVERSE contain more information than merely NEUTRAL?
    "MOM_W_OTHER_R_MINUS_N": (("WORKING", "REVERSE"), ("WORKING", "NEUTRAL")),
    # Holding momentum WORKING fixed: conflict versus confirmation.
    "MOM_W_OTHER_R_MINUS_W": (("WORKING", "REVERSE"), ("WORKING", "WORKING")),
    # Holding other factor WORKING fixed: does momentum reversal differ from mere neutrality?
    "MOM_R_MINUS_N_OTHER_W": (("REVERSE", "WORKING"), ("NEUTRAL", "WORKING")),
    # Rotation versus broad confirmation.
    "MOM_R_OTHER_W_MINUS_BOTH_W": (("REVERSE", "WORKING"), ("WORKING", "WORKING")),
}


def build_contrasts(results: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    keys = ["sample", "universe", "cut_name", "factor_a", "factor_b", "family_pair"]
    for key, g in results.groupby(keys):
        base = dict(zip(keys, key))
        for cname, (left_state, right_state) in PREDEFINED_CONTRASTS.items():
            left = g[(g.state_a == left_state[0]) & (g.state_b == left_state[1])]
            right = g[(g.state_a == right_state[0]) & (g.state_b == right_state[1])]
            if left.empty or right.empty:
                continue
            l, r = left.iloc[0], right.iloc[0]
            row = {
                **base,
                "contrast": cname,
                "left_state": f"{left_state[0]}|{left_state[1]}",
                "right_state": f"{right_state[0]}|{right_state[1]}",
                "n_left": int(l.n),
                "n_right": int(r.n),
            }
            for h in FWD_MARKET_HORIZONS:
                col = f"mkt_{h}d_mean"
                if col in g.columns and pd.notna(l.get(col)) and pd.notna(r.get(col)):
                    row[f"mkt_{h}d_diff"] = float(l[col] - r[col])
            for prefix in ("a", "b"):
                for fh in ("5d", "20d"):
                    col = f"{prefix}_fwd_{fh}_mean"
                    if col in g.columns and pd.notna(l.get(col)) and pd.notna(r.get(col)):
                        row[f"{prefix}_fwd_{fh}_diff"] = float(l[col] - r[col])
            rows.append(row)
    return pd.DataFrame(rows)


def train_oos_stability(contrasts: pd.DataFrame) -> pd.DataFrame:
    keys = ["universe", "cut_name", "factor_a", "factor_b", "family_pair", "contrast"]
    tr = contrasts[contrasts["sample"] == "TRAIN"]
    oo = contrasts[contrasts["sample"] == "OOS"]
    diff_cols = [c for c in contrasts.columns if c.endswith("_diff")]
    rows: list[dict] = []
    for col in diff_cols:
        a = tr[keys + [col]].rename(columns={col: "train_diff"})
        b = oo[keys + [col]].rename(columns={col: "oos_diff"})
        m = a.merge(b, on=keys, how="inner").dropna(subset=["train_diff", "oos_diff"])
        for _, r in m.iterrows():
            rows.append({
                **{k: r[k] for k in keys},
                "outcome": col,
                "train_diff": r.train_diff,
                "oos_diff": r.oos_diff,
                "same_sign": bool(np.sign(r.train_diff) == np.sign(r.oos_diff)),
                "signed_oos_confirmation": float(np.sign(r.train_diff) * r.oos_diff),
            })
    return pd.DataFrame(rows)


def pct(x: float) -> str:
    return "nan" if pd.isna(x) else f"{x:+.2%}"


def summarize(results: pd.DataFrame, stability: pd.DataFrame) -> str:
    lines = [
        "# Factor Pair-State Regime Research", "",
        "Question: when momentum is WORKING/NEUTRAL/REVERSE, does another factor family being WORKING/NEUTRAL/REVERSE change subsequent market or factor outcomes?", 
        "Primary pairs are predeclared: MOM1M and MOM12_1 crossed with each Revision, Value, and Flow factor (12 pairs).",
        "State variable = trailing 20D canonical factor long-short spread. Main state cut (Q33): for each universe/factor, WORKING if spread >= TRAIN 33rd percentile of |spread|, REVERSE if spread <= negative of that cut, otherwise NEUTRAL. Q25/Q50 are robustness definitions.",
        "All state thresholds are fit on 2016-2022 TRAIN and frozen for 2023+ OOS. Future factor outcomes use the next non-overlapping 5D period or next four periods (~20D).",
        "20D forward market/factor windows overlap across 5D state dates; inference is descriptive. This is post-discovery research, not untouched OOS.", "",
        "## Main-cut (Q33) same-universe market outcomes", "",
    ]

    main = results[results.cut_name == MAIN_CUT]
    focus_universes = [u for u in ("K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ", "KOSDAQ_PLUS_KOSPI_EX_K200") if u in main.universe.unique()]
    interesting_cells = [
        ("WORKING", "WORKING", "MOM W / Other W"),
        ("WORKING", "REVERSE", "MOM W / Other R"),
        ("REVERSE", "WORKING", "MOM R / Other W"),
        ("REVERSE", "REVERSE", "MOM R / Other R"),
    ]
    for u in focus_universes:
        lines += [f"### {u}", ""]
        z = main[main.universe == u]
        for fam in ("MOMENTUM_X_REVISION", "MOMENTUM_X_VALUE", "MOMENTUM_X_FLOW"):
            lines.append(f"{fam}:")
            for sa, sb, label in interesting_cells:
                cell = z[(z.family_pair == fam) & (z.state_a == sa) & (z.state_b == sb)]
                if cell.empty:
                    continue
                for sample in ("TRAIN", "OOS"):
                    s = cell[cell["sample"] == sample]
                    if s.empty:
                        continue
                    m5 = s["mkt_5d_mean"].median() if "mkt_5d_mean" in s else np.nan
                    m20 = s["mkt_20d_mean"].median() if "mkt_20d_mean" in s else np.nan
                    lines.append(f"- {label}, {sample}: median across constituent pairs market +5D {pct(m5)}, +20D {pct(m20)} (pairs={len(s)})")
            lines.append("")

    lines += ["## Predefined contrast stability", "",
              "Positive MOM_W_OTHER_R_MINUS_N means that, conditional on momentum working, an outright reversal in the other factor predicts a higher outcome than the other factor merely being neutral. Negative means the reverse state is worse.",
              "Positive MOM_R_MINUS_N_OTHER_W means that, conditional on the other factor working, an outright momentum reversal predicts a higher outcome than momentum merely being neutral.", ""]

    s = stability[(stability.cut_name == MAIN_CUT) & stability.outcome.isin(["mkt_5d_diff", "mkt_20d_diff", "b_fwd_20d_diff", "a_fwd_20d_diff"])]
    if not s.empty:
        agg = (s.groupby(["family_pair", "contrast", "outcome"])
               .agg(n=("same_sign", "size"), same_sign_rate=("same_sign", "mean"),
                    median_train=("train_diff", "median"), median_oos=("oos_diff", "median"))
               .reset_index())
        for fam in ("MOMENTUM_X_REVISION", "MOMENTUM_X_VALUE", "MOMENTUM_X_FLOW"):
            lines.append(f"### {fam}")
            zz = agg[agg.family_pair == fam]
            for _, r in zz.sort_values(["same_sign_rate", "outcome"], ascending=[False, True]).iterrows():
                lines.append(
                    f"- {r.contrast} / {r.outcome}: sign-stability {r.same_sign_rate:.0%} (n={int(r.n)}), "
                    f"median TRAIN {pct(r.median_train)}, OOS {pct(r.median_oos)}"
                )
            lines.append("")

    lines += ["## Guardrails", "",
              "- Pair states preserve information that breadth discards, but create more cells; cell counts and TRAIN/OOS direction stability matter more than the single best return.",
              "- WORKING vs REVERSE is economically directional; NEUTRAL is a factor-specific dead zone calibrated only from TRAIN magnitude.",
              "- The 12 primary pairs were fixed before this run. Do not promote an isolated pair solely because its OOS return is extreme.",
              "- Breadth remains a useful low-dimensional benchmark; this layer asks whether the identity and sign of the working factors add information beyond the count.", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    f, market = load_inputs()
    states, thresholds = build_state_panel(f)
    results = build_pair_results(f, states, market)
    contrasts = build_contrasts(results)
    stability = train_oos_stability(contrasts)

    thresholds.to_csv(OUT / "state_thresholds.csv", index=False, encoding="utf-8-sig")
    states.to_csv(OUT / "factor_state_panel.csv", index=False, encoding="utf-8-sig")
    results.to_csv(OUT / "pair_state_results.csv", index=False, encoding="utf-8-sig")
    contrasts.to_csv(OUT / "predefined_contrasts.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(OUT / "train_oos_stability.csv", index=False, encoding="utf-8-sig")
    summary = summarize(results, stability)
    (OUT / "RESEARCH_SUMMARY.md").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
