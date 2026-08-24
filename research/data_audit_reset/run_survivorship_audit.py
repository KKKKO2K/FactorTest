from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np

import run_data_audit as a

OUT = Path(__file__).resolve().parent / "results_survivorship"
OUT.mkdir(parents=True, exist_ok=True)


def raw_basic(path: Path) -> pd.DataFrame:
    df = a.read_csv(path)
    cc = a.code_col(df)
    nc = a.find_col(df, exact=("Name", "StockName", "종목명"), contains=("name", "종목명"))
    market_c = a.find_col(df, exact=("상장된 시장",), contains=("상장된 시장", "market"))
    k_c = a.find_col(df, contains=("코스피200", "k200"))
    out = pd.DataFrame({"code": a.norm_code(df[cc])})
    out["name"] = df[nc].astype(str) if nc else ""
    out["market"] = df[market_c].astype(str).str.upper().str.strip() if market_c else ""
    out["k200"] = a.numeric(df[k_c]).fillna(0).astype(int) if k_c else 0
    return out.drop_duplicates("code", keep="last").set_index("code")


def listed_set(x: pd.DataFrame) -> set[str]:
    return set(x.index[x.market.isin(["KOSPI", "KOSDAQ"])])


def factor_rowset(path: Path) -> set[str]:
    df = a.read_csv(path)
    return set(a.norm_code(df[a.code_col(df)]))


def main() -> None:
    refs = {k: a.dated_files(v) for k, v in a.REFS.items()}
    factors = {k: a.dated_files(v) for k, v in a.FACTORS.items()}
    dates = list(refs["basic_info"])
    first, last = dates[0], dates[-1]
    b0, b1 = raw_basic(refs["basic_info"][first]), raw_basic(refs["basic_info"][last])
    s0, s1 = listed_set(b0), listed_set(b1)
    entries, exits = s1 - s0, s0 - s1

    rows = []
    # One snapshot nearest each year-end.
    for year in sorted(set(d.year for d in dates)):
        ds = [d for d in dates if d.year == year]
        dt = ds[-1]
        b = raw_basic(refs["basic_info"][dt])
        s = listed_set(b)
        rows.append({
            "date": dt, "year": year, "basic_rows": len(b), "listed": len(s),
            "kospi": int(b.market.eq("KOSPI").sum()), "kosdaq": int(b.market.eq("KOSDAQ").sum()),
            "k200": int((b.market.eq("KOSPI") & b.k200.eq(1)).sum()),
            "listed_overlap_with_final": len(s & s1),
            "listed_not_in_final": len(s - s1),
            "final_listed_not_yet_listed": len(s1 - s),
        })
    annual = pd.DataFrame(rows)
    annual.to_csv(OUT / "annual_universe_lineage.csv", index=False, encoding="utf-8-sig")

    # Basic master-row behavior.
    master_j = len(set(b0.index) & set(b1.index)) / len(set(b0.index) | set(b1.index))
    exit_still_present_as_row_final = sum(c in b1.index for c in exits)
    entry_already_present_as_row_first = sum(c in b0.index for c in entries)

    # Factor row universe turnover between endpoints and relation to listed entries/exits.
    frows = []
    for f in a.FACTORS:
        r0 = factor_rowset(factors[f][first]) if first in factors[f] else set()
        r1 = factor_rowset(factors[f][last]) if last in factors[f] else set()
        union = r0 | r1
        frows.append({
            "factor": f, "first_rows": len(r0), "last_rows": len(r1),
            "endpoint_jaccard": len(r0 & r1) / len(union) if union else np.nan,
            "first_only": len(r0 - r1), "last_only": len(r1 - r0),
            "first_factor_rows_that_later_exit_listing": len(r0 & exits),
            "last_factor_rows_that_are_post2016_entries": len(r1 & entries),
        })
    fdf = pd.DataFrame(frows)
    fdf.to_csv(OUT / "factor_rowset_endpoint_turnover.csv", index=False, encoding="utf-8-sig")

    # Examples for human inspection.
    def examples(codes: set[str], frame: pd.DataFrame, n=25):
        vals = []
        for c in sorted(codes)[:n]:
            vals.append({"code": c, "name": frame.loc[c, "name"] if c in frame.index else "", "market": frame.loc[c, "market"] if c in frame.index else ""})
        return vals
    pd.DataFrame(examples(exits, b0)).to_csv(OUT / "examples_2016_listed_not_final.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(examples(entries, b1)).to_csv(OUT / "examples_final_listed_not_2016.csv", index=False, encoding="utf-8-sig")

    lines = ["# Survivorship / Universe Lineage Audit", "",
             f"- First snapshot: {first.date()}", f"- Last snapshot: {last.date()}",
             f"- Basic master rows first/last: {len(b0)} / {len(b1)}", f"- Basic master row-set endpoint Jaccard: {master_j:.3f}",
             f"- Listed KOSPI+KOSDAQ first/last: {len(s0)} / {len(s1)}",
             f"- 2016-listed names not listed at final date: {len(exits)}",
             f"- Final-listed names not listed in 2016: {len(entries)}",
             f"- Of 2016-listed exits, still present as rows in final basic master: {exit_still_present_as_row_final}/{len(exits)}",
             f"- Of post-2016 listed entries, already present as rows in first basic master: {entry_already_present_as_row_first}/{len(entries)}",
             "", "Interpretation: a static/superset master row list is not itself survivorship bias if historical market-membership flags are point-in-time. The key evidence is whether both later entrants and later exits are represented with changing historical market status.",
             "", "## Factor row-set endpoint turnover", "", "| Factor | First | Last | Endpoint Jaccard | First-only | Last-only |", "|---|---:|---:|---:|---:|---:|"]
    for _, r in fdf.iterrows():
        lines.append(f"| {r.factor} | {int(r.first_rows)} | {int(r.last_rows)} | {r.endpoint_jaccard:.3f} | {int(r.first_only)} | {int(r.last_only)} |")
    lines += ["", "## Annual listed-universe lineage", "", "| Year | Listed | KOSPI | KOSDAQ | K200 | Names later absent by final | Final names not yet listed |", "|---|---:|---:|---:|---:|---:|---:|"]
    for _, r in annual.iterrows():
        lines.append(f"| {int(r.year)} | {int(r.listed)} | {int(r.kospi)} | {int(r.kosdaq)} | {int(r.k200)} | {int(r.listed_not_in_final)} | {int(r.final_listed_not_yet_listed)} |")
    (OUT / "SURVIVORSHIP_AUDIT_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
