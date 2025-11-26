"""
Tax calculation functions for individual and corporate entities.

Uses New Tax Regime slabs for India (2023+).
"""


def calculate_individual_tax(old_income, deductions, age, employment_type="Salaried"):
    """
    Calculate income tax for an individual using New Tax Regime.

    Args:
        old_income (float): Gross annual income
        deductions (float): Total deductions (standard or itemized)
        age (int): Age of the individual (currently unused in New Regime)
        employment_type (str): "Salaried" or "Self Employed"

    Returns:
        tuple: (total_tax, slab_details, steps_dict)
            - total_tax: final tax payable including cess
            - slab_details: dict of {slab_label: tax_in_slab}
            - steps_dict: detailed breakdown (gross, deductions, taxable, tax_before, rebate, tax_after, cess, total)
    """
    taxable = max(0, old_income - deductions)

    # New Tax Regime slabs (unified for salaried and self-employed)
    slabs = [
        (700_000, 0.00),     # 0-7L: 0%
        (400_000, 0.05),     # 7L-11L: 5%
        (400_000, 0.10),     # 11L-15L: 10%
        (400_000, 0.15),     # 15L-19L: 15%
        (400_000, 0.20),     # 19L-23L: 20%
        (400_000, 0.25),     # 23L-27L: 25%
        (float('inf'), 0.30) # 27L+: 30%
    ]
    labels = ["0–7L", "7L–11L", "11L–15L", "15L–19L", "19L–23L", "23L–27L", "Above 27L"]

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
        "tax_before": round(tax_before, 2),
        "rebate": rebate,
        "tax_after": round(tax_after, 2),
        "cess": round(cess, 2),
        "total": total
    }


def calculate_corporate_tax(gross_income, deductions, entity_type):
    """
    Calculate income tax for a corporate entity.

    Args:
        gross_income (float): Gross annual income
        deductions (float): Total deductions
        entity_type (str): "Company" or other corporate type

    Returns:
        tuple: (total_tax, slab_details, steps_dict)
    """
    taxable = max(0, gross_income - deductions)
    slab_details = {}

    if entity_type == "Company":
        rate = 0.22 if gross_income <= 5_000_000 else 0.30
    else:
        rate = 0.30

    tax_before = taxable * rate
    slab_details[f"{int(rate*100)}% Flat"] = round(tax_before, 2)
    cess = tax_before * 0.04
    total = round(tax_before + cess, 2)

    return total, slab_details, {
        "gross": gross_income,
        "deductions": deductions,
        "taxable": taxable,
        "tax_before": round(tax_before, 2),
        "rebate": 0,
        "tax_after": round(tax_before, 2),
        "cess": round(cess, 2),
        "total": total
    }
