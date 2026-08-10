from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd

import run_cross_factor_liquidity as base

HERE = Path(__file__).resolve().parent
OUT = HERE / "results_multi_universe"
OUT.mkdir(parents=True, exist_ok=True)
SPLIT = base.OOS_START
TOP_NS = (10, 20)
COSTS = base.COSTS_BPS

UNIVERSES = (
    "K200",
    "KOSPI_EX_K200",
    "KOSPI_ALL",
    "KOSDAQ",
    "KOSPI_KOSDAQ_ALL",
    "KOSDAQ_PLUS_KOSPI_EX_K200",
)

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


def load_market_by_date() -> dict[pd.Timestamp, pd.Series]:
    out = {}
    for dt, p in base.dated_files(base.BASIC).items():
        if dt < base.START:
            continue
        df = base.read_csv(p)
        cc = base.code_col(df)
        mc = base.find_col(df, exact=("상장된 시장",), contains=("상장된 시장", "market"))
        if mc is None:
            continue
        codes = base.norm_code(df[cc])
        vals = df[mc].astype(str).str.upper().str.strip()
        out[dt] = pd.Series(vals.to_numpy(), index=codes).groupby(level=0).last()
    return out


def universe_codes(name: str, k: pd.Series, market: pd.Series) -> pd.Index:
    market = market.reindex(k.index)
    is_kospi = market.eq("KOSPI")
    is_kosdaq = market.eq("KOSDAQ")
    if name == "K200":
        mask = k.eq(1)
    elif name == "KOSPI_EX_K200":
        mask = is_kospi & k.eq(0)
    elif name == "KOSPI_ALL":
        mask = is_kospi
    elif name == "KOSDAQ":
        mask = is_kosdaq
    elif name == "KOSPI_KOSDAQ_ALL":
        mask = is_kospi | is_kosdaq
    elif name == "KOSDAQ_PLUS_KOSPI_EX_K200":
        mask = (is_kospi | is_kosdaq) & k.eq(0)
    else:
        raise KeyError(name)
    return k.index[mask.fillna(False)]


def residual_ta_rank(raw: pd.Series, mcap: pd.Series) -> pd.Series:
    x = pd.concat([raw.rename("ta"), mcap.rename("mcap")], axis=1).dropna()
    x = x[(x.ta > 0) & (x.mcap > 0)]
    if len(x) < 30:
        return pd.Series(index=raw.index, dtype=float)
    lx = np.log(x.mcap.to_numpy())
    ly = np.log(x.ta.to_numpy())
    beta, alpha = np.polyfit(lx, ly, 1)
    resid = ly - (alpha + beta * lx)
    return base.pct_rank(pd.Series(resid, index=x.index), True).reindex(raw.index)


def build_scores(factor_score: pd.Series, liq: dict[str, pd.Series], mcap: pd.Series) -> dict[str, pd.Series]:
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


def max_dd(r: pd.Series) -> float:
    nav = (1.0 + r.fillna(0.0)).cumprod()
    return float((nav / nav.cummax() - 1.0).min()) if len(nav) else np.nan


def main() -> None:
    returns, mcap, k200_by_date = base.load_basic()
    market_by_date = load_market_by_date()
    ta = base.load_trading_amount()
    fwd = base.forward_returns(returns, base.HORIZON)
    liq_frames = base.build_liquidity_features(ta, mcap)
    factor_files = {name: base.dated_files(folder) for name, folder in base.FACTORS.items()}

    common = sorted(set(returns.index) & set(ta.index) & set(k200_by_date) & set(market_by_date))
    dates = [d for d in common if d >= base.START][::base.STEP]

    current: dict[tuple, list[str]] = {}
    rows: list[dict] = []

    for dt in dates:
        if dt not in fwd.index:
            continue
        k = k200_by_date[dt]
        market = market_by_date[dt]
        mc_full = mcap.loc[dt]
        liq_full = {name: frame.loc[dt] if dt in frame.index else pd.Series(dtype=float)
                    for name, frame in liq_frames.items()}

        factor_raw = {}
        for factor, files in factor_files.items():
            if dt in files:
                factor_raw[factor] = base.load_factor(files[dt])

        for universe in UNIVERSES:
            codes = universe_codes(universe, k, market)
            y = fwd.loc[dt].reindex(codes)
            min_obs = 80 if universe == "K200" else 150
            if y.notna().sum() < min_obs:
                continue
            mc = mc_full.reindex(codes)
            liq = {name: s.reindex(codes) for name, s in liq_full.items()}

            for factor, raw_full in factor_raw.items():
                raw = raw_full.reindex(codes)
                if raw.notna().sum() < max(50, min_obs // 2):
                    continue
                for direction, high_good in (("HIGH", True), ("LOW", False)):
                    factor_score = base.pct_rank(raw, high_good=high_good)
                    scores = build_scores(factor_score, liq, mc)
                    for overlay, score in scores.items():
                        eligible = score.replace([np.inf, -np.inf], np.nan).dropna()
                        for n in TOP_NS:
                            names = base.select_top(score, n)
                            if len(names) < n:
                                continue
                            gross = float(y.reindex(names).mean())
                            for cost in COSTS:
                                key = (universe, factor, direction, overlay, n, cost)
                                turn = base.overlap_turnover(current.get(key, []), names, n)
                                net = gross - turn * cost / 10000.0
                                rows.append({
                                    "date": dt, "universe": universe, "factor": factor,
                                    "direction": direction, "overlay": overlay, "top_n": n,
                                    "cost_bps": cost, "net": net, "turnover": turn,
                                    "universe_n": len(codes), "eligible_n": len(eligible),
                                })
                                current[key] = names

    periods = pd.DataFrame(rows)
    periods["date"] = pd.to_datetime(periods["date"])
    periods.to_csv(OUT / "periods.csv", index=False, encoding="utf-8-sig")

    summaries = []
    group_cols = ["universe", "factor", "direction", "overlay", "top_n", "cost_bps"]
    for k, g in periods.groupby(group_cols):
        for sample, mask in (
            ("TRAIN_PRE_2023", g.date < SPLIT),
            ("OOS_2023_PLUS", g.date >= SPLIT),
            ("FULL", pd.Series(True, index=g.index)),
        ):
            x = g[mask]
            if len(x) < 3:
                continue
            summaries.append({
                "sample": sample, "universe": k[0], "factor": k[1], "direction": k[2],
                "overlay": k[3], "top_n": k[4], "cost_bps": k[5], "n_periods": len(x),
                "annualized_return": ann_return(x.net), "sharpe": sharpe(x.net),
                "mdd": max_dd(x.net), "avg_turnover": float(x.turnover.mean()),
                "avg_universe_n": float(x.universe_n.mean()), "avg_eligible_n": float(x.eligible_n.mean()),
            })
    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT / "summary.csv", index=False, encoding="utf-8-sig")

    comps = []
    comp_group = ["sample", "universe", "factor", "direction", "top_n", "cost_bps"]
    for k, g in summary.groupby(comp_group):
        b = g[g.overlay == "BASE"]
        if b.empty:
            continue
        b = b.iloc[0]
        for _, r in g[g.overlay != "BASE"].iterrows():
            comps.append({
                "sample": k[0], "universe": k[1], "factor": k[2], "direction": k[3],
                "top_n": k[4], "cost_bps": k[5], "overlay": r.overlay,
                "return_delta": r.annualized_return - b.annualized_return,
                "sharpe_delta": r.sharpe - b.sharpe,
                "mdd_delta": r.mdd - b.mdd,
                "turnover_delta": r.avg_turnover - b.avg_turnover,
            })
    comp = pd.DataFrame(comps)
    comp.to_csv(OUT / "vs_base.csv", index=False, encoding="utf-8-sig")

    agg = []
    for (sample, universe, overlay), g in comp.groupby(["sample", "universe", "overlay"]):
        agg.append({
            "sample": sample, "universe": universe, "overlay": overlay, "n_configs": len(g),
            "return_improve_share": float((g.return_delta > 0).mean()),
            "sharpe_improve_share": float((g.sharpe_delta > 0).mean()),
            "mdd_improve_share": float((g.mdd_delta > 0).mean()),
            "median_return_delta": float(g.return_delta.median()),
            "median_sharpe_delta": float(g.sharpe_delta.median()),
            "median_turnover_delta": float(g.turnover_delta.median()),
        })
    agg = pd.DataFrame(agg)
    agg.to_csv(OUT / "aggregate.csv", index=False, encoding="utf-8-sig")

    decay = []
    for universe in UNIVERSES:
        for overlay in sorted(comp.overlay.unique()):
            tr = agg[(agg.universe == universe) & (agg.overlay == overlay) & (agg["sample"] == "TRAIN_PRE_2023")]
            oo = agg[(agg.universe == universe) & (agg.overlay == overlay) & (agg["sample"] == "OOS_2023_PLUS")]
            if tr.empty or oo.empty:
                continue
            tr, oo = tr.iloc[0], oo.iloc[0]
            decay.append({
                "universe": universe, "overlay": overlay,
                "train_return_improve_share": tr.return_improve_share,
                "oos_return_improve_share": oo.return_improve_share,
                "train_median_return_delta": tr.median_return_delta,
                "oos_median_return_delta": oo.median_return_delta,
                "oos_minus_train_return_delta": oo.median_return_delta - tr.median_return_delta,
                "train_sharpe_improve_share": tr.sharpe_improve_share,
                "oos_sharpe_improve_share": oo.sharpe_improve_share,
                "train_mdd_improve_share": tr.mdd_improve_share,
                "oos_mdd_improve_share": oo.mdd_improve_share,
            })
    decay = pd.DataFrame(decay)
    decay.to_csv(OUT / "train_oos_decay.csv", index=False, encoding="utf-8-sig")

    # Freeze factor direction using train BASE performance separately within each universe.
    frozen = {}
    train_base = summary[(summary["sample"] == "TRAIN_PRE_2023") & (summary.overlay == "BASE")]
    sign_perf = train_base.groupby(["universe", "factor", "direction"])["annualized_return"].mean().reset_index()
    for (universe, factor), g in sign_perf.groupby(["universe", "factor"]):
        frozen[(universe, factor)] = g.sort_values("annualized_return", ascending=False).iloc[0].direction

    frozen_oos = summary[summary["sample"] == "OOS_2023_PLUS"].copy()
    frozen_oos = frozen_oos[frozen_oos.apply(lambda r: frozen.get((r.universe, r.factor)) == r.direction, axis=1)]
    frozen_oos.to_csv(OUT / "frozen_direction_oos.csv", index=False, encoding="utf-8-sig")

    lines = ["# Trading-value overlays across market universes", "",
             "All universes are point-in-time. Both factor directions are tested for robustness; factor direction is also train-selected and frozen for OOS.", ""]
    for universe in UNIVERSES:
        lines += [f"## {universe}", ""]
        for sample in ("TRAIN_PRE_2023", "OOS_2023_PLUS"):
            lines.append(f"### {sample}")
            z = agg[(agg.universe == universe) & (agg["sample"] == sample)].sort_values(
                ["return_improve_share", "median_return_delta"], ascending=False
            )
            for _, r in z.iterrows():
                lines.append(
                    f"- {r.overlay}: return improve {r.return_improve_share:.0%}, Sharpe improve {r.sharpe_improve_share:.0%}, "
                    f"MDD improve {r.mdd_improve_share:.0%}, median return delta {r.median_return_delta:+.2%}, "
                    f"turnover delta {r.median_turnover_delta:+.2f}"
                )
            lines.append("")

    lines += ["# Cross-universe ACT5_KEEP_TOP70", ""]
    z = agg[(agg.overlay == "ACT5_KEEP_TOP70") & (agg["sample"].isin(["TRAIN_PRE_2023", "OOS_2023_PLUS"]))]
    for universe in UNIVERSES:
        tr = z[(z.universe == universe) & (z["sample"] == "TRAIN_PRE_2023")]
        oo = z[(z.universe == universe) & (z["sample"] == "OOS_2023_PLUS")]
        if tr.empty or oo.empty:
            continue
        tr, oo = tr.iloc[0], oo.iloc[0]
        lines.append(
            f"- {universe}: TRAIN improve {tr.return_improve_share:.0%}, median {tr.median_return_delta:+.2%}; "
            f"OOS improve {oo.return_improve_share:.0%}, median {oo.median_return_delta:+.2%}"
        )

    lines += ["", "# Frozen train direction: OOS Top10 / 30bps best overlay", ""]
    key = frozen_oos[(frozen_oos.top_n == 10) & (frozen_oos.cost_bps == 30)]
    for universe in UNIVERSES:
        lines.append(f"## {universe}")
        for factor in sorted(key[key.universe == universe].factor.unique()):
            g = key[(key.universe == universe) & (key.factor == factor)]
            b = g[g.overlay == "BASE"]
            if b.empty:
                continue
            b = b.iloc[0]
            best = g.sort_values("annualized_return", ascending=False).iloc[0]
            lines.append(
                f"- {factor} ({frozen[(universe, factor)]}): BASE {b.annualized_return:.2%} / Sh {b.sharpe:.2f}; "
                f"best {best.overlay} {best.annualized_return:.2%} / Sh {best.sharpe:.2f}; "
                f"delta {best.annualized_return - b.annualized_return:+.2%}"
            )
        lines.append("")

    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print((OUT / "RESEARCH_SUMMARY.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
