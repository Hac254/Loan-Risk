# Web View Setup Guide — LoanRisk AI

This guide walks you through running the **Flask web server** that powers the loan risk assessment UI. The web app connects the existing HTML interfaces to the trained `LoanRiskPredictor` model.

---

## What You Get

| URL | Page | Description |
|-----|------|-------------|
| `http://127.0.0.1:5000/` | Public assessment | Fill a form, get instant JSON-powered risk result (no login) |
| `http://127.0.0.1:5000/login` | Bank portal login | Sign in as bank officer or admin |
| `http://127.0.0.1:5000/dashboard` | Officer dashboard | Submit applicants and view flash-message results |
| `http://127.0.0.1:5000/download_data` | CSV export | Admin-only download of `data/loans.csv` |

**Demo login credentials:**

| Role | Username | Password |
|------|----------|----------|
| Bank Officer | `officer` | `officer123` |
| Admin (charts + metrics) | `admin` | `admin123` |

---

## Architecture Overview

```
Browser (HTML + JavaScript)
        │
        ▼
   app.py  (Flask server on port 5000)
        │
        ├── /predict          → LoanRiskPredictor.predict()
        ├── /dashboard/predict → same model, form POST
        └── static/visualisations/ ← charts copied from outputs/
        │
        ▼
   loan_risk_predictor.py + data/loans.csv
```

The old root-level `website.html` and `frontend.html` files were **static mock-ups**. The working web UI now lives in:

- `templates/index.html` — public page (replaces `website.html`)
- `templates/dashboard.html` — portal page (replaces `frontend.html`)
- `templates/login.html` — login screen
- `app.py` — Flask backend

---

## Step-by-Step Instructions

### Step 1 — Open a terminal in the project folder

**PowerShell (Windows):**

```powershell
cd c:\Users\PC\Downloads\project_09_loan_risk
```

**Command Prompt:**

```cmd
cd c:\Users\PC\Downloads\project_09_loan_risk
```

**macOS / Linux:**

```bash
cd /path/to/project_09_loan_risk
```

---

### Step 2 — Install Python dependencies

Install all packages including Flask:

```powershell
pip install -r requirements.txt
```

Expected packages: `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`, `flask`.

Verify Flask installed:

```powershell
python -c "import flask; print(flask.__version__)"
```

---

### Step 3 — Generate charts (first run only)

The admin dashboard displays PNG charts. Generate them once if `outputs/` is empty:

```powershell
$env:MPLBACKEND = "Agg"
python main.py --batch
```

You should see `Saved visualisations to ...\outputs`. The Flask app copies these into `static/visualisations/` automatically on startup.

---

### Step 4 — Start the Flask web server

```powershell
python app.py
```

Expected console output:

```
Starting LoanRisk web server at http://127.0.0.1:5000
Public UI:  http://127.0.0.1:5000/
Portal login: http://127.0.0.1:5000/login
 * Running on http://127.0.0.1:5000
```

**Keep this terminal open** while using the web app. Press `Ctrl+C` to stop the server.

> **Alternative:** `flask --app app run --debug` also works if you prefer the Flask CLI.

---

### Step 5 — Open the public assessment page

1. Open your browser (Chrome, Edge, or Firefox).
2. Go to: **http://127.0.0.1:5000/**
3. Fill in the applicant form with sample values:

| Field | Example value |
|-------|---------------|
| Age | `34` |
| Monthly Income (KSh) | `85000` |
| Employment Duration | `5` |
| Loan Amount (KSh) | `500000` |
| Credit Score | `680` |
| Dependents | `2` |
| Collateral | `No` |
| Education | `Tertiary` |
| Loan Term | `24` months |

4. Click **Analyze Application**.
5. The right panel shows:
   - **Approved** or **High Risk** badge
   - Risk message and recommendation
   - Approval likelihood percentage
   - Model confidence

If you see *"Connection failure interacting with the core engine"*, the Flask server is not running — return to Step 4.

---

### Step 6 — Use the bank officer portal

1. Go to: **http://127.0.0.1:5000/login**
2. Sign in with `officer` / `officer123`.
3. You are redirected to **http://127.0.0.1:5000/dashboard**.
4. Submit an applicant using the same fields as Step 5.
5. A green or red banner at the top shows the assessment result (prediction, probability, risk rating, recommendation).

---

### Step 7 — View the admin dashboard (optional)

1. Log out (click **Exit** in the nav bar).
2. Log in with `admin` / `admin123`.
3. The dashboard now includes:
   - **Model Performance Dashboard** — KNN vs Naive Bayes precision/recall/F1 tables
   - **Model Training Visualisations** — correlation heatmap, KNN tuning, model comparison, default distribution
   - **Export Dataset CSV** button

---

### Step 8 — Verify the API directly (optional)

Test the `/predict` endpoint from PowerShell:

```powershell
curl -X POST http://127.0.0.1:5000/predict `
  -F "age=34" `
  -F "income_ksh=85000" `
  -F "loan_amount_ksh=500000" `
  -F "employment_years=5" `
  -F "credit_score=680" `
  -F "num_dependents=2" `
  -F "has_collateral=No" `
  -F "education_level=Tertiary" `
  -F "loan_term_months=24"
```

Expected JSON response (values will vary):

```json
{
  "success": true,
  "approved": true,
  "probability": 0.72,
  "confidence": 72.0,
  "message": "Low risk — Approve with standard terms",
  "risk_rating": "Low"
}
```

Health check:

```powershell
curl http://127.0.0.1:5000/health
```

---

## File Reference

| File | Purpose |
|------|---------|
| `app.py` | Flask server — routes, login, prediction API |
| `templates/index.html` | Public web UI |
| `templates/login.html` | Login page |
| `templates/dashboard.html` | Officer/admin portal |
| `static/frontend.css` | Portal styling |
| `static/visualisations/*.png` | Charts served to admin dashboard |
| `loan_risk_predictor.py` | ML model used by the server |
| `data/loans.csv` | Training dataset |

---

## Troubleshooting

### "Connection failure interacting with the core engine"

- **Cause:** Flask server is not running, or you opened `website.html` directly from disk (`file://`).
- **Fix:** Start the server with `python app.py` and use `http://127.0.0.1:5000/` — not the old HTML files.

### Port 5000 already in use

```powershell
# Find and stop the process using port 5000 (Windows)
netstat -ano | findstr :5000
```

Or change the port in `app.py` (last line): `app.run(debug=True, host="127.0.0.1", port=8080)`

### Charts missing on admin dashboard

Run batch mode first:

```powershell
$env:MPLBACKEND = "Agg"
python main.py --batch
```

Restart `python app.py` — charts are copied to `static/visualisations/` on startup.

### `ModuleNotFoundError: No module named 'flask'`

```powershell
pip install flask
```

Or reinstall all deps: `pip install -r requirements.txt`

### First startup is slow

The server trains KNN and Naive Bayes on first request (~10–30 seconds). Subsequent predictions are fast because the model is cached in memory.

### Matplotlib font cache warning

Harmless on first run. Set `$env:MPLBACKEND = "Agg"` before starting if you see display-related warnings.

---

## VS Code / Cursor Debug (optional)

Update `.vscode/launch.json` to launch Chrome against the Flask server:

1. Start the server: `python app.py`
2. Open **http://127.0.0.1:5000/** in the browser

Or add a compound launch configuration for server + browser debugging.

---

## Quick Start Cheat Sheet

Copy and paste this entire block:

```powershell
cd c:\Users\PC\Downloads\project_09_loan_risk
pip install -r requirements.txt
$env:MPLBACKEND = "Agg"
python main.py --batch
python app.py
```

Then open **http://127.0.0.1:5000/** in your browser.

---

## Security Note

Demo passwords (`officer123`, `admin123`) are for local development only. Do not deploy this configuration to production without changing `app.secret_key` and implementing proper authentication.
