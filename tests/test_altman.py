"""
tests/test_altman.py
Tests for EquityAnalyzer.compute_altman_z()

Uses infy and hdfcbank fixtures from conftest.py.
No network calls — all data from fixtures.
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import EquityAnalyzer


@pytest.fixture
def analyzer():
    return EquityAnalyzer()


def test_altman_safe_zone_for_infy(analyzer, infy):
    """INFY is a healthy IT company with no debt — should be firmly in SAFE zone."""
    result = analyzer.compute_altman_z(infy)
    assert not result.get("skipped"), f"Expected result, got skipped: {result.get('reason')}"
    assert result["z_score"] > 2.99, f"Expected SAFE zone (>2.99), got {result['z_score']}"
    assert result["zone"] == "SAFE"


def test_altman_skipped_for_banking_sector(analyzer, hdfcbank):
    """Banking sector stocks must be skipped — model not applicable to financial firms."""
    hdfcbank.sector = "Banking"
    result = analyzer.compute_altman_z(hdfcbank)
    assert result.get("skipped") is True
    assert "reason" in result
    assert "Banking" in result["reason"] or "financial" in result["reason"].lower()


def test_altman_skipped_when_data_missing(analyzer, infy):
    """Setting working_capital=None on the snapshot should force a skip."""
    infy.working_capital = None
    result = analyzer.compute_altman_z(infy)
    assert result.get("skipped") is True
    assert "reason" in result


def test_altman_disclaimer_present(analyzer, infy):
    """Disclaimer must be present and mention academic use only."""
    result = analyzer.compute_altman_z(infy)
    if result.get("skipped"):
        pytest.skip("Snapshot did not have enough data for Z-Score (fixture issue)")
    disc = result.get("disclaimer", "")
    assert disc, "Disclaimer must not be empty"
    disc_lower = disc.lower()
    assert "academic" in disc_lower or "not validated" in disc_lower or "research" in disc_lower, (
        f"Disclaimer should mention academic/not validated/research: '{disc}'"
    )


def test_altman_component_sum_equals_z(analyzer, infy):
    """Math check: 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5 must equal z_score."""
    result = analyzer.compute_altman_z(infy)
    if result.get("skipped"):
        pytest.skip("Snapshot did not have enough data for Z-Score (fixture issue)")
    computed = (
        1.2 * result["X1"]
        + 1.4 * result["X2"]
        + 3.3 * result["X3"]
        + 0.6 * result["X4"]
        + 1.0 * result["X5"]
    )
    assert abs(computed - result["z_score"]) < 0.01, (
        f"Component sum {computed:.4f} != z_score {result['z_score']:.4f}"
    )
