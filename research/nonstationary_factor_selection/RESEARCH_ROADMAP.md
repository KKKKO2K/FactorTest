# Non-stationary Factor Selection — Research Roadmap

## Purpose

This research track asks a different question from prior Factor Regime / Factor Dynamics work:

> Given the same 8 canonical factor payoff series, can factor **selection and weighting** be improved by solving the decision problem directly rather than forecasting a stable future-return law?

The track deliberately avoids discrete regimes, KMeans/HMM labels, hand-tuned HIGH/LOW thresholds, and post-hoc parameter sweeps.

## Canonical data

Source: `research/factor_regime_v1/results/factor_5d_returns.csv`

Factors:
- MOM1M
- MOM12_1
- OP12_REV
- OPFY1_REV
- PBR12MF
- PER12MF
- PRIVATE_FLOW
- FOREIGN_FLOW

Universes:
- K200
- KOSDAQ
- KOSPI_EX_K200
- KOSPI_ALL
- KOSPI_KOSDAQ_ALL
- KOSDAQ_PLUS_KOSPI_EX_K200

Each universe is evaluated separately; cross-universe information is used only by methods that explicitly require it.

## Chronological evaluation

- Discovery / calibration: 2016–2019
- Validation: 2020–2022
- Confirmation: 2023–2024
- Stress diagnostics: 2025 and 2026

2025/2026 cannot create a PASS.

Economic evaluation is based on 5D factor-portfolio returns and reports 0 / 10 / 30 bps cost per unit factor-weight turnover. The primary economic comparison uses 10 bps.

Primary gate for a candidate selector:
- median ΔSharpe versus EW8 > 0 in both 2020–22 and 2023–24;
- Sharpe improvement in at least 4/6 universes in both periods.

A method can still be scientifically interesting without passing this economic gate; failures are retained.

---

# Stage A — Online Learning / Regret Minimization

## Question

Can an adaptive full-information learner track changing factor quality without explicitly forecasting the next factor return?

## Pre-registered methods

### EW8 benchmark
Equal weight across all 8 factors.

### MOM20_TOP2 benchmark
At each decision date, equal weight the two factors with the strongest trailing four 5D returns. This is a simple winner-chasing benchmark, not a candidate research model.

### ADAPTIVE_HEDGE
Full-information multiplicative weights with no tuned fixed learning rate:
- factor update signal = discovery-vol-normalized current 5D return, clipped to [-1, 1];
- learning rate at update t: `eta_t = sqrt(2*log(8)/max(t,1))`;
- next-period weights are normalized exponentiated cumulative gains.

### FTRL
Entropy-regularized follow-the-regularized-leader using cumulative normalized factor returns:
- score = cumulative clipped discovery-vol-normalized return;
- temperature scales with `sqrt(t)`;
- no eta sweep.

All weights for date t are computed using information available through date t-1.

---

# Stage B — Change-point Adaptive Selection

## Question

Is fixed-window factor momentum failing because the relevant historical window changes through time?

## Detection

Use only past factor-return vectors. Calibrate a multivariate mean-change statistic on 2016–19 and freeze its threshold at the 95th percentile of discovery rolling-window statistics.

At each later date:
- inspect the current segment, capped at the latest 40 observations;
- require at least 12 observations with at least 6 observations on each side of a candidate split;
- choose the split that maximizes reduction in cross-factor SSE;
- if the statistic exceeds the frozen discovery threshold, reset the active history to the detected post-break segment.

No threshold sweep is allowed.

## Selection rules

### CP_TOP2
Equal weight the two factors with the strongest cumulative discovery-vol-normalized return since the most recent detected change point.

### CP_SOFTMAX
Softmax-weight the same since-change scores with temperature `sqrt(segment_length)`.

Compare with EW8 and fixed MOM20_TOP2.

---

# Stage C — Bayesian / Latent Factor Quality

## Question

Can the six universe payoffs be treated as noisy measurements of a latent time-varying quality for each factor?

## Model

For each factor:

`r[f,u,t] = alpha[f,t] + observation_noise[f,u,t]`

`alpha[f,t] = alpha[f,t-1] + state_noise[f,t]`

Use a one-dimensional Kalman filter per factor.

Parameters are estimated once from Discovery 2016–19:
- observation noise from cross-universe residual variance;
- state innovation variance from the time variation of the discovery cross-universe mean, net of estimated observation noise.

No parameter grid is searched.

At each t, update posterior using all six current universe observations, then use the posterior for t+1 selection.

## Selection rules

### LATENT_PROB
Convert posterior `mu/sigma` to `P(alpha > 0)` under a Gaussian approximation and normalize probabilities into long-only factor weights.

### LATENT_TOP3
Equal weight the three factors with highest posterior `P(alpha > 0)`.

These weights are global across universes; economic performance is evaluated separately in all six universes.

---

# Stage D — Pairwise Learning-to-Rank

## Question

Can relative ranking be learned more reliably than absolute factor return?

## Discovery-only model

Train one pooled pairwise logistic model on 2016–19 observations.

For every factor pair i,j at date t, predict whether factor i's next 5D cross-universe-common payoff exceeds factor j's.

Features are differences in primitive factor-state variables available at t:
- current 5D common payoff;
- trailing 20D common payoff;
- trailing 60D common payoff;
- trailing 20D common-payoff volatility;
- current cross-sectional rank.

The logistic coefficient vector is frozen after 2019. No model-class or regularization sweep.

## Selection rules

### PAIRWISE_SOFT
For each factor, sum its predicted win probabilities against the other seven factors; normalize positive tournament scores into weights.

### PAIRWISE_TOP3
Equal weight the three highest tournament-score factors.

---

# Stage E — Diversity-Aware Factor Selection

## Question

Even if quality estimates are noisy, does selecting a less redundant subset improve the factor-selection outcome?

This stage does not invent a new quality forecast. It takes Stage C and Stage D quality scores and asks whether portfolio construction adds value.

## Fixed subset size

Select exactly 3 of 8 factors. No k sweep.

## Rolling similarity

For each universe, estimate the 8×8 factor correlation matrix from the trailing 12 observations (~60D), using only information available before the holding period.

## Determinantal subset rule

For each 3-factor subset S, maximize:

`det( diag(q_S) * (Corr_S + 0.05 I) * diag(q_S) )`

where q is a positive quality score:
- `DPP_LATENT3`: Stage C posterior-positive probabilities;
- `DPP_PAIRWISE3`: Stage D tournament scores rescaled positive.

The 0.05 ridge is fixed ex ante for numerical stability; it is not tuned.

Compare directly with:
- LATENT_TOP3;
- PAIRWISE_TOP3;
- EW8.

---

# Research discipline

1. No method is promoted on a single universe.
2. 2025/2026 are stress slices only.
3. No post-hoc parameter or subset-size sweep after seeing results.
4. Failure of one method does not justify silently changing its objective.
5. Stage E is incremental portfolio-construction attribution, not a new alpha model.
6. If all five approaches fail, the conclusion is stronger than a failed regime classifier: the current return-only panel does not support robust dynamic factor selection under several distinct decision frameworks.
