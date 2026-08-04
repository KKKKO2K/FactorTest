from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "source" / "factor_all_values"
BASIC = DATA / "reference_snapshots" / "basic_info"
OUT = ROOT / "analysis" / "transparent_rule_results"
OUT.mkdir(parents=True, exist_ok=True)
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.csv$")
SPLIT = pd.Timestamp("2023-05-26")
START = pd.Timestamp("2016-04-01")
FACTOR_DIRS = {
    "per": DATA / "PER(12MF)",
    "pbr": DATA / "PBR(12MF)",
    "op12": DATA / "OP(12MF_1M_CHG)",
    "opfy1": DATA / "OP(FY1_1M_CHG)",
    "short": DATA / "단기모멘텀",
    "long": DATA / "모멘텀(12-1)",
    "private": DATA / "사모수급",
    "foreign": DATA / "외국인수급",
}


def read_csv(path: Path) -> pd.DataFrame:
    last = None
    for enc in ("utf-8-sig", "utf-8", "cp949", "euc-kr"):
        try:
            return pd.read_csv(path, encoding=enc, low_memory=False)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Could not read {path}: {last}")


def dated_files(folder: Path):
    out = {}
    for p in folder.glob("*.csv"):
        m = DATE_RE.match(p.name)
        if m:
            out[pd.Timestamp(m.group(1))] = p
    return dict(sorted(out.items()))


def code_col(df):
    for c in df.columns:
        if str(c).strip().lower() in {"code", "stockcode", "종목코드", "ticker"}:
            return c
    raise KeyError(list(df.columns))


def find_col(df, exact=(), contains=()):
    for c in df.columns:
        if str(c).strip() in exact:
            return c
    for c in df.columns:
        s = str(c).strip().lower()
        if any(k.lower() in s for k in contains):
            return c
    return None


def norm_code(s):
    x = s.astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    return x.where(x.str.startswith("A"), "A" + x.str.zfill(6))


def load_basic():
    rows = []
    panels = {}
    for dt, p in dated_files(BASIC).items():
        df = read_csv(p)
        cc = code_col(df)
        rc = find_col(df, exact=("수정주가수익률",), contains=("수정주가수익률",))
        mc = find_col(df, exact=("시가총액",), contains=("시가총액",))
        mk = find_col(df, exact=("상장된 시장",), contains=("상장된 시장", "market"))
        kc = find_col(df, contains=("코스피200", "k200"))
        if rc is None or mc is None:
            continue
        idx = norm_code(df[cc]).to_numpy()
        panel = pd.DataFrame({
            "ret": (pd.to_numeric(df[rc], errors="coerce") / 100).to_numpy(),
            "mcap": pd.to_numeric(df[mc], errors="coerce").to_numpy(),
            "market": df[mk].astype(str).str.upper().str.strip().to_numpy() if mk else np.repeat("", len(df)),
            "k200": pd.to_numeric(df[kc], errors="coerce").fillna(0).astype(int).to_numpy() if kc else np.zeros(len(df), dtype=int),
        }, index=idx).groupby(level=0).last()
        panels[dt] = panel
        rows.append(pd.DataFrame({"date": dt, "code": panel.index, "ret": panel.ret.to_numpy()}))
    returns = pd.concat(rows).pivot(index="date", columns="code", values="ret").sort_index()
    return returns, panels


def load_factor(folder: Path, dt: pd.Timestamp):
    p = folder / f"{dt.date().isoformat()}.csv"
    if not p.exists():
        return pd.Series(dtype=float)
    df = read_csv(p)
    cc = code_col(df)
    vc = find_col(df, exact=("FactorValue",), contains=("factorvalue",))
    codes = norm_code(df[cc])
    vals = pd.to_numeric(df[vc], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return pd.Series(vals.to_numpy(), index=codes).groupby(level=0).last()


def forward_return(daily, h):
    logs = np.log1p(daily.clip(lower=-0.999999))
    return np.expm1(sum(logs.shift(-i) for i in range(1, h + 1)))


def good_rank(s, raw_high_good=True):
    # Percentile 1 means best.
    return pd.to_numeric(s, errors="coerce").rank(pct=True, method="average", ascending=raw_high_good)


def feature_frame(dt, basic, cache):
    base = basic[dt]
    codes = base.index[base.market.str.contains("KOSPI", na=False) & (base.k200 == 0)]
    x = pd.DataFrame(index=codes)
    for k, folder in FACTOR_DIRS.items():
        key = (k, dt)
        if key not in cache:
            cache[key] = load_factor(folder, dt)
        x[k] = cache[key].reindex(codes)
    # Train-period directions established in the preceding all-factor research.
    x["cheap_per"] = good_rank(x.per, raw_high_good=False)
    x["cheap_pbr"] = good_rank(x.pbr, raw_high_good=False)
    x["value"] = x[["cheap_per", "cheap_pbr"]].mean(axis=1)
    x["revision"] = pd.concat([good_rank(x.op12, True), good_rank(x.opfy1, True)], axis=1).mean(axis=1)
    x["op12_good"] = good_rank(x.op12, True)
    x["short_reversal"] = good_rank(x.short, raw_high_good=False)
    x["private_good"] = good_rank(x.private, raw_high_good=True)
    x["foreign_good"] = good_rank(x.foreign, raw_high_good=False)
    x["long_contrarian"] = good_rank(x.long, raw_high_good=False)
    return x


def strategies(x):
    out = {}
    # Baselines.
    out["OLD4_LINEAR"] = x[["value", "revision"]].mean(axis=1)
    out["NEW4_LINEAR"] = x[["short_reversal", "long_contrarian", "private_good", "foreign_good"]].mean(axis=1)

    # Transparent new-factor candidates.
    out["PRIVATE_REVERSAL_LINEAR"] = 0.55 * x.private_good + 0.45 * x.short_reversal

    gate1 = (x.private_good >= 0.70) & (x.short_reversal >= 0.50)
    out["PRIVATE_REVERSAL_GATE"] = (0.60 * x.private_good + 0.40 * x.short_reversal).where(gate1)

    gate2 = gate1 & (x.op12_good >= 0.20)
    out["PRIVATE_REVERSAL_REV_VETO"] = (0.45*x.private_good + 0.35*x.short_reversal + 0.20*x.op12_good).where(gate2)

    # Two economic paths: institutional accumulation with revision support, or oversold value rebound with private-flow confirmation.
    route_a = (x.private_good >= 0.85) & (x.op12_good >= 0.50)
    route_b = (x.short_reversal >= 0.85) & (x.value >= 0.60) & (x.private_good >= 0.50)
    score_a = 0.60*x.private_good + 0.25*x.op12_good + 0.15*x.short_reversal
    score_b = 0.45*x.short_reversal + 0.30*x.value + 0.25*x.private_good
    out["DUAL_ROUTE"] = pd.concat([score_a.where(route_a), score_b.where(route_b)], axis=1).max(axis=1, skipna=True)
    out["DUAL_ROUTE"] = out["DUAL_ROUTE"].where(route_a | route_b)

    # A milder hybrid to avoid tiny candidate sets.
    hybrid_gate = (x.private_good >= 0.60) & (x.short_reversal >= 0.55) & (x.op12_good >= 0.25)
    out["HYBRID_3WAY"] = (0.40*x.private_good + 0.35*x.short_reversal + 0.15*x.op12_good + 0.10*x.value).where(hybrid_gate)
    return out


def period_test(returns, basic, h=20, n=25, cost_bps=30, buffer=False):
    fwd = forward_return(returns, h)
    dates = returns.index[returns.index >= START][::h]
    cache = {}
    records = []
    current = {name: [] for name in ["OLD4_LINEAR","NEW4_LINEAR","PRIVATE_REVERSAL_LINEAR","PRIVATE_REVERSAL_GATE","PRIVATE_REVERSAL_REV_VETO","DUAL_ROUTE","HYBRID_3WAY"]}
    for dt in dates:
        if dt not in basic or dt not in fwd.index:
            continue
        x = feature_frame(dt, basic, cache)
        y = fwd.loc[dt].reindex(x.index)
        for name, score in strategies(x).items():
            s = score.replace([np.inf,-np.inf],np.nan).dropna().sort_values(ascending=False)
            if len(s) < 10:
                continue
            if buffer and current[name]:
                retain = set(s.head(min(len(s), int(n*1.5))).index)
                keep = [c for c in current[name] if c in retain]
                fill = [c for c in s.index if c not in keep]
                names = (keep+fill)[:n]
            else:
                names = s.head(n).index.tolist()
            old = set(current[name]); new = set(names)
            turn = 1.0 if not old else 1 - len(old & new) / max(1, n)
            current[name] = names
            port = y.reindex(names).mean()
            bench = y.reindex(s.index).mean()
            records.append({"date":dt,"strategy":name,"gross":port,"bench":bench,"excess_gross":port-bench,
                            "turnover":turn,"net":port-turn*cost_bps/10000,"excess":port-bench-turn*cost_bps/10000,
                            "n":len(names),"eligible":len(s)})
    return pd.DataFrame(records)


def summarize(df, h):
    rows=[]
    for name,g0 in df.groupby("strategy"):
        for label,lo,hi in (("train",START,SPLIT),("test",SPLIT,None)):
            g=g0[g0.date>=lo]
            if hi is not None: g=g[g.date<hi]
            if len(g)<10: continue
            periods=252/h
            ex=g.excess
            nav=(1+ex).cumprod()
            rows.append({"strategy":name,"sample":label,"n_periods":len(g),
                         "excess_ann":ex.mean()*periods,
                         "excess_sharpe":ex.mean()/ex.std(ddof=1)*math.sqrt(periods) if ex.std(ddof=1)>0 else np.nan,
                         "excess_mdd":(nav/nav.cummax()-1).min(),
                         "avg_turnover":g.turnover.mean(),"annual_turnover":g.turnover.mean()*periods,
                         "avg_eligible":g.eligible.mean()})
    return pd.DataFrame(rows)


def main():
    returns,basic=load_basic()
    all_results=[]
    for buffer in (False,True):
        for cost in (30,60,100):
            periods=period_test(returns,basic,h=20,n=25,cost_bps=cost,buffer=buffer)
            periods["buffer"]=buffer; periods["cost_bps"]=cost
            all_results.append(periods)
    detail=pd.concat(all_results,ignore_index=True)
    detail.to_csv(OUT/"transparent_rule_periods.csv",index=False,encoding="utf-8-sig")
    summaries=[]
    for (buffer,cost),g in detail.groupby(["buffer","cost_bps"]):
        s=summarize(g,20); s["buffer"]=buffer; s["cost_bps"]=cost; summaries.append(s)
    summary=pd.concat(summaries,ignore_index=True)
    summary.to_csv(OUT/"transparent_rule_summary.csv",index=False,encoding="utf-8-sig")
    key=summary[(summary.sample=="test")&(summary.cost_bps==30)&(~summary.buffer)].sort_values("excess_sharpe",ascending=False)
    (OUT/"summary.md").write_text("# Transparent new-factor rules: KOSPI ex-K200\n\n"+key.to_markdown(index=False),encoding="utf-8")
    print(key.to_string(index=False))

if __name__=="__main__":
    main()
