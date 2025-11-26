import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import math
import time
import re
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np

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
def calculate_individual_tax(old_income, deductions, age, employment_type="Salaried"):
    taxable = max(0, old_income - deductions)
    
    print(f"TAX CALC: Income={old_income}, Deductions={deductions}, Taxable={taxable}")
    
    # CORRECT TAX SLABS for New Regime 2024-25
    slabs = [
        (300_000, 0.00),     # 0-3L: 0%
        (300_000, 0.05),     # 3L-6L: 5%
        (400_000, 0.10),     # 6L-10L: 10%
        (500_000, 0.15),     # 10L-15L: 15%
        (float('inf'), 0.20) # Above 15L: 20%
    ]
    
    rem = taxable
    slab_details = {}
    tax_before = 0.0
    slab_names = ["0–3L", "3L–6L", "6L–10L", "10L–15L", "Above 15L"]
    
    for i, (size, rate) in enumerate(slabs):
        if rem <= 0:
            break
        part = min(rem, size)
        tax_in_slab = part * rate
        slab_details[slab_names[i]] = round(tax_in_slab, 2)
        tax_before += tax_in_slab
        rem -= part
        print(f"SLAB {slab_names[i]}: {part} * {rate} = {tax_in_slab}")

    # Rebate under section 87A (for income up to 7L)
    rebate = min(tax_before, 12500) if taxable <= 700000 else 0
    tax_after = tax_before - rebate
    cess = tax_after * 0.04  # 4% health and education cess
    total = round(tax_after + cess, 2)
    
    print(f"FINAL: TaxBefore={tax_before}, Rebate={rebate}, Cess={cess}, Total={total}")
    
    return total, slab_details, {
        "gross": old_income,
        "deductions": deductions,
        "taxable": taxable,
        "tax_before": round(tax_before, 2),
        "rebate": rebate,
        "tax_after": round(tax_after, 2),
        "cess": round(cess, 2),
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

# ------------------- SMOOTH ANIMATION SYSTEM -------------------
class SmoothAnimator:
    def __init__(self):
        self.animation_queue = []
    
    def add_step(self, callback, delay=0):
        self.animation_queue.append((callback, delay))
    
    def execute(self):
        for callback, delay in self.animation_queue:
            app.after(delay, callback)
        self.animation_queue.clear()

def animate_number(widget, target, duration=800, prefix="₹"):
    """Buttery smooth number animation"""
    current_text = widget.cget("text")
    start = float(current_text.replace(prefix, "").replace(",", "") or 0)
    
    steps = 40
    step_time = max(10, duration // steps)
    
    def ease_out_quad(t):
        return t * (2 - t)
    
    def update(step):
        progress = step / steps
        eased = ease_out_quad(progress)
        current_val = start + (target - start) * eased
        widget.config(text=f"{prefix}{int(current_val):,}")
        
        if step < steps:
            widget.after(step_time, lambda: update(step + 1))
        else:
            widget.config(text=f"{prefix}{int(target):,}")
    
    update(0)

def slide_in(widget, duration=400):
    """Smooth slide-in animation for frames"""
    original_info = widget.place_info()
    widget.place(x=1000, y=original_info.get('y', 0))
    widget.update()
    
    steps = 20
    step_time = duration // steps
    target_x = int(original_info.get('x', 0))
    
    def animate(step):
        progress = step / steps
        current_x = 1000 + (target_x - 1000) * progress
        widget.place(x=int(current_x))
        
        if step < steps:
            widget.after(step_time, lambda: animate(step + 1))
        else:
            widget.place(x=target_x)
    
    animate(0)

# ------------------- COMPLETE MATPLOTLIB DASHBOARD -------------------
class CompleteDashboard:
    def __init__(self, steps, emi, entity_type):
        self.steps = steps
        self.emi = emi
        self.entity_type = entity_type
        self.current_tab = 0
        self.animations = []
        
        self.create_complete_dashboard()
    
    def create_complete_dashboard(self):
        self.window = ttk.Toplevel(title="📊 Complete Financial Dashboard")
        self.window.geometry("1400x900")
        self.window.minsize(800, 600)
        
        # Make window responsive and maximize by default
        self.window.state('zoomed')  # Maximize on Windows
        
        # Make window responsive
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Modern header
        header_frame = ttk.Frame(self.window, padding=20)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(0, weight=1)
        
        ttk.Label(
            header_frame, 
            text="Complete Financial Analysis Dashboard", 
            font=("Segoe UI", 20, "bold"),
            bootstyle="primary"
        ).grid(row=0, column=0, sticky="w")
        
        ttk.Label(
            header_frame,
            text="Professional Tax Visualization with Smooth Animations",
            font=("Segoe UI", 11),
            bootstyle="secondary"
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.window, bootstyle="primary")
        self.notebook.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
        
        # Make notebook responsive
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Create complete tabs
        self.create_income_tab()
        self.create_tax_tab()
        self.create_insights_tab()
        
        # Force layout update after window is fully rendered
        # Also bind to Configure so we can refresh when the window geometry settles
        self.window.after(100, self.refresh_layout)
        self.window.after(500, self.refresh_layout)
        self._config_after_id = None
        self.window.bind("<Configure>", self.on_configure)

        # Start animations for first tab
        self.window.after(600, self.animate_current_tab)
    
    def on_tab_changed(self, event):
        """Trigger complete chart animations when tab changes"""
        current_tab = self.notebook.index(self.notebook.select())
        self.current_tab = current_tab
        
        # Stop any existing animations
        for anim in self.animations:
            if hasattr(anim, 'event_source') and anim.event_source:
                anim.event_source.stop()
        
        # Start complete animations for current tab
        self.window.after(300, self.animate_current_tab)
    
    def refresh_layout(self):
        """Force layout refresh for all figures when window is fully rendered"""
        try:
            # ensure geometry/layout tasks are processed
            self.window.update_idletasks()
            if hasattr(self, 'fig1') and self.fig1:
                self.fig1.tight_layout()
                self.canvas1.draw()
            if hasattr(self, 'fig2') and self.fig2:
                self.fig2.tight_layout()
                self.canvas2.draw()
            if hasattr(self, 'fig3') and self.fig3:
                self.fig3.tight_layout()
                self.canvas3.draw()
        except Exception as e:
            pass  # Ignore any layout errors

    def on_configure(self, event):
        """Debounced configure handler to refresh layout after resizing/zoom events."""
        try:
            if self._config_after_id:
                self.window.after_cancel(self._config_after_id)
        except Exception:
            pass
        # Schedule a refresh shortly after configure events stop
        self._config_after_id = self.window.after(200, self.refresh_layout)
    
    def create_income_tab(self):
        tab1 = ttk.Frame(self.notebook)
        self.notebook.add(tab1, text="💰 Income Distribution")
        
        # Make tab responsive
        tab1.grid_rowconfigure(0, weight=1)
        tab1.grid_columnconfigure(0, weight=1)
        
        # Create figure with responsive size
        self.fig1 = plt.Figure(figsize=(16, 10), dpi=80)
        self.fig1.patch.set_facecolor('#f8f9fa')
        
        # Create subplots
        self.ax1_1 = self.fig1.add_subplot(231)
        self.ax1_2 = self.fig1.add_subplot(232)
        self.ax1_3 = self.fig1.add_subplot(233)
        self.ax1_4 = self.fig1.add_subplot(212)
        
        self.canvas1 = FigureCanvasTkAgg(self.fig1, tab1)
        self.canvas1.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        tab1.grid_rowconfigure(0, weight=1)
        tab1.grid_columnconfigure(0, weight=1)
    
    def animate_income_tab(self):
        """Complete animations for income tab"""
        gross = self.steps["gross"]
        deductions = self.steps["deductions"]
        tax = self.steps["total"]
        take_home = max(0, gross - deductions - tax - self.emi)
        
        # Clear all axes
        for ax in [self.ax1_1, self.ax1_2, self.ax1_3, self.ax1_4]:
            ax.clear()
        
        # Data for animations
        values = [deductions, tax, self.emi, take_home]
        labels = ['Deductions', 'Tax', 'EMI', 'Net Income']
        colors = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#6BCF7F']
        
        # 1. Main Pie Chart - Income Distribution
        def animate_main_pie(frame):
            self.ax1_1.clear()
            if frame <= len(values):
                current_values = [v if i < frame else 0.1 for i, v in enumerate(values)]
                wedges, texts, autotexts = self.ax1_1.pie(
                    current_values, labels=labels, colors=colors,
                    autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
                    startangle=90, shadow=True
                )
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                self.ax1_1.set_title('Income Distribution', fontsize=14, fontweight='bold', pad=20)
            return []
        
        # 2. Monthly Breakdown
        monthly_takehome = take_home / 12
        monthly_emi = self.emi
        monthly_remaining = monthly_takehome - monthly_emi
        monthly_data = [monthly_takehome, monthly_emi, monthly_remaining]
        monthly_labels = ['Monthly Income', 'Monthly EMI', 'Disposable Income']
        monthly_colors = ['#27AE60', '#E74C3C', '#3498DB']
        
        def animate_monthly_pie(frame):
            self.ax1_2.clear()
            if frame <= len(monthly_data):
                current_values = [v if i < frame else 0.1 for i, v in enumerate(monthly_data)]
                wedges, texts, autotexts = self.ax1_2.pie(
                    current_values, labels=monthly_labels, colors=monthly_colors,
                    autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
                    startangle=90, wedgeprops=dict(width=0.3)
                )
                self.ax1_2.set_title('Monthly Cash Flow', fontsize=14, fontweight='bold', pad=20)
            return []
        
        # 3. Tax Efficiency
        tax_efficiency = ((gross - tax) / gross * 100) if gross > 0 else 0
        efficiency_data = [tax, gross - tax]
        efficiency_labels = ['Tax Paid', 'Remaining Income']
        efficiency_colors = ['#E74C3C', '#27AE60']
        
        def animate_efficiency(frame):
            self.ax1_3.clear()
            if frame <= 2:
                current_values = efficiency_data[:frame] + [0.1] * (2 - frame)
                wedges, texts, autotexts = self.ax1_3.pie(
                    current_values, colors=efficiency_colors,
                    autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
                    startangle=90
                )
                self.ax1_3.set_title(f'Tax Efficiency: {tax_efficiency:.1f}%', fontsize=14, fontweight='bold', pad=20)
            return []
        
        # 4. Complete Bar Chart
        categories = ['Gross Income', 'Deductions', 'Tax Paid', 'Monthly EMI', 'Net Take-home']
        amounts = [gross, deductions, tax, self.emi, take_home]
        bar_colors = ['#4361EE', '#FF6B6B', '#4ECDC4', '#FFD93D', '#6BCF7F']
        
        def animate_complete_bar(frame):
            self.ax1_4.clear()
            if frame > 0:
                current_categories = categories[:frame]
                current_amounts = amounts[:frame]
                current_colors = bar_colors[:frame]
                
                bars = self.ax1_4.bar(current_categories, current_amounts, color=current_colors, alpha=0.8)
                self.ax1_4.set_title('Complete Financial Overview', fontsize=14, fontweight='bold', pad=20)
                self.ax1_4.tick_params(axis='x', rotation=15)
                self.ax1_4.grid(True, alpha=0.3)
                
                # Add value labels
                for bar, amount in zip(bars, current_amounts):
                    height = bar.get_height()
                    self.ax1_4.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                            f'₹{amount:,.0f}', ha='center', va='bottom', fontweight='bold')
            return []
        
        # Create all animations
        ani1 = animation.FuncAnimation(self.fig1, animate_main_pie, frames=len(values)+1, interval=400, repeat=False)
        ani2 = animation.FuncAnimation(self.fig1, animate_monthly_pie, frames=len(monthly_data)+1, interval=400, repeat=False)
        ani3 = animation.FuncAnimation(self.fig1, animate_efficiency, frames=3, interval=400, repeat=False)
        ani4 = animation.FuncAnimation(self.fig1, animate_complete_bar, frames=len(amounts)+1, interval=500, repeat=False)
        
        self.animations.extend([ani1, ani2, ani3, ani4])
        self.fig1.tight_layout()
        self.canvas1.draw()
    
    def create_tax_tab(self):
        tab2 = ttk.Frame(self.notebook)
        self.notebook.add(tab2, text="📈 Tax Analysis")
        
        tab2.grid_rowconfigure(0, weight=1)
        tab2.grid_columnconfigure(0, weight=1)
        
        self.fig2 = plt.Figure(figsize=(16, 10), dpi=80)
        self.fig2.patch.set_facecolor('#f8f9fa')
        
        # Create 2x2 grid for tax analysis
        self.ax2_1 = self.fig2.add_subplot(221)
        self.ax2_2 = self.fig2.add_subplot(222)
        self.ax2_3 = self.fig2.add_subplot(223)
        self.ax2_4 = self.fig2.add_subplot(224)
        
        self.canvas2 = FigureCanvasTkAgg(self.fig2, tab2)
        self.canvas2.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        tab2.grid_rowconfigure(0, weight=1)
        tab2.grid_columnconfigure(0, weight=1)
    
    def animate_tax_tab(self):
        """Complete animations for tax tab - WITH CORRECTED SLABS"""
        gross = self.steps["gross"]
        tax = self.steps["total"]
        taxable = self.steps["taxable"]
        
        # Clear all axes
        for ax in [self.ax2_1, self.ax2_2, self.ax2_3, self.ax2_4]:
            ax.clear()
        
        # 1. Tax Breakdown - USING CORRECT SLABS
        slab_data = []
        slab_labels = []
        slab_colors = []
        
        if self.entity_type == "Individual":
            # CORRECT TAX SLABS for New Regime 2024-25
            slabs = [
                (300_000, 0.00),     # 0-3L: 0%
                (300_000, 0.05),     # 3L-6L: 5%
                (400_000, 0.10),     # 6L-10L: 10%
                (500_000, 0.15),     # 10L-15L: 15%
                (float('inf'), 0.20) # Above 15L: 20%
            ]
            
            # Calculate actual slab-wise amounts
            rem = taxable
            slab_amounts = []
            slab_percentages = ["0%", "5%", "10%", "15%", "20%"]
            
            for size, rate in slabs:
                if rem <= 0:
                    slab_amounts.append(0)
                    continue
                part = min(rem, size)
                slab_amounts.append(part)
                rem -= part
            
            slab_data = slab_amounts
            slab_labels = [f'0-3L\n0%', f'3L-6L\n5%', f'6L-10L\n10%', f'10L-15L\n15%', f'15L+\n20%']
            slab_colors = ['#27AE60', '#F39C12', '#E74C3C', '#8E44AD', '#3498DB']
        else:
            slab_data = [taxable]
            slab_labels = [f'Corporate Tax\n{22 if gross <= 5000000 else 30}%']
            slab_colors = ['#3498DB']
        
        def animate_tax_breakdown(frame):
            self.ax2_1.clear()
            if frame > 0:
                current_data = slab_data[:frame]
                current_labels = slab_labels[:frame]
                current_colors = slab_colors[:frame]
                
                bars = self.ax2_1.bar(current_labels, current_data, color=current_colors, alpha=0.8)
                self.ax2_1.set_title('Tax Slab Distribution', fontsize=14, fontweight='bold', pad=20)
                self.ax2_1.set_ylabel('Amount (₹)', fontweight='bold')
                self.ax2_1.grid(True, alpha=0.3)
                
                for bar, amount in zip(bars, current_data):
                    if amount > 0:  # Only show labels for non-zero amounts
                        height = bar.get_height()
                        self.ax2_1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                                f'₹{amount:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=8)
            return []
        
        # 2. Tax Rate Comparison
        tax_rates = [0, 5, 10, 15, 20]  # CORRECT RATES
        actual_rate = (tax / taxable * 100) if taxable > 0 else 0
        
        def animate_rate_comparison(frame):
            self.ax2_2.clear()
            if frame > 0:
                current_rates = tax_rates[:frame]
                current_labels = ['0%', '5%', '10%', '15%', '20%'][:frame]
                
                bars = self.ax2_2.bar(current_labels, current_rates, color='lightblue', alpha=0.6)
                if frame == len(tax_rates):
                    self.ax2_2.axhline(y=actual_rate, color='red', linestyle='--', linewidth=3, 
                                   label=f'Your Effective Rate: {actual_rate:.1f}%')
                    self.ax2_2.legend()
                self.ax2_2.set_title('Tax Rate Comparison', fontsize=14, fontweight='bold', pad=20)
                self.ax2_2.set_ylabel('Tax Rate (%)', fontweight='bold')
                self.ax2_2.set_ylim(0, 25)  # Set reasonable y-axis limit
                self.ax2_2.grid(True, alpha=0.3)
            return []
        
        # 3. Tax vs Income - USING CORRECTED FUNCTION
        income_levels = np.linspace(300000, 2000000, 8)
        tax_levels = [calculate_individual_tax(inc, 50000, 30)[0] for inc in income_levels]
        
        def animate_tax_curve(frame):
            self.ax2_3.clear()
            if frame > 0:
                current_income = income_levels[:frame]
                current_tax = tax_levels[:frame]
                
                self.ax2_3.plot(current_income, current_tax, 'o-', linewidth=3, color='#E74C3C')
                self.ax2_3.set_title('Tax vs Income', fontsize=14, fontweight='bold', pad=20)
                self.ax2_3.set_xlabel('Income (₹)', fontweight='bold')
                self.ax2_3.set_ylabel('Tax (₹)', fontweight='bold')
                self.ax2_3.grid(True, alpha=0.3)
                
                # Add current user's point
                if frame == len(income_levels):
                    self.ax2_3.plot(gross, tax, 'ro', markersize=10, label='Your Position')
                    self.ax2_3.legend()
            return []
        
        # 4. Tax Components
        components = ['Basic Tax', 'Rebate', 'Cess', 'Total Tax']
        component_values = [self.steps["tax_before"], self.steps["rebate"], self.steps["cess"], self.steps["total"]]
        component_colors = ['#3498DB', '#27AE60', '#F39C12', '#E74C3C']
        
        def animate_components(frame):
            self.ax2_4.clear()
            if frame > 0:
                current_values = component_values[:frame]
                current_labels = components[:frame]
                current_colors = component_colors[:frame]
                
                bars = self.ax2_4.bar(current_labels, current_values, color=current_colors, alpha=0.8)
                self.ax2_4.set_title('Tax Components', fontsize=14, fontweight='bold', pad=20)
                self.ax2_4.set_ylabel('Amount (₹)', fontweight='bold')
                self.ax2_4.grid(True, alpha=0.3)
                
                for bar, amount in zip(bars, current_values):
                    height = bar.get_height()
                    if amount > 0:  # Only show labels for non-zero amounts
                        self.ax2_4.text(bar.get_x() + bar.get_width()/2., height + 1000,
                                f'₹{amount:,.0f}', ha='center', va='bottom', fontweight='bold')
            return []
        
        # Create all animations
        ani1 = animation.FuncAnimation(self.fig2, animate_tax_breakdown, frames=len(slab_data)+1, interval=400, repeat=False)
        ani2 = animation.FuncAnimation(self.fig2, animate_rate_comparison, frames=len(tax_rates)+1, interval=400, repeat=False)
        ani3 = animation.FuncAnimation(self.fig2, animate_tax_curve, frames=len(income_levels)+1, interval=300, repeat=False)
        ani4 = animation.FuncAnimation(self.fig2, animate_components, frames=len(components)+1, interval=400, repeat=False)
        
        self.animations.extend([ani1, ani2, ani3, ani4])
        self.fig2.tight_layout()
        self.canvas2.draw()
    
    def create_insights_tab(self):
        tab3 = ttk.Frame(self.notebook)
        self.notebook.add(tab3, text="💡 Financial Insights")
        
        tab3.grid_rowconfigure(0, weight=1)
        tab3.grid_columnconfigure(0, weight=1)
        
        self.fig3 = plt.Figure(figsize=(16, 10), dpi=80)
        self.fig3.patch.set_facecolor('#f8f9fa')
        
        # Create 2x2 grid for insights
        self.ax3_1 = self.fig3.add_subplot(221)
        self.ax3_2 = self.fig3.add_subplot(222)
        self.ax3_3 = self.fig3.add_subplot(223)
        self.ax3_4 = self.fig3.add_subplot(224)
        
        self.canvas3 = FigureCanvasTkAgg(self.fig3, tab3)
        self.canvas3.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        tab3.grid_rowconfigure(0, weight=1)
        tab3.grid_columnconfigure(0, weight=1)
    
    def animate_insights_tab(self):
        """Complete animations for insights tab"""
        gross = self.steps["gross"]
        deductions = self.steps["deductions"]
        tax = self.steps["total"]
        take_home = max(0, gross - deductions - tax - self.emi)
        
        # Clear all axes
        for ax in [self.ax3_1, self.ax3_2, self.ax3_3, self.ax3_4]:
            ax.clear()
        
        # 1. Savings Potential
        current_savings = deductions
        max_possible = min(gross * 0.3, 150000)
        potential = max(0, max_possible - current_savings)
        
        savings_data = [current_savings, potential]
        savings_labels = ['Current Savings', 'Additional Potential']
        savings_colors = ['#3498DB', '#F39C12']
        
        def animate_savings(frame):
            self.ax3_1.clear()
            if frame > 0:
                current_data = savings_data[:frame]
                current_labels = savings_labels[:frame]
                current_colors = savings_colors[:frame]
                
                bars = self.ax3_1.bar(current_labels, current_data, color=current_colors, alpha=0.8)
                self.ax3_1.set_title('Tax Savings Potential', fontsize=14, fontweight='bold', pad=20)
                self.ax3_1.set_ylabel('Amount (₹)', fontweight='bold')
                self.ax3_1.grid(True, alpha=0.3)
                
                for bar, amount in zip(bars, current_data):
                    height = bar.get_height()
                    self.ax3_1.text(bar.get_x() + bar.get_width()/2., height + 1000,
                            f'₹{amount:,.0f}', ha='center', va='bottom', fontweight='bold')
            return []
        
        # 2. Investment Recommendations
        investment_options = ['PPF', 'NPS', 'ELSS', 'Health Insurance', 'Home Loan']
        investment_impact = [150000, 50000, 150000, 25000, 200000]
        investment_colors = ['#27AE60', '#3498DB', '#E74C3C', '#9B59B6', '#F39C12']
        
        def animate_investments(frame):
            self.ax3_2.clear()
            if frame <= len(investment_impact):
                current_values = investment_impact[:frame] + [0.1] * (len(investment_impact) - frame)
                current_labels = investment_options[:frame]
                current_colors = investment_colors[:frame]
                
                wedges, texts, autotexts = self.ax3_2.pie(
                    current_values, labels=current_labels, colors=current_colors,
                    autopct=lambda p: f'{p:.0f}' if p > 1 else '',
                    startangle=90
                )
                self.ax3_2.set_title('Recommended Investments', fontsize=14, fontweight='bold', pad=20)
            return []
        
        # 3. Monthly Budget
        monthly_data = [take_home/12, self.emi, (take_home/12 - self.emi)]
        monthly_labels = ['Monthly Income', 'Monthly EMI', 'Disposable Income']
        monthly_colors = ['#27AE60', '#E74C3C', '#3498DB']
        
        def animate_budget(frame):
            self.ax3_3.clear()
            if frame <= len(monthly_data):
                current_values = monthly_data[:frame] + [0.1] * (len(monthly_data) - frame)
                wedges, texts, autotexts = self.ax3_3.pie(
                    current_values, labels=monthly_labels, colors=monthly_colors,
                    autopct=lambda p: f'{p:.1f}%' if p > 1 else '',
                    startangle=90
                )
                self.ax3_3.set_title('Monthly Budget', fontsize=14, fontweight='bold', pad=20)
            return []
        
        # 4. Yearly Projection
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_income = [take_home/12] * 12
        cumulative_income = np.cumsum(monthly_income)
        
        def animate_projection(frame):
            self.ax3_4.clear()
            if frame > 0:
                current_months = months[:frame]
                current_cumulative = cumulative_income[:frame]
                
                self.ax3_4.plot(current_months, current_cumulative, 'o-', linewidth=3, color='#27AE60')
                self.ax3_4.fill_between(current_months, current_cumulative, alpha=0.3, color='#27AE60')
                self.ax3_4.set_title('Yearly Income Projection', fontsize=14, fontweight='bold', pad=20)
                self.ax3_4.set_ylabel('Cumulative Income (₹)', fontweight='bold')
                self.ax3_4.grid(True, alpha=0.3)
            return []
        
        # Create all animations
        ani1 = animation.FuncAnimation(self.fig3, animate_savings, frames=len(savings_data)+1, interval=400, repeat=False)
        ani2 = animation.FuncAnimation(self.fig3, animate_investments, frames=len(investment_impact)+1, interval=400, repeat=False)
        ani3 = animation.FuncAnimation(self.fig3, animate_budget, frames=len(monthly_data)+1, interval=400, repeat=False)
        ani4 = animation.FuncAnimation(self.fig3, animate_projection, frames=len(months)+1, interval=300, repeat=False)
        
        self.animations.extend([ani1, ani2, ani3, ani4])
        self.fig3.tight_layout()
        self.canvas3.draw()
    
    def animate_current_tab(self):
        """Animate the currently active tab"""
        if self.current_tab == 0:
            self.animate_income_tab()
        elif self.current_tab == 1:
            self.animate_tax_tab()
        elif self.current_tab == 2:
            self.animate_insights_tab()

# ------------------- MODERN UI COMPONENTS -------------------
class ModernCard(ttk.Frame):
    def __init__(self, parent, title="", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(borderwidth=1, relief="solid", padding=20)
        
        # Header
        if title:
            header = ttk.Frame(self)
            header.pack(fill="x", pady=(0, 15))
            
            ttk.Label(
                header, 
                text=title, 
                font=("Segoe UI", 12, "bold")
            ).pack(side="left")
        
        self.content = ttk.Frame(self)
        self.content.pack(fill="both", expand=True)

# ------------------- MODERN UI LOGIC -------------------
animator = SmoothAnimator()

def on_pan_change(event=None):
    pan = entry_pan.get().strip().upper()
    if validate_pan(pan):
        entry_pan.configure(bootstyle="success")
        entity_type = get_pan_entity_type(pan)
        entity_label.config(text=f"🏢 {entity_type}", bootstyle="success")
        btn_calculate.config(state="normal")
    else:
        entry_pan.configure(bootstyle="danger")
        entity_label.config(text="❌ Invalid PAN", bootstyle="danger")
        btn_calculate.config(state="disabled")

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
        messagebox.showerror("Error", "Please enter a valid PAN number")
        return

    try:
        income = float(income_var.get())
        deductions = float(deduction_var.get())
        emi = float(emi_var.get())
        age = int(age_var.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numeric values")
        return

    # DEBUG: Print what we're getting
    entity = get_pan_entity_type(pan)
    emp_type = employment_type_var.get()
    print(f"DEBUG: Entity={entity}, Employment Type='{emp_type}'")
    print(f"DEBUG: Income={income}, Deductions={deductions}, Age={age}")

    # Perform calculation directly (no queuing)
    if entity == "Individual":
        print("DEBUG: Using Individual tax calculation")
        total_tax, slab, steps = calculate_individual_tax(income, deductions, age, emp_type)
    else:
        print("DEBUG: Using Corporate tax calculation")
        total_tax, slab, steps = calculate_corporate_tax(income, deductions, entity)
    
    print(f"DEBUG: Calculated Tax={total_tax}")
    print(f"DEBUG: Slab details={slab}")
    
    take_home = income - deductions - total_tax - emi
    save_pan_data_db(pan, income, deductions, emi, age)
    
    # Store results
    app.calc_results = {
        "total_tax": total_tax,
        "take_home": take_home,
        "steps": steps,
        "slab": slab,
        "emi": emi,
        "pan": pan,
        "entity": entity,
        "age": age,
        "employment_type": emp_type
    }
    
    # Animate quick results
    animate_number(lbl_tax, total_tax, 600)
    animate_number(lbl_takehome, take_home, 600)
    
    # Update efficiency metrics
    update_efficiency_metrics()
    
    # Update and show detailed analysis
    update_details_text(app.calc_results)
    
    # Show dashboard button
    btn_dashboard.config(state="normal", text="📊 View Dashboard", bootstyle="info")
    loading_label.config(text="✅ Calculation complete! Click 'View Dashboard' for detailed charts.")

def update_efficiency_metrics():
    if hasattr(app, 'calc_results'):
        steps = app.calc_results["steps"]
        gross = steps["gross"]
        tax = steps["total"]
        deductions = steps["deductions"]
        
        # Calculate actual efficiency
        tax_efficiency = ((gross - tax) / gross * 100) if gross > 0 else 0
        savings_potential = max(0, 150000 - deductions)  # Max section 80C limit
        
        # Update efficiency labels
        efficiency_labels[0].config(text=f"{tax_efficiency:.1f}%")
        efficiency_labels[1].config(text=f"₹{savings_potential:,.0f}")

def update_details_text(results):
    steps = results["steps"]
    emp_type = results.get("employment_type", "Salaried")
    detail_lines = [
        "📊 TAX ANALYSIS REPORT",
        "=" * 50,
        f"🔹 PAN: {results['pan']}",
        f"🔹 Entity: {results['entity']}",
        f"🔹 Employment Type: {emp_type}",
        f"🔹 Gross Income: ₹{steps['gross']:,.2f}",
        f"🔹 Deductions: ₹{steps['deductions']:,.2f}",
        f"🔹 Taxable Income: ₹{steps['taxable']:,.2f}",
        "",
        "💰 TAX BREAKDOWN:",
        "-" * 30
    ]
    
    for lab, amt in results["slab"].items():
        if amt > 0:  # Only show non-zero slabs
            detail_lines.append(f"  📈 {lab}: ₹{amt:,.2f}")
    
    detail_lines.extend([
        "",
        "🎯 FINAL CALCULATION:",
        "-" * 30,
        f"  Tax Before Rebate: ₹{steps['tax_before']:,.2f}",
        f"  Rebate Applied: ₹{steps['rebate']:,.2f}",
        f"  Tax After Rebate: ₹{steps['tax_after']:,.2f}",
        f"  Cess (4%): ₹{steps['cess']:,.2f}",
        f"  💰 TOTAL TAX: ₹{steps['total']:,.2f}",
        f"  🏠 Monthly EMI: ₹{results['emi']:,.2f}",
        f"  💵 NET TAKE-HOME: ₹{results['take_home']:,.2f}",
        "",
        f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    ])

    txt_details.config(state="normal")
    txt_details.delete("1.0", tk.END)
    txt_details.insert(tk.END, "\n".join(detail_lines))
    txt_details.config(state="disabled")

def toggle_theme():
    current = app.style.theme.name
    if current == "morph":
        app.style.theme_use("darkly")
        theme_btn.config(text="☀️ Light Mode")
    else:
        app.style.theme_use("morph")
        theme_btn.config(text="🌙 Dark Mode")

def reset_form():
    entry_pan.delete(0, tk.END)
    entry_pan.insert(0, "ABCDP1234F")
    employment_type_var.set("Salaried")
    on_employment_type_change()
    income_var.set("750000")
    emi_var.set("10000")
    age_var.set("30")
    txt_details.config(state="normal")
    txt_details.delete("1.0", tk.END)
    txt_details.config(state="disabled")
    lbl_tax.config(text="₹0")
    lbl_takehome.config(text="₹0")
    loading_label.config(text="")
    btn_dashboard.config(state="disabled", text="📊 View Dashboard")
    # Reset efficiency metrics
    efficiency_labels[0].config(text="0%")
    efficiency_labels[1].config(text="₹0")
    on_pan_change()

# ------------------- MODERN ANDROID-STYLE UI BUILD -------------------
app = ttk.Window(themename="morph")
app.title("💼 TaxFlow Pro - Complete Tax Calculator")
app.geometry("1300x1000")
app.minsize(1200, 800)

# Create employment type variable AFTER app is created
employment_type_var = tk.StringVar(value="Salaried")

def on_employment_type_change():
    """Update standard deduction based on employment type"""
    emp_type = employment_type_var.get()
    if emp_type == "Salaried":
        deduction_var.set("75000")
    else:  # Self Employed
        deduction_var.set("0")

# Financial input variables
income_var = tk.StringVar(value="750000")
deduction_var = tk.StringVar(value="75000")
emi_var = tk.StringVar(value="10000")
age_var = tk.StringVar(value="30")

# Modern header
header_frame = ttk.Frame(app, padding=(40, 25, 40, 20))
header_frame.pack(fill="x")

# Main title
title_container = ttk.Frame(header_frame)
title_container.pack(fill="x", pady=(0, 10))

ttk.Label(
    title_container,
    text="💼",
    font=("Segoe UI", 32)
).pack(side="left", padx=(0, 15))

title_text = ttk.Frame(title_container)
title_text.pack(side="left")

ttk.Label(
    title_text,
    text="TaxFlow Pro",
    font=("Segoe UI", 28, "bold")
).pack(anchor="w")

ttk.Label(
    title_text,
    text="Complete AI-Powered Tax Calculator & Financial Insights",
    font=("Segoe UI", 12),
    bootstyle="secondary"
).pack(anchor="w", pady=(5, 0))

# Theme toggle
theme_btn = ttk.Button(header_frame, text="🌙 Dark Mode", command=toggle_theme, 
                      bootstyle="outline", width=15)
theme_btn.pack(anchor="ne", pady=(0, 10))

# Main content
main_container = ttk.Frame(app, padding=30)
main_container.pack(fill="both", expand=True)

# Left column - Input and Quick Results
left_column = ttk.Frame(main_container)
left_column.pack(side="left", fill="both", expand=True, padx=(0, 15))

# Right column - Detailed Analysis
right_column = ttk.Frame(main_container)
right_column.pack(side="right", fill="both", expand=True, padx=(15, 0))

# Input section
input_card = ModernCard(left_column, title="📝 Financial Profile")
input_card.pack(fill="x", pady=(0, 20))

# Input grid
input_grid = ttk.Frame(input_card.content)
input_grid.pack(fill="x", pady=10)

# PAN input
pan_frame = ttk.Frame(input_grid)
pan_frame.pack(fill="x", pady=12)

ttk.Label(pan_frame, text="PAN Number", font=("Segoe UI", 11, "bold")).pack(side="left")
entry_pan = ttk.Entry(pan_frame, font=("Segoe UI", 11), width=25)
entry_pan.pack(side="left", padx=(20, 30))
entry_pan.insert(0, "ABCDP1234F")
entry_pan.bind("<KeyRelease>", on_pan_change)
entry_pan.bind("<FocusOut>", autofill_pan)

entity_label = ttk.Label(pan_frame, text="👤 Individual", font=("Segoe UI", 10), bootstyle="success")
entity_label.pack(side="left")

# Employment Type Selection (Salaried vs Self Employed)
employment_frame = ttk.Frame(input_grid)
employment_frame.pack(fill="x", pady=12)

ttk.Label(employment_frame, text="Employment Type", font=("Segoe UI", 11, "bold")).pack(side="left")

radio_frame = ttk.Frame(employment_frame)
radio_frame.pack(side="left", padx=(20, 0))

ttk.Radiobutton(
    radio_frame, 
    text="💼 Salaried", 
    variable=employment_type_var, 
    value="Salaried",
    command=on_employment_type_change,
    bootstyle="info"
).pack(side="left", padx=(0, 20))

ttk.Radiobutton(
    radio_frame, 
    text="👨‍💼 Self Employed", 
    variable=employment_type_var, 
    value="Self Employed",
    command=on_employment_type_change,
    bootstyle="warning"
).pack(side="left")

# ------------------- CUSTOM INPUT WITH DROPDOWN -------------------
class FlexibleInput(ttk.Frame):
    """Entry field with Frame-based dropdown for preset values"""
    def __init__(self, parent, variable, presets, **kwargs):
        super().__init__(parent, **kwargs)
        self.variable = variable
        self.presets = presets
        self.dropdown_open = False
        self.root = parent
        
        # Find root window
        w = parent
        while hasattr(w, 'master') and w.master:
            w = w.master
        self.root_window = w
        
        # Container for entry and dropdown button
        input_container = ttk.Frame(self)
        input_container.pack(fill="x", expand=True)
        
        # Manual entry field
        self.entry = ttk.Entry(input_container, textvariable=variable, font=("Segoe UI", 10), width=20)
        self.entry.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        # Dropdown button
        self.dropdown_btn = ttk.Button(
            input_container, 
            text="▼", 
            width=3,
            command=self.toggle_dropdown,
            bootstyle="secondary-outline"
        )
        self.dropdown_btn.pack(side="left")
        
        # Create hidden dropdown frame (will be placed dynamically)
        self.dropdown_frame = tk.Frame(self.root_window, bg="white", relief="solid", borderwidth=1)
        
        # Listbox for presets
        scrollbar = ttk.Scrollbar(self.dropdown_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.listbox = tk.Listbox(
            self.dropdown_frame, 
            font=("Segoe UI", 10),
            yscrollcommand=scrollbar.set,
            height=6,
            width=20,
            relief="flat"
        )
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)
        
        # Populate listbox
        for preset in presets:
            self.listbox.insert(tk.END, preset)
        
        # Bind selection
        self.listbox.bind("<Button-1>", self.on_select)
        self.listbox.bind("<Return>", self.on_select)
        self.listbox.bind("<Escape>", lambda e: self.close_dropdown())
        
        # Bind entry focus loss
        self.entry.bind("<FocusOut>", lambda e: self.after(100, self.close_dropdown_safe))
        
        # Bind root window click to close dropdown
        self.root_window.bind("<Button-1>", self.on_root_click, add=True)
    
    def toggle_dropdown(self):
        if self.dropdown_open:
            self.close_dropdown()
        else:
            self.open_dropdown()
    
    def open_dropdown(self):
        if self.dropdown_open:
            return
        
        self.dropdown_open = True
        
        # Get entry position
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height() + 2
        width = self.entry.winfo_width() + self.dropdown_btn.winfo_width() + 8
        
        # Place dropdown frame absolutely on root window
        self.dropdown_frame.place(x=x, y=y, width=width, height=140)
        self.listbox.focus()
    
    def close_dropdown(self):
        self.dropdown_open = False
        self.dropdown_frame.place_forget()
    
    def close_dropdown_safe(self):
        if self.dropdown_open:
            self.close_dropdown()
    
    def on_root_click(self, event):
        # Close dropdown if click is outside the entry/button/dropdown
        if self.dropdown_open:
            if not (self.entry.winfo_ismapped() or self.dropdown_btn.winfo_ismapped()):
                return
            
            # Check if click is within entry, button, or dropdown
            entry_x0 = self.entry.winfo_rootx()
            entry_x1 = entry_x0 + self.entry.winfo_width()
            btn_x0 = self.dropdown_btn.winfo_rootx()
            btn_x1 = btn_x0 + self.dropdown_btn.winfo_width()
            
            dropdown_x0 = self.dropdown_frame.winfo_rootx()
            dropdown_x1 = dropdown_x0 + self.dropdown_frame.winfo_width()
            
            entry_y0 = self.entry.winfo_rooty()
            entry_y1 = entry_y0 + self.entry.winfo_height()
            
            dropdown_y0 = self.dropdown_frame.winfo_rooty()
            dropdown_y1 = dropdown_y0 + self.dropdown_frame.winfo_height()
            
            click_in_entry = (entry_x0 <= event.x_root <= entry_x1 and entry_y0 <= event.y_root <= entry_y1)
            click_in_btn = (btn_x0 <= event.x_root <= btn_x1 and entry_y0 <= event.y_root <= entry_y1)
            click_in_dropdown = (dropdown_x0 <= event.x_root <= dropdown_x1 and dropdown_y0 <= event.y_root <= dropdown_y1)
            
            if not (click_in_entry or click_in_btn or click_in_dropdown):
                self.close_dropdown()
    
    def on_select(self, event):
        selection = self.listbox.curselection()
        if selection:
            value = self.listbox.get(selection[0])
            self.variable.set(value)
            self.close_dropdown()

# Financial inputs
financial_inputs = [
    ("💰 Annual Income", "750000", ["500000", "750000", "1000000", "1500000", "2000000"]),
    ("📉 Deductions", "50000", ["0", "50000", "100000", "150000", "200000"]),
    ("🏠 Monthly EMI", "10000", ["0", "5000", "10000", "15000", "20000", "25000"]),
    ("👤 Age", "30", [str(i) for i in range(18, 101, 5)])
]

variables = [income_var, deduction_var, emi_var, age_var]

for i, (label, default, values) in enumerate(financial_inputs):
    row = ttk.Frame(input_grid)
    row.pack(fill="x", pady=8)
    
    ttk.Label(row, text=label, font=("Segoe UI", 10), width=15).pack(side="left")
    
    FlexibleInput(row, variables[i], values).pack(side="left", padx=(15, 0), fill="x", expand=True)

# Action buttons
action_frame = ttk.Frame(left_column)
action_frame.pack(fill="x", pady=(0, 20))

btn_calculate = ttk.Button(action_frame, text="🚀 Calculate Tax", command=calculate_tax, 
                          bootstyle="success", width=20)
btn_calculate.pack(side="left", padx=(0, 15))
btn_calculate.config(state="disabled")

btn_reset = ttk.Button(action_frame, text="🔄 Reset", command=reset_form, 
                     bootstyle="warning", width=15)
btn_reset.pack(side="left", padx=(0, 15))

btn_dashboard = ttk.Button(action_frame, text="📊 View Dashboard", 
                          command=lambda: CompleteDashboard(app.calc_results["steps"], 
                                                           app.calc_results["emi"], 
                                                           app.calc_results["entity"]),
                          bootstyle="info", width=18)
btn_dashboard.pack(side="left", padx=(0, 20))
btn_dashboard.config(state="disabled")

loading_label = ttk.Label(action_frame, text="", font=("Segoe UI", 11, "bold"), bootstyle="info")
loading_label.pack(side="left")

# Quick results card
quick_card = ModernCard(left_column, title="⚡ Quick Results")
quick_card.pack(fill="x", pady=(0, 20))

quick_content = ttk.Frame(quick_card.content)
quick_content.pack(fill="x", pady=15)

ttk.Label(quick_content, text="Tax Payable", font=("Segoe UI", 12)).grid(row=0, column=0, sticky="w", pady=8)
lbl_tax = ttk.Label(quick_content, text="₹0", font=("Segoe UI", 20, "bold"), bootstyle="danger")
lbl_tax.grid(row=0, column=1, sticky="e", pady=8)

ttk.Label(quick_content, text="Net Take-Home", font=("Segoe UI", 12)).grid(row=1, column=0, sticky="w", pady=8)
lbl_takehome = ttk.Label(quick_content, text="₹0", font=("Segoe UI", 20, "bold"), bootstyle="success")
lbl_takehome.grid(row=1, column=1, sticky="e", pady=8)

quick_content.columnconfigure(1, weight=1)

# Efficiency card
efficiency_card = ModernCard(left_column, title="📊 Efficiency Metrics")
efficiency_card.pack(fill="x")

efficiency_content = ttk.Frame(efficiency_card.content)
efficiency_content.pack(fill="x", pady=15)

ttk.Label(efficiency_content, text="Tax Efficiency", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", pady=6)
efficiency_label1 = ttk.Label(efficiency_content, text="0%", font=("Segoe UI", 16, "bold"), bootstyle="info")
efficiency_label1.grid(row=0, column=1, sticky="e", pady=6)

ttk.Label(efficiency_content, text="Savings Potential", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="w", pady=6)
efficiency_label2 = ttk.Label(efficiency_content, text="₹0", font=("Segoe UI", 16, "bold"), bootstyle="warning")
efficiency_label2.grid(row=1, column=1, sticky="e", pady=6)

efficiency_labels = [efficiency_label1, efficiency_label2]
efficiency_content.columnconfigure(1, weight=1)

# Detailed analysis card
details_card = ModernCard(right_column, title="📋 Detailed Tax Analysis")
details_card.pack(fill="both", expand=True)

# Text area with scroll
text_container = ttk.Frame(details_card.content)
text_container.pack(fill="both", expand=True)

txt_details = tk.Text(
    text_container, 
    wrap="word", 
    font=("Segoe UI", 10),
    bg="#f8f9fa",
    fg="#2d3436",
    relief="flat",
    padx=20,
    pady=20,
    borderwidth=0
)
scrollbar = ttk.Scrollbar(text_container, command=txt_details.yview)
txt_details.configure(yscrollcommand=scrollbar.set)

txt_details.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")
txt_details.config(state="disabled")

# Initialize
app.after(100, on_pan_change)

app.mainloop()