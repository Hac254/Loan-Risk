# Project 09 — Loan Default Risk Predictor

A diploma capstone project that predicts loan default risk in a **Kenyan banking context**. It generates synthetic applicant data, trains **K-Nearest Neighbours (KNN)** and **Gaussian Naive Bayes** classifiers, produces analytics charts, and offers an interactive **bank officer CLI** for single-applicant risk assessment.

---

## What This Project Does

1. **Data** — Creates or loads 200 synthetic loan records (`data/loans.csv`) with features such as age, monthly income (KSh), loan amount, credit score, collateral, education, and a `default` label (~30% default rate).
2. **Machine learning** — The `LoanRiskPredictor` class loads data, preprocesses features, tunes KNN (K = 1–20 via 5-fold cross-validation), trains Naive Bayes, and evaluates both models.
3. **Visualisations** — Saves seven PNG charts to `outputs/` (correlation heatmap, default distribution, credit score box plot, KNN tuning curve, confusion matrices, model comparison, default rate by loan bracket).
4. **Decision support** — Predicts default probability and assigns a **Low / Medium / High** risk rating with a lending recommendation.

Additional materials in this folder include written reports (`reports/`), a separate OOP student grading demo (`reports/Student.py`), legacy/alternate Python scripts, and static HTML mock-ups for a web UI (no backend included).

---

## Project Structure

Use the **root folder** `project_09_loan_risk` as the working directory. Ignore duplicate nested copies (`project_09_loan_risk/project_09_loan_risk/`, `project_09_loan_risk - Copy/`) — they are redundant backups.

```
project_09_loan_risk/
├── main.py                    # Primary entry point (recommended)
├── loan_risk_predictor.py     # LoanRiskPredictor OOP class
├── generate_dataset.py        # Synthetic CSV generator
├── requirements.txt           # Python dependencies
├── data/
│   └── loans.csv              # Loan records (auto-generated if missing)
├── outputs/                   # Generated charts (PNG)
├── reports/
│   ├── REPORT.md              # Technical project report
│   ├── FINANCE_ESSAY.md       # Finance theory essay
│   └── Student.py             # Separate OOP student report-card demo
├── app.py                     # Flask web server (see WEB_GUIDE.md)
├── templates/                 # Working web UI templates
├── static/                    # CSS and chart assets for web UI
└── .vscode/launch.json        # VS Code Chrome debug config (localhost:8080)
```

---

## Prerequisites

- **Python 3.10+** (tested on Python 3.13)
- **pip** package manager
- Internet not required after dependencies are installed

---

## Setup

Open a terminal in the project root:

```powershell
cd c:\Users\PC\Downloads\project_09_loan_risk
pip install -r requirements.txt
```

Dependencies: `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`.

---

## How to Run Successfully

### 1. Main pipeline (recommended)

**Batch mode** — trains models, evaluates them, and saves charts without prompting for input:

```powershell
cd c:\Users\PC\Downloads\project_09_loan_risk
$env:MPLBACKEND = "Agg"
python main.py --batch
```

**Interactive mode** — same as above, then opens the bank officer CLI to assess one applicant:

```powershell
python main.py
```

You will be prompted for applicant details (age, income, loan amount, credit score, etc.). Example inputs:

| Prompt | Example |
|--------|---------|
| Age | `34` |
| Monthly income (KSh) | `85000` |
| Loan amount (KSh) | `500000` |
| Employment years | `5` |
| Credit score | `680` |
| Dependents | `2` |
| Collateral | `Yes` or `No` |
| Education | `Secondary`, `Tertiary`, or `Graduate` |
| Loan term (months) | `24` |

Expected output includes model accuracy/F1 scores and a line such as:

```
Saved visualisations to ...\outputs
Batch mode complete.
```

Charts appear in `outputs/`.

### 2. Regenerate dataset only

```powershell
python generate_dataset.py
```

Creates/overwrites `data/loans.csv` with 200 records.

### 3. Student OOP demo (separate exercise)

```powershell
python reports\Student.py
```

Prints report cards for five students, ranks best/weakest, and demonstrates validation (invalid marks raise `ValueError`).

### 4. Legacy script (optional)

`import numpy as np.py` is an **older standalone version** with a different dataset schema (gender, employment status, credit history, etc.). It runs independently but is **not** used by `main.py`:

```powershell
$env:MPLBACKEND = "Agg"
python "import numpy as np.py"
```

This script ends in an interactive loop; type `exit` at the first prompt to quit.

---

## File Review Summary

| File | Status | Notes |
|------|--------|-------|
| `main.py` | OK | Runs successfully with `--batch` and interactive CLI |
| `loan_risk_predictor.py` | Fixed | Syntax error on line 231 (`cv=5,=`) corrected to `cv=5,` |
| `generate_dataset.py` | OK | Generates CSV with ~30% default rate |
| `data/loans.csv` | OK | 200 records, valid CSV |
| `reports/Student.py` | Fixed | Truncated last line completed (`get_total_students()`) |
| `reports/REPORT.md` | OK | Technical documentation |
| `reports/FINANCE_ESSAY.md` | OK | Finance essay |
| `import numpy as np.py` | OK | Runs on Windows after Unicode checkmarks replaced with `[OK]` |
| `website.html` | Legacy mock-up | Use `http://127.0.0.1:5000/` after running `python app.py` |
| `frontend.html` | Legacy mock-up | Use `http://127.0.0.1:5000/dashboard` after login |
| `app.py` + `templates/` | OK | Full working web UI — see **WEB_GUIDE.md** |
| `frontend.css`, `styles.css` | OK | Styles only |
| `.vscode/launch.json` | OK | Opens Chrome at `http://localhost:8080` (needs a web server) |
| `outputs/*.png` | OK | Generated by `main.py --batch` |
| Nested duplicate folders | Ignore | Redundant copies of the same files |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` for pandas/sklearn | Run `pip install -r requirements.txt` |
| Matplotlib hangs or is slow on first run | Set `$env:MPLBACKEND = "Agg"` before running |
| `UnicodeEncodeError` on Windows | Use the updated scripts; or run `$env:PYTHONIOENCODING = "utf-8"` |
| `website.html` shows "Connection failure" | Expected — open the file directly in a browser; there is no `/predict` API |
| Seaborn `FutureWarning` about `palette` | Harmless warning in `main.py`; does not affect results |

---

## Model Output (example)

After a successful batch run you should see metrics similar to:

- **KNN** — ~82% accuracy, F1 ~0.61, best K ≈ 11  
- **Naive Bayes** — ~78% accuracy, F1 ~0.59  

Exact numbers vary slightly with the random seed baked into the dataset generator.

---

## Risk Rating Logic

| Default probability | Rating | Recommendation |
|--------------------|--------|----------------|
| &lt; 35% | Low | Approve with standard terms |
| 35% – 65% | Medium | Approve with enhanced monitoring |
| ≥ 65% | High | Decline or require collateral/guarantor |

---

## Further Reading

- [GITHUB_AND_LOCAL_SETUP.md](GITHUB_AND_LOCAL_SETUP.md) — upload to GitHub and run locally from a clone
- [WEB_GUIDE.md](WEB_GUIDE.md) — web UI setup and browser usage
- `reports/REPORT.md` — methodology, architecture, learning outcomes  
- `reports/FINANCE_ESSAY.md` — Kenyan lending and credit risk theory  

---

## Quick Start (copy-paste)

```powershell
cd c:\Users\PC\Downloads\project_09_loan_risk
pip install -r requirements.txt
$env:MPLBACKEND = "Agg"
python main.py --batch
```

Then open `outputs/` to view the generated charts.

### Web UI

See **[WEB_GUIDE.md](WEB_GUIDE.md)** for full step-by-step instructions.

```powershell
pip install -r requirements.txt
$env:MPLBACKEND = "Agg"
python main.py --batch
python app.py
```

Open **http://127.0.0.1:5000/** in your browser.
