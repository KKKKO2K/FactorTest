from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "source" / "factor_all_values"
OUT = ROOT / "analysis" / "all_factor_inventory"
OUT.mkdir(parents=True, exist_ok=True)
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
EXCLUDE = {"reference_snapshots"}


def read_csv(path: Path) -> pd.DataFrame:
    last = None
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Could not read {path}: {last}")


def dated_files(folder: Path):
    out = []
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out.append((pd.Timestamp(m.group(1)), p))
    return sorted(out)


def find_code_col(df: pd.DataFrame):
    for c in df.columns:
        if str(c).strip().lower() in {"code", "stockcode", "종목코드", "ticker"}:
            return c
    return None


def factor_value_col(df: pd.DataFrame, code_col):
    for c in df.columns:
        if str(c).strip().lower() == "factorvalue":
            return c
    candidates = []
    for c in df.columns:
        if c == code_col or str(c).lower().startswith("unnamed") or str(c).strip().lower() in {"sourcerow"}:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        if s.notna().sum() >= 20 and s.nunique(dropna=True) >= 5:
            candidates.append((c, int(s.notna().sum())))
    return max(candidates, key=lambda x: x[1])[0] if candidates else None


def inspect_file(path: Path):
    df = read_csv(path)
    code_col = find_code_col(df)
    val_col = factor_value_col(df, code_col)
    vals = pd.to_numeric(df[val_col], errors="coerce") if val_col is not None else pd.Series(dtype=float)
    return {
        "rows": len(df),
        "columns": json.dumps([str(c) for c in df.columns], ensure_ascii=False),
        "code_col": str(code_col) if code_col is not None else "",
        "value_col": str(val_col) if val_col is not None else "",
        "n_valid": int(vals.notna().sum()),
        "n_unique": int(vals.nunique(dropna=True)),
        "min": float(vals.min()) if vals.notna().any() else None,
        "max": float(vals.max()) if vals.notna().any() else None,
    }


def main():
    rows = []
    for folder in sorted(p for p in DATA.iterdir() if p.is_dir() and p.name not in EXCLUDE):
        files = dated_files(folder)
        if not files:
            continue
        first_dt, first_path = files[0]
        last_dt, last_path = files[-1]
        first = inspect_file(first_path)
        last = inspect_file(last_path)
        rows.append({
            "factor": folder.name,
            "n_files": len(files),
            "first_date": first_dt.date().isoformat(),
            "last_date": last_dt.date().isoformat(),
            "first_rows": first["rows"],
            "first_valid": first["n_valid"],
            "last_rows": last["rows"],
            "last_valid": last["n_valid"],
            "value_col": last["value_col"],
            "columns": last["columns"],
            "last_min": last["min"],
            "last_max": last["max"],
        })
    inv = pd.DataFrame(rows).sort_values("factor")
    inv.to_csv(OUT / "factor_inventory.csv", index=False, encoding="utf-8-sig")
    (OUT / "summary.md").write_text(
        "# All-factor inventory\n\n" + inv.to_markdown(index=False), encoding="utf-8"
    )
    print(inv.to_string(index=False))


if __name__ == "__main__":
    main()
