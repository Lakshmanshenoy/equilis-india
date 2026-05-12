# Equilis India

Equilis India is a compliance-first equity research pipeline for Indian listed
companies. It fetches public-market data, validates it, computes core financial
ratios and forensic checks, builds Bear/Base/Bull scenario tables, and renders
markdown or PDF reports with the standard research disclaimer attached.

## What is included

- `core/` — async fetch, normalize, validate, analyze, scenario, and render pipeline
- `plugins/` — NSE, BSE, Screener.in, Tickertape, and PDF export adapters
- `cli/` — Node.js command line interface over the Python pipeline
- `skills/equity-research/` — portable agent skill, prompts, templates, and references
- `docs/` — architecture, compliance, data-source, and plugin authoring notes
- `tests/` — fixture-backed unit and integration coverage with no live network calls

## Principles

- No investment advice or single-point conclusions
- Bear/Base/Bull scenario analysis only
- Live data fetches for market-sensitive fields
- Validation before analysis and rendering
- Source and fetch-time attribution in reports
- Standard disclaimer appended to every report-like output

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
npm install
```

```bash
node cli/index.js --help
python3 -m pytest
```

## CLI examples

```bash
node cli/index.js analyze INFY
node cli/index.js analyze INFY --output pdf
node cli/index.js scenario INFY --bear 5 --base 12 --bull 20 --horizon 3
node cli/index.js compare INFY TCS WIPRO HCL
node cli/index.js report RELIANCE --format pdf
node cli/index.js screen --sector Banking --min-roe 15 --max-pe 25
```

## Output locations

Markdown reports are saved to `~/Downloads/equilis-reports/`.
Branded reports from `report` are saved to `~/Downloads/equilis-reports/` unless
`--output-dir` is provided.

## Current limitations

- BSE code resolution is available, but coverage depends on BSE search/API response quality.
- Screener.in is scraped because it does not expose a public API.
- Index universe files under `data/index_lists/` are seed lists and should be refreshed
  before production screening.
- This is a research automation tool, not a SEBI-registered research analyst.
