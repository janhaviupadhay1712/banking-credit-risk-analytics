"""
generate_data.py
-----------------
Generates a realistic, intentionally messy Banking Credit Risk dataset
(20,000+ records) for the Credit Risk Analytics portfolio project.

Messiness injected on purpose (for the cleaning demo):
- Missing values in Income, Credit_Score, DTI, Employment_Type, Region
- Duplicate Customer_ID rows
- Outliers in Income, Loan_Amount, Age
- Inconsistent category casing/spacing ("self employed", "Self-Employed", "SELF EMPLOYED")
- Mixed date formats
- Negative / impossible values (negative DTI, Age=150)
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

SEED = 42
np.random.seed(SEED)
random.seed(SEED)

N = 21500  # will drop some in cleaning to land >20,000 clean rows

# ---------------------------------------------------------------
# Reference categories
# ---------------------------------------------------------------
employment_types = ["Salaried", "Self-Employed", "Business Owner", "Unemployed", "Retired"]
loan_types = ["Personal Loan", "Home Loan", "Auto Loan", "Education Loan", "Credit Card", "Business Loan"]
regions = ["North", "South", "East", "West", "Central"]
loan_status_options = ["Active", "Closed", "Default", "Delinquent", "Written Off"]

region_branches = {
    "North": ["Delhi", "Chandigarh", "Lucknow"],
    "South": ["Bengaluru", "Chennai", "Hyderabad"],
    "East": ["Kolkata", "Patna", "Bhubaneswar"],
    "West": ["Mumbai", "Pune", "Ahmedabad"],
    "Central": ["Bhopal", "Nagpur", "Raipur"],
}

# ---------------------------------------------------------------
# Base fields
# ---------------------------------------------------------------
customer_id = np.arange(100001, 100001 + N)

age = np.random.normal(40, 12, N).round().astype(int)
age = np.clip(age, 18, 75)

income = np.random.lognormal(mean=10.9, sigma=0.55, size=N).round(-2)  # skewed income

employment_type = np.random.choice(
    employment_types, N, p=[0.50, 0.20, 0.12, 0.08, 0.10]
)

credit_score = np.random.normal(650, 90, N).round().astype(int)
credit_score = np.clip(credit_score, 300, 900)

dti = np.random.normal(35, 15, N).round(1)  # debt-to-income %

loan_type = np.random.choice(
    loan_types, N, p=[0.28, 0.18, 0.20, 0.12, 0.14, 0.08]
)

base_loan_amount = {
    "Personal Loan": 400000, "Home Loan": 3500000, "Auto Loan": 800000,
    "Education Loan": 900000, "Credit Card": 150000, "Business Loan": 2000000,
}
loan_amount = np.array([
    max(20000, np.random.normal(base_loan_amount[lt], base_loan_amount[lt] * 0.35))
    for lt in loan_type
]).round(-3)

interest_rate = np.round(np.random.normal(11.5, 3.2, N), 2)
interest_rate = np.clip(interest_rate, 6.0, 24.0)

loan_term_options = [12, 24, 36, 48, 60, 84, 120, 180, 240]
loan_term = np.random.choice(loan_term_options, N)

region = np.random.choice(regions, N)
branch = [random.choice(region_branches[r]) for r in region]

previous_defaults = np.random.choice([0, 1, 2, 3], N, p=[0.72, 0.16, 0.08, 0.04])
late_payments = np.random.poisson(1.4, N)
late_payments = np.clip(late_payments, 0, 24)

# ---------------------------------------------------------------
# Risk-correlated Days Past Due / Loan Status / Outstanding Amount
# ---------------------------------------------------------------
risk_score = (
    (900 - credit_score) / 600 * 0.35
    + dti.clip(0, 100) / 100 * 0.30
    + previous_defaults / 3 * 0.20
    + late_payments / 24 * 0.15
)
risk_score = np.clip(risk_score, 0, 1)

days_past_due = np.where(
    np.random.rand(N) < risk_score * 0.6,
    np.random.exponential(45, N).astype(int),
    0
)
days_past_due = np.clip(days_past_due, 0, 720)

loan_status = []
for dpd, rs in zip(days_past_due, risk_score):
    if dpd == 0:
        loan_status.append(np.random.choice(["Active", "Closed"], p=[0.75, 0.25]))
    elif dpd <= 30:
        loan_status.append("Delinquent")
    elif dpd <= 90:
        loan_status.append(np.random.choice(["Delinquent", "Default"], p=[0.5, 0.5]))
    else:
        loan_status.append(np.random.choice(["Default", "Written Off"], p=[0.6, 0.4]))
loan_status = np.array(loan_status)

pct_outstanding = np.where(
    loan_status == "Closed", 0,
    np.where(np.isin(loan_status, ["Default", "Written Off"]),
             np.random.uniform(0.4, 1.0, N),
             np.random.uniform(0.1, 0.95, N))
)
outstanding_amount = (loan_amount * pct_outstanding).round(-2)

# ---------------------------------------------------------------
# Dates
# ---------------------------------------------------------------
start_date = datetime(2021, 1, 1)
end_date = datetime(2024, 12, 31)
app_dates = [start_date + timedelta(days=random.randint(0, (end_date - start_date).days)) for _ in range(N)]

def payment_date_for(app_date, status):
    if status == "Closed":
        return app_date + timedelta(days=random.randint(90, 900))
    if status in ("Active", "Delinquent"):
        # last payment recent-ish
        return app_date + timedelta(days=random.randint(30, 800))
    return app_date + timedelta(days=random.randint(60, 700))

payment_dates = [payment_date_for(d, s) for d, s in zip(app_dates, loan_status)]

df = pd.DataFrame({
    "Customer_ID": customer_id,
    "Age": age,
    "Income": income,
    "Employment_Type": employment_type,
    "Credit_Score": credit_score,
    "DTI": dti,
    "Loan_Type": loan_type,
    "Loan_Amount": loan_amount,
    "Interest_Rate": interest_rate,
    "Loan_Term_Months": loan_term,
    "Region": region,
    "Branch": branch,
    "Previous_Defaults": previous_defaults,
    "Late_Payments": late_payments,
    "Outstanding_Amount": outstanding_amount,
    "Days_Past_Due": days_past_due,
    "Loan_Status": loan_status,
    "Application_Date": app_dates,
    "Payment_Date": payment_dates,
})

# ---------------------------------------------------------------
# INTENTIONAL MESSINESS
# ---------------------------------------------------------------

# 1) Missing values (MCAR-ish, realistic %)
for col, frac in [("Income", 0.035), ("Credit_Score", 0.02), ("DTI", 0.025),
                   ("Employment_Type", 0.015), ("Region", 0.01), ("Interest_Rate", 0.01)]:
    idx = df.sample(frac=frac, random_state=np.random.randint(0, 10000)).index
    df.loc[idx, col] = np.nan

# 2) Inconsistent categorical text
messy_employment_map_idx = df.sample(frac=0.06, random_state=1).index
def messify_employment(val):
    choices = ["self employed", "Self-Employed", "SELF EMPLOYED", " Self Employed ", "self-employed"]
    return random.choice(choices) if val == "Self-Employed" else val
df.loc[messy_employment_map_idx, "Employment_Type"] = df.loc[messy_employment_map_idx, "Employment_Type"].apply(messify_employment)

messy_region_idx = df.sample(frac=0.04, random_state=2).index
def messify_region(val):
    if pd.isna(val):
        return val
    choices = {"North": ["north", "NORTH", " North"], "South": ["south", "SOUTH "],
               "East": ["east", "EAST"], "West": ["west", " West"], "Central": ["central", "CENTRAL"]}
    return random.choice(choices.get(val, [val]))
df.loc[messy_region_idx, "Region"] = df.loc[messy_region_idx, "Region"].apply(messify_region)

messy_status_idx = df.sample(frac=0.03, random_state=3).index
def messify_status(val):
    choices = {"Default": ["default", "DEFAULT", "Defaulted"], "Active": ["active", "ACTIVE"],
               "Closed": ["closed", "CLOSED"], "Delinquent": ["delinquent", "DELINQUENT"],
               "Written Off": ["written off", "WRITTEN-OFF", "Write-Off"]}
    return random.choice(choices.get(val, [val]))
df.loc[messy_status_idx, "Loan_Status"] = df.loc[messy_status_idx, "Loan_Status"].apply(messify_status)

# 3) Outliers
outlier_idx = df.sample(frac=0.005, random_state=4).index
df.loc[outlier_idx, "Income"] = df.loc[outlier_idx, "Income"] * np.random.uniform(8, 15)

outlier_age_idx = df.sample(frac=0.002, random_state=5).index
df.loc[outlier_age_idx, "Age"] = np.random.choice([1, 150, 999, -5], size=len(outlier_age_idx))

outlier_loan_idx = df.sample(frac=0.003, random_state=6).index
df.loc[outlier_loan_idx, "Loan_Amount"] = df.loc[outlier_loan_idx, "Loan_Amount"] * np.random.uniform(6, 10)

# 4) Impossible / negative values
neg_dti_idx = df.sample(frac=0.004, random_state=7).index
df.loc[neg_dti_idx, "DTI"] = -df.loc[neg_dti_idx, "DTI"]

neg_income_idx = df.sample(frac=0.002, random_state=8).index
df.loc[neg_income_idx, "Income"] = -1 * np.random.uniform(1000, 5000, len(neg_income_idx))

# 5) Duplicates - duplicate ~350 full rows (same Customer_ID appears twice)
dup_rows = df.sample(n=350, random_state=9)
df = pd.concat([df, dup_rows], ignore_index=True)

# 6) Mixed date string formats (store Application_Date as mixed-format strings for a subset)
def mixed_format(d):
    fmt = random.choice(["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d-%b-%Y"])
    return d.strftime(fmt)

mixed_idx = df.sample(frac=0.05, random_state=10).index
df["Application_Date"] = df["Application_Date"].astype(object)
df.loc[mixed_idx, "Application_Date"] = df.loc[mixed_idx, "Application_Date"].apply(mixed_format)
df.loc[~df.index.isin(mixed_idx), "Application_Date"] = df.loc[~df.index.isin(mixed_idx), "Application_Date"].apply(lambda d: d.strftime("%Y-%m-%d") if not isinstance(d, str) else d)

df["Payment_Date"] = df["Payment_Date"].apply(lambda d: d.strftime("%Y-%m-%d") if not isinstance(d, str) else d)

# Shuffle rows
df = df.sample(frac=1, random_state=11).reset_index(drop=True)

out_path = "loan_data_raw.csv"
df.to_csv(out_path, index=False)
print(f"Saved {len(df)} rows to {out_path}")
print(df.isna().sum())
