# Exact Weighted-Momentum Factor Regime Research

## Design

- Momentum = exact legacy weighted momentum `(12*R1M + 4*R3M + 2*R6M + R12M)/17`.
- Revision = equal-weight rank composite of OP(12MF 1M chg) and OP(FY1 1M chg).
- Value = equal-weight low-is-good rank composite of PBR(12MF) and PER(12MF).
- Flow = equal-weight rank composite of private-flow and foreign-flow factors.
- Market-cap floor = KRW 250bn.
- Factor preferred/opposite legs = top/bottom 20%; 5D realized legs, compounded to a 20D state.
- Relative state uses preferred 20D return minus opposite 20D return. TRAIN absolute-spread Q33 defines the W/N/R dead-zone and is frozen after 2022.
- `R-` means the factor is relatively reversing and its preferred leg is absolutely negative.
- Primary meta-state test:
  - `MOM_RISK_ROTATION_SUPPORT`: Momentum R- while at least 2 of Revision/Value/Flow preferred 20D legs are positive.
  - `MOM_BROAD_RISK_OFF`: Momentum R- while at most 1 of Revision/Value/Flow preferred 20D legs is positive.
- Market outcomes begin at t+1 for +1D/+5D/+20D. 2023+ is post-discovery validation, not untouched OOS.

## 1. Primary hypothesis: other-factor positive absolute returns do NOT robustly forecast a better market after Momentum breakdown

### +20D same-universe market return

| Universe | TRAIN Rotation support | TRAIN Broad risk-off | Support - risk-off | 2023+ Rotation support | 2023+ Broad risk-off | Support - risk-off |
|---|---:|---:|---:|---:|---:|---:|
| K200 | +1.15% | +0.97% | +0.18%p | -3.03% | +3.16% | -6.19%p |
| KOSPI_ALL | +1.77% | -0.27% | +2.04%p | -1.80% | +0.83% | -2.63%p |
| KOSPI_EX_K200 | +0.12% | +0.05% | +0.07%p | +0.17% | -0.72% | +0.90%p |
| KOSDAQ | +1.72% | +2.32% | -0.59%p | -0.27% | +0.11% | -0.37%p |
| KOSDAQ_PLUS_KOSPI_EX_K200 | +1.38% | +2.17% | -0.78%p | -1.42% | +0.27% | -1.69%p |

The cleanest TRAIN support was KOSPI_ALL, but it reversed after 2023. K200 reversed even more strongly. Only KOSPI_EX_K200 has the hypothesized ordering in both samples, and the TRAIN contrast is negligible. Therefore the simple rule `Momentum breaks + other preferred legs stay positive => bullish market` is rejected as a general market-timing signal.

The absolute signs are still useful descriptively: they distinguish a style rotation from contemporaneous broad weakness. The problem is the jump from contemporaneous classification to forward-index prediction.

## 2. Family spread correlations are much more structurally stable

The most persistent relationships are:

- Momentum × Revision: positive.
  - K200 +0.55 TRAIN -> +0.48 POST.
  - KOSPI_EX_K200 +0.33 -> +0.21.
  - KOSDAQ +0.27 -> +0.26.
  - KOSDAQ_PLUS_KOSPI_EX_K200 +0.35 -> +0.29.
- Momentum × Value: negative.
  - K200 -0.34 -> -0.24.
  - KOSPI_EX_K200 -0.26 -> -0.20.
  - KOSDAQ -0.28 -> -0.29.
  - KOSDAQ_PLUS_KOSPI_EX_K200 -0.25 -> -0.26.
- Revision × Value is also generally negative and became more negative in several recent universes.
- Flow correlations are weaker and less stable; e.g. KOSPI_EX_K200 Flow × Momentum moved from -0.09 to +0.30.

Implication: Value is the clearest orthogonal counter-style to Momentum; Revision is substantially momentum-like; Flow should not be treated as a fixed orthogonal sleeve.

## 3. Simple factor breadth is not a universal market-timing signal

`positive_abs_breadth` is the fraction of Momentum/Revision/Value/Flow preferred 20D legs above zero. High-minus-low future +20D market return:

- KOSPI_EX_K200: +0.68%p TRAIN -> -0.71%p POST.
- KOSDAQ: -1.19%p TRAIN -> +0.52%p POST.
- KOSDAQ_PLUS_KOSPI_EX_K200: -1.36%p TRAIN -> -0.15%p POST.
- KOSPI_ALL: -0.03%p TRAIN -> +2.73%p POST, but this is not stable inside POST; 2023-24 was negative.
- K200: +0.04%p TRAIN -> +2.65%p POST, likewise strongly regime-driven.

Thus `more factor preferred legs positive => higher next-month index return` is not a stable cross-universe rule.

## 4. Dispersion is more promising, but only in specific universes

High-minus-low factor-spread dispersion versus future +20D market return:

- K200: +2.34%p TRAIN -> +1.43%p POST.
- KOSDAQ: +1.61%p TRAIN -> +1.62%p POST.
- KOSPI_ALL: +3.18%p TRAIN -> -0.31%p POST.
- KOSPI_EX_K200: +2.95%p TRAIN -> -3.88%p POST.
- KOSDAQ_PLUS_KOSPI_EX_K200: +2.65%p TRAIN -> -0.16%p POST.

So factor dispersion has a repeatable positive association with later market returns in K200 and KOSDAQ, but not as a universal market signal.

## 5. Rolling average factor correlation

The 60D average correlation state is also universe-specific. KOSDAQ is the notable candidate: high-minus-low average correlation corresponds to +20D market return of about +1.40%p in TRAIN and +3.72%p in 2023+, while K200 changes sign. This is exploratory rather than a production rule.

## Current conclusion

1. Preserve preferred absolute return, opposite absolute return, and relative spread. The W+/W-/N/R+/R- framework is conceptually useful.
2. Reject the simple market-timing hypothesis that positive absolute returns in alternate factors during Momentum R- reliably imply a better subsequent index path.
3. The factor-state map is currently more useful for **factor allocation / understanding rotation** than for hard **index risk-on/risk-off timing**.
4. Structural correlation is the strongest result: Momentum and Revision cluster together; Value is the cleanest orthogonal style; Flow is less stable.
5. For market timing, keep only universe-specific candidates for further validation: K200/KOSDAQ factor-spread dispersion, and KOSDAQ rolling factor correlation.
6. Do not optimize many discrete pair cells: prior research showed severe cell sparsity. Aggregate four-family states and common contrasts should remain primary.
