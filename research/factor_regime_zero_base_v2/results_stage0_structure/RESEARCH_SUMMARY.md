# Stage 0 — Factor Payoff Empirical Structure Map

This stage intentionally contains no predictor selection, no clustering, no regime labels and no trading-rule test.
The purpose is to establish which factor-payoff phenomena exist before deciding what to forecast.

## Data

- Factors: MOM1M, MOM12_1, OP12_REV, OPFY1_REV, PBR12MF, PER12MF, PRIVATE_FLOW, FOREIGN_FLOW
- Universes: 6
- Factor return observations: 24907

## Unconditional phenomenon map

- 2016_2019: rank persistence median +0.071; top2 exact survival 25.1%; top2-in-top4 survival 52.2%; top2 alpha vs EW8 +0.11%; winner-minus-loser +0.27%; dispersion persistence +0.167; absolute-opportunity persistence +0.063
- 2020_2022: rank persistence median +0.083; top2 exact survival 28.8%; top2-in-top4 survival 52.1%; top2 alpha vs EW8 +0.11%; winner-minus-loser +0.68%; dispersion persistence +0.237; absolute-opportunity persistence +0.097
- 2023_2024: rank persistence median +0.012; top2 exact survival 26.3%; top2-in-top4 survival 48.5%; top2 alpha vs EW8 -0.03%; winner-minus-loser -0.16%; dispersion persistence +0.121; absolute-opportunity persistence +0.053
- 2025: rank persistence median +0.095; top2 exact survival 23.0%; top2-in-top4 survival 50.0%; top2 alpha vs EW8 -0.14%; winner-minus-loser +0.54%; dispersion persistence -0.066; absolute-opportunity persistence -0.038
- 2026: rank persistence median +0.095; top2 exact survival 22.0%; top2-in-top4 survival 55.0%; top2 alpha vs EW8 +0.52%; winner-minus-loser +2.11%; dispersion persistence -0.233; absolute-opportunity persistence -0.147
- FULL: rank persistence median +0.077; top2 exact survival 26.1%; top2-in-top4 survival 51.8%; top2 alpha vs EW8 +0.11%; winner-minus-loser +0.51%; dispersion persistence +0.221; absolute-opportunity persistence +0.142

## Cross-universe agreement

- 2016_2019: median 20D factor-rank agreement across universe pairs +0.690; positive pair-date share 92.0%
- 2020_2022: median 20D factor-rank agreement across universe pairs +0.690; positive pair-date share 91.1%
- 2023_2024: median 20D factor-rank agreement across universe pairs +0.690; positive pair-date share 85.4%
- 2025: median 20D factor-rank agreement across universe pairs +0.714; positive pair-date share 89.7%
- 2026: median 20D factor-rank agreement across universe pairs +0.738; positive pair-date share 89.3%
- FULL: median 20D factor-rank agreement across universe pairs +0.690; positive pair-date share 90.1%

## Stage-0 interpretation rule

No PASS/FAIL is assigned here. Stage 1 may only target phenomena that are visibly present across multiple eras and universes.
A phenomenon that appears only in 2025/2026 or only in one universe is not eligible for Stage 1 predictor research.
The next action after reading these diagnostics is to pre-register at most 2–3 target phenomena before constructing any forecasting features.