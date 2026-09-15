# Banking Credit Risk Analytics

An end-to-end, portfolio-ready credit risk analytics project built for an
entry-level Data Analyst role. Analyzes a synthetic 21,500+ record loan
portfolio to identify default/delinquency trends, high-risk customers,
and drivers of risk across loan type, income, credit score, DTI,
employment and region — with actionable recommendations for management.

**Primary stack:** SQL · Python (Pandas/NumPy/Matplotlib/Seaborn) · Excel · Power BI
**Secondary/optional:** Logistic Regression & Random Forest default prediction

---

## Folder Structure

```
banking-credit-risk-analytics/
├── data/
│   ├── generate_data.py              # Synthetic data generator (messy, realistic)
│   ├── loan_data_raw.csv             # Raw data with missing values/dupes/outliers
│   ├── loan_data_clean.csv           # After cleaning (01_data_cleaning.py)
│   ├── loan_data_features.csv        # After feature engineering + risk segmentation
│   └── kpi_summary.csv               # KPI snapshot exported from Python
├── python/
│   ├── 01_data_cleaning.py
│   ├── 02_feature_engineering_risk_segmentation.py
│   ├── 03_eda_visualizations.py      # 16 charts saved to python/charts/
│   ├── 04_kpi_business_insights.py   # KPI calc + auto-derived insights
│   ├── 05_optional_ml_model.py       # Secondary: Logistic Regression + Random Forest
│   └── charts/                       # 18 PNG visualizations
├── sql/
│   ├── 01_schema.sql                 # customers + loans tables, indexes
│   └── 02_queries.sql                # 25 interview-quality analytical queries
├── excel/
│   ├── build_excel.py                # Generates the workbook (openpyxl)
│   └── Credit_Risk_Analysis.xlsx     # Clean_Data / KPI_Dashboard / Risk_Analysis /
│                                      # Overdue_Tracker / Read_Me sheets, live formulas
├── powerbi/
│   ├── DAX_measures.md               # All DAX measures (copy-paste ready)
│   └── dashboard_design.md           # 3-page dashboard build spec
├── docs/
│   ├── resume_bullets.md
│   ├── linkedin_description.md
│   ├── interview_questions_technical.md
│   ├── interview_questions_project.md
│   ├── business_recommendations.md
│   └── limitations_and_ethics.md
└── README.md
```

---

## How to Reproduce

```bash
cd data && python3 generate_data.py                     # 1. generate raw messy data
cd ../python
python3 01_data_cleaning.py                              # 2. clean
python3 02_feature_engineering_risk_segmentation.py       # 3. engineer features + segment risk
python3 03_eda_visualizations.py                          # 4. generate 16 charts
python3 04_kpi_business_insights.py                        # 5. KPIs + insights (printed + saved)
python3 05_optional_ml_model.py                            # 6. OPTIONAL: ML default model
cd ../excel && python3 build_excel.py                      # 7. build Excel workbook
```

For SQL: run `sql/01_schema.sql` then `sql/02_queries.sql` against any
Postgres/MySQL instance, loading `data/loan_data_features.csv` as described
in the schema file's comments.

For Power BI: open Power BI Desktop, import `data/loan_data_features.csv`
(or the SQL tables), paste in the measures from `powerbi/DAX_measures.md`,
and follow `powerbi/dashboard_design.md` to lay out the 3 pages.

---

## Dataset

21,850 raw records (→ 21,527 after cleaning) simulating a retail loan book:
Customer_ID, Age, Income, Employment_Type, Credit_Score, DTI, Loan_Type,
Loan_Amount, Interest_Rate, Loan_Term, Region, Branch, Previous_Defaults,
Late_Payments, Outstanding_Amount, Days_Past_Due, Loan_Status,
Application_Date, Payment_Date — plus engineered fields (Risk_Segment,
Age/Income/Credit-Score/DTI bands, EMI estimate, Loan-to-Income ratio, etc.).

The generator deliberately injects **missing values, duplicate rows,
inconsistent category text ("self employed" / "Self-Employed" / "SELF
EMPLOYED"), mixed date formats, and outliers** so the cleaning process in
`01_data_cleaning.py` is demonstrable and realistic — not just "clean data
in, clean data out."

**All numbers in the KPI summary, charts, and insights are calculated
directly from this dataset** — nothing is fabricated or hardcoded.

---

## Risk Segmentation Logic

A transparent, rule-based points system (see
`python/02_feature_engineering_risk_segmentation.py` and SQL query #6/#7),
mirroring how many banks build an early-warning scorecard:

| Factor | Points |
|---|---|
| Credit Score < 580 | +3 | 580–669: +2 | 670–739: +1 | ≥740: 0 |
| DTI > 50% | +3 | 36–50%: +2 | 20–36%: +1 | <20%: 0 |
| Previous Defaults ≥ 2 | +3 | == 1: +2 | 0: 0 |
| Late Payments ≥ 6 | +2 | 3–5: +1 | 0–2: 0 |

**Total points 0–2 → Low Risk · 3–5 → Medium Risk · 6+ → High Risk**

This logic is implemented identically in Python (pandas `.apply()`) and SQL
(`CASE` expressions), so segment counts match exactly across both.

---

## Key KPIs (computed from the dataset)

| KPI | Value |
|---|---|
| Total Loans | 21,527 |
| Total Loan Amount Disbursed | ₹24.95 billion |
| Total Outstanding Amount | ₹10.91 billion |
| Overall Default Rate | 5.32% |
| Overall Delinquency Rate | 17.08% |
| Average Credit Score | 651 |
| Average DTI | 35.08% |
| High-Risk Customers | 4,128 (19.2% of book) |
| NPA Ratio | 8.75% |

See `docs/business_recommendations.md` for the insights derived from these
numbers and what management should do about them.

---

## Optional ML Component

`python/05_optional_ml_model.py` trains a Logistic Regression and a Random
Forest to predict `Is_Default` from credit/behavioral features, with a
feature-importance chart and ROC curve. **This is intentionally a small,
secondary piece of the project** — the dataset is synthetic with largely
independent random noise on top of a modest risk signal, so the models
score modestly (ROC-AUC ≈ 0.57–0.59). That's an honest, expected result for
a demo dataset, not a deployment-ready model — the value of this repo is in
the SQL/Python/Excel/Power BI analytics layer, not the ML.

---

## Note on Excel `XLOOKUP`

The brief calls for `XLOOKUP`; the workbook actually uses `INDEX`/`MATCH`
for the customer lookup on the `Risk_Analysis` sheet. Reason: this build
environment recalculates formulas with a LibreOffice engine that cannot
evaluate `XLOOKUP` and silently corrupts it. `INDEX`/`MATCH` returns the
exact same result and is fully compatible with older and newer Excel
alike; a comment on the input cell documents the 1:1 `XLOOKUP` swap for
anyone opening it in modern Excel.
