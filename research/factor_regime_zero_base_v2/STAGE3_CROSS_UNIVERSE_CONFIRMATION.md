# Stage 3 Pre-Registration — Cross-Universe Factor Confirmation

Written after Stage 2 and before Stage-3 results are observed.

## Motivation from zero-base evidence

Stage 0 found one exceptionally stable contemporaneous structure: the 8-factor ranking is highly similar across the six universe definitions, with median pairwise 20D rank correlation around +0.69 or higher in every era.

At the same time, unconditional current-top2 continuation is near random-overlap baselines. Therefore the next question is not whether factor winners persist on average, but whether **cross-universe confirmation distinguishes robust factor signals from local noise**.

This is different from forecasting aggregate coherence. Stage 1 already rejected aggregate future-coherence prediction.

## Observation unit

Each observation is `date × universe × factor`.

At each date and universe:
- `LOCAL_RANK20`: percentile rank of the factor's current 20D payoff among the 8 factors.

Across the six universes for the same date and factor:
- `GLOBAL_MEAN_RANK20`: mean of the six local percentile ranks;
- `GLOBAL_TOP2_SHARE`: fraction of universes where the factor is in the current top 2;
- `GLOBAL_POSITIVE_SHARE`: fraction of universes where current 20D factor payoff is positive;
- `GLOBAL_MEAN_PAYOFF20`: mean current 20D factor payoff across universes;
- `GLOBAL_RANK_DISPERSION20`: standard deviation of local factor ranks across universes.

Targets:
- local future 20D factor payoff;
- local future 20D factor percentile rank.

## Primary hypothesis — global rank confirmation

`GLOBAL_MEAN_RANK20` should predict local future factor payoff/rank at least as well as, and ideally better than, `LOCAL_RANK20`.

Primary PASS gate, evaluated separately in 2020–22 and 2023–24:
1. median universe cross-sectional IC of GLOBAL_MEAN_RANK20 vs future payoff > +0.05;
2. positive IC in at least 4/6 universes;
3. median `GLOBAL IC - LOCAL IC` > +0.02.

Both periods must pass.

## Secondary hypothesis — locally strong factors need global confirmation

Restrict to factors that are current local top 2.

Define `GLOBALLY_CONFIRMED = GLOBAL_TOP2_SHARE >= 0.50`, i.e. the factor is top-2 in at least 3 of 6 universes.

For each validation period, compare future 20D payoff of confirmed vs unconfirmed local-top2 observations.

Secondary PASS requires:
- positive confirmed-minus-unconfirmed mean future payoff in the median universe in both 2020–22 and 2023–24;
- positive spread in at least 4/6 universes in both periods;
- at least 15 observations in each comparison cell for a universe-period to count.

## Secondary diagnostic — disagreement penalty

Test `-GLOBAL_RANK_DISPERSION20` against future local payoff. Lower rank disagreement is hypothesized to be better.

This is diagnostic only unless it independently meets the same IC gate as the primary hypothesis.

## Samples

- Discovery/context only: 2016–2019.
- Validation: 2020–2022.
- Confirmation: 2023–2024.
- Stress: 2025 and 2026.

No threshold other than the natural 3-of-6 confirmation rule may be changed after results.

## Decision rule

If cross-universe confirmation fails, do not continue building factor-return-only regime variables from the same 8-factor panel. The next research extension must introduce genuinely new information such as stock-level breadth, factor holdings overlap, or external market/macro state.
