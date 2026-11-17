"""Independent check of sql/scorecard.sql: same scorecard rebuilt in plain pandas/numpy."""
import numpy as np, pandas as pd
d = pd.read_csv("data/purchase_orders.csv", parse_dates=["promised_date", "received_date"])
rows = []
for sup, g in d.groupby("supplier"):
    late = g[g.received_date > g.promised_date]
    paid = (g.invoiced_rate * g.qty_received).sum()
    r = dict(supplier=sup, pos=len(g),
             on_time_pct=100 * (g.received_date <= g.promised_date).mean(),
             avg_days_late=(late.received_date - late.promised_date).dt.days.mean(),
             fill_pct=100 * g.qty_received.sum() / g.qty_ordered.sum(),
             reject_pct=100 * g.qty_rejected.sum() / g.qty_received.sum(),
             price_idx=paid / (g.market_rate * g.qty_received).sum(),
             usable_price_idx=paid / (g.market_rate * (g.qty_received - g.qty_rejected)).sum(),
             paid_value=paid)
    rows.append(r)
p = pd.DataFrame(rows)
p["quality_pts"] = (100 - 10 * p.reject_pct).clip(lower=0)
p["price_pts"] = (100 - 1000 * (p.price_idx - 0.95)).clip(0, 100)
p["score"] = 0.35*p.on_time_pct + 0.25*p.fill_pct + 0.25*p.quality_pts + 0.15*p.price_pts
p["score_price_first"] = 0.15*p.on_time_pct + 0.10*p.fill_pct + 0.25*p.quality_pts + 0.50*p.price_pts
p["price_rank"] = p.price_idx.rank(method="min").astype(int)
p["score_rank"] = p.score.rank(ascending=False, method="min").astype(int)
p["price_first_rank"] = p.score_price_first.rank(ascending=False, method="min").astype(int)

s = pd.read_csv("results/scorecard.csv").set_index("supplier")
p = p.set_index("supplier").loc[s.index]
print("exact scores:", p.score.round(6).to_dict())
bad = 0
DEC = dict(pos=0, on_time_pct=1, avg_days_late=1, fill_pct=1, reject_pct=1, price_idx=3, usable_price_idx=3,
           paid_value=0, score=1, score_price_first=1)
# The SQL output is rounded. Compare the unrounded pandas value with it inside half a rounding step
# (SQL rounds 1.25 to 1.3, Python's round() gives 1.2, so exact ties are the only gap possible).
for c, dec in DEC.items():
    diff = (p[c] - s[c]).abs().max(); tol = 0.5 * 10 ** (-dec) + 1e-9
    print(f"{c:20s} max diff {diff:.6f} (allowed {tol:.4f})"); bad += diff > tol
for c in ["price_rank","score_rank","price_first_rank"]:
    n = int((p[c] != s[c]).sum()); print(f"{c:20s} mismatches {n}"); bad += n
print("ALL MATCH" if not bad else f"MISMATCHES: {bad}")
