# Stage 3 Protocol — Cross-Factor Directed Transmission Network

Stage 1/2 found only weak and unstable same-factor cross-universe propagation. Stage 3 asks a genuinely different question:

> Does movement in one **factor family** lead movement in another factor family?

Examples of the mechanism under test include `FLOW -> REVISION -> MOMENTUM`, but no such chain is assumed ex ante.

## Clean common factor tape

Use only the three mutually disjoint primitive universes:
- K200
- KOSPI_EX_K200
- KOSDAQ

For each factor × universe series, normalize using 2016–19 mean/std only.

For each factor/date define the primitive-universe common tape:

`F[t,f] = mean(z[t,f,K200], z[t,f,KOSPI_EX_K200], z[t,f,KOSDAQ])`

Composite universes are excluded from the primary network.

## Directed edge test

For every ordered pair of distinct factors `A -> B` (56 edges), fit on Discovery 2016–19:

Baseline:

`B[t+1] ~ 1 + B[t]`

Augmented:

`B[t+1] ~ 1 + B[t] + A[t]`

Evaluate frozen models in:
- Validation 2020–22
- Confirmation 2023–24
- Stress 2025
- Stress 2026

Primary metric:

`incremental_OOS_R2 = 1 - MSE_aug / MSE_base`

## Discovery sign stability

For each edge separately estimate the source coefficient in:
- 2016–17
- 2018–19

The sign must agree across the two discovery halves for an edge to qualify as stable.

## Time-shift placebo

For each edge and evaluation era, keep frozen Discovery coefficients but circularly shift the source-factor sequence by every feasible non-zero offset.

The observed temporal alignment passes if its incremental OOS R² is better than at least 90% of shifted alignments (`p <= 0.10`).

## Primary PASS gate

A cross-factor edge passes only if:
1. incremental OOS R² > 0 in both Validation and Confirmation;
2. Discovery source-coefficient sign is stable across 2016–17 and 2018–19;
3. time-shift placebo p <= 0.10 in both Validation and Confirmation.

2025/26 cannot create a PASS.

## Directionality

For every `A -> B`, compare with `B -> A`.

A passing edge is labelled `DIRECTIONAL` only if its incremental OOS R² exceeds the reverse edge in both Validation and Confirmation.

Otherwise it is labelled `BIDIRECTIONAL/PAIR-DYNAMIC`.

## Multiple-testing discipline

There are 56 candidate directed edges. Do not report a long list of marginal edges.

Headline results are:
- number of PASS edges;
- number of DIRECTIONAL PASS edges;
- any connected path of at least two passing directed edges (e.g. A -> B -> C);
- source/destination factor families that repeatedly appear in passing edges.

The combined two-era placebo requirement plus discovery sign stability is the pre-registered false-discovery control for this exploratory network stage. No threshold is relaxed after results.

## Next step

- If directed edges survive: run Stage 3B horizon / impulse-response falsification on those exact edges only.
- If no robust edges survive: reject simple cross-factor lead/lag and move to Stage 4 pairwise relative-value dynamics, which asks whether factor **spreads** have stable mean-reversion/trend behavior even when individual factor directions do not.

No portfolio backtest is permitted in Stage 3.
