"""
Regression tests for critical-field validation and report coverage diagnostics.
"""

from datetime import datetime

import pytest

from core.models.company import (
    BalanceSheetData,
    CashFlowData,
    CompanySnapshot,
    IncomeData,
    MarketData,
    PriceData,
    ShareholdingData,
)
from core.renderer import ReportRenderer
from core.validator import DataQualityError, DataValidator


def _make_snapshot() -> CompanySnapshot:
    s = CompanySnapshot(ticker="RELIANCE", exchange="NSE")
    s.snapshot_date = datetime.now()
    s.price = PriceData(
        cmp=2941.0,
        week52_high=3024.9,
        week52_low=2220.3,
        source="nse_api",
        fetched_at=datetime.now(),
        source_url="https://example.com/price",
    )
    s.market = MarketData(market_cap=1990000, enterprise_value=2180000, shares_outstanding=677.0)
    s.income = IncomeData(revenue_ttm=1000122, ebitda_ttm=181580, pat_ttm=69000, eps_ttm=101.9)
    s.balance_sheet = BalanceSheetData(total_debt=330000, current_assets=350000, current_liabilities=280000)
    s.cash_flow = CashFlowData(cfo_ttm=120000, capex_ttm=-115000, fcf_ttm=5000)
    s.shareholding = ShareholdingData(promoter_holding=50.33, source="bse_filings", fetched_at=datetime.now())
    return s


def test_validator_fails_when_critical_metrics_missing():
    s = _make_snapshot()
    s.income.pat_ttm = None

    with pytest.raises(DataQualityError) as exc:
        DataValidator().validate(s)

    issues = exc.value.issues
    assert any(i.field == "income.pat_ttm" for i in issues)


def test_renderer_includes_field_coverage_section():
    s = _make_snapshot()
    s.shareholding.promoter_holding = None

    md = ReportRenderer().render_markdown(snapshot=s)

    assert "## Field Coverage" in md
    assert "| Promoter Holding | Unavailable |" in md
    assert "| CMP | Present |" in md
