"""Episode 2: Procurement lag detection.
Finds suppliers whose delivery time is drifting longer, using a linear trend per supplier,
and sizes the extra stock buffer that drift forces you to hold.
Run from the episode-2 folder:  python python/procurement_lag.py"""
import pandas as pd
from scipy import stats

po = pd.read_csv("data/purchase_orders.csv", parse_dates=["order_date", "received_date"])

# 1. Lead time per order, and whether it beat the supplier's promise
po["lead_days"] = (po["received_date"] - po["order_date"]).dt.days
po["late"] = po["lead_days"] > po["promised_days"]
start, end = po["order_date"].min(), po["order_date"].max()
po["t"] = (po["order_date"] - start).dt.days          # days since the first order

rows = []
for (sid, name), g in po.groupby(["supplier_id", "supplier_name"]):
    fit = stats.linregress(g["t"], g["lead_days"])      # lead_days = intercept + slope * t
    first = g[g["order_date"] < start + pd.Timedelta(days=90)]["lead_days"].mean()
    last_g = g[g["order_date"] > end - pd.Timedelta(days=90)]
    last = last_g["lead_days"].mean()
    daily_value = g["po_value"].sum() / ((end - start).days + 1)    # Rs bought per day
    rows.append({
        "supplier": name, "orders": len(g),
        "first_90d_avg": round(first, 1), "last_90d_avg": round(last, 1),
        "slope_per_90d": round(fit.slope * 90, 2),
        "p_value": fit.pvalue, "r_squared": round(fit.rvalue ** 2, 2),
        "late_pct_last_90d": round(100 * last_g["late"].mean()),
        "extra_buffer_rs": round((last - first) * daily_value),
    })

res = pd.DataFrame(rows)
# 2. Flag only drifts that are both real (p < 0.01) and big enough to matter (0.5+ days per quarter)
res["drifting"] = (res["p_value"] < 0.01) & (res["slope_per_90d"] >= 0.5)
res["p_value"] = res["p_value"].map(lambda p: "<0.001" if p < 0.001 else f"{p:.3f}")
res = res.sort_values("slope_per_90d", ascending=False).reset_index(drop=True)
print(res.to_string(index=False))

d = res[res["drifting"]]
print(f"\n{len(d)} of {len(res)} suppliers are drifting.")
print(f"Extra stock buffer they force you to hold: Rs {d['extra_buffer_rs'].sum():,.0f}")
res.to_csv("python/lag_summary.csv", index=False)
