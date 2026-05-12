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


def _safe_float(value) -> Optional[float]:
    """Convert value to float safely, returning None on failure."""
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None


class BseFilingsPlugin(BasePlugin):
    name = "bse_filings"
    display_name = "BSE India (Filings)"
    supports_live_price = False
    base_url = BSE_BASE

    def __init__(self, session=None, bse_code_map: Optional[dict] = None):
        self._session = session
        # Optional dict mapping NSE ticker → BSE 6-digit code
        self._bse_code_map: dict = bse_code_map or {}
        # In-memory cache for dynamically resolved BSE codes
        self._bse_code_cache: dict = {}

    def _bse_code(self, ticker: str) -> Optional[str]:
        ticker_upper = ticker.upper()
        return self._bse_code_cache.get(ticker_upper) or self._bse_code_map.get(ticker_upper)

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
            normalised = self._normalise_shareholding(data, ticker)
            return self._make_result(normalised, f"{url}?scripcode={code}")
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

    async def _get_scrip_code(self, ticker: str, session=None) -> Optional[str]:
        """
        Resolve BSE scrip code from NSE ticker via BSE security search API.
        Caches result in _bse_code_cache to avoid repeated lookups.
        """
        ticker_upper = ticker.upper()
        # Check in-memory cache first
        if ticker_upper in self._bse_code_cache:
            return self._bse_code_cache[ticker_upper]
        # Fall back to static map
        if ticker_upper in self._bse_code_map:
            code = self._bse_code_map[ticker_upper]
            self._bse_code_cache[ticker_upper] = code
            return code
        # Dynamic lookup via BSE API
        url = f"{BSE_API_BASE}/fetchsecurityalldata/w"
        params = {"Type": "EQ", "text": ticker_upper}
        try:
            data = await self._get_json(url, params=params)
            records = data if isinstance(data, list) else data.get("Table", data.get("data", []))
            for rec in records:
                if str(rec.get("scrip_code") or rec.get("SCRIP_CODE") or "").strip():
                    code = str(rec.get("scrip_code") or rec.get("SCRIP_CODE")).strip()
                    self._bse_code_cache[ticker_upper] = code
                    return code
        except Exception as e:
            logger.warning(f"[bse_filings] Failed to resolve scrip code for {ticker}: {e}")
        return None

    async def fetch_announcements(self, ticker: str, days: int = 90) -> FetchResult:
        """
        Fetch recent BSE corporate announcements for a ticker.
        Returns up to 90 days of announcements by default.
        """
        code = self._bse_code(ticker) or await self._get_scrip_code(ticker)
        if not code:
            raise ValueError(f"BSE code not found for {ticker}.")
        url = f"{BSE_API_BASE}/AnnSubCategoryGetData/w"
        params = {"strCat": "-1", "strPrevDate": "", "strScrip": code,
                  "strSearch": "P", "strToDate": "", "strType": "C"}
        try:
            data = await self._get_json(url, params=params)
            announcements = data if isinstance(data, list) else data.get("Table", data.get("data", []))
            return self._make_result(
                {"announcements": announcements[:100]},
                f"{url}?strScrip={code}",
            )
        except Exception as e:
            logger.warning(f"[bse_filings] Failed to fetch announcements for {ticker}: {e}")
            raise

    def _normalise_shareholding(self, raw: dict, ticker: str) -> dict:
        """
        Normalise raw BSE shareholding API response to standard field names.

        Computes:
        - promoter_holding_change_4q: change over last 4 quarters (percentage points)
        - promoter_pledge_change_4q: change in pledging over last 4 quarters
        - Returns last 8 quarters of history, newest first
        """
        records = []
        if isinstance(raw, list):
            records = raw
        elif isinstance(raw, dict):
            records = raw.get("Table", raw.get("data", []))

        # Sort by quarter descending (newest first)
        def _quarter_key(r):
            return r.get("QUARTER", r.get("quarter", ""))

        records = sorted(records, key=_quarter_key, reverse=True)[:8]

        promoter_history = []
        pledge_history   = []
        for rec in records:
            ph = rec.get("PROMOTER_HOLDING") or rec.get("promoter_holding")
            pp = rec.get("PROMOTER_PLEDGE")  or rec.get("promoter_pledge", 0)
            try:
                promoter_history.append(float(ph) if ph is not None else None)
                pledge_history.append(float(pp) if pp is not None else 0.0)
            except (TypeError, ValueError):
                promoter_history.append(None)
                pledge_history.append(None)

        # Change over 4 quarters (index 0 = newest, index 4 = 4 quarters ago)
        def _change_4q(hist):
            if len(hist) >= 5 and hist[0] is not None and hist[4] is not None:
                return round(hist[0] - hist[4], 2)
            return None

        latest = records[0] if records else {}
        return {
            "promoter_holding":          promoter_history[0] if promoter_history else None,
            "promoter_pledging":         pledge_history[0] if pledge_history else None,
            "promoter_holding_change_4q": _change_4q(promoter_history),
            "promoter_pledge_change_4q":  _change_4q(pledge_history),
            "promoter_holding_history":  promoter_history,
            "fii_holding":               _safe_float(latest.get("FII_HOLDING") or latest.get("fii_holding")),
            "dii_holding":               _safe_float(latest.get("DII_HOLDING") or latest.get("dii_holding")),
            "public_holding":            _safe_float(latest.get("PUBLIC_HOLDING") or latest.get("public_holding")),
            "quarters":                  [r.get("QUARTER", r.get("quarter", "")) for r in records],
            "source": "bse_filings",
        }

    def health_check(self) -> bool:
        """Ping the BSE scrip header endpoint for Infosys (500209)."""
        try:
            import requests
            url = f"{BSE_API_BASE}/getScripHeaderData/w"
            r = requests.get(url, params={"Scrip_Cd": "500209"}, headers=BSE_HEADERS, timeout=8)
            return r.status_code < 500
        except Exception:
            return False
