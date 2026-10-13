"""Saves results/cement_forecast.png: Cement OPC 53, what sold vs each forecast (Apr to Sep 2026)."""
import pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
d = pd.read_csv("data/monthly_demand.csv", parse_dates=["month"])
f = pd.read_csv("results/test_forecasts.csv")
sku = "Cement OPC 53 (50kg bag)"
h = d[(d.sku == sku) & (d.month >= "2025-10-01")]
x = f[f.sku == sku]
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.plot(h.month.dt.strftime("%Y-%m"), h.units, "k-o", label="Actual")
ax.plot(x.month, x.moving_avg, "r--s", label="3-month moving average")
ax.plot(x.month, x.trend_x_index, "b--^", label="Trend x seasonal index")
ax.set_ylabel("Bags per month"); ax.set_title(f"{sku}: forecast made on 31 Mar 2026 (sample data)")
ax.tick_params(axis="x", rotation=60); ax.legend(); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig("results/cement_forecast.png", dpi=150)
