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
from datetime import datetime, timezone
from typing import Optional

from core.cache import CacheManager
from plugins._base import BasePlugin, FetchResult

logger = logging.getLogger(__name__)

# Source priority chains — first available and non-stale wins
PRICE_SOURCES = ["nse_api", "tickertape"]
FINANCIAL_SOURCES = ["screener_in", "tickertape", "bse_filings"]
SHAREHOLDING_SOURCES = ["bse_filings", "screener_in"]
CORPORATE_ACTION_SOURCES = ["nse_api", "bse_filings"]

# ── Phase 3: concurrency, retry, and TTL configuration ────────────────────────
SOURCE_CONCURRENCY: dict[str, int] = {
    "screener_in": 3,
    "nse_api": 5,
    "bse_filings": 2,
    "tickertape": 3,
}

MAX_RETRIES: int = 3
RETRY_BACKOFF: list[int] = [1, 3, 7]  # seconds to wait before each retry attempt

TTL_CONFIG: dict[str, int] = {
    "price":           15,     # minutes
    "financials":      360,
    "shareholding":    1440,
    "corp_actions":    1440,
    "concalls":        10080,
    "peers":           1440,
}


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
        self._semaphores: dict[str, asyncio.Semaphore] = {
            src: asyncio.Semaphore(c) for src, c in SOURCE_CONCURRENCY.items()
        }

    def _plugin(self, name: str) -> Optional[BasePlugin]:
        return self._plugins.get(name)

    def _is_fresh(self, data_type: str, ticker: str) -> bool:
        return self._cache.get(data_type, ticker) is not None

    def _result_is_fresh(self, result: FetchResult, data_type: str) -> bool:
        """Return True if a cached FetchResult is within TTL for the data type."""
        ttl_minutes = TTL_CONFIG.get(data_type, 60)
        if not result or not hasattr(result, "fetched_at"):
            return False
        fetched_at = result.fetched_at
        now = datetime.now(timezone.utc) if getattr(fetched_at, "tzinfo", None) else datetime.now()
        delta = (now - fetched_at).total_seconds() / 60
        return delta < ttl_minutes

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
            sem = self._semaphores.get(name, asyncio.Semaphore(5))
            try:
                async with sem:
                    result: FetchResult = await asyncio.wait_for(
                        getattr(plugin, method)(ticker), timeout=30
                    )
                if result and self._result_is_fresh(result, data_type):
                    self._cache.set(data_type, ticker, result)
                    return result
                elif result:
                    self._cache.set(data_type, ticker, result)
                    return result
            except NotImplementedError:
                logger.debug(f"[fetcher] {name} does not support {method}")
            except asyncio.TimeoutError:
                logger.warning(f"[fetcher] {name}.{method}({ticker}) timed out after 30s")
            except Exception as e:
                logger.warning(f"[fetcher] {name}.{method}({ticker}) failed: {e}")

        logger.error(
            f"[fetcher] All sources failed for {data_type}/{ticker}: {source_names}"
        )
        return None

    async def fetch_price(self, ticker: str) -> Optional[FetchResult]:
        return await self._fetch_with_retry(
            "price", ticker, PRICE_SOURCES, "fetch_price"
        )

    async def fetch_financials(self, ticker: str) -> Optional[FetchResult]:
        return await self._fetch_with_retry(
            "financials", ticker, FINANCIAL_SOURCES, "fetch_financials"
        )

    async def fetch_shareholding(self, ticker: str) -> Optional[FetchResult]:
        return await self._fetch_with_retry(
            "shareholding", ticker, SHAREHOLDING_SOURCES, "fetch_shareholding"
        )

    async def fetch_corporate_actions(self, ticker: str) -> Optional[FetchResult]:
        return await self._fetch_with_retry(
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

    async def _fetch_with_retry(
        self,
        data_type: str,
        ticker: str,
        source_names: list[str],
        method: str,
    ) -> Optional[FetchResult]:
        """
        Fetch data with up to MAX_RETRIES attempts.
        Uses RETRY_BACKOFF delays between attempts on failure.
        """
        last_exc: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                result = await self._try_sources(data_type, ticker, source_names, method)
                if result is not None:
                    return result
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    f"[fetcher] {data_type}/{ticker} attempt {attempt+1} failed: {exc}"
                )
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_BACKOFF[attempt])
        if last_exc:
            logger.error(
                f"[fetcher] {data_type}/{ticker} exhausted {MAX_RETRIES} retries: {last_exc}"
            )
        return None

    async def fetch_all_concurrent(self, tickers: list[str]) -> dict[str, "FetchBundle"]:
        """
        Fetch all data for a list of tickers concurrently.
        Returns a dict mapping ticker -> FetchBundle.
        """
        async def _fetch_one(ticker: str) -> tuple[str, "FetchBundle"]:
            try:
                bundle = await self.fetch_all(ticker)
                return ticker, bundle
            except Exception as exc:
                return ticker, self._error_bundle(ticker, exc)

        results = await asyncio.gather(*[_fetch_one(t) for t in tickers])
        return dict(results)

    def _error_bundle(self, ticker: str, exc: Exception) -> "FetchBundle":
        """Return a FetchBundle that records a top-level fetch error."""
        return FetchBundle(
            ticker=ticker,
            errors={"fetch_all": str(exc)},
        )
