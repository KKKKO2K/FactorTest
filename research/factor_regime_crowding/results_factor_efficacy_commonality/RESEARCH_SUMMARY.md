# Factor Efficacy / Commonality Screen — Mixed OPFY1+CF20

- Purpose: distinguish healthy broad factor strength from a state where FACTOR_20D is HIGH but the target OPFY1 factor is weak/lagging or factor returns have collapsed into a common mode.
- All factor-strength metrics use only canonical 5D factor returns through the signal date. 20D metrics compound four 5D observations; correlation/commonality uses the trailing 24 5D observations (~120D).
- Adverse direction is pre-specified: weak OPFY1 / weak Revision-vs-Momentum is bad; high factor-return correlation/commonality is bad.
- Cutoffs are TRAIN 2016-22 HIGH-state terciles only and frozen later.

## Screen results

- REVISION_FAMILY_RANK20 (LOW_BAD, cutoff=0.7500): early d=-0.89%, late d=+0.81%, OOS d=+4.94%, 2025 flag=73%, 2026 negative capture=92%, 2026 bad mean=-7.83%; PASS=False
- REVISION_MINUS_MOMENTUM20 (LOW_BAD, cutoff=0.0078): early d=+1.37%, late d=-3.28%, OOS d=+4.30%, 2025 flag=59%, 2026 negative capture=83%, 2026 bad mean=-8.13%; PASS=False
- OPFY1_SPREAD_SHARE20 (LOW_BAD, cutoff=0.2972): early d=+1.25%, late d=-0.40%, OOS d=+1.90%, 2025 flag=55%, 2026 negative capture=75%, 2026 bad mean=-8.55%; PASS=False
- PC1_SHARE_120D (HIGH_BAD, cutoff=0.3908): early d=+2.32%, late d=+0.62%, OOS d=+5.52%, 2025 flag=0%, 2026 negative capture=67%, 2026 bad mean=-14.05%; PASS=False
- OPFY1_LS_RANK20 (LOW_BAD, cutoff=0.6250): early d=+0.55%, late d=-2.99%, OOS d=+3.23%, 2025 flag=55%, 2026 negative capture=58%, 2026 bad mean=-7.22%; PASS=False
- REV_MOM_CORR_120D (HIGH_BAD, cutoff=0.4221): early d=+1.45%, late d=+5.71%, OOS d=+1.31%, 2025 flag=50%, 2026 negative capture=50%, 2026 bad mean=-14.39%; PASS=False
- OPFY1_MINUS_FACTOR_MEDIAN20 (LOW_BAD, cutoff=0.0013): early d=+1.09%, late d=-3.17%, OOS d=+3.67%, 2025 flag=36%, 2026 negative capture=42%, 2026 bad mean=-5.55%; PASS=False
- OPFY1_LS_ACCEL20 (LOW_BAD, cutoff=-0.0011): early d=-1.30%, late d=+0.23%, OOS d=+1.97%, 2025 flag=41%, 2026 negative capture=33%, 2026 bad mean=-3.73%; PASS=False
- OPFY1_LS20 (LOW_BAD, cutoff=0.0202): early d=+1.20%, late d=-3.74%, OOS d=+3.07%, 2025 flag=27%, 2026 negative capture=17%, 2026 bad mean=+0.63%; PASS=False
- AVG_PAIR_CORR_120D (HIGH_BAD, cutoff=0.1198): early d=+2.35%, late d=-3.05%, OOS d=-5.23%, 2025 flag=68%, 2026 negative capture=0%, 2026 bad mean=NA; PASS=False

## Passed features

- None.

## 2026 HIGH chronology — candidate-specific factor quality

- 2026-02-11: FB=0.625; OPFY1_LS20=+5.12%; rank=0.75; Rev-Mom=+1.36%; spread_share=0.16; avg_corr120=+0.04; pc1=0.31; fwd20=+0.65%
- 2026-02-23: FB=0.625; OPFY1_LS20=+5.03%; rank=0.88; Rev-Mom=+2.78%; spread_share=0.12; avg_corr120=+0.03; pc1=0.31; fwd20=-3.93%
- 2026-03-03: FB=0.750; OPFY1_LS20=+2.18%; rank=0.50; Rev-Mom=-1.31%; spread_share=0.22; avg_corr120=+0.03; pc1=0.32; fwd20=-7.22%
- 2026-03-10: FB=0.875; OPFY1_LS20=+7.56%; rank=0.88; Rev-Mom=+1.77%; spread_share=1.00; avg_corr120=+0.04; pc1=0.34; fwd20=-6.69%
- 2026-03-17: FB=0.750; OPFY1_LS20=+4.63%; rank=0.88; Rev-Mom=-2.95%; spread_share=0.58; avg_corr120=+0.02; pc1=0.35; fwd20=+0.11%
- 2026-03-24: FB=0.750; OPFY1_LS20=+3.76%; rank=0.62; Rev-Mom=-1.12%; spread_share=1.00; avg_corr120=+0.02; pc1=0.35; fwd20=+8.35%
- 2026-04-14: FB=0.625; OPFY1_LS20=-2.04%; rank=0.25; Rev-Mom=-2.77%; spread_share=0.26; avg_corr120=+0.04; pc1=0.37; fwd20=+16.51%
- 2026-04-28: FB=0.625; OPFY1_LS20=+0.42%; rank=0.50; Rev-Mom=-4.27%; spread_share=0.01; avg_corr120=+0.04; pc1=0.37; fwd20=-11.06%
- 2026-05-07: FB=0.625; OPFY1_LS20=+4.46%; rank=0.62; Rev-Mom=-3.35%; spread_share=0.10; avg_corr120=+0.04; pc1=0.41; fwd20=-22.60%
- 2026-05-14: FB=0.750; OPFY1_LS20=+6.45%; rank=0.50; Rev-Mom=-5.54%; spread_share=0.25; avg_corr120=+0.04; pc1=0.40; fwd20=-12.74%
- 2026-05-21: FB=0.750; OPFY1_LS20=+7.26%; rank=0.75; Rev-Mom=-6.75%; spread_share=1.00; avg_corr120=+0.03; pc1=0.40; fwd20=-13.33%
- 2026-05-29: FB=0.750; OPFY1_LS20=+4.88%; rank=0.75; Rev-Mom=-5.57%; spread_share=0.24; avg_corr120=+0.05; pc1=0.40; fwd20=-9.82%
- 2026-06-08: FB=0.750; OPFY1_LS20=+2.00%; rank=0.62; Rev-Mom=-4.54%; spread_share=0.05; avg_corr120=+0.04; pc1=0.40; fwd20=-3.55%
- 2026-06-15: FB=0.750; OPFY1_LS20=+3.23%; rank=0.88; Rev-Mom=-0.66%; spread_share=0.14; avg_corr120=+0.03; pc1=0.41; fwd20=-17.68%
- 2026-06-29: FB=0.750; OPFY1_LS20=+3.53%; rank=0.50; Rev-Mom=-0.48%; spread_share=0.14; avg_corr120=+0.01; pc1=0.42; fwd20=-22.60%
- 2026-07-06: FB=0.750; OPFY1_LS20=+3.06%; rank=0.50; Rev-Mom=+0.05%; spread_share=0.30; avg_corr120=+0.00; pc1=0.43; fwd20=-10.08%
- 2026-07-13: FB=0.625; OPFY1_LS20=+2.61%; rank=0.50; Rev-Mom=-1.74%; spread_share=0.07; avg_corr120=+0.00; pc1=0.43; fwd20=NA
- 2026-07-21: FB=0.625; OPFY1_LS20=+3.62%; rank=0.50; Rev-Mom=+0.92%; spread_share=0.10; avg_corr120=+0.00; pc1=0.44; fwd20=NA
- 2026-07-28: FB=0.750; OPFY1_LS20=+0.53%; rank=0.38; Rev-Mom=-0.65%; spread_share=0.01; avg_corr120=-0.01; pc1=0.46; fwd20=NA

## Guardrails

- No feature weights or cutoffs are optimized on 2025/2026.
- A passing single feature goes directly to unchanged exact daily-NAV Gross/Net30/Net60 testing; near-miss combinations are not allowed.
- 2023+ is robustness/stress evidence rather than pristine untouched OOS.