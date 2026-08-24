# Stock-Level Liquidity State Screen — Zero Base Stage 4A

- Inputs are point-in-time stock/liquidity aggregates already produced by Factor Regime v1: market ACT5/ACT1 breadth, KOSDAQ trading-amount share, and mean ACT5 support among factor-top stocks. No old regime labels or thresholds are used.
- Added features are factor-top minus market ACT5 support and four-state changes in each liquidity/participation measure.
- Primary economic target is future current-top2-factor alpha vs EW8. Factor momentum, future factor range and top2 relative loss are secondary diagnostics.
- Annual expanding walk-forward; feature direction and tercile thresholds use only prior data. PASS gate matches prior zero-base screens.

## Coverage: 2016-04-01 to 2026-05-07

## Result: 16 PASS relations out of 40 screened

- TARGET_TOP2_ALPHA_VS_EW8_20 <- MKT_ACT1_BREADTH (LOW_TARGET): DEV +0.070, CONFIRM +0.241, H-L +2.04%, universes 6/6, 2025 -0.035, 2026 -0.063
- TARGET_TOP2_RELATIVE_LOSS_20 <- MKT_ACT1_BREADTH (HIGH_TARGET): DEV +0.070, CONFIRM +0.241, H-L +2.04%, universes 6/6, 2025 -0.035, 2026 -0.063
- TARGET_FWD_RANGE_20 <- KOSDAQ_TA_SHARE (HIGH_TARGET): DEV +0.135, CONFIRM +0.191, H-L +2.75%, universes 6/6, 2025 +0.038, 2026 +0.082
- TARGET_FWD_RANGE_20 <- MKT_ACT5_BREADTH (HIGH_TARGET): DEV +0.073, CONFIRM +0.164, H-L +1.24%, universes 6/6, 2025 +0.091, 2026 -0.110
- TARGET_TOP2_ALPHA_VS_EW8_20 <- MKT_ACT1_CHANGE_4 (LOW_TARGET): DEV +0.047, CONFIRM +0.130, H-L +1.13%, universes 5/6, 2025 -0.033, 2026 -0.240
- TARGET_TOP2_RELATIVE_LOSS_20 <- MKT_ACT1_CHANGE_4 (HIGH_TARGET): DEV +0.047, CONFIRM +0.130, H-L +1.13%, universes 5/6, 2025 -0.033, 2026 -0.240
- TARGET_TOP2_ALPHA_VS_EW8_20 <- MKT_ACT5_BREADTH (LOW_TARGET): DEV +0.018, CONFIRM +0.122, H-L +1.04%, universes 4/6, 2025 +0.008, 2026 -0.003
- TARGET_TOP2_RELATIVE_LOSS_20 <- MKT_ACT5_BREADTH (HIGH_TARGET): DEV +0.018, CONFIRM +0.122, H-L +1.04%, universes 4/6, 2025 +0.008, 2026 -0.003
- TARGET_FACTOR_MOM_20 <- MKT_ACT1_BREADTH (LOW_TARGET): DEV +0.047, CONFIRM +0.097, H-L +2.11%, universes 5/6, 2025 +0.076, 2026 +0.119
- TARGET_FACTOR_MOM_20 <- MKT_ACT1_CHANGE_4 (LOW_TARGET): DEV +0.001, CONFIRM +0.090, H-L +0.68%, universes 6/6, 2025 -0.041, 2026 -0.206
- TARGET_FWD_RANGE_20 <- FACTOR_TOP_ACT5_BREADTH_MEAN (HIGH_TARGET): DEV +0.060, CONFIRM +0.080, H-L +0.74%, universes 5/6, 2025 -0.107, 2026 -0.156
- TARGET_TOP2_ALPHA_VS_EW8_20 <- MKT_ACT5_CHANGE_4 (LOW_TARGET): DEV +0.001, CONFIRM +0.065, H-L +1.03%, universes 5/6, 2025 -0.069, 2026 -0.110
- TARGET_TOP2_RELATIVE_LOSS_20 <- MKT_ACT5_CHANGE_4 (HIGH_TARGET): DEV +0.001, CONFIRM +0.065, H-L +1.03%, universes 5/6, 2025 -0.069, 2026 -0.110
- TARGET_FACTOR_MOM_20 <- FACTOR_TOP_ACT5_BREADTH_MEAN (LOW_TARGET): DEV +0.069, CONFIRM +0.056, H-L +0.74%, universes 5/6, 2025 +0.086, 2026 +0.180
- TARGET_TOP2_ALPHA_VS_EW8_20 <- FACTOR_TOP_ACT5_BREADTH_MEAN (LOW_TARGET): DEV +0.072, CONFIRM +0.044, H-L +0.78%, universes 5/6, 2025 +0.050, 2026 +0.036
- TARGET_TOP2_RELATIVE_LOSS_20 <- FACTOR_TOP_ACT5_BREADTH_MEAN (HIGH_TARGET): DEV +0.072, CONFIRM +0.044, H-L +0.78%, universes 5/6, 2025 +0.050, 2026 +0.036

## Best relations for TOP2 alpha vs EW8

- MKT_ACT1_BREADTH (LOW_GOOD): PASS=True; DEV +0.070, CONFIRM +0.241, H-L +2.04%, universes 6/6, 2025 -0.035, 2026 -0.063
- MKT_ACT1_CHANGE_4 (LOW_GOOD): PASS=True; DEV +0.047, CONFIRM +0.130, H-L +1.13%, universes 5/6, 2025 -0.033, 2026 -0.240
- MKT_ACT5_BREADTH (LOW_GOOD): PASS=True; DEV +0.018, CONFIRM +0.122, H-L +1.04%, universes 4/6, 2025 +0.008, 2026 -0.003
- MKT_ACT5_CHANGE_4 (LOW_GOOD): PASS=True; DEV +0.001, CONFIRM +0.065, H-L +1.03%, universes 5/6, 2025 -0.069, 2026 -0.110
- FACTOR_TOP_ACT5_CHANGE_4 (LOW_GOOD): PASS=False; DEV -0.029, CONFIRM +0.049, H-L +1.05%, universes 4/6, 2025 -0.031, 2026 -0.107
- FACTOR_TOP_ACT5_BREADTH_MEAN (LOW_GOOD): PASS=True; DEV +0.072, CONFIRM +0.044, H-L +0.78%, universes 5/6, 2025 +0.050, 2026 +0.036
- FACTOR_TOP_MINUS_MKT_ACT5_CHANGE_4 (HIGH_GOOD): PASS=False; DEV -0.003, CONFIRM +0.037, H-L +0.06%, universes 4/6, 2025 -0.045, 2026 -0.059
- FACTOR_TOP_MINUS_MKT_ACT5 (HIGH_GOOD): PASS=False; DEV -0.071, CONFIRM -0.044, H-L -0.49%, universes 1/6, 2025 -0.022, 2026 -0.054
- KOSDAQ_TA_SHARE (LOW_GOOD): PASS=False; DEV -0.119, CONFIRM -0.091, H-L -0.11%, universes 2/6, 2025 -0.019, 2026 -0.094
- KOSDAQ_TA_SHARE_CHANGE_4 (LOW_GOOD): PASS=False; DEV -0.029, CONFIRM -0.125, H-L -1.13%, universes 3/6, 2025 -0.082, 2026 -0.075

## Next step

- If liquidity-state predictors add stable TOP2-vs-EW8 information, combine only those survivors with the persistence score as an active-risk permission signal.
- If these aggregate liquidity states fail, reconstruct leader-specific stock participation/turnover/overlap from raw point-in-time factor holdings; do not tune the existing factor-return thresholds.