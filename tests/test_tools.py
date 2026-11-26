import pytest
from src.tools import app_safety_result, compare_offer, prepay


def test_compare_offer_zero_fees():
    res = compare_offer(300000, 12.0, 36, fee_pct=0, other=0)
    assert abs(res["effective_annual_rate"] - 12.0) <= 0.05
    assert res["fees"] == 0.0
    assert res["gst"] == 0.0
    assert res["money_in_hand"] == 300000.0


def test_compare_offer_gst_and_higher_fee():
    res1 = compare_offer(300000, 12.0, 36, fee_pct=1.0, other=0)
    res2 = compare_offer(300000, 12.0, 36, fee_pct=3.0, other=0)

    # GST is 18% of processing fee
    # For 3,00,000 at 1%, proc_fee = 3,000, gst = 540, fees = 3,540
    assert res1["proc_fee"] == 3000.0
    assert res1["gst"] == pytest.approx(540.0, 0.01)
    assert res1["fees"] == pytest.approx(3540.0, 0.01)

    # Higher fee -> higher effective annual rate
    assert res2["effective_annual_rate"] > res1["effective_annual_rate"]
    assert res1["effective_annual_rate"] > 12.0


def test_compare_offer_flat_fee():
    res = compare_offer(300000, 11.0, 36, fee_amt=5000, other=500)
    assert res["proc_fee"] == 5000.0
    assert res["gst"] == 900.0
    assert res["fees"] == 6400.0
    assert res["money_in_hand"] == 300000.0 - 6400.0


def test_prepay_zero_lump():
    res = prepay(300000, 11.0, 36, 12, lump=0)
    assert res["interest_saved"] == 0.0
    assert res["net_saving"] == 0.0
    assert res["months_saved"] == 0
    assert res["charge_paid"] == 0.0


def test_prepay_full_foreclosure():
    res = prepay(300000, 11.0, 36, 12, lump=500000)
    assert res["is_foreclosure"] is True
    assert res["months_saved"] == 24  # 36 - 12
    assert res["new_emi"] == 0.0
    assert res["interest_saved"] > 0.0
    assert res["net_saving"] == res["interest_saved"]  # charge_pct is 0


def test_prepay_mode_tenure_vs_emi():
    # After 12 months, prepay 50,000
    res_tenure = prepay(300000, 11.0, 36, 12, lump=50000, mode="tenure")
    res_emi = prepay(300000, 11.0, 36, 12, lump=50000, mode="emi")

    # Mode 1 (tenure) saves months
    assert res_tenure["months_saved"] > 0
    assert res_tenure["interest_saved"] > 0

    # Mode 2 (emi) lowers EMI
    assert res_emi["months_saved"] == 0
    assert res_emi["new_emi"] < res_tenure["new_emi"]
    assert res_emi["interest_saved"] > 0


def test_prepay_charge_reduces_saving():
    res_no_charge = prepay(300000, 11.0, 36, 12, lump=50000, charge_pct=0.0)
    res_with_charge = prepay(300000, 11.0, 36, 12, lump=50000, charge_pct=3.0)

    assert res_with_charge["charge_paid"] == 1500.0
    assert res_with_charge["interest_saved"] == pytest.approx(res_no_charge["interest_saved"], 0.01)
    assert res_with_charge["net_saving"] == pytest.approx(res_no_charge["net_saving"] - 1500.0, 0.01)


def test_app_safety_all_safe():
    # Q1: yes, Q2: no, Q3: no, Q4: yes, Q5: no, Q6: no
    safe_answers = ["yes", "no", "no", "yes", "no", "no"]
    res = app_safety_result(safe_answers)
    assert res["status"] == "green"
    assert res["level"] == "success"
    assert res["red_flags"] == 0
    assert res["not_sures"] == 0
    assert res["safe_count"] == 6


def test_app_safety_all_not_sure():
    res = app_safety_result(["not_sure"] * 6)
    assert res["status"] == "unanswered"
    assert res["level"] == "info"
    assert res["red_flags"] == 0
    assert res["not_sures"] == 6


def test_app_safety_incomplete_no_red_flags():
    # 5 safe, 1 not_sure
    answers = ["yes", "no", "no", "yes", "no", "not_sure"]
    res = app_safety_result(answers)
    assert res["status"] == "incomplete"
    assert res["level"] == "warning"
    assert res["red_flags"] == 0
    assert res["not_sures"] == 1
    assert res["safe_count"] == 5


def test_app_safety_one_red_flag():
    # Q2 (fees before loan) answered Yes -> 1 red flag
    answers = ["yes", "yes", "no", "yes", "no", "no"]
    res = app_safety_result(answers)
    assert res["status"] == "amber"
    assert res["level"] == "warning"
    assert res["red_flags"] == 1


def test_app_safety_multiple_red_flags():
    # Q2 (fee before) yes, Q3 (access contacts) yes -> 2 red flags
    answers = ["yes", "yes", "yes", "yes", "no", "no"]
    res = app_safety_result(answers)
    assert res["status"] == "red"
    assert res["level"] == "error"
    assert res["red_flags"] == 2


def test_app_safety_red_flag_with_not_sure():
    # 1 red flag, 2 not sure -> still amber
    answers = ["yes", "yes", "not_sure", "not_sure", "no", "no"]
    res = app_safety_result(answers)
    assert res["status"] == "amber"
    assert res["red_flags"] == 1
    assert res["not_sures"] == 2
