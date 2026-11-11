"""Episode 8 dataset: weekly price and units for 6 SKUs of a building-materials store.
Synthetic, seeded. The TRUE price elasticity of each SKU, the seasonal shape and the
habit of raising prices in busy weeks are SET here. The analysis has to find them."""
import numpy as np, pandas as pd

rng = np.random.default_rng(2026 + 8)
WEEKS = 52
starts = pd.date_range("2025-10-01", periods=WEEKS, freq="7D")
month = starts.month.values

# sku: (cost, markup_at_start, base_weekly_units, true_elasticity, season by month Oct..Sep)
SKUS = {
 "Cement OPC 53":  (365.0, 0.030, 380, -0.60, [1.15,1.20,1.10,1.00,0.95,1.10,1.15,1.00,0.80,0.70,0.65,0.85]),
 "TMT Bar 12mm":   (62.0,  0.050, 300, -0.90, [1.10,1.15,1.10,1.00,1.00,1.10,1.15,1.05,0.85,0.75,0.70,0.80]),
 "River Sand":     (48.0,  0.100, 260, -0.40, [1.05,1.10,1.15,1.15,1.10,1.15,1.20,1.05,0.70,0.55,0.50,0.75]),
 "Emulsion Paint": (2150.0,0.160, 40,  -1.80, [1.30,1.35,1.00,0.85,0.80,0.90,1.00,1.05,0.90,0.85,0.90,1.00]),
 "Wall Putty":     (780.0, 0.180, 60,  -1.40, [1.10,1.15,1.05,0.95,0.95,1.05,1.10,1.05,0.90,0.85,0.85,0.95]),
 "Floor Tile 2x2": (310.0, 0.140, 90,  -2.10, [1.00,1.10,1.15,1.10,1.00,1.05,1.20,1.15,0.90,0.80,0.75,0.85]),
}
# calendar month -> position in the Oct..Sep list
pos = {10:0,11:1,12:2,1:3,2:4,3:5,4:6,5:7,6:8,7:9,8:10,9:11}

rows, skus = [], []
for sku,(cost,mk,base,e,season) in SKUS.items():
    p0 = round(cost*(1+mk))
    skus.append((sku,cost))
    s = np.array([season[pos[m]] for m in month])
    # price: held for a few weeks, then moved. Raised in busy weeks, cut in slow weeks.
    price = np.empty(WEEKS); cur = p0; t = 0
    while t < WEEKS:
        hold = int(rng.integers(1,4))
        price[t:t+hold] = cur
        t += hold
        busy = s[min(t,WEEKS-1)] - 1.0              # + busy, - slow
        step = rng.choice([0.03,0.04,0.05,0.06,0.08]) 
        up = rng.random() < 0.5 + 1.0*busy          # busy weeks push the shop to raise
        if cur > p0*1.10: up = False                 # shop never strays far from its usual price
        if cur < p0*0.96: up = True
        cur = max(float(np.ceil(cost*1.005)), float(round(cur*(1+step if up else 1-step))))   # whole rupees, never at or below cost
    price = price[:WEEKS]
    growth = 1 + 0.002*np.arange(WEEKS)
    mean = base*s*growth*(price/p0)**e
    units = np.maximum(1, np.round(mean*rng.lognormal(0,0.04,WEEKS))).astype(int)
    for i in range(WEEKS):
        rows.append((starts[i].date(), i+1, int(month[i]), sku, int(price[i]), int(units[i])))

pd.DataFrame(rows, columns=["week_start","week","month","sku","price","units"]).to_csv("data/weekly_sales.csv", index=False)
pd.DataFrame(skus, columns=["sku","cost_price"]).to_csv("data/skus.csv", index=False)
pd.DataFrame([(k,v[3]) for k,v in SKUS.items()], columns=["sku","true_elasticity"]).to_csv("data/true_elasticity_generator.csv", index=False)
print("rows", len(rows))
