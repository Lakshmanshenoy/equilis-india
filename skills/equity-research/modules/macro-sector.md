# Macro and sector overlay module

## India-specific macro watchpoints

### RBI policy cycle
- Current repo rate and stance: fetch from rbi.org.in/monetary-policy.
- Rate-sensitive sectors: Banks, NBFCs, Housing Finance, Real Estate.
  Rising rates compress NIMs for banks; falling rates expand them.
- Liquidity: SLR, CRR, LAF corridor. Tight liquidity → NBFC stress.
- Credit growth: fetch from RBI DBIE (dbie.rbi.org.in) → sectoral credit deployment.

### Union Budget
- Capex allocation: check Budget speech for infrastructure outlay (roads, railways, defence).
  Beneficiaries: L&T, KNR, PNC Infra, BEML, BEL, Mazagon Dock etc.
- PLI schemes: fetch active PLI schemes from DPIIT website.
  Current active sectors: semiconductors, electronics, pharma APIs, textiles,
  food processing, auto components, advanced chemistry cells.
- Import duty changes: check customs notification; relevant for metals, electronics.
- Tax changes: surcharge, MAT, dividend distribution — affects PAT directly.

### FII / DII flows
- Fetch from NSE website → Reports → FII/DII data (monthly).
- Net FII buying in a sector over 3 months = institutional accumulation signal.
- Net FII selling + DII buying = domestic confidence, foreign risk-off.
- Note: FII flows in F&O (index + stock futures) can diverge from cash market flows.

### Monsoon and agriculture
- IMD forecast: imd.gov.in (June–September season).
- Impact sectors:
  - Good monsoon: FMCG rural demand, two-wheeler rural, agri-input companies, MFIs.
  - Bad monsoon: pressure on rural demand, food inflation, RBI forced to hold rates.
- Kharif and Rabi MSP announcements: check CACP press releases.

### INR and commodity sensitivity
- INR/USD: weaker INR helps IT exporters, pharma exporters; hurts importers (crude, electronics).
- Brent crude: every $10/bbl rise adds ~₹70,000 Cr to India's import bill.
  Direct hit: OMCs (HPCL, BPCL, IOC), aviation (IndiGo, Air India), paints.
  Indirect hit: logistics costs across sectors.
- Steel and aluminium: relevant for auto, capital goods, construction.
- Cotton: relevant for textiles (Vardhman, Arvind, Welspun).

## Sector-specific frameworks

### Banks and NBFCs
Key metrics: NIM, GNPA, NNPA, PCR, CASA ratio, CD ratio, capital adequacy (CRAR), slippage ratio.
Fetch from: RBI supervisory returns (summary published quarterly), company investor presentations.
Watch: RBI's prompt corrective action (PCA) framework — any bank under PCA is high-risk.

### IT services
Key metrics: Revenue in USD (constant currency growth), EBIT margin, headcount, utilisation, attrition.
Macro link: US GDP, US unemployment, enterprise IT budgets (Gartner IT spend forecast).
Watch: visa costs (H1-B fees), pricing pressure in legacy services, GenAI cannibalisation of
low-end BFSI and BPO work.

### Pharmaceuticals
Key metrics: US generics revenue + filings (ANDA count), domestic formulations growth,
API volumes, USFDA compliance (Form 483s, warning letters).
Fetch: USFDA website (fda.gov/drugs) for inspection outcomes; company filings for ANDA count.
Watch: price erosion in US generics (IQVIA data), Ayushman Bharat drug pricing.

### Consumer and FMCG
Key metrics: Volume growth (not value — strips out price), gross margin (input cost sensitivity),
rural/urban mix, distribution reach.
Macro link: rural wage growth (MGNREGS disbursement, rabi/kharif MSP), urban wage growth,
CPI food inflation (directly hits gross margins for food companies).

### Cement
Key metrics: Volume (MT), realisations (₹/tonne), cost/tonne (energy = 35–40% of cost),
capacity utilisation, EBITDA/tonne.
Macro link: government housing and infra capex, real estate demand.
Watch: fuel cost (pet coke imports), logistics cost (diesel).

### Capital goods and defence
Key metrics: Order book, order inflow rate, book-to-bill ratio (>2x healthy), execution timeline.
Macro link: Union Budget capex, Defence Acquisition Procedure (DAP) approvals, PLI for defence.
Watch: working capital cycle (government delays in payment), L1 pricing pressure.

## Output format for macro section
Write a 200–300 word narrative covering:
1. Current macro environment and its net effect on this sector (positive / negative / neutral).
2. Specific policy tailwinds or headwinds in the next 12 months.
3. One key macro risk that could invalidate the base scenario.
