"""
05_optional_ml_model.py  (OPTIONAL / SECONDARY COMPONENT)
------------------------------------------------------------
A simple, secondary ML model to predict loan default using Logistic
Regression and Random Forest. This is NOT the focus of the project —
SQL / Python-EDA / Excel / Power BI are the primary deliverables.
This script exists to show baseline ML capability only.

Run: python 05_optional_ml_model.py
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (classification_report, roc_auc_score,
                              confusion_matrix, RocCurveDisplay)
import matplotlib.pyplot as plt

df = pd.read_csv("../data/loan_data_features.csv")

features_num = ["Age", "Income", "Credit_Score", "DTI", "Previous_Defaults",
                 "Late_Payments", "Loan_Amount", "Interest_Rate", "Loan_to_Income_Ratio"]
features_cat = ["Employment_Type", "Loan_Type", "Region"]
target = "Is_Default"

X = df[features_num + features_cat]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

preprocess = ColumnTransformer([
    ("num", StandardScaler(), features_num),
    ("cat", OneHotEncoder(handle_unknown="ignore"), features_cat),
])

# ---- Logistic Regression ----
log_reg = Pipeline([
    ("prep", preprocess),
    ("model", LogisticRegression(max_iter=1000, class_weight="balanced"))
])
log_reg.fit(X_train, y_train)
log_pred = log_reg.predict(X_test)
log_proba = log_reg.predict_proba(X_test)[:, 1]

print("=" * 60)
print("LOGISTIC REGRESSION RESULTS")
print("=" * 60)
print(classification_report(y_test, log_pred))
print(f"ROC-AUC: {roc_auc_score(y_test, log_proba):.3f}")

# ---- Random Forest ----
rf = Pipeline([
    ("prep", preprocess),
    ("model", RandomForestClassifier(n_estimators=300, max_depth=8,
                                      class_weight="balanced", random_state=42))
])
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_proba = rf.predict_proba(X_test)[:, 1]

print("\n" + "=" * 60)
print("RANDOM FOREST RESULTS")
print("=" * 60)
print(classification_report(y_test, rf_pred))
print(f"ROC-AUC: {roc_auc_score(y_test, rf_proba):.3f}")

# ---- Feature importance (Random Forest) ----
ohe_cols = rf.named_steps["prep"].named_transformers_["cat"].get_feature_names_out(features_cat)
all_features = features_num + list(ohe_cols)
importances = rf.named_steps["model"].feature_importances_
feat_imp = pd.Series(importances, index=all_features).sort_values(ascending=False).head(15)

fig, ax = plt.subplots(figsize=(9, 7))
feat_imp.sort_values().plot(kind="barh", ax=ax, color="steelblue")
ax.set_title("Top 15 Feature Importances — Random Forest Default Model")
fig.tight_layout()
fig.savefig("charts/17_ml_feature_importance.png", dpi=150)
print("\nSaved feature importance chart to charts/17_ml_feature_importance.png")

# ---- ROC curve comparison ----
fig, ax = plt.subplots(figsize=(7, 6))
RocCurveDisplay.from_predictions(y_test, log_proba, name="Logistic Regression", ax=ax)
RocCurveDisplay.from_predictions(y_test, rf_proba, name="Random Forest", ax=ax)
ax.set_title("ROC Curve — Default Prediction Models")
fig.tight_layout()
fig.savefig("charts/18_ml_roc_curve.png", dpi=150)
print("Saved ROC curve chart to charts/18_ml_roc_curve.png")

print("\nNote: ML is a secondary/optional component of this project.")
print("Primary deliverables are SQL, Python EDA, Excel and Power BI.")
