from pathlib import Path

path = Path(__file__).with_name("k200_aug7_refresh.py")
source = path.read_text(encoding="utf-8")

old_index = '''def fetch_naver_index(page_size: int = 300) -> pd.DataFrame:\n    url = f"https://m.stock.naver.com/api/index/KPI200/price?pageSize={page_size}&page=1"\n    r = requests.get(url, headers=HEADERS, timeout=30)\n    r.raise_for_status()\n    f = pd.DataFrame(r.json())\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n'''
new_index = '''def fetch_naver_index(page_size: int = 300) -> pd.DataFrame:\n    frames = []\n    page = 1\n    while sum(len(x) for x in frames) < page_size:\n        url = f"https://m.stock.naver.com/api/index/KPI200/price?pageSize=60&page={page}"\n        r = requests.get(url, headers=HEADERS, timeout=30)\n        r.raise_for_status()\n        data = r.json()\n        if not data:\n            break\n        frames.append(pd.DataFrame(data))\n        if len(data) < 60:\n            break\n        page += 1\n    f = pd.concat(frames, ignore_index=True)\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n'''

old_stock = '''def fetch_naver_stock(code: str, page_size: int = 80) -> pd.DataFrame:\n    url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize={page_size}&page=1"\n    r = requests.get(url, headers=HEADERS, timeout=30)\n    r.raise_for_status()\n    f = pd.DataFrame(r.json())\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n'''
new_stock = '''def fetch_naver_stock(code: str, page_size: int = 80) -> pd.DataFrame:\n    frames = []\n    page = 1\n    while sum(len(x) for x in frames) < page_size:\n        url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize=60&page={page}"\n        r = requests.get(url, headers=HEADERS, timeout=30)\n        r.raise_for_status()\n        data = r.json()\n        if not data:\n            break\n        frames.append(pd.DataFrame(data))\n        if len(data) < 60:\n            break\n        page += 1\n    f = pd.concat(frames, ignore_index=True)\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n'''

if old_index not in source or old_stock not in source:
    raise RuntimeError("Expected Naver fetch functions not found")
source = source.replace(old_index, new_index).replace(old_stock, new_stock)
ns = {"__name__": "__main__", "__file__": str(path)}
exec(compile(source, str(path), "exec"), ns)
