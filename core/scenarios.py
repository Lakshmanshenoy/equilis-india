"""
core/scenarios.py
Scenario and sensitivity engine.

All outputs are explicitly framed as mathematical outcomes of stated assumptions.
No price targets. No recommendations. Scenario labels: Bear / Base / Bull.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Dict, List, Optional

from core.models.company import CompanySnapshot
from core.models.scenario import ScenarioResult, SingleScenario

logger = logging.getLogger(__name__)

# Default scenario growth rate assumptions
DEFAULT_SCENARIO_ASSUMPTIONS = {
    "Bear": 0.05,   # 5% PAT growth
    "Base": 0.12,   # 12% PAT growth
    "Bull": 0.20,   # 20% PAT growth
}

DEFAULT_PE_MULTIPLES = [15.0, 20.0, 25.0, 30.0, 35.0]

# Macro sensitivity definitions by sector
MACRO_SENSITIVITIES = {
    "IT_SECTOR": {
        "INR_DEPRECIATION": {
            "description": "Impact of 5% INR depreciation on revenue (USD earner)",
            "revenue_impact_pct": +0.04,  # ~4% revenue uplift
            "note": "Approximate only. Hedging policies vary by company.",
        },
        "US_RECESSION": {
            "description": "Scenario: 10% cut in IT discretionary spend by US clients",
            "revenue_impact_pct": -0.08,
            "note": "Severity varies — product companies vs service companies differ.",
        },
    },
    "BANKING": {
        "RBI_RATE_HIKE_100BPS": {
            "description": "RBI hikes repo rate by 100bps",
            "nim_impact_bps": +15,
            "note": "Floating rate loan book benefits. Fixed rate liabilities lag.",
        },
        "RBI_RATE_CUT_100BPS": {
            "description": "RBI cuts repo rate by 100bps",
            "nim_impact_bps": -10,
            "note": "Asset repricing faster than liability repricing in rate-cut cycle.",
        },
    },
}

SCENARIO_COMPLIANCE_NOTE = (
    "The above are mathematical outcomes of explicitly stated growth-rate and "
    "PE-multiple assumptions. They do not constitute earnings forecasts, price "
    "targets, or investment recommendations."
)


def earnings_scenarios(
    snapshot: CompanySnapshot,
    assumptions: Optional[dict] = None,
    pe_multiples: Optional[list[float]] = None,
    horizon_years: int = 3,
) -> ScenarioResult:
    """
    Compute Bear / Base / Bull earnings scenarios.

    Parameters
    ----------
    snapshot      : Normalised CompanySnapshot with at minimum income.pat_ttm
    assumptions   : Dict of {label: growth_rate} overriding defaults
    pe_multiples  : List of PE multiples to apply across each scenario
    horizon_years : Projection horizon (default 3 years)
    """
    assumptions = assumptions or DEFAULT_SCENARIO_ASSUMPTIONS
    pe_multiples = pe_multiples or DEFAULT_PE_MULTIPLES

    inc = snapshot.income
    mkt = snapshot.market
    price = snapshot.price

    if not inc or not inc.pat_ttm:
        logger.warning(f"[scenarios] {snapshot.ticker}: pat_ttm missing — cannot run scenarios")
        return ScenarioResult(
            ticker=snapshot.ticker,
            computed_at=datetime.now().isoformat(),
        )

    base_pat = inc.pat_ttm
    shares = mkt.shares_outstanding if mkt else None
    base_eps = inc.eps_ttm
    base_pe = None
    if price and price.cmp and base_eps:
        base_pe = price.cmp / base_eps if base_eps != 0 else None

    scenario_outputs: list[SingleScenario] = []

    for label, growth_rate in assumptions.items():
        projected_pat = base_pat * ((1 + growth_rate) ** horizon_years)
        projected_eps = None
        if shares:
            projected_eps = projected_pat / shares

        pe_results: dict[str, float] = {}
        if projected_eps:
            for pe in pe_multiples:
                key = f"PE_{int(pe)}x"
                pe_results[key] = round(projected_eps * pe, 1)

        scenario_outputs.append(SingleScenario(
            label=label,
            assumption_pat_growth=f"{growth_rate * 100:.1f}%",
            projected_pat_cr=round(projected_pat, 1),
            projected_eps=round(projected_eps, 2) if projected_eps else None,
            at_current_pe=round(projected_eps * base_pe, 1) if projected_eps and base_pe else None,
            pe_scenarios=pe_results,
        ))

    return ScenarioResult(
        ticker=snapshot.ticker,
        base_pat_ttm=base_pat,
        base_eps_ttm=base_eps,
        base_pe_ttm=base_pe,
        shares_outstanding=shares,
        scenarios=scenario_outputs,
        assumptions_stated=True,
        computed_at=datetime.now().isoformat(),
        compliance_note=SCENARIO_COMPLIANCE_NOTE,
    )


def sensitivity_table(
    base_value: float,
    row_var_range: list[float],
    col_var_range: list[float],
    formula: Callable[[float, float, float], float],
    row_label: str = "Growth Rate",
    col_label: str = "PE Multiple",
) -> dict:
    """
    Generate a 2D sensitivity table.

    Parameters
    ----------
    base_value    : Anchor value (e.g. base EPS or PAT)
    row_var_range : List of row variable values (e.g. growth rates)
    col_var_range : List of column variable values (e.g. PE multiples)
    formula       : Callable(base_value, row_var, col_var) → output value
    row_label     : Human-readable row variable label
    col_label     : Human-readable column variable label

    Returns a nested dict: {row_label_str: {col_label_str: value}}
    """
    table: dict = {}
    for row_var in row_var_range:
        row_key = f"{row_label}={row_var:.1%}" if row_var < 1 else f"{row_label}={row_var:.1f}"
        table[row_key] = {}
        for col_var in col_var_range:
            col_key = f"{col_label}={col_var:.1f}"
            table[row_key][col_key] = round(formula(base_value, row_var, col_var), 1)
    return table


# ── Phase 2: ScenarioEngine class with GrowthScenario dataclasses ────────────

COMPLIANCE_DISCLAIMER = (
    "The following are mathematical outcomes of explicitly stated assumptions. "
    "They do not constitute forecasts, price targets, or investment recommendations. "
    "Assumptions are illustrative and user-defined."
)


@dataclass
class GrowthScenario:
    label: str                           # "Bear", "Base", "Bull"
    pat_growth: float                    # e.g. 0.05 for 5%
    pe_multiples: List[float]
    years_forward: int = 1


@dataclass
class ScenarioOutput:
    label: str
    pat_growth_assumed: float
    projected_pat_cr: float
    projected_eps: float
    pe_matrix: Dict[str, float]          # "PE 20x" → implied value per share
    disclaimer: str = field(default_factory=lambda: COMPLIANCE_DISCLAIMER)


@dataclass
class SensitivityTable:
    title: str
    row_label: str
    col_label: str
    data: object                         # pandas DataFrame or dict fallback
    disclaimer: str = field(default_factory=lambda: COMPLIANCE_DISCLAIMER)


@dataclass
class ScenarioEngineResult:
    ticker: str
    base_pat_cr: float
    base_eps: float
    base_pe: Optional[float]
    scenarios: List[ScenarioOutput]
    sensitivity_table: Optional[SensitivityTable]
    macro_context: Optional[dict]
    disclaimer: str = field(default_factory=lambda: COMPLIANCE_DISCLAIMER)


class ScenarioEngine:

    def run(
        self,
        snapshot: CompanySnapshot,
        scenarios: List[GrowthScenario],
        include_sensitivity: bool = True,
        include_macro: bool = True,
    ) -> ScenarioEngineResult:
        inc   = snapshot.income
        price = snapshot.price

        base_pat = inc.pat_ttm if inc else 0.0
        base_eps = inc.eps_ttm if inc else 0.0
        base_pe  = None
        if price and price.cmp and base_eps:
            base_pe = price.cmp / base_eps if base_eps != 0 else None

        scenario_outputs = [
            self._compute_scenario(s, base_pat, base_eps)
            for s in scenarios
        ]

        sensitivity = None
        if include_sensitivity:
            growth_range = [s.pat_growth for s in scenarios]
            pe_range     = scenarios[0].pe_multiples if scenarios else [20.0, 25.0, 30.0]
            sensitivity  = self._build_sensitivity_table(base_eps, growth_range, pe_range)

        macro_context = None
        if include_macro and snapshot.sector in MACRO_SENSITIVITY_CONFIG:
            macro_context = MACRO_SENSITIVITY_CONFIG[snapshot.sector]

        return ScenarioEngineResult(
            ticker=snapshot.ticker,
            base_pat_cr=base_pat,
            base_eps=base_eps,
            base_pe=base_pe,
            scenarios=scenario_outputs,
            sensitivity_table=sensitivity,
            macro_context=macro_context,
        )

    def _compute_scenario(
        self,
        scenario: GrowthScenario,
        base_pat: float,
        base_eps: float,
    ) -> ScenarioOutput:
        projected_pat = base_pat * ((1 + scenario.pat_growth) ** scenario.years_forward)
        projected_eps = base_eps * ((1 + scenario.pat_growth) ** scenario.years_forward)
        pe_matrix = {
            f"PE {pe:.0f}x": round(projected_eps * pe, 2)
            for pe in scenario.pe_multiples
        }
        return ScenarioOutput(
            label=scenario.label,
            pat_growth_assumed=scenario.pat_growth,
            projected_pat_cr=round(projected_pat, 1),
            projected_eps=round(projected_eps, 2),
            pe_matrix=pe_matrix,
        )

    def _build_sensitivity_table(
        self,
        base_eps: float,
        growth_range: List[float],
        pe_range: List[float],
    ) -> SensitivityTable:
        """2D sensitivity: rows = PAT growth, cols = PE multiples, cells = implied value."""
        try:
            import pandas as pd
            data = {}
            for pe in pe_range:
                col_values = [round(base_eps * (1 + g) * pe, 1) for g in growth_range]
                data[f"PE {pe:.0f}x"] = col_values
            index = [f"PAT Growth {g:.0%}" for g in growth_range]
            df = pd.DataFrame(data, index=index)
        except ImportError:
            # Fallback: plain dict
            df = {
                f"PE {pe:.0f}x": [round(base_eps * (1 + g) * pe, 1) for g in growth_range]
                for pe in pe_range
            }
        return SensitivityTable(
            title="Implied Value per Share (₹) — Sensitivity Table",
            row_label="PAT Growth",
            col_label="PE Multiple",
            data=df,
        )


def parse_scenario_args(
    growth_str: str,
    pe_str: str,
    years: int = 1,
) -> List[GrowthScenario]:
    """
    Parse CLI-style args into GrowthScenario objects.
    growth_str: "bear=5,base=12,bull=18"  (values as %)
    pe_str:     "18,22,26"
    """
    pe_multiples = [float(p) for p in pe_str.split(",")]
    scenarios: List[GrowthScenario] = []
    for part in growth_str.split(","):
        label, val = part.split("=")
        scenarios.append(GrowthScenario(
            label=label.strip().title(),
            pat_growth=float(val.strip()) / 100,
            pe_multiples=pe_multiples,
            years_forward=years,
        ))
    return scenarios


# ── Macro Sensitivity Reference Data ─────────────────────────────────────────
# Factual sector-level context only. Not stock-specific. Not predictive.

MACRO_SENSITIVITY_CONFIG: Dict[str, dict] = {
    "Information Technology": {
        "factors": [
            {
                "factor": "INR/USD Exchange Rate",
                "observation": (
                    "Indian IT exports are USD-denominated. A weaker INR increases reported "
                    "INR revenue for the same USD billing. Historically, ~1% INR depreciation "
                    "has been associated with approximately 0.5%–0.8% revenue uplift at the "
                    "company level, modulated by hedging policy."
                ),
                "caveats": [
                    "Hedging ratios vary by company",
                    "Partial USD cost base offsets upside",
                ],
            },
            {
                "factor": "US/EU Discretionary IT Spending",
                "observation": (
                    "BFSI, retail, and manufacturing verticals are historically cyclical in "
                    "their IT spend. During GFC (FY09) and COVID (FY21), large-cap IT revenue "
                    "growth moderated by 3–8% vs prior year trend. Cost-optimisation mandates "
                    "can partially offset discretionary cuts."
                ),
                "caveats": [
                    "Company-specific vertical mix is material",
                    "AI-related spend adds a new cycle layer",
                ],
            },
        ],
        "disclaimer": (
            "Macro sensitivity is sector-level context for research framing only. "
            "Not company-specific. Not predictive."
        ),
    },
    "Banking": {
        "factors": [
            {
                "factor": "RBI Repo Rate",
                "observation": (
                    "NIM sensitivity to rate changes depends on CASA ratio, proportion of "
                    "floating-rate loans, and repricing lag. A 50bps rate increase has "
                    "historically been associated with 10–20bps NIM expansion for banks with "
                    "high CASA, with a 1–2 quarter lag."
                ),
                "caveats": [
                    "Fixed-rate loan mix dampens sensitivity",
                    "Competition on deposit pricing",
                ],
            },
            {
                "factor": "Credit Cycle / NPA",
                "observation": (
                    "Gross NPA ratios are a lagging indicator. Stress build-up in specific "
                    "sectors (e.g., infrastructure, MSME) precedes reported NPA increases by "
                    "2–4 quarters typically."
                ),
                "caveats": ["Provisioning policy affects reported P&L timing"],
            },
        ],
        "disclaimer": (
            "Macro sensitivity is sector-level context for research framing only. "
            "Not company-specific. Not predictive."
        ),
    },
    "Pharma": {
        "factors": [
            {
                "factor": "US Generics Pricing",
                "observation": (
                    "US generics pricing has faced structural deflation of 5–10% annually due "
                    "to consolidation among US pharmacy buyers. Companies with complex generics "
                    "(injectables, controlled substances) have shown relatively lower price erosion."
                ),
                "caveats": [
                    "Pipeline mix is the key differentiator",
                    "USFDA inspection outcomes add binary risk",
                ],
            },
        ],
        "disclaimer": (
            "Macro sensitivity is sector-level context for research framing only. "
            "Not company-specific. Not predictive."
        ),
    },
    "FMCG": {
        "factors": [
            {
                "factor": "Rural Demand / Monsoon",
                "observation": (
                    "Rural India accounts for 35–40% of FMCG volumes. Normal monsoon years "
                    "have historically correlated with 1–2% higher rural volume growth for "
                    "mass-market FMCG categories."
                ),
                "caveats": [
                    "Urban premiumisation trend reduces rural dependence over time",
                ],
            },
            {
                "factor": "Input Cost (Crude / Palm Oil / Packaging)",
                "observation": (
                    "Gross margin is sensitive to crude (packaging, fuel), palm oil (edible "
                    "oils, soaps), and wheat/sugar for food categories. Input cost tailwinds "
                    "have historically preceded EBITDA margin recovery by 1–2 quarters."
                ),
                "caveats": [
                    "Pricing power varies by brand strength and category competitiveness",
                ],
            },
        ],
        "disclaimer": (
            "Macro sensitivity is sector-level context for research framing only. "
            "Not company-specific. Not predictive."
        ),
    },
}

MACRO_SENSITIVITY_CONFIG.update({
    "Cement": {
        "repo_rate": {"sensitivity": "medium", "direction": "inverse"},
        "infrastructure_spend": {"sensitivity": "high", "direction": "positive"},
        "coal_price": {"sensitivity": "high", "direction": "inverse"},
    },
    "Auto": {
        "repo_rate": {"sensitivity": "high", "direction": "inverse"},
        "fuel_price": {"sensitivity": "medium", "direction": "inverse"},
        "rural_income": {"sensitivity": "high", "direction": "positive"},
    },
    "Steel": {
        "china_exports": {"sensitivity": "high", "direction": "inverse"},
        "infrastructure_spend": {"sensitivity": "high", "direction": "positive"},
        "iron_ore_price": {"sensitivity": "medium", "direction": "inverse"},
    },
    "Consumer Durables": {
        "repo_rate": {"sensitivity": "medium", "direction": "inverse"},
        "rural_income": {"sensitivity": "high", "direction": "positive"},
        "monsoon": {"sensitivity": "medium", "direction": "positive"},
    },
    "Telecom": {
        "arpu_trend": {"sensitivity": "high", "direction": "positive"},
        "spectrum_cost": {"sensitivity": "medium", "direction": "inverse"},
        "subscriber_growth": {"sensitivity": "high", "direction": "positive"},
    },
    "Power": {
        "fuel_price": {"sensitivity": "high", "direction": "inverse"},
        "capacity_utilisation": {"sensitivity": "high", "direction": "positive"},
        "policy_tariff": {"sensitivity": "medium", "direction": "positive"},
    },
    "Real Estate": {
        "repo_rate": {"sensitivity": "high", "direction": "inverse"},
        "housing_demand": {"sensitivity": "high", "direction": "positive"},
        "cement_steel_cost": {"sensitivity": "medium", "direction": "inverse"},
    },
})

