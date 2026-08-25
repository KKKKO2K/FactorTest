# Stage 3 — Sector-Confirmed Raw Winner Test

## Question
Among factors that are already selected by trailing 20D RAW performance, does positive trailing 20D within-sector selection identify more durable factor strength than sector-driven apparent strength?

This is a **quality-confirmation test**, not a new ranking model.

## Inputs
Use only Stage 1 stock-level decomposition outputs. For each universe/factor/date:
- `RAW20`: sum of the four completed prior 5D `raw_ls` observations.
- `WITHIN20`: sum of the four completed prior 5D `within_selection` observations.
- next realized factor payoff: current 5D `raw_ls`.

No contemporaneous or future information enters RAW20/WITHIN20.

## Candidate set
At every date × universe with at least six factors having complete RAW20/WITHIN20/current raw payoff:
1. rank factors by RAW20;
2. retain RAW20 Top2 only;
3. label each Top2 factor:
   - `CONFIRMED` if `WITHIN20 > 0`;
   - `UNCONFIRMED` if `WITHIN20 <= 0`.

The zero threshold is fixed ex ante. No quantile or optimized cutoff is allowed.

## Primary estimand
The cleanest comparison uses only **discordant Top2 dates**: exactly one of the RAW20 Top2 is CONFIRMED and the other is UNCONFIRMED.

For each discordant date × universe:

`PAIR_DIFF = next5D_raw_return(CONFIRMED) - next5D_raw_return(UNCONFIRMED)`.

This directly compares two factors selected under the same date, same universe, and same RAW20 Top2 condition.

## Secondary diagnostics
- future raw payoff of all CONFIRMED vs all UNCONFIRMED RAW20 Top2 candidates;
- each group’s payoff relative to the same-date EW8 factor payoff;
- confirmation frequency;
- results by factor identity, to ensure one factor is not driving the phenomenon;
- 2025 and 2026 as stress-only diagnostics.

## Primary universes
Only the three disjoint primitive universes count toward the primary gate:
- K200
- KOSPI_EX_K200
- KOSDAQ

Composite universes are descriptive only.

## Era discipline
- 2016–19: discovery/context only
- 2020–22: validation
- 2023–24: confirmation
- 2025 / 2026: stress only

## Primary gate
The hypothesis passes only if **both** 2020–22 and 2023–24 satisfy all of:
1. median primitive-universe mean `PAIR_DIFF > 0`;
2. at least 2 of 3 primitive universes have positive mean `PAIR_DIFF`;
3. pooled mean `PAIR_DIFF > 0`;
4. pooled win rate `P(PAIR_DIFF > 0) > 50%`.

If this gate fails, do not build a veto portfolio from this hypothesis.

## Stage 4 conditional rule
Only if Stage 3 passes, preregister before viewing Stage 4 results a fixed backfill portfolio:
- start with RAW20 ranking;
- exclude factors with `WITHIN20 <= 0`;
- select the highest-ranked two remaining confirmed factors;
- if fewer than two are confirmed, leave the missing slot in EW8 rather than tuning a replacement rule.

Stage 4 must compare this fixed rule with ordinary RAW20 Top2 and EW8 without changing the zero threshold.