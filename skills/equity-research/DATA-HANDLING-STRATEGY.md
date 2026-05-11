# Equity Research Skill — Data Handling & Presentation Strategy

**Version**: 2.0 (Enhanced with Data Validation & Presentation Layer)  
**Date**: May 10, 2026  
**Status**: ✅ Production Ready

---

## Executive Summary

Your equity research skill now includes a **complete data capture-to-presentation pipeline**:

1. ✅ **Data Capturing Framework** — 4 tiers of sources, validation procedures
2. ✅ **Cross-Verification Mechanism** — Mandatory 2+ source checks before analysis
3. ✅ **Gap Detection & Resolution** — Protocol for handling missing data
4. ✅ **Presentation Layer Integration** — Professional styling, color-coded components
5. ✅ **Automated PDF Generation** — Production-ready reports saved to Downloads

---

## Part 1: How Data Is Captured

### Source Hierarchy (Trust Order)

```
TIER 1 (Highest Trust) ★★★★★
├─ BSE/NSE Official Filings (PDF)
├─ Audited Annual Reports
├─ Certified Financial Statements
└─ Company Concalls (Official)

TIER 2 (Moderate Trust) ★★★★☆
├─ Screener.in (Aggregated official data)
├─ BSE API (Real-time exchange data)
├─ Credit Ratings (CRISIL, ICRA)
└─ Broker Reports (Professional analysis)

TIER 3 (Supplementary Only) ★★★☆☆
├─ Media Reports (News articles)
├─ Management Presentations (Marketing)
├─ Analyst Notes (Opinion-based)
└─ Social Media (User-generated)
```

**Rule**: Never use only Tier 2/3 sources. Always anchor to Tier 1 + verify with at least 1 other source.

### Capture Workflow

```
Step 1: PLAN
  ├─ Define period (FY17-FY26? FY20-FY26?)
  ├─ List required data (P&L, BS, CF, quarterly, peer data)
  └─ Identify sources (Screener → BSE → Company IR)

Step 2: EXTRACT
  ├─ Pull consolidated financials (5+ years, minimum)
  ├─ Get quarterly details (12 quarters trending)
  ├─ Download annual report notes (segment, contingencies, RPTs)
  └─ Locate latest concall transcript (management context)

Step 3: CROSS-VERIFY (MANDATORY) ✓
  ├─ Screener.in revenue vs. Annual Report revenue → Match?
  ├─ Operating margin vs. Independent calculation → Match?
  ├─ Peer comparables vs. Sector median → Outlier check?
  └─ FY26 commentary in concall → Explains anomalies?

Step 4: VALIDATE
  ├─ Consistency check (same accounting standard all years?)
  ├─ Trend analysis (detect unusual jumps)
  ├─ Reconciliation (segment totals = company total?)
  └─ Audit check (auditor signed off? No red flags?)

Step 5: DOCUMENT
  ├─ List all sources used + dates accessed
  ├─ Flag any missing data + workaround
  ├─ Explain assumptions (forward estimates, peer proxies)
  └─ State confidence level (High/Medium/Low)
```

---

## Part 2: Cross-Verification (Quality Assurance)

### Validation Checklist

**Before ANY analysis starts, verify:**

| Check | What to Do | Example |
|-------|-----------|---------|
| **Source Verification** | Each figure from ≥2 sources | Revenue: Screener ₹4,128 Cr vs. Annual Report ₹4,128 Cr ✓ |
| **Trend Analysis** | Plot 5+ years, detect spikes | FY26 revenue +41% vs. FY25 → Investigate via concall |
| **Peer Comparison** | Compare ratios vs. competitors | EBITDA margin 25.2% vs. sector 18% → Competitive advantage confirmed |
| **Accounting Quality** | Auditor signed off? | Beneish M-Score, RPT intensity, contingent liabilities |
| **Currency/Units** | All INR? Same consolidation basis? | Ensure consolidated financials throughout |
| **Completeness** | P&L, BS, CF available? | At least 5 years; 12 quarters for growth |

### Example Cross-Verification

```
FIGURE TO VERIFY: FY26 EBITDA Margin = 25.2%

Source 1 — Screener.in
  → Shows: EBITDA ₹1,040 Cr / Revenue ₹4,128 Cr = 25.2% ✓

Source 2 — Annual Report
  → P&L shows: Revenue ₹4,128 Cr
  → Operating Profit ₹1,040 Cr (before D&A)
  → D&A: ₹368 Cr
  → EBITDA: ₹1,040 Cr ✓ (Matches!)

Source 3 — Peer Comparison
  → Sector average: 18-20%
  → This company: 25.2%
  → Explanation: Superior technology, higher pricing power ✓

VERDICT: ✅ APPROVED FOR ANALYSIS
  ✓ Verified across 3 sources
  ✓ Consistent with peer advantage
  ✓ No red flags detected
```

---

## Part 3: Gap Detection & Resolution

### If Data Is Missing...

| Missing Data | How to Solve | Confidence Impact |
|---|---|---|
| **Recent Q results (not yet announced)** | Use Screener estimates or prior Q | Medium — flag as estimate |
| **Segment breakdown (not disclosed)** | Use consolidated; note limitation | Medium — affects competitive analysis |
| **Forward guidance (management hasn't given)** | Use 3-year historical growth rate | Medium-Low — state assumption clearly |
| **Peer comparables (small cap)** | Use sector median from Screener | Low — acknowledge outlier risk |
| **Concall transcript (older company)** | Skip; rely on financial data only | Medium — reduces management credibility check |

**Critical Rule**: If **core financials** (P&L, Balance Sheet) are missing → **STOP. Cannot proceed.**

### Documentation Template

When there's a gap, document it:

```
DATA GAP IDENTIFIED:
  → Segment revenue breakdown not separately disclosed

WORKAROUND APPLIED:
  → Used consolidated revenue; noted that Auto Precision segment 
    represents ~65% (per prior year notes)

CONFIDENCE IMPACT:
  → Medium — Segment growth analysis has ±5% margin of error
  
MENTIONED IN REPORT:
  → "Segment breakdown estimated from prior disclosures; 
     actual mix may vary slightly."
```

---

## Part 4: Presentation Layer (Visual Design)

### Color-Coded Component System

Your presentation layer includes professional styling:

| Section Type | Color | Purpose |
|---|---|---|
| 🔴 **Risk Sections** | Red (#ff3d00) + light bg | Downside scenarios, vulnerabilities |
| 🟢 **Valuation Sections** | Green (#00c853) + light bg | DCF, fair value, price targets |
| 🔵 **Financial Sections** | Blue (#2e86ff) + light bg | Statements, ratios, trends |
| ⚪ **Executive Summary** | Gradient teal→blue | Key takeaways, investment view |

### Report Structure (Professional)

```
╔════════════════════════════════════════════╗
║  EXECUTIVE SUMMARY                         ║
║  • Investment view (Favorable/Neutral/     ║
║    Unfavorable)                            ║
║  • Scenario valuation range                ║
║  • 4-5 KPI cards (grid layout)             ║
╚════════════════════════════════════════════╝

╔════════════════════════════════════════════╗
║  COMPANY PROFILE                           ║
║  • Business overview (prose)               ║
║  • Segment breakdown (colored table)       ║
║  • Market opportunity (cards by segment)   ║
╚════════════════════════════════════════════╝

╔════════════════════════════════════════════╗
║  FINANCIAL ANALYSIS (Color: Blue)         ║
║  • 11-year trends (table + chart)          ║
║  • Quarterly performance (bar chart)       ║
║  • DuPont decomposition (5-factor table)   ║
║  • Cash flow quality (assessment)          ║
╚════════════════════════════════════════════╝

╔════════════════════════════════════════════╗
║  VALUATION (Color: Green)                 ║
║  • DCF model (summary + sensitivity)       ║
║  • Multiples comparison (P/E, EV/EBITDA)  ║
║  • Bull/Base/Bear scenarios (probabilities)║
║  • Scenario-based valuation range          ║
╚════════════════════════════════════════════╝

╔════════════════════════════════════════════╗
║  RISKS & CATALYSTS (Color: Red)           ║
║  • Downside scenarios (impact analysis)    ║
║  • Key monitoring metrics                  ║
╚════════════════════════════════════════════╝
```

---

## Part 5: Automated PDF Generation & File Saving

### Final Step: Generate Professional PDF

**Output Location**: `$HOME/Downloads/[COMPANY]-Comprehensive-Research-[DATE].pdf`

```bash
# Automatic workflow:
Analysis Text 
  → Presentation Layer Components (color-coded) 
    → Styled HTML with embedded CSS
      → Chrome Headless
        → Production PDF (A4, 40px margins, color background)
          → Auto-save to Downloads folder
            → Auto-open in Preview
```

### File Naming Convention

```
[COMPANY_NAME]-[ANALYSIS_TYPE]-[YYYY-MM-DD].pdf

Examples:
✓ SONACOMS-Comprehensive-Research-2026-05-10.pdf
✓ APCOTEX-Valuation-Analysis-2026-05-10.pdf
✓ TCS-Concall-Analysis-2026-05-09.pdf
```

### PDF Specifications

- **Format**: A4 (210 x 297 mm)
- **Margins**: 40px all sides
- **Font**: Segoe UI / Helvetica Neue (professional, web-safe)
- **Styling**: Color-coded cards, styled tables, gradient headers
- **Pages**: Auto page breaks at section boundaries
- **Print-Ready**: Yes (background colors included)

---

## Part 6: Complete Workflow (From Data to PDF)

### Phase 1: Planning & Data Capture (30 min)

```
1. Define company, period, analysis type
2. Check Screener.in for data availability
3. Download annual report + concall transcript
4. List peer comparables (3-5 companies)
5. Identify gaps (if any)
```

### Phase 2: Validation & Quality Assurance (20 min)

```
1. Cross-verify Screener vs. Annual Report figures
2. Plot 5-year trends (detect anomalies)
3. Benchmark against peers (outlier check)
4. Review audit report (red flags?)
5. Complete validation checklist ✓
```

### Phase 3: Analysis (Using RCTOF Framework)

```
1. Load relevant reference prompt (financial-analysis.md, valuation-prompts.md, etc.)
2. Inject company data + documents
3. Apply RCTOF (Role-Context-Task-Output-Follow-up)
4. Run analysis (DCF, moat, management, thesis)
5. Generate structured output (prose + tables)
```

### Phase 4: Presentation & PDF Generation (15 min)

```
1. Format analysis with section headers (## headers)
2. Add tables, metrics, KPIs (color-coded)
3. Run PDF generator:
   skills/equity-research/tools/generate-styled-report-pdf.sh \
     input.md ~/Downloads/COMPANY-Research-DATE.pdf
4. Verify PDF renders correctly (blue gradients, colored sections, styled tables)
5. Auto-save to Downloads folder ✓
6. Auto-open in Preview
```

---

## Part 7: Quality Checklist (Before Finalizing)

**Complete before publishing any report:**

### Data Quality
- [ ] All figures verified against ≥2 sources?
- [ ] Trends make sense (5+ year history)?
- [ ] Peer comparisons included (context)?
- [ ] All anomalies investigated + explained?
- [ ] Missing data gaps documented?

### Analysis Quality
- [ ] All sections follow RCTOF framework?
- [ ] Assumptions stated explicitly?
- [ ] Numbers cross-checked (DCF math, multiples)?
- [ ] Bull/Base/Bear probabilities realistic?
- [ ] Risk assessment comprehensive?

### Presentation Quality
- [ ] Color-coded sections properly applied?
- [ ] Tables formatted + styled?
- [ ] Executive summary punchy (≤2 pages)?
- [ ] Investment view clear (Favorable/Neutral/Unfavorable)?
- [ ] Scenario valuation range justified with reasoning?

### PDF Quality
- [ ] PDF generated successfully?
- [ ] File saved to Downloads folder?
- [ ] Correct naming convention?
- [ ] Colors/styling rendered properly?
- [ ] All pages readable (no formatting breaks)?

---

## Part 8: Monitoring Metrics Going Forward

**After analysis is published, monitor these metrics quarterly:**

| Metric | Action | Frequency |
|--------|--------|-----------|
| **Quarterly Revenue Growth** | Track vs. assumption | Every quarter |
| **EBITDA Margin** | Monitor for compression | Every quarter |
| **FCF Generation** | Verify self-funding growth (CFO > Capex) | Every quarter |
| **Stock Price vs. Scenario Range** | Reset range if significant divergence | Semi-annual |
| **Management Guidance Accuracy** | Update Walk the Talk credibility score | Annual |
| **Peer Relative Performance** | Check if competitive position stable | Annual |

---

## Conclusion

Your equity research skill now handles **complete end-to-end workflow**:

✅ **Data Capture** → Multiple verified sources  
✅ **Cross-Verification** → Mandatory 2+ source checks  
✅ **Gap Management** → Protocol for missing data  
✅ **Professional Analysis** → RCTOF framework  
✅ **Beautiful Presentation** → Color-coded, styled components  
✅ **Automated PDF** → Production-ready, auto-saved to Downloads  

**Result**: World-class, publication-ready equity research reports generated consistently.

---

**For Questions**: Refer to `skills/equity-research/references/`

- Data strategy: `data-validation-strategy.md`
- PDF generation: `pdf-generation.md`
- Specific analysis: See relevant reference file (financial-analysis.md, valuation-prompts.md, etc.)
