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


SECTOR_NORMALISATION_MAP: dict[str, str] = {
    "Information Technology": "IT",
    "IT - Software": "IT",
    "Banks": "Banking",
    "Finance": "Banking",
    "NBFC": "Banking",
    "Pharmaceuticals": "Pharma",
    "FMCG": "FMCG",
    "Consumer Goods": "FMCG",
    "Cement & Cement Products": "Cement",
    "Automobile": "Auto",
    "Auto Ancillaries": "Auto",
    "Steel": "Steel",
    "Metals - Ferrous": "Steel",
    "Power Generation & Distribution": "Power",
    "Telecom - Equipment & Accessories": "Telecom",
    "Consumer Durables": "Consumer Durables",
    "Real Estate": "Real Estate",
}


def normalise_sector(raw_sector: str) -> str:
    """Map raw sector string to canonical sector name used in MACRO_SENSITIVITY_CONFIG."""
    return SECTOR_NORMALISATION_MAP.get(raw_sector, raw_sector)


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
            source_name = bundle.price.source_name.lower()
            if "tickertape" in source_name:
                snapshot.tickertape_raw.update(bundle.price.data)
            elif "bse" in source_name:
                snapshot.bse_raw.update(bundle.price.data)
            else:
                snapshot.nse_raw.update(bundle.price.data)
            self._merge_market_from_price(snapshot, bundle.price.data)
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

        if not tables:
            self._normalise_direct_financials(snapshot, result.data)
            return

        income = IncomeData()
        bs = BalanceSheetData()
        cf = CashFlowData()
        market = MarketData()

        # ── P&L ──────────────────────────────────────────────────────────────
        income_rows = tables.get("income", {}).get("rows", {})
        income.revenue_ttm = _screener_unit_to_crore(
            ttm.get("Sales") or ttm.get("Revenue") or ttm.get("Revenue from Operations") or
            self._last_val_any(income_rows, "Sales", "Revenue", "Revenue from Operations", "Total Income")
        )
        income.pat_ttm = _screener_unit_to_crore(
            ttm.get("Net Profit") or ttm.get("Profit after tax") or
            self._last_val_any(income_rows, "Net Profit", "Profit after tax", "PAT")
        )
        income.ebitda_ttm = _screener_unit_to_crore(
            ttm.get("Operating Profit") or ttm.get("EBITDA") or
            self._last_val_any(income_rows, "Operating Profit", "EBITDA", "PBDIT")
        )
        income.eps_ttm = _to_float(
            ttm.get("EPS in Rs") or ttm.get("EPS") or
            self._last_val_any(income_rows, "EPS in Rs", "EPS")
        )
        income.revenue_5y = self._extract_series_any(income_rows, "Sales", "Revenue", "Revenue from Operations", "Total Income")
        income.pat_5y = self._extract_series_any(income_rows, "Net Profit", "Profit after tax", "PAT")
        income.ebitda_5y = self._extract_series_any(income_rows, "Operating Profit", "EBITDA", "PBDIT")

        # ── Balance sheet ─────────────────────────────────────────────────────
        bs_rows = tables.get("balance_sheet", {}).get("rows", {})
        bs.total_assets = _screener_unit_to_crore(
            self._last_val_any(bs_rows, "Total Assets")
        )
        total_equity = _screener_unit_to_crore(
            self._last_val_any(bs_rows, "Total Equity", "Net Worth", "Shareholders Funds")
        )
        if total_equity is None:
            equity_capital = _screener_unit_to_crore(self._last_val_any(bs_rows, "Equity Capital", "Share Capital"))
            reserves = _screener_unit_to_crore(self._last_val_any(bs_rows, "Reserves", "Reserves & Surplus"))
            if equity_capital is not None and reserves is not None:
                total_equity = equity_capital + reserves
        bs.equity = total_equity
        bs.total_debt = _screener_unit_to_crore(
            self._last_val_any(bs_rows, "Borrowings", "Total Debt", "Debt")
        )
        bs.current_assets = _screener_unit_to_crore(
            self._last_val_any(bs_rows, "Current Assets")
        )
        bs.current_liabilities = _screener_unit_to_crore(
            self._last_val_any(bs_rows, "Current Liabilities")
        )
        bs.inventory = _screener_unit_to_crore(
            self._last_val_any(bs_rows, "Inventories", "Inventory")
        )
        bs.receivables = _screener_unit_to_crore(
            self._last_val_any(bs_rows, "Trade Receivables", "Debtors", "Receivables")
        )
        bs.cash = _screener_unit_to_crore(
            self._last_val_any(bs_rows, "Cash Equivalents", "Cash & Bank", "Cash and Cash Equivalents")
        )

        # ── Cash flow ─────────────────────────────────────────────────────────
        cf_rows = tables.get("cash_flow", {}).get("rows", {})
        cf.cfo_ttm = _screener_unit_to_crore(
            self._last_val_any(cf_rows, "Cash from Operations", "Cash from Operating Activity", "Operating Activity")
        )
        cf.capex_ttm = _screener_unit_to_crore(
            self._last_val_any(cf_rows, "Capital Expenditure", "CAPEX")
        )
        if cf.cfo_ttm is not None and cf.capex_ttm is not None:
            cf.fcf_ttm = cf.cfo_ttm - abs(cf.capex_ttm)
        cf.ocf_5y = self._extract_series_any(cf_rows, "Cash from Operations", "Cash from Operating Activity", "Operating Activity")

        snapshot.income = income
        snapshot.balance_sheet = bs
        snapshot.cash_flow = cf
        if snapshot.market is None:
            snapshot.market = market
        if (
            snapshot.market.shares_outstanding is None
            and income.pat_ttm is not None
            and income.eps_ttm not in (None, 0)
        ):
            # PAT is in crore and EPS is in rupees; output shares outstanding in million.
            snapshot.market.shares_outstanding = (income.pat_ttm * 10.0) / income.eps_ttm

    def _normalise_direct_financials(self, snapshot: CompanySnapshot, data: dict) -> None:
        """Normalise plugin payloads that already use standard-ish field names."""
        income_src = data.get("income") or data
        balance_src = data.get("balance") or data.get("balance_sheet") or data
        cash_src = data.get("cashflow") or data.get("cash_flow") or data
        market_src = data.get("market") or data

        income = IncomeData(
            revenue_ttm=_to_float(income_src.get("revenue_ttm") or income_src.get("revenue") or income_src.get("netSales")),
            ebitda_ttm=_to_float(income_src.get("ebitda_ttm") or income_src.get("ebitda")),
            pat_ttm=_to_float(income_src.get("pat_ttm") or income_src.get("pat") or income_src.get("netProfit")),
            eps_ttm=_to_float(income_src.get("eps_ttm") or income_src.get("eps")),
            dividend_per_share=_to_float(income_src.get("dividend_per_share") or income_src.get("dps")),
            revenue_5y=[v for v in (_to_float(x) for x in income_src.get("revenue_5y", [])) if v is not None],
            pat_5y=[v for v in (_to_float(x) for x in income_src.get("pat_5y", [])) if v is not None],
            ebitda_5y=[v for v in (_to_float(x) for x in income_src.get("ebitda_5y", [])) if v is not None],
        )
        bs = BalanceSheetData(
            total_assets=_to_float(balance_src.get("total_assets") or balance_src.get("totalAssets")),
            current_assets=_to_float(balance_src.get("current_assets") or balance_src.get("currentAssets")),
            current_liabilities=_to_float(balance_src.get("current_liabilities") or balance_src.get("currentLiabilities")),
            total_debt=_to_float(balance_src.get("total_debt") or balance_src.get("totalDebt") or balance_src.get("borrowings")),
            equity=_to_float(balance_src.get("equity") or balance_src.get("netWorth")),
            cash=_to_float(balance_src.get("cash") or balance_src.get("cashEquivalents")),
            inventory=_to_float(balance_src.get("inventory") or balance_src.get("inventories")),
            receivables=_to_float(balance_src.get("receivables") or balance_src.get("tradeReceivables")),
            payables=_to_float(balance_src.get("payables") or balance_src.get("tradePayables")),
            book_value_per_share=_to_float(balance_src.get("book_value_per_share") or balance_src.get("bookValuePerShare")),
        )
        cf = CashFlowData(
            cfo_ttm=_to_float(cash_src.get("cfo_ttm") or cash_src.get("cfo") or cash_src.get("operatingCashFlow")),
            capex_ttm=_to_float(cash_src.get("capex_ttm") or cash_src.get("capex")),
            ocf_5y=[v for v in (_to_float(x) for x in cash_src.get("ocf_5y", [])) if v is not None],
        )
        if cf.cfo_ttm is not None and cf.capex_ttm is not None:
            cf.fcf_ttm = cf.cfo_ttm - abs(cf.capex_ttm)

        market = snapshot.market or MarketData()
        market.market_cap = market.market_cap or _to_float(market_src.get("market_cap") or market_src.get("marketCap"))
        market.enterprise_value = market.enterprise_value or _to_float(market_src.get("enterprise_value") or market_src.get("enterpriseValue"))
        market.shares_outstanding = market.shares_outstanding or _to_float(
            market_src.get("shares_outstanding") or market_src.get("sharesOutstanding")
        )

        snapshot.income = income
        snapshot.balance_sheet = bs
        snapshot.cash_flow = cf
        snapshot.market = market

    def _merge_market_from_price(self, snapshot: CompanySnapshot, data: dict) -> None:
        market_cap = _to_float(data.get("market_cap_cr") or data.get("market_cap") or data.get("marketCap"))
        shares = _to_float(data.get("shares_outstanding") or data.get("sharesOutstanding"))
        if market_cap is None and shares is None:
            return
        if snapshot.market is None:
            snapshot.market = MarketData()
        snapshot.market.market_cap = snapshot.market.market_cap or market_cap
        snapshot.market.shares_outstanding = snapshot.market.shares_outstanding or shares

    def _normalise_shareholding(self, result) -> ShareholdingData:
        d = result.data
        rows = {}
        if isinstance(d, dict) and "rows" in d:
            rows = d["rows"]
        if isinstance(d, dict) and not rows:
            return ShareholdingData(
                promoter_holding=_to_float(d.get("promoter_holding")),
                promoter_pledging=_to_float(d.get("promoter_pledging") or d.get("promoter_pledge")),
                fii_holding=_to_float(d.get("fii_holding")),
                dii_holding=_to_float(d.get("dii_holding")),
                public_holding=_to_float(d.get("public_holding")),
                fetched_at=result.fetched_at,
                source=result.source_name,
                promoter_holding_history=[
                    v for v in (_to_float(x) for x in d.get("promoter_holding_history", []))
                    if v is not None
                ],
            )
        return ShareholdingData(
            promoter_holding=_to_float(self._last_val(rows, "Promoters")),
            promoter_pledging=_to_float(self._last_val(rows, "Pledged") or
                                        self._last_val(rows, "Promoter Pledge")),
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
        key_norm = DataNormalizer._norm_key(key)
        for row_key, row_vals in rows.items():
            if DataNormalizer._norm_key(row_key) == key_norm and row_vals:
                return row_vals[-1]
        return None

    @staticmethod
    def _last_val_any(rows: dict, *keys: str) -> Optional[str]:
        for key in keys:
            val = DataNormalizer._last_val(rows, key)
            if val is not None:
                return val
        return None

    @staticmethod
    def _norm_key(value: str) -> str:
        return re.sub(r"[^a-z0-9]", "", (value or "").lower())

    @staticmethod
    def _extract_series(rows: dict, key: str) -> list[float]:
        """Extract all numeric values from a table row, oldest-first."""
        raw_vals = rows.get(key, [])
        if not raw_vals:
            key_norm = DataNormalizer._norm_key(key)
            for row_key, row_vals in rows.items():
                if DataNormalizer._norm_key(row_key) == key_norm:
                    raw_vals = row_vals
                    break
        result = []
        for v in raw_vals:
            f = _screener_unit_to_crore(v)
            if f is not None:
                result.append(f)
        return result

    @staticmethod
    def _extract_series_any(rows: dict, *keys: str) -> list[float]:
        for key in keys:
            vals = DataNormalizer._extract_series(rows, key)
            if vals:
                return vals
        return []
