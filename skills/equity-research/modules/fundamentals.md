# Fundamentals module

## Ratio formulas (India-specific definitions)

### Profitability
- **EBITDA margin** = EBITDA / Revenue × 100
- **PAT margin** = PAT / Revenue × 100
- **ROCE** = EBIT / (Total Assets – Current Liabilities) × 100
- **ROE** = PAT / Average Shareholders' Equity × 100
- **ROIC** = NOPAT / Invested Capital × 100
  where NOPAT = EBIT × (1 – effective tax rate)
  and Invested Capital = Total Equity + Total Debt – Cash

### DuPont decomposition of ROE
ROE = Net Margin × Asset Turnover × Equity Multiplier
- Net Margin = PAT / Revenue
- Asset Turnover = Revenue / Total Assets
- Equity Multiplier = Total Assets / Shareholders' Equity
Always decompose ROE — a high ROE from leverage is fundamentally different from one from margins.

### Valuation multiples
- **P/E** = CMP / EPS (TTM). Note: use diluted EPS.
- **EV/EBITDA** = Enterprise Value / EBITDA
  where EV = Market Cap + Total Debt – Cash and Equivalents + Minority Interest
- **EV/Sales** = EV / Revenue (useful for loss-making or early-stage companies)
- **P/B** = CMP / Book Value per Share
- **FCF Yield** = FCF per Share / CMP × 100
  where FCF = OCF – Maintenance Capex

### DCF — three-scenario structure (mandatory)
**Inputs to always state explicitly:**
- Base revenue (TTM or last full year, ₹ Cr)
- Revenue growth rate assumption (%, per year, for 5 years)
- EBITDA margin assumption (%)
- Depreciation rate (% of gross block)
- Tax rate (effective, from last 3 years average)
- Capex assumption (% of revenue or absolute ₹ Cr)
- Working capital days (receivables + inventory – payables)
- Terminal growth rate (never >6% for Indian companies; use 4–5% as default)
- WACC (compute from: cost of equity via CAPM using 10Y G-sec as risk-free rate,
  beta from NSE data, equity risk premium 6–7% for India; cost of debt = current
  borrowing rate from annual report; weighted by market-value capital structure)

**Output format:**
| Input | Bear | Base | Bull |
|---|---|---|---|
| Revenue CAGR (5Y) | X% | Y% | Z% |
| EBITDA margin | X% | Y% | Z% |
| WACC | X% | Y% | Z% |
| Terminal growth | X% | Y% | Z% |
| **Implied value (₹/share)** | **X** | **Y** | **Z** |
| vs CMP | X% discount/premium | Y% | Z% |

Never present a single target price. Always show the range.

### Working capital analysis
- Debtor days = (Trade Receivables / Revenue) × 365
- Inventory days = (Inventory / COGS) × 365
- Creditor days = (Trade Payables / Purchases) × 365
- Cash conversion cycle = Debtor days + Inventory days – Creditor days
Flag: CCC increasing year-on-year for 3+ years (cash-trap risk)
Flag: CCC < 0 for retail/FMCG (usually healthy — float business)
