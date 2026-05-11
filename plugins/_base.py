"""
plugins/_base.py
Abstract base interface for all data source plugins.
The core pipeline only calls these methods — it is agnostic to the underlying source.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FetchResult:
    data: dict
    source_url: str
    fetched_at: datetime
    source_name: str
    is_fallback: bool = False


class DataUnavailableError(Exception):
    """Raised when all sources in the fallback chain fail."""
    pass


class BasePlugin(ABC):
    name: str = ""               # e.g., "screener_in"
    display_name: str = ""       # e.g., "Screener.in"
    supports_live_price: bool = False
    base_url: str = ""

    @abstractmethod
    async def fetch_price(self, ticker: str) -> FetchResult:
        """Return current market price and 52W range."""
        pass

    @abstractmethod
    async def fetch_financials(self, ticker: str) -> FetchResult:
        """Return P&L, Balance Sheet, Cash Flow for last 5 fiscal years."""
        pass

    @abstractmethod
    async def fetch_shareholding(self, ticker: str) -> FetchResult:
        """Return shareholding pattern for last 4 quarters."""
        pass

    async def fetch_concall_transcript(self, ticker: str) -> FetchResult:
        """Optional. Return latest concall transcript or summary."""
        raise NotImplementedError(f"{self.name} does not support concall transcripts")

    async def fetch_corporate_actions(self, ticker: str) -> FetchResult:
        """Optional. Return dividends, splits, bonuses, rights."""
        raise NotImplementedError(f"{self.name} does not support corporate actions")

    async def fetch_peers(self, ticker: str) -> FetchResult:
        """Optional. Return peer company list for the ticker."""
        raise NotImplementedError(f"{self.name} does not support peer lists")

    def health_check(self) -> bool:
        """Verify source is reachable. Called at startup. Override in each plugin."""
        return True

    def _make_result(self, data: dict, url: str, is_fallback: bool = False) -> FetchResult:
        return FetchResult(
            data=data,
            source_url=url,
            fetched_at=datetime.now(),
            source_name=self.display_name,
            is_fallback=is_fallback,
        )
