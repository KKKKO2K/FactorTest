from __future__ import annotations

import base64
import gzip
import re
from pathlib import Path

wrapper = Path(__file__).with_name("run_all_factor_research.py").read_text(encoding="utf-8")
payload = re.search(r'base64\.b64decode\("([A-Za-z0-9+/=]+)"\)', wrapper)
source = gzip.decompress(base64.b64decode(payload.group(1))).decode("utf-8")
for i, line in enumerate(source.splitlines(), 1):
    if 405 <= i <= 430:
        print(f"{i}: {line}")
