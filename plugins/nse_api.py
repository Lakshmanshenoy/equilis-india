"""
plugins/nse_api.py
NSE India adapter — live price, corporate actions, historical OHLCV.

Key NSE API quirks:
- NSE requires a valid browser session cookie. First hit the homepage to get
  cookies, then call the API endpoints using the same session.
- All API calls must include Referer: https://www.nseindia.com
- Rate limiting is aggressive — add delays between calls in bulk scenarios.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from plugins._base import BasePlugin, FetchResult

logger = logging.getLogger(__name__)

NSE_BASE = "https://www.nseindia.com"
NSE_QUOTE_URL = f"{NSE_BASE}/api/quote-equity"
NSE_HISTORY_URL = f"{NSE_BASE}/api/historical/cm/equity"
NSE_CORP_ACTIONS_URL = f"{NSE_BASE}/api/corporates-corporate-actions"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": NSE_BASE,
}


class NseApiPlugin(BasePlugin):
    name = "nse_api"
    display_name = "NSE India"
    supports_live_price = True
    base_url = NSE_BASE

    def __init__(self, session=None):
        self._session = session
        self._cookies: dict = {}
        self._session_refreshed_at: Optional[datetime] = None

    async def _ensure_session(self) -> None:
        """
        Hit NSE homepage to obtain session cookies required for API calls.
        Refresh if session is older than 10 minutes.
        """
        if self._session_refreshed_at:
            age = (datetime.now() - self._session_refreshed_at).total_seconds()
            if age < 600:  # 10 minutes
                return
        try:
            import aiohttp
            if self._session:
                async with self._session.get(NSE_BASE, headers=REQUEST_HEADERS) as resp:
                    self._cookies = {k: v.value for k, v in resp.cookies.items()}
            else:
                async with aiohttp.ClientSession() as s:
                    async with s.get(NSE_BASE, headers=REQUEST_HEADERS) as resp:
                        self._cookies = {k: v.value for k, v in resp.cookies.items()}
            self._session_refreshed_at = datetime.now()
            logger.debug("[nse_api] Session cookies refreshed")
        except Exception as e:
            logger.warning(f"[nse_api] Could not refresh session: {e}")

    async def _get_json(self, url: str, params: dict = None) -> dict:
        """Authenticated JSON GET with session cookies."""
        await self._ensure_session()
        import aiohttp
        headers = {**REQUEST_HEADERS}
        if self._session:
            async with self._session.get(
                url, params=params, headers=headers, cookies=self._cookies
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
        else:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    url, params=params, headers=headers, cookies=self._cookies
                ) as resp:
                    resp.raise_for_status()
                    return await resp.json()

    async def fetch_price(self, ticker: str) -> FetchResult:
        """
        Fetch live CMP, 52W high/low, market cap from NSE quote API.
        Returns structured dict suitable for CompanySnapshot.price.
        """
        url = NSE_QUOTE_URL
        params = {"symbol": ticker.upper()}
        try:
            data = await self._get_json(url, params=params)
            price_data = self._extract_price(data)
            logger.info(f"[nse_api] Live price fetched for {ticker}: ₹{price_data.get('cmp')}")
            return self._make_result(price_data, f"{url}?symbol={ticker.upper()}")
        except Exception as e:
            logger.warning(f"[nse_api] Failed to fetch price for {ticker}: {e}")
            raise

    async def fetch_financials(self, ticker: str) -> FetchResult:
        """
        NSE does not provide structured financials. Raises NotImplementedError.
        Use screener_in or bse_filings for financial statements.
        """
        raise NotImplementedError(
            "NSE API does not provide financial statements. "
            "Use screener_in or bse_filings plugins instead."
        )

    async def fetch_shareholding(self, ticker: str) -> FetchResult:
        """NSE shareholding — delegates to BSE for accuracy."""
        raise NotImplementedError(
            "Use bse_filings for shareholding pattern (more accurate source)."
        )

    async def fetch_corporate_actions(self, ticker: str) -> FetchResult:
        """Fetch dividends, splits, bonuses from NSE corporate actions API."""
        url = NSE_CORP_ACTIONS_URL
        params = {"symbol": ticker.upper(), "subject": ""}
        try:
            data = await self._get_json(url, params=params)
            return self._make_result({"actions": data}, url)
        except Exception as e:
            logger.warning(f"[nse_api] Failed to fetch corporate actions for {ticker}: {e}")
            raise

    def health_check(self) -> bool:
        try:
            import requests
            r = requests.head(NSE_BASE, timeout=5)
            return r.status_code < 500
        except Exception:
            return False

    def _extract_price(self, raw: dict) -> dict:
        """Extract standardised price fields from NSE quote response."""
        pd = raw.get("priceInfo", {})
        meta = raw.get("metadata", {})
        info = raw.get("info", {})
        week_hl = pd.get("weekHighLow", {})
        return {
            "cmp": pd.get("lastPrice"),
            "open": pd.get("open"),
            "prev_close": pd.get("previousClose"),
            "day_high": pd.get("intraDayHighLow", {}).get("max"),
            "day_low": pd.get("intraDayHighLow", {}).get("min"),
            "week52_high": week_hl.get("max"),
            "week52_low": week_hl.get("min"),
            "market_cap": meta.get("pdSectionData", {}).get("totalTradedValue"),
            "pe_ttm": info.get("pdSectionData", {}).get("pdSymbolPe"),
            "volume": pd.get("totalTradedVolume"),
            "symbol": raw.get("info", {}).get("symbol"),
        }
