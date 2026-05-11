# Forensic flags module

## Purpose
Systematic red-flag scan before any valuation work. Run this first.
A forensic flag does not mean fraud — it means the analyst must investigate further
before relying on reported numbers.

## Beneish M-score
Run: `python core/beneish.py --ticker <SYMBOL>`

The script computes 8 ratios from 2 years of financial data:
1. DSRI — Days Sales Receivable Index
2. GMI — Gross Margin Index
3. AQI — Asset Quality Index
4. SGI — Sales Growth Index
5. DEPI — Depreciation Index
6. SGAI — SG&A Index
7. LVGI — Leverage Index
8. TATA — Total Accruals to Total Assets

**Interpretation:**
- M-score > –1.78: manipulation likely (not certain). Investigate further.
- M-score –1.78 to –2.22: grey zone. Review specific flagged ratios.
- M-score < –2.22: unlikely manipulation based on this model alone.

Note: Beneish was calibrated on US data. Apply with India-specific judgment.
Indian-specific adjustments: related-party revenue inflation is more common than
pure accrual manipulation — check RPT as % of revenue separately.

## Manual checklist

### Cash flow quality
- [ ] PAT vs OCF gap: compute (PAT – OCF) / PAT for last 5 years.
  If consistently >30%, probe: what is the difference? Receivables? Advances to subsidiaries?
- [ ] CFO/EBITDA ratio: should be >50% consistently. Below 30% is a flag.
- [ ] Free cash flow: has the company generated positive FCF in at least 3 of last 5 years?
  Capex-heavy industries (cement, steel) may have negative FCF in growth years — context matters.

### Balance sheet quality
- [ ] Goodwill: large goodwill from acquisitions — is there a risk of impairment?
- [ ] Deferred tax asset: very large DTA relative to book equity → probe what created it.
- [ ] Investments in subsidiaries/associates: are these disclosed with fair value?
- [ ] Capital WIP: large CWIP stuck for >3 years → probe stalled project.
- [ ] Loans and advances to group companies: proxy for fund diversion.

### Promoter and governance
- [ ] Promoter pledging: fetch from BSE shareholding pattern for last 8 quarters.
  Plot trend. >20% pledged or rising trend → flag.
- [ ] Promoter selling: check bulk/block deal history on NSE for last 2 years.
- [ ] Auditor: has the statutory auditor changed in last 3 years?
  If yes, what reason was disclosed? Voluntary resignation → flag.
- [ ] Related-party transactions: fetch from notes to accounts in annual report.
  Compute RPT (sales + purchases + loans) as % of revenue. >10% → flag.
- [ ] Number of subsidiaries/associates: >20 with unclear business rationale → flag.
- [ ] Remuneration: promoter + family remuneration as % of PAT. >10% → flag.

### Debt quality
- [ ] Debt maturity profile: is there a large bullet repayment in <2 years?
- [ ] Interest coverage: EBIT / Interest expense. <2x → risk zone; <1x → distress.
- [ ] Net debt / EBITDA: >4x is high for most sectors; >6x is distress territory.
  Exception: infrastructure, real estate — use sector norms.
- [ ] Off-balance-sheet: check lease liabilities (Ind AS 116), guarantees given.

## Output format for forensic section
Present as a two-column table:
| Flag | Status | Detail |
|---|---|---|
| PAT vs OCF gap | 🟡 WATCH | Gap >20% in FY24, FY23; investigate receivables |
| Promoter pledging | 🔴 FLAG | 34% pledged as of Q3 FY25, rising trend |
| Auditor change | ✅ CLEAR | Same auditor for 8 years |
| ... | | |

Use: ✅ CLEAR · 🟡 WATCH · 🔴 FLAG
