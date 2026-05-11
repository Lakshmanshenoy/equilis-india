# Adding a New Data Plugin

This guide walks through creating a new data source plugin for the equilis-india pipeline.
Plugins live in `plugins/` and must implement the `BasePlugin` interface from `plugins/_base.py`.

---

## Step 1 — Understand the interface

All plugins inherit from `BasePlugin` and must implement these abstract methods:

```python
# plugins/_base.py

class BasePlugin(ABC):

    @abstractmethod
    async def fetch_price(self, ticker: str) -> FetchResult:
        """Fetch live price data. Raise NotImplementedError if not supported."""

    @abstractmethod
    async def fetch_financials(self, ticker: str) -> FetchResult:
        """Fetch financial statements. Raise NotImplementedError if not supported."""

    @abstractmethod
    async def fetch_shareholding(self, ticker: str) -> FetchResult:
        """Fetch shareholding pattern. Raise NotImplementedError if not supported."""
```

Optional methods (with default `NotImplementedError` implementations):
- `fetch_concall_transcript(ticker)`
- `fetch_corporate_actions(ticker)`
- `fetch_peers(ticker)`

Return type is always `FetchResult`:

```python
@dataclass
class FetchResult:
    data: dict                # Parsed data — see schema below
    source_url: str           # URL or API endpoint called
    fetched_at: datetime      # UTC timestamp of the fetch
    source_name: str          # Human-readable source name
    is_fallback: bool = False # True if this is a secondary source
```

---

## Step 2 — Create the plugin file

Create `plugins/my_source.py`:

```python
"""
plugins/my_source.py
MySource adapter — [brief description of what this source provides].
"""

from __future__ import annotations
import aiohttp
from datetime import datetime
from plugins._base import BasePlugin, DataUnavailableError, FetchResult


class MySourcePlugin(BasePlugin):
    name = "my_source"
    display_name = "My Source"
    BASE_URL = "https://api.mysource.com/v1"

    def __init__(self, api_key: str = ""):
        self._api_key = api_key
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if not self._session or self._session.closed:
            headers = {"Authorization": f"Bearer {self._api_key}"}
            self._session = aiohttp.ClientSession(headers=headers)
        return self._session

    async def fetch_price(self, ticker: str) -> FetchResult:
        session = await self._get_session()
        url = f"{self.BASE_URL}/quote/{ticker}"
        async with session.get(url) as resp:
            if resp.status != 200:
                raise DataUnavailableError(f"HTTP {resp.status} from {url}")
            raw = await resp.json()

        return self._make_result(
            data={
                "cmp": raw["price"],
                "week52_high": raw["high_52w"],
                "week52_low": raw["low_52w"],
            },
            source_url=url,
            source_name=self.display_name,
        )

    async def fetch_financials(self, ticker: str) -> FetchResult:
        raise NotImplementedError("MySource does not support financials.")

    async def fetch_shareholding(self, ticker: str) -> FetchResult:
        raise NotImplementedError("MySource does not support shareholding.")
```

---

## Step 3 — Register in the source priority list

Edit `core/fetcher.py` to add your plugin to the appropriate priority chain:

```python
# core/fetcher.py

PRICE_SOURCES = ["nse_api", "my_source", "tickertape"]    # add "my_source" here
FINANCIAL_SOURCES = ["screener_in", "tickertape", "bse_filings"]
SHAREHOLDING_SOURCES = ["bse_filings", "screener_in"]
```

The fetcher will try sources in order, falling back to the next on failure.

---

## Step 4 — Instantiate in `build_plugins()`

Edit `core/_cli_runner.py`:

```python
def build_plugins(no_cache: bool = False) -> dict:
    plugins = {}
    # ... existing plugins ...
    try:
        from plugins.my_source import MySourcePlugin
        plugins["my_source"] = MySourcePlugin(api_key=os.environ.get("MY_SOURCE_KEY", ""))
    except Exception:
        pass
    return plugins
```

---

## Step 5 — Export from `plugins/__init__.py`

```python
# plugins/__init__.py
from plugins.my_source import MySourcePlugin
```

---

## Step 6 — Write a test

Add to `tests/test_fetcher.py` or create `tests/test_my_source.py`:

```python
import asyncio
from plugins.my_source import MySourcePlugin

def test_my_source_returns_price():
    # Use aiohttp MockSession or monkeypatch
    ...
```

---

## Data Schema Reference

Your `fetch_price` result `data` dict must include:
```python
{
    "cmp": float,          # Current market price
    "week52_high": float,  # 52-week high
    "week52_low": float,   # 52-week low
}
```

Your `fetch_financials` result `data` dict must include (Screener-style tables):
```python
{
    "tables": {
        "income": {
            "headers": ["Metric", "FY20", "FY21", ...],
            "rows": {
                "Sales": [90000, 100000, ...],
                "Net Profit": [15000, 18000, ...],
                "Operating Profit": [22000, 26000, ...],
            }
        },
        "balance_sheet": { ... },
        "cash_flow": { ... },
    },
    "ttm": {
        "revenue": float,
        "pat": float,
        "ebitda": float,
    }
}
```

---

## Checklist

- [ ] Plugin class inherits `BasePlugin`
- [ ] `name` and `display_name` class attributes set
- [ ] `fetch_price`, `fetch_financials`, `fetch_shareholding` implemented (or raise `NotImplementedError`)
- [ ] Returns `FetchResult` with correct `source_url` and `fetched_at`
- [ ] Added to priority list in `core/fetcher.py`
- [ ] Instantiated in `core/_cli_runner.py` `build_plugins()`
- [ ] Exported from `plugins/__init__.py`
- [ ] Tests written and passing
- [ ] Rate limiting added if required by source
- [ ] Auth credentials via environment variable (never hard-coded)
