"""Episode 4: forecast the next 6 months of demand, plain moving average vs seasonal method.
Forecast made on 31 Mar 2026 for Apr to Sep 2026, then compared with what actually sold."""
import numpy as np, pandas as pd

d = pd.read_csv("data/monthly_demand.csv", parse_dates=["month"])
cost = pd.read_csv("data/skus.csv").set_index("sku")["cost_price"]
CUT = pd.Timestamp("2026-04-01")                      # train = before, test = from this month

def ma_forecast(y_train, n):                          # 1. plain 3-month moving average, held flat
    return np.repeat(y_train[-3:].mean(), n)

def seasonal_naive(y_train, n):                       # 2. same month last year
    return y_train[-12:][:n]                          #    (train ends Mar, so this starts at last Apr)

def trend_x_index(y_train, months_train, months_test):  # 3. trend line x seasonal index
    t = np.arange(len(y_train))
    b, a = np.polyfit(t, y_train, 1)                  # straight-line trend: a + b*t
    ratio = y_train / (a + b * t)                     # how far each month sat above/below trend
    idx = pd.Series(ratio).groupby(months_train).mean()
    idx = idx / idx.mean()                            # index per calendar month, averages 1.0
    t_f = np.arange(len(y_train), len(y_train) + len(months_test))
    return (a + b * t_f) * idx.reindex(months_test).values

out, rows = [], []
for sku, g in d.groupby("sku"):
    g = g.sort_values("month")
    tr, te = g[g.month < CUT], g[g.month >= CUT]
    y, a = tr.units.values.astype(float), te.units.values.astype(float)
    fc = {"moving_avg": ma_forecast(y, len(te)),
          "seasonal_naive": seasonal_naive(y, len(te)),
          "trend_x_index": trend_x_index(y, tr.month.dt.month.values, te.month.dt.month.values)}
    for name, f in fc.items():
        net = (f - a).sum() * cost[sku]                       # Rs of stock built up (+) or short (-) at cost by September
        rows.append(dict(sku=sku, method=name, wape_pct=100 * np.abs(f - a).sum() / a.sum(),
                         bias_pct=100 * (f - a).sum() / a.sum(), net_stock_rs=net,
                         abs_err_rs=(np.abs(f - a) * cost[sku]).sum(), actual_rs=(a * cost[sku]).sum()))
    out.append(pd.DataFrame({"month": te.month.dt.strftime("%Y-%m").values, "sku": sku, "actual": a,
                             **{k: np.round(v, 1) for k, v in fc.items()}}))

res = pd.DataFrame(rows)
pd.concat(out).to_csv("results/test_forecasts.csv", index=False)
res.round(2).to_csv("results/forecast_results.csv", index=False)

pd.set_option("display.width", 200)
piv = res.pivot(index="sku", columns="method", values="wape_pct").round(1)
print("WAPE % by SKU (lower is better)\n", piv[["moving_avg", "seasonal_naive", "trend_x_index"]])
tot = res.groupby("method")[["abs_err_rs", "actual_rs", "net_stock_rs"]].sum()
tot["value_wape_pct"] = 100 * tot.abs_err_rs / tot.actual_rs
print("\nAll 6 SKUs, value-weighted\n", tot.round(1))
