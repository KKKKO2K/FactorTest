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

The historical workbook definition has been recovered:

- rank direction: descending
- TopN: 20
- market-cap cutoff: KRW 250bn
- raw signal: weighted average of 1M / 3M / 6M / 12M returns
- exact weights: `12 : 4 : 2 : 1`

So the legacy score is:

`WEIGHTED_MOM = (12 * R1M + 4 * R3M + 2 * R6M + R12M) / 17`

The return-horizon convention was independently recovered by matching the 2026-06-17 workbook snapshot. Calendar-month/as-of returns reproduced the workbook components with about 0.029 percentage-point RMSE and the weighted factor with about 0.023 percentage-point RMSE; a fixed 21/63/126/252-trading-day convention was materially worse.

### Weighted Momentum stage-gate result

The reconstructed primary **fails the independent-primary gate** under the research portfolio implementation (equal-weight Top20, market cap >= KRW 250bn, 10D rebalance, 30bp one-way cost, 10 rebalance phases).

2017-2024 median results:

- K200: CAGR -10.05%, Sharpe -0.34, benchmark-relative CAGR -11.75%, IR -0.63.
- KOSPI ex-K200: CAGR -12.68%, Sharpe -0.32, excess -14.73%, IR -0.67.
- KOSPI all: CAGR -14.80%, Sharpe -0.38, excess -16.42%, IR -0.58.
- KOSDAQ: CAGR -4.74%, Sharpe 0.05, excess -6.07%, IR -0.10.
- KOSPI+KOSDAQ: CAGR -10.00%, Sharpe -0.08, excess -11.66%, IR -0.20.
- KOSDAQ + KOSPI ex-K200: CAGR -9.26%, Sharpe -0.06, excess -10.70%, IR -0.22.

All six universes had 0/10 positive excess-CAGR phases over 2017-2024.

A separate sign diagnostic does not support a simple rank-direction mistake. In 2017-2022, cross-sectional 10D IC was negative in essentially every phase/universe and the high-score Top20 generally underperformed the low-score Bottom20. From 2023 onward the extreme Top20 often improved even while average cross-sectional IC remained negative, indicating a nonlinear/regime-dependent signal rather than a stable monotonic long-momentum factor.

**Decision:** do not proceed to `WEIGHTED_MOM + CF20` or liquidity overlays as a production-candidate research path. CF20 must not be used to rescue this weak primary. If weighted momentum is revisited, the next question is portfolio-construction / historical factor-tracking reconciliation, not overlay optimization.

## Current factor status

- `MOM1M`, `MOM12_1`: simple diagnostic factors; failed to establish strong independent long-only quality in the portfolio audit.
- `WEIGHTED_MOM`: reconstructed and source-validated, but **failed the independent-primary stage gate**; no CF20/liquidity promotion.
- Revision / Value / Flow: remain candidate primary factors, but each must pass independent portfolio-level review before any CF20 or liquidity overlay is considered.

## Guardrails

- 2016-2024 has been repeatedly inspected; 2025/2026 are stress diagnostics, not pristine OOS.
- No parameter search is allowed to rescue a weak primary.
- Large raw/intermediate research outputs must be preserved. If a file may approach GitHub's 100MB per-file limit, store ordered gzip CSV chunks plus a manifest with row ranges/counts, schema, file sizes and SHA-256; retain reusable chunk readers.
- Internal cap-weighted universe benchmarks are sanity-check proxies. Use official benchmark series before production-level attribution where available.
