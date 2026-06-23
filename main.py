"""Project 9: Loan Default Risk Predictor — Kenyan banking context."""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from generate_dataset import generate_loan_dataset
from loan_risk_predictor import LoanRiskPredictor


def create_visualisations(predictor: LoanRiskPredictor, output_dir: Path) -> None:
    """Generate four or more analysis charts."""
    df = predictor.raw_df
    sns.set_theme(style="whitegrid")

    numeric_cols = predictor.NUMERIC_FEATURES + ["default"]
    encoded = df.copy()
    encoded["default"] = (encoded["default"] == "Yes").astype(int)
    encoded["has_collateral"] = (encoded["has_collateral"] == "Yes").astype(int)
    education_map = {
        "Primary": 0,
        "Secondary": 1,
        "Tertiary": 2,
        "Graduate": 3,
    }
    encoded["education_level"] = encoded["education_level"].map(education_map)

    corr_cols = predictor.NUMERIC_FEATURES + ["has_collateral", "education_level", "default"]
    corr = encoded[corr_cols].corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdYlGn_r", ax=ax)
    ax.set_title("Feature Correlation Heatmap")
    fig.tight_layout()
    fig.savefig(output_dir / "correlation_heatmap.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    default_counts = df["default"].value_counts()
    colors = ["#2ecc71", "#e74c3c"]
    ax.pie(
        default_counts.values,
        labels=default_counts.index,
        autopct="%1.1f%%",
        colors=colors,
        startangle=90,
    )
    ax.set_title("Loan Default Distribution")
    fig.savefig(output_dir / "default_distribution.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    df["default_flag"] = (df["default"] == "Yes").astype(int)
    sns.boxplot(data=df, x="default", y="credit_score", palette="Set2", ax=ax)
    ax.set_title("Credit Score by Default Status")
    ax.set_xlabel("Default")
    fig.tight_layout()
    fig.savefig(output_dir / "credit_score_by_default.png", dpi=150)
    plt.close(fig)

    cv_df = predictor.cross_validate_knn()
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.errorbar(
        cv_df["k"],
        cv_df["mean_f1"],
        yerr=cv_df["std_f1"],
        marker="o",
        capsize=3,
        color="#3498db",
    )
    ax.axvline(predictor.best_k, color="#e74c3c", linestyle="--", label=f"Best K={predictor.best_k}")
    ax.set_xlabel("K (Number of Neighbours)")
    ax.set_ylabel("Mean F1 Score (5-fold CV)")
    ax.set_title("KNN Cross-Validation: Tuning K")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "knn_k_tuning.png", dpi=150)
    plt.close(fig)

    knn_result = predictor.evaluation_results.get("knn")
    nb_result = predictor.evaluation_results.get("naive_bayes")
    if knn_result and nb_result:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4))
        for ax, result, title in zip(
            axes,
            [knn_result, nb_result],
            ["KNN Confusion Matrix", "Naive Bayes Confusion Matrix"],
        ):
            sns.heatmap(
                result.confusion,
                annot=True,
                fmt="d",
                cmap="Blues",
                xticklabels=["No", "Yes"],
                yticklabels=["No", "Yes"],
                ax=ax,
            )
            ax.set_xlabel("Predicted")
            ax.set_ylabel("Actual")
            ax.set_title(title)
        fig.tight_layout()
        fig.savefig(output_dir / "model_confusion_matrices.png", dpi=150)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(7, 5))
        names = ["KNN", "Naive Bayes"]
        accuracies = [knn_result.accuracy, nb_result.accuracy]
        f1_scores = [knn_result.f1, nb_result.f1]
        x = np.arange(len(names))
        width = 0.35
        ax.bar(x - width / 2, accuracies, width, label="Accuracy", color="#3498db")
        ax.bar(x + width / 2, f1_scores, width, label="F1 Score", color="#9b59b6")
        ax.set_xticks(x)
        ax.set_xticklabels(names)
        ax.set_ylim(0, 1)
        ax.set_title("Model Comparison: KNN vs Naive Bayes")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output_dir / "model_comparison.png", dpi=150)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    df["loan_bracket"] = pd.cut(
        df["loan_amount_ksh"],
        bins=[0, 250_000, 500_000, 1_000_000, 2_500_000],
        labels=["<250K", "250-500K", "500K-1M", ">1M"],
    )
    default_by_bracket = df.groupby("loan_bracket", observed=True)["default"].apply(
        lambda s: (s == "Yes").mean()
    )
    default_by_bracket.plot(kind="bar", color="#e67e22", ax=ax)
    ax.set_title("Default Rate by Loan Amount Bracket (KSh)")
    ax.set_ylabel("Default Rate")
    ax.set_xlabel("Loan Bracket")
    plt.xticks(rotation=0)
    fig.tight_layout()
    fig.savefig(output_dir / "default_by_loan_bracket.png", dpi=150)
    plt.close(fig)

    print(f"\nSaved visualisations to {output_dir}")


def run_bank_officer_cli(predictor: LoanRiskPredictor) -> None:
    """Interactive CLI for bank officers to assess applicant risk."""
    print("\n=== Bank Officer Loan Risk Assessment ===")
    print("Enter applicant details (or press Enter to skip and exit).\n")

    try:
        age = int(input("Age (22-65): ").strip())
        income_ksh = float(input("Monthly income (KSh): ").strip())
        loan_amount_ksh = float(input("Requested loan amount (KSh): ").strip())
        employment_years = int(input("Years of employment: ").strip())
        credit_score = int(input("Credit score (300-850): ").strip())
        num_dependents = int(input("Number of dependents: ").strip())
        has_collateral = input("Has collateral? (Yes/No): ").strip().capitalize()
        education_level = input(
            "Education (Primary/Secondary/Tertiary/Graduate): "
        ).strip().capitalize()
        loan_term_months = int(input("Loan term in months: ").strip())
    except (ValueError, EOFError):
        print("Invalid input. Exiting CLI.")
        return

    applicant = {
        "age": age,
        "income_ksh": income_ksh,
        "loan_amount_ksh": loan_amount_ksh,
        "employment_years": employment_years,
        "credit_score": credit_score,
        "num_dependents": num_dependents,
        "has_collateral": has_collateral,
        "education_level": education_level,
        "loan_term_months": loan_term_months,
    }

    result = predictor.predict(applicant)
    print("\n--- Risk Assessment Result ---")
    print(f"Default prediction : {result['default_prediction']}")
    print(f"Default probability: {result['default_probability']:.2%}")
    print(f"Risk rating        : {result['risk_rating']}")
    print(f"Recommendation     : {result['recommendation']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Loan Default Risk Predictor")
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Train and generate charts only (skip interactive CLI)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = Path(__file__).parent
    data_path = base / "data" / "loans.csv"
    output_dir = base / "outputs"
    output_dir.mkdir(exist_ok=True)

    if not data_path.exists():
        generate_loan_dataset().to_csv(data_path, index=False)

    predictor = LoanRiskPredictor(data_path)
    df = predictor.load_data()
    default_rate = (df["default"] == "Yes").mean()
    print(f"Loaded {len(df)} loan records (default rate: {default_rate:.1%})")

    predictor.preprocess()
    predictor.train("knn")
    predictor.train("naive_bayes")

    print("\n=== Model Evaluation ===")
    for model_type in ("knn", "naive_bayes"):
        result = predictor.evaluate(model_type)
        print(f"\n{result.model_name.upper()} — Accuracy: {result.accuracy:.2%}, F1: {result.f1:.3f}")
        if result.best_k:
            print(f"Best K: {result.best_k}")
        print(result.report)

    create_visualisations(predictor, output_dir)

    if args.batch:
        print("\nBatch mode complete. See reports/FINANCE_ESSAY.md and reports/REPORT.md.")
        return

    run_bank_officer_cli(predictor)
    print("\nSee reports/FINANCE_ESSAY.md and reports/REPORT.md for documentation.")


if __name__ == "__main__":
    main()
