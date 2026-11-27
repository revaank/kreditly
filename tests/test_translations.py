"""Tests for translation completeness and sample cases integrity."""
from __future__ import annotations

import json
from pathlib import Path
from src.profiles import DEFAULT_PROFILE
from src.translations import EN, HI


def test_every_key_in_en_exists_in_hi():
    diff = set(EN.keys()) - set(HI.keys())
    assert not diff, f"Keys present in EN but missing in HI: {diff}"


def test_every_key_in_hi_exists_in_en():
    diff = set(HI.keys()) - set(EN.keys())
    assert not diff, f"Keys present in HI but missing in EN: {diff}"


def test_samples_have_all_default_profile_keys():
    cases_path = Path(__file__).resolve().parents[1] / "src" / "sample_cases.json"
    assert cases_path.exists(), "sample_cases.json not found"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    assert len(cases) > 0, "No sample cases found"

    required_keys = set(DEFAULT_PROFILE.keys())
    for case in cases:
        case_id = case.get("id", "unknown")
        values = case.get("values", {})
        missing = required_keys - set(values.keys())
        assert not missing, f"Sample '{case_id}' is missing DEFAULT_PROFILE keys: {missing}"
