"""Episode 8: price elasticity per SKU. Baseline (price vs units only) next to a model
that also controls for calendar month and a time trend. Run from the episode-8 folder."""
import numpy as np, pandas as pd, statsmodels.formula.api as smf

d = pd.read_csv("data/weekly_sales.csv")
cost = pd.read_csv("data/skus.csv").set_index("sku").cost_price
true = pd.read_csv("data/true_elasticity_generator.csv").set_index("sku").true_elasticity
d["lq"], d["lp"] = np.log(d.units), np.log(d.price)

rows = []
for sku, g in d.groupby("sku", sort=False):
    naive = smf.ols("lq ~ lp", g).fit(cov_type="HC1")
    model = smf.ols("lq ~ lp + C(month) + week", g).fit(cov_type="HC1")
    lo, hi = model.conf_int().loc["lp"]
    units, rev = g.units.sum(), (g.units * g.price).sum()
    avg_price = rev / units
    margin = (avg_price - cost[sku]) / avg_price
    rows.append(dict(sku=sku, price_changes=int((g.price.diff().fillna(0) != 0).sum()),
        price_min=g.price.min(), price_max=g.price.max(),
        naive_e=naive.params["lp"], model_e=model.params["lp"], model_se=model.bse["lp"],
        ci_low=lo, ci_high=hi, true_e=true[sku],
        true_in_ci=bool(lo <= true[sku] <= hi),
        units=units, revenue=rev, avg_price=avg_price, cost=cost[sku], margin=margin,
        gross_profit=rev - units * cost[sku]))
r = pd.DataFrame(rows)

# What-if: cut every price by 3 percent, units move by (0.97 ** elasticity)
CUT = 0.03
def gp_change(e):
    q = r.units * (1 - CUT) ** e
    new = q * (r.avg_price * (1 - CUT) - r.cost)
    return new - r.gross_profit
r["breakeven_uplift_pct"] = 100 * CUT / (r.margin - CUT)          # extra units needed to break even
r["model_uplift_pct"] = 100 * ((1 - CUT) ** r.model_e - 1)         # extra units the model expects
r["gp_change_model"] = gp_change(r.model_e)
r["gp_change_naive"] = gp_change(r.naive_e)
r["gp_change_true"] = gp_change(r.true_e)

r.round(4).to_csv("results/elasticity_by_sku.csv", index=False)
pd.set_option("display.width", 220, "display.max_columns", 30)
print(r[["sku","price_changes","naive_e","model_e","model_se","ci_low","ci_high","true_e","true_in_ci"]].round(2).to_string(index=False))
print()
print(r[["sku","margin","breakeven_uplift_pct","model_uplift_pct","gp_change_model","gp_change_naive","gp_change_true"]].round(2).to_string(index=False))
print()
print("Annual gross profit:", round(r.gross_profit.sum()), "| revenue:", round(r.revenue.sum()))
print("3% cut, gross profit change (model):", round(r.gp_change_model.sum()), "| naive:", round(r.gp_change_naive.sum()), "| true:", round(r.gp_change_true.sum()))
