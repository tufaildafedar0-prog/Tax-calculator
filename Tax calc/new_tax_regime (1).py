import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import math
import time
import re
import sqlite3
from datetime import datetime

# ------------------- DATABASE SETUP -------------------
DB_FILE = "tax_calculator.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS pan_users (
    pan TEXT PRIMARY KEY,
    income REAL,
    deductions REAL,
    emi REAL,
    age INTEGER,
    timestamp TEXT
)
''')
conn.commit()

def save_pan_data_db(pan, income, deductions, emi, age):
    now = datetime.now().isoformat()
    c.execute('''
    INSERT INTO pan_users (pan, income, deductions, emi, age, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(pan) DO UPDATE SET
        income=excluded.income,
        deductions=excluded.deductions,
        emi=excluded.emi,
        age=excluded.age,
        timestamp=excluded.timestamp
    ''', (pan, income, deductions, emi, age, now))
    conn.commit()

def get_pan_data_db(pan):
    c.execute("SELECT income, deductions, emi, age FROM pan_users WHERE pan=?", (pan,))
    row = c.fetchone()
    if row:
        return {"income": row[0], "deductions": row[1], "emi": row[2], "age": row[3]}
    return {}

# ------------------- PAN VALIDATION -------------------
def validate_pan(pan):
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    return bool(re.match(pattern, pan.upper()))

def get_pan_entity_type(pan):
    c = pan[3].upper()
    if c == 'P':
        return "Individual"
    elif c == 'C':
        return "Company"
    else:
        return "Other"

# ------------------- TAX CALCULATION -------------------
def calculate_individual_tax(old_income, deductions, age):
    taxable = max(0, old_income - deductions)
    if age < 60:
        slabs = [(250_000, 0.0), (250_000, 0.05), (500_000, 0.20), (float('inf'), 0.30)]
        labels = ["0–2.5L","2.5L–5L","5L–10L","Above 10L"]
    elif age < 80:
        slabs = [(300_000, 0.0), (200_000, 0.05), (500_000, 0.20), (float('inf'), 0.30)]
        labels = ["0–3L","3L–5L","5L–10L","Above 10L"]
    else:
        slabs = [(500_000, 0.0), (500_000, 0.20), (float('inf'), 0.30)]
        labels = ["0–5L","5L–10L","Above 10L"]

    rem = taxable
    slab_details = {}
    tax_before = 0.0
    for (size, rate), lab in zip(slabs, labels):
        if rem <= 0:
            break
        part = min(rem, size)
        t = part * rate
        slab_details[lab] = round(t, 2)
        tax_before += t
        rem -= part

    rebate = min(tax_before, 12500) if taxable <= 500_000 else 0
    tax_after = tax_before - rebate
    cess = tax_after * 0.04
    total = round(tax_after + cess, 2)
    return total, slab_details, {
        "gross": old_income,
        "deductions": deductions,
        "taxable": taxable,
        "tax_before": round(tax_before,2),
        "rebate": rebate,
        "tax_after": round(tax_after,2),
        "cess": round(cess,2),
        "total": total
    }

def calculate_corporate_tax(gross_income, deductions, entity_type):
    taxable = max(0, gross_income - deductions)
    slab_details = {}
    if entity_type == "Company":
        rate = 0.22 if gross_income <= 5_000_000 else 0.30
    else:
        rate = 0.30
    tax_before = taxable * rate
    slab_details[f"{int(rate*100)}% Flat"] = round(tax_before,2)
    cess = tax_before * 0.04
    total = round(tax_before + cess,2)
    return total, slab_details, {
        "gross": gross_income,
        "deductions": deductions,
        "taxable": taxable,
        "tax_before": round(tax_before,2),
        "rebate": 0,
        "tax_after": round(tax_before,2),
        "cess": round(cess,2),
        "total": total
    }

# ------------------- ANIMATIONS -------------------
def animate_number(widget, target, duration=0.8):
    steps = int(duration * 50)
    current = 0
    increment = target/steps if steps else target
    for _ in range(steps):
        current += increment
        widget.config(text=f"₹{int(current):,}")
        widget.update()
        time.sleep(duration/steps)
    widget.config(text=f"₹{int(target):,}")

def animate_pie_chart(steps, emi, entity_type, theme):
    win = ttk.Toplevel(title="Income Distribution")
    win.geometry("480x380")
    canvas_bg = "white" if theme=="light" else "#2c3e50"
    canvas = tk.Canvas(win, width=470, height=360, bg=canvas_bg)
    canvas.pack()

    gross = steps["gross"]
    deductions = steps["deductions"]
    tax = steps["total"]
    take_home = max(0, gross - deductions - tax - emi)

    values = [deductions, tax, emi, take_home]
    labels = [
        f"Deductions\n₹{deductions:,.0f}",
        f"Tax\n₹{tax:,.0f}",
        f"EMI\n₹{emi:,.0f}",
        f"Net\n₹{take_home:,.0f}"
    ]
    colors = ["#ff7675", "#74b9ff", "#55efc4", "#ffeaa7"]

    total = sum(values)
    if total <= 0: return

    start_angle = 0
    text_color = "#222" if theme=="light" else "white"

    for i, val in enumerate(values):
        extent = val/total * 360
        slice_steps = int(extent)
        for _ in range(slice_steps):
            canvas.create_arc(130,50,310,230, start=start_angle, extent=1, fill=colors[i], outline="")
            start_angle += 1
            canvas.update()
            time.sleep(0.004)

    lx, ly = 330, 60
    for i, lab in enumerate(labels):
        canvas.create_rectangle(lx, ly + i*28, lx+15, ly+15 + i*28, fill=colors[i], outline="")
        canvas.create_text(lx+25, ly + 8 + i*28, text=lab, anchor="w", font=("Segoe UI",9), fill=text_color)

# ------------------- UI LOGIC -------------------
def on_pan_change(event=None):
    pan = entry_pan.get().strip().upper()
    if validate_pan(pan):
        entry_pan.configure(bootstyle="success")
        btn_calculate.configure(state="normal")
    else:
        entry_pan.configure(bootstyle="danger")
        btn_calculate.configure(state="disabled")

def autofill_pan(event=None):
    pan = entry_pan.get().strip().upper()
    data = get_pan_data_db(pan)
    if data:
        income_var.set(str(data.get("income","")))
        deduction_var.set(str(data.get("deductions","")))
        emi_var.set(str(data.get("emi","")))
        age_var.set(str(data.get("age","30")))

def calculate_tax():
    pan = entry_pan.get().strip().upper()
    if not validate_pan(pan):
        messagebox.showerror("PAN Error", "Enter a valid PAN (e.g. ABCDE1234F).")
        return

    entity = get_pan_entity_type(pan)

    try:
        income = float(income_var.get())
        deductions = float(deduction_var.get())
        emi = float(emi_var.get())
        age = int(age_var.get())
    except:
        messagebox.showerror("Invalid Input", "Please enter numeric values.")
        return

    if entity == "Individual":
        total_tax, slab, steps = calculate_individual_tax(income, deductions, age)
    else:
        total_tax, slab, steps = calculate_corporate_tax(income, deductions, entity)

    take_home = income - deductions - total_tax - emi

    # Save to database
    save_pan_data_db(pan, income, deductions, emi, age)

    animate_number(lbl_tax, total_tax)
    animate_number(lbl_takehome, take_home)

    # Step-by-step details
    detail_lines = [
        f"PAN: {pan}",
        f"Entity Type: {entity}",
        f"Gross / Turnover: ₹{steps['gross']:,.2f}",
        f"Deductions: ₹{steps['deductions']:,.2f}",
        f"Taxable Income: ₹{steps['taxable']:,.2f}"
    ]
    if entity == "Individual":
        detail_lines.append(f"Age: {age} years")
        if age >= 60:
            detail_lines.append("Senior citizen benefits applied.")
    detail_lines.append("\nTax Breakdown by Slab:")
    for lab, amt in slab.items():
        detail_lines.append(f"  {lab}: ₹{amt:,.2f}")
    detail_lines += [
        f"Tax Before Rebate: ₹{steps['tax_before']:,.2f}",
        f"Rebate: ₹{steps['rebate']:,.2f}",
        f"Tax After Rebate: ₹{steps['tax_after']:,.2f}",
        f"Cess (4%): ₹{steps['cess']:,.2f}",
        f"Total Tax: ₹{steps['total']:,.2f}",
        f"Monthly EMI: ₹{emi:,.2f}",
        f"Net / Take-Home: ₹{take_home:,.2f}"
    ]

    txt_details.config(state="normal")
    txt_details.delete("1.0", tk.END)
    for ln in detail_lines:
        txt_details.insert(tk.END, ln + "\n")
    txt_details.config(state="disabled")

    app.update()
    time.sleep(1)
    theme = "light" if app.style.theme.name == "morph" else "dark"
    animate_pie_chart(steps, emi, entity, theme)

# ------------------- UI BUILD -------------------
app = ttk.Window(themename="morph")
app.title("Tax & EMI Calculator — PAN‑based")
app.geometry("960x780")
app.bind("<F11>", lambda e: app.attributes("-fullscreen", not app.attributes("-fullscreen")))
app.bind("<Escape>", lambda e: app.attributes("-fullscreen", False))

header = ttk.Frame(app, padding=20)
header.pack(fill="x")
ttk.Label(header, text="PAN‑based Tax & EMI Calculator", font=("Segoe UI Semibold", 24)).pack()
ttk.Label(header, text="Supports Individuals & Corporates", bootstyle="secondary", font=("Segoe UI", 11)).pack(pady=(0,10))

theme_btn = ttk.Button(header, text="🌙 Dark Mode", bootstyle="info-outline", command=lambda: (
    app.style.theme_use("darkly") if app.style.theme.name=="morph" else app.style.theme_use("morph"),
    theme_btn.config(text=("☀ Light Mode" if app.style.theme.name=="darkly" else "🌙 Dark Mode"))
))
theme_btn.pack()

input_frame = ttk.Labelframe(app, text="Inputs", padding=15)
input_frame.pack(fill="x", padx=20, pady=10)

# PAN
ttk.Label(input_frame, text="PAN Number:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
entry_pan = ttk.Entry(input_frame)
entry_pan.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
entry_pan.insert(0, "ABCDE1234F")
entry_pan.bind("<KeyRelease>", on_pan_change)
entry_pan.bind("<FocusOut>", autofill_pan)

# Income
ttk.Label(input_frame, text="Gross / Turnover (₹):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
income_var = tk.StringVar()
income_dropdown = ttk.Combobox(input_frame, textvariable=income_var, values=[
    "300000","500000","750000","1000000","2000000","5000000","10000000"])
income_dropdown.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
income_dropdown.set("500000")

# Deductions
ttk.Label(input_frame, text="Deductions (₹):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
deduction_var = tk.StringVar()
deduction_dropdown = ttk.Combobox(input_frame, textvariable=deduction_var, values=[
    "0","50000","100000","150000","200000"])
deduction_dropdown.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
deduction_dropdown.set("0")

# EMI
ttk.Label(input_frame, text="Monthly EMI (₹):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
emi_var = tk.StringVar()
emi_dropdown = ttk.Combobox(input_frame, textvariable=emi_var, values=[
    "0","5000","10000","15000","20000","25000"])
emi_dropdown.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
emi_dropdown.set("0")

# Age
ttk.Label(input_frame, text="Age (Years):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
age_var = tk.StringVar()
age_dropdown = ttk.Combobox(input_frame, textvariable=age_var, values=[str(i) for i in range(18,101)])
age_dropdown.grid(row=4, column=1, sticky="ew", padx=5, pady=5)
age_dropdown.set("30")

input_frame.columnconfigure(1, weight=1)

btn_frame = ttk.Frame(app)
btn_frame.pack(fill="x", padx=20, pady=10)
btn_calculate = ttk.Button(btn_frame, text="Calculate", bootstyle="success", command=calculate_tax)
btn_calculate.pack(side="left", expand=True, padx=10)
btn_calculate.configure(state="disabled")

ttk.Button(btn_frame, text="Reset", bootstyle="warning", command=lambda: [
    entry_pan.delete(0, tk.END),
    entry_pan.insert(0, "ABCDE1234F"),
    income_dropdown.set("500000"),
    deduction_dropdown.set("0"),
    emi_dropdown.set("0"),
    age_dropdown.set("30"),
    txt_details.config(state="normal"),
    txt_details.delete("1.0", tk.END),
    txt_details.config(state="disabled"),
    btn_calculate.configure(state="disabled")
]).pack(side="left", expand=True, padx=10)

# Output
output_frame = ttk.Labelframe(app, text="Summary", padding=15)
output_frame.pack(fill="x", padx=20, pady=10)
ttk.Label(output_frame, text="Tax Payable:", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="w")
lbl_tax = ttk.Label(output_frame, text="₹0", font=("Segoe UI Bold", 14), bootstyle="danger")
lbl_tax.grid(row=0, column=1, sticky="e")
ttk.Label(output_frame, text="Net / Take‑Home after EMI:", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w")
lbl_takehome = ttk.Label(output_frame, text="₹0", font=("Segoe UI Bold", 14), bootstyle="success")
lbl_takehome.grid(row=1, column=1, sticky="e")
output_frame.columnconfigure(1, weight=1)

# Detailed
details_frame = ttk.Labelframe(app, text="Detailed Calculation", padding=15)
details_frame.pack(fill="both", expand=True, padx=20, pady=10)
txt_details = tk.Text(details_frame, height=14, wrap="word", bg="#f7f7f7", fg="#222")
txt_details.pack(fill="both", expand=True)
txt_details.config(state="disabled")

app.mainloop()
