# Sector Decomposition Reset — Stage 1 Plan

## Goal
Restart factor research from stock-level primitives. The first question is not which factor to select, but **what a factor return actually consists of** once WICS industry exposure is separated from within-industry stock selection.

## Data
- Source: `source/factor_all_values`
- Period: 2016-01-04 to 2026-08-07
- Eligible stock set: the factor-row PIT investable universe (empirically ~KRW 250bn+ market cap)
- 8 factors: MOM1M, MOM12_1, OP12_REV, OPFY1_REV, PBR12MF, PER12MF, PRIVATE_FLOW, FOREIGN_FLOW
- Daily adjusted stock returns, market/K200 membership, market cap
- User-supplied current WICS middle-industry mapping; missing labels retained as `UNKNOWN`

## Universe definitions
Primary disjoint universes:
1. K200
2. eligible KOSPI ex-K200
3. eligible KOSDAQ

Composite diagnostics:
4. KOSPI ALL
5. KOSPI + KOSDAQ ALL
6. KOSDAQ + KOSPI ex-K200

Do not count the three composites as independent replications.

## Rebalance / payoff convention
- Signal dates: every 5th available trading date from the source calendar.
- Payoff: compounded adjusted stock return over the next 5 trading dates.
- Non-overlapping 5D blocks by construction.
- Factor direction: higher-is-better except PER12MF and PBR12MF, where lower is better.
- Each factor uses its own valid-value universe. No forced all-8 intersection.

## Raw factor portfolio
Within each date × universe × factor:
- rank all valid stocks by economically favorable factor value;
- top leg = best 20%; bottom leg = worst 20%;
- equal weight stocks in each leg;
- `RAW_LS = TOP_RETURN - BOTTOM_RETURN`.

## Exact sector decomposition of RAW_LS
For each WICS sector `s`:
- `wT_s`, `wB_s`: sector weights in raw top / bottom legs;
- `R_s`: equal-weight forward 5D return of all factor-valid stocks in that sector;
- `RT_s`, `RB_s`: forward returns of raw top / bottom stocks in that sector.

Define:

`ALLOCATION = sum_s (wT_s - wB_s) * R_s`

`WITHIN_SELECTION = sum_s [wT_s*(RT_s-R_s) - wB_s*(RB_s-R_s)]`

Identity check required:

`RAW_LS = ALLOCATION + WITHIN_SELECTION`

up to numerical tolerance.

## Sector-neutral factor portfolio
Independently construct a clean sector-neutral long-short portfolio:
- within each sector with at least 5 valid stocks, take `k=floor(20% * n_sector)` best and worst names, minimum 1;
- top and bottom take the same number from each sector;
- equal weight selected stocks globally, which makes top/bottom sector weights identical by construction;
- `NEUTRAL_LS = NEUTRAL_TOP - NEUTRAL_BOTTOM`.

## Stage 1 questions (descriptive, no factor-selection model)
1. How much of raw factor payoff comes from sector allocation vs within-sector selection?
2. Which factors retain mean return / Sharpe after sector neutralization?
3. Is the answer stable across 2016-19, 2020-22, 2023-24, 2025, 2026?
4. Is sector dependence materially different between K200, ex-K200 and KOSDAQ?
5. How concentrated are raw factor legs by sector, and which factors carry the largest active sector bets?

## Predeclared diagnostics
Per factor × universe × era report:
- mean 5D RAW_LS, ALLOCATION, WITHIN_SELECTION, NEUTRAL_LS
- annualized Sharpe of RAW_LS and NEUTRAL_LS (`sqrt(252/5)` scaling)
- correlation RAW_LS vs NEUTRAL_LS
- `selection_mean_share = mean(WITHIN_SELECTION) / mean(RAW_LS)` when denominator is economically nontrivial; otherwise NA
- variance shares using covariance-consistent decomposition:
  - `cov(RAW, ALLOCATION)/var(RAW)`
  - `cov(RAW, WITHIN_SELECTION)/var(RAW)`
  These two must sum to ~1 because RAW = ALLOCATION + WITHIN_SELECTION.
- median active sector weight = `0.5 * sum_s |wT_s-wB_s|`
- median top/bottom sector HHI

## Interpretation rule
This stage does **not** choose a factor-selection rule. It establishes whether recent raw factor success can reasonably be separated into:
- sector-driven payoff; and
- genuine within-sector stock-selection payoff.

Only after this decomposition is stable enough will Stage 2 pre-register any predictive or selection test based on the quality of factor payoff.
