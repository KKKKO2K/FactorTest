from __future__ import annotations

from pathlib import Path
import math
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "source" / "factor_all_values"
BASIC = DATA / "reference_snapshots" / "basic_info"
TRADING = DATA / "reference_snapshots" / "trading_amount"
SECTOR_PANEL = ROOT / "research" / "sector_decomposition_reset" / "results_stage1" / "sector_decomposition_panel.csv"
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

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")


def read_csv(path: Path) -> pd.DataFrame:
    last = None
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Could not read {path}: {last}")


def find_col(df: pd.DataFrame, exact=(), contains=()) -> str | None:
    for c in df.columns:
        if str(c).strip() in exact:
            return c
    for c in df.columns:
        z = str(c).strip().lower()
        if any(t.lower() in z for t in contains):
            return c
    return None


def norm_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return x.where(x.str.startswith("A"), "A" + x.str.zfill(6))


def numeric(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out = {}
    for p in folder.iterdir():
        if not p.is_file():
            continue
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def load_basic(path: Path, need_meta: bool = True) -> pd.DataFrame:
    df = read_csv(path)
    cc = find_col(df, exact=("Code", "StockCode", "종목코드"))
    ret_c = find_col(df, exact=("수정주가수익률",), contains=("수정주가수익률", "return"))
    if cc is None or ret_c is None:
        raise KeyError(f"Basic columns missing in {path.name}")
    out = pd.DataFrame({
        "code": norm_code(df[cc]),
        "ret": numeric(df[ret_c]) / 100.0,
    })
    if need_meta:
        market_c = find_col(df, exact=("상장된 시장",), contains=("상장된 시장", "market"))
        k200_c = find_col(df, contains=("코스피200", "k200"))
        if market_c is None or k200_c is None:
            raise KeyError(f"Universe columns missing in {path.name}")
        out["market"] = df[market_c].astype(str).str.upper().str.strip()
        out["k200"] = numeric(df[k200_c]).fillna(0).astype(int)
    return out.drop_duplicates("code", keep="last").set_index("code")


def load_trading(path: Path) -> pd.Series:
    df = read_csv(path)
    cc = find_col(df, exact=("Code", "StockCode", "종목코드"))
    vc = find_col(df, exact=("거래대금(십억원)",), contains=("거래대금", "trading"))
    if cc is None or vc is None:
        raise KeyError(f"Trading columns missing in {path.name}: {list(df.columns)}")
    s = pd.Series(numeric(df[vc]).to_numpy(), index=norm_code(df[cc]))
    return s.groupby(level=0).last()


def load_factor(path: Path, direction: int) -> pd.DataFrame:
    df = read_csv(path)
    cc = find_col(df, exact=("StockCode", "Code", "종목코드"))
    vc = find_col(df, exact=("FactorValue",), contains=("factorvalue",))
    if cc is None or vc is None:
        raise KeyError(f"Factor columns missing in {path}")
    out = pd.DataFrame({"code": norm_code(df[cc]), "value": numeric(df[vc])})
    out = out.drop_duplicates("code", keep="last").dropna(subset=["value"])
    out["score"] = direction * out["value"]
    return out.set_index("code")


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


def build_daily_matrices(
    dates: list[pd.Timestamp],
    basic_files: dict[pd.Timestamp, Path],
    trading_files: dict[pd.Timestamp, Path],
) -> tuple[pd.Index, np.ndarray, np.ndarray]:
    master = load_basic(basic_files[dates[0]], need_meta=False).index
    code_to_pos = pd.Series(np.arange(len(master), dtype=int), index=master)
    ret = np.full((len(dates), len(master)), np.nan, dtype=np.float32)
    ta = np.full((len(dates), len(master)), np.nan, dtype=np.float32)

    for i, dt in enumerate(dates):
        b = load_basic(basic_files[dt], need_meta=False)
        pos = code_to_pos.reindex(b.index).dropna().astype(int)
        if len(pos):
            vals = b.reindex(pos.index).ret.to_numpy(dtype=float)
            ret[i, pos.to_numpy()] = vals.astype(np.float32)

        t = load_trading(trading_files[dt])
        pos_t = code_to_pos.reindex(t.index).dropna().astype(int)
        if len(pos_t):
            vals_t = t.reindex(pos_t.index).to_numpy(dtype=float)
            ta[i, pos_t.to_numpy()] = vals_t.astype(np.float32)

        if (i + 1) % 250 == 0 or i + 1 == len(dates):
            print(f"loaded daily return/trading matrices {i+1}/{len(dates)}")

    return master, ret, ta


def pairwise_breadth(top_ret: np.ndarray, bot_ret: np.ndarray) -> float:
    top = top_ret[np.isfinite(top_ret)]
    bot = bot_ret[np.isfinite(bot_ret)]
    if len(top) == 0 or len(bot) == 0:
        return np.nan
    sb = np.sort(bot)
    wins = np.searchsorted(sb, top, side="left").sum()
    ties = (np.searchsorted(sb, top, side="right") - np.searchsorted(sb, top, side="left")).sum()
    return float((wins + 0.5 * ties) / (len(top) * len(bot)))


def concentration(top_ret: np.ndarray, bot_ret: np.ndarray) -> float:
    nt = max(1, len(top_ret))
    nb = max(1, len(bot_ret))
    contrib = np.concatenate([top_ret / nt, -bot_ret / nb])
    a = np.abs(contrib[np.isfinite(contrib)])
    denom = a.sum()
    if len(a) == 0 or denom <= 0:
        return np.nan
    k = min(5, len(a))
    return float(np.sort(a)[-k:].sum() / denom)


def calc_block_metrics(x: pd.DataFrame) -> dict | None:
    x = x.dropna(subset=["score", "fwd"]).copy()
    n = len(x)
    if n < 10:
        return None
    n_side = max(1, int(math.floor(0.20 * n)))
    if 2 * n_side >= n:
        return None
    x = x.sort_values("score", ascending=False, kind="mergesort")
    top = x.iloc[:n_side]
    bot = x.iloc[-n_side:]
    top_ret = top.fwd.to_numpy(dtype=float)
    bot_ret = bot.fwd.to_numpy(dtype=float)
    raw = float(np.nanmean(top_ret) - np.nanmean(bot_ret))

    pb = pairwise_breadth(top_ret, bot_ret)
    conc = concentration(top_ret, bot_ret)

    ar = x.activity_ratio.replace([np.inf, -np.inf], np.nan)
    valid_ar = ar.dropna()
    if len(valid_ar) >= max(10, int(0.5 * n)):
        pct = valid_ar.rank(method="average", pct=True)
        sleeve_codes = top.index.union(bot.index)
        sleeve_pct = pct.reindex(sleeve_codes).dropna()
        liq = float(sleeve_pct.mean() - pct.mean()) if len(sleeve_pct) else np.nan
        activity_coverage = float(len(sleeve_pct) / len(sleeve_codes)) if len(sleeve_codes) else np.nan
    else:
        liq = np.nan
        activity_coverage = np.nan

    return {
        "n_valid": n,
        "n_side": n_side,
        "raw_ls_rebuilt": raw,
        "pairwise_breadth": pb,
        "top5_abs_contrib_share": conc,
        "liquidity_support": liq,
        "activity_coverage": activity_coverage,
    }


def main() -> None:
    if not SECTOR_PANEL.exists():
        raise FileNotFoundError(f"Missing frozen sector decomposition panel: {SECTOR_PANEL}")

    sector = pd.read_csv(SECTOR_PANEL, parse_dates=["signal_date", "payoff_end_date"])
    sector_key = sector.set_index(["signal_date", "universe", "factor"])[["raw_ls", "allocation", "within_selection"]]

    basic_files = dated_files(BASIC)
    trading_files = dated_files(TRADING)
    dates = list(basic_files)
    if list(trading_files) != dates:
        raise RuntimeError("Trading dates do not exactly match basic-info dates")

    master, ret_mat, ta_mat = build_daily_matrices(dates, basic_files, trading_files)
    pos_map = pd.Series(np.arange(len(master), dtype=int), index=master)

    signal_idx = list(range(0, len(dates) - 5, 5))
    rows = []
    max_raw_diff = 0.0

    for jj, idx in enumerate(signal_idx, start=1):
        sig = dates[idx]
        signal_basic = load_basic(basic_files[sig], need_meta=True)

        # Replicate the original factor-return convention: missing daily returns contribute zero.
        r5 = np.prod(1.0 + np.nan_to_num(ret_mat[idx + 1: idx + 6].astype(float), nan=0.0), axis=0) - 1.0

        if idx >= 19:
            base = np.nanmean(ta_mat[idx - 19: idx + 1].astype(float), axis=0)
            block = np.nanmean(ta_mat[idx + 1: idx + 6].astype(float), axis=0)
            with np.errstate(divide="ignore", invalid="ignore"):
                act = np.where((base > 0) & np.isfinite(base) & np.isfinite(block), block / base, np.nan)
        else:
            act = np.full(len(master), np.nan, dtype=float)

        for factor, (folder, direction) in FACTORS.items():
            fpath = folder / f"{sig.date()}.csv"
            if not fpath.exists():
                continue
            fac = load_factor(fpath, direction)
            p = pos_map.reindex(fac.index)
            keep = p.notna()
            fac = fac.loc[keep].copy()
            pp = p.loc[keep].astype(int).to_numpy()
            fac["fwd"] = r5[pp]
            fac["activity_ratio"] = act[pp]

            for universe, codes in masks(signal_basic, fac.index).items():
                x = fac.reindex(codes)
                met = calc_block_metrics(x)
                if met is None:
                    continue
                key = (sig, universe, factor)
                if key not in sector_key.index:
                    continue
                srow = sector_key.loc[key]
                raw_diff = abs(float(met["raw_ls_rebuilt"]) - float(srow.raw_ls))
                max_raw_diff = max(max_raw_diff, raw_diff)
                rows.append({
                    "signal_date": sig,
                    "universe": universe,
                    "factor": factor,
                    "raw_ls": float(srow.raw_ls),
                    "allocation": float(srow.allocation),
                    "within_selection": float(srow.within_selection),
                    **met,
                })

        if jj % 25 == 0 or jj == len(signal_idx):
            print(f"processed quality blocks {jj}/{len(signal_idx)}; rows={len(rows)}")

    out = pd.DataFrame(rows).sort_values(["universe", "factor", "signal_date"]).reset_index(drop=True)
    out.to_csv(OUT / "factor_quality_block_panel.csv", index=False)

    if max_raw_diff > 1e-10:
        raise RuntimeError(f"Rebuilt raw factor payoff does not match sector panel: max diff={max_raw_diff}")

    summary = (out.groupby(["universe", "factor"], observed=True)
               .agg(n_blocks=("signal_date", "size"),
                    mean_pairwise_breadth=("pairwise_breadth", "mean"),
                    mean_top5_abs_contrib_share=("top5_abs_contrib_share", "mean"),
                    mean_liquidity_support=("liquidity_support", "mean"),
                    median_activity_coverage=("activity_coverage", "median"))
               .reset_index())
    summary.to_csv(OUT / "factor_quality_block_summary.csv", index=False)

    text = [
        "# Stage 1 Factor Quality Panel — Results",
        "",
        f"- Blocks: {out.signal_date.nunique()}",
        f"- Factor/universe rows: {len(out):,}",
        f"- Max rebuilt raw payoff difference vs frozen sector panel: {max_raw_diff:.3e}",
        f"- Median activity coverage: {out.activity_coverage.median():.2%}",
        "",
        "Stage 1 constructs only preregistered stock-level internals. No predictive result is evaluated here.",
    ]
    (OUT / "RESEARCH_SUMMARY.md").write_text("\n".join(text), encoding="utf-8")


if __name__ == "__main__":
    main()
