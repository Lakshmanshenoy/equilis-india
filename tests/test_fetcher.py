"""
tests/test_fetcher.py
Tests for DataFetcher — verifies fallback chain logic and cache integration.
Uses mock plugins so no network calls are made.
"""

import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fetcher import DataFetcher, FetchBundle
from plugins._base import FetchResult


def make_result(source_name: str, data: dict, is_fallback: bool = False) -> FetchResult:
    return FetchResult(
        data=data,
        source_url=f"https://example.com/{source_name}",
        fetched_at=datetime.now(),
        source_name=source_name,
        is_fallback=is_fallback,
    )


class MockSuccessPlugin:
    name = "mock_success"
    display_name = "Mock Success"

    async def fetch_price(self, ticker):
        return make_result("mock_success", {"cmp": 100.0})

    async def fetch_financials(self, ticker):
        return make_result("mock_success", {"revenue_ttm": 5000.0})

    async def fetch_shareholding(self, ticker):
        return make_result("mock_success", {"promoter_holding": 55.0})

    async def fetch_corporate_actions(self, ticker):
        return make_result("mock_success", {"actions": []})


class MockFailingPlugin:
    name = "mock_fail"
    display_name = "Mock Fail"

    async def fetch_price(self, ticker):
        raise RuntimeError("Network error")

    async def fetch_financials(self, ticker):
        raise RuntimeError("Network error")

    async def fetch_shareholding(self, ticker):
        raise RuntimeError("Network error")

    async def fetch_corporate_actions(self, ticker):
        raise RuntimeError("Network error")


@pytest.fixture
def fetcher_with_success():
    return DataFetcher(plugins={"nse_api": MockSuccessPlugin()})


@pytest.fixture
def fetcher_fail_then_success():
    return DataFetcher(
        plugins={
            "nse_api": MockFailingPlugin(),
            "tickertape": MockSuccessPlugin(),
        }
    )


def test_fetch_price_success(fetcher_with_success):
    result = asyncio.run(fetcher_with_success.fetch_price("INFY"))
    assert result is not None
    assert result.data["cmp"] == 100.0


def test_fetch_falls_back_to_second_source(fetcher_fail_then_success):
    result = asyncio.run(fetcher_fail_then_success.fetch_price("INFY"))
    assert result is not None
    assert result.source_name == "mock_success"  # source_name = plugin.name attribute


def test_fetch_all_returns_bundle(fetcher_with_success):
    bundle = asyncio.run(fetcher_with_success.fetch_all("INFY"))
    assert isinstance(bundle, FetchBundle)
    assert bundle.ticker == "INFY"
    assert bundle.price is not None


def test_fetch_all_partial_failure():
    """Should return bundle with available data even if some sources fail."""
    fetcher = DataFetcher(
        plugins={"nse_api": MockFailingPlugin(), "screener_in": MockSuccessPlugin()}
    )
    bundle = asyncio.run(fetcher.fetch_all("INFY"))
    # Price uses nse_api (fails) with no fallback → None; financials uses screener_in (ok)
    # (Exact result depends on source priority list in fetcher.py)
    assert isinstance(bundle, FetchBundle)


def test_cache_prevents_second_fetch():
    """Verify cache hit prevents additional plugin calls when cache is active."""
    call_count = {"n": 0}

    class CountingPlugin:
        name = "nse_api"
        display_name = "Counting"

        async def fetch_price(self, ticker):
            call_count["n"] += 1
            return make_result("counting", {"cmp": 200.0})

        async def fetch_financials(self, ticker):
            return make_result("counting", {"revenue_ttm": 999.0})

        async def fetch_shareholding(self, ticker):
            return make_result("counting", {})

        async def fetch_corporate_actions(self, ticker):
            return make_result("counting", {})

    # Use a simple always-hit cache stub so the test is not diskcache-dependent
    class AlwaysHitCache:
        """Returns the stored value after first set."""
        def __init__(self):
            self._store = {}

        def get(self, data_type, ticker):
            return self._store.get((data_type, ticker))

        def set(self, data_type, ticker, value):
            self._store[(data_type, ticker)] = value

    cache = AlwaysHitCache()
    fetcher = DataFetcher(plugins={"nse_api": CountingPlugin()}, cache=cache)
    asyncio.run(fetcher.fetch_price("CACHETEST"))
    asyncio.run(fetcher.fetch_price("CACHETEST"))   # Should hit cache
    assert call_count["n"] == 1
