# Architecture

## Layer diagram

```
IDE / Agent (Claude Code, Cursor, VS Code Copilot)
        │
        ▼
plugins/claude-code/        ← slash commands, agent integration
        │
        ▼
skills/equity-research/     ← SKILL.md entry point
  ├── modules/              ← fundamentals, forensic-flags, macro-sector,
  │                            technicals, peer-comparison, concall-parser
  └── references/           ← data-sources.md, compliance-disclaimer.md
        │
        ▼
core/                       ← Python pipeline
  ├── fetch.py              ← Screener.in + NSE live price
  ├── validate.py           ← field presence, range, cross-source checks
  ├── beneish.py            ← Beneish M-score computation
  └── render.py             ← markdown → PDF via weasyprint
        │
        ▼
Data sources
  Tier 1: BSE / NSE / MCA21 / SEBI / RBI / MOSPI (regulatory)
  Tier 2: Screener.in / Trendlyne (aggregators)
  Tier 3: News / brokerage (corroboration only)
        │
        ▼
Output: ~/Downloads/equilis-reports/<TICKER>_<DATE>.pdf
```

## Design principles

1. **Validate before use** — every data fetch passes through `validate.py` before analysis begins
2. **Cite everything** — every figure in output carries `[Source: <name>, fetched <date>]`
3. **Scenario, not target** — all valuation outputs show Bear / Base / Bull; no single target price
4. **Compliance by default** — `compliance-disclaimer.md` is injected at the end of every report; no buy/sell/hold language anywhere
5. **Portable skill layer** — modules in `skills/equity-research/modules/` work across IDEs; the core Python scripts are optional automation

## Adding a new plugin

1. Create `plugins/<your-agent>/` directory
2. Add a `plugin.json` with `name`, `version`, `commands`, `skill`, and `disclaimer` fields
3. Reference `skills/equity-research/SKILL.md` as the skill entry point
4. Add a `README.md` with installation steps and slash command table

## Adding a new skill module

1. Create `skills/equity-research/modules/<module-name>.md`
2. Add the module to Step 2 of `skills/equity-research/SKILL.md` with a brief description and the relative path
3. Follow the format of existing modules: title → purpose → when-to-use → output format

## Contract

The host adapter should never reimplement the analysis logic.
