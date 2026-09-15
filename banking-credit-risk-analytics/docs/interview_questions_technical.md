# 15 Technical Interview Questions & Answers

**1. What's the difference between `WHERE` and `HAVING`?**
`WHERE` filters individual rows before aggregation; `HAVING` filters groups
after `GROUP BY` has aggregated them. E.g., `WHERE loan_status = 'Default'`
filters raw rows, while `HAVING COUNT(*) >= 50` (used in my branch query)
filters branches only after their loan counts are aggregated.

**2. Explain the difference between `RANK()`, `DENSE_RANK()`, and `ROW_NUMBER()`.**
`ROW_NUMBER()` gives every row a unique sequential number regardless of ties.
`RANK()` gives tied rows the same rank but skips the next rank number
(1,1,3). `DENSE_RANK()` also ties but doesn't skip (1,1,2). I used `RANK()`
to rank customers by outstanding amount within each region — ties (equal
outstanding amounts) correctly share a rank.

**3. What is a CTE and why use one over a subquery?**
A Common Table Expression (`WITH x AS (...)`) is a named, temporary result
set scoped to one query. It improves readability for multi-step logic (like
my risk-scoring CTE reused across several queries) and can be referenced
multiple times without rewriting the subquery, though it isn't automatically
faster — the optimizer may still inline it.

**4. How does `LEFT JOIN` differ from `INNER JOIN`, and when would you use each?**
`INNER JOIN` returns only rows with a match in both tables; `LEFT JOIN`
returns all rows from the left table plus matches from the right (NULLs
where no match). I'd use `LEFT JOIN` if I wanted to include customers with
zero loans in a customer-level report — `INNER JOIN` (what I used) is
correct when every row must represent an actual loan.

**5. What does `Pandas.groupby().transform()` do, and why did you use it in cleaning?**
`transform()` applies a function per group but returns a result aligned to
the original DataFrame's index (same length), unlike `agg()` which collapses
to one row per group. I used it to impute missing `Income` with the *median
income of that customer's Employment_Type* rather than one global median —
more representative for a salaried vs. self-employed customer.

**6. Why use the median instead of the mean to fill missing numeric values?**
Income and loan amounts are right-skewed (a few very high earners). The mean
is pulled upward by these outliers; the median is robust to skew and
represents a more typical value, which is why I used it for Income, DTI,
Interest Rate, and Age.

**7. Explain the IQR method for outlier detection.**
Compute Q1 (25th percentile) and Q3 (75th percentile), then IQR = Q3 - Q1.
Values below `Q1 - k×IQR` or above `Q3 + k×IQR` (I used k=3 for a
conservative cap, since k=1.5 is quite aggressive on already-skewed
financial data) are treated as outliers. I capped rather than dropped them
to avoid losing legitimate high-income/high-loan customers.

**8. What's the difference between `DIVIDE()` and `/` in DAX?**
`DIVIDE(a, b, alt)` safely returns an alternate result (default BLANK) when
the denominator is 0 or BLANK, avoiding the `/0` error that `a/b` throws
under certain filter contexts — critical for KPI cards in Power BI when a
slicer selection could return an empty table.

**9. What is the difference between a fact table and a dimension table?**
A fact table holds transactional/measurable events (here: `Loans` — one row
per loan, with amounts, dates, status). A dimension table holds descriptive
attributes for filtering/grouping (here: `Customers` — one row per customer,
with demographic attributes). This star-schema-style split (vs. one flat
table) makes the Power BI model more efficient and avoids duplicating
customer attributes across every loan row.

**10. How would you detect and handle duplicate records in Pandas?**
`df.duplicated(subset=[...])` flags duplicates by a chosen key combination;
`df.drop_duplicates(subset=[...], keep='first')` removes them. I used a
composite key (Customer_ID + Loan_Type + Loan_Amount + Application_Date)
rather than the whole row, since a full-row duplicate check can miss
near-duplicates with a stray formatting difference in one column.

**11. What's `NTILE()` used for, and how did you apply it?**
`NTILE(n)` splits ordered rows into `n` roughly equal-sized buckets — I used
`NTILE(10)` to build credit-score deciles, then measured default rate per
decile. This is a standard bureau/risk-analytics technique to check that
risk scores are monotonic (lower score → higher default rate) without
needing a full statistical model.

**12. Why use `VARCHAR` with a `CHECK` constraint for `credit_score` instead of just an `INT`?**
The `CHECK (credit_score BETWEEN 300 AND 900)` constraint enforces domain
validity at the database level — it stops invalid values (like the `999` or
negative ages I intentionally injected into the raw data) from ever being
inserted, which is a stronger guarantee than relying on application-level
validation alone.

**13. What's the difference between `COUNT(*)` and `COUNT(column_name)`?**
`COUNT(*)` counts all rows regardless of NULLs. `COUNT(column_name)` counts
only non-NULL values in that column. I used `COUNT(*)` for total loans, but
would use `COUNT(Payment_Date)` if I specifically wanted to count loans that
have had at least one payment recorded.

**14. How do you decide between one-hot encoding and label encoding for categorical features in a model?**
One-hot encoding creates a binary column per category — appropriate for
nominal (unordered) categories like `Loan_Type` or `Region`, since label
encoding would wrongly imply an order/magnitude relationship. I used
`OneHotEncoder` for Employment_Type, Loan_Type and Region in the optional
ML pipeline; label/ordinal encoding is better suited to genuinely ordered
categories like the Credit_Score_Band.

**15. What is `class_weight='balanced'` doing in your Logistic Regression / Random Forest models, and why did you need it?**
It automatically re-weights the loss function inversely proportional to
class frequency, penalizing mistakes on the minority class (defaults, ~5%
of the data) more heavily. Without it, a model can get high "accuracy" by
just predicting "no default" for everyone — `class_weight='balanced'` forces
it to actually try to separate the classes, though on this dataset the true
lift is still modest since the synthetic risk signal is intentionally noisy.
