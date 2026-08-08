from pathlib import Path

fixed1 = Path(__file__).with_name("k200_aug7_refresh_fixed.py")
base_path = Path(__file__).with_name("k200_aug7_refresh.py")
source = base_path.read_text(encoding="utf-8")

# Apply pagination patch from fixed1 without executing it.
wrapper = fixed1.read_text(encoding="utf-8")
start = wrapper.index("old_index = ")
# Simpler: duplicate the exact textual patches here.
old_index = '''def fetch_naver_index(page_size: int = 300) -> pd.DataFrame:\n    url = f"https://m.stock.naver.com/api/index/KPI200/price?pageSize={page_size}&page=1"\n    r = requests.get(url, headers=HEADERS, timeout=30)\n    r.raise_for_status()\n    f = pd.DataFrame(r.json())\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n'''
new_index = '''def fetch_naver_index(page_size: int = 300) -> pd.DataFrame:\n    frames = []\n    page = 1\n    while sum(len(x) for x in frames) < page_size:\n        url = f"https://m.stock.naver.com/api/index/KPI200/price?pageSize=60&page={page}"\n        r = requests.get(url, headers=HEADERS, timeout=30)\n        r.raise_for_status()\n        data = r.json()\n        if not data:\n            break\n        frames.append(pd.DataFrame(data))\n        if len(data) < 60:\n            break\n        page += 1\n    f = pd.concat(frames, ignore_index=True)\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n'''
old_stock = '''def fetch_naver_stock(code: str, page_size: int = 80) -> pd.DataFrame:\n    url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize={page_size}&page=1"\n    r = requests.get(url, headers=HEADERS, timeout=30)\n    r.raise_for_status()\n    f = pd.DataFrame(r.json())\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n'''
new_stock = '''def fetch_naver_stock(code: str, page_size: int = 80) -> pd.DataFrame:\n    frames = []\n    page = 1\n    while sum(len(x) for x in frames) < page_size:\n        url = f"https://m.stock.naver.com/api/stock/{code}/price?pageSize=60&page={page}"\n        r = requests.get(url, headers=HEADERS, timeout=30)\n        r.raise_for_status()\n        data = r.json()\n        if not data:\n            break\n        frames.append(pd.DataFrame(data))\n        if len(data) < 60:\n            break\n        page += 1\n    f = pd.concat(frames, ignore_index=True)\n    f["date"] = pd.to_datetime(f["localTradedAt"])\n    f["open"] = f["openPrice"].map(num)\n    f["close"] = f["closePrice"].map(num)\n    return f.set_index("date")[["open", "close"]].sort_index()\n'''
source = source.replace(old_index, new_index).replace(old_stock, new_stock)

source = source.replace(
    '    p_latest = panel.xs(latest_dt, level="date")\n',
    '    p_latest_full = panel.loc[[latest_dt]]\n    p_latest = p_latest_full.xs(latest_dt, level="date")\n'
)
source = source.replace(
    '    latest_targets = off.targets_for_date(p_latest, scores[latest_dt], basic_panels[latest_dt])\n',
    '    latest_targets = off.targets_for_date(p_latest_full, scores[latest_dt], basic_panels[latest_dt])\n'
)
source = source.replace(
    '    p_old = panel.xs(OLD_DATE, level="date")\n    old_targets = off.targets_for_date(p_old, scores[OLD_DATE], basic_panels[OLD_DATE])\n',
    '    p_old_full = panel.loc[[OLD_DATE]]\n    p_old = p_old_full.xs(OLD_DATE, level="date")\n    old_targets = off.targets_for_date(p_old_full, scores[OLD_DATE], basic_panels[OLD_DATE])\n'
)

ns = {"__name__": "__main__", "__file__": str(base_path)}
exec(compile(source, str(base_path), "exec"), ns)
