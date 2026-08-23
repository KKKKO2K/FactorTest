# Zero-Base Factor Persistence / Rotation — Stage 1

This screen uses the canonical factor long-short payoff panel directly. No B/F regime labels, KMeans states, previously selected regime thresholds, or future-derived labels are predictors.

- Panel: 2016-04-01 to 2026-05-07, 2,951 state observations, 6 universes.
- Factors: MOM1M, MOM12_1, OP12_REV, OPFY1_REV, PBR12MF, PER12MF, PRIVATE_FLOW, FOREIGN_FLOW.
- Annual expanding walk-forward starts in 2020. Predictor direction and tercile thresholds are fitted only on observations before each evaluation year.
- 2025/2026 are stress slices, not pristine untouched OOS.

## Predeclared PASS gate

A feature-target relation passes only if train-learned direction has positive median OOS Spearman in 2020-22 and again in 2023-24, 2023-24 universe-median directed Spearman is positive in at least 4/6 universes, and the 2023-24 train-threshold high-vs-low target spread has the same directed sign.

## Result: 29 PASS relations out of 90 screened

- TARGET_TOP2_SAME_20 <- CROSS_HORIZON_RANK_CORR: DEV IC +0.064, CONFIRM IC +0.179, CONFIRM H-L +0.080, positive universes 5/6, 2025 IC -0.001, 2026 IC -0.254
- TARGET_FACTOR_MOM_20 <- CROSS_HORIZON_RANK_CORR: DEV IC +0.027, CONFIRM IC +0.179, CONFIRM H-L +0.006, positive universes 5/6, 2025 IC -0.187, 2026 IC +0.012
- TARGET_TOP2_SURVIVAL_20 <- DISPERSION_60: DEV IC +0.174, CONFIRM IC +0.175, CONFIRM H-L +0.125, positive universes 5/6, 2025 IC -0.127, 2026 IC -0.138
- TARGET_TOP2_SURVIVAL_20 <- ABS_OPPORTUNITY_20: DEV IC +0.110, CONFIRM IC +0.162, CONFIRM H-L +0.026, positive universes 6/6, 2025 IC -0.070, 2026 IC +0.142
- TARGET_TOP2_SURVIVAL_20 <- LOSER_WEAKNESS_20: DEV IC +0.056, CONFIRM IC +0.131, CONFIRM H-L +0.087, positive universes 5/6, 2025 IC -0.014, 2026 IC +0.040
- TARGET_TOP2_SAME_20 <- DISPERSION_60: DEV IC +0.103, CONFIRM IC +0.130, CONFIRM H-L +0.063, positive universes 6/6, 2025 IC -0.021, 2026 IC -0.042
- TARGET_RANK_CORR_20 <- SIGN_ALIGNMENT_20_60: DEV IC +0.143, CONFIRM IC +0.128, CONFIRM H-L +0.128, positive universes 5/6, 2025 IC -0.083, 2026 IC +0.052
- TARGET_RANK_CORR_20 <- DISPERSION_60: DEV IC +0.104, CONFIRM IC +0.120, CONFIRM H-L +0.132, positive universes 5/6, 2025 IC -0.013, 2026 IC +0.020
- TARGET_TOP2_SURVIVAL_20 <- DISPERSION_20: DEV IC +0.059, CONFIRM IC +0.113, CONFIRM H-L +0.066, positive universes 5/6, 2025 IC -0.023, 2026 IC +0.134
- TARGET_TOP2_SURVIVAL_20 <- LEADER_STRENGTH_20: DEV IC +0.039, CONFIRM IC +0.106, CONFIRM H-L +0.045, positive universes 5/6, 2025 IC -0.044, 2026 IC +0.138
- TARGET_TOP2_SURVIVAL_20 <- DISPERSION_CHANGE_20: DEV IC +0.097, CONFIRM IC +0.106, CONFIRM H-L +0.048, positive universes 5/6, 2025 IC +0.048, 2026 IC -0.031
- TARGET_FACTOR_MOM_20 <- PC1_SHARE_60: DEV IC +0.023, CONFIRM IC +0.097, CONFIRM H-L +0.010, positive universes 4/6, 2025 IC +0.074, 2026 IC -0.023
- TARGET_TOP2_SURVIVAL_20 <- RANGE_20: DEV IC +0.086, CONFIRM IC +0.097, CONFIRM H-L +0.062, positive universes 5/6, 2025 IC -0.020, 2026 IC +0.189
- TARGET_RANK_CORR_20 <- LEADER_STRENGTH_20: DEV IC +0.083, CONFIRM IC +0.092, CONFIRM H-L +0.105, positive universes 5/6, 2025 IC -0.107, 2026 IC +0.102
- TARGET_TOP2_SURVIVAL_20 <- BREADTH_CHANGE_20: DEV IC +0.002, CONFIRM IC +0.081, CONFIRM H-L +0.045, positive universes 4/6, 2025 IC -0.165, 2026 IC -0.163
- TARGET_RANK_CORR_60 <- DISPERSION_CHANGE_20: DEV IC +0.004, CONFIRM IC +0.079, CONFIRM H-L +0.078, positive universes 5/6, 2025 IC +0.005, 2026 IC +0.156
- TARGET_TOP2_SURVIVAL_20 <- SIGN_ALIGNMENT_20_60: DEV IC +0.022, CONFIRM IC +0.079, CONFIRM H-L +0.038, positive universes 4/6, 2025 IC +0.068, 2026 IC +0.164
- TARGET_RANK_CORR_20 <- RANGE_20: DEV IC +0.105, CONFIRM IC +0.061, CONFIRM H-L +0.011, positive universes 5/6, 2025 IC -0.070, 2026 IC +0.124
- TARGET_RANK_CORR_20 <- ABS_OPPORTUNITY_20: DEV IC +0.098, CONFIRM IC +0.059, CONFIRM H-L +0.007, positive universes 5/6, 2025 IC -0.084, 2026 IC +0.218
- TARGET_RANK_CORR_20 <- LOSER_WEAKNESS_20: DEV IC +0.071, CONFIRM IC +0.059, CONFIRM H-L +0.079, positive universes 5/6, 2025 IC -0.052, 2026 IC +0.027

## Best relations by target

### TARGET_RANK_CORR_20
- CROSS_HORIZON_RANK_CORR: PASS=False; DEV -0.031, CONFIRM +0.205, CONFIRM H-L +0.199, universes 6/6, 2025 -0.211, 2026 -0.227
- SIGN_ALIGNMENT_20_60: PASS=True; DEV +0.143, CONFIRM +0.128, CONFIRM H-L +0.128, universes 5/6, 2025 -0.083, 2026 +0.052
- DISPERSION_60: PASS=True; DEV +0.104, CONFIRM +0.120, CONFIRM H-L +0.132, universes 5/6, 2025 -0.013, 2026 +0.020
- LEADER_STRENGTH_20: PASS=True; DEV +0.083, CONFIRM +0.092, CONFIRM H-L +0.105, universes 5/6, 2025 -0.107, 2026 +0.102
- BREADTH_20: PASS=False; DEV -0.009, CONFIRM +0.086, CONFIRM H-L +0.058, universes 3/6, 2025 -0.218, 2026 +0.294

### TARGET_RANK_CORR_60
- PC1_SHARE_60: PASS=False; DEV -0.112, CONFIRM +0.128, CONFIRM H-L -0.052, universes 4/6, 2025 +0.143, 2026 +0.292
- DISPERSION_CHANGE_20: PASS=True; DEV +0.004, CONFIRM +0.079, CONFIRM H-L +0.078, universes 5/6, 2025 +0.005, 2026 +0.156
- BREADTH_20: PASS=False; DEV -0.058, CONFIRM +0.026, CONFIRM H-L +0.006, universes 2/6, 2025 -0.105, 2026 +0.180
- DISPERSION_60: PASS=False; DEV -0.129, CONFIRM +0.019, CONFIRM H-L +0.066, universes 4/6, 2025 +0.258, 2026 +0.331
- LEADER_STRENGTH_20: PASS=False; DEV -0.028, CONFIRM +0.008, CONFIRM H-L -0.023, universes 1/6, 2025 -0.007, 2026 +0.023

### TARGET_TOP2_SURVIVAL_20
- DISPERSION_60: PASS=True; DEV +0.174, CONFIRM +0.175, CONFIRM H-L +0.125, universes 5/6, 2025 -0.127, 2026 -0.138
- ABS_OPPORTUNITY_20: PASS=True; DEV +0.110, CONFIRM +0.162, CONFIRM H-L +0.026, universes 6/6, 2025 -0.070, 2026 +0.142
- LOSER_WEAKNESS_20: PASS=True; DEV +0.056, CONFIRM +0.131, CONFIRM H-L +0.087, universes 5/6, 2025 -0.014, 2026 +0.040
- DISPERSION_20: PASS=True; DEV +0.059, CONFIRM +0.113, CONFIRM H-L +0.066, universes 5/6, 2025 -0.023, 2026 +0.134
- LEADER_STRENGTH_20: PASS=True; DEV +0.039, CONFIRM +0.106, CONFIRM H-L +0.045, universes 5/6, 2025 -0.044, 2026 +0.138

### TARGET_TOP2_SAME_20
- CROSS_HORIZON_RANK_CORR: PASS=True; DEV +0.064, CONFIRM +0.179, CONFIRM H-L +0.080, universes 5/6, 2025 -0.001, 2026 -0.254
- DISPERSION_60: PASS=True; DEV +0.103, CONFIRM +0.130, CONFIRM H-L +0.063, universes 6/6, 2025 -0.021, 2026 -0.042
- BREADTH_60: PASS=False; DEV -0.047, CONFIRM +0.070, CONFIRM H-L +0.013, universes 4/6, 2025 +0.041, 2026 -0.006
- SIGN_ALIGNMENT_20_60: PASS=False; DEV -0.011, CONFIRM +0.062, CONFIRM H-L +0.024, universes 4/6, 2025 -0.009, 2026 -0.077
- BREADTH_20: PASS=False; DEV +0.027, CONFIRM +0.055, CONFIRM H-L +0.013, universes 3/6, 2025 -0.079, 2026 -0.061

### TARGET_FACTOR_MOM_20
- CROSS_HORIZON_RANK_CORR: PASS=True; DEV +0.027, CONFIRM +0.179, CONFIRM H-L +0.006, universes 5/6, 2025 -0.187, 2026 +0.012
- PC1_SHARE_60: PASS=True; DEV +0.023, CONFIRM +0.097, CONFIRM H-L +0.010, universes 4/6, 2025 +0.074, 2026 -0.023
- LEADER_STRENGTH_20: PASS=True; DEV +0.036, CONFIRM +0.058, CONFIRM H-L +0.013, universes 5/6, 2025 -0.104, 2026 +0.145
- ABS_OPPORTUNITY_20: PASS=False; DEV -0.007, CONFIRM +0.054, CONFIRM H-L -0.006, universes 5/6, 2025 -0.022, 2026 +0.243
- SIGN_ALIGNMENT_20_60: PASS=True; DEV +0.037, CONFIRM +0.052, CONFIRM H-L +0.004, universes 5/6, 2025 +0.014, 2026 +0.051

## Unconditional target context

- DEV_2020_2022: rank-persistence20 median across universes +0.083; top2-same mean 28.5%; factor-momentum20 mean +0.68%
- CONFIRM_2023_2024: rank-persistence20 median across universes +0.012; top2-same mean 26.4%; factor-momentum20 mean +0.05%
- BULL_2025: rank-persistence20 median across universes +0.095; top2-same mean 22.3%; factor-momentum20 mean +0.68%
- YTD_2026: rank-persistence20 median across universes -0.012; top2-same mean 17.6%; factor-momentum20 mean -0.54%

## Next step rule

- If robust PASS relations exist, Stage 1b should combine only those predeclared survivors in a simple expanding ridge/logistic model and test a non-overlapping 20D factor-momentum-vs-rotation policy.
- If Stage 1 has no robust relation, move to Factor Opportunity rather than tuning thresholds on 2025/2026.