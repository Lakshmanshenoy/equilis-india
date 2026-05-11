# Technical context module

## Purpose
This module provides technical context to support — not drive — fundamental analysis.
Technical signals help calibrate entry/exit zones for scenario sizing. They are
never used as standalone signals in this research framework.

## Data sources
- **Prices, volumes, delivery %:** NSE bhav copy (nseindia.com → Market Data → Bhav Copy).
  Download the daily bhav CSV for the required date range.
- **Moving averages:** Compute from bhav copy price series (closing price).
- **F&O data (if applicable):** NSE option chain (nseindia.com → F&O → Option Chain).
- **52-week high/low:** NSE equity screener or Screener.in.

## What to compute and report

### Price context
- Current price vs 50-DMA: above = positive short-term momentum; below = negative.
- Current price vs 200-DMA: above = long-term uptrend; below = long-term downtrend.
- 52-week high/low range: where is CMP in the range?
  Formula: (CMP – 52W Low) / (52W High – 52W Low) × 100 = percentile position.
  Report as: "CMP is at the Xth percentile of its 52-week range."
- Distance from 52W high: (52W High – CMP) / 52W High × 100.

### Volume and delivery analysis
- 20-day average daily volume: compute from bhav copy.
- Delivery %: from bhav copy (DELQTY / TRDQTY × 100).
  - Delivery % consistently >50% → institutional accumulation likely.
  - Delivery % <30% on rising price → speculative; less conviction.
  - Spike in delivery % on a price up-move → strong accumulation signal.
- Compare current delivery % to 30-day average delivery % to identify anomalies.

### F&O context (only for F&O stocks)
- **Open Interest (OI):** Fetch from NSE F&O bhav copy.
  - Rising price + rising OI = fresh long buildup (bullish).
  - Rising price + falling OI = short covering (less conviction).
  - Falling price + rising OI = fresh short buildup (bearish).
  - Falling price + falling OI = long unwinding (less conviction).
- **Put-Call Ratio (PCR):** Sum of put OI / sum of call OI.
  - PCR > 1.2 = excessive bearishness → potential reversal up.
  - PCR < 0.7 = excessive optimism → potential reversal down.
  - Use as a contrarian indicator, not a directional one.
- **Max pain:** the price at which maximum options contracts expire worthless.
  Report as a reference point only.
- **Cost of carry:** for futures, compute annualised basis.
  Positive and high carry → bullish futures positioning.

## Output format for technical section
Present as a structured block, not a narrative:

```
Technical context — <TICKER> as of <DATE>
─────────────────────────────────────────
CMP:              ₹X
50-DMA:           ₹X  (CMP is X% above/below)
200-DMA:          ₹X  (CMP is X% above/below)
52W High:         ₹X  (CMP is X% below 52W high)
52W Low:          ₹X  (CMP is X% above 52W low)
52W percentile:   X% (0 = at 52W low, 100 = at 52W high)

Volume (20D avg):     X lakh shares/day
Delivery % (today):   X%
Delivery % (30D avg): X%
Delivery signal:      [Institutional accumulation / Speculative / Neutral]

F&O (if applicable):
  OI trend:   [Fresh longs / Short covering / Fresh shorts / Long unwinding]
  PCR:        X.XX [Bearish extreme / Neutral / Bullish extreme]
  Max pain:   ₹X
```

Do not use technical levels as price targets. Do not say "resistance at X" or "support at Y"
as if these are investment-relevant conclusions. Technical context informs scenario framing only.
