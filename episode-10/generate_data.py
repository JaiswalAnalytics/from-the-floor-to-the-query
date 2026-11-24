"""Episode 10 dataset: sales, supplier bills and month-end stock for a building-materials store.
Synthetic, seeded. Stock days, credit terms, payment delays and supplier terms are SET here.
Flows start 1 Aug 2025 (a 2-month warm-up) so the October 2025 month-end balances are not
understated; the analysis window is 1 Oct 2025 to 30 Sep 2026."""
import numpy as np, pandas as pd

rng = np.random.default_rng(2026 + 10)

# category: (share of revenue, gross margin, stock days, days the store takes to pay the supplier)
CATS = {
 "Cement OPC 53":  (0.30, 0.035, 10, 10),
 "TMT Bar 12mm":   (0.22, 0.060, 18,  7),
 "River Sand":     (0.12, 0.100,  5,  3),
 "Emulsion Paint": (0.14, 0.140, 50, 30),
 "Wall Putty":     (0.08, 0.180, 42, 30),
 "Floor Tile 2x2": (0.14, 0.120, 95, 20),
}
# customer type: (share of revenue, average sale line in Rs, credit days allowed)
TYPES = {
 "Contractor":   (0.72, 28000, 30),
 "Homeowner":    (0.24,  7500,  0),
 "Small repair": (0.04,  2500,  7),
}
SEASON = {10:1.10, 11:1.10, 12:1.00, 1:1.00, 2:1.00, 3:1.05, 4:1.05, 5:0.95, 6:0.80, 7:0.70, 8:0.70, 9:0.85}
BASE = 2_900_000                                   # Rs of sales in a month with season 1.0
months = pd.period_range("2025-08", "2026-09", freq="M")
names, shares = list(CATS), np.array([v[0] for v in CATS.values()])

sales = []
for i, m in enumerate(months):
    target_m = BASE * SEASON[m.month] * (1 + 0.008 * i)
    dim = m.days_in_month
    for t, (sh, avg, terms) in TYPES.items():
        total, target = 0, target_m * sh
        while total < target:
            val = max(500, int(round(rng.lognormal(np.log(avg) - 0.5 * 0.6**2, 0.6))))
            cat = rng.choice(names, p=shares)
            d = m.to_timestamp() + pd.Timedelta(days=int(rng.integers(0, dim)))
            if t == "Contractor":   late = int(rng.poisson(8)) + (25 if rng.random() < 0.12 else 0)
            elif t == "Small repair": late = int(rng.poisson(2))
            else:                    late = 0
            cogs = int(round(val * (1 - CATS[cat][1])))
            sales.append((d.date(), t, cat, val, cogs, (d + pd.Timedelta(days=terms + late)).date()))
            total += val
sales = pd.DataFrame(sales, columns=["sale_date","customer_type","category","revenue","cogs","paid_date"])
sales.insert(0, "sale_id", [f"S{n+1:05d}" for n in range(len(sales))])
sales["sale_date"] = pd.to_datetime(sales.sale_date)

bills, stock, n = [], [], 0
opening = {}
for m in months:
    dim = m.days_in_month
    me = m.to_timestamp(how="end").normalize()
    for cat, (sh, mg, sdays, pdays) in CATS.items():
        cogs = int(sales[(sales.category == cat) & (sales.sale_date.dt.to_period("M") == m)].cogs.sum())
        if cat not in opening: opening[cat] = sdays * cogs / dim
        target = sdays * cogs / dim * rng.uniform(0.92, 1.08)
        buy = max(0, int(round(cogs + target - opening[cat])))
        w = rng.dirichlet(np.ones(4)); amts = [int(round(buy * x)) for x in w[:3]]; amts.append(buy - sum(amts))
        for a in amts:
            n += 1
            d = m.to_timestamp() + pd.Timedelta(days=int(rng.integers(0, dim)))
            bills.append((f"B{n:04d}", d.date(), cat, a, (d + pd.Timedelta(days=pdays + int(rng.poisson(1.5)))).date()))
        closing = int(round(opening[cat])) + buy - cogs
        stock.append((me.date(), cat, closing)); opening[cat] = closing
bills = pd.DataFrame(bills, columns=["bill_id","bill_date","category","amount","paid_date"])
stock = pd.DataFrame(stock, columns=["month_end","category","closing_stock"])

sales.assign(sale_date=sales.sale_date.dt.date).to_csv("data/sales.csv", index=False)
bills.to_csv("data/purchases.csv", index=False)
stock.to_csv("data/inventory_month_end.csv", index=False)
pd.DataFrame([(k, *v) for k, v in CATS.items()], columns=["category","set_revenue_share","set_margin","set_stock_days","set_payable_days"]
   ).to_csv("data/settings_generator.csv", index=False)
print("sales", len(sales), "bills", len(bills), "stock rows", len(stock))
