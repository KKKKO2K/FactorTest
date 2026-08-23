# Transition-Probability Market Allocation Audit

- This is a mechanical action test of the one Factor Regime signal that passed the information-value gate: B × F substate for next-B-down probability.
- TRAIN 2016-22 conditional probabilities are frozen. Exposure = 1 - predicted P(next B down). B×F exposure is TRAIN-normalized to the same average exposure as B-only, then clipped to [0,1].
- Signal dated t applies from the next trading day. Market daily returns are the same universe cap-weighted series used in Factor Regime v1.
- Costs of 0/10/30 bps are charged only on absolute allocator exposure changes at state updates. No return-fitted exposure threshold is used.

## Cost 0 bps

### TRAIN_2016_2022
- median ΔCAGR +0.09%; ΔSharpe +0.006; ΔMDD +0.12%; Δavg exposure -0.01%; CAGR-better 5/6, MDD-better 4/6

### OOS_2023_2024
- median ΔCAGR +0.13%; ΔSharpe +0.007; ΔMDD +0.28%; Δavg exposure -0.04%; CAGR-better 6/6, MDD-better 4/6

### BULL_2025
- median ΔCAGR +0.40%; ΔSharpe +0.023; ΔMDD +0.35%; Δavg exposure +0.36%; CAGR-better 4/6, MDD-better 6/6

### YTD_2026
- median ΔCAGR -0.03%; ΔSharpe -0.034; ΔMDD -1.28%; Δavg exposure +0.61%; CAGR-better 2/6, MDD-better 2/6

## Cost 10 bps

### TRAIN_2016_2022
- median ΔCAGR +0.02%; ΔSharpe +0.001; ΔMDD +0.08%; Δavg exposure -0.01%; CAGR-better 4/6, MDD-better 4/6

### OOS_2023_2024
- median ΔCAGR +0.07%; ΔSharpe +0.003; ΔMDD +0.24%; Δavg exposure -0.04%; CAGR-better 4/6, MDD-better 4/6

### BULL_2025
- median ΔCAGR +0.32%; ΔSharpe +0.019; ΔMDD +0.33%; Δavg exposure +0.36%; CAGR-better 4/6, MDD-better 6/6

### YTD_2026
- median ΔCAGR -0.08%; ΔSharpe -0.035; ΔMDD -1.28%; Δavg exposure +0.61%; CAGR-better 2/6, MDD-better 2/6

## Cost 30 bps

### TRAIN_2016_2022
- median ΔCAGR -0.07%; ΔSharpe -0.005; ΔMDD -0.02%; Δavg exposure -0.01%; CAGR-better 0/6, MDD-better 3/6

### OOS_2023_2024
- median ΔCAGR -0.05%; ΔSharpe -0.004; ΔMDD +0.18%; Δavg exposure -0.04%; CAGR-better 3/6, MDD-better 4/6

### BULL_2025
- median ΔCAGR +0.17%; ΔSharpe +0.012; ΔMDD +0.30%; Δavg exposure +0.36%; CAGR-better 4/6, MDD-better 5/6

### YTD_2026
- median ΔCAGR -0.18%; ΔSharpe -0.037; ΔMDD -1.28%; Δavg exposure +0.61%; CAGR-better 1/6, MDD-better 2/6

## OOS 2023-24 universe detail — 10 bps

- K200: ΔCAGR -0.09%, ΔSharpe -0.008, ΔMDD -1.06%, avg exposure 85.3% vs 85.2%
- KOSDAQ: ΔCAGR +0.11%, ΔSharpe +0.004, ΔMDD +0.27%, avg exposure 84.0% vs 84.9%
- KOSDAQ_PLUS_KOSPI_EX_K200: ΔCAGR +0.26%, ΔSharpe +0.014, ΔMDD +0.34%, avg exposure 88.0% vs 88.2%
- KOSPI_ALL: ΔCAGR +0.03%, ΔSharpe +0.002, ΔMDD -0.12%, avg exposure 87.2% vs 87.0%
- KOSPI_EX_K200: ΔCAGR +0.38%, ΔSharpe +0.026, ΔMDD +0.99%, avg exposure 83.5% vs 84.3%
- KOSPI_KOSDAQ_ALL: ΔCAGR -0.04%, ΔSharpe -0.002, ΔMDD +0.22%, avg exposure 87.2% vs 86.6%

## Interpretation gate

- Production evidence requires OOS 2023-24 median Sharpe improvement and non-worse median MDD at 10 bps, with Sharpe improvement in at least 4/6 universes.
- 2025/2026-only success is stress evidence, not confirmation.
- This allocation mapping is intentionally mechanical; if it fails, do not tune probability thresholds on 2025/2026.