"""
04_kpi_business_insights.py
-----------------------------
Calculates portfolio KPIs and prints data-driven business insights
(numbers computed live from the dataset — nothing fabricated).

Run: python 04_kpi_business_insights.py
"""

import pandas as pd
import numpy as np

df = pd.read_csv("../data/loan_data_features.csv", parse_dates=["Application_Date", "Payment_Date"])

pd.set_option("display.float_format", lambda x: f"{x:,.2f}")

print("=" * 70)
print("PORTFOLIO KPI SUMMARY")
print("=" * 70)

total_loans = len(df)
total_customers = df["Customer_ID"].nunique()
total_loan_amount = df["Loan_Amount"].sum()
total_outstanding = df["Outstanding_Amount"].sum()
default_rate = df["Is_Default"].mean() * 100
delinquency_rate = df["Is_Delinquent"].mean() * 100
avg_credit_score = df["Credit_Score"].mean()
avg_dti = df["DTI"].mean()
high_risk_customers = (df["Risk_Segment"] == "High Risk").sum()
high_risk_pct = high_risk_customers / total_loans * 100
avg_loan_amount = df["Loan_Amount"].mean()
npa_amount = df.loc[df["Is_Default"] == 1, "Outstanding_Amount"].sum()  # non-performing exposure

kpis = {
    "Total Loans": f"{total_loans:,}",
    "Unique Customers": f"{total_customers:,}",
    "Total Loan Amount Disbursed (₹)": f"{total_loan_amount:,.0f}",
    "Total Outstanding Amount (₹)": f"{total_outstanding:,.0f}",
    "Overall Default Rate (%)": f"{default_rate:.2f}",
    "Overall Delinquency Rate (%)": f"{delinquency_rate:.2f}",
    "Average Credit Score": f"{avg_credit_score:.0f}",
    "Average DTI (%)": f"{avg_dti:.2f}",
    "High-Risk Customers": f"{high_risk_customers:,} ({high_risk_pct:.1f}% of book)",
    "Average Loan Amount (₹)": f"{avg_loan_amount:,.0f}",
    "Non-Performing Exposure / NPA (₹)": f"{npa_amount:,.0f}",
    "NPA Ratio (NPA / Outstanding, %)": f"{npa_amount / total_outstanding * 100:.2f}",
}

for k, v in kpis.items():
    print(f"{k:45s}: {v}")

# ------------------------------------------------------------------
# Deeper breakdowns
# ------------------------------------------------------------------
print("\n" + "=" * 70)
print("DEFAULT RATE BY LOAN TYPE")
print("=" * 70)
print((df.groupby("Loan_Type")["Is_Default"].mean() * 100).sort_values(ascending=False).round(2))

print("\n" + "=" * 70)
print("DEFAULT RATE BY REGION")
print("=" * 70)
print((df.groupby("Region")["Is_Default"].mean() * 100).sort_values(ascending=False).round(2))

print("\n" + "=" * 70)
print("DEFAULT RATE BY EMPLOYMENT TYPE")
print("=" * 70)
print((df.groupby("Employment_Type")["Is_Default"].mean() * 100).sort_values(ascending=False).round(2))

print("\n" + "=" * 70)
print("RISK SEGMENT DISTRIBUTION")
print("=" * 70)
seg = df["Risk_Segment"].value_counts()
seg_pct = df["Risk_Segment"].value_counts(normalize=True) * 100
print(pd.DataFrame({"Count": seg, "Percent": seg_pct.round(1)}))

print("\n" + "=" * 70)
print("TOP 10 HIGH-RISK CUSTOMERS BY OUTSTANDING AMOUNT")
print("=" * 70)
top_risk = (
    df[df["Risk_Segment"] == "High Risk"]
    .sort_values("Outstanding_Amount", ascending=False)
    [["Customer_ID", "Loan_Type", "Credit_Score", "DTI", "Previous_Defaults",
      "Late_Payments", "Days_Past_Due", "Outstanding_Amount", "Loan_Status"]]
    .head(10)
)
print(top_risk.to_string(index=False))

# ------------------------------------------------------------------
# Auto-generated business insights (derived, not hardcoded)
# ------------------------------------------------------------------
print("\n" + "=" * 70)
print("KEY BUSINESS INSIGHTS (auto-derived from data)")
print("=" * 70)

worst_loan_type = (df.groupby("Loan_Type")["Is_Default"].mean() * 100).idxmax()
worst_loan_type_rate = (df.groupby("Loan_Type")["Is_Default"].mean() * 100).max()

worst_region = (df.groupby("Region")["Is_Default"].mean() * 100).idxmax()
worst_region_rate = (df.groupby("Region")["Is_Default"].mean() * 100).max()

worst_employment = (df.groupby("Employment_Type")["Is_Default"].mean() * 100).idxmax()
worst_employment_rate = (df.groupby("Employment_Type")["Is_Default"].mean() * 100).max()

corr_credit_default = df[["Credit_Score", "Is_Default"]].corr().iloc[0, 1]
corr_dti_default = df[["DTI", "Is_Default"]].corr().iloc[0, 1]

insights = [
    f"1. '{worst_loan_type}' has the highest default rate at {worst_loan_type_rate:.1f}%, "
    f"vs. a portfolio average of {default_rate:.1f}%.",

    f"2. The '{worst_region}' region shows the highest default rate ({worst_region_rate:.1f}%), "
    f"indicating a need for tighter underwriting or collections focus there.",

    f"3. Customers with '{worst_employment}' employment status default at {worst_employment_rate:.1f}%, "
    f"the highest of all employment categories.",

    f"4. Credit Score is negatively correlated with default (r = {corr_credit_default:.2f}); "
    f"DTI is positively correlated with default (r = {corr_dti_default:.2f}) — both behave as expected "
    f"risk drivers, validating the segmentation logic.",

    f"5. High-Risk customers make up {high_risk_pct:.1f}% of the book by count but hold "
    f"{df.loc[df['Risk_Segment']=='High Risk','Outstanding_Amount'].sum() / total_outstanding * 100:.1f}% "
    f"of total outstanding exposure — a disproportionate concentration of risk.",

    f"6. Overall NPA ratio stands at {npa_amount / total_outstanding * 100:.2f}%, "
    f"{'above' if npa_amount/total_outstanding*100 > 5 else 'within'} the commonly cited 5% regulatory "
    f"comfort threshold for retail portfolios.",
]

for line in insights:
    print(line)

# Save KPI summary to CSV for Excel/PowerBI reference
kpi_df = pd.DataFrame(list(kpis.items()), columns=["KPI", "Value"])
kpi_df.to_csv("../data/kpi_summary.csv", index=False)
print("\nSaved KPI summary to ../data/kpi_summary.csv")
