"""Episode 7 - RFM in pandas, written separately from the SQL so the two can be compared."""
import os
import numpy as np, pandas as pd
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

AS_OF = pd.Timestamp("2026-10-01")
o = pd.read_csv("data/orders.csv", parse_dates=["order_date"])
c = pd.read_csv("data/customers.csv")

g = o.groupby("customer_id").agg(last=("order_date", "max"), frequency=("order_id", "count"),
                                 monetary=("order_value", "sum")).reset_index()
g["recency_days"] = (AS_OF - g["last"]).dt.days

g["r_score"] = pd.cut(g["recency_days"], [-1, 30, 60, 90, 180, 10**6], labels=[5, 4, 3, 2, 1]).astype(int)
g["f_score"] = pd.cut(g["frequency"], [0, 1, 2, 4, 7, 10**6], labels=[1, 2, 3, 4, 5]).astype(int)

def ntile(values_sorted_index, n_buckets=5):
    """Same split as SQL NTILE: the first (n % 5) buckets get one extra row."""
    n = len(values_sorted_index)
    base, extra = divmod(n, n_buckets)
    sizes = [base + 1 if k < extra else base for k in range(n_buckets)]
    return np.repeat(np.arange(1, n_buckets + 1), sizes)

g = g.sort_values(["monetary", "customer_id"]).reset_index(drop=True)
g["m_score"] = ntile(g.index)

def segment(r):
    if r.r_score >= 4 and r.f_score >= 4: return "Champions"
    if r.r_score >= 3 and r.f_score >= 3: return "Loyal"
    if r.r_score <= 2 and r.f_score >= 3: return "At risk"
    if r.f_score == 1 and r.r_score >= 4: return "New"
    if r.f_score <= 2 and r.r_score <= 2: return "Lapsed one-timers"
    return "Occasional"
g["segment"] = g.apply(segment, axis=1)
g = g.sort_values("customer_id")
g.drop(columns="last").to_csv("results/pandas_rfm_customers.csv", index=False)

s = g.groupby("segment").agg(customers=("customer_id", "count"), revenue=("monetary", "sum"),
                             avg_orders=("frequency", "mean"), avg_spend=("monetary", "mean"),
                             avg_recency_days=("recency_days", "mean"))
s["customer_share_pct"] = 100 * s.customers / s.customers.sum()
s["revenue_share_pct"] = 100 * s.revenue / s.revenue.sum()
s = s.sort_values("revenue", ascending=False).round(1)
s.to_csv("results/pandas_segment_summary.csv")
print(s.to_string())

# Segments never saw the customer type. Do they find the contractors anyway?
mix = g.merge(c, on="customer_id").groupby(["segment", "customer_type"]).size().unstack(fill_value=0)
print(); print(mix.to_string())
champ = mix.loc["Champions"]
print("\nContractors among Champions: %.1f%%" % (100 * champ["Contractor"] / champ.sum()))

# The NTILE pitfall: ranking one-order customers into 5 equal buckets splits identical customers.
one = g[g.frequency == 1].sort_values("customer_id")
print("\nCustomers with exactly 1 order:", len(one),
      "-> NTILE(5) on frequency would give them", len(set(ntile(one.index))), "different scores")
