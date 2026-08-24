# Stage 2 — Discovery Bootstrap / Epistemic Confidence Protocol

## Motivation

Stage 1 rejected confidence defined from a single model's probability geometry: large pairwise margins did not consistently imply better future ranking accuracy.

This stage does **not** tune the Stage-1 threshold or add another single-model margin. It changes the meaning of confidence:

> confidence = how consistently independently resampled Discovery models produce the same factor ranking.

This is an epistemic/model-stability concept rather than a probability-distance concept.

The stage remains post-hoc exploratory because 2020–24 results have already been inspected.

## Frozen training information

Only 2016–19 data are used to fit models or calibrate confidence distributions.

Base pairwise features remain unchanged:
- current 5D difference
- trailing 20D difference
- trailing 60D difference
- trailing 20D volatility difference
- current rank difference

No feature is added.

## Bootstrap ensemble

- 100 pairwise logistic models.
- deterministic RNG seed: `20260824`.
- moving-block bootstrap over Discovery decision dates.
- block length: 8 five-day observations (~40 trading days).
- all 28 factor-pair observations from a sampled date move together as one state block.

This preserves within-date cross-factor structure and some serial dependence.

## Ensemble ranking

At each decision date each of the 100 models produces 28 pairwise probabilities and 8 Borda scores.

The operative factor quality score is the **mean Borda score across models**.

Always-on ensemble benchmarks:
- `ENS_SOFT`: normalized ensemble-mean Borda score.
- `ENS_TOP3`: equal weight predicted top 3.
- `ENS_BOTTOM2_VETO`: equal weight six factors excluding predicted bottom 2.

## Epistemic confidence metrics

1. `PAIR_VOTE_AGREEMENT`
   - for each factor pair, fraction of bootstrap models voting `i > j`;
   - convert to `2*abs(vote_share-0.5)` and average over 28 pairs.

2. `TOP3_JACCARD`
   - compute ensemble-mean top3 set;
   - average Jaccard similarity between each bootstrap model's top3 set and the ensemble top3.

3. `TOP1_VOTE_SHARE`
   - fraction of bootstrap models whose top-ranked factor equals the ensemble top-ranked factor.

4. `SCORE_MODEL_SD`
   - average across 8 factors of the standard deviation of Borda scores across bootstrap models;
   - lower is more confident.

5. `EPI_CONF`
   - equal-weight average of Discovery-standardized `PAIR_VOTE_AGREEMENT`, `TOP3_JACCARD`, `TOP1_VOTE_SHARE`, and negative `SCORE_MODEL_SD`.
   - standardization uses 2016–19 confidence distributions only.

No realized-return outcome is used to weight these metrics.

## Abstention calibration

Same structure as Stage 1:
- hard threshold = Discovery 80th percentile of `EPI_CONF`;
- continuous intensity = `max(0, 2*DiscoveryEmpiricalPercentile(EPI_CONF)-1)`.

No alternative thresholds will be searched.

## Portfolio rules

- `EPI_CONF_SOFT`: ENS_SOFT only above q80, else EW8.
- `EPI_CONF_HALF_TOP3`: `EW8 + 0.5*(ENS_TOP3-EW8)` above q80, else EW8.
- `EPI_CONT_HALF_TOP3`: same half-top3 direction with continuous intensity; zero below Discovery median.
- `EPI_CONF_BOTTOM2_VETO`: bottom2 veto above q80, else EW8.

Costs: 0/10/30 bps per unit factor-weight turnover.

## Diagnostics

Using Discovery-fixed epistemic-confidence quintiles, report for 2020–22, 2023–24, 2025, 2026:
- realized factor-rank IC;
- top3-minus-EW8 spread;
- bottom2-veto-minus-EW8 spread.

The same primary-style economic gate is retained:
- 10bp median ΔSharpe vs EW8 > 0;
- >=4/6 universes improve;
- required in both 2020–22 and 2023–24.

## Anti-overfitting rule

If epistemic confidence also fails, stop confidence engineering on this sample. Do not change block length, bootstrap count, threshold, tilt cap, or confidence components after inspecting results.
