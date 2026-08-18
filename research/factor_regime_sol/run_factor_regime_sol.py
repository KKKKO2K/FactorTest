from __future__ import annotations

import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
WM_DIR = ROOT / "research" / "weighted_momentum_filter_sol"
sys.path.insert(0, str(WM_DIR))
import run_weighted_momentum_filter as wm  # noqa: E402

DATA = ROOT / "source" / "factor_all_values"
OUT = Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

START = pd.Timestamp("2016-01-01")
SPLIT = pd.Timestamp("2023-01-01")
STEP = 5
HOLD = 5
Q_SIDE = 0.20
MCAP_CUTOFF_BN = 250.0
HORIZONS = (1, 5, 20)
CUT_Q = 1.0 / 3.0

UNIVERSES = wm.UNIVERSES
FAMILY_ORDER = ("MOMENTUM", "REVISION", "VALUE", "FLOW")
FACTOR_DIRS = {
    "OP12": DATA / "OP(12MF_1M_CHG)",
    "OPFY1": DATA / "OP(FY1_1M_CHG)",
    "PBR": DATA / "PBR(12MF)",
    "PER": DATA / "PER(12MF)",
    "PRIVATE": DATA / "사모수급",
    "FOREIGN": DATA / "외국인수급",
}
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")

SAMPLES = {
    "TRAIN_2016_2022": (pd.Timestamp("2016-01-01"), pd.Timestamp("2022-12-31")),
    "POST_2023_PLUS": (pd.Timestamp("2023-01-01"), pd.Timestamp("2099-12-31")),
    "POST_2023_2024": (pd.Timestamp("2023-01-01"), pd.Timestamp("2024-12-31")),
    "BULL_2025": (pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    "YTD_2026": (pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")),
}


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out = {}
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def load_factor(path: Path) -> pd.Series:
    df = wm.read_csv(path)
    cc = wm.find_col(df, exact=("StockCode", "Code", "종목코드"))
    vc = wm.find_col(df, exact=("FactorValue",), contains=("FactorValue", "factor value"))
    if cc is None or vc is None:
        raise ValueError(f"factor schema not found: {path}")
    s = pd.Series(pd.to_numeric(df[vc], errors="coerce").to_numpy(), index=wm.normalize_code(df[cc]))
    return s[~s.index.duplicated(keep="last")]


def pct_good(s: pd.Series, high_good: bool = True) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    # Larger rank is always economically better.
    return x.rank(pct=True, method="average", ascending=high_good)


def fwd_compound(returns: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(returns.clip(lower=-0.999999).fillna(0.0))
    return np.expm1(sum(logs.shift(-i) for i in range(1, h + 1)))


def row_compound(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return (1.0 + df).rolling(n, min_periods=n).apply(np.prod, raw=True) - 1.0


def forward_market(mkt: pd.DataFrame, h: int) -> pd.DataFrame:
    logs = np.log1p(mkt.clip(lower=-0.999999).fillna(0.0))
    return np.expm1(sum(logs.shift(-i) for i in range(1, h + 1)))


def make_market_returns(returns, mcap, k200_by_date, market_by_date):
    rows = []
    dates = list(returns.index)
    for i in range(1, len(dates)):
        dt, prev = dates[i], dates[i - 1]
        if prev not in k200_by_date or prev not in market_by_date or prev not in mcap.index:
            continue
        for u in UNIVERSES:
            codes = wm.universe_codes(u, prev, k200_by_date, market_by_date)
            r = pd.to_numeric(returns.loc[dt].reindex(codes), errors="coerce")
            w = pd.to_numeric(mcap.loc[prev].reindex(codes), errors="coerce")
            z = pd.concat([r.rename("r"), w.rename("w")], axis=1).dropna()
            z = z[z.w > 0]
            if len(z) < 30:
                continue
            rows.append({"date": dt, "universe": u, "return": float((z.r * z.w).sum() / z.w.sum())})
    return pd.DataFrame(rows).pivot(index="date", columns="universe", values="return").sort_index()


def composite_scores(dt, elig, wmom, files):
    w = pd.to_numeric(wmom.loc[dt].reindex(elig), errors="coerce")
    raw = {k: load_factor(v[dt]).reindex(elig) for k, v in files.items()}
    revision = pd.concat([pct_good(raw["OP12"], True), pct_good(raw["OPFY1"], True)], axis=1).mean(axis=1, skipna=False)
    value = pd.concat([pct_good(raw["PBR"], False), pct_good(raw["PER"], False)], axis=1).mean(axis=1, skipna=False)
    flow = pd.concat([pct_good(raw["PRIVATE"], True), pct_good(raw["FOREIGN"], True)], axis=1).mean(axis=1, skipna=False)
    return {
        "MOMENTUM": pct_good(w, True),
        "REVISION": revision,
        "VALUE": value,
        "FLOW": flow,
    }


def build_factor_5d(returns, mcap, k200_by_date, market_by_date, wmom):
    files = {k: dated_files(p) for k, p in FACTOR_DIRS.items()}
    common = set(returns.index) & set(mcap.index) & set(k200_by_date) & set(market_by_date)
    for x in files.values():
        common &= set(x)
    dates = sorted(d for d in common if d >= START)
    signal_dates = dates[::STEP]
    fwd5 = fwd_compound(returns, HOLD)
    rows = []
    for i, dt in enumerate(signal_dates, 1):
        if dt not in fwd5.index or dt not in wmom.index:
            continue
        for u in UNIVERSES:
            codes = wm.universe_codes(u, dt, k200_by_date, market_by_date)
            mc = pd.to_numeric(mcap.loc[dt].reindex(codes), errors="coerce")
            elig = mc.index[(mc >= MCAP_CUTOFF_BN).fillna(False)]
            if len(elig) < 40:
                continue
            fam = composite_scores(dt, elig, wmom, files)
            y = pd.to_numeric(fwd5.loc[dt].reindex(elig), errors="coerce")
            for f, score in fam.items():
                z = pd.concat([score.rename("score"), y.rename("y")], axis=1).dropna().sort_values("score", ascending=False)
                n = int(math.floor(len(z) * Q_SIDE))
                if n < 8:
                    continue
                top, bot = z.head(n), z.tail(n)
                rows.append({
                    "signal_date": dt,
                    "date": returns.index[min(returns.index.get_loc(dt) + HOLD, len(returns.index) - 1)],
                    "universe": u,
                    "family": f,
                    "top_abs_5d": float(top.y.mean()),
                    "bottom_abs_5d": float(bot.y.mean()),
                    "spread_5d": float(top.y.mean() - bot.y.mean()),
                    "n_side": n,
                })
        if i % 100 == 0:
            print(f"factor periods {i}/{len(signal_dates)}", flush=True)
    return pd.DataFrame(rows)


def build_state_panel(f5):
    rows, cuts = [], []
    for u, g in f5.groupby("universe"):
        top5 = g.pivot(index="date", columns="family", values="top_abs_5d").sort_index()
        bot5 = g.pivot(index="date", columns="family", values="bottom_abs_5d").sort_index()
        spr5 = g.pivot(index="date", columns="family", values="spread_5d").sort_index()
        top20, bot20 = row_compound(top5, 4), row_compound(bot5, 4)
        spread20 = top20 - bot20
        family_cut = {}
        for f in FAMILY_ORDER:
            if f not in spread20.columns:
                continue
            tr = spread20.loc[spread20.index < SPLIT, f].dropna()
            c = float(tr.abs().quantile(CUT_Q)) if len(tr) >= 40 else np.nan
            if np.isfinite(c) and c > 0:
                family_cut[f] = c
                cuts.append({"universe": u, "family": f, "cut_q": CUT_Q, "abs_spread_cut": c, "train_n": len(tr)})
        corr60 = spr5.rolling(12, min_periods=8).corr()
        for dt in spread20.index:
            states = {}
            vals = {}
            for f, c in family_cut.items():
                rel = spread20.at[dt, f]
                ta = top20.at[dt, f]
                ba = bot20.at[dt, f]
                if not np.isfinite(rel) or not np.isfinite(ta) or not np.isfinite(ba):
                    continue
                rs = "WORKING" if rel >= c else ("REVERSE" if rel <= -c else "NEUTRAL")
                if rs == "WORKING": state = "W+" if ta > 0 else "W-"
                elif rs == "REVERSE": state = "R+" if ta > 0 else "R-"
                else: state = "N"
                states[f] = state
                vals[f] = (float(ta), float(ba), float(rel), rs)
            if len(vals) < 4:
                continue
            # Average pairwise 60D correlation of 5D family spreads.
            hist = spr5.loc[:dt].tail(12)
            cmat = hist.corr(min_periods=8)
            arr = cmat.to_numpy()[np.triu_indices(len(cmat), 1)] if len(cmat) >= 2 else np.array([])
            arr = arr[np.isfinite(arr)]
            avgcorr = float(arr.mean()) if len(arr) else np.nan
            sprs = pd.Series({f: vals[f][2] for f in vals})
            tops = pd.Series({f: vals[f][0] for f in vals})
            mom_state = states["MOMENTUM"]
            other_pos = float((tops.drop("MOMENTUM") > 0).mean())
            other_work = float(pd.Series({f: states[f].startswith("W") for f in states if f != "MOMENTUM"}).mean())
            if mom_state == "R-" and other_pos >= 2/3:
                meta = "MOM_RISK_ROTATION_SUPPORT"
            elif mom_state == "R-" and other_pos <= 1/3:
                meta = "MOM_BROAD_RISK_OFF"
            elif mom_state == "R+" and other_pos >= 2/3:
                meta = "BULLISH_STYLE_SHIFT"
            elif mom_state == "W+" and other_pos >= 2/3:
                meta = "BROAD_CONFIRMATION"
            else:
                meta = "OTHER"
            row = {
                "date": dt, "universe": u,
                "positive_abs_breadth": float((tops > 0).mean()),
                "working_breadth": float(np.mean([states[f].startswith("W") for f in states])),
                "abs_confirmed_breadth": float(np.mean([states[f] == "W+" for f in states])),
                "bearish_reverse_breadth": float(np.mean([states[f] == "R-" for f in states])),
                "other_positive_abs_breadth": other_pos,
                "other_working_breadth": other_work,
                "spread_dispersion": float(sprs.std(ddof=1)),
                "avg_corr_60d": avgcorr,
                "mom_state": mom_state,
                "meta_state": meta,
            }
            for f in FAMILY_ORDER:
                row[f"{f.lower()}_state"] = states[f]
                row[f"{f.lower()}_top_abs20"] = vals[f][0]
                row[f"{f.lower()}_spread20"] = vals[f][2]
            rows.append(row)
    return pd.DataFrame(rows), pd.DataFrame(cuts)


def nw_tstat_mean(x: pd.Series, maxlags: int) -> float:
    x = pd.Series(x).dropna().astype(float).to_numpy()
    n = len(x)
    if n < 8:
        return np.nan
    e = x - x.mean()
    gamma0 = float(np.dot(e, e) / n)
    s = gamma0
    L = min(maxlags, n - 2)
    for l in range(1, L + 1):
        gamma = float(np.dot(e[l:], e[:-l]) / n)
        weight = 1.0 - l / (L + 1.0)
        s += 2.0 * weight * gamma
    se = math.sqrt(max(s, 0.0) / n)
    return float(x.mean() / se) if se > 0 else np.nan


def summarize_states(panel, market):
    fwd = {h: forward_market(market, h) for h in HORIZONS}
    rows = []
    for u, g in panel.groupby("universe"):
        for sample, (lo, hi) in SAMPLES.items():
            z0 = g[(g.date >= lo) & (g.date <= hi)]
            for state, z in z0.groupby("meta_state"):
                if state == "OTHER" or len(z) < 8:
                    continue
                for h in HORIZONS:
                    if u not in fwd[h].columns:
                        continue
                    x = z.date.map(fwd[h][u]).dropna()
                    if len(x) < 8:
                        continue
                    rows.append({
                        "sample": sample, "universe": u, "state": state, "horizon": h,
                        "n": len(x), "mean": float(x.mean()), "median": float(x.median()),
                        "positive_share": float((x > 0).mean()), "nw_tstat_mean": nw_tstat_mean(x, max(1, int(math.ceil(h / STEP)))),
                    })
    return pd.DataFrame(rows)


def summarize_breadth(panel, market):
    fwd = {h: forward_market(market, h) for h in HORIZONS}
    vars_ = ("positive_abs_breadth", "abs_confirmed_breadth", "bearish_reverse_breadth", "spread_dispersion", "avg_corr_60d")
    rows = []
    for u, g in panel.groupby("universe"):
        train = g[g.date < SPLIT]
        for v in vars_:
            x = train[v].dropna()
            if len(x) < 40 or x.nunique() < 3:
                continue
            q1, q2 = x.quantile([1/3, 2/3]).tolist()
            gg = g[g[v].notna()].copy()
            gg["bin"] = np.where(gg[v] <= q1, "LOW", np.where(gg[v] >= q2, "HIGH", "MID"))
            for sample, (lo, hi) in SAMPLES.items():
                s = gg[(gg.date >= lo) & (gg.date <= hi)]
                for h in HORIZONS:
                    if u not in fwd[h].columns:
                        continue
                    ss = s.copy(); ss["fwd"] = ss.date.map(fwd[h][u])
                    lo_x = ss[ss.bin == "LOW"].fwd.dropna(); hi_x = ss[ss.bin == "HIGH"].fwd.dropna()
                    if len(lo_x) < 8 or len(hi_x) < 8:
                        continue
                    rows.append({
                        "sample": sample, "universe": u, "variable": v, "horizon": h,
                        "train_q1": q1, "train_q2": q2, "n_low": len(lo_x), "n_high": len(hi_x),
                        "low_mean": float(lo_x.mean()), "high_mean": float(hi_x.mean()),
                        "high_minus_low": float(hi_x.mean() - lo_x.mean()),
                    })
    return pd.DataFrame(rows)


def correlation_summary(f5):
    rows = []
    for u, g in f5.groupby("universe"):
        x = g.pivot(index="date", columns="family", values="spread_5d").sort_index()
        for sample, (lo, hi) in SAMPLES.items():
            z = x[(x.index >= lo) & (x.index <= hi)]
            c = z.corr(min_periods=20)
            for i, a in enumerate(c.columns):
                for b in c.columns[i+1:]:
                    rows.append({"sample": sample, "universe": u, "family_a": a, "family_b": b, "corr": float(c.loc[a,b])})
    return pd.DataFrame(rows)


def write_summary(state_res, breadth_res, corr):
    focus = ["K200", "KOSPI_EX_K200", "KOSDAQ", "KOSDAQ_PLUS_KOSPI_EX_K200"]
    lines = [
        "# Exact Weighted-Momentum Factor Regime Research", "",
        "Momentum = exact legacy weighted momentum. Revision/Value/Flow are equal-weight rank composites of their two source factors.",
        "Factor legs = top/bottom 20% within universe after KRW 250bn market-cap cutoff, refreshed every 5 trading days.",
        "20D state compounds four realized 5D preferred/opposite legs. State thresholds use TRAIN absolute-spread Q33 and are frozen for 2023+.",
        "State date is after the 20D history is observed; market outcomes start at t+1. 2023+ is post-discovery validation, not untouched OOS.", "",
        "Meta states: MOM_RISK_ROTATION_SUPPORT = Momentum R- while >=2/3 of Revision/Value/Flow preferred legs remain positive; MOM_BROAD_RISK_OFF = Momentum R- while <=1/3 remain positive.", "",
    ]
    for sample in ("TRAIN_2016_2022", "POST_2023_PLUS", "POST_2023_2024", "BULL_2025", "YTD_2026"):
        lines += [f"## {sample}", "", "| Universe | State | n | +5D mean | +5D pos | +20D mean | +20D pos |", "|---|---|---:|---:|---:|---:|---:|"]
        for u in focus:
            q = state_res[(state_res.sample == sample) & (state_res.universe == u)]
            for st in ("MOM_RISK_ROTATION_SUPPORT", "MOM_BROAD_RISK_OFF", "BULLISH_STYLE_SHIFT", "BROAD_CONFIRMATION"):
                a = q[(q.state == st) & (q.horizon == 5)]
                b = q[(q.state == st) & (q.horizon == 20)]
                if a.empty or b.empty: continue
                aa, bb = a.iloc[0], b.iloc[0]
                lines.append(f"| {u} | {st} | {int(min(aa.n,bb.n))} | {aa['mean']:+.2%} | {aa.positive_share:.1%} | {bb['mean']:+.2%} | {bb.positive_share:.1%} |")
        lines.append("")
    lines += ["## Breadth high-minus-low, POST_2023_PLUS (+20D)", "", "| Universe | Variable | H-L |", "|---|---|---:|"]
    q = breadth_res[(breadth_res.sample == "POST_2023_PLUS") & (breadth_res.horizon == 20)]
    for u in focus:
        for v in ("positive_abs_breadth", "abs_confirmed_breadth", "bearish_reverse_breadth", "spread_dispersion", "avg_corr_60d"):
            z = q[(q.universe == u) & (q.variable == v)]
            if not z.empty: lines.append(f"| {u} | {v} | {z.iloc[0].high_minus_low:+.2%} |")
    lines += ["", "## Family spread correlations, POST_2023_PLUS", "", "| Universe | Pair | Corr |", "|---|---|---:|"]
    q = corr[corr.sample == "POST_2023_PLUS"]
    for u in focus:
        for _, r in q[q.universe == u].sort_values("corr").iterrows():
            lines.append(f"| {u} | {r.family_a} × {r.family_b} | {r['corr']:+.2f} |")
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    returns, mcap, k200_by_date, market_by_date = wm.load_basic()
    wmom, _ = wm.calendar_weighted_momentum(returns, mcap)
    print(f"basic loaded returns={returns.shape}; wmom={wmom.shape}", flush=True)
    f5 = build_factor_5d(returns, mcap, k200_by_date, market_by_date, wmom)
    f5.to_csv(OUT / "family_factor_5d.csv", index=False, encoding="utf-8-sig")
    panel, cuts = build_state_panel(f5)
    panel.to_csv(OUT / "state_panel.csv", index=False, encoding="utf-8-sig")
    cuts.to_csv(OUT / "state_thresholds.csv", index=False, encoding="utf-8-sig")
    market = make_market_returns(returns, mcap, k200_by_date, market_by_date)
    market.to_csv(OUT / "market_daily_returns.csv", encoding="utf-8-sig")
    state_res = summarize_states(panel, market)
    breadth_res = summarize_breadth(panel, market)
    corr = correlation_summary(f5)
    state_res.to_csv(OUT / "state_market_results.csv", index=False, encoding="utf-8-sig")
    breadth_res.to_csv(OUT / "breadth_market_results.csv", index=False, encoding="utf-8-sig")
    corr.to_csv(OUT / "family_spread_correlations.csv", index=False, encoding="utf-8-sig")
    write_summary(state_res, breadth_res, corr)
    print(f"done factor5={len(f5):,}; states={len(panel):,}; market_days={len(market):,}", flush=True)


if __name__ == "__main__":
    main()
