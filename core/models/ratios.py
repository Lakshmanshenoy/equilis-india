"""
core/models/ratios.py
RatioSet — computed financial ratios with source attribution.
All ratio values are floats or None if input data was unavailable.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProfitabilityRatios:
    gross_margin: Optional[float] = None
    ebitda_margin: Optional[float] = None
    pat_margin: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    roce: Optional[float] = None


@dataclass
class DuPontDecomposition:
    net_profit_margin: Optional[float] = None
    asset_turnover: Optional[float] = None
    equity_multiplier: Optional[float] = None
    roe_dupont: Optional[float] = None
    roe_reported: Optional[float] = None


@dataclass
class LeverageRatios:
    debt_to_equity: Optional[float] = None
    debt_to_ebitda: Optional[float] = None
    interest_coverage: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None


@dataclass
class ValuationRatios:
    pe_ttm: Optional[float] = None
    pb: Optional[float] = None
    ev_ebitda: Optional[float] = None
    ev_sales: Optional[float] = None
    peg: Optional[float] = None
    div_yield: Optional[float] = None


@dataclass
class EfficiencyRatios:
    receivables_days: Optional[float] = None
    inventory_days: Optional[float] = None
    payables_days: Optional[float] = None
    cash_conversion_cycle: Optional[float] = None
    asset_turnover: Optional[float] = None


@dataclass
class CashFlowQuality:
    cfo_pat_ratio: Optional[float] = None
    quality_signal: str = "UNKNOWN"   # HIGH / MEDIUM / LOW
    note: str = ""


@dataclass
class RatioSet:
    ticker: str
    fiscal_year: str = ""
    profitability: Optional[ProfitabilityRatios] = None
    dupont: Optional[DuPontDecomposition] = None
    leverage: Optional[LeverageRatios] = None
    valuation: Optional[ValuationRatios] = None
    efficiency: Optional[EfficiencyRatios] = None
    cash_flow_quality: Optional[CashFlowQuality] = None
    computed_at: str = ""
