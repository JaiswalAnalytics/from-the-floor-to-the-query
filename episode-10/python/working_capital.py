"""Episode 10: cash conversion cycle (DIO + DSO - DPO) and the cash it ties up.
Run from the episode-10 folder. Window: 1 Oct 2025 to 30 Sep 2026 (12 month-ends)."""
import numpy as np, pandas as pd
pd.set_option("display.width", 220, "display.max_columns", 30)

COST_OF_MONEY = 0.18     # ASSUMPTION: 18% a year, same as Episode 6
DAYS = 365
SLOW = ["Emulsion Paint", "Wall Putty", "Floor Tile 2x2"]
STOCK_CUT, FASTER_DAYS, LONGER_DAYS = 0.30, 10, 5     # the three what-if levers (assumptions)

s = pd.read_csv("data/sales.csv", parse_dates=["sale_date", "paid_date"])
b = pd.read_csv("data/purchases.csv", parse_dates=["bill_date", "paid_date"])
k = pd.read_csv("data/inventory_month_end.csv", parse_dates=["month_end"])
mes = pd.date_range("2025-10-31", "2026-09-30", freq="ME")
win = s[(s.sale_date >= "2025-10-01") & (s.sale_date <= "2026-09-30")]

rows = []
for me in mes:
    mo = win[win.sale_date.dt.to_period("M") == me.to_period("M")]
    rows.append(dict(month_end=me.date(), revenue=mo.revenue.sum(), cogs=mo.cogs.sum(),
        inventory=k[k.month_end == me].closing_stock.sum(),
        receivables=s[(s.sale_date <= me) & (s.paid_date > me)].revenue.sum(),
        payables=b[(b.bill_date <= me) & (b.paid_date > me)].amount.sum()))
m = pd.DataFrame(rows)
m.to_csv("results/monthly_balances.csv", index=False)

rev, cogs = m.revenue.sum(), m.cogs.sum()
inv, ar, ap = m.inventory.mean(), m.receivables.mean(), m.payables.mean()
dio, dso, dpo = inv / cogs * DAYS, ar / rev * DAYS, ap / cogs * DAYS
wc = inv + ar - ap
gp = rev - cogs
summ = dict(revenue=rev, cogs=cogs, gross_profit=gp, avg_inventory=inv, avg_receivables=ar, avg_payables=ap,
            dio=dio, dso=dso, dpo=dpo, ccc=dio + dso - dpo, working_capital=wc,
            carrying_cost=wc * COST_OF_MONEY, carrying_pct_of_gp=100 * wc * COST_OF_MONEY / gp)

# by category (stock and supplier side) and by customer type (credit side)
cat = []
for c, g in win.groupby("category"):
    ic = k[(k.category == c) & k.month_end.isin(mes)].closing_stock.mean()
    pc = np.mean([b[(b.category == c) & (b.bill_date <= me) & (b.paid_date > me)].amount.sum() for me in mes])
    cat.append(dict(category=c, cogs=g.cogs.sum(), avg_inventory=ic, dio=ic / g.cogs.sum() * DAYS,
                    avg_payables=pc, dpo=pc / g.cogs.sum() * DAYS, slow=int(c in SLOW)))
cat = pd.DataFrame(cat)
typ = []
for t, g in win.groupby("customer_type"):
    a = np.mean([s[(s.customer_type == t) & (s.sale_date <= me) & (s.paid_date > me)].revenue.sum() for me in mes])
    typ.append(dict(customer_type=t, revenue=g.revenue.sum(), avg_receivables=a, dso=a / g.revenue.sum() * DAYS))
typ = pd.DataFrame(typ)
cat.to_csv("results/by_category.csv", index=False); typ.to_csv("results/by_customer_type.csv", index=False)

# what-if levers
l1 = STOCK_CUT * cat[cat.slow == 1].avg_inventory.sum()
l2 = typ[typ.customer_type == "Contractor"].revenue.iloc[0] / DAYS * FASTER_DAYS
l3 = cogs / DAYS * LONGER_DAYS
rel = l1 + l2 + l3
lev = pd.DataFrame([("Cut stock days 30% on paint, putty, tile", l1), ("Contractors pay 10 days faster", l2),
                    ("Suppliers give 5 more days", l3), ("Total cash released", rel)], columns=["lever", "cash_released"])
lev["yearly_saving_at_18pct"] = lev.cash_released * COST_OF_MONEY
lev.to_csv("results/levers.csv", index=False)
summ.update(lever1=l1, lever2=l2, lever3=l3, released=rel, saving=rel * COST_OF_MONEY,
            wc_after=wc - rel, ccc_after=(inv - l1) / cogs * DAYS + (ar - l2) / rev * DAYS - (ap + l3) / cogs * DAYS)
pd.DataFrame([summ]).T.rename(columns={0: "value"}).to_csv("results/summary.csv")

print(m.round(0).to_string(index=False)); print()
print(cat.round(1).to_string(index=False)); print()
print(typ.round(1).to_string(index=False)); print()
print(lev.round(0).to_string(index=False)); print()
for kx, v in summ.items(): print(f"{kx:20s} {v:,.2f}")
