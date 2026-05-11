"""
core/models/company.py
CompanySnapshot — the central data contract passed between pipeline stages.
Every field carries source and fetch-time metadata for compliance and validation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class PriceData:
    cmp: float
    week52_high: float
    week52_low: float
    source: str
    fetched_at: datetime
    source_url: str = ""


@dataclass
class MarketData:
    market_cap: Optional[float] = None        # ₹ Crore
    shares_outstanding: Optional[float] = None  # millions
    enterprise_value: Optional[float] = None  # ₹ Crore


@dataclass
class BalanceSheetData:
    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    total_debt: Optional[float] = None
    equity: Optional[float] = None
    retained_earnings: Optional[float] = None
    cash: Optional[float] = None
    inventory: Optional[float] = None
    receivables: Optional[float] = None
    payables: Optional[float] = None
    ppe: Optional[float] = None               # Property, plant & equipment
    total_liabilities: Optional[float] = None
    working_capital: Optional[float] = None
    book_value_per_share: Optional[float] = None


@dataclass
class IncomeData:
    revenue_ttm: Optional[float] = None
    ebitda_ttm: Optional[float] = None
    ebit: Optional[float] = None
    pat_ttm: Optional[float] = None           # Profit after tax
    gross_profit: Optional[float] = None
    interest_expense: Optional[float] = None
    depreciation: Optional[float] = None
    other_income: Optional[float] = None
    eps_ttm: Optional[float] = None
    eps_growth_5yr: Optional[float] = None    # CAGR as decimal, e.g. 0.12
    dividend_per_share: Optional[float] = None
    # 5-year annual series (index 0 = oldest)
    revenue_5y: list[float] = field(default_factory=list)
    pat_5y: list[float] = field(default_factory=list)
    ebitda_5y: list[float] = field(default_factory=list)


@dataclass
class CashFlowData:
    cfo_ttm: Optional[float] = None           # Operating cash flow
    capex_ttm: Optional[float] = None
    fcf_ttm: Optional[float] = None           # cfo - capex
    ocf_5y: list[float] = field(default_factory=list)


@dataclass
class ShareholdingData:
    promoter_holding: Optional[float] = None  # %
    promoter_pledging: Optional[float] = None  # % of promoter holding pledged
    fii_holding: Optional[float] = None
    dii_holding: Optional[float] = None
    public_holding: Optional[float] = None
    fetched_at: Optional[datetime] = None
    source: str = ""
    # History (last 4 quarters, newest first)
    promoter_holding_history: list[float] = field(default_factory=list)


@dataclass
class YearlyFinancials:
    """Per-year financial snapshot used for multi-year trend analysis."""
    fiscal_year: str = ""
    revenue: Optional[float] = None
    pat: Optional[float] = None
    ebitda: Optional[float] = None
    cfo: Optional[float] = None
    capex: Optional[float] = None
    total_assets: Optional[float] = None
    equity: Optional[float] = None
    receivables: Optional[float] = None
    inventory: Optional[float] = None
    other_income: Optional[float] = None
    pbt: Optional[float] = None
    related_party_txn: Optional[float] = None
    shares_outstanding: Optional[float] = None
    roce: Optional[float] = None


@dataclass
class SourceMeta:
    source_name: str
    source_url: str
    fetched_at: datetime
    is_fallback: bool = False


@dataclass
class CompanySnapshot:
    ticker: str
    exchange: str                              # "NSE" or "BSE"
    company_name: str = ""
    sector: str = ""
    industry: str = ""

    price: Optional[PriceData] = None
    market: Optional[MarketData] = None
    income: Optional[IncomeData] = None
    balance_sheet: Optional[BalanceSheetData] = None
    cash_flow: Optional[CashFlowData] = None
    shareholding: Optional[ShareholdingData] = None

    # Cross-source raw readings for validator
    screener_raw: dict = field(default_factory=dict)
    tickertape_raw: dict = field(default_factory=dict)
    bse_raw: dict = field(default_factory=dict)
    nse_raw: dict = field(default_factory=dict)

    sources: list[SourceMeta] = field(default_factory=list)
    snapshot_date: Optional[datetime] = None

    # Multi-year history (newest first, e.g. FY24 at index 0)
    history: list["YearlyFinancials"] = field(default_factory=list)

    # Computed ratios (attached after analysis stage, used by peer pipeline)
    ratios: Optional[object] = None

    def get_metric(self, metric: str, source: str) -> Optional[float]:
        """Retrieve a specific metric from a named raw source dict."""
        raw = getattr(self, f"{source}_raw", {})
        return raw.get(metric)
