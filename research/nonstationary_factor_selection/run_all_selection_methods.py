from __future__ import annotations

from itertools import combinations
from pathlib import Path
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "research/factor_regime_v1/results/factor_5d_returns.csv"
OUT = Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

FACTORS = ["MOM1M", "MOM12_1", "OP12_REV", "OPFY1_REV", "PBR12MF", "PER12MF", "PRIVATE_FLOW", "FOREIGN_FLOW"]
UNIVERSES = ["K200", "KOSDAQ", "KOSPI_EX_K200", "KOSPI_ALL", "KOSPI_KOSDAQ_ALL", "KOSDAQ_PLUS_KOSPI_EX_K200"]
PERIODS = ["VAL_2020_2022", "CONF_2023_2024", "STRESS_2025", "STRESS_2026"]
COSTS_BPS = [0, 10, 30]
N = len(FACTORS)


def period_of_date(dt):
    y = pd.Timestamp(dt).year
    if 2020 <= y <= 2022: return "VAL_2020_2022"
    if 2023 <= y <= 2024: return "CONF_2023_2024"
    if y == 2025: return "STRESS_2025"
    if y == 2026: return "STRESS_2026"
    return None


def softmax(x):
    x = np.asarray(x, dtype=float)
    x = x - np.nanmax(x)
    e = np.exp(np.clip(x, -50, 50))
    return e / e.sum() if e.sum() > 0 else np.ones(len(x)) / len(x)


def project_simplex(v):
    v = np.asarray(v, dtype=float)
    u = np.sort(v)[::-1]
    cssv = np.cumsum(u)
    idx = np.where(u * np.arange(1, len(v) + 1) > (cssv - 1))[0]
    if len(idx) == 0: return np.ones(len(v)) / len(v)
    rho = idx[-1]
    theta = (cssv[rho] - 1) / (rho + 1)
    w = np.maximum(v - theta, 0)
    return w / w.sum() if w.sum() > 0 else np.ones(len(v)) / len(v)


def norm_cdf(x):
    x = np.asarray(x, dtype=float)
    return 0.5 * (1 + np.vectorize(math.erf)(x / math.sqrt(2)))


def ann_sharpe(x):
    x = pd.to_numeric(x, errors="coerce").dropna()
    if len(x) < 4 or x.std(ddof=1) <= 0: return np.nan
    return float(x.mean() / x.std(ddof=1) * math.sqrt(252 / 5))


def cagr_5d(x):
    x = pd.to_numeric(x, errors="coerce").dropna()
    if len(x) < 2 or (x <= -1).any(): return np.nan
    nav = float(np.prod(1 + x.to_numpy(dtype=float)))
    years = len(x) * 5 / 252
    return float(nav ** (1 / years) - 1) if nav > 0 and years > 0 else np.nan


def max_drawdown(x):
    x = pd.to_numeric(x, errors="coerce").dropna()
    if len(x) == 0 or (x <= -1).any(): return np.nan
    nav = pd.Series(np.cumprod(1 + x.to_numpy(dtype=float)))
    return float((nav / nav.cummax() - 1).min())


def load_data():
    f = pd.read_csv(SRC)
    f["date"] = pd.to_datetime(f["date"])
    f = f[f.factor.isin(FACTORS) & f.universe.isin(UNIVERSES)].copy()
    f["ls_return"] = pd.to_numeric(f["ls_return"], errors="coerce")
    f = f.dropna(subset=["date", "universe", "factor", "ls_return"])
    mats = {}
    for u in UNIVERSES:
        w = f[f.universe.eq(u)].pivot(index="date", columns="factor", values="ls_return").sort_index().reindex(columns=FACTORS).dropna(how="any")
        mats[u] = w
    common = f.groupby(["date", "factor"], as_index=False).ls_return.mean().pivot(index="date", columns="factor", values="ls_return").sort_index().reindex(columns=FACTORS).dropna(how="any")
    dates = set(common.index)
    for w in mats.values(): dates &= set(w.index)
    dates = pd.DatetimeIndex(sorted(dates))
    return f, {u:w.loc[dates] for u,w in mats.items()}, common.loc[dates]


def discovery_stds(mats):
    out = {}
    for u,w in mats.items():
        s = w[w.index.year <= 2019].std(ddof=1).replace(0, np.nan)
        fill = float(np.nanmedian(s.to_numpy(dtype=float)))
        out[u] = s.fillna(fill if np.isfinite(fill) and fill > 0 else 1.0)
    return out


def empty_weights(index):
    return pd.DataFrame(np.ones((len(index), N))/N, index=index, columns=FACTORS)


def stage_a_weights(mats, dstd):
    result = {}
    for u,w in mats.items():
        std = dstd[u].to_numpy(dtype=float)
        result[("EW8",u)] = empty_weights(w.index)
        wm = empty_weights(w.index)
        for i in range(len(w)):
            if i >= 4:
                score = w.iloc[i-4:i].sum().to_numpy(dtype=float)
                top = np.argsort(score)[-2:]
                ww = np.zeros(N); ww[top] = 0.5; wm.iloc[i] = ww
        result[("MOM20_TOP2",u)] = wm
        wh, wf = empty_weights(w.index), empty_weights(w.index)
        G = np.zeros(N)
        for i in range(len(w)):
            t = max(i,1)
            wh.iloc[i] = softmax(math.sqrt(2*math.log(N)/t)*G)
            wf.iloc[i] = project_simplex(G/math.sqrt(t))
            G += np.clip(w.iloc[i].to_numpy(dtype=float)/std, -1, 1)
        result[("ADAPTIVE_HEDGE",u)] = wh
        result[("FTRL",u)] = wf
    return result


def best_split_stat(y, min_side=6):
    y = np.asarray(y, dtype=float); n = len(y)
    if n < 2*min_side: return np.nan, None
    full = np.sum((y-y.mean(axis=0))**2)
    if full <= 1e-12: return 0.0, None
    best, best_k = -np.inf, None
    for k in range(min_side, n-min_side+1):
        a,b = y[:k],y[k:]
        sse = np.sum((a-a.mean(axis=0))**2)+np.sum((b-b.mean(axis=0))**2)
        stat = (full-sse)/full
        if stat > best: best,best_k = stat,k
    return float(best), best_k


def discovery_cp_threshold(z, dates):
    d = z[dates.year <= 2019]; stats=[]
    for end in range(12,len(d)+1):
        s,_ = best_split_stat(d[max(0,end-40):end],6)
        if np.isfinite(s): stats.append(s)
    return float(np.quantile(stats,.95)) if stats else 1.0


def stage_b_weights(mats,dstd):
    result={}; cp_rows=[]
    for u,w in mats.items():
        z = w.to_numpy(dtype=float)/dstd[u].to_numpy(dtype=float)
        threshold = discovery_cp_threshold(z,w.index)
        topw,softw = empty_weights(w.index),empty_weights(w.index)
        seg_start=0
        for i in range(len(w)):
            if i-seg_start >= 12:
                ws=max(seg_start,i-40); stat,k=best_split_stat(z[ws:i],6)
                if np.isfinite(stat) and stat>threshold and k is not None and ws+k>seg_start:
                    seg_start=ws+k
                    cp_rows.append({"universe":u,"decision_date":w.index[i],"segment_start":w.index[seg_start],"stat":stat,"threshold":threshold})
            hist=z[seg_start:i]
            if len(hist):
                score=hist.sum(axis=0); top=np.argsort(score)[-2:]
                ww=np.zeros(N); ww[top]=.5; topw.iloc[i]=ww
                softw.iloc[i]=softmax(score/math.sqrt(len(hist)))
        result[("CP_TOP2",u)]=topw; result[("CP_SOFTMAX",u)]=softw
    return result,pd.DataFrame(cp_rows)


def latent_params(f):
    rows=[]; params={}
    for fac in FACTORS:
        p=f[(f.factor.eq(fac))&(f.date.dt.year<=2019)].pivot(index="date",columns="universe",values="ls_return").reindex(columns=UNIVERSES).dropna(how="any")
        y=p.mean(axis=1); resid=p.sub(y,axis=0)
        obs_ind=float(np.nanmean(np.nanvar(resid.to_numpy(dtype=float),axis=0,ddof=1)))
        r=max(obs_ind/len(UNIVERSES),1e-8)
        q=max(float(y.diff().dropna().var(ddof=1))-2*r,max(float(y.var(ddof=1))*1e-4,1e-8))
        p0=max(float(y.var(ddof=1)),r)
        params[fac]=(q,r,p0); rows.append({"factor":fac,"state_var_q":q,"mean_obs_var_r":r,"initial_var_p0":p0})
    return params,pd.DataFrame(rows)


def stage_c_weights(f,dates):
    params,param_df=latent_params(f); obs={}
    for fac in FACTORS:
        p=f[f.factor.eq(fac)].pivot(index="date",columns="universe",values="ls_return").reindex(columns=UNIVERSES)
        obs[fac]=p.reindex(dates).mean(axis=1).to_numpy(dtype=float)
    wprob,wtop=empty_weights(dates),empty_weights(dates)
    qdf=pd.DataFrame(index=dates,columns=FACTORS,dtype=float)
    mu=np.zeros(N); P=np.array([params[f][2] for f in FACTORS],dtype=float)
    for i,dt in enumerate(dates):
        pp=np.clip(norm_cdf(mu/np.sqrt(np.maximum(P,1e-12))),1e-6,1-1e-6)
        qdf.iloc[i]=pp; wprob.iloc[i]=pp/pp.sum(); top=np.argsort(pp)[-3:]
        ww=np.zeros(N); ww[top]=1/3; wtop.iloc[i]=ww
        for j,fac in enumerate(FACTORS):
            q,r,_=params[fac]; ppred=P[j]+q; y=obs[fac][i]
            if np.isfinite(y):
                K=ppred/(ppred+r); mu[j]=mu[j]+K*(y-mu[j]); P[j]=(1-K)*ppred
            else: P[j]=ppred
    weights={}
    for u in UNIVERSES:
        weights[("LATENT_PROB",u)]=wprob.copy(); weights[("LATENT_TOP3",u)]=wtop.copy()
    return weights,qdf,param_df


def common_features(common):
    arr=common.to_numpy(dtype=float); rows=[]
    for i in range(11,len(common)):
        cur=arr[i]; tr20=arr[i-3:i+1].sum(axis=0); tr60=arr[i-11:i+1].sum(axis=0); vol20=arr[i-3:i+1].std(axis=0,ddof=1)
        ranks=pd.Series(cur).rank(method="average",pct=True).to_numpy(dtype=float)
        rows.append((i,np.column_stack([cur,tr20,tr60,vol20,ranks])))
    return rows


def fit_logistic(X,y,l2=1e-3,n_iter=800):
    X=np.asarray(X,dtype=float); y=np.asarray(y,dtype=float); mean=X.mean(axis=0); std=X.std(axis=0,ddof=1); std[std<=1e-12]=1
    Z=np.column_stack([np.ones(len(X)),(X-mean)/std]); beta=np.zeros(Z.shape[1])
    for it in range(n_iter):
        p=1/(1+np.exp(-np.clip(Z@beta,-30,30))); grad=Z.T@(y-p)/len(y); grad[1:]-=l2*beta[1:]
        beta += (0.3/math.sqrt(1+it/50))*grad
    return beta,mean,std


def stage_d_weights(common):
    feats=common_features(common); arr=common.to_numpy(dtype=float); X=[]; y=[]
    for i,feat in feats:
        if i+1>=len(common) or common.index[i+1].year>2019: continue
        nxt=arr[i+1]
        for a,b in combinations(range(N),2): X.append(feat[a]-feat[b]); y.append(float(nxt[a]>nxt[b]))
    beta,mean,std=fit_logistic(np.asarray(X),np.asarray(y))
    wsoft,wtop=empty_weights(common.index),empty_weights(common.index); qdf=pd.DataFrame(np.ones((len(common),N))/N,index=common.index,columns=FACTORS)
    for i,feat in feats:
        if i+1>=len(common): continue
        score=np.zeros(N)
        for a,b in combinations(range(N),2):
            z=np.r_[1.,(feat[a]-feat[b]-mean)/std]; p=float(1/(1+np.exp(-np.clip(z@beta,-30,30))))
            score[a]+=p; score[b]+=1-p
        q=np.clip(score/(N-1),1e-6,None); ti=i+1; qdf.iloc[ti]=q; wsoft.iloc[ti]=q/q.sum(); top=np.argsort(q)[-3:]
        ww=np.zeros(N); ww[top]=1/3; wtop.iloc[ti]=ww
    weights={}
    for u in UNIVERSES:
        weights[("PAIRWISE_SOFT",u)]=wsoft.copy(); weights[("PAIRWISE_TOP3",u)]=wtop.copy()
    coef=pd.DataFrame({"feature":["intercept","current5_diff","trail20_diff","trail60_diff","vol20_diff","rank_diff"],"coefficient":beta})
    diag=[]
    for p in PERIODS:
        vals=[]
        for i,dt in enumerate(common.index):
            if period_of_date(dt)==p: vals.append(pd.Series(qdf.iloc[i]).rank().corr(pd.Series(common.iloc[i]).rank()))
        diag.append({"period":p,"median_same_period_selection_rank_ic":float(np.nanmedian(vals)) if vals else np.nan})
    return weights,qdf,coef,pd.DataFrame(diag)


def best_dpp_subset(q,corr):
    best_det=-np.inf; best=None
    for s in combinations(range(N),3):
        ix=np.array(s,dtype=int); qs=np.clip(q[ix],1e-6,None); C=corr[np.ix_(ix,ix)]+.05*np.eye(3); d=float(np.linalg.det(np.diag(qs)@C@np.diag(qs)))
        if d>best_det: best_det,best=d,ix
    return best,best_det


def stage_e_weights(mats,latent_q,pair_q):
    result={}; diag=[]
    for u,w in mats.items():
        wl,wp=empty_weights(w.index),empty_weights(w.index)
        for i,dt in enumerate(w.index):
            hist=w.iloc[max(0,i-12):i]
            corr=hist.corr().to_numpy(dtype=float) if len(hist)>=6 else np.eye(N)
            if not np.isfinite(corr).all(): corr=np.eye(N)
            ql=latent_q.loc[dt].to_numpy(dtype=float); qp=pair_q.loc[dt].to_numpy(dtype=float)
            sl,dl=best_dpp_subset(ql,corr); sp,dp=best_dpp_subset(qp,corr)
            x=np.zeros(N); x[sl]=1/3; wl.iloc[i]=x; x=np.zeros(N); x[sp]=1/3; wp.iloc[i]=x
            tl=np.argsort(ql)[-3:]; tp=np.argsort(qp)[-3:]
            def ac(ix):
                C=corr[np.ix_(ix,ix)]; vals=C[np.triu_indices_from(C,1)]; return float(vals.mean())
            diag.append({"date":dt,"universe":u,"dpp_latent_det":dl,"dpp_pairwise_det":dp,"dpp_latent_avg_corr":ac(sl),"top3_latent_avg_corr":ac(tl),"dpp_pairwise_avg_corr":ac(sp),"top3_pairwise_avg_corr":ac(tp)})
        result[("DPP_LATENT3",u)]=wl; result[("DPP_PAIRWISE3",u)]=wp
    return result,pd.DataFrame(diag)


def evaluate_weights(mats,weights):
    ret_rows=[]; perf_rows=[]
    for (strategy,u),ww in weights.items():
        r=mats[u].reindex(ww.index); gross=pd.Series(np.sum(ww.to_numpy(dtype=float)*r.to_numpy(dtype=float),axis=1),index=ww.index)
        turnover=.5*ww.diff().abs().sum(axis=1); turnover.iloc[0]=0
        for cost in COSTS_BPS:
            net=gross-(cost/10000)*turnover
            for dt in ww.index:
                p=period_of_date(dt)
                if p is not None: ret_rows.append({"date":dt,"period":p,"universe":u,"strategy":strategy,"cost_bps":cost,"gross_return":gross.loc[dt],"net_return":net.loc[dt],"turnover":turnover.loc[dt]})
            for p in PERIODS:
                m=np.array([period_of_date(d)==p for d in ww.index]); x=net[m]; t=turnover[m]
                perf_rows.append({"period":p,"universe":u,"strategy":strategy,"cost_bps":cost,"n_5d":len(x),"sharpe":ann_sharpe(x),"cagr":cagr_5d(x),"max_drawdown":max_drawdown(x),"annualized_weight_turnover":float(t.mean()*252/5) if len(t) else np.nan})
    return pd.DataFrame(ret_rows),pd.DataFrame(perf_rows)


def summarize_gates(perf):
    p10=perf[perf.cost_bps.eq(10)].copy(); ew=p10[p10.strategy.eq("EW8")][["period","universe","sharpe","cagr"]].rename(columns={"sharpe":"ew_sharpe","cagr":"ew_cagr"}); mom=p10[p10.strategy.eq("MOM20_TOP2")][["period","universe","sharpe"]].rename(columns={"sharpe":"mom_sharpe"})
    z=p10.merge(ew,on=["period","universe"],how="left").merge(mom,on=["period","universe"],how="left"); z["delta_sharpe_vs_ew8"]=z.sharpe-z.ew_sharpe; z["delta_sharpe_vs_mom20"]=z.sharpe-z.mom_sharpe; z["delta_cagr_vs_ew8"]=z.cagr-z.ew_cagr
    rows=[]
    for s in sorted(z.strategy.unique()):
        if s=="EW8": continue
        for p in PERIODS:
            q=z[(z.strategy.eq(s))&(z.period.eq(p))]
            rows.append({"strategy":s,"period":p,"median_delta_sharpe_vs_ew8":float(q.delta_sharpe_vs_ew8.median()),"positive_universes_vs_ew8":int((q.delta_sharpe_vs_ew8>0).sum()),"median_delta_sharpe_vs_mom20":float(q.delta_sharpe_vs_mom20.median()),"median_delta_cagr_vs_ew8":float(q.delta_cagr_vs_ew8.median())})
    out=pd.DataFrame(rows); gates=[]
    for s in sorted(out.strategy.unique()):
        a=out[(out.strategy.eq(s))&(out.period.eq("VAL_2020_2022"))]; b=out[(out.strategy.eq(s))&(out.period.eq("CONF_2023_2024"))]
        passed=bool(len(a) and len(b) and a.iloc[0].median_delta_sharpe_vs_ew8>0 and a.iloc[0].positive_universes_vs_ew8>=4 and b.iloc[0].median_delta_sharpe_vs_ew8>0 and b.iloc[0].positive_universes_vs_ew8>=4)
        gates.append({"strategy":s,"primary_gate_pass":passed})
    return out.merge(pd.DataFrame(gates),on="strategy",how="left")


def write_report(gate,cp,dpp_diag):
    def rr(s,p):
        q=gate[(gate.strategy.eq(s))&(gate.period.eq(p))]; return None if q.empty else q.iloc[0]
    stage_map={"Stage A — Online learning":["ADAPTIVE_HEDGE","FTRL"],"Stage B — Change-point adaptive":["CP_TOP2","CP_SOFTMAX"],"Stage C — Latent factor quality":["LATENT_PROB","LATENT_TOP3"],"Stage D — Pairwise ranking":["PAIRWISE_SOFT","PAIRWISE_TOP3"],"Stage E — Diversity-aware selection":["DPP_LATENT3","DPP_PAIRWISE3"]}
    lines=["# Non-stationary Factor Selection — Research Results","","All methods were pre-specified in `RESEARCH_ROADMAP.md` before this run.","Primary economic gate uses 10 bps cost per unit factor-weight turnover.","2025/2026 are stress diagnostics only.",""]
    for title,ss in stage_map.items():
        lines += [f"## {title}",""]
        for s in ss:
            v,c,y25,y26=rr(s,"VAL_2020_2022"),rr(s,"CONF_2023_2024"),rr(s,"STRESS_2025"),rr(s,"STRESS_2026")
            if v is None or c is None: continue
            passed=bool(gate[gate.strategy.eq(s)].primary_gate_pass.iloc[0])
            lines.append(f"- **{s}** — PASS={passed}; VAL ΔSharpe {v.median_delta_sharpe_vs_ew8:+.3f} ({int(v.positive_universes_vs_ew8)}/6), CONF {c.median_delta_sharpe_vs_ew8:+.3f} ({int(c.positive_universes_vs_ew8)}/6); 2025 {y25.median_delta_sharpe_vs_ew8:+.3f}; 2026 {y26.median_delta_sharpe_vs_ew8:+.3f}")
        lines.append("")
    lines += ["## Stage E incremental attribution",""]
    for dpp,base in [("DPP_LATENT3","LATENT_TOP3"),("DPP_PAIRWISE3","PAIRWISE_TOP3")]:
        for p in PERIODS:
            a,b=rr(dpp,p),rr(base,p)
            if a is not None and b is not None: lines.append(f"- {dpp} vs {base}, {p}: median Sharpe attribution {(a.median_delta_sharpe_vs_ew8-b.median_delta_sharpe_vs_ew8):+.3f}")
    if len(cp):
        cnt=cp.groupby("universe").size(); lines += ["","## Change-point diagnostics","",f"- Total detected change points: {len(cp)}; median per universe {float(cnt.median()):.1f}"]
    if len(dpp_diag):
        lines += ["","## Diversity diagnostics","",f"- DPP_LATENT3 minus quality-only top3 median selected pair correlation: {(dpp_diag.dpp_latent_avg_corr-dpp_diag.top3_latent_avg_corr).median():+.3f}",f"- DPP_PAIRWISE3 minus quality-only top3 median selected pair correlation: {(dpp_diag.dpp_pairwise_avg_corr-dpp_diag.top3_pairwise_avg_corr).median():+.3f}"]
    passers=sorted(gate[gate.primary_gate_pass].strategy.unique()); lines += ["","## Bottom line",""]
    if passers: lines += ["Primary-gate survivors: "+", ".join(passers)+".","A passing selector still requires robustness checks against implementation assumptions before any production use."]
    else: lines += ["No dynamic factor-selection method passes the pre-registered 2020–24 cross-universe gate.","This would be a strong negative result because the return-only panel has then failed under online, adaptive-window, latent-quality, pairwise-ranking, and diversity-aware selection frameworks."]
    return "\n".join(lines)


def main():
    f,mats,common=load_data(); dstd=discovery_stds(mats); weights={}
    weights.update(stage_a_weights(mats,dstd)); wb,cp=stage_b_weights(mats,dstd); weights.update(wb); wc,latent_q,param_df=stage_c_weights(f,common.index); weights.update(wc); wd,pair_q,pair_coef,pair_diag=stage_d_weights(common); weights.update(wd); we,dpp_diag=stage_e_weights(mats,latent_q,pair_q); weights.update(we)
    ret_panel,perf=evaluate_weights(mats,weights); gate=summarize_gates(perf)
    ret_panel.to_csv(OUT/"strategy_return_panel.csv",index=False,encoding="utf-8-sig"); perf.to_csv(OUT/"performance_by_universe.csv",index=False,encoding="utf-8-sig"); gate.to_csv(OUT/"primary_gate_summary.csv",index=False,encoding="utf-8-sig"); cp.to_csv(OUT/"change_points.csv",index=False,encoding="utf-8-sig"); param_df.to_csv(OUT/"latent_model_parameters.csv",index=False,encoding="utf-8-sig"); latent_q.reset_index(names="date").to_csv(OUT/"latent_quality_scores.csv",index=False,encoding="utf-8-sig"); pair_coef.to_csv(OUT/"pairwise_logit_coefficients.csv",index=False,encoding="utf-8-sig"); pair_diag.to_csv(OUT/"pairwise_rank_diagnostics.csv",index=False,encoding="utf-8-sig"); pair_q.reset_index(names="date").to_csv(OUT/"pairwise_quality_scores.csv",index=False,encoding="utf-8-sig"); dpp_diag.to_csv(OUT/"diversity_diagnostics.csv",index=False,encoding="utf-8-sig")
    report=write_report(gate,cp,dpp_diag); (OUT/"RESEARCH_SUMMARY.md").write_text(report,encoding="utf-8"); print(report)

if __name__=="__main__": main()
