# Data Sources Reference

All data fetched by the equilis-india pipeline. **Never use recalled training-data figures.**

---

## 1. NSE India API

**Base URL:** `https://www.nseindia.com/api/`
**Plugin:** `plugins/nse_api.py`
**Authority for:** Live price, 52-week high/low, corporate actions, F&O data

### Endpoints used
| Endpoint                              | Data Provided                       |
| ------------------------------------- | ----------------------------------- |
| `/quote-equity?symbol=<TICKER>`       | CMP, 52W high/low, previous close, volume |
| `/corporate-announcements`            | Dividends, bonus, splits, rights    |
| `/option-chain-equities?symbol=<T>`   | OI, PCR, max pain (F&O stocks only) |

### Authentication
- Requires session cookie (no API key needed)
- Session established by hitting `https://www.nseindia.com` homepage first
- Session TTL: 10 minutes (auto-refreshed in `NseApiPlugin._ensure_session()`)

### Rate limits
- No documented public limit; stay ≤ 2 req/s to avoid 429 errors
- Plugin adds no explicit rate limit — honour NSE's fair-use expectations

### IMPORTANT
**Never use NSE API CMP as the sole source for intraday trading context.** NSE data is
real-time during market hours but may be delayed by 1–3 minutes in high-volume sessions.

---

## 2. Screener.in

**Base URL:** `https://www.screener.in/company/<TICKER>/consolidated/`
**Plugin:** `plugins/screener_in.py`
**Authority for:** 10-year P&L, Balance Sheet, Cash Flow history; peer lists; concall links

### Data parsed
| Section          | Parser method           | Fields                                |
| ---------------- | ----------------------- | ------------------------------------- |
| Income statement | `_parse_financials`     | Revenue, EBITDA, PAT, EPS (10 years)  |
| Balance sheet    | `_parse_financials`     | Assets, debt, equity, cash (10 years) |
| Cash flow        | `_parse_financials`     | CFO, CapEx, FCF (10 years)            |
| TTM data         | `_extract_ttm`          | Latest trailing twelve months         |
| Shareholding     | `_parse_shareholding`   | Promoter, FII, DII, Public (quarterly)|
| Concall links    | `_parse_concalls`       | PDF URLs for transcripts              |
| Peers            | `_parse_peers`          | List of sector peers with key ratios  |

### Rate limits
- Screener enforces rate limiting; plugin adds **3-second delay** between requests
- Never hammer Screener — respect their free-tier service

### CRITICAL WARNING
**Screener.in CMP is stale cache.** Do NOT use `screener_raw["cmp"]` as the current
market price. Use NSE API for live price. `fetch_price()` in `ScreenerInPlugin` raises
`NotImplementedError` intentionally.

---

## 3. BSE India Filings API

**Base URL:** `https://api.bseindia.com/BseIndiaAPI/api/`
**Plugin:** `plugins/bse_filings.py`
**Authority for:** SEBI-mandated shareholding pattern; XBRL financial filings

### Endpoints used
| Endpoint                        | Data Provided                        |
| ------------------------------- | ------------------------------------ |
| `ShareHoldingPatterns/w`        | Quarterly shareholding (SEBI format) |
| `AnnualReport/w`                | Annual report PDF links              |
| `XBRL/w`                        | XBRL financial data                  |

### Authentication
- BSE 6-digit company code required (passed via `bse_code_map` dict at plugin init)
- No API key for public endpoints; headers must include `Referer: https://www.bseindia.com`

### IMPORTANT
Shareholding patterns filed with BSE/NSE are SEBI-mandated and legally authoritative.
Always prefer BSE shareholding over Screener.in shareholding for compliance accuracy.

---

## 4. Tickertape

**Base URL:** `https://api.tickertape.in/`
**Plugin:** `plugins/tickertape.py`
**Authority for:** Fallback for price and financials only; all results marked `is_fallback=True`

### Use case
Used only when NSE API (price) or Screener.in (financials) are unavailable.
Never use Tickertape as primary source.

---

## 5. RBI DBIE Portal

**URL:** `https://dbie.rbi.org.in/`
**Plugin:** None (manual fetch / user-invoked)
**Authority for:** Macro data — repo rate, CRR, SLR, credit growth, FX reserves, INR data

### Key data series
| Series                     | Update frequency | Lag      |
| -------------------------- | ---------------- | -------- |
| Policy repo rate            | Per MPC meeting  | Same day |
| Bank credit growth (YoY)   | Fortnightly      | ~14 days |
| INR/USD reference rate      | Daily            | Same day |
| CPI/WPI inflation           | Monthly          | ~12 days |
| IIP (industrial production) | Monthly          | ~6 weeks |

---

## 6. News Sources (corroborative only)

| Source         | Use for                       | Citation rule          |
| -------------- | ----------------------------- | ---------------------- |
| MoneyControl   | Concall summaries, news       | Corroborate, don't cite alone |
| Economic Times | Sector news, policy updates   | Corroborate, don't cite alone |
| NSE Announcements | Regulatory filings, AGM   | Authoritative — cite directly |
| BSE Notices    | Corporate actions             | Authoritative — cite directly |

---

## Cache TTL Reference

| Data Type         | TTL      | Source of truth   |
| ----------------- | -------- | ----------------- |
| Live price        | 15 min   | NSE API           |
| Financials        | 6 hours  | Screener.in       |
| Shareholding      | 24 hours | BSE Filings       |
| Corporate actions | 24 hours | NSE API           |
| Concall transcripts | 7 days | Screener.in       |
| Peer list         | 24 hours | Screener.in       |
| News              | 4 hours  | Not cached        |

Cache lives at `~/.equilis/cache` (diskcache). Invalidate with `CacheManager.invalidate(ticker)`.
