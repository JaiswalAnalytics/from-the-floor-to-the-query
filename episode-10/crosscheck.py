"""Independent check of python/working_capital.py: the same numbers rebuilt in DuckDB SQL."""
import duckdb, pandas as pd
con = duckdb.connect()
con.execute("""
CREATE VIEW me AS SELECT (date_trunc('month', d) + INTERVAL 1 MONTH - INTERVAL 1 DAY)::DATE AS me
  FROM generate_series(DATE '2025-10-01', DATE '2026-09-01', INTERVAL 1 MONTH) t(d);
CREATE VIEW s AS SELECT * FROM 'data/sales.csv';
CREATE VIEW b AS SELECT * FROM 'data/purchases.csv';
CREATE VIEW k AS SELECT * FROM 'data/inventory_month_end.csv';
""")
q = con.execute("""
WITH w AS (SELECT * FROM s WHERE sale_date BETWEEN DATE '2025-10-01' AND DATE '2026-09-30'),
tot AS (SELECT sum(revenue) rev, sum(cogs) cogs FROM w),
inv AS (SELECT avg(t) a FROM (SELECT sum(closing_stock) t FROM k WHERE month_end IN (SELECT me FROM me) GROUP BY month_end)),
slow AS (SELECT avg(t) a FROM (SELECT sum(closing_stock) t FROM k WHERE month_end IN (SELECT me FROM me)
         AND category IN ('Emulsion Paint','Wall Putty','Floor Tile 2x2') GROUP BY month_end)),
ar AS (SELECT avg(t) a FROM (SELECT me.me, coalesce(sum(s.revenue),0) t FROM me LEFT JOIN s ON s.sale_date<=me.me AND s.paid_date>me.me GROUP BY me.me)),
arc AS (SELECT avg(t) a FROM (SELECT me.me, coalesce(sum(s.revenue),0) t FROM me LEFT JOIN s ON s.customer_type='Contractor' AND s.sale_date<=me.me AND s.paid_date>me.me GROUP BY me.me)),
ap AS (SELECT avg(t) a FROM (SELECT me.me, coalesce(sum(b.amount),0) t FROM me LEFT JOIN b ON b.bill_date<=me.me AND b.paid_date>me.me GROUP BY me.me)),
crev AS (SELECT sum(revenue) r FROM w WHERE customer_type='Contractor')
SELECT tot.rev, tot.cogs, inv.a inv, ar.a ar, ap.a ap, slow.a slow, crev.r crev,
       inv.a/tot.cogs*365 dio, ar.a/tot.rev*365 dso, ap.a/tot.cogs*365 dpo,
       inv.a + ar.a - ap.a wc,
       0.30*slow.a l1, crev.r/365*10 l2, tot.cogs/365*5 l3
FROM tot, inv, ar, ap, slow, crev
""").df().iloc[0]
q["ccc"] = q.dio + q.dso - q.dpo
q["carrying_cost"] = q.wc * 0.18
q["released"] = q.l1 + q.l2 + q.l3
q["ccc_after"] = (q.inv - q.l1)/q.cogs*365 + (q.ar - q.l2)/q.rev*365 - (q.ap + q.l3)/q.cogs*365

p = pd.read_csv("results/summary.csv", index_col=0).value
pairs = {"revenue":"rev","cogs":"cogs","avg_inventory":"inv","avg_receivables":"ar","avg_payables":"ap","dio":"dio","dso":"dso",
         "dpo":"dpo","ccc":"ccc","working_capital":"wc","carrying_cost":"carrying_cost","lever1":"l1","lever2":"l2","lever3":"l3",
         "released":"released","ccc_after":"ccc_after"}
worst = 0
for pk, sk in pairs.items():
    d = abs(p[pk] - q[sk]); worst = max(worst, d); print(f"{pk:18s} python {p[pk]:>16,.4f}  sql {q[sk]:>16,.4f}  diff {d:.8f}")
print("ALL MATCH (max diff %.8f)" % worst if worst < 0.01 else "MISMATCH, max diff %.4f" % worst)
