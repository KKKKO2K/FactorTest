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
OUT = Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
H = 10
TOPN = 20
MCAP_CUTOFF_BN = 250.0
COSTS_BP = (30, 60)
UNIVERSES = wm.UNIVERSES
PERIODS = wm.PERIODS

FACTOR_PATHS = {
    "OP12_REV": DATA / "OP(12MF_1M_CHG)",
    "OPFY1_REV": DATA / "OP(FY1_1M_CHG)",
    "PBR12MF": DATA / "PBR(12MF)",
    "PER12MF": DATA / "PER(12MF)",
}
FACTOR_HIGH_GOOD = {
    "OP12_REV": True,
    "OPFY1_REV": True,
    "PBR12MF": False,
    "PER12MF": False,
}
OVERLAYS = (
    "BASE",
    "ACT5_KEEP_TOP70",
    "ACT1_W10",
    "RESID_TA_W10",
    "RAW_TA_W10",
    "MCAP_W10",
)


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out = {}
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def load_trading_amount() -> pd.DataFrame:
    rows = []
    for i, (dt, p) in enumerate(dated_files(TRADING).items(), 1):
        df = wm.read_csv(p)
        cc = wm.find_col(df, exact=("Code", "StockCode", "종목코드"))
        vc = wm.find_col(df, exact=("거래대금(십억원)",), contains=("거래대금", "trading"))
        if cc is None or vc is None:
            continue
        codes = wm.normalize_code(df[cc])
        vals = pd.to_numeric(df[vc], errors="coerce")
        rows.append(pd.DataFrame({"date": dt, "code": codes, "value": vals}))
        if i % 500 == 0:
            print(f"loaded trading amount {i}", flush=True)
    if not rows:
        raise RuntimeError(f"No trading amount files under {TRADING}")
    return pd.concat(rows, ignore_index=True).pivot(index="date", columns="code", values="value").sort_index()


def load_factor(path: Path) -> pd.Series:
    df = wm.read_csv(path)
    cc = wm.find_col(df, exact=("Code", "StockCode", "종목코드"))
    vc = wm.find_col(df, exact=("FactorValue",), contains=("factorvalue",))
    if cc is None or vc is None:
        return pd.Series(dtype=float)
    codes = wm.normalize_code(df[cc])
    vals = pd.to_numeric(df[vc], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return pd.Series(vals.to_numpy(), index=codes).groupby(level=0).last()


def pct_rank(s: pd.Series, high_good: bool = True) -> pd.Series:
    # Score 1.0 = best.
    return pd.to_numeric(s, errors="coerce").rank(pct=True, method="average", ascending=high_good)


def residual_ta_rank(raw: pd.Series, mcap: pd.Series) -> pd.Series:
    x = pd.concat([raw.rename("ta"), mcap.rename("mcap")], axis=1).dropna()
    x = x[(x.ta > 0) & (x.mcap > 0)]
    if len(x) < 30:
        return pd.Series(index=raw.index, dtype=float)
    lx = np.log(x.mcap.to_numpy(float))
    ly = np.log(x.ta.to_numpy(float))
    beta, alpha = np.polyfit(lx, ly, 1)
    resid = ly - (alpha + beta * lx)
    return pct_rank(pd.Series(resid, index=x.index), True).reindex(raw.index)


def liquidity_frames(ta: pd.DataFrame, mcap: pd.DataFrame) -> dict[str, pd.DataFrame]:
    raw = ta.reindex(index=mcap.index, columns=mcap.columns).where(lambda x: x > 0)
    hist20 = raw.shift(1).rolling(20, min_periods=15).mean()
    act1 = raw / hist20
    recent5 = raw.rolling(5, min_periods=4).mean()
    prior20 = raw.shift(5).rolling(20, min_periods=15).mean()
    act5 = recent5 / prior20
    return {"raw": raw, "act1": act1, "act5": act5}


def build_overlay_scores(base: pd.Series, raw: pd.Series, act1: pd.Series, act5: pd.Series, mcap: pd.Series) -> dict[str, pd.Series]:
    act5_r = pct_rank(act5, True)
    act1_r = pct_rank(act1, True)
    raw_r = pct_rank(raw, True)
    mcap_r = pct_rank(mcap, True)
    resid_r = residual_ta_rank(raw, mcap)
    return {
        "BASE": base,
        "ACT5_KEEP_TOP70": base.where(act5_r >= 0.30),
        "ACT1_W10": 0.90 * base + 0.10 * act1_r,
        "RESID_TA_W10": 0.90 * base + 0.10 * resid_r,
        "RAW_TA_W10": 0.90 * base + 0.10 * raw_r,
        "MCAP_W10": 0.90 * base + 0.10 * mcap_r,
    }


def forward_returns(daily: pd.DataFrame, horizon: int = H) -> pd.DataFrame:
    logs = np.log1p(daily.clip(lower=-0.999999).fillna(0.0))
    acc = sum(logs.shift(-i) for i in range(1, horizon + 1))
    return np.expm1(acc)


def ann_return(r: pd.Series) -> float:
    r = pd.Series(r).dropna()
    if len(r) == 0:
        return np.nan
    return float((1.0 + r).prod() ** ((252.0 / H) / len(r)) - 1.0)


def sharpe(r: pd.Series) -> float:
    r = pd.Series(r).dropna()
    if len(r) < 3:
        return np.nan
    sd = r.std(ddof=1)
    return float(r.mean() / sd * math.sqrt(252.0 / H)) if np.isfinite(sd) and sd > 0 else np.nan


def mdd(r: pd.Series) -> float:
    r = pd.Series(r).dropna()
    nav = (1.0 + r).cumprod()
    return float((nav / nav.cummax() - 1.0).min()) if len(nav) else np.nan


def overlap_turnover(old: list[str], new: list[str]) -> float:
    if not old:
        return 1.0
    return float(1.0 - len(set(old) & set(new)) / TOPN)


def period_name(dt: pd.Timestamp) -> list[str]:
    out = []
    for name, (start, end) in PERIODS.items():
        if start <= dt <= end:
            out.append(name)
    return out


def select_top(score: pd.Series) -> list[str]:
    s = score.replace([np.inf, -np.inf], np.nan).dropna().sort_values(ascending=False)
    return s.head(TOPN).index.tolist() if len(s) >= TOPN else []


def summarize_phase(rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    stats = []
    for (u, f, ov, phase, cost), g in rows.groupby(["universe", "factor", "overlay", "phase", "cost_bp"]):
        g = g.sort_values("date")
        for period, (start, end) in PERIODS.items():
            z = g[(g.date >= start) & (g.date <= end)]
            if len(z) < 4:
                continue
            stats.append({
                "universe": u, "factor": f, "overlay": ov, "phase": int(phase), "cost_bp": int(cost),
                "period": period, "n_periods": len(z), "ann_return": ann_return(z.net),
                "sharpe": sharpe(z.net), "mdd": mdd(z.net), "avg_turnover": float(z.turnover.mean()),
                "avg_eligible_n": float(z.eligible_n.mean()),
            })
    stats = pd.DataFrame(stats)

    key = ["universe", "factor", "phase", "cost_bp", "period"]
    base = stats[stats.overlay == "BASE"][key + ["ann_return", "sharpe", "mdd", "avg_turnover"]].rename(columns={
        "ann_return": "base_ann_return", "sharpe": "base_sharpe", "mdd": "base_mdd", "avg_turnover": "base_turnover"
    })
    pair = stats[stats.overlay != "BASE"].merge(base, on=key, how="left")
    pair["delta_ann_return"] = pair.ann_return - pair.base_ann_return
    pair["delta_sharpe"] = pair.sharpe - pair.base_sharpe
    pair["delta_mdd"] = pair.mdd - pair.base_mdd
    pair["delta_turnover"] = pair.avg_turnover - pair.base_turnover
    summary = pair.groupby(["universe", "factor", "overlay", "cost_bp", "period"], as_index=False).agg(
        n_phases=("delta_ann_return", "count"),
        median_delta_ann_return=("delta_ann_return", "median"),
        median_delta_sharpe=("delta_sharpe", "median"),
        median_delta_mdd=("delta_mdd", "median"),
        median_delta_turnover=("delta_turnover", "median"),
        return_better_phases=("delta_ann_return", lambda s: int((s > 0).sum())),
        sharpe_better_phases=("delta_sharpe", lambda s: int((s > 0).sum())),
        mdd_better_phases=("delta_mdd", lambda s: int((s > 0).sum())),
    )
    return stats, summary


def write_summary(summary: pd.DataFrame) -> None:
    lines = [
        "# Primary-factor × trading-amount overlay (independent staggered-phase replication)",
        "",
        "Top20; market-cap >= KRW 250bn; 10 trading-day holding; 10 staggered phases; equal weight.",
        "ACT5 = recent 5D average trading amount / preceding non-overlapping 20D average.",
        "ACT5_KEEP_TOP70 removes the cross-sectional bottom 30% of ACT5 before selecting on the original factor.",
        "Primary factors: exact weighted momentum, weighted momentum + R1M>=0 gate, OP12 revision, OP FY1 revision, PBR, PER.",
        "",
        "## NET30 — ACT5_KEEP_TOP70 paired median delta annualized return",
        "",
    ]
    focus = ["PRE_STRESS_2017_2024", "EARLY_2017_2019", "LATE_2020_2022", "NORMAL_2023_2024", "BULL_2025", "YTD_2026"]
    factors = ["WEIGHTED_MOM", "WEIGHTED_MOM_R1M_GE0", "OP12_REV", "OPFY1_REV", "PBR12MF", "PER12MF"]
    for period in focus:
        lines.append(f"### {period}")
        q = summary[(summary.period == period) & (summary.cost_bp == 30) & (summary.overlay == "ACT5_KEEP_TOP70")]
        for u in UNIVERSES:
            parts = []
            for f in factors:
                x = q[(q.universe == u) & (q.factor == f)]
                if x.empty:
                    continue
                r = x.iloc[0]
                parts.append(f"{f} {r.median_delta_ann_return:+.2%} ({int(r.return_better_phases)}/{int(r.n_phases)})")
            if parts:
                lines.append(f"- {u}: " + "; ".join(parts))
        lines.append("")
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    returns, mcap, k200_by_date, market_by_date = wm.load_basic()
    ta = load_trading_amount()
    print(f"returns={returns.shape}; ta={ta.shape}", flush=True)
    wm_score, r1m = wm.calendar_weighted_momentum(returns, mcap)
    liq = liquidity_frames(ta, mcap)
    fwd = forward_returns(returns)
    factor_files = {name: dated_files(path) for name, path in FACTOR_PATHS.items()}

    common = sorted(set(returns.index) & set(mcap.index) & set(ta.index) & set(k200_by_date) & set(market_by_date))
    common = [d for d in common if d >= pd.Timestamp("2017-01-01")]
    phase_map = {d: i % H for i, d in enumerate(common)}
    current: dict[tuple, list[str]] = {}
    rows = []

    for i, dt in enumerate(common, 1):
        if dt not in fwd.index or dt not in wm_score.index:
            continue
        phase = phase_map[dt]
        mc_full = pd.to_numeric(mcap.loc[dt], errors="coerce")
        raw_full = liq["raw"].loc[dt] if dt in liq["raw"].index else pd.Series(dtype=float)
        act1_full = liq["act1"].loc[dt] if dt in liq["act1"].index else pd.Series(dtype=float)
        act5_full = liq["act5"].loc[dt] if dt in liq["act5"].index else pd.Series(dtype=float)

        raw_factor = {}
        for f, files in factor_files.items():
            if dt in files:
                raw_factor[f] = load_factor(files[dt])

        for u in UNIVERSES:
            codes = wm.universe_codes(u, dt, k200_by_date, market_by_date)
            mc = mc_full.reindex(codes)
            eligible = mc.index[(mc >= MCAP_CUTOFF_BN).fillna(False)]
            if len(eligible) < 40:
                continue
            y = fwd.loc[dt].reindex(eligible)
            raw = raw_full.reindex(eligible)
            act1 = act1_full.reindex(eligible)
            act5 = act5_full.reindex(eligible)
            mc_e = mc.reindex(eligible)

            factor_scores = {}
            w = pd.to_numeric(wm_score.loc[dt].reindex(eligible), errors="coerce")
            factor_scores["WEIGHTED_MOM"] = pct_rank(w, True)
            recent = pd.to_numeric(r1m.loc[dt].reindex(eligible), errors="coerce")
            factor_scores["WEIGHTED_MOM_R1M_GE0"] = pct_rank(w.where(recent >= 0), True)

            for f, s in raw_factor.items():
                s = s.reindex(eligible)
                factor_scores[f] = pct_rank(s, FACTOR_HIGH_GOOD[f])

            for f, base_score in factor_scores.items():
                if base_score.notna().sum() < TOPN:
                    continue
                overlays = build_overlay_scores(base_score, raw, act1, act5, mc_e)
                for ov, score in overlays.items():
                    names = select_top(score)
                    if len(names) < TOPN:
                        continue
                    gross = float(y.reindex(names).mean())
                    valid = int(score.replace([np.inf, -np.inf], np.nan).notna().sum())
                    key0 = (u, f, ov, phase)
                    turn = overlap_turnover(current.get(key0, []), names)
                    current[key0] = names
                    for cost in COSTS_BP:
                        net = gross - turn * cost / 10000.0
                        rows.append({"date": dt, "phase": phase, "universe": u, "factor": f, "overlay": ov,
                                     "cost_bp": cost, "gross": gross, "net": net, "turnover": turn, "eligible_n": valid})
        if i % 250 == 0:
            print(f"processed {i}/{len(common)}", flush=True)

    periods = pd.DataFrame(rows)
    periods["date"] = pd.to_datetime(periods.date)
    periods.to_csv(OUT / "period_returns.csv", index=False, encoding="utf-8-sig")
    stats, summary = summarize_phase(periods)
    stats.to_csv(OUT / "phase_stats.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "paired_summary.csv", index=False, encoding="utf-8-sig")
    write_summary(summary)
    print(f"done rows={len(periods):,}; phase_stats={len(stats):,}; paired={len(summary):,}", flush=True)


if __name__ == "__main__":
    main()
