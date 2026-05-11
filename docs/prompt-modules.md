# Prompt Module System

The equilis-india prompt module system provides structured prompts for each type of
equity analysis. Prompts live in `skills/equity-research/prompts/` and are designed
to be composed with live pipeline data.

---

## Module Inventory

| File                       | Purpose                              | Input Variables          |
| -------------------------- | ------------------------------------ | ------------------------ |
| `fundamentals.md`          | 7-section fundamental analysis       | snapshot, ratios, scenarios |
| `peer_compare.md`          | Peer-to-peer sector comparison       | snapshots[], ratios_list[] |
| `red_flags.md`             | Forensic accounting red-flag scan    | snapshot, ratios, red_flags |
| `scenario_base.md`         | Bear/Base/Bull scenario engine       | snapshot, scenario_result |
| `macro_sensitivity.md`     | Macro variable impact analysis       | snapshot, sector, macro_vars |

---

## How prompts are invoked

### Via pipeline (automatic)
The `core/renderer.py` renders a full report using data from the pipeline result. The
rendered markdown is structured per the prompt modules automatically — no manual prompt
invocation needed for a standard `analyze` command.

### Via AI agent (manual composition)
When using the agent directly (e.g., in VS Code Copilot), the agent reads the relevant
prompt file and fills template variables from the live `CompanySnapshot`.

Example agent flow for `fundamentals`:
1. Agent reads `skills/equity-research/prompts/fundamentals.md`
2. Agent fetches live data via `AnalysisPipeline.run(PipelineConfig(ticker="INFY"))`
3. Agent fills `{{snapshot}}`, `{{ratios}}`, `{{scenarios}}` from `PipelineResult`
4. Agent generates the 7-section report
5. Agent appends compliance disclaimer from `references/compliance-disclaimer.md`

---

## Composing multiple modules

Modules can be combined for complex analyses. Example:

**Full Forensic + Scenario report:**
1. `fundamentals.md` — sections 1–4 (overview, performance, BS, DuPont)
2. `red_flags.md` — full forensic checklist with Beneish + Altman
3. `scenario_base.md` — Bear/Base/Bull sensitivity table
4. `macro_sensitivity.md` — if sector is IT, Banking, or commodity-exposed

---

## Template variable substitution

Template variables use `{{double_braces}}` syntax. They map to `PipelineResult` fields:

| Template variable     | Source field                                     |
| --------------------- | ------------------------------------------------ |
| `{{snapshot}}`        | `PipelineResult.snapshot` (CompanySnapshot)      |
| `{{ratios}}`          | `PipelineResult.ratios` (RatioSet)               |
| `{{scenarios}}`       | `PipelineResult.scenarios` (ScenarioResult)      |
| `{{red_flags}}`       | `PipelineResult.red_flags` (list[dict])          |
| `{{ticker}}`          | `CompanySnapshot.ticker`                         |
| `{{company_name}}`    | `CompanySnapshot.company_name`                   |
| `{{sector}}`          | `CompanySnapshot.sector`                         |
| `{{cmp}}`             | `CompanySnapshot.price.cmp`                      |
| `{{market_cap}}`      | `CompanySnapshot.market.market_cap`              |
| `{{bear_growth}}`     | `PipelineConfig.scenario_params["bear"]` or 5%  |
| `{{base_growth}}`     | `PipelineConfig.scenario_params["base"]` or 12% |
| `{{bull_growth}}`     | `PipelineConfig.scenario_params["bull"]` or 20% |

---

## Adding a new prompt module

1. Create `skills/equity-research/prompts/my_module.md`
2. Define:
   - **Role** block
   - **Compliance Block** (mandatory — copy verbatim from other modules)
   - **Input** block listing required variables
   - **Output Structure** block
   - **Forbidden Language** block
3. Register in the module inventory table above
4. Update `SKILL.md` Prompt Module Index table

---

## Compliance rules for all prompts

Every prompt module MUST:
- Include the verbatim compliance block at the top of every generated output
- Prohibit buy/sell/hold language (see `docs/compliance.md` for full list)
- Cite source and fetch timestamp for every financial figure
- Present scenarios as a table, never as a single value
- Include relevant model disclaimers (Altman, Beneish, scenario)
