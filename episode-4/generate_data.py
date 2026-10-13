"""Episode 4: synthetic monthly demand for a building-materials store.
A sample dataset built to look like a small store. Not real records. Seeded: same output every run.
36 months, Oct 2023 to Sep 2026, 6 SKUs, each with its own seasonal shape.
Run: python generate_data.py"""
import numpy as np, pandas as pd
from pathlib import Path

rng = np.random.default_rng(2026)
MONTHS = pd.date_range("2023-10-01", "2026-09-01", freq="MS")

# seasonal shape Jan..Dec (rescaled below so each averages 1.0)
SHAPES = {
 "Cement OPC 53 (50kg bag)":  [1.10,1.15,1.20,1.15,1.05,0.90,0.70,0.70,0.80,1.00,1.05,1.10],
 "TMT Bar 12mm (per kg)":     [1.05,1.10,1.15,1.10,1.05,0.95,0.80,0.80,0.90,1.00,1.05,1.05],
 "River Sand (per cft)":      [1.10,1.15,1.20,1.15,1.00,0.75,0.55,0.55,0.70,1.05,1.15,1.15],
 "Emulsion Paint (20L)":      [0.95,1.00,1.15,1.00,0.90,0.85,0.75,0.80,0.95,1.45,1.35,0.85],
 "Wall Putty (40kg)":         [0.95,1.00,1.15,1.00,0.90,0.85,0.75,0.80,0.95,1.40,1.30,0.90],
 "Floor Tile 2x2 (box)":      [1.00,1.20,1.25,1.15,0.95,0.80,0.70,0.75,0.90,1.10,1.10,1.10],
}
# base monthly units, yearly growth, cost price (Rs)
BASE = {
 "Cement OPC 53 (50kg bag)": (1200, 0.06, 365), "TMT Bar 12mm (per kg)": (6000, 0.05, 57),
 "River Sand (per cft)": (5000, 0.04, 38), "Emulsion Paint (20L)": (40, 0.07, 4100),
 "Wall Putty (40kg)": (90, 0.06, 780), "Floor Tile 2x2 (box)": (150, 0.05, 520),
}
rows = []
for sku, shape in SHAPES.items():
    shape = np.array(shape) / np.mean(shape)
    base, g, _ = BASE[sku]
    for t, m in enumerate(MONTHS):
        mu = base * (1 + g) ** (t / 12) * shape[m.month - 1]
        rows.append((m.date(), sku, int(round(mu * rng.lognormal(0, 0.07)))))
d = pd.DataFrame(rows, columns=["month", "sku", "units"])
Path("data").mkdir(exist_ok=True)
d.to_csv("data/monthly_demand.csv", index=False)
pd.DataFrame([(k, v[2]) for k, v in BASE.items()], columns=["sku", "cost_price"]).to_csv("data/skus.csv", index=False)
print(len(d), "rows,", d.sku.nunique(), "SKUs,", d.month.min(), "to", d.month.max())
