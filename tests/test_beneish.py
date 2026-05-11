"""
tests/test_beneish.py
Tests for Beneish M-score computation.
Run: python -m pytest tests/test_beneish.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.beneish import compute_beneish, interpret

CLEAN_YEAR1 = {
    "revenue": 100000, "gross_profit": 30000, "total_assets": 80000,
    "current_assets": 20000, "ppe": 40000, "depreciation": 4000,
    "sga": 5000, "total_debt": 20000, "trade_receivables": 10000,
    "net_income": 8000, "ocf": 9000, "cogs": 70000,
}
CLEAN_YEAR2 = {
    "revenue": 95000, "gross_profit": 28000, "total_assets": 75000,
    "current_assets": 18000, "ppe": 38000, "depreciation": 3800,
    "sga": 4800, "total_debt": 19000, "trade_receivables": 9500,
    "net_income": 7500, "ocf": 8500, "cogs": 67000,
}


def test_clean_company_low_risk():
    result = compute_beneish(CLEAN_YEAR1, CLEAN_YEAR2)
    assert result["m_score"] is not None
    assert result["m_score"] < -2.22, f"Expected low risk, got M={result['m_score']:.3f}"


def test_interpret_returns_string():
    assert isinstance(interpret(-3.0), str)
    assert isinstance(interpret(-2.0), str)
    assert isinstance(interpret(-1.5), str)
    assert isinstance(interpret(None), str)


def test_missing_data_handled():
    year1_incomplete = {k: v for k, v in CLEAN_YEAR1.items() if k != "sga"}
    result = compute_beneish(year1_incomplete, CLEAN_YEAR2)
    # Should still run without crash, missing_fields should be 1
    assert result["missing_fields"] >= 1
