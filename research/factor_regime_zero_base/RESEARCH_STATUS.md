# Zero-Base Factor Regime Research Status

## Current research order

1. **Factor Persistence / Rotation** — completed Stage 1 + economic Stage 1b.
2. **Factor Opportunity** — completed Stage 2 + combined Stage 2b policy.
3. **Factor Crash / Crowding** — completed factor-return-only Stage 3 + Stage 3b crash cap; factor-return-only crash research is frozen.
4. **Stock-Level Regime Extension** — completed Stage 4A aggregate stock/liquidity predictive screen + Stage 4B hard permission policy.
5. **Continuous Factor Risk Budgeting** — Stage 5 survivor-based continuous tilt completed; all three continuous variants passed the predeclared 10 bps gate. A feature-selection-bias audit using the entire predeclared Stage-1 and Stage-4A candidate sets is now the required robustness step before production interpretation.
6. **Leader-Specific Raw Stock Extension** — only if the selection-bias audit fails; reconstruct leader-specific participation, turnover/ADV, contribution concentration and holdings overlap from raw point-in-time stock data.
7. **Market Transition** — secondary use only after the factor-allocation questions above are exhausted.

## Stage 5 result — survivor-based continuous tilt

Portfolio mapping was frozen before the run:

`w_t = EW8 + lambda_t * (TOP2 - EW8)`

with `lambda` bounded to [-0.25,+0.25], prior-data percentile mapping only, and no threshold/max-tilt sweep.

At 10 bps:
- Persistence continuous: DEV 2020-22 median ΔSharpe vs EW8 +0.129; CONFIRM 2023-24 +0.159; 4/6 confirmation universes improve.
- Liquidity continuous: DEV +0.001; CONFIRM +0.190; 4/6 confirmation universes improve.
- Combined continuous: DEV +0.093; CONFIRM +0.158; 5/6 confirmation universes improve.
- Combined also remains positive in 2025 (+0.074 median ΔSharpe) and YTD 2026 (+0.029).

This is the strongest economic Factor Regime result so far. However the survivor lists themselves were selected using prior Stage-1 / Stage-4A DEV+CONFIRM evidence, so 2023-24 is not an untouched validation sample. The result is therefore **promising but not yet production-grade**.

## Required robustness audit now running

To remove feature-selection leakage from the predictor list:
- Persistence block uses **all 18 predictors declared before Stage 1**, not the seven survivors.
- Liquidity block uses **all 10 aggregate stock/liquidity features declared before Stage 4A**, not the three survivors.
- No features are removed using 2020-24 outcomes.
- Only direction, standardization and empirical percentile mapping are estimated from prior data each evaluation year.
- Portfolio mapping and max tilt remain exactly unchanged: EW8 + lambda*(TOP2-EW8), lambda in [-0.25,+0.25].
- Same 0/10/30 bps costs and non-overlapping 20D schedule.

Robustness PASS at 10 bps requires:
- positive median ΔSharpe vs EW8 in DEV 2020-22;
- positive median ΔSharpe vs EW8 in CONFIRM 2023-24;
- >=4/6 confirmation universes improving.

If the all-feature robustness audit passes, the Factor Regime conclusion can be upgraded to: **continuous factor risk-budgeting signal with broad selection-free evidence**. If it fails, Stage 5 remains an exploratory survivor-selection result and the next allocation work must use genuinely leader-specific raw stock information rather than retuning these aggregates.
