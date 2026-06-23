# GitHub Upload & Local Setup Guide

This guide covers two workflows:

1. **Part A** — How to upload this project to GitHub (for the project owner)
2. **Part B** — How anyone can download the project and run it on their own machine

For project overview and feature documentation, see [README.md](README.md).  
For the web UI specifically, see [WEB_GUIDE.md](WEB_GUIDE.md).

---

## Before You Start

### What you need

| Tool | Purpose | Download |
|------|---------|----------|
| **Git** | Version control, push/pull code | https://git-scm.com/downloads |
| **GitHub account** | Host the repository online | https://github.com/signup |
| **Python 3.10+** | Run the project | https://www.python.org/downloads/ |
| **pip** | Install Python packages | Included with Python |

Verify installations:

```powershell
git --version
python --version
pip --version
```

On macOS/Linux, use `python3` and `pip3` if `python` points to Python 2.

---

# Part A — Upload the Project to GitHub

Follow these steps on the machine that currently has the project files.

---

## Step A1 — Clean up the project folder

Before uploading, work from the **root project folder** only:

```
project_09_loan_risk/
├── main.py
├── app.py
├── loan_risk_predictor.py
├── generate_dataset.py
├── requirements.txt
├── data/
├── templates/
├── static/
├── reports/
└── ...
```

**Delete or exclude** duplicate backup folders — they should not go to GitHub:

- `project_09_loan_risk - Copy/`
- `project_09_loan_risk/project_09_loan_risk/` (nested duplicate)

A `.gitignore` file is already included in the repo to ignore these automatically.

---

## Step A2 — Create a GitHub repository

1. Log in to **https://github.com**
2. Click the **+** icon (top-right) → **New repository**
3. Fill in:
   - **Repository name:** `project-09-loan-risk` (or any name you prefer)
   - **Description:** `Loan default risk predictor — Kenyan banking ML capstone`
   - **Visibility:** Public (so others can clone) or Private
   - **Do NOT** check "Add a README" — you already have one locally
4. Click **Create repository**

GitHub will show setup commands. Keep that page open.

---

## Step A3 — Initialize Git in your project folder

Open a terminal in the project root:

**Windows (PowerShell):**

```powershell
cd c:\Users\PC\Downloads\project_09_loan_risk
```

**macOS / Linux:**

```bash
cd ~/Downloads/project_09_loan_risk
```

Initialize Git and make the first commit:

```powershell
git init
git add .
git status
```

Review `git status` — you should see project files staged, but **not** `__pycache__/`, `.venv/`, or duplicate backup folders (they are in `.gitignore`).

Create the first commit:

```powershell
git commit -m "Initial commit: loan default risk predictor with CLI and web UI"
```

---

## Step A4 — Connect to GitHub and push

Replace `YOUR_USERNAME` and `YOUR_REPO` with your actual GitHub username and repository name.

**HTTPS (easiest for beginners):**

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

Example:

```powershell
git remote add origin https://github.com/janedoe/project-09-loan-risk.git
git push -u origin main
```

When prompted:

- **Username:** your GitHub username
- **Password:** use a **Personal Access Token** (not your GitHub password)  
  Create one at: https://github.com/settings/tokens → **Generate new token (classic)** → enable `repo` scope

**SSH (if you already have SSH keys set up):**

```powershell
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

---

## Step A5 — Verify the upload

1. Refresh your GitHub repository page in the browser
2. Confirm these files are visible:
   - `README.md`
   - `main.py`, `app.py`, `loan_risk_predictor.py`
   - `requirements.txt`
   - `templates/`, `reports/`, `data/`
3. Your repository URL will look like:

   ```
   https://github.com/YOUR_USERNAME/project-09-loan-risk
   ```

Share this URL with anyone who needs to download the project.

---

## Step A6 — Push future updates (optional)

After making changes locally:

```powershell
git add .
git commit -m "Describe what you changed"
git push
```

---

# Part B — Download and Run Locally (For Anyone)

Anyone with the GitHub link can follow these steps on **Windows, macOS, or Linux**.

---

## Step B1 — Get the project files

Choose **one** method:

### Option 1 — Git clone (recommended)

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

Example:

```powershell
git clone https://github.com/janedoe/project-09-loan-risk.git
cd project-09-loan-risk
```

### Option 2 — Download ZIP (no Git required)

1. Open the GitHub repository in your browser
2. Click the green **Code** button
3. Click **Download ZIP**
4. Extract the ZIP to a folder, e.g. `project_09_loan_risk`
5. Open a terminal in that folder:

   ```powershell
   cd path\to\project_09_loan_risk
   ```

---

## Step B2 — Install Python

1. Download Python from https://www.python.org/downloads/
2. During installation on **Windows**, check:
   - **Add Python to PATH**
3. Verify:

   ```powershell
   python --version
   ```

   Expected: `Python 3.10.x` or higher.

   On macOS/Linux if needed:

   ```bash
   python3 --version
   ```

---

## Step B3 — Create a virtual environment (recommended)

A virtual environment keeps project dependencies isolated.

**Windows (PowerShell):**

```powershell
cd path\to\project_09_loan_risk
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you get an execution policy error on Windows:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
cd path/to/project_09_loan_risk
python3 -m venv venv
source venv/bin/activate
```

Your prompt should show `(venv)` when the environment is active.

---

## Step B4 — Install dependencies

With the virtual environment activated:

```powershell
pip install -r requirements.txt
```

This installs: `numpy`, `pandas`, `matplotlib`, `seaborn`, `scikit-learn`, `flask`.

Verify key packages:

```powershell
python -c "import pandas, sklearn, flask; print('All packages OK')"
```

---

## Step B5 — Run the CLI (command-line version)

**Batch mode** — trains models and saves charts without prompts:

**Windows:**

```powershell
$env:MPLBACKEND = "Agg"
python main.py --batch
```

**macOS / Linux:**

```bash
export MPLBACKEND=Agg
python main.py --batch
```

**Expected output:**

```
Loaded 200 loan records (default rate: 30.0%)
=== Model Evaluation ===
KNN — Accuracy: ~82%
...
Saved visualisations to .../outputs
Batch mode complete.
```

Charts are saved in the `outputs/` folder.

**Interactive mode** — includes a bank officer prompt after training:

```powershell
python main.py
```

---

## Step B6 — Run the web UI in a browser

1. Generate charts first (if not done in Step B5):

   **Windows:**

   ```powershell
   $env:MPLBACKEND = "Agg"
   python main.py --batch
   ```

   **macOS / Linux:**

   ```bash
   export MPLBACKEND=Agg
   python main.py --batch
   ```

2. Start the Flask web server:

   ```powershell
   python app.py
   ```

3. Open your browser and go to:

   | Page | URL |
   |------|-----|
   | Public risk assessment | http://127.0.0.1:5000/ |
   | Bank portal login | http://127.0.0.1:5000/login |

4. **Demo login credentials:**

   | Role | Username | Password |
   |------|----------|----------|
   | Bank Officer | `officer` | `officer123` |
   | Admin (charts + metrics) | `admin` | `admin123` |

5. On the public page, fill in the form and click **Analyze Application** to see the risk result.

6. Press `Ctrl+C` in the terminal to stop the server when finished.

> **Important:** Do not open `website.html` or `frontend.html` directly from the file explorer. Those are legacy static files. Always use `http://127.0.0.1:5000/` after starting `python app.py`.

See [WEB_GUIDE.md](WEB_GUIDE.md) for more web UI details.

---

## Step B7 — Confirm everything works

Use this checklist:

- [ ] `python main.py --batch` completes without errors
- [ ] PNG files appear in `outputs/`
- [ ] `python app.py` starts and shows `Running on http://127.0.0.1:5000`
- [ ] Browser opens http://127.0.0.1:5000/ and the form loads
- [ ] Clicking **Analyze Application** shows a risk result (not a connection error)
- [ ] Login at http://127.0.0.1:5000/login works with demo credentials

---

# Troubleshooting

## Git / GitHub issues

| Problem | Solution |
|---------|----------|
| `git: command not found` | Install Git from https://git-scm.com/downloads |
| `remote origin already exists` | Run `git remote remove origin`, then add again |
| `Authentication failed` on push | Use a Personal Access Token instead of your password |
| Pushed duplicate folders | Delete them locally, add to `.gitignore`, commit and push again |

## Python / pip issues

| Problem | Solution |
|---------|----------|
| `python: command not found` | Install Python; on macOS/Linux try `python3` |
| `pip: command not found` | Run `python -m pip install -r requirements.txt` |
| `ModuleNotFoundError: No module named 'pandas'` | Activate venv first, then `pip install -r requirements.txt` |
| Permission errors on pip | Use a virtual environment (Step B3) |

## Runtime issues

| Problem | Solution |
|---------|----------|
| Matplotlib window hangs | Set `MPLBACKEND=Agg` before running (see Step B5) |
| `Connection failure` in browser | Start `python app.py` first; use `http://127.0.0.1:5000/` not local HTML files |
| Port 5000 already in use | Stop other apps on port 5000, or change port in `app.py` |
| First web request is slow | Normal — the ML model trains on first request (~10–30 seconds) |
| `data/loans.csv` missing | Run `python generate_dataset.py` or `python main.py --batch` |

---

# Quick Reference — Full Local Setup

Copy and paste (replace the `cd` path with your folder):

**Windows:**

```powershell
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:MPLBACKEND = "Agg"
python main.py --batch
python app.py
```

Then open **http://127.0.0.1:5000/** in your browser.

**macOS / Linux:**

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export MPLBACKEND=Agg
python main.py --batch
python app.py
```

Then open **http://127.0.0.1:5000/** in your browser.

---

# Related Documentation

| File | Contents |
|------|----------|
| [README.md](README.md) | Project overview, file structure, CLI usage |
| [WEB_GUIDE.md](WEB_GUIDE.md) | Web UI setup, routes, demo accounts, API testing |
| [reports/REPORT.md](reports/REPORT.md) | Technical methodology and architecture |
| [reports/FINANCE_ESSAY.md](reports/FINANCE_ESSAY.md) | Finance theory essay |

---

# Security Reminder

- Demo passwords (`officer123`, `admin123`) are for **local development only**
- Never commit `.env` files, API keys, or real credentials
- Change `app.secret_key` in `app.py` before any production deployment
