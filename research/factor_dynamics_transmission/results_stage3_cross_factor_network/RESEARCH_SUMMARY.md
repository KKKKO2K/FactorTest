# Stage 3 — Cross-Factor Directed Transmission Network

Primary tape uses only K200, KOSPI ex-K200, and KOSDAQ common factor returns.
All 56 directed edges were pre-registered before this run.

- PASS edges: 0/56
- DIRECTIONAL PASS edges: 0/56


## Two-edge paths

- None

## Strongest near-misses

- PBR12MF -> MOM1M: VAL +0.0091, CONF +0.0194, sign_stable=True, placebo p=0.141/0.093
- OP12_REV -> MOM1M: VAL -0.0288, CONF +0.0175, sign_stable=True, placebo p=0.638/0.041
- OP12_REV -> MOM12_1: VAL +0.0091, CONF +0.0159, sign_stable=True, placebo p=0.007/0.134
- OPFY1_REV -> MOM1M: VAL -0.0195, CONF +0.0142, sign_stable=True, placebo p=0.591/0.052
- MOM1M -> MOM12_1: VAL -0.0238, CONF +0.0127, sign_stable=True, placebo p=0.779/0.206
- MOM12_1 -> PBR12MF: VAL -0.0313, CONF +0.0127, sign_stable=True, placebo p=0.624/0.165
- MOM1M -> PRIVATE_FLOW: VAL -0.0111, CONF +0.0127, sign_stable=True, placebo p=0.658/0.031
- PBR12MF -> FOREIGN_FLOW: VAL +0.0119, CONF +0.0125, sign_stable=False, placebo p=0.047/0.124
- MOM12_1 -> PER12MF: VAL -0.0104, CONF +0.0108, sign_stable=False, placebo p=0.671/0.320
- MOM1M -> PBR12MF: VAL -0.0606, CONF +0.0106, sign_stable=True, placebo p=0.852/0.155

## Decision

No simple cross-factor lead/lag edge survives. Reject the directed-network hypothesis at 5D and move to pairwise factor relative-value dynamics, a different estimand based on spread behavior rather than directional forecasting.