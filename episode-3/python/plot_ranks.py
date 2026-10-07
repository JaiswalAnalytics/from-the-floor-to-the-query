"""Saves results/margin_top6.png: margin % of the 6 best sellers vs the store blend."""
import pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
r = pd.read_csv("results/sku_margin.csv").nsmallest(6, "revenue_rank")
blend = 100 * pd.read_csv("results/sku_margin.csv").eval("gross_profit").sum() / pd.read_csv("results/sku_margin.csv").revenue.sum()
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(r.sku_name[::-1], r.margin_pct[::-1], color="#e63222")
ax.axvline(blend, color="#0f1d3a", ls="--", label=f"Store blend {blend:.1f}%")
ax.set_xlabel("Gross margin %"); ax.set_title("Margin on the 6 best sellers (sample data)"); ax.legend()
fig.tight_layout(); fig.savefig("results/margin_top6.png", dpi=150)
