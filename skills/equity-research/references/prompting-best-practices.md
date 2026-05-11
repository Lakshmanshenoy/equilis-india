# Prompting Best Practices

## 1.1 The RCTOF Framework

Every strong prompt contains five elements:

- **R — Role**: Define who the AI is (e.g., world-class equity analyst, forensic accounting expert).
- **C — Context**: Specify what documents or data you are providing and any material constraints.
- **T — Task**: Give precise, numbered instructions for what needs to be done.
- **O — Output Format**: Specify format: tables, prose, bullet points, section headers, length.
- **F — Follow-up Hook**: End with a question-invite and a positive reinforcer.

---

## 1.2 Universal Closing Lines (add to every prompt)

```
"If you are uncertain about any fact or figure, state 'Unable to verify' rather than guessing."
"Before you begin, ask me any clarifying questions you need."
"I will reward you if you do this task well."
```

> Removing "I will reward you" reduces output quality noticeably in testing. Keep it.

---

## 1.3 Role Definition Options

Use one of the following, matched to your task:

```
You are a world-class equity analyst at a top-tier institutional fund.
You are a forensic accounting expert specialising in detecting earnings manipulation.
You are a senior fund manager with 20 years of experience in Indian markets.
You are an expert in [SECTOR] in India and track every listed company in this space.
You are a buy-side analyst preparing an investment note for the CIO of a long-only fund.
```

---

## 1.4 Self-Role Definition (for simpler queries)

When you want the AI to calibrate to your knowledge level:

```
"I am a novice in finance — explain this to me as if I am 12 years old."
"I am a CFA with 10 years of equity research experience."
```

---

## 1.5 Output Modifiers

Append these to any prompt to shape the style:

```
"Keep your output PDF-style: crisp section headers, bullet points under each, and a summary table at the end."
"Be heavy on analysis. Avoid filler text. Every sentence must add information."
"Avoid a salesy tone. Keep the analysis neutral and factual."
"Flag any assumption you make explicitly with '[ASSUMED]'."
"For every data point, note the source year and document."
```

---

## 1.6 Chain-of-Thought Activation

Add this when you need deep reasoning (forensics, valuations, scenario analysis):

```
Think step by step before answering. Show your reasoning process,
especially for any quantitative calculations or causal inferences.
```

---

## 1.7 Document Injection Line

Add this line when uploading a file:

```
I have attached [Annual Report / Concall transcript / DRHP / Credit Rating Report]
for [Company Name] for [FY/Period]. Use this as your primary source.
```

---

## 1.8 Data Sourcing for Indian Listed Companies

For a complete investment thesis, combine multiple free sources:

### Primary Data Stack

| Data Needed | Source | Access |
|------------|--------|--------|
| 5-yr financials, quarterly history, ratios | Screener.in | Free — `screener.in/company/<TICKER>/` |
| Concall transcripts (Q3FY26, Q2FY26, etc.) | BSE corporate filings | Free — link from Screener Documents section |
| Investor presentation PPTs | BSE corporate filings | Free — link from Screener Documents section |
| Annual reports | BSE corporate filings | Free |
| Credit ratings | CRISIL/ICRA/CARE | Usually linked from Screener Documents |
| DRHP/IPO filings | SEBI | `sebi.gov.in/filings/public-issues/` |
| Short seller meetings | BSE announcements | Via Screener Announcements |

### Tool for PDF Extraction

**Use PyMuPDF — NOT Scrapling** (Scrapling is for HTML only).

```python
import urllib.request, ssl, pymupdf

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://www.bseindia.com/xml-data/corpfiling/AttachHis/<FILEID>.pdf'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
    data = resp.read()

doc = pymupdf.open(stream=data, format='pdf')
text = ''.join(page.get_text() for page in doc)
```

### Workflow for a New Company

1. Get screener URL → extract standalone financials, ratios, quarterly history
2. From Screener Documents → copy BSE links for latest concall transcript + PPT
3. Download transcript PDF → extract text → feed to Concall Analysis prompt
4. Download annual report PDF → extract text → feed to Annual Report prompt
5. Combine outputs into Investment Thesis using thesis-building.md prompt

See [data-sourcing-tools.md](./data-sourcing-tools.md) for full pipeline details.
