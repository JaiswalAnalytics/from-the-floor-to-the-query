"""Episode 3: synthetic SKU sales for a building-materials store.
A sample dataset built to look like a small store. Not real records. Seeded: same output every run.
Run: python generate_data.py"""
import numpy as np, pandas as pd
from pathlib import Path

rng = np.random.default_rng(2026)
END = pd.Timestamp("2026-09-30"); START = END - pd.Timedelta(days=179)   # 180 days

# name, category, cost (Rs), markup margin on list price (%), popularity weight, avg qty per sale line
SKUS = [
 ("Cement OPC 53 (50kg bag)","Cement",365,3.0,10,25),("Cement PPC (50kg bag)","Cement",345,4.0,9,25),("White Cement (5kg)","Cement",160,18,1,2),
 ("TMT Bar 8mm (per kg)","Steel",58,5.0,8,200),("TMT Bar 12mm (per kg)","Steel",57,5.0,7,220),("TMT Bar 16mm (per kg)","Steel",57,5.5,5,260),
 ("Binding Wire (per kg)","Steel",70,14,2,5),("MS Angle 40mm (piece)","Steel",640,9,1.5,2),
 ("River Sand (per cft)","Aggregates",38,12,7,150),("Gravel 20mm (per cft)","Aggregates",34,12,6,120),("Red Bricks (per 1000)","Aggregates",7200,8,4,2),
 ("Floor Tile 2x2 (box)","Tiles",520,22,3,6),("Wall Tile 1x1.5 (box)","Tiles",380,24,2.5,6),("Vitrified Tile 4x2 (box)","Tiles",1250,20,1.5,4),
 ("Tile Adhesive (20kg)","Tiles",310,26,3,4),("Tile Grout (1kg)","Tiles",95,35,1.5,3),
 ("Primer (20L)","Paints",2400,16,2,1.5),("Emulsion (20L)","Paints",4100,18,2,1.5),("Distemper (20kg)","Paints",1050,17,1.5,2),
 ("Wall Putty (40kg)","Paints",780,21,3,3),("Enamel Paint (1L)","Paints",420,25,1.5,3),("Paint Brush 4in","Paints",80,40,1,3),
 ("Waterproofing Chemical (5L)","Paints",780,28,1.5,2),
 ("Wash Basin","Sanitary",1400,25,0.8,1),("WC Pan","Sanitary",2600,22,0.6,1),("Bib Cock Tap","Sanitary",260,38,2,3),
 ("Shower Set","Sanitary",900,35,0.6,1),("Water Tank 500L","Sanitary",4200,12,0.4,1),("Health Faucet","Sanitary",380,40,1,2),
 ("PVC Pipe 4in (3m)","Pipes",520,11,2,6),("CPVC Pipe 1in (3m)","Pipes",310,15,2,8),("PVC Elbow 4in","Pipes",55,38,2.5,10),
 ("Solvent Cement (250ml)","Pipes",120,33,2,3),("GI Pipe 1in (6m)","Pipes",1450,10,0.8,3),
 ("Wire 1.5mm (90m coil)","Electrical",1300,13,2.5,3),("Wire 2.5mm (90m coil)","Electrical",2050,13,2,3),("MCB 16A","Electrical",210,30,1.8,4),
 ("Switch 6A","Electrical",38,42,3,10),("LED Bulb 9W","Electrical",85,38,2.5,6),("Conduit Pipe 25mm (3m)","Electrical",48,28,2,15),
 ("Nails 2in (per kg)","Hardware",82,20,2,4),("Door Hinge 4in (pair)","Hardware",140,35,1.5,4),("Padlock 65mm","Hardware",190,40,1,2),
 ("Screws (box of 100)","Hardware",60,45,1.5,4),("Door Handle","Hardware",450,38,0.6,2),("Hammer","Hardware",260,30,0.4,1),("Drill Bit Set","Hardware",420,36,0.5,1),
 ("Wood Adhesive (1kg)","Hardware",210,32,1,3),("Plywood 8x4 18mm","Hardware",3300,14,0.8,4),("Flush Door 7x3","Hardware",2900,15,0.4,1),
]
sku = pd.DataFrame(SKUS, columns=["sku_name","category","cost_price","list_margin_pct","pop","qty_mean"])
sku.insert(0, "sku_id", [f"S{i+1:02d}" for i in range(len(sku))])
sku["list_price"] = (sku.cost_price * (1 + sku.list_margin_pct/100)).round(0)

rows, sid = [], 1
for d in pd.date_range(START, END):
    season = 1.0 + 0.15*np.sin(d.dayofyear/58)
    for _, s in sku.iterrows():
        for _ in range(rng.poisson(s["pop"] * 0.13 * season)):
            q = max(1, int(round(rng.lognormal(np.log(max(s.qty_mean,1)), 0.5))))
            disc = 0.0
            if rng.random() < 0.35:
                disc = rng.uniform(1, 6)                     # contractor / bulk discount (%)
                if q >= s.qty_mean * 1.5: disc += rng.uniform(0, 3)
            price = round(s.list_price * (1 - disc/100), 2)
            rows.append((f"L{sid:06d}", d.date(), s.sku_id, q, price)); sid += 1
sales = pd.DataFrame(rows, columns=["line_id","sale_date","sku_id","qty","unit_price"])

Path("data").mkdir(exist_ok=True)
sku[["sku_id","sku_name","category","cost_price","list_price"]].to_csv("data/skus.csv", index=False)
sales.to_csv("data/sales_lines.csv", index=False)
print(len(sku), "SKUs,", len(sales), "sale lines,", sales.sale_date.min(), "to", sales.sale_date.max())
