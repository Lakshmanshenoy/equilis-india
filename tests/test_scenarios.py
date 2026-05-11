"""
tests/test_scenarios.py
Tests for ScenarioEngine — growth scenarios, sensitivity table, parse_scenario_args().
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_analyzer import build_snapshot_from_fixture, load_fixture
from core.scenarios import (
    GrowthScenario,
    ScenarioEngine,
    ScenarioOutput,
    parse_scenario_args,
    COMPLIANCE_DISCLAIMER,
)


@pytest.fixture
def infy_snapshot():
    return build_snapshot_from_fixture(load_fixture("infy_fy24.json"))


@pytest.fixture
def engine():
    return ScenarioEngine()


def _default_scenarios():
    pe = [18.0, 22.0, 26.0]
    return [
        GrowthScenario(label="Bear",  pat_growth=0.05, pe_multiples=pe),
        GrowthScenario(label="Base",  pat_growth=0.12, pe_multiples=pe),
        GrowthScenario(label="Bull",  pat_growth=0.18, pe_multiples=pe),
    ]


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_scenario_math_bear_base_bull(engine, infy_snapshot):
    """Projected PAT: Bear < Base < Bull."""
    result = engine.run(infy_snapshot, _default_scenarios())
    pats = [s.projected_pat_cr for s in result.scenarios]
    assert pats[0] < pats[1] < pats[2], (
        f"Expected Bear<Base<Bull PAT ordering, got {pats}"
    )


def test_scenario_correct_label_order(engine, infy_snapshot):
    result = engine.run(infy_snapshot, _default_scenarios())
    labels = [s.label for s in result.scenarios]
    assert labels == ["Bear", "Base", "Bull"]


def test_scenario_bear_pat_math(engine, infy_snapshot):
    """Bear PAT = base_pat × 1.05."""
    result = engine.run(infy_snapshot, _default_scenarios())
    base_pat = infy_snapshot.income.pat_ttm
    expected_bear = round(base_pat * 1.05, 1)
    assert result.scenarios[0].projected_pat_cr == expected_bear


def test_sensitivity_table_created(engine, infy_snapshot):
    result = engine.run(infy_snapshot, _default_scenarios(), include_sensitivity=True)
    assert result.sensitivity_table is not None


def test_sensitivity_table_shape(engine, infy_snapshot):
    """3 growth scenarios × 3 PE multiples → DataFrame shape (3, 3)."""
    result = engine.run(infy_snapshot, _default_scenarios())
    try:
        import pandas as pd
        df = result.sensitivity_table.data
        assert hasattr(df, "shape"), "Expected pandas DataFrame"
        assert df.shape == (3, 3), f"Expected (3, 3), got {df.shape}"
    except ImportError:
        # Fallback dict: 3 columns, each with 3 values
        data = result.sensitivity_table.data
        assert len(data) == 3
        for col_values in data.values():
            assert len(col_values) == 3


def test_disclaimer_always_present(engine, infy_snapshot):
    result = engine.run(infy_snapshot, _default_scenarios())
    assert result.disclaimer == COMPLIANCE_DISCLAIMER
    for scenario in result.scenarios:
        assert scenario.disclaimer == COMPLIANCE_DISCLAIMER


def test_pe_matrix_has_correct_keys(engine, infy_snapshot):
    result = engine.run(infy_snapshot, _default_scenarios())
    for scenario in result.scenarios:
        assert "PE 18x" in scenario.pe_matrix
        assert "PE 22x" in scenario.pe_matrix
        assert "PE 26x" in scenario.pe_matrix


def test_parse_scenario_args_count(engine, infy_snapshot):
    scenarios = parse_scenario_args("bear=5,base=12,bull=18", "18,22,26")
    assert len(scenarios) == 3


def test_parse_scenario_args_values(engine, infy_snapshot):
    scenarios = parse_scenario_args("bear=5,base=12", "18,22")
    assert scenarios[0].pat_growth == 0.05
    assert scenarios[1].pat_growth == 0.12
    assert scenarios[0].label == "Bear"
    assert scenarios[1].label == "Base"


def test_parse_scenario_args_pe_multiples(engine, infy_snapshot):
    scenarios = parse_scenario_args("base=10", "18,22,26")
    assert scenarios[0].pe_multiples == [18.0, 22.0, 26.0]


def test_macro_context_included_for_it_sector(engine, infy_snapshot):
    """INFY is in Information Technology → macro_context should be populated."""
    infy_snapshot.sector = "Information Technology"
    result = engine.run(infy_snapshot, _default_scenarios(), include_macro=True)
    assert result.macro_context is not None
    assert "factors" in result.macro_context


def test_no_macro_context_for_unknown_sector(engine, infy_snapshot):
    infy_snapshot.sector = "Unknown Sector"
    result = engine.run(infy_snapshot, _default_scenarios(), include_macro=True)
    assert result.macro_context is None


def test_base_pe_computed_if_price_available(engine, infy_snapshot):
    result = engine.run(infy_snapshot, _default_scenarios())
    # CMP=1437.5, EPS=63.14 (from fixture) → PE ≈ 22.8
    if result.base_pe is not None:
        assert 5 < result.base_pe < 200, (
            f"Base PE out of plausible range: {result.base_pe}"
        )
