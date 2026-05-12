"""
tests/conftest.py
Shared pytest fixtures for Phase 3 tests.
Uses the same build_snapshot_from_fixture() pattern as test_analyzer.py
to correctly construct nested CompanySnapshot dataclasses from JSON.
"""

import json
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models.company import (
    BalanceSheetData,
    CashFlowData,
    CompanySnapshot,
    IncomeData,
    MarketData,
    PriceData,
    ShareholdingData,
    YearlyFinancials,
)

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(filename: str) -> dict:
    with open(os.path.join(FIXTURES_DIR, filename)) as f:
        return json.load(f)


def build_snapshot(data: dict) -> CompanySnapshot:
    """Build a fully-typed CompanySnapshot from a raw JSON fixture dict."""
    snap = CompanySnapshot(
        ticker=data["ticker"],
        exchange=data.get("exchange", "NSE"),
        company_name=data.get("company_name", ""),
        sector=data.get("sector", ""),
        industry=data.get("industry", ""),
        snapshot_date=datetime.now(),
    )
    p = data.get("price", {})
    if p:
        snap.price = PriceData(
            cmp=p.get("cmp"),
            week52_high=p.get("week52_high"),
            week52_low=p.get("week52_low"),
            source=p.get("source", ""),
            fetched_at=datetime.now(),
        )
    m = data.get("market", {})
    if m:
        snap.market = MarketData(
            market_cap=m.get("market_cap"),
            shares_outstanding=m.get("shares_outstanding"),
            enterprise_value=m.get("enterprise_value"),
        )
    inc = data.get("income", {})
    if inc:
        snap.income = IncomeData(
            revenue_ttm=inc.get("revenue_ttm"),
            ebitda_ttm=inc.get("ebitda_ttm"),
            ebit=inc.get("ebit"),
            pat_ttm=inc.get("pat_ttm"),
            gross_profit=inc.get("gross_profit"),
            interest_expense=inc.get("interest_expense"),
            depreciation=inc.get("depreciation"),
            eps_ttm=inc.get("eps_ttm"),
            eps_growth_5yr=inc.get("eps_growth_5yr"),
            dividend_per_share=inc.get("dividend_per_share"),
            revenue_5y=inc.get("revenue_5y", []),
            pat_5y=inc.get("pat_5y", []),
            ebitda_5y=inc.get("ebitda_5y", []),
        )
    bs = data.get("balance_sheet", {})
    if bs:
        snap.balance_sheet = BalanceSheetData(
            total_assets=bs.get("total_assets"),
            current_assets=bs.get("current_assets"),
            current_liabilities=bs.get("current_liabilities"),
            total_debt=bs.get("total_debt"),
            equity=bs.get("equity"),
            retained_earnings=bs.get("retained_earnings"),
            cash=bs.get("cash"),
            inventory=bs.get("inventory"),
            receivables=bs.get("receivables"),
            payables=bs.get("payables"),
            ppe=bs.get("ppe"),
            book_value_per_share=bs.get("book_value_per_share"),
        )
    cf = data.get("cash_flow", {})
    if cf:
        snap.cash_flow = CashFlowData(
            cfo_ttm=cf.get("cfo_ttm"),
            capex_ttm=cf.get("capex_ttm"),
            fcf_ttm=cf.get("fcf_ttm"),
            ocf_5y=cf.get("ocf_5y", []),
        )
    sh = data.get("shareholding", {})
    if sh:
        snap.shareholding = ShareholdingData(
            promoter_holding=sh.get("promoter_holding"),
            promoter_pledging=sh.get("promoter_pledging"),
            fii_holding=sh.get("fii_holding"),
            dii_holding=sh.get("dii_holding"),
            public_holding=sh.get("public_holding"),
            promoter_holding_history=sh.get("promoter_holding_history", []),
        )
    snap.screener_raw = data.get("screener_raw", {})
    for yr in data.get("history", []):
        snap.history.append(YearlyFinancials(
            fiscal_year=yr.get("fiscal_year", ""),
            revenue=yr.get("revenue"),
            pat=yr.get("pat"),
            ebitda=yr.get("ebitda"),
            cfo=yr.get("cfo"),
            capex=yr.get("capex"),
            total_assets=yr.get("total_assets"),
            equity=yr.get("equity"),
            receivables=yr.get("receivables"),
            inventory=yr.get("inventory"),
            other_income=yr.get("other_income"),
            pbt=yr.get("pbt"),
            related_party_txn=yr.get("related_party_txn"),
            shares_outstanding=yr.get("shares_outstanding"),
            roce=yr.get("roce"),
        ))
    return snap


# ── Core snapshot fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def infy():
    return build_snapshot(load_fixture("infy_fy24.json"))


@pytest.fixture
def hdfcbank():
    return build_snapshot(load_fixture("hdfcbank_fy24.json"))


@pytest.fixture
def reliance():
    return build_snapshot(load_fixture("reliance_fy24.json"))


@pytest.fixture
def tcs():
    return build_snapshot(load_fixture("tcs_fy24.json"))


@pytest.fixture
def wipro():
    return build_snapshot(load_fixture("wipro_fy24.json"))


# ── Mock infrastructure ────────────────────────────────────────────────────────

@pytest.fixture
def mock_fetcher():
    """AsyncMock fetcher that serves infy_fy24 fixture data."""
    from plugins._base import FetchResult
    infy_data = load_fixture("infy_fy24.json")
    result = FetchResult(
        data=infy_data,
        source_url="https://mock.example.com/infy",
        fetched_at=datetime.now(),
        source_name="mock",
    )
    fetcher = MagicMock()
    fetcher.fetch_price = AsyncMock(return_value=result)
    fetcher.fetch_financials = AsyncMock(return_value=result)
    fetcher.fetch_shareholding = AsyncMock(return_value=result)
    fetcher.fetch_corporate_actions = AsyncMock(return_value=result)
    fetcher.fetch_all = AsyncMock(return_value=result)
    fetcher.fetch_all_concurrent = AsyncMock(return_value={"INFY": result})
    return fetcher


@pytest.fixture
def mock_cache():
    """MagicMock cache that behaves as empty (no hits)."""
    cache = MagicMock()
    cache.get = MagicMock(return_value=None)
    cache.set = MagicMock(return_value=True)
    cache.disabled = False
    return cache
