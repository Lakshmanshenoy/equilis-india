"""
core/models/scenario.py
ScenarioResult — output of the scenario/sensitivity engine.
Framed as mathematical outcomes of explicit assumptions only.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SingleScenario:
    label: str                              # "Bear", "Base", "Bull"
    assumption_pat_growth: str              # e.g. "12.0%"
    projected_pat_cr: Optional[float] = None
    projected_eps: Optional[float] = None
    at_current_pe: Optional[float] = None
    pe_scenarios: dict = field(default_factory=dict)  # {"PE_20x": 1234.0, ...}
    disclaimer: str = "Mathematical output of stated assumptions only."


@dataclass
class ScenarioResult:
    ticker: str
    base_pat_ttm: Optional[float] = None
    base_eps_ttm: Optional[float] = None
    base_pe_ttm: Optional[float] = None
    shares_outstanding: Optional[float] = None
    scenarios: list[SingleScenario] = field(default_factory=list)
    sensitivity_table: Optional[dict] = None    # {row_label: {col_label: value}}
    assumptions_stated: bool = False
    computed_at: str = ""
    sources: list[str] = field(default_factory=list)
    compliance_note: str = (
        "The above are mathematical outcomes of explicitly stated assumptions. "
        "They do not constitute forecasts, price targets, or investment recommendations."
    )
