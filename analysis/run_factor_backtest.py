from __future__ import annotations

import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "source" / "factor_all_values" / "reference_snapshots"
OUT = ROOT / "analysis" / "results"
OUT.mkdir(parents=True, exist_ok=True)

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
META_WORDS = {
    "결산월", "구성종목", "상장된 시장", "시장", "market", "name", "code",
    "수정주가수익률", "시가총액", "이전 시가총액", "return", "ret",
}


def read_csv(path: Path) -> pd.DataFrame:
    errors = []
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as exc:
            errors.append(f"{enc}: {exc}")
    raise RuntimeError(f"Could not read {path}: {' | '.join(errors)}")


def find_code_col(df: pd.DataFrame) -> str | None:
    for c in df.columns:
        if str(c).strip().lower() in {"code", "종목코드", "ticker"}:
            return c
    for c in df.columns:
        s = df[c].astype(str)
        if s.str.match(r"^A?\d{6}$").mean() > 0.5:
            return c
    return None


def normalize_code(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    x = x.where(x.str.startswith("A"), "A" + x.str.zfill(6))
    return x


def dated_files(folder: Path) -> dict[pd.Timestamp, Path]:
    out = {}
    if not folder.exists():
        return out
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def locate_basic_info() -> Path:
    direct = SNAP / "basic_info"
    if direct.exists():
        return direct
    candidates = [p for p in SNAP.iterdir() if p.is_dir() and "basic" in p.name.lower()]
    if not candidates:
        raise FileNotFoundError("basic_info snapshot directory not found")
    return candidates[0]


def detect_return_col(df: pd.DataFrame) -> str:
    preferred = [c for c in df.columns if "수정주가수익률" in str(c)]
    if preferred:
        return preferred[0]
    candidates = [c for c in df.columns if str(c).strip().lower() in {"return", "ret", "daily_return"}]
    if candidates:
        return candidates[0]
    raise KeyError(f"Return column not found. Columns={list(df.columns)}")


def load_returns() -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    caps = []
    files = dated_files(locate_basic_info())
    for dt, p in files.items():
        df = read_csv(p)
        code_col = find_code_col(df)
        if code_col is None:
            continue
        ret_col = detect_return_col(df)
        tmp = pd.DataFrame({
            "date": dt,
            "code": normalize_code(df[code_col]),
            "ret": pd.to_numeric(df[ret_col], errors="coerce") / 100.0,
        })
        rows.append(tmp)
        cap_cols = [c for c in df.columns if str(c).strip() == "시가총액"]
        if cap_cols:
            cap = pd.DataFrame({
                "date": dt,
                "code": normalize_code(df[code_col]),
                "mcap": pd.to_numeric(df[cap_cols[0]], errors="coerce"),
            })
            caps.append(cap)
    if not rows:
        raise RuntimeError("No daily return snapshots found")
    r = pd.concat(rows, ignore_index=True).drop_duplicates(["date", "code"], keep="last")
    r = r.pivot(index="date", columns="code", values="ret").sort_index()
    c = pd.concat(caps, ignore_index=True).drop_duplicates(["date", "code"], keep="last") if caps else pd.DataFrame()
    if not c.empty:
        c = c.pivot(index="date", columns="code", values="mcap").sort_index()
    return r, c


def forward_returns(daily: pd.DataFrame, horizon: int) -> pd.DataFrame:
    # Signal observed at t close; target starts at t+1 to prevent same-day leakage.
    logret = np.log1p(daily.clip(lower=-0.999999))
    target = sum(logret.shift(-i) for i in range(1, horizon + 1))
    return np.expm1(target)


def is_metadata_column(name: str) -> bool:
    s = str(name).strip().lower()
    return any(w.lower() in s for w in META_WORDS) or s.startswith("unnamed") or s == ""


def discover_signals() -> tuple[dict[str, dict[pd.Timestamp, pd.Series]], pd.DataFrame]:
    signals: dict[str, dict[pd.Timestamp, pd.Series]] = {}
    inventory = []
    excluded_dirs = {"basic_info", "universe_definition"}
    for folder in sorted(p for p in SNAP.iterdir() if p.is_dir()):
        files = dated_files(folder)
        if not files:
            continue
        inventory.append({"directory": folder.name, "n_files": len(files), "first": min(files), "last": max(files)})
        if folder.name in excluded_dirs:
            continue
        for dt, p in files.items():
            try:
                df = read_csv(p)
            except Exception:
                continue
            code_col = find_code_col(df)
            if code_col is None:
                continue
            codes = normalize_code(df[code_col])
            for col in df.columns:
                if col == code_col or is_metadata_column(col):
                    continue
                vals = pd.to_numeric(df[col], errors="coerce")
                n = int(vals.notna().sum())
                nunique = int(vals.nunique(dropna=True))
                if n < 30 or nunique < 5:
                    continue
                key = f"{folder.name}::{str(col).strip()}"
                signals.setdefault(key, {})[dt] = pd.Series(vals.to_numpy(), index=codes).groupby(level=0).last()
    return signals, pd.DataFrame(inventory)


def winsor_z(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)
    if s.notna().sum() < 20:
        return s * np.nan
    lo, hi = s.quantile([0.01, 0.99])
    s = s.clip(lo, hi)
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and np.isfinite(sd) else s * np.nan


def evaluate_signal(name: str, snapshots: dict[pd.Timestamp, pd.Series], fwd: dict[int, pd.DataFrame]) -> list[dict]:
    rows = []
    for h, target in fwd.items():
        observations = []
        for dt, sig in snapshots.items():
            if dt not in target.index:
                continue
            y = target.loc[dt]
            x = sig.reindex(y.index)
            pair = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna()
            if len(pair) < 50 or pair.x.nunique() < 5:
                continue
            ic = spearmanr(pair.x, pair.y).statistic
            try:
                q = pd.qcut(pair.x.rank(method="first"), 5, labels=False)
                qret = pair.groupby(q).y.mean()
                spread = float(qret.iloc[-1] - qret.iloc[0]) if len(qret) == 5 else np.nan
            except Exception:
                spread = np.nan
            observations.append((dt, len(pair), ic, spread))
        if len(observations) < 20:
            continue
        obs = pd.DataFrame(observations, columns=["date", "n", "ic", "spread"]).sort_values("date")
        split = max(10, int(len(obs) * 0.7))
        train, test = obs.iloc[:split], obs.iloc[split:]
        if len(test) < 5:
            continue
        orient = 1.0 if train.ic.mean() >= 0 else -1.0
        rows.append({
            "factor": name,
            "horizon": h,
            "n_dates": len(obs),
            "first_date": obs.date.min().date().isoformat(),
            "last_date": obs.date.max().date().isoformat(),
            "avg_names": obs.n.mean(),
            "train_ic": orient * train.ic.mean(),
            "test_ic": orient * test.ic.mean(),
            "test_ic_t": (orient * test.ic.mean()) / (test.ic.std(ddof=1) / math.sqrt(len(test))) if test.ic.std(ddof=1) > 0 else np.nan,
            "test_ic_positive": (orient * test.ic > 0).mean(),
            "train_spread": orient * train.spread.mean(),
            "test_spread": orient * test.spread.mean(),
            "orientation": int(orient),
            "split_date": obs.iloc[split].date.date().isoformat(),
        })
    return rows


def evaluate_composite(signals, selected, orientation, target, dates):
    records = []
    for dt in dates:
        pieces = []
        for f in selected:
            s = signals[f].get(dt)
            if s is not None:
                pieces.append(winsor_z(s) * orientation[f])
        if len(pieces) < max(2, len(selected) // 2):
            continue
        score = pd.concat(pieces, axis=1).mean(axis=1)
        if dt not in target.index:
            continue
        y = target.loc[dt]
        pair = pd.concat([score.rename("x"), y.rename("y")], axis=1).dropna()
        if len(pair) < 50:
            continue
        ic = spearmanr(pair.x, pair.y).statistic
        q = pd.qcut(pair.x.rank(method="first"), 5, labels=False)
        qret = pair.groupby(q).y.mean()
        spread = float(qret.iloc[-1] - qret.iloc[0]) if len(qret) == 5 else np.nan
        records.append((dt, len(pair), ic, spread))
    if not records:
        return None, pd.DataFrame()
    obs = pd.DataFrame(records, columns=["date", "n", "ic", "spread"]).sort_values("date")
    summary = {
        "n_dates": len(obs),
        "first_date": obs.date.min().date().isoformat(),
        "last_date": obs.date.max().date().isoformat(),
        "avg_names": obs.n.mean(),
        "ic": obs.ic.mean(),
        "ic_t": obs.ic.mean() / (obs.ic.std(ddof=1) / math.sqrt(len(obs))) if len(obs) > 1 and obs.ic.std(ddof=1) > 0 else np.nan,
        "ic_positive": (obs.ic > 0).mean(),
        "spread": obs.spread.mean(),
    }
    return summary, obs


def main():
    daily, mcap = load_returns()
    fwd = {h: forward_returns(daily, h) for h in (1, 5, 20)}
    signals, inventory = discover_signals()
    inventory.to_csv(OUT / "snapshot_inventory.csv", index=False, encoding="utf-8-sig")

    result_rows = []
    for i, (name, snaps) in enumerate(signals.items(), 1):
        result_rows.extend(evaluate_signal(name, snaps, fwd))
        if i % 25 == 0:
            print(f"evaluated {i}/{len(signals)} signal columns")
    results = pd.DataFrame(result_rows)
    if results.empty:
        raise RuntimeError(f"No signals passed minimum coverage. Discovered={len(signals)}")
    results = results.sort_values(["horizon", "test_ic"], ascending=[True, False])
    results.to_csv(OUT / "single_factor_results.csv", index=False, encoding="utf-8-sig")

    composites = []
    comp_obs_all = []
    for h in (1, 5, 20):
        sub = results[results.horizon == h].copy()
        if sub.empty:
            continue
        # Select only from train statistics; test period remains untouched.
        eligible = sub[(sub.n_dates >= 40) & (sub.train_ic >= 0.015)].copy()
        eligible = eligible.sort_values(["train_ic", "n_dates"], ascending=False)
        selected = eligible.factor.head(10).tolist()
        if len(selected) < 2:
            continue
        orientation = dict(zip(eligible.factor, eligible.orientation))
        split_date = pd.Timestamp(eligible.iloc[0].split_date)
        test_dates = daily.index[daily.index >= split_date]
        summary, obs = evaluate_composite(signals, selected, orientation, fwd[h], test_dates)
        if summary is None:
            continue
        summary.update({"horizon": h, "factors": json.dumps(selected, ensure_ascii=False)})
        composites.append(summary)
        obs["horizon"] = h
        comp_obs_all.append(obs)
    pd.DataFrame(composites).to_csv(OUT / "composite_results.csv", index=False, encoding="utf-8-sig")
    if comp_obs_all:
        pd.concat(comp_obs_all).to_csv(OUT / "composite_timeseries.csv", index=False, encoding="utf-8-sig")

    lines = [
        "# Factor backtest summary",
        "",
        f"- Daily-return dates: {daily.index.min().date()} to {daily.index.max().date()} ({len(daily)} trading snapshots)",
        f"- Return universe: {daily.shape[1]} unique codes",
        f"- Snapshot directories: {len(inventory)}",
        f"- Candidate numeric signal columns: {len(signals)}",
        "- Signal timing: factor at t close; forward return begins t+1 (same-day return excluded)",
        "- Validation: chronological 70% train / 30% test; factor direction chosen using train only",
        "",
    ]
    for h in (1, 5, 20):
        top = results[results.horizon == h].sort_values("test_ic", ascending=False).head(15)
        lines += [f"## Top single factors: {h}-day forward return", "", top.to_markdown(index=False), ""]
    if composites:
        lines += ["## Out-of-sample equal-weight composites", "", pd.DataFrame(composites).to_markdown(index=False), ""]
    (OUT / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
