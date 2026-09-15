"""
02_feature_engineering_risk_segmentation.py
--------------------------------------------
Builds derived features and assigns each loan/customer to a
Low / Medium / High risk segment using a transparent, rule-based
score built from Credit_Score, DTI, Previous_Defaults and Late_Payments.

Run: python 02_feature_engineering_risk_segmentation.py
"""

import pandas as pd
import numpy as np

df = pd.read_csv("../data/loan_data_clean.csv", parse_dates=["Application_Date", "Payment_Date"])

# ------------------------------------------------------------------
# Feature engineering
# ------------------------------------------------------------------

# 1. Age bands
df["Age_Group"] = pd.cut(
    df["Age"], bins=[17, 25, 35, 45, 55, 65, 100],
    labels=["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
)

# 2. Income bands
df["Income_Band"] = pd.cut(
    df["Income"], bins=[-1, 300000, 600000, 1000000, 2000000, np.inf],
    labels=["<3L", "3-6L", "6-10L", "10-20L", "20L+"]
)

# 3. Credit score bands (standard bureau-style bands)
df["Credit_Score_Band"] = pd.cut(
    df["Credit_Score"], bins=[299, 579, 669, 739, 799, 900],
    labels=["Poor (300-579)", "Fair (580-669)", "Good (670-739)", "Very Good (740-799)", "Excellent (800-900)"]
)

# 4. DTI bands
df["DTI_Band"] = pd.cut(
    df["DTI"], bins=[-1, 20, 36, 50, 1000],
    labels=["Low (<20%)", "Moderate (20-36%)", "High (36-50%)", "Very High (>50%)"]
)

# 5. Is delinquent / is default flags
df["Is_Delinquent"] = df["Loan_Status"].isin(["Delinquent", "Default", "Written Off"]).astype(int)
df["Is_Default"] = df["Loan_Status"].isin(["Default", "Written Off"]).astype(int)

# 6. Loan-to-Income ratio
df["Loan_to_Income_Ratio"] = (df["Loan_Amount"] / df["Income"].replace(0, np.nan)).round(2)

# 7. Outstanding % of loan
df["Outstanding_Pct"] = (df["Outstanding_Amount"] / df["Loan_Amount"].replace(0, np.nan) * 100).round(1)

# 8. Estimated Monthly Installment (simple EMI formula)
r = (df["Interest_Rate"] / 100) / 12
n = df["Loan_Term_Months"]
df["EMI_Estimate"] = np.where(
    r > 0,
    (df["Loan_Amount"] * r * (1 + r) ** n) / ((1 + r) ** n - 1),
    df["Loan_Amount"] / n
).round(0)

# 9. Application year / month (for trend analysis)
df["Application_Year"] = df["Application_Date"].dt.year
df["Application_Month"] = df["Application_Date"].dt.to_period("M").astype(str)

# 10. Overdue flag (30+ DPD)
df["Is_Overdue_30plus"] = (df["Days_Past_Due"] >= 30).astype(int)
df["Is_Overdue_90plus"] = (df["Days_Past_Due"] >= 90).astype(int)

# ------------------------------------------------------------------
# RISK SEGMENTATION LOGIC (rule-based, points system — fully transparent)
# ------------------------------------------------------------------
# Each factor contributes risk points; total points map to a segment.
# This mirrors how many banks build an early-warning / collections
# scorecard without a full statistical model.
#
#   Credit_Score < 580        -> +3 pts   | 580-669 -> +2 | 670-739 -> +1 | >=740 -> 0
#   DTI > 50%                 -> +3 pts   | 36-50%  -> +2 | 20-36%  -> +1 | <20%  -> 0
#   Previous_Defaults >= 2    -> +3 pts   | == 1    -> +2 | == 0    -> 0
#   Late_Payments >= 6        -> +2 pts   | 3-5     -> +1 | 0-2     -> 0
#
#   Total points 0-2   -> Low Risk
#   Total points 3-5   -> Medium Risk
#   Total points 6+    -> High Risk
# ------------------------------------------------------------------

def credit_score_points(score):
    if score < 580: return 3
    if score < 670: return 2
    if score < 740: return 1
    return 0

def dti_points(dti):
    if dti > 50: return 3
    if dti > 36: return 2
    if dti > 20: return 1
    return 0

def default_points(n):
    if n >= 2: return 3
    if n == 1: return 2
    return 0

def late_pay_points(n):
    if n >= 6: return 2
    if n >= 3: return 1
    return 0

df["Risk_Points"] = (
    df["Credit_Score"].apply(credit_score_points)
    + df["DTI"].apply(dti_points)
    + df["Previous_Defaults"].apply(default_points)
    + df["Late_Payments"].apply(late_pay_points)
)

def risk_segment(pts):
    if pts >= 6:
        return "High Risk"
    if pts >= 3:
        return "Medium Risk"
    return "Low Risk"

df["Risk_Segment"] = df["Risk_Points"].apply(risk_segment)

# ------------------------------------------------------------------
# Save engineered dataset
# ------------------------------------------------------------------
out_path = "../data/loan_data_features.csv"
df.to_csv(out_path, index=False)

print("Feature engineering complete.")
print(df["Risk_Segment"].value_counts())
print(f"Saved to {out_path}")
