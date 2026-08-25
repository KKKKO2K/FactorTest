# Sector Decomposition Reset — Research Status

## Scope
Fresh stock-level research using PIT factor values, stock returns, universe membership, and static WICS middle-industry mapping. No prior Factor Regime labels or selection models are used.

## Stage 1 — Exact sector decomposition
For each 5D factor payoff:

`RAW = SECTOR_ALLOCATION + WITHIN_SECTOR_SELECTION`

A separately constructed sector-neutral factor portfolio is also produced.

- 519 non-overlapping 5D blocks
- 24,912 factor/universe observations
- decomposition max identity error ~7.6e-17

Main descriptive conclusion: factor payoffs are not simply sector bets. Within-sector selection generally explains a large share of payoff variance, but sector allocation can materially alter the level and even the sign of observed raw factor returns.

## Stage 2 — Use within/neutral factor momentum directly for factor selection
Trailing 20D RAW, WITHIN, and NEUTRAL factor performance were compared as selectors of the next 5D factor payoff.

Result: FAIL.

- WITHIN20: 2020–22 median primitive IC +0.021; 2023–24 +0.012. It did not improve sufficiently over RAW20.
- NEUTRAL20: 2020–22 +0.040; 2023–24 -0.032.

Conclusion: simply replacing raw factor momentum with within-sector or sector-neutral factor momentum is not a robust selector.

## Stage 3 — Quality confirmation inside RAW20 Top2
Preregistered question: among factors already in RAW20 Top2, does `WITHIN20 > 0` identify a more durable winner?

Primary test used only discordant dates where one RAW20 Top2 factor had WITHIN20 > 0 and the other had WITHIN20 <= 0.

Result: preregistered diagnostic gate PASS.

Primitive-universe pooled results:
- 2020–22: confirmed minus unconfirmed +0.609% per next 5D; win rate 55.3%; n=47; pooled t=1.21.
- 2023–24: +1.086%; win rate 63.2%; n=38; pooled t=1.56.

But the effect is not broad across universes:
- K200: positive in 2020–22 and 2023–24.
- KOSPI ex-K200: positive in both.
- KOSDAQ: mean pair difference negative in both.

It is also not stable across all eras:
- 2016–19 pooled mean -0.020%.
- 2025 pooled mean -1.641%.
- 2026 sample is very small.

A further practical limitation is selectivity. Among primitive-universe RAW20 Top2 candidates, `WITHIN20 > 0` is already true for roughly 91–93% of candidates in 2020–24. Thus the diagnostic only distinguishes a small set of warning cases.

## Stage 4 — Fixed veto/backfill portfolio
Because Stage 3 passed, one implementation was preregistered before viewing results:
1. rank factors by RAW20;
2. exclude WITHIN20 <= 0;
3. choose the top two remaining confirmed factors;
4. each missing confirmed slot falls back to 50% EW factor basket;
5. no threshold, top-k, or fallback tuning.

Result: primary gate FAIL.

Primitive-universe medians:
- 2020–22: Sharpe improvement vs RAW_TOP2 +0.203; 2/3 universes positive; mean-return improvement +0.0702% per 5D; alpha vs EW +0.1242%.
- 2023–24: Sharpe improvement +0.008; 2/3 positive; mean-return improvement -0.0004%; alpha vs EW -0.0116%.
- 2025: negative.
- 2026: positive but stress-only and short.

The 10bp meta-allocation-turnover proxy does not alter the conclusion.

### Why Stage 3 can pass while Stage 4 fails
Stage 3 asks a narrow paired question: on rare discordant RAW Top2 dates, is the confirmed member better than the unconfirmed member?

Stage 4 requires a different and harder statement: if an unconfirmed Top2 factor is removed, is the next lower-ranked confirmed factor (or EW fallback) a better replacement?

Stage 3 does not establish that replacement proposition. The fixed Stage 4 rule therefore fails despite the positive diagnostic spread.

## Canonical conclusion
WICS decomposition adds useful **diagnostic information about the quality/source of factor returns**, but the tested sector-confirmation variable does not yet support a robust factor-selection portfolio rule.

Keep:
- exact RAW / sector-allocation / within-sector decomposition;
- sector-neutral factor return as a diagnostic;
- the observation that rare sector-unconfirmed RAW winners can be warning cases, especially in KOSPI/K200 samples.

Reject/freeze on this sample:
- direct WITHIN20 or NEUTRAL20 winner ranking;
- `WITHIN20 > 0` fixed veto/backfill rule;
- threshold/top-k/fallback tuning after Stage 4.

## Next research implication
Do not tune the binary confirmation rule on the same sample. The more promising next use of the decomposition is to study **factor construction and factor-return quality**, e.g. whether a factor's raw payoff is driven by sector allocation, genuine within-sector selection, breadth/concentration, and liquidity support, before returning to a new selection rule on a separately defined hypothesis.