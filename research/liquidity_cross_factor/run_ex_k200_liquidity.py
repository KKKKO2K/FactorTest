from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

import run_cross_factor_liquidity as base

HERE = Path(__file__).resolve().parent
OUT = HERE / "results_ex_k200"
OUT.mkdir(parents=True, exist_ok=True)
SPLIT = base.OOS_START

OVERLAYS = (
    "BASE",
    "RAW_TA_W10",
    "MCAP_W10",
    "RESID_TA_W10",
    "TURNOVER_W10",
    "ACT1_W10",
    "ACT5_W10",
    "ACT5_KEEP_TOP70",
    "ACT5_KEEP_TOP50",
    "ACT5_GT1",
)


def load_basic_with_market():
    returns, mcap, k200 = base.load_basic()
    market_by_date = {}
    for dt, p in base.dated_files(base.BASIC).items():
        if dt < base.START:
            continue
        df = base.read_csv(p)
        cc = base.code_col(df)
        mc = base.find_col(df, exact=("상장된 시장",), contains=("상장된 시장", "market"))
        if mc is None:
            continue
        codes = base.norm_code(df[cc])
        market = df[mc].astype(str).str.upper().str.strip()
        market_by_date[dt] = pd.Series(market.to_numpy(), index=codes).groupby(level=0).last()
    return returns, mcap, k200, market_by_date


def residual_ta_rank(raw: pd.Series, mcap: pd.Series) -> pd.Series:
    x = pd.concat([raw.rename("ta"), mcap.rename("mcap")], axis=1).dropna()
    x = x[(x.ta > 0) & (x.mcap > 0)]
    if len(x) < 30:
        return pd.Series(index=raw.index, dtype=float)
    lx = np.log(x.mcap.to_numpy())
    ly = np.log(x.ta.to_numpy())
    beta, alpha = np.polyfit(lx, ly, 1)
    resid = ly - (alpha + beta * lx)
    s = pd.Series(resid, index=x.index)
    return base.pct_rank(s, high_good=True).reindex(raw.index)


def overlay_scores(factor_score: pd.Series, liq: dict[str, pd.Series], mcap: pd.Series) -> dict[str, pd.Series]:
    raw_r = base.pct_rank(liq["raw"], True)
    mcap_r = base.pct_rank(mcap, True)
    resid_r = residual_ta_rank(liq["raw"], mcap)
    turn_r = base.pct_rank(liq["turnover"], True)
    act1_r = base.pct_rank(liq["act1"], True)
    act5_r = base.pct_rank(liq["act5"], True)
    return {
        "BASE": factor_score,
        "RAW_TA_W10": 0.90 * factor_score + 0.10 * raw_r,
        "MCAP_W10": 0.90 * factor_score + 0.10 * mcap_r,
        "RESID_TA_W10": 0.90 * factor_score + 0.10 * resid_r,
        "TURNOVER_W10": 0.90 * factor_score + 0.10 * turn_r,
        "ACT1_W10": 0.90 * factor_score + 0.10 * act1_r,
        "ACT5_W10": 0.90 * factor_score + 0.10 * act5_r,
        "ACT5_KEEP_TOP70": factor_score.where(act5_r >= 0.30),
        "ACT5_KEEP_TOP50": factor_score.where(act5_r >= 0.50),
        "ACT5_GT1": factor_score.where(liq["act5"] > 1.0),
    }


def ann_return(r: pd.Series) -> float:
    if len(r) == 0:
        return np.nan
    return float((1.0 + r).prod() ** ((252.0 / base.HORIZON) / len(r)) - 1.0)


def sharpe(r: pd.Series) -> float:
    sd = r.std(ddof=1)
    if len(r) < 3 or pd.isna(sd) or sd <= 0:
        return np.nan
    return float(r.mean() / sd * math.sqrt(252.0 / base.HORIZON))


def mdd(r: pd.Series) -> float:
    nav = (1.0 + r.fillna(0.0)).cumprod()
    return float((nav / nav.cummax() - 1.0).min()) if len(nav) else np.nan


def main() -> None:
    returns, mcap, k200_by_date, market_by_date = load_basic_with_market()
    ta = base.load_trading_amount()
    fwd = base.forward_returns(returns, base.HORIZON)
    liq_frames = base.build_liquidity_features(ta, mcap)
    factor_files = {name: base.dated_files(folder) for name, folder in base.FACTORS.items()}

    common_dates = sorted(set(returns.index) & set(ta.index) & set(k200_by_date) & set(market_by_date))
    dates = [d for d in common_dates if d >= base.START][::base.STEP]

    rows = []
    current = {}
    for dt in dates:
        if dt not in fwd.index:
            continue
        k = k200_by_date[dt]
        market = market_by_date[dt].reindex(k.index)
        codes = k.index[(k == 0) & market.str.contains("KOSPI", na=False)]
        y = fwd.loc[dt].reindex(codes)
        if y.notna().sum() < 150:
            continue
        mc = mcap.loc[dt].reindex(codes)
        liq = {name: frame.loc[dt].reindex(codes) if dt in frame.index else pd.Series(index=codes, dtype=float)
               for name, frame in liq_frames.items()}

        for factor, files in factor_files.items():
            if dt not in files:
                continue
            raw = base.load_factor(files[dt]).reindex(codes)
            for direction, high_good in (("HIGH", True), ("LOW", False)):
                fs = base.pct_rank(raw, high_good=high_good)
                scores = overlay_scores(fs, liq, mc)
                for overlay, score in scores.items():
                    eligible = score.replace([np.inf, -np.inf], np.nan).dropna()
                    for n in base.TOP_NS:
                        names = base.select_top(score, n)
                        if len(names) < n:
                            continue
                        gross = float(y.reindex(names).mean())
                        benchmark = float(y.reindex(eligible.index).mean()) if len(eligible) else np.nan
                        for cost in base.COSTS_BPS:
                            key = (factor, direction, overlay, n, cost)
                            turn = base.overlap_turnover(current.get(key, []), names, n)
                            net = gross - turn * cost / 10000.0
                            rows.append({
                                "date": dt, "factor": factor, "direction": direction, "overlay": overlay,
                                "top_n": n, "cost_bps": cost, "gross": gross, "benchmark": benchmark,
                                "net": net, "turnover": turn, "eligible": len(eligible),
                            })
                            current[key] = names

    periods = pd.DataFrame(rows)
    periods["date"] = pd.to_datetime(periods["date"])
    periods.to_csv(OUT / "periods.csv", index=False, encoding="utf-8-sig")

    summaries = []
    for k, g in periods.groupby(["factor", "direction", "overlay", "top_n", "cost_bps"]):
        for sample, mask in (
            ("TRAIN_PRE_2023", g.date < SPLIT),
            ("OOS_2023_PLUS", g.date >= SPLIT),
            ("FULL", pd.Series(True, index=g.index)),
        ):
            x = g[mask]
            if len(x) < 3:
                continue
            summaries.append({
                "sample": sample, "factor": k[0], "direction": k[1], "overlay": k[2],
                "top_n": k[3], "cost_bps": k[4], "n_periods": len(x),
                "annualized_return": ann_return(x.net), "sharpe": sharpe(x.net),
                "mdd": mdd(x.net), "avg_turnover": float(x.turnover.mean()),
                "avg_eligible": float(x.eligible.mean()),
            })
    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT / "summary.csv", index=False, encoding="utf-8-sig")

    comps = []
    for k, g in summary.groupby(["sample", "factor", "direction", "top_n", "cost_bps"]):
        b = g[g.overlay == "BASE"]
        if b.empty:
            continue
        b = b.iloc[0]
        for _, r in g[g.overlay != "BASE"].iterrows():
            comps.append({
                "sample": k[0], "factor": k[1], "direction": k[2], "top_n": k[3], "cost_bps": k[4],
                "overlay": r.overlay,
                "return_delta": r.annualized_return - b.annualized_return,
                "sharpe_delta": r.sharpe - b.sharpe,
                "mdd_delta": r.mdd - b.mdd,
                "turnover_delta": r.avg_turnover - b.avg_turnover,
            })
    comp = pd.DataFrame(comps)
    comp.to_csv(OUT / "vs_base.csv", index=False, encoding="utf-8-sig")

    agg = []
    for (sample, overlay), g in comp.groupby(["sample", "overlay"]):
        agg.append({
            "sample": sample, "overlay": overlay, "n_configs": len(g),
            "return_improve_share": float((g.return_delta > 0).mean()),
            "sharpe_improve_share": float((g.sharpe_delta > 0).mean()),
            "mdd_improve_share": float((g.mdd_delta > 0).mean()),
            "median_return_delta": float(g.return_delta.median()),
            "median_sharpe_delta": float(g.sharpe_delta.median()),
            "median_turnover_delta": float(g.turnover_delta.median()),
        })
    agg = pd.DataFrame(agg)
    agg.to_csv(OUT / "aggregate.csv", index=False, encoding="utf-8-sig")

    # Train-selected direction based on BASE annualized return, then frozen into OOS.
    train_base = summary[(summary["sample"] == "TRAIN_PRE_2023") & (summary["overlay"] == "BASE")]
    # Average across TopN/cost only for sign choice, not overlay choice.
    sign_perf = train_base.groupby(["factor", "direction"])["annualized_return"].mean().reset_index()
    frozen = {}
    for factor, g in sign_perf.groupby("factor"):
        frozen[factor] = g.sort_values("annualized_return", ascending=False).iloc[0].direction

    frozen_rows = []
    for _, r in summary[summary["sample"] == "OOS_2023_PLUS"].iterrows():
        if frozen.get(r.factor) == r.direction:
            frozen_rows.append(r.to_dict())
    frozen_df = pd.DataFrame(frozen_rows)
    frozen_df.to_csv(OUT / "frozen_direction_oos.csv", index=False, encoding="utf-8-sig")

    lines = ["# KOSPI ex-K200 trading-value overlay research", "",
             "Universe: point-in-time KOSPI stocks excluding KOSPI200 constituents.",
             "Both raw factor directions are tested; train-selected direction is also frozen for OOS review.", ""]
    for sample in ("TRAIN_PRE_2023", "OOS_2023_PLUS"):
        lines += [f"## {sample}", ""]
        z = agg[agg["sample"] == sample].sort_values(["return_improve_share", "median_return_delta"], ascending=False)
        for _, r in z.iterrows():
            lines.append(
                f"- {r.overlay}: return improve {r.return_improve_share:.0%}, Sharpe improve {r.sharpe_improve_share:.0%}, "
                f"MDD improve {r.mdd_improve_share:.0%}, median return delta {r.median_return_delta:+.2%}, "
                f"turnover delta {r.median_turnover_delta:+.2f}"
            )
        lines.append("")

    lines += ["## Frozen train direction: OOS Top10 / 30 bps", ""]
    key = frozen_df[(frozen_df.top_n == 10) & (frozen_df.cost_bps == 30)]
    for factor in sorted(key.factor.unique()):
        g = key[key.factor == factor]
        b = g[g.overlay == "BASE"]
        if b.empty:
            continue
        b = b.iloc[0]
        best = g.sort_values("annualized_return", ascending=False).iloc[0]
        lines.append(
            f"- {factor} ({frozen[factor]}): BASE {b.annualized_return:.2%} / Sh {b.sharpe:.2f}; "
            f"best {best.overlay} {best.annualized_return:.2%} / Sh {best.sharpe:.2f}; "
            f"delta {best.annualized_return - b.annualized_return:+.2%}"
        )
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((OUT / "RESEARCH_SUMMARY.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
