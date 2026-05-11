# Data source map — India equity research

Use this file to determine the correct source for any data field.
Never use a lower-authority source if a higher one is available.

## Tier 1 — Regulatory / Exchange (highest authority)
| Data needed | Source | URL |
|---|---|---|
| Annual report (full PDF) | BSE filing portal | bseindia.com → Corporates → Financial Results |
| Annual report (NSE) | NSE filing portal | nseindia.com → Companies → Annual Reports |
| Shareholding pattern | BSE/NSE (quarterly) | bseindia.com → Shareholding |
| DRHP / prospectus | SEBI EDGAR | sebi.gov.in or bseindia.com |
| Corporate announcements | BSE / NSE | bseindia.com → Announcements |
| Bulk / block deals | NSE | nseindia.com → Market Data → Bulk Deals |
| F&O OI, option chain | NSE | nseindia.com → Derivatives → Option Chain |
| Bhav copy (prices, volume, delivery %) | NSE | nseindia.com → Market Data → Bhav Copy |
| XBRL financials | MCA21 portal | mca.gov.in |
| RBI policy rates | RBI | rbi.org.in/monetary-policy |
| Sectoral credit data | RBI DBIE | dbie.rbi.org.in |
| CPI, IIP, GDP | MOSPI | mospi.gov.in |
| PLI scheme details | DPIIT | dpiit.gov.in |
| USFDA inspection outcomes | FDA | fda.gov/drugs/drug-manufacturing |

## Tier 2 — Aggregators (use to cross-check Tier 1, cite Tier 1 in output)
| Data needed | Source | URL |
|---|---|---|
| 10-year financial history | Screener.in | screener.in |
| Peer comparison ratios | Screener.in | screener.in |
| Concall transcripts | Screener.in / BSE | screener.in → Concalls |
| Analyst estimates (consensus) | Trendlyne | trendlyne.com |
| Institutional holding history | Trendlyne / Tijori | trendlyne.com |
| FII/DII flows | NSE / Trendlyne | nseindia.com → FII/DII Data |

## Tier 3 — News and commentary (corroboration only, never cite alone)
| Source | Use for |
|---|---|
| Economic Times / Business Standard | News, sector context |
| MoneyControl | Concall snippets (verify against BSE filing) |
| CNBC-TV18 / BloombergQuint | Management interviews (note: unscripted, not binding) |
| Brokerage reports | Cross-check assumptions only — they may have buy-side bias |

## Citation format in output
Every figure must be cited as: `[Source: <name>, fetched <YYYY-MM-DD>]`
Example: Revenue ₹4,230 Cr [Source: Screener.in via BSE XBRL, fetched 2025-05-01]
