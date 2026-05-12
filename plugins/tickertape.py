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
        """
        Tickertape does not provide shareholding data.
        Use BSE filings plugin for accurate SEBI-grade shareholding patterns.
        """
        raise NotImplementedError(
            "Tickertape does not provide shareholding data. "
            "Use BSE filings plugin (bse_filings.py) for shareholding patterns."
        )

    def _normalise_financials(self, raw: dict) -> dict:
        """
        Map Tickertape-specific field names to the standard CompanySnapshot schema.
        Returns a dict with standard keys; missing fields map to None.
        """
        income = raw.get("income") or {}
        balance = raw.get("balance") or {}
        cf = raw.get("cashflow") or {}
        return {
            "revenue_ttm": income.get("netSales") or income.get("revenue"),
            "ebitda_ttm": income.get("ebitda"),
            "pat_ttm": income.get("pat") or income.get("netProfit"),
            "eps_ttm": income.get("eps"),
            "total_assets": balance.get("totalAssets"),
            "total_debt": balance.get("totalDebt") or balance.get("borrowings"),
            "equity": balance.get("equity") or balance.get("netWorth"),
            "current_assets": balance.get("currentAssets"),
            "current_liabilities": balance.get("currentLiabilities"),
            "cash": balance.get("cash") or balance.get("cashEquivalents"),
            "cfo_ttm": cf.get("cfo") or cf.get("operatingCashFlow"),
            "capex_ttm": cf.get("capex"),
        }

    async def _get_session(self):
        """Lazy-initialise a persistent aiohttp.ClientSession with standard headers."""
        import aiohttp
        if not self._session or self._session.closed:
            self._session = aiohttp.ClientSession(headers={
                "User-Agent": "Mozilla/5.0 (compatible; equilis-india/2.0; research-only)",
                "Accept": "application/json",
            })
        return self._session

    def health_check(self) -> bool:
        try:
            import requests
            r = requests.head(f"{TICKERTAPE_BASE}/", timeout=5)
            return r.status_code < 500
        except Exception:
            return False
