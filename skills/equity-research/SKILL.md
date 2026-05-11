---
name: equity-research
description: "Equity research AI prompt library for Indian markets. Use when: analysing financial statements, annual reports, concall transcripts, forensic accounting, IPO/DRHP, valuation (DCF, SOTP, Reverse DCF, Bull/Base/Bear), technical analysis (Dow Theory, Stage Analysis, LTI), sector deep dives, moat analysis, management quality assessment, Walk the Talk checks, DuPont ROE, growth triggers, short thesis/devil's advocate, earnings revision tracking, peer-to-peer sector comparison, or building fundamental investment thesis."
argument-hint: "Type of analysis: financials | concall | annual-report | forensics | valuation | technical | sector | moat | management | ipo | thesis"
---

# Equity Research AI Prompt Library

Refined & Augmented Edition — 2025 (Indian Markets)
Covers: Financial Statements | Annual Reports | Concalls | Forensics | Valuation | Sector Deep Dives | Technicals

## When to Use

Invoke this skill when you need to:
- **Generate comprehensive equity research reports** (15-20 pages, full RCTOF framework) — **DEFAULT OUTPUT**
- Generate **SEBI-safe research notes** and **educational deep dives** instead of advisory stock calls
- Analyse **financial statements**, **annual reports**, or **concall transcripts**
- Run **forensic accounting** or accounting quality checks
- Build **investment theses** or **fundamental checklists**
- Perform **valuations** (DCF, SOTP, Reverse DCF, Bull/Base/Bear scenarios)
- Conduct **technical analysis** (Dow Theory, Stage Analysis, LTI)
- Assess **moat**, **management quality**, or **capital allocation**
- Perform **sector deep dives** or **peer comparisons**
- Build **relative ranking frameworks** across multiple companies without giving portfolio advice
- Add **market intelligence** (macro, sector, and capital flow context) to company analysis
- Support **interactive copilot-style queries** like compare, explain, risk, and sector-view
- Compile prompts into safe, structured outputs with reusable templates
- Track prompt versions, scoring, and performance over time
- Learn from prior analyses using institutional memory and cross-company patterns
- Build **Walk the Talk** execution track records
- Run **short thesis / devil's advocate** stress tests
- **Generate beautiful, publication-ready PDFs** from equity research reports

### Default Output Standard

**Unless otherwise specified, all equity research outputs should be:**
- ✅ **Comprehensive reports** (15-20 pages minimum)
- ✅ **Full RCTOF framework** applied to every section
- ✅ **Multi-dimensional analysis** (financials, valuation, moat, management, technicals, risks, catalysts)
- ✅ **Structured JSON intermediate** (mandatory before presentation rendering)
- ✅ **SEBI-safe framing** (insight-driven, not advice-driven)
- ✅ **Scenario-based valuation ranges**, not explicit stock calls or target-price recommendations
- ✅ **Mandatory disclaimer** stating educational / informational purpose only
- ✅ **Professional PDF** with styled headers, color-coded sections, formatted tables
- ✅ **Saved to Downloads** with naming convention: `[COMPANY]-Comprehensive-Research-[DATE].pdf`

Do NOT produce brief summaries, quick scans, or one-liners unless explicitly requested. Every analysis should be thorough, well-evidenced, publication-ready, and explicitly non-advisory.

### SEBI-Safe Output Rules

The default compliance boundary is:

- Do NOT use `BUY`, `SELL`, `HOLD`, `ACCUMULATE`, `REDUCE`, or equivalent advisory labels
- Do NOT suggest portfolio allocation percentages or action-oriented portfolio construction
- Do NOT use direct advisory language such as `you should buy`, `recommended entry`, or `target price call`
- Use `Investment View: Favorable / Neutral / Unfavorable`
- Use `Risk-Reward: Attractive / Balanced / Skewed to downside`
- Use `Scenario-Based Valuation Range: Bull / Base / Bear`
- Label reports as `Research Note`, `Investment Analysis`, or `Educational Deep Dive`

---

## Universal Prompt Framework: RCTOF

Every prompt in this library follows the **RCTOF** framework. Apply it to every query:

| Element | What to include |
|---------|----------------|
| **R** — Role | "You are a world-class equity analyst..." |
| **C** — Context | Document type, company name, period |
| **T** — Task | Numbered, precise instructions |
| **O** — Output Format | Tables, prose, bullet points, section headers, length |
| **F** — Follow-up Hook | "Ask clarifying questions before starting. I will reward you if done well." |

### Universal Closing Lines (add to every prompt)
```
"If you are uncertain about any fact or figure, state 'Unable to verify' rather than guessing."
"Before you begin, ask me any clarifying questions you need."
"Do NOT provide explicit buy/sell recommendations. Frame all outputs as analytical insights and scenario-based interpretations. Avoid advisory language."
"I will reward you if you do this task well."
```

### Chain-of-Thought Activation (forensics, valuation, scenario analysis)
```
Think step by step before answering. Show your reasoning process,
especially for any quantitative calculations or causal inferences.
```

### Document Injection Line (when uploading a file)
```
I have attached [Annual Report / Concall transcript / DRHP / Credit Rating Report]
for [Company Name] for [FY/Period]. Use this as your primary source.
```

See [Prompting Best Practices](./references/prompting-best-practices.md) for full role definitions and output modifiers.

---

## Prompt Selection Guide

### By Document Type

| Document You Have | Prompt to Use |
|-------------------|---------------|
| P&L + Balance Sheet + Cash Flow | [Financial Statement Analysis](./references/financial-analysis.md) |
| Annual Report PDF | [Annual Report Analysis](./references/annual-report.md) |
| Full concall transcript (portfolio co.) | [Concall Deep Analysis](./references/concall-analysis.md) |
| Full concall transcript (screening) | [Concall Brief Analysis](./references/concall-analysis.md) |
| DRHP / IPO filing | [IPO / DRHP Analysis](./references/ipo-drhp.md) |
| Multiple concalls + annual reports | [Walk the Talk](./references/thesis-building.md) |
| Weekly stock chart | [Technical Analysis](./references/technical-analysis.md) |

### By Analysis Type

| Analysis Needed | Reference File |
|----------------|---------------|
| Forensic accounting / accounting quality | [Forensic Accounting](./references/forensic-accounting.md) |
| DuPont ROE decomposition | [Financial Analysis](./references/financial-analysis.md) |
| Bull/Base/Bear, DCF, SOTP, Reverse DCF | [Valuation Prompts](./references/valuation-prompts.md) |
| Growth triggers checklist | [Thesis Building](./references/thesis-building.md) |
| Full investment thesis one-pager | [Thesis Building](./references/thesis-building.md) |
| Moat analysis (Porter's + economic moat) | [Moat & Management](./references/moat-management.md) |
| Management quality scorecard | [Moat & Management](./references/moat-management.md) |
| Short thesis / bear case stress test | [Short Thesis](./references/short-thesis.md) |
| Earnings revision & guidance tracking | [Earnings Revision Tracker](./references/earnings-revision-tracker.md) |
| SOTP (Sum-of-Parts) for conglomerates | [SOTP Valuation](./references/sotp-valuation.md) |
| Technical analysis with LTI overlays | [Long-Term Indicator](./references/long-term-indicator.md) |
| Peer comparison across sector | [Sector Analysis](./references/sector-analysis.md) |
| Sector deep dive (12 sectors covered) | [Sector Deep Dives](./references/sector-deep-dives.md) |
| Value chain mapping | [Sector Analysis](./references/sector-analysis.md) |
| Beautiful PDF report generation | [PDF Generation & Formatting](./references/pdf-generation.md) |

---

## Comprehensive Report Framework (Default Output)

### Structure: 15-20 Pages, Full RCTOF Framework

All equity research outputs should follow this structure **by default** unless specifically modified. Each section applies full RCTOF (Role-Context-Task-Output-Follow-up).

```
╔════════════════════════════════════════════════════════════════════════════╗
║           COMPREHENSIVE EQUITY RESEARCH REPORT (15-20 Pages)              ║
║                    Default Output Structure                               ║
╚════════════════════════════════════════════════════════════════════════════╝

📄 COVER PAGE (0.5 pages)
├─ Company name, ticker, current price
├─ Report date, analyst, investment-view badge
└─ Scenario valuation range, risk-reward framing, disclaimer marker

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣ EXECUTIVE SUMMARY (1-1.5 pages) ⭐ CRITICAL SECTION
├─ 2-3 sentence investment thesis (why own/avoid this stock)
├─ Key metrics card (Price, P/E, Market Cap, ROE, ROCE, Debt/Equity)
├─ Investment View box (Favorable/Neutral/Unfavorable with confidence score 1-5)
├─ Scenario-based valuation range with 12/24-month context
├─ Asymmetric risk/reward (upside % vs downside %)
├─ Top 3 growth drivers (next 2 years)
└─ Top 3 risks (probability × impact assessment)

2️⃣ COMPANY PROFILE & BUSINESS MODEL (1-1.5 pages)
├─ Company overview (2-3 paragraphs)
├─ Business segments breakdown (% of revenue, profit)
├─ Market position (global/domestic, market share if available)
├─ Competitive positioning (vs. top 3-5 peers)
├─ Key end-markets (customer concentration, industry trends)
├─ Supply chain overview (backward/forward integration)
└─ ESG snapshot (if material)

3️⃣ FINANCIAL ANALYSIS: 11-YEAR HISTORICAL (2-2.5 pages)
├─ Revenue trend (FY-5 to FY+1E) with CAGR, growth acceleration
├─ Profitability trend (EBITDA %, PAT %, FCF %)
├─ Return metrics (ROE, ROCE) vs. WACC (spread analysis)
├─ DuPont ROE decomposition (5-factor: Margin × Leverage × Turnover × etc.)
├─ Capital efficiency (Capex intensity, working capital trends)
├─ Balance sheet evolution (Debt/Equity, Cash conversion, CFO/PAT)
├─ Key assumptions driving FY+1/FY+2 forecasts
└─ Deviation flags (if current guidance differs from trend)

4️⃣ QUARTERLY PERFORMANCE & GROWTH MOMENTUM (1.5 pages)
├─ Last 12-16 quarters of revenue/profit trends
├─ Growth acceleration/deceleration analysis
├─ Margin stability assessment (management execution)
├─ Guidance accuracy track record (beat/miss/in-line count)
├─ Seasonal patterns (if any)
├─ Management commentary from latest concall (key quotes)
└─ Risk flags (slowdowns, margin pressures, volume challenges)

5️⃣ BALANCE SHEET QUALITY & DEBT ASSESSMENT (1 page)
├─ Cash position & net debt (free cash position assessment)
├─ Debt structure (maturity profile, interest rates)
├─ Debt/Equity, Debt/EBITDA ratios vs. peers & rating
├─ Asset quality (receivables turnover, inventory days)
├─ Contingent liabilities & off-balance-sheet risk
├─ Dividend sustainability (FCF payout ratio)
├─ Credit rating history (any recent changes)
└─ Financial flexibility assessment (covenant headroom)

6️⃣ CASH FLOW QUALITY & CAPEX EFFICIENCY (1 page)
├─ Operating cash flow trend (CFO as % of PAT — should be >100%)
├─ Free cash flow available to equity (FCF = CFO - Capex)
├─ Capex intensity (% of sales) and asset turnover
├─ Working capital efficiency (DIO, DSO, DPO trends)
├─ Cash conversion cycle
├─ Capex cycle stage (growth/maintenance/wind-down)
└─ Sustainability of dividends & buybacks

7️⃣ VALUATION ANALYSIS (2-2.5 pages) ⭐ CRITICAL SECTION
├─ DCF Valuation (Base/Bull/Bear case)
│  ├─ WACC calculation (risk-free rate, beta, cost of equity)
│  ├─ Revenue/margin assumptions (justified by growth drivers)
│  ├─ Terminal value assumption (perpetual growth %, multiple check)
│  ├─ Sensitivity grid (WACC vs. growth rate)
│  └─ Fair value range with probability weighting
│
├─ Multiples Analysis
│  ├─ P/E: Current vs. Historical avg vs. Peers vs. Fair value implied
│  ├─ EV/EBITDA: Same comparison set
│  ├─ P/B, P/FCF, P/Sales: Industry context
│  └─ PEG ratio (P/E relative to growth)
│
├─ Reverse DCF Analysis
│  ├─ What growth is market pricing in at current price?
│  ├─ Is it realistic given history & catalysts?
│  └─ Margin of safety assessment
│
└─ Intrinsic Value Convergence
   ├─ DCF fair value vs. multiples-based value (triangulation)
   ├─ Valuation certainty score (1-5)
   └─ Key valuation risks

8️⃣ SCENARIO ANALYSIS: BULL/BASE/BEAR (1-1.5 pages)
├─ Base Case (50% probability)
│  ├─ FY26 revenue & margin assumptions
│  ├─ FY30 terminal year metrics
│  ├─ Scenario valuation range and implied return profile
│  └─ Key assumptions (market growth, competitive wins, execution)
│
├─ Bull Case (25% probability) — What goes right?
│  ├─ Accelerated market penetration or new market entry
│  ├─ Margin upside (leverage, pricing power, cost advantages)
│  ├─ Upper valuation range and implied return profile
│  └─ Triggers for bull case execution
│
└─ Bear Case (25% probability) — What goes wrong?
   ├─ Market share loss or slower growth
   ├─ Margin compression (competition, cost inflation)
    ├─ Lower valuation range and downside profile
   └─ Probability & timing of bear case

9️⃣ GROWTH DRIVERS & CATALYSTS (1.5-2 pages)
├─ Near-term catalysts (0-12 months)
│  ├─ Product launches, market entry, deals
│  ├─ Quarterly beat potential
│  ├─ Guidance raise visibility
│  └─ Timeline & probability for each catalyst
│
├─ Medium-term drivers (1-3 years)
│  ├─ Market adoption curves (product lifecycle stage)
│  ├─ Operational leverage potential
│  ├─ M&A or capacity expansion upside
│  ├─ Pricing power opportunities
│  └─ Duration of growth runway
│
└─ Long-term structural tailwinds (3+ years)
   ├─ TAM expansion (market growth secular trends)
   ├─ Industry consolidation benefits
   ├─ Regulatory changes (tailwinds vs. headwinds)
   └─ Technology/disruption risks (what could kill growth)

🔟 MOAT & COMPETITIVE POSITION (1-1.5 pages)
├─ Economic moat assessment (5/10 score with rationale)
├─ Type of moat (cost advantage, switching costs, brand, IP, network)
├─ ROCE vs. WACC spread (moat strength indicator)
├─ Durability (improving, stable, deteriorating)
├─ Competitive positioning (relative to top 3 players)
├─ Barriers to entry (capex, regulatory, technology)
├─ Threat of substitution & disruption
├─ Porter's Five Forces intensity (each force rated 1-5)
└─ Moat score trajectory (strengthening/weakening trend)

1️⃣1️⃣ MANAGEMENT QUALITY & CAPITAL ALLOCATION (1-1.5 pages)
├─ Management scorecard (5 dimensions, 5-point scale each)
│  ├─ Vision & strategy clarity (do they have a clear direction?)
│  ├─ Execution track record (delivery on guidance/plans)
│  ├─ Capital allocation (ROIC on capex, M&A, dividends)
│  ├─ Shareholder communication (transparency, credibility)
│  └─ Incentive alignment (skin in game, compensation structure)
│
├─ Track record analysis
│  ├─ Guidance accuracy (beat/miss frequency over 3+ years)
│  ├─ Execution of strategic initiatives (projects delivered on time/budget)
│  ├─ M&A track record (if any deals done)
│  └─ Dividend history & buyback history
│
├─ Governance assessment
│  ├─ Board independence (independent director %)
│  ├─ Related party transactions (if any, materiality assessment)
│  ├─ Red flags (regulatory issues, turnover, etc.)
│  └─ Walk the Talk check (do mgmt actions match rhetoric?)
│
└─ Management rating (3/5 to 4.5/5 scale)

1️⃣2️⃣ TECHNICAL ANALYSIS & PRICE ACTION (1 page)
├─ Stage analysis (Stage 1-4: where in cycle is stock?)
├─ Current chart pattern (breakout, topping, consolidation)
├─ Support & resistance levels (identify 3-5 key levels)
├─ Long-term indicators (RSI, MACD, moving averages)
├─ Volume profile (institutional interest vs. retail)
├─ Technical vs. fundamental disconnect (if any)
└─ Entry/exit levels recommended (based on technicals)

1️⃣3️⃣ RISK ASSESSMENT & DOWNSIDE SCENARIOS (1.5-2 pages)
├─ Primary risks (ranked by probability × impact)
│  ├─ Business risk (competition, market slowdown, execution)
│  ├─ Financial risk (leverage, interest rates, refinance risk)
│  ├─ Valuation risk (multiple compression if growth misses)
│  ├─ Macro risk (recession, inflation, rate impact)
│  ├─ Regulatory risk (policy changes, compliance)
│  └─ Governance risk (management changes, fraud risk)
│
├─ Probability × impact matrix (P×I scores for each risk)
├─ Scenario downside quantification (% downside for each risk)
├─ Risk mitigation factors (what reduces probability/impact?)
├─ Key metrics to monitor (early warning indicators)
└─ Review triggers (if downside thesis begins materializing)

1️⃣4️⃣ FINAL INVESTMENT CONTEXT & MONITORING PLAN (1 page)
├─ Investment View (Favorable/Neutral/Unfavorable) with confidence (1-5)
├─ Scenario valuation range
│  ├─ 12-month valuation band
│  ├─ Bull/base/bear case ranges
│  └─ Upside/downside envelope from current price
│
├─ Expected return profile (CAGR % over 2-3 years, scenario-based)
├─ Risk/reward profile (upside % vs. downside %)
├─ Monitoring framework
│  ├─ What existing holders should monitor
│  ├─ What prospective investors should evaluate before acting independently
│  ├─ Key valuation reset triggers
│  └─ Conditions that would improve or weaken the view
│
├─ Monitoring dashboard (key metrics to track)
│  ├─ Quarterly expectations (revenue growth, margin)
│  ├─ Valuation reset triggers
│  ├─ Risk materialization indicators
│  └─ Review frequency (quarterly/bi-annual)
│
└─ Thesis review date (when to revisit analysis)

1️⃣5️⃣ APPENDIX (Optional, 1-2 pages)
├─ Peer comparison matrix (10-15 metrics vs. top 3-5 players)
├─ Detailed financial projections (FY26-30: P&L, BS, CF)
├─ Valuation sensitivity tables (multiple axes)
├─ Glossary of terms & definitions
└─ Data sources & methodology notes
```

### Page Count Breakdown
- **Minimum**: 15 pages (core sections 1-14)
- **Typical**: 17-20 pages (core + detailed tables/charts)
- **Maximum**: 22-25 pages (includes appendix + peer matrix)

### Content Density Guidelines
- **Executive Summary**: Dense, KPIs + visuals + clear thesis
- **Analysis sections**: Balanced prose + tables (not pure numbers)
- **Valuation**: Heavy on tables, sensitivity grids, clearly explained assumptions
- **Catalysts/Risks**: Bullets + probability assessments
- **Final Recommendation**: Clear action plan, not ambiguous
- **Final Section**: Clear investment context, scenario framing, and monitoring plan without advisory language

### Quality Checklist
- ✅ Every section applies RCTOF framework fully
- ✅ Numbers are verified against 2+ sources (Screener + BSE + company)
- ✅ Fair value converges from multiple methods (DCF + multiples + reverse DCF)
- ✅ Bull/Base/Bear cases are probability-weighted, not arbitrary
- ✅ All assumptions are justified (why this growth rate, margin, WACC, etc.)
- ✅ Moat analysis is evidence-based (ROCE vs. WACC spread, competitive actions)
- ✅ Management assessment includes specific track record examples
- ✅ Risks are quantified (% downside impact for each)
- ✅ Technical analysis confirms or explains disconnect with fundamentals
- ✅ Report language is SEBI-safe and explicitly non-advisory
- ✅ Mandatory disclaimer is present in every final output
- ✅ PDF is professionally styled with gradients, color-coded sections, proper tables
- ✅ Report saved to Downloads with naming convention: `[COMPANY]-Comprehensive-Research-[DATE].pdf`

---

## Data Capturing & Validation Framework

### 1. Data Source Hierarchy (Reliability Order)

| Priority | Source | Type | Validation |
|----------|--------|------|-----------|
| **Tier 1 (Highest)** | Company filings (BSE, NSE) | Official statutory documents | Cross-check with auditor reports |
| **Tier 1** | Annual reports & concalls | Management disclosure | Verify against financial statements |
| **Tier 2** | Screener.in, BSE API | Curated financial data | Cross-check multiple sources |
| **Tier 2** | Credit rating reports (CRISIL, ICRA) | Professional assessment | Use for context, not primary data |
| **Tier 3** | Media reports, analyst notes | Secondary sources | Verify before using in analysis |
| **Tier 3** | Social media, unverified blogs | User-generated | **Do NOT use for analysis** |

### 2. Data Capturing Procedure

**Step 1: Identify Required Data Sets**
- Financial statements (P&L, Balance Sheet, Cash Flow) — Last 3-5 years minimum
- Quarterly trends — Last 8-12 quarters for growth validation
- Management commentary — Concalls, shareholder letters
- Industry/peer data — Comparable companies for contextualization
- Technical data — Stock price, volume (for valuation anchoring)

**Step 2: Primary Data Extraction**
```
PREFERRED SOURCES:
1. Screener.in — Fast, consolidated, multi-year data
2. BSE/NSE filings — Official, audited financials
3. Company investor relations — Annual reports, concall transcripts
4. Python extraction script — Automate Screener.in data pull (see tools/)
```

**Step 3: Cross-Check Mechanism (MANDATORY)**
Before using any data point in analysis:
- ✓ Verify against 2+ independent sources (example: Screener + BSE PDF)
- ✓ Check for consistency across years (spot anomalies)
- ✓ Reconcile quarter-to-quarter trends
- ✓ Validate with peer comparables (detect outliers)
- ✓ Cross-reference with management commentary (flag inconsistencies)

**Step 4: Gap Detection & Resolution**

| Missing Data | Action | Fallback |
|--------------|--------|----------|
| **Recent quarterly data** | Check latest investor presentation on company website | Use most recent available; state the period |
| **Segment performance** | Extract from annual report, Note disclosures | Use consolidated if not available; flag in report |
| **Industry benchmarks** | Pull from peer financial statements or CRISIL reports | Use Screener.in sector median; acknowledge limitation |
| **Management guidance** | Listen to latest concall or read shareholder letter | Use historical guidance accuracy; state assumption |
| **Technical/cyclical data** | Chart analysis, volume trends, institutional buying/selling | Use long-term trends; avoid short-term noise |

### 3. Data Validation Checklist (Before Analysis)

- [ ] **Financial Completeness**: Have P&L, BS, CF, and notes for 5+ years?
- [ ] **Quarterly Granularity**: Do we have 12+ quarters for growth trends?
- [ ] **Source Diversification**: Verified against 2+ independent sources?
- [ ] **Anomaly Detection**: Any unusual jumps or reversals? Explained?
- [ ] **Peer Contextualization**: Do metrics align with industry norms?
- [ ] **Currency Consistency**: All figures in same currency (INR)?
- [ ] **Accounting Standards**: Same standard (Ind-AS) for all years?
- [ ] **Related Party Transactions**: Auditor reported? Material?
- [ ] **Contingent Liabilities**: Any disclosed? Impact on valuation?
- [ ] **Management Credibility**: Historical accuracy of guidance?

**If any box is unchecked**: Flag the limitation in the report. Do NOT proceed with analysis if Tier-1 data is missing.

---

## Presentation Layer & Visual Reporting

## SEBI-Safe Compliance Layer (V3)

### Core Principle

> Stay insight-driven, not advice-driven.

### Mandatory Removals

The skill must not output:

- BUY / SELL / HOLD recommendations
- Target prices as explicit calls
- Portfolio allocation suggestions
- Direct advisory wording

### Approved Replacement Language

- `Investment View: Favorable / Neutral / Unfavorable`
- `Risk-Reward: Attractive / Balanced / Skewed to downside`
- `Scenario-Based Valuation Range: Bull / Base / Bear`
- `Uncertainty: High / Medium / Low`

### Mandatory Disclaimer Engine

Every PDF, note, and chat output must include a disclaimer equivalent to:

```text
DISCLAIMER:

This document is for educational and informational purposes only.
It does not constitute investment advice, recommendation, or solicitation to buy or sell any securities.

The author is not a SEBI-registered Research Analyst.

Readers should conduct their own research or consult a registered financial advisor before making investment decisions.
```

### Branding Rules

Always label outputs as:

- `Research Note`
- `Investment Analysis`
- `Educational Deep Dive`

Avoid:

- `Recommendation Report`
- `Stock Advice`

## V4 Portfolio + Ranking Engine (SEBI-Safe)

### Purpose

Add multi-company ranking and portfolio context without issuing portfolio recommendations.

### Core Philosophy

> Rank ideas. Do not recommend actions.

### Architecture

```
Multi-Stock Input
→ Analysis Engine (per stock)
→ Insight Engine
→ Scoring Engine
→ Ranking Engine
→ Portfolio Context Engine
→ Presentation Layer
→ PDF / Dashboard
```

### Required V4 Outputs

- Comparative ranking
- Relative attractiveness scoring
- Top tier / mid tier / lower tier grouping
- Risk vs return scatter or ranking ladder when useful
- Clear note that ranking reflects relative attractiveness, not advice

### Approved Language

- `Ranks highest on combined metrics`
- `Appears relatively more attractive`
- `Scores strongest on risk-reward basis`

Disallowed:

- `Top stocks to buy`
- `Recommended portfolio`
- `Allocate 20% to X`

## V5 Market Intelligence Layer (SEBI-Safe)

### Purpose

Add market-wide context through macro, sector, and capital-flow interpretation.

### Architecture

```
Market Data (Macro + Sector + Flows)
→ Macro Engine
→ Sector Engine
→ Flow Engine
→ Signal Engine
→ Insight Layer
→ Presentation Layer
```

### Required V5 Sections

1. Market Overview
    - Inflation, rates, liquidity, macro stance
2. Sector Trends
    - Winners, laggards, relative strength, sector rotation
3. Capital Flows
    - FII / DII trends, domestic support, foreign selling pressure
4. Key Signals
    - Risk-on / risk-off, industrial cycle strength, defensiveness, rotation
5. Implications
    - Non-advisory implications linking macro → sector → stock

### Approved Language

- `Market conditions suggest...`
- `Sector showing relative strength`
- `Liquidity conditions remain tight`

Avoid:

- `Market will go up`
- `Invest in this sector`

## V6 Copilot Layer (SEBI-Safe, User-Facing Intelligence)

### Core Philosophy

> Help users think better, not outsource decisions.

### Architecture

```
User Input (Chat / Query)
→ Intent Engine
→ Context Engine
→ Memory Engine
→ Orchestration Layer
→ V1-V5 Engines
→ Response Generator
→ UI / Chat Output
```

### Supported Query Types

- Compare X vs Y
- Explain this company
- What are key risks?
- Which sector is strong?
- Why is this stock falling?

### UX Modes

1. Beginner Mode
    - Simpler language, concept explanation
2. Analyst Mode
    - Metrics-heavy, detailed breakdown
3. Investor Mode
    - Insights + context + risk-reward framing without advice

### Response Rules

Every interactive response must:

- Include non-advisory framing
- Prefer `appears relatively stronger` over directive wording
- End with a short note that it is for educational purposes only and not investment advice

## Prompt Compiler + Learning Stack

### Objective

Create a reusable layer that compiles raw prompts into safe, structured prompts, tracks prompt versions, evaluates outputs, and learns from prior work.

### Core Philosophy

> Raw prompt → compiler → safe structured prompt → evaluation → learning loop

### 1. Prompt Compiler System

The compiler must standardize and sanitize every raw prompt before use.

#### Required architecture

```
prompt_compiler/
├── base/
│   ├── safety_block.js
│   ├── style_rules.js
├── transforms/
│   ├── sanitize.js
│   ├── enrich.js
├── templates/
│   ├── financial.js
│   ├── valuation.js
│   ├── risk.js
│   ├── comparison.js
└── compiler.js
```

#### Compiler rules

- Inject a safety block into every compiled prompt
- Sanitize direct advisory language into neutral analytical language
- Enrich prompts with scenario analysis, risks, and assumption clarity
- Prefer structured output instructions over freeform output

### 2. Prompt Versioning + A/B Testing

Treat prompts as versioned assets, not static text.

#### Required architecture

```
prompt_system/
├── versions/
│   ├── v1/
│   ├── v2/
│   ├── v3/
├── registry.js
├── evaluator.js
├── selector.js
└── logger.js
```

#### Versioning rules

- Keep multiple prompt versions in a registry
- Select variants for testing when comparing prompt performance
- Score outputs for structure, clarity, scenario depth, and safety
- Log prompt version performance for later improvement
- Retire weak prompt variants and promote stronger ones

### 3. Evaluation Dashboard

Track prompt quality with a simple scoring and comparison UI.

#### Required architecture

```
evaluation_dashboard/
├── backend/
│   ├── api.js
│   ├── db.js
├── frontend/
│   ├── dashboard.html
│   ├── dashboard.js
│   ├── styles.css
└── evaluator/
    ├── scoring.js
```

#### Dashboard metrics

- Average score per prompt version
- Best performing prompt version
- Score distribution
- Safety violations
- Scenario coverage and assumption clarity

### 4. Meta-Learning System

Extract reusable patterns across companies, sectors, and report types.

#### Required architecture

```
meta_learning/
├── knowledge_base.js
├── pattern_engine.js
├── retrieval_engine.js
└── updater.js
```

#### Learning rules

- Store analytical patterns, not recommendations
- Reuse patterns such as `high ROCE + low growth → valuation risk`
- Retrieve relevant historical patterns for similar contexts
- Update knowledge after each high-quality analysis

### 5. Institutional Memory Layer

Persist company-level analytical history so the system can reason over time.

#### Required architecture

```
institutional_memory/
├── database/
│   ├── companies.json
│   ├── history.json
├── memory_engine.js
├── tracker.js
├── retrieval.js
└── updater.js
```

#### Memory rules

- Store factual and analytical observations only
- Track changes in revenue growth, margins, ROE, valuation, and key insights
- Retrieve prior observations when revisiting a company
- Use memory to describe trend shifts, not to suggest actions

### Integration Flow

```
Raw Prompt
→ Prompt Compiler
→ Prompt Registry / Version Selector
→ LLM Output
→ Evaluator
→ Dashboard Logger
→ Meta-Learning Pattern Store
→ Institutional Memory Update
→ Next Prompt / Next Report
```

### Required Output Behavior

Every output generated through this stack must remain:

- SEBI-safe
- Neutral and educational
- Structured and scenario-based
- Logged for evaluation
- Stored as a learning signal for future analysis

### Operating Standard

Use this stack whenever the task involves:

- Building new prompts
- Comparing prompt variants
- Evaluating report quality
- Reusing patterns across companies
- Tracking longitudinal company memory

## Presentation Layer V2 (Institutional Grade)

### Objective

Upgrade output quality to investor-grade presentation standards by introducing a strict rendering pipeline:

```
Input (Raw Data / Prompts)
→ Analysis Engine
→ Structured JSON (MANDATORY)
→ Presentation Engine V2
→ HTML (Styled + Charts)
→ PDF (Puppeteer/Chrome)
```

### Critical Shift: Structured JSON is Mandatory

All comprehensive report prompts must produce a structured JSON payload before visual rendering.

```json
{
    "sections": [
        {
            "title": "Executive Summary",
            "type": "summary",
            "highlights": [],
            "metrics": [],
            "insights": []
        }
    ]
}
```

If structured JSON is missing, do not proceed to final presentation generation.

### V2 Presentation Engine Structure

```
presentation_v2/
├── mapper.js
├── components.js
├── charts.js
├── renderer.js
├── pdf.js
├── styles.css
├── template.html
└── index.js
```

### Core Components

1. **Mapper (Intelligence Layer)**
     - Converts structured JSON to UI blocks
     - Detects and styles context:
         - risk → red blocks
         - growth → green highlights
         - valuation → visual cards

2. **Components**
     - `summary-card`
     - `metric-grid`
     - `callout`
     - `risk-box`
     - `valuation-bar`
     - `chart-container`

3. **Charts (Mandatory)**
     Use Chart.js to generate at minimum:
     - Revenue trend
     - Margin trend
     - ROCE vs peers
     - Valuation comparison
     - Scenario outcomes

### Design System (V2)

- Primary: `#0B1F3A`
- Accent: `#2E86FF`
- Green: `#00C853`
- Red: `#FF3D00`

Layout rules:
- Max 2-3 visual elements per page
- Use whitespace aggressively
- One key message per section

### Auto-Generated Key Pages

1. Cover page
     - Company name
     - Tagline
     - Rating badge

2. Executive dashboard
     - Price vs fair value (visual)
     - Key metrics grid
     - 3 key insights

3. Financial charts
     - Revenue + EBITDA
     - Margin trend

4. Valuation page
     - P/E vs peers
     - DCF summary

5. Risks page
     - Risk heatmap
     - Probability vs impact

### Integration Skeleton

```js
import { mapData } from "./mapper.js";
import { renderHTML } from "./renderer.js";
import { generatePDF } from "./pdf.js";

export async function generateReport(data) {
    const structured = mapData(data);
    const html = renderHTML(structured);
    const pdf = await generatePDF(html);
    return pdf;
}
```

### Chart Example (Chart.js)

```js
import Chart from "chart.js/auto";

export function createRevenueChart(data) {
    return {
        type: "line",
        data: {
            labels: data.years,
            datasets: [
                {
                    label: "Revenue",
                    data: data.values
                }
            ]
        }
    };
}
```

### Intelligence Layer Enhancements

- Auto-highlight: `overvalued`, `declining growth`
- Auto color-code metrics by risk/opportunity context
- Auto-generate section-level insights from structured data

### CLI Integration

```bash
generate-report input.json output.pdf
```

### V2 Output Standard

Target presentation quality: institutional memo quality with clear hierarchy, chart-led storytelling, and minimal visual clutter.

### 1. Professional Report Structure (Enhanced)

All reports should follow this structure for maximum visual impact:

```
1. Executive Summary (1-2 pages)
    ├─ Investment View (Visual badge: Favorable/Neutral/Unfavorable)
    ├─ Scenario Valuation Range (Color-coded)
   ├─ Key Metrics (4-5 KPI cards in grid)
   └─ Quick verdict (2-3 sentences max)

2. Company Profile & Business Model (1 page)
   ├─ Business overview (prose)
   ├─ Competitive positioning (comparison table)
   └─ Market opportunity (colored cards by segment)

3. Financial Analysis (2-3 pages)
   ├─ Revenue & Profitability Trend (line chart + table)
   ├─ Cash Flow Quality (bar chart + assessment)
   ├─ DuPont ROE Decomposition (5-factor table)
   └─ Balance Sheet Strength (debt ratios, cash position)

4. Valuation (2-3 pages)
   ├─ DCF Model (summary table + sensitivity grid)
   ├─ Multiples Analysis (P/E, EV/EBITDA, P/B comparison)
   ├─ Scenario Analysis (Bull/Base/Bear with probability)
   └─ Reverse DCF (what market is pricing in)

5. Growth Triggers & Catalysts (1 page)
   ├─ Near-term catalysts (0-12 months, timeline table)
   ├─ Medium-term drivers (1-3 years, impact assessment)
   └─ Downside risks (probability x impact matrix)

6. Moat & Competitive Position (1 page)
   ├─ Moat scoring (5/10 scale with evidence)
   ├─ Porter's Five Forces (intensity table)
   └─ Durability assessment (ROCE-WACC spread trend)

7. Management & Capital Allocation (1 page)
   ├─ Scorecard (5 dimensions, 5-point scale)
   ├─ Track record (guidance accuracy, execution)
   └─ Shareholder returns (dividend, buyback history)

8. Investment Context & Monitoring (1 page)
    ├─ Final investment context with clear wording
    ├─ Scenario valuation range with 12/24-month horizon
   ├─ Risk/reward assessment (asymmetric upside/downside)
   └─ Monitoring metrics & review triggers
```

### 2. Color-Coded Components (CSS Integration)

The presentation layer includes pre-built styled components:

| Component Type | Color | Use Case |
|---|---|---|
| **Risk Sections** | Red (#ff3d00) + light red bg | Downside scenarios, risks, concerns |
| **Valuation Sections** | Green (#00c853) + light green bg | DCF, multiples, fair value, targets |
| **Financial Sections** | Blue (#2e86ff) + light blue bg | Statements, margins, ratios, trends |
| **Standard Text** | Dark gray (#2c3e50) | Narrative, explanations, context |
| **Executive Summary** | Gradient (teal→blue) | Key takeaways, ratings |

**Implementation**: Use these color codes in tables, section headers, KPI cards, and visual emphasis.

### 3. PDF Generation & File Saving Instructions

**Final Step in Every Report Generation:**

All reports MUST be converted to beautifully styled PDFs using the professional presentation layer CSS. Follow this exact procedure:

```bash
# Step 1: Convert markdown report to HTML
pandoc "report.md" -t html -o /tmp/report_content.html

# Step 2: Create styled wrapper with embedded CSS
cat > /tmp/styled_report.html << 'STYLE'
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        /* PROFESSIONAL STYLING */
        body {
            font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.7;
            color: #2c3e50;
            background: white;
            padding: 40px;
            font-size: 11pt;
        }
        
        h1 {
            background: linear-gradient(135deg, #1a5f7a 0%, #2c5aa0 100%);
            color: white;
            padding: 20px;
            margin: 40px 0 20px 0;
            border-radius: 8px;
            font-size: 24pt;
            font-weight: 700;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15);
            page-break-before: always;
        }
        
        h1:first-of-type {
            page-break-before: avoid;
        }
        
        h2 {
            background: linear-gradient(90deg, #2c5aa0 0%, #3d6fb8 100%);
            color: white;
            padding: 12px 16px;
            margin: 25px 0 12px 0;
            border-radius: 5px;
            font-size: 14pt;
            font-weight: 600;
            page-break-after: avoid;
        }
        
        h3 {
            color: #1a5f7a;
            padding: 10px 0;
            margin: 16px 0 8px 0;
            border-left: 4px solid #2c5aa0;
            padding-left: 12px;
            font-size: 12pt;
            font-weight: 600;
            page-break-after: avoid;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            font-size: 10pt;
            page-break-inside: avoid;
        }
        
        table th {
            background: linear-gradient(135deg, #1a5f7a 0%, #2c5aa0 100%);
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: 600;
        }
        
        table td {
            padding: 8px 10px;
            border: 1px solid #ddd;
        }
        
        table tr:nth-child(even) {
            background-color: #f0f4f8;
        }
        
        ul, ol {
            margin: 12px 0 12px 25px;
        }
        
        li {
            margin: 6px 0;
            line-height: 1.6;
        }
        
        /* COLOR-CODED SECTIONS */
        .risk-section {
            border-left: 5px solid #e74c3c;
            background: #ffecec;
            padding: 12px 15px;
            margin: 12px 0;
            page-break-inside: avoid;
        }
        
        .valuation-section {
            border-left: 5px solid #27ae60;
            background: #e8f5e9;
            padding: 12px 15px;
            margin: 12px 0;
            page-break-inside: avoid;
        }
        
        .financial-section {
            border-left: 5px solid #2e86ff;
            background: #f0f6ff;
            padding: 12px 15px;
            margin: 12px 0;
            page-break-inside: avoid;
        }
        
        strong {
            color: #1a5f7a;
            font-weight: 700;
        }
        
        em {
            color: #2c5aa0;
            font-style: italic;
        }
        
        blockquote {
            border-left: 4px solid #2c5aa0;
            padding-left: 15px;
            margin-left: 0;
            color: #555;
            font-style: italic;
            margin: 12px 0;
        }
        
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #2c5aa0, transparent);
            margin: 25px 0;
        }
        
        @media print {
            body {
                background: white;
                padding: 40px;
            }
            
            h1, h2 {
                page-break-after: avoid;
            }
            
            table, .risk-section, .valuation-section, .financial-section {
                page-break-inside: avoid;
            }
        }
    </style>
</head>
<body>
STYLE

# Insert the HTML content
cat /tmp/report_content.html >> /tmp/styled_report.html
echo "</body></html>" >> /tmp/styled_report.html

# Step 3: Convert styled HTML to PDF with Chrome headless
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --headless \
    --disable-gpu \
    --print-to-pdf="$HOME/Downloads/[COMPANY_NAME]-Equity-Research-[DATE].pdf" \
    --print-to-pdf-no-header \
    file:///tmp/styled_report.html

# Step 4: Verify and open
open "$HOME/Downloads/[COMPANY_NAME]-Equity-Research-[DATE].pdf"
```

**PDF Specifications:**
- ✓ **Format**: A4 (210 x 297 mm)
- ✓ **Margins**: 40px (all sides)
- ✓ **Page Breaks**: After each major section (automatic)
- ✓ **Background Printing**: Enabled (colors/backgrounds print)
- ✓ **Typography**: Professional sans-serif with hierarchy
- ✓ **File Location**: `$HOME/Downloads/[COMPANY]-[ANALYSIS-TYPE]-[DATE].pdf`
- ✓ **File Naming**: COMPANY-Comprehensive-Research-[YYYY-MM-DD].pdf

**Styling Applied (ALWAYS Embedded):**
- ✅ Blue gradient headers (#1a5f7a → #2c5aa0)
- ✅ Color-coded borders (risk=red, valuation=green, financial=blue)
- ✅ Professional table styling with alternating rows
- ✅ Responsive typography hierarchy (h1-h6, body text)
- ✅ Automatic page breaks at logical points
- ✅ Print-optimized layouts with proper spacing
- ✅ Blockquotes, lists, and emphasis formatting
- ✅ Box shadows and visual depth on headers
- ✅ Light backgrounds for readability

**⚠️ CRITICAL**: This CSS is NOT optional. Every PDF must include embedded styling. If PDF looks plain/ugly, the CSS was not embedded—see Step 2 above.

### 4. Presentation Layer Component Library

Pre-built tools in `skills/equity-research/tools/`:

| File | Purpose | Integration |
|------|---------|---|
| **generate-styled-report-pdf.sh** | Best-quality PDF with full embedded CSS | Recommended method |
| **equity-report-to-pdf.sh** | Bash-based PDF generation | Legacy method |
| **equity-report-to-pdf.py** | Python-based PDF generation | Legacy method |
| **README.md** | Usage guide | Reference |

**Auto-Integration Flow:**
```
Analysis Text → generate-styled-report-pdf.sh
  → pandoc markdown → HTML
  → Styled HTML wrapper with embedded CSS
  → Chrome headless → PDF
  → Downloads folder (save with naming convention)
```

---

## Procedure (Comprehensive Report Default)

**DEFAULT: Always generate comprehensive 15-20 page reports following the framework above unless explicitly told otherwise.**

### Standard Workflow for Comprehensive Reports

1. **Confirm scope** — Ask clarifying questions if needed, but assume comprehensive analysis (15-20 pages, all 15 sections) is default

2. **Identify company & period** — Company name, ticker, fiscal year coverage (recommend 11-year historical + 2-year forecast)

3. **Validate data availability** 
   - ✓ Check Screener.in for P&L, BS, CF, ratios, peers (5 min)
   - ✓ Verify against BSE filings if needed (for audit quality)
   - ✓ Flag any missing data (segments, concalls, guidance)
   - ✓ Confirm 2+ source verification for all key metrics

4. **Load reference templates** 
   - Use [financial-analysis.md](./references/financial-analysis.md) for financials (Section 3-6)
   - Use [valuation-prompts.md](./references/valuation-prompts.md) for DCF/scenarios (Section 7-8)
   - Use [moat-management.md](./references/moat-management.md) for moat/management (Sections 10-11)
   - Use [technical-analysis.md](./references/technical-analysis.md) for technicals (Section 12)
   - Use [short-thesis.md](./references/short-thesis.md) for risks (Section 13)
   - Use [thesis-building.md](./references/thesis-building.md) for catalysts & final verdict (Sections 9, 14)

5. **Apply RCTOF to each section**
   - **R**: You are a world-class equity analyst specializing in [sector]
   - **C**: Analyzing [Company], FY[X]-FY[X+1], consolidated numbers, Indian markets
   - **T**: Analyze using [specific financial/valuation/moat framework]. Output specific: tables, prose, KPIs
    - **O**: Format as [15-20 page markdown report with all sections]. Use numbers, not "approximately". Keep the output explicitly non-advisory and SEBI-safe.
   - **F**: "Ask clarifying questions before starting. I will reward you if executed excellently."

6. **Inject primary documents** 
   - Screener.in page (current price, financials, peers, ratings)
   - Annual report (if detailed segment/cash flow analysis needed)
   - Latest concall transcript (if catalysts/management quality relevant)
   - Any credit rating report (for debt/risk assessment)

7. **Maintain consistent data sourcing**
   - All financial data from Tier-1 sources (Screener + BSE + company)
   - Cross-verify 2+ sources for all key metrics
   - Flag "Unable to verify" if data gaps exist
   - Do NOT guess or infer missing data

8. **Generate comprehensive markdown report** 
   - Follow the 15-section structure exactly (Sections 1-15 in framework above)
   - Each section should be 1-2 pages (aim for 15-20 total)
   - Apply full RCTOF thinking to each section (evidence-based, not surface-level)
   - Use tables for: financials, valuation, scenarios, peer comparisons, risks
   - Use prose for: thesis, catalysts, moat assessment, management quality, technicals
    - Replace directive recommendations with investment view, risk-reward framing, scenario ranges, and monitoring triggers

9. **Generate styled PDF** 
   - Convert markdown → HTML → styled PDF using embedded CSS
   - Command: `skills/equity-research/tools/generate-styled-report-pdf.sh [INPUT.md] ~/Downloads/[COMPANY]-Comprehensive-Research-[DATE].pdf`
   - Verify: PDF should have blue gradient headers, color-coded sections, styled tables
   - Auto-save to: `~/Downloads/[COMPANY]-Comprehensive-Research-[YYYY-MM-DD].pdf`
   - Never skip PDF styling step—ugly PDFs are NOT acceptable
    - Inject mandatory SEBI-safe disclaimer before final render

### Multi-Company / Portfolio Context Workflow

When the user asks to compare multiple companies or rank ideas:

1. Run the standard company analysis per stock
2. Score each company on growth, profitability, valuation, and balance sheet strength
3. Rank companies by combined score
4. Group into top tier / mid tier / lower tier
5. Present the result as relative attractiveness or comparative ranking only
6. Do not suggest allocation weights, portfolio mixes, or top buys

### Market Intelligence Workflow

When the user asks for macro, sector, or market context:

1. Build macro view (inflation, rates, liquidity, stance)
2. Build sector view (growth, momentum, relative strength)
3. Build flow view (FII, DII, trend)
4. Synthesize a signal layer (risk-on, risk-off, sector rotation, macro pressure)
5. Link these signals to company analysis without making directional market calls

### Copilot Workflow

When the user interacts conversationally:

1. Detect intent (`comparison`, `deep_analysis`, `explanation`, `risk_analysis`, `sector_view`, `general`)
2. Build context from single-company, multi-company, sector, or summary inputs
3. Respond in the selected UX mode (`Beginner`, `Analyst`, `Investor`)
4. Keep answers conversational but metrics-grounded
5. Append a brief educational-only, non-investment-advice note

### When to Deviate from Comprehensive Default

**Short analysis OK only if explicitly requested:**
- ✅ "Quick financial check" → 3-5 pages
- ✅ "Concall rapid scan" → 2-3 pages
- ✅ "Earnings surprise analysis" → 1-2 pages
- ✅ "Valuation only" → 4-5 pages

**Otherwise, ALWAYS produce comprehensive 15-20 page report with all sections.**

---

## Quick-Start Template (Copy & Customize)

### Financial Statement Check
```
You are a world-class equity analyst specialising in financial statement analysis.
I have attached [image/PDF] of the financial statements of [COMPANY NAME].
Use consolidated financials. State 'Unable to verify' if uncertain.
[→ See full prompt in financial-analysis.md]
```

### Concall Rapid Scan
```
You are a financial research assistant analysing a concall transcript.
Use only the content of the transcript. Keep each section to 3–5 bullet points.
[→ See full prompt in concall-analysis.md]
```

### Investment Thesis One-Pager
```
You are a fundamental equity research analyst preparing a professional-grade,
forward-looking investment report on [COMPANY NAME].
Use only the latest available data (Q4FY25 or TTM).
[→ See full prompt in thesis-building.md]
```

---

## Sector Coverage (Deep Dives Available)

EMD / Electronics | Jewellery | Financial Exchanges | QSR | Food Delivery |
Data Centres | FMCG | Passenger Vehicles | Footwear | Health Insurance |
Tyres | Cables & Wires | Wealth Management | CDMO/CRO | Hotels | Lab-Grown Diamonds |
**Pharma Ingredients & CDMO**

See [Sector Deep Dives](./references/sector-deep-dives.md) for sector-specific templates.

---

## Reference Files

| File | Contents |
|------|----------|
| [prompting-best-practices.md](./references/prompting-best-practices.md) | RCTOF, role definitions, output modifiers, chain-of-thought |
| [financial-analysis.md](./references/financial-analysis.md) | Financial statements, DuPont ROE |
| [annual-report.md](./references/annual-report.md) | Annual report deep analysis |
| [concall-analysis.md](./references/concall-analysis.md) | Deep + brief concall analysis |
| [forensic-accounting.md](./references/forensic-accounting.md) | Beneish M-Score, CARO, RPTs |
| [ipo-drhp.md](./references/ipo-drhp.md) | IPO / DRHP analysis |
| [valuation-prompts.md](./references/valuation-prompts.md) | DCF, SOTP, Reverse DCF, Bull/Base/Bear |
| [thesis-building.md](./references/thesis-building.md) | Fundamental checklist, growth triggers, Walk the Talk |
| [technical-analysis.md](./references/technical-analysis.md) | Dow Theory, Stage Analysis |
| [long-term-indicator.md](./references/long-term-indicator.md) | LTI (VSTOP, RSI, ADX, CRS) technical analysis |
| [moat-management.md](./references/moat-management.md) | Moat analysis, management quality scorecard |
| [short-thesis.md](./references/short-thesis.md) | Bear case, short thesis / devil's advocate |
| [earnings-revision-tracker.md](./references/earnings-revision-tracker.md) | Earnings revision, guidance tracking |
| [sotp-valuation.md](./references/sotp-valuation.md) | Sum-of-Parts (SOTP) valuation for conglomerates |
| [sector-analysis.md](./references/sector-analysis.md) | P2P comparison, value chain analysis |
| [sector-deep-dives.md](./references/sector-deep-dives.md) | 16 sector-specific templates |
| [data-validation-strategy.md](./references/data-validation-strategy.md) | **Data capturing, source hierarchy, cross-verification, gap resolution** |
| [data-sourcing-tools.md](./references/data-sourcing-tools.md) | Data sourcing: Screener.in, BSE PDFs, Python extraction pipeline |
| [pdf-generation.md](./references/pdf-generation.md) | Professional PDF generation, Chrome headless, styling, automation |
