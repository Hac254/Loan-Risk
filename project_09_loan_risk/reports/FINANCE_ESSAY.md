# Finance Essay: Loan Default Risk in the Kenyan Banking Sector

## Introduction

Microfinance and commercial lending are central to Kenya's economy. Institutions such as Equity Bank, KCB, and SACCOs disburse billions of Kenyan Shillings (KSh) annually to individuals and small businesses. However, non-performing loans (NPLs) remain a persistent challenge. The Central Bank of Kenya (CBK) monitors NPL ratios closely because high default rates erode bank capital, reduce lending capacity, and can trigger systemic risk in the financial sector.

This essay explains the financial concepts behind loan default prediction and why machine learning supports — but does not replace — prudent credit assessment.

## What Is Loan Default?

A **loan default** occurs when a borrower fails to meet contractual repayment obligations within an agreed grace period. In Kenya, defaults may arise from:

- **Income volatility** — informal sector workers and jua kali entrepreneurs often face irregular cash flows.
- **Over-borrowing** — applicants request amounts disproportionate to their monthly income.
- **External shocks** — drought, fuel price spikes, or health emergencies can disrupt repayment.
- **Weak collateral** — unsecured personal loans carry higher loss-given-default exposure.

Banks classify risk using the **5 Cs of credit**: Character, Capacity, Capital, Collateral, and Conditions. Our capstone model approximates Capacity (income vs loan size), Capital (employment stability), and Collateral through structured features.

## Key Financial Ratios

### Debt-to-Income (DTI)

DTI compares total debt obligations to gross income. In this project, we approximate burden as:

```
DTI proxy = loan_amount_ksh / (monthly_income_ksh × loan_term_months)
```

A high DTI suggests the applicant may struggle to service the loan alongside living expenses. Kenyan lenders typically prefer DTI ratios below 40% for consumer credit, though SACCOs may apply different thresholds for member loans.

### Credit Score

Credit scores (300–850) summarise repayment history reported to CRBs (Credit Reference Bureaus) such as Metropol and TransUnion. Lower scores correlate with prior delinquencies, bounced cheques, or mobile loan defaults on platforms like M-Shwari and Fuliza.

### Collateral and Education as Risk Modifiers

Collateral reduces **loss given default (LGD)** — the amount a bank loses after recovery efforts. Higher education levels often correlate with stable employment, though this is a statistical tendency, not a guarantee.

## Why Predict Default Risk?

Proactive risk scoring enables:

1. **Pricing** — higher-risk loans may carry higher interest rates (risk-based pricing).
2. **Provisioning** — IFRS 9 requires expected credit loss provisions; better forecasts improve balance-sheet accuracy.
3. **Portfolio management** — concentration limits can be applied to high-risk segments.
4. **Regulatory compliance** — CBK prudential guidelines expect boards to monitor credit quality.

## Machine Learning in Credit Risk

Traditional scorecards use logistic regression with manually engineered features. Modern approaches include:

- **K-Nearest Neighbours (KNN)** — classifies applicants by similarity to historical cases; intuitive for loan officers.
- **Naive Bayes** — fast probabilistic classifier assuming feature independence.
- **Gradient boosting** — industry standard for large datasets (not used here due to diploma scope).

Our project compares KNN and Naive Bayes on 200 synthetic Kenyan loan records. The bank officer CLI maps predicted default probability to **Low**, **Medium**, or **High** risk bands, supporting human-in-the-loop decisions.

## Ethical and Regulatory Considerations

AI credit models must comply with Kenya's **Data Protection Act 2019** and avoid discriminatory bias against protected groups. Transparency matters: applicants denied credit should understand the basis of the decision where practicable. Synthetic data, as used in this project, is appropriate for learning but must be replaced with audited production data before deployment.

## Conclusion

Loan default prediction bridges finance and artificial intelligence. By quantifying risk from income, credit history, collateral, and demographic factors, banks can lend more responsibly while expanding financial inclusion. The ultimate goal is not to automate rejection, but to equip officers with evidence-based tools that protect both the institution and the borrower.
