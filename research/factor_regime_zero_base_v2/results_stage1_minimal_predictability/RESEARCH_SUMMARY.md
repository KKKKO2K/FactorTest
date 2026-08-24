# Stage 1 — Minimal Predictability Test

Targets and predictor sets were pre-registered in STAGE1_TARGETS.md before this run.
Discovery 2016–19 is used only for sign and frozen terciles; PASS requires independent 2020–22 validation and 2023–24 confirmation.
2025/2026 are stress slices and cannot create a PASS.

## Opportunity target: 3 PASS of 9 predictors

- range20: PASS=True; VAL IC +0.234 (6/6); CONF IC +0.133 (6/6); VAL H-L +0.81%; CONF H-L +0.59%; 2025 IC -0.066; 2026 IC -0.187
- dispersion20: PASS=True; VAL IC +0.237 (6/6); CONF IC +0.121 (6/6); VAL H-L +0.96%; CONF H-L +0.35%; 2025 IC -0.066; 2026 IC -0.233
- abs_opportunity20: PASS=True; VAL IC +0.180 (5/6); CONF IC +0.086 (6/6); VAL H-L +0.79%; CONF H-L +0.36%; 2025 IC -0.179; 2026 IC -0.169
- pc1_share_60: PASS=False; VAL IC +0.154 (4/6); CONF IC +0.075 (3/6); VAL H-L -0.14%; CONF H-L +0.14%; 2025 IC -0.006; 2026 IC -0.215
- leader_abs_share20: PASS=False; VAL IC +0.005 (3/6); CONF IC +0.012 (4/6); VAL H-L -0.06%; CONF H-L +0.15%; 2025 IC -0.021; 2026 IC +0.174
- current_cross_universe_coherence: PASS=False; VAL IC +0.018 (4/6); CONF IC -0.066 (3/6); VAL H-L +0.04%; CONF H-L -0.19%; 2025 IC -0.050; 2026 IC +0.076
- breadth20: PASS=False; VAL IC +0.086 (5/6); CONF IC -0.074 (2/6); VAL H-L +0.28%; CONF H-L +0.16%; 2025 IC +0.156; 2026 IC -0.097
- rank_agreement_20_60: PASS=False; VAL IC -0.049 (1/6); CONF IC -0.101 (1/6); VAL H-L -0.15%; CONF H-L -0.38%; 2025 IC +0.035; 2026 IC +0.419
- avg_pair_corr_60: PASS=False; VAL IC +0.359 (6/6); CONF IC -0.146 (0/6); VAL H-L +1.67%; CONF H-L -0.77%; 2025 IC +0.154; 2026 IC -0.122

## Coherence target: 0 PASS of 6 predictors

- median_dispersion20: PASS=False; VAL IC +0.110; CONF IC +0.070; VAL H-L +0.021; CONF H-L -0.055; 2025 IC -0.113; 2026 IC -0.152
- median_abs_opportunity20: PASS=False; VAL IC +0.108; CONF IC +0.033; VAL H-L +0.053; CONF H-L -0.029; 2025 IC -0.375; 2026 IC -0.175
- current_cross_universe_coherence: PASS=False; VAL IC +0.014; CONF IC -0.054; VAL H-L +0.001; CONF H-L -0.079; 2025 IC +0.076; 2026 IC +0.271
- median_avg_pair_corr_60: PASS=False; VAL IC +0.283; CONF IC -0.119; VAL H-L +0.100; CONF H-L -0.124; 2025 IC +0.174; 2026 IC +0.033
- median_rank_agreement_20_60: PASS=False; VAL IC +0.084; CONF IC -0.260; VAL H-L +0.054; CONF H-L -0.200; 2025 IC +0.101; 2026 IC +0.594
- median_pc1_share_60: PASS=False; VAL IC +0.166; CONF IC -0.355; VAL H-L +0.025; CONF H-L -0.199; 2025 IC -0.429; 2026 IC -0.171

## Interpretation discipline

- No composite or portfolio rule is tested here.
- Only PASS predictors are eligible for Stage 2 falsification tests.
- If a target has no PASS predictor, stop that target rather than broadening the feature set.