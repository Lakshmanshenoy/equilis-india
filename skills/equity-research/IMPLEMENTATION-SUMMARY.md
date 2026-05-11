# ✅ Equity Research Skill — Updated Data Handling & Presentation System

**Status**: PRODUCTION READY (May 10, 2026)

---

## What Was Updated?

### 1. **SKILL.md** — Main skill file
✅ **Added Section**: "Data Capturing & Validation Framework"
- Data source hierarchy (Tier 1/2/3)
- Capturing workflow (5 steps)
- Cross-verification checklist (mandatory)
- Gap detection & resolution table

✅ **Added Section**: "Presentation Layer & Visual Reporting"
- Professional report structure (8 sections)
- Color-coded components (Risk/Valuation/Financial)
- PDF generation & file saving instructions
- Presentation layer component library

✅ **Updated Procedure**: Now includes 8 steps (was 6)
- Added: Data validation step
- Added: PDF generation & file saving step

---

### 2. **New File**: `data-validation-strategy.md`
Comprehensive guide covering:
- Source hierarchy with 15 sources ranked by reliability
- Data capturing workflow (5 phases)
- Cross-verification process with real examples
- Gap detection framework (10+ common gaps with solutions)
- Validation checklist (20-point quality assurance)
- Anomaly detection & investigation
- Data documentation template
- Automation tools & scripts

---

### 3. **New File**: `DATA-HANDLING-STRATEGY.md`
Executive summary covering:
- How data is captured (source hierarchy + workflow)
- Cross-verification examples (revenue, EBITDA margin)
- Gap detection & resolution (what to do if data is missing)
- Presentation layer (color-coded system)
- Automated PDF generation (workflow + file saving)
- Complete end-to-end workflow (4 phases)
- Quality checklist & monitoring metrics

---

## Key Answers to Your Questions

### Q1: How are we handling data capturing?

**Answer**: 4-tier source hierarchy with mandatory cross-verification

```
CAPTURE WORKFLOW:
1. Plan (define period, required data, sources)
2. Extract (from Screener, BSE, company reports)
3. Cross-Verify (≥2 sources must match)
4. Validate (consistency, trends, audit quality)
5. Document (sources, gaps, assumptions)
```

**Primary Sources** (in order):
1. Screener.in (fastest, pre-compiled 11-year data)
2. BSE PDF filings (most authoritative, audited)
3. Company investor relations (for context & guidance)
4. Peer comparables (from Screener or competitor reports)

---

### Q2: Are we cross-checking if we can get ALL required data?

**Answer**: YES — Mandatory validation checklist

Before ANY analysis starts, we verify:
- ✅ **Completeness**: P&L, BS, CF for 5+ years?
- ✅ **Granularity**: Quarterly data for 12 quarters available?
- ✅ **Verification**: Each figure from ≥2 independent sources?
- ✅ **Consistency**: All years same accounting standard (Ind-AS)?
- ✅ **Quality**: Auditor signed off? No red flags?
- ✅ **Outliers**: Anomalies explained by management?
- ✅ **Peers**: Benchmarked against 3-5 comparables?

**If ANY check fails** → Flag the gap with workaround or STOP if critical data missing.

---

### Q3: What measures are we taking if data is missing?

**Answer**: Gap detection & resolution framework

| Missing Data | How to Solve | When to STOP |
|---|---|---|
| **Recent Q results** | Use Screener estimates | Only if >1 year old |
| **Segment breakdown** | Use consolidated + note | Safe to proceed |
| **Guidance** | Use 3-year historical average | State assumption |
| **Peer data** | Use sector median | Flag as proxy |
| **Core financials** | Cannot proceed | **STOP analysis** |

**Process**: Document every workaround in report with confidence level stated.

---

## Implementation: Presentation Layer

### Visual Design System (Integrated)

Pre-built tools in `skills/equity-research/tools/`:

| File | Purpose |
|------|---------|
| `generate-styled-report-pdf.sh` | Best-quality PDF with full embedded CSS |
| `equity-report-to-pdf.sh` | Bash-based PDF generation |
| `equity-report-to-pdf.py` | Python-based PDF generation |
| `README.md` | Usage guide |

**Auto-Applied Colors**:
- 🔴 **Risk sections** → Red (#ff3d00) + light red background
- 🟢 **Valuation sections** → Green (#00c853) + light green background
- 🔵 **Financial sections** → Blue (#2e86ff) + light blue background

---

## Implementation: Automated PDF Saving to Downloads

### Complete Workflow

```
Step 1: Generate Analysis
  └─ Using RCTOF framework + data verified ✓

Step 2: Format Output
  └─ Markdown with ## headers (standard sections)

Step 3: Apply Presentation Layer
  └─ generate-styled-report-pdf.sh embeds full CSS
  └─ Blue gradient headers, color-coded sections
  └─ Styled tables with alternating rows

Step 4: Generate HTML + PDF
  └─ pandoc markdown → HTML
  └─ Chrome headless → PDF (A4, 40px margins)
  └─ Output: $HOME/Downloads/[COMPANY]-Comprehensive-Research-[DATE].pdf

Step 5: Auto-Open
  └─ open command → Opens in Preview
  └─ File ready for sharing/publishing
```

### File Naming Convention

```
[COMPANY_TICKER]-[ANALYSIS_TYPE]-[YYYY-MM-DD].pdf

Examples:
✓ SONACOMS-Comprehensive-Research-2026-05-10.pdf
✓ APCOTEX-Valuation-Analysis-2026-05-10.pdf  
✓ TCS-Sector-Deep-Dive-2026-05-10.pdf
✓ RELIANCE-Short-Thesis-2026-05-10.pdf
```

---

## File Structure (Complete)

```
equilis-india/skills/equity-research/
├── SKILL.md ← Full 1499-line source (comprehensive)
├── DATA-HANDLING-STRATEGY.md ← Executive summary
├── IMPLEMENTATION-SUMMARY.md ← This file
│
├── references/
│   ├── financial-analysis.md
│   ├── annual-report.md
│   ├── concall-analysis.md
│   ├── forensic-accounting.md
│   ├── ipo-drhp.md
│   ├── valuation-prompts.md
│   ├── thesis-building.md
│   ├── technical-analysis.md
│   ├── long-term-indicator.md
│   ├── moat-management.md
│   ├── short-thesis.md
│   ├── earnings-revision-tracker.md
│   ├── sotp-valuation.md
│   ├── sector-analysis.md
│   ├── sector-deep-dives.md
│   ├── data-validation-strategy.md
│   ├── data-sourcing-tools.md
│   ├── prompting-best-practices.md
│   └── pdf-generation.md
│
└── tools/
    ├── README.md
    ├── equity-report-to-pdf.sh
    ├── equity-report-to-pdf.py
    └── generate-styled-report-pdf.sh
```

---

## Quality Assurance Checklist

Before finalizing any report:

### Data Quality
- [ ] All figures verified against ≥2 sources?
- [ ] Anomalies investigated + explained?
- [ ] Peer comparison included for context?
- [ ] Missing data gaps documented?
- [ ] Confidence level stated for each assumption?

### Analysis Quality
- [ ] RCTOF framework applied correctly?
- [ ] Assumptions explicit + justified?
- [ ] Numbers double-checked (DCF math, multiples)?
- [ ] Risk assessment comprehensive?
- [ ] Bull/Base/Bear scenarios realistic?

### Presentation Quality
- [ ] Section headers properly formatted (## headers)?
- [ ] Tables included with data?
- [ ] Executive summary ≤2 pages?
- [ ] Investment view clear + framed correctly?
- [ ] Mandatory SEBI-safe disclaimer present?

### PDF Quality
- [ ] Generated successfully?
- [ ] Saved to Downloads folder?
- [ ] Correct naming convention?
- [ ] Colors/styling rendered properly?
- [ ] All pages readable (no breaks)?

---

## Example: SONACOMS Report Test

✅ **Tested with**: Sona BLW Precision Forgings Ltd (SONACOMS)

**Data Captured**:
- 11-year financials (FY17-FY26) from Screener.in
- Cross-verified against annual reports
- 13 quarters of quarterly data
- Peer comparables (Motherson, Bosch, Bharat Forge)
- Management credibility from concalls

**Analysis Produced**:
- Executive summary (clear investment view: Neutral)
- 11-year financial trends
- DuPont ROE decomposition
- DCF valuation (scenario-based range)
- Bull/Base/Bear scenarios
- Moat analysis (5.5/10)
- Management quality (3.9/5)
- Technical analysis with entry/exit

**PDF Generated**:
- File: `SONACOMS-Comprehensive-Research-2026-05-10.pdf`
- Location: `~/Downloads/`
- Styling: Blue gradient headers, color-coded sections, styled tables
