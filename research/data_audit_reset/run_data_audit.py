from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import json
import math
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "source" / "factor_all_values"
REF = DATA / "reference_snapshots"
OUT = Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
AUDIT_STEP = 5

FACTORS = {
    "MOM1M": DATA / "단기모멘텀",
    "MOM12_1": DATA / "모멘텀(12-1)",
    "OP12_REV": DATA / "OP(12MF_1M_CHG)",
    "OPFY1_REV": DATA / "OP(FY1_1M_CHG)",
    "PBR12MF": DATA / "PBR(12MF)",
    "PER12MF": DATA / "PER(12MF)",
    "PRIVATE_FLOW": DATA / "사모수급",
    "FOREIGN_FLOW": DATA / "외국인수급",
}

REFS = {
    "basic_info": REF / "basic_info",
    "trading_amount": REF / "trading_amount",
    "universe_definition": REF / "universe_definition",
}


def read_csv(path: Path) -> pd.DataFrame:
    last = None
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Could not read {path}: {last}")


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out = {}
    if not folder.exists():
        return out
    for p in folder.iterdir():
        if not p.is_file():
            continue
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def find_col(df: pd.DataFrame, exact=(), contains=()) -> str | None:
    for c in df.columns:
        if str(c).strip() in exact:
            return c
    for c in df.columns:
        label = str(c).strip().lower()
        if any(token.lower() in label for token in contains):
            return c
    return None


def code_col(df: pd.DataFrame) -> str:
    c = find_col(df, exact=("Code", "StockCode", "종목코드", "Ticker"))
    if c is None:
        raise KeyError(f"Code column missing: {list(df.columns)}")
    return c


def norm_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return x.where(x.str.startswith("A"), "A" + x.str.zfill(6))


def numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def q(x: list[float], p: float) -> float:
    a = np.asarray([v for v in x if pd.notna(v)], dtype=float)
    return float(np.quantile(a, p)) if len(a) else np.nan


def file_inventory(name: str, files: dict[pd.Timestamp, Path], base_dates: list[pd.Timestamp]) -> dict:
    dates = list(files)
    base = set(base_dates)
    own = set(dates)
    overlap_base = [d for d in base_dates if (not dates or (d >= dates[0] and d <= dates[-1]))]
    missing = sorted(set(overlap_base) - own)
    extra = sorted(own - base)
    return {
        "dataset": name,
        "n_files": len(dates),
        "first_date": dates[0] if dates else pd.NaT,
        "last_date": dates[-1] if dates else pd.NaT,
        "missing_dates_vs_basic_within_own_span": len(missing),
        "extra_dates_vs_basic": len(extra),
        "missing_date_examples": ";".join(str(d.date()) for d in missing[:10]),
        "extra_date_examples": ";".join(str(d.date()) for d in extra[:10]),
    }


def sample_dates_from_basic(base_dates: list[pd.Timestamp]) -> list[pd.Timestamp]:
    if not base_dates:
        return []
    d = base_dates[::AUDIT_STEP]
    if base_dates[0] not in d:
        d = [base_dates[0]] + d
    if base_dates[-1] not in d:
        d = d + [base_dates[-1]]
    return sorted(set(d))


def load_basic_snapshot(path: Path) -> pd.DataFrame:
    df = read_csv(path)
    cc = code_col(df)
    market_c = find_col(df, exact=("상장된 시장",), contains=("상장된 시장", "market"))
    k_c = find_col(df, contains=("코스피200", "k200"))
    ret_c = find_col(df, exact=("수정주가수익률",), contains=("수정주가수익률", "daily_return"))
    mc_c = find_col(df, exact=("시가총액",), contains=("시가총액", "marketcap"))
    out = pd.DataFrame({"code": norm_code(df[cc])})
    out["market"] = df[market_c].astype(str).str.upper().str.strip() if market_c else ""
    out["k200"] = numeric(df[k_c]).fillna(0).astype(int) if k_c else 0
    out["ret"] = numeric(df[ret_c]) / 100.0 if ret_c else np.nan
    out["mcap"] = numeric(df[mc_c]) if mc_c else np.nan
    return out.drop_duplicates("code", keep="last").set_index("code")


def load_trading_snapshot(path: Path) -> pd.Series:
    df = read_csv(path)
    cc = code_col(df)
    vc = find_col(df, exact=("거래대금(십억원)",), contains=("거래대금", "trading"))
    if vc is None:
        return pd.Series(dtype=float)
    x = pd.Series(numeric(df[vc]).to_numpy(), index=norm_code(df[cc]))
    return x.groupby(level=0).last()


def load_factor_snapshot(path: Path) -> tuple[pd.Series, dict]:
    df = read_csv(path)
    cc = code_col(df)
    vc = find_col(df, exact=("FactorValue",), contains=("factorvalue",))
    if vc is None:
        raise KeyError(f"FactorValue missing: {path}")
    codes = norm_code(df[cc])
    vals = numeric(df[vc])
    raw_nonblank = df[vc].notna() & df[vc].astype(str).str.strip().ne("")
    nonnumeric = int((raw_nonblank & vals.isna()).sum())
    dup = int(codes.duplicated(keep=False).sum())
    s = pd.Series(vals.to_numpy(), index=codes).groupby(level=0).last()
    finite = s.dropna()
    stats = {
        "rows": len(df),
        "unique_codes": int(codes.nunique()),
        "valid_values": int(vals.notna().sum()),
        "blank_or_invalid_values": int(vals.isna().sum()),
        "blank_rate": float(vals.isna().mean()) if len(vals) else np.nan,
        "nonnumeric_nonblank": nonnumeric,
        "duplicate_code_rows": dup,
        "value_p01": float(finite.quantile(.01)) if len(finite) else np.nan,
        "value_p50": float(finite.quantile(.50)) if len(finite) else np.nan,
        "value_p99": float(finite.quantile(.99)) if len(finite) else np.nan,
        "value_std": float(finite.std(ddof=1)) if len(finite) > 1 else np.nan,
    }
    return s, stats


def universe_masks(basic: pd.DataFrame) -> dict[str, pd.Index]:
    kospi = basic.index[basic.market.eq("KOSPI")]
    kosdaq = basic.index[basic.market.eq("KOSDAQ")]
    k200 = basic.index[basic.market.eq("KOSPI") & basic.k200.eq(1)]
    ex = basic.index[basic.market.eq("KOSPI") & basic.k200.eq(0)]
    return {
        "K200": k200,
        "KOSPI_EX_K200": ex,
        "KOSDAQ": kosdaq,
        "KOSPI_ALL": kospi,
        "KOSPI_KOSDAQ_ALL": kospi.union(kosdaq),
        "KOSDAQ_PLUS_KOSPI_EX_K200": ex.union(kosdaq),
    }


def consecutive_run_stats(signatures: list[str]) -> tuple[int, int, float]:
    if not signatures:
        return 0, 0, np.nan
    changes = sum(a != b for a, b in zip(signatures[:-1], signatures[1:]))
    max_run = 1
    run = 1
    for a, b in zip(signatures[:-1], signatures[1:]):
        if a == b:
            run += 1
            max_run = max(max_run, run)
        else:
            run = 1
    unchanged_share = 1 - changes / max(1, len(signatures) - 1)
    return changes, max_run, float(unchanged_share)


def audit_universe_definition_all(files: dict[pd.Timestamp, Path]) -> tuple[pd.DataFrame, dict]:
    rows = []
    signatures = []
    prev_set = None
    for dt, path in files.items():
        df = read_csv(path)
        cc = code_col(df)
        codes = norm_code(df[cc])
        kcol = find_col(df, exact=("KOSPI200",), contains=("kospi200", "코스피200"))
        kpcol = find_col(df, exact=("KOSPI",), contains=("kospi",))
        allcol = find_col(df, exact=("ALL",), contains=("all",))
        kset = set(codes[numeric(df[kcol]).fillna(0).eq(1)]) if kcol else set()
        kpset = set(codes[numeric(df[kpcol]).fillna(0).eq(1)]) if kpcol else set()
        aset = set(codes[numeric(df[allcol]).fillna(0).eq(1)]) if allcol else set()
        sig = hashlib.sha1("|".join(sorted(kset)).encode()).hexdigest()
        signatures.append(sig)
        changed = prev_set is not None and kset != prev_set
        rows.append({"date": dt, "rows": len(df), "all_count": len(aset), "kospi_count": len(kpset), "k200_count": len(kset), "k200_changed_vs_prev_file": changed})
        prev_set = kset
    changes, max_run, unchanged_share = consecutive_run_stats(signatures)
    diag = {"n_k200_set_changes": changes, "max_consecutive_files_same_k200_set": max_run, "share_consecutive_files_same_k200_set": unchanged_share}
    return pd.DataFrame(rows), diag


def main() -> None:
    factor_files = {k: dated_files(v) for k, v in FACTORS.items()}
    ref_files = {k: dated_files(v) for k, v in REFS.items()}
    basic_dates = list(ref_files["basic_info"])
    sample_dates = sample_dates_from_basic(basic_dates)

    inventory = []
    for name, files in {**factor_files, **ref_files}.items():
        inventory.append(file_inventory(name, files, basic_dates))
    inv = pd.DataFrame(inventory)
    inv.to_csv(OUT / "file_inventory.csv", index=False, encoding="utf-8-sig")

    udf_daily, udf_diag = audit_universe_definition_all(ref_files["universe_definition"])
    udf_daily.to_csv(OUT / "universe_definition_daily.csv", index=False, encoding="utf-8-sig")

    factor_daily_rows = []
    reference_rows = []
    coverage_rows = []
    intersection_rows = []
    previous_factor = {}
    schema_counter: dict[str, Counter] = {k: Counter() for k in list(FACTORS) + list(REFS)}

    cov_agg = {(f, u): {"eligible": 0, "valid": 0, "daily": []} for f in FACTORS for u in ["K200","KOSPI_EX_K200","KOSDAQ","KOSPI_ALL","KOSPI_KOSDAQ_ALL","KOSDAQ_PLUS_KOSPI_EX_K200"]}
    all8_agg = {u: {"eligible": 0, "valid_all8": 0, "daily": []} for u in ["K200","KOSPI_EX_K200","KOSDAQ","KOSPI_ALL","KOSPI_KOSDAQ_ALL","KOSDAQ_PLUS_KOSPI_EX_K200"]}

    for dt in sample_dates:
        if dt not in ref_files["basic_info"]:
            continue
        bpath = ref_files["basic_info"][dt]
        braw = read_csv(bpath)
        schema_counter["basic_info"]["|".join(map(str, braw.columns))] += 1
        basic = load_basic_snapshot(bpath)
        masks = universe_masks(basic)

        t = load_trading_snapshot(ref_files["trading_amount"][dt]) if dt in ref_files["trading_amount"] else pd.Series(dtype=float)
        if dt in ref_files["trading_amount"]:
            traw = read_csv(ref_files["trading_amount"][dt])
            schema_counter["trading_amount"]["|".join(map(str, traw.columns))] += 1
        if dt in ref_files["universe_definition"]:
            uraw = read_csv(ref_files["universe_definition"][dt])
            schema_counter["universe_definition"]["|".join(map(str, uraw.columns))] += 1
            ucc = code_col(uraw)
            ucodes = norm_code(uraw[ucc])
            ukcol = find_col(uraw, exact=("KOSPI200",), contains=("kospi200", "코스피200"))
            ukps = find_col(uraw, exact=("KOSPI",), contains=("kospi",))
            u_k200 = set(ucodes[numeric(uraw[ukcol]).fillna(0).eq(1)]) if ukcol else set()
            u_kospi = set(ucodes[numeric(uraw[ukps]).fillna(0).eq(1)]) if ukps else set()
        else:
            u_k200, u_kospi = set(), set()

        b_k200 = set(masks["K200"])
        b_kospi = set(masks["KOSPI_ALL"])
        listed = masks["KOSPI_KOSDAQ_ALL"]
        reference_rows.append({
            "date": dt,
            "basic_rows": len(basic),
            "listed_kospi": len(masks["KOSPI_ALL"]),
            "listed_kosdaq": len(masks["KOSDAQ"]),
            "basic_k200": len(masks["K200"]),
            "udf_kospi": len(u_kospi),
            "udf_k200": len(u_k200),
            "k200_symmetric_difference": len(b_k200 ^ u_k200) if u_k200 else np.nan,
            "kospi_symmetric_difference": len(b_kospi ^ u_kospi) if u_kospi else np.nan,
            "listed_return_coverage": float(basic.ret.reindex(listed).notna().mean()) if len(listed) else np.nan,
            "listed_mcap_positive_coverage": float((basic.mcap.reindex(listed) > 0).mean()) if len(listed) else np.nan,
            "listed_trading_amount_coverage": float(t.reindex(listed).notna().mean()) if len(listed) else np.nan,
            "listed_trading_positive_share": float((t.reindex(listed) > 0).mean()) if len(listed) else np.nan,
            "daily_return_abs_gt_50pct": int((basic.ret.reindex(listed).abs() > .50).sum()),
            "daily_return_le_minus100pct": int((basic.ret.reindex(listed) <= -1).sum()),
            "k200_flag_outside_kospi": int((basic.k200.eq(1) & ~basic.market.eq("KOSPI")).sum()),
        })

        fseries = {}
        for factor, files in factor_files.items():
            if dt not in files:
                continue
            rawdf = read_csv(files[dt])
            schema_counter[factor]["|".join(map(str, rawdf.columns))] += 1
            s, st = load_factor_snapshot(files[dt])
            prev = previous_factor.get(factor)
            if prev is not None:
                z = pd.concat([prev.rename("prev"), s.rename("cur")], axis=1).dropna()
                unchanged = float(np.isclose(z.prev, z.cur, rtol=0, atol=1e-12).mean()) if len(z) else np.nan
                rankcorr = float(z.prev.rank().corr(z.cur.rank())) if len(z) >= 10 else np.nan
            else:
                unchanged, rankcorr = np.nan, np.nan
            previous_factor[factor] = s
            fseries[factor] = s
            factor_daily_rows.append({"date": dt, "factor": factor, **st, "unchanged_share_vs_prev_sample": unchanged, "rank_corr_vs_prev_sample": rankcorr})
            for u, codes in masks.items():
                denom = len(codes)
                valid = int(s.reindex(codes).notna().sum())
                ratio = valid / denom if denom else np.nan
                cov_agg[(factor, u)]["eligible"] += denom
                cov_agg[(factor, u)]["valid"] += valid
                if pd.notna(ratio): cov_agg[(factor, u)]["daily"].append(ratio)

        if len(fseries) == len(FACTORS):
            all8 = pd.DataFrame(fseries).notna().all(axis=1)
            for u, codes in masks.items():
                denom = len(codes)
                valid = int(all8.reindex(codes).fillna(False).sum())
                ratio = valid / denom if denom else np.nan
                all8_agg[u]["eligible"] += denom
                all8_agg[u]["valid_all8"] += valid
                if pd.notna(ratio): all8_agg[u]["daily"].append(ratio)
                intersection_rows.append({"date": dt, "universe": u, "eligible": denom, "valid_all8": valid, "coverage": ratio})

    fd = pd.DataFrame(factor_daily_rows)
    fd.to_csv(OUT / "factor_daily_quality_sampled.csv", index=False, encoding="utf-8-sig")
    rd = pd.DataFrame(reference_rows)
    rd.to_csv(OUT / "reference_quality_sampled.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(intersection_rows).to_csv(OUT / "all8_intersection_daily_sampled.csv", index=False, encoding="utf-8-sig")

    for (factor, u), a in cov_agg.items():
        coverage_rows.append({
            "factor": factor, "universe": u,
            "weighted_coverage": a["valid"] / a["eligible"] if a["eligible"] else np.nan,
            "median_daily_coverage": float(np.median(a["daily"])) if a["daily"] else np.nan,
            "p10_daily_coverage": q(a["daily"], .10),
            "p90_daily_coverage": q(a["daily"], .90),
            "sampled_eligible_obs": a["eligible"], "sampled_valid_obs": a["valid"],
        })
    covdf = pd.DataFrame(coverage_rows)
    covdf.to_csv(OUT / "coverage_by_factor_universe.csv", index=False, encoding="utf-8-sig")

    all8_rows = []
    for u, a in all8_agg.items():
        all8_rows.append({
            "universe": u,
            "weighted_all8_coverage": a["valid_all8"] / a["eligible"] if a["eligible"] else np.nan,
            "median_daily_all8_coverage": float(np.median(a["daily"])) if a["daily"] else np.nan,
            "p10_daily_all8_coverage": q(a["daily"], .10),
            "p90_daily_all8_coverage": q(a["daily"], .90),
            "sampled_eligible_obs": a["eligible"], "sampled_valid_all8_obs": a["valid_all8"],
        })
    all8df = pd.DataFrame(all8_rows)
    all8df.to_csv(OUT / "all8_intersection_by_universe.csv", index=False, encoding="utf-8-sig")

    schema_rows = []
    for name, cnt in schema_counter.items():
        for schema, n in cnt.most_common():
            schema_rows.append({"dataset": name, "sampled_files_with_schema": n, "columns": schema})
    pd.DataFrame(schema_rows).to_csv(OUT / "schema_variants_sampled.csv", index=False, encoding="utf-8-sig")

    # Aggregate factor content quality.
    fq_rows = []
    for factor, g in fd.groupby("factor"):
        fq_rows.append({
            "factor": factor, "sampled_files": len(g),
            "median_rows": float(g.rows.median()), "p10_rows": float(g.rows.quantile(.10)), "p90_rows": float(g.rows.quantile(.90)),
            "weighted_blank_rate": float(g.blank_or_invalid_values.sum() / g.rows.sum()) if g.rows.sum() else np.nan,
            "files_with_nonnumeric_nonblank": int((g.nonnumeric_nonblank > 0).sum()),
            "files_with_duplicate_code_rows": int((g.duplicate_code_rows > 0).sum()),
            "median_rank_corr_vs_prev_5d_sample": float(g.rank_corr_vs_prev_sample.median()),
            "median_unchanged_share_vs_prev_5d_sample": float(g.unchanged_share_vs_prev_sample.median()),
        })
    fq = pd.DataFrame(fq_rows)
    fq.to_csv(OUT / "factor_quality_summary.csv", index=False, encoding="utf-8-sig")

    # Markdown summary.
    lines = ["# Source Data Audit — Reset", "", f"Content quality sampled every {AUDIT_STEP} basic-info trading dates, plus endpoints. File/date inventory is exhaustive.", ""]
    lines += ["## 1. File inventory", "", "| Dataset | Files | First | Last | Missing vs basic calendar |", "|---|---:|---|---|---:|"]
    for _, r in inv.iterrows():
        lines.append(f"| {r.dataset} | {int(r.n_files)} | {str(r.first_date)[:10]} | {str(r.last_date)[:10]} | {int(r.missing_dates_vs_basic_within_own_span)} |")

    lines += ["", "## 2. Factor content quality", "", "| Factor | Blank/invalid | Median rows | 5D rank persistence | Exact unchanged share |", "|---|---:|---:|---:|---:|"]
    for _, r in fq.iterrows():
        lines.append(f"| {r.factor} | {r.weighted_blank_rate:.1%} | {r.median_rows:.0f} | {r.median_rank_corr_vs_prev_5d_sample:+.3f} | {r.median_unchanged_share_vs_prev_5d_sample:.1%} |")

    lines += ["", "## 3. Factor coverage by primitive universe", "", "Weighted valid FactorValue coverage across sampled dates:", "", "| Factor | K200 | KOSPI ex-K200 | KOSDAQ |", "|---|---:|---:|---:|"]
    for factor in FACTORS:
        vals = []
        for u in ("K200", "KOSPI_EX_K200", "KOSDAQ"):
            z = covdf[(covdf.factor == factor) & (covdf.universe == u)]
            vals.append(z.iloc[0].weighted_coverage if len(z) else np.nan)
        lines.append(f"| {factor} | {vals[0]:.1%} | {vals[1]:.1%} | {vals[2]:.1%} |")

    lines += ["", "## 4. All-8-factor intersection", "", "| Universe | Weighted coverage | Median daily | P10 daily |", "|---|---:|---:|---:|"]
    for _, r in all8df.iterrows():
        lines.append(f"| {r.universe} | {r.weighted_all8_coverage:.1%} | {r.median_daily_all8_coverage:.1%} | {r.p10_daily_all8_coverage:.1%} |")

    if len(rd):
        lines += ["", "## 5. Reference-data quality", ""]
        lines += [f"- Median listed KOSPI names: {rd.listed_kospi.median():.0f}", f"- Median listed KOSDAQ names: {rd.listed_kosdaq.median():.0f}", f"- Median basic-info K200 count: {rd.basic_k200.median():.0f}", f"- Median basic vs universe_definition K200 symmetric difference: {rd.k200_symmetric_difference.dropna().median():.0f}", f"- Median listed daily-return coverage: {rd.listed_return_coverage.median():.1%}", f"- Median listed positive-market-cap coverage: {rd.listed_mcap_positive_coverage.median():.1%}", f"- Median listed trading-amount coverage: {rd.listed_trading_amount_coverage.median():.1%}", f"- Median listed positive trading-amount share: {rd.listed_trading_positive_share.median():.1%}"]
        lines += [f"- universe_definition K200 set changes across all files: {udf_diag['n_k200_set_changes']}", f"- Longest consecutive files with identical K200 set: {udf_diag['max_consecutive_files_same_k200_set']}", f"- Share of consecutive universe-definition files with unchanged K200 set: {udf_diag['share_consecutive_files_same_k200_set']:.1%}"]

    lines += ["", "## Audit interpretation rules", "", "- `Blank/invalid` includes empty and non-numeric FactorValue cells.", "- Coverage denominators use point-in-time KOSPI/KOSDAQ labels and K200 flag in `basic_info`, matching the current research loaders.", "- `universe_definition` is audited independently to detect membership inconsistencies.", "- The all-8 intersection is important for any model that requires every factor simultaneously; single-factor research should not unnecessarily impose this intersection.", "- Factor-value scale is not compared across factors; only within-factor numeric quality and cross-sectional coverage are audited."]
    (OUT / "DATA_AUDIT_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
