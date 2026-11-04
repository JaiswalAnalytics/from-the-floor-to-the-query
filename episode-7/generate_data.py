"""Episode 7 - synthetic customers and orders for a building-materials store.
Sample data only. Seeded, so every run gives the same files.
Return habits AND "going quiet" habits were SET here, per customer type."""
import os
import numpy as np, pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("data", exist_ok=True)
rng = np.random.default_rng([2026, 7])

MONTHS = pd.period_range("2025-10", "2026-09", freq="M")
END = pd.Timestamp("2026-09-30")
TYPES = {   #               share  monthly order chance  median basket  monthly chance of going quiet for good
    "Contractor":   dict(share=0.20, p=0.55, median=14000, quit=0.06),
    "Homeowner":    dict(share=0.65, p=0.05, median=6500,  quit=0.00),
    "Small repair": dict(share=0.15, p=0.18, median=1800,  quit=0.04),
}
EXISTING = 700   # customers already on the books before Oct 2025
cust, orders = [], []
cid = oid = 0

def simulate(cid, t, m0, first):
    global oid
    c = TYPES[t]
    month, active = m0, True
    while month <= MONTHS[-1] and active:
        if first or rng.random() < c["p"]:
            d = month.start_time + pd.Timedelta(days=int(rng.integers(0, month.days_in_month)))
            if d <= END:
                oid += 1
                value = int(round(rng.lognormal(np.log(c["median"]), 0.45), -1))
                orders.append((f"O{oid:05d}", f"C{cid:04d}", d.date(), value))
        first = False
        if rng.random() < c["quit"]:
            active = False
        month = month + 1

names = list(TYPES); probs = [v["share"] for v in TYPES.values()]
for _ in range(EXISTING):
    cid += 1
    t = str(rng.choice(names, p=probs))
    cust.append((f"C{cid:04d}", t))
    simulate(cid, t, MONTHS[0], first=False)
for m in MONTHS:
    for _ in range(int(rng.integers(85, 120))):
        cid += 1
        t = str(rng.choice(names, p=probs))
        cust.append((f"C{cid:04d}", t))
        simulate(cid, t, m, first=True)

pd.DataFrame(cust, columns=["customer_id", "customer_type"]).to_csv("data/customers.csv", index=False)
o = pd.DataFrame(orders, columns=["order_id", "customer_id", "order_date", "order_value"])
o.sort_values(["order_date", "order_id"]).to_csv("data/orders.csv", index=False)
print(len(cust), "customers,", o.customer_id.nunique(), "ordered,", len(o), "orders, revenue", int(o.order_value.sum()))
