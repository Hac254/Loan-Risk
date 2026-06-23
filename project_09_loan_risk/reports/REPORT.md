# Project 9 Report: Loan Default Risk Predictor

## 1. Project Overview

This capstone implements a loan default risk prediction system for a Kenyan banking context. The system generates 200 synthetic loan records, trains K-Nearest Neighbours (KNN) and Gaussian Naive Bayes classifiers, produces visual analytics, and provides an interactive bank officer CLI with Low/Medium/High risk ratings.

## 2. Objectives

- Generate realistic synthetic loan data with approximately 30% default rate.
- Implement an OOP `LoanRiskPredictor` class with `load_data()`, `preprocess()`, `train()`, `predict()`, and `evaluate()` methods.
- Tune KNN using 5-fold cross-validation over K = 1–20.
- Compare KNN against Naive Bayes on accuracy and F1 score.
- Deliver four or more visualisations including a feature correlation heatmap.
- Provide an interactive CLI for bank officers.

## 3. Dataset

| Feature | Description |
|---------|-------------|
| `applicant_id` | Unique identifier (APP001–APP200) |
| `age` | Applicant age (22–65) |
| `income_ksh` | Monthly income in Kenyan Shillings |
| `loan_amount_ksh` | Requested loan amount |
| `employment_years` | Years in current/continuous employment |
| `credit_score` | Bureau score (300–850) |
| `num_dependents` | Number of financial dependents |
| `has_collateral` | Yes/No |
| `education_level` | Primary, Secondary, Tertiary, Graduate |
| `loan_term_months` | Repayment period |
| `default` | Target: Yes/No |

Default labels are generated using a logistic model incorporating debt burden, credit score, dependents, employment, collateral, and education — calibrated to ~30% positive class.

## 4. Methodology

### 4.1 Preprocessing

- Categorical encoding: `has_collateral` → binary; `education_level` → ordinal 0–3.
- Feature scaling via `StandardScaler` (critical for distance-based KNN).
- Stratified 75/25 train-test split.

### 4.2 KNN with Cross-Validation

`GridSearchCV` evaluates K from 1 to 20 using 5-fold cross-validation and F1 scoring. The best K is selected and stored for inference.

### 4.3 Naive Bayes

`GaussianNB` assumes features follow a Gaussian distribution. It serves as a fast probabilistic baseline that does not require scaling (though scaling is applied consistently for fair comparison).

### 4.4 Risk Rating Logic

| Default Probability | Risk Rating | Recommendation |
|--------------------|-------------|----------------|
| < 35% | Low | Approve with standard terms |
| 35% – 65% | Medium | Approve with enhanced monitoring |
| ≥ 65% | High | Decline or require collateral/guarantor |

## 5. Architecture

```
project_09_loan_risk/
├── main.py                  # Entry point: train, visualise, CLI
├── loan_risk_predictor.py   # LoanRiskPredictor OOP class
├── generate_dataset.py      # Synthetic data generator
├── data/loans.csv
├── outputs/                 # PNG visualisations
└── reports/
    ├── FINANCE_ESSAY.md
    └── REPORT.md
```

## 6. Visualisations

1. **correlation_heatmap.png** — Pearson correlations between numeric features and default.
2. **default_distribution.png** — Pie chart of Yes/No default split.
3. **credit_score_by_default.png** — Box plot comparing credit scores.
4. **knn_k_tuning.png** — CV F1 scores across K values with best-K marker.
5. **model_confusion_matrices.png** — Side-by-side confusion matrices.
6. **model_comparison.png** — Bar chart of accuracy and F1.
7. **default_by_loan_bracket.png** — Default rate by loan amount bracket.

## 7. How to Run

```bash
cd project_09_loan_risk
python main.py
```

The script auto-generates `data/loans.csv` if missing, trains both models, saves charts to `outputs/`, and launches the bank officer CLI.

## 8. Learning Outcomes

| LO | Evidence |
|----|----------|
| LO1 | Finance essay on Kenyan lending and credit risk theory |
| LO2 | KNN vs Naive Bayes comparison, CV-based hyperparameter tuning |
| LO3 | OOP design, PEP 8, matplotlib/seaborn visualisation |
| LO4 | End-to-end applied AI: data → model → CLI decision support |

## 9. Limitations and Future Work

- Synthetic data does not capture real CRB reporting nuances.
- Gaussian Naive Bayes assumes feature independence (loan amount and income are correlated).
- Future versions could add SHAP explainability and integration with live CRB APIs.

## 10. Conclusion

The project demonstrates how classification algorithms support loan officers in quantifying default risk. KNN provides intuitive neighbourhood-based reasoning; Naive Bayes offers a fast probabilistic alternative. Together with visual analytics and the interactive CLI, the system fulfils the diploma capstone requirements for applied AI in finance.
