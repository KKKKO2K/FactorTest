from __future__ import annotations

from pathlib import Path

source_path = Path(__file__).with_name("creative_factor_lab.py")
source = source_path.read_text(encoding="utf-8")
source = source.replace(
    'ic = valid[factor].corr(valid["future"], method="spearman")',
    'ic = valid[factor].rank(method="average").corr(valid["future"].rank(method="average"))',
)
exec(compile(source, str(source_path), "exec"))
