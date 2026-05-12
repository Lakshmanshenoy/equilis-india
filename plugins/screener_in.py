"""
plugins/screener_in.py
Screener.in adapter — primary source for financial statements and peer lists.

Known quirks:
- CMP on Screener.in is a stale cache — NEVER use for current price.
- Always prefer consolidated P&L over standalone.
- Rate limit: ~10 req/min. This plugin enforces a 3-second delay between requests.

Usage note: Screener.in does not have a public API. This plugin scrapes the
consolidated view. Respect their terms of service. Add authentication headers
if you have a Screener.in account.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from core.http_client import build_aiohttp_connector
from plugins._base import BasePlugin, FetchResult

logger = logging.getLogger(__name__)

SCREENER_BASE = "https://www.screener.in"
REQUEST_DELAY = 3.0  # seconds between requests (rate limit)


class ScreenerInPlugin(BasePlugin):
    name = "screener_in"
    display_name = "Screener.in"
    supports_live_price = False  # CMP is stale — do not use
    base_url = SCREENER_BASE

    def __init__(self, session=None):
        self._session = session  # aiohttp.ClientSession, injected
        self._last_request_at: Optional[datetime] = None

    async def _get(self, url: str) -> str:
        """Rate-limited HTTP GET. Returns response text."""
        # Enforce delay
        if self._last_request_at:
            elapsed = (datetime.now() - self._last_request_at).total_seconds()
            if elapsed < REQUEST_DELAY:
                await asyncio.sleep(REQUEST_DELAY - elapsed)

        import aiohttp
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml",
        }
        if self._session:
            async with self._session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                self._last_request_at = datetime.now()
                return await resp.text()
        else:
            async with aiohttp.ClientSession(connector=build_aiohttp_connector()) as session:
                async with session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    self._last_request_at = datetime.now()
                    return await resp.text()

    async def fetch_price(self, ticker: str) -> FetchResult:
        """
        Screener CMP is stale — this method raises NotImplementedError.
        Use nse_api or tickertape for live prices.
        """
        raise NotImplementedError(
            "Screener.in CMP is a stale cache. Use NSE API or Tickertape for live prices."
        )

    async def fetch_financials(self, ticker: str) -> FetchResult:
        """
        Fetch consolidated P&L, Balance Sheet, and Cash Flow from Screener.in.
        Returns raw parsed tables — normalizer will standardise units and labels.
        """
        url = f"{SCREENER_BASE}/company/{ticker.upper()}/consolidated/"
        try:
            html = await self._get(url)
            data = self._parse_financials(html, ticker)
            logger.info(f"[screener_in] Fetched financials for {ticker}")
            return self._make_result(data, url)
        except Exception as e:
            logger.warning(f"[screener_in] Failed to fetch financials for {ticker}: {e}")
            raise

    async def fetch_shareholding(self, ticker: str) -> FetchResult:
        """Fetch shareholding pattern from Screener.in."""
        url = f"{SCREENER_BASE}/company/{ticker.upper()}/consolidated/"
        try:
            html = await self._get(url)
            data = self._parse_shareholding(html)
            return self._make_result(data, url)
        except Exception as e:
            logger.warning(f"[screener_in] Failed to fetch shareholding for {ticker}: {e}")
            raise

    async def fetch_concall_transcript(self, ticker: str) -> FetchResult:
        """Fetch list of concall transcripts from Screener.in."""
        url = f"{SCREENER_BASE}/company/{ticker.upper()}/concalls/"
        try:
            html = await self._get(url)
            data = self._parse_concalls(html)
            return self._make_result(data, url)
        except Exception as e:
            logger.warning(f"[screener_in] Failed to fetch concalls for {ticker}: {e}")
            raise

    async def fetch_peers(self, ticker: str) -> FetchResult:
        """Extract peer list from Screener.in company page."""
        url = f"{SCREENER_BASE}/company/{ticker.upper()}/consolidated/"
        try:
            html = await self._get(url)
            data = self._parse_peers(html)
            return self._make_result(data, url)
        except Exception as e:
            logger.warning(f"[screener_in] Failed to fetch peers for {ticker}: {e}")
            raise

    def health_check(self) -> bool:
        """Quick reachability check (synchronous, called at startup)."""
        try:
            import requests
            r = requests.head(SCREENER_BASE, timeout=5)
            return r.status_code < 500
        except Exception:
            return False

    # ── Parser methods (BeautifulSoup) ────────────────────────────────────────

    def _parse_financials(self, html: str, ticker: str) -> dict:
        """
        Parse annual P&L, balance sheet, and cash flow tables.
        Returns raw dict; normalizer handles unit conversion.
        """
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        result = {"ticker": ticker, "source": "screener_in", "tables": {}}

        section_ids = {
            "profit-loss":    "income",
            "balance-sheet":  "balance_sheet",
            "cash-flow":      "cash_flow",
            "quarters":       "quarterly",
        }
        for section_id, key in section_ids.items():
            section = soup.find("section", {"id": section_id})
            if section:
                result["tables"][key] = self._parse_table(section)

        if self._needs_backfill(result["tables"]):
            backfill = self._parse_financials_with_scrapling(html)
            for key, table in backfill.items():
                if not result["tables"].get(key):
                    result["tables"][key] = table
                elif not result["tables"][key].get("rows") and table.get("rows"):
                    result["tables"][key] = table

        # Extract TTM values from quarterly section if available
        result["ttm"] = self._extract_ttm(soup)
        return result

    def _parse_table(self, section) -> dict:
        """Parse a Screener-style responsive table into {header: [values]} dict."""
        table = section.find("table")
        if not table:
            return {}
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        rows = {}
        tbody = table.find("tbody") or table
        for tr in tbody.find_all("tr"):
            cells = tr.find_all(["td", "th"])
            if len(cells) < 2:
                continue
            row_label = cells[0].get_text(strip=True)
            if not row_label or row_label.lower() in {"particulars", "items"}:
                continue
            values = [c.get_text(strip=True).replace(",", "") for c in cells[1:]]
            rows[row_label] = values
        return {"headers": headers, "rows": rows}

    def _needs_backfill(self, tables: dict) -> bool:
        core = ("income", "balance_sheet", "cash_flow")
        for key in core:
            if not tables.get(key) or not tables.get(key, {}).get("rows"):
                return True
        return False

    def _parse_financials_with_scrapling(self, html: str) -> dict:
        """Optional backfill parser using Scrapling selectors when BS4 misses sections."""
        try:
            from scrapling.parser import Selector
            from bs4 import BeautifulSoup
        except Exception:
            return {}

        page = Selector(content=html)
        section_ids = {
            "profit-loss": "income",
            "balance-sheet": "balance_sheet",
            "cash-flow": "cash_flow",
            "quarters": "quarterly",
        }
        parsed = {}
        for sid, key in section_ids.items():
            section = page.css(f"section#{sid}").first
            if not section:
                continue
            table = section.css("table").first
            if not table:
                continue
            soup = BeautifulSoup(table.get(), "lxml")
            parsed[key] = self._parse_table(soup)
        return parsed

    def _extract_ttm(self, soup) -> dict:
        """Extract TTM (trailing twelve months) figures from quarterly section."""
        ttm = {}
        quarters_section = soup.find("section", {"id": "quarters"})
        if not quarters_section:
            return ttm
        table = quarters_section.find("table")
        if not table:
            return ttm
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        ttm_col = None
        for i, h in enumerate(headers):
            if "ttm" in h.lower():
                ttm_col = i
                break
        if ttm_col is None:
            return ttm
        for tr in table.find_all("tr"):
            cells = tr.find_all("td")
            if len(cells) > ttm_col:
                label = cells[0].get_text(strip=True)
                value = cells[ttm_col].get_text(strip=True).replace(",", "")
                ttm[label] = value
        return ttm

    def _parse_shareholding(self, html: str) -> dict:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        section = soup.find("section", {"id": "shareholding"})
        if not section:
            return {}
        return self._parse_table(section)

    def _parse_concalls(self, html: str) -> dict:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        transcripts = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "concall" in href or "transcript" in href.lower():
                transcripts.append({
                    "title": a.get_text(strip=True),
                    "url": href if href.startswith("http") else SCREENER_BASE + href,
                })
        return {"transcripts": transcripts}

    def _parse_peers(self, html: str) -> dict:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        peers_section = soup.find("section", {"id": "peers"})
        if not peers_section:
            return {"peers": []}
        peers = []
        for a in peers_section.find_all("a", href=True):
            href = a["href"]
            if "/company/" in href:
                name = a.get_text(strip=True)
                ticker = href.split("/company/")[-1].strip("/").split("/")[0].upper()
                peers.append({"ticker": ticker, "name": name})
        return {"peers": peers}
