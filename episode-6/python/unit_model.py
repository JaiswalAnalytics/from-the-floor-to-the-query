"""Episode 6 - unit economics of one store (pandas).
Gross profit -> minus delivery, credit cost, bad debt -> contribution -> minus fixed cost -> operating profit."""
import os
import pandas as pd
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

CAPITAL_RATE = 0.18   # ASSUMPTION: yearly cost of money tied up in credit sales

o = pd.read_csv("data/orders.csv", parse_dates=["order_date"])
fx = pd.read_csv("data/fixed_costs.csv")

o["gross_profit"] = o["order_value"] - o["cogs"]
o["credit_cost"] = o["order_value"] * CAPITAL_RATE * o["credit_days"] / 365
o["bad_debt_loss"] = o["order_value"] * o["bad_debt"]
o["contribution"] = o["gross_profit"] - o["delivery_cost"] - o["credit_cost"] - o["bad_debt_loss"]

# 1) by customer type
g = o.groupby("customer_type").agg(
    orders=("order_id", "count"), customers=("customer_id", "nunique"),
    revenue=("order_value", "sum"), gross_profit=("gross_profit", "sum"),
    delivery=("delivery_cost", "sum"), credit_cost=("credit_cost", "sum"),
    bad_debt=("bad_debt_loss", "sum"), contribution=("contribution", "sum"))
g["gross_margin_pct"] = 100 * g["gross_profit"] / g["revenue"]
g["contribution_margin_pct"] = 100 * g["contribution"] / g["revenue"]
g["contribution_per_order"] = g["contribution"] / g["orders"]
g["contribution_per_customer"] = g["contribution"] / g["customers"]
g = g.sort_values("revenue", ascending=False)

# 2) store P&L
t = g[["revenue", "gross_profit", "delivery", "credit_cost", "bad_debt", "contribution", "orders", "customers"]].sum()
fixed = fx[["rent", "salaries", "electricity", "other"]].sum().sum()
op = t["contribution"] - fixed
cm = t["contribution"] / t["revenue"]
breakeven_rev = fixed / cm
pl = pd.Series({
    "revenue": t["revenue"], "gross_profit": t["gross_profit"], "delivery": t["delivery"],
    "credit_cost": t["credit_cost"], "bad_debt": t["bad_debt"], "contribution": t["contribution"],
    "fixed_costs": fixed, "operating_profit": op,
    "gross_margin_pct": 100 * t["gross_profit"] / t["revenue"], "contribution_margin_pct": 100 * cm,
    "breakeven_revenue_year": breakeven_rev, "breakeven_revenue_month": breakeven_rev / 12,
    "avg_revenue_month": t["revenue"] / 12})

# 3) monthly view
o["month"] = o["order_date"].dt.strftime("%Y-%m")
mo = o.groupby("month").agg(revenue=("order_value", "sum"), contribution=("contribution", "sum"))
mo["fixed"] = fx.set_index("month")[["rent", "salaries", "electricity", "other"]].sum(axis=1)
mo["operating_profit"] = mo["contribution"] - mo["fixed"]

g.round(2).to_csv("results/by_customer_type.csv")
pl.round(2).to_csv("results/store_pl.csv", header=["value"])
mo.round(2).to_csv("results/monthly.csv")
pd.set_option("display.width", 200)
print(g.round(1).T.to_string()); print(); print(pl.round(1).to_string()); print(); print(mo.round(0).to_string())
print("months in loss:", int((mo.operating_profit < 0).sum()))
