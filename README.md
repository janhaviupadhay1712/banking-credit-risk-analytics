Bilkul. 👍 Neeche **complete README.md ek single copy-paste block** mein hai. Isko **poora select → copy → VS Code ke `README.md` mein paste** kar dena.

````markdown
# 🏦 Banking Credit Risk Analytics

An end-to-end **Credit Risk Analytics** project designed to analyze loan portfolio performance, identify high-risk customers, monitor defaults and delinquency, and provide actionable business insights using **Python, PostgreSQL, SQL, Excel, and Power BI**.

The project analyzes **21,527 cleaned loan records** and transforms raw loan data into analytical insights through data cleaning, feature engineering, SQL analysis, risk segmentation, and interactive Power BI dashboards.

---

## 🎯 Project Objective

The objective of this project is to help a banking or financial institution:

- Monitor loan portfolio performance
- Identify default and delinquency patterns
- Detect high-risk customers
- Analyze credit score and DTI risk
- Monitor outstanding loan exposure
- Compare risk across loan types and regions
- Support data-driven credit and collection decisions

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Data cleaning, feature engineering and EDA |
| Pandas / NumPy | Data processing |
| Matplotlib / Seaborn | Data visualization |
| PostgreSQL | Relational database |
| SQL | Credit risk analysis |
| Excel | KPI analysis and reporting |
| Power BI | Interactive dashboards |
| DAX | KPI calculations and risk metrics |
| Git / GitHub | Version control and portfolio |

---

## 🔄 Project Workflow

```text
Raw Loan Dataset
       ↓
Python Data Cleaning
       ↓
Feature Engineering
       ↓
Risk Segmentation
       ↓
PostgreSQL Database
       ↓
SQL Business Analysis
       ↓
Excel Reporting
       ↓
Power BI Dashboard
       ↓
Business Insights
````

---

## 📊 Dataset

The dataset contains loan-level information including:

* Customer ID
* Age
* Income
* Employment Type
* Credit Score
* DTI
* Loan Type
* Loan Amount
* Interest Rate
* Loan Term
* Region
* Branch
* Previous Defaults
* Late Payments
* Outstanding Amount
* Days Past Due
* Loan Status
* Application Date
* Payment Date

### Dataset Size

* Raw records: **21,850**
* Cleaned records: **21,527**
* Loan portfolio analyzed: **21K+ records**

The dataset contains realistic data-quality challenges such as missing values, duplicate records, inconsistent categories, mixed date formats, and outliers.

---

# 🐍 Python Analytics

Python is used for data cleaning, feature engineering, exploratory analysis, and KPI generation.

### 1. Data Cleaning

File:

```text
python/01_data_cleaning.py
```

Tasks performed:

* Handle missing values
* Remove duplicate records
* Standardize categorical values
* Convert dates
* Handle outliers
* Generate cleaned dataset

### 2. Feature Engineering & Risk Segmentation

File:

```text
python/02_feature_engineering_risk_segmentation.py
```

Additional analytical features include:

* Risk Segment
* Credit Score Band
* DTI Band
* Income Band
* Age Band
* EMI Estimate
* Loan-to-Income Ratio

### 3. Exploratory Data Analysis

File:

```text
python/03_eda_visualizations.py
```

Visualizations include:

* Loan status distribution
* Default rate by loan type
* Default rate by region
* Monthly default trends
* Credit score by risk segment
* DTI by risk segment
* Outstanding amount by region
* Days past due distribution
* Branch-level risk
* Correlation analysis

---

# 🧮 Risk Segmentation

A transparent rule-based risk scoring methodology is used to categorize customers.

| Risk Factor           | Points |
| --------------------- | -----: |
| Credit Score < 580    |     +3 |
| Credit Score 580–669  |     +2 |
| Credit Score 670–739  |     +1 |
| Credit Score ≥ 740    |      0 |
| DTI > 50%             |     +3 |
| DTI 36–50%            |     +2 |
| DTI 20–36%            |     +1 |
| Previous Defaults ≥ 2 |     +3 |
| Previous Defaults = 1 |     +2 |
| Late Payments ≥ 6     |     +2 |
| Late Payments 3–5     |     +1 |

### Risk Categories

```text
0–2 points → Low Risk
3–5 points → Medium Risk
6+ points  → High Risk
```

This methodology is used to identify customers who may require additional monitoring or collection attention.

---

# 🗄️ PostgreSQL & SQL Analysis

The cleaned loan data is stored in PostgreSQL using relational tables such as:

* `customers`
* `loans`

SQL scripts:

```text
sql/
├── 01_schema.sql
└── 02_queries.sql
```

The project contains **25 analytical SQL queries** covering:

* Loan portfolio analysis
* Customer analysis
* Default rate
* Delinquency
* Risk segmentation
* Regional risk
* Loan-type performance
* Outstanding exposure
* Days Past Due analysis
* Customer ranking
* Trend analysis
* Branch-level risk

---

# 📈 Power BI Dashboard

The project contains a **2-page interactive Power BI dashboard**.

## Page 1 — Executive Dashboard

### KPIs

* Total Loans
* Total Customers
* Total Disbursed
* Total Outstanding
* Default Rate
* Average Credit Score

### Visualizations

* Default Rate by Loan Type
* Loan Status Distribution
* Monthly Default Rate Trend
* Default Rate by Region

### Interactive Filters

* Loan Type
* Region
* Loan Status

---

## Page 2 — Risk & Collections

### KPIs

* High Risk Customers
* Customers 90+ DPD
* Average DTI
* Average Credit Score

### Visualizations

* Risk Segment Distribution
* Outstanding Amount by Loan Status
* Credit Score vs DTI Risk Analysis
* Top 10 Customers by Outstanding Exposure

The dashboard supports interactive cross-filtering between KPIs, charts, and slicers.

---

# 📊 Portfolio KPIs

The analyzed portfolio contains the following key metrics:

| KPI                         |   Value |
| --------------------------- | ------: |
| Total Loans                 |  21,527 |
| Total Loan Amount Disbursed | ₹24.95B |
| Total Outstanding Amount    | ₹10.91B |
| Overall Default Rate        |   5.32% |
| Overall Delinquency Rate    |  17.08% |
| Average Credit Score        |     651 |
| Average DTI                 |  35.08% |
| High-Risk Customers         |   4,128 |
| NPA Ratio                   |   8.75% |

---

# 💼 Business Value

The analysis can support banking teams in several areas.

### Credit Risk

Identify customers with combinations of:

* Low credit scores
* High DTI
* Previous defaults
* Frequent late payments

### Collections

Use Days Past Due and outstanding exposure to prioritize collection activities.

### Portfolio Management

Compare loan performance across:

* Loan types
* Regions
* Branches
* Customer risk segments

### Early Risk Detection

High-risk customers can be prioritized for proactive monitoring before accounts become severely delinquent.

---

# 📁 Project Structure

```text
banking-credit-risk-analytics/
│
├── data/
│   ├── loan_data_raw.csv
│   ├── loan_data_clean.csv
│   ├── loan_data_features.csv
│   ├── kpi_summary.csv
│   └── generate_data.py
│
├── python/
│   ├── 01_data_cleaning.py
│   ├── 02_feature_engineering_risk_segmentation.py
│   ├── 03_eda_visualizations.py
│   ├── 04_kpi_business_insights.py
│   ├── 05_optional_ml_model.py
│   └── charts/
│
├── sql/
│   ├── 01_schema.sql
│   └── 02_queries.sql
│
├── excel/
│   ├── build_excel.py
│   └── Credit_Risk_Analysis.xlsx
│
├── powerbi/
│   ├── DAX_measures.md
│   └── dashboard_design.md
│
├── docs/
│   ├── business_recommendations.md
│   ├── interview_questions_project.md
│   ├── interview_questions_technical.md
│   ├── resume_bullets.md
│   ├── linkedin_description.md
│   └── limitations_and_ethics.md
│
├── .gitignore
└── README.md
```

---

# 🚀 How to Run

## 1. Python Environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn openpyxl
```

Run the Python pipeline:

```bash
python python/01_data_cleaning.py
python python/02_feature_engineering_risk_segmentation.py
python python/03_eda_visualizations.py
python python/04_kpi_business_insights.py
```

### Optional Machine Learning

The ML component is optional:

```bash
python python/05_optional_ml_model.py
```

---

# 🗄️ PostgreSQL Setup

Create the PostgreSQL database and execute:

```text
sql/01_schema.sql
```

Load the cleaned data into the database.

Then execute:

```text
sql/02_queries.sql
```

The SQL scripts perform the main analytical queries used in the project.

---

# 📊 Power BI Setup

Open the Power BI project in Power BI Desktop.

The dashboard can be connected to the PostgreSQL database or built using:

```text
data/loan_data_features.csv
```

DAX measures are documented in:

```text
powerbi/DAX_measures.md
```

Dashboard layout and visual configuration are documented in:

```text
powerbi/dashboard_design.md
```

---

# 📑 Excel Reporting

The project also includes an Excel-based reporting workbook:

```text
excel/Credit_Risk_Analysis.xlsx
```

The workbook contains reporting and analysis sheets for:

* KPI Dashboard
* Risk Analysis
* Overdue Tracking
* Clean Data

---

# 🤖 Optional Machine Learning

An optional machine learning component is included using:

* Logistic Regression
* Random Forest

The ML component can be used to experiment with loan-default prediction based on selected customer and loan features.

The core project does **not depend on the ML component** and can be completed using the Python, PostgreSQL, SQL, Excel, and Power BI workflow.

---

# ⚠️ Limitations

* The dataset is synthetic and intended for portfolio and learning purposes.
* The risk scoring methodology is rule-based and should not be treated as a production credit decisioning model.
* Real-world banking applications require validated historical data, regulatory controls, model validation, fairness testing, and explainability.
* Machine learning predictions should be validated before being used for real credit decisions.

---

# 🔮 Future Improvements

Possible future enhancements include:

* Real-time loan monitoring
* Automated risk alerts
* Advanced ML-based default prediction
* Model explainability using SHAP
* Automated Power BI refresh
* Customer-level risk alerts
* Collection prioritization model
* Cloud deployment
* Role-based analytics dashboard

---

# 👩‍💻 Author

**Janhavi**

GitHub:
[https://github.com/janhaviupadhay1712](https://github.com/janhaviupadhay1712)

---

⭐ If you found this project useful, consider giving the repository a star.

````
