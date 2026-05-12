"""
Tests for DataNormalizer label matching and flexible Screener row extraction.
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.fetcher import FetchBundle
from core.normalizer import DataNormalizer
from plugins._base import FetchResult


def _result(data: dict, source_name: str = "screener_in") -> FetchResult:
    return FetchResult(
        data=data,
        source_url="https://example.com",
        fetched_at=datetime.now(),
        source_name=source_name,
        is_fallback=False,
    )


def test_normalizer_handles_alternate_screener_row_labels():
    tables = {
        "income": {
            "rows": {
                "Revenue from Operations": ["100", "110", "120", "130", "140"],
                "Profit after tax": ["10", "11", "12", "13", "14"],
                "EBITDA": ["20", "21", "22", "23", "24"],
                "EPS": ["5", "5.2", "5.4", "5.6", "5.8"],
            }
        },
        "balance_sheet": {
            "rows": {
                "Total Assets": ["500"],
                "Share Capital": ["70"],
                "Debt": ["90"],
                "Current Assets": ["150"],
                "Current Liabilities": ["100"],
                "Inventory": ["20"],
                "Receivables": ["25"],
                "Cash and Cash Equivalents": ["30"],
            }
        },
        "cash_flow": {
            "rows": {
                "Cash from Operating Activity": ["60", "65", "70", "75", "80"],
                "CAPEX": ["-20"],
            }
        },
    }

    bundle = FetchBundle(
        ticker="ALT",
        financials=_result({"tables": tables, "ttm": {}}),
    )

    snapshot = DataNormalizer().normalise(bundle, ticker="ALT")

    assert snapshot.income.revenue_ttm == 140.0
    assert snapshot.income.pat_ttm == 14.0
    assert snapshot.income.ebitda_ttm == 24.0
    assert snapshot.income.eps_ttm == 5.8
    assert snapshot.balance_sheet.total_debt == 90.0
    assert snapshot.cash_flow.cfo_ttm == 80.0
