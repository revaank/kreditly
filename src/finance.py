"""Transparent rupee calculations used for the live loan summary."""
def emi(principal: float, annual_rate: float, months: int) -> float:
    if months <= 0: return 0.0
    monthly_rate = annual_rate / 1200
    if monthly_rate == 0: return principal / months
    factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * factor / (factor - 1)

def affordability(monthly_income: float, existing_emi: float, new_emi: float) -> float:
    return ((existing_emi + new_emi) / monthly_income * 100) if monthly_income > 0 else 0.0

def foir(monthly_income: float, existing_emi: float, new_emi: float) -> float:
    return affordability(monthly_income, existing_emi, new_emi)

def format_inr(value: float) -> str:
    """Format rupees with Indian digit grouping, e.g. ₹12,00,000."""
    digits = str(int(round(max(0, value))))
    if len(digits) <= 3: return f"₹{digits}"
    rest, groups = digits[:-3], []
    while rest:
        groups.insert(0, rest[-2:]); rest = rest[:-2]
    return "₹" + ",".join(groups + [digits[-3:]])

def loan_summary(principal: float, rate: float, months: int):
    monthly = emi(principal, rate, months); total = monthly * months
    return {"emi": monthly, "interest": max(0, total - principal), "total": total}
