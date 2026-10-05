"""Synthetic purchase orders for a building-materials store (not real data).
8 suppliers, 12 months of orders (1 Oct 2025 to 30 Sep 2026). Seeded, so results repeat."""
import csv, random, datetime as dt
random.seed(11)
START = dt.date(2025, 10, 1)
DAYS = 365
END = dt.date(2026, 9, 30)
# supplier, category, promised days, base lead days, total drift over the year (days), noise sd, orders, avg PO value (Rs)
S = [
 ('SUP01','Sharma Cement Traders','Cement',            3, 3.0,  0.0, 0.7, 70, 120000),
 ('SUP02','Rao Steel Wholesale','Steel',               5, 5.0,  3.2, 0.8, 62, 250000),
 ('SUP03','Gupta Tile House','Tiles',                  7, 7.0,  3.6, 0.9, 58, 110000),
 ('SUP04','Verma Paint Dealers','Paint',               4, 4.0,  2.6, 0.7, 66, 90000),
 ('SUP05','Singh Pipes & Fittings','Plumbing',         4, 4.0,  0.0, 0.7, 64, 60000),
 ('SUP06','Mishra Electricals','Electrical',           5, 5.0,  1.0, 0.8, 60, 50000),
 ('SUP07','Khan Sanitaryware','Sanitary',              8, 8.0,  0.0, 2.3, 52, 80000),
 ('SUP08','Yadav Hardware Mart','Hardware',            3, 3.0,  0.0, 0.6, 72, 30000),
]
rows, n = [], 0
for sid, name, cat, promised, base, drift, sd, orders, val in S:
    days = sorted(random.sample(range(DAYS), orders))
    for d in days:
        lead = base + drift * d / DAYS + random.gauss(0, sd)
        lead = max(1, round(lead))
        od = START + dt.timedelta(days=d)
        if od + dt.timedelta(days=lead) > END: continue   # keep only orders already received
        n += 1
        po_value = round(val * random.uniform(0.6, 1.4) / 100) * 100
        rows.append((f'PO{n:04d}', sid, name, cat, od.isoformat(), promised, (od + dt.timedelta(days=lead)).isoformat(), po_value))
rows.sort(key=lambda r: r[4])
with open('data/purchase_orders.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['po_id','supplier_id','supplier_name','category','order_date','promised_days','received_date','po_value'])
    w.writerows(rows)
print(len(rows), 'purchase orders')
