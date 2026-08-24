# Non-stationary Factor Selection — Research Results

All methods were pre-specified in `RESEARCH_ROADMAP.md` before this run.
Primary economic gate uses 10 bps cost per unit factor-weight turnover.
2025/2026 are stress diagnostics only.

## Stage A — Online learning

- **ADAPTIVE_HEDGE** — PASS=False; VAL ΔSharpe +0.800 (5/6), CONF -0.171 (2/6); 2025 +1.606; 2026 -2.581
- **FTRL** — PASS=False; VAL ΔSharpe +0.804 (5/6), CONF -0.201 (2/6); 2025 +1.581; 2026 -2.857

## Stage B — Change-point adaptive

- **CP_TOP2** — PASS=False; VAL ΔSharpe +0.180 (4/6), CONF -0.326 (1/6); 2025 +0.988; 2026 -2.189
- **CP_SOFTMAX** — PASS=False; VAL ΔSharpe +0.409 (5/6), CONF -0.299 (0/6); 2025 +0.939; 2026 -1.982

## Stage C — Latent factor quality

- **LATENT_PROB** — PASS=False; VAL ΔSharpe -0.687 (0/6), CONF -0.739 (0/6); 2025 +0.329; 2026 -0.539
- **LATENT_TOP3** — PASS=False; VAL ΔSharpe -0.736 (0/6), CONF -0.972 (0/6); 2025 -0.519; 2026 -0.853

## Stage D — Pairwise ranking

- **PAIRWISE_SOFT** — PASS=False; VAL ΔSharpe +0.050 (6/6), CONF -0.057 (0/6); 2025 +0.100; 2026 +0.020
- **PAIRWISE_TOP3** — PASS=False; VAL ΔSharpe -0.130 (1/6), CONF -0.670 (0/6); 2025 +0.480; 2026 -1.232

## Stage E — Diversity-aware selection

- **DPP_LATENT3** — PASS=False; VAL ΔSharpe -0.699 (0/6), CONF -0.895 (0/6); 2025 -0.333; 2026 -0.721
- **DPP_PAIRWISE3** — PASS=False; VAL ΔSharpe -0.195 (1/6), CONF -0.277 (2/6); 2025 +0.071; 2026 -0.562

## Stage E incremental attribution

- DPP_LATENT3 vs LATENT_TOP3, VAL_2020_2022: median Sharpe attribution +0.036
- DPP_LATENT3 vs LATENT_TOP3, CONF_2023_2024: median Sharpe attribution +0.077
- DPP_LATENT3 vs LATENT_TOP3, STRESS_2025: median Sharpe attribution +0.186
- DPP_LATENT3 vs LATENT_TOP3, STRESS_2026: median Sharpe attribution +0.133
- DPP_PAIRWISE3 vs PAIRWISE_TOP3, VAL_2020_2022: median Sharpe attribution -0.066
- DPP_PAIRWISE3 vs PAIRWISE_TOP3, CONF_2023_2024: median Sharpe attribution +0.393
- DPP_PAIRWISE3 vs PAIRWISE_TOP3, STRESS_2025: median Sharpe attribution -0.408
- DPP_PAIRWISE3 vs PAIRWISE_TOP3, STRESS_2026: median Sharpe attribution +0.670

## Change-point diagnostics

- Total detected change points: 89; median per universe 10.5

## Diversity diagnostics

- DPP_LATENT3 minus quality-only top3 median selected pair correlation: +0.000
- DPP_PAIRWISE3 minus quality-only top3 median selected pair correlation: -0.192

## Bottom line

No dynamic factor-selection method passes the pre-registered 2020–24 cross-universe gate.
This would be a strong negative result because the return-only panel has then failed under online, adaptive-window, latent-quality, pairwise-ranking, and diversity-aware selection frameworks.