"""Compares the SQL result (run_sql.py) with the independent pandas result (python/rfm_pandas.py), customer by customer."""
import os
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
a = pd.read_csv("results/sql_rfm_customers.csv").set_index("customer_id").sort_index()
b = pd.read_csv("results/pandas_rfm_customers.csv").set_index("customer_id").sort_index()
print("customers  SQL / pandas:", len(a), "/", len(b))
for col in ["recency_days", "frequency", "monetary", "r_score", "f_score", "m_score", "segment"]:
    print(f"mismatches in {col:13s}:", int((a[col] != b[col]).sum()))
