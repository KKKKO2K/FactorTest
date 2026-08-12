from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

import run_full_state_map as base

HERE = Path(__file__).resolve().parent
OUT = HERE / "results"
OUT.mkdir(parents=True, exist_ok=True)

# Non-overlapping validation blocks preserve enough observations for granular state contrasts.
# Every block fits state thresholds using only data strictly before the block.
VALID_BLOCKS = (
    (2020, 2021),
    (2022, 2023),
    (2024, 2025),
)


def build_block_states(p: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for start_year, end_year in VALID_BLOCKS:
        v0 = pd.Timestamp(f"{start_year}-01-01")
        v1 = pd.Timestamp(f"{end_year + 1}-01-01")
        label = f"{start_year}-{end_year}"
        for (u, fam), g in p.groupby(["universe", "family"]):
            tr = g[(g.date >= base.STATIC_TRAIN_START) & (g.date < v0)].spread_20d.dropna()
            if len(tr) < 40:
                continue
            cut = float(tr.abs().quantile(base.CUTS[base.MAIN_CUT]))
            if not np.isfinite(cut) or cut <= 0:
                continue
            z = g[(g.date >= base.STATIC_TRAIN_START) & (g.date < v1)]
            for r in z.itertuples():
                split = "VALID" if v0 <= r.date < v1 else ("TRAIN" if r.date < v0 else None)
                if split is None or not (np.isfinite(r.spread_20d) and np.isfinite(r.top_20d)):
                    continue
                rows.append({
                    "eval_block": label, "valid_start": v0, "valid_end": v1, "split": split,
                    "date": r.date, "universe": u, "family": fam,
                    "state6": base.state6_from(r.spread_20d, r.top_20d, cut), "cut": cut,
                    "top_20d": r.top_20d, "bottom_20d": r.bottom_20d, "spread_20d": r.spread_20d,
                    "spread_60d": r.spread_60d,
                    "member_positive_spread_share_20d": r.member_positive_spread_share_20d,
                    "member_same_sign_20d": r.member_same_sign_20d,
                })
    return pd.DataFrame(rows)


def build_block_contrasts(states: pd.DataFrame, primitives: pd.DataFrame, market: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    for block in states.eval_block.unique():
        for fa, fb in base.FAMILY_PAIRS:
            for split in ("TRAIN", "VALID"):
                ss = states[(states.eval_block == block) & (states.split == split)]
                x = base.prepare_pair_obs(ss, primitives, market, fa, fb)
                for u, g in x.groupby("universe"):
                    for anchor, other, ac, oc in ((fa, fb, "state_a", "state_b"), (fb, fa, "state_b", "state_a")):
                        for cname, (ast, left, right) in base.CONTRASTS.items():
                            row = base.contrast_one(
                                g, ac, oc, cname, ast, left, right,
                                {"eval_block": block, "split": split, "universe": u,
                                 "family_pair": f"{fa}_X_{fb}", "anchor_family": anchor, "other_family": other}
                            )
                            if row:
                                rows.append(row)
    raw = pd.DataFrame(rows)
    stability = []
    if raw.empty:
        return raw, pd.DataFrame()
    outcomes = [c for c in raw.columns if c.endswith("_diff")]
    keys = ["universe", "family_pair", "anchor_family", "other_family", "contrast"]
    for key, g in raw.groupby(keys):
        tr = g[g.split == "TRAIN"]
        va = g[g.split == "VALID"]
        for out in outcomes:
            m = tr[["eval_block", out]].merge(va[["eval_block", out]], on="eval_block", suffixes=("_train", "_valid")).dropna()
            if m.empty:
                continue
            same = np.sign(m[f"{out}_train"]) == np.sign(m[f"{out}_valid"])
            stability.append({
                **dict(zip(keys, key)), "outcome": out, "n_blocks": len(m),
                "sign_stability": float(same.mean()),
                "median_train_diff": float(m[f"{out}_train"].median()),
                "median_valid_diff": float(m[f"{out}_valid"].median()),
                "positive_valid_block_share": float((m[f"{out}_valid"] > 0).mean()),
                "min_valid_n_left": int(va.n_left.min()) if len(va) else np.nan,
                "min_valid_n_right": int(va.n_right.min()) if len(va) else np.nan,
            })
    return raw, pd.DataFrame(stability)


def write_summary(stability: pd.DataFrame) -> str:
    lines = [
        "# Full State Map — Non-overlapping Block Walk-forward", "",
        "Validation blocks: 2020-2021, 2022-2023, 2024-2025. Each block uses an expanding training sample ending strictly before the block.",
        "This block design is used because annual W+/W-/N+/N-/R+/R- conditional cells are too sparse for the predeclared minimum of 8 observations per side.",
        "No minimum-N rule was relaxed; the validation horizon was widened instead.", "",
        "## Market +20D contrasts with all 3 blocks available", "",
    ]
    if stability.empty:
        lines.append("No contrast survived all requirements.")
        return "\n".join(lines) + "\n"
    z = stability[(stability.outcome == "mkt_20d_diff") & (stability.n_blocks == len(VALID_BLOCKS))].copy()
    z["abs_valid"] = z.median_valid_diff.abs()
    z = z.sort_values(["sign_stability", "abs_valid"], ascending=[False, False])
    for _, r in z.iterrows():
        lines.append(
            f"- {r.universe} | {r.anchor_family}->{r.other_family} | {r.contrast}: "
            f"sign {r.sign_stability:.0%}; median TRAIN {r.median_train_diff:+.2%}, VALID {r.median_valid_diff:+.2%}; "
            f"min valid n {int(r.min_valid_n_left)}/{int(r.min_valid_n_right)}"
        )
    lines += ["", "## Interpretation discipline", "",
              "- Three blocks are still a small validation count; 100% means 3/3, not proof of invariance.",
              "- Prefer relations whose sign is stable, median TRAIN and VALID effect have similar magnitude, and both sides retain adequate sample counts.",
              "- Static 2023+ cells remain descriptive and must not override block walk-forward evidence.", ""]
    return "\n".join(lines) + "\n"


def main() -> None:
    f, market = base.load_inputs()
    primitives = base.add_forward_family_metrics(base.build_family_primitives(f))
    states = build_block_states(primitives)
    raw, stability = build_block_contrasts(states, primitives, market)
    states.to_csv(OUT / "family_states_block_walkforward.csv", index=False, encoding="utf-8-sig")
    raw.to_csv(OUT / "common_contrasts_block_walkforward.csv", index=False, encoding="utf-8-sig")
    stability.to_csv(OUT / "block_walkforward_contrast_stability.csv", index=False, encoding="utf-8-sig")
    (OUT / "BLOCK_WALKFORWARD_SUMMARY.md").write_text(write_summary(stability), encoding="utf-8")
    print(f"block states: {len(states):,}")
    print(f"block contrasts: {len(raw):,}")
    print(f"stability rows: {len(stability):,}")


if __name__ == "__main__":
    main()
