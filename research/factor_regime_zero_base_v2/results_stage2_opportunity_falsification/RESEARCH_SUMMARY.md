# Stage 2 — Opportunity Clustering Falsification

Primary hypothesis: current 20D cross-factor dispersion predicts future cross-factor dispersion.
All robustness tests were pre-registered before this run. No portfolio rule is tested.

## Classification: REJECT_OR_CONDITIONAL
- Historical robustness gate passed: False

## Primary 20D relation

- 2016_2019: median IC +0.164, positive universes 6/6
- 2020_2022: median IC +0.237, positive universes 6/6
- 2023_2024: median IC +0.121, positive universes 6/6
- 2025: median IC -0.066, positive universes 1/6
- 2026: median IC -0.167, positive universes 0/6

## Horizon robustness

- Forward 10D: 2020_2022 +0.240; 2023_2024 +0.198; 2025 +0.005; 2026 +0.053
- Forward 20D: 2020_2022 +0.237; 2023_2024 +0.121; 2025 -0.066; 2026 -0.167
- Forward 40D: 2020_2022 +0.273; 2023_2024 -0.071; 2025 -0.092; 2026 -0.136
- Forward 60D: 2020_2022 +0.299; 2023_2024 -0.024; 2025 -0.105; 2026 +0.132

## Falsification checks

- Gap-5D: 2020-22 +0.235, 2023-24 -0.085, 2025 -0.046, 2026 -0.380
- Vol-normalized: 2020-22 +0.124, 2023-24 +0.229, 2025 +0.062, 2026 -0.078
- Non-overlap-20D: 2020-22 +0.130, 2023-24 +0.003, 2025 +0.049, 2026 NA
- Leave-one-factor-out positive in both validation periods: 8/8 (MOM1M, MOM12_1, OP12_REV, OPFY1_REV, PBR12MF, PER12MF, PRIVATE_FLOW, FOREIGN_FLOW)

## Cross-universe aggregate

- 2016_2019: raw IC +0.196, normalized IC +0.154
- 2020_2022: raw IC +0.298, normalized IC +0.113
- 2023_2024: raw IC +0.203, normalized IC +0.243
- 2025: raw IC -0.205, normalized IC -0.050
- 2026: raw IC -0.069, normalized IC -0.051

## Interpretation rule

- A historical PASS with negative 2025/2026 is a recent structural break, not a production signal.
- Do not search for a trading threshold from this output.
- If historically robust, the next research question is what observable state explains persistence versus mean reversion in opportunity; if not robust, stop Factor Opportunity as a regime target.