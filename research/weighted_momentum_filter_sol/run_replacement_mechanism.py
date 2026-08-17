from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import run_weighted_momentum_filter as m

OUT = HERE / "results_replacement_mechanism"
OUT.mkdir(parents=True, exist_ok=True)
HORIZON = 10
START = pd.Timestamp("2017-01-01")


def period_of(dt: pd.Timestamp) -> list[str]:
    out = []
    for name, (lo, hi) in m.PERIODS.items():
        if lo <= dt <= hi:
            out.append(name)
    return out


def fwd_compound(returns: pd.DataFrame, dt: pd.Timestamp, codes: list[str], horizon: int = HORIZON) -> pd.Series:
    if dt not in returns.index:
        return pd.Series(index=codes, dtype=float)
    i = returns.index.get_loc(dt)
    if not isinstance(i, (int, np.integer)) or i + horizon >= len(returns.index):
        return pd.Series(index=codes, dtype=float)
    w = returns.iloc[i + 1 : i + 1 + horizon].reindex(columns=codes)
    # Match portfolio simulator convention: missing daily return contributes 0; extreme bad returns clipped above -100%.
    w = w.clip(lower=-0.999999).fillna(0.0)
    return (1.0 + w).prod(axis=0) - 1.0


def build_pairs(returns, mcap, k200_by_date, market_by_date, wm, r1m):
    common = sorted(set(returns.index) & set(mcap.index) & set(k200_by_date) & set(market_by_date))
    common = [d for d in common if d >= START]
    phase_map = {d: i % HORIZON for i, d in enumerate(common)}
    pair_rows = []
    valid_rows = []

    for n, dt in enumerate(common, 1):
        if dt not in wm.index or dt not in r1m.index:
            continue
        iret = returns.index.get_loc(dt)
        if not isinstance(iret, (int, np.integer)) or iret + HORIZON >= len(returns.index):
            continue
        mc = pd.to_numeric(mcap.loc[dt], errors="coerce")

        for u in m.UNIVERSES:
            codes = m.universe_codes(u, dt, k200_by_date, market_by_date)
            mc_u = mc.reindex(codes)
            eligible = mc_u.index[(mc_u >= m.MCAP_CUTOFF_BN).fillna(False)]
            if len(eligible) < 40:
                continue

            score = pd.to_numeric(wm.loc[dt].reindex(eligible), errors="coerce")
            recent = pd.to_numeric(r1m.loc[dt].reindex(eligible), errors="coerce")
            ranked = score.dropna().sort_values(ascending=False)
            base_top = ranked.head(m.TOPN).index.tolist()
            filtered_ranked = score.where(recent >= 0.0).dropna().sort_values(ascending=False)
            filt_top = filtered_ranked.head(m.TOPN).index.tolist()
            if len(base_top) != m.TOPN or len(filt_top) != m.TOPN:
                continue

            base_set, filt_set = set(base_top), set(filt_top)
            removed = [c for c in base_top if c not in filt_set]
            added = [c for c in filt_top if c not in base_set]
            # Both lists inherit descending legacy-WMOM order. Pair kth removed with kth replacement.
            if len(removed) != len(added):
                raise RuntimeError(f"replacement count mismatch {dt} {u}: {len(removed)} vs {len(added)}")

            valid_rows.append({
                "date": dt,
                "phase": phase_map[dt],
                "universe": u,
                "n_replaced": len(removed),
                "has_replacement": int(len(removed) > 0),
            })
            if not removed:
                continue

            fwd_codes = removed + added
            fwd = fwd_compound(returns, dt, fwd_codes)
            rank_map = {c: j + 1 for j, c in enumerate(ranked.index.tolist())}

            for j, (r, a) in enumerate(zip(removed, added), 1):
                rr = float(fwd.get(r, np.nan))
                ar = float(fwd.get(a, np.nan))
                if not (np.isfinite(rr) and np.isfinite(ar)):
                    continue
                pair_rows.append({
                    "date": dt,
                    "phase": phase_map[dt],
                    "universe": u,
                    "pair_no": j,
                    "removed_code": r,
                    "added_code": a,
                    "removed_wmom": float(score.get(r, np.nan)),
                    "added_wmom": float(score.get(a, np.nan)),
                    "wmom_sacrifice": float(score.get(a, np.nan) - score.get(r, np.nan)),
                    "removed_r1m": float(recent.get(r, np.nan)),
                    "added_r1m": float(recent.get(a, np.nan)),
                    "removed_legacy_rank": int(rank_map[r]),
                    "added_legacy_rank": int(rank_map[a]),
                    "removed_fwd10": rr,
                    "added_fwd10": ar,
                    "pair_delta_fwd10": ar - rr,
                    "added_wins": int(ar > rr),
                })

        if n % 250 == 0:
            print(f"paired {n}/{len(common)}", flush=True)

    return pd.DataFrame(pair_rows), pd.DataFrame(valid_rows)


def build_event_rows(pairs: pd.DataFrame) -> pd.DataFrame:
    if pairs.empty:
        return pd.DataFrame()
    return pairs.groupby(["date", "phase", "universe"], as_index=False).agg(
        n_pairs=("pair_no", "count"),
        removed_mean_fwd10=("removed_fwd10", "mean"),
        added_mean_fwd10=("added_fwd10", "mean"),
        event_delta_fwd10=("pair_delta_fwd10", "mean"),
        pair_win_rate=("added_wins", "mean"),
        avg_removed_r1m=("removed_r1m", "mean"),
        avg_added_r1m=("added_r1m", "mean"),
        avg_wmom_sacrifice=("wmom_sacrifice", "mean"),
        avg_removed_rank=("removed_legacy_rank", "mean"),
        avg_added_rank=("added_legacy_rank", "mean"),
    )


def summarize(pairs: pd.DataFrame, events: pd.DataFrame, valid: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    pair_frames = []
    event_frames = []
    for period, (lo, hi) in m.PERIODS.items():
        p = pairs[(pairs.date >= lo) & (pairs.date <= hi)].copy()
        e = events[(events.date >= lo) & (events.date <= hi)].copy()
        v = valid[(valid.date >= lo) & (valid.date <= hi)].copy()
        for u in m.UNIVERSES:
            pu, eu, vu = p[p.universe == u], e[e.universe == u], v[v.universe == u]
            if pu.empty or eu.empty or vu.empty:
                continue
            phase_means = eu.groupby("phase").event_delta_fwd10.mean()
            pair_frames.append({
                "universe": u,
                "period": period,
                "n_valid_dates": len(vu),
                "replacement_event_rate": float(vu.has_replacement.mean()),
                "avg_replacements_all_valid_dates": float(vu.n_replaced.mean()),
                "n_replacement_events": len(eu),
                "n_pairs": len(pu),
                "mean_removed_fwd10": float(pu.removed_fwd10.mean()),
                "mean_added_fwd10": float(pu.added_fwd10.mean()),
                "mean_pair_delta_fwd10": float(pu.pair_delta_fwd10.mean()),
                "median_pair_delta_fwd10": float(pu.pair_delta_fwd10.median()),
                "pair_win_rate": float(pu.added_wins.mean()),
                "mean_removed_r1m": float(pu.removed_r1m.mean()),
                "mean_added_r1m": float(pu.added_r1m.mean()),
                "mean_wmom_sacrifice": float(pu.wmom_sacrifice.mean()),
                "mean_removed_rank": float(pu.removed_legacy_rank.mean()),
                "mean_added_rank": float(pu.added_legacy_rank.mean()),
            })
            event_frames.append({
                "universe": u,
                "period": period,
                "n_events": len(eu),
                "mean_event_delta_fwd10": float(eu.event_delta_fwd10.mean()),
                "median_event_delta_fwd10": float(eu.event_delta_fwd10.median()),
                "positive_event_rate": float((eu.event_delta_fwd10 > 0).mean()),
                "median_phase_mean_delta_fwd10": float(phase_means.median()),
                "phase_win_count": int((phase_means > 0).sum()),
                "n_phases": int(phase_means.size),
                "worst_phase_mean_delta_fwd10": float(phase_means.min()),
                "best_phase_mean_delta_fwd10": float(phase_means.max()),
            })
    return pd.DataFrame(pair_frames), pd.DataFrame(event_frames)


def write_summary(pair_summary: pd.DataFrame, event_summary: pd.DataFrame):
    lines = [
        "# Weighted Momentum R1M<0 Veto — Direct Replacement Mechanism",
        "",
        "Mechanism test: at each formation close, compare legacy-WMOM Top20 names removed solely because `R1M < 0` with the next-best legacy-WMOM names admitted by the `R1M >= 0` gate.",
        "Forward return is compounded `t+1 ... t+10`, matching the existing portfolio simulator's rebalance timing and missing-return convention.",
        "When multiple names are replaced, removed and added names are paired in descending legacy-WMOM rank order.",
        "",
    ]
    focus = ["PRE_STRESS_2017_2024", "EARLY_2017_2019", "LATE_2020_2022", "NORMAL_2023_2024", "BULL_2025", "YTD_2026"]
    for period in focus:
        lines += [f"## {period}", "", "| Universe | Event rate | Avg # repl | Removed fwd10 | Added fwd10 | Pair Δ | Pair win | Event Δ | Event +rate | Phase wins |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for u in m.UNIVERSES:
            p = pair_summary[(pair_summary.universe == u) & (pair_summary.period == period)]
            e = event_summary[(event_summary.universe == u) & (event_summary.period == period)]
            if p.empty or e.empty:
                continue
            a, b = p.iloc[0], e.iloc[0]
            lines.append(
                f"| {u} | {a.replacement_event_rate:.1%} | {a.avg_replacements_all_valid_dates:.2f} | {a.mean_removed_fwd10:+.2%} | {a.mean_added_fwd10:+.2%} | {a.mean_pair_delta_fwd10:+.2%} | {a.pair_win_rate:.1%} | {b.mean_event_delta_fwd10:+.2%} | {b.positive_event_rate:.1%} | {int(b.phase_win_count)}/{int(b.n_phases)} |"
            )
        lines.append("")
    lines += [
        "## Interpretation",
        "",
        "- `Pair Δ` is the stock-level added-minus-removed 10D return, weighting each replacement pair equally.",
        "- `Event Δ` first averages simultaneous replacements within a date, then weights each replacement date equally.",
        "- `Phase wins` tests timing robustness across the same 10 staggered 10-trading-day schedules; it is not an independence-based p-value.",
        "- A positive result here supports the proposed veto mechanism directly; it does not by itself establish that 0% is uniquely optimal.",
        "",
    ]
    (OUT / "MECHANISM_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    returns, mcap, k200_by_date, market_by_date = m.load_basic()
    print(f"returns={returns.shape}; mcap={mcap.shape}", flush=True)
    wm, r1m = m.calendar_weighted_momentum(returns, mcap)
    pairs, valid = build_pairs(returns, mcap, k200_by_date, market_by_date, wm, r1m)
    events = build_event_rows(pairs)
    pair_summary, event_summary = summarize(pairs, events, valid)
    pairs.to_csv(OUT / "replacement_pairs.csv", index=False, encoding="utf-8-sig")
    valid.to_csv(OUT / "valid_dates.csv", index=False, encoding="utf-8-sig")
    events.to_csv(OUT / "replacement_events.csv", index=False, encoding="utf-8-sig")
    pair_summary.to_csv(OUT / "pair_summary.csv", index=False, encoding="utf-8-sig")
    event_summary.to_csv(OUT / "event_summary.csv", index=False, encoding="utf-8-sig")
    write_summary(pair_summary, event_summary)
    print(f"done pairs={len(pairs):,}; events={len(events):,}; valid_dates={len(valid):,}", flush=True)


if __name__ == "__main__":
    main()
