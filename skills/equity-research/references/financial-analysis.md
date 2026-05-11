# Financial Statement Analysis & DuPont ROE

## 2. Financial Statement Analysis

Use this prompt when you upload a P&L, Balance Sheet, and Cash Flow Statement (image or PDF).

```
You are a world-class equity analyst specialising in financial statement analysis.

I have attached [image/PDF] of the financial statements of [COMPANY NAME].
Use consolidated financials. If uncertain about any number, state 'Unable to verify'.

Analyse the following across FY2021 to the latest available data:

BALANCE SHEET QUALITY
1. Is the balance sheet strong or weak? (Net worth, tangible assets, debt structure)
2. Key leverage ratios over time: Debt/Equity, Debt/EBITDA, Net Debt/EBITDA.
   Flag if leverage is improving or deteriorating.
3. Contingent liabilities — compare size to net worth. Flag if >10% of net worth.
4. Asset quality: any large write-offs, impairments, or goodwill concerns?

CASH FLOW ANALYSIS
5. Are operating cash flows strong or weak vs. net profit?
   Calculate CFO/PAT ratio for each year. Flag if consistently <0.8.
6. Can the company fund its growth via internal accruals (FCF = CFO – Capex)?
7. What does the financing cash flow tell us about capital structure changes?

GROWTH & PROFITABILITY
8. Revenue and PAT growth rates (YoY and CAGR over the period).
9. Profitability ratios: ROE, ROCE — trend and quality of returns.
10. Margin analysis: Gross, EBITDA, and PAT margins — maintained or eroding?

WORKING CAPITAL
11. DSO (Debtor Days), DIO (Inventory Days), DPO (Creditor Days) trends.
    Flag deterioration in working capital cycle.

PIOTROSKI F-SCORE
12. Calculate the Piotroski F-Score based on available data.
    Interpret the score (0-3 = weak, 4-6 = average, 7-9 = strong).

OUTPUT FORMAT
- Lead with a summary table: metric vs. year
- Follow with brief prose commentary per section
- End with a 3-line overall verdict: Strengths / Weaknesses / Watch Points

Ask me clarifying questions before you begin. I will reward you if done well.
```

### Key Thresholds
- CFO/PAT < 0.8 consistently → flag
- Contingent liabilities > 10% of net worth → flag
- Piotroski 0–3 = weak, 4–6 = average, 7–9 = strong

---

## 6. DuPont ROE Analysis

Use this prompt to deeply understand what drives a company's Return on Equity. Works best with screener.in link or uploaded financials.

```
You are an expert financial analyst specialising in financial statement analysis.

Data Source: [Paste screener.in link OR upload financial statements]
Company: [COMPANY NAME]
Period: FY21–FY25 (Treat March 2025 as FY25)

TASK: Perform a comprehensive DuPont ROE analysis.

STEP 1 — 3-FACTOR DuPont Breakdown (for each year):
   ROE = Net Profit Margin × Asset Turnover × Financial Leverage
   Present this as a table: Year | ROE | NPM | Asset Turnover | Leverage

STEP 2 — 5-FACTOR DuPont Breakdown (extended):
   ROE = Tax Burden × Interest Burden × EBIT Margin × Asset Turnover × Leverage
   Identify which factor is the primary ROE driver in each year.

STEP 3 — TREND COMMENTARY:
   • Which driver improved or worsened ROE over the period?
   • Is ROE quality high (driven by margins/turnover) or low (driven by leverage)?
   • Is the current ROE sustainable?

STEP 4 — PEER CONTEXT:
   If possible, compare this company's DuPont components to 2–3 listed peers.

STEP 5 — PLAIN ENGLISH SUMMARY:
   Explain the entire DuPont analysis as if speaking to a 15-year-old.
   Use simple analogies. No jargon.

Ask me any questions before starting. I will reward you if done well.
```
