"""Independent checks of python/elasticity.py.
1) Baseline slope again in DuckDB SQL (regr_slope on logs).
2) Controlled model again with plain numpy least squares (no statsmodels)."""
import duckdb, numpy as np, pandas as pd

res = pd.read_csv("results/elasticity_by_sku.csv").set_index("sku")
d = pd.read_csv("data/weekly_sales.csv")

sql = duckdb.sql("""
  SELECT sku, regr_slope(ln(units), ln(price)) AS naive_sql
  FROM 'data/weekly_sales.csv' GROUP BY sku
""").df().set_index("sku")

out = []
for sku, g in d.groupby("sku"):
    X = np.column_stack([np.log(g.price), g.week,
                         *[(g.month == m).astype(float) for m in range(1, 13)]])   # 12 month columns = intercept
    beta, *_ = np.linalg.lstsq(X, np.log(g.units), rcond=None)
    out.append((sku, beta[0]))
np_ = pd.DataFrame(out, columns=["sku", "model_np"]).set_index("sku")

c = res[["naive_e", "model_e"]].join(sql).join(np_)
c["diff_naive"] = (c.naive_e - c.naive_sql).abs()
c["diff_model"] = (c.model_e - c.model_np).abs()
print(c.round(6).to_string())
print("max diff naive (python vs SQL):", c.diff_naive.max())
print("max diff model (statsmodels vs numpy):", c.diff_model.max())
