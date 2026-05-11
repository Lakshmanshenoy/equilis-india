"""
core/normalizer.py
DataNormalizer — converts raw FetchBundle into a typed CompanySnapshot.

Responsibilities:
1. Unit standardisation → ₹ Crore throughout
2. FY label alignment (Indian April–March)
3. Null-safe extraction with fallback logic
4. Assembling CompanySnapshot from multiple FetchResult sources
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any, Optional

from core.fetcher import FetchBundle
from core.models.company import (
    BalanceSheetData,
    CashFlowData,
    CompanySnapshot,
    IncomeData,
    MarketData,
    PriceData,
    ShareholdingData,
    SourceMeta,
)

logger = logging.getLogger(__name__)


def _to_float(value: Any) -> Optional[float]:
    """Null-safe conversion to float. Returns None on failure."""
    if value is None:
        return None
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return None


def _screener_unit_to_crore(raw_value: str) -> Optional[float]:
    """
    Screener.in reports figures in ₹ Crore by default.
    This function strips commas/spaces and handles edge cases.
    """
    if not raw_value:
        return None
    cleaned = str(raw_value).replace(",", "").replace("₹", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _make_fy_label(index: int, latest_fy_end_year: int) -> str:
    """
    Convert a list index (0 = oldest) to FY label.
    E.g. latest_fy_end_year=2024, 5 years → ["FY20","FY21","FY22","FY23","FY24"]
    """
    year = latest_fy_end_year - 4 + index
    return f"FY{str(year)[-2:]}"


class DataNormalizer:
    """
    Transforms raw plugin outputs (FetchBundle) into a structured CompanySnapshot.
    """

    def normalise(
        self,
        bundle: FetchBundle,
        ticker: str,
        exchange: str = "NSE",
        latest_fy_end_year: Optional[int] = None,
    ) -> CompanySnapshot:
        """
        Main entry point. Returns a CompanySnapshot with all available fields
        populated from the sources in the FetchBundle.
        """
        if latest_fy_end_year is None:
            latest_fy_end_year = datetime.now().year
            if datetime.now().month < 4:   # Before April → still previous FY
                latest_fy_end_year -= 1

        snapshot = CompanySnapshot(ticker=ticker, exchange=exchange)
        snapshot.snapshot_date = datetime.now()

        if bundle.price:
            snapshot.price = self._normalise_price(bundle.price)
            snapshot.nse_raw.update(bundle.price.data)
            snapshot.sources.append(SourceMeta(
                source_name=bundle.price.source_name,
                source_url=bundle.price.source_url,
                fetched_at=bundle.price.fetched_at,
                is_fallback=bundle.price.is_fallback,
            ))

        if bundle.financials:
            self._normalise_financials(snapshot, bundle.financials, latest_fy_end_year)
            if "screener" in bundle.financials.source_name.lower():
                snapshot.screener_raw.update(bundle.financials.data)
            elif "tickertape" in bundle.financials.source_name.lower():
                snapshot.tickertape_raw.update(bundle.financials.data)
            elif "bse" in bundle.financials.source_name.lower():
                snapshot.bse_raw.update(bundle.financials.data)
            snapshot.sources.append(SourceMeta(
                source_name=bundle.financials.source_name,
                source_url=bundle.financials.source_url,
                fetched_at=bundle.financials.fetched_at,
                is_fallback=bundle.financials.is_fallback,
            ))

        if bundle.shareholding:
            snapshot.shareholding = self._normalise_shareholding(bundle.shareholding)
            snapshot.sources.append(SourceMeta(
                source_name=bundle.shareholding.source_name,
                source_url=bundle.shareholding.source_url,
                fetched_at=bundle.shareholding.fetched_at,
                is_fallback=bundle.shareholding.is_fallback,
            ))

        return snapshot

    def _normalise_price(self, result) -> PriceData:
        d = result.data
        return PriceData(
            cmp=_to_float(d.get("cmp") or d.get("lastPrice")),
            week52_high=_to_float(d.get("week52_high") or d.get("high52")),
            week52_low=_to_float(d.get("week52_low") or d.get("low52")),
            source=result.source_name,
            fetched_at=result.fetched_at,
            source_url=result.source_url,
        )

    def _normalise_financials(
        self,
        snapshot: CompanySnapshot,
        result,
        latest_fy_end_year: int,
    ) -> None:
        """Extract income, balance sheet, cash flow from screener/tickertape data."""
        tables = result.data.get("tables", {})
        ttm = result.data.get("ttm", {})

        income = IncomeData()
        bs = BalanceSheetData()
        cf = CashFlowData()
        market = MarketData()

        # ── P&L ──────────────────────────────────────────────────────────────
        income_rows = tables.get("income", {}).get("rows", {})
        income.revenue_ttm = _screener_unit_to_crore(
            ttm.get("Sales") or ttm.get("Revenue") or
            self._last_val(income_rows, "Sales")
        )
        income.pat_ttm = _screener_unit_to_crore(
            ttm.get("Net Profit") or self._last_val(income_rows, "Net Profit")
        )
        income.ebitda_ttm = _screener_unit_to_crore(
            ttm.get("Operating Profit") or
            self._last_val(income_rows, "Operating Profit")
        )
        income.eps_ttm = _to_float(
            ttm.get("EPS in Rs") or self._last_val(income_rows, "EPS in Rs")
        )
        income.revenue_5y = self._extract_series(income_rows, "Sales")
        income.pat_5y = self._extract_series(income_rows, "Net Profit")
        income.ebitda_5y = self._extract_series(income_rows, "Operating Profit")

        # ── Balance sheet ─────────────────────────────────────────────────────
        bs_rows = tables.get("balance_sheet", {}).get("rows", {})
        bs.total_assets = _screener_unit_to_crore(
            self._last_val(bs_rows, "Total Assets")
        )
        bs.equity = _screener_unit_to_crore(
            self._last_val(bs_rows, "Equity Capital") or
            self._last_val(bs_rows, "Total Equity")
        )
        bs.total_debt = _screener_unit_to_crore(
            self._last_val(bs_rows, "Borrowings") or
            self._last_val(bs_rows, "Total Debt")
        )
        bs.current_assets = _screener_unit_to_crore(
            self._last_val(bs_rows, "Current Assets")
        )
        bs.current_liabilities = _screener_unit_to_crore(
            self._last_val(bs_rows, "Current Liabilities")
        )
        bs.inventory = _screener_unit_to_crore(
            self._last_val(bs_rows, "Inventories")
        )
        bs.receivables = _screener_unit_to_crore(
            self._last_val(bs_rows, "Trade Receivables") or
            self._last_val(bs_rows, "Debtors")
        )
        bs.cash = _screener_unit_to_crore(
            self._last_val(bs_rows, "Cash Equivalents") or
            self._last_val(bs_rows, "Cash & Bank")
        )

        # ── Cash flow ─────────────────────────────────────────────────────────
        cf_rows = tables.get("cash_flow", {}).get("rows", {})
        cf.cfo_ttm = _screener_unit_to_crore(
            self._last_val(cf_rows, "Cash from Operations") or
            self._last_val(cf_rows, "Operating Activity")
        )
        cf.capex_ttm = _screener_unit_to_crore(
            self._last_val(cf_rows, "Capital Expenditure") or
            self._last_val(cf_rows, "CAPEX")
        )
        if cf.cfo_ttm is not None and cf.capex_ttm is not None:
            cf.fcf_ttm = cf.cfo_ttm - abs(cf.capex_ttm)
        cf.ocf_5y = self._extract_series(cf_rows, "Cash from Operations")

        snapshot.income = income
        snapshot.balance_sheet = bs
        snapshot.cash_flow = cf
        if snapshot.market is None:
            snapshot.market = market

    def _normalise_shareholding(self, result) -> ShareholdingData:
        d = result.data
        rows = {}
        if isinstance(d, dict) and "rows" in d:
            rows = d["rows"]
        return ShareholdingData(
            promoter_holding=_to_float(self._last_val(rows, "Promoters")),
            fii_holding=_to_float(self._last_val(rows, "FIIs") or
                                   self._last_val(rows, "Foreign Institutions")),
            dii_holding=_to_float(self._last_val(rows, "DIIs") or
                                   self._last_val(rows, "Domestic Institutions")),
            public_holding=_to_float(self._last_val(rows, "Public")),
            fetched_at=result.fetched_at,
            source=result.source_name,
        )

    @staticmethod
    def _last_val(rows: dict, key: str) -> Optional[str]:
        """Return the most recent (last) value from a table row."""
        vals = rows.get(key, [])
        if vals:
            return vals[-1]
        return None

    @staticmethod
    def _extract_series(rows: dict, key: str) -> list[float]:
        """Extract all numeric values from a table row, oldest-first."""
        raw_vals = rows.get(key, [])
        result = []
        for v in raw_vals:
            f = _screener_unit_to_crore(v)
            if f is not None:
                result.append(f)
        return result
