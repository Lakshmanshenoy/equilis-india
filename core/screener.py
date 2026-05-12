"""
core/screener.py
FundamentalScreener — runs rule-based screens over index universes.

Supported operators in filter strings: >, <, >=, <=, ==
Percentage fields (roe, pat_margin, promoter_holding, etc.) are divided by 100
when expressed as percent in filter strings (e.g. "roe>15" → 0.15 internally).

Usage:
    screener = FundamentalScreener(fetcher)
    result = await screener.run(
        index="nifty50",
        filters=["roe>15", "pe_ratio<30"],
        sort_by="roe",
        sort_order="desc",
        limit=20,
    )
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

# ── Index universe file paths ─────────────────────────────────────────────────

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEX_LISTS: dict[str, str] = {
    "nifty50":        os.path.join(_BASE_DIR, "data", "index_lists", "nifty50.txt"),
    "nifty100":       os.path.join(_BASE_DIR, "data", "index_lists", "nifty100.txt"),
    "nifty200":       os.path.join(_BASE_DIR, "data", "index_lists", "nifty200.txt"),
    "nifty500":       os.path.join(_BASE_DIR, "data", "index_lists", "nifty500.txt"),
    "niftymidcap150": os.path.join(_BASE_DIR, "data", "index_lists", "niftymidcap150.txt"),
}

SCREENER_DISCLAIMER = (
    "Results represent stocks matching the specified quantitative filters at the "
    "time of screening. This is not a recommendation to buy, sell, or hold any security. "
    "Quantitative screens do not account for qualitative factors, management quality, "
    "corporate governance, or business moat. Always perform independent due diligence "
    "before making any investment decision."
)

# Fields that are expressed as percentages in filter strings (e.g. roe>15 means >0.15)
_PERCENT_FIELDS = {
    "roe", "roce", "pat_margin", "ebitda_margin", "gross_margin",
    "promoter_holding", "promoter_pledging", "fii_holding", "dii_holding",
    "revenue_growth_5y", "eps_growth_5yr",
}


@dataclass
class ParsedFilter:
    field: str
    op: str
    value: float


@dataclass
class ScreenerResult:
    universe_size: int
    matched_count: int
    results: list[dict]
    filters_applied: list[str]
    sort_field: Optional[str]
    disclaimer: str = field(default=SCREENER_DISCLAIMER)


class FundamentalScreener:
    """
    Rule-based fundamental screener over index ticker universes.
    Requires a DataFetcher with plugins to retrieve financial data.
    """

    def __init__(self, fetcher=None):
        self._fetcher = fetcher

    async def run(
        self,
        index: str = "nifty50",
        sector: Optional[str] = None,
        filters: Optional[list[str]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        limit: int = 50,
    ) -> ScreenerResult:
        """
        Run a screen over an index universe.

        Args:
            index:      One of INDEX_LISTS keys.
            sector:     If provided, restrict to this sector (normalised name).
            filters:    List of filter strings like ["roe>15", "pe_ratio<30"].
            sort_by:    Field to sort results by.
            sort_order: "asc" or "desc".
            limit:      Maximum results to return.

        Returns:
            ScreenerResult with matched results, metadata, and disclaimer.
        """
        tickers = self._load_universe(index)
        universe_size = len(tickers)

        parsed_filters = self._parse_filters(filters or [])

        # Fetch data for all tickers concurrently if fetcher available
        raw_data: dict[str, dict] = {}
        if self._fetcher is not None:
            try:
                bundles = await self._fetcher.fetch_all_concurrent(tickers)
                for ticker, bundle in bundles.items():
                    if bundle and bundle.financials:
                        raw_data[ticker] = bundle.financials.data or {}
            except Exception as e:
                logger.warning(f"[screener] fetch_all_concurrent failed: {e}")

        # Build result rows and apply filters
        matched: list[dict] = []
        for ticker in tickers:
            raw = raw_data.get(ticker, {})
            row = {"ticker": ticker, "sector": self._ticker_sector(ticker)}
            row.update(raw)

            if sector and row.get("sector", "Unknown") != sector:
                continue
            if not self._passes_filters(row, parsed_filters):
                continue
            matched.append(row)

        # Sort
        if sort_by:
            reverse = sort_order.lower() != "asc"
            matched.sort(
                key=lambda r: (r.get(sort_by) is None, r.get(sort_by) or 0),
                reverse=reverse,
            )

        return ScreenerResult(
            universe_size=universe_size,
            matched_count=len(matched),
            results=matched[:limit],
            filters_applied=[f.field + f.op + str(f.value) for f in parsed_filters],
            sort_field=sort_by,
            disclaimer=SCREENER_DISCLAIMER,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _load_universe(self, index: str) -> list[str]:
        """Load tickers from the index list file. Returns empty list on error."""
        path = INDEX_LISTS.get(index)
        if not path or not os.path.exists(path):
            logger.warning(f"[screener] Index file not found for '{index}': {path}")
            return []
        tickers = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    tickers.append(line.upper())
        return tickers

    def _parse_filters(self, filter_strs: list[str]) -> list[ParsedFilter]:
        """
        Parse filter strings into ParsedFilter objects.
        Percentage fields are divided by 100 (e.g. "roe>15" → value=0.15).
        Supported ops: >=, <=, >, <, ==
        """
        pattern = re.compile(r"^([a-zA-Z_]+)\s*(>=|<=|>|<|==)\s*([\d.]+)$")
        parsed = []
        for f in filter_strs:
            m = pattern.match(f.strip())
            if not m:
                logger.warning(f"[screener] Ignoring unparseable filter: '{f}'")
                continue
            field_name = m.group(1)
            op = m.group(2)
            raw_val = float(m.group(3))
            if field_name in _PERCENT_FIELDS:
                raw_val = raw_val / 100.0
            parsed.append(ParsedFilter(field=field_name, op=op, value=raw_val))
        return parsed

    def _passes_filters(self, row: dict, filters: list[ParsedFilter]) -> bool:
        """Return True only if the row passes all filters. Missing field → False."""
        for f in filters:
            val = row.get(f.field)
            if val is None:
                return False
            try:
                val = float(val)
            except (TypeError, ValueError):
                return False
            if f.op == ">":
                if not (val > f.value):
                    return False
            elif f.op == "<":
                if not (val < f.value):
                    return False
            elif f.op == ">=":
                if not (val >= f.value):
                    return False
            elif f.op == "<=":
                if not (val <= f.value):
                    return False
            elif f.op == "==":
                if not (val == f.value):
                    return False
        return True

    def _ticker_sector(self, ticker: str) -> str:
        """Return sector for ticker. Returns 'Unknown' if not available."""
        # Stub — in a production build this would look up the ticker's sector
        # from a local mapping file or from the fetcher's normalised snapshot.
        return "Unknown"
