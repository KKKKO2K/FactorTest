from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

import run_factor_regime as v1

OUT = Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)


def summarize(corr_long: pd.DataFrame, spreads: pd.DataFrame, events: pd.DataFrame) -> str:
    lines = [
        "# Factor Regime v1", "",
        "Canonical-direction factor portfolios; top-minus-bottom 20% spread plus top-20% absolute return.",
        "5-trading-day non-overlapping factor-return periods. State at t uses only factor returns realized through t.",
        "State terciles are estimated on 2016-2022 TRAIN and frozen for 2023+ OOS. Market returns use prior-day market-cap weights.",
        "", "## Factor correlation change", "",
    ]
    c = (corr_long[corr_long.factor_a != corr_long.factor_b]
         .groupby(["universe", "sample"])["corr"].mean().reset_index())
    for u in v1.FACTOR_UNIVERSES:
        tr = c[(c.universe == u) & (c["sample"] == "TRAIN")]
        oo = c[(c.universe == u) & (c["sample"] == "OOS")]
        if not tr.empty and not oo.empty:
            lines.append(f"- {u}: avg pairwise corr TRAIN {tr.iloc[0]['corr']:+.2f} -> OOS {oo.iloc[0]['corr']:+.2f}")

    lines += ["", "## Same-universe market: strongest sign-stable state relations", ""]
    stable_rows = []
    for u in v1.FACTOR_UNIVERSES:
        lines += [f"### {u}", ""]
        for h in v1.HORIZONS:
            tr = spreads[(spreads["sample"] == "TRAIN") & (spreads.factor_universe == u) &
                         (spreads.market_target == u) & (spreads.horizon == h)]
            oo = spreads[(spreads["sample"] == "OOS") & (spreads.factor_universe == u) &
                         (spreads.market_target == u) & (spreads.horizon == h)]
            m = tr[["state", "high_minus_low", "diff_tstat"]].merge(
                oo[["state", "high_minus_low", "diff_tstat", "low_mean", "high_mean",
                    "low_positive_share", "high_positive_share"]],
                on="state", suffixes=("_train", "_oos"))
            if m.empty:
                continue
            m["same_sign"] = np.sign(m.high_minus_low_train) == np.sign(m.high_minus_low_oos)
            m["score"] = m.same_sign.astype(float) * m.high_minus_low_oos.abs()
            lines.append(f"Horizon {h}D:")
            for _, r in m.sort_values("score", ascending=False).head(5).iterrows():
                lines.append(
                    f"- {r.state}: TRAIN H-L {r.high_minus_low_train:+.2%}, OOS H-L {r.high_minus_low_oos:+.2%} "
                    f"(t={r.diff_tstat_oos:+.2f}); low/high means {r.low_mean:+.2%}/{r.high_mean:+.2%}; "
                    f"same-sign={bool(r.same_sign)}"
                )
                if r.same_sign:
                    stable_rows.append({
                        "factor_universe": u, "horizon": h, "state": r.state,
                        "train_high_minus_low": r.high_minus_low_train,
                        "oos_high_minus_low": r.high_minus_low_oos,
                        "oos_tstat": r.diff_tstat_oos,
                        "oos_low_mean": r.low_mean, "oos_high_mean": r.high_mean,
                        "oos_low_positive_share": r.low_positive_share,
                        "oos_high_positive_share": r.high_positive_share,
                    })
        lines.append("")

    stable = pd.DataFrame(stable_rows)
    stable.to_csv(OUT / "stable_same_universe_states.csv", index=False, encoding="utf-8-sig")

    lines += ["## Strong-leader correction events", "",
              "Event = trailing ~60D factor leader strength in TRAIN-defined top tercile AND latest 5D leader spread return < 0.",
              "High/low support is split with TRAIN medians. The key question is whether other factor portfolios staying positive matters for the next market return.", ""]
    if not events.empty:
        for u in v1.FACTOR_UNIVERSES:
            z = events[(events["sample"] == "OOS") & (events.factor_universe == u) & (events.market_target == u)]
            if z.empty:
                continue
            lines.append(f"### {u}")
            for _, r in z.assign(absdiff=z.high_minus_low.abs()).sort_values("absdiff", ascending=False).head(8).iterrows():
                lines.append(
                    f"- {r.support_state}, {int(r.horizon)}D: high-support {r.high_support_mean:+.2%} vs "
                    f"low-support {r.low_support_mean:+.2%}; diff {r.high_minus_low:+.2%}, "
                    f"t={r.diff_tstat:+.2f}, n={int(r.n_high)}/{int(r.n_low)}"
                )
            lines.append("")

    lines += ["## Guardrails", "",
              "- This is screening, not a production timing model.",
              "- 20D forward returns overlap across 5D state dates, so naïve t-stats overstate formal significance.",
              "- Only TRAIN/OOS sign-stable states should be eligible for a later small composite; do not select on OOS magnitude alone.", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    returns, mcap, k200_by_date = v1.base.load_basic()
    market_by_date = v1.mu.load_market_by_date()
    ta = v1.base.load_trading_amount()
    liq_frames = v1.base.build_liquidity_features(ta, mcap)

    market_returns = v1.make_market_returns(returns, mcap, k200_by_date, market_by_date)
    market_returns.to_csv(OUT / "market_daily_returns.csv", encoding="utf-8-sig")
    market_fwd = {h: v1.forward_market(market_returns, h) for h in v1.HORIZONS}

    factor_long, liq_states, _ = v1.build_factor_period_returns(
        returns, mcap, k200_by_date, market_by_date, ta, liq_frames)
    factor_long.to_csv(OUT / "factor_5d_returns.csv", index=False, encoding="utf-8-sig")
    liq_states.to_csv(OUT / "liquidity_states.csv", index=False, encoding="utf-8-sig")

    states, corr_long = v1.build_states(factor_long, liq_states)
    states.to_csv(OUT / "regime_states.csv", index=False, encoding="utf-8-sig")
    corr_long.to_csv(OUT / "factor_correlation_long.csv", index=False, encoding="utf-8-sig")

    bins, spreads = v1.state_bin_tests(states, market_fwd)
    bins.to_csv(OUT / "state_tercile_results.csv", index=False, encoding="utf-8-sig")
    spreads.to_csv(OUT / "state_high_low_spreads.csv", index=False, encoding="utf-8-sig")

    events = v1.leader_event_tests(states, market_fwd)
    events.to_csv(OUT / "leader_correction_events.csv", index=False, encoding="utf-8-sig")

    text = summarize(corr_long, spreads, events)
    (OUT / "RESEARCH_SUMMARY.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
