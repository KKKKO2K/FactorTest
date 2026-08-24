# Factor Dynamics / Transmission — Research Status

## Purpose

This track intentionally abandoned discrete Factor Regime classification and reused the same canonical 8-factor × 6-universe payoff panel to ask structurally different questions:

- Does factor information propagate across universes?
- Do common versus local shocks behave differently?
- Do factor families lead other factor families?
- Do factor-pair spreads have stable trend/reversal laws?
- Do similar historical factor configurations recur with similar future outcomes?

No B/F regime states, F_HIGH/F_LOW labels, KMeans/HMM states, prior survivor variables, or prior portfolio rules are inputs to this track.

---

## Stage 1 — Common/Local Decomposition + Same-Factor Cross-Universe Propagation

### Common/local geometry

After Discovery-only volatility normalization, the cross-universe common component explains a large share of factor-return variance:
- Discovery median common variance share: 0.683
- Validation 2020–22: 0.697
- Confirmation 2023–24: 0.733
- 2025: 0.686
- 2026: 0.679

But common factor shocks do not show stable next-5D continuation:
- 2020–22 median common next-5D IC: -0.007
- 2023–24: -0.069

Local residuals show only weak mean reversion:
- 2020–22 median local next-5D IC: -0.004
- 2023–24: -0.021

### Directed universe edges

5/30 ordered universe edges passed the initial factor-aggregated OOS gate; 3 were directionally stronger than their reverse edge.

The cleanest disjoint primitive-universe result was:

`KOSDAQ -> K200`

- 2020–22 median incremental OOS R²: +0.0026, 6/8 factors positive
- 2023–24: +0.0003, 5/8 factors positive
- reverse K200 -> KOSDAQ was negative in both eras

Because several other passing edges involved composite/overlapping universe definitions, Stage 2 restricted the mechanism test to the three disjoint primitives: K200, KOSPI_EX_K200, KOSDAQ.

---

## Stage 2 — KOSDAQ -> K200 Falsification

Classification: **WEAK_DIRECTIONAL**

After controlling for the contemporaneous KOSPI ex-K200 factor tape:

### NEXT5 unique KOSDAQ information
- 2020–22 median unique KOSDAQ R²: +0.0021; 5/8 factors positive
- 2023–24: +0.0019; 4/8 positive

Unique ex-K200 information was near zero, so KOSDAQ remained relatively more informative at the 5D horizon.

However the edge failed the pre-registered robustness gates:
- primary unique-control gate: FAIL because Confirmation had only 4/8 positive factors;
- discovery 2016–17 vs 2018–19 KOSDAQ coefficient sign matched for only 1/8 factors;
- placebo p: 0.054 in Validation but 0.124 in Confirmation;
- leave-one-factor-out Confirmation remained positive after only 4/8 omissions;
- GAP5 and longer horizons were mostly non-positive.

Interpretation:

> There is a small, unusually time-aligned KOSDAQ-leading trace, but not a stable cross-market transmission law.

Do not tune it into a trading rule.

---

## Stage 3 — Cross-Factor Directed Transmission Network

Question: can one factor family predict another factor family after the destination factor's own lag is controlled?

Primary tape used only the three disjoint primitive universes.

56 ordered factor edges were pre-registered.

Result:
- PASS edges: **0/56**
- DIRECTIONAL PASS edges: **0/56**
- two-edge transmission paths: none

Near-misses such as `PBR12MF -> MOM1M` or `OP12_REV -> MOM12_1` failed at least one of validation, confirmation, discovery sign stability, or time-shift placebo.

Conclusion:

> No stable 5D Flow -> Revision -> Momentum-style directed network is supported by the current return-only panel.

---

## Stage 4 — Pairwise Factor Relative-Value Dynamics

Question: even if individual factors are not predictable, do the 28 factor-pair spreads have pair-specific continuation or mean-reversion laws?

Two pre-registered specifications per pair:
1. trailing-20D relative momentum/reversal;
2. 20D-versus-60D relative dislocation/mean-reversion.

Total tests: 28 × 2 = 56.

Result:
- PASS pair/specs: **0/56**

No relation survived validation + confirmation + discovery sign stability + time-shift placebo.

Conclusion:

> Simple linear pair-specific relative-value dynamics are not stable enough to support a law-like allocation rule.

---

## Stage 5 — Recurrent Configurations / Analog Forecasting

This stage abandoned linear lag models.

Discovery 2016–19 was used as a fixed historical analog library with k=10 nearest neighbors.

Two pre-registered state representations:
- `SNAPSHOT`: current 8-factor cross-sectional configuration;
- `PATH20`: concatenated last-four 5D configurations.

Baselines:
- Discovery unconditional next-vector mean;
- simple persistence of the current relative factor vector.

### SNAPSHOT
Classification: **NO_RECURRENCE**

- 2020–22 median rank IC: analog +0.024 vs unconditional -0.095 vs persistence +0.024
- analog MSE 0.745 vs unconditional 0.703
- placebo p = 0.398
- 2023–24 rank IC: -0.071; analog MSE 0.713 vs unconditional 0.682; placebo p = 0.853

2026 was unusually strong (rank IC +0.274, placebo p=0.042), but stress-only success cannot create a PASS.

### PATH20
Classification: **NO_RECURRENCE**

- 2020–22 median rank IC -0.060; placebo p=0.838
- 2023–24 +0.024; placebo p=0.424
- analog MSE remained worse than unconditional in both eras

Conclusion:

> Similar-looking historical factor configurations do not reliably produce similar next-period factor outcomes.

---

# What the same return panel DOES contain

The strongest robust fact is **contemporaneous geometry**, not temporal forecastability.

1. Factor returns across universe definitions share a very large common component.
2. Factor rankings across universes are strongly synchronized.
3. There are short-lived traces of universe-to-universe timing asymmetry, especially KOSDAQ -> K200, but these are unstable under stricter falsification.
4. Neither simple directed factor networks, factor-pair laws, nor nearest-neighbor recurrence converts that geometry into stable forward prediction.

This explains why prior regime-style work repeatedly produced weak ICs or promising subperiods but unstable economic rules.

---

# Research directions still available using the SAME return data

These are deliberately different from the already-tested state/lag/analog approaches.

## A. Spectral / Dynamic-Mode Rotation Analysis

Question:

> Is the 8-factor vector governed by recurring oscillatory modes or phase rotations even though next-return prediction is weak?

Candidate methods:
- Dynamic Mode Decomposition (DMD)
- Singular Spectrum Analysis (SSA)
- frequency-domain coherence / phase lead-lag

The output would be rotation frequencies and phase relationships, not a HIGH/LOW state.

## B. Information-Theoretic Dependence

Question:

> Is there nonlinear directional dependence that linear OOS regressions miss?

Candidate methods:
- transfer entropy with strict permutation bias correction;
- conditional mutual information;
- symbolic-state transition information.

This should be treated as exploratory unless it survives temporal permutation tests and era replication.

## C. Forecast the GEOMETRY, not returns

The strongest observed structure is cross-factor/cross-universe covariance rather than factor mean returns.

Alternative target:
- future factor correlation matrix;
- future common-component strength;
- future diversification ratio / effective number of independent factor bets;
- covariance eigenvalue concentration.

This could have value for **factor risk budgeting** even if it cannot choose future winners.

## D. Change-point / Structural-Break Detection

Rather than forecasting the next factor return, identify whether the data-generating relationship itself has changed:
- covariance change points;
- coefficient sign instability;
- common-component loading changes;
- 2025/2026 structural-break diagnostics.

This is a monitoring/risk problem, not alpha forecasting.

---

# Current recommendation

Do **not** go back to more F_HIGH/F_LOW, KMeans, breadth/dispersion thresholds, pair-specific windows, or larger linear VARs.

If continuing with the same data, the most defensible next experiment is:

> **forecastability of factor covariance / diversification geometry**

because contemporaneous common structure is the one feature that survived every reframing.

If the goal remains alpha / factor winner selection rather than risk budgeting, genuinely new information will probably be required after the return-only experiments above.
