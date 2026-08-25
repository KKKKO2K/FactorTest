# Stage 4 — Fixed Sector-Confirmation Veto/Backfill Portfolio

Stage 3 passed its preregistered diagnostic gate. Stage 4 therefore tests one fixed economic implementation. No threshold or parameter search is permitted.

## Inputs
For each date × universe, using only completed prior observations:
- `RAW20` = sum of prior four 5D raw factor payoffs.
- `WITHIN20` = sum of prior four 5D within-sector selection components.
- current 5D `raw_ls` is the realized payoff.

Require at least six factors with complete inputs.

## Benchmarks
### EW
Equal weight across all factors with complete inputs on that date.

### RAW_TOP2
Top two factors by RAW20, 50% factor-allocation weight each.

## Fixed veto/backfill rule: SECTOR_CONFIRMED_TOP2
1. Rank all available factors by RAW20.
2. Remove every factor with `WITHIN20 <= 0`.
3. Take the highest-ranked two remaining factors.
4. Each confirmed slot receives 50% of the meta-factor portfolio.
5. If fewer than two confirmed factors exist, each missing 50% slot is allocated to that date's EW factor basket.
   - 2 confirmed: 50% + 50% confirmed factors.
   - 1 confirmed: 50% confirmed factor + 50% EW.
   - 0 confirmed: 100% EW.

The zero confirmation threshold and two-slot structure are fixed from Stage 3. No alternative threshold, top-k, or fallback is allowed.

## Return and turnover
- Gross return = weighted average of realized current 5D `raw_ls` factor payoffs.
- Meta-allocation turnover = `0.5 * sum(abs(w_t - w_{t-1}))` across the canonical eight factor weights.
- A 10bp per unit meta-turnover cost proxy is reported as a secondary implementation diagnostic. It is not a full stock-level trading-cost model.

## Primary universes and eras
Primary universes: K200, KOSPI_EX_K200, KOSDAQ.

Era discipline:
- 2016–19: context
- 2020–22: validation
- 2023–24: confirmation
- 2025/2026: stress only

## Primary gate
The fixed veto rule passes only if **both** 2020–22 and 2023–24 satisfy all of:
1. median primitive-universe gross Sharpe improvement vs RAW_TOP2 > 0;
2. at least 2/3 primitive universes have positive Sharpe improvement vs RAW_TOP2;
3. median primitive-universe mean return difference vs RAW_TOP2 > 0;
4. median primitive-universe mean alpha vs EW > 0.

10bp meta-turnover-cost results must also be reported but do not override the primary gate because this cost proxy does not model stock-level sleeve turnover.

## Stop rule
Regardless of outcome, do not tune `WITHIN20 > 0`, top-k, fallback weights, or lookback on the same sample after Stage 4.