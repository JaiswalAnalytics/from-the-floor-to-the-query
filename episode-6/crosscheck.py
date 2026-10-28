"""Compares the pandas model (python/unit_model.py) with the independent DuckDB SQL (run_sql.py). Differences should be rounding only."""
import os
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
a = pd.read_csv("results/sql_contribution_by_type.csv").set_index("customer_type")
b = pd.read_csv("results/by_customer_type.csv").set_index("customer_type")
print("max diff gross_profit        :", (a.gross_profit - b.gross_profit).abs().max())
print("max diff contribution (Rs)   :", round((a.contribution - b.contribution).abs().max(), 2))
print("max diff gross margin %      :", (a.gross_margin_pct - b.gross_margin_pct.round(1)).abs().max())
print("max diff contribution margin %:", (a.contribution_margin_pct - b.contribution_margin_pct.round(1)).abs().max())
s = pd.read_csv("results/sql_store_pl.csv").iloc[0]
p = pd.read_csv("results/store_pl.csv", index_col=0)["value"]
for k in ["revenue", "gross_profit", "contribution", "fixed_costs", "operating_profit", "breakeven_revenue_year"]:
    print(f"store {k:24s} diff:", round(abs(s[k] - p[k]), 2))
