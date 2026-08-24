# Factor Dynamics / Transmission — Research Roadmap

## Why this research exists

This track deliberately abandons the idea that the 8-factor payoff panel must be compressed into a discrete `Factor Regime`.

The object of study is the full dynamic panel

`R[t, factor, universe]`

with 8 canonical factors observed across 6 universe definitions through time.

The central question is no longer **what state are we in?**. It is:

> **How does factor information move, diffuse, separate, converge, and rotate across universes and across factors?**

Prior Factor-Regime work is archive/context only. No B/F states, F_HIGH/F_LOW labels, KMeans/HMM states, survivor feature lists, opportunity thresholds, or prior portfolio rules are inputs to this track.

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

The 5D factor long-short payoff is the primitive observation. New transformations are allowed only when they answer a different economic question, not to rescue a failed state classifier.

---

# Research sequence

## Stage 1 — Common / Local Decomposition + Same-Factor Cross-Universe Propagation

### Question 1A — Common vs local shocks
For each factor and date, decompose the six universe returns into:

`factor_common[t,f] = mean_u R[t,f,u]`

`factor_local[t,f,u] = R[t,f,u] - factor_common[t,f]`

Then ask separately:
- Does the common shock continue or mean-revert?
- Does a local residual shock persist, mean-revert, or diffuse into other universes?

This is different from winner persistence because it distinguishes **system-wide factor information** from **universe-specific deviation**.

### Question 1B — Directed cross-universe propagation
For every factor and ordered universe pair `A -> B`, test whether A's current 5D factor payoff predicts B's next 5D payoff **after controlling for B's own current payoff**.

Discovery model:

`B[t+1] ~ 1 + B[t]`  (baseline)

vs

`B[t+1] ~ 1 + B[t] + A[t]`  (propagation model)

Coefficients and standardization are frozen from 2016–2019. The augmented model must improve genuinely forward prediction in 2020–22 and 2023–24 to support an edge.

Primary object is not 240 individual p-values. It is the **30 directed universe edges aggregated across all 8 factors**.

A directed universe edge is eligible only if, in both 2020–22 and 2023–24:
- median incremental OOS R² across the 8 factors is positive; and
- at least 5/8 factors have positive incremental OOS R².

2025 and 2026 are stress/structural-break diagnostics and cannot create a PASS.

### Outputs
- common-shock continuation table;
- local-residual continuation/mean-reversion table;
- 30-edge universe propagation matrix;
- factor-by-edge incremental OOS R² table;
- leader/follower summary by universe;
- reverse-edge comparison to distinguish real directionality from symmetric co-movement.

No portfolio backtest is allowed in Stage 1.

---

## Stage 2 — Cross-Factor Directed Network

Only if Stage 1 shows that temporal transmission exists somewhere.

Collapse the six universes into a robust common factor tape and test whether one factor predicts another after the destination factor's own history is controlled.

Candidate methods, in order:
1. pairwise destination-controlled lead/lag;
2. ridge VAR;
3. sparse VAR / elastic-net network only if sample size supports it.

Key questions:
- Does FLOW lead REVISION?
- Does REVISION lead MOMENTUM?
- Does VALUE lead or lag risk-on factor families?
- Are any edges stable across eras rather than being one-cycle artifacts?

Output is a directed factor transmission graph, not a regime label.

---

## Stage 3 — Pairwise Factor Relative-Value Dynamics

Study all 28 factor pairs directly.

For factor spread `S[f1,f2] = F[f1] - F[f2]`, test:
- relative momentum;
- mean reversion;
- horizon dependence;
- asymmetric behavior after large positive vs negative spread shocks.

This can succeed even when absolute factor winner persistence is near chance.

---

## Stage 4 — Shock → Response / Impulse Map

Define large shocks using discovery-period scale only, then perform event studies.

Separate:
- common factor shocks;
- universe-local residual shocks;
- cross-factor shocks.

Map response at +5D / +10D / +20D / +40D.

The goal is to identify repeatable sequences such as:

`Foreign Flow shock -> Revision response -> Momentum response`

or

`KOSDAQ local factor shock -> KOSPI ex-K200 -> K200`

No threshold is promoted to a trading rule without a separate holdout test.

---

## Stage 5 — Dynamic Modes / Rotation Geometry (Exploratory)

Only after the simpler directed tests.

Treat the 8-dimensional common factor vector as a dynamic system and look for repeated modes using:
- Dynamic Mode Decomposition;
- spectral / frequency decomposition;
- singular-spectrum analysis.

Question:

> Is factor leadership better described as a recurring rotation/oscillation than as a persistent state?

This stage is exploratory by design and cannot override negative results from simpler tests.

---

# Research discipline

## Time splits
- Discovery: 2016–2019
- Validation: 2020–2022
- Confirmation: 2023–2024
- Stress/read-through: 2025
- Stress/read-through: 2026 YTD

Because later periods have already been inspected in prior research, none of these should be described as pristine untouched OOS. The split is used to control tuning and sign selection.

## Anti-data-mining rules
- Pre-register each stage's estimand and aggregation rule before running it.
- Do not optimize thresholds on 2025/26.
- Do not promote an isolated factor/universe pair as a main result.
- Prefer grouped replication across factors, universes, and eras.
- Compare every directional relationship with its reverse edge.
- If a relationship vanishes after controlling for destination own-lag, treat it as contemporaneous co-movement, not propagation.
- No portfolio construction until a predictive dynamic survives its dedicated falsification stage.

# Current priority

**Run Stage 1 first.**

The strongest prior descriptive fact was strong contemporaneous agreement of factor rankings across universe definitions. Stage 1 asks the new question that prior regime work did not answer:

> **Is that common factor tape generated simultaneously, or does factor information systematically propagate from some universe definitions into others?**
