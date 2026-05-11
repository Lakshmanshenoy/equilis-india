"""
tests/test_red_flags.py
Tests for EquityAnalyzer.run_red_flag_scan() — structured RedFlagScanResult.
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_analyzer import build_snapshot_from_fixture, load_fixture
from core.analyzer import EquityAnalyzer
from core.models.ratios import RedFlagScanResult
from core.models.company import ShareholdingData


@pytest.fixture
def infy_snapshot():
    return build_snapshot_from_fixture(load_fixture("infy_fy24.json"))


@pytest.fixture
def analyzer():
    return EquityAnalyzer()


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_run_red_flag_scan_returns_result_type(analyzer, infy_snapshot):
    result = analyzer.run_red_flag_scan(infy_snapshot)
    assert isinstance(result, RedFlagScanResult)


def test_no_red_flags_for_clean_fixture(analyzer, infy_snapshot):
    """
    INFY fixture has healthy financials:
    - Receivables growing in line with revenue (no inflation)
    - No negative CFO
    - No promoter pledge (ShareholdingData defaults to None pledging)
    → red_count should be 0.
    """
    result = analyzer.run_red_flag_scan(infy_snapshot)
    assert result.red_count == 0, (
        f"Expected red_count=0 for clean fixture, got {result.red_count}. "
        f"Flags: {[f['flag_id'] for f in result.flags if f['severity']=='RED']}"
    )


def test_negative_cfo_triggers_red_flag(analyzer, infy_snapshot):
    """CFO negative while PAT positive → NEGATIVE_CFO_POSITIVE_PAT RED flag."""
    infy_snapshot.history[0].cfo = -1000.0   # FY24: negative CFO
    result = analyzer.run_red_flag_scan(infy_snapshot)
    flag_ids = [f["flag_id"] for f in result.flags]
    assert "NEGATIVE_CFO_POSITIVE_PAT" in flag_ids
    red_flags = [f for f in result.flags if f["flag_id"] == "NEGATIVE_CFO_POSITIVE_PAT"]
    assert all(f["severity"] == "RED" for f in red_flags)
    assert result.red_count >= 1


def test_high_promoter_pledge_triggers_yellow(analyzer, infy_snapshot):
    """Promoter pledge > 30% → HIGH_PROMOTER_PLEDGE YELLOW flag."""
    if infy_snapshot.shareholding is None:
        infy_snapshot.shareholding = ShareholdingData(
            promoter_holding=60.0,
            promoter_pledging=45.0,
            fii_holding=20.0,
            dii_holding=15.0,
            public_holding=5.0,
            promoter_holding_history=[60.0, 61.0, 62.0],
        )
    else:
        infy_snapshot.shareholding.promoter_pledging = 45.0
    result = analyzer.run_red_flag_scan(infy_snapshot)
    flag_ids = [f["flag_id"] for f in result.flags]
    assert "HIGH_PROMOTER_PLEDGE" in flag_ids
    pledge_flag = next(f for f in result.flags if f["flag_id"] == "HIGH_PROMOTER_PLEDGE")
    assert pledge_flag["severity"] == "YELLOW"


def test_receivables_growth_flag(analyzer, infy_snapshot):
    """
    Inflate latest receivables 3x the revenue CAGR → RECEIVABLES_GROWTH_EXCEEDS_REVENUE flag.
    Revenue 3yr CAGR ≈ 15.2%; need rec_cagr > 18.3%.
    FY20 receivables=15200, so set FY24 receivables=100000 to get huge CAGR.
    """
    infy_snapshot.history[0].receivables = 100000   # FY24 → huge rec_cagr
    result = analyzer.run_red_flag_scan(infy_snapshot)
    flag_ids = [f["flag_id"] for f in result.flags]
    assert "RECEIVABLES_GROWTH_EXCEEDS_REVENUE" in flag_ids


def test_summary_is_non_empty(analyzer, infy_snapshot):
    result = analyzer.run_red_flag_scan(infy_snapshot)
    assert isinstance(result.summary, str)
    assert len(result.summary) > 10


def test_summary_clean_if_no_flags(analyzer, infy_snapshot):
    result = analyzer.run_red_flag_scan(infy_snapshot)
    # If clean (no flags raised), summary should say no anomalies
    if result.red_count == 0 and result.yellow_count == 0:
        assert "no anomalies" in result.summary.lower() or "no" in result.summary.lower()


def test_promoter_selling_flag(analyzer, infy_snapshot):
    """Promoter selling 5pp → PROMOTER_SELLING flag."""
    if infy_snapshot.shareholding is None:
        infy_snapshot.shareholding = ShareholdingData(
            promoter_holding=55.0,
            promoter_pledging=0.0,
            fii_holding=20.0,
            dii_holding=15.0,
            public_holding=10.0,
            promoter_holding_history=[55.0, 56.0, 58.0, 60.0],
        )
    else:
        infy_snapshot.shareholding.promoter_holding_history = [55.0, 56.0, 58.0, 60.0]
    result = analyzer.run_red_flag_scan(infy_snapshot)
    flag_ids = [f["flag_id"] for f in result.flags]
    assert "PROMOTER_SELLING" in flag_ids


def test_flag_structure_has_required_keys(analyzer, infy_snapshot):
    """All flags must have the canonical Phase 2 schema keys."""
    infy_snapshot.history[0].cfo = -1000.0
    result = analyzer.run_red_flag_scan(infy_snapshot)
    for flag in result.flags:
        for key in ("flag_id", "category", "severity", "observation", "source"):
            assert key in flag, f"Flag missing key '{key}': {flag}"
