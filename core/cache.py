"""
core/cache.py
Disk-based cache with per-data-type TTLs.
Cache directory: ~/.equilis/cache  (gitignored at runtime)
"""

import logging
import os
from typing import Any, Optional

CACHE_DIR = os.path.expanduser("~/.equilis/cache")
logger = logging.getLogger(__name__)

# TTLs in seconds
TTL_CONFIG = {
    "price":          60 * 15,            # 15 minutes
    "financials":     60 * 60 * 6,        # 6 hours
    "shareholding":   60 * 60 * 24,       # 24 hours
    "corporate_actions": 60 * 60 * 24,   # 24 hours
    "concall":        60 * 60 * 24 * 7,  # 7 days
    "peers":          60 * 60 * 24,       # 24 hours
    "news":           60 * 60 * 4,        # 4 hours
}


class CacheManager:
    """
    Disk-based key-value cache with TTL per data type.
    Falls back to no-cache behaviour if diskcache is unavailable or disabled=True.

    Parameters
    ----------
    cache_dir : str
        Directory for the diskcache store. Defaults to ~/.equilis/cache.
    disabled : bool
        When True, all operations are no-ops (useful for testing or --no-cache flag).
    """

    def __init__(self, cache_dir: str = CACHE_DIR, disabled: bool = False):
        self.disabled = disabled
        if disabled:
            self._cache    = {}
            self._available = False
            return
        try:
            import diskcache
            os.makedirs(cache_dir, exist_ok=True)
            self._cache    = diskcache.Cache(cache_dir)
            self._available = True
        except ImportError:
            self._cache    = {}
            self._available = False
        except Exception as exc:
            logger.warning("[cache] diskcache unavailable at %s: %s", cache_dir, exc)
            self._cache    = {}
            self._available = False

    def get(self, data_type: str, ticker: str) -> Optional[Any]:
        if self.disabled or not self._available:
            return None
        key = self._key(data_type, ticker)
        return self._cache.get(key)

    def set(self, data_type: str, ticker: str, value: Any) -> None:
        if self.disabled or not self._available:
            return
        key = self._key(data_type, ticker)
        ttl = TTL_CONFIG.get(data_type, 3600)
        self._cache.set(key, value, expire=ttl)

    def invalidate(self, ticker: str) -> int:
        """Force-clear all cached data for a ticker. Returns count deleted."""
        if self.disabled or not self._available:
            return 0
        count = 0
        for data_type in TTL_CONFIG:
            key = self._key(data_type, ticker)
            if self._cache.delete(key):
                count += 1
        return count

    def invalidate_ticker(self, ticker: str) -> int:
        """Alias for invalidate() — returns count cleared."""
        return self.invalidate(ticker)

    def invalidate_type(self, data_type: str, ticker: str) -> None:
        """Invalidate a specific data type for a ticker."""
        if self.disabled or not self._available:
            return
        self._cache.delete(self._key(data_type, ticker))

    def warm_ticker(self, ticker: str, fetcher) -> dict:
        """
        Pre-populate cache for all standard data types for a ticker.
        Runs fetcher.fetch_<type>() synchronously via asyncio.run().
        Returns {data_type: "cached" | "failed: <reason>"}.
        """
        import asyncio

        results: dict = {}
        for data_type in list(TTL_CONFIG.keys()):
            method_name = f"fetch_{data_type}"
            method = getattr(fetcher, method_name, None)
            if method is None:
                results[data_type] = "skipped: method not found"
                continue
            try:
                data = asyncio.run(method(ticker))
                self.set(data_type, ticker, data)
                results[data_type] = "cached"
            except Exception as exc:
                results[data_type] = f"failed: {exc}"

        return results

    def stats(self) -> dict:
        if self.disabled:
            return {"available": False, "disabled": True}
        if not self._available:
            return {"available": False}
        return {
            "available": True,
            "cache_dir": str(getattr(self._cache, "directory", "unknown")),
            "size_bytes": self._cache.volume(),
        }

    @staticmethod
    def _key(data_type: str, ticker: str) -> str:
        return f"{data_type}:{ticker.upper()}"
