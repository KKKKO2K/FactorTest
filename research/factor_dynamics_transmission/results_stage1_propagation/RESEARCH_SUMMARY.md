# Stage 1 — Common/Local Factor Shocks and Cross-Universe Propagation

This stage was pre-registered in `STAGE1_PROTOCOL.md` before results were viewed.
No regime labels or portfolio rules are used.

## Test A — Common versus local factor dynamics

- DISC_2016_2019: median common next-5D IC +0.085 (5/8 factors positive); median local next-5D IC -0.019 (28/48 local series negative); median common variance share 0.683
- VAL_2020_2022: median common next-5D IC -0.007 (4/8 factors positive); median local next-5D IC -0.004 (26/48 local series negative); median common variance share 0.697
- CONF_2023_2024: median common next-5D IC -0.069 (2/8 factors positive); median local next-5D IC -0.021 (26/48 local series negative); median common variance share 0.733
- STRESS_2025: median common next-5D IC -0.014 (4/8 factors positive); median local next-5D IC -0.047 (27/48 local series negative); median common variance share 0.686
- STRESS_2026: median common next-5D IC +0.094 (5/8 factors positive); median local next-5D IC -0.048 (33/48 local series negative); median common variance share 0.679

## Test B — Directed same-factor universe propagation

- PASS edges: 5/30
- Directional PASS edges: 3/30

### Passing edges
- KOSDAQ -> KOSPI_ALL: DIRECTIONAL; VAL median incremental OOS R2 +0.0007 (7/8 positive), CONF +0.0028 (8/8); reverse advantage VAL +0.0340, CONF +0.0213; local diffusion IC VAL +0.024, CONF -0.027
- KOSPI_KOSDAQ_ALL -> KOSPI_ALL: DIRECTIONAL; VAL median incremental OOS R2 +0.0004 (6/8 positive), CONF +0.0004 (5/8); reverse advantage VAL +0.0140, CONF +0.0017; local diffusion IC VAL -0.007, CONF +0.031
- KOSDAQ -> K200: DIRECTIONAL; VAL median incremental OOS R2 +0.0026 (6/8 positive), CONF +0.0003 (5/8); reverse advantage VAL +0.0095, CONF +0.0091; local diffusion IC VAL +0.025, CONF +0.037
- KOSPI_KOSDAQ_ALL -> K200: BIDIRECTIONAL/COMMON; VAL median incremental OOS R2 +0.0018 (5/8 positive), CONF +0.0028 (5/8); reverse advantage VAL +0.0059, CONF -0.0064; local diffusion IC VAL +0.050, CONF +0.021
- KOSDAQ_PLUS_KOSPI_EX_K200 -> K200: BIDIRECTIONAL/COMMON; VAL median incremental OOS R2 +0.0015 (5/8 positive), CONF +0.0023 (6/8); reverse advantage VAL +0.0092, CONF -0.0008; local diffusion IC VAL +0.021, CONF +0.020

## Strongest non-passing edges by confirmation incremental OOS R2

- KOSDAQ -> KOSPI_ALL: PASS=True; VAL +0.0007 (7/8), CONF +0.0028 (8/8), reverse advantage CONF +0.0213
- KOSPI_KOSDAQ_ALL -> KOSPI_ALL: PASS=True; VAL +0.0004 (6/8), CONF +0.0004 (5/8), reverse advantage CONF +0.0017
- KOSDAQ -> K200: PASS=True; VAL +0.0026 (6/8), CONF +0.0003 (5/8), reverse advantage CONF +0.0091
- KOSPI_KOSDAQ_ALL -> K200: PASS=True; VAL +0.0018 (5/8), CONF +0.0028 (5/8), reverse advantage CONF -0.0064
- KOSDAQ_PLUS_KOSPI_EX_K200 -> K200: PASS=True; VAL +0.0015 (5/8), CONF +0.0023 (6/8), reverse advantage CONF -0.0008
- K200 -> KOSPI_EX_K200: PASS=False; VAL -0.0130 (1/8), CONF +0.0102 (5/8), reverse advantage CONF +0.0074
- K200 -> KOSPI_ALL: PASS=False; VAL -0.0046 (1/8), CONF +0.0092 (6/8), reverse advantage CONF +0.0110
- K200 -> KOSPI_KOSDAQ_ALL: PASS=False; VAL -0.0041 (2/8), CONF +0.0092 (7/8), reverse advantage CONF +0.0064

## Decision rule

At least one genuinely directional same-factor universe edge survives. Stage 2 should first falsify those exact edges with alternative horizons / gap tests before moving to cross-factor transmission.