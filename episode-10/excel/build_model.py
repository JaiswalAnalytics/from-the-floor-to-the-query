"""Builds excel/working_capital_model.xlsx with live formulas.
Values typed in (blue) come from the Python results in results/. Everything else is a formula.
Run from the episode-10 folder, then recalculate (see README)."""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment

F = "Arial"
blue, black, green = Font(name=F, color="0000FF", size=10), Font(name=F, size=10), Font(name=F, color="008000", size=10)
bold, title = Font(name=F, bold=True, size=10), Font(name=F, bold=True, size=14)
head = Font(name=F, bold=True, color="FFFFFF", size=10); headfill = PatternFill("solid", fgColor="14213D")
yellow = PatternFill("solid", fgColor="FFFF00"); grey = PatternFill("solid", fgColor="EEEEEE")
RS, DAYS, PCT, DT = '#,##0;(#,##0);-', '0.0', '0.0%', 'dd-mmm-yyyy'

m = pd.read_csv("results/monthly_balances.csv", parse_dates=["month_end"])
cat = pd.read_csv("results/by_category.csv"); typ = pd.read_csv("results/by_customer_type.csv")
summ = pd.read_csv("results/summary.csv", index_col=0).value

wb = Workbook()
def hdr(ws, row, labels):
    for i, t in enumerate(labels, 1):
        c = ws.cell(row, i, t); c.font, c.fill = head, headfill; c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[row].height = 32
def put(ws, ref, v, font=black, fmt=None, fill=None):
    c = ws[ref]; c.value = v; c.font = font
    if fmt: c.number_format = fmt
    if fill: c.fill = fill
    return c

# ---------------- Notes
ws = wb.active; ws.title = "Notes"
put(ws, "A1", "Episode 10 of 10: Working capital cycle (From the Floor to the Query)", title)
notes = [
 "Synthetic data built to look like a building-materials store. All amounts in rupees (Rs).",
 "Window: 1 Oct 2025 to 30 Sep 2026 (12 month-ends). Balances are month-end figures; averages are the mean of the 12 month-ends.",
 "Cash conversion cycle = DIO (days in stock) + DSO (days customers take to pay) - DPO (days the store takes to pay suppliers).",
 "DIO = average inventory / COGS x days. DSO = average receivables / revenue x days. DPO = average payables / COGS x days.",
 "",
 "COLOUR LEGEND:  blue = typed-in input (edit these)   black = formula   green = link to another sheet   yellow fill = key assumption",
 "Edit only the blue cells. The yellow cells on the Inputs sheet drive the cost of money and the three what-if levers.",
 "Blue values on Monthly, Categories and Customers come from the Python results (results/*.csv), which were cross-checked against SQL.",
 "",
 "ASSUMPTIONS (mine, not facts about any store): cost of money 18% a year (same as Episode 6); the three lever sizes; stock days, credit terms and",
 "supplier terms were SET in the data generator. Rejected, damaged or returned goods are not modelled.",
 "Levers (default sizes; the live values are the yellow cells on Inputs): (1) cut stock days 30% on the slow categories (paint, putty, tile), (2) contractors pay 10 days faster, (3) suppliers give 5 more days.",
 "Sheets: Inputs, Monthly, Categories, Customers, Summary (the answer), Checks (Excel against Python).",
]
for i, t in enumerate(notes, 3): put(ws, f"A{i}", t)
ws.column_dimensions["A"].width = 150

# ---------------- Inputs
wi = wb.create_sheet("Inputs")
put(wi, "A1", "Inputs and assumptions", title)
rows = [(4, "Cost of money (a year)", 0.18, PCT, "ASSUMPTION: 18% a year, same as Episode 6"),
        (5, "Days in the year", 365, '0', "Window 1 Oct 2025 to 30 Sep 2026 is 365 days"),
        (6, "Lever 1: cut in stock days on slow categories", 0.30, PCT, "ASSUMPTION: my what-if, not a forecast"),
        (7, "Lever 2: contractors pay this many days faster", 10, '0', "ASSUMPTION: my what-if, not a forecast"),
        (8, "Lever 3: suppliers give this many more days", 5, '0', "ASSUMPTION: my what-if, not a forecast")]
hdr(wi, 3, ["Input", "Value", "Note"])
for r, lab, v, f, n in rows:
    put(wi, f"A{r}", lab); put(wi, f"B{r}", v, blue, f, yellow); put(wi, f"C{r}", n)
wi.column_dimensions["A"].width = 48; wi.column_dimensions["B"].width = 12; wi.column_dimensions["C"].width = 50

# ---------------- Monthly
wm = wb.create_sheet("Monthly")
put(wm, "A1", "Month-end balances and days (Rs)", title)
hdr(wm, 4, ["Month end", "Days in month", "Revenue", "COGS", "Gross profit", "Inventory", "Receivables", "Payables", "DIO", "DSO", "DPO", "Cycle (days)"])
for i, r in m.iterrows():
    x = 5 + i
    put(wm, f"A{x}", r.month_end.to_pydatetime(), blue, DT); put(wm, f"B{x}", f"=DAY(A{x})", black, '0')
    put(wm, f"C{x}", int(r.revenue), blue, RS); put(wm, f"D{x}", int(r.cogs), blue, RS); put(wm, f"E{x}", f"=C{x}-D{x}", black, RS)
    put(wm, f"F{x}", int(r.inventory), blue, RS); put(wm, f"G{x}", int(r.receivables), blue, RS); put(wm, f"H{x}", int(r.payables), blue, RS)
    put(wm, f"I{x}", f"=F{x}/D{x}*B{x}", black, DAYS); put(wm, f"J{x}", f"=G{x}/C{x}*B{x}", black, DAYS)
    put(wm, f"K{x}", f"=H{x}/D{x}*B{x}", black, DAYS); put(wm, f"L{x}", f"=I{x}+J{x}-K{x}", black, DAYS)
put(wm, "A17", "Year", bold)
for col in "CDE": put(wm, f"{col}17", f"=SUM({col}5:{col}16)", bold, RS)
for col in "FGH": put(wm, f"{col}17", f"=AVERAGE({col}5:{col}16)", bold, RS)
put(wm, "I17", "=F17/D17*Inputs!$B$5", bold, DAYS); put(wm, "J17", "=G17/C17*Inputs!$B$5", bold, DAYS)
put(wm, "K17", "=H17/D17*Inputs!$B$5", bold, DAYS); put(wm, "L17", "=I17+J17-K17", bold, DAYS)
put(wm, "A19", "Row 17: revenue, COGS and profit are totals; inventory, receivables and payables are averages of the 12 month-ends; DIO, DSO, DPO use annual flows.")
put(wm, "A20", "Monthly days (rows 5 to 16) use that month's flows and are lumpy; the year row is the figure to use. Blue values: Python results/monthly_balances.csv.")
wm.column_dimensions["A"].width = 14
for c in "BCDEFGHIJKL": wm.column_dimensions[c].width = 14

# ---------------- Categories
wc = wb.create_sheet("Categories")
put(wc, "A1", "By product category (stock and supplier side)", title)
hdr(wc, 4, ["Category", "COGS (Rs)", "Avg inventory (Rs)", "DIO (days)", "Avg payables (Rs)", "DPO (days)", "Slow category? (1 = yes)", "Stock released by lever 1 (Rs)"])
for i, r in cat.iterrows():
    x = 5 + i
    put(wc, f"A{x}", r.category); put(wc, f"B{x}", round(r.cogs), blue, RS); put(wc, f"C{x}", round(r.avg_inventory, 2), blue, RS)
    put(wc, f"D{x}", f"=C{x}/B{x}*Inputs!$B$5", black, DAYS); put(wc, f"E{x}", round(r.avg_payables, 2), blue, RS)
    put(wc, f"F{x}", f"=E{x}/B{x}*Inputs!$B$5", black, DAYS); put(wc, f"G{x}", int(r.slow), blue, '0')
    put(wc, f"H{x}", f"=C{x}*G{x}*Inputs!$B$6", black, RS)
put(wc, "A11", "Total", bold)
for col in "BCEH": put(wc, f"{col}11", f"=SUM({col}5:{col}10)", bold, RS)
put(wc, "D11", "=C11/B11*Inputs!$B$5", bold, DAYS); put(wc, "F11", "=E11/B11*Inputs!$B$5", bold, DAYS)
put(wc, "A13", "Blue values: Python results/by_category.csv. The slow flag is my choice (the three slowest stock days); change it to test other categories.")
wc.column_dimensions["A"].width = 18
for c in "BCDEFGH": wc.column_dimensions[c].width = 18

# ---------------- Customers
wu = wb.create_sheet("Customers")
put(wu, "A1", "By customer type (credit side)", title)
hdr(wu, 4, ["Customer type", "Revenue (Rs)", "Avg receivables (Rs)", "DSO (days)", "Lever 2 applies? (1 = yes)", "Cash released by lever 2 (Rs)"])
for i, r in typ.iterrows():
    x = 5 + i
    put(wu, f"A{x}", r.customer_type); put(wu, f"B{x}", round(r.revenue), blue, RS); put(wu, f"C{x}", round(r.avg_receivables, 2), blue, RS)
    put(wu, f"D{x}", f"=C{x}/B{x}*Inputs!$B$5", black, DAYS); put(wu, f"E{x}", int(r.customer_type == "Contractor"), blue, '0')
    put(wu, f"F{x}", f"=B{x}*E{x}/Inputs!$B$5*Inputs!$B$7", black, RS)
put(wu, "A8", "Total", bold)
for col in "BCF": put(wu, f"{col}8", f"=SUM({col}5:{col}7)", bold, RS)
put(wu, "D8", "=C8/B8*Inputs!$B$5", bold, DAYS)
put(wu, "A10", "Blue values: Python results/by_customer_type.csv. Homeowners pay at the counter, so their receivables are zero.")
wu.column_dimensions["A"].width = 18
for c in "BCDEF": wu.column_dimensions[c].width = 22

# ---------------- Summary
wsu = wb.create_sheet("Summary")
put(wsu, "A1", "Summary: how long cash stays stuck", title)
hdr(wsu, 3, ["Measure", "Value", "Unit / note"])
S = [
 (4, "Revenue", "=Monthly!C17", RS, "Rs, 12 months", green), (5, "COGS", "=Monthly!D17", RS, "Rs, 12 months", green),
 (6, "Gross profit", "=B4-B5", RS, "Rs", black),
 (8, "Average inventory", "=Monthly!F17", RS, "Rs, mean of 12 month-ends", green), (9, "Average receivables", "=Monthly!G17", RS, "Rs", green),
 (10, "Average payables", "=Monthly!H17", RS, "Rs", green),
 (12, "DIO: days in stock", "=B8/B5*Inputs!B5", DAYS, "days", black), (13, "DSO: days customers take to pay", "=B9/B4*Inputs!B5", DAYS, "days", black),
 (14, "DPO: days the store takes to pay", "=B10/B5*Inputs!B5", DAYS, "days", black), (15, "Cash conversion cycle", "=B12+B13-B14", DAYS, "days = DIO + DSO - DPO", black),
 (17, "Working capital tied up", "=B8+B9-B10", RS, "Rs = inventory + receivables - payables", black),
 (18, "Cost of carrying it (a year)", "=B17*Inputs!B4", RS, "Rs at the cost of money on Inputs", black),
 (19, "Carrying cost as % of gross profit", "=B18/B6", PCT, "", black),
 (21, "Lever 1: stock released", "=Categories!H11", RS, "Rs", green), (22, "Lever 2: receivables released", "=Customers!F8", RS, "Rs", green),
 (23, "Lever 3: payables extended", "=B5/Inputs!B5*Inputs!B8", RS, "Rs", black), (24, "Total cash released", "=SUM(B21:B23)", RS, "Rs", black),
 (25, "Yearly saving at the cost of money", "=B24*Inputs!B4", RS, "Rs", black), (26, "Working capital after levers", "=B17-B24", RS, "Rs", black),
 (27, "Cash conversion cycle after levers", "=(B8-B21)/B5*Inputs!B5+(B9-B22)/B4*Inputs!B5-(B10+B23)/B5*Inputs!B5", DAYS, "days", black),
]
for r, lab, f, nf, note, fnt in S:
    put(wsu, f"A{r}", lab, bold if r in (15, 17, 18, 24, 27) else black); put(wsu, f"B{r}", f, fnt, nf); put(wsu, f"C{r}", note)
wsu.column_dimensions["A"].width = 40; wsu.column_dimensions["B"].width = 18; wsu.column_dimensions["C"].width = 42

# ---------------- Checks
wk = wb.create_sheet("Checks")
put(wk, "A1", "Checks: this workbook against the Python results", title)
hdr(wk, 3, ["Measure", "Python (results/summary.csv)", "Excel (this file)", "Difference", "Tolerance", "Status"])
C = [("Revenue", "revenue", "Summary!B4", 0.5), ("COGS", "cogs", "Summary!B5", 0.5), ("Average inventory", "avg_inventory", "Summary!B8", 0.5),
     ("Average receivables", "avg_receivables", "Summary!B9", 0.5), ("Average payables", "avg_payables", "Summary!B10", 0.5),
     ("DIO", "dio", "Summary!B12", 0.001), ("DSO", "dso", "Summary!B13", 0.001), ("DPO", "dpo", "Summary!B14", 0.001),
     ("Cash conversion cycle", "ccc", "Summary!B15", 0.001), ("Working capital tied up", "working_capital", "Summary!B17", 0.5),
     ("Carrying cost a year", "carrying_cost", "Summary!B18", 0.5), ("Lever 1", "lever1", "Summary!B21", 1), ("Lever 2", "lever2", "Summary!B22", 1),
     ("Lever 3", "lever3", "Summary!B23", 1), ("Total cash released", "released", "Summary!B24", 1), ("Cycle after levers", "ccc_after", "Summary!B27", 0.001)]
for i, (lab, key, ref, tol) in enumerate(C):
    x = 4 + i
    put(wk, f"A{x}", lab); put(wk, f"B{x}", float(summ[key]), blue, '#,##0.0000'); put(wk, f"C{x}", f"={ref}", green, '#,##0.0000')
    put(wk, f"D{x}", f"=C{x}-B{x}", black, '0.0000'); put(wk, f"E{x}", tol, blue, '0.000'); put(wk, f"F{x}", f'=IF(ABS(D{x})<=E{x},"OK","CHECK")')
n = 4 + len(C)
put(wk, f"A{n+1}", "Internal consistency (should be 0)", bold)
I = [("Inventory: categories total minus monthly average", "=Categories!C11-Monthly!F17"), ("Payables: categories total minus monthly average", "=Categories!E11-Monthly!H17"),
     ("Receivables: customers total minus monthly average", "=Customers!C8-Monthly!G17"), ("Revenue: customers total minus monthly total", "=Customers!B8-Monthly!C17"),
     ("COGS: categories total minus monthly total", "=Categories!B11-Monthly!D17")]
for j, (lab, f) in enumerate(I):
    x = n + 2 + j; put(wk, f"A{x}", lab); put(wk, f"D{x}", f, black, '0.0000'); put(wk, f"E{x}", 2, blue, '0.000'); put(wk, f"F{x}", f'=IF(ABS(D{x})<=E{x},"OK","CHECK")')
last = n + 1 + len(I)
put(wk, f"A{last+2}", "All checks", bold); put(wk, f"F{last+2}", f'=IF(COUNTIF(F4:F{last},"CHECK")=0,"ALL OK","CHECK")', bold)
wk.column_dimensions["A"].width = 52
for c in "BCDEF": wk.column_dimensions[c].width = 22
wb.save("excel/working_capital_model.xlsx"); print("saved")
