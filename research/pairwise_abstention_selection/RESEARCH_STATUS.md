# Pairwise Ranking + Abstention — Research Status

## Research question

The prior non-stationary factor-selection track found one unusual survivor: a Discovery-trained pairwise ranking model had positive factor-rank IC in every later era, but concentrated selection failed economically.

This follow-up asked:

> Can we identify when that ranking signal is trustworthy enough to justify deviating from EW8?

The research is post-hoc exploratory because prior 2020–24 pairwise results were already inspected before this track began.

---

# Stage 1 — Single-model probability confidence

Confidence was defined from the frozen pairwise model's own probability geometry:
- pairwise margin from 50/50;
- Borda score dispersion;
- top-score gap;
- cycle/transitivity consistency.

All standardization and hard/continuous thresholds used Discovery 2016–19 only.

## Result: REJECT

High internal probability confidence did **not** consistently imply better ranking accuracy.

Q5 versus Q1–4:
- 2020–22 rank IC: +0.036 vs +0.107
- 2023–24: +0.143 vs -0.048
- 2025: +0.000 vs +0.226
- 2026: -0.071 vs +0.250

Economic abstention rules all failed the primary-style 10bp gate.

Interpretation:

> A logistic model being far from 50/50 is model conviction, not validated reliability.

Do not tune probability-margin thresholds.

---

# Stage 2 — Bootstrap epistemic/model-stability confidence

Instead of asking whether one model is confident, Stage 2 asked whether **independently resampled Discovery histories produce the same ranking**.

Protocol:
- 100 moving-block bootstrap models;
- Discovery 2016–19 only;
- block length 8 five-day states (~40 trading days);
- fixed RNG seed 20260824;
- no new factor features;
- ensemble confidence from pair-vote agreement, top3-set agreement, top1 vote share, and low cross-model score dispersion;
- q80 and continuous intensity calibrated only from Discovery confidence distributions.

## Result: DIAGNOSTIC_ONLY

### Ranking-quality diagnostic

Epistemic high-confidence dates did identify materially better ranking quality in both historical evaluation eras.

Q5 versus Q1–4:

#### 2020–22
- rank IC: **+0.167 vs +0.095**
- top3 minus EW8 5D spread: **+0.269% vs +0.118%**
- bottom2-veto minus EW8: **+0.285% vs +0.117%**

#### 2023–24
- rank IC: **+0.071 vs -0.024**
- top3 minus EW8: **+0.298% vs -0.036%**
- bottom2-veto minus EW8: -0.183% vs -0.039%

Thus the most robust epistemic signal is **positive selection / top-factor ranking**, not bad-factor veto.

Stress behavior remains unstable:
- 2025 epistemic Q5 underperformed lower-confidence dates;
- 2026 epistemic Q5 was exceptionally strong (rank IC +0.536; top3-EW8 +1.461%).

### Signal frequency

Discovery-q80 high-confidence dates were rare:
- 2020–22: 8.1% of dates
- 2023–24: 12.4%
- 2025: 14.3%
- 2026: 13.8%

This rarity is economically important: a useful conditional ranking signal can have limited effect on whole-portfolio Sharpe when EW8 is held most of the time.

### Economic implementations at 10bp

#### `EPI_CONF_SOFT`
- 2020–22 ΔSharpe +0.022, 6/6 universes
- 2023–24 -0.004, 2/6

#### `EPI_CONF_HALF_TOP3`
- 2020–22 **-0.004**, 3/6
- 2023–24 **+0.025**, 4/6
- median ΔCAGR vs EW8: +0.38%p in 2020–22 and +0.59%p in 2023–24

This is the closest economic implementation to the gate, but it still fails because Validation median ΔSharpe is slightly negative and only 3/6 universes improve.

#### `EPI_CONT_HALF_TOP3`
- 2020–22 +0.007, 3/6
- 2023–24 -0.102, 0/6

#### `EPI_CONF_BOTTOM2_VETO`
- 2020–22 +0.077, 6/6
- 2023–24 -0.240, 0/6

No strategy passes the predeclared economic gate.

---

# What changed versus prior factor-selection conclusions

The evidence now supports a more precise hierarchy:

1. **Pairwise relative ranking contains weak but unusually persistent predictive information.**
2. **Single-model probability magnitude does not tell us when that ranking is trustworthy.**
3. **Discovery bootstrap/model agreement does identify historically higher-quality ranking dates.**
4. **Those dates are sparse, and the predeclared low-amplitude implementations do not robustly improve whole-portfolio Sharpe.**
5. Therefore the unresolved question is no longer simply `can factors be ranked?`; it is whether a sparse, conditional ranking edge is economically large enough to deserve an active sleeve.

This is meaningfully different from prior regime, persistence, opportunity, online-learning, and change-point failures.

---

# Current research interpretation

Best research lead from the return-only factor-selection work:

> **Epistemic-confidence-conditioned positive factor selection**

The most defensible candidate rule from this historical work is the already-frozen `EPI_CONF_HALF_TOP3` architecture:
- EW8 normally;
- only on Discovery-bootstrap high-confidence dates, tilt 50% of the way toward pairwise top3;
- q80 threshold and bootstrap design remain frozen.

It is **not production-validated** and did not pass the historical Sharpe gate. It is retained because:
- its underlying confidence diagnostic passed in both 2020–22 and 2023–24;
- median CAGR increment was positive in both eras;
- it avoids always-on concentration;
- it gives a precise frozen hypothesis for future untouched data.

## Research stop rule

Do not on this same sample:
- change q80 to q70/q90;
- change the 50% tilt cap;
- change bootstrap block length or number of models;
- add/remove confidence features;
- switch to full top3 only because Q5 spreads look attractive;
- optimize by 2025/2026.

Those would convert the current diagnostic discovery into sample tuning.

## Next legitimate validation

The next clean test should be on **new data not used in designing this track**, with the entire model and implementation frozen.

If new data confirm that bootstrap epistemic confidence separates ranking quality, the economic implementation can then be revisited using a new training/validation cycle.
