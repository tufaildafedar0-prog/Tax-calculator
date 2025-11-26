# TaxFlow Pro — PAN-based Tax & Financial Insights (Desktop)

TaxFlow Pro is a desktop application (Tkinter + ttkbootstrap) that calculates income tax, shows a detailed breakdown, and provides an animated dashboard with financial visualizations. The app stores recent user input locally in SQLite for quick autofill.

**Highlights**
- Friendly UI: themed widgets using `ttkbootstrap` and a compact entry+dropdown control for quick presets.
- PAN-aware: validates PAN format and uses the PAN character to suggest entity type (Individual/Company). You can override via the Employment/Entity selector.
- Employment toggle: choose `Salaried` (auto-applies ₹75,000 standard deduction) or `Self Employed` (no standard deduction).
- New tax regime slabs: configurable for realistic simulations; salaried users get 0% on 0–7L after standard deduction.
- Responsive animated dashboard: Matplotlib charts embedded in the app with tabs (Income Distribution, Tax Analysis, Financial Insights). The dashboard is fully responsive and reflows correctly on fullscreen/minimize/resize.
- Persistence: recent PAN entries and financial inputs are persisted in `tax_calculator.db` (SQLite).

## Files
- `new_tax_regime (1).py` — main application (Tkinter + ttkbootstrap). Consider renaming to `tax_calculator.py` for a cleaner filename.
- `pan_data.json` — sample PAN data (optional)
- `tax_calculator.db` — local SQLite DB (created at runtime; excluded via `.gitignore`)

## Features & Behavior
- PAN validation using regex `^[A-Z]{5}[0-9]{4}[A-Z]$`.
- Entity detection inspects the 4th character of PAN (index 3): `'P'` → Individual, `'C'` → Company, otherwise marked `Other` (which historically was treated as corporate). You can override by selecting `Salaried`/`Self Employed` in the UI.
- Standard deduction: `Salaried` auto-fills ₹75,000; `Self Employed` uses ₹0 by default.
- Tax calculation includes rebate logic and 4% cess.
- Dashboard animations are debounced to ensure correct layout on fullscreen/resize.

## Requirements
- Python 3.10+ recommended (3.8+ should work)
- Recommended packages (install from `requirements.txt`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install at minimum:

```powershell
pip install ttkbootstrap matplotlib numpy pillow
```

## Run (Windows PowerShell)

Open PowerShell, activate the virtualenv and run the app from the project folder.

```powershell
cd "d:\\Tax calc\\Tax calc"
.\.venv\Scripts\Activate.ps1
python "new_tax_regime (1).py"
```

Tip: rename the script to remove spaces/parentheses for easier CLI usage:

```powershell
git mv "new_tax_regime (1).py" tax_calculator.py
git commit -m "Rename script to tax_calculator.py"
```

## Commit & Push to GitHub

I'll commit and push local changes for you if you want. Typical steps (if repo already has `origin` remote set):

```powershell
cd "d:\\Tax calc\\Tax calc"
git add .
git commit -m "chore: update README and UI improvements"
git push
```

If you haven't connected a remote yet, create a GitHub repo and add remote:

```powershell
gh repo create <username>/<repo-name> --public --source=. --remote=origin --push
# or
git remote add origin https://github.com/<username>/<repo-name>.git
git branch -M main
git push -u origin main
```

## Troubleshooting
- If the dashboard appears clipped on first open, the UI includes debounced layout refreshes — try maximizing once; if it still cuts off, run the app from a terminal to check logs.
- If PAN detection mis-classifies you, use a PAN with the 4th char set to `P` for Individuals (e.g. `ABCDP1234F`) or override via the Employment selector.

## Roadmap (suggested next steps)
- Rename the main script to `tax_calculator.py` and refactor calculation logic into a `taxlib` module for unit testing.
- Add pytest unit tests for tax slabs and DB persistence.
- Add CI (GitHub Actions) for tests and linting.
- Create an installer build (PyInstaller) for Windows distribution.

---

If you want, I can now commit this README update and push everything to your GitHub repo — say "Yes, push" and I'll run the git commands (I'll check the remote first and report back). 
