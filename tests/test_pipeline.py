"""
tests/test_pipeline.py
Integration tests for AnalysisPipeline with mock plugins.
Verifies stage sequencing, partial-failure handling, and render output.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import Optional

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import AnalysisPipeline, PipelineConfig, PipelineResult
from core.cache import CacheManager
from plugins._base import FetchResult

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name: str) -> dict:
    with open(os.path.join(FIXTURE_DIR, name)) as f:
        return json.load(f)


def _make_result(source_name: str, data: dict) -> FetchResult:
    return FetchResult(
        data=data,
        source_url=f"https://example.com/{source_name}",
        fetched_at=datetime.now(),
        source_name=source_name,
        is_fallback=False,
    )


class FixturePlugin:
    """Plugin that returns pre-loaded fixture data."""

    name = "screener_in"
    display_name = "Screener.in (fixture)"

    def __init__(self, fixture_name: str):
        self._data = load_fixture(fixture_name)

    async def fetch_price(self, ticker: str) -> FetchResult:
        p = self._data.get("price", {})
        return _make_result("fixture_nse", {
            "cmp": p.get("cmp"),
            "week52_high": p.get("week52_high"),
            "week52_low": p.get("week52_low"),
        })

    async def fetch_financials(self, ticker: str) -> FetchResult:
        inc = self._data.get("income", {})
        bs = self._data.get("balance_sheet", {})
        cf = self._data.get("cash_flow", {})
        # Build a minimal screener-style tables dict
        tables = {
            "income": {
                "headers": ["Metric", "FY20", "FY21", "FY22", "FY23", "FY24"],
                "rows": {
                    "Sales": [str(v) for v in inc.get("revenue_5y", [])],
                    "Net Profit": [str(v) for v in inc.get("pat_5y", [])],
                    "Operating Profit": [str(v) for v in inc.get("ebitda_5y", [])],
                    "EPS in Rs": [str(inc.get("eps_ttm", ""))],
                },
            },
            "balance_sheet": {
                "headers": [],
                "rows": {
                    "Total Assets": [str(bs.get("total_assets", ""))],
                    "Equity Capital": [str(bs.get("equity", ""))],
                    "Borrowings": [str(bs.get("total_debt", ""))],
                    "Current Assets": [str(bs.get("current_assets", ""))],
                    "Current Liabilities": [str(bs.get("current_liabilities", ""))],
                    "Trade Receivables": [str(bs.get("receivables", ""))],
                    "Inventories": [str(bs.get("inventory", ""))],
                    "Cash Equivalents": [str(bs.get("cash", ""))],
                    "Trade Payables": [str(bs.get("payables", ""))],
                },
            },
            "cash_flow": {
                "headers": [],
                "rows": {
                    "Cash from Operations": [str(v) for v in cf.get("ocf_5y", [])],
                    "Capital Expenditure": [str(cf.get("capex_ttm", ""))],
                },
            },
        }
        return _make_result("fixture_screener", {
            "tables": tables,
            "ttm": {
                "Sales": str(inc.get("revenue_ttm", "")),
                "Net Profit": str(inc.get("pat_ttm", "")),
                "Operating Profit": str(inc.get("ebitda_ttm", "")),
                "EPS in Rs": str(inc.get("eps_ttm", "")),
            },
        })

    async def fetch_shareholding(self, ticker: str) -> FetchResult:
        sh = self._data.get("shareholding", {})
        return _make_result("fixture_screener", {
            "rows": {
                "Promoters": [str(sh.get("promoter_holding", ""))],
                "FIIs": [str(sh.get("fii_holding", ""))],
                "DIIs": [str(sh.get("dii_holding", ""))],
                "Public": [str(sh.get("public_holding", ""))],
            },
        })

    async def fetch_corporate_actions(self, ticker: str) -> FetchResult:
        return _make_result("fixture_screener", {"actions": []})


@pytest.fixture
def infy_pipeline():
    plugin = FixturePlugin("infy_fy24.json")
    return AnalysisPipeline(plugins={"nse_api": plugin, "screener_in": plugin}, cache=CacheManager(disabled=True))


@pytest.fixture
def reliance_pipeline():
    plugin = FixturePlugin("reliance_fy24.json")
    return AnalysisPipeline(plugins={"nse_api": plugin, "screener_in": plugin}, cache=CacheManager(disabled=True))


# ── Pipeline success tests ────────────────────────────────────────────────────

def test_pipeline_infy_success(infy_pipeline):
    config = PipelineConfig(ticker="INFY", save_report=False, skip_validation=True)
    result: PipelineResult = asyncio.run(infy_pipeline.run(config))
    assert result.success is True
    assert result.stage == "complete"
    assert result.snapshot is not None
    assert result.ratios is not None


def test_pipeline_produces_markdown(infy_pipeline):
    config = PipelineConfig(ticker="INFY", save_report=False, skip_validation=True)
    result = asyncio.run(infy_pipeline.run(config))
    assert result.report_markdown is not None
    assert "INFY" in result.report_markdown
    assert "COMPLIANCE DISCLAIMER" in result.report_markdown


def test_pipeline_reliance_success(reliance_pipeline):
    config = PipelineConfig(ticker="RELIANCE", save_report=False, skip_validation=True)
    result = asyncio.run(reliance_pipeline.run(config))
    assert result.success is True


def test_pipeline_scenarios_generated(infy_pipeline):
    config = PipelineConfig(ticker="INFY", save_report=False, skip_validation=True)
    result = asyncio.run(infy_pipeline.run(config))
    assert result.scenarios is not None
    labels = [s.label for s in result.scenarios.scenarios]
    assert "Bear" in labels
    assert "Base" in labels
    assert "Bull" in labels


def test_pipeline_red_flags_populated(infy_pipeline):
    config = PipelineConfig(ticker="INFY", save_report=False, skip_validation=True)
    result = asyncio.run(infy_pipeline.run(config))
    assert result.red_flags is not None
    # red_flags is a list (may be empty for a healthy company like INFY)
    assert isinstance(result.red_flags, list)


# ── Partial failure tests ─────────────────────────────────────────────────────

def test_pipeline_fails_gracefully_no_plugins():
    pipeline = AnalysisPipeline(plugins={})
    config = PipelineConfig(ticker="XYZ", save_report=False, skip_validation=True)
    result = asyncio.run(pipeline.run(config))
    assert result.success is False
    assert result.error is not None


# ── Pipeline config tests ─────────────────────────────────────────────────────

def test_pipeline_config_defaults():
    config = PipelineConfig(ticker="TCS")
    assert config.exchange == "NSE"
    assert config.output_format == "markdown"
    assert config.save_report is True
    assert config.skip_validation is False
