from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WM_DIR = ROOT / "research" / "weighted_momentum_filter_sol"
sys.path.insert(0, str(WM_DIR))
import run_weighted_momentum_filter as wm  # noqa: E402
sys.path.insert(0, str(HERE))
import run_wmom_liquidity as liq  # noqa: E402

OUT = HERE / "results_act5_replacement_mechanism"
OUT.mkdir(parents=True, exist_ok=True)
H = 10
START = pd.Timestamp("2017-01-01")
FACTORS = ("WEIGHTED_MOM", "WEIGHTED_MOM_R1M_GE0")


def fwd_compound(returns: pd.DataFrame, dt: pd.Timestamp, codes: list[str]) -> pd.Series:
    if dt not in returns.index:
        return pd.Series(index=codes, dtype=float)
    i = returns.index.get_loc(dt)
    if not isinstance(i, (int, np.integer)) or i + H >= len(returns.index):
        return pd.Series(index=codes, dtype=float)
    x = returns.iloc[i + 1:i + 1 + H].reindex(columns=codes).clip(lower=-0.999999).fillna(0.0)
    return (1.0 + x).prod(axis=0) - 1.0


def build_pairs(returns, mcap, k200_by_date, market_by_date, wmom, r1m, ta):
    raw = ta.reindex(index=mcap.index, columns=mcap.columns).where(lambda x: x > 0)
    recent5 = raw.rolling(5, min_periods=4).mean()
    prior20 = raw.shift(5).rolling(20, min_periods=15).mean()
    act5 = recent5 / prior20

    common = sorted(set(returns.index) & set(mcap.index) & set(raw.index) & set(k200_by_date) & set(market_by_date))
    common = [d for d in common if d >= START]
    phase_map = {d: i % H for i, d in enumerate(common)}
    pairs, valid = [], []

    for n, dt in enumerate(common, 1):
        iret = returns.index.get_loc(dt)
        if not isinstance(iret, (int, np.integer)) or iret + H >= len(returns.index):
            continue
        mc_full = pd.to_numeric(mcap.loc[dt], errors="coerce")

        for u in wm.UNIVERSES:
            codes = wm.universe_codes(u, dt, k200_by_date, market_by_date)
            mc = mc_full.reindex(codes)
            eligible = mc.index[(mc >= wm.MCAP_CUTOFF_BN).fillna(False)]
            if len(eligible) < 40:
                continue

            w = pd.to_numeric(wmom.loc[dt].reindex(eligible), errors="coerce")
            r = pd.to_numeric(r1m.loc[dt].reindex(eligible), errors="coerce")
            a5 = pd.to_numeric(act5.loc[dt].reindex(eligible), errors="coerce")
            a5_rank = liq.pct_rank(a5, True)
            raw_ta = pd.to_numeric(raw.loc[dt].reindex(eligible), errors="coerce")

            for factor in FACTORS:
                fscore = w if factor == "WEIGHTED_MOM" else w.where(r >= 0.0)
                ranked = fscore.dropna().sort_values(ascending=False)
                base_top = ranked.head(wm.TOPN).index.tolist()
                filtered_ranked = fscore.where(a5_rank >= 0.30).dropna().sort_values(ascending=False)
                filt_top = filtered_ranked.head(wm.TOPN).index.tolist()
                if len(base_top) != wm.TOPN or len(filt_top) != wm.TOPN:
                    continue

                bset, fset = set(base_top), set(filt_top)
                removed = [c for c in base_top if c not in fset]
                added = [c for c in filt_top if c not in bset]
                if len(removed) != len(added):
                    raise RuntimeError(f"replacement count mismatch {dt} {u} {factor}")

                valid.append({
                    "date": dt, "phase": phase_map[dt], "universe": u, "factor": factor,
                    "n_replaced": len(removed), "has_replacement": int(bool(removed)),
                })
                if not removed:
                    continue

                fwd = fwd_compound(returns, dt, removed + added)
                rank_map = {c: j + 1 for j, c in enumerate(ranked.index.tolist())}
                for j, (rem, add) in enumerate(zip(removed, added), 1):
                    rr, ar = float(fwd.get(rem, np.nan)), float(fwd.get(add, np.nan))
                    if not (np.isfinite(rr) and np.isfinite(ar)):
                        continue
                    pairs.append({
                        "date": dt, "phase": phase_map[dt], "universe": u, "factor": factor, "pair_no": j,
                        "removed_code": rem, "added_code": add,
                        "removed_factor_rank": int(rank_map[rem]), "added_factor_rank": int(rank_map[add]),
                        "removed_wmom": float(w.get(rem, np.nan)), "added_wmom": float(w.get(add, np.nan)),
                        "wmom_sacrifice": float(w.get(add, np.nan) - w.get(rem, np.nan)),
                        "removed_r1m": float(r.get(rem, np.nan)), "added_r1m": float(r.get(add, np.nan)),
                        "removed_act5": float(a5.get(rem, np.nan)), "added_act5": float(a5.get(add, np.nan)),
                        "removed_act5_rank": float(a5_rank.get(rem, np.nan)), "added_act5_rank": float(a5_rank.get(add, np.nan)),
                        "removed_raw_ta": float(raw_ta.get(rem, np.nan)), "added_raw_ta": float(raw_ta.get(add, np.nan)),
                        "removed_fwd10": rr, "added_fwd10": ar, "pair_delta_fwd10": ar - rr,
                        "added_wins": int(ar > rr),
                    })
        if n % 250 == 0:
            print(f"paired {n}/{len(common)}", flush=True)

    return pd.DataFrame(pairs), pd.DataFrame(valid)


def build_events(pairs: pd.DataFrame) -> pd.DataFrame:
    if pairs.empty:
        return pd.DataFrame()
    return pairs.groupby(["date", "phase", "universe", "factor"], as_index=False).agg(
        n_pairs=("pair_no", "count"),
        removed_mean_fwd10=("removed_fwd10", "mean"),
        added_mean_fwd10=("added_fwd10", "mean"),
        event_delta_fwd10=("pair_delta_fwd10", "mean"),
        pair_win_rate=("added_wins", "mean"),
        avg_removed_act5=("removed_act5", "mean"),
        avg_added_act5=("added_act5", "mean"),
        avg_removed_r1m=("removed_r1m", "mean"),
        avg_added_r1m=("added_r1m", "mean"),
        avg_removed_factor_rank=("removed_factor_rank", "mean"),
        avg_added_factor_rank=("added_factor_rank", "mean"),
    )


def summarize(pairs: pd.DataFrame, events: pd.DataFrame, valid: pd.DataFrame):
    rows = []
    for period, (lo, hi) in wm.PERIODS.items():
        for u in wm.UNIVERSES:
            for factor in FACTORS:
                p = pairs[(pairs.date >= lo) & (pairs.date <= hi) & (pairs.universe == u) & (pairs.factor == factor)]
                e = events[(events.date >= lo) & (events.date <= hi) & (events.universe == u) & (events.factor == factor)]
                v = valid[(valid.date >= lo) & (valid.date <= hi) & (valid.universe == u) & (valid.factor == factor)]
                if p.empty or e.empty or v.empty:
                    continue
                phase_means = e.groupby("phase").event_delta_fwd10.mean()
                rows.append({
                    "universe": u, "factor": factor, "period": period,
                    "n_valid_dates": len(v), "replacement_event_rate": float(v.has_replacement.mean()),
                    "avg_replacements_all_valid_dates": float(v.n_replaced.mean()),
                    "n_events": len(e), "n_pairs": len(p),
                    "mean_removed_fwd10": float(p.removed_fwd10.mean()),
                    "mean_added_fwd10": float(p.added_fwd10.mean()),
                    "mean_pair_delta_fwd10": float(p.pair_delta_fwd10.mean()),
                    "median_pair_delta_fwd10": float(p.pair_delta_fwd10.median()),
                    "pair_win_rate": float(p.added_wins.mean()),
                    "mean_event_delta_fwd10": float(e.event_delta_fwd10.mean()),
                    "positive_event_rate": float((e.event_delta_fwd10 > 0).mean()),
                    "phase_win_count": int((phase_means > 0).sum()), "n_phases": int(phase_means.size),
                    "mean_removed_act5": float(p.removed_act5.mean()), "mean_added_act5": float(p.added_act5.mean()),
                    "mean_removed_act5_rank": float(p.removed_act5_rank.mean()), "mean_added_act5_rank": float(p.added_act5_rank.mean()),
                    "mean_removed_r1m": float(p.removed_r1m.mean()), "mean_added_r1m": float(p.added_r1m.mean()),
                    "mean_removed_factor_rank": float(p.removed_factor_rank.mean()), "mean_added_factor_rank": float(p.added_factor_rank.mean()),
                })
    return pd.DataFrame(rows)


def write_md(s: pd.DataFrame):
    lines = [
        "# ACT5 Bottom-30% Veto — Direct Replacement Mechanism",
        "",
        "Base factor portfolio is either exact legacy Weighted Momentum or Weighted Momentum after the R1M>=0 veto.",
        "ACT5 is recent 5D average trading amount divided by the preceding non-overlapping 20D average; cross-sectional bottom 30% is vetoed.",
        "Removed and replacement names are paired in descending original factor rank; forward return is t+1...t+10 compounded.",
        "",
    ]
    focus = ["PRE_STRESS_2017_2024", "EARLY_2017_2019", "LATE_2020_2022", "NORMAL_2023_2024", "BULL_2025", "YTD_2026"]
    for period in focus:
        lines += [f"## {period}", "", "| Universe | Factor | Event rate | Avg repl | Removed 10D | Added 10D | Pair Δ | Pair win | Event Δ | Event + | Phases |", "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        q = s[s.period == period]
        for u in wm.UNIVERSES:
            for factor in FACTORS:
                z = q[(q.universe == u) & (q.factor == factor)]
                if z.empty:
                    continue
                r = z.iloc[0]
                lines.append(f"| {u} | {factor} | {r.replacement_event_rate:.1%} | {r.avg_replacements_all_valid_dates:.2f} | {r.mean_removed_fwd10:+.2%} | {r.mean_added_fwd10:+.2%} | {r.mean_pair_delta_fwd10:+.2%} | {r.pair_win_rate:.1%} | {r.mean_event_delta_fwd10:+.2%} | {r.positive_event_rate:.1%} | {int(r.phase_win_count)}/{int(r.n_phases)} |")
        lines.append("")
    lines += [
        "## Interpretation", "",
        "- Positive Pair/Event Delta means the ACT5 veto directly replaced stale-activity factor winners with names that subsequently outperformed over 10D.",
        "- Comparing WEIGHTED_MOM with WEIGHTED_MOM_R1M_GE0 tests whether ACT5 adds information after the recent-price-trend veto.",
        "- Phase wins are timing-robustness diagnostics, not independent statistical tests.",
    ]
    (OUT / "MECHANISM_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    returns, mcap, k200_by_date, market_by_date = wm.load_basic()
    ta = liq.load_ta()
    wmom, r1m = wm.calendar_weighted_momentum(returns, mcap)
    pairs, valid = build_pairs(returns, mcap, k200_by_date, market_by_date, wmom, r1m, ta)
    events = build_events(pairs)
    summary = summarize(pairs, events, valid)
    pairs.to_csv(OUT / "replacement_pairs.csv", index=False, encoding="utf-8-sig")
    valid.to_csv(OUT / "valid_dates.csv", index=False, encoding="utf-8-sig")
    events.to_csv(OUT / "replacement_events.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUT / "summary.csv", index=False, encoding="utf-8-sig")
    write_md(summary)
    print(f"done pairs={len(pairs):,}; events={len(events):,}; valid={len(valid):,}", flush=True)


if __name__ == "__main__":
    main()
