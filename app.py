"""Flask web server for the Loan Default Risk Predictor."""

from __future__ import annotations

import shutil
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from sklearn.metrics import classification_report

from generate_dataset import generate_loan_dataset
from loan_risk_predictor import LoanRiskPredictor

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "data" / "loans.csv"
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_VIZ_DIR = BASE_DIR / "static" / "visualisations"

USERS = {
    "officer": {"password": "officer123", "role": "officer", "display_name": "Bank Officer"},
    "admin": {"password": "admin123", "role": "admin", "display_name": "Risk Admin"},
}

app = Flask(__name__)
app.secret_key = "loan-risk-dev-key-change-in-production"

_predictor: LoanRiskPredictor | None = None


def get_predictor() -> LoanRiskPredictor:
    """Load, train, and cache the ML predictor."""
    global _predictor
    if _predictor is None:
        if not DATA_PATH.exists():
            DATA_PATH.parent.mkdir(exist_ok=True)
            generate_loan_dataset().to_csv(DATA_PATH, index=False)

        _predictor = LoanRiskPredictor(DATA_PATH)
        _predictor.load_data()
        _predictor.preprocess()
        _predictor.train("knn")
        _predictor.train("naive_bayes")
        _predictor.evaluate("knn")
        _predictor.evaluate("naive_bayes")
        sync_visualisations()
    return _predictor


def sync_visualisations() -> None:
    """Copy chart PNGs from outputs/ to static/visualisations/."""
    STATIC_VIZ_DIR.mkdir(parents=True, exist_ok=True)
    chart_map = {
        "correlation_heatmap.png": "correlation_heatmap.png",
        "knn_k_tuning.png": "knn_k_tuning.png",
        "model_comparison.png": "model_comparison.png",
        "default_distribution.png": "risk_distribution.png",
        "model_confusion_matrices.png": "model_confusion_matrices.png",
        "credit_score_by_default.png": "credit_score_by_default.png",
        "default_by_loan_bracket.png": "default_by_loan_bracket.png",
    }
    for source_name, dest_name in chart_map.items():
        source = OUTPUT_DIR / source_name
        if source.exists():
            shutil.copy2(source, STATIC_VIZ_DIR / dest_name)


def build_metrics() -> dict:
    """Build template-friendly metrics for the admin dashboard."""
    predictor = get_predictor()
    metrics: dict = {}

    for key, label in [("knn", "KNN"), ("naive_bayes", "Naive Bayes")]:
        model = predictor.models[key]
        y_pred = model.predict(predictor.x_test)
        report = classification_report(
            predictor.y_test,
            y_pred,
            target_names=list(predictor.label_encoder.classes_),
            output_dict=True,
            zero_division=0,
        )
        no_stats = report.get("No", {})
        yes_stats = report.get("Yes", {})
        metrics[label] = {
            "accuracy": predictor.evaluation_results[key].accuracy,
            "report": {
                "0": {
                    "precision": no_stats.get("precision", 0),
                    "recall": no_stats.get("recall", 0),
                    "f1-score": no_stats.get("f1-score", 0),
                },
                "1": {
                    "precision": yes_stats.get("precision", 0),
                    "recall": yes_stats.get("recall", 0),
                    "f1-score": yes_stats.get("f1-score", 0),
                },
            },
        }
    return metrics


def parse_applicant_form(form) -> dict:
    """Parse and validate applicant fields from a form submission."""
    education = form.get("education_level", "Secondary").strip().capitalize()
    collateral = form.get("has_collateral", "No").strip().capitalize()
    if collateral not in {"Yes", "No"}:
        collateral = "No"

    return {
        "age": int(form["age"]),
        "income_ksh": float(form["income_ksh"]),
        "loan_amount_ksh": float(form["loan_amount_ksh"]),
        "employment_years": int(form["employment_years"]),
        "credit_score": int(form["credit_score"]),
        "num_dependents": int(form["num_dependents"]),
        "has_collateral": collateral,
        "education_level": education,
        "loan_term_months": int(form["loan_term_months"]),
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user" not in session:
            flash("Please log in to access the bank officer portal.", "danger")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def index():
    """Public loan risk assessment page."""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict_api():
    """JSON prediction endpoint for the public UI."""
    try:
        applicant = parse_applicant_form(request.form)
        result = get_predictor().predict(applicant)
        default_prob = result["default_probability"]
        approval_prob = 1 - default_prob
        approved = result["default_prediction"] == "No"

        return jsonify(
            {
                "success": True,
                "approved": approved,
                "probability": approval_prob,
                "confidence": max(default_prob, approval_prob) * 100,
                "message": (
                    f"{result['risk_rating']} risk — {result['recommendation']}"
                ),
                "default_prediction": result["default_prediction"],
                "default_probability": default_prob,
                "risk_rating": result["risk_rating"],
                "recommendation": result["recommendation"],
            }
        )
    except (KeyError, ValueError, TypeError) as exc:
        return jsonify({"success": False, "error": str(exc)}), 400


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        account = USERS.get(username)

        if account and account["password"] == password:
            session["user"] = account["display_name"]
            session["username"] = username
            session["role"] = account["role"]
            flash(f"Welcome, {account['display_name']}.", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    metrics = build_metrics() if session.get("role") == "admin" else None
    return render_template(
        "dashboard.html",
        user=session.get("user", "Officer"),
        metrics=metrics,
    )


@app.route("/dashboard/predict", methods=["POST"])
@login_required
def dashboard_predict():
    try:
        applicant = parse_applicant_form(request.form)
        result = get_predictor().predict(applicant)
        flash(
            (
                f"Assessment complete — Prediction: {result['default_prediction']} | "
                f"Default probability: {result['default_probability']:.1%} | "
                f"Risk: {result['risk_rating']} | "
                f"Recommendation: {result['recommendation']}"
            ),
            "success" if result["risk_rating"] == "Low" else "danger",
        )
    except (KeyError, ValueError, TypeError) as exc:
        flash(f"Invalid form data: {exc}", "danger")

    return redirect(url_for("dashboard"))


@app.route("/download_data")
@login_required
def download_data():
    if session.get("role") != "admin":
        flash("Only administrators can download the dataset.", "danger")
        return redirect(url_for("dashboard"))

    if not DATA_PATH.exists():
        generate_loan_dataset().to_csv(DATA_PATH, index=False)

    return send_file(DATA_PATH, as_attachment=True, download_name="loans.csv")


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    if not OUTPUT_DIR.exists() or not any(OUTPUT_DIR.glob("*.png")):
        from main import create_visualisations

        OUTPUT_DIR.mkdir(exist_ok=True)
        predictor = get_predictor()
        create_visualisations(predictor, OUTPUT_DIR)

    print("Starting LoanRisk web server at http://127.0.0.1:5000")
    print("Public UI:  http://127.0.0.1:5000/")
    print("Portal login: http://127.0.0.1:5000/login")
    app.run(debug=True, host="127.0.0.1", port=5000)
