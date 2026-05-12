"""Tests for report rendering sections and diagnostics."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.renderer import ReportRenderer


def test_render_includes_source_health_diagnostics(infy):
    renderer = ReportRenderer(output_dir="/tmp")
    md = renderer.render_markdown(
        snapshot=infy,
        fetch_errors={
            "financials": "No source returned data for financials.",
            "shareholding": "No source returned data for shareholding.",
        },
    )

    assert "Source Health Diagnostics" in md
    assert "Financials" in md
    assert "Shareholding" in md
