"""
01_data_cleaning.py
--------------------
Cleans the raw loan dataset: fixes inconsistent categories, mixed date
formats, duplicates, missing values, and outliers. Saves a clean CSV
used by every downstream step (EDA, SQL load, Excel, Power BI).

Run: python 01_data_cleaning.py
"""

import pandas as pd
import numpy as np

RAW_PATH = "../data/loan_data_raw.csv"
CLEAN_PATH = "../data/loan_data_clean.csv"

df = pd.read_csv(RAW_PATH)
print(f"Raw shape: {df.shape}")

# ------------------------------------------------------------------
# 1. Remove duplicate rows (full-row duplicates from same Customer_ID)
# ------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates(subset=["Customer_ID", "Loan_Type", "Loan_Amount", "Application_Date"], keep="first")
print(f"Removed {before - len(df)} duplicate rows")

# ------------------------------------------------------------------
# 2. Standardize categorical text (strip, title-case, map variants)
# ------------------------------------------------------------------
def clean_text(x):
    if pd.isna(x):
        return x
    return str(x).strip().title()

df["Employment_Type"] = df["Employment_Type"].apply(clean_text)
employment_map = {
    "Self Employed": "Self-Employed",
    "Self-Employed": "Self-Employed",
}
df["Employment_Type"] = df["Employment_Type"].replace(employment_map)

df["Region"] = df["Region"].apply(clean_text)
df["Loan_Status"] = df["Loan_Status"].apply(clean_text)
status_map = {"Defaulted": "Default", "Write-Off": "Written Off", "Written-Off": "Written Off"}
df["Loan_Status"] = df["Loan_Status"].replace(status_map)

# ------------------------------------------------------------------
# 3. Parse mixed-format dates
# ------------------------------------------------------------------
def parse_mixed_date(val):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y", "%d-%b-%Y"):
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            continue
    return pd.NaT

df["Application_Date"] = df["Application_Date"].apply(parse_mixed_date)
df["Payment_Date"] = pd.to_datetime(df["Payment_Date"], errors="coerce")

# ------------------------------------------------------------------
# 4. Fix impossible / negative values
# ------------------------------------------------------------------
df.loc[(df["Age"] < 18) | (df["Age"] > 90), "Age"] = np.nan
df.loc[df["Income"] < 0, "Income"] = np.nan
df.loc[df["DTI"] < 0, "DTI"] = df.loc[df["DTI"] < 0, "DTI"].abs()
df.loc[df["DTI"] > 150, "DTI"] = np.nan  # unrealistic DTI

# ------------------------------------------------------------------
# 5. Cap outliers using IQR method (Income, Loan_Amount)
# ------------------------------------------------------------------
def cap_outliers_iqr(series, k=3.0):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return series.clip(lower=max(lower, 0), upper=upper)

df["Income"] = cap_outliers_iqr(df["Income"])
df["Loan_Amount"] = cap_outliers_iqr(df["Loan_Amount"])

# ------------------------------------------------------------------
# 6. Impute missing values
#    - Numeric: median (robust to skew), grouped by Loan_Type where sensible
#    - Categorical: mode
# ------------------------------------------------------------------
df["Income"] = df.groupby("Employment_Type")["Income"].transform(lambda s: s.fillna(s.median()))
df["Income"] = df["Income"].fillna(df["Income"].median())

df["Credit_Score"] = df["Credit_Score"].fillna(df["Credit_Score"].median())
df["DTI"] = df["DTI"].fillna(df["DTI"].median())
df["Interest_Rate"] = df["Interest_Rate"].fillna(df["Interest_Rate"].median())
df["Age"] = df["Age"].fillna(df["Age"].median())

df["Employment_Type"] = df["Employment_Type"].fillna(df["Employment_Type"].mode()[0])
df["Region"] = df["Region"].fillna(df["Region"].mode()[0])

# ------------------------------------------------------------------
# 7. Drop rows where dates could not be parsed / core keys missing
# ------------------------------------------------------------------
df = df.dropna(subset=["Application_Date", "Loan_Status"])

# ------------------------------------------------------------------
# 8. Correct data types
# ------------------------------------------------------------------
df["Age"] = df["Age"].astype(int)
df["Credit_Score"] = df["Credit_Score"].astype(int)
df["Customer_ID"] = df["Customer_ID"].astype(int)

# ------------------------------------------------------------------
# 9. Final sanity filters
# ------------------------------------------------------------------
df = df[(df["Credit_Score"] >= 300) & (df["Credit_Score"] <= 900)]
df = df[df["Loan_Amount"] > 0]

df = df.reset_index(drop=True)
print(f"Clean shape: {df.shape}")
print(df.isna().sum().sum(), "remaining missing values")

df.to_csv(CLEAN_PATH, index=False)
print(f"Saved cleaned dataset to {CLEAN_PATH}")
