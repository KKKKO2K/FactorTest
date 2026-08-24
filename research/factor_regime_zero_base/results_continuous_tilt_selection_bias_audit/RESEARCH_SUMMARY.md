# Continuous Tilt Feature-Selection Bias Audit

- Purpose: test whether the Stage-5 continuous-tilt result survives without using the DEV/CONFIRM survivor lists to choose inputs.
- Persistence block uses all 18 predictors declared before Stage 1; liquidity block uses all 10 aggregate stock/liquidity features declared before Stage 4A.
- No feature is removed because of 2020-24 performance. Only feature direction, standardization and percentile mapping are estimated from prior data each evaluation year.
- Portfolio mapping is unchanged from Stage 5: EW8 + lambda*(TOP2-EW8), lambda in [-0.25,+0.25].
- No max-tilt sweep, no threshold sweep, and no post-result feature pruning.

## Predeclared robustness gate

- At 10 bps: positive median Sharpe delta vs EW8 in DEV 2020-22 and CONFIRM 2023-24, with >=4/6 confirmation universes improving.
- 2025/2026 are stress evidence only.

## Cost 0 bps

### PERSIST_ALL_CONT
- DEV_2020_2022: median ΔSharpe +0.139; ΔCAGR +0.93%; ΔMDD +0.68%; better Sharpe 6/6; median |lambda| 0.143; annual turnover 2.00
- CONFIRM_2023_2024: median ΔSharpe +0.026; ΔCAGR +0.07%; ΔMDD +0.32%; better Sharpe 4/6; median |lambda| 0.128; annual turnover 1.73
- BULL_2025: median ΔSharpe +0.119; ΔCAGR +1.96%; ΔMDD +0.04%; better Sharpe 4/6; median |lambda| 0.119; annual turnover 1.56
- YTD_2026: median ΔSharpe +0.244; ΔCAGR +2.79%; ΔMDD +0.00%; better Sharpe 5/6; median |lambda| 0.120; annual turnover 2.04

### LIQ_ALL_CONT
- DEV_2020_2022: median ΔSharpe +0.007; ΔCAGR +0.07%; ΔMDD +0.00%; better Sharpe 3/6; median |lambda| 0.124; annual turnover 1.86
- CONFIRM_2023_2024: median ΔSharpe +0.047; ΔCAGR +0.57%; ΔMDD -0.45%; better Sharpe 3/6; median |lambda| 0.112; annual turnover 1.58
- BULL_2025: median ΔSharpe -0.058; ΔCAGR -0.33%; ΔMDD -0.26%; better Sharpe 2/6; median |lambda| 0.136; annual turnover 1.86
- YTD_2026: median ΔSharpe +0.047; ΔCAGR +1.04%; ΔMDD +0.01%; better Sharpe 3/6; median |lambda| 0.161; annual turnover 1.94

### COMBINED_ALL_CONT
- DEV_2020_2022: median ΔSharpe +0.101; ΔCAGR +0.55%; ΔMDD +0.68%; better Sharpe 6/6; median |lambda| 0.129; annual turnover 1.95
- CONFIRM_2023_2024: median ΔSharpe +0.040; ΔCAGR +0.22%; ΔMDD +0.06%; better Sharpe 3/6; median |lambda| 0.111; annual turnover 1.60
- BULL_2025: median ΔSharpe +0.013; ΔCAGR +0.64%; ΔMDD -0.20%; better Sharpe 3/6; median |lambda| 0.147; annual turnover 1.81
- YTD_2026: median ΔSharpe +0.174; ΔCAGR +1.03%; ΔMDD +0.04%; better Sharpe 5/6; median |lambda| 0.149; annual turnover 1.99

## Cost 10 bps

### PERSIST_ALL_CONT
- DEV_2020_2022: median ΔSharpe +0.112; ΔCAGR +0.73%; ΔMDD +0.60%; better Sharpe 5/6; median |lambda| 0.143; annual turnover 2.00
- CONFIRM_2023_2024: median ΔSharpe +0.002; ΔCAGR -0.11%; ΔMDD +0.28%; better Sharpe 4/6; median |lambda| 0.128; annual turnover 1.73
- BULL_2025: median ΔSharpe +0.102; ΔCAGR +1.80%; ΔMDD +0.04%; better Sharpe 4/6; median |lambda| 0.119; annual turnover 1.56
- YTD_2026: median ΔSharpe +0.222; ΔCAGR +2.50%; ΔMDD -0.01%; better Sharpe 5/6; median |lambda| 0.120; annual turnover 2.04

### LIQ_ALL_CONT
- DEV_2020_2022: median ΔSharpe -0.016; ΔCAGR -0.10%; ΔMDD -0.03%; better Sharpe 2/6; median |lambda| 0.124; annual turnover 1.86
- CONFIRM_2023_2024: median ΔSharpe +0.024; ΔCAGR +0.40%; ΔMDD -0.50%; better Sharpe 3/6; median |lambda| 0.112; annual turnover 1.58
- BULL_2025: median ΔSharpe -0.082; ΔCAGR -0.53%; ΔMDD -0.28%; better Sharpe 2/6; median |lambda| 0.136; annual turnover 1.86
- YTD_2026: median ΔSharpe +0.030; ΔCAGR +0.77%; ΔMDD +0.01%; better Sharpe 3/6; median |lambda| 0.161; annual turnover 1.94

### COMBINED_ALL_CONT
- DEV_2020_2022: median ΔSharpe +0.076; ΔCAGR +0.39%; ΔMDD +0.59%; better Sharpe 6/6; median |lambda| 0.129; annual turnover 1.95
- CONFIRM_2023_2024: median ΔSharpe +0.016; ΔCAGR +0.03%; ΔMDD +0.01%; better Sharpe 3/6; median |lambda| 0.111; annual turnover 1.60
- BULL_2025: median ΔSharpe -0.012; ΔCAGR +0.45%; ΔMDD -0.23%; better Sharpe 3/6; median |lambda| 0.147; annual turnover 1.81
- YTD_2026: median ΔSharpe +0.158; ΔCAGR +0.76%; ΔMDD +0.04%; better Sharpe 5/6; median |lambda| 0.149; annual turnover 1.99

## Cost 30 bps

### PERSIST_ALL_CONT
- DEV_2020_2022: median ΔSharpe +0.057; ΔCAGR +0.34%; ΔMDD +0.44%; better Sharpe 5/6; median |lambda| 0.143; annual turnover 2.00
- CONFIRM_2023_2024: median ΔSharpe -0.044; ΔCAGR -0.46%; ΔMDD +0.19%; better Sharpe 2/6; median |lambda| 0.128; annual turnover 1.73
- BULL_2025: median ΔSharpe +0.066; ΔCAGR +1.49%; ΔMDD +0.02%; better Sharpe 4/6; median |lambda| 0.119; annual turnover 1.56
- YTD_2026: median ΔSharpe +0.177; ΔCAGR +1.92%; ΔMDD -0.02%; better Sharpe 5/6; median |lambda| 0.120; annual turnover 2.04

### LIQ_ALL_CONT
- DEV_2020_2022: median ΔSharpe -0.061; ΔCAGR -0.44%; ΔMDD -0.09%; better Sharpe 0/6; median |lambda| 0.124; annual turnover 1.86
- CONFIRM_2023_2024: median ΔSharpe -0.021; ΔCAGR +0.07%; ΔMDD -0.62%; better Sharpe 3/6; median |lambda| 0.112; annual turnover 1.58
- BULL_2025: median ΔSharpe -0.131; ΔCAGR -0.91%; ΔMDD -0.32%; better Sharpe 2/6; median |lambda| 0.136; annual turnover 1.86
- YTD_2026: median ΔSharpe -0.003; ΔCAGR +0.25%; ΔMDD -0.01%; better Sharpe 3/6; median |lambda| 0.161; annual turnover 1.94

### COMBINED_ALL_CONT
- DEV_2020_2022: median ΔSharpe +0.027; ΔCAGR +0.05%; ΔMDD +0.42%; better Sharpe 3/6; median |lambda| 0.129; annual turnover 1.95
- CONFIRM_2023_2024: median ΔSharpe -0.034; ΔCAGR -0.33%; ΔMDD -0.10%; better Sharpe 3/6; median |lambda| 0.111; annual turnover 1.60
- BULL_2025: median ΔSharpe -0.061; ΔCAGR +0.06%; ΔMDD -0.29%; better Sharpe 2/6; median |lambda| 0.147; annual turnover 1.81
- YTD_2026: median ΔSharpe +0.125; ΔCAGR +0.20%; ΔMDD +0.03%; better Sharpe 5/6; median |lambda| 0.149; annual turnover 1.99

## Gate result at 10 bps

- PERSIST_ALL_CONT: PASS=True; DEV +0.112; CONFIRM +0.002; CONFIRM better 4/6
- LIQ_ALL_CONT: PASS=False; DEV -0.016; CONFIRM +0.024; CONFIRM better 3/6
- COMBINED_ALL_CONT: PASS=False; DEV +0.076; CONFIRM +0.016; CONFIRM better 3/6

## Interpretation

- A PASS here is materially stronger evidence than Stage 5 because the predictor list itself no longer embeds the 2023-24 survivor screen.
- A FAIL does not erase the underlying IC findings, but would downgrade Stage 5 to an exploratory survivor-selection result.