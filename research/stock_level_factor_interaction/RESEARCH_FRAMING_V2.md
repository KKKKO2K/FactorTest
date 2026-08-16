# Factor Research Framing V2

## Why this reset exists

The CF20 portfolio audit showed that the previously constructed eight-factor equal-notional aggregate is not a strong standalone long-only strategy. That aggregate was never the object originally validated by the CF20 research. CF20 was validated as an incremental stock-selection overlay versus each primary factor sleeve.

Therefore the production/research hierarchy is reset as follows.

## Research hierarchy

1. **Independent primary factor**
   - A primary factor must first be evaluated on its own economic and portfolio merits.
   - Report absolute CAGR, MDD, Sharpe, Calmar, turnover, and benchmark-relative CAGR / tracking error / information ratio.
   - Use 10 rebalance phases and the same point-in-time discipline used by the portfolio audit.
   - A weak primary is not rescued or promoted merely because an overlay improves it.

2. **Frozen CF20 enhancement**
   - Only after the primary is independently credible, test the frozen score:
     `CF20 = 0.80 * primary_rank + 0.20 * other-three-family consensus`.
   - The 20% weight remains frozen. Prior sensitivity suggested a broad small-overlay plateau around 15-20%, but no ex-post re-optimization is allowed.
   - Evaluate incremental CAGR, Sharpe, relative performance, turnover, and phase consistency versus the same primary.

3. **Liquidity quality-control overlay**
   - Only after primary + CF20 are credible, test a predeclared liquidity veto.
   - Liquidity is treated primarily as an eligibility / signal-quality variable, not automatically as another alpha score.
   - The liquidity overlay must add incremental value after CF20 rather than merely improve a weak baseline.

4. **Production construction**
   - Portfolio weighting and benchmark integration are a separate layer from stock ranking.
   - Do not infer that an equal-weight Top-N research sleeve is itself the intended production portfolio.

## Retired interpretation

- The `PRIMARY8` and `CF20` eight-factor equal-notional aggregates are **diagnostic only** and are removed from the production-candidate set.
- Their weak standalone performance does not invalidate an incremental CF20 effect, but it invalidates any claim that the equal-sleeve CF20 aggregate was previously proven as a strong strategy.

## Momentum reset

The simple research inputs `MOM1M` and `MOM12_1` are not accepted as substitutes for the historical `모멘텀(가중)` factor.

The historical workbook definition has now been recovered:

- rank direction: descending
- TopN: 20
- market-cap cutoff: KRW 250bn
- raw signal: weighted average of 1M / 3M / 6M / 12M returns
- recovered exact weights: `12 : 4 : 2 : 1`

So the legacy score is:

`WEIGHTED_MOM = (12 * R1M + 4 * R3M + 2 * R6M + R12M) / 17`

The next Momentum study must first reconstruct and validate this signal against the workbook snapshot, then evaluate its standalone portfolio, and only then test CF20 on it.

## Current factor status

- `MOM1M`, `MOM12_1`: simple diagnostic factors; failed to establish strong independent long-only quality in the portfolio audit.
- `WEIGHTED_MOM`: under revalidation; do not assume strength until the reconstruction backtest is complete.
- Revision / Value / Flow: remain candidate primary factors, but each should also pass independent portfolio-level review before production use.

## Guardrails

- 2016-2024 has been repeatedly inspected; 2025/2026 are stress diagnostics, not pristine OOS.
- No parameter search is allowed to rescue a weak primary.
- Large raw/intermediate research outputs must be preserved. If a file may approach GitHub's 100MB per-file limit, store ordered gzip CSV chunks plus a manifest with row ranges/counts, schema, file sizes and SHA-256; retain reusable chunk readers.
- Internal cap-weighted universe benchmarks are sanity-check proxies. Use official benchmark series before production-level attribution where available.
