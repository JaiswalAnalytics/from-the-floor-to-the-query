"""Episode 5 - synthetic customer orders for a building-materials store.
Sample data only. Seeded, so every run gives the same file.
Repeat behaviour was SET here (contractors come back, homeowners mostly do not)."""
import os
import numpy as np, pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("data", exist_ok=True)
rng = np.random.default_rng(2026)

START, END = pd.Timestamp("2025-10-01"), pd.Timestamp("2026-09-30")
MONTHS = pd.period_range("2025-10", "2026-09", freq="M")
# monthly chance a customer of this type orders again, and typical basket (Rs)
TYPES = {"Contractor": dict(share=0.20, p=0.55, median=14000),
         "Homeowner":  dict(share=0.65, p=0.05, median=6500),
         "Small repair": dict(share=0.15, p=0.18, median=1800)}

cust, orders = [], []
cid = oid = 0
for m in MONTHS:
    n_new = int(rng.integers(85, 120))
    days = m.days_in_month
    for _ in range(n_new):
        cid += 1
        t = rng.choice(list(TYPES), p=[v["share"] for v in TYPES.values()])
        cfg = TYPES[t]
        cust.append((f"C{cid:04d}", t))
        month = m
        first = True
        while month <= MONTHS[-1]:
            if first or rng.random() < cfg["p"]:
                d = m.start_time + pd.Timedelta(days=int(rng.integers(0, days))) if first else \
                    month.start_time + pd.Timedelta(days=int(rng.integers(0, month.days_in_month)))
                if d <= END:
                    oid += 1
                    val = int(round(rng.lognormal(np.log(cfg["median"]), 0.45), -1))
                    orders.append((f"O{oid:05d}", f"C{cid:04d}", d.date(), val))
            first = False
            month = month + 1
cust = pd.DataFrame(cust, columns=["customer_id", "customer_type"])
orders = pd.DataFrame(orders, columns=["order_id", "customer_id", "order_date", "order_value"])
cust.to_csv("data/customers.csv", index=False)
orders.sort_values(["order_date", "order_id"]).to_csv("data/orders.csv", index=False)
print(len(cust), "customers,", len(orders), "orders")
