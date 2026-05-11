"""
core/scenarios.py
Scenario and sensitivity engine.

All outputs are explicitly framed as mathematical outcomes of stated assumptions.
No price targets. No recommendations. Scenario labels: Bear / Base / Bull.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Callable, Optional

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
