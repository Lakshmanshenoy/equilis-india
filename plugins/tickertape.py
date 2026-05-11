"""
plugins/tickertape.py
Tickertape adapter — fallback for price, financials, and shareholding.
Used when NSE API and Screener.in are unavailable or return incomplete data.
"""

import logging
from datetime import datetime

from plugins._base import BasePlugin, FetchResult

logger = logging.getLogger(__name__)

TICKERTAPE_BASE = "https://api.tickertape.in"


class TickertapePlugin(BasePlugin):
    name = "tickertape"
    display_name = "Tickertape"
    supports_live_price = True
    base_url = TICKERTAPE_BASE

    def __init__(self, session=None):
        self._session = session

    async def _get_json(self, url: str, params: dict = None) -> dict:
        import aiohttp
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (compatible; equilis-india/2.0; research-only)"
            ),
            "Accept": "application/json",
        }
        if self._session:
            async with self._session.get(url, params=params, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()
        else:
            async with aiohttp.ClientSession() as s:
                async with s.get(url, params=params, headers=headers) as resp:
                    resp.raise_for_status()
                    return await resp.json()

    async def fetch_price(self, ticker: str) -> FetchResult:
        """Fetch live CMP from Tickertape (fallback)."""
        url = f"{TICKERTAPE_BASE}/stocks/{ticker.upper()}/get-quote"
        try:
            data = await self._get_json(url)
            price = data.get("data", {}).get("price", {})
            result = {
                "cmp": price.get("lastPrice"),
                "week52_high": price.get("high52"),
                "week52_low": price.get("low52"),
                "source": "tickertape",
            }
            logger.info(f"[tickertape] Live price fetched for {ticker}")
            return self._make_result(result, url, is_fallback=True)
        except Exception as e:
            logger.warning(f"[tickertape] Failed to fetch price for {ticker}: {e}")
            raise

    async def fetch_financials(self, ticker: str) -> FetchResult:
        """Fetch financial statements from Tickertape (fallback)."""
        url = f"{TICKERTAPE_BASE}/stocks/{ticker.upper()}/financials"
        try:
            data = await self._get_json(url)
            return self._make_result(data.get("data", {}), url, is_fallback=True)
        except Exception as e:
            logger.warning(f"[tickertape] Failed to fetch financials for {ticker}: {e}")
            raise

    async def fetch_shareholding(self, ticker: str) -> FetchResult:
        """Fetch shareholding from Tickertape (fallback)."""
        url = f"{TICKERTAPE_BASE}/stocks/{ticker.upper()}/shareholding"
        try:
            data = await self._get_json(url)
            return self._make_result(data.get("data", {}), url, is_fallback=True)
        except Exception as e:
            logger.warning(f"[tickertape] Failed to fetch shareholding for {ticker}: {e}")
            raise

    def health_check(self) -> bool:
        try:
            import requests
            r = requests.head(f"{TICKERTAPE_BASE}/", timeout=5)
            return r.status_code < 500
        except Exception:
            return False
