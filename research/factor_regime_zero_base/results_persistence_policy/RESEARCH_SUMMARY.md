# Persistence / Rotation Stage 1b — Economic Policy Audit

- Feature set is frozen to the seven Stage-1 PASS predictors for TARGET_FACTOR_MOM_20.
- Each evaluation year estimates only feature standardization and predictor direction from prior data.
- Composite top tercile -> current top-2 factors; bottom tercile -> current bottom-2 factors; middle -> equal-weight 8 factors.
- Decisions are sampled every fourth 5D state so the 20D holding windows do not overlap.
- Costs are charged on factor-sleeve one-way turnover. MDD is 20D-rebalance NAV MDD, not daily-NAV MDD.
- 2025/2026 are stress evidence, not pristine untouched OOS because Stage 1 already inspected them.

## Cost 0 bps

- DEV_2020_2022: median ΔCAGR vs TOP2 +1.16%; ΔSharpe +0.129; ΔMDD +6.22%; better Sharpe 5/6 universes; median ΔSharpe vs EW8 -0.369; median sign-hit 50.0%
- CONFIRM_2023_2024: median ΔCAGR vs TOP2 +3.37%; ΔSharpe +0.488; ΔMDD +8.17%; better Sharpe 5/6 universes; median ΔSharpe vs EW8 -0.020; median sign-hit 58.3%
- BULL_2025: median ΔCAGR vs TOP2 +7.56%; ΔSharpe +0.963; ΔMDD +5.30%; better Sharpe 4/6 universes; median ΔSharpe vs EW8 -0.702; median sign-hit 54.2%
- YTD_2026: median ΔCAGR vs TOP2 +15.15%; ΔSharpe +1.001; ΔMDD +1.08%; better Sharpe 5/6 universes; median ΔSharpe vs EW8 -0.494; median sign-hit 62.5%

## Cost 10 bps

- DEV_2020_2022: median ΔCAGR vs TOP2 +1.18%; ΔSharpe +0.112; ΔMDD +6.15%; better Sharpe 4/6 universes; median ΔSharpe vs EW8 -0.445; median sign-hit 50.0%
- CONFIRM_2023_2024: median ΔCAGR vs TOP2 +3.37%; ΔSharpe +0.481; ΔMDD +8.37%; better Sharpe 5/6 universes; median ΔSharpe vs EW8 -0.085; median sign-hit 58.3%
- BULL_2025: median ΔCAGR vs TOP2 +7.76%; ΔSharpe +0.955; ΔMDD +5.10%; better Sharpe 4/6 universes; median ΔSharpe vs EW8 -0.782; median sign-hit 54.2%
- YTD_2026: median ΔCAGR vs TOP2 +15.23%; ΔSharpe +0.962; ΔMDD +1.07%; better Sharpe 5/6 universes; median ΔSharpe vs EW8 -0.545; median sign-hit 62.5%

## Cost 30 bps

- DEV_2020_2022: median ΔCAGR vs TOP2 +1.22%; ΔSharpe +0.078; ΔMDD +6.01%; better Sharpe 4/6 universes; median ΔSharpe vs EW8 -0.597; median sign-hit 50.0%
- CONFIRM_2023_2024: median ΔCAGR vs TOP2 +3.38%; ΔSharpe +0.468; ΔMDD +9.12%; better Sharpe 5/6 universes; median ΔSharpe vs EW8 -0.215; median sign-hit 58.3%
- BULL_2025: median ΔCAGR vs TOP2 +8.13%; ΔSharpe +0.938; ΔMDD +4.72%; better Sharpe 4/6 universes; median ΔSharpe vs EW8 -0.942; median sign-hit 54.2%
- YTD_2026: median ΔCAGR vs TOP2 +15.37%; ΔSharpe +0.883; ΔMDD +1.02%; better Sharpe 5/6 universes; median ΔSharpe vs EW8 -0.645; median sign-hit 62.5%

## 2025 / 2026 universe detail — 10 bps

- BULL_2025 K200: policy Sharpe +1.53 vs TOP2 +0.06 (Δ +1.47); ΔCAGR +27.17%; actions TOP2/BOTTOM2/EW8 25%/25%/50%
- BULL_2025 KOSDAQ: policy Sharpe -0.00 vs TOP2 +0.23 (Δ -0.23); ΔCAGR -2.95%; actions TOP2/BOTTOM2/EW8 25%/42%/33%
- BULL_2025 KOSDAQ_PLUS_KOSPI_EX_K200: policy Sharpe +0.12 vs TOP2 +1.71 (Δ -1.59); ΔCAGR -17.96%; actions TOP2/BOTTOM2/EW8 42%/33%/25%
- BULL_2025 KOSPI_ALL: policy Sharpe +1.43 vs TOP2 -0.40 (Δ +1.83); ΔCAGR +26.24%; actions TOP2/BOTTOM2/EW8 17%/50%/33%
- BULL_2025 KOSPI_EX_K200: policy Sharpe +2.18 vs TOP2 +0.84 (Δ +1.33); ΔCAGR +11.96%; actions TOP2/BOTTOM2/EW8 33%/25%/42%
- BULL_2025 KOSPI_KOSDAQ_ALL: policy Sharpe +1.17 vs TOP2 +0.59 (Δ +0.58); ΔCAGR +3.55%; actions TOP2/BOTTOM2/EW8 8%/50%/42%
- YTD_2026 K200: policy Sharpe +2.11 vs TOP2 +0.27 (Δ +1.84); ΔCAGR +55.77%; actions TOP2/BOTTOM2/EW8 25%/75%/0%
- YTD_2026 KOSDAQ: policy Sharpe +2.01 vs TOP2 +2.62 (Δ -0.62); ΔCAGR -32.88%; actions TOP2/BOTTOM2/EW8 25%/50%/25%
- YTD_2026 KOSDAQ_PLUS_KOSPI_EX_K200: policy Sharpe +4.12 vs TOP2 +3.02 (Δ +1.10); ΔCAGR -34.18%; actions TOP2/BOTTOM2/EW8 0%/25%/75%
- YTD_2026 KOSPI_ALL: policy Sharpe +2.29 vs TOP2 +1.46 (Δ +0.83); ΔCAGR +36.05%; actions TOP2/BOTTOM2/EW8 25%/75%/0%
- YTD_2026 KOSPI_EX_K200: policy Sharpe +2.07 vs TOP2 +1.39 (Δ +0.68); ΔCAGR +6.57%; actions TOP2/BOTTOM2/EW8 25%/50%/25%
- YTD_2026 KOSPI_KOSDAQ_ALL: policy Sharpe +1.31 vs TOP2 -1.91 (Δ +3.22); ΔCAGR +23.88%; actions TOP2/BOTTOM2/EW8 50%/50%/0%

## Interpretation rule

- Do not tune score cutoffs after seeing these results. If policy improvement is broad in 2023-24 and survives both 2025 and 2026 stress, the persistence/rotation axis is economically actionable.
- If predictive IC survives but policy value is unstable, retain persistence as a monitoring/risk state and proceed to Factor Opportunity.