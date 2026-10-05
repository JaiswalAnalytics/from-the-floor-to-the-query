"""Draws lead time over time for every supplier, with the fitted trend line. Saves lag_trends.png"""
import pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
po = pd.read_csv("data/purchase_orders.csv", parse_dates=["order_date", "received_date"])
po["lead"] = (po.received_date - po.order_date).dt.days
po["t"] = (po.order_date - po.order_date.min()).dt.days
fig, axes = plt.subplots(2, 4, figsize=(14, 6.2), sharex=True)
for ax, (name, g) in zip(axes.flat, po.groupby("supplier_name")):
    r = stats.linregress(g.t, g.lead)
    drift = r.pvalue < .01 and r.slope * 90 >= .5
    c = "#ee4266" if drift else "#14213d"
    ax.scatter(g.order_date, g.lead, s=9, color=c, alpha=.55)
    ax.plot(g.order_date, r.intercept + r.slope * g.t, color=c, lw=2.2)
    ax.set_title(f"{name}\n{r.slope*90:+.2f} days per quarter", fontsize=9.5, color=c, fontweight="bold")
    ax.tick_params(labelsize=7.5); ax.grid(alpha=.2)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.suptitle("Delivery time per purchase order, Oct 2025 to Sep 2026 (red = drifting slower)", fontsize=12, fontweight="bold")
fig.autofmt_xdate(rotation=30); fig.tight_layout()
fig.savefig("lag_trends.png", dpi=130)
