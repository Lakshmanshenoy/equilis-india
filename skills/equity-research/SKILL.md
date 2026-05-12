---
name: equilis-india-equity-research
description: |
  Use when asked to research, analyse, or summarise an Indian listed company (NSE or BSE).
  Covers fundamental ratio analysis, forensic accounting checks, sector and macro overlay,
  technical context, and peer comparison. Always cites source and fetch date for every figure.
  Never issues buy/sell/hold recommendations — scenario-based analysis only.
  Trigger phrases: "research <ticker>", "analyse <company>", "fundamentals of <stock>",
  "forensic check on <company>", "peer comparison for <sector>", "concall summary for <ticker>".
argument-hint: "Type of analysis: financials | concall | annual-report | forensics | valuation | technical | sector | moat | management | ipo | thesis | peers | scenario | macro"
version: "2.2"
pipeline: "core/pipeline.py"
cli: "cli/index.js"
---

# Equilis India — Equity Research Skill (v2.2)

## Overview
This skill turns the agent into a structured Indian equity researcher backed by the
Equilis India v2 async pipeline. It produces institutional-quality scenario analysis
grounded in live-fetched data, with every figure cited with its source and fetch
timestamp, and every output stamped with the SEBI-compliant research disclaimer.

**Architecture:** `cli/index.js` (CLI) → `core/_cli_runner.py` → `core/pipeline.py`
(fetch → validate → normalise → analyse → scenarios → render)

## When to use this skill
- User asks for analysis of any NSE- or BSE-listed company
- User asks for a sector overview, macro overlay, or peer comparison
- User asks for a forensic accounting check or red-flag scan
- User asks to parse or summarise an earnings concall transcript
- User asks for a scenario model or sensitivity analysis

## When NOT to use this skill
- User asks for a general explanation of how markets work (use general knowledge)
- User asks about non-Indian securities (this skill is India-specific)
- User explicitly asks for a buy/sell recommendation (redirect: explain you provide
  scenario analysis only, not investment advice)

---

## Pipeline Quick Reference

### CLI commands (primary interface)
```bash
# Full fundamental analysis with PDF report
node cli/index.js analyze INFY --output pdf

# Bear/Base/Bull scenario with custom growth rates
node cli/index.js scenario INFY --bear 5 --base 12 --bull 20 --horizon 3

# Peer sector comparison
node cli/index.js compare INFY TCS WIPRO HCL --sector it

# Screener (sector filter)
node cli/index.js screen --sector banking --min-roe 15 --max-pe 15

# Standalone report generation
node cli/index.js report RELIANCE --output pdf
```

### Python direct (for development / Jupyter)
```python
import asyncio
from core.pipeline import AnalysisPipeline, PipelineConfig

pipeline = AnalysisPipeline(plugins={"nse_api": NseApiPlugin(), "screener_in": ScreenerInPlugin()})
result = await pipeline.run(PipelineConfig(ticker="INFY"))
print(result.report_markdown)
```

---

## Workflow — step by step

### Step 1 — Resolve the company
- Confirm NSE symbol, BSE scrip code, ISIN, and full registered name.
- Check F&O eligibility (OI and options data available if yes).
- Market cap category: Large-cap (>₹20,000 Cr), Mid-cap (₹5,000–20,000 Cr),
  Small-cap (<₹5,000 Cr).

### Step 2 — Fetch data via pipeline
Run `node cli/index.js analyze <TICKER>` OR invoke `AnalysisPipeline.run()`.

**Source priority (enforced by `core/fetcher.py`):**
| Data Type     | Primary       | Fallback 1   | Fallback 2   |
| ------------- | ------------- | ------------ | ------------ |
| Live price    | NSE API       | Tickertape   | —            |
| Financials    | Screener.in   | Tickertape   | BSE XBRL     |
| Shareholding  | BSE Filings   | Screener.in  | —            |
| Corp actions  | NSE API       | BSE Filings  | —            |

**IMPORTANT:** Never use Screener.in CMP — it is stale cache. Price always from NSE API.

**Fetch resilience (implemented):**
- TLS handling uses certifi CA roots (`core/http_client.py`) for better cross-machine reliability.
- Optional local debugging override: `EQUILIS_DISABLE_SSL_VERIFY=1`.
- Screener parser uses BeautifulSoup first, with optional Scrapling backfill for DOM drift.
- BSE scrip-code lookup uses BSE API first, then Screener-token fallback if needed.
- Report rendering includes `Source Health Diagnostics` and `Field Coverage` tables so missing fields are explicit.

If any source slice is unavailable, continue with partial output and explicitly surface
source-health diagnostics in the report.

**Fields always fetched:**
- Revenue, EBITDA, PAT (last 5 years + TTM)
- EPS (basic and diluted), DPS
- Total debt, cash, net debt
- Equity share capital, reserves, book value per share
- Operating cash flow, FCF (CFO − CapEx)
- Promoter holding % + pledging % (last 4–8 quarters)
- Current price, 52-week high/low (live fetch only)

### Step 3 — Validate data quality
`core/validator.py` runs automatically in the pipeline. Key checks:
- Completeness: all required sections present
- Critical metrics hard-fail: `price.cmp`, `income.revenue_ttm`, `income.pat_ttm`, `income.ebitda_ttm`
- Freshness: CMP not older than 30 min; shareholding not older than 95 days
- Internal consistency: FCF = CFO − CapEx; EPS = PAT / shares
- Cross-source: flag >5% divergence between Screener and Tickertape on key fields

### Step 4 — Compute ratios and forensic flags
`EquityAnalyzer.compute_all()` computes:
- Profitability: Gross Margin, EBITDA Margin, PAT Margin, ROE, ROA, ROCE
- DuPont: 3-factor decomposition (NP Margin × Asset Turnover × Equity Multiplier)
- Leverage: D/E, D/EBITDA, Interest Coverage, Current Ratio, Quick Ratio
- Valuation: P/E, P/B, EV/EBITDA, EV/Sales, PEG, Dividend Yield
- Efficiency: Receivables Days, Inventory Days, Payables Days, CCC, Asset Turnover
- Cash Flow Quality: CFO/PAT ratio with HIGH/MEDIUM/LOW signal
- Beneish M-Score: `core/beneish.py` (>−1.78 = possible earnings manipulation risk)
- Altman Z-Score: academic reference only; US calibration disclaimer mandatory

See `skills/equity-research/prompts/red_flags.md` for the forensic checklist.

### Step 5 — Build three scenarios
`core/scenarios.earnings_scenarios()` or `node cli/index.js scenario <TICKER>`

**Always three scenarios, never one:**
| Scenario | Default PAT CAGR | Rationale |
| -------- | ---------------- | --------- |
| Bear     | 5%               | Industry headwinds, margin pressure |
| Base     | 12%              | Historical 5Y CAGR continuation |
| Bull     | 20%              | Operating leverage + market share gain |

Present a sensitivity table across PE multiples 15×–35×.
See `skills/equity-research/prompts/scenario_base.md` for full template.

### Step 6 — Sector and macro overlay
See `skills/equity-research/prompts/macro_sensitivity.md` for sector-variable sets.
- RBI rate stance → banking/NBFC/real estate
- INR/USD → IT services (60–70% USD revenue)
- Commodity prices → FMCG, metals, chemicals
- PLI scheme status → manufacturing, electronics, pharma
- Monsoon index → FMCG, agri, 2-wheelers, rural consumption

### Step 7 — Peer comparison
Run `node cli/index.js compare <T1> <T2> <T3> --sector <sector>`
or use `skills/equity-research/prompts/peer_compare.md`.

Build comparison across:
1. Profitability (EBITDA Margin, PAT Margin, ROE, ROCE)
2. Balance sheet quality (D/E, CFO/PAT, Current Ratio)
3. Valuation (P/E, EV/EBITDA, P/B)
4. Shareholding structure

See template: `skills/equity-research/templates/peer_table.md`

### Step 8 — Render report and save
- Report auto-saved to `~/Downloads/equilis-reports/TICKER_YYYYMMDD.md`
- PDF: `node cli/index.js report <TICKER> --output pdf`
- Uses template: `skills/equity-research/templates/company_report.md`
- Compliance disclaimer appended automatically by `core/renderer.py`
- Source failures are included in a `Source Health Diagnostics` section.

---

## Prompt Module Index

| Prompt File                                   | Use For                              |
| --------------------------------------------- | ------------------------------------ |
| `prompts/fundamentals.md`                     | Full financial analysis (7 sections) |
| `prompts/peer_compare.md`                     | Peer-to-peer sector comparison       |
| `prompts/red_flags.md`                        | Forensic accounting red-flag scan    |
| `prompts/scenario_base.md`                    | Bear/Base/Bull scenario analysis     |
| `prompts/macro_sensitivity.md`                | Macro impact analysis                |

---

## Compliance Rules (HARD LIMITS)

1. **Never** use: buy, sell, hold, accumulate, reduce, outperform, underperform.
2. **Never** present a single DCF or scenario output as a price target.
3. **Never** use recalled training-data figures for prices, ratios, or earnings.
4. **Always** cite source and fetch timestamp for every financial figure.
5. **Always** include the disclaimer from `references/compliance-disclaimer.md`.
6. **Always** present Bear/Base/Bull scenarios together — never the base case alone.
7. **Always** state Altman Z-Score disclaimer (US manufacturing calibration, 1968).
8. **Always** state Beneish M-Score disclaimer (probabilistic screen, not allegation).

---

## Data Source Hierarchy

| Priority | Source           | Authority For                     |
| -------- | ---------------- | --------------------------------- |
| 1        | BSE/NSE XBRL     | Shareholding, audited financials  |
| 2        | Screener.in      | 10-year financial history, trends |
| 3        | NSE API          | Live price, corporate actions     |
| 4        | Tickertape       | Fallback for price + financials   |
| 5        | RBI DBIE         | Macro data (rates, credit, INR)   |
| 6        | MoneyControl/ET  | News, concall summaries only      |

See `docs/data-sources.md` for full source list with rate limits and authentication notes.

## Missing Data Policy
- Never silently drop unavailable data fields.
- Report each unavailable fetch category with reason where possible.
- Preserve completed sections and continue scenario analysis with available validated inputs.
- Prefer explicit `N/A` over inferred values unless derivation logic is coded and auditable.
- Always include a `Field Coverage` section marking critical metrics as `Present` or `Unavailable`.

---

## Indian FY Calendar
- FY runs April 1 → March 31
- Label convention: FY24 = April 2023 → March 2024
- TTM = trailing twelve months (most recent four quarters)
- Currency: ₹ Crore throughout (1 Crore = 10 million)
