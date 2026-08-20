# Participation Divergence Screen — Mixed OPFY1+CF20

- Stage 2 is explicitly post-discovery: Stage 1 showed 2025 vs 2026 separation in stock-level participation/dispersion/concentration, so these results are hypothesis refinement rather than pristine OOS.
- The composite is still mechanically defined: four pre-specified participation-quality features, equal weights, TRAIN-HIGH empirical-CDF scaling only; no return-fitted weights.
- Stress acceleration is the four-state change in that equal-weight risk score. Adverse-change count is the number of the four components deteriorating versus four state observations earlier.
- FACTOR_UNIVERSE_BREADTH_DIVERGENCE is FACTOR_20D breadth minus Mixed-universe trailing-20D positive-stock breadth.
- All cutoffs are 2016-22 HIGH-state 2/3 quantiles and are frozen for later periods.

## Screen results

- FACTOR_UNIVERSE_BREADTH_DIVERGENCE cutoff=0.4023: early d=+0.68%, late d=-0.32%, OOS d=-0.11%, 2025 flag=9%, 2026 negative capture=50%, 2026 bad mean=-8.15%; PASS=False
- PARTICIPATION_STRESS_LEVEL cutoff=0.6038: early d=+2.20%, late d=-0.52%, OOS d=-1.55%, 2025 flag=27%, 2026 negative capture=50%, 2026 bad mean=-7.75%; PASS=False
- ADVERSE_CHANGE_COUNT_4STATE cutoff=3.0000: early d=+1.07%, late d=-3.75%, OOS d=-2.26%, 2025 flag=32%, 2026 negative capture=42%, 2026 bad mean=-5.22%; PASS=False
- PARTICIPATION_STRESS_ACCEL_4STATE cutoff=0.2485: early d=-0.12%, late d=-4.76%, OOS d=-2.99%, 2025 flag=14%, 2026 negative capture=33%, 2026 bad mean=-4.88%; PASS=False

## Passed features

- None.

## 2026 HIGH chronology

- 2026-02-11: FB=0.625; stress=0.265; accel=-0.421; adverse_count=1; divergence=-0.102; fwd20=+0.65%
- 2026-02-23: FB=0.625; stress=0.269; accel=-0.473; adverse_count=1; divergence=-0.094; fwd20=-3.93%
- 2026-03-03: FB=0.750; stress=0.501; accel=+0.210; adverse_count=3; divergence=+0.332; fwd20=-7.22%
- 2026-03-10: FB=0.875; stress=0.750; accel=+0.496; adverse_count=4; divergence=+0.603; fwd20=-6.69%
- 2026-03-17: FB=0.750; stress=0.618; accel=+0.353; adverse_count=3; divergence=+0.448; fwd20=+0.11%
- 2026-03-24: FB=0.750; stress=0.717; accel=+0.448; adverse_count=3; divergence=+0.507; fwd20=+8.35%
- 2026-04-14: FB=0.625; stress=0.305; accel=-0.313; adverse_count=0; divergence=+0.065; fwd20=+16.51%
- 2026-04-28: FB=0.625; stress=0.263; accel=-0.567; adverse_count=1; divergence=-0.212; fwd20=-11.06%
- 2026-05-07: FB=0.625; stress=0.262; accel=-0.531; adverse_count=1; divergence=-0.116; fwd20=-22.60%
- 2026-05-14: FB=0.750; stress=0.386; accel=+0.081; adverse_count=2; divergence=+0.362; fwd20=-12.74%
- 2026-05-21: FB=0.750; stress=0.578; accel=+0.142; adverse_count=1; divergence=+0.567; fwd20=-13.33%
- 2026-05-29: FB=0.750; stress=0.924; accel=+0.660; adverse_count=3; divergence=+0.644; fwd20=-9.82%
- 2026-06-08: FB=0.750; stress=0.900; accel=+0.638; adverse_count=3; divergence=+0.699; fwd20=-3.55%
- 2026-06-15: FB=0.750; stress=0.924; accel=+0.537; adverse_count=3; divergence=+0.665; fwd20=-17.68%
- 2026-06-29: FB=0.750; stress=0.933; accel=+0.009; adverse_count=2; divergence=+0.640; fwd20=-22.60%
- 2026-07-06: FB=0.750; stress=0.820; accel=-0.079; adverse_count=1; divergence=+0.374; fwd20=-10.08%
- 2026-07-13: FB=0.625; stress=0.960; accel=+0.036; adverse_count=3; divergence=+0.487; fwd20=NA
- 2026-07-21: FB=0.625; stress=0.868; accel=-0.099; adverse_count=0; divergence=+0.408; fwd20=NA
- 2026-07-28: FB=0.750; stress=0.820; accel=-0.112; adverse_count=0; divergence=+0.507; fwd20=NA

## Guardrails

- Because Stage 2 feature construction was motivated by the observed 2025/2026 contrast, a PASS here is candidate evidence, not final confirmation.
- Do not optimize weights, lag length, or cutoff after seeing this table. A passing specification should go directly to exact daily-NAV testing unchanged.