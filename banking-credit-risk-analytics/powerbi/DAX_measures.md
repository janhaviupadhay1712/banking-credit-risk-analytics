# Power BI — DAX Measures

Data model: two tables, `Customers` and `Loans` (matches `sql/01_schema.sql`),
joined **1-to-many** on `Customer_ID` (one customer → many loans). Alternatively,
load the single flat file `data/loan_data_features.csv` as one table named
`Loans` — every measure below works either way (just drop the `RELATED()` calls
if using the flat table, since the fields are already on one row).

Also load a **Date table** (`Calendar`) and mark it as a Date Table, related to
`Loans[Application_Date]`, for clean time-intelligence.

```DAX
Calendar =
CALENDAR (
    MIN ( Loans[Application_Date] ),
    MAX ( Loans[Application_Date] )
)
```

---

## Core Volume Measures

```DAX
Total Loans = COUNTROWS ( Loans )

Total Customers = DISTINCTCOUNT ( Loans[Customer_ID] )

Total Loan Amount = SUM ( Loans[Loan_Amount] )

Total Outstanding Amount = SUM ( Loans[Outstanding_Amount] )

Average Loan Amount = AVERAGE ( Loans[Loan_Amount] )

Average Credit Score = AVERAGE ( Loans[Credit_Score] )
-- If Credit_Score lives on Customers: AVERAGE ( Customers[Credit_Score] )

Average DTI = AVERAGE ( Loans[DTI] )
```

## Risk & Default Measures

```DAX
Default Loans =
CALCULATE (
    COUNTROWS ( Loans ),
    Loans[Loan_Status] IN { "Default", "Written Off" }
)

Default Rate % =
DIVIDE ( [Default Loans], [Total Loans], 0 )

Delinquent Loans =
CALCULATE (
    COUNTROWS ( Loans ),
    Loans[Loan_Status] IN { "Delinquent", "Default", "Written Off" }
)

Delinquency Rate % =
DIVIDE ( [Delinquent Loans], [Total Loans], 0 )

High-Risk Customers =
CALCULATE (
    DISTINCTCOUNT ( Loans[Customer_ID] ),
    Loans[Risk_Segment] = "High Risk"
)

High-Risk % of Book =
DIVIDE ( [High-Risk Customers], [Total Customers], 0 )

NPA Amount (Non-Performing Exposure) =
CALCULATE (
    SUM ( Loans[Outstanding_Amount] ),
    Loans[Loan_Status] IN { "Default", "Written Off" }
)

NPA Ratio % =
DIVIDE ( [NPA Amount (Non-Performing Exposure)], [Total Outstanding Amount], 0 )

Overdue Amount (30+ DPD) =
CALCULATE (
    SUM ( Loans[Outstanding_Amount] ),
    Loans[Days_Past_Due] >= 30
)

Overdue Loan Count (90+ DPD) =
CALCULATE (
    COUNTROWS ( Loans ),
    Loans[Days_Past_Due] >= 90
)
```

## Time Intelligence

```DAX
Loans MTD = TOTALMTD ( [Total Loans], Calendar[Date] )

Default Rate % (Prior Month) =
CALCULATE ( [Default Rate %], DATEADD ( Calendar[Date], -1, MONTH ) )

Default Rate % MoM Change =
[Default Rate %] - [Default Rate % (Prior Month)]

YoY Default Rate % =
CALCULATE ( [Default Rate %], SAMEPERIODLASTYEAR ( Calendar[Date] ) )
```

## Segmentation Helper Measures

```DAX
-- Used for tooltips / KPI cards that need a plain-language verdict
Portfolio Risk Verdict =
VAR HighRiskPct = [High-Risk % of Book]
RETURN
    SWITCH (
        TRUE (),
        HighRiskPct > 0.25, "⚠ Elevated Risk",
        HighRiskPct > 0.15, "Watch",
        "Stable"
    )

Avg Outstanding per High-Risk Customer =
DIVIDE (
    CALCULATE ( SUM ( Loans[Outstanding_Amount] ), Loans[Risk_Segment] = "High Risk" ),
    [High-Risk Customers],
    0
)
```

## Ranking (for "Top Branches" / "Top Customers" visuals)

```DAX
Branch Default Rank =
RANKX ( ALL ( Loans[Branch] ), [Default Rate %], , DESC )

Customer Outstanding Rank =
RANKX ( ALL ( Loans[Customer_ID] ), [Total Outstanding Amount], , DESC )
```

All measures use `DIVIDE()` instead of `/` to avoid divide-by-zero errors
when a filter context returns an empty table (e.g., a slicer selection with
no matching loans).
