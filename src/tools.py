"""Borrower tools: loan offer comparison, prepayment math, and app safety check."""
from __future__ import annotations

import math
from src.finance import emi, loan_summary


def compare_offer(
    amount: float,
    rate: float,
    months: int,
    fee_pct: float | None = None,
    fee_amt: float | None = None,
    other: float = 0.0,
) -> dict:
    """Compare a personal loan offer by computing all-in costs and effective annual rate.

    Returns emi, total_interest, fees (processing fee + 18% GST + other charges),
    total_cost, money_in_hand, and effective_annual_rate (annual rate r such that
    the present value of the EMI stream equals money_in_hand, solved by bisection).
    """
    amount = float(amount)
    rate = float(rate)
    months = int(months)
    other = float(other or 0.0)

    if fee_amt is not None and fee_amt != "":
        proc_fee = float(fee_amt)
    elif fee_pct is not None and fee_pct != "":
        proc_fee = amount * (float(fee_pct) / 100.0)
    else:
        proc_fee = 0.0

    gst = proc_fee * 0.18
    fees = proc_fee + gst + other
    summary = loan_summary(amount, rate, months)
    emi_val = summary["emi"]
    total_interest = summary["interest"]
    total_cost = total_interest + fees
    money_in_hand = amount - fees

    # Compute effective annual rate via bisection (monthly IRR * 12)
    # Target: E * (1 - (1+m)^(-n)) / m = money_in_hand
    if money_in_hand <= 0 or emi_val <= 0 or months <= 0:
        effective_annual_rate = 0.0
    elif abs(fees) < 1e-6:
        effective_annual_rate = round(rate, 2)
    else:
        # Bisection on monthly rate m
        low = 0.0
        high = 5.0  # 500% monthly rate
        # Function: f(m) = PV(m) - money_in_hand
        # PV(m) decreases as m increases
        # At m=0, PV = months * emi_val
        pv_low = months * emi_val
        if pv_low <= money_in_hand:
            # Net money received >= total repayments (extremely negative fees or zero interest)
            effective_annual_rate = 0.0
        else:
            # Ensure high is high enough
            for _ in range(10):
                pv_high = emi_val * (1.0 - (1.0 + high) ** (-months)) / high
                if pv_high < money_in_hand:
                    break
                high *= 2.0

            for _ in range(80):
                mid = (low + high) / 2.0
                if mid == 0:
                    pv_mid = months * emi_val
                else:
                    pv_mid = emi_val * (1.0 - (1.0 + mid) ** (-months)) / mid
                if pv_mid > money_in_hand:
                    low = mid
                else:
                    high = mid

            monthly_irr = (low + high) / 2.0
            effective_annual_rate = round(monthly_irr * 12.0 * 100.0, 2)

    return {
        "emi": emi_val,
        "total_interest": total_interest,
        "proc_fee": proc_fee,
        "gst": gst,
        "other": other,
        "fees": fees,
        "total_cost": total_cost,
        "money_in_hand": money_in_hand,
        "effective_annual_rate": effective_annual_rate,
    }


def prepay(
    amount: float,
    rate: float,
    months: int,
    after_month: int,
    lump: float,
    charge_pct: float = 0.0,
    mode: str = "tenure",
) -> dict:
    """Compute interest and time/EMI savings from a lump-sum prepayment.

    Parameters:
      amount: loan principal in ₹
      rate: annual interest rate in %
      months: total loan tenure in months
      after_month: prepayment done after this many EMIs paid (1 .. months-1)
      lump: lump sum amount in ₹
      charge_pct: prepayment/foreclosure charge (% of lump prepaid)
      mode: 'tenure' (keep EMI, finish sooner) or 'emi' (keep end date, lower EMI)
    """
    amount = float(amount)
    rate = float(rate)
    months = int(months)
    after_month = max(1, min(int(after_month), months - 1))
    lump = max(0.0, float(lump))
    charge_pct = max(0.0, float(charge_pct))
    norm_mode = "emi" if "emi" in str(mode).lower() else "tenure"

    r_month = (rate / 1200.0) if rate > 0 else 0.0
    orig_emi = emi(amount, rate, months)

    # 1. Simulate original schedule
    bal = amount
    orig_balances = [bal]
    orig_interests = []
    for _ in range(months):
        if r_month > 0:
            int_m = bal * r_month
            prin_m = orig_emi - int_m
        else:
            int_m = 0.0
            prin_m = orig_emi
        if prin_m > bal:
            prin_m = bal
        bal = max(0.0, bal - prin_m)
        orig_balances.append(bal)
        orig_interests.append(int_m)

    outstanding_balance = orig_balances[after_month]
    orig_remaining_interest = sum(orig_interests[after_month:])

    if lump <= 0 or outstanding_balance <= 0.01:
        return {
            "outstanding_balance": outstanding_balance,
            "is_foreclosure": False,
            "lump_used": 0.0,
            "charge_paid": 0.0,
            "interest_saved": 0.0,
            "months_saved": 0,
            "new_emi": orig_emi,
            "net_saving": 0.0,
            "original_balances": orig_balances,
            "prepay_balances": list(orig_balances),
        }

    # Check foreclosure
    is_foreclosure = lump >= (outstanding_balance - 0.5)
    actual_lump = outstanding_balance if is_foreclosure else lump
    charge_paid = actual_lump * (charge_pct / 100.0)

    if is_foreclosure:
        interest_saved = orig_remaining_interest
        months_saved = months - after_month
        new_emi = 0.0
        net_saving = interest_saved - charge_paid
        prepay_balances = list(orig_balances[:after_month + 1])
        prepay_balances[-1] = 0.0
        while len(prepay_balances) <= months:
            prepay_balances.append(0.0)

        return {
            "outstanding_balance": outstanding_balance,
            "is_foreclosure": True,
            "lump_used": actual_lump,
            "charge_paid": charge_paid,
            "interest_saved": interest_saved,
            "months_saved": months_saved,
            "new_emi": new_emi,
            "net_saving": net_saving,
            "original_balances": orig_balances,
            "prepay_balances": prepay_balances,
        }

    new_balance = outstanding_balance - actual_lump
    rem_months = months - after_month

    if norm_mode == "tenure":
        # Keep EMI, finish sooner
        new_emi = orig_emi
        cur_bal = new_balance
        prepay_balances = list(orig_balances[:after_month + 1])
        prepay_balances[-1] = cur_bal
        new_remaining_interest = 0.0
        months_used = 0

        while cur_bal > 0.01 and months_used < rem_months:
            int_m = cur_bal * r_month
            prin_m = orig_emi - int_m
            if prin_m >= cur_bal:
                prin_m = cur_bal
                cur_bal = 0.0
                new_remaining_interest += int_m
                months_used += 1
                prepay_balances.append(0.0)
                break
            cur_bal -= prin_m
            new_remaining_interest += int_m
            months_used += 1
            prepay_balances.append(cur_bal)

        while len(prepay_balances) <= months:
            prepay_balances.append(0.0)

        months_saved = rem_months - months_used
        interest_saved = max(0.0, orig_remaining_interest - new_remaining_interest)
        net_saving = interest_saved - charge_paid

    else:
        # Keep end date, lower EMI
        new_emi = emi(new_balance, rate, rem_months)
        cur_bal = new_balance
        prepay_balances = list(orig_balances[:after_month + 1])
        prepay_balances[-1] = cur_bal
        new_remaining_interest = 0.0

        for _ in range(rem_months):
            int_m = cur_bal * r_month
            prin_m = new_emi - int_m
            if prin_m >= cur_bal:
                prin_m = cur_bal
                cur_bal = 0.0
            else:
                cur_bal -= prin_m
            new_remaining_interest += int_m
            prepay_balances.append(cur_bal)

        months_saved = 0
        interest_saved = max(0.0, orig_remaining_interest - new_remaining_interest)
        net_saving = interest_saved - charge_paid

    return {
        "outstanding_balance": outstanding_balance,
        "is_foreclosure": False,
        "lump_used": actual_lump,
        "charge_paid": charge_paid,
        "interest_saved": interest_saved,
        "months_saved": months_saved,
        "new_emi": new_emi,
        "net_saving": net_saving,
        "original_balances": orig_balances,
        "prepay_balances": prepay_balances,
    }
