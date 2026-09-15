# Project Limitations & Ethical Considerations

## Limitations

1. **Synthetic dataset.** The data is generated, not real bank data. Risk
   correlations (credit score → default, DTI → default, etc.) were
   deliberately built into the generator so the analysis has something
   realistic to find, but the exact figures (5.3% default rate, 8.75% NPA
   ratio, etc.) are illustrative of methodology, not a real institution's
   actual performance.

2. **No true out-of-time validation for the ML component.** The optional
   Logistic Regression / Random Forest model uses a random train/test
   split. A production credit model needs an out-of-time split (train on
   older vintages, test on newer ones) to realistically estimate how it
   would perform on genuinely *future* applicants — a random split
   overstates real-world reliability.

3. **Modest ML performance is expected, not a bug.** Because the synthetic
   risk signal is intentionally noisy (to mimic realistic ambiguity), the
   models achieve only modest ROC-AUC (~0.57–0.59). This is an honest
   result and is not the focus of the project — see README.

4. **Risk segmentation thresholds are illustrative, not regulator-approved.**
   The point-based Low/Medium/High cutoffs were chosen to produce a
   reasonable-looking distribution and clear default-rate separation
   between segments, not derived from a formal statistical
   optimization or validated against actual charge-off experience, as a
   real bank's model risk management function would require.

5. **No macroeconomic or time-varying context.** Real default rates are
   heavily influenced by macro conditions (interest rate cycles,
   unemployment, regional economic shocks) that this dataset doesn't
   model — the "monthly trend" here reflects only the synthetic generation
   process, not real economic cycles.

6. **Single flat snapshot, not a full loan lifecycle.** Each loan has one
   current status/DPD value rather than a full payment history over time,
   which limits the kind of vintage/cohort analysis a real risk team would
   do (e.g., tracking how a loan's risk evolves month-by-month from
   origination).

7. **Power BI deliverable is a design spec, not a compiled .pbix.**
   Power BI Desktop isn't available in this build environment; the DAX
   measures and page layout are fully specified and copy-paste ready, but
   assembling the actual report file is a manual final step.

## Ethical Considerations

1. **Fair lending / disparate impact.** Any real-world version of this
   analysis must be checked for disparate impact on protected
   characteristics (age, gender, etc. where legally protected), even when
   those attributes aren't explicit model inputs — proxies (e.g., region,
   employment type) can correlate with protected classes. This project
   uses Region and Employment_Type as risk factors for demonstration only;
   a production deployment would require a fair-lending review.

2. **Explainability over black-box scoring.** The rule-based risk
   segmentation was deliberately chosen over an opaque ML score for the
   *primary* segmentation output, because credit decisions affecting real
   people should be explainable to the customer and to a regulator/auditor
   — "your DTI is above 50%" is a concrete, appealable reason; a raw model
   probability is not.

3. **Data privacy.** All customer records here are synthetic. A real
   version of this project would require the loan data to be anonymized/
   pseudonymized, access-controlled, and handled per applicable banking
   data-privacy regulations (e.g., data localization, GDPR, or local
   equivalents) before ever reaching an analyst's laptop.

4. **Avoiding over-reliance on a single score for high-stakes decisions.**
   Even a well-validated risk segment should inform, not replace, human
   underwriting judgment for borderline or high-value cases — automated
   flags are a triage tool, not a final verdict.

5. **Model drift and fairness monitoring.** Any scorecard or ML model
   deployed in production needs ongoing monitoring (like the credit-score
   decile check recommended in `business_recommendations.md`) to catch both
   performance drift and any emerging fairness issues as the applicant
   population changes over time.
