"""
tests/test_bse_plugin.py
Tests for BseFilingsPlugin — normalise_shareholding, fetch_price, scrip code cache.

No live network calls — all tests use mocked HTTP or in-memory data.
"""

import json
import os
import sys
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from plugins.bse_filings import BseFilingsPlugin

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def load_fixture(name: str) -> dict:
    with open(os.path.join(FIXTURES_DIR, name)) as f:
        return json.load(f)


@pytest.fixture
def bse_plugin():
    return BseFilingsPlugin(bse_code_map={"INFY": "500209", "TCS": "532540"})


# ── Shareholding normalisation ─────────────────────────────────────────────────

def test_normalise_shareholding_extracts_promoter_pledge(bse_plugin):
    """_normalise_shareholding should extract key fields including pledge change."""
    raw = load_fixture("bse_shareholding_infy.json")
    result = bse_plugin._normalise_shareholding(raw, "INFY")

    assert "promoter_holding" in result
    assert "promoter_pledging" in result
    assert "promoter_holding_change_4q" in result
    assert "promoter_pledge_change_4q" in result
    assert "promoter_holding_history" in result
    assert isinstance(result["promoter_holding_history"], list)
    # INFY promoter holding is ~14.8% in the fixture
    assert result["promoter_holding"] is not None
    assert 10.0 < result["promoter_holding"] < 20.0


def test_normalise_shareholding_history_is_list(bse_plugin):
    """History should be returned as a non-empty list of quarter labels."""
    raw = load_fixture("bse_shareholding_infy.json")
    result = bse_plugin._normalise_shareholding(raw, "INFY")
    quarters = result.get("quarters", [])
    assert isinstance(quarters, list)
    assert len(quarters) > 0, "Expected at least one quarter in history"


# ── fetch_price not implemented ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_price_raises_not_implemented(bse_plugin):
    """BSE plugin does not support live price — must raise NotImplementedError."""
    with pytest.raises(NotImplementedError):
        await bse_plugin.fetch_price("INFY")


# ── Scrip code cache ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_get_scrip_code_uses_cache(bse_plugin):
    """If ticker is already in _bse_code_cache, no API call should be made."""
    bse_plugin._bse_code_cache["INFY"] = "500209"
    # Patch _get_json so that if it's called, the test will fail
    bse_plugin._get_json = AsyncMock(side_effect=AssertionError("API should not be called"))
    code = await bse_plugin._get_scrip_code("INFY")
    assert code == "500209"
