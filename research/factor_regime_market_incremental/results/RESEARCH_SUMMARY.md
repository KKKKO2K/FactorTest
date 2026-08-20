# Factor Regime — Incremental Market-State Value

- Question: does frozen factor-state information improve market-state/downside prediction beyond the frozen B-state alone?
- Models are non-parametric TRAIN 2016-22 conditional event rates. Augmented cells with <20 TRAIN observations fall back to the B-state probability; no 2023+ fitting is allowed.
- Predictors: B_ONLY; B_FSUB = B × frozen F_HIGH/F_LOW; B_FB20 = B × frozen FACTOR_20D LOW/MID/HIGH; B_FSUB_FB20 = all three.
- Targets: next B-state down-transition; negative 20D market return; >=5% forward-20D drawdown.
- Lower Brier/log-loss is better; higher AUC is better. Primary confirmation sample is 2023-24; 2025/2026 are stress descriptions.

## TARGET_NEXT_B_DOWN

### OOS_2023_2024
- B_FSUB: median ΔBrier -0.0005; median Δlogloss -0.0065; median ΔAUC +0.0265; Brier-better universes 4/6
- B_FB20: median ΔBrier +0.0007; median Δlogloss +0.0028; median ΔAUC -0.0007; Brier-better universes 2/6
- B_FSUB_FB20: median ΔBrier +0.0032; median Δlogloss +0.0023; median ΔAUC +0.0352; Brier-better universes 2/6

### BULL_2025
- B_FSUB: median ΔBrier -0.0032; median Δlogloss -0.0155; median ΔAUC +0.0698; Brier-better universes 6/6
- B_FB20: median ΔBrier +0.0020; median Δlogloss +0.0046; median ΔAUC -0.0296; Brier-better universes 0/6
- B_FSUB_FB20: median ΔBrier +0.0018; median Δlogloss +0.0044; median ΔAUC +0.0185; Brier-better universes 2/6

### YTD_2026
- B_FSUB: median ΔBrier -0.0004; median Δlogloss +0.0214; median ΔAUC +0.0000; Brier-better universes 4/6
- B_FB20: median ΔBrier -0.0032; median Δlogloss -0.0033; median ΔAUC +0.1120; Brier-better universes 5/6
- B_FSUB_FB20: median ΔBrier -0.0030; median Δlogloss +0.0345; median ΔAUC +0.1303; Brier-better universes 3/6

## TARGET_MKT_NEG20

### OOS_2023_2024
- B_FSUB: median ΔBrier +0.0013; median Δlogloss +0.0025; median ΔAUC +0.0484; Brier-better universes 2/6
- B_FB20: median ΔBrier +0.0033; median Δlogloss +0.0072; median ΔAUC +0.0207; Brier-better universes 0/6
- B_FSUB_FB20: median ΔBrier +0.0061; median Δlogloss +0.0127; median ΔAUC +0.0096; Brier-better universes 1/6

### BULL_2025
- B_FSUB: median ΔBrier +0.0089; median Δlogloss +0.0179; median ΔAUC -0.0453; Brier-better universes 0/6
- B_FB20: median ΔBrier +0.0035; median Δlogloss +0.0069; median ΔAUC -0.0497; Brier-better universes 2/6
- B_FSUB_FB20: median ΔBrier +0.0094; median Δlogloss +0.0189; median ΔAUC -0.0585; Brier-better universes 1/6

### YTD_2026
- B_FSUB: median ΔBrier +0.0050; median Δlogloss +0.0098; median ΔAUC -0.0361; Brier-better universes 2/6
- B_FB20: median ΔBrier +0.0016; median Δlogloss +0.0029; median ΔAUC -0.0470; Brier-better universes 3/6
- B_FSUB_FB20: median ΔBrier -0.0118; median Δlogloss -0.0242; median ΔAUC +0.0165; Brier-better universes 4/6

## TARGET_DD5_20

### OOS_2023_2024
- B_FSUB: median ΔBrier +0.0005; median Δlogloss +0.0002; median ΔAUC +0.0361; Brier-better universes 3/6
- B_FB20: median ΔBrier +0.0024; median Δlogloss +0.0055; median ΔAUC +0.0066; Brier-better universes 3/6
- B_FSUB_FB20: median ΔBrier +0.0030; median Δlogloss +0.0108; median ΔAUC +0.0257; Brier-better universes 2/6

### BULL_2025
- B_FSUB: median ΔBrier +0.0048; median Δlogloss +0.0104; median ΔAUC -0.0475; Brier-better universes 1/6
- B_FB20: median ΔBrier +0.0031; median Δlogloss +0.0083; median ΔAUC -0.0805; Brier-better universes 1/6
- B_FSUB_FB20: median ΔBrier +0.0086; median Δlogloss +0.0222; median ΔAUC -0.0787; Brier-better universes 1/6

### YTD_2026
- B_FSUB: median ΔBrier -0.0020; median Δlogloss -0.0045; median ΔAUC +0.0235; Brier-better universes 4/6
- B_FB20: median ΔBrier +0.0028; median Δlogloss +0.0130; median ΔAUC +0.0530; Brier-better universes 3/6
- B_FSUB_FB20: median ΔBrier -0.0007; median Δlogloss +0.0052; median ΔAUC +0.0007; Brier-better universes 3/6

## Universe detail — OOS 2023-24 next-B-down

- K200: B_FSUB ΔBrier=+0.0007, ΔAUC=+0.014; B_FB20 ΔBrier=+0.0013, ΔAUC=+0.007; B_FSUB_FB20 ΔBrier=+0.0021, ΔAUC=+0.026
- KOSDAQ: B_FSUB ΔBrier=-0.0004, ΔAUC=+0.034; B_FB20 ΔBrier=+0.0001, ΔAUC=-0.009; B_FSUB_FB20 ΔBrier=-0.0008, ΔAUC=+0.045
- KOSDAQ_PLUS_KOSPI_EX_K200: B_FSUB ΔBrier=-0.0015, ΔAUC=+0.053; B_FB20 ΔBrier=+0.0054, ΔAUC=-0.019; B_FSUB_FB20 ΔBrier=+0.0058, ΔAUC=-0.048
- KOSPI_ALL: B_FSUB ΔBrier=-0.0017, ΔAUC=+0.032; B_FB20 ΔBrier=-0.0003, ΔAUC=+0.016; B_FSUB_FB20 ΔBrier=-0.0017, ΔAUC=+0.044
- KOSPI_EX_K200: B_FSUB ΔBrier=+0.0001, ΔAUC=+0.006; B_FB20 ΔBrier=-0.0002, ΔAUC=+0.027; B_FSUB_FB20 ΔBrier=+0.0043, ΔAUC=+0.046
- KOSPI_KOSDAQ_ALL: B_FSUB ΔBrier=-0.0006, ΔAUC=+0.021; B_FB20 ΔBrier=+0.0054, ΔAUC=-0.022; B_FSUB_FB20 ΔBrier=+0.0057, ΔAUC=-0.010

## Interpretation gate

- PASS as market-regime information only if an augmented model improves 2023-24 median Brier and does so in at least 4/6 universes for the same target.
- A 2025/2026-only improvement is not confirmation.
- This test evaluates information value, not a trading strategy; any market allocation rule would require a separate pre-specified mapping and exact NAV test.