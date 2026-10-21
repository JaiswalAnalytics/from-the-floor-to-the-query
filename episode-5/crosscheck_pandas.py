"""Independent pandas check of the SQL results (no DuckDB)."""
import os
import pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
o = pd.read_csv("data/orders.csv", parse_dates=["order_date"])
c = pd.read_csv("data/customers.csv")
o["m"] = o["order_date"].dt.to_period("M")
first = o.groupby("customer_id").agg(first_date=("order_date", "min"), cohort=("m", "min"))

# 1) cohort retention table
o = o.join(first, on="customer_id")
o["month_n"] = (o["m"] - o["cohort"]).apply(lambda x: x.n)
act = o.drop_duplicates(["customer_id", "month_n"]).groupby(["cohort", "month_n"]).size()
size = first.groupby("cohort").size()
ret = (act / size.reindex(act.index.get_level_values(0)).values * 100).round(1)
sql = pd.read_csv("results/cohort_retention.csv")
sql["cohort"] = pd.to_datetime(sql["cohort_month"]).dt.to_period("M")
diff = sql.set_index(["cohort", "month_n"])["retention_pct"] - ret
print("max retention difference:", diff.abs().max())

# 2) never back within 3 months (mature customers)
mature = first[first["first_date"] < "2026-07-01"]
j = o[o["customer_id"].isin(mature.index)]
back = j[(j["order_date"] > j["first_date"]) & (j["month_n"] <= 3)].groupby("customer_id").size()
print("mature:", len(mature), "came back:", len(back),
      "never back %:", round(100 * (1 - len(back) / len(mature)), 1))

# 3) revenue by type
pc = o.groupby("customer_id").agg(n=("order_id", "count"), rev=("order_value", "sum")).join(c.set_index("customer_id"))
g = pc.groupby("customer_type").agg(customers=("n", "size"), repeat=("n", lambda s: round(100 * (s > 1).mean(), 1)), rev=("rev", "sum"))
g["share"] = (100 * g["rev"] / g["rev"].sum()).round(1)
print(g.sort_values("rev", ascending=False))
print("repeat customers' revenue share:", round(100 * pc.loc[pc.n > 1, "rev"].sum() / pc.rev.sum(), 1))
