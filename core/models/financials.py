"""
core/models/financials.py
FinancialStatement — annual or TTM financial statement data.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class FinancialStatement:
    """Annual financial statement (P&L + BS + CF in one struct)."""
    fiscal_year: str                          # e.g. "FY24"

    # P&L
    revenue: Optional[float] = None
    cogs: Optional[float] = None
    gross_profit: Optional[float] = None
    ebitda: Optional[float] = None
    ebit: Optional[float] = None
    interest_expense: Optional[float] = None
    depreciation: Optional[float] = None
    pbt: Optional[float] = None
    tax: Optional[float] = None
    pat: Optional[float] = None
    other_income: Optional[float] = None
    eps_diluted: Optional[float] = None
    dividend_per_share: Optional[float] = None

    # Balance sheet
    total_assets: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    total_debt: Optional[float] = None
    equity: Optional[float] = None
    retained_earnings: Optional[float] = None
    inventory: Optional[float] = None
    receivables: Optional[float] = None
    payables: Optional[float] = None
    ppe: Optional[float] = None
    cash: Optional[float] = None

    # Cash flow
    cfo: Optional[float] = None
    capex: Optional[float] = None
    cff: Optional[float] = None              # Financing activities

    # Audit & governance
    auditor: str = ""
    audit_qualified: bool = False

    # Source metadata
    source: str = ""
    source_url: str = ""

    @property
    def fcf(self) -> Optional[float]:
        if self.cfo is not None and self.capex is not None:
            return self.cfo - abs(self.capex)
        return None

    @property
    def working_capital(self) -> Optional[float]:
        if self.current_assets is not None and self.current_liabilities is not None:
            return self.current_assets - self.current_liabilities
        return None

    @property
    def total_liabilities(self) -> Optional[float]:
        if self.total_assets is not None and self.equity is not None:
            return self.total_assets - self.equity
        return None
