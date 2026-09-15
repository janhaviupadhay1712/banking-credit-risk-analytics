# Data-Driven Business Recommendations

Based on figures calculated directly from the cleaned 21,527-record
dataset (`python/04_kpi_business_insights.py`). Exact numbers will differ
if the script is re-run with a different random seed or on a different
dataset, but the analytical approach and recommendation logic hold.

1. **Tighten underwriting on Credit Card and Business Loan products.**
   These carry the highest default rates in the portfolio (5.9% and 5.7%
   respectively, vs. a 5.3% overall average). Recommend a stricter minimum
   credit score / lower DTI ceiling specifically for these two products.

2. **Increase collections resourcing in the South region.**
   South shows the highest regional default rate (5.85% vs. 4.86% in
   North, the best-performing region). A regional gap of ~1 point on a
   book this size translates to material NPA exposure — recommend a
   focused collections/monitoring push there.

3. **Add an "Unemployed" applicant review gate.**
   Unemployed customers default at 6.2%, the highest of any employment
   category — meaningfully above Salaried (5.3%) and Business Owner (4.9%).
   Recommend manual underwriter review (not auto-approval) for this
   segment, or a lower approval loan-to-income cap.

4. **Prioritize the High-Risk segment for proactive outreach — it is
   capital-concentrated, not just volume-concentrated.** High-Risk
   customers are ~19% of the book by count but hold a *disproportionate*
   share of total outstanding exposure — losing even a fraction of this
   segment to default has an outsized balance-sheet impact vs. its
   headcount share.

5. **Investigate the 90+ DPD bucket as a collections/write-off priority
   list.** The `Overdue_Tracker` sheet and SQL query #22 isolate loans 90+
   days past due — these are the loans closest to formal write-off and
   should be first in line for structured settlement offers or legal
   recovery, since recovery probability drops sharply the longer DPD runs.

6. **Re-examine risk-based pricing.** SQL query #24 compares average
   interest rate across risk segments — if High-Risk customers aren't
   priced meaningfully higher than Low-Risk ones, the bank is under-pricing
   for the risk it's carrying. Recommend aligning interest rate bands more
   tightly to the Risk_Segment output.

7. **Set an NPA ratio alert threshold.** The portfolio's NPA ratio (NPA /
   total outstanding) sits above the commonly cited 5% comfort zone for
   retail books — recommend a standing Power BI alert/report whenever this
   crosses a management-defined threshold, rather than discovering it at
   quarter-end.

8. **Audit underperforming branches, not just underperforming products.**
   The branch-level default-rate query (with a minimum 50-loan floor to
   avoid small-sample noise) surfaces specific branches with elevated
   default rates — worth investigating whether this reflects local
   underwriting laxity, a weaker regional economy, or a training gap for
   loan officers at those branches.

9. **Use the Credit Score decile analysis to sanity-check the scorecard
   quarterly.** If default rate stops decreasing monotonically as score
   decile improves, that's an early signal the underlying population has
   shifted (e.g., a change in the applicant mix) and the risk scorecard
   thresholds may need recalibration.

10. **Track month-over-month default rate trend as a leading indicator,**
    not just the point-in-time snapshot. The `08_monthly_default_rate_trend`
    chart and SQL query #16 (LAG-based MoM change) let management catch a
    deteriorating trend early, before it shows up in the headline annual
    default rate.
