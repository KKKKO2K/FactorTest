from __future__ import annotations

from pathlib import Path

path = Path(__file__).with_name("run_cross_factor_liquidity.py")
source = path.read_text(encoding="utf-8")

# Pandas 3: DataFrame.sample is a method, so attribute-style access cannot be
# used for a column named "sample". Keep the research source readable while
# applying the compatibility fix at execution time.
source = source.replace('summary.sample == sample', 'summary["sample"] == sample')
source = source.replace('robust.sample == "OOS_2023_PLUS"', 'robust["sample"] == "OOS_2023_PLUS"')
source = source.replace('summary.sample == "OOS_2023_PLUS"', 'summary["sample"] == "OOS_2023_PLUS"')
source = source.replace('standalone.sample == "OOS_2023_PLUS"', 'standalone["sample"] == "OOS_2023_PLUS"')

exec(compile(source, str(path), "exec"))
