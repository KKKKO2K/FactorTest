# Factor Crash-Risk Cap — Stage 3b

- Crash score is frozen to LOSER_WEAKNESS_20, DISPERSION_20, and TOP2_PREMIUM_20, selected because each passed the Stage-3 DEV/CONFIRM gate for current-top2 relative loss and at least one other adverse target.
- Predictor directions and top-tercile crash threshold are estimated only from prior data each year.
- The cap only changes one action: when persistence-only says TOP2 and crash risk is in the train-defined top tercile, use EW8 instead. BOTTOM2 and EW8 decisions are untouched.
- Decisions are non-overlapping 20D; costs apply to one-way factor-sleeve turnover.

## Cost 0 bps

- DEV_2020_2022: ΔSharpe vs persistence +0.000; ΔCAGR +0.00%; ΔMDD +0.00%; better Sharpe 2/6; ΔSharpe vs EW8 -0.342; cap-trigger share 2.6%
- CONFIRM_2023_2024: ΔSharpe vs persistence -0.069; ΔCAGR -1.21%; ΔMDD +0.00%; better Sharpe 2/6; ΔSharpe vs EW8 -0.162; cap-trigger share 8.3%
- BULL_2025: ΔSharpe vs persistence +0.018; ΔCAGR +0.19%; ΔMDD +0.00%; better Sharpe 3/6; ΔSharpe vs EW8 -0.702; cap-trigger share 4.2%
- YTD_2026: ΔSharpe vs persistence +0.000; ΔCAGR +0.00%; ΔMDD +0.00%; better Sharpe 0/6; ΔSharpe vs EW8 -0.494; cap-trigger share 0.0%

## Cost 10 bps

- DEV_2020_2022: ΔSharpe vs persistence +0.000; ΔCAGR +0.00%; ΔMDD +0.00%; better Sharpe 2/6; ΔSharpe vs EW8 -0.418; cap-trigger share 2.6%
- CONFIRM_2023_2024: ΔSharpe vs persistence -0.068; ΔCAGR -1.17%; ΔMDD +0.01%; better Sharpe 2/6; ΔSharpe vs EW8 -0.222; cap-trigger share 8.3%
- BULL_2025: ΔSharpe vs persistence +0.018; ΔCAGR +0.19%; ΔMDD +0.00%; better Sharpe 3/6; ΔSharpe vs EW8 -0.782; cap-trigger share 4.2%
- YTD_2026: ΔSharpe vs persistence +0.000; ΔCAGR +0.00%; ΔMDD +0.00%; better Sharpe 0/6; ΔSharpe vs EW8 -0.545; cap-trigger share 0.0%

## Cost 30 bps

- DEV_2020_2022: ΔSharpe vs persistence +0.000; ΔCAGR +0.00%; ΔMDD +0.00%; better Sharpe 2/6; ΔSharpe vs EW8 -0.570; cap-trigger share 2.6%
- CONFIRM_2023_2024: ΔSharpe vs persistence -0.064; ΔCAGR -1.10%; ΔMDD +0.00%; better Sharpe 1/6; ΔSharpe vs EW8 -0.333; cap-trigger share 8.3%
- BULL_2025: ΔSharpe vs persistence +0.018; ΔCAGR +0.18%; ΔMDD +0.00%; better Sharpe 3/6; ΔSharpe vs EW8 -0.942; cap-trigger share 4.2%
- YTD_2026: ΔSharpe vs persistence +0.000; ΔCAGR +0.00%; ΔMDD +0.00%; better Sharpe 0/6; ΔSharpe vs EW8 -0.645; cap-trigger share 0.0%

## 10 bps universe detail

### DEV_2020_2022
- K200: cap Sharpe +0.34 vs persistence +0.41 (Δ -0.07) vs EW8 +0.93; ΔCAGR vs persistence -0.90%; trigger 3%
- KOSDAQ: cap Sharpe +0.55 vs persistence +0.55 (Δ +0.00) vs EW8 +0.69; ΔCAGR vs persistence +0.00%; trigger 0%
- KOSDAQ_PLUS_KOSPI_EX_K200: cap Sharpe +0.89 vs persistence +0.89 (Δ +0.00) vs EW8 +0.91; ΔCAGR vs persistence +0.00%; trigger 0%
- KOSPI_ALL: cap Sharpe +0.84 vs persistence +0.73 (Δ +0.12) vs EW8 +1.10; ΔCAGR vs persistence +0.79%; trigger 8%
- KOSPI_EX_K200: cap Sharpe +0.26 vs persistence +0.35 (Δ -0.09) vs EW8 +0.99; ΔCAGR vs persistence -1.56%; trigger 16%
- KOSPI_KOSDAQ_ALL: cap Sharpe +0.28 vs persistence +0.21 (Δ +0.07) vs EW8 +1.23; ΔCAGR vs persistence +0.79%; trigger 3%

### CONFIRM_2023_2024
- K200: cap Sharpe +1.26 vs persistence +1.36 (Δ -0.10) vs EW8 +1.48; ΔCAGR vs persistence -1.89%; trigger 8%
- KOSDAQ: cap Sharpe +1.23 vs persistence +1.37 (Δ -0.14) vs EW8 +0.54; ΔCAGR vs persistence -9.60%; trigger 12%
- KOSDAQ_PLUS_KOSPI_EX_K200: cap Sharpe +1.12 vs persistence +1.12 (Δ +0.00) vs EW8 +0.75; ΔCAGR vs persistence -0.03%; trigger 8%
- KOSPI_ALL: cap Sharpe +1.01 vs persistence +1.21 (Δ -0.20) vs EW8 +1.25; ΔCAGR vs persistence -2.92%; trigger 8%
- KOSPI_EX_K200: cap Sharpe +0.27 vs persistence +0.19 (Δ +0.08) vs EW8 +0.49; ΔCAGR vs persistence +0.99%; trigger 8%
- KOSPI_KOSDAQ_ALL: cap Sharpe +0.69 vs persistence +0.73 (Δ -0.04) vs EW8 +1.34; ΔCAGR vs persistence -0.45%; trigger 4%

### BULL_2025
- K200: cap Sharpe +1.73 vs persistence +1.53 (Δ +0.20) vs EW8 +1.99; ΔCAGR vs persistence +3.58%; trigger 8%
- KOSDAQ: cap Sharpe +0.03 vs persistence -0.00 (Δ +0.04) vs EW8 +1.26; ΔCAGR vs persistence +0.38%; trigger 8%
- KOSDAQ_PLUS_KOSPI_EX_K200: cap Sharpe +0.12 vs persistence +0.12 (Δ +0.00) vs EW8 +1.48; ΔCAGR vs persistence +0.00%; trigger 0%
- KOSPI_ALL: cap Sharpe +1.43 vs persistence +1.43 (Δ +0.00) vs EW8 +2.14; ΔCAGR vs persistence +0.00%; trigger 0%
- KOSPI_EX_K200: cap Sharpe +2.32 vs persistence +2.18 (Δ +0.14) vs EW8 +1.91; ΔCAGR vs persistence +0.99%; trigger 8%
- KOSPI_KOSDAQ_ALL: cap Sharpe +1.17 vs persistence +1.17 (Δ +0.00) vs EW8 +2.02; ΔCAGR vs persistence +0.00%; trigger 0%

### YTD_2026
- K200: cap Sharpe +2.11 vs persistence +2.11 (Δ +0.00) vs EW8 +3.22; ΔCAGR vs persistence +0.00%; trigger 0%
- KOSDAQ: cap Sharpe +2.01 vs persistence +2.01 (Δ +0.00) vs EW8 +2.80; ΔCAGR vs persistence +0.00%; trigger 0%
- KOSDAQ_PLUS_KOSPI_EX_K200: cap Sharpe +4.12 vs persistence +4.12 (Δ +0.00) vs EW8 +2.96; ΔCAGR vs persistence +0.00%; trigger 0%
- KOSPI_ALL: cap Sharpe +2.29 vs persistence +2.29 (Δ +0.00) vs EW8 +2.58; ΔCAGR vs persistence +0.00%; trigger 0%
- KOSPI_EX_K200: cap Sharpe +2.03 vs persistence +2.07 (Δ -0.05) vs EW8 +0.81; ΔCAGR vs persistence -0.48%; trigger 25%
- KOSPI_KOSDAQ_ALL: cap Sharpe +1.31 vs persistence +1.31 (Δ +0.00) vs EW8 +3.65; ΔCAGR vs persistence +0.00%; trigger 0%

## Interpretation

- Do not retune the threshold after this run. A useful crash cap should improve persistence-only broadly without depending on 2025 or 2026 alone.
- If it fails, factor-return-only crowding has reached its useful limit; the next crash research should add stock-level participation, turnover/ADV and holdings-overlap data.