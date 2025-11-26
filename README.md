# 💼 TaxFlow Pro — Smart Income Tax Calculator

A modern desktop application for calculating income tax, exploring detailed financial breakdowns, and visualizing tax insights with an interactive, responsive dashboard. Built with Python, Tkinter, and Matplotlib.

**Instantly calculate your tax liability, view financial projections, and make informed decisions with TaxFlow Pro.**

---

## 🚀 Features

### 💰 Smart Tax Calculator
- **PAN Validation**: Validates PAN format and auto-detects entity type (Individual/Company).
- **Employment Toggle**: Choose between `Salaried` (₹75K standard deduction) or `Self Employed` (₹0 deduction).
- **New Tax Regime Slabs**: Realistic tax brackets for India's New Tax Regime (2023+).
- **Salaried Benefit**: Individuals earning 0–7L get **0% tax** after standard deduction.
- **Instant Results**: Animated number counters for quick tax payable and net take-home display.
- **Step-by-Step Breakdown**: Detailed report showing taxable income, slabs, rebate, cess, and final tax.

### 📊 Responsive Animated Dashboard
Three interactive tabs with live Matplotlib charts:
- **💰 Income Distribution**: Pie and bar charts showing deductions, tax, EMI, and net income.
- **📈 Tax Analysis**: Tax slab breakdown, rate comparison, and income-vs-tax curves.
- **💡 Financial Insights**: Savings potential, investment recommendations, monthly budget, and yearly projections.
- **Fullscreen & Resize Safe**: Debounced layout refresh ensures charts reflow perfectly on fullscreen, minimize, or resize.

### 💾 Smart Input Memory
- **Autofill Recent Entries**: Saves PAN, income, deductions, EMI, and age in SQLite for instant recall.
- **Quick Presets**: Dropdown menus for common income levels, deductions, EMI, and age ranges.
- **Manual Override**: Entry + dropdown hybrid—type custom values or pick presets.

### 🎨 Modern UI
- **Themed Widgets**: Professional dark/light toggle using `ttkbootstrap`.
- **Responsive Grid**: Adapts to window size; left panel (inputs), right panel (detailed analysis).
- **Loading Feedback**: Clear status messages and error dialogs.
- **Keyboard Friendly**: Full keyboard navigation and accessible controls.

---

## 🛠️ Technologies Used
- **Python 3.10+** — Core language
- **Tkinter + ttkbootstrap** — Modern themed GUI framework
- **Matplotlib + FigureCanvasTkAgg** — Embedded animated charts
- **SQLite3** — Local data persistence
- **NumPy** — Numerical calculations

---

## 📋 How to Use

### 1. Clone & Setup

```powershell
git clone https://github.com/tufaildafedar0-prog/Tax-calculator.git
cd "Tax calculator"
```

### 2. Create Virtual Environment & Install Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run the Application

```powershell
cd "Tax calc"
python "new_tax_regime (1).py"
```

Or (if renamed):

```powershell
python tax_calculator.py
```

### 4. Calculate Your Tax

1. **Enter PAN**: Validates format; auto-detects Individual/Company (or override with Employment toggle).
2. **Choose Employment Type**: `Salaried` (auto-fills ₹75K deduction) or `Self Employed` (₹0).
3. **Enter Financial Details**: Income, Deductions, Monthly EMI, Age (use dropdowns or type custom values).
4. **Calculate**: Click **🚀 Calculate Tax** → see instant results and detailed breakdown.
5. **Explore Dashboard**: Click **📊 View Dashboard** → interact with three tabs of animated charts.
6. **Maximize/Resize**: Dashboard is fully responsive; charts reflow automatically.

### 5. Reset or Search New PAN

- Click **🔄 Reset** to clear all inputs and start fresh.
- Edit the PAN field directly to autofill previous entries.

---

## 📁 Project Structure

```
Tax calculator/
├── README.md
├── requirements.txt
├── .gitignore
└── Tax calc/
    ├── new_tax_regime (1).py        # Main application (Tkinter + Matplotlib)
    ├── pan_data.json                 # Sample PAN data (reference)
    └── tax_calculator.db             # SQLite DB (auto-created, ignored by git)
```

---

## ⚙️ Configuration

### PAN Validation & Entity Detection
- **Format**: `^[A-Z]{5}[0-9]{4}[A-Z]$` (standard Indian PAN format)
- **Example Valid PANs**:
  - `ABCDP1234F` → Individual (P at position 4)
  - `ABCDC1234F` → Company (C at position 4)
  - For testing with standard deduction, use any PAN with 'P' and select `Salaried`.

### Tax Regime
- **Standard Deduction** (Salaried): ₹75,000
- **Tax Slabs** (New Tax Regime, unified for all ages):
  - 0–7L: **0%**
  - 7L–11L: **5%**
  - 11L–15L: **10%**
  - 15L–19L: **15%**
  - 19L–23L: **20%**
  - 23L–27L: **25%**
  - 27L+: **30%**
- **Rebate**: ₹12,500 (if taxable ≤ 5L)
- **Cess**: 4% on tax after rebate

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Dashboard charts clipped on first open** | Dashboard includes auto-refresh logic. Try maximizing/minimizing once; charts will reflow. |
| **PAN shows as "Other"** | Use a PAN with 'P' at position 4 (e.g., `ABCDP1234F`), or select `Salaried` from Employment toggle to override. |
| **App won't start** | Ensure Python 3.8+ and all dependencies are installed. Run `pip install -r requirements.txt` again. |
| **"No module named 'ttkbootstrap'"** | Missing dependency. Run: `pip install ttkbootstrap matplotlib numpy pillow`. |

---

## 📈 Roadmap (Upcoming Features)

- ✅ Employment toggle (Salaried/Self Employed) — **DONE**
- ✅ Responsive dashboard with debounced layout — **DONE**
- ⬜ Rename script to `tax_calculator.py` and refactor into `taxlib` module
- ⬜ Unit tests for tax calculations and DB persistence (pytest)
- ⬜ GitHub Actions CI/CD pipeline (lint + test)
- ⬜ PyInstaller build for Windows executable distribution
- ⬜ CSV/PDF export of tax reports
- ⬜ Old Tax Regime calculator (comparison mode)

---

## 📧 Contact & Support

For questions, feedback, or issues:
- **Email**: [tufaildafedar0@gmail.com](mailto:tufaildafedar0@gmail.com)
- **GitHub Issues**: [Tax-calculator Issues](https://github.com/tufaildafedar0-prog/Tax-calculator/issues)

---

## 📄 License

This project is open source. See `LICENSE` for details (or add one).

---

**Made with ❤️ by [Your Name]** — Simplifying tax calculations, one click at a time. 
