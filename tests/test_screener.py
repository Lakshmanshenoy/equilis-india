"""
tests/test_screener.py
Tests for FundamentalScreener — filter parser, filter logic, and result structure.

No network calls — all tests use mocked or in-memory data.
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screener import FundamentalScreener, SCREENER_DISCLAIMER


@pytest.fixture
def screener():
    return FundamentalScreener(fetcher=None)


# ── Filter parser ──────────────────────────────────────────────────────────────

def test_filter_parser_percent_conversion(screener):
    """Fields in _PERCENT_FIELDS should have their value divided by 100."""
    filters = screener._parse_filters(["roe>15"])
    assert len(filters) == 1
    assert filters[0].field == "roe"
    assert filters[0].op == ">"
    assert abs(filters[0].value - 0.15) < 1e-9


def test_filter_parser_non_percent_field(screener):
    """Non-percent fields (pe_ratio) should retain their raw numeric value."""
    filters = screener._parse_filters(["pe_ratio<30"])
    assert len(filters) == 1
    assert abs(filters[0].value - 30.0) < 1e-9


# ── Filter application ─────────────────────────────────────────────────────────

def test_passes_filters_all_pass(screener):
    """Row satisfying all filters should pass."""
    filters = screener._parse_filters(["roe>15", "pe_ratio<30"])
    row = {"ticker": "TEST", "roe": 0.20, "pe_ratio": 25.0}
    assert screener._passes_filters(row, filters) is True


def test_passes_filters_one_fails(screener):
    """Row failing any filter should not pass."""
    filters = screener._parse_filters(["roe>15", "pe_ratio<30"])
    row = {"ticker": "TEST", "roe": 0.10, "pe_ratio": 25.0}  # roe 10% < 15%
    assert screener._passes_filters(row, filters) is False


def test_passes_filters_missing_field_fails(screener):
    """A missing field must cause the row to fail (conservative behaviour)."""
    filters = screener._parse_filters(["roe>15"])
    row = {"ticker": "TEST", "pe_ratio": 25.0}  # roe missing
    assert screener._passes_filters(row, filters) is False


# ── Screener result ────────────────────────────────────────────────────────────

def test_screener_result_has_disclaimer(screener):
    """SCREENER_DISCLAIMER must contain 'not' and 'recommendation'."""
    disc = SCREENER_DISCLAIMER.lower()
    assert "not" in disc
    assert "recommendation" in disc
