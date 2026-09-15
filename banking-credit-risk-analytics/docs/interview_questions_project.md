# 10 Project-Specific Interview Questions & Answers

**1. Walk me through your project end-to-end.**
I generated a realistic, intentionally messy 21,850-record loan dataset,
cleaned it in Pandas (missing values, duplicates, inconsistent categories,
mixed dates, outliers), engineered features like Loan-to-Income ratio and
credit score bands, and built a transparent rule-based Low/Medium/High risk
scorecard. I then analyzed the cleaned data three ways: 16+ Python
visualizations and KPIs, 25 SQL queries (joins, CTEs, window functions), and
a 3-page Power BI dashboard with DAX measures — plus a formula-driven Excel
workbook for stakeholders who live in spreadsheets. I closed with a small,
secondary ML model and a set of data-backed business recommendations.

**2. Why did you build your own risk segmentation instead of using a credit bureau score directly?**
A bureau score alone doesn't capture behavior specific to *this* loan book —
prior defaults and recent late payments matter a lot for early-warning
purposes. I built an additive points system across four factors (Credit
Score, DTI, Previous Defaults, Late Payments) so each contribution is fully
explainable to a non-technical stakeholder — important in banking, where
risk decisions often need to be justified to auditors/regulators, unlike a
black-box ML score.

**3. How did you validate that your risk segments actually reflect real risk?**
I checked that default/delinquency rate increases monotonically from Low →
Medium → High risk segments, and cross-validated with a SQL credit-score
decile analysis (`NTILE(10)`) showing default rate falling as score rises.
I also computed the correlation between Credit Score / DTI and `Is_Default`
directly — both point the expected direction, confirming the scorecard
logic is behaving sensibly rather than being arbitrary.

**4. Your dataset is synthetic — how do you know your findings are meaningful?**
They're meaningful as a *methodology demonstration*, not as real business
truth. I built risk correlations into the generator on purpose (e.g., high
DTI/low credit score customers get a higher chance of being flagged
delinquent), so the patterns the analysis surfaces are the same shape a
real portfolio would show, but the specific numbers (5.3% default rate,
etc.) are illustrative, not a real bank's actual figures. I say this
explicitly in the README and limitations doc rather than overselling it.

**5. What was the hardest part of the data cleaning process?**
Deciding *how* to impute missing Income without distorting the risk
analysis. A single global median would have masked the real difference
between, say, Salaried and Unemployed applicants. I used
`groupby('Employment_Type').transform()` to impute within each employment
group instead — a small design choice, but it meaningfully changes
downstream default-rate-by-income-band results.

**6. Why did you cap outliers instead of removing them?**
Removing rows loses real customers — extreme values in Income/Loan_Amount
in a retail bank are outliers but not necessarily invalid. I used the IQR
method with a conservative multiplier (k=3) to cap rather than delete,
keeping every customer in the analysis while preventing a handful of
extreme values from skewing averages and chart scales.

**7. How would this project change with a real production dataset?**
I'd expect: (a) far more nuanced missingness patterns requiring domain input
from risk/collections teams rather than a blanket median-impute, (b)
regulatory constraints on which features can be used in a scorecard (e.g.,
fair lending rules), (c) a proper train/validation/out-of-time test split
for any ML component instead of a single random split, and (d) engagement
with actual bank stakeholders to define what "high risk" should trigger
operationally (collections call, credit limit freeze, etc.).

**8. Why is SQL, Python, Excel and Power BI the priority here, not the ML model?**
Because that's what an entry-level Data Analyst role actually does day to
day — reporting, dashboards, ad hoc SQL, and stakeholder-facing Excel/Power
BI work, not building production ML models (that's typically a Data
Scientist / ML Engineer's remit). I built the ML piece to show I *can*, but
scoped the project to reflect the actual job.

**9. What would you tell a branch/regional manager based on this analysis?**
That default rate varies meaningfully by region and loan type — e.g. Credit
Card and Business Loan products default at a higher rate than Education
Loans, and certain branches (flagged in the branch default-rate query)
underperform even after controlling for a minimum loan volume. I'd
recommend tighter underwriting thresholds or more frequent monitoring for
those specific segments rather than a blanket policy change across the
whole portfolio.

**10. If you had one more week, what would you add?**
Three things: (1) a proper out-of-time backtest for the ML model instead of
a random split, to simulate predicting *future* defaults from *past* data;
(2) cohort/vintage analysis — tracking default rate by the loan's
origination month over its lifetime, rather than only by current status;
and (3) an actual .pbix file built and screenshotted in Power BI Desktop,
since this environment could only produce the DAX/design spec, not the
binary report file itself.
