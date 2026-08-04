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
source = source.replace(
    "single_rows, selected_rows, result_rows, yearly_rows, importance_rows, rules = [], [], [], [], []",
    "single_rows, selected_rows, result_rows, yearly_rows, importance_rows, rules = [], [], [], [], [], {}",
)
source = source.replace(
    "pd.concat(importance_rows, ignore_index=True).to_csv",
    "(pd.concat(importance_rows, ignore_index=True) if importance_rows else pd.DataFrame()).to_csv",
)
exec(compile(source, str(Path(__file__).with_name("run_all_factor_research_source.py")), "exec"))
