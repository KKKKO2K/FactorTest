# Zero-Base Factor Opportunity — Stage 2

Question: can information observable at t predict how much cross-factor opportunity will exist over the next 20D?

- Targets are forward cross-factor dispersion, mean absolute factor payoff, and best-minus-worst range across the same eight canonical factor sleeves.
- Predictors are the same 18 predeclared contemporaneous structural features used in Stage 1.
- Direction and thresholds are re-estimated only from data before each evaluation year.
- PASS gate matches Stage 1: positive directed median IC in 2020-22 and 2023-24, positive 2023-24 directed H-L, and positive universe-median IC in at least 4/6 universes.

## Result: 19 PASS relations out of 54 screened

- TARGET_FWD_ABS_OPPORTUNITY_20 <- WINNER_GAP_20: DEV IC +0.011, CONFIRM IC +0.149, CONFIRM H-L +0.10%, universes 5/6, 2025 IC +0.049, 2026 IC -0.162
- TARGET_FWD_RANGE_20 <- DISPERSION_20: DEV IC +0.108, CONFIRM IC +0.115, CONFIRM H-L +1.14%, universes 6/6, 2025 IC -0.036, 2026 IC -0.163
- TARGET_FWD_RANGE_20 <- RANGE_20: DEV IC +0.112, CONFIRM IC +0.110, CONFIRM H-L +1.03%, universes 6/6, 2025 IC -0.038, 2026 IC -0.159
- TARGET_FWD_DISPERSION_20 <- LEADER_STRENGTH_20: DEV IC +0.131, CONFIRM IC +0.105, CONFIRM H-L +0.11%, universes 6/6, 2025 IC +0.036, 2026 IC -0.277
- TARGET_FWD_DISPERSION_20 <- ABS_OPPORTUNITY_20: DEV IC +0.031, CONFIRM IC +0.103, CONFIRM H-L +0.20%, universes 6/6, 2025 IC -0.179, 2026 IC -0.120
- TARGET_FWD_ABS_OPPORTUNITY_20 <- LEADER_STRENGTH_20: DEV IC +0.109, CONFIRM IC +0.099, CONFIRM H-L +0.09%, universes 6/6, 2025 IC +0.146, 2026 IC -0.332
- TARGET_FWD_DISPERSION_20 <- RANGE_20: DEV IC +0.087, CONFIRM IC +0.098, CONFIRM H-L +0.29%, universes 6/6, 2025 IC -0.066, 2026 IC -0.146
- TARGET_FWD_RANGE_20 <- LEADER_STRENGTH_20: DEV IC +0.094, CONFIRM IC +0.090, CONFIRM H-L +0.29%, universes 6/6, 2025 IC +0.038, 2026 IC -0.252
- TARGET_FWD_DISPERSION_20 <- DISPERSION_20: DEV IC +0.080, CONFIRM IC +0.089, CONFIRM H-L +0.27%, universes 6/6, 2025 IC -0.066, 2026 IC -0.167
- TARGET_FWD_ABS_OPPORTUNITY_20 <- DISPERSION_20: DEV IC +0.094, CONFIRM IC +0.089, CONFIRM H-L +0.16%, universes 5/6, 2025 IC +0.005, 2026 IC -0.130
- TARGET_FWD_DISPERSION_20 <- WINNER_GAP_20: DEV IC +0.093, CONFIRM IC +0.087, CONFIRM H-L +0.28%, universes 5/6, 2025 IC -0.021, 2026 IC -0.105
- TARGET_FWD_ABS_OPPORTUNITY_20 <- RANGE_20: DEV IC +0.076, CONFIRM IC +0.079, CONFIRM H-L +0.23%, universes 5/6, 2025 IC -0.013, 2026 IC -0.107
- TARGET_FWD_RANGE_20 <- ABS_OPPORTUNITY_20: DEV IC +0.043, CONFIRM IC +0.078, CONFIRM H-L +0.76%, universes 6/6, 2025 IC -0.133, 2026 IC -0.140
- TARGET_FWD_RANGE_20 <- BREADTH_CHANGE_20: DEV IC +0.151, CONFIRM IC +0.062, CONFIRM H-L +0.70%, universes 4/6, 2025 IC +0.073, 2026 IC -0.198
- TARGET_FWD_RANGE_20 <- WINNER_GAP_20: DEV IC +0.086, CONFIRM IC +0.058, CONFIRM H-L +0.96%, universes 5/6, 2025 IC -0.005, 2026 IC -0.102
- TARGET_FWD_RANGE_20 <- BREADTH_60: DEV IC +0.080, CONFIRM IC +0.058, CONFIRM H-L +0.37%, universes 4/6, 2025 IC +0.273, 2026 IC +0.037
- TARGET_FWD_ABS_OPPORTUNITY_20 <- BREADTH_20: DEV IC +0.054, CONFIRM IC +0.055, CONFIRM H-L +0.34%, universes 6/6, 2025 IC +0.006, 2026 IC +0.288
- TARGET_FWD_ABS_OPPORTUNITY_20 <- ABS_OPPORTUNITY_20: DEV IC +0.097, CONFIRM IC +0.042, CONFIRM H-L +0.05%, universes 4/6, 2025 IC -0.038, 2026 IC -0.140
- TARGET_FWD_DISPERSION_20 <- BREADTH_60: DEV IC +0.106, CONFIRM IC +0.016, CONFIRM H-L +0.16%, universes 4/6, 2025 IC +0.295, 2026 IC +0.071

## Best relations by target

### TARGET_FWD_DISPERSION_20
- LEADER_STRENGTH_20: PASS=True; DEV +0.131, CONFIRM +0.105, H-L +0.11%, universes 6/6, 2025 +0.036, 2026 -0.277
- ABS_OPPORTUNITY_20: PASS=True; DEV +0.031, CONFIRM +0.103, H-L +0.20%, universes 6/6, 2025 -0.179, 2026 -0.120
- RANGE_20: PASS=True; DEV +0.087, CONFIRM +0.098, H-L +0.29%, universes 6/6, 2025 -0.066, 2026 -0.146
- DISPERSION_20: PASS=True; DEV +0.080, CONFIRM +0.089, H-L +0.27%, universes 6/6, 2025 -0.066, 2026 -0.167
- WINNER_GAP_20: PASS=True; DEV +0.093, CONFIRM +0.087, H-L +0.28%, universes 5/6, 2025 -0.021, 2026 -0.105
- DISPERSION_CHANGE_20: PASS=False; DEV -0.060, CONFIRM +0.065, H-L +0.81%, universes 3/6, 2025 +0.148, 2026 -0.012

### TARGET_FWD_ABS_OPPORTUNITY_20
- WINNER_GAP_20: PASS=True; DEV +0.011, CONFIRM +0.149, H-L +0.10%, universes 5/6, 2025 +0.049, 2026 -0.162
- DISPERSION_CHANGE_20: PASS=False; DEV -0.010, CONFIRM +0.144, H-L +0.70%, universes 5/6, 2025 +0.211, 2026 -0.069
- LEADER_STRENGTH_20: PASS=True; DEV +0.109, CONFIRM +0.099, H-L +0.09%, universes 6/6, 2025 +0.146, 2026 -0.332
- DISPERSION_20: PASS=True; DEV +0.094, CONFIRM +0.089, H-L +0.16%, universes 5/6, 2025 +0.005, 2026 -0.130
- RANGE_20: PASS=True; DEV +0.076, CONFIRM +0.079, H-L +0.23%, universes 5/6, 2025 -0.013, 2026 -0.107
- BREADTH_20: PASS=True; DEV +0.054, CONFIRM +0.055, H-L +0.34%, universes 6/6, 2025 +0.006, 2026 +0.288

### TARGET_FWD_RANGE_20
- DISPERSION_CHANGE_20: PASS=False; DEV -0.075, CONFIRM +0.171, H-L +3.22%, universes 4/6, 2025 +0.134, 2026 -0.056
- DISPERSION_20: PASS=True; DEV +0.108, CONFIRM +0.115, H-L +1.14%, universes 6/6, 2025 -0.036, 2026 -0.163
- RANGE_20: PASS=True; DEV +0.112, CONFIRM +0.110, H-L +1.03%, universes 6/6, 2025 -0.038, 2026 -0.159
- LEADER_STRENGTH_20: PASS=True; DEV +0.094, CONFIRM +0.090, H-L +0.29%, universes 6/6, 2025 +0.038, 2026 -0.252
- ABS_OPPORTUNITY_20: PASS=True; DEV +0.043, CONFIRM +0.078, H-L +0.76%, universes 6/6, 2025 -0.133, 2026 -0.140
- BREADTH_CHANGE_20: PASS=True; DEV +0.151, CONFIRM +0.062, H-L +0.70%, universes 4/6, 2025 +0.073, 2026 -0.198

## Next-step rule

- If opportunity is forecastable, freeze the robust opportunity predictors and use them only as an active-risk gate around the persistence/rotation signal.
- High opportunity + persistence -> top-factor tilt; high opportunity + rotation -> contrarian-factor tilt; low opportunity -> EW8.
- Do not optimize opportunity thresholds on 2025/2026.