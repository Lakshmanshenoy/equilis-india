---
name: equilis-india-equity-research
description: |
  Use when asked to research, analyse, or summarise an Indian listed company (NSE or BSE).
  Covers fundamental ratio analysis, forensic accounting checks, sector and macro overlay,
  technical context, and peer comparison. Always cites source and fetch date for every figure.
  Never issues buy/sell/hold recommendations — scenario-based analysis only.
  Trigger phrases: "research <ticker>", "analyse <company>", "fundamentals of <stock>",
  "forensic check on <company>", "peer comparison for <sector>", "concall summary for <ticker>".
argument-hint: "Type of analysis: financials | concall | annual-report | forensics | valuation | technical | sector | moat | management | ipo | thesis"
---

# Equilis India — Equity Research Skill

## Overview
This skill turns the agent into a structured Indian equity researcher. It produces
institutional-quality scenario analysis grounded in verified public data, with every
figure cited and every output stamped with the SEBI-compliant research disclaimer.

## When to use this skill
- User asks for analysis of any NSE- or BSE-listed company
- User asks for a sector overview, macro overlay, or peer comparison
- User asks for a forensic accounting check or red-flag scan
- User asks to parse or summarise an earnings concall transcript
- User asks for a DCF or ratio-based scenario model

## When NOT to use this skill
- User asks for a general explanation of how markets work (use general knowledge)
- User asks about non-Indian securities (this skill is India-specific)
- User explicitly asks for a buy/sell recommendation (redirect: explain you provide scenario
  analysis only, not investment advice)

---

## Workflow — step by step

### Step 1 — Identify the company
- Resolve the ticker: confirm NSE symbol, BSE scrip code, ISIN, and full registered name.
- Check if the stock is in F&O — if yes, note that OI and options data are available.
- Check market cap category: Large-cap (>₹20,000 Cr), Mid-cap (₹5,000–20,000 Cr),
  Small-cap (<₹5,000 Cr). This determines peer set and liquidity context.

### Step 2 — Fetch and validate financials
Run `core/fetch.py --ticker <NSE_SYMBOL>` or manually:
1. Go to Screener.in → search ticker → export 10-year P&L, Balance Sheet, Cash Flow.
2. Cross-check against BSE filing portal for the most recent annual report.
3. Run `core/validate.py` — flag any field where fetched value differs >5% from Screener.

**Fields to always fetch:**
- Revenue, EBITDA, PAT (last 5 years + TTM)
- EPS (basic and diluted), DPS
- Total debt, cash and equivalents, net debt
- Equity share capital, reserves, book value per share
- Operating cash flow, free cash flow (OCF minus capex)
- ROCE, ROE, ROIC (last 5 years)
- Promoter holding % + pledged % (last 8 quarters)
- Current price, 52-week high/low (fetch live — never recall)

### Step 3 — Run the forensic checklist
See `skills/equity-research/modules/forensic-flags.md` for full detail.
Quick checklist:
- [ ] PAT vs OCF divergence: if PAT grows but OCF flat/falling for 3+ years → flag
- [ ] Receivables days trend: rising consistently → flag
- [ ] Inventory days trend: rising consistently in non-seasonal business → flag
- [ ] Debt: sudden large increase not explained by capex → flag
- [ ] Promoter pledging: >20% of holding pledged → flag; rising trend → flag
- [ ] Related-party transactions as % of revenue: >10% → flag
- [ ] Auditor change in last 3 years: note and investigate reason
- [ ] Contingent liabilities: large undisclosed or fast-growing → flag
- [ ] Beneish M-score: run via `core/beneish.py` — score >-1.78 → earnings manipulation risk

### Step 4 — Compute ratios and scenarios
See `skills/equity-research/modules/fundamentals.md` for formulas.

**Valuation scenarios — always three, never one:**
| Scenario | Assumption | Output |
|---|---|---|
| Bear | Revenue growth –50% of mgmt guidance, margin compression 200 bps | Implied value |
| Base | Revenue growth = 5-year CAGR, margins stable | Implied value |
| Bull | Revenue growth = mgmt guidance, margin expansion 100 bps | Implied value |

Present all three. Never present only the base case.

### Step 5 — Sector and macro overlay
See `skills/equity-research/modules/macro-sector.md` for India-specific context.
- Check RBI policy stance and its effect on the sector (especially banks, NBFCs, real estate)
- Check PLI scheme applicability
- Check Budget capex announcements relevant to the sector
- Note FII/DII flow trend for the sector (last 3 months, NSE data)
- Monsoon context for FMCG, agri-inputs, two-wheelers

### Step 6 — Technical context
See `skills/equity-research/modules/technicals.md`.
Even for fundamental research, note:
- Position relative to 50-DMA and 200-DMA
- Delivery percentage vs 30-day average (NSE bhav copy)
- If F&O stock: OI trend, PCR, max pain level
- 52-week high/low context (is it near a breakout or breakdown zone?)

### Step 7 — Peer comparison
See `skills/equity-research/modules/peer-comparison.md`.
- Identify 4–5 closest listed peers by business model (not just sector)
- Build ratio table: P/E, EV/EBITDA, EV/Sales, P/B, ROE, ROCE, Debt/Equity, FCF yield
- Highlight where the subject company trades at premium or discount vs peers
- Note if premium/discount is historically justified

### Step 8 — Output and disclaimer
- Write the report in the format defined in `docs/report-template.md`
- Save to `~/Downloads/equilis-reports/TICKER_YYYYMMDD.md`
- Inject disclaimer from `skills/equity-research/references/compliance-disclaimer.md`
- If PDF requested, run `core/render.py --input <path> --output <path>.pdf`
