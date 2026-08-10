from pathlib import Path

HERE = Path(__file__).resolve().parent
src_path = HERE / "k200_factor_sleeve_topn_sensitivity.py"
source = src_path.read_text(encoding="utf-8")
source = source.replace('summary.sample == "test"', 'summary["sample"] == "test"')
source = source.replace('summary.sample == "train"', 'summary["sample"] == "train"')
source = source.replace('attribution.sample == "test"', 'attribution["sample"] == "test"')
source = source.replace('outlier.sample == "test"', 'outlier["sample"] == "test"')
source = source.replace('consensus.sample == "test"', 'consensus["sample"] == "test"')
ns = {"__name__": "__main__", "__file__": str(src_path)}
exec(compile(source, str(src_path), "exec"), ns)
