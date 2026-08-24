# Stage 5 — Recurrent Factor Configurations / Analog Forecasting

- Discovery analog library: 2016-2019 only
- Fixed neighbors: k=10

## SNAPSHOT: NO_RECURRENCE
- Primary gate: False; placebo gate: False
- VAL_2020_2022: rank IC analog +0.024 vs unconditional -0.095 vs persistence +0.024; MSE 0.745 vs 0.703/1.458; top2 28.4%; neighbor sim 0.783; placebo p=0.398
- CONF_2023_2024: rank IC analog -0.071 vs unconditional -0.286 vs persistence -0.095; MSE 0.713 vs 0.682/1.441; top2 25.5%; neighbor sim 0.785; placebo p=0.853
- STRESS_2025: rank IC analog +0.060 vs unconditional -0.250 vs persistence +0.060; MSE 0.760 vs 0.724/1.364; top2 27.1%; neighbor sim 0.798; placebo p=0.319
- STRESS_2026: rank IC analog +0.274 vs unconditional -0.131 vs persistence +0.131; MSE 1.758 vs 1.772/3.189; top2 37.5%; neighbor sim 0.805; placebo p=0.042

## PATH20: NO_RECURRENCE
- Primary gate: False; placebo gate: False
- VAL_2020_2022: rank IC analog -0.060 vs unconditional -0.095 vs persistence +0.024; MSE 0.763 vs 0.703/1.458; top2 26.0%; neighbor sim 0.434; placebo p=0.838
- CONF_2023_2024: rank IC analog +0.024 vs unconditional -0.286 vs persistence -0.095; MSE 0.723 vs 0.682/1.441; top2 22.4%; neighbor sim 0.442; placebo p=0.424
- STRESS_2025: rank IC analog -0.071 vs unconditional -0.250 vs persistence +0.060; MSE 0.768 vs 0.724/1.364; top2 24.0%; neighbor sim 0.460; placebo p=0.770
- STRESS_2026: rank IC analog +0.155 vs unconditional -0.131 vs persistence +0.131; MSE 1.818 vs 1.772/3.189; top2 35.7%; neighbor sim 0.481; placebo p=0.120

## Decision

Neither snapshot nor 20D-path analog forecasting beats simple baselines robustly. The tested return-only panel has strong contemporaneous geometry but little stable temporal predictability even under a local nonlinear recurrence method.