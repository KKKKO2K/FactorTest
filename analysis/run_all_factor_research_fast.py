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

repls = {
    '"ret": pd.to_numeric(df[rc], errors="coerce") / 100.0,': '"ret": (pd.to_numeric(df[rc], errors="coerce") / 100.0).to_numpy(),',
    '"mcap": pd.to_numeric(df[mc], errors="coerce"),': '"mcap": pd.to_numeric(df[mc], errors="coerce").to_numpy(),',
    '"market": df[mk].astype(str).str.upper().str.strip() if mk else "",': '"market": df[mk].astype(str).str.upper().str.strip().to_numpy() if mk else np.repeat("", len(df)),',
    '"k200": pd.to_numeric(df[kc], errors="coerce").fillna(0).astype(int) if kc else 0,': '"k200": pd.to_numeric(df[kc], errors="coerce").fillna(0).astype(int).to_numpy() if kc else np.zeros(len(df), dtype=int),',
    'single_rows, selected_rows, result_rows, yearly_rows, importance_rows, rules = [], [], [], [], []': 'single_rows, selected_rows, result_rows, yearly_rows, importance_rows, rules = [], [], [], [], [], {}',
    '.where((long_mom >= 0.65) & (flow >= 0.50), -1)': '.where((long_mom >= 0.65) & (flow >= 0.50))',
    '.where((long_mom >= 0.65) & short_mom.between(0.15, 0.65), -1)': '.where((long_mom >= 0.65) & short_mom.between(0.15, 0.65))',
    '.where((value >= 0.65) & (long_mom >= 0.50) & (revision >= 0.15), -1)': '.where((value >= 0.65) & (long_mom >= 0.50) & (revision >= 0.15))',
    '.where((revision >= 0.65) & (flow >= 0.50), -1)': '.where((revision >= 0.65) & (flow >= 0.50))',
    'universes = list(TARGET_N)': 'universes = ["K200", "KOSPI_EX_K200", "KOSDAQ", "TOP30_MCAP"]',
    'for buffer in (False, True):': 'for buffer in (False,):',
    'singles = pd.concat(single_rows, ignore_index=True)': 'singles = pd.concat(single_rows, ignore_index=True) if single_rows else pd.DataFrame()',
}
for old, new in repls.items():
    source = source.replace(old, new)
needle = 'scores = create_scores(dates, universe, all_factors, selected, factor_panels, basic_panels, orientation, (hgb, tree, model_cols))'
replacement = needle + '\n            keep_strategies = {"OLD4_LINEAR", "NEW4_LINEAR", "ALL8_LINEAR", "SELECTED_PRUNED", "CONSENSUS_VETO", "HGB_NONLINEAR", "MOM_FLOW_CONFIRM", "TREND_PULLBACK", "VALUE_TREND_VETO", "REVISION_FLOW"}\n            scores = {k: v for k, v in scores.items() if k in keep_strategies}'
source = source.replace(needle, replacement)
exec(compile(source, str(Path(__file__).with_name("run_all_factor_research_fast_source.py")), "exec"))
