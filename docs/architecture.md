# Architecture Reference

## System Overview

Equilis India is an async equity research pipeline for Indian listed companies.
It fetches live data from NSE, Screener.in, and BSE filings, validates and normalises
it into a typed data model, computes financial ratios, generates Bear/Base/Bull scenarios,
and renders a SEBI-compliant markdown report.

---

## Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│  CLI Layer (Node.js ESM)                                            │
│  cli/index.js  →  cli/commands/{analyze,compare,screen,scenario,   │
│                                 report}.js                          │
│  cli/utils/{spinner,formatter}.js                                   │
└─────────────────┬───────────────────────────────────────────────────┘
                  │ child_process spawn("python3")
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Python CLI Runner                                                  │
│  core/_cli_runner.py  (argparse → pipeline → JSON envelope stdout)  │
└─────────────────┬───────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Pipeline (core/pipeline.py)                                        │
│                                                                     │
│  Stage 1: Fetch      core/fetcher.py                                │
│  Stage 2: Normalise  core/normalizer.py                             │
│  Stage 3: Validate   core/validator.py                              │
│  Stage 4: Analyse    core/analyzer.py                               │
│  Stage 5: Scenarios  core/scenarios.py                              │
│  Stage 6: Render     core/renderer.py                               │
└──────┬──────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Plugin Layer                                                        │
│                                                                      │
│  plugins/nse_api.py      ← live price, corp actions                  │
│  plugins/screener_in.py  ← 10yr financials, shareholding, concalls   │
│  plugins/bse_filings.py  ← SEBI-authoritative shareholding, XBRL     │
│  plugins/tickertape.py   ← fallback price + financials               │
│  plugins/pdf_export.py   ← weasyprint HTML→PDF output                │
│  plugins/_base.py        ← BasePlugin ABC + FetchResult dataclass    │
└──────┬───────────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Cache Layer (core/cache.py)                                         │
│  ~/.equilis/cache  (diskcache — TTL per data type)                   │
│                                                                      │
│  price: 15min  |  financials: 6hr  |  shareholding: 24hr            │
│  corp_actions: 24hr  |  concalls: 7d  |  peers: 24hr                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
Ticker (NSE symbol)
      │
      ▼ core/fetcher.py
DataFetcher.fetch_all(ticker)
  ├── fetch_price()       → PRICE_SOURCES = [nse_api, tickertape]
  ├── fetch_financials()  → FINANCIAL_SOURCES = [screener_in, tickertape, bse_filings]
  ├── fetch_shareholding()→ SHAREHOLDING_SOURCES = [bse_filings, screener_in]
  └── fetch_corp_actions()→ CORPORATE_ACTION_SOURCES = [nse_api, bse_filings]
      │
      ▼  FetchBundle (raw FetchResult objects)
core/normalizer.py
  DataNormalizer.normalise(bundle)
      │
      ▼  CompanySnapshot (typed, ₹ Crore normalised)
core/validator.py
  DataValidator.validate(snapshot)
  → ValidationIssue list (INFO / WARNING / ERROR)
  → Raises DataQualityError on ERROR severity
      │
      ▼  (validated snapshot)
core/analyzer.py
  EquityAnalyzer.compute_all(snapshot)
  → RatioSet (profitability, dupont, leverage, valuation, efficiency, cfq)
  EquityAnalyzer.red_flag_scan(snapshot)
  → list[dict] red flags with severity
      │
      ▼
core/scenarios.py
  earnings_scenarios(snapshot)
  → ScenarioResult (Bear/Base/Bull × PE multiples)
      │
      ▼
core/renderer.py
  ReportRenderer.render_markdown(snapshot, ratios, scenarios, ...)
  → str (markdown report)
  ReportRenderer.save(content, ticker)
  → ~/Downloads/equilis-reports/TICKER_YYYYMMDD.md
```

---

## Key Data Models (`core/models/`)

| Class             | File             | Purpose                                         |
| ----------------- | ---------------- | ----------------------------------------------- |
| `CompanySnapshot` | `company.py`     | Central data contract between pipeline stages   |
| `PriceData`       | `company.py`     | CMP, 52W high/low, source, fetch timestamp      |
| `IncomeData`      | `company.py`     | Revenue, EBITDA, PAT, EPS (TTM + 5Y series)     |
| `BalanceSheetData`| `company.py`     | Assets, debt, equity, working capital           |
| `CashFlowData`    | `company.py`     | CFO, CapEx, FCF (TTM + 5Y series)               |
| `ShareholdingData`| `company.py`     | Promoter %, FII %, DII %, pledging %, history   |
| `FinancialStatement` | `financials.py` | Annual P&L + BS + CF in one struct (FY label) |
| `RatioSet`        | `ratios.py`      | All computed ratios (6 sub-objects)             |
| `ScenarioResult`  | `scenario.py`    | Bear/Base/Bull × PE multiples → per-share values |

---

## Source Priority (enforced by `core/fetcher.py`)

| Data Type          | Primary       | Fallback 1   | Fallback 2   |
| ------------------ | ------------- | ------------ | ------------ |
| Live price         | NSE API       | Tickertape   | —            |
| P&L / BS / CF      | Screener.in   | Tickertape   | BSE XBRL     |
| Shareholding       | BSE Filings   | Screener.in  | —            |
| Corporate actions  | NSE API       | BSE Filings  | —            |

**Never use Screener.in for live price** — it serves cached data.

---

## Output Files

| Output              | Path                                          |
| ------------------- | --------------------------------------------- |
| Markdown report     | `~/Downloads/equilis-reports/TICKER_YYYYMMDD.md` |
| PDF report          | `~/Downloads/equilis-reports/TICKER_YYYYMMDD.pdf` |
| CLI JSON envelope   | stdout (piped from `core/_cli_runner.py`)      |

---

## Technology Stack

| Layer      | Technology      | Version     | Notes                                   |
| ---------- | --------------- | ----------- | --------------------------------------- |
| CLI        | Node.js ESM     | ≥18.0.0     | Commander ^12, ora ^8                   |
| Pipeline   | Python 3        | ≥3.11       | Tested on 3.14                          |
| HTTP       | aiohttp         | ≥3.9        | Async HTTP for all plugin fetches       |
| Cache      | diskcache       | ≥5.6        | Optional; falls back to no-cache        |
| HTML parse | BeautifulSoup4  | ≥4.12       | Screener.in parsing                     |
| PDF export | weasyprint      | ≥61.0       | Primary; fpdf2 as fallback              |
| Testing    | pytest          | ≥8.0        | All 32 tests passing                    |
| Currency   | ₹ Crore         | —           | All values normalised to Crore          |

---

## Design Principles

1. **Validate before use** — every fetch passes through `validator.py` before analysis begins
2. **Cite everything** — every figure in output carries source and fetch timestamp
3. **Scenario, not target** — all valuation outputs show Bear/Base/Bull; no single target price
4. **Compliance by default** — disclaimer auto-injected by `renderer.py`; no buy/sell/hold anywhere
5. **Graceful degradation** — pipeline stages are fault-tolerant; partial data returns partial output
6. **Cache-transparent** — fetcher checks cache before network; normaliser is cache-agnostic

---

## Security Notes

- No API keys are hard-coded. All credentials via environment variables.
- NSE/BSE session cookies are ephemeral and stored in-memory only.
- Cache contains financial data only — no PII, no credentials.
- `core/_cli_runner.py` receives args via `argparse` — no shell injection vectors.
- Output goes only to stdout (JSON) and `~/Downloads/equilis-reports/` (files).

---

## Adding a new plugin

See `docs/adding-a-plugin.md` for the full step-by-step guide.

## Adding a new prompt module

See `docs/prompt-modules.md` for the prompt system reference.
