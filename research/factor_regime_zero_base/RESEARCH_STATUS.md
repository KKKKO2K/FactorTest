# Zero-Base Factor Regime Research Status

## Current research order

1. **Factor Persistence / Rotation** — completed Stage 1 + economic Stage 1b.
2. **Factor Opportunity** — completed Stage 2 + combined Stage 2b policy.
3. **Factor Crash / Crowding** — completed factor-return-only Stage 3 + Stage 3b crash cap; factor-return-only crash research is frozen.
4. **Stock-Level Regime Extension** — completed Stage 4A aggregate stock/liquidity predictive screen + Stage 4B hard permission policy.
5. **Continuous Factor Risk Budgeting** — completed Stage 5 survivor-based continuous tilt and selection-bias audit.
6. **Leader-Specific Raw Stock Extension** — next research priority if we want to improve selection quality beyond the weak robust Persistence edge: leader-specific participation, turnover/ADV, contribution concentration and holdings overlap from raw point-in-time stock data.
7. **Market Transition** — secondary use only after the factor-allocation questions above are exhausted.

## Stage 5 — continuous factor risk budgeting

Portfolio mapping was frozen before the run:

`w_t = EW8 + lambda_t * (TOP2 - EW8)`

with `lambda` bounded to [-0.25,+0.25], prior-data percentile mapping only, and no threshold/max-tilt sweep.

### Exploratory survivor-based result
Using seven Stage-1 Persistence survivors and three Stage-4A Liquidity survivors, all three continuous variants passed the predeclared 10 bps gate:
- Persistence continuous: DEV 2020-22 median ΔSharpe vs EW8 +0.129; 2023-24 +0.159; 4/6 confirmation universes improve.
- Liquidity continuous: DEV +0.001; 2023-24 +0.190; 4/6 improve.
- Combined continuous: DEV +0.093; 2023-24 +0.158; 5/6 improve.
- Combined remains positive in 2025 (+0.074 median ΔSharpe) and YTD 2026 (+0.029).

However these predictor lists were selected using prior DEV/CONFIRM screens, so the survivor-based result is exploratory rather than clean validation.

## Selection-bias audit — stricter result

To remove predictor-list leakage:
- Persistence uses **all 18 predictors declared before Stage 1**.
- Liquidity uses **all 10 aggregate stock/liquidity features declared before Stage 4A**.
- No feature is removed using 2020-24 outcomes.
- Only feature direction, standardization and empirical percentile mapping use prior data each evaluation year.
- Portfolio mapping and max tilt are unchanged.

At 10 bps:

### PERSIST_ALL_CONT — technical PASS, economically weak confirmation
- DEV 2020-22 median ΔSharpe vs EW8: **+0.112**; 5/6 universes improve.
- 2023-24 median ΔSharpe: **+0.002**; 4/6 universes improve.
- 2025 median ΔSharpe: **+0.102**; 4/6 improve.
- YTD 2026 median ΔSharpe: **+0.222**; 5/6 improve.
- 30 bps 2023-24 median ΔSharpe turns negative (-0.044), so the robust edge is cost-sensitive.

The 2023-24 universe detail shows that the technical 4/6 PASS is not uniformly strong: KOSDAQ and KOSDAQ+KOSPI ex-K200 are clearly positive, K200 is slightly positive, KOSPI_ALL is essentially flat, while KOSPI_EX_K200 and KOSPI+KOSDAQ_ALL are negative. Therefore this should be called a **weak/conditional economic PASS**, not a production-ready signal.

### LIQ_ALL_CONT — FAIL
- DEV median ΔSharpe -0.016.
- 2023-24 +0.024 but only 3/6 universes improve.
- Aggregate liquidity/selectivity does not survive selection-free implementation as a standalone continuous allocation signal.

### COMBINED_ALL_CONT — FAIL
- DEV +0.076.
- 2023-24 +0.016 but only 3/6 universes improve.
- The survivor-based Combined result overstates the robustness of adding aggregate liquidity to Persistence.

## Current best interpretation of Factor Regime

The most defensible result is narrower than the exploratory Stage-5 result:

1. **Persistence is the only axis with selection-free economic evidence.**
   - Factor leadership persistence contains predictive information.
   - Expressing it as a small continuous tilt around EW8 is superior to hard TOP2/BOTTOM2 regime switching.
   - The edge is modest and cost-sensitive in 2023-24, so it is not yet production-grade.

2. **Opportunity is forecastable but not independently monetized.**
   - Current factor dispersion/range predicts future factor opportunity.
   - Hard opportunity gating failed economically.
   - Keep Opportunity as context / active-risk magnitude information rather than a standalone switch.

3. **Aggregate Liquidity/Selectivity is predictive in screens but not robust as an allocation block.**
   - Stage 4A ICs were real enough to motivate further work, but the all-feature continuous implementation fails the strict gate.
   - Do not use the current aggregate liquidity block in a production combined score.

4. **Factor-return-only crash/crowding is exhausted.**
   - No further threshold tuning on factor-return transforms.

## Research conclusion so far

Factor Regime should not be represented as a discrete F_HIGH/F_LOW label. The evidence supports a **continuous factor risk-budgeting framework**, but only the Persistence component currently has selection-free economic support, and that support is weak in the 2023-24 confirmation period.

The current production posture should therefore be:

- **EW8 remains the core.**
- **Persistence continuous tilt = research candidate / conditional overlay, not production default.**
- **Opportunity = monitoring/context variable.**
- **Aggregate Liquidity = research-only until leader-specific stock information is tested.**

## Next predeclared research step

If continuing Factor Regime research, do not retune the ±25% tilt amplitude or survivor lists. Add genuinely new leader-specific stock-level information:

- positive-return breadth within current factor leaders;
- leader contribution concentration;
- current leader turnover / ADV rank and acceleration;
- holding retention and turnover;
- cross-factor holding overlap / multiplicity;
- leader liquidity support relative to the same-universe market baseline.

Primary target remains **future current-TOP2 alpha vs EW8**, with future reversal and factor opportunity as secondary targets. Use annual expanding walk-forward, 6 universes, prior-only transformations, and keep 2025/2026 as stress evidence rather than tuning samples.
