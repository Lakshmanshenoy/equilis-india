# Valuation Prompts

## 14.1 Sector Valuation Ratios Reference

```
You are a world-class valuation analyst.
Task: Create a comprehensive reference table of valuation ratios used
across different sectors in India.

Format: Sector | Primary Ratio | Secondary Ratio | Why These Ratios Apply
Cover at minimum: FMCG, Banking, Cement, Hospitals, AMC, Chemicals, IT,
Real Estate, Infrastructure, Insurance, QSR, Jewellery, Cables, Auto OEMs.

After the table, add a 1-paragraph note on when to override the standard
ratio (e.g., early-stage company, loss-making, cyclical bottom).
I will reward you if done well.
```

---

## 14.2 Growth Triggers of a Company

```
You are a world-class analyst specialising in identifying company growth triggers.
Company: [COMPANY NAME]
Documents attached: [annual reports / concalls / credit reports]

Find all growth triggers in a structured table:
Trigger | Type (Margin/Capex/Geographic/Product/Deleverage/Corporate Action)
       | Current Status | Expected Timeline | Revenue Impact (High/Med/Low)

After the table:
• Top 3 triggers most likely to materialise in 12–24 months
• Key quarterly metrics to monitor for each trigger
• Overall conviction: High / Medium / Low — with reasoning

I will reward you if done well.
```

---

## 14.3 Bull / Base / Bear Scenario Analysis

```
You are a world-class valuation analyst.
Company: [COMPANY NAME]
Current Market Price: ₹[___] | Shares Outstanding: [___] Cr

Build a Bull / Base / Bear scenario analysis using PE ratio and IRR.

ASSUMPTIONS (edit for your company):
Bull:  Revenue growth [17.5% / 20% / 20%] for FY26/27/28
       EBITDA margin [___% / ___% / ___%], PE multiple [35x]
Base:  Revenue growth [15% / 18% / 18%]
       EBITDA margin [___% / ___% / ___%], PE multiple [30x]
Bear:  Revenue growth [10% / 10% / 10%]
       EBITDA margin [___% / ___% / ___%], PE multiple [20x]

FOR EACH SCENARIO OUTPUT:
• Year-by-year PAT projection table
• Target EPS at end of FY28
• Implied market cap and price per share
• Upside / downside vs. current market price (%)
• 2-year and 3-year IRR
• Probability weight: Bull [__]% / Base [__]% / Bear [__]%
• Probability-weighted target price

I will reward you if done well.
```

---

## 14.4 DCF Analysis

```
You are a financial modelling expert specialising in DCF valuations.
Company: [COMPANY NAME]
Screener Link: https://www.screener.in/company/[TICKER]/consolidated/

Build a comprehensive DCF model. Structure:

1. Company Summary
2. Historical Financial Analysis (FY20–FY25)
   • Revenue CAGR, margin trends (gross/EBITDA/net)
   • Working capital efficiency, leverage, ROE, ROIC
3. DCF Assumptions
   • Revenue growth by segment (if data available)
   • Margin trajectory with drivers
   • Working capital as % of revenue
   • Capex forecasts and rationale
   • D&A schedule, tax rate assumptions
4. DCF Valuation (10-year explicit period)
   • WACC: 10% | Terminal growth rate: 2%
   • EV to Equity bridge (minus net debt, plus cash)
   • Per share intrinsic value
5. Sensitivity Table
   • Rows: WACC (8%, 9%, 10%, 11%, 12%)
   • Columns: Terminal growth (1%, 1.5%, 2%, 2.5%, 3%)
6. Valuation Insights
   • Key drivers of value
   • Margin expansion sustainability
   • Capital structure recommendations

Present with year-by-year tables. Be precise about %s and timelines.
I will reward you if done well.
```

---

## 14.5 Reverse DCF — What Does the Market Price In?

```
You are a world-class valuation analyst.
Company: [COMPANY NAME]
Current Market Price: ₹[___] | Shares Outstanding: [___] Cr
Latest Screener.in link: [paste]

TASK: Perform a Reverse DCF analysis.
Instead of calculating the 'fair value', work backwards from the current market price
to determine what growth rate and margin assumptions the market is implying.

Assumptions to hold fixed:
• WACC: 10%
• Terminal growth rate: 2%
• Tax rate: [current effective rate]
• Capex/Revenue: [current trend]

OUTPUT:
• Implied revenue CAGR (FY25–FY30) = ?
• Implied EBITDA margin at terminal = ?
• Are these assumptions realistic based on company history and sector context?

SENSITIVITY TABLE
What price does the stock deserve at different growth rates?
Rows: Revenue CAGR (5%, 8%, 12%, 15%, 20%)
Columns: EBITDA Margin (current, +100bps, +200bps, -100bps)

VERDICT
Is the market pricing in reasonable, optimistic, or unrealistic assumptions?
What would need to go right for the market to be correct?

Ask questions before starting. I will reward you if done well.
```

---

## 20. Sum-of-Parts (SOTP) Valuation

Use for holding companies, conglomerates, or businesses with multiple distinct segments.

```
You are a world-class valuation analyst specialising in SOTP valuations.
Company: [COMPANY NAME] — a conglomerate/holding company with distinct businesses.
Data sources: Screener.in [link], uploaded annual reports, credit reports

Build a rigorous Sum-of-Parts valuation:

STEP 1 — SEGMENT IDENTIFICATION
List each distinct business segment with:
Segment Name | Revenue | EBITDA | EBITDA Margin | Is it listed?

STEP 2 — VALUATION METHODOLOGY PER SEGMENT
Choose the appropriate method for each segment:
• Core operating business: EV/EBITDA or P/E (use peer multiples)
• Listed subsidiary: use current market cap × holding %
  (apply 20–30% holding company discount)
• Real estate / land bank: book value or NAV
• Financial services: P/Book
• Early-stage / loss-making: Revenue multiple or DCF

STEP 3 — SOTP TABLE
Segment | Metric Used | Value | Multiple | EV (₹ Cr)
...
Total Enterprise Value
Less: Net Debt
= Equity Value
÷ Shares Outstanding
= Intrinsic Value Per Share

STEP 4 — DISCOUNT TO NAV ANALYSIS
• Current market cap vs. SOTP value
• Premium or discount to SOTP: __%
• Historical average discount (if available)
• Why does/should a discount exist? Is it justified?

STEP 5 — CATALYST FOR DISCOUNT NARROWING
What corporate events or operational improvements could close the gap?
(Demerger, IPO of subsidiary, stake sale, improved disclosure, buyback)

Ask questions before starting. I will reward you if done well.
```
