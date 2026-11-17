"""Episode 9 dataset: purchase orders from 8 suppliers, 1 Oct 2025 to 30 Sep 2026.
Synthetic, seeded. Each supplier's delivery habits and price level are SET here
(the trap: the cheapest quoted rate belongs to the least reliable supplier)."""
import numpy as np, pandas as pd

rng = np.random.default_rng(2026 + 9)

# supplier: (category, base market rate Rs/unit, typical qty, n_orders, promised_days,
#            on_time_prob, mean_days_late, fill_rate, reject_rate, price_index_vs_market, invoice_creep)
S = {
 "Sharma Cement":       ("Cement",      365.0, 400, 110, 3, 0.93, 1.5, 0.990, 0.008, 1.01, 0.002),
 "Tiwari Steel":        ("Steel",        62.0, 900,  95, 5, 0.58, 4.0, 0.930, 0.035, 0.94, 0.015),
 "Yadav Sand Supply":   ("Sand",         48.0, 700,  90, 2, 0.80, 2.0, 0.970, 0.015, 0.98, 0.005),
 "Pandey Paints":       ("Paint",      2150.0,  25,  70, 4, 0.90, 1.5, 0.985, 0.010, 1.04, 0.003),
 "Mehta Tiles":         ("Tile",        310.0, 120,  80, 6, 0.72, 3.0, 0.950, 0.045, 0.99, 0.008),
 "Chauhan Pipes":       ("Pipes",       145.0, 150,  75, 4, 0.96, 1.0, 0.995, 0.005, 1.06, 0.001),
 "Saxena Electricals":  ("Electricals", 520.0,  60,  85, 5, 0.85, 2.0, 0.970, 0.020, 1.02, 0.010),
 "Dubey Hardware":      ("Hardware",    210.0,  80,  95, 3, 0.75, 2.5, 0.960, 0.012, 0.97, 0.004),
}
first, last = pd.Timestamp("2025-10-01"), pd.Timestamp("2026-09-22")   # late orders still land by 30 Sep
span = (last - first).days
rows, n = [], 0
for sup, (cat, base, qty, n_po, prom, p_on, late_mean, fill, rej, pidx, creep) in S.items():
    odays = np.sort(rng.integers(0, span + 1, n_po))
    p_short = (1 - fill) / 0.175                       # short orders lose 5 to 30 percent
    for d in odays:
        n += 1
        od = first + pd.Timedelta(days=int(d))
        market = round(base * (1 + 0.0004 * d) * rng.normal(1, 0.015), 2)
        quoted = round(market * pidx * rng.normal(1, 0.005), 2)
        invoiced = round(quoted * (1 + creep * rng.uniform(0, 2)), 2)
        q_ord = max(5, int(round(qty * rng.lognormal(0, 0.25))))
        q_rec = q_ord if rng.random() > p_short else int(round(q_ord * (1 - rng.uniform(0.05, 0.30))))
        q_rej = int(rng.binomial(q_rec, rej))
        if rng.random() < p_on: delay = int(rng.choice([-1, 0, 0, 0]))
        else:                   delay = 1 + int(rng.poisson(max(late_mean - 1, 0.1)))
        rows.append((f"PO{n:04d}", sup, cat, od.date(), (od + pd.Timedelta(days=prom)).date(),
                     (od + pd.Timedelta(days=prom + delay)).date(), q_ord, q_rec, q_rej, market, quoted, invoiced))
df = pd.DataFrame(rows, columns=["po_id","supplier","category","order_date","promised_date","received_date",
                                 "qty_ordered","qty_received","qty_rejected","market_rate","quoted_rate","invoiced_rate"])
df.to_csv("data/purchase_orders.csv", index=False)
pd.DataFrame([(k, v[0], v[5], v[7], v[8], v[9]) for k, v in S.items()],
  columns=["supplier","category","set_on_time_prob","set_fill_rate","set_reject_rate","set_price_index"]
  ).to_csv("data/supplier_settings_generator.csv", index=False)
print("rows", len(df))
