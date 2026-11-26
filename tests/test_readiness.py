"""Unit tests for Indian lending readiness, standing rules, and safe borrowing calculations."""
import pytest
from src.readiness import safe_loan_amount, standing, standing_reasons, total_foir, normalize_cibil


def test_total_foir():
    assert total_foir(65000, 5000, 10000) == pytest.approx(23.1, abs=0.1)
    assert total_foir(100000, 0, 25000) == 25.0
    assert total_foir(0, 5000, 5000) == 100.0
    assert total_foir(0, 0, 0) == 0.0


def test_normalize_cibil():
    assert normalize_cibil(0) == "excellent"
    assert normalize_cibil(1) == "good"
    assert normalize_cibil(2) == "average"
    assert normalize_cibil(3) == "low"
    assert normalize_cibil(4) == "no_history"
    assert normalize_cibil(5) == "dont_know"
    assert normalize_cibil("Excellent · 750+") == "excellent"
    assert normalize_cibil("Good · 700–749") == "good"
    assert normalize_cibil("Average · 650–699") == "average"
    assert normalize_cibil("Low · below 650") == "low"
    assert normalize_cibil("Don't know") == "dont_know"
    assert normalize_cibil("उत्कृष्ट (750+)") == "excellent"


def test_standing_good():
    # FOIR <= 40, CIBIL Excellent or Good, lenders >= half
    assert standing(foir_pct=25.0, cibil_band="good", lenders_meeting=5, lenders_total=6) == "good"
    assert standing(foir_pct=40.0, cibil_band="excellent", lenders_meeting=3, lenders_total=6) == "good"
    assert standing(foir_pct=39.9, cibil_band=1, lenders_meeting=3, lenders_total=6) == "good"


def test_standing_almost():
    # Edge case 1: FOIR just above 40 (40.1%), good CIBIL, half lenders -> almost
    assert standing(foir_pct=40.1, cibil_band="good", lenders_meeting=5, lenders_total=6) == "almost"

    # Edge case 2: Exactly 55% FOIR, average CIBIL, >= 1 lender -> almost
    assert standing(foir_pct=55.0, cibil_band="average", lenders_meeting=2, lenders_total=6) == "almost"

    # CIBIL "Don't know" counts as not Low
    assert standing(foir_pct=35.0, cibil_band="dont_know", lenders_meeting=4, lenders_total=6) == "almost"
    assert standing(foir_pct=50.0, cibil_band=4, lenders_meeting=1, lenders_total=6) == "almost"

    # Low lender count (< half, but >= 1) with low FOIR and good CIBIL -> almost
    assert standing(foir_pct=25.0, cibil_band="good", lenders_meeting=2, lenders_total=6) == "almost"


def test_standing_work():
    # FOIR above 55% -> work
    assert standing(foir_pct=55.1, cibil_band="good", lenders_meeting=5, lenders_total=6) == "work"
    assert standing(foir_pct=80.0, cibil_band="excellent", lenders_meeting=6, lenders_total=6) == "work"

    # CIBIL is Low (<650) -> work (even if FOIR is very low)
    assert standing(foir_pct=20.0, cibil_band="low", lenders_meeting=5, lenders_total=6) == "work"
    assert standing(foir_pct=30.0, cibil_band=3, lenders_meeting=5, lenders_total=6) == "work"

    # 0 lenders meeting -> work
    assert standing(foir_pct=30.0, cibil_band="good", lenders_meeting=0, lenders_total=6) == "work"


def test_standing_reasons():
    reasons = standing_reasons(foir_pct=23.0, cibil_band="good", lenders_meeting=5, lenders_total=6)
    assert len(reasons) == 3
    assert any("23%" in r for r in reasons)
    assert any("Good" in r for r in reasons)
    assert any("5 of 6" in r for r in reasons)


def test_safe_loan_amount_hand_calculated():
    # Hand-calculated example:
    # Monthly income: ₹65,000, Existing EMI: ₹5,000, 11% rate, 36 months
    # Comfortable (40% FOIR limit = ₹26,000 - ₹5,000 = ₹21,000 EMI available)
    # Principal for ₹21,000 EMI is ₹6,41,442 -> rounded down to ₹6,40,000
    safe_comf = safe_loan_amount(monthly_income=65000, existing_emi=5000, annual_rate=11.0, months=36, max_foir=40)
    assert safe_comf == 640000

    # Stretch (50% FOIR limit = ₹32,500 - ₹5,000 = ₹27,500 EMI available)
    # Principal for ₹27,500 EMI is ₹8,39,984 -> rounded down to ₹8,30,000
    safe_stretch = safe_loan_amount(monthly_income=65000, existing_emi=5000, annual_rate=11.0, months=36, max_foir=50)
    assert safe_stretch == 830000


def test_safe_loan_amount_existing_emi_exceeds_limit():
    # When existing EMI already exceeds max_foir limit, returns 0
    # 40% of 65000 is 26000. If existing EMI is 27000:
    assert safe_loan_amount(monthly_income=65000, existing_emi=27000, annual_rate=11.0, months=36, max_foir=40) == 0

    # Boundary case: existing EMI equals limit exactly:
    assert safe_loan_amount(monthly_income=65000, existing_emi=26000, annual_rate=11.0, months=36, max_foir=40) == 0

    # Invalid inputs return 0
    assert safe_loan_amount(monthly_income=0, existing_emi=5000, annual_rate=11.0, months=36, max_foir=40) == 0
    assert safe_loan_amount(monthly_income=65000, existing_emi=5000, annual_rate=11.0, months=0, max_foir=40) == 0
