from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

import run_data_audit as a

OUT = Path(__file__).resolve().parent / "results_coverage_bias"
OUT.mkdir(parents=True, exist_ok=True)

PRIMITIVE = ("K200", "KOSPI_EX_K200", "KOSDAQ")


def main() -> None:
    factor_files = {k: a.dated_files(v) for k, v in a.FACTORS.items()}
    ref_files = {k: a.dated_files(v) for k, v in a.REFS.items()}
    basic_dates = list(ref_files["basic_info"])
    dates = a.sample_dates_from_basic(basic_dates)

    daily = []
    size_rows = []
    set_rows = []
    all8_year_rows = []

    for dt in dates:
        if dt not in ref_files["basic_info"]:
            continue
        basic = a.load_basic_snapshot(ref_files["basic_info"][dt])
        masks = a.universe_masks(basic)
        fvals = {}
        frows = {}
        for f, files in factor_files.items():
            if dt not in files:
                continue
            df = a.read_csv(files[dt])
            cc = a.code_col(df)
            vc = a.find_col(df, exact=("FactorValue",), contains=("factorvalue",))
            codes = a.norm_code(df[cc])
            vals = a.numeric(df[vc])
            rowset = set(codes)
            s = pd.Series(vals.to_numpy(), index=codes).groupby(level=0).last()
            fvals[f] = s
            frows[f] = rowset

        if not fvals:
            continue

        # Cross-factor row-universe similarity.
        names = sorted(frows)
        jac = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                x, y = frows[names[i]], frows[names[j]]
                if x or y:
                    jac.append(len(x & y) / len(x | y))
        set_rows.append({
            "date": dt,
            "n_factor_files": len(names),
            "median_pairwise_rowset_jaccard": float(np.median(jac)) if jac else np.nan,
            "min_pairwise_rowset_jaccard": float(np.min(jac)) if jac else np.nan,
        })

        for u in PRIMITIVE:
            codes = masks[u]
            if not len(codes):
                continue
            mc = basic.mcap.reindex(codes)
            # quintile 1=smallest, 5=largest; ties tolerated.
            rank = mc.rank(pct=True, method="average")
            bucket = pd.cut(rank, bins=[0, .2, .4, .6, .8, 1.0000001], labels=[1,2,3,4,5], include_lowest=True)

            for f in a.FACTORS:
                if f not in fvals:
                    continue
                row_membership = pd.Series(pd.Index(codes).isin(frows[f]), index=codes)
                valid = fvals[f].reindex(codes).notna()
                daily.append({
                    "date": dt, "year": dt.year, "universe": u, "factor": f,
                    "eligible": len(codes),
                    "row_members": int(row_membership.sum()),
                    "valid_values": int(valid.sum()),
                    "row_membership_coverage": float(row_membership.mean()),
                    "valid_value_coverage": float(valid.mean()),
                    "valid_given_row": float(valid.sum() / row_membership.sum()) if row_membership.sum() else np.nan,
                })
                for b in range(1, 6):
                    ix = bucket.index[bucket.eq(b)]
                    if not len(ix):
                        continue
                    size_rows.append({
                        "date": dt, "year": dt.year, "universe": u, "factor": f, "mcap_quintile": b,
                        "eligible": len(ix),
                        "row_membership_coverage": float(row_membership.reindex(ix).mean()),
                        "valid_value_coverage": float(valid.reindex(ix).mean()),
                    })

            if len(fvals) == len(a.FACTORS):
                all8 = pd.DataFrame({f: s.reindex(codes) for f, s in fvals.items()}).notna().all(axis=1)
                all8_year_rows.append({"date": dt, "year": dt.year, "universe": u, "eligible": len(codes), "valid_all8": int(all8.sum()), "coverage": float(all8.mean())})

        # Is the common factor row universe approximately a top-market-cap screen?
        if "MOM1M" in frows:
            listed = masks["KOSPI_KOSDAQ_ALL"]
            rowset = set(listed) & frows["MOM1M"]
            n = len(rowset)
            topn = set(basic.mcap.reindex(listed).dropna().sort_values(ascending=False).head(n).index)
            union = rowset | topn
            set_rows[-1].update({
                "mom1m_rows_in_listed": n,
                "top_mcap_n_jaccard": len(rowset & topn) / len(union) if union else np.nan,
                "share_factor_rows_in_top_mcap_n": len(rowset & topn) / n if n else np.nan,
                "median_mcap_pct_rank_of_factor_rows": float(basic.mcap.reindex(listed).rank(pct=True).reindex(list(rowset)).median()) if n else np.nan,
            })

    d = pd.DataFrame(daily)
    s = pd.DataFrame(size_rows)
    sets = pd.DataFrame(set_rows)
    a8 = pd.DataFrame(all8_year_rows)
    d.to_csv(OUT / "coverage_daily_sampled.csv", index=False, encoding="utf-8-sig")
    s.to_csv(OUT / "size_bias_daily_sampled.csv", index=False, encoding="utf-8-sig")
    sets.to_csv(OUT / "factor_rowset_similarity.csv", index=False, encoding="utf-8-sig")
    a8.to_csv(OUT / "all8_daily_sampled.csv", index=False, encoding="utf-8-sig")

    yearly = d.groupby(["year","universe","factor"], as_index=False).agg(
        median_row_membership_coverage=("row_membership_coverage","median"),
        median_valid_value_coverage=("valid_value_coverage","median"),
        median_valid_given_row=("valid_given_row","median"),
        sampled_dates=("date","count"),
    )
    yearly.to_csv(OUT / "coverage_by_year.csv", index=False, encoding="utf-8-sig")

    size = s.groupby(["universe","factor","mcap_quintile"], as_index=False).agg(
        median_row_membership_coverage=("row_membership_coverage","median"),
        median_valid_value_coverage=("valid_value_coverage","median"),
    )
    size.to_csv(OUT / "coverage_by_mcap_quintile.csv", index=False, encoding="utf-8-sig")

    a8y = a8.groupby(["year","universe"], as_index=False).agg(median_all8_coverage=("coverage","median"), sampled_dates=("date","count"))
    a8y.to_csv(OUT / "all8_coverage_by_year.csv", index=False, encoding="utf-8-sig")

    # Compact summary.
    lines = ["# Factor Coverage Bias Audit", "", "## Row universe vs value availability", ""]
    overall = d.groupby(["universe","factor"], as_index=False).agg(
        row_cov=("row_membership_coverage","median"), valid_cov=("valid_value_coverage","median"), valid_given_row=("valid_given_row","median"))
    for u in PRIMITIVE:
        lines += [f"### {u}", "", "| Factor | Row membership | Valid value | Valid given row |", "|---|---:|---:|---:|"]
        for _, r in overall[overall.universe.eq(u)].iterrows():
            lines.append(f"| {r.factor} | {r.row_cov:.1%} | {r.valid_cov:.1%} | {r.valid_given_row:.1%} |")
        lines.append("")

    lines += ["## Size bias", "", "Median valid-value coverage by market-cap quintile (Q1 smallest, Q5 largest):", ""]
    for u in PRIMITIVE:
        lines += [f"### {u}", "", "| Factor | Q1 | Q2 | Q3 | Q4 | Q5 |", "|---|---:|---:|---:|---:|---:|"]
        for f in a.FACTORS:
            z = size[(size.universe.eq(u)) & (size.factor.eq(f))]
            vals = []
            for b in range(1, 6):
                qv = z[z.mcap_quintile.eq(b)]
                vals.append(qv.iloc[0].median_valid_value_coverage if len(qv) else np.nan)
            lines.append(f"| {f} | " + " | ".join(f"{v:.1%}" for v in vals) + " |")
        lines.append("")

    lines += ["## Common row-set diagnostics", ""]
    if len(sets):
        lines += [
            f"- Median pairwise Jaccard across the 8 factor row sets: {sets.median_pairwise_rowset_jaccard.median():.3f}",
            f"- Median minimum pairwise Jaccard on a date: {sets.min_pairwise_rowset_jaccard.median():.3f}",
            f"- MOM1M row set vs same-N top market-cap set median Jaccard: {sets.top_mcap_n_jaccard.median():.3f}",
            f"- Median share of MOM1M listed rows that are in same-N top market-cap set: {sets.share_factor_rows_in_top_mcap_n.median():.1%}",
            f"- Median market-cap percentile of MOM1M-covered listed stocks: {sets.median_mcap_pct_rank_of_factor_rows.median():.1%}",
        ]

    lines += ["", "## All-8 intersection by year", ""]
    for u in PRIMITIVE:
        z = a8y[a8y.universe.eq(u)]
        lines.append(f"### {u}")
        for _, r in z.iterrows():
            lines.append(f"- {int(r.year)}: {r.median_all8_coverage:.1%}")
        lines.append("")

    (OUT / "COVERAGE_BIAS_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
