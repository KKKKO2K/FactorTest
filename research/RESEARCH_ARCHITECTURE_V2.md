# Factor Research Architecture v2

## Core lesson

Do not compress economically distinct information before testing the question that needs it. Preserve factor identity, preferred-leg absolute return, opposite-leg absolute return, and relative spread first. Breadth and composite regime scores are downstream summaries.

## Layer 0 — Primitive factor outcomes

For every factor/universe/date keep:

- preferred portfolio absolute return
- opposite portfolio absolute return
- preferred minus opposite relative spread
- point-in-time universe and portfolio membership

These are the primitive observables. Relative spread alone cannot distinguish positive alpha from defensive relative performance.

## Layer 1 — Factor state

Relative state is defined from a TRAIN-calibrated dead zone around zero:

- WORKING
- NEUTRAL
- REVERSE

Then attach preferred-leg absolute sign:

- W+ = relative working, preferred absolute return > 0
- W- = relative working, preferred absolute return <= 0
- N+ / N- retained diagnostically; N may be collapsed when sample size is limited
- R+ = relative reverse, preferred absolute return > 0
- R- = relative reverse, preferred absolute return <= 0

Use cumulative preferred and opposite leg returns to define multi-period spread; retain compounded legacy LS only as a robustness diagnostic.

## Layer 2 — Cross-factor interaction / rotation

Predeclare economically meaningful family pairs before looking for winners:

- Momentum x Revision
- Momentum x Value
- Momentum x Flow

Primary pair regimes:

- Genuine rotation: Momentum R- + Other W+
- Defensive rotation: Momentum R- + Other W-
- Bullish style shift: Momentum R+ + Other W+
- Broad confirmation: Momentum W+ + Other W+
- Defensive confirmation: Momentum W- + Other W-
- Broad breakdown: Momentum R- + Other R-

Do not label Momentum R + Other W as rotation without absolute-leg confirmation.

## Layer 3 — Cross-factor summaries

Only after factor states are preserved, create summaries:

- Relative working breadth
- Absolute-confirmed breadth (W+ share)
- Defensive-working breadth (W- share)
- Reverse breadth
- Bullish reverse breadth (R+ share)
- Bearish reverse breadth (R- share)
- Dispersion
- Correlation
- Leader strength / leader correction

Breadth is a summary layer, not the primitive regime state.

## Layer 4 — Market participation / liquidity

Keep stock-selection liquidity overlays separate from market-state liquidity variables.

Stock-selection layer:

- ACT1 confirmation
- ACT5 stale-signal veto
- residual trading amount / turnover robustness

Market-state layer:

- MKT_ACT5_BREADTH
- MKT_ACT1_BREADTH
- factor-winner activity breadth

Do not infer market timing from a stock-selection overlay without a separate test.

## Layer 5 — Market regime and decisions

Test whether factor identity/state, rotation, cross-factor summaries, and market participation explain:

- future +1D / +5D / +20D market return
- downside / drawdown risk
- persistence or reversal of each factor
- factor allocation implications

K200, KOSPI ex-K200, and KOSDAQ must be modeled separately unless evidence supports pooling.

## Research tracks

### A. Factor Enhancement

Question: does an auxiliary signal improve a specific factor's stock-selection performance?

Examples:

- MOM12-1 + 1M conditioning
- liquidity confirmation
- stale-signal veto

Primary evaluation: IC, top portfolio excess return, hit rate, turnover, costs, universe robustness.

### B. Factor State / Rotation

Question: which factors are making money absolutely, which are only relatively strong, which are reversing, and is leadership rotating?

Primary evaluation: W+/W-/N/R+/R- states, pair regimes, next factor returns, next market returns.

### C. Market Regime

Question: given factor states/rotation and participation, what does the market do next?

Primary evaluation: market returns and downside conditional on factor-state and liquidity-state combinations.

## Validation discipline

- 2016-2022 vs 2023+ is no longer an untouched OOS split because 2023+ informed horizon and state discovery.
- Current 2023+ results are post-discovery validation.
- Next formal validation should use expanding or rolling walk-forward estimation, with thresholds fit only on information available before each validation year.
- Prefer parameter neighborhoods and sign stability over the single best backtest cell.
- Predeclare pair families and contrasts before promoting a result.
- Keep sample counts visible for all conditional-state cells.
