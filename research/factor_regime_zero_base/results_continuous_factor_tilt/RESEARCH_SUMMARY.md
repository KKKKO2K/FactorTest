# Continuous Factor Risk-Budget Tilt — Zero Base Stage 5

- EW8 is always retained as the core portfolio.
- Frozen mapping before this run: w = EW8 + lambda * (TOP2 - EW8), lambda bounded to [-0.25, +0.25].
- Persistence block uses the seven Stage-1 factor-momentum survivors; liquidity/selectivity block uses MKT_ACT1_BREADTH, MKT_ACT1_CHANGE_4 and FACTOR_TOP_ACT5_BREADTH_MEAN.
- Feature directions, standardization and empirical percentile maps use only prior data each evaluation year.
- Combined tilt is equal-block Persistence / Liquidity; no threshold sweep and no max-tilt sweep.
- Decisions are non-overlapping 20D; costs apply to one-way factor-sleeve turnover.
- Primary benchmark is EW8. 2025/26 are stress evidence, not pristine untouched OOS.

## Predeclared success gate

- At 10 bps, a model must have positive median Sharpe delta vs EW8 in both DEV 2020-22 and CONFIRM 2023-24.
- It must improve Sharpe in at least 4/6 universes in CONFIRM 2023-24.
- 2025/2026-only success is insufficient.

## Cost 0 bps

### PERSIST_CONT
- DEV_2020_2022: median ΔSharpe vs EW8 +0.155; ΔCAGR +1.21%; ΔMDD +0.74%; better Sharpe 6/6 universes; median |lambda| 0.138; median annual turnover 2.00
- CONFIRM_2023_2024: median ΔSharpe vs EW8 +0.184; ΔCAGR +1.06%; ΔMDD +0.35%; better Sharpe 4/6 universes; median |lambda| 0.135; median annual turnover 1.71
- BULL_2025: median ΔSharpe vs EW8 +0.099; ΔCAGR +1.70%; ΔMDD +0.04%; better Sharpe 5/6 universes; median |lambda| 0.131; median annual turnover 1.74
- YTD_2026: median ΔSharpe vs EW8 +0.127; ΔCAGR +2.26%; ΔMDD +0.05%; better Sharpe 4/6 universes; median |lambda| 0.146; median annual turnover 1.99

### LIQ_CONT
- DEV_2020_2022: median ΔSharpe vs EW8 +0.022; ΔCAGR +0.42%; ΔMDD +0.14%; better Sharpe 3/6 universes; median |lambda| 0.123; median annual turnover 1.84
- CONFIRM_2023_2024: median ΔSharpe vs EW8 +0.212; ΔCAGR +2.33%; ΔMDD -0.21%; better Sharpe 4/6 universes; median |lambda| 0.105; median annual turnover 1.55
- BULL_2025: median ΔSharpe vs EW8 +0.020; ΔCAGR +0.23%; ΔMDD -0.18%; better Sharpe 3/6 universes; median |lambda| 0.137; median annual turnover 1.82
- YTD_2026: median ΔSharpe vs EW8 +0.020; ΔCAGR +0.14%; ΔMDD +0.01%; better Sharpe 3/6 universes; median |lambda| 0.156; median annual turnover 1.95

### COMBINED_CONT
- DEV_2020_2022: median ΔSharpe vs EW8 +0.117; ΔCAGR +0.86%; ΔMDD +0.26%; better Sharpe 6/6 universes; median |lambda| 0.129; median annual turnover 1.96
- CONFIRM_2023_2024: median ΔSharpe vs EW8 +0.185; ΔCAGR +1.32%; ΔMDD +0.12%; better Sharpe 5/6 universes; median |lambda| 0.124; median annual turnover 1.71
- BULL_2025: median ΔSharpe vs EW8 +0.092; ΔCAGR +1.54%; ΔMDD -0.09%; better Sharpe 5/6 universes; median |lambda| 0.129; median annual turnover 1.73
- YTD_2026: median ΔSharpe vs EW8 +0.038; ΔCAGR +2.16%; ΔMDD +0.02%; better Sharpe 4/6 universes; median |lambda| 0.109; median annual turnover 1.69

## Cost 10 bps

### PERSIST_CONT
- DEV_2020_2022: median ΔSharpe vs EW8 +0.129; ΔCAGR +1.05%; ΔMDD +0.65%; better Sharpe 5/6 universes; median |lambda| 0.138; median annual turnover 2.00
- CONFIRM_2023_2024: median ΔSharpe vs EW8 +0.159; ΔCAGR +0.88%; ΔMDD +0.31%; better Sharpe 4/6 universes; median |lambda| 0.135; median annual turnover 1.71
- BULL_2025: median ΔSharpe vs EW8 +0.077; ΔCAGR +1.51%; ΔMDD +0.03%; better Sharpe 5/6 universes; median |lambda| 0.131; median annual turnover 1.74
- YTD_2026: median ΔSharpe vs EW8 +0.107; ΔCAGR +2.04%; ΔMDD +0.05%; better Sharpe 4/6 universes; median |lambda| 0.146; median annual turnover 1.99

### LIQ_CONT
- DEV_2020_2022: median ΔSharpe vs EW8 +0.001; ΔCAGR +0.26%; ΔMDD +0.11%; better Sharpe 3/6 universes; median |lambda| 0.123; median annual turnover 1.84
- CONFIRM_2023_2024: median ΔSharpe vs EW8 +0.190; ΔCAGR +2.16%; ΔMDD -0.26%; better Sharpe 4/6 universes; median |lambda| 0.105; median annual turnover 1.55
- BULL_2025: median ΔSharpe vs EW8 +0.003; ΔCAGR +0.04%; ΔMDD -0.20%; better Sharpe 3/6 universes; median |lambda| 0.137; median annual turnover 1.82
- YTD_2026: median ΔSharpe vs EW8 +0.003; ΔCAGR -0.11%; ΔMDD +0.01%; better Sharpe 3/6 universes; median |lambda| 0.156; median annual turnover 1.95

### COMBINED_CONT
- DEV_2020_2022: median ΔSharpe vs EW8 +0.093; ΔCAGR +0.67%; ΔMDD +0.22%; better Sharpe 6/6 universes; median |lambda| 0.129; median annual turnover 1.96
- CONFIRM_2023_2024: median ΔSharpe vs EW8 +0.158; ΔCAGR +1.12%; ΔMDD +0.07%; better Sharpe 5/6 universes; median |lambda| 0.124; median annual turnover 1.71
- BULL_2025: median ΔSharpe vs EW8 +0.074; ΔCAGR +1.33%; ΔMDD -0.12%; better Sharpe 5/6 universes; median |lambda| 0.129; median annual turnover 1.73
- YTD_2026: median ΔSharpe vs EW8 +0.029; ΔCAGR +2.00%; ΔMDD +0.02%; better Sharpe 4/6 universes; median |lambda| 0.109; median annual turnover 1.69

## Cost 30 bps

### PERSIST_CONT
- DEV_2020_2022: median ΔSharpe vs EW8 +0.079; ΔCAGR +0.72%; ΔMDD +0.47%; better Sharpe 5/6 universes; median |lambda| 0.138; median annual turnover 2.00
- CONFIRM_2023_2024: median ΔSharpe vs EW8 +0.110; ΔCAGR +0.51%; ΔMDD +0.23%; better Sharpe 4/6 universes; median |lambda| 0.135; median annual turnover 1.71
- BULL_2025: median ΔSharpe vs EW8 +0.033; ΔCAGR +1.12%; ΔMDD +0.01%; better Sharpe 4/6 universes; median |lambda| 0.131; median annual turnover 1.74
- YTD_2026: median ΔSharpe vs EW8 +0.066; ΔCAGR +1.60%; ΔMDD +0.05%; better Sharpe 4/6 universes; median |lambda| 0.146; median annual turnover 1.99

### LIQ_CONT
- DEV_2020_2022: median ΔSharpe vs EW8 -0.040; ΔCAGR -0.07%; ΔMDD +0.05%; better Sharpe 3/6 universes; median |lambda| 0.123; median annual turnover 1.84
- CONFIRM_2023_2024: median ΔSharpe vs EW8 +0.144; ΔCAGR +1.81%; ΔMDD -0.37%; better Sharpe 4/6 universes; median |lambda| 0.105; median annual turnover 1.55
- BULL_2025: median ΔSharpe vs EW8 -0.047; ΔCAGR -0.36%; ΔMDD -0.24%; better Sharpe 3/6 universes; median |lambda| 0.137; median annual turnover 1.82
- YTD_2026: median ΔSharpe vs EW8 -0.030; ΔCAGR -0.59%; ΔMDD -0.01%; better Sharpe 3/6 universes; median |lambda| 0.156; median annual turnover 1.95

### COMBINED_CONT
- DEV_2020_2022: median ΔSharpe vs EW8 +0.045; ΔCAGR +0.31%; ΔMDD +0.16%; better Sharpe 4/6 universes; median |lambda| 0.129; median annual turnover 1.96
- CONFIRM_2023_2024: median ΔSharpe vs EW8 +0.106; ΔCAGR +0.73%; ΔMDD -0.03%; better Sharpe 5/6 universes; median |lambda| 0.124; median annual turnover 1.71
- BULL_2025: median ΔSharpe vs EW8 +0.039; ΔCAGR +0.93%; ΔMDD -0.17%; better Sharpe 3/6 universes; median |lambda| 0.129; median annual turnover 1.73
- YTD_2026: median ΔSharpe vs EW8 +0.010; ΔCAGR +1.67%; ΔMDD +0.01%; better Sharpe 4/6 universes; median |lambda| 0.109; median annual turnover 1.69

## Gate result at 10 bps

- PERSIST_CONT: PASS=True; DEV median ΔSharpe +0.129; CONFIRM +0.159; CONFIRM better universes 4/6
- LIQ_CONT: PASS=True; DEV median ΔSharpe +0.001; CONFIRM +0.190; CONFIRM better universes 4/6
- COMBINED_CONT: PASS=True; DEV median ΔSharpe +0.093; CONFIRM +0.158; CONFIRM better universes 5/6

## Interpretation rule

- Do not change max tilt or percentile mapping after seeing this output.
- If the continuous form passes, treat Factor Regime as a bounded active-risk budgeting signal rather than a discrete state classifier.
- If it fails, the surviving IC remains useful for monitoring, but the next allocation research must add genuinely leader-specific raw stock information rather than retuning the same factor-return/liquidity aggregates.