# Stock-Liquidity Active Permission Policy — Stage 4B

- Liquidity permission score is frozen to MKT_ACT1_BREADTH, its 4-state change, and FACTOR_TOP_ACT5_BREADTH_MEAN because each passed both Stage-4A TOP2-vs-EW8 alpha and factor-momentum targets in DEV/CONFIRM.
- Directions and the top-tercile permission threshold are estimated only from prior data each year.
- LIQ_TOP2_GATE: TOP2 only when permission is high, otherwise EW8.
- PERSIST_LIQ_GATE: persistence TOP2/BOTTOM2/EW8 action is allowed only when permission is high, otherwise EW8.
- Decisions are non-overlapping 20D and costs apply to one-way factor-sleeve turnover. 2023-24 is feature-selection-contaminated and 2025/26 are previously inspected stress slices.

## Cost 0 bps

- DEV_2020_2022 LIQ_TOP2: median ΔSharpe vs EW8 -0.313; ΔCAGR +0.74%; ΔMDD -4.93%; better Sharpe 1/6; ΔSharpe vs persistence +0.112; permission 36.5%
- DEV_2020_2022 PERSIST×LIQ: median ΔSharpe vs EW8 -0.246; ΔCAGR -1.05%; ΔMDD -1.31%; better Sharpe 2/6; ΔSharpe vs persistence -0.067; permission 36.5%
- CONFIRM_2023_2024 LIQ_TOP2: median ΔSharpe vs EW8 -0.111; ΔCAGR +6.27%; ΔMDD -2.39%; better Sharpe 1/6; ΔSharpe vs persistence -0.239; permission 32.7%
- CONFIRM_2023_2024 PERSIST×LIQ: median ΔSharpe vs EW8 -0.075; ΔCAGR +1.80%; ΔMDD -0.36%; better Sharpe 2/6; ΔSharpe vs persistence -0.207; permission 32.7%
- BULL_2025 LIQ_TOP2: median ΔSharpe vs EW8 -0.671; ΔCAGR -4.16%; ΔMDD -2.22%; better Sharpe 0/6; ΔSharpe vs persistence -0.081; permission 20.8%
- BULL_2025 PERSIST×LIQ: median ΔSharpe vs EW8 -0.106; ΔCAGR -0.97%; ΔMDD +0.00%; better Sharpe 2/6; ΔSharpe vs persistence +0.426; permission 20.8%
- YTD_2026 LIQ_TOP2: median ΔSharpe vs EW8 +0.100; ΔCAGR +0.62%; ΔMDD +0.00%; better Sharpe 5/6; ΔSharpe vs persistence +0.630; permission 25.0%
- YTD_2026 PERSIST×LIQ: median ΔSharpe vs EW8 +0.179; ΔCAGR +1.28%; ΔMDD +0.09%; better Sharpe 4/6; ΔSharpe vs persistence -0.016; permission 25.0%

## Cost 10 bps

- DEV_2020_2022 LIQ_TOP2: median ΔSharpe vs EW8 -0.355; ΔCAGR +0.09%; ΔMDD -5.17%; better Sharpe 0/6; ΔSharpe vs persistence +0.128; permission 36.5%
- DEV_2020_2022 PERSIST×LIQ: median ΔSharpe vs EW8 -0.298; ΔCAGR -1.45%; ΔMDD -1.46%; better Sharpe 2/6; ΔSharpe vs persistence -0.042; permission 36.5%
- CONFIRM_2023_2024 LIQ_TOP2: median ΔSharpe vs EW8 -0.153; ΔCAGR +5.60%; ΔMDD -2.63%; better Sharpe 1/6; ΔSharpe vs persistence -0.237; permission 32.7%
- CONFIRM_2023_2024 PERSIST×LIQ: median ΔSharpe vs EW8 -0.110; ΔCAGR +1.49%; ΔMDD -0.44%; better Sharpe 2/6; ΔSharpe vs persistence -0.180; permission 32.7%
- BULL_2025 LIQ_TOP2: median ΔSharpe vs EW8 -0.693; ΔCAGR -4.60%; ΔMDD -2.26%; better Sharpe 0/6; ΔSharpe vs persistence -0.034; permission 20.8%
- BULL_2025 PERSIST×LIQ: median ΔSharpe vs EW8 -0.118; ΔCAGR -1.20%; ΔMDD +0.00%; better Sharpe 2/6; ΔSharpe vs persistence +0.483; permission 20.8%
- YTD_2026 LIQ_TOP2: median ΔSharpe vs EW8 +0.060; ΔCAGR +0.05%; ΔMDD +0.00%; better Sharpe 4/6; ΔSharpe vs persistence +0.655; permission 25.0%
- YTD_2026 PERSIST×LIQ: median ΔSharpe vs EW8 +0.136; ΔCAGR +0.71%; ΔMDD +0.05%; better Sharpe 4/6; ΔSharpe vs persistence +0.028; permission 25.0%

## Cost 30 bps

- DEV_2020_2022 LIQ_TOP2: median ΔSharpe vs EW8 -0.446; ΔCAGR -1.21%; ΔMDD -5.88%; better Sharpe 0/6; ΔSharpe vs persistence +0.160; permission 36.5%
- DEV_2020_2022 PERSIST×LIQ: median ΔSharpe vs EW8 -0.401; ΔCAGR -2.24%; ΔMDD -1.72%; better Sharpe 1/6; ΔSharpe vs persistence +0.007; permission 36.5%
- CONFIRM_2023_2024 LIQ_TOP2: median ΔSharpe vs EW8 -0.239; ΔCAGR +4.27%; ΔMDD -3.17%; better Sharpe 1/6; ΔSharpe vs persistence -0.234; permission 32.7%
- CONFIRM_2023_2024 PERSIST×LIQ: median ΔSharpe vs EW8 -0.181; ΔCAGR +0.87%; ΔMDD -0.58%; better Sharpe 1/6; ΔSharpe vs persistence -0.128; permission 32.7%
- BULL_2025 LIQ_TOP2: median ΔSharpe vs EW8 -0.755; ΔCAGR -5.60%; ΔMDD -2.33%; better Sharpe 0/6; ΔSharpe vs persistence +0.059; permission 20.8%
- BULL_2025 PERSIST×LIQ: median ΔSharpe vs EW8 -0.141; ΔCAGR -1.66%; ΔMDD +0.00%; better Sharpe 2/6; ΔSharpe vs persistence +0.595; permission 20.8%
- YTD_2026 LIQ_TOP2: median ΔSharpe vs EW8 -0.022; ΔCAGR -1.08%; ΔMDD -0.07%; better Sharpe 3/6; ΔSharpe vs persistence +0.705; permission 25.0%
- YTD_2026 PERSIST×LIQ: median ΔSharpe vs EW8 +0.049; ΔCAGR -0.43%; ΔMDD -0.02%; better Sharpe 3/6; ΔSharpe vs persistence +0.113; permission 25.0%

## 10 bps universe detail — LIQ_TOP2

### DEV_2020_2022
- K200: gate Sharpe +0.17 vs EW8 +0.93 (Δ -0.75); ΔCAGR -5.74%; permission 32%
- KOSDAQ: gate Sharpe +0.12 vs EW8 +0.69 (Δ -0.57); ΔCAGR -3.44%; permission 34%
- KOSDAQ_PLUS_KOSPI_EX_K200: gate Sharpe +0.89 vs EW8 +0.91 (Δ -0.02); ΔCAGR +2.99%; permission 39%
- KOSPI_ALL: gate Sharpe +0.99 vs EW8 +1.10 (Δ -0.11); ΔCAGR +0.88%; permission 32%
- KOSPI_EX_K200: gate Sharpe +0.85 vs EW8 +0.99 (Δ -0.14); ΔCAGR +3.80%; permission 39%
- KOSPI_KOSDAQ_ALL: gate Sharpe +0.60 vs EW8 +1.23 (Δ -0.63); ΔCAGR -0.70%; permission 42%

### CONFIRM_2023_2024
- K200: gate Sharpe +1.04 vs EW8 +1.48 (Δ -0.44); ΔCAGR +2.60%; permission 42%
- KOSDAQ: gate Sharpe +0.86 vs EW8 +0.54 (Δ +0.32); ΔCAGR +8.60%; permission 29%
- KOSDAQ_PLUS_KOSPI_EX_K200: gate Sharpe +0.62 vs EW8 +0.75 (Δ -0.13); ΔCAGR -0.33%; permission 21%
- KOSPI_ALL: gate Sharpe +1.17 vs EW8 +1.25 (Δ -0.08); ΔCAGR +9.52%; permission 38%
- KOSPI_EX_K200: gate Sharpe +0.03 vs EW8 +0.49 (Δ -0.46); ΔCAGR -4.33%; permission 32%
- KOSPI_KOSDAQ_ALL: gate Sharpe +1.16 vs EW8 +1.34 (Δ -0.17); ΔCAGR +11.99%; permission 33%

### BULL_2025
- K200: gate Sharpe +1.02 vs EW8 +1.99 (Δ -0.97); ΔCAGR -8.24%; permission 25%
- KOSDAQ: gate Sharpe +0.85 vs EW8 +1.26 (Δ -0.41); ΔCAGR -4.02%; permission 17%
- KOSDAQ_PLUS_KOSPI_EX_K200: gate Sharpe +1.10 vs EW8 +1.48 (Δ -0.37); ΔCAGR -3.99%; permission 8%
- KOSPI_ALL: gate Sharpe +0.36 vs EW8 +2.14 (Δ -1.77); ΔCAGR -14.64%; permission 33%
- KOSPI_EX_K200: gate Sharpe +0.63 vs EW8 +1.91 (Δ -1.29); ΔCAGR -5.17%; permission 42%
- KOSPI_KOSDAQ_ALL: gate Sharpe +1.61 vs EW8 +2.02 (Δ -0.41); ΔCAGR -1.71%; permission 17%

### YTD_2026
- K200: gate Sharpe +3.67 vs EW8 +3.22 (Δ +0.45); ΔCAGR +6.98%; permission 25%
- KOSDAQ: gate Sharpe +2.27 vs EW8 +2.80 (Δ -0.54); ΔCAGR -4.26%; permission 25%
- KOSDAQ_PLUS_KOSPI_EX_K200: gate Sharpe +2.91 vs EW8 +2.96 (Δ -0.05); ΔCAGR -0.59%; permission 25%
- KOSPI_ALL: gate Sharpe +3.34 vs EW8 +2.58 (Δ +0.76); ΔCAGR +8.56%; permission 25%
- KOSPI_EX_K200: gate Sharpe +0.83 vs EW8 +0.81 (Δ +0.01); ΔCAGR +0.03%; permission 25%
- KOSPI_KOSDAQ_ALL: gate Sharpe +3.76 vs EW8 +3.65 (Δ +0.11); ΔCAGR +0.08%; permission 25%

## Interpretation

- Do not tune the permission threshold after this run. A meaningful result must improve on EW8 broadly and not rely on one calendar slice.
- If the gate fails economically despite Stage-4A IC, the next step is leader-specific raw stock participation/turnover/overlap rather than more aggregate-liquidity transformations.