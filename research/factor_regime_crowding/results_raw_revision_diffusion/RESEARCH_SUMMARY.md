# Raw Revision Diffusion Screen — Mixed OPFY1+CF20

- This is the final early-warning screen using the factor input itself rather than realized factor returns or later stock participation.
- Raw OPFY1/OP12 FactorValue is read at the signal close. Positive breadth means the share of Mixed stocks with positive revision; selected metrics use the actual OPFY1+CF20 top20 from the precomputed holdings audit.
- Adverse direction is pre-specified: narrow/weaker revision diffusion or deterioration versus four state observations earlier is bad.
- Cutoffs are TRAIN 2016-22 HIGH-state terciles only and frozen later. Same strict split/OOS/2025-control/2026-capture gate is used.

## Screen results

- OPFY1_MEDIAN_RAW cutoff=0.0000: early d=+1.23%, late d=+0.11%, OOS d=-7.20%, 2025 flag=100%, 2026 negative capture=100%, 2026 bad mean=-7.23%; PASS=False
- SELECTED_OPFY1_POS_SHARE cutoff=1.0000: early d=NA, late d=NA, OOS d=NA, 2025 flag=100%, 2026 negative capture=100%, 2026 bad mean=-7.23%; PASS=False
- SELECTED_DUAL_UPGRADE_SHARE cutoff=0.9000: early d=-2.31%, late d=+1.36%, OOS d=+0.36%, 2025 flag=50%, 2026 negative capture=83%, 2026 bad mean=-7.29%; PASS=False
- SELECTED_OPFY1_MEDIAN_ACCEL_4STATE cutoff=-3.5817: early d=-1.09%, late d=-0.93%, OOS d=-0.47%, 2025 flag=45%, 2026 negative capture=42%, 2026 bad mean=-6.34%; PASS=False
- OPFY1_POS_BREADTH_ACCEL_4STATE cutoff=-0.0289: early d=-3.17%, late d=+0.24%, OOS d=-1.71%, 2025 flag=55%, 2026 negative capture=33%, 2026 bad mean=-4.45%; PASS=False
- OPFY1_POS_BREADTH cutoff=0.3165: early d=-1.56%, late d=+0.22%, OOS d=+0.70%, 2025 flag=41%, 2026 negative capture=17%, 2026 bad mean=-16.34%; PASS=False
- OPFY1_P75_RAW cutoff=0.8519: early d=-1.76%, late d=+1.24%, OOS d=-1.96%, 2025 flag=50%, 2026 negative capture=17%, 2026 bad mean=-16.34%; PASS=False
- DUAL_UPGRADE_BREADTH cutoff=0.0359: early d=-0.41%, late d=-0.02%, OOS d=+0.70%, 2025 flag=55%, 2026 negative capture=17%, 2026 bad mean=-16.34%; PASS=False
- SELECTED_OPFY1_MEDIAN_RAW cutoff=11.3633: early d=-0.38%, late d=+2.27%, OOS d=-1.59%, 2025 flag=23%, 2026 negative capture=8%, 2026 bad mean=-22.60%; PASS=False
- OP12_POS_BREADTH cutoff=0.6618: early d=+1.24%, late d=-1.45%, OOS d=-1.44%, 2025 flag=32%, 2026 negative capture=8%, 2026 bad mean=-3.93%; PASS=False

## Passed features

- None.

## 2026 HIGH chronology — raw revision diffusion

- 2026-02-11: FB=0.625; FY1 breadth=0.32; FY1 median=+0.000; dual breadth=0.04; selected FY1+=1.00; selected median=+24.877; selected dual=0.80; breadth accel=-0.64; fwd20=+0.65%
- 2026-02-23: FB=0.625; FY1 breadth=0.34; FY1 median=+0.000; dual breadth=0.04; selected FY1+=1.00; selected median=+24.592; selected dual=0.90; breadth accel=-0.60; fwd20=-3.93%
- 2026-03-03: FB=0.750; FY1 breadth=0.36; FY1 median=+0.000; dual breadth=0.04; selected FY1+=1.00; selected median=+21.478; selected dual=0.85; breadth accel=-0.57; fwd20=-7.22%
- 2026-03-10: FB=0.875; FY1 breadth=0.40; FY1 median=+0.000; dual breadth=0.04; selected FY1+=1.00; selected median=+21.478; selected dual=0.85; breadth accel=+0.09; fwd20=-6.69%
- 2026-03-17: FB=0.750; FY1 breadth=0.43; FY1 median=+0.000; dual breadth=0.05; selected FY1+=1.00; selected median=+24.730; selected dual=0.85; breadth accel=+0.11; fwd20=+0.11%
- 2026-03-24: FB=0.750; FY1 breadth=0.40; FY1 median=+0.000; dual breadth=0.04; selected FY1+=1.00; selected median=+21.973; selected dual=0.85; breadth accel=+0.06; fwd20=+8.35%
- 2026-04-14: FB=0.625; FY1 breadth=0.32; FY1 median=+0.000; dual breadth=0.04; selected FY1+=1.00; selected median=+19.661; selected dual=0.90; breadth accel=-0.11; fwd20=+16.51%
- 2026-04-28: FB=0.625; FY1 breadth=0.35; FY1 median=+0.000; dual breadth=0.04; selected FY1+=1.00; selected median=+18.656; selected dual=0.90; breadth accel=-0.02; fwd20=-11.06%
- 2026-05-07: FB=0.625; FY1 breadth=0.37; FY1 median=+0.000; dual breadth=0.05; selected FY1+=1.00; selected median=+26.006; selected dual=0.85; breadth accel=+0.04; fwd20=-22.60%
- 2026-05-14: FB=0.750; FY1 breadth=0.39; FY1 median=+0.000; dual breadth=0.05; selected FY1+=1.00; selected median=+41.440; selected dual=0.80; breadth accel=+0.07; fwd20=-12.74%
- 2026-05-21: FB=0.750; FY1 breadth=0.46; FY1 median=+0.000; dual breadth=0.06; selected FY1+=1.00; selected median=+41.663; selected dual=0.85; breadth accel=+0.12; fwd20=-13.33%
- 2026-05-29: FB=0.750; FY1 breadth=0.45; FY1 median=+0.000; dual breadth=0.05; selected FY1+=1.00; selected median=+37.489; selected dual=0.90; breadth accel=+0.10; fwd20=-9.82%
- 2026-06-08: FB=0.750; FY1 breadth=0.46; FY1 median=+0.000; dual breadth=0.05; selected FY1+=1.00; selected median=+31.930; selected dual=0.95; breadth accel=+0.08; fwd20=-3.55%
- 2026-06-15: FB=0.750; FY1 breadth=0.39; FY1 median=+0.000; dual breadth=0.05; selected FY1+=1.00; selected median=+21.146; selected dual=0.90; breadth accel=-0.01; fwd20=-17.68%
- 2026-06-29: FB=0.750; FY1 breadth=0.23; FY1 median=+0.000; dual breadth=0.03; selected FY1+=1.00; selected median=+9.313; selected dual=0.90; breadth accel=-0.22; fwd20=-22.60%
- 2026-07-06: FB=0.750; FY1 breadth=0.26; FY1 median=+0.000; dual breadth=0.03; selected FY1+=1.00; selected median=+12.245; selected dual=0.95; breadth accel=-0.20; fwd20=-10.08%
- 2026-07-13: FB=0.625; FY1 breadth=0.29; FY1 median=+0.000; dual breadth=0.03; selected FY1+=1.00; selected median=+17.983; selected dual=0.85; breadth accel=-0.10; fwd20=NA
- 2026-07-21: FB=0.625; FY1 breadth=0.33; FY1 median=+0.000; dual breadth=0.04; selected FY1+=1.00; selected median=+18.025; selected dual=0.85; breadth accel=+0.02; fwd20=NA
- 2026-07-28: FB=0.750; FY1 breadth=0.38; FY1 median=+0.000; dual breadth=0.04; selected FY1+=1.00; selected median=+23.502; selected dual=0.90; breadth accel=+0.15; fwd20=NA

## Guardrails

- Do not combine near-misses if none passes. Failure here means the current data stack does not support a robust ex-ante OPFY1 breakdown timer.
- Any single passing feature must be tested unchanged on exact daily NAV before production use.