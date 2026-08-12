# Contemporaneous Market-Regime Research

No forward return, future drawdown, or calendar-year label enters regime fitting. All features are observable through the state date.
Primary test: fixed 5-state GMM. BASE uses market trend/volatility/drawdown plus 5D-vs-20D trading-value breadth; FULL adds factor absolute/relative breadth, family interactions, leader strength/dispersion, and leader-rotation flags.
Models are fit on 2016-2022 and frozen for 2023 onward. K=3..6 is robustness only.

## Incremental diagnostics: FULL vs BASE, K=5


## FULL-state future outcomes (attached after classification)


## Calendar-period composition of FULL states


## Same-market / different-factor states in TRAIN

- None passed the predeclared screen: base centroid distance <=1.5z and factor centroid distance >=1.5z.

## Rule-based archetype check: 2023-2024

- K200: MIXED n=36 +20D=+0.39%; OTHER_UPTREND n=27 +20D=+0.26%; DEFENSIVE_WEAKNESS n=15 +20D=+1.28%; BROAD_WEAKNESS n=8 +20D=-2.12%; BROAD_EXPANSION n=5 +20D=-1.26%; CONCENTRATED_TREND n=5 +20D=+2.40%
- KOSPI_ALL: MIXED n=38 +20D=+0.15%; OTHER_UPTREND n=21 +20D=+0.85%; DEFENSIVE_WEAKNESS n=15 +20D=+1.58%; CONCENTRATED_TREND n=7 +20D=-0.96%; BROAD_EXPANSION n=6 +20D=-0.72%; BROAD_WEAKNESS n=5 +20D=-3.96%; ROTATION n=5 +20D=+2.35%
- KOSPI_EX_K200: MIXED n=39 +20D=-0.09%; OTHER_UPTREND n=26 +20D=+1.60%; DEFENSIVE_WEAKNESS n=15 +20D=+2.59%; BROAD_EXPANSION n=7 +20D=-1.87%; BROAD_WEAKNESS n=5 +20D=-1.99%; ROTATION n=5 +20D=+0.16%
- KOSDAQ: MIXED n=22 +20D=-2.03%; OTHER_UPTREND n=22 +20D=+2.71%; DEFENSIVE_WEAKNESS n=19 +20D=+0.76%; BROAD_WEAKNESS n=15 +20D=-1.07%; CONCENTRATED_TREND n=12 +20D=+1.81%; BROAD_EXPANSION n=6 +20D=-3.05%

## Guardrails

- State IDs are ordered by TRAIN 60D market return, not named ex post as bull/bear.
- Factor interaction is incremental only if FULL distinguishes economically different states that BASE cannot recover and those distinctions survive after 2022.
- Future outcomes validate economic meaning; they never define the states.
- 2025 and 2026 are kept separate in composition diagnostics.

