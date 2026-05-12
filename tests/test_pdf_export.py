"""
tests/test_pdf_export.py
Tests for PDFReportExporter — Weasyprint + Jinja2 HTML/PDF pipeline.

Uses CompanySnapshot fixtures from conftest.py (the `infy` fixture).
No live data calls.
"""

import os
import sys
import tempfile
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def infy_analysis(infy):
    """Alias: infy CompanySnapshot used as the analysis object passed to exporter."""
    return infy


@pytest.fixture
def peer_result_fixture():
    """Minimal peer result that satisfies the new peer_context builder."""
    return SimpleNamespace(
        ticker="INFY",
        tickers=["INFY", "TCS"],
        company_name="Infosys Limited",
        sector="Information Technology",
        universe_size=10,
        peers=[],
        comparison_table={},
        sector_medians={},
        snapshots={},
        errors={},
        sources={},
        data_quality=[],
        macro_context=None,
    )


# ---------------------------------------------------------------------------
# HTML rendering tests (fast — no PDF conversion)
# ---------------------------------------------------------------------------

def test_html_render_no_exception(infy_analysis):
    """render_html() must not raise and must return a valid HTML string."""
    from plugins.pdf_export import PDFReportExporter
    exporter = PDFReportExporter()
    html = exporter.render_html(infy_analysis)
    assert "<html" in html, "Output must be an HTML document"
    assert "INFY" in html or "Infosys" in html, "Ticker or company name must appear"


def test_disclaimer_in_html(infy_analysis):
    """The rendered HTML must contain the full disclaimer text."""
    from plugins.pdf_export import PDFReportExporter
    exporter = PDFReportExporter()
    html = exporter.render_html(infy_analysis)
    assert "does not constitute investment advice" in html.lower() or \
           "not investment advice" in html.lower(), \
           "Disclaimer phrase missing"
    assert "sebi" in html.lower(), "SEBI reference missing from disclaimer"


def test_html_contains_report_date(infy_analysis):
    """HTML must contain a non-empty report date."""
    from plugins.pdf_export import PDFReportExporter
    exporter = PDFReportExporter()
    html = exporter.render_html(infy_analysis)
    # Report date is formatted like "15 Jan 2025"
    import re
    assert re.search(r"\d{4}", html), "Year not found in rendered HTML"


# ---------------------------------------------------------------------------
# PDF output tests
# ---------------------------------------------------------------------------

def test_pdf_creates_file(infy_analysis):
    """export_analysis() must create a non-empty PDF file."""
    from plugins.pdf_export import PDFReportExporter
    exporter = PDFReportExporter()
    with tempfile.TemporaryDirectory() as d:
        path = exporter.export_analysis(infy_analysis, dest_dir=d)
        assert os.path.exists(path), f"PDF not created: {path}"
        assert path.endswith(".pdf"), f"Expected .pdf extension, got: {path}"
        assert os.path.getsize(path) > 15_000, \
            f"PDF suspiciously small: {os.path.getsize(path)} bytes"


def test_pdf_filename_format(infy_analysis):
    """Filename must contain ticker, 'equilis', and end with .pdf."""
    from plugins.pdf_export import PDFReportExporter
    exporter = PDFReportExporter()
    with tempfile.TemporaryDirectory() as d:
        path = exporter.export_analysis(infy_analysis, dest_dir=d)
        fname = os.path.basename(path)
        assert "INFY" in fname, f"Ticker 'INFY' not in filename: {fname}"
        assert "equilis" in fname.lower(), f"'equilis' not in filename: {fname}"
        assert fname.endswith(".pdf"), f"Expected .pdf extension: {fname}"


EXPECTED_PDF_SIZE_MIN = 15_000
EXPECTED_PDF_SIZE_MAX = 5_000_000


def test_pdf_size_in_expected_range(infy_analysis):
    """PDF must be within reasonable byte range (80 KB – 2 MB)."""
    from plugins.pdf_export import PDFReportExporter
    exporter = PDFReportExporter()
    with tempfile.TemporaryDirectory() as d:
        path = exporter.export_analysis(infy_analysis, dest_dir=d)
        size = os.path.getsize(path)
        assert EXPECTED_PDF_SIZE_MIN <= size <= EXPECTED_PDF_SIZE_MAX, \
            f"PDF size {size} bytes outside expected range [{EXPECTED_PDF_SIZE_MIN}, {EXPECTED_PDF_SIZE_MAX}]"


def test_peer_pdf_creates_file(peer_result_fixture):
    """export_peer_comparison() must create a file with 'PEER' in the filename."""
    from plugins.pdf_export import PDFReportExporter
    exporter = PDFReportExporter()
    with tempfile.TemporaryDirectory() as d:
        path = exporter.export_peer_comparison(peer_result_fixture, dest_dir=d)
        assert os.path.exists(path), f"Peer PDF not created: {path}"
        fname = os.path.basename(path)
        assert "PEER" in fname.upper(), f"'PEER' not in filename: {fname}"
        assert path.endswith(".pdf"), f"Expected .pdf extension: {path}"


def test_peer_html_contains_tickers(peer_result_fixture):
    """Peer HTML must contain the ticker names from the peer_result."""
    from plugins.pdf_export import PDFReportExporter
    exporter = PDFReportExporter()
    ctx = exporter._peer_context(peer_result_fixture)
    html = exporter._render("peer_report.html.j2", ctx)
    assert "INFY" in html or "TCS" in html, "Peer tickers not found in rendered HTML"
