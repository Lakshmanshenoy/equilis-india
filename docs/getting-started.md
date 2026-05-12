# Getting Started

This guide covers installation, configuration, and running your first analysis.

---

## Prerequisites

| Requirement | Minimum version | Notes |
| --- | --- | --- |
| Python | 3.11 | Developed and tested on 3.14 |
| Node.js | 18 LTS | Required for the CLI layer |
| npm | 9 | Bundled with Node.js |

---

## 1 — Clone and set up

```bash
git clone https://github.com/Lakshmanshenoy/equilis-india.git
cd equilis-india
```

### Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Node.js CLI layer

```bash
npm install
```

---

## 2 — Verify the install

```bash
# Check the Python pipeline
.venv/bin/python -c "from core.pipeline import AnalysisPipeline; print('OK')"

# Check the CLI
node cli/index.js --help
```

Expected CLI output:

```
Usage: equilis [options] [command]

Equilis India — fundamental equity research for Indian markets

Commands:
  analyze <ticker>       Full fundamental analysis for a single ticker
  compare <tickers...>   Peer-to-peer comparison table for 2–5 tickers
  screen                 Screen stocks by financial criteria
  scenario <ticker>      Bear / Base / Bull scenario analysis
  report <ticker>        Generate full PDF research report
```

---

## 3 — Run your first analysis

### Full analysis (markdown output)

```bash
node cli/index.js analyze INFY
```

### Full analysis with PDF report (saved to `~/Downloads/`)

```bash
node cli/index.js analyze INFY --output pdf
```

### Bear / Base / Bull scenario

```bash
# Growth rates as percentages; horizon in years
node cli/index.js scenario INFY --bear 5 --base 12 --bull 20 --horizon 3
```

### Peer comparison

```bash
node cli/index.js compare INFY TCS WIPRO HCL --output markdown
```

### Sector screener

```bash
node cli/index.js screen --sector banking --min-roe 15 --max-pe 15
```

### Generate a standalone PDF report

```bash
node cli/index.js report RELIANCE
```

---

## 4 — Use the Python pipeline directly (Jupyter / scripts)

```python
import asyncio
from core.pipeline import AnalysisPipeline, PipelineConfig
from plugins.nse_api import NseApiPlugin
from plugins.screener_in import ScreenerInPlugin

pipeline = AnalysisPipeline(plugins={
    "nse_api": NseApiPlugin(),
    "screener_in": ScreenerInPlugin(),
})

result = asyncio.run(pipeline.run(PipelineConfig(ticker="INFY")))
print(result.report_markdown)
```

Access individual outputs:

```python
snap = result.snapshot

# Key financials
print(snap.income.revenue_ttm)     # ₹ Crore
print(snap.income.pat_ttm)
print(snap.market.market_cap)

# Altman Z-Score
from core.analyzer import EquityAnalyzer
analyzer = EquityAnalyzer()
z = analyzer.compute_altman_z(snap)
print(z["z_score"], z["zone"])     # e.g. 3.42, SAFE

# Scenarios
print(result.scenario_result)
```

---

## 5 — Run the test suite

```bash
.venv/bin/pytest tests/ -q
```

All 112 tests should pass. The test suite uses fixture JSON files under `tests/fixtures/`
and `CacheManager(disabled=True)` — no network calls are made.

---

## 6 — Output location

| Output type | Default path |
| --- | --- |
| PDF reports (CLI) | `~/Downloads/equilis-reports/` |
| PDF reports (Python) | `~/Downloads/` |
| Cache | `~/.equilis/cache/` |

Pass `--output-dir <path>` to the `report` command to override the PDF destination.

---

## 7 — Common options

| Flag | Applies to | Effect |
| --- | --- | --- |
| `--output pdf` | `analyze`, `compare` | Saves a branded PDF to `~/Downloads/` |
| `--no-cache` | `analyze`, `report` | Bypasses disk cache, forces live fetch |
| `--skip-validation` | `analyze` | Skips the data quality gate (dev only) |
| `--exchange BSE` | `analyze`, `report` | Uses BSE scrip code lookup instead of NSE |

---

## Next steps

- **Add a data plugin** → see [adding-a-plugin.md](adding-a-plugin.md)
- **Understand the pipeline stages** → see [architecture.md](architecture.md)
- **Data sources and field mappings** → see [data-sources.md](data-sources.md)
- **Compliance and disclaimer rules** → see [compliance.md](compliance.md)
