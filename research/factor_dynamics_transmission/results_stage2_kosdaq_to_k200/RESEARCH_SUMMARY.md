# Stage 2 — KOSDAQ -> K200 Propagation Falsification

This stage tests only the clean primitive-universe edge selected in Stage 1.
Composite universes are excluded from the primary mechanism test.

## Classification: WEAK_DIRECTIONAL

- Primary unique-control gate: False
- Leave-one-factor-out stable: False
- Time-shift placebo gate: False

## Horizon summary

### NEXT5
- VAL_2020_2022: unique KOSDAQ R2 +0.0021 (5/8 positive); unique ex-K200 R2 -0.0002; KQ-EX +0.0027; simple KOSDAQ R2 +0.0026
- CONF_2023_2024: unique KOSDAQ R2 +0.0019 (4/8 positive); unique ex-K200 R2 -0.0000; KQ-EX +0.0054; simple KOSDAQ R2 +0.0003
- STRESS_2025: unique KOSDAQ R2 -0.0092 (3/8 positive); unique ex-K200 R2 +0.0009; KQ-EX +0.0061; simple KOSDAQ R2 -0.0054
- STRESS_2026: unique KOSDAQ R2 +0.0045 (5/8 positive); unique ex-K200 R2 +0.0131; KQ-EX -0.0118; simple KOSDAQ R2 +0.0033

### GAP5
- VAL_2020_2022: unique KOSDAQ R2 -0.0021 (2/8 positive); unique ex-K200 R2 -0.0017; KQ-EX +0.0013; simple KOSDAQ R2 -0.0046
- CONF_2023_2024: unique KOSDAQ R2 -0.0061 (2/8 positive); unique ex-K200 R2 +0.0039; KQ-EX -0.0080; simple KOSDAQ R2 -0.0053
- STRESS_2025: unique KOSDAQ R2 -0.0060 (3/8 positive); unique ex-K200 R2 -0.0051; KQ-EX -0.0034; simple KOSDAQ R2 -0.0064
- STRESS_2026: unique KOSDAQ R2 +0.0015 (5/8 positive); unique ex-K200 R2 +0.0031; KQ-EX -0.0016; simple KOSDAQ R2 +0.0034

### NEXT10
- VAL_2020_2022: unique KOSDAQ R2 +0.0000 (4/8 positive); unique ex-K200 R2 -0.0020; KQ-EX +0.0014; simple KOSDAQ R2 -0.0018
- CONF_2023_2024: unique KOSDAQ R2 -0.0000 (4/8 positive); unique ex-K200 R2 +0.0002; KQ-EX -0.0010; simple KOSDAQ R2 -0.0002
- STRESS_2025: unique KOSDAQ R2 -0.0014 (2/8 positive); unique ex-K200 R2 +0.0014; KQ-EX -0.0054; simple KOSDAQ R2 +0.0013
- STRESS_2026: unique KOSDAQ R2 +0.0025 (4/8 positive); unique ex-K200 R2 +0.0020; KQ-EX +0.0053; simple KOSDAQ R2 +0.0018

### NEXT20
- VAL_2020_2022: unique KOSDAQ R2 +0.0003 (5/8 positive); unique ex-K200 R2 +0.0019; KQ-EX +0.0009; simple KOSDAQ R2 +0.0000
- CONF_2023_2024: unique KOSDAQ R2 -0.0049 (2/8 positive); unique ex-K200 R2 -0.0010; KQ-EX -0.0062; simple KOSDAQ R2 -0.0045
- STRESS_2025: unique KOSDAQ R2 -0.0017 (4/8 positive); unique ex-K200 R2 +0.0018; KQ-EX -0.0053; simple KOSDAQ R2 -0.0012
- STRESS_2026: unique KOSDAQ R2 +0.0029 (5/8 positive); unique ex-K200 R2 +0.0043; KQ-EX -0.0022; simple KOSDAQ R2 +0.0006

## Discovery coefficient stability

- KOSDAQ coefficient same sign in 2016-17 and 2018-19 for 1/8 factors.
- FOREIGN_FLOW: 2016-17 -0.045; 2018-19 -0.081; same_sign=True
- MOM12_1: 2016-17 -0.069; 2018-19 +0.231; same_sign=False
- MOM1M: 2016-17 -0.078; 2018-19 +0.142; same_sign=False
- OP12_REV: 2016-17 -0.202; 2018-19 +0.113; same_sign=False
- OPFY1_REV: 2016-17 -0.113; 2018-19 +0.031; same_sign=False
- PBR12MF: 2016-17 -0.003; 2018-19 +0.165; same_sign=False
- PER12MF: 2016-17 -0.091; 2018-19 +0.056; same_sign=False
- PRIVATE_FLOW: 2016-17 +0.057; 2018-19 -0.003; same_sign=False

## Time-shift placebo

- VAL_2020_2022: observed median unique KQ R2 +0.0021; placebo median -0.0011; q90 +0.0011; observed percentile 95.2%; p=0.054
- CONF_2023_2024: observed median unique KQ R2 +0.0019; placebo median -0.0011; q90 +0.0023; observed percentile 88.5%; p=0.124
- STRESS_2025: observed median unique KQ R2 -0.0092; placebo median -0.0020; q90 +0.0025; observed percentile 8.3%; p=0.918
- STRESS_2026: observed median unique KQ R2 +0.0045; placebo median -0.0007; q90 +0.0032; observed percentile 96.4%; p=0.069

## Leave-one-factor-out

- VAL_2020_2022: median across omissions +0.0021; minimum omission median +0.0009; positive after all 8/8 omissions
- CONF_2023_2024: median across omissions +0.0019; minimum omission median -0.0006; positive after all 4/8 omissions

## Interpretation

The KOSDAQ-leading pattern survives some controls but not all falsification checks. Keep it as a candidate dynamic, but do not call it a stable transmission law or tune it into a trading rule.