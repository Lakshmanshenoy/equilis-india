"""
core/fetcher.py
Async DataFetcher — orchestrates multi-source data collection with fallback chains.

Data source priority:
  Price:         nse_api → tickertape
  Financials:    screener_in → tickertape → bse_filings
  Shareholding:  bse_filings → screener_in
  Corp actions:  nse_api → bse_filings
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.cache import CacheManager
from plugins._base import BasePlugin, FetchResult

logger = logging.getLogger(__name__)

# Source priority chains — first available and non-stale wins
PRICE_SOURCES = ["nse_api", "tickertape"]
FINANCIAL_SOURCES = ["screener_in", "tickertape", "bse_filings"]
SHAREHOLDING_SOURCES = ["bse_filings", "screener_in"]
CORPORATE_ACTION_SOURCES = ["nse_api", "bse_filings"]


@dataclass
class FetchBundle:
    """All raw fetched data for a single ticker before normalisation."""
    ticker: str
    price: Optional[FetchResult] = None
    financials: Optional[FetchResult] = None
    shareholding: Optional[FetchResult] = None
    corporate_actions: Optional[FetchResult] = None
    errors: dict = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = {}


class DataFetcher:
    """
    Async fetcher that delegates to registered plugins with fallback chains
    and transparent disk caching.
    """

    def __init__(
        self,
        plugins: dict[str, BasePlugin],
        cache: Optional[CacheManager] = None,
    ):
        self._plugins: dict[str, BasePlugin] = plugins
        self._cache: CacheManager = cache or CacheManager()

    def _plugin(self, name: str) -> Optional[BasePlugin]:
        return self._plugins.get(name)

    def _is_fresh(self, data_type: str, ticker: str) -> bool:
        return self._cache.get(data_type, ticker) is not None

    async def _try_sources(
        self,
        data_type: str,
        ticker: str,
        source_names: list[str],
        method: str,
    ) -> Optional[FetchResult]:
        """
        Attempt each source in order. Return first successful result.
        Cache hit (if fresh) short-circuits network calls.
        """
        cached = self._cache.get(data_type, ticker)
        if cached:
            logger.debug(f"[fetcher] Cache hit: {data_type}/{ticker}")
            return cached

        for name in source_names:
            plugin = self._plugin(name)
            if not plugin:
                continue
            try:
                result: FetchResult = await getattr(plugin, method)(ticker)
                self._cache.set(data_type, ticker, result)
                return result
            except NotImplementedError:
                logger.debug(f"[fetcher] {name} does not support {method}")
            except Exception as e:
                logger.warning(f"[fetcher] {name}.{method}({ticker}) failed: {e}")

        logger.error(
            f"[fetcher] All sources failed for {data_type}/{ticker}: {source_names}"
        )
        return None

    async def fetch_price(self, ticker: str) -> Optional[FetchResult]:
        return await self._try_sources(
            "price", ticker, PRICE_SOURCES, "fetch_price"
        )

    async def fetch_financials(self, ticker: str) -> Optional[FetchResult]:
        return await self._try_sources(
            "financials", ticker, FINANCIAL_SOURCES, "fetch_financials"
        )

    async def fetch_shareholding(self, ticker: str) -> Optional[FetchResult]:
        return await self._try_sources(
            "shareholding", ticker, SHAREHOLDING_SOURCES, "fetch_shareholding"
        )

    async def fetch_corporate_actions(self, ticker: str) -> Optional[FetchResult]:
        return await self._try_sources(
            "corporate_actions", ticker, CORPORATE_ACTION_SOURCES,
            "fetch_corporate_actions"
        )

    async def fetch_all(self, ticker: str) -> FetchBundle:
        """
        Concurrently fetch price, financials, shareholding, and corporate actions.
        Returns a FetchBundle regardless of partial failures.
        """
        tasks = [
            self.fetch_price(ticker),
            self.fetch_financials(ticker),
            self.fetch_shareholding(ticker),
            self.fetch_corporate_actions(ticker),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        price, financials, shareholding, corp_actions = results

        bundle = FetchBundle(ticker=ticker)
        errors: dict = {}

        def _assign(attr, result, label):
            if isinstance(result, Exception):
                errors[label] = str(result)
                return None
            return result

        bundle.price = _assign("price", price, "price")
        bundle.financials = _assign("financials", financials, "financials")
        bundle.shareholding = _assign("shareholding", shareholding, "shareholding")
        bundle.corporate_actions = _assign(
            "corporate_actions", corp_actions, "corporate_actions"
        )
        bundle.errors = errors

        if errors:
            logger.warning(f"[fetcher] Partial fetch for {ticker}: {list(errors.keys())} failed")

        return bundle
