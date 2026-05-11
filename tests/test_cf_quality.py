"""
tests/test_cf_quality.py
Tests for EquityAnalyzer.compute_cf_quality_trend() — multi-year CFO/PAT quality.
"""

import sys
import os
import copy

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_analyzer import build_snapshot_from_fixture, load_fixture
from core.analyzer import EquityAnalyzer
from core.models.ratios import CashFlowQualityResult


@pytest.fixture
def infy_snapshot():
    return build_snapshot_from_fixture(load_fixture("infy_fy24.json"))


@pytest.fixture
def analyzer():
    return EquityAnalyzer()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_cf_quality_returns_result_type(analyzer, infy_snapshot):
    result = analyzer.compute_cf_quality_trend(infy_snapshot)
    assert isinstance(result, CashFlowQualityResult)


def test_cf_quality_high_signal_for_infy(analyzer, infy_snapshot):
    """All INFY fixture years have CFO/PAT > 1.0 → overall signal should be HIGH."""
    result = analyzer.compute_cf_quality_trend(infy_snapshot)
    # FY24: 31200/26248 ≈ 1.189; all years similarly above 1.0
    assert result.overall_signal == "HIGH", (
        f"Expected HIGH signal for INFY, got {result.overall_signal}"
    )


def test_cf_quality_returns_5_years(analyzer, infy_snapshot):
    result = analyzer.compute_cf_quality_trend(infy_snapshot)
    assert len(result.by_year) == 5


def test_cf_quality_cfo_pat_ratio_correct(analyzer, infy_snapshot):
    """FY24 CFO/PAT = 31200/26248 ≈ 1.188."""
    result = analyzer.compute_cf_quality_trend(infy_snapshot)
    fy24 = next(yr for yr in result.by_year if yr["fiscal_year"] == "FY24")
    expected = 31200 / 26248
    assert abs(fy24["cfo_pat"] - expected) < 0.01, (
        f"Expected CFO/PAT ≈ {expected:.3f}, got {fy24['cfo_pat']}"
    )


def test_red_signal_when_cfo_negative_pat_positive(analyzer, infy_snapshot):
    """If CFO is negative while PAT is positive → signal RED, overall RED."""
    infy_snapshot.history[0].cfo = -500.0   # FY24: turn CFO negative
    result = analyzer.compute_cf_quality_trend(infy_snapshot)
    fy24 = next(yr for yr in result.by_year if yr["fiscal_year"] == "FY24")
    assert fy24["signal"] == "RED"
    assert result.overall_signal == "RED"


def test_consecutive_low_count(analyzer, infy_snapshot):
    """Force FY24 and FY23 to LOW (ratio < 0.8) → consecutive_low_years = 2."""
    infy_snapshot.history[0].cfo = infy_snapshot.history[0].pat * 0.6  # FY24 → LOW
    infy_snapshot.history[1].cfo = infy_snapshot.history[1].pat * 0.7  # FY23 → LOW
    result = analyzer.compute_cf_quality_trend(infy_snapshot)
    assert result.consecutive_low_years == 2


def test_low_signal_when_ratio_below_0_8(analyzer, infy_snapshot):
    """CFO/PAT = 0.65 → LOW signal."""
    infy_snapshot.history[0].cfo = infy_snapshot.history[0].pat * 0.65
    result = analyzer.compute_cf_quality_trend(infy_snapshot)
    fy24 = next(yr for yr in result.by_year if yr["fiscal_year"] == "FY24")
    assert fy24["signal"] == "LOW"


def test_medium_signal_when_ratio_0_85(analyzer, infy_snapshot):
    """CFO/PAT = 0.85 → MEDIUM signal."""
    infy_snapshot.history[0].cfo = infy_snapshot.history[0].pat * 0.85
    result = analyzer.compute_cf_quality_trend(infy_snapshot)
    fy24 = next(yr for yr in result.by_year if yr["fiscal_year"] == "FY24")
    assert fy24["signal"] == "MEDIUM"


def test_observations_populated_on_red_year(analyzer, infy_snapshot):
    """RED signal year should generate an observation string."""
    infy_snapshot.history[0].cfo = -1000.0
    result = analyzer.compute_cf_quality_trend(infy_snapshot)
    assert any("FY24" in obs for obs in result.observations), (
        "Expected FY24 observation for RED signal year"
    )
