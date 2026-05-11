"""
core/cache.py
Disk-based cache with per-data-type TTLs.
Cache directory: ~/.equilis/cache  (gitignored at runtime)
"""

import os
import hashlib
from typing import Any, Optional

CACHE_DIR = os.path.expanduser("~/.equilis/cache")

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
    Falls back to no-cache behaviour if diskcache is unavailable.
    """

    def __init__(self):
        try:
            import diskcache
            os.makedirs(CACHE_DIR, exist_ok=True)
            self._cache = diskcache.Cache(CACHE_DIR)
            self._available = True
        except ImportError:
            self._cache = {}
            self._available = False

    def get(self, data_type: str, ticker: str) -> Optional[Any]:
        if not self._available:
            return None
        key = self._key(data_type, ticker)
        return self._cache.get(key)

    def set(self, data_type: str, ticker: str, value: Any) -> None:
        if not self._available:
            return
        key = self._key(data_type, ticker)
        ttl = TTL_CONFIG.get(data_type, 3600)
        self._cache.set(key, value, expire=ttl)

    def invalidate(self, ticker: str) -> int:
        """Force-clear all cached data for a ticker. Returns count deleted."""
        if not self._available:
            return 0
        count = 0
        for data_type in TTL_CONFIG:
            key = self._key(data_type, ticker)
            if self._cache.delete(key):
                count += 1
        return count

    def invalidate_type(self, data_type: str, ticker: str) -> None:
        """Invalidate a specific data type for a ticker."""
        if not self._available:
            return
        self._cache.delete(self._key(data_type, ticker))

    def stats(self) -> dict:
        if not self._available:
            return {"available": False}
        return {
            "available": True,
            "cache_dir": CACHE_DIR,
            "size_bytes": self._cache.volume(),
        }

    @staticmethod
    def _key(data_type: str, ticker: str) -> str:
        return f"{data_type}:{ticker.upper()}"
