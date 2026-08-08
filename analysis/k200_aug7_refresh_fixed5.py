from pathlib import Path

base_path=Path(__file__).with_name("k200_aug7_refresh_fixed4.py")
source=base_path.read_text(encoding="utf-8")
source=source.replace(
'        out[asset] = fetch_naver_stock(asset)\n',
'        price_code = asset[1:] if str(asset).startswith("A") else str(asset)\n        out[asset] = fetch_naver_stock(price_code)\n'
)
ns={"__name__":"__main__","__file__":str(base_path)}
exec(compile(source,str(base_path),"exec"),ns)
