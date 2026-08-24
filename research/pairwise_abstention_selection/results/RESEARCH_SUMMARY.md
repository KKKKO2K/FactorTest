# Pairwise Ranking + Abstention / Confidence Sizing

This follow-up is explicitly post-hoc exploratory. The ranking model remains frozen from Discovery 2016–19, and confidence thresholds are calibrated only from Discovery confidence distributions.

## Classification: **REJECT**

- Confidence diagnostic gate: False
- Abstention strategies passing the primary-style economic gate: None

## Does confidence identify better ranking periods?

- VAL_2020_2022: Q5 rank IC +0.036 vs Q1-4 +0.107; Q5 top3-EW8 +0.014% vs +0.170%; Q5 bottom2-veto-EW8 -0.014% vs +0.190%
- CONF_2023_2024: Q5 rank IC +0.143 vs Q1-4 -0.048; Q5 top3-EW8 -0.042% vs -0.051%; Q5 bottom2-veto-EW8 +0.055% vs -0.090%
- STRESS_2025: Q5 rank IC +0.000 vs Q1-4 +0.226; Q5 top3-EW8 +0.098% vs +0.298%; Q5 bottom2-veto-EW8 +0.051% vs +0.096%
- STRESS_2026: Q5 rank IC -0.071 vs Q1-4 +0.250; Q5 top3-EW8 +0.200% vs +0.201%; Q5 bottom2-veto-EW8 +0.160% vs +0.443%

## Confidence activation

- VAL_2020_2022: high-confidence dates 28.4%; mean continuous intensity 0.308; median combined confidence -0.015
- CONF_2023_2024: high-confidence dates 23.7%; mean continuous intensity 0.267; median combined confidence -0.072
- STRESS_2025: high-confidence dates 36.7%; mean continuous intensity 0.373; median combined confidence +0.219
- STRESS_2026: high-confidence dates 55.2%; mean continuous intensity 0.554; median combined confidence +0.739

## Economic results at 10 bps

- **PAIRWISE_SOFT** — gate=False; VAL ΔSharpe +0.050 (6/6), CONF -0.057 (0/6), 2025 +0.100, 2026 +0.020; median annualized turnover VAL/CONF 1.24/1.35
- **PAIRWISE_TOP3** — gate=False; VAL ΔSharpe -0.130 (1/6), CONF -0.670 (0/6), 2025 +0.480, 2026 -1.232; median annualized turnover VAL/CONF 16.35/17.49
- **PAIRWISE_BOTTOM2_VETO** — gate=False; VAL ΔSharpe +0.375 (6/6), CONF -0.501 (0/6), 2025 +0.271, 2026 +0.156; median annualized turnover VAL/CONF 5.51/7.27
- **CONF_SOFT** — gate=False; VAL ΔSharpe -0.042 (1/6), CONF -0.016 (1/6), 2025 +0.024, 2026 -0.058; median annualized turnover VAL/CONF 0.74/0.67
- **CONF_HALF_TOP3** — gate=False; VAL ΔSharpe -0.171 (1/6), CONF -0.195 (0/6), 2025 -0.014, 2026 -0.639; median annualized turnover VAL/CONF 4.10/3.70
- **CONT_HALF_TOP3** — gate=False; VAL ΔSharpe -0.126 (1/6), CONF -0.216 (0/6), 2025 +0.110, 2026 -0.568; median annualized turnover VAL/CONF 4.23/4.33
- **CONF_BOTTOM2_VETO** — gate=False; VAL ΔSharpe -0.256 (1/6), CONF +0.011 (4/6), 2025 +0.005, 2026 -0.305; median annualized turnover VAL/CONF 2.95/2.86

## Interpretation

The frozen pairwise model's internal confidence geometry does not reliably separate good ranking periods from bad ones, and abstention does not rescue the economic selection problem. Do not tune thresholds or add confidence features on the same sample.