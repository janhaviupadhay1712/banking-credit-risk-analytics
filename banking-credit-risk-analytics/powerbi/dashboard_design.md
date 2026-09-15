# Power BI Dashboard Design — 3-Page Credit Risk Report

> No .pbix binary is included (Power BI Desktop isn't available in this
> environment to generate one). This is a build-ready spec: load
> `data/loan_data_features.csv` (or the SQL tables) into Power BI Desktop,
> paste in the measures from `DAX_measures.md`, and lay out the pages below —
> it will take ~45–60 minutes to assemble.

**Theme:** Navy (#1F4E78) + white background, red/amber/green for risk,
Segoe UI font, consistent card style across pages.

---

## Page 1 — Executive Overview

**Top KPI card strip (5 cards):**
`Total Loans` · `Total Loan Amount` · `Total Outstanding Amount` ·
`Default Rate %` · `Delinquency Rate %`

**Visuals:**
- **Line chart:** Monthly loan applications + Default Rate % (dual axis) — trend over time
- **Donut chart:** Loan portfolio by `Loan_Status`
- **Stacked bar:** Risk Segment distribution (Low/Medium/High) by count and by Outstanding Amount
- **Map or bar chart:** Total Outstanding Amount by `Region`
- **Card:** `NPA Ratio %` with conditional color (green <5%, amber 5–8%, red >8%)

**Slicers (panel on left, applies to whole page):**
`Region`, `Loan_Type`, `Application_Year`, `Employment_Type`

---

## Page 2 — Credit Risk Analysis

**KPI strip:** `High-Risk Customers` · `High-Risk % of Book` · `Average Credit Score` · `Average DTI` · `NPA Amount`

**Visuals:**
- **Matrix/heatmap:** Risk Segment (rows) × Loan_Type (columns), values = Default Rate %, background color scale
- **Scatter chart:** Credit_Score (x) vs DTI (y), size = Outstanding_Amount, color = Risk_Segment
- **Bar chart:** Default Rate % by Credit_Score_Band
- **Bar chart:** Default Rate % by DTI_Band
- **Bar chart:** Default Rate % by Employment_Type
- **Clustered column:** Average Interest Rate by Risk Segment (shows if risk-based pricing is working)

**Slicers:** `Risk_Segment`, `Credit_Score_Band`, `DTI_Band`

---

## Page 3 — Loan / Customer Insights

**KPI strip:** `Total Customers` · `Average Loan Amount` · `Overdue Amount (30+ DPD)` · `Overdue Loan Count (90+ DPD)`

**Visuals:**
- **Bar chart:** Top 10 Branches by Default Rate % (uses `Branch Default Rank` measure, filtered `<= 10`)
- **Column chart:** Loan volume & amount by `Loan_Type`
- **Bar chart:** DPD bucket analysis (Current / 1-30 / 31-60 / 61-90 / 90+) — count & outstanding amount
- **Detailed table — "High-Risk Customer Watchlist":**
  Columns: `Customer_ID`, `Region`, `Branch`, `Loan_Type`, `Credit_Score`, `DTI`,
  `Previous_Defaults`, `Late_Payments`, `Days_Past_Due`, `Outstanding_Amount`,
  `Loan_Status`, `Risk_Segment`
  - Filtered to `Risk_Segment = "High Risk"`, sorted by `Outstanding_Amount` descending
  - Conditional formatting (background color) on `Days_Past_Due` and `Risk_Segment`
  - Add a "Drill through" from the Page 1/2 visuals into this table filtered by
    whatever segment/region/loan type was clicked

**Slicers:** `Region`, `Branch`, `Loan_Type`

---

## Cross-page interactivity checklist
- [ ] Bookmarks for "Reset filters" button on each page
- [ ] Drill-through from Region/Loan_Type visuals to the Page 3 customer table
- [ ] Tooltips showing `Portfolio Risk Verdict` measure on hover over KPI cards
- [ ] Consistent color mapping: Low Risk = green, Medium Risk = amber, High Risk = red, used identically across all 3 pages
