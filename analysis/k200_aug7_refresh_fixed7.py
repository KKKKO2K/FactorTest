from pathlib import Path

base_path=Path(__file__).with_name("k200_aug7_refresh_fixed6.py")
source=base_path.read_text(encoding="utf-8")
# Insert fallback into the generated original-source replacement by adding one more text replacement
# to the wrapper before it executes the source.
needle='''ns={"__name__":"__main__","__file__":str(base_path)}\nexec(compile(source,str(base_path),"exec"),ns)\n'''
replacement='''source=source.replace(\n    '        s = float(p.loc[start, start_field])\\n        e = float(p.loc[end, "close"])\\n',\n    '        s = float(p.loc[start, start_field])\\n        if (not np.isfinite(s)) or s == 0.0:\\n            s = float(p.loc[start, "close"])\\n        e = float(p.loc[end, "close"])\\n'\n)\nns={"__name__":"__main__","__file__":str(base_path)}\nexec(compile(source,str(base_path),"exec"),ns)\n'''
if needle not in source:
    raise RuntimeError("wrapper execution marker not found")
source=source.replace(needle,replacement)
ns={"__name__":"__main__","__file__":str(base_path)}
exec(compile(source,str(base_path),"exec"),ns)
