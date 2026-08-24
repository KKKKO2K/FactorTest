# Non-stationary Factor Selection — Research Status

## Purpose

This track directly tested factor selection/weighting using the same canonical 8-factor × 6-universe 5D payoff panel, without requiring a stable Factor Regime or a stable forward-return regression.

Methods tested:
1. Online learning / regret minimization
2. Change-point-adaptive selection
3. Bayesian latent factor quality
4. Pairwise learning-to-rank
5. Diversity-aware subset selection
6. Post-hoc exploratory negative selection using the pairwise rank signal

Primary economic gate: at 10 bps per unit factor-weight turnover, median ΔSharpe vs EW8 > 0 and at least 4/6 universes improved in both 2020–22 and 2023–24. 2025/2026 are stress diagnostics only.

## Bottom line

**No method passes the pre-registered 2020–24 cross-universe gate.**

The negative result is stronger than the prior Factor-Regime failures because the selection problem was attacked under several genuinely different decision frameworks rather than through alternative state labels.

However one sub-result remains scientifically interesting: the frozen Discovery-trained pairwise ranking model has positive cross-sectional rank IC in every later era, while concentrated selection based on that ranking still fails economically. This suggests that weak relative-ranking information may exist, but is too small or unstable to justify aggressive factor concentration.

---

## Stage A — Online learning / regret minimization

### ADAPTIVE_HEDGE
10 bps median ΔSharpe vs EW8:
- 2020–22: +0.800, 5/6 universes
- 2023–24: -0.171, 2/6
- 2025: +1.606, 6/6
- 2026: -2.581, 0/6

### FTRL
- 2020–22: +0.804, 5/6
- 2023–24: -0.201, 2/6
- 2025: +1.581, 6/6
- 2026: -2.857, 0/6

Interpretation:

> Full-information adaptive weighting can exploit prolonged factor trends, but the advantage is highly non-stationary. The same low-turnover adaptive machinery that worked strongly in 2020–22 and 2025 became harmful in 2023–24 and especially 2026.

This is not mainly a transaction-cost problem: annualized factor-weight turnover was low relative to hard TOP2 switching.

---

## Stage B — Change-point adaptive factor momentum

### CP_TOP2
- 2020–22: +0.180, 4/6
- 2023–24: -0.326, 1/6
- 2025: +0.988, 5/6
- 2026: -2.189, 0/6

### CP_SOFTMAX
- 2020–22: +0.409, 5/6
- 2023–24: -0.299, 0/6
- 2025: +0.939, 5/6
- 2026: -1.982, 0/6

89 change points were detected across the six universe definitions under the frozen Discovery-calibrated threshold.

Interpretation:

> Allowing the lookback to reset after detected breaks does not solve the factor-selection problem. It reproduces the same era dependence seen in online trend-following.

Do not tune the change-point threshold after seeing these results.

---

## Stage C — Bayesian latent factor quality

### LATENT_PROB
- 2020–22: -0.687, 0/6
- 2023–24: -0.739, 0/6

### LATENT_TOP3
- 2020–22: -0.736, 0/6
- 2023–24: -0.972, 0/6

Interpretation:

> Treating six universe payoffs as noisy measurements of a latent factor alpha does not create useful selection information. Cross-universe synchronization is mostly contemporaneous information, not a stable forecast of next-period factor quality.

This is the cleanest rejection in the track.

---

## Stage D — Pairwise learning-to-rank

The Discovery-only pooled pairwise logit learns the following directional structure:
- current 5D difference: negative coefficient (-0.120)
- trailing 20D difference: positive (+0.185)
- trailing 60D difference: small positive (+0.035)
- trailing 20D volatility difference: negative (-0.062)
- current cross-sectional rank difference: positive (+0.132)

Thus the fitted relation combines very-short-term reversal with medium-horizon relative momentum and a mild low-vol preference.

### Predictive ranking diagnostic
Median rank IC of the frozen tournament score against realized factor payoff:
- 2020–22: +0.107
- 2023–24: +0.048
- 2025: +0.238
- 2026: +0.143

This is positive in every later era.

### Economic implementation

PAIRWISE_SOFT:
- 2020–22: +0.050 ΔSharpe, 6/6 universes
- 2023–24: -0.057, 0/6
- 2025: +0.100, 5/6
- 2026: +0.020, 4/6

PAIRWISE_TOP3:
- 2020–22: -0.130, 1/6
- 2023–24: -0.670, 0/6

Interpretation:

> Relative ranking is the only method in this track showing a directionally stable predictive diagnostic, but the signal is weak. Soft weighting remains close to EW8; concentrated TOP3 selection destroys the benefit.

This is a **weak research lead**, not a validated selection strategy.

---

## Stage E — Diversity-aware selection

### DPP_LATENT3
- 2020–22: -0.699, 0/6
- 2023–24: -0.895, 0/6

### DPP_PAIRWISE3
- 2020–22: -0.195, 1/6
- 2023–24: -0.277, 2/6

DPP_PAIRWISE3 reduced selected average pair correlation versus quality-only pairwise TOP3 by a median -0.192, so the diversification mechanism itself worked mechanically.

But lower redundancy did not overcome weak selection alpha.

Interpretation:

> Better subset diversification can improve a bad concentrated selector, but cannot manufacture alpha when quality ranking is too weak.

---

## Stage F — Pairwise bottom-two veto (post-hoc exploratory)

Because pairwise rank IC was positive in every era while TOP3 concentration failed, one additional **post-hoc** test asked whether the signal works better for negative selection than winner selection.

PAIRWISE_BOTTOM2_VETO, equal weight the remaining six factors:
- 2020–22: +0.375 ΔSharpe, 6/6
- 2023–24: -0.501, 0/6
- 2025: +0.271, 4/6
- 2026: +0.156, 4/6

This is not confirmatory because the test was designed after seeing Stage D.

Interpretation:

> Bad-factor avoidance can be useful in some eras, but the 2023–24 failure shows that the stable positive rank IC is not large enough to support a robust veto rule either.

---

# Cross-method interpretation

The most striking common pattern is not method-specific:

- 2020–22: adaptive / relative-selection methods often improve materially on EW8.
- 2023–24: essentially every active selection rule is worse than EW8.
- 2025: many adaptive methods work again.
- 2026: trend-following online and change-point methods break badly, while the mild pairwise-soft signal remains near EW8.

This implies that **the economic value of active factor selection is itself time-varying**, even when the underlying ranking signal remains weakly positive.

The current evidence therefore favors a hierarchy:

1. **EW8 is a very strong default.**
2. Hard/concentrated positive selection is consistently fragile.
3. Low-amplitude relative ranking is the least fragile active method, but still fails the confirmation gate.
4. Diversification helps implementation but does not rescue weak alpha.
5. Online adaptation and change-point resets can amplify whichever factor trend environment happens to prevail; they do not create robustness.

# What remains worth testing

Using the same return-only data, the one defensible selection question still open is **confidence/abstention**, not another ranking formula:

> Can the system identify when the pairwise ranking signal is strong enough to deviate from EW8, while otherwise abstaining and staying diversified?

That would use the already-frozen pairwise model and test an economically different action rule: `EW8 unless ranking confidence is unusually high`.

Because the current results have already been inspected, any such test must be explicitly labeled exploratory unless a future untouched sample is available.
