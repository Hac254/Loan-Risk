"""Generate synthetic Kenyan loan records with realistic default patterns."""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_loan_dataset(n_records: int = 200, seed: int = 42) -> pd.DataFrame:
    """Create loan applicant records in Kenyan KSh context."""
    rng = np.random.default_rng(seed)

    age = rng.integers(22, 65, n_records)
    income_ksh = rng.integers(15_000, 250_000, n_records)
    loan_amount_ksh = rng.integers(50_000, 2_000_000, n_records)
    employment_years = rng.integers(0, 30, n_records)
    credit_score = rng.integers(300, 850, n_records)
    num_dependents = rng.integers(0, 7, n_records)
    has_collateral = rng.choice(["Yes", "No"], n_records, p=[0.45, 0.55])
    education_level = rng.choice(
        ["Primary", "Secondary", "Tertiary", "Graduate"],
        n_records,
        p=[0.10, 0.35, 0.40, 0.15],
    )
    loan_term_months = rng.choice([6, 12, 24, 36, 48, 60], n_records)

    debt_to_income = loan_amount_ksh / (income_ksh * loan_term_months + 1)
    collateral_bonus = np.where(has_collateral == "Yes", -0.8, 0.0)
    education_bonus = np.select(
        [
            education_level == "Graduate",
            education_level == "Tertiary",
            education_level == "Secondary",
        ],
        [-0.6, -0.3, -0.1],
        default=0.4,
    )

    default_logit = (
        0.9 * debt_to_income
        + 0.004 * (650 - credit_score)
        + 0.03 * num_dependents
        - 0.04 * employment_years
        - 0.008 * (age - 35)
        + collateral_bonus
        + education_bonus
        + rng.normal(0, 0.35, n_records)
    )
    default_prob = 1 / (1 + np.exp(-default_logit))

    target_rate = 0.30
    threshold = np.quantile(default_prob, 1 - target_rate)
    default = np.where(default_prob >= threshold, "Yes", "No")

    return pd.DataFrame(
        {
            "applicant_id": [f"APP{i:03d}" for i in range(1, n_records + 1)],
            "age": age,
            "income_ksh": income_ksh,
            "loan_amount_ksh": loan_amount_ksh,
            "employment_years": employment_years,
            "credit_score": credit_score,
            "num_dependents": num_dependents,
            "has_collateral": has_collateral,
            "education_level": education_level,
            "loan_term_months": loan_term_months,
            "default": default,
        }
    )


if __name__ == "__main__":
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)
    df = generate_loan_dataset()
    path = data_dir / "loans.csv"
    df.to_csv(path, index=False)
    default_rate = (df["default"] == "Yes").mean()
    print(f"Saved {len(df)} records to {path}")
    print(f"Default rate: {default_rate:.1%}")
