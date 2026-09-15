"""
03_eda_visualizations.py
-------------------------
Exploratory Data Analysis: 15 meaningful visualizations covering
default/delinquency trends, risk by segment, income, credit score,
DTI, employment, region and portfolio composition.

Saves each chart as a PNG into ../python/charts/

Run: python 03_eda_visualizations.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid", palette="Set2")
plt.rcParams["figure.figsize"] = (10, 6)
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.titleweight"] = "bold"

OUT_DIR = "charts"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv("../data/loan_data_features.csv", parse_dates=["Application_Date", "Payment_Date"])

def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, name), dpi=150)
    plt.close(fig)
    print(f"Saved {name}")

# 1. Loan Status distribution
fig, ax = plt.subplots()
order = df["Loan_Status"].value_counts().index
sns.countplot(data=df, x="Loan_Status", order=order, ax=ax)
ax.set_title("Loan Portfolio by Status")
ax.set_xlabel("")
save(fig, "01_loan_status_distribution.png")

# 2. Default rate by Loan Type
fig, ax = plt.subplots()
default_by_type = df.groupby("Loan_Type")["Is_Default"].mean().sort_values(ascending=False) * 100
sns.barplot(x=default_by_type.values, y=default_by_type.index, ax=ax)
ax.set_title("Default Rate (%) by Loan Type")
ax.set_xlabel("Default Rate (%)")
save(fig, "02_default_rate_by_loan_type.png")

# 3. Default rate by Region
fig, ax = plt.subplots()
default_by_region = df.groupby("Region")["Is_Default"].mean().sort_values(ascending=False) * 100
sns.barplot(x=default_by_region.index, y=default_by_region.values, ax=ax)
ax.set_title("Default Rate (%) by Region")
ax.set_ylabel("Default Rate (%)")
save(fig, "03_default_rate_by_region.png")

# 4. Credit Score distribution by Risk Segment
fig, ax = plt.subplots()
sns.boxplot(data=df, x="Risk_Segment", y="Credit_Score",
            order=["Low Risk", "Medium Risk", "High Risk"], ax=ax)
ax.set_title("Credit Score Distribution by Risk Segment")
save(fig, "04_credit_score_by_risk_segment.png")

# 5. DTI distribution by Risk Segment
fig, ax = plt.subplots()
sns.boxplot(data=df, x="Risk_Segment", y="DTI",
            order=["Low Risk", "Medium Risk", "High Risk"], ax=ax)
ax.set_title("DTI (%) Distribution by Risk Segment")
save(fig, "05_dti_by_risk_segment.png")

# 6. Risk Segment portfolio share (pie)
fig, ax = plt.subplots()
seg_counts = df["Risk_Segment"].value_counts()
ax.pie(seg_counts.values, labels=seg_counts.index, autopct="%1.1f%%", startangle=90,
       colors=sns.color_palette("Set2"))
ax.set_title("Portfolio Share by Risk Segment")
save(fig, "06_risk_segment_share.png")

# 7. Monthly application trend
fig, ax = plt.subplots(figsize=(12, 6))
monthly = df.groupby("Application_Month").size()
monthly.plot(ax=ax, marker="o")
ax.set_title("Monthly Loan Application Volume")
ax.set_ylabel("Number of Loans")
ax.set_xlabel("Month")
plt.setp(ax.get_xticklabels(), rotation=90, fontsize=7)
save(fig, "07_monthly_application_trend.png")

# 8. Monthly default rate trend
fig, ax = plt.subplots(figsize=(12, 6))
monthly_default = df.groupby("Application_Month")["Is_Default"].mean() * 100
monthly_default.plot(ax=ax, marker="o", color="firebrick")
ax.set_title("Monthly Default Rate (%) Trend")
ax.set_ylabel("Default Rate (%)")
plt.setp(ax.get_xticklabels(), rotation=90, fontsize=7)
save(fig, "08_monthly_default_rate_trend.png")

# 9. Income vs Credit Score (scatter, colored by risk)
fig, ax = plt.subplots()
sample = df.sample(min(3000, len(df)), random_state=1)
sns.scatterplot(data=sample, x="Income", y="Credit_Score", hue="Risk_Segment",
                 alpha=0.5, ax=ax, hue_order=["Low Risk", "Medium Risk", "High Risk"])
ax.set_xlim(0, sample["Income"].quantile(0.98))
ax.set_title("Income vs Credit Score by Risk Segment")
save(fig, "09_income_vs_credit_score.png")

# 10. Employment Type vs Default Rate
fig, ax = plt.subplots()
emp_default = df.groupby("Employment_Type")["Is_Default"].mean().sort_values(ascending=False) * 100
sns.barplot(x=emp_default.values, y=emp_default.index, ax=ax)
ax.set_title("Default Rate (%) by Employment Type")
ax.set_xlabel("Default Rate (%)")
save(fig, "10_default_rate_by_employment.png")

# 11. Outstanding Amount by Region (bar)
fig, ax = plt.subplots()
outstanding_region = df.groupby("Region")["Outstanding_Amount"].sum().sort_values(ascending=False) / 1e7
sns.barplot(x=outstanding_region.index, y=outstanding_region.values, ax=ax)
ax.set_title("Total Outstanding Amount by Region (₹ Crore)")
ax.set_ylabel("Outstanding (₹ Cr)")
save(fig, "11_outstanding_by_region.png")

# 12. Credit Score Band vs Risk Segment (stacked heatmap-like crosstab)
fig, ax = plt.subplots()
ctab = pd.crosstab(df["Credit_Score_Band"], df["Risk_Segment"], normalize="index") * 100
ctab = ctab[["Low Risk", "Medium Risk", "High Risk"]]
ctab.plot(kind="bar", stacked=True, ax=ax, colormap="RdYlGn_r")
ax.set_title("Risk Segment Composition by Credit Score Band")
ax.set_ylabel("% of Customers")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
save(fig, "12_risk_composition_by_score_band.png")

# 13. Days Past Due distribution (delinquent/default loans only)
fig, ax = plt.subplots()
overdue = df[df["Days_Past_Due"] > 0]
sns.histplot(overdue["Days_Past_Due"], bins=40, kde=True, ax=ax, color="darkorange")
ax.set_title("Days Past Due Distribution (Overdue Loans)")
save(fig, "13_days_past_due_distribution.png")

# 14. Loan Amount distribution by Loan Type
fig, ax = plt.subplots()
sns.boxplot(data=df, x="Loan_Type", y="Loan_Amount", ax=ax)
ax.set_title("Loan Amount Distribution by Loan Type")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
save(fig, "14_loan_amount_by_type.png")

# 15. Top 10 branches by default rate (min 50 loans)
fig, ax = plt.subplots()
branch_stats = df.groupby("Branch").agg(loans=("Customer_ID", "count"), default_rate=("Is_Default", "mean"))
branch_stats = branch_stats[branch_stats["loans"] >= 50].sort_values("default_rate", ascending=False).head(10)
sns.barplot(x=branch_stats["default_rate"].values * 100, y=branch_stats.index, ax=ax)
ax.set_title("Top 10 Branches by Default Rate (min. 50 loans)")
ax.set_xlabel("Default Rate (%)")
save(fig, "15_top_branches_default_rate.png")

# 16. Correlation heatmap of key numeric risk drivers (bonus chart)
fig, ax = plt.subplots(figsize=(9, 7))
numeric_cols = ["Age", "Income", "Credit_Score", "DTI", "Previous_Defaults",
                 "Late_Payments", "Days_Past_Due", "Loan_to_Income_Ratio", "Is_Default"]
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
ax.set_title("Correlation Heatmap: Key Risk Drivers")
save(fig, "16_correlation_heatmap.png")

print("\nAll charts saved to ./charts/")
