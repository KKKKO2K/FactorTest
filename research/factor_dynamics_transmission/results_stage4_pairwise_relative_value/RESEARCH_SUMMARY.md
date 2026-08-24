# Stage 4 — Pairwise Factor Relative-Value Dynamics

- PASS pair/specs: 0/56

No pair/spec survives the full validation + confirmation + sign-stability + placebo gate.

## Strongest near-misses

- OPFY1_REV vs FOREIGN_FLOW / TRAIL20: CONTINUATION; VAL -0.0191; CONF +0.0537; stable=True; p=0.568/0.447
- MOM1M vs PRIVATE_FLOW / TRAIL20: CONTINUATION; VAL -0.0653; CONF +0.0500; stable=False; p=0.795/0.266
- MOM1M vs MOM12_1 / TRAIL20: REVERSAL; VAL -0.0487; CONF +0.0413; stable=True; p=0.849/0.032
- MOM1M vs PRIVATE_FLOW / DISLOCATION: ACCELERATION; VAL -0.0389; CONF +0.0287; stable=True; p=0.493/0.277
- PER12MF vs PRIVATE_FLOW / TRAIL20: REVERSAL; VAL -0.1672; CONF +0.0127; stable=True; p=0.897/0.277
- MOM12_1 vs OP12_REV / TRAIL20: CONTINUATION; VAL +0.0301; CONF +0.0125; stable=False; p=0.075/0.926
- MOM1M vs OPFY1_REV / DISLOCATION: MEAN_REVERSION; VAL -0.0200; CONF +0.0112; stable=False; p=0.507/0.191
- OP12_REV vs FOREIGN_FLOW / TRAIL20: CONTINUATION; VAL +0.0048; CONF +0.0111; stable=False; p=0.247/0.745
- PBR12MF vs PRIVATE_FLOW / TRAIL20: REVERSAL; VAL -0.0526; CONF +0.0088; stable=True; p=0.774/0.266
- OP12_REV vs PER12MF / TRAIL20: REVERSAL; VAL -0.0580; CONF +0.0081; stable=True; p=0.945/0.309
- PBR12MF vs PRIVATE_FLOW / DISLOCATION: MEAN_REVERSION; VAL -0.0127; CONF +0.0058; stable=False; p=0.678/0.394
- PER12MF vs FOREIGN_FLOW / TRAIL20: REVERSAL; VAL -0.1014; CONF +0.0027; stable=False; p=0.870/0.362

## Decision

Simple linear pairwise continuation/dislocation dynamics do not survive. Stop linear lag engineering and reserve the next stage for explicitly exploratory nonlinear/rotation geometry rather than adding more ad hoc windows.