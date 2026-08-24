# Stage 2 — Does sector-neutral factor strength select future factors better?

## Motivation
Stage 1 shows that raw factor payoff can materially differ from its within-sector component and from an independently constructed sector-neutral factor portfolio. Stage 2 asks whether that distinction is useful for **factor selection**, without fitting a new return-forecasting model.

## Information set
At each 5D signal date `t`, only completed prior 5D blocks are observable. For each universe × factor, construct trailing 20D scores from the previous four completed blocks (`shift(1).rolling(4)`):

1. `RAW20` = sum of prior 4 `raw_ls`
2. `WITHIN20` = sum of prior 4 exact `within_selection`
3. `NEUTRAL20` = sum of prior 4 independently constructed `neutral_ls`

No current-block payoff enters a predictor.

## Selection estimand
For every date × universe, rank the available 8 factors cross-sectionally by each score. Evaluate the ranking against:
- next/current block `raw_ls` (what the investor would earn using the ordinary factor construction), and
- next/current block `neutral_ls` (cleaner within-sector payoff target).

Primary universes: K200, eligible KOSPI ex-K200, eligible KOSDAQ.
Composite universes remain diagnostics only.

## Metrics
For each score × universe × era:
- Spearman rank IC with future 5D raw factor payoff
- Spearman rank IC with future 5D neutral factor payoff
- Top-2 selected factor mean future RAW_LS minus EW8 factor mean
- Top-2 selected factor mean future NEUTRAL_LS minus EW8 neutral-factor mean
- exact top-2 overlap with realized future top-2 (diagnostic)

## Eras
- Discovery: 2016-19
- Validation: 2020-22
- Confirmation: 2023-24
- Stress only: 2025, 2026

## Primary hypothesis
A sector-quality score (`WITHIN20` or `NEUTRAL20`) is a credible improvement over ordinary recent factor momentum (`RAW20`) only if, in both 2020-22 and 2023-24:
1. median primitive-universe IC to future RAW_LS is positive;
2. at least 2 of 3 primitive universes have positive IC;
3. median IC exceeds RAW20 by at least +0.02; and
4. median primitive-universe Top2-minus-EW8 future RAW_LS is positive.

No threshold, lookback, factor subset, or weighting parameter will be changed after seeing Stage 2 results.
