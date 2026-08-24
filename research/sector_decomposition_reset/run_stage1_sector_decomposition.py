from __future__ import annotations

from pathlib import Path
import math
import re

import numpy as np
import pandas as pd

from wics_embedded import wics_map

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "source" / "factor_all_values"
BASIC = DATA / "reference_snapshots" / "basic_info"
OUT = Path(__file__).resolve().parent / "results_stage1"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = {
    "MOM1M": (DATA / "단기모멘텀", +1),
    "MOM12_1": (DATA / "모멘텀(12-1)", +1),
    "OP12_REV": (DATA / "OP(12MF_1M_CHG)", +1),
    "OPFY1_REV": (DATA / "OP(FY1_1M_CHG)", +1),
    "PBR12MF": (DATA / "PBR(12MF)", -1),
    "PER12MF": (DATA / "PER(12MF)", -1),
    "PRIVATE_FLOW": (DATA / "사모수급", +1),
    "FOREIGN_FLOW": (DATA / "외국인수급", +1),
}

ERA_ORDER = ["2016-19", "2020-22", "2023-24", "2025", "2026", "FULL"]


def read_csv(path: Path) -> pd.DataFrame:
    last = None
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Could not read {path}: {last}")


def norm_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return x.where(x.str.startswith("A"), "A" + x.str.zfill(6))


def numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def find_col(df: pd.DataFrame, exact=(), contains=()) -> str | None:
    for c in df.columns:
        if str(c).strip() in exact:
            return c
    for c in df.columns:
        z = str(c).strip().lower()
        if any(t.lower() in z for t in contains):
            return c
    return None


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out = {}
    pat = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
    for p in folder.iterdir():
        if not p.is_file():
            continue
        m = pat.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def load_basic(path: Path) -> pd.DataFrame:
    df = read_csv(path)
    cc = find_col(df, exact=("Code", "StockCode", "종목코드"))
    market_c = find_col(df, exact=("상장된 시장",), contains=("상장된 시장", "market"))
    k200_c = find_col(df, contains=("코스피200", "k200"))
    ret_c = find_col(df, exact=("수정주가수익률",), contains=("수정주가수익률", "return"))
    if cc is None or market_c is None or k200_c is None or ret_c is None:
        raise KeyError(f"Missing required basic columns in {path.name}: {list(df.columns)}")
    out = pd.DataFrame({
        "code": norm_code(df[cc]),
        "market": df[market_c].astype(str).str.upper().str.strip(),
        "k200": numeric(df[k200_c]).fillna(0).astype(int),
        "ret": numeric(df[ret_c]) / 100.0,
    })
    return out.drop_duplicates("code", keep="last").set_index("code")


def load_factor(path: Path, direction: int) -> pd.DataFrame:
    df = read_csv(path)
    cc = find_col(df, exact=("StockCode", "Code", "종목코드"))
    vc = find_col(df, exact=("FactorValue",), contains=("factorvalue",))
    if cc is None or vc is None:
        raise KeyError(f"Missing factor columns in {path}")
    out = pd.DataFrame({"code": norm_code(df[cc]), "value": numeric(df[vc])})
    out = out.drop_duplicates("code", keep="last").dropna(subset=["value"])
    out["score"] = direction * out["value"]
    return out.set_index("code")


def forward_block_return(paths: list[Path]) -> pd.Series:
    acc: pd.Series | None = None
    for p in paths:
        b = load_basic(p)["ret"]
        if acc is None:
            acc = (1.0 + b)
        else:
            idx = acc.index.union(b.index)
            acc = acc.reindex(idx).fillna(1.0) * (1.0 + b.reindex(idx).fillna(0.0))
    assert acc is not None
    return acc - 1.0


def masks(signal_basic: pd.DataFrame, eligible: pd.Index) -> dict[str, pd.Index]:
    b = signal_basic.reindex(eligible)
    kospi = b.index[b.market.eq("KOSPI")]
    kosdaq = b.index[b.market.eq("KOSDAQ")]
    k200 = b.index[b.market.eq("KOSPI") & b.k200.eq(1)]
    ex = b.index[b.market.eq("KOSPI") & b.k200.eq(0)]
    return {
        "K200": k200,
        "KOSPI_EX_K200": ex,
        "KOSDAQ": kosdaq,
        "KOSPI_ALL": kospi,
        "KOSPI_KOSDAQ_ALL": kospi.union(kosdaq),
        "KOSDAQ_PLUS_KOSPI_EX_K200": ex.union(kosdaq),
    }


def hhi_from_counts(counts: pd.Series) -> float:
    n = counts.sum()
    if n <= 0:
        return np.nan
    w = counts / n
    return float((w * w).sum())


def calc_one(x: pd.DataFrame) -> tuple[dict, list[dict]] | None:
    # x: code index, score, fwd, sector
    x = x.dropna(subset=["score", "fwd"]).copy()
    n = len(x)
    if n < 10:
        return None
    n_side = max(1, int(math.floor(0.20 * n)))
    if 2 * n_side >= n:
        return None
    x = x.sort_values(["score"], ascending=False, kind="mergesort")
    top = x.iloc[:n_side].copy()
    bot = x.iloc[-n_side:].copy()

    top_ret = float(top.fwd.mean())
    bot_ret = float(bot.fwd.mean())
    raw = top_ret - bot_ret

    sector_bench = x.groupby("sector", dropna=False).fwd.mean()
    top_n = top.groupby("sector", dropna=False).size()
    bot_n = bot.groupby("sector", dropna=False).size()
    sectors = sector_bench.index.union(top_n.index).union(bot_n.index)

    alloc = 0.0
    within = 0.0
    contrib_rows = []
    for s in sectors:
        rs = float(sector_bench.get(s, np.nan))
        nt = int(top_n.get(s, 0))
        nb = int(bot_n.get(s, 0))
        wt = nt / n_side
        wb = nb / n_side
        rt = float(top.loc[top.sector.eq(s), "fwd"].mean()) if nt else np.nan
        rb = float(bot.loc[bot.sector.eq(s), "fwd"].mean()) if nb else np.nan
        a = (wt - wb) * rs
        sel_t = wt * (rt - rs) if nt else 0.0
        sel_b = -wb * (rb - rs) if nb else 0.0
        sel = sel_t + sel_b
        alloc += a
        within += sel
        contrib_rows.append({
            "sector": s,
            "top_weight": wt,
            "bottom_weight": wb,
            "sector_benchmark_return": rs,
            "allocation_contribution": a,
            "within_selection_contribution": sel,
        })

    identity_error = raw - alloc - within

    top_counts = top.groupby("sector").size()
    bot_counts = bot.groupby("sector").size()
    active_l1 = 0.5 * sum(abs(float(top_n.get(s, 0))/n_side - float(bot_n.get(s, 0))/n_side) for s in sectors)

    # sector-neutral portfolio: same count from top and bottom within each sector
    ntops = []
    nbots = []
    neutral_sector_count = 0
    for s, g in x.groupby("sector", dropna=False):
        g = g.sort_values("score", ascending=False, kind="mergesort")
        ns = len(g)
        if ns < 5:
            continue
        k = max(1, int(math.floor(0.20 * ns)))
        if 2 * k > ns:
            continue
        ntops.append(g.iloc[:k])
        nbots.append(g.iloc[-k:])
        neutral_sector_count += 1
    if ntops and nbots:
        ntop = pd.concat(ntops, axis=0)
        nbot = pd.concat(nbots, axis=0)
        neutral_top = float(ntop.fwd.mean())
        neutral_bottom = float(nbot.fwd.mean())
        neutral_ls = neutral_top - neutral_bottom
        neutral_n_side = len(ntop)
    else:
        neutral_top = neutral_bottom = neutral_ls = np.nan
        neutral_n_side = 0

    metrics = {
        "n_valid": n,
        "n_side": n_side,
        "raw_top_return": top_ret,
        "raw_bottom_return": bot_ret,
        "raw_ls": raw,
        "allocation": alloc,
        "within_selection": within,
        "identity_error": identity_error,
        "neutral_top_return": neutral_top,
        "neutral_bottom_return": neutral_bottom,
        "neutral_ls": neutral_ls,
        "neutral_n_side": neutral_n_side,
        "neutral_sector_count": neutral_sector_count,
        "active_sector_weight": float(active_l1),
        "top_sector_hhi": hhi_from_counts(top_counts),
        "bottom_sector_hhi": hhi_from_counts(bot_counts),
        "n_sectors_valid": int(x.sector.nunique(dropna=False)),
        "n_sectors_top": int(top.sector.nunique(dropna=False)),
        "n_sectors_bottom": int(bot.sector.nunique(dropna=False)),
    }
    return metrics, contrib_rows


def era(dt: pd.Timestamp) -> str:
    y = dt.year
    if y <= 2019:
        return "2016-19"
    if y <= 2022:
        return "2020-22"
    if y <= 2024:
        return "2023-24"
    return str(y)


def sharpe_5d(s: pd.Series) -> float:
    z = s.dropna()
    if len(z) < 5 or z.std(ddof=1) <= 0:
        return np.nan
    return float(z.mean() / z.std(ddof=1) * np.sqrt(252.0 / 5.0))


def summarize(g: pd.DataFrame) -> pd.Series:
    raw = g.raw_ls
    a = g.allocation
    w = g.within_selection
    neu = g.neutral_ls
    vr = raw.var(ddof=1)
    alloc_var_share = np.cov(raw, a, ddof=1)[0, 1] / vr if len(g) > 2 and vr > 0 else np.nan
    within_var_share = np.cov(raw, w, ddof=1)[0, 1] / vr if len(g) > 2 and vr > 0 else np.nan
    mean_raw = raw.mean()
    mean_within = w.mean()
    mean_share = mean_within / mean_raw if abs(mean_raw) >= 0.0005 else np.nan
    return pd.Series({
        "n_obs": len(g),
        "mean_raw_5d": mean_raw,
        "mean_allocation_5d": a.mean(),
        "mean_within_selection_5d": mean_within,
        "mean_neutral_5d": neu.mean(),
        "raw_sharpe": sharpe_5d(raw),
        "neutral_sharpe": sharpe_5d(neu),
        "raw_neutral_corr": raw.corr(neu),
        "selection_mean_share": mean_share,
        "allocation_variance_share": alloc_var_share,
        "within_variance_share": within_var_share,
        "variance_share_sum": alloc_var_share + within_var_share if pd.notna(alloc_var_share) and pd.notna(within_var_share) else np.nan,
        "median_active_sector_weight": g.active_sector_weight.median(),
        "median_top_sector_hhi": g.top_sector_hhi.median(),
        "median_bottom_sector_hhi": g.bottom_sector_hhi.median(),
        "median_n_valid": g.n_valid.median(),
        "median_neutral_n_side": g.neutral_n_side.median(),
        "max_abs_identity_error": g.identity_error.abs().max(),
    })


def main() -> None:
    wm = wics_map()
    if len(wm) != 2557:
        raise RuntimeError(f"WICS map row count mismatch: {len(wm)}")
    if len(set(wm.values())) != 29:
        raise RuntimeError(f"WICS category count mismatch: {len(set(wm.values()))}")

    basic_files = dated_files(BASIC)
    dates = list(basic_files)
    # signal date followed by exactly five non-overlapping trading dates
    signal_idx = list(range(0, len(dates) - 5, 5))

    panel_rows: list[dict] = []
    sector_rows: list[dict] = []

    for ii, idx in enumerate(signal_idx, start=1):
        sig = dates[idx]
        fwd_dates = dates[idx + 1: idx + 6]
        signal_basic = load_basic(basic_files[sig])
        fwd = forward_block_return([basic_files[d] for d in fwd_dates])

        for factor, (folder, direction) in FACTORS.items():
            fpath = folder / f"{sig.date()}.csv"
            if not fpath.exists():
                continue
            fac = load_factor(fpath, direction)
            fac["fwd"] = fwd.reindex(fac.index)
            fac["sector"] = [wm.get(c, "UNKNOWN") for c in fac.index]
            umasks = masks(signal_basic, fac.index)
            for universe, codes in umasks.items():
                x = fac.reindex(codes).dropna(subset=["score", "fwd"])
                res = calc_one(x)
                if res is None:
                    continue
                met, contrib = res
                base = {
                    "signal_date": sig.date().isoformat(),
                    "payoff_end_date": fwd_dates[-1].date().isoformat(),
                    "era": era(sig),
                    "universe": universe,
                    "factor": factor,
                }
                panel_rows.append(base | met)
                for r in contrib:
                    sector_rows.append(base | r)

        if ii % 25 == 0 or ii == len(signal_idx):
            print(f"processed {ii}/{len(signal_idx)} signal blocks; panel rows={len(panel_rows)}")

    panel = pd.DataFrame(panel_rows)
    sector = pd.DataFrame(sector_rows)
    panel["signal_date"] = pd.to_datetime(panel.signal_date)
    panel["payoff_end_date"] = pd.to_datetime(panel.payoff_end_date)

    panel.to_csv(OUT / "sector_decomposition_panel.csv", index=False)

    # era summaries + FULL
    chunks = []
    for e in ["2016-19", "2020-22", "2023-24", "2025", "2026"]:
        z = panel.loc[panel.era.eq(e)]
        if len(z):
            s = z.groupby(["universe", "factor"], observed=True).apply(summarize).reset_index()
            s.insert(0, "era", e)
            chunks.append(s)
    sfull = panel.groupby(["universe", "factor"], observed=True).apply(summarize).reset_index()
    sfull.insert(0, "era", "FULL")
    chunks.append(sfull)
    summary = pd.concat(chunks, ignore_index=True)
    summary.to_csv(OUT / "factor_sector_decomposition_summary.csv", index=False)

    # Sector-level mean contribution summary
    if len(sector):
        sec = (sector.groupby(["era", "universe", "factor", "sector"], observed=True)
               .agg(n_obs=("allocation_contribution", "size"),
                    mean_top_weight=("top_weight", "mean"),
                    mean_bottom_weight=("bottom_weight", "mean"),
                    mean_active_weight=("top_weight", lambda x: np.nan),
                    mean_allocation_contribution=("allocation_contribution", "mean"),
                    mean_within_selection_contribution=("within_selection_contribution", "mean"))
               .reset_index())
        # replace placeholder active weight with direct |top-bottom| mean from raw sector rows
        active = (sector.assign(abs_active=(sector.top_weight-sector.bottom_weight).abs())
                  .groupby(["era", "universe", "factor", "sector"], observed=True).abs_active.mean())
        sec = sec.drop(columns=["mean_active_weight"]).merge(active.rename("mean_abs_top_bottom_weight").reset_index(), on=["era", "universe", "factor", "sector"], how="left")
        sec.to_csv(OUT / "sector_contribution_summary.csv", index=False)

    # Compact cross-era table for quick review
    prim = summary.loc[summary.universe.isin(["K200", "KOSPI_EX_K200", "KOSDAQ"])].copy()
    prim.to_csv(OUT / "primitive_universe_summary.csv", index=False)

    # QA / headline summary
    max_err = float(panel.identity_error.abs().max())
    if max_err > 1e-10:
        raise RuntimeError(f"Sector decomposition identity failed: max error {max_err}")

    lines = [
        "# Stage 1 Sector Decomposition — Results",
        "",
        f"- Signal blocks: {panel.signal_date.nunique()}",
        f"- Panel rows: {len(panel):,}",
        f"- Max |RAW - ALLOCATION - WITHIN_SELECTION|: {max_err:.3e}",
        f"- WICS mapping rows/categories: {len(wm):,} / {len(set(wm.values()))}",
        "",
        "## Primitive-universe headline table",
        "",
        "See `primitive_universe_summary.csv` for all factors and eras.",
        "",
        "Stage 1 is descriptive only. No factor-selection rule is promoted from these results.",
    ]
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
