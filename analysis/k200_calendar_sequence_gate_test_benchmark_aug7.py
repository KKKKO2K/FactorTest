from pathlib import Path
import numpy as np
import pandas as pd
import requests

base_path = Path(__file__).resolve().parent / "k200_calendar_sequence_gate_test.py"
source = base_path.read_text(encoding="utf-8")
source = source.replace('summary[summary.sample == "test"]', 'summary[summary["sample"] == "test"]')
source = source.replace(
    'k200_period = enh.forward_index_returns(k200_close, signal_dates, STEP)',
    'k200_period = forward_index_returns_aligned(k200_close, signal_dates, STEP, returns.index)'
)
ns = {"__name__": "k200_calendar_sequence_gate_benchmark_aug7", "__file__": str(base_path)}
exec(compile(source, str(base_path), "exec"), ns)

lab = ns["lab"]
enh = ns["enh"]
OUT = ns["OUT"]
START, END, STEP = ns["START"], ns["END"], ns["STEP"]


def build_true_calendar_panel(returns, basic_panels):
    trading = returns.loc[(returns.index >= START) & (returns.index <= END)].index
    schedule = list(trading[::STEP])
    available = sorted(pd.Timestamp(x) for x in basic_panels if pd.Timestamp(x) <= END)
    available_np = np.array(available, dtype="datetime64[ns]")
    asof_map = {}
    for dt in schedule:
        pos = np.searchsorted(available_np, np.datetime64(dt), side="right") - 1
        if pos >= 0:
            asof_map[pd.Timestamp(dt)] = available[int(pos)]
    scheduled_panels = {dt: basic_panels[eff] for dt, eff in asof_map.items()}

    glb = lab.build_panel.__globals__
    original_raw = glb["raw_snapshot"]
    original_step = glb["STEP"]
    original_start = glb["START"]
    original_end = glb["END"]

    def raw_scheduled(dt, universe, returns_, _scheduled, factor_cache):
        eff = asof_map[pd.Timestamp(dt)]
        f = original_raw(eff, universe, returns_, basic_panels, factor_cache)
        q = f.reset_index()
        q["date"] = pd.Timestamp(dt)
        return q.set_index(["date", "code"])

    try:
        glb["raw_snapshot"] = raw_scheduled
        glb["STEP"] = 1
        glb["START"] = START
        glb["END"] = END
        panel = lab.build_panel("K200", returns, scheduled_panels)
    finally:
        glb["raw_snapshot"] = original_raw
        glb["STEP"] = original_step
        glb["START"] = original_start
        glb["END"] = original_end

    schedule_map = pd.DataFrame([
        {
            "scheduled_date": dt,
            "factor_snapshot_date": eff,
            "calendar_day_staleness": int((dt - eff).days),
            "exact_snapshot": bool(dt == eff),
        }
        for dt, eff in asof_map.items()
    ])
    return panel, scheduled_panels, schedule_map


def _num(x):
    if x is None or x == "":
        return np.nan
    return float(str(x).replace(",", ""))


def _fetch_naver_recent():
    frames = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for page in (1, 2):
        url = f"https://m.stock.naver.com/api/index/KPI200/price?pageSize=60&page={page}"
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        f = pd.DataFrame(r.json())
        if f.empty:
            continue
        f["date"] = pd.to_datetime(f["localTradedAt"])
        f["naver_close"] = f["closePrice"].map(_num)
        frames.append(f[["date", "naver_close"]])
    if not frames:
        raise RuntimeError("Naver KOSPI200 response was empty")
    f = pd.concat(frames, ignore_index=True).drop_duplicates("date", keep="first")
    naver = f.set_index("date")["naver_close"].dropna().sort_index()
    naver.index = pd.to_datetime(naver.index).tz_localize(None)
    return naver


def download_kospi200_patched():
    yahoo = original_download().copy()
    yahoo.index = pd.to_datetime(yahoo.index).tz_localize(None)
    yahoo = pd.to_numeric(yahoo, errors="coerce").dropna().sort_index()
    naver = _fetch_naver_recent()

    patched = pd.concat([yahoo.rename("yahoo_close"), naver.rename("naver_close")], axis=1)
    patched["patched_close"] = patched["naver_close"].combine_first(patched["yahoo_close"])
    patched["source"] = np.where(patched["naver_close"].notna(), "NAVER", "YAHOO")
    overlap = patched[patched["yahoo_close"].notna() & patched["naver_close"].notna()].copy()
    overlap["abs_diff"] = (overlap["naver_close"] - overlap["yahoo_close"]).abs()
    overlap["pct_diff"] = overlap["naver_close"] / overlap["yahoo_close"] - 1.0

    audit = patched.loc[patched.index >= pd.Timestamp("2026-04-01")].copy()
    audit.index.name = "date"
    audit.to_csv(OUT / "k200_benchmark_patch_audit.csv", encoding="utf-8-sig")
    overlap.loc[overlap.index >= pd.Timestamp("2026-04-01")].to_csv(
        OUT / "k200_benchmark_overlap_check.csv", encoding="utf-8-sig"
    )

    close = patched["patched_close"].dropna().sort_index().rename("k200_close")
    print("=== K200 BENCHMARK PATCH ===")
    print(f"Yahoo range: {yahoo.index.min().date()} -> {yahoo.index.max().date()} ({len(yahoo)} rows)")
    print(f"Naver range: {naver.index.min().date()} -> {naver.index.max().date()} ({len(naver)} rows)")
    print(f"Patched range: {close.index.min().date()} -> {close.index.max().date()} ({len(close)} rows)")
    if not overlap.empty:
        recent_overlap = overlap.loc[overlap.index >= pd.Timestamp("2026-04-01")]
        if not recent_overlap.empty:
            print(f"Recent overlap max abs pct diff: {recent_overlap['pct_diff'].abs().max():.8f}")
    for dt in [pd.Timestamp("2026-07-07"), pd.Timestamp("2026-07-22"), pd.Timestamp("2026-08-06"), pd.Timestamp("2026-08-07")]:
        print(dt.date(), close.get(dt, np.nan), patched.loc[dt, "source"] if dt in patched.index else "MISSING")
    return close


def forward_index_returns_aligned(close, signal_dates, horizon, stock_calendar):
    stock_idx = pd.DatetimeIndex(stock_calendar).sort_values()
    close = close.sort_index()
    rows = []
    for dt in signal_dates:
        dt = pd.Timestamp(dt)
        pos = stock_idx.searchsorted(dt, side="left")
        if pos >= len(stock_idx) or stock_idx[pos] != dt or pos + horizon >= len(stock_idx):
            rows.append({"date": dt, "end_date": pd.NaT, "k200_return": np.nan})
            continue
        end_dt = pd.Timestamp(stock_idx[pos + horizon])
        if dt not in close.index or end_dt not in close.index:
            rows.append({"date": dt, "end_date": end_dt, "k200_return": np.nan})
            continue
        r = float(close.loc[end_dt] / close.loc[dt] - 1.0)
        rows.append({"date": dt, "end_date": end_dt, "k200_return": r})
    audit = pd.DataFrame(rows)
    audit.to_csv(OUT / "k200_aligned_period_returns.csv", index=False, encoding="utf-8-sig")
    print("=== ALIGNED K200 RECENT PERIODS ===")
    print(audit.tail(8).to_string(index=False))
    return audit.set_index("date")["k200_return"]


original_download = enh.download_kospi200
ns["build_true_calendar_panel"] = build_true_calendar_panel
ns["forward_index_returns_aligned"] = forward_index_returns_aligned
enh.download_kospi200 = download_kospi200_patched
ns["main"]()
