# Concall parser module

## Purpose
Extract structured, citable information from earnings call transcripts.
Input: PDF or text transcript. Output: structured summary with direct quotes.

## How to trigger
User says: "parse the concall for <TICKER> <quarter>", or provides a PDF.
Download transcript from: BSE filings portal → Announcements → Concall transcript.
Alternatively: Company IR website, or Screener.in concall section.

## Extraction framework

### 1. Management guidance (always extract these)
- Revenue guidance: exact words, not paraphrase. Quote directly.
- Margin guidance: exact words.
- Capex guidance: ₹ amount, timeline, purpose.
- Volume / operational guidance (sector-specific).
- Dividend / buyback intent.

### 2. Changes from prior quarter
Compare this quarter's concall against the previous quarter's on these dimensions:
- Did management upgrade or downgrade revenue guidance?
- Did the tone on margin outlook change?
- Were any new risks mentioned that weren't in the prior call?
- Were any prior commitments met, missed, or deferred?

### 3. Key risks disclosed by management
- List verbatim (quoted, with page/timestamp reference if available).
- Do not soften or summarise risk language.

### 4. Analyst questions that went unanswered or were deflected
- Flag questions where management changed subject, gave a non-answer, or said
  "we'll update in the next quarter". These are signal.

### 5. Red-flag language patterns
Watch for:
- Passive voice for bad news: "challenges were encountered" vs "we missed targets"
- Forward-looking hedging without specifics: "remain optimistic" with no numbers
- "One-time" items that recur: flag if same "one-time" item appeared in prior year
- Deflection of direct questions about receivables, debt, or subsidiary performance

## Output format

```
Concall summary — <TICKER> <Quarter> <Year>
Source: <URL or filename>  Fetched: <date>
─────────────────────────────────────────────

GUIDANCE
Revenue:   "[exact quote]"
Margin:    "[exact quote]"
Capex:     "[exact quote]"

CHANGES FROM PRIOR QUARTER
[Bullet list of what changed vs prior concall]

KEY RISKS (management-disclosed)
- "[direct quote]" — p.X / timestamp XX:XX

UNANSWERED / DEFLECTED QUESTIONS
- Q: [analyst question verbatim]  A: [management response or deflection noted]

RED-FLAG LANGUAGE
- [Flag + exact quote + why it is flagged]

DISCLAIMER
This summary is for research purposes only. Quotes are reproduced from a publicly
available regulatory filing. This does not constitute investment advice.
```
