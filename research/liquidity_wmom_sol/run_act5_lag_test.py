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
TRADING = DATA / "reference_snapshots" / "trading_amount"
OUT = Path(__file__).resolve().parent / "results_act5_lag_test"
OUT.mkdir(parents=True, exist_ok=True)

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
H = 10
TOPN = 20
MCAP_CUTOFF_BN = 250.0
COSTS_BP = (30, 60)
UNIVERSES = wm.UNIVERSES
PERIODS = wm.PERIODS
FACTORS = ("WEIGHTED_MOM", "WEIGHTED_MOM_R1M_GE0")
OVERLAYS = ("BASE", "ACT5_T_KEEP_TOP70", "ACT5_LAG1_KEEP_TOP70")


def dated_files(folder: Path):
    out = {}
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def load_ta():
    rows = []
    for i, (dt, p) in enumerate(dated_files(TRADING).items(), 1):
        df = wm.read_csv(p)
        cc = wm.find_col(df, exact=("Code", "StockCode", "종목코드"))
        vc = wm.find_col(df, exact=("거래대금(십억원)",), contains=("거래대금", "trading"))
        if cc is None or vc is None:
            continue
        rows.append(pd.DataFrame({
            "date": dt,
            "code": wm.normalize_code(df[cc]),
            "value": pd.to_numeric(df[vc], errors="coerce"),
        }))
        if i % 500 == 0:
            print(f"loaded TA {i}", flush=True)
    if not rows:
        raise RuntimeError("No trading amount data")
    return pd.concat(rows, ignore_index=True).pivot(index="date", columns="code", values="value").sort_index()


def pct_rank(s, high_good=True):
    return pd.to_numeric(s, errors="coerce").rank(pct=True, method="average", ascending=high_good)


def fwd10(returns):
    logs = np.log1p(returns.clip(lower=-0.999999).fillna(0.0))
    return np.expm1(sum(logs.shift(-i) for i in range(1, H + 1)))


def ann(r):
    r = pd.Series(r).dropna()
    return float((1 + r).prod() ** ((252 / H) / len(r)) - 1) if len(r) else np.nan


def sharpe(r):
    r = pd.Series(r).dropna()
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(252 / H)) if len(r) >= 3 and np.isfinite(sd) and sd > 0 else np.nan


def mdd(r):
    r = pd.Series(r).dropna()
    nav = (1 + r).cumprod()
    return float((nav / nav.cummax() - 1).min()) if len(nav) else np.nan


def select(score):
    s = score.replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)
    return s.head(TOPN).index.tolist() if len(s) >= TOPN else []


def turnover(old, new):
    return 1.0 if not old else float(1 - len(set(old) & set(new)) / TOPN)


def main():
    returns, mcap, k200_by_date, market_by_date = wm.load_basic()
    ta = load_ta().reindex(index=mcap.index, columns=mcap.columns)
    wmom, r1m = wm.calendar_weighted_momentum(returns, mcap)

    raw = ta.where(ta > 0)
    recent5 = raw.rolling(5, min_periods=4).mean()
    prior20 = raw.shift(5).rolling(20, min_periods=15).mean()
    act5_t = recent5 / prior20
    # Strict timing robustness: only the ACT5 value known at the PRIOR trading-date close.
    act5_lag1 = act5_t.shift(1)

    fwd = fwd10(returns)
    common = sorted(set(returns.index) & set(mcap.index) & set(raw.index) & set(k200_by_date) & set(market_by_date))
    common = [d for d in common if d >= pd.Timestamp("2017-01-01")]
    phase_map = {d: i % H for i, d in enumerate(common)}

    current = {}
    rows = []
    diag = []

    for i, dt in enumerate(common, 1):
        if dt not in fwd.index:
            continue
        phase = phase_map[dt]
        mcfull = pd.to_numeric(mcap.loc[dt], errors="coerce")

        for u in UNIVERSES:
            codes = wm.universe_codes(u, dt, k200_by_date, market_by_date)
            mc = mcfull.reindex(codes)
            elig = mc.index[(mc >= MCAP_CUTOFF_BN).fillna(False)]
            if len(elig) < 40:
                continue

            w = pd.to_numeric(wmom.loc[dt].reindex(elig), errors="coerce")
            rr = pd.to_numeric(r1m.loc[dt].reindex(elig), errors="coerce")
            factor_scores = {
                "WEIGHTED_MOM": pct_rank(w, True),
                "WEIGHTED_MOM_R1M_GE0": pct_rank(w.where(rr >= 0), True),
            }

            a5t = pd.to_numeric(act5_t.loc[dt].reindex(elig), errors="coerce")
            a5l = pd.to_numeric(act5_lag1.loc[dt].reindex(elig), errors="coerce")
            a5t_r = pct_rank(a5t, True)
            a5l_r = pct_rank(a5l, True)
            y = fwd.loc[dt].reindex(elig)

            for f, base in factor_scores.items():
                ovs = {
                    "BASE": base,
                    "ACT5_T_KEEP_TOP70": base.where(a5t_r >= 0.30),
                    "ACT5_LAG1_KEEP_TOP70": base.where(a5l_r >= 0.30),
                }
                base_names = select(base)
                for ov, score in ovs.items():
                    names = select(score)
                    if len(names) < TOPN:
                        continue
                    gross = float(y.reindex(names).mean())
                    key = (u, f, ov, phase)
                    t = turnover(current.get(key, []), names)
                    current[key] = names
                    diag.append({
                        "date": dt, "phase": phase, "universe": u, "factor": f, "overlay": ov,
                        "eligible_n": int(score.notna().sum()),
                        "n_changed_vs_base": len(set(base_names) - set(names)) if base_names else np.nan,
                    })
                    for c in COSTS_BP:
                        rows.append({
                            "date": dt, "phase": phase, "universe": u, "factor": f,
                            "overlay": ov, "cost_bp": c,
                            "net": gross - t * c / 10000.0, "gross": gross, "turnover": t,
                        })
        if i % 250 == 0:
            print(f"processed {i}/{len(common)}", flush=True)

    x = pd.DataFrame(rows)
    x["date"] = pd.to_datetime(x.date)
    x.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(diag).to_csv(OUT / "diagnostics.csv", index=False, encoding="utf-8-sig")

    stats = []
    for (u, f, ov, phase, c), g in x.groupby(["universe", "factor", "overlay", "phase", "cost_bp"]):
        for period, (lo, hi) in PERIODS.items():
            z = g[(g.date >= lo) & (g.date <= hi)].sort_values("date")
            if len(z) < 4:
                continue
            stats.append({
                "universe": u, "factor": f, "overlay": ov, "phase": phase, "cost_bp": c,
                "period": period, "ann_return": ann(z.net), "sharpe": sharpe(z.net),
                "mdd": mdd(z.net), "avg_turnover": float(z.turnover.mean()),
            })
    st = pd.DataFrame(stats)
    st.to_csv(OUT / "phase_stats.csv", index=False, encoding="utf-8-sig")

    key = ["universe", "factor", "phase", "cost_bp", "period"]
    b = st[st.overlay == "BASE"][key + ["ann_return", "sharpe", "mdd", "avg_turnover"]].rename(columns={
        "ann_return": "base_return", "sharpe": "base_sharpe", "mdd": "base_mdd", "avg_turnover": "base_turnover"
    })
    p = st[st.overlay != "BASE"].merge(b, on=key, how="left")
    p["delta_return"] = p.ann_return - p.base_return
    p["delta_sharpe"] = p.sharpe - p.base_sharpe
    p["delta_mdd"] = p.mdd - p.base_mdd
    p["delta_turnover"] = p.avg_turnover - p.base_turnover
    p.to_csv(OUT / "phase_vs_base.csv", index=False, encoding="utf-8-sig")

    sm = p.groupby(["universe", "factor", "overlay", "cost_bp", "period"], as_index=False).agg(
        n_phases=("delta_return", "count"),
        median_delta_return=("delta_return", "median"),
        median_delta_sharpe=("delta_sharpe", "median"),
        median_delta_mdd=("delta_mdd", "median"),
        median_delta_turnover=("delta_turnover", "median"),
        return_wins=("delta_return", lambda s: int((s > 0).sum())),
    )
    sm.to_csv(OUT / "paired_summary.csv", index=False, encoding="utf-8-sig")

    dg = pd.DataFrame(diag)
    dsum = []
    for (u, f, ov), g in dg[dg.overlay != "BASE"].groupby(["universe", "factor", "overlay"]):
        for period, (lo, hi) in PERIODS.items():
            z = g[(g.date >= lo) & (g.date <= hi)]
            if z.empty:
                continue
            dsum.append({
                "universe": u, "factor": f, "overlay": ov, "period": period,
                "avg_eligible_n": float(z.eligible_n.mean()),
                "avg_changed_vs_base": float(z.n_changed_vs_base.mean()),
            })
    pd.DataFrame(dsum).to_csv(OUT / "diagnostic_summary.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# ACT5 Timing Robustness — Same-Day vs 1-Day Lag", "",
        "Exact legacy WMOM; Top20; mcap >= KRW 250bn; 10D hold; 10 staggered phases.",
        "`ACT5_T`: recent 5D / preceding non-overlapping 20D through formation-date close.",
        "`ACT5_LAG1`: the exact same ACT5 signal shifted by one trading day, so formation uses only information known at the prior close.", "",
    ]
    focus = ["PRE_STRESS_2017_2024", "EARLY_2017_2019", "LATE_2020_2022", "NORMAL_2023_2024", "BULL_2025", "YTD_2026"]
    for period in focus:
        lines += [f"## {period}", "", "| Universe | Factor | Same-day Δ | Same-day wins | Lag1 Δ | Lag1 wins |", "|---|---|---:|---:|---:|---:|"]
        q = sm[(sm.period == period) & (sm.cost_bp == 30)]
        for u in UNIVERSES:
            for f in FACTORS:
                a = q[(q.universe == u) & (q.factor == f) & (q.overlay == "ACT5_T_KEEP_TOP70")]
                l = q[(q.universe == u) & (q.factor == f) & (q.overlay == "ACT5_LAG1_KEEP_TOP70")]
                if a.empty or l.empty:
                    continue
                a, l = a.iloc[0], l.iloc[0]
                lines.append(f"| {u} | {f} | {a.median_delta_return:+.2%} | {int(a.return_wins)}/{int(a.n_phases)} | {l.median_delta_return:+.2%} | {int(l.return_wins)}/{int(l.n_phases)} |")
        lines.append("")
    (OUT / "TIMING_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"done {len(x):,} rows", flush=True)


if __name__ == "__main__":
    main()
