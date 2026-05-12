"""Tests for ScreenerInPlugin HTML parsing resilience."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.screener_in import ScreenerInPlugin


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _fixture(name: str) -> str:
    with open(os.path.join(FIXTURES_DIR, name), "r", encoding="utf-8") as f:
        return f.read()


def test_parse_financials_handles_th_row_headers_and_alias_labels():
    plugin = ScreenerInPlugin()
    html = _fixture("screener_financials_sample.html")

    parsed = plugin._parse_financials(html, "SAMPLE")

    tables = parsed["tables"]
    assert "income" in tables
    assert "balance_sheet" in tables
    assert "cash_flow" in tables

    income_rows = tables["income"]["rows"]
    assert "Revenue from Operations" in income_rows
    assert income_rows["Revenue from Operations"][-1] == "1350"

    cf_rows = tables["cash_flow"]["rows"]
    assert "Cash from Operating Activity" in cf_rows


def test_extract_ttm_reads_last_ttm_column():
    plugin = ScreenerInPlugin()
    html = _fixture("screener_financials_sample.html")
    parsed = plugin._parse_financials(html, "SAMPLE")

    ttm = parsed.get("ttm", {})
    assert ttm.get("Revenue from Operations") == "1350"
    assert ttm.get("EPS") == "21.0"
