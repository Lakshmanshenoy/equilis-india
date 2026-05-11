# Data Validation & Capturing Strategy

## Overview

This guide documents how to systematically capture financial data, validate its accuracy, and identify gaps before conducting equity analysis. Proper data validation prevents misleading analysis and ensures professional-grade research.

---

## I. Data Source Hierarchy

### Tier 1 Sources (Use First)
**Official, audited, statutory disclosure**

| Source | Type | Validation | Reliability |
|--------|------|-----------|-------------|
| **BSE/NSE Filings (PDF)** | Statutory submission | Signed by auditors & company secretary | ★★★★★ (Highest) |
| **Annual Reports** | Management disclosure | Auditor report attached | ★★★★★ |
| **Concall Transcripts** | Management guidance | Official, timestamped | ★★★★☆ |
| **Financial Statements** | GAAP/Ind-AS compliant | Consolidated + Standalone | ★★★★★ |

### Tier 2 Sources (Cross-Verify)
**Curated data, aggregated from official sources**

| Source | Type | Validation | Reliability |
|--------|------|-----------|-------------|
| **Screener.in** | Financial data aggregation | Sourced from BSE/company reports | ★★★★☆ |
| **BSE API** | Real-time stock data | Official exchange data | ★★★★★ |
| **Credit ratings** (CRISIL, ICRA) | Professional assessment | Based on company filings | ★★★★☆ |
| **Institutional reports** (brokers) | Analysis + data | Caveats disclosed | ★★★☆☆ |

### Tier 3 Sources (Supplementary Only)
**Secondary sources, use for context only**

| Source | Type | Validation | Reliability |
|--------|------|-----------|-------------|
| **Media reports** | News coverage | Journalist attribution | ★★★☆☆ |
| **Analyst notes** | Professional opinion | Biases/conflicts may exist | ★★★☆☆ |
| **Management presentations** | Investor decks | Marketing, may lack detail | ★★☆☆☆ |
| **Social media** | User-generated | No verification | ★☆☆☆☆ |

---

## II. Data Capturing Workflow

### Phase 1: Planning (Before Data Capture)

**Checklist:**
- [ ] Company name, ticker, fiscal year defined
- [ ] Analysis period identified (e.g., FY17-FY26)
- [ ] Financial statement types needed (consolidated/standalone)
- [ ] Frequency required (annual/quarterly)
- [ ] KPIs identified (revenue, margins, FCF, etc.)

**Required Data Sets:**

| Data Set | Minimum Period | Granularity | Priority |
|----------|---|---|---|
| **Financial Statements** | 5 years | Annual | **CRITICAL** |
| **Quarterly Results** | 12 quarters | Q-o-Q | **CRITICAL** |
| **Cash Flow** | 5 years | Annual | **CRITICAL** |
| **Segment Performance** | 3 years | Annual | Important |
| **Management Guidance** | 2-3 years | Concall | Important |
| **Peer Data** | Latest year | Industry avg | Supporting |

### Phase 2: Source Identification

```
For [Company Name]:
1. Check Screener.in → Verify data availability
2. Download latest annual report → Extract from Notes
3. Access BSE filing → Cross-check figures
4. Locate latest concall transcript → Management context
5. Identify 3-5 peer comparables → Industry benchmarking
```

### Phase 3: Data Extraction

**Primary Source (Recommended Order):**

1. **Screener.in (Fastest)**
   - 11-year consolidated financials pre-compiled
   - Quarterly breakdowns available
   - Peer comparables included
   - ⚠️ Always verify 2 figures against source documents

2. **BSE PDFs (Most Authoritative)**
   - Official filing documents
   - Auditor certification attached
   - Full disclosure notes
   - ⏱️ Time-consuming but definitive

3. **Company Investor Relations**
   - Latest annual reports
   - Concall transcripts
   - Investor presentations
   - ⚠️ Use for guidance & context, not as primary data

### Phase 4: Cross-Verification (MANDATORY)

**Before using any data point in analysis:**

```
Step 1: Extract from Screener.in
  ↓
Step 2: Verify against BSE PDF (or annual report)
  ↓
Step 3: Check for anomalies (unusual jumps?)
  ↓
Step 4: Contextualize against peer data
  ↓
Step 5: Reconcile with management commentary
  ↓
APPROVED FOR ANALYSIS ✓
```

**Verification Checklist for Each Figure:**

- [ ] Figure exists in 2+ sources?
- [ ] Figures match (or explain minor variance)?
- [ ] Consistency with prior year (no unexplained jumps)?
- [ ] Matches peer benchmarks (outlier detection)?
- [ ] Auditor signed off (consolidated financials)?
- [ ] Currency consistent (all INR)?
- [ ] Accounting standard consistent (Ind-AS)?

---

## III. Gap Detection & Resolution Framework

### Common Data Gaps & Solutions

| Missing Data | Cause | Solution | Impact |
|---|---|---|---|
| **Recent Q results** | Company hasn't announced | Use Screener.in estimates or prior reported quarter | State period in report |
| **Segment breakup** | Not separately disclosed | Extract from annual report notes; use consolidated | Flag limitation; note assumption |
| **Cash flow detail** | Only annual available | Use free cash flow from operating CF minus capex | Acceptable for trend analysis |
| **Guidance** | Management hasn't given | Use 3-year average growth as baseline | State assumption clearly |
| **Peer data** | Small company, limited peers | Use sector median from Screener; note constraint | Flag in competitive analysis |
| **Forward estimates** | Not yet available | Use consensus estimates (if available) or calculate | Mark as estimates, not actuals |

### Decision Rules for Missing Data

| Scenario | Decision | Action |
|---|---|---|
| **Core financials missing (P&L, BS)** | ❌ STOP | Cannot proceed; request company to disclose |
| **Quarterly detail missing** | ⚠️ PROCEED WITH CAUTION | Use annual only; acknowledge lower granularity |
| **Peer comp missing** | ✓ PROCEED | Use sector medians; flag deviation from norms |
| **Forward guidance missing** | ✓ PROCEED | Use historical guidance accuracy; build estimates |
| **Management commentary missing** | ✓ PROCEED | Rely on financial data; increase forensic check |

---

## IV. Data Validation Checklist

**MANDATORY: Complete before starting analysis**

### Financial Data Completeness
- [ ] P&L statement for 5+ years? (Revenue, EBITDA, PAT)
- [ ] Balance sheet for 5+ years? (Assets, liabilities, equity)
- [ ] Cash flow statement for 3+ years? (Operating, investing, financing)
- [ ] Quarterly data for 8-12 quarters? (For growth trend detection)
- [ ] Notes to accounts? (Related parties, contingencies, accounting policies)

### Data Quality & Consistency
- [ ] All years use same accounting standard (Ind-AS)?
- [ ] Currency consistent throughout (all INR)?
- [ ] Consolidation basis same (all consolidated)?
- [ ] No unusual year-on-year jumps unexplained?
- [ ] Segment data reconciles with total?
- [ ] Cash balance matches across statements?

### Audit & Compliance
- [ ] Auditor certificate attached?
- [ ] No "subject to" qualifications in audit opinion?
- [ ] No significant contingent liabilities disclosed?
- [ ] No related party transaction red flags?
- [ ] No off-balance sheet SPVs or financing structures?

### Contextual Data
- [ ] Stock price & market cap verified?
- [ ] Peers identified (3-5 comparables)?
- [ ] Industry/sector growth rate obtained?
- [ ] Management credibility assessed (guidance track record)?
- [ ] Any corporate actions (splits, consolidations) adjusted?

### Gap Documentation
- [ ] All missing data flagged in report?
- [ ] Workarounds explained (e.g., using estimates)?
- [ ] Limitations acknowledged in analysis?
- [ ] Confidence level on each assumption stated?

---

## V. Cross-Verification Examples

### Example 1: Revenue Validation

```
DATA POINT: FY26 Revenue = ₹4,128 Cr

VERIFICATION PROCESS:

Source 1 (Screener.in):
  → Revenue FY26: ₹4,128 Cr ✓

Source 2 (Annual Report PDF):
  → Standalone: ₹3,800 Cr
  → Other income: ₹328 Cr
  → Total: ₹4,128 Cr ✓

Source 3 (BSE Filing):
  → Consolidated Revenue: ₹4,128 Cr ✓

ANOMALY CHECK:
  → FY25 Revenue: ₹2,930 Cr
  → Growth: +41% YoY (investigate if unusual)
  → Concall mention: "EV traction motor ramp-up drove growth" ✓
  
PEER COMPARISON:
  → Sector average revenue growth: +12%
  → This company: +41% (OUTLIER - positive, not concerning)

VERDICT: ✅ APPROVED
  Figure verified across 3 sources
  Growth explained by management
  Context from concall validates spike
  No red flags
```

### Example 2: EBITDA Margin Validation

```
DATA POINT: FY26 EBITDA Margin = 25.2%

VERIFICATION PROCESS:

Source 1 (Screener.in):
  → EBITDA: ₹1,040 Cr
  → Margin: 25.2% ✓

Source 2 (Annual Report):
  → EBITDA calculation:
    - Revenue: ₹4,128 Cr
    - Costs of materials: ₹2,400 Cr
    - Employee costs: ₹400 Cr
    - Other expenses: ₹288 Cr
    - EBITDA: ₹1,040 Cr ✓ (Matches!)

HISTORICAL TREND:
  → FY24 margin: 26.1%
  → FY25 margin: 28.0% (peak)
  → FY26 margin: 25.2% (slight compression)
  → Reason: New capex depreciation, pre-launch costs ✓

PEER COMPARISON:
  → Sector avg margin: 18-20%
  → This company: 25.2% (PREMIUM, justified by tech)

VERDICT: ✅ APPROVED
  Margin verified via multiple methods
  Compression explained (capex stage)
  Above peer average (competitive advantage confirmed)
  Sustainable margin level identified
```

---

## VI. Anomaly Detection & Investigation

### Red Flag Indicators

| Anomaly | Investigation | Action |
|---|---|---|
| **Revenue jumps >30% YoY unexplained** | Check for M&A, new customer, product launch, accounting change | Request clarification from concall/investor relations |
| **Margins declining despite revenue growth** | Price pressure? Cost inflation? Operating deleverage? | Forensic check on cost structure |
| **Cash decrease while profits increase** | Working capital spike? Dividends? Capex surge? | Analyze cash flow statement detail |
| **Debt rising while FCF positive** | Acquisition? Shareholder returns? Strategy change? | Cross-check with management updates |
| **Peer outlier (both ways)** | Sector-specific advantage or disadvantage? | Compare business model, products, markets |

### Investigation Process

```
ANOMALY DETECTED
  ↓
REVIEW SOURCE DOCUMENTS (annual report notes)
  ↓
LISTEN TO CONCALL (management explanation)
  ↓
CHECK PEER DATA (is it sector-wide or company-specific?)
  ↓
ASSESS IMPACT (does it affect valuation/risk?)
  ↓
DOCUMENT FINDING (state assumption/limitation in report)
```

---

## VII. Data Documentation Template

Use this template to document all data sources used:

```
ANALYSIS: [Company Name] - [Report Type]
PERIOD: [FY Start] to [FY End]
DATE: [YYYY-MM-DD]

DATA SOURCES USED:
1. Screener.in
   - Last accessed: [Date]
   - Period covered: [FY17-FY26]
   - Verification: Cross-checked against [Annual Report/BSE filing]
   - Status: ✓ Verified

2. Annual Report [FY26]
   - Company: [Name]
   - Auditor: [Name]
   - Qualification: None
   - Verification: Matches Screener.in figures
   - Status: ✓ Verified

3. Concall Transcript [Q4 FY26]
   - Date: [YYYY-MM-DD]
   - Management guidance mentioned: [Key points]
   - Verification: Context for revenue spike explained
   - Status: ✓ Contextual

GAPS IDENTIFIED:
- None (all critical data available)
- OR
- [Gap description] → [Workaround/Assumption used]

CONFIDENCE LEVEL: [HIGH/MEDIUM/LOW] with reasoning

PREPARED BY: [Your name]
PEER REVIEWED BY: [Reviewer name] — [Date]
```

---

## VIII. Quality Assurance Checklist (Pre-Analysis)

**Before starting any analysis, complete this checklist:**

- [ ] **Data Completeness** — All critical financials obtained (P&L, BS, CF)?
- [ ] **Source Verification** — Each figure verified against 2+ sources?
- [ ] **Anomaly Resolution** — All unusual spikes explained?
- [ ] **Peer Context** — Data benchmarked against 3-5 peers?
- [ ] **Trend Consistency** — 5+ year trends plotted (identify turning points)?
- [ ] **Gap Documentation** — Missing data flagged with workaround?
- [ ] **Accounting Quality** — Audit signed off? No red flags?
- [ ] **Management Credibility** — Guidance accuracy assessed (3+ quarters)?
- [ ] **Currency/Unit Consistency** — All figures in same units (INR, Cr)?
- [ ] **Period Clarity** — Fiscal vs. calendar, standalone vs. consolidated clearly stated?

**If ANY box is unchecked:** Do not proceed. Go back and resolve the gap.

---

## IX. Tools & Automation

### Python Data Extraction Script
```python
# Extract financial data from Screener.in programmatically
# See tools/equity-report-to-pdf.py for the full pipeline

# Usage:
#   python equity-report-to-pdf.py --ticker SONACOMS --years 11
#
# Output:
#   - CSV file with 11-year consolidated financials
#   - Quarterly data for last 12 quarters
#   - Peer comparison table
#   - Automated gap detection report
```

---

## X. When to Flag Analysis as "Unable to Verify"

Mark data as "Unable to verify" if:
- Figure not found in company filings (both consolidated & standalone)
- Contradictory data across 2+ sources with no explanation
- Management commentary conflicts with financial statements
- Data from less reliable sources (Tier 3) without Tier 1 corroboration
- Forward estimates (not actual reported data)
- Discontinued business/one-time items without clear segregation

**Example:**
> "Management mentioned '₹500 Cr new contract win' in concall, but this is not yet reflected in financial statements. Unable to verify until Q-next results are published."

---

**This strategy ensures that every figure used in analysis is defensible, cross-verified, and properly contextualized.**
