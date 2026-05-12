"""
tests/test_tickertape_plugin.py
Tests for TickertapePlugin — shareholding raises NotImplementedError, 
_normalise_financials maps fields correctly.

No live network calls.
"""

import sys
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.tickertape import TickertapePlugin


@pytest.fixture
def plugin():
    return TickertapePlugin()


# ── shareholding raises NotImplementedError ────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_shareholding_raises_not_implemented(plugin):
    """Tickertape does not support shareholding — must raise NotImplementedError."""
    with pytest.raises(NotImplementedError) as exc_info:
        await plugin.fetch_shareholding("INFY")
    assert "shareholding" in str(exc_info.value).lower() or "bse" in str(exc_info.value).lower()


# ── _normalise_financials ──────────────────────────────────────────────────────

def test_normalise_financials_maps_revenue(plugin):
    """_normalise_financials must map netSales to revenue_ttm."""
    raw = {
        "income": {"netSales": 153670, "pat": 26248, "ebitda": 40100, "eps": 63.08},
        "balance": {"totalAssets": 119400, "equity": 68900, "totalDebt": 3200},
    }
    result = plugin._normalise_financials(raw)
    assert result.get("revenue_ttm") == 153670
    assert result.get("pat_ttm") == 26248
    assert result.get("total_assets") == 119400


def test_normalise_financials_handles_empty(plugin):
    """_normalise_financials must not crash on empty input."""
    result = plugin._normalise_financials({})
    # All values should be None, no exception raised
    assert isinstance(result, dict)
    assert result.get("revenue_ttm") is None


# ── health_check (mocked) ──────────────────────────────────────────────────────

def test_health_check_returns_bool(plugin):
    """health_check must return a bool regardless of network state."""
    with patch("requests.head") as mock_head:
        mock_head.return_value = MagicMock(status_code=200)
        result = plugin.health_check()
    assert isinstance(result, bool)
