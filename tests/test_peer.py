"""
tests/test_peer.py
Tests for PeerComparisonPipeline and PeerComparisonResult.
Uses mock snapshots — no live network calls.
"""

import sys
import os
import asyncio
import statistics

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.peer import PeerComparisonPipeline, PEER_COMPARISON_METRICS
from core.models.peer import PeerComparisonResult
from core.models.company import CompanySnapshot, IncomeData, MarketData
from core.models.ratios import (
    RatioSet,
    ProfitabilityRatios,
    LeverageRatios,
    ValuationRatios,
    EfficiencyRatios,
)
from datetime import datetime


# ── Mock helpers ──────────────────────────────────────────────────────────────

class _MockRatioSet:
    """Minimal ratios container that mirrors RatioSet attribute structure."""

    def __init__(self, roe=None, roce=None, de=None, pe=None):
        self.profitability = type("P", (), {"roe": roe, "roce": roce, "pat_margin": None, "ebitda_margin": None})()
        self.leverage      = type("L", (), {"debt_to_equity": de, "current_ratio": None})()
        self.valuation     = type("V", (), {"pe_ttm": pe, "ev_ebitda": None})()
        self.efficiency    = None


def build_mock_snapshot(ticker: str, revenue: float = 0, pat: float = 0,
                        market_cap: float = 0, roe: float = None) -> CompanySnapshot:
    snap = CompanySnapshot(
        ticker=ticker,
        exchange="NSE",
        company_name=ticker,
        sector="Information Technology",
        snapshot_date=datetime.now(),
    )
    snap.income = IncomeData(
        revenue_ttm=revenue, pat_ttm=pat,
        ebitda_ttm=None, ebit=None, gross_profit=None,
        interest_expense=None, depreciation=None,
        eps_ttm=None, eps_growth_5yr=None,
        dividend_per_share=None, revenue_5y=[], pat_5y=[], ebitda_5y=[],
    )
    snap.market = MarketData(market_cap=market_cap, shares_outstanding=None, enterprise_value=None)
    snap.ratios  = _MockRatioSet(roe=roe)
    snap.sources = []
    return snap


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_peer_comparison_result_structure():
    """PeerComparisonResult should have all required fields."""
    result = PeerComparisonResult(
        tickers=["INFY", "TCS"],
        snapshots={"INFY": object(), "TCS": object()},
        comparison_table={"ROE": {"INFY": 0.31, "TCS": 0.44}},
        sector_medians={"ROE": 0.375},
        errors={},
        sources={"INFY": "screener.in", "TCS": "screener.in"},
    )
    assert result.tickers == ["INFY", "TCS"]
    assert "ROE" in result.comparison_table
    assert result.sector_medians["ROE"] == 0.375


def test_sector_median_computed_correctly():
    """Median of [0.165, 0.311, 0.445] should equal 0.311."""
    snapshots = {
        "A": build_mock_snapshot("A", roe=0.165),
        "B": build_mock_snapshot("B", roe=0.311),
        "C": build_mock_snapshot("C", roe=0.445),
    }

    class _MockPipeline(PeerComparisonPipeline):
        def __init__(self):
            pass   # skip real init

    pipeline = _MockPipeline()
    medians = pipeline._compute_sector_medians(snapshots, ["ROE"])
    assert medians.get("ROE") == 0.311


def test_failed_ticker_goes_to_errors_not_snapshots():
    """A ticker that fails fetch should appear in errors, not snapshots."""

    async def _run_with_one_failure():
        class _FailFetcher:
            async def fetch_all(self, ticker):
                raise ConnectionError(f"No data for {ticker}")

        class _FakeAnalyzer:
            def compute_all(self, snapshot):
                return _MockRatioSet()

        class _FakeValidator:
            pass

        pipeline = PeerComparisonPipeline(_FailFetcher(), _FakeValidator(), _FakeAnalyzer())

        tickers = ["INFY", "FAIL_TICKER"]

        # Override _fetch_and_analyze so only FAIL_TICKER raises
        original = pipeline._fetch_and_analyze

        async def _patched(ticker):
            if ticker == "FAIL_TICKER":
                raise RuntimeError("Simulated failure")
            return build_mock_snapshot(ticker)

        pipeline._fetch_and_analyze = _patched
        return await pipeline.run(tickers)

    result = asyncio.run(_run_with_one_failure())
    assert "FAIL_TICKER" in result.errors
    assert "FAIL_TICKER" not in result.snapshots
    assert "INFY" in result.snapshots


def test_resolve_path_traverses_correctly():
    """_resolve_path should traverse nested attributes."""

    class _MockPipeline(PeerComparisonPipeline):
        def __init__(self):
            pass

    snap     = build_mock_snapshot("TEST", roe=0.311)
    pipeline = _MockPipeline()
    roe_val  = pipeline._resolve_path(snap, "ratios.profitability.roe")
    assert roe_val == 0.311


def test_resolve_path_raises_on_missing_attr():
    """_resolve_path should raise AttributeError for non-existent paths."""

    class _MockPipeline(PeerComparisonPipeline):
        def __init__(self):
            pass

    snap     = build_mock_snapshot("TEST")
    pipeline = _MockPipeline()
    with pytest.raises(AttributeError):
        pipeline._resolve_path(snap, "ratios.nonexistent.field")


def test_build_comparison_table_structure():
    """Comparison table keys should be metric names; values should have per-ticker entries."""

    class _MockPipeline(PeerComparisonPipeline):
        def __init__(self):
            pass

    snapshots = {
        "INFY": build_mock_snapshot("INFY", revenue=153670, roe=0.311),
        "TCS":  build_mock_snapshot("TCS",  revenue=240000, roe=0.445),
    }
    pipeline = _MockPipeline()
    table    = pipeline._build_comparison_table(snapshots, ["Revenue TTM (₹Cr)", "ROE"])

    assert "Revenue TTM (₹Cr)" in table
    assert "INFY" in table["Revenue TTM (₹Cr)"]
    assert table["Revenue TTM (₹Cr)"]["INFY"] == 153670
    assert "ROE" in table
    assert abs(table["ROE"]["TCS"] - 0.445) < 0.001


def test_peer_comparison_metrics_registry():
    """PEER_COMPARISON_METRICS should be a list of 3-tuples."""
    for entry in PEER_COMPARISON_METRICS:
        assert len(entry) == 3, f"Expected 3-tuple, got {len(entry)}-tuple: {entry}"
        name, path, fmt = entry
        assert isinstance(name, str)
        assert isinstance(path, str)
        assert "." in path or path.isidentifier()
