import pytest

from src.india_model import FEATURES, assess, build_features

BASE = dict(age=30, employment="salaried", cibil_band="good", credit_years=5, active_loans=1,
            overdue_loans=0, missed_emi_last_6m=0, new_loans_last_6m=0, loan_enquiries=0, existing_emi=5000)


def test_build_features_shape_and_order():
    X, assumed = build_features(BASE)
    assert list(X.columns) == FEATURES
    assert assumed == []
    assert X.iloc[0]["bureau_score"] == 720
    assert X.iloc[0]["credit_history_months"] == 60


def test_no_history_sets_flag_and_zero_defaults():
    X, assumed = build_features(dict(age=22, employment="salaried", cibil_band="no_history"))
    assert X.iloc[0]["no_credit_history"] == 1
    assert X.iloc[0]["active_loans"] == 0
    assert assumed == []


def test_dont_know_marks_assumed():
    _, assumed = build_features(dict(age=28, employment="self_employed", cibil_band="dont_know"))
    assert "bureau_score" in assumed
    assert "credit_history_months" in assumed


def test_exact_score_wins_over_band():
    X, _ = build_features({**BASE, "cibil_score": 801})
    assert X.iloc[0]["bureau_score"] == 801


@pytest.mark.parametrize("feature", ["missed_emi_last_6m", "overdue_loans", "loan_enquiries", "new_loans_last_6m"])
def test_more_problems_never_lower_risk(feature):
    probs = [assess({**BASE, feature: n})["probability"] for n in range(5)]
    assert all(b >= a - 1e-6 for a, b in zip(probs, probs[1:]))


def test_assess_output():
    r = assess(BASE)
    assert r["band"] in {"lower", "typical", "higher"}
    assert 0 <= r["probability"] <= 1
    assert len(r["reasons"]) == 3
    assert r["reasons"][2]["label"]


def test_stressed_profile_is_higher_than_strong():
    strong = assess({**BASE, "cibil_band": "excellent"})
    stressed = assess({**BASE, "cibil_band": "low", "overdue_loans": 2, "missed_emi_last_6m": 2, "loan_enquiries": 4})
    assert stressed["probability"] > strong["probability"]
    assert stressed["band"] == "higher"


def test_hindi_labels():
    r = assess(BASE, lang="hi")
    assert any("ऀ" <= ch <= "ॿ" for ch in r["reasons"][0]["label"])
