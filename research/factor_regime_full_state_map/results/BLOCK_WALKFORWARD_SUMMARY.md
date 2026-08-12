# Full State Map — Non-overlapping Block Walk-forward

Validation blocks: 2020-2021, 2022-2023, 2024-2025. Each block uses an expanding training sample ending strictly before the block.
This block design is used because annual W+/W-/N+/N-/R+/R- conditional cells are too sparse for the predeclared minimum of 8 observations per side.
No minimum-N rule was relaxed; the validation horizon was widened instead.

## Market +20D contrasts with all 3 blocks available

- KOSPI_ALL | REVISION->FLOW | CONFIRM_WPLUS_VS_NEUTRAL_WHEN_ANCHOR_WPLUS: sign 67%; median TRAIN +1.92%, VALID +2.62%; min valid n 8/9
- KOSPI_EX_K200 | REVISION->FLOW | CONFIRM_WPLUS_VS_NEUTRAL_WHEN_ANCHOR_WPLUS: sign 33%; median TRAIN -0.36%, VALID +0.41%; min valid n 15/8

## Interpretation discipline

- Three blocks are still a small validation count; 100% means 3/3, not proof of invariance.
- Prefer relations whose sign is stable, median TRAIN and VALID effect have similar magnitude, and both sides retain adequate sample counts.
- Static 2023+ cells remain descriptive and must not override block walk-forward evidence.

