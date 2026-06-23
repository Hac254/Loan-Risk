"""Loan default risk prediction using KNN and Naive Bayes."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler


@dataclass
class EvaluationResult:
    """Container for model evaluation metrics."""

    model_name: str
    accuracy: float
    f1: float
    report: str
    confusion: np.ndarray
    best_k: int | None = None


class LoanRiskPredictor:
    """Predict loan default risk for Kenyan bank applicants."""

    NUMERIC_FEATURES = [
        "age",
        "income_ksh",
        "loan_amount_ksh",
        "employment_years",
        "credit_score",
        "num_dependents",
        "loan_term_months",
    ]
    CATEGORICAL_FEATURES = ["has_collateral", "education_level"]
    TARGET = "default"

    def __init__(self, data_path: str | Path) -> None:
        self.data_path = Path(data_path)
        self.raw_df: pd.DataFrame | None = None
        self.processed_df: pd.DataFrame | None = None
        self.feature_columns: list[str] = []
        self.label_encoder = LabelEncoder()
        self.scaler = StandardScaler()
        self.models: dict[str, Any] = {}
        self.x_train: np.ndarray | None = None
        self.x_test: np.ndarray | None = None
        self.y_train: np.ndarray | None = None
        self.y_test: np.ndarray | None = None
        self.evaluation_results: dict[str, EvaluationResult] = {}
        self.best_k: int = 5

    def load_data(self) -> pd.DataFrame:
        """Load loan records from CSV."""
        self.raw_df = pd.read_csv(self.data_path)
        return self.raw_df

    def preprocess(self, test_size: float = 0.25, random_state: int = 42) -> tuple:
        """Encode categoricals, scale numerics, and split train/test."""
        if self.raw_df is None:
            self.load_data()

        df = self.raw_df.copy()
        df["has_collateral"] = (df["has_collateral"] == "Yes").astype(int)

        education_map = {
            "Primary": 0,
            "Secondary": 1,
            "Tertiary": 2,
            "Graduate": 3,
        }
        df["education_level"] = df["education_level"].map(education_map)

        self.feature_columns = self.NUMERIC_FEATURES + [
            "has_collateral",
            "education_level",
        ]
        self.processed_df = df

        x = df[self.feature_columns].values
        y = self.label_encoder.fit_transform(df[self.TARGET])

        x_scaled = self.scaler.fit_transform(x)
        split = train_test_split(
            x_scaled,
            y,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        )
        self.x_train, self.x_test, self.y_train, self.y_test = split
        return split

    def train(self, model_type: str = "knn") -> Any:
        """Train KNN (with CV tuning) or Gaussian Naive Bayes."""
        if self.x_train is None:
            self.preprocess()

        model_type = model_type.lower()
        if model_type == "knn":
            param_grid = {"n_neighbors": list(range(1, 21))}
            grid = GridSearchCV(
                KNeighborsClassifier(),
                param_grid,
                cv=5,
                scoring="f1",
            )
            grid.fit(self.x_train, self.y_train)
            model = grid.best_estimator_
            self.best_k = int(grid.best_params_["n_neighbors"])
            self.models["knn"] = model
            return model

        if model_type in {"nb", "naive_bayes", "gaussian_nb"}:
            model = GaussianNB()
            model.fit(self.x_train, self.y_train)
            self.models["naive_bayes"] = model
            return model

        raise ValueError(f"Unsupported model_type: {model_type}")

    def predict(self, applicant: dict[str, Any]) -> dict[str, Any]:
        """Predict default risk for a single applicant."""
        if "knn" not in self.models:
            self.train("knn")

        education_map = {
            "Primary": 0,
            "Secondary": 1,
            "Tertiary": 2,
            "Graduate": 3,
        }

        row = {
            "age": float(applicant["age"]),
            "income_ksh": float(applicant["income_ksh"]),
            "loan_amount_ksh": float(applicant["loan_amount_ksh"]),
            "employment_years": float(applicant["employment_years"]),
            "credit_score": float(applicant["credit_score"]),
            "num_dependents": float(applicant["num_dependents"]),
            "loan_term_months": float(applicant["loan_term_months"]),
            "has_collateral": 1 if applicant["has_collateral"] == "Yes" else 0,
            "education_level": education_map[applicant["education_level"]],
        }

        features = np.array([[row[col] for col in self.feature_columns]])
        features_scaled = self.scaler.transform(features)

        model = self.models["knn"]
        prediction = model.predict(features_scaled)[0]
        probabilities = model.predict_proba(features_scaled)[0]
        default_idx = list(self.label_encoder.classes_).index("Yes")
        default_prob = float(probabilities[default_idx])

        if default_prob < 0.35:
            risk_rating = "Low"
        elif default_prob < 0.65:
            risk_rating = "Medium"
        else:
            risk_rating = "High"

        label = self.label_encoder.inverse_transform([prediction])[0]
        return {
            "default_prediction": label,
            "default_probability": round(default_prob, 4),
            "risk_rating": risk_rating,
            "recommendation": (
                "Approve with standard terms"
                if risk_rating == "Low"
                else "Approve with enhanced monitoring"
                if risk_rating == "Medium"
                else "Decline or require collateral/guarantor"
            ),
        }

    def evaluate(self, model_type: str = "knn") -> EvaluationResult:
        """Evaluate a trained model on the held-out test set."""
        if self.x_test is None:
            self.preprocess()

        key = "knn" if model_type.lower() == "knn" else "naive_bayes"
        if key not in self.models:
            self.train(model_type)

        model = self.models[key]
        y_pred = model.predict(self.x_test)
        accuracy = accuracy_score(self.y_test, y_pred)
        f1 = f1_score(self.y_test, y_pred, pos_label=1)
        report = classification_report(
            self.y_test,
            y_pred,
            target_names=list(self.label_encoder.classes_),
        )
        confusion = confusion_matrix(self.y_test, y_pred)

        result = EvaluationResult(
            model_name=key,
            accuracy=accuracy,
            f1=f1,
            report=report,
            confusion=confusion,
            best_k=self.best_k if key == "knn" else None,
        )
        self.evaluation_results[key] = result
        return result

    def cross_validate_knn(self) -> pd.DataFrame:
        """Return mean CV scores for K values 1-20."""
        if self.x_train is None:
            self.preprocess()

        rows = []
        for k in range(1, 21):
            model = KNeighborsClassifier(n_neighbors=k)
            scores = cross_val_score(
                model,
                self.x_train,
                self.y_train,
                cv=5,=
                scoring="f1",
            )
            rows.append({"k": k, "mean_f1": scores.mean(), "std_f1": scores.std()})

        return pd.DataFrame(rows)
