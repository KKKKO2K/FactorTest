# Factor Return Quality / Internals — Research Plan

## Objective
Study whether the **quality/source of a recent factor move** contains incremental information for the next factor payoff after controlling for the magnitude of the recent move itself.

This is not a Factor Regime exercise and does not use prior HIGH/LOW labels, clustering, KMeans, dispersion/breadth regime states, or prior selection rules.

## Data
- Daily PIT stock-level factor values for 8 canonical factors.
- Daily stock returns and point-in-time universe membership.
- Daily trading amount.
- Static WICS middle-industry mapping carried from the sector-decomposition scratch track.
- Existing exact sector decomposition output is reused only as an audited accounting input:
  `RAW = SECTOR_ALLOCATION + WITHIN_SECTOR_SELECTION`.

Primary universes are the three disjoint primitive universes:
- K200
- KOSPI_EX_K200
- KOSDAQ

Composite universes are descriptive only.

## Timeline discipline
Every quality feature at signal date t is formed only from the **four completed prior non-overlapping 5D blocks**. The current 5D payoff beginning after t is the target.

- 2016–19: discovery/context only
- 2020–22: validation
- 2023–24: confirmation
- 2025 / 2026: stress-only

No feature sign or threshold is chosen from validation/confirmation results.

## Block-level stock-internal measures
For each factor × universe × completed 5D block, reconstruct the factor Top20% and Bottom20% sleeves using the signal-date PIT factor values.

### 1. Positive-direction pairwise breadth
`PAIRWISE_BREADTH = P(r_top_stock > r_bottom_stock)` across all Top×Bottom stock pairs during the realized 5D block.

This is market-relative breadth: 0.5 is neutral, values above 0.5 mean the preferred factor sleeve broadly beat the opposite sleeve rather than the L/S result being driven by a few names.

### 2. Contribution concentration
Each stock's equal-weight contribution to the factor L/S payoff is:
- Top leg: `+r_i / N_top`
- Bottom leg: `-r_i / N_bottom`

`TOP5_ABS_CONTRIB_SHARE` is the fraction of total absolute L/S contribution accounted for by the five largest absolute stock contributions.

Lower concentration is treated ex ante as higher-quality participation.

### 3. Trading-activity support
For each stock in a completed factor block:
- baseline activity = mean daily trading amount over the 20 trading days ending on the factor signal date;
- realized-block activity = mean daily trading amount during the following 5 trading days;
- activity ratio = realized-block / baseline.

Within each factor-valid universe, convert the activity ratio to a cross-sectional percentile rank.

`LIQUIDITY_SUPPORT` = mean activity percentile of Top+Bottom sleeve stocks minus mean activity percentile of all factor-valid stocks.

Higher values mean the factor sleeves attracted more trading activity than the surrounding universe while the factor payoff was realized.

### 4. Within-sector support
Use the exact WICS decomposition from the completed block. At the 20D level this is summarized as the share of recent factor-direction magnitude supported by within-sector selection rather than sector allocation.

## 20D quality features at evaluation date
Using only the previous four completed blocks:

- `RAW20 = sum(raw_ls)`
- `WITHIN20 = sum(within_selection)`
- `ALLOCATION20 = sum(allocation)`

Quality axes:

1. `WITHIN_ALIGNMENT`
   `sign(RAW20) * WITHIN20 / (abs(WITHIN20) + abs(ALLOCATION20) + eps)`
   Higher means the direction of the recent factor move was supported more by within-sector stock selection.

2. `BREADTH_ALIGNMENT`
   Let `BREADTH20` be the mean prior-four-block pairwise breadth.
   - if RAW20 >= 0: `BREADTH_ALIGNMENT = BREADTH20`
   - if RAW20 < 0: `BREADTH_ALIGNMENT = 1 - BREADTH20`
   Higher means stock-level breadth confirms the direction of the recent 20D factor move.

3. `BROAD_CONTRIBUTION`
   `1 - mean(TOP5_ABS_CONTRIB_SHARE)` over the prior four blocks.
   Higher means recent factor payoff was less dependent on a few stocks.

4. `LIQUIDITY_SUPPORT20`
   Mean prior-four-block `LIQUIDITY_SUPPORT`.
   Higher means the recent factor sleeves experienced stronger relative trading activity.

## Targets
### Primary selection target
`NEXT_RAW5`: next realized 5D raw factor payoff.

The baseline selector is `RAW20`.

For each quality axis, create a direction-aware quality score for absolute factor selection:
`SIGNED_QUALITY = sign(RAW20) * centered_cross_sectional_rank(QUALITY)`.

The primary estimand is the cross-sectional partial rank IC between `SIGNED_QUALITY` and `NEXT_RAW5`, controlling for the cross-sectional rank of `RAW20`.

### Mechanism target
`CONTINUATION5 = sign(RAW20) * NEXT_RAW5`.

The secondary estimand is the partial rank IC between raw quality and `CONTINUATION5`, controlling for `abs(RAW20)` rank. This tests whether quality specifically distinguishes durable vs fragile recent moves.

### Selection diagnostic
Within the four factors with the highest RAW20 on each date × universe, compare next 5D payoff of the two higher-quality factors vs the two lower-quality factors.

No optimized cutoff is used.

## Primary survival gate for a quality axis
A quality axis survives only if **both** 2020–22 and 2023–24 satisfy:
1. median primitive-universe mean primary partial IC > +0.02;
2. primary partial IC positive in at least 2 of 3 primitive universes;
3. median primitive-universe Top4 high-quality minus low-quality next-5D spread > 0;
4. Top4 quality spread positive in at least 2 of 3 primitive universes.

Discovery and stress eras cannot rescue a failure.

## Multiple-testing discipline
There are exactly four preregistered quality axes. No feature transformation, sign flip, threshold search, top-k search, or ad-hoc combination is allowed after seeing Stage 2 results.

If one or more axes survive, the next stage will falsify only those survivors with gap / non-overlap / factor-identity diagnostics before any portfolio rule is built.

If none survive, stop this quality-selection avenue rather than engineering more variants from the same sample.
