# HIGH-Breadth Feature Diagnostics — Mixed OPFY1+CF20

Universe is restricted to dates where frozen FACTOR_20D is HIGH. For each existing regime feature, the adverse direction and 1/3 or 2/3 cutoff are chosen using TRAIN 2016-22 only.
The screen then asks whether that frozen adverse extreme remains worse in 2023-24, avoids flagging most healthy 2025 HIGH dates, and captures at least half of 2026 HIGH dates with negative forward 20D finalist return.
This is exploratory feature screening, not a production rule; multiple-testing risk remains.

## Screen results

- RELATIVE_WORKING_BREADTH: TRAIN rho +0.06, LOW_BAD, cutoff 0.5000; TRAIN bad-rest -0.55%, OOS -1.53%, 2025 flagged 50%, 2026 flagged 55%, 2026 bad mean -3.18%; SCREEN=NO
- MKT_RET_20D: TRAIN rho -0.05, HIGH_BAD, cutoff 0.0145; TRAIN bad-rest +0.70%, OOS -3.37%, 2025 flagged 73%, 2026 flagged 55%, 2026 bad mean -9.48%; SCREEN=NO
- MKT_RET_60D: TRAIN rho -0.03, HIGH_BAD, cutoff 0.0384; TRAIN bad-rest +0.74%, OOS +0.95%, 2025 flagged 73%, 2026 flagged 64%, 2026 bad mean -5.77%; SCREEN=NO
- DEFENSIVE_WORKING_BREADTH: TRAIN rho +0.04, LOW_BAD, cutoff 0.0000; TRAIN bad-rest +0.27%, OOS -0.85%, 2025 flagged 91%, 2026 flagged 64%, 2026 bad mean -5.77%; SCREEN=NO
- WPLUS_PAIR_SHARE: TRAIN rho -0.02, HIGH_BAD, cutoff 0.1667; TRAIN bad-rest +0.38%, OOS -0.47%, 2025 flagged 77%, 2026 flagged 55%, 2026 bad mean -9.48%; SCREEN=NO
- CONFLICT_PAIR_SHARE: TRAIN rho +0.06, LOW_BAD, cutoff 0.0000; TRAIN bad-rest -1.14%, OOS +3.56%, 2025 flagged 68%, 2026 flagged 100%, 2026 bad mean -7.71%; SCREEN=NO
- FAMILY_MEMBER_AGREEMENT: TRAIN rho +0.14, LOW_BAD, cutoff 0.7500; TRAIN bad-rest -1.38%, OOS +3.41%, 2025 flagged 73%, 2026 flagged 73%, 2026 bad mean -6.11%; SCREEN=NO
- MKT_VOL_20D: TRAIN rho +0.08, LOW_BAD, cutoff 0.1307; TRAIN bad-rest -0.10%, OOS -1.31%, 2025 flagged 9%, 2026 flagged 0%, 2026 bad mean NA; SCREEN=NO
- MKT_DD_60D: TRAIN rho -0.09, HIGH_BAD, cutoff -0.0255; TRAIN bad-rest -0.52%, OOS -4.40%, 2025 flagged 77%, 2026 flagged 45%, 2026 bad mean -9.94%; SCREEN=NO
- LEADER_STRENGTH_60D: TRAIN rho +0.08, LOW_BAD, cutoff 0.0483; TRAIN bad-rest -2.18%, OOS -3.03%, 2025 flagged 27%, 2026 flagged 9%, 2026 bad mean -11.06%; SCREEN=NO
- LIQ_5D_20D: TRAIN rho +0.15, LOW_BAD, cutoff 0.2911; TRAIN bad-rest -1.98%, OOS +1.52%, 2025 flagged 23%, 2026 flagged 36%, 2026 bad mean -11.10%; SCREEN=NO
- ABS_CONFIRMED_BREADTH: TRAIN rho -0.02, HIGH_BAD, cutoff 0.5000; TRAIN bad-rest +0.62%, OOS +0.92%, 2025 flagged 68%, 2026 flagged 45%, 2026 bad mean -9.17%; SCREEN=NO
- SPREAD_DISPERSION_20D: TRAIN rho +0.07, LOW_BAD, cutoff 0.0213; TRAIN bad-rest -0.00%, OOS +1.51%, 2025 flagged 41%, 2026 flagged 27%, 2026 bad mean +4.41%; SCREEN=NO
- MKT_MOM_ACCEL: TRAIN rho -0.04, HIGH_BAD, cutoff 0.0043; TRAIN bad-rest +0.57%, OOS -2.35%, 2025 flagged 64%, 2026 flagged 45%, 2026 bad mean -9.94%; SCREEN=NO

## Passed features

- None. Existing continuous regime features do not cleanly separate healthy 2025 HIGH from 2026 breakdown under this frozen screen.

## Guardrails

- Do not combine multiple features merely because they look good here; that would compound selection bias.
- A passed feature must next be tested as a single pre-specified interaction on full daily NAV with the same 10 phase and Net30/Net60 framework.
- 2025 is used here specifically as a healthy-bull false-positive control, not as optimization target.
