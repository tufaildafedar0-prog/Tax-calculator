# PAN-based Tax & EMI Calculator

Simple desktop GUI app (Tkinter + ttkbootstrap) to calculate tax and monthly take-home based on PAN, income, deductions, EMI and age. The app supports individual and corporate flows and stores recent PAN entries in a local SQLite database.

## What it does
- Validates a PAN and determines entity type
- Calculates tax using typical Indian slabs for individuals and flat rates for corporates
- Applies rebate and cess (4%) where applicable
- Shows a step-by-step breakdown and a small animated pie chart
- Persists recent PAN inputs in a local SQLite database

## Files
- `new_tax_regime (1).py` — main application (Tkinter + ttkbootstrap)
- `pan_data.json` — example saved PAN entries
- `tax_calculator.db` — local SQLite DB (created/used at runtime)

## Requirements
- Python 3.10+ (3.8+ should also work)
- `ttkbootstrap` (for themed widgets)

Install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run (Windows PowerShell)

Change directory to the project folder then run the script (the filename contains spaces/parentheses, so quote it):

```powershell
cd "d:\\Tax calc\\Tax calc"
python "new_tax_regime (1).py"
```

## Preparing a GitHub repo and pushing

1. Initialize local repo and commit files:

```powershell
cd "d:\\Tax calc"
git init -b main
git add .
git commit -m "Initial commit: PAN-based Tax & EMI Calculator"
```

2. Create remote repository and push (choose one):

- Using GitHub CLI (`gh`):

```powershell
gh repo create <username>/<repo-name> --public --source=. --remote=origin --push
```

- Or manually create a repo on github.com, then add remote and push:

```powershell
git remote add origin https://github.com/<username>/<repo-name>.git
git branch -M main
git push -u origin main
```

## Notes
- The app creates `tax_calculator.db` in the working directory. Add it to `.gitignore` if you don't want to commit DB files.
- If you'd like, I can: add a `requirements.txt`, `.gitignore`, create the repo using `gh`, or automate the git steps for you — tell me which you prefer.

---
Created with help from GitHub Copilot.
