"""Episode 6 - synthetic orders and fixed costs for a building-materials store.
Sample data only. Seeded, so every run gives the same files.
Margins, delivery habits, credit terms and bad debt were SET here, per customer type."""
import os
import numpy as np, pandas as pd
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("data", exist_ok=True)
rng = np.random.default_rng([2026, 6])

MONTHS = pd.period_range("2025-10", "2026-09", freq="M")
END = pd.Timestamp("2026-09-30")
TYPES = {
    #               share  monthly return  median basket  margin mean/sd  deliver  median delivery cost  credit share
    "Contractor":   dict(share=0.20, p=0.55, median=14000, m=(0.055, 0.015), deliver=0.80, dcost=550, credit=0.70),
    "Homeowner":    dict(share=0.65, p=0.05, median=6500,  m=(0.100, 0.030), deliver=0.45, dcost=450, credit=0.00),
    "Small repair": dict(share=0.15, p=0.18, median=1800,  m=(0.140, 0.040), deliver=0.05, dcost=300, credit=0.00),
}
CREDIT_DAYS = [15, 30, 45, 60]
BAD_DEBT_P = 0.005
EXISTING = 700       # customers already on the books before Oct 2025   # chance a credit order is never paid

cust, orders = [], []
cid = oid = 0

def simulate(cid, t, m0, first):
    """Walk one customer month by month from m0. first=True: first order lands in m0."""
    global oid
    c = TYPES[t]
    month = m0
    while month <= MONTHS[-1]:
        if first or rng.random() < c["p"]:
            d = month.start_time + pd.Timedelta(days=int(rng.integers(0, month.days_in_month)))
            if d <= END:
                oid += 1
                value = int(round(rng.lognormal(np.log(c["median"]), 0.45), -1))
                margin = float(np.clip(rng.normal(*c["m"]), 0.01, 0.30))
                cogs = int(round(value * (1 - margin)))
                delivered = int(rng.random() < c["deliver"])
                dcost = int(round(rng.lognormal(np.log(c["dcost"]), 0.25), -1)) if delivered else 0
                on_credit = rng.random() < c["credit"]
                cdays = int(rng.choice(CREDIT_DAYS)) if on_credit else 0
                bad = int(on_credit and rng.random() < BAD_DEBT_P)
                orders.append((f"O{oid:05d}", f"C{cid:04d}", t, d.date(), value, cogs, delivered, dcost, cdays, bad))
        first = False
        month = month + 1

names = list(TYPES); probs = [v["share"] for v in TYPES.values()]
# existing customers already on the books before Oct 2025 (they only return, they are not "new")
for _ in range(EXISTING):
    cid += 1
    t = str(rng.choice(names, p=probs))
    cust.append((f"C{cid:04d}", t))
    simulate(cid, t, MONTHS[0], first=False)
# new customers who first buy during the year
for m in MONTHS:
    for _ in range(int(rng.integers(85, 120))):
        cid += 1
        t = str(rng.choice(names, p=probs))
        cust.append((f"C{cid:04d}", t))
        simulate(cid, t, m, first=True)

pd.DataFrame(cust, columns=["customer_id", "customer_type"]).to_csv("data/customers.csv", index=False)
o = pd.DataFrame(orders, columns=["order_id", "customer_id", "customer_type", "order_date", "order_value",
                                  "cogs", "delivered", "delivery_cost", "credit_days", "bad_debt"])
o.sort_values(["order_date", "order_id"]).to_csv("data/orders.csv", index=False)

fixed = []
for m in MONTHS:
    fixed.append((str(m), 30000, 60000, int(rng.integers(7000, 10000)), int(rng.integers(6000, 8000))))
pd.DataFrame(fixed, columns=["month", "rent", "salaries", "electricity", "other"]).to_csv("data/fixed_costs.csv", index=False)
print(len(cust), "customers,", len(o), "orders, revenue", int(o.order_value.sum()))
