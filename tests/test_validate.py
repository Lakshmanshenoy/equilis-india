"""
tests/test_validate.py
Regression tests for the validation gate.
Run: python -m pytest tests/test_validate.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.validate import run_validation

VALID_DATA = {
    "ticker": "RELIANCE",
    "fetched_at": "2025-05-01T10:00:00Z",
    "fundamentals": {
        "revenue_5y": [450000, 480000, 510000, 530000, 560000],
        "ebitda_5y": [80000, 85000, 90000, 95000, 100000],
        "pat_5y": [23000, 25000, 28000, 30000, 32000],
        "ocf_5y": [20000, 22000, 25000, 27000, 29000],
        "total_debt": 120000,
        "cash": 35000,
        "eps_ttm": 47.5,
        "promoter_holding": 50.1,
        "promoter_pledging": 0.0,
        "trade_receivables_5y": [18000, 20000, 22000, 24000, 26000],
        "inventory_5y": [60000, 65000, 70000, 72000, 75000],
        "trade_payables_5y": [40000, 43000, 46000, 48000, 51000],
    },
    "price": {
        "cmp": 2850.0,
        "week52_high": 3024.0,
        "week52_low": 2220.0,
    }
}


def test_valid_data_passes():
    errors = run_validation(VALID_DATA)
    assert errors == [], f"Expected no errors, got: {errors}"


def test_missing_cmp_flagged():
    data = {**VALID_DATA, "price": {"week52_high": 3024.0, "week52_low": 2220.0}}
    errors = run_validation(data)
    assert any("cmp" in e.lower() for e in errors), "Missing CMP should be flagged"


def test_cmp_above_52w_high_flagged():
    data = {
        **VALID_DATA,
        "price": {"cmp": 3500.0, "week52_high": 3024.0, "week52_low": 2220.0}
    }
    errors = run_validation(data)
    assert any("52W High" in e for e in errors), "CMP > 52W High should be flagged"


def test_promoter_holding_out_of_range():
    fundamentals = {**VALID_DATA["fundamentals"], "promoter_holding": 110.0}
    data = {**VALID_DATA, "fundamentals": fundamentals}
    errors = run_validation(data)
    assert any("promoter_holding" in e for e in errors)


def test_missing_revenue_flagged():
    fundamentals = {k: v for k, v in VALID_DATA["fundamentals"].items() if k != "revenue_5y"}
    data = {**VALID_DATA, "fundamentals": fundamentals}
    errors = run_validation(data)
    assert any("revenue_5y" in e for e in errors)
