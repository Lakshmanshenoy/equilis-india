# Earnings Revision Tracker

## Standalone Earnings Revision Tracker

Use after each quarterly result to track management guidance evolution, estimate revision momentum, and guidance credibility for portfolio companies.

```
You are a buy-side analyst focused on earnings revision tracking.
Company: [COMPANY NAME]
Input: last 4 concall transcripts, broker reports, latest results press release

TASK 1 — GUIDANCE EVOLUTION
Track how management guidance has changed each quarter:

| Quarter | Revenue Guidance | EBITDA Margin | Volume/KPI Guidance | Tone Change |
|---------|-----------------|---------------|---------------------|-------------|
| Q1FY25  |                 |               |                     |             |
| Q2FY25  |                 |               |                     |             |
| Q3FY25  |                 |               |                     |             |
| Q4FY25  |                 |               |                     |             |

TASK 2 — ESTIMATE REVISION MOMENTUM
For each metric, was consensus revised UP / DOWN / STABLE and why?

| Metric  | Q1→Q2 | Q2→Q3 | Q3→Q4 | Driver of Revision |
|---------|-------|-------|-------|--------------------|
| Revenue |       |       |       |                    |
| EBITDA  |       |       |       |                    |
| PAT     |       |       |       |                    |

TASK 3 — SURPRISE ANALYSIS
| Quarter | Revenue Beat/Miss % | EBITDA Beat/Miss % | PAT Beat/Miss % | Day-after move |
|---------|--------------------|--------------------|-----------------|----------------|
| Q1FY25  |                    |                    |                 |                |
| Q2FY25  |                    |                    |                 |                |
| Q3FY25  |                    |                    |                 |                |
| Q4FY25  |                    |                    |                 |                |

TASK 4 — GUIDANCE CREDIBILITY RATING
Rate management on guidance quality:
• Conservative → consistently beats: Positive signal (management sandbagging)
• Realistic → on target: Neutral — predictable
• Aggressive → consistently misses: Red flag — lose credibility
• Guidance cut cycle (cut 2+ quarters in a row): Major red flag

TASK 5 — FORWARD ESTIMATES & KEY RISKS
Based on latest concall guidance + revision trend:
| Metric | FY26E | FY27E | Key Upside Risk | Key Downside Risk |
|--------|-------|-------|-----------------|-------------------|
| Revenue |      |       |                 |                   |
| EBITDA  |      |       |                 |                   |
| PAT     |      |       |                 |                   |

KEY INDICATORS TO TRACK QUARTERLY:
• Margin trajectory (gross → EBITDA → PAT compression or expansion)
• Capex intensity vs. revenue growth
• Guidance accuracy percentage
• Management credibility score (1–10)
• Governance: any changes in promoter shareholding, auditor, KMP

Ask questions before starting. I will reward you if done well.
```

### Revision Signal Dictionary

| Signal | Interpretation |
|--------|---------------|
| Revenue beat + PAT beat | Strong execution — positive |
| Revenue beat + PAT miss | Margin compression — investigate |
| Revenue miss + PAT beat | Cost-cutting mode — monitor |
| Revenue miss + PAT miss | Fundamental miss — de-rate risk |
| Guidance cut 2+ quarters | Guidance cut cycle — major red flag |
| Guidance raised mid-year | Positive revision momentum |
| Sandbagging pattern | Indicates conservative management |
