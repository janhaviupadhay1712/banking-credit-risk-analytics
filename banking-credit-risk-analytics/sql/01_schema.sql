-- ============================================================
-- 01_schema.sql
-- Banking Credit Risk Analytics — Database Schema
-- Compatible with PostgreSQL / MySQL (minor dialect tweaks noted)
-- ============================================================

DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS customers;

-- ------------------------------------------------------------
-- CUSTOMERS: one row per customer (demographic + bureau data)
-- ------------------------------------------------------------
CREATE TABLE customers (
    customer_id         INT PRIMARY KEY,
    age                  INT NOT NULL,
    income               DECIMAL(14,2) NOT NULL,
    employment_type      VARCHAR(30) NOT NULL,
    credit_score         INT NOT NULL CHECK (credit_score BETWEEN 300 AND 900),
    dti                  DECIMAL(6,2) NOT NULL,          -- Debt-to-Income %
    region               VARCHAR(20) NOT NULL,
    branch               VARCHAR(30) NOT NULL,
    previous_defaults    INT NOT NULL DEFAULT 0,
    late_payments        INT NOT NULL DEFAULT 0
);

-- ------------------------------------------------------------
-- LOANS: one row per loan (can be multiple loans per customer)
-- ------------------------------------------------------------
CREATE TABLE loans (
    loan_id              INT PRIMARY KEY AUTO_INCREMENT,  -- MySQL syntax
    -- Postgres: loan_id SERIAL PRIMARY KEY,
    customer_id          INT NOT NULL,
    loan_type            VARCHAR(30) NOT NULL,
    loan_amount           DECIMAL(14,2) NOT NULL,
    interest_rate         DECIMAL(5,2) NOT NULL,
    loan_term_months      INT NOT NULL,
    outstanding_amount    DECIMAL(14,2) NOT NULL,
    days_past_due         INT NOT NULL DEFAULT 0,
    loan_status           VARCHAR(20) NOT NULL,           -- Active/Closed/Delinquent/Default/Written Off
    application_date      DATE NOT NULL,
    payment_date          DATE,
    CONSTRAINT fk_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- ------------------------------------------------------------
-- Indexes to support the analytical queries in 02_queries.sql
-- ------------------------------------------------------------
CREATE INDEX idx_loans_customer_id   ON loans (customer_id);
CREATE INDEX idx_loans_status        ON loans (loan_status);
CREATE INDEX idx_loans_type          ON loans (loan_type);
CREATE INDEX idx_loans_app_date      ON loans (application_date);
CREATE INDEX idx_customers_region    ON customers (region);
CREATE INDEX idx_customers_score     ON customers (credit_score);

-- ------------------------------------------------------------
-- Loading data (example — adjust path/client for your engine)
-- ------------------------------------------------------------
-- Recommended approach: load ../data/loan_data_features.csv into a
-- staging table `loan_data_stg` (all VARCHAR) with your DB client's
-- bulk-load tool, then split into customers/loans with INSERT...SELECT:

-- PostgreSQL example:
-- \copy loan_data_stg FROM '../data/loan_data_features.csv' WITH (FORMAT csv, HEADER true);

-- INSERT INTO customers (customer_id, age, income, employment_type, credit_score,
--                         dti, region, branch, previous_defaults, late_payments)
-- SELECT DISTINCT customer_id::int, age::int, income::decimal, employment_type,
--        credit_score::int, dti::decimal, region, branch,
--        previous_defaults::int, late_payments::int
-- FROM loan_data_stg;

-- INSERT INTO loans (customer_id, loan_type, loan_amount, interest_rate,
--                     loan_term_months, outstanding_amount, days_past_due,
--                     loan_status, application_date, payment_date)
-- SELECT customer_id::int, loan_type, loan_amount::decimal, interest_rate::decimal,
--        loan_term_months::int, outstanding_amount::decimal, days_past_due::int,
--        loan_status, application_date::date, payment_date::date
-- FROM loan_data_stg;
