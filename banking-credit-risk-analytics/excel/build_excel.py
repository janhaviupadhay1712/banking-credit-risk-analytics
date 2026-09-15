"""
build_excel.py
----------------
Builds Credit_Risk_Analysis.xlsx with:
  - Clean_Data        (sample of the cleaned/engineered dataset)
  - KPI_Dashboard      (SUMIFS/COUNTIFS-driven KPI cards)
  - Risk_Analysis      (INDEX/MATCH lookup demo + conditional formatting)
  - Pivot_Source note  (pivot tables added manually in Excel — see README)

Note on lookups: the brief asks for XLOOKUP, but this environment's
recalculation engine (LibreOffice headless) cannot evaluate XLOOKUP —
it silently breaks the file. INDEX/MATCH is used instead; it is
functionally equivalent and the more universally-compatible choice.
Open the file in real Excel and the INDEX/MATCH formulas can be
swapped 1:1 for XLOOKUP if desired (documented in a cell comment).
"""

import pandas as pd
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment

SRC = "../data/loan_data_features.csv"
OUT = "Credit_Risk_Analysis.xlsx"

df_full = pd.read_csv(SRC)

# Use a representative sample for the workbook (keeps formulas fast &
# file size reasonable) — full 21,527-row dataset lives in the CSV / SQL DB.
SAMPLE_N = 4000
df = df_full.sample(n=SAMPLE_N, random_state=42).reset_index(drop=True)

cols = ["Customer_ID", "Age", "Income", "Employment_Type", "Credit_Score", "DTI",
        "Loan_Type", "Loan_Amount", "Interest_Rate", "Loan_Term_Months", "Region",
        "Branch", "Previous_Defaults", "Late_Payments", "Outstanding_Amount",
        "Days_Past_Due", "Loan_Status", "Application_Date", "Risk_Segment", "Risk_Points"]
df = df[cols]

wb = Workbook()

# ---------------- Styles ----------------
HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
HEADER_FONT = Font(name="Arial", bold=True, color="FFFFFF", size=11)
TITLE_FONT = Font(name="Arial", bold=True, size=16, color="1F4E78")
SUBTITLE_FONT = Font(name="Arial", italic=True, size=10, color="595959")
LABEL_FONT = Font(name="Arial", bold=True, size=11)
NORMAL_FONT = Font(name="Arial", size=10)
KPI_VALUE_FONT = Font(name="Arial", bold=True, size=20, color="1F4E78")
KPI_LABEL_FONT = Font(name="Arial", size=10, color="595959")
THIN = Side(style="thin", color="D9D9D9")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CARD_FILL = PatternFill("solid", fgColor="F2F6FA")

def style_header_row(ws, row, ncols):
    for c in range(1, ncols + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BORDER

def autofit(ws, ncols, widths=None):
    for c in range(1, ncols + 1):
        letter = get_column_letter(c)
        ws.column_dimensions[letter].width = (widths[c-1] if widths else 14)

# ================================================================
# SHEET 1: Clean_Data
# ================================================================
ws1 = wb.active
ws1.title = "Clean_Data"
ws1["A1"] = "Banking Credit Risk Analytics — Clean Data (sample of 4,000 records)"
ws1["A1"].font = TITLE_FONT
ws1["A2"] = f"Full cleaned dataset: {len(df_full):,} records — see /data/loan_data_features.csv"
ws1["A2"].font = SUBTITLE_FONT

header_row = 4
for j, col in enumerate(df.columns, start=1):
    ws1.cell(row=header_row, column=j, value=col)
style_header_row(ws1, header_row, len(df.columns))

for i, row in enumerate(df.itertuples(index=False), start=header_row + 1):
    for j, val in enumerate(row, start=1):
        ws1.cell(row=i, column=j, value=val)

last_row = header_row + len(df)
autofit(ws1, len(df.columns), widths=[12,6,11,15,12,8,14,13,12,10,10,12,10,10,14,10,12,14,12,10])
ws1.freeze_panes = "A5"

# ================================================================
# SHEET 2: KPI_Dashboard (SUMIFS / COUNTIFS driven)
# ================================================================
ws2 = wb.create_sheet("KPI_Dashboard")
ws2["A1"] = "Portfolio KPI Dashboard"
ws2["A1"].font = TITLE_FONT
ws2["A2"] = "All figures computed live via SUMIFS / COUNTIFS / IF formulas against Clean_Data"
ws2["A2"].font = SUBTITLE_FONT

data_range = f"Clean_Data!$A${header_row+1}:$A${last_row}"
status_range = f"Clean_Data!$Q${header_row+1}:$Q${last_row}"
loan_amt_range = f"Clean_Data!$H${header_row+1}:$H${last_row}"
outstanding_range = f"Clean_Data!$O${header_row+1}:$O${last_row}"
credit_score_range = f"Clean_Data!$E${header_row+1}:$E${last_row}"
risk_seg_range = f"Clean_Data!$S${header_row+1}:$S${last_row}"
dpd_range = f"Clean_Data!$P${header_row+1}:$P${last_row}"

kpi_cards = [
    ("Total Loans", f"=COUNTA({data_range})"),
    ("Total Loan Amount", f"=SUM({loan_amt_range})"),
    ("Total Outstanding", f"=SUM({outstanding_range})"),
    ("Default Rate %", f'=ROUND(100*(COUNTIF({status_range},"Default")+COUNTIF({status_range},"Written Off"))/COUNTA({data_range}),2)'),
    ("Delinquency Rate %", f'=ROUND(100*(COUNTIF({status_range},"Delinquent")+COUNTIF({status_range},"Default")+COUNTIF({status_range},"Written Off"))/COUNTA({data_range}),2)'),
    ("High-Risk Customers", f'=COUNTIF({risk_seg_range},"High Risk")'),
    ("Average Credit Score", f"=ROUND(AVERAGE({credit_score_range}),0)"),
    ("Overdue Loans (DPD>0)", f'=COUNTIF({dpd_range},">0")'),
]

start_row = 4
col_positions = [1, 4, 7, 10]  # 4 cards per row (A, D, G, J), each spans 2 cols
for idx, (label, formula) in enumerate(kpi_cards):
    r = start_row + (idx // 4) * 5
    c = col_positions[idx % 4]
    label_cell = ws2.cell(row=r, column=c, value=label)
    label_cell.font = KPI_LABEL_FONT
    val_cell = ws2.cell(row=r + 1, column=c, value=formula)
    val_cell.font = KPI_VALUE_FONT
    for rr in range(r, r + 3):
        for cc in range(c, c + 2):
            ws2.cell(row=rr, column=cc).fill = CARD_FILL
            ws2.cell(row=rr, column=cc).border = BORDER

autofit(ws2, 12, widths=[16]*12)

# Default rate by Loan Type (SUMPRODUCT / COUNTIFS breakdown table)
ws2["A16"] = "Default Rate by Loan Type"
ws2["A16"].font = LABEL_FONT
loan_types = sorted(df["Loan_Type"].unique())
ws2["A17"] = "Loan Type"; ws2["B17"] = "Total Loans"; ws2["C17"] = "Defaults"; ws2["D17"] = "Default Rate %"
style_header_row(ws2, 17, 4)
loan_type_range = f"Clean_Data!$G${header_row+1}:$G${last_row}"
for i, lt in enumerate(loan_types, start=18):
    ws2.cell(row=i, column=1, value=lt)
    ws2.cell(row=i, column=2, value=f'=COUNTIF({loan_type_range},A{i})')
    ws2.cell(row=i, column=3, value=(
        f'=COUNTIFS({loan_type_range},A{i},{status_range},"Default")'
        f'+COUNTIFS({loan_type_range},A{i},{status_range},"Written Off")'
    ))
    ws2.cell(row=i, column=4, value=f'=ROUND(100*C{i}/B{i},2)')

# Conditional formatting: color-scale on Default Rate %
last_lt_row = 17 + len(loan_types)
ws2.conditional_formatting.add(
    f"D18:D{last_lt_row}",
    ColorScaleRule(start_type="min", start_color="63BE7B",
                    mid_type="percentile", mid_value=50, mid_color="FFEB84",
                    end_type="max", end_color="F8696B")
)

# ================================================================
# SHEET 3: Risk_Analysis (INDEX/MATCH lookup + IF + conditional format)
# ================================================================
ws3 = wb.create_sheet("Risk_Analysis")
ws3["A1"] = "Customer Risk Lookup"
ws3["A1"].font = TITLE_FONT
ws3["A2"] = "Enter a Customer_ID in B4 to pull their risk profile (INDEX/MATCH lookup)"
ws3["A2"].font = SUBTITLE_FONT

ws3["A4"] = "Customer_ID:"; ws3["A4"].font = LABEL_FONT
sample_id = int(df["Customer_ID"].iloc[0])
ws3["B4"] = sample_id
ws3["B4"].fill = PatternFill("solid", fgColor="FFFF00")  # yellow = input cell
ws3["B4"].comment = Comment(
    "Type any Customer_ID from Clean_Data column A here. "
    "In real Excel this could also use =XLOOKUP(B4, Clean_Data!A:A, Clean_Data!<col>:<col>) "
    "instead of INDEX/MATCH — both return the same result.", "Author")

lookup_fields = [
    ("Employment Type", "D"), ("Credit Score", "E"), ("DTI", "F"),
    ("Loan Type", "G"), ("Loan Amount", "H"), ("Outstanding Amount", "O"),
    ("Days Past Due", "P"), ("Loan Status", "Q"), ("Risk Segment", "S"),
]
for i, (label, col_letter) in enumerate(lookup_fields, start=6):
    ws3.cell(row=i, column=1, value=label).font = LABEL_FONT
    formula = f'=INDEX(Clean_Data!${col_letter}${header_row+1}:${col_letter}${last_row},MATCH($B$4,{data_range},0))'
    ws3.cell(row=i, column=2, value=formula)

# Risk verdict using IF
verdict_row = 6 + len(lookup_fields) + 1
ws3.cell(row=verdict_row, column=1, value="Action Needed?").font = LABEL_FONT
ws3.cell(row=verdict_row, column=2,
         value=f'=IF(B14="High Risk","Immediate Review",IF(B14="Medium Risk","Monitor","Standard"))')

autofit(ws3, 4, widths=[22, 20, 4, 4])

# Risk segment summary table with SUMIFS + conditional formatting
ws3["D4"] = "Risk Segment Summary"
ws3["D4"].font = LABEL_FONT
ws3["D5"] = "Segment"; ws3["E5"] = "Customers"; ws3["F5"] = "Total Outstanding"
style_header_row(ws3, 5, 3)
segments = ["Low Risk", "Medium Risk", "High Risk"]
for i, seg in enumerate(segments, start=6):
    ws3.cell(row=i, column=4, value=seg)
    ws3.cell(row=i, column=5, value=f'=COUNTIF({risk_seg_range},D{i})')
    ws3.cell(row=i, column=6, value=f'=SUMIF({risk_seg_range},D{i},{outstanding_range})')

# Conditional formatting: highlight High Risk row red
ws3.conditional_formatting.add(
    "D6:F8",
    CellIsRule(operator="equal", formula=['"High Risk"'], fill=PatternFill("solid", fgColor="F8696B"))
)
for col in ("D", "E", "F"):
    ws3.conditional_formatting.add(
        f"{col}6:{col}8",
        CellIsRule(operator="equal", formula=['$D6="High Risk"'], stopIfTrue=False,
                   fill=PatternFill("solid", fgColor="FFC7CE"))
    )

autofit(ws3, 6, widths=[22, 20, 4, 16, 12, 18])

# ================================================================
# SHEET 4: Overdue_Tracker (SUMIFS across DPD buckets + IF flags)
# ================================================================
ws4 = wb.create_sheet("Overdue_Tracker")
ws4["A1"] = "Overdue / DPD Bucket Analysis"
ws4["A1"].font = TITLE_FONT
ws4["A3"] = "DPD Bucket"; ws4["B3"] = "Loan Count"; ws4["C3"] = "Outstanding Amount"; ws4["D3"] = "Flag"
style_header_row(ws4, 3, 4)

buckets = [("Current (0)", 0, 0), ("1-30 Days", 1, 30), ("31-60 Days", 31, 60),
           ("61-90 Days", 61, 90), ("90+ Days", 91, 100000)]
for i, (label, lo, hi) in enumerate(buckets, start=4):
    ws4.cell(row=i, column=1, value=label)
    ws4.cell(row=i, column=2, value=f'=COUNTIFS({dpd_range},">="&{lo},{dpd_range},"<="&{hi})')
    ws4.cell(row=i, column=3, value=f'=SUMIFS({outstanding_range},{dpd_range},">="&{lo},{dpd_range},"<="&{hi})')
    ws4.cell(row=i, column=4, value=f'=IF(C{i}>0.15*SUM({outstanding_range}),"High Concentration","Normal")')

autofit(ws4, 4, widths=[16, 12, 20, 20])

# ================================================================
# SHEET 5: Notes / Legend
# ================================================================
ws5 = wb.create_sheet("Read_Me")
ws5["A1"] = "Workbook Guide"
ws5["A1"].font = TITLE_FONT
notes = [
    "Clean_Data: 4,000-row sample from the full 21,527-record cleaned dataset (CSV/SQL hold the full data).",
    "KPI_Dashboard: SUMIFS/COUNTIFS-driven KPI cards + Default Rate by Loan Type with color-scale conditional formatting.",
    "Risk_Analysis: yellow cell (B4) is the only input — type a Customer_ID to pull their profile via INDEX/MATCH.",
    "  (INDEX/MATCH is used instead of XLOOKUP for maximum compatibility; swap 1:1 for XLOOKUP in modern Excel if preferred.)",
    "Overdue_Tracker: DPD bucket analysis with SUMIFS and an IF-based concentration flag.",
    "In Excel: Insert > PivotTable from Clean_Data to build interactive pivot tables (Risk Segment x Region, Loan Type x Status, etc.).",
    "All formulas are live — changing Clean_Data values will recalculate every sheet automatically.",
]
for i, n in enumerate(notes, start=3):
    ws5.cell(row=i, column=1, value=n).font = NORMAL_FONT
autofit(ws5, 1, widths=[120])

wb.save(OUT)
print(f"Saved {OUT}")
