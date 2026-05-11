# Data Sourcing: Tools & Workflows for Indian Equity Research

## Overview

This file documents the tools, libraries, and workflows discovered through field research for gathering Indian equity research data — especially from free/limited-access sources like Screener.in, BSE/NSE corporate filings, and SEBI DRHP databases.

---

## Tool Chain

| Task | Tool | Install |
|------|------|---------|
| PDF extraction from URLs | **PyMuPDF** (`pymupdf`) | `pip install pymupdf` |
| HTML scraping (NOT PDFs) | **Scrapling** | `pip install scrapling` |
| SSL bypass (macOS) | Python built-in `ssl` module | Built-in |
| HTTP requests | Python `urllib.request` | Built-in |

### Why not Scrapling for PDFs?

Scrapling is designed for HTML web pages — it will fail on binary files like PDFs. Use `urllib` + `PyMuPDF` for PDFs.

---

## Workflow 1: Screener.in → Investment Thesis

### Step 1: Find the company's Screener URL

Pattern: `https://www.screener.in/company/<TICKER>/`

For Blue Jet Healthcare: `https://www.screener.in/company/BLUEJET/`

Screener provides (free, no login):
- Standalone P&L, Balance Sheet, Cash Flow
- Quarterly results (up to ~13 quarters)
- Ratios (ROCE, ROE, P/E, EV/EBITDA, etc.)
- Shareholding pattern
- Announcements and document links

**Note:** Consolidated financials on Screener are often incomplete (only 2 years shown for recently listed companies). Use **standalone** as primary.

### Step 2: Consolidated view

Pattern: `https://www.screener.in/company/<TICKER>/consolidated/`

Some data is hidden behind Screener login (premium). The free tier still shows ~80% of what you need.

---

## Workflow 2: BSE/NSE Corporate Filings → Concall Transcripts & Annual Reports

### BSE Scrip Page Pattern
```
https://www.bseindia.com/stock-share-price/blue-jet-healthcare-ltd/BLUEJET/544009/
```

### Corporate Filings URL (for transcripts, PPTs, annual reports)

From the BSE scrip page, look in the **Documents** section of Screener for links. Key patterns:

**Concall Transcripts:**
```
https://www.bseindia.com/xml-data/corpfiling/AttachHis/<FILEID>.pdf
```
e.g., Feb 2026 Q3FY26 transcript: `58e8d6ed-127b-49f9-812e-50efac0dfc7f.pdf`

**Investor Presentation PPTs:**
Same URL pattern, `.pdf` suffix — BSE uploads PPTs as PDFs.
e.g., Feb 2026 PPT: `bb8db615-1ee1-4364-b96b-062c4cff8cd5.pdf`

**Annual Reports:**
```
https://www.bseindia.com/xml-data/corpfiling/AttachHis/<FILEID>.pdf
```

### Finding Transcript/PPT Links from Screener

Screener's Documents section lists all available filings with direct links. Copy the link from the transcript row.

---

## Workflow 3: Python PDF Extraction Pipeline

### Installation

```bash
pip install pymupdf
```

### Complete Pipeline Script

```python
import urllib.request
import ssl
import pymupdf  # PyMuPDF

# Step 1: SSL bypass (needed on macOS + Python 3.14 where cert chain may fail)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Step 2: Download PDF
url = 'https://www.bseindia.com/xml-data/corpfiling/AttachHis/<FILEID>.pdf'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
req = urllib.request.Request(url, headers=headers)

with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
    data = resp.read()

# Step 3: Save locally
pdf_path = '/tmp/company_concall.pdf'
with open(pdf_path, 'wb') as f:
    f.write(data)
print(f"Downloaded {len(data)} bytes")

# Step 4: Extract text with PyMuPDF
doc = pymupdf.open(pdf_path)
print(f"Pages: {len(doc)}")

full_text = ""
for page in doc:
    full_text += page.get_text() + "\n"
doc.close()

# Step 5: Save extracted text
txt_path = '/tmp/company_concall.txt'
with open(txt_path, 'w') as f:
    f.write(full_text)

print(f"Extracted {len(full_text)} characters")
```

### Extracting Specific Sections from Transcripts

```python
with open('/tmp/company_concall.txt', 'r') as f:
    text = f.read()

# Find Q&A start
qa_start = text.lower().find('question and answer')

# Find closing remarks
end_phrases = ['thank you all', 'thank you, everyone', 'thank you very much']
end_idx = len(text)
for phrase in end_phrases:
    idx = text.lower().find(phrase, qa_start + 2000)
    if idx > 0:
        end_idx = min(end_idx, idx)

# Extract Q&A section
qa_text = text[qa_start:end_idx+500]

# Print full Q&A
print(qa_text)

# Extract opening management remarks (before Q&A)
opening = text[:qa_start]
print(opening)
```

---

## Workflow 4: SEBI DRHP / IPO Filing

```
https://www.sebi.gov.in/filings/public-issues/oct-2023/blue-jet-healthcare-limited-prospectus_78516.html
```

DRHP links are available on Screener's Documents section and directly from SEBI.

---

## Workflow 5: Additional Data Sources

### Moneycontrol
Pattern: `https://www.moneycontrol.com/india/stockpricequote/<sector>/<company>/<code>`

e.g., Blue Jet: `https://www.moneycontrol.com/india/stockpricequote/pharmaceuticals/bluejethealthcare/BJH01`

**Limitation:** Full financial data is behind paywall (shows "No Data" / locked content). Use Screener as primary.

### NSE Company Search
Pattern: `https://www.nseindia.com/get-quotes/equote?symbol=BLUEJET`

NSE filings page: corporate filings section of the company page.

### Credit Ratings (CARE, CRISIL, ICRA)

Often linked from Screener Documents:
```
https://www.careratings.com/upload/CompanyFiles/PR/202512141208_Blue_Jet_Healthcare_Limited.pdf
```

### Screener AI Insights (Premium)
Some advanced data like global market share, capacity utilization, number of customers — requires Screener premium. The free tier shows "Log in to view" for these fields.

---

## Screener URL Patterns for Quick Access

| View | URL Pattern |
|------|------------|
| Company home | `screener.in/company/<TICKER>/` |
| Consolidated view | `screener.in/company/<TICKER>/consolidated/` |
| Quarterly results | Append `/#quarters` |
| Profit & Loss | Append `/#profit-loss` |
| Balance Sheet | Append `/#balance-sheet` |
| Cash Flow | Append `/#cash-flow` |
| Ratios | Append `/#ratios` |
| Shareholding | Append `/#shareholding` |

---

## Notes & Troubleshooting

### SSL Errors on macOS (Python 3.14+)
```
ssl.SSLCertVerificationError: certificate verify failed
```
**Fix:** Use `ssl.CERT_NONE` context as shown above. This is a macOS Python 3.14 cert chain issue, not a real SSL problem.

### PDF is binary / Scrapling fails
Scrapling is for HTML only. Use `urllib` to download the PDF bytes, then `pymupdf` to extract text. Do NOT try to parse PDFs as HTML.

### Concall Transcript Date vs. Period Mapping
- Q1 FY26 = Apr-Jun 2025 → typically held Jul/Aug 2025
- Q2 FY26 = Jul-Sep 2025 → typically held Oct/Nov 2025
- Q3 FY26 = Oct-Dec 2025 → typically held Jan/Feb 2026
- Q4 FY26 = Jan-Mar 2026 → typically held May 2026

Transcript date in PDF header confirms the period.

### Trading Window Closures
BSE announcements often note trading window closures. Example:
> "Trading window closed from April 1, 2026 until 48 hours after audited FY2025-26 results."

This means FY26 results are pending. Check for this to avoid stale analysis.

### Muddy Waters / Short Seller Meetings
If a short seller (Muddy Waters Capital, Hindenburg, etc.) is mentioned in announcements as having a meeting — always verify no UPSI was disclosed. Blue Jet announced a Muddy Waters meeting in March 2026 with explicit "no UPSI disclosed" caveat.

---

## Blue Jet Healthcare Case Study — Complete Data Stack

This is the complete data sourcing workflow used for the Blue Jet Healthcare thesis:

| Data Needed | Source | URL |
|------------|--------|-----|
| Financials (5yr) | Screener.in standalone | `screener.in/company/BLUEJET/` |
| Quarterly history (13Q) | Screener.in standalone | `screener.in/company/BLUEJET/#quarters` |
| Shareholding | Screener.in | `screener.in/company/BLUEJET/#shareholding` |
| Q3FY26 transcript | BSE corporate filings | `58e8d6ed-127b-49f9-812e-50efac0dfc7f.pdf` |
| Q3FY26 PPT | BSE corporate filings | `bb8db615-1ee1-4364-b96b-062c4cff8cd5.pdf` |
| FY25 Annual Report | BSE corporate filings | `226bdeff-5812-4e8c-b29f-95a86d0b5bf4.pdf` |
| Credit rating | CARE Ratings | Listed on Screener Documents |
| DRHP | SEBI | Linked from Screener Documents |
| Muddy Waters meeting | BSE announcement | Via Screener Announcements |
| Vizag groundbreaking | BSE announcement | Via Screener Announcements |

**Total cost:** ₹0 (all free sources)
**Time to build thesis:** ~45 minutes
**Key insight:** The Q3FY26 concall revealed a materially weaker quarter (-40% YoY) that Screener standalone data alone would not have highlighted — demonstrating why transcript access is critical for thesis quality.
