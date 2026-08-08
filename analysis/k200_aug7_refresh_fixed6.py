from pathlib import Path

base_path=Path(__file__).with_name("k200_aug7_refresh.py")
source=base_path.read_text(encoding="utf-8")
source=source.replace("import requests\n", "import requests\nimport yfinance as yf\n")

# Naver pagination.
source=source.replace(
'''def fetch_naver_index(page_size: int = 300) -> pd.DataFrame:\n    url = f"https://m.stock.naver.com/api/index/KPI200/price?pageSize={page_size}&page=1"\n    r = requests.get(url, headers=HEADERS, timeout=30)\n    r.raise_for_status()\n    f = pd.DataFrame(r.json())\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n''',
'''def fetch_naver_index(page_size: int = 300) -> pd.DataFrame:\n    frames=[]; page=1\n    while sum(len(x) for x in frames) < page_size:\n        url=f"https://m.stock.naver.com/api/index/KPI200/price?pageSize=60&page={page}"\n        r=requests.get(url,headers=HEADERS,timeout=30); r.raise_for_status(); data=r.json()\n        if not data: break\n        frames.append(pd.DataFrame(data))\n        if len(data)<60: break\n        page+=1\n    f=pd.concat(frames,ignore_index=True)\n    f["date"]=pd.to_datetime(f["localTradedAt"]); f["open"]=f["openPrice"].map(num); f["close"]=f["closePrice"].map(num)\n    return f.set_index("date")[["open","close"]].sort_index()\n''')
source=source.replace(
'''def fetch_naver_stock(code: str, page_size: int = 80) -> pd.DataFrame:\n    url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize={page_size}&page=1"\n    r = requests.get(url, headers=HEADERS, timeout=30)\n    r.raise_for_status()\n    f = pd.DataFrame(r.json())\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    for src, dst in (("closePrice", "close"), ("openPrice", "open")):\n        frame[dst] = frame[src].map(num)\n    return frame.set_index("date")[["open", "close"]].sort_index()\n''',
'''def fetch_naver_stock(code: str, page_size: int = 80) -> pd.DataFrame:\n    pass\n''')
# Above variant may not match; apply exact function from current source.
old_stock='''def fetch_naver_stock(code: str, page_size: int = 80) -> pd.DataFrame:\n    url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize={page_size}&page=1"\n    r = requests.get(url, headers=HEADERS, timeout=30)\n    r.raise_for_status()\n    f = pd.DataFrame(r.json())\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n'''
new_stock='''def fetch_naver_stock(code: str, page_size: int = 80) -> pd.DataFrame:\n    code = str(code)\n    if code.startswith("A"):\n        code = code[1:]\n    frames=[]; page=1\n    while sum(len(x) for x in frames) < page_size:\n        url=f"https://m.stock.naver.com/api/stock/{code}/price?pageSize=60&page={page}"\n        r=requests.get(url,headers=HEADERS,timeout=30); r.raise_for_status(); data=r.json()\n        if not data: break\n        frames.append(pd.DataFrame(data))\n        if len(data)<60: break\n        page+=1\n    if frames:\n        f=pd.concat(frames,ignore_index=True)\n        f["date"]=pd.to_datetime(f["localTradedAt"]); f["open"]=f["openPrice"].map(num); f["close"]=f["closePrice"].map(num)\n        return f.set_index("date")[["open","close"]].sort_index()\n    y=yf.download(f"{code}.KS",start="2026-07-15",end="2026-08-09",auto_adjust=False,progress=False)\n    if y.empty: raise RuntimeError(f"No price data for {code}")\n    if isinstance(y.columns,pd.MultiIndex): op=y["Open"].iloc[:,0]; cl=y["Close"].iloc[:,0]\n    else: op=y["Open"]; cl=y["Close"]\n    f=pd.DataFrame({"open":op,"close":cl}); f.index=pd.to_datetime(f.index).tz_localize(None)\n    return f.sort_index()\n'''
source=source.replace(old_stock,new_stock)

# Preserve date level for target generation.
source=source.replace('    p_latest = panel.xs(latest_dt, level="date")\n','    p_latest_full = panel.loc[[latest_dt]]\n    p_latest = p_latest_full.xs(latest_dt, level="date")\n')
source=source.replace('    latest_targets = off.targets_for_date(p_latest, scores[latest_dt], basic_panels[latest_dt])\n','    latest_targets = off.targets_for_date(p_latest_full, scores[latest_dt], basic_panels[latest_dt])\n')
source=source.replace('    p_old = panel.xs(OLD_DATE, level="date")\n    old_targets = off.targets_for_date(p_old, scores[OLD_DATE], basic_panels[OLD_DATE])\n','    p_old_full = panel.loc[[OLD_DATE]]\n    p_old = p_old_full.xs(OLD_DATE, level="date")\n    old_targets = off.targets_for_date(p_old_full, scores[OLD_DATE], basic_panels[OLD_DATE])\n')
# Normalize target output index field.
source=source.replace('    f = weights.rename("weight").reset_index().rename(columns={"index": "asset"})\n','    f = weights.rename("weight").reset_index()\n    f = f.rename(columns={f.columns[0]: "asset"})\n')

ns={"__name__":"__main__","__file__":str(base_path)}
exec(compile(source,str(base_path),"exec"),ns)
