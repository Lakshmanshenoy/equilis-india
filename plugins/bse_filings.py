"""
plugins/bse_filings.py
BSE India adapter — XBRL filings, shareholding patterns, annual reports.

Primary authority for:
- Shareholding patterns (per SEBI mandate, filed quarterly)
- XBRL structured financial data from annual reports
- Rights, bonus, split announcements
"""

import logging
from datetime import datetime
from typing import Optional

from plugins._base import BasePlugin, FetchResult

logger = logging.getLogger(__name__)

BSE_BASE = "https://www.bseindia.com"
BSE_API_BASE = "https://api.bseindia.com/BseIndiaAPI/api"

BSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": BSE_BASE,
    "Accept": "application/json, text/plain, */*",
}


class BseFilingsPlugin(BasePlugin):
    name = "bse_filings"
    display_name = "BSE India (Filings)"
    supports_live_price = False
    base_url = BSE_BASE

    def __init__(self, session=None, bse_code_map: Optional[dict] = None):
        self._session = session
        # Optional dict mapping NSE ticker → BSE 6-digit code
        self._bse_code_map: dict = bse_code_map or {}

    def _bse_code(self, ticker: str) -> Optional[str]:
        return self._bse_code_map.get(ticker.upper())

    async def _get_json(self, url: str, params: dict = None) -> dict:
        import aiohttp
        if self._session:
            async with self._session.get(
                url, params=params, headers=BSE_HEADERS
            ) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        else:
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    url, params=params, headers=BSE_HEADERS
                ) as resp:
                    resp.raise_for_status()
                    return await resp.json(content_type=None)

    async def fetch_price(self, ticker: str) -> FetchResult:
        """BSE does not provide a clean price API — raises NotImplementedError."""
        raise NotImplementedError("Use nse_api or tickertape for live price.")

    async def fetch_financials(self, ticker: str) -> FetchResult:
        """
        Fetch structured financial data from BSE XBRL filing API.
        Requires BSE company code (6-digit). Uses code_map if provided.
        """
        code = self._bse_code(ticker)
        if not code:
            raise ValueError(
                f"BSE code not found for {ticker}. "
                "Provide bse_code_map at plugin init or use screener_in."
            )
        url = f"{BSE_API_BASE}/FinancialResults/w"
        params = {"scripcode": code, "type": "C"}  # C = Consolidated
        try:
            data = await self._get_json(url, params=params)
            return self._make_result(data, f"{url}?scripcode={code}")
        except Exception as e:
            logger.warning(f"[bse_filings] Failed to fetch financials for {ticker}: {e}")
            raise

    async def fetch_shareholding(self, ticker: str) -> FetchResult:
        """
        Fetch latest shareholding pattern from BSE.
        BSE is the authoritative source per SEBI mandate.
        """
        code = self._bse_code(ticker)
        if not code:
            # Try to resolve via BSE search
            raise ValueError(
                f"BSE code not found for {ticker}. Provide bse_code_map at init."
            )
        url = f"{BSE_API_BASE}/Stockholding/w"
        params = {"scripcode": code}
        try:
            data = await self._get_json(url, params=params)
            return self._make_result(data, f"{url}?scripcode={code}")
        except Exception as e:
            logger.warning(f"[bse_filings] Failed to fetch shareholding for {ticker}: {e}")
            raise

    async def fetch_corporate_actions(self, ticker: str) -> FetchResult:
        """Fetch dividends, bonus, splits, rights from BSE corporate actions."""
        code = self._bse_code(ticker)
        if not code:
            raise ValueError(f"BSE code not found for {ticker}.")
        url = f"{BSE_API_BASE}/CorporateActions/w"
        params = {"scripcode": code, "flag": "D"}
        try:
            data = await self._get_json(url, params=params)
            return self._make_result(data, f"{url}?scripcode={code}")
        except Exception as e:
            logger.warning(f"[bse_filings] Failed to fetch corporate actions for {ticker}: {e}")
            raise

    def health_check(self) -> bool:
        try:
            import requests
            r = requests.head(BSE_BASE, timeout=5)
            return r.status_code < 500
        except Exception:
            return False
