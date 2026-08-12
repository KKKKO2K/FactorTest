from __future__ import annotations

import itertools
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import TimeSeriesSplit, cross_val_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FULL = ROOT / "research" / "factor_regime_full_state_map" / "results"
ABS = ROOT / "research" / "factor_regime_absolute_states" / "results"
HORIZON = ROOT / "research" / "factor_regime_horizon_robustness" / "results"
REG = ROOT / "research" / "factor_regime_v1" / "results"
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_START = pd.Timestamp("2016-01-01")
TRAIN_END = pd.Timestamp("2023-01-01")
MAIN_CUT = "Q33"
PRIMARY_K = 5
K_GRID = (3, 4, 5, 6)
MIN_CLUSTER_SHARE = 0.05
FAMILIES = ("MOMENTUM", "REVISION", "VALUE", "FLOW")

BASE_FEATURES = [
    "MKT_RET_20D", "MKT_RET_60D", "MKT_VOL_20D", "MKT_DD_60D", "LIQ_5D_20D",
]
FACTOR_FEATURES = [
    "RELATIVE_WORKING_BREADTH", "ABS_CONFIRMED_BREADTH", "DEFENSIVE_WORKING_BREADTH",
    "BEARISH_REVERSE_BREADTH", "WPLUS_FAMILY_SHARE", "WMINUS_FAMILY_SHARE",
    "RMINUS_FAMILY_SHARE", "WPLUS_PAIR_SHARE", "CONFLICT_PAIR_SHARE",
    "LEADER_STRENGTH_60D", "SPREAD_DISPERSION_20D", "LEADER_RMINUS",
    "GENUINE_ROTATION", "DEFENSIVE_ROTATION",
]
FULL_FEATURES = BASE_FEATURES + FACTOR_FEATURES

PERIODS = {
    "CAL_2016_2019": (pd.Timestamp("2016-01-01"), pd.Timestamp("2020-01-01")),
    "CAL_2020_2021": (pd.Timestamp("2020-01-01"), pd.Timestamp("2022-01-01")),
    "CAL_2022": (pd.Timestamp("2022-01-01"), pd.Timestamp("2023-01-01")),
    "NORMAL_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2025-01-01")),
    "STRONG_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2026-01-01")),
    "HYPER_2026_YTD": (pd.Timestamp("2026-01-01"), pd.Timestamp("2027-01-01")),
}


def compound_roll(s: pd.Series, n: int) -> pd.Series:
    return (1.0 + s).rolling(n, min_periods=n).apply(np.prod, raw=True) - 1.0


def forward_market(market: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(market.clip(lower=-0.999999))
    acc = sum(logs.shift(-i) for i in range(1, h + 1))
    return np.expm1(acc)


def market_context(market: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for u in market.columns:
        r = market[u].dropna().sort_index()
        idx = (1.0 + r).cumprod()
        ret20 = compound_roll(r, 20)
        ret60 = compound_roll(r, 60)
        vol20 = r.rolling(20, min_periods=20).std(ddof=1) * math.sqrt(252)
        dd60 = idx / idx.rolling(60, min_periods=60).max() - 1.0
        f5 = forward_market(market[[u]], 5)[u]
        f20 = forward_market(market[[u]], 20)[u]
        for dt in r.index:
            if not all(np.isfinite(x.get(dt, np.nan)) for x in (ret20, ret60, vol20, dd60)):
                continue
            future = r.loc[r.index > dt].head(20)
            if len(future) >= 5:
                path = (1.0 + future).cumprod()
                fwd_dd20 = float(path.min() - 1.0)
                fwd_vol20 = float(future.std(ddof=1) * math.sqrt(252)) if len(future) >= 10 else np.nan
            else:
                fwd_dd20 = np.nan
                fwd_vol20 = np.nan
            rows.append({
                "date": dt, "universe": u,
                "MKT_RET_20D": float(ret20.loc[dt]), "MKT_RET_60D": float(ret60.loc[dt]),
                "MKT_VOL_20D": float(vol20.loc[dt]), "MKT_DD_60D": float(dd60.loc[dt]),
                "MKT_FWD_5D": float(f5.get(dt, np.nan)), "MKT_FWD_20D": float(f20.get(dt, np.nan)),
                "MKT_FWD_DD20": fwd_dd20, "MKT_FWD_VOL20": fwd_vol20,
            })
    return pd.DataFrame(rows)


def load_liquidity() -> pd.DataFrame:
    x = pd.read_csv(HORIZON / "horizon_state_values.csv")
    x["date"] = pd.to_datetime(x["date"])
    required = {"date", "universe", "liq_current_days", "liq_baseline_days", "liq_breadth"}
    if not required.issubset(x.columns):
        raise ValueError(f"horizon_state_values schema mismatch: {sorted(x.columns)}")
    out = []
    for recent, label in ((5, "LIQ_5D_20D"), (1, "LIQ_1D_20D")):
        z = x[(x.liq_current_days == recent) & (x.liq_baseline_days == 20)].copy()
        if "factor_window_blocks" in z.columns:
            z = z[z.factor_window_blocks == 4]
        z = z.groupby(["date", "universe"], as_index=False).liq_breadth.mean()
        z = z.rename(columns={"liq_breadth": label})
        out.append(z)
    return out[0].merge(out[1], on=["date", "universe"], how="outer")


def build_family_interactions(states: pd.DataFrame, prim: pd.DataFrame) -> pd.DataFrame:
    s = states[states.cut_name == MAIN_CUT].copy()
    p = prim.copy()
    rows = []
    for (dt, u), g in s.groupby(["date", "universe"]):
        if g.family.nunique() < 4:
            continue
        state = g.set_index("family").state6.to_dict()
        pg = p[(p.date == dt) & (p.universe == u)].set_index("family")
        if pg.empty or len(pg) < 4:
            continue
        nwp = sum(v == "W+" for v in state.values())
        nwm = sum(v == "W-" for v in state.values())
        nrm = sum(v == "R-" for v in state.values())
        pair_den = math.comb(4, 2)
        wplus_pair = math.comb(nwp, 2) / pair_den if nwp >= 2 else 0.0
        conflict_pair = nwp * nrm / pair_den
        spreads20 = pg.spread_20d.astype(float)
        spreads60 = pg.spread_60d.astype(float)
        leader = spreads60.idxmax() if spreads60.notna().sum() >= 3 else None
        leader_strength = float(spreads60.max() - spreads60.median()) if leader is not None else np.nan
        leader_state = state.get(leader) if leader else None
        alts = [state[f] for f in FAMILIES if f != leader and f in state] if leader else []
        leader_rminus = float(leader_state == "R-")
        genuine = float(leader_state == "R-" and any(v == "W+" for v in alts))
        defensive = float(leader_state == "R-" and not any(v == "W+" for v in alts) and any(v == "W-" for v in alts))
        rows.append({
            "date": dt, "universe": u,
            "WPLUS_FAMILY_SHARE": nwp / 4.0, "WMINUS_FAMILY_SHARE": nwm / 4.0,
            "RMINUS_FAMILY_SHARE": nrm / 4.0, "WPLUS_PAIR_SHARE": wplus_pair,
            "CONFLICT_PAIR_SHARE": conflict_pair,
            "LEADER_FAMILY": leader, "LEADER_STATE": leader_state,
            "LEADER_STRENGTH_60D": leader_strength,
            "SPREAD_DISPERSION_20D": float(spreads20.std(ddof=0)),
            "LEADER_RMINUS": leader_rminus, "GENUINE_ROTATION": genuine,
            "DEFENSIVE_ROTATION": defensive,
            "FAMILY_MEMBER_AGREEMENT": float(g.member_same_sign_20d.mean()),
        })
    return pd.DataFrame(rows)


def build_panel() -> pd.DataFrame:
    states = pd.read_csv(FULL / "family_states_static.csv")
    states["date"] = pd.to_datetime(states["date"])
    prim = pd.read_csv(FULL / "family_primitives.csv")
    prim["date"] = pd.to_datetime(prim["date"])
    breadth = pd.read_csv(ABS / "refined_breadth_panel.csv")
    breadth["date"] = pd.to_datetime(breadth["date"])
    market = pd.read_csv(REG / "market_daily_returns.csv", index_col=0)
    market.index = pd.to_datetime(market.index)
    market = market.sort_index()

    dates = states[states.cut_name == MAIN_CUT][["date", "universe"]].drop_duplicates()
    panel = dates.merge(market_context(market), on=["date", "universe"], how="left")
    panel = panel.merge(load_liquidity(), on=["date", "universe"], how="left")
    panel = panel.merge(breadth, on=["date", "universe"], how="left")
    panel = panel.merge(build_family_interactions(states, prim), on=["date", "universe"], how="left")
    panel = panel.sort_values(["universe", "date"]).reset_index(drop=True)
    return panel


def period_name(dt: pd.Timestamp) -> str:
    for name, (lo, hi) in PERIODS.items():
        if lo <= dt < hi:
            return name
    return "OTHER"


def eta_squared(y: pd.Series, groups: pd.Series) -> float:
    z = pd.DataFrame({"y": y, "g": groups}).dropna()
    if len(z) < 20 or z.g.nunique() < 2:
        return np.nan
    overall = z.y.mean()
    ss_total = ((z.y - overall) ** 2).sum()
    if ss_total <= 0:
        return np.nan
    ss_between = sum(len(g) * (g.y.mean() - overall) ** 2 for _, g in z.groupby("g"))
    return float(ss_between / ss_total)


def run_lengths(labels: pd.Series) -> list[int]:
    vals = labels.tolist()
    if not vals:
        return []
    runs, cur, n = [], vals[0], 1
    for v in vals[1:]:
        if v == cur:
            n += 1
        else:
            runs.append(n); cur = v; n = 1
    runs.append(n)
    return runs


def fit_gmm_one(g: pd.DataFrame, features: list[str], k: int):
    train = g[(g.date >= TRAIN_START) & (g.date < TRAIN_END)].dropna(subset=features).copy()
    allz = g.dropna(subset=features).copy()
    if len(train) < max(120, k * 15):
        return None
    scaler = StandardScaler().fit(train[features])
    xt = scaler.transform(train[features])
    xa = scaler.transform(allz[features])
    model = GaussianMixture(n_components=k, covariance_type="diag", n_init=20, random_state=42, reg_covar=1e-5)
    model.fit(xt)
    raw_train = model.predict(xt)
    shares = pd.Series(raw_train).value_counts(normalize=True)
    if shares.min() < MIN_CLUSTER_SHARE:
        return None
    raw_all = model.predict(xa)
    tmp = train[["date", "MKT_RET_60D", "ABS_CONFIRMED_BREADTH"]].copy()
    tmp["raw"] = raw_train
    order = tmp.groupby("raw").agg(trend=("MKT_RET_60D", "mean"), absconf=("ABS_CONFIRMED_BREADTH", "mean")).sort_values(["trend", "absconf"]).index.tolist()
    mapping = {raw: f"S{i+1}" for i, raw in enumerate(order)}
    train["state"] = [mapping[x] for x in raw_train]
    allz["state"] = [mapping[x] for x in raw_all]
    sil = float(silhouette_score(xt, raw_train)) if len(set(raw_train)) > 1 else np.nan
    return scaler, model, train, allz, sil


def cv_base_explains_full(train: pd.DataFrame) -> tuple[float, float]:
    z = train.dropna(subset=BASE_FEATURES + ["state"]).copy()
    if len(z) < 100 or z.state.nunique() < 3:
        return np.nan, np.nan
    x = StandardScaler().fit_transform(z[BASE_FEATURES])
    y = z.state.to_numpy()
    tscv = TimeSeriesSplit(n_splits=5)
    clf = LogisticRegression(max_iter=2000, multi_class="auto")
    scores = cross_val_score(clf, x, y, cv=tscv, scoring="accuracy")
    majority = float(pd.Series(y).value_counts(normalize=True).max())
    return float(scores.mean()), majority


def profile_states(allz: pd.DataFrame, features: list[str], model_type: str, universe: str, k: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    prof = []
    periods = []
    outcomes = []
    allz = allz.copy()
    allz["period"] = allz.date.map(period_name)
    for st, z in allz.groupby("state"):
        tr = z[(z.date >= TRAIN_START) & (z.date < TRAIN_END)]
        row = {"model": model_type, "universe": universe, "k": k, "state": st, "train_n": len(tr), "all_n": len(z)}
        for c in features:
            row[c] = float(tr[c].mean()) if len(tr) else np.nan
        for c in ["MKT_FWD_5D", "MKT_FWD_20D", "MKT_FWD_DD20", "MKT_FWD_VOL20"]:
            row[c] = float(tr[c].mean()) if len(tr) else np.nan
        prof.append(row)
        for per, zp in z.groupby("period"):
            if per == "OTHER":
                continue
            periods.append({"model": model_type, "universe": universe, "k": k, "state": st, "period": per, "n": len(zp),
                            "share_within_period": len(zp) / len(z[z.period == per]) if len(z[z.period == per]) else np.nan,
                            "MKT_FWD_20D": float(zp.MKT_FWD_20D.mean()), "MKT_FWD_DD20": float(zp.MKT_FWD_DD20.mean())})
        for sample, mask in (("TRAIN", z.date < TRAIN_END), ("POST_2023", z.date >= TRAIN_END), ("NORMAL_2023_2024", (z.date >= pd.Timestamp("2023-01-01")) & (z.date < pd.Timestamp("2025-01-01")))):
            q = z[mask]
            if len(q) < 5:
                continue
            outcomes.append({"model": model_type, "universe": universe, "k": k, "state": st, "sample": sample, "n": len(q),
                             "MKT_FWD_5D": float(q.MKT_FWD_5D.mean()), "MKT_FWD_20D": float(q.MKT_FWD_20D.mean()),
                             "MKT_FWD_DD20": float(q.MKT_FWD_DD20.mean()), "MKT_FWD_VOL20": float(q.MKT_FWD_VOL20.mean())})
    return pd.DataFrame(prof), pd.DataFrame(periods), pd.DataFrame(outcomes)


def transitions(allz: pd.DataFrame, model_type: str, universe: str, k: int) -> tuple[pd.DataFrame, dict]:
    z = allz.sort_values("date").copy()
    nxt = z.state.shift(-1)
    rows = []
    for (a, b), n in pd.DataFrame({"a": z.state, "b": nxt}).dropna().value_counts().items():
        den = int((z.state.iloc[:-1] == a).sum())
        rows.append({"model": model_type, "universe": universe, "k": k, "from_state": a, "to_state": b, "n": int(n), "prob": float(n / den) if den else np.nan})
    same = float((z.state.iloc[1:].to_numpy() == z.state.iloc[:-1].to_numpy()).mean()) if len(z) > 1 else np.nan
    runs = run_lengths(z.state)
    metrics = {"persistence": same, "median_run": float(np.median(runs)) if runs else np.nan, "mean_run": float(np.mean(runs)) if runs else np.nan}
    return pd.DataFrame(rows), metrics


def compare_same_market_states(train: pd.DataFrame, universe: str) -> pd.DataFrame:
    scaler = StandardScaler().fit(train[FULL_FEATURES])
    zvals = pd.DataFrame(scaler.transform(train[FULL_FEATURES]), columns=FULL_FEATURES, index=train.index)
    zvals["state"] = train.state.values
    cent = zvals.groupby("state").mean()
    outcome = train.groupby("state")[["MKT_FWD_20D", "MKT_FWD_DD20"]].mean()
    rows = []
    for a, b in itertools.combinations(cent.index, 2):
        base_dist = float(np.linalg.norm(cent.loc[a, BASE_FEATURES] - cent.loc[b, BASE_FEATURES]))
        factor_dist = float(np.linalg.norm(cent.loc[a, FACTOR_FEATURES] - cent.loc[b, FACTOR_FEATURES]))
        if base_dist <= 1.5 and factor_dist >= 1.5:
            rows.append({"universe": universe, "state_a": a, "state_b": b, "base_distance_z": base_dist, "factor_distance_z": factor_dist,
                         "fwd20_a": outcome.at[a, "MKT_FWD_20D"], "fwd20_b": outcome.at[b, "MKT_FWD_20D"],
                         "fwd20_diff": outcome.at[a, "MKT_FWD_20D"] - outcome.at[b, "MKT_FWD_20D"],
                         "fwd_dd20_a": outcome.at[a, "MKT_FWD_DD20"], "fwd_dd20_b": outcome.at[b, "MKT_FWD_DD20"]})
    return pd.DataFrame(rows)


def fit_models(panel: pd.DataFrame):
    assignments, profiles, period_rows, outcomes, trans, diagnostics, same_market = [], [], [], [], [], [], []
    for u, g0 in panel.groupby("universe"):
        g = g0.sort_values("date").copy()
        for model_type, features in (("BASE", BASE_FEATURES), ("FULL", FULL_FEATURES)):
            for k in K_GRID:
                fit = fit_gmm_one(g, features, k)
                if fit is None:
                    continue
                scaler, model, tr, allz, sil = fit
                bic = float(model.bic(scaler.transform(tr[features])))
                tdf, tm = transitions(allz, model_type, u, k)
                post = allz[allz.date >= TRAIN_END]
                diag = {"model": model_type, "universe": u, "k": k, "train_n": len(tr), "bic": bic, "silhouette_train": sil,
                        "persistence_all": tm["persistence"], "median_run_all": tm["median_run"],
                        "eta2_fwd20_post": eta_squared(post.MKT_FWD_20D, post.state), "eta2_fwd_dd20_post": eta_squared(post.MKT_FWD_DD20, post.state)}
                if model_type == "FULL" and k == PRIMARY_K:
                    acc, maj = cv_base_explains_full(tr)
                    diag["base_cv_accuracy_for_full_state"] = acc
                    diag["base_majority_accuracy"] = maj
                    sm = compare_same_market_states(tr, u)
                    if not sm.empty:
                        same_market.append(sm)
                diagnostics.append(diag)
                if k != PRIMARY_K:
                    continue
                keep = allz[["date", "universe", "state"] + features + ["MKT_FWD_5D", "MKT_FWD_20D", "MKT_FWD_DD20", "MKT_FWD_VOL20"]].copy()
                keep.insert(0, "model", model_type)
                assignments.append(keep)
                p, pr, o = profile_states(allz, features, model_type, u, k)
                profiles.append(p); period_rows.append(pr); outcomes.append(o); trans.append(tdf)
    return (
        pd.concat(assignments, ignore_index=True) if assignments else pd.DataFrame(),
        pd.concat(profiles, ignore_index=True) if profiles else pd.DataFrame(),
        pd.concat(period_rows, ignore_index=True) if period_rows else pd.DataFrame(),
        pd.concat(outcomes, ignore_index=True) if outcomes else pd.DataFrame(),
        pd.concat(trans, ignore_index=True) if trans else pd.DataFrame(),
        pd.DataFrame(diagnostics),
        pd.concat(same_market, ignore_index=True) if same_market else pd.DataFrame(),
    )


def fit_rule_states(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for u, g0 in panel.groupby("universe"):
        g = g0.dropna(subset=FULL_FEATURES).sort_values("date").copy()
        tr = g[(g.date >= TRAIN_START) & (g.date < TRAIN_END)]
        if len(tr) < 150:
            continue
        q = {}
        for c in ["MKT_RET_60D", "LIQ_5D_20D", "ABS_CONFIRMED_BREADTH", "DEFENSIVE_WORKING_BREADTH", "LEADER_STRENGTH_60D"]:
            q[c] = tr[c].quantile([1/3, 2/3]).to_dict()
        for r in g.itertuples():
            trend_up = r.MKT_RET_60D >= q["MKT_RET_60D"][2/3]
            trend_down = r.MKT_RET_60D <= q["MKT_RET_60D"][1/3]
            part_high = r.LIQ_5D_20D >= q["LIQ_5D_20D"][2/3]
            part_low = r.LIQ_5D_20D <= q["LIQ_5D_20D"][1/3]
            abs_high = r.ABS_CONFIRMED_BREADTH >= q["ABS_CONFIRMED_BREADTH"][2/3]
            abs_low = r.ABS_CONFIRMED_BREADTH <= q["ABS_CONFIRMED_BREADTH"][1/3]
            def_high = r.DEFENSIVE_WORKING_BREADTH >= q["DEFENSIVE_WORKING_BREADTH"][2/3]
            leader_high = r.LEADER_STRENGTH_60D >= q["LEADER_STRENGTH_60D"][2/3]
            if r.GENUINE_ROTATION > 0:
                state = "ROTATION"
            elif trend_up and part_high and abs_high:
                state = "BROAD_EXPANSION"
            elif trend_up and leader_high and (part_low or abs_low):
                state = "CONCENTRATED_TREND"
            elif trend_down and (def_high or r.LEADER_RMINUS > 0):
                state = "DEFENSIVE_WEAKNESS"
            elif trend_down:
                state = "BROAD_WEAKNESS"
            elif trend_up:
                state = "OTHER_UPTREND"
            else:
                state = "MIXED"
            rows.append({"date": r.date, "universe": u, "state": state, "MKT_FWD_5D": r.MKT_FWD_5D, "MKT_FWD_20D": r.MKT_FWD_20D,
                         "MKT_FWD_DD20": r.MKT_FWD_DD20, "MKT_RET_60D": r.MKT_RET_60D, "LIQ_5D_20D": r.LIQ_5D_20D,
                         "ABS_CONFIRMED_BREADTH": r.ABS_CONFIRMED_BREADTH, "DEFENSIVE_WORKING_BREADTH": r.DEFENSIVE_WORKING_BREADTH,
                         "LEADER_STRENGTH_60D": r.LEADER_STRENGTH_60D})
    return pd.DataFrame(rows)


def summarize_rule(rule: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (u, st), g in rule.groupby(["universe", "state"]):
        for sample, mask in (("TRAIN", g.date < TRAIN_END), ("POST_2023", g.date >= TRAIN_END), ("NORMAL_2023_2024", (g.date >= pd.Timestamp("2023-01-01")) & (g.date < pd.Timestamp("2025-01-01")))):
            z = g[mask]
            if len(z) < 5:
                continue
            rows.append({"universe": u, "state": st, "sample": sample, "n": len(z), "ret60": float(z.MKT_RET_60D.mean()),
                         "liq": float(z.LIQ_5D_20D.mean()), "abs_confirmed": float(z.ABS_CONFIRMED_BREADTH.mean()),
                         "defensive": float(z.DEFENSIVE_WORKING_BREADTH.mean()), "leader_strength": float(z.LEADER_STRENGTH_60D.mean()),
                         "fwd5": float(z.MKT_FWD_5D.mean()), "fwd20": float(z.MKT_FWD_20D.mean()), "fwd_dd20": float(z.MKT_FWD_DD20.mean())})
    return pd.DataFrame(rows)


def write_summary(diag: pd.DataFrame, outcomes: pd.DataFrame, period: pd.DataFrame, same_market: pd.DataFrame, rule_sum: pd.DataFrame) -> str:
    lines = [
        "# Contemporaneous Market-Regime Research", "",
        "Regimes are fit without any forward return, future drawdown, or calendar-year label. The state vector uses only information observable through each state date.",
        "Primary comparison is a fixed 5-state GMM: BASE = market trend/volatility/drawdown + 5D-vs-20D trading-value breadth; FULL adds factor absolute/relative breadth, family W+/W-/R- interaction, leader strength, dispersion, and leader-rotation flags.",
        "Models are fit on 2016-2022 and frozen for 2023 onward. K=3..6 BIC is robustness only. Future returns/downside are attached only after state assignment.", "",
        "## Incremental diagnostics: FULL vs BASE, fixed K=5", "",
    ]
    d = diag[diag.k == PRIMARY_K].copy()
    for u in sorted(d.universe.unique()):
        b = d[(d.universe == u) & (d.model == "BASE")]
        f = d[(d.universe == u) & (d.model == "FULL")]
        if b.empty or f.empty:
            continue
        b, f = b.iloc[0], f.iloc[0]
        lines.append(f"- {u}: silhouette BASE {b.silhouette_train:.2f} vs FULL {f.silhouette_train:.2f}; persistence {b.persistence_all:.0%} vs {f.persistence_all:.0%}; post-2023 eta2 next20 {b.eta2_fwd20_post:.2f} vs {f.eta2_fwd20_post:.2f}; eta2 downside {b.eta2_fwd_dd20_post:.2f} vs {f.eta2_fwd_dd20_post:.2f}; BASE-only CV accuracy for FULL states {f.get('base_cv_accuracy_for_full_state', np.nan):.0%} vs majority {f.get('base_majority_accuracy', np.nan):.0%}")
    lines += ["", "## FULL-state outcomes by universe (fixed K=5)", ""]
    z = outcomes[(outcomes.model == "FULL") & (outcomes.sample.isin(["TRAIN", "NORMAL_2023_2024", "POST_2023"]))].copy()
    for u in sorted(z.universe.unique()):
        lines.append(f"### {u}")
        for sample in ["TRAIN", "NORMAL_2023_2024", "POST_2023"]:
            q = z[(z.universe == u) & (z["sample"] == sample)].sort_values("state")
            if q.empty:
                continue
            desc = "; ".join(f"{r.state}: n={int(r.n)}, +20D {r.MKT_FWD_20D:+.2%}, fwdDD {r.MKT_FWD_DD20:+.2%}" for r in q.itertuples())
            lines.append(f"- {sample}: {desc}")
    lines += ["", "## Calendar-period composition of FULL states", ""]
    pp = period[period.model == "FULL"].copy()
    for u in [x for x in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"] if x in pp.universe.unique()]:
        lines.append(f"### {u}")
        for per in PERIODS:
            q = pp[(pp.universe == u) & (pp.period == per)].sort_values("share_within_period", ascending=False)
            if q.empty:
                continue
            top = ", ".join(f"{r.state} {r.share_within_period:.0%}" for r in q.head(3).itertuples())
            lines.append(f"- {per}: {top}")
    lines += ["", "## Same-market / different-factor state pairs in TRAIN", ""]
    if same_market.empty:
        lines.append("- None met the predeclared centroid-distance screen (base distance <=1.5z and factor distance >=1.5z).")
    else:
        for _, r in same_market.sort_values("factor_distance_z", ascending=False).head(20).iterrows():
            lines.append(f"- {r.universe} {r.state_a}/{r.state_b}: base distance {r.base_distance_z:.2f}z, factor distance {r.factor_distance_z:.2f}z; next20 difference {r.fwd20_diff:+.2%}")
    lines += ["", "## Rule-based archetype check", ""]
    rr = rule_sum[rule_sum["sample"] == "NORMAL_2023_2024"].copy()
    for u in [x for x in ["K200", "KOSPI_ALL", "KOSPI_EX_K200", "KOSDAQ"] if x in rr.universe.unique()]:
        q = rr[rr.universe == u].sort_values("n", ascending=False)
        desc = "; ".join(f"{r.state} n={int(r.n)} +20D={r.fwd20:+.2%}" for r in q.itertuples())
        lines.append(f"- {u}: {desc}")
    lines += ["", "## Interpretation discipline", "",
              "- A useful contemporaneous regime representation should create persistent, economically distinct states without using future outcomes to define them.",
              "- Factor interaction is incremental only if FULL creates economically meaningful distinctions not recoverable from BASE market/liquidity features alone, and those distinctions persist out of sample.",
              "- State IDs are ordered by TRAIN 60D market return, not named ex post as bull/bear. Economic labels should be attached only after profile inspection.",
              "- 2023+ is post-discovery validation; 2025 and 2026 are reported separately in period composition rather than pooled into one OOS average.", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    panel = build_panel()
    panel.to_csv(OUT / "contemporaneous_state_vector.csv", index=False, encoding="utf-8-sig")
    assignments, profiles, periods, outcomes, trans, diag, same_market = fit_models(panel)
    rule = fit_rule_states(panel)
    rule_sum = summarize_rule(rule)

    assignments.to_csv(OUT / "gmm_state_assignments.csv", index=False, encoding="utf-8-sig")
    profiles.to_csv(OUT / "gmm_state_profiles.csv", index=False, encoding="utf-8-sig")
    periods.to_csv(OUT / "gmm_period_composition.csv", index=False, encoding="utf-8-sig")
    outcomes.to_csv(OUT / "gmm_state_outcomes.csv", index=False, encoding="utf-8-sig")
    trans.to_csv(OUT / "gmm_transition_matrix.csv", index=False, encoding="utf-8-sig")
    diag.to_csv(OUT / "gmm_model_diagnostics.csv", index=False, encoding="utf-8-sig")
    same_market.to_csv(OUT / "same_market_different_factor_states.csv", index=False, encoding="utf-8-sig")
    rule.to_csv(OUT / "rule_state_assignments.csv", index=False, encoding="utf-8-sig")
    rule_sum.to_csv(OUT / "rule_state_summary.csv", index=False, encoding="utf-8-sig")
    (OUT / "RESEARCH_SUMMARY.md").write_text(write_summary(diag, outcomes, periods, same_market, rule_sum), encoding="utf-8")
    print(f"state vector rows: {len(panel):,}")
    print(f"GMM assignments: {len(assignments):,}")
    print(f"same-market factor splits: {len(same_market):,}")


if __name__ == "__main__":
    main()
