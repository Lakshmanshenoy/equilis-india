"""
tests/test_dupont.py
Tests for EquityAnalyzer.compute_dupont_trend() — multi-year DuPont decomposition.
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_analyzer import build_snapshot_from_fixture, load_fixture
from core.analyzer import EquityAnalyzer
from core.models.ratios import DuPontResult


@pytest.fixture
def infy_snapshot():
    return build_snapshot_from_fixture(load_fixture("infy_fy24.json"))


@pytest.fixture
def analyzer():
    return EquityAnalyzer()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_dupont_returns_5_years_for_complete_history(analyzer, infy_snapshot):
    result = analyzer.compute_dupont_trend(infy_snapshot)
    assert isinstance(result, DuPontResult)
    assert len(result.by_year) == 5, (
        f"Expected 5 years of DuPont data, got {len(result.by_year)}"
    )


def test_dupont_product_equals_reported_roe(analyzer, infy_snapshot):
    """NPM × AT × EM must equal PAT/Equity (reconciliation_gap < 0.01)."""
    result = analyzer.compute_dupont_trend(infy_snapshot)
    for yr in result.by_year:
        assert yr["reconciliation_gap"] < 0.01, (
            f"{yr['fiscal_year']}: DuPont gap={yr['reconciliation_gap']:.4f} "
            f"(dupont={yr['roe_dupont']:.4f}, reported={yr['roe_reported']:.4f})"
        )


def test_dupont_latest_year_is_fy24(analyzer, infy_snapshot):
    result = analyzer.compute_dupont_trend(infy_snapshot)
    assert result.by_year[0]["fiscal_year"] == "FY24"


def test_dupont_handles_missing_year_gracefully(analyzer, infy_snapshot):
    """If one year has missing equity, it should be silently skipped."""
    infy_snapshot.history[2].equity = None     # FY22 — third year
    result = analyzer.compute_dupont_trend(infy_snapshot)
    years_in_result = [yr["fiscal_year"] for yr in result.by_year]
    assert "FY22" not in years_in_result
    assert len(result.by_year) == 4


def test_dupont_driver_observation_is_non_empty(analyzer, infy_snapshot):
    result = analyzer.compute_dupont_trend(infy_snapshot)
    assert isinstance(result.driver_observation, str)
    assert len(result.driver_observation) > 20, (
        "driver_observation should be a meaningful description"
    )


def test_dupont_trend_note_mentions_margin_direction(analyzer, infy_snapshot):
    result = analyzer.compute_dupont_trend(infy_snapshot)
    note = result.trend_note.lower()
    # INFY NPM: FY20=0.1828, FY24=0.1708 → compressed
    assert "compressed" in note or "expanded" in note, (
        f"trend_note should mention margin direction: {result.trend_note}"
    )


def test_dupont_roe_values_in_plausible_range(analyzer, infy_snapshot):
    result = analyzer.compute_dupont_trend(infy_snapshot)
    for yr in result.by_year:
        # INFY ROE ~0.24-0.38 range based on fixture data
        assert 0.10 < yr["roe_dupont"] < 0.60, (
            f"{yr['fiscal_year']}: ROE {yr['roe_dupont']:.4f} out of expected range"
        )
