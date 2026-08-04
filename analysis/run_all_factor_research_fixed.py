from __future__ import annotations

import base64
import gzip
import re
from pathlib import Path

wrapper = Path(__file__).with_name("run_all_factor_research.py").read_text(encoding="utf-8")
payload = re.search(r'base64\.b64decode\("([A-Za-z0-9+/=]+)"\)', wrapper)
if payload is None:
    raise RuntimeError("Embedded research payload not found")
source = gzip.decompress(base64.b64decode(payload.group(1))).decode("utf-8")

# Correct pandas alignment: the explicit StockCode index must receive positional arrays,
# not Series indexed 0..n-1 (which otherwise align to all-NaN).
source = source.replace(
    '"ret": pd.to_numeric(df[rc], errors="coerce") / 100.0,',
    '"ret": (pd.to_numeric(df[rc], errors="coerce") / 100.0).to_numpy(),',
)
source = source.replace(
    '"mcap": pd.to_numeric(df[mc], errors="coerce"),',
    '"mcap": pd.to_numeric(df[mc], errors="coerce").to_numpy(),',
)
source = source.replace(
    '"market": df[mk].astype(str).str.upper().str.strip() if mk else "",',
    '"market": df[mk].astype(str).str.upper().str.strip().to_numpy() if mk else np.repeat("", len(df)),',
)
source = source.replace(
    '"k200": pd.to_numeric(df[kc], errors="coerce").fillna(0).astype(int) if kc else 0,',
    '"k200": pd.to_numeric(df[kc], errors="coerce").fillna(0).astype(int).to_numpy() if kc else np.zeros(len(df), dtype=int),',
)

# Fix result-container initialization.
source = source.replace(
    "single_rows, selected_rows, result_rows, yearly_rows, importance_rows, rules = [], [], [], [], []",
    "single_rows, selected_rows, result_rows, yearly_rows, importance_rows, rules = [], [], [], [], [], {}",
)

# Hard gates should exclude names (NaN), not assign a low but still investable score.
source = source.replace(
    '.where((long_mom >= 0.65) & (flow >= 0.50), -1)',
    '.where((long_mom >= 0.65) & (flow >= 0.50))',
)
source = source.replace(
    '.where((long_mom >= 0.65) & short_mom.between(0.15, 0.65), -1)',
    '.where((long_mom >= 0.65) & short_mom.between(0.15, 0.65))',
)
source = source.replace(
    '.where((value >= 0.65) & (long_mom >= 0.50) & (revision >= 0.15), -1)',
    '.where((value >= 0.65) & (long_mom >= 0.50) & (revision >= 0.15))',
)
source = source.replace(
    '.where((revision >= 0.65) & (flow >= 0.50), -1)',
    '.where((revision >= 0.65) & (flow >= 0.50))',
)

source = source.replace(
    "singles = pd.concat(single_rows, ignore_index=True)",
    "singles = pd.concat(single_rows, ignore_index=True) if single_rows else pd.DataFrame()",
)

exec(compile(source, str(Path(__file__).with_name("run_all_factor_research_source.py")), "exec"))
