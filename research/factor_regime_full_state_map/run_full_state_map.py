from __future__ import annotations

import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SRC = ROOT / "research" / "factor_regime_v1" / "results"
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

STATIC_SPLIT = pd.Timestamp("2023-01-01")
STATIC_TRAIN_START = pd.Timestamp("2016-01-01")
CUTS = {"Q25": 0.25, "Q33": 1/3, "Q50": 0.50}
MAIN_CUT = "Q33"
MIN_N = 8
HORIZONS = (1, 5, 20)
WF_START_YEAR = 2021

FAMILY_MEMBERS = {
    "MOMENTUM": ("MOM1M", "MOM12_1"),
    "REVISION": ("OP12_REV", "OPFY1_REV"),
    "VALUE": ("PBR12MF", "PER12MF"),
    "FLOW": ("PRIVATE_FLOW", "FOREIGN_FLOW"),
}
FAMILIES = tuple(FAMILY_MEMBERS)
FAMILY_PAIRS = list(itertools.combinations(FAMILIES, 2))

STATE6 = ("W+", "W-", "N+", "N-", "R+", "R-")


def compound_roll(s: pd.Series, n: int) -> pd.Series:
    return (1.0 + s).rolling(n, min_periods=n).apply(np.prod, raw=True) - 1.0


def future_compound(s: pd.Series, n: int) -> pd.Series:
    out = 1.0 + s.shift(-1)
    for i in range(2, n + 1):
        out = out * (1.0 + s.shift(-i))
    return out - 1.0


def forward_market(market: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market.clip(lower=-0.999999))
    acc = sum(logs.shift(-i) for i in range(1, h + 1))
    return np.expm1(acc)


def mean_tstat(x: pd.Series) -> float:
    x = x.dropna()
    if len(x) < 3:
        return np.nan
    sd = x.std(ddof=1)
    return float(x.mean() / (sd / math.sqrt(len(x)))) if sd > 0 else np.nan


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    f = pd.read_csv(SRC / "factor_5d_returns.csv")
    f["date"] = pd.to_datetime(f["date"])
    req = {"date", "universe", "factor", "ls_return", "top_abs_return"}
    miss = req - set(f.columns)
    if miss:
        raise ValueError(f"factor_5d_returns.csv missing {sorted(miss)}")
    f["bottom_abs_return"] = f["top_abs_return"] - f["ls_return"]
    market = pd.read_csv(SRC / "market_daily_returns.csv", index_col=0)
    market.index = pd.to_datetime(market.index)
    return f.sort_values(["universe", "date", "factor"]), market.sort_index()


def build_family_primitives(f: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for u, g in f.groupby("universe"):
        top = g.pivot(index="date", columns="factor", values="top_abs_return").sort_index()
        bot = g.pivot(index="date", columns="factor", values="bottom_abs_return").sort_index()
        for fam, members in FAMILY_MEMBERS.items():
            members = [m for m in members if m in top.columns]
            if len(members) != 2:
                continue
            fam_top5 = top[members].mean(axis=1, skipna=False)
            fam_bot5 = bot[members].mean(axis=1, skipna=False)
            fam_sp5 = fam_top5 - fam_bot5
            fam_top20 = compound_roll(fam_top5, 4)
            fam_bot20 = compound_roll(fam_bot5, 4)
            fam_sp20 = fam_top20 - fam_bot20
            fam_top60 = compound_roll(fam_top5, 12)
            fam_bot60 = compound_roll(fam_bot5, 12)
            fam_sp60 = fam_top60 - fam_bot60

            member_sp20 = {}
            for m in members:
                mt = compound_roll(top[m], 4)
                mb = compound_roll(bot[m], 4)
                member_sp20[m] = mt - mb

            for dt in fam_top5.index:
                vals = [member_sp20[m].get(dt, np.nan) for m in members]
                finite = [v for v in vals if np.isfinite(v)]
                if not (np.isfinite(fam_top20.get(dt, np.nan)) and np.isfinite(fam_bot20.get(dt, np.nan))):
                    continue
                pos_share = float(np.mean([v > 0 for v in finite])) if finite else np.nan
                same_sign = float(len(finite) == 2 and ((finite[0] > 0 and finite[1] > 0) or (finite[0] < 0 and finite[1] < 0)))
                rows.append({
                    "date": dt, "universe": u, "family": fam,
                    "top_5d": float(fam_top5.loc[dt]), "bottom_5d": float(fam_bot5.loc[dt]), "spread_5d": float(fam_sp5.loc[dt]),
                    "top_20d": float(fam_top20.loc[dt]), "bottom_20d": float(fam_bot20.loc[dt]), "spread_20d": float(fam_sp20.loc[dt]),
                    "top_60d": float(fam_top60.get(dt, np.nan)), "bottom_60d": float(fam_bot60.get(dt, np.nan)), "spread_60d": float(fam_sp60.get(dt, np.nan)),
                    "member_positive_spread_share_20d": pos_share,
                    "member_same_sign_20d": same_sign,
                    "member1": members[0], "member2": members[1],
                    "member1_spread_20d": float(vals[0]) if np.isfinite(vals[0]) else np.nan,
                    "member2_spread_20d": float(vals[1]) if np.isfinite(vals[1]) else np.nan,
                })
    return pd.DataFrame(rows)


def state6_from(rel: float, top_abs: float, cut: float) -> str:
    if rel >= cut:
        return "W+" if top_abs > 0 else "W-"
    if rel <= -cut:
        return "R+" if top_abs > 0 else "R-"
    return "N+" if top_abs > 0 else "N-"


def build_static_states(p: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, cuts = [], []
    for (u, fam), g in p.groupby(["universe", "family"]):
        tr = g[(g.date >= STATIC_TRAIN_START) & (g.date < STATIC_SPLIT)].spread_20d.dropna()
        if len(tr) < 40:
            continue
        for cn, q in CUTS.items():
            cut = float(tr.abs().quantile(q))
            if not np.isfinite(cut) or cut <= 0:
                continue
            cuts.append({"universe": u, "family": fam, "cut_name": cn, "cut": cut, "train_n": len(tr)})
            for r in g.itertuples():
                if not (np.isfinite(r.spread_20d) and np.isfinite(r.top_20d)):
                    continue
                rows.append({
                    "date": r.date, "universe": u, "family": fam, "cut_name": cn,
                    "state6": state6_from(r.spread_20d, r.top_20d, cut),
                    "cut": cut, "top_20d": r.top_20d, "bottom_20d": r.bottom_20d, "spread_20d": r.spread_20d,
                    "spread_60d": r.spread_60d,
                    "member_positive_spread_share_20d": r.member_positive_spread_share_20d,
                    "member_same_sign_20d": r.member_same_sign_20d,
                })
    return pd.DataFrame(rows), pd.DataFrame(cuts)


def build_walkforward_states(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    max_year = int(p.date.dt.year.max())
    for eval_year in range(WF_START_YEAR, max_year + 1):
        y0, y1 = pd.Timestamp(f"{eval_year}-01-01"), pd.Timestamp(f"{eval_year+1}-01-01")
        for (u, fam), g in p.groupby(["universe", "family"]):
            tr = g[(g.date >= STATIC_TRAIN_START) & (g.date < y0)].spread_20d.dropna()
            if len(tr) < 40:
                continue
            cut = float(tr.abs().quantile(CUTS[MAIN_CUT]))
            if not np.isfinite(cut) or cut <= 0:
                continue
            z = g[(g.date >= STATIC_TRAIN_START) & (g.date < y1)].copy()
            for r in z.itertuples():
                split = "VALID" if y0 <= r.date < y1 else ("TRAIN" if r.date < y0 else None)
                if split is None or not (np.isfinite(r.spread_20d) and np.isfinite(r.top_20d)):
                    continue
                rows.append({
                    "eval_year": eval_year, "split": split, "date": r.date, "universe": u, "family": fam,
                    "state6": state6_from(r.spread_20d, r.top_20d, cut), "cut": cut,
                    "top_20d": r.top_20d, "bottom_20d": r.bottom_20d, "spread_20d": r.spread_20d,
                    "spread_60d": r.spread_60d,
                    "member_positive_spread_share_20d": r.member_positive_spread_share_20d,
                    "member_same_sign_20d": r.member_same_sign_20d,
                })
    return pd.DataFrame(rows)


def add_forward_family_metrics(p: pd.DataFrame) -> pd.DataFrame:
    out = []
    for (u, fam), g in p.groupby(["universe", "family"]):
        z = g.sort_values("date").copy()
        z["top_fwd_5d"] = future_compound(z.set_index("date").top_5d, 1).reindex(z.date).to_numpy()
        z["top_fwd_20d"] = future_compound(z.set_index("date").top_5d, 4).reindex(z.date).to_numpy()
        z["bottom_fwd_5d"] = future_compound(z.set_index("date").bottom_5d, 1).reindex(z.date).to_numpy()
        z["bottom_fwd_20d"] = future_compound(z.set_index("date").bottom_5d, 4).reindex(z.date).to_numpy()
        z["spread_fwd_5d"] = z.top_fwd_5d - z.bottom_fwd_5d
        z["spread_fwd_20d"] = z.top_fwd_20d - z.bottom_fwd_20d
        out.append(z)
    return pd.concat(out, ignore_index=True)


def prepare_pair_obs(states: pd.DataFrame, primitives: pd.DataFrame, market: pd.DataFrame,
                     family_a: str, family_b: str, cut_name: str | None = None,
                     eval_year: int | None = None, split: str | None = None) -> pd.DataFrame:
    s = states.copy()
    if cut_name is not None and "cut_name" in s.columns:
        s = s[s.cut_name == cut_name]
    if eval_year is not None:
        s = s[s.eval_year == eval_year]
    if split is not None:
        s = s[s.split == split]
    a = s[s.family == family_a][["date", "universe", "state6", "top_20d", "spread_20d", "member_same_sign_20d"]].rename(columns={
        "state6": "state_a", "top_20d": "top20_a", "spread_20d": "spread20_a", "member_same_sign_20d": "agree_a"})
    b = s[s.family == family_b][["date", "universe", "state6", "top_20d", "spread_20d", "member_same_sign_20d"]].rename(columns={
        "state6": "state_b", "top_20d": "top20_b", "spread_20d": "spread20_b", "member_same_sign_20d": "agree_b"})
    x = a.merge(b, on=["date", "universe"], how="inner")
    if x.empty:
        return x
    pm = primitives[["date", "universe", "family", "top_fwd_5d", "top_fwd_20d", "spread_fwd_5d", "spread_fwd_20d"]]
    pa = pm[pm.family == family_a].drop(columns="family").rename(columns={c: f"a_{c}" for c in ["top_fwd_5d", "top_fwd_20d", "spread_fwd_5d", "spread_fwd_20d"]})
    pb = pm[pm.family == family_b].drop(columns="family").rename(columns={c: f"b_{c}" for c in ["top_fwd_5d", "top_fwd_20d", "spread_fwd_5d", "spread_fwd_20d"]})
    x = x.merge(pa, on=["date", "universe"], how="left").merge(pb, on=["date", "universe"], how="left")
    fwd = {h: forward_market(market, h) for h in HORIZONS}
    for h in HORIZONS:
        vals = []
        for r in x.itertuples():
            vals.append(fwd[h].at[r.date, r.universe] if r.date in fwd[h].index and r.universe in fwd[h].columns else np.nan)
        x[f"mkt_{h}d"] = vals
    return x


def summarize_cell(z: pd.DataFrame, base: dict) -> dict:
    row = dict(base)
    row["n"] = len(z)
    row["mean_agree_a"] = float(z.agree_a.mean()) if z.agree_a.notna().any() else np.nan
    row["mean_agree_b"] = float(z.agree_b.mean()) if z.agree_b.notna().any() else np.nan
    for h in HORIZONS:
        y = z[f"mkt_{h}d"].dropna()
        if len(y):
            row[f"mkt_{h}d_mean"] = float(y.mean())
            row[f"mkt_{h}d_median"] = float(y.median())
            row[f"mkt_{h}d_positive_share"] = float((y > 0).mean())
            row[f"mkt_{h}d_tstat"] = mean_tstat(y)
    for c in ["a_top_fwd_5d", "a_top_fwd_20d", "a_spread_fwd_5d", "a_spread_fwd_20d",
              "b_top_fwd_5d", "b_top_fwd_20d", "b_spread_fwd_5d", "b_spread_fwd_20d"]:
        y = z[c].dropna()
        if len(y):
            row[f"{c}_mean"] = float(y.mean())
            row[f"{c}_positive_share"] = float((y > 0).mean())
    return row


def build_static_pair_matrix(states: pd.DataFrame, primitives: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fa, fb in FAMILY_PAIRS:
        x = prepare_pair_obs(states, primitives, market, fa, fb, cut_name=MAIN_CUT)
        for u, g in x.groupby("universe"):
            for sample, mask in (("TRAIN", g.date < STATIC_SPLIT), ("POST_DISCOVERY", g.date >= STATIC_SPLIT)):
                s = g[mask]
                for (sa, sb), z in s.groupby(["state_a", "state_b"]):
                    if len(z) < MIN_N:
                        continue
                    rows.append(summarize_cell(z, {"sample": sample, "universe": u, "family_a": fa, "family_b": fb,
                                                  "family_pair": f"{fa}_X_{fb}", "state_a": sa, "state_b": sb}))
    return pd.DataFrame(rows)


# Common, predeclared conditional contrasts. Each is also evaluated with A/B roles reversed.
CONTRASTS = {
    "CONFIRM_WPLUS_VS_NEUTRAL_WHEN_ANCHOR_WPLUS": ("W+", {"W+"}, {"N+", "N-"}),
    "CONFLICT_RMINUS_VS_NEUTRAL_WHEN_ANCHOR_WPLUS": ("W+", {"R-"}, {"N+", "N-"}),
    "ALT_WPLUS_VS_NEUTRAL_WHEN_ANCHOR_RMINUS": ("R-", {"W+"}, {"N+", "N-"}),
    "ALT_WMINUS_VS_NEUTRAL_WHEN_ANCHOR_RMINUS": ("R-", {"W-"}, {"N+", "N-"}),
    "GENUINE_VS_DEFENSIVE_SUPPORT_WHEN_ANCHOR_RMINUS": ("R-", {"W+"}, {"W-"}),
}


def contrast_one(x: pd.DataFrame, anchor_col: str, other_col: str, cname: str,
                 anchor_state: str, left_states: set[str], right_states: set[str], base: dict) -> dict | None:
    z = x[x[anchor_col] == anchor_state]
    left = z[z[other_col].isin(left_states)]
    right = z[z[other_col].isin(right_states)]
    if len(left) < MIN_N or len(right) < MIN_N:
        return None
    row = dict(base)
    row.update({"contrast": cname, "n_left": len(left), "n_right": len(right)})
    outcomes = [f"mkt_{h}d" for h in HORIZONS] + [
        "a_top_fwd_5d", "a_top_fwd_20d", "a_spread_fwd_5d", "a_spread_fwd_20d",
        "b_top_fwd_5d", "b_top_fwd_20d", "b_spread_fwd_5d", "b_spread_fwd_20d"]
    for c in outcomes:
        l, r = left[c].dropna(), right[c].dropna()
        if len(l) and len(r):
            row[f"{c}_left"] = float(l.mean())
            row[f"{c}_right"] = float(r.mean())
            row[f"{c}_diff"] = float(l.mean() - r.mean())
    return row


def build_static_contrasts(states: pd.DataFrame, primitives: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for fa, fb in FAMILY_PAIRS:
        x = prepare_pair_obs(states, primitives, market, fa, fb, cut_name=MAIN_CUT)
        for u, g in x.groupby("universe"):
            for sample, mask in (("TRAIN", g.date < STATIC_SPLIT), ("POST_DISCOVERY", g.date >= STATIC_SPLIT)):
                s = g[mask]
                for anchor, other, ac, oc in ((fa, fb, "state_a", "state_b"), (fb, fa, "state_b", "state_a")):
                    for cname, (ast, left, right) in CONTRASTS.items():
                        row = contrast_one(s, ac, oc, cname, ast, left, right,
                                           {"sample": sample, "universe": u, "family_pair": f"{fa}_X_{fb}",
                                            "anchor_family": anchor, "other_family": other})
                        if row:
                            rows.append(row)
    return pd.DataFrame(rows)


def build_walkforward_contrasts(wf_states: pd.DataFrame, primitives: pd.DataFrame, market: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    years = sorted(wf_states.eval_year.unique())
    for y in years:
        for fa, fb in FAMILY_PAIRS:
            for split in ("TRAIN", "VALID"):
                x = prepare_pair_obs(wf_states, primitives, market, fa, fb, eval_year=int(y), split=split)
                for u, g in x.groupby("universe"):
                    for anchor, other, ac, oc in ((fa, fb, "state_a", "state_b"), (fb, fa, "state_b", "state_a")):
                        for cname, (ast, left, right) in CONTRASTS.items():
                            row = contrast_one(g, ac, oc, cname, ast, left, right,
                                               {"eval_year": int(y), "split": split, "universe": u,
                                                "family_pair": f"{fa}_X_{fb}", "anchor_family": anchor, "other_family": other})
                            if row:
                                rows.append(row)
    raw = pd.DataFrame(rows)
    stab = []
    if raw.empty:
        return raw, pd.DataFrame()
    outcomes = [c for c in raw.columns if c.endswith("_diff")]
    keys = ["universe", "family_pair", "anchor_family", "other_family", "contrast"]
    for key, g in raw.groupby(keys):
        tr = g[g.split == "TRAIN"]
        va = g[g.split == "VALID"]
        for out in outcomes:
            m = tr[["eval_year", out]].merge(va[["eval_year", out]], on="eval_year", suffixes=("_train", "_valid")).dropna()
            if m.empty:
                continue
            same = np.sign(m[f"{out}_train"]) == np.sign(m[f"{out}_valid"])
            stab.append({
                **dict(zip(keys, key)), "outcome": out, "n_years": len(m),
                "sign_stability": float(same.mean()),
                "median_train_diff": float(m[f"{out}_train"].median()),
                "median_valid_diff": float(m[f"{out}_valid"].median()),
                "positive_valid_year_share": float((m[f"{out}_valid"] > 0).mean()),
            })
    return raw, pd.DataFrame(stab)


def build_leader_events(states: pd.DataFrame, primitives: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    s = states[states.cut_name == MAIN_CUT].copy()
    rows = []
    fwd = {h: forward_market(market, h) for h in HORIZONS}
    for u, g in s.groupby("universe"):
        wide60 = g.pivot(index="date", columns="family", values="spread_60d").sort_index()
        leader_info = []
        for dt, r in wide60.iterrows():
            rr = r.dropna()
            if len(rr) < 3:
                continue
            leader = rr.idxmax()
            strength = float(rr.max() - rr.median())
            leader_info.append((dt, leader, strength))
        li = pd.DataFrame(leader_info, columns=["date", "leader", "leader_strength"])
        if li.empty:
            continue
        cut = li[li.date < STATIC_SPLIT].leader_strength.quantile(2/3)
        for dt, leader, strength in li.itertuples(index=False):
            if not np.isfinite(strength) or strength < cut:
                continue
            cur = g[g.date == dt].set_index("family")
            if leader not in cur.index or cur.at[leader, "state6"] != "R-":
                continue
            for alt in FAMILIES:
                if alt == leader or alt not in cur.index:
                    continue
                alt_state = cur.at[alt, "state6"]
                if alt_state == "W+":
                    regime = "GENUINE_ROTATION"
                elif alt_state == "W-":
                    regime = "DEFENSIVE_ROTATION"
                elif alt_state in ("N+", "N-"):
                    regime = "NO_CLEAR_ROTATION"
                else:
                    regime = "ALT_REVERSE"
                base = {"date": dt, "sample": "TRAIN" if dt < STATIC_SPLIT else "POST_DISCOVERY", "universe": u,
                        "leader_family": leader, "alternative_family": alt, "leader_strength": strength,
                        "leader_strength_cut": float(cut), "leader_state": "R-", "alternative_state": alt_state,
                        "rotation_regime": regime}
                for h in HORIZONS:
                    base[f"mkt_{h}d"] = fwd[h].at[dt, u] if dt in fwd[h].index and u in fwd[h].columns else np.nan
                pm = primitives[(primitives.universe == u) & (primitives.date == dt)].set_index("family")
                if leader in pm.index:
                    base["leader_top_fwd20"] = pm.at[leader, "top_fwd_20d"]
                    base["leader_spread_fwd20"] = pm.at[leader, "spread_fwd_20d"]
                if alt in pm.index:
                    base["alt_top_fwd20"] = pm.at[alt, "top_fwd_20d"]
                    base["alt_spread_fwd20"] = pm.at[alt, "spread_fwd_20d"]
                rows.append(base)
    return pd.DataFrame(rows)


def summarize_leader_events(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if events.empty:
        return pd.DataFrame()
    for key, g in events.groupby(["sample", "universe", "rotation_regime"]):
        if len(g) < MIN_N:
            continue
        row = {"sample": key[0], "universe": key[1], "rotation_regime": key[2], "n": len(g)}
        for c in ["mkt_5d", "mkt_20d", "leader_top_fwd20", "leader_spread_fwd20", "alt_top_fwd20", "alt_spread_fwd20"]:
            x = g[c].dropna()
            if len(x):
                row[f"{c}_mean"] = float(x.mean())
                row[f"{c}_median"] = float(x.median())
                row[f"{c}_positive_share"] = float((x > 0).mean())
        rows.append(row)
    return pd.DataFrame(rows)


def write_summary(static_matrix: pd.DataFrame, static_contrasts: pd.DataFrame,
                  wf_stability: pd.DataFrame, leader_summary: pd.DataFrame) -> str:
    lines = [
        "# Full Factor-Family State Map", "",
        "Architecture: preserve preferred/opposite absolute returns first; build equal-weight family sleeves; then classify family W+/W-/N+/N-/R+/R-.",
        "Families: Momentum, Revision, Value, Flow. All six family pairs are analyzed symmetrically. Family member agreement is retained so averaging does not hide constituent conflict.",
        "Static 2016-2022 / 2023+ tables are descriptive; formal validation is expanding annual walk-forward starting in 2021, with Q33 dead-zone thresholds fit only on prior years.",
        "Common contrasts are predeclared and applied identically to every ordered family relationship. 20D forward returns overlap across 5D state dates; inference is descriptive.", "",
        "## Walk-forward contrast stability — market 20D", "",
    ]
    if not wf_stability.empty:
        z = wf_stability[wf_stability.outcome == "mkt_20d_diff"].copy()
        z = z[z.n_years >= 3].sort_values(["sign_stability", "median_valid_diff"], ascending=[False, False])
        for _, r in z.head(30).iterrows():
            lines.append(f"- {r.universe} | {r.anchor_family}->{r.other_family} | {r.contrast}: sign {r.sign_stability:.0%} over {int(r.n_years)} years; median TRAIN {r.median_train_diff:+.2%}, VALID {r.median_valid_diff:+.2%}")
    lines += ["", "## Static post-discovery pair cells — selected by sample size, not return", ""]
    if not static_matrix.empty:
        z = static_matrix[static_matrix["sample"] == "POST_DISCOVERY"].sort_values("n", ascending=False)
        for _, r in z.head(24).iterrows():
            lines.append(f"- {r.universe} {r.family_pair} {r.state_a}/{r.state_b}: n={int(r.n)}, +5D {r.get('mkt_5d_mean', np.nan):+.2%}, +20D {r.get('mkt_20d_mean', np.nan):+.2%}, member agreement {r.mean_agree_a:.0%}/{r.mean_agree_b:.0%}")
    lines += ["", "## Generalized strong-leader rotation", ""]
    if not leader_summary.empty:
        for _, r in leader_summary.sort_values(["sample", "universe", "rotation_regime"]).iterrows():
            lines.append(f"- {r['sample']} {r.universe} {r.rotation_regime}: n={int(r.n)}, market +5D {r.get('mkt_5d_mean', np.nan):+.2%}, +20D {r.get('mkt_20d_mean', np.nan):+.2%}; alt top +20D {r.get('alt_top_fwd20_mean', np.nan):+.2%}")
    lines += ["", "## Guardrails", "",
              "- Do not promote a single cell because its return is extreme; use common contrasts, walk-forward sign stability, sample size, and neighboring definitions.",
              "- Family states are equal-weight sleeves of the two constituent factors, not votes. Member agreement remains visible and should be checked before interpreting a family label.",
              "- Rotation is directional only in the leader module. The six-pair map itself is a symmetric state map, avoiding a Momentum-centric assumption.",
              "- Liquidity breadth should be overlaid only after stable factor-state relations are identified; it is not used to select relations in this run.", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    f, market = load_inputs()
    primitives = add_forward_family_metrics(build_family_primitives(f))
    static_states, static_cuts = build_static_states(primitives)
    wf_states = build_walkforward_states(primitives)
    static_matrix = build_static_pair_matrix(static_states, primitives, market)
    static_contrasts = build_static_contrasts(static_states, primitives, market)
    wf_raw, wf_stability = build_walkforward_contrasts(wf_states, primitives, market)
    leader_events = build_leader_events(static_states, primitives, market)
    leader_summary = summarize_leader_events(leader_events)

    primitives.to_csv(OUT / "family_primitives.csv", index=False, encoding="utf-8-sig")
    static_states.to_csv(OUT / "family_states_static.csv", index=False, encoding="utf-8-sig")
    static_cuts.to_csv(OUT / "family_state_thresholds_static.csv", index=False, encoding="utf-8-sig")
    wf_states.to_csv(OUT / "family_states_walkforward.csv", index=False, encoding="utf-8-sig")
    static_matrix.to_csv(OUT / "full_pair_state_matrix.csv", index=False, encoding="utf-8-sig")
    static_contrasts.to_csv(OUT / "common_contrasts_static.csv", index=False, encoding="utf-8-sig")
    wf_raw.to_csv(OUT / "common_contrasts_walkforward.csv", index=False, encoding="utf-8-sig")
    wf_stability.to_csv(OUT / "walkforward_contrast_stability.csv", index=False, encoding="utf-8-sig")
    leader_events.to_csv(OUT / "generalized_leader_rotation_events.csv", index=False, encoding="utf-8-sig")
    leader_summary.to_csv(OUT / "generalized_leader_rotation_summary.csv", index=False, encoding="utf-8-sig")
    (OUT / "RESEARCH_SUMMARY.md").write_text(write_summary(static_matrix, static_contrasts, wf_stability, leader_summary), encoding="utf-8")

    print(f"family primitives: {len(primitives):,}")
    print(f"static pair cells: {len(static_matrix):,}")
    print(f"walk-forward contrasts: {len(wf_raw):,}")
    print(f"leader events: {len(leader_events):,}")


if __name__ == "__main__":
    main()
