# Stage 2 — Bootstrap Epistemic Confidence

This stage is post-hoc exploratory. All model fitting, bootstrap resampling, and confidence calibration use Discovery 2016–19 only.

## Classification: **DIAGNOSTIC_ONLY**

- Diagnostic gate: True
- Economic passers: None

## Q5 epistemic confidence versus lower-confidence dates

- VAL_2020_2022: rank IC Q5 +0.167 vs Q1-4 +0.095; top3-EW8 +0.269% vs +0.118%; bottom2-veto-EW8 +0.285% vs +0.117%
- CONF_2023_2024: rank IC Q5 +0.071 vs Q1-4 -0.024; top3-EW8 +0.298% vs -0.036%; bottom2-veto-EW8 -0.183% vs -0.039%
- STRESS_2025: rank IC Q5 -0.179 vs Q1-4 +0.214; top3-EW8 -0.080% vs +0.239%; bottom2-veto-EW8 +0.029% vs +0.091%
- STRESS_2026: rank IC Q5 +0.536 vs Q1-4 +0.048; top3-EW8 +1.461% vs -0.085%; bottom2-veto-EW8 +1.148% vs +0.105%

## Activation

- VAL_2020_2022: high-confidence 8.1%; mean intensity 0.123; median EPI_CONF -0.313
- CONF_2023_2024: high-confidence 12.4%; mean intensity 0.148; median EPI_CONF -0.365
- STRESS_2025: high-confidence 14.3%; mean intensity 0.167; median EPI_CONF -0.425
- STRESS_2026: high-confidence 13.8%; mean intensity 0.140; median EPI_CONF -0.782

## Economic results at 10 bps

- **ENS_SOFT** — gate=False; VAL ΔSharpe +0.051 (6/6), CONF -0.056 (0/6), 2025 +0.096, 2026 +0.074
- **ENS_TOP3** — gate=False; VAL ΔSharpe -0.099 (1/6), CONF -0.468 (0/6), 2025 +0.454, 2026 -1.456
- **ENS_BOTTOM2_VETO** — gate=False; VAL ΔSharpe +0.330 (6/6), CONF -0.518 (0/6), 2025 +0.254, 2026 +0.069
- **EPI_CONF_SOFT** — gate=False; VAL ΔSharpe +0.022 (6/6), CONF -0.004 (2/6), 2025 -0.018, 2026 +0.341
- **EPI_CONF_HALF_TOP3** — gate=False; VAL ΔSharpe -0.004 (3/6), CONF +0.025 (4/6), 2025 -0.175, 2026 +0.195
- **EPI_CONT_HALF_TOP3** — gate=False; VAL ΔSharpe +0.007 (3/6), CONF -0.102 (0/6), 2025 +0.001, 2026 +0.249
- **EPI_CONF_BOTTOM2_VETO** — gate=False; VAL ΔSharpe +0.077 (6/6), CONF -0.240 (0/6), 2025 -0.076, 2026 +0.609

## Decision

Epistemic model stability contains some useful information. Because the experiment is post-hoc, any survivor remains a candidate for future untouched validation rather than a production rule.