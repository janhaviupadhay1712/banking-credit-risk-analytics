-- ============================================================
-- 02_queries.sql
-- Banking Credit Risk Analytics — Analytical SQL Queries
-- 25 interview-quality queries: JOINs, GROUP BY, CASE, CTEs,
-- subqueries, and window functions.
-- ============================================================

-- ------------------------------------------------------------
-- 1. Overall portfolio default rate
-- ------------------------------------------------------------
SELECT
    COUNT(*)                                                       AS total_loans,
    SUM(CASE WHEN loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END) AS default_loans,
    ROUND(100.0 * SUM(CASE WHEN loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                            AS default_rate_pct
FROM loans;

-- ------------------------------------------------------------
-- 2. Overall delinquency rate (30+ DPD, Delinquent/Default/Written Off)
-- ------------------------------------------------------------
SELECT
    ROUND(100.0 * SUM(CASE WHEN loan_status IN ('Delinquent','Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS delinquency_rate_pct
FROM loans;

-- ------------------------------------------------------------
-- 3. Default rate by Loan Type
-- ------------------------------------------------------------
SELECT
    loan_type,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(CASE WHEN loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY loan_type
ORDER BY default_rate_pct DESC;

-- ------------------------------------------------------------
-- 4. Default rate by Region (JOIN customers <-> loans)
-- ------------------------------------------------------------
SELECT
    c.region,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(CASE WHEN l.loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS default_rate_pct
FROM loans l
JOIN customers c ON c.customer_id = l.customer_id
GROUP BY c.region
ORDER BY default_rate_pct DESC;

-- ------------------------------------------------------------
-- 5. Default rate by Employment Type
-- ------------------------------------------------------------
SELECT
    c.employment_type,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(CASE WHEN l.loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS default_rate_pct
FROM loans l
JOIN customers c ON c.customer_id = l.customer_id
GROUP BY c.employment_type
ORDER BY default_rate_pct DESC;

-- ------------------------------------------------------------
-- 6. Risk segmentation using CASE (rebuilds the Python risk score in SQL)
-- ------------------------------------------------------------
SELECT
    c.customer_id,
    c.credit_score,
    c.dti,
    c.previous_defaults,
    c.late_payments,
    (
      CASE WHEN c.credit_score < 580 THEN 3 WHEN c.credit_score < 670 THEN 2
           WHEN c.credit_score < 740 THEN 1 ELSE 0 END
      + CASE WHEN c.dti > 50 THEN 3 WHEN c.dti > 36 THEN 2 WHEN c.dti > 20 THEN 1 ELSE 0 END
      + CASE WHEN c.previous_defaults >= 2 THEN 3 WHEN c.previous_defaults = 1 THEN 2 ELSE 0 END
      + CASE WHEN c.late_payments >= 6 THEN 2 WHEN c.late_payments >= 3 THEN 1 ELSE 0 END
    ) AS risk_points,
    CASE
        WHEN (
          CASE WHEN c.credit_score < 580 THEN 3 WHEN c.credit_score < 670 THEN 2
               WHEN c.credit_score < 740 THEN 1 ELSE 0 END
          + CASE WHEN c.dti > 50 THEN 3 WHEN c.dti > 36 THEN 2 WHEN c.dti > 20 THEN 1 ELSE 0 END
          + CASE WHEN c.previous_defaults >= 2 THEN 3 WHEN c.previous_defaults = 1 THEN 2 ELSE 0 END
          + CASE WHEN c.late_payments >= 6 THEN 2 WHEN c.late_payments >= 3 THEN 1 ELSE 0 END
        ) >= 6 THEN 'High Risk'
        WHEN (
          CASE WHEN c.credit_score < 580 THEN 3 WHEN c.credit_score < 670 THEN 2
               WHEN c.credit_score < 740 THEN 1 ELSE 0 END
          + CASE WHEN c.dti > 50 THEN 3 WHEN c.dti > 36 THEN 2 WHEN c.dti > 20 THEN 1 ELSE 0 END
          + CASE WHEN c.previous_defaults >= 2 THEN 3 WHEN c.previous_defaults = 1 THEN 2 ELSE 0 END
          + CASE WHEN c.late_payments >= 6 THEN 2 WHEN c.late_payments >= 3 THEN 1 ELSE 0 END
        ) >= 3 THEN 'Medium Risk'
        ELSE 'Low Risk'
    END AS risk_segment
FROM customers c;

-- ------------------------------------------------------------
-- 7. Risk segment distribution with a CTE (reuses query 6 logic)
-- ------------------------------------------------------------
WITH risk_calc AS (
    SELECT
        c.customer_id,
        (
          CASE WHEN c.credit_score < 580 THEN 3 WHEN c.credit_score < 670 THEN 2
               WHEN c.credit_score < 740 THEN 1 ELSE 0 END
          + CASE WHEN c.dti > 50 THEN 3 WHEN c.dti > 36 THEN 2 WHEN c.dti > 20 THEN 1 ELSE 0 END
          + CASE WHEN c.previous_defaults >= 2 THEN 3 WHEN c.previous_defaults = 1 THEN 2 ELSE 0 END
          + CASE WHEN c.late_payments >= 6 THEN 2 WHEN c.late_payments >= 3 THEN 1 ELSE 0 END
        ) AS risk_points
    FROM customers c
),
segmented AS (
    SELECT customer_id,
           CASE WHEN risk_points >= 6 THEN 'High Risk'
                WHEN risk_points >= 3 THEN 'Medium Risk'
                ELSE 'Low Risk' END AS risk_segment
    FROM risk_calc
)
SELECT risk_segment, COUNT(*) AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_book
FROM segmented
GROUP BY risk_segment
ORDER BY customers DESC;

-- ------------------------------------------------------------
-- 8. Top 10 high-risk customers by outstanding exposure (subquery)
-- ------------------------------------------------------------
SELECT customer_id, loan_type, outstanding_amount, days_past_due, loan_status
FROM loans
WHERE customer_id IN (
    SELECT customer_id FROM customers
    WHERE credit_score < 600 AND dti > 45 AND previous_defaults >= 1
)
ORDER BY outstanding_amount DESC
LIMIT 10;

-- ------------------------------------------------------------
-- 9. Total outstanding & overdue amount by Loan Status
-- ------------------------------------------------------------
SELECT
    loan_status,
    COUNT(*) AS loan_count,
    SUM(outstanding_amount) AS total_outstanding,
    SUM(CASE WHEN days_past_due > 0 THEN outstanding_amount ELSE 0 END) AS total_overdue_amount
FROM loans
GROUP BY loan_status
ORDER BY total_outstanding DESC;

-- ------------------------------------------------------------
-- 10. Monthly application volume and default rate trend
-- ------------------------------------------------------------
SELECT
    DATE_TRUNC('month', application_date) AS app_month,     -- MySQL: DATE_FORMAT(application_date,'%Y-%m-01')
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(CASE WHEN loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY DATE_TRUNC('month', application_date)
ORDER BY app_month;

-- ------------------------------------------------------------
-- 11. Top 5 branches by default rate (min. 50 loans) — HAVING clause
-- ------------------------------------------------------------
SELECT
    c.branch,
    COUNT(*) AS total_loans,
    ROUND(100.0 * SUM(CASE WHEN l.loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS default_rate_pct
FROM loans l
JOIN customers c ON c.customer_id = l.customer_id
GROUP BY c.branch
HAVING COUNT(*) >= 50
ORDER BY default_rate_pct DESC
LIMIT 5;

-- ------------------------------------------------------------
-- 12. Customers with more than one active loan (window function)
-- ------------------------------------------------------------
SELECT customer_id, loan_count
FROM (
    SELECT customer_id, COUNT(*) OVER (PARTITION BY customer_id) AS loan_count
    FROM loans
    WHERE loan_status = 'Active'
) t
WHERE loan_count > 1
GROUP BY customer_id, loan_count
ORDER BY loan_count DESC;

-- ------------------------------------------------------------
-- 13. Rank customers by outstanding amount within each region (window fn)
-- ------------------------------------------------------------
SELECT
    c.region,
    c.customer_id,
    l.outstanding_amount,
    RANK() OVER (PARTITION BY c.region ORDER BY l.outstanding_amount DESC) AS region_rank
FROM loans l
JOIN customers c ON c.customer_id = l.customer_id
QUALIFY region_rank <= 5;   -- Snowflake/BigQuery syntax
-- Standard SQL alternative (wrap in subquery + WHERE rnk <=5) shown in query 14.

-- ------------------------------------------------------------
-- 14. Same as #13 in ANSI-standard SQL (no QUALIFY) — top 5 per region
-- ------------------------------------------------------------
SELECT * FROM (
    SELECT
        c.region,
        c.customer_id,
        l.outstanding_amount,
        RANK() OVER (PARTITION BY c.region ORDER BY l.outstanding_amount DESC) AS region_rank
    FROM loans l
    JOIN customers c ON c.customer_id = l.customer_id
) ranked
WHERE region_rank <= 5
ORDER BY region, region_rank;

-- ------------------------------------------------------------
-- 15. Running total of monthly disbursement (window function)
-- ------------------------------------------------------------
SELECT
    app_month,
    monthly_disbursed,
    SUM(monthly_disbursed) OVER (ORDER BY app_month) AS cumulative_disbursed
FROM (
    SELECT DATE_TRUNC('month', application_date) AS app_month,
           SUM(loan_amount) AS monthly_disbursed
    FROM loans
    GROUP BY DATE_TRUNC('month', application_date)
) monthly
ORDER BY app_month;

-- ------------------------------------------------------------
-- 16. Month-over-month change in default rate (LAG window function)
-- ------------------------------------------------------------
WITH monthly_default AS (
    SELECT
        DATE_TRUNC('month', application_date) AS app_month,
        ROUND(100.0 * SUM(CASE WHEN loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END)
              / COUNT(*), 2) AS default_rate_pct
    FROM loans
    GROUP BY DATE_TRUNC('month', application_date)
)
SELECT
    app_month,
    default_rate_pct,
    LAG(default_rate_pct) OVER (ORDER BY app_month) AS prev_month_rate,
    ROUND(default_rate_pct - LAG(default_rate_pct) OVER (ORDER BY app_month), 2) AS mom_change
FROM monthly_default
ORDER BY app_month;

-- ------------------------------------------------------------
-- 17. Credit score decile analysis (NTILE window function)
-- ------------------------------------------------------------
WITH deciles AS (
    SELECT
        c.customer_id,
        c.credit_score,
        l.loan_status,
        NTILE(10) OVER (ORDER BY c.credit_score) AS score_decile
    FROM customers c
    JOIN loans l ON l.customer_id = c.customer_id
)
SELECT
    score_decile,
    MIN(credit_score) AS min_score,
    MAX(credit_score) AS max_score,
    COUNT(*) AS loans,
    ROUND(100.0 * SUM(CASE WHEN loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2) AS default_rate_pct
FROM deciles
GROUP BY score_decile
ORDER BY score_decile;

-- ------------------------------------------------------------
-- 18. Customers whose DTI is above their region's average (correlated subquery)
-- ------------------------------------------------------------
SELECT c.customer_id, c.region, c.dti
FROM customers c
WHERE c.dti > (
    SELECT AVG(c2.dti) FROM customers c2 WHERE c2.region = c.region
)
ORDER BY c.region, c.dti DESC;

-- ------------------------------------------------------------
-- 19. High-risk customer master list (multiple JOINs + CASE flags)
-- ------------------------------------------------------------
SELECT
    c.customer_id,
    c.age,
    c.income,
    c.employment_type,
    c.credit_score,
    c.dti,
    c.region,
    l.loan_type,
    l.outstanding_amount,
    l.days_past_due,
    l.loan_status,
    CASE WHEN c.credit_score < 580 THEN 'Y' ELSE 'N' END AS low_credit_flag,
    CASE WHEN c.dti > 50 THEN 'Y' ELSE 'N' END            AS high_dti_flag,
    CASE WHEN c.previous_defaults >= 1 THEN 'Y' ELSE 'N' END AS prior_default_flag
FROM customers c
JOIN loans l ON l.customer_id = c.customer_id
WHERE l.loan_status IN ('Delinquent','Default','Written Off')
  AND (c.credit_score < 580 OR c.dti > 50 OR c.previous_defaults >= 1)
ORDER BY l.outstanding_amount DESC;

-- ------------------------------------------------------------
-- 20. Average DTI and Credit Score by Risk Segment (CTE)
-- ------------------------------------------------------------
WITH risk_calc AS (
    SELECT
        c.customer_id, c.credit_score, c.dti,
        (
          CASE WHEN c.credit_score < 580 THEN 3 WHEN c.credit_score < 670 THEN 2
               WHEN c.credit_score < 740 THEN 1 ELSE 0 END
          + CASE WHEN c.dti > 50 THEN 3 WHEN c.dti > 36 THEN 2 WHEN c.dti > 20 THEN 1 ELSE 0 END
          + CASE WHEN c.previous_defaults >= 2 THEN 3 WHEN c.previous_defaults = 1 THEN 2 ELSE 0 END
          + CASE WHEN c.late_payments >= 6 THEN 2 WHEN c.late_payments >= 3 THEN 1 ELSE 0 END
        ) AS risk_points
    FROM customers c
)
SELECT
    CASE WHEN risk_points >= 6 THEN 'High Risk'
         WHEN risk_points >= 3 THEN 'Medium Risk'
         ELSE 'Low Risk' END AS risk_segment,
    ROUND(AVG(credit_score), 0) AS avg_credit_score,
    ROUND(AVG(dti), 2)          AS avg_dti,
    COUNT(*)                    AS customers
FROM risk_calc
GROUP BY 1
ORDER BY customers DESC;

-- ------------------------------------------------------------
-- 21. Loan type portfolio mix (% share of total disbursed amount)
-- ------------------------------------------------------------
SELECT
    loan_type,
    SUM(loan_amount) AS total_disbursed,
    ROUND(100.0 * SUM(loan_amount) / SUM(SUM(loan_amount)) OVER (), 1) AS pct_of_portfolio
FROM loans
GROUP BY loan_type
ORDER BY total_disbursed DESC;

-- ------------------------------------------------------------
-- 22. Customers with 90+ days past due — collections priority list
-- ------------------------------------------------------------
SELECT
    c.customer_id, c.income, c.credit_score, l.loan_type,
    l.outstanding_amount, l.days_past_due, l.loan_status
FROM loans l
JOIN customers c ON c.customer_id = l.customer_id
WHERE l.days_past_due >= 90
ORDER BY l.outstanding_amount DESC;

-- ------------------------------------------------------------
-- 23. Year-over-year default rate comparison (self-join style with CTE)
-- ------------------------------------------------------------
WITH yearly AS (
    SELECT
        EXTRACT(YEAR FROM application_date) AS app_year,
        COUNT(*) AS total_loans,
        SUM(CASE WHEN loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END) AS defaults
    FROM loans
    GROUP BY EXTRACT(YEAR FROM application_date)
)
SELECT
    app_year,
    total_loans,
    defaults,
    ROUND(100.0 * defaults / total_loans, 2) AS default_rate_pct,
    ROUND(100.0 * defaults / total_loans
          - LAG(ROUND(100.0 * defaults / total_loans, 2)) OVER (ORDER BY app_year), 2) AS yoy_change_pp
FROM yearly
ORDER BY app_year;

-- ------------------------------------------------------------
-- 24. Interest rate vs risk segment (are riskier customers priced higher?)
-- ------------------------------------------------------------
WITH risk_calc AS (
    SELECT
        c.customer_id,
        (
          CASE WHEN c.credit_score < 580 THEN 3 WHEN c.credit_score < 670 THEN 2
               WHEN c.credit_score < 740 THEN 1 ELSE 0 END
          + CASE WHEN c.dti > 50 THEN 3 WHEN c.dti > 36 THEN 2 WHEN c.dti > 20 THEN 1 ELSE 0 END
          + CASE WHEN c.previous_defaults >= 2 THEN 3 WHEN c.previous_defaults = 1 THEN 2 ELSE 0 END
          + CASE WHEN c.late_payments >= 6 THEN 2 WHEN c.late_payments >= 3 THEN 1 ELSE 0 END
        ) AS risk_points
    FROM customers c
)
SELECT
    CASE WHEN r.risk_points >= 6 THEN 'High Risk'
         WHEN r.risk_points >= 3 THEN 'Medium Risk'
         ELSE 'Low Risk' END AS risk_segment,
    ROUND(AVG(l.interest_rate), 2) AS avg_interest_rate,
    COUNT(*) AS loans
FROM loans l
JOIN risk_calc r ON r.customer_id = l.customer_id
GROUP BY 1
ORDER BY avg_interest_rate DESC;

-- ------------------------------------------------------------
-- 25. Portfolio summary dashboard query (single-row KPI snapshot)
-- ------------------------------------------------------------
SELECT
    COUNT(DISTINCT l.customer_id)                                    AS total_customers,
    COUNT(*)                                                          AS total_loans,
    SUM(l.loan_amount)                                                AS total_disbursed,
    SUM(l.outstanding_amount)                                         AS total_outstanding,
    ROUND(100.0 * SUM(CASE WHEN l.loan_status IN ('Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                              AS default_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN l.loan_status IN ('Delinquent','Default','Written Off') THEN 1 ELSE 0 END)
          / COUNT(*), 2)                                              AS delinquency_rate_pct,
    ROUND(AVG(c.credit_score), 0)                                     AS avg_credit_score,
    ROUND(AVG(c.dti), 2)                                              AS avg_dti
FROM loans l
JOIN customers c ON c.customer_id = l.customer_id;
