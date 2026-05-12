"""
tests/test_pdf_export.py
Tests for PDFReportExporter — file creation, filename format, peer export.

Requires fpdf2 to be installed. Tests are skipped gracefully if not available.
No live data calls — uses CompanySnapshot fixtures from conftest.py.
"""

import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _fpdf_available():
    try:
        import fpdf  # noqa: F401
        return True
    except ImportError:
        return False


pytestmark = pytest.mark.skipif(
    not _fpdf_available(), reason="fpdf2 not installed"
)


@pytest.fixture
def exporter():
    from plugins.pdf_export import PDFReportExporter
    return PDFReportExporter()


def test_pdf_export_creates_file(exporter, infy):
    """export_analysis() should create a non-empty PDF file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = exporter.export_analysis(infy, dest_dir=tmpdir)
        assert os.path.exists(filepath), f"PDF file not found: {filepath}"
        assert filepath.endswith(".pdf"), f"Expected .pdf extension, got: {filepath}"
        size = os.path.getsize(filepath)
        assert size > 1_000, f"PDF too small ({size} bytes) — likely empty"


def test_pdf_filename_contains_ticker(exporter, infy):
    """The filename must contain the ticker (uppercase) and 'equilis'."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = exporter.export_analysis(infy, dest_dir=tmpdir)
        basename = os.path.basename(filepath)
        assert "INFY" in basename.upper(), f"Ticker 'INFY' not in filename: {basename}"
        assert "equilis" in basename.lower(), f"'equilis' not in filename: {basename}"


def test_pdf_peer_export(exporter):
    """export_peer_comparison() should create a file with 'PEER' in the filename."""
    from types import SimpleNamespace
    peer_result = SimpleNamespace(
        ticker="INFY",
        company_name="Infosys Limited",
        sector="Information Technology",
        universe_size=10,
        peers=[],
        data_quality=[],
        macro_context=None,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = exporter.export_peer_comparison(peer_result, dest_dir=tmpdir)
        basename = os.path.basename(filepath)
        assert os.path.exists(filepath), f"Peer PDF not created: {filepath}"
        assert "PEER" in basename.upper(), f"'PEER' not in filename: {basename}"
