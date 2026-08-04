from __future__ import annotations

from pathlib import Path

source_path = Path(__file__).with_name("creative_factor_lab.py")
source = source_path.read_text(encoding="utf-8")
source = source.replace(
    'UNIVERSES = ("KOSPI_EX_K200", "KOSDAQ", "K200")',
    'UNIVERSES = ("KOSPI_EX_K200",)',
)
source = source.replace('STEPS = (5, 10)', 'STEPS = (5,)')
source = source.replace('COSTS = (30, 60, 100)', 'COSTS = (60,)')
source = source.replace(
    'ic = valid[factor].corr(valid["future"], method="spearman")',
    'ic = valid[factor].rank(method="average").corr(valid["future"].rank(method="average"))',
)
source = source.replace(
    'panel.to_pickle(OUT / f"feature_panel_{universe}_{step}d.pkl")',
    'pass',
)
exec(compile(source, str(source_path), "exec"))
