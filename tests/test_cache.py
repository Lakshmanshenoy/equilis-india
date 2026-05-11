"""
tests/test_cache.py
Tests for CacheManager — Phase 2 updates (cache_dir param, disabled mode, invalidate_ticker).
"""

import sys
import os
import shutil

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.cache import CacheManager

TEST_CACHE_DIR = "/tmp/equilis_test_cache"


@pytest.fixture(autouse=True)
def clean_test_cache():
    """Remove test cache directory before and after each test."""
    if os.path.exists(TEST_CACHE_DIR):
        shutil.rmtree(TEST_CACHE_DIR)
    yield
    if os.path.exists(TEST_CACHE_DIR):
        shutil.rmtree(TEST_CACHE_DIR)


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_cache_returns_none_on_miss():
    cache = CacheManager(cache_dir=TEST_CACHE_DIR)
    result = cache.get("price", "INFY")
    assert result is None


def test_cache_stores_and_retrieves():
    cache = CacheManager(cache_dir=TEST_CACHE_DIR)
    payload = {"cmp": 1437.5, "ticker": "INFY"}
    cache.set("price", "INFY", payload)
    retrieved = cache.get("price", "INFY")
    if cache._available:
        # diskcache present — should retrieve the stored value
        assert retrieved == payload
    else:
        # diskcache not installed — graceful fallback, returns None
        assert retrieved is None


def test_cache_disabled_always_returns_none():
    """disabled=True must make all gets return None."""
    cache = CacheManager(cache_dir=TEST_CACHE_DIR, disabled=True)
    cache.set("price", "INFY", {"cmp": 1437.5})
    result = cache.get("price", "INFY")
    assert result is None


def test_cache_disabled_flag_attribute():
    cache_on  = CacheManager(cache_dir=TEST_CACHE_DIR, disabled=False)
    cache_off = CacheManager(cache_dir=TEST_CACHE_DIR, disabled=True)
    assert cache_off.disabled is True
    assert cache_on.disabled is False


def test_invalidate_ticker_returns_int():
    cache = CacheManager(cache_dir=TEST_CACHE_DIR)
    count = cache.invalidate_ticker("INFY")
    assert isinstance(count, int)
    assert count >= 0


def test_invalidate_ticker_alias_matches_invalidate():
    """invalidate_ticker(t) should return same result as invalidate(t)."""
    cache1 = CacheManager(cache_dir=TEST_CACHE_DIR)
    cache2 = CacheManager(cache_dir=TEST_CACHE_DIR)
    # Both caches are empty so both should return 0
    r1 = cache1.invalidate_ticker("INFY")
    r2 = cache2.invalidate("INFY")
    assert r1 == r2


def test_invalidate_ticker_clears_all_types():
    """After setting multiple types, invalidate_ticker should clear them."""
    cache = CacheManager(cache_dir=TEST_CACHE_DIR)
    if not cache._available:
        pytest.skip("diskcache not installed — skip disk invalidation test")
    cache.set("price",        "RELIANCE", {"cmp": 2800})
    cache.set("financials",   "RELIANCE", {"revenue": 500000})
    cache.set("shareholding", "RELIANCE", {"promoter": 50.3})
    count = cache.invalidate_ticker("RELIANCE")
    assert count == 3
    assert cache.get("price",      "RELIANCE") is None
    assert cache.get("financials", "RELIANCE") is None


def test_stats_returns_dict():
    cache = CacheManager(cache_dir=TEST_CACHE_DIR)
    stats = cache.stats()
    assert isinstance(stats, dict)
    assert "available" in stats


def test_stats_disabled_has_disabled_key():
    cache = CacheManager(cache_dir=TEST_CACHE_DIR, disabled=True)
    stats = cache.stats()
    assert stats.get("disabled") is True


def test_key_is_uppercase_ticker():
    key = CacheManager._key("price", "infy")
    assert key == "price:INFY"
