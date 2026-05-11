"""
tests/test_analyzer.py
Tests for EquityAnalyzer — verifies ratio computations against known fixtures.
All expected values are computed from infy_fy24.json reference data.
"""

import json
import os
import sys
from datetime import datetime

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.analyzer import EquityAnalyzer
from core.models.company import (
    BalanceSheetData,
    CashFlowData,
    CompanySnapshot,
    IncomeData,
    MarketData,
    PriceData,
    ShareholdingData,
)

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name: str) -> dict:
    with open(os.path.join(FIXTURE_DIR, name)) as f:
        return json.load(f)


def build_snapshot_from_fixture(data: dict) -> CompanySnapshot:
    snap = CompanySnapshot(
        ticker=data["ticker"],
        exchange=data["exchange"],
        company_name=data.get("company_name", ""),
        sector=data.get("sector", ""),
        snapshot_date=datetime.now(),
    )
    p = data.get("price", {})
    snap.price = PriceData(
        cmp=p.get("cmp"),
        week52_high=p.get("week52_high"),
        week52_low=p.get("week52_low"),
        source=p.get("source", ""),
        fetched_at=datetime.now(),
    )
    m = data.get("market", {})
    snap.market = MarketData(
        market_cap=m.get("market_cap"),
        shares_outstanding=m.get("shares_outstanding"),
        enterprise_value=m.get("enterprise_value"),
    )
    inc = data.get("income", {})
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
    snap.cash_flow = CashFlowData(
        cfo_ttm=cf.get("cfo_ttm"),
        capex_ttm=cf.get("capex_ttm"),
        fcf_ttm=cf.get("fcf_ttm"),
        ocf_5y=cf.get("ocf_5y", []),
    )
    sh = data.get("shareholding", {})
    snap.shareholding = ShareholdingData(
        promoter_holding=sh.get("promoter_holding"),
        promoter_pledging=sh.get("promoter_pledging"),
        fii_holding=sh.get("fii_holding"),
        dii_holding=sh.get("dii_holding"),
        public_holding=sh.get("public_holding"),
        promoter_holding_history=sh.get("promoter_holding_history", []),
    )
    snap.screener_raw = data.get("screener_raw", {})
    return snap


@pytest.fixture
def infy_snapshot():
    return build_snapshot_from_fixture(load_fixture("infy_fy24.json"))


@pytest.fixture
def reliance_snapshot():
    return build_snapshot_from_fixture(load_fixture("reliance_fy24.json"))


@pytest.fixture
def analyzer():
    return EquityAnalyzer()


# ── Profitability ─────────────────────────────────────────────────────────────

def test_pat_margin_infy(analyzer, infy_snapshot):
    ratios = analyzer.compute_profitability(infy_snapshot)
    assert ratios.pat_margin is not None
    expected = 26248 / 153670
    assert abs(ratios.pat_margin - expected) < 0.001


def test_ebitda_margin_infy(analyzer, infy_snapshot):
    ratios = analyzer.compute_profitability(infy_snapshot)
    assert ratios.ebitda_margin is not None
    expected = 40100 / 153670
    assert abs(ratios.ebitda_margin - expected) < 0.001


def test_roe_infy(analyzer, infy_snapshot):
    ratios = analyzer.compute_profitability(infy_snapshot)
    assert ratios.roe is not None
    expected = 26248 / 68900
    assert abs(ratios.roe - expected) < 0.001


# ── DuPont ────────────────────────────────────────────────────────────────────

def test_dupont_roe_consistency(analyzer, infy_snapshot):
    dp = analyzer.dupont_decomposition(infy_snapshot)
    assert dp.roe_dupont is not None
    # DuPont ROE should be within 1% of reported ROE
    prof = analyzer.compute_profitability(infy_snapshot)
    assert abs(dp.roe_dupont - dp.roe_reported) < 0.02


# ── Cash flow quality ─────────────────────────────────────────────────────────

def test_cfo_pat_ratio_infy(analyzer, infy_snapshot):
    cfq = analyzer.cash_flow_quality(infy_snapshot)
    expected = 31200 / 26248
    assert abs(cfq.cfo_pat_ratio - expected) < 0.001
    assert cfq.quality_signal == "HIGH"


# ── Leverage ──────────────────────────────────────────────────────────────────

def test_debt_equity_infy(analyzer, infy_snapshot):
    lev = analyzer.leverage_ratios(infy_snapshot)
    expected = 3200 / 68900
    assert lev.debt_to_equity is not None
    assert abs(lev.debt_to_equity - expected) < 0.001


def test_current_ratio_infy(analyzer, infy_snapshot):
    lev = analyzer.leverage_ratios(infy_snapshot)
    expected = 71200 / 28900
    assert lev.current_ratio is not None
    assert abs(lev.current_ratio - expected) < 0.01


# ── Valuation ─────────────────────────────────────────────────────────────────

def test_pe_infy(analyzer, infy_snapshot):
    val = analyzer.valuation_ratios(infy_snapshot)
    expected = 1437.5 / 63.08
    assert val.pe_ttm is not None
    assert abs(val.pe_ttm - expected) < 0.1


# ── Red flags ─────────────────────────────────────────────────────────────────

def test_no_red_flags_infy(analyzer, infy_snapshot):
    flags = analyzer.red_flag_scan(infy_snapshot)
    # INFY has healthy CFO and low debt — should have zero critical flags
    critical = [f for f in flags if f["severity"] == "CRITICAL"]
    assert len(critical) == 0


def test_altman_z_infy(analyzer, infy_snapshot):
    z = analyzer.altman_z_score(infy_snapshot)
    assert "score" in z
    assert "disclaimer" in z
    assert "Altman" in z["disclaimer"]
    # INFY should be in safe zone (z > 2.99) being a profitable tech company
    if z["score"] is not None:
        assert z["score"] > 0


# ── Missing data handling ─────────────────────────────────────────────────────

def test_handles_missing_income():
    snap = CompanySnapshot(ticker="TEST", exchange="NSE")
    analyzer = EquityAnalyzer()
    result = analyzer.compute_profitability(snap)
    assert result.pat_margin is None
    assert result.roe is None


def test_compute_all_returns_ratio_set(analyzer, infy_snapshot):
    ratios = analyzer.compute_all(infy_snapshot)
    assert ratios.ticker == "INFY"
    assert ratios.profitability is not None
    assert ratios.leverage is not None
    assert ratios.valuation is not None
