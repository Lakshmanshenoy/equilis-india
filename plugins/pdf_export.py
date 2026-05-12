"""
PDF Report Generator — equilis-india
Uses Weasyprint (HTML → PDF) + Jinja2 templates.

Replaces the legacy fpdf2 implementation.

Public API
----------
    exporter = PDFReportExporter(dest_dir="~/Downloads")
    path = exporter.export_analysis(snapshot)          # CompanySnapshot → PDF
    path = exporter.export_peer_comparison(peer_result)
    path = exporter.export_scenario(scenario_result, snapshot)
    html = exporter.render_html(snapshot)              # debug / preview
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from core.compliance import render_disclaimer

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent / "skills" / "equity-research" / "templates"
DEFAULT_DEST   = Path.home() / "Downloads"
REPORT_VERSION = "1.0.0"

DISCLAIMER_FULL = render_disclaimer(ticker="TICKER")


# ---------------------------------------------------------------------------
# Jinja2 filters
# ---------------------------------------------------------------------------

def _fmt_inr(val) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if abs(v) >= 1_00_000:
            return f"₹{v / 1_00_000:,.2f}L Cr"
        return f"₹{v:,.0f} Cr"
    except Exception:
        return str(val)


def _fmt_pct(val, decimals=1) -> str:
    if val is None:
        return "N/A"
    try:
        return f"{float(val) * 100:.{decimals}f}%"
    except Exception:
        return str(val)


def _fmt_ratio(val, decimals=2) -> str:
    if val is None:
        return "N/A"
    try:
        return f"{float(val):.{decimals}f}x"
    except Exception:
        return str(val)


def _fmt_signed(val, pct=True) -> str:
    if val is None:
        return "N/A"
    try:
        v = float(val)
        sign = "+" if v >= 0 else ""
        suffix = "%" if pct else ""
        return f"{sign}{v:.1f}{suffix}"
    except Exception:
        return str(val)


def _fmt_na(val, fallback="N/A") -> str:
    return fallback if val is None else str(val)


def _fmt_date(val) -> str:
    if val is None:
        return ""
    if isinstance(val, str):
        return val
    try:
        return val.strftime("%-d %b %Y")
    except Exception:
        return str(val)


def _signal_class(signal: str) -> str:
    mapping = {
        "HIGH": "signal-high",
        "MEDIUM": "signal-med",
        "LOW": "signal-low",
        "RED": "signal-red",
        "SAFE": "signal-high",
        "GREY": "signal-med",
        "DISTRESS": "signal-red",
    }
    return mapping.get(str(signal).upper(), "signal-med")


def _make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["inr"]        = _fmt_inr
    env.filters["pct"]        = _fmt_pct
    env.filters["ratio"]      = _fmt_ratio
    env.filters["signed"]     = _fmt_signed
    env.filters["na"]         = _fmt_na
    env.filters["date_fmt"]   = _fmt_date
    env.filters["signal_cls"] = _signal_class
    return env


# ---------------------------------------------------------------------------
# Context builders
# ---------------------------------------------------------------------------

def _flatten_ratios(snapshot) -> SimpleNamespace:
    """
    Build a flat SimpleNamespace with all ratio fields sourced from
    snapshot.ratios (a RatioSet) or computed on-the-fly via EquityAnalyzer.
    Also picks up income-level fields (eps_ttm) that live on the snapshot.
    """
    ratioset = getattr(snapshot, "ratios", None)
    if ratioset is None:
        try:
            from core.analyzer import EquityAnalyzer
            ratioset = EquityAnalyzer().compute_all(snapshot)
        except Exception:
            ratioset = None

    profitability = getattr(ratioset, "profitability", None) if ratioset else None
    leverage      = getattr(ratioset, "leverage",      None) if ratioset else None
    valuation     = getattr(ratioset, "valuation",     None) if ratioset else None
    efficiency    = getattr(ratioset, "efficiency",    None) if ratioset else None

    income = getattr(snapshot, "income", None)

    return SimpleNamespace(
        # Profitability
        roe              = getattr(profitability, "roe",           None),
        roa              = getattr(profitability, "roa",           None),
        roce             = getattr(profitability, "roce",          None),
        gross_margin     = getattr(profitability, "gross_margin",  None),
        ebitda_margin    = getattr(profitability, "ebitda_margin", None),
        pat_margin       = getattr(profitability, "pat_margin",    None),
        # Leverage
        debt_to_equity   = getattr(leverage, "debt_to_equity",    None),
        net_debt_ebitda  = getattr(leverage, "debt_to_ebitda",    None),
        interest_coverage = getattr(leverage, "interest_coverage", None),
        current_ratio    = getattr(leverage, "current_ratio",     None),
        quick_ratio      = getattr(leverage, "quick_ratio",       None),
        # Valuation
        pe_ttm           = getattr(valuation, "pe_ttm",   None),
        pb               = getattr(valuation, "pb",       None),
        ev_ebitda        = getattr(valuation, "ev_ebitda", None),
        ev_sales         = getattr(valuation, "ev_sales", None),
        peg              = getattr(valuation, "peg",      None),
        div_yield        = getattr(valuation, "div_yield", None),
        # Efficiency
        receivables_days       = getattr(efficiency, "receivables_days",       None),
        inventory_days         = getattr(efficiency, "inventory_days",         None),
        payables_days          = getattr(efficiency, "payables_days",          None),
        cash_conversion_cycle  = getattr(efficiency, "cash_conversion_cycle",  None),
        asset_turnover         = getattr(efficiency, "asset_turnover",         None),
        # Income-level
        eps_ttm    = getattr(income, "eps_ttm",    None) if income else None,
        revenue_ttm = getattr(income, "revenue_ttm", None) if income else None,
        pat_ttm     = getattr(income, "pat_ttm",     None) if income else None,
        ebitda_ttm  = getattr(income, "ebitda_ttm",  None) if income else None,
    )


def _get_dupont(snapshot) -> object:
    """Return DuPontResult from analyzer, or a stub if unavailable."""
    ratioset = getattr(snapshot, "ratios", None)
    if ratioset is None:
        try:
            from core.analyzer import EquityAnalyzer
            ratioset = EquityAnalyzer().compute_all(snapshot)
        except Exception:
            return None
    # Prefer multi-year result if available
    dupont_result = getattr(ratioset, "dupont_result", None)
    if dupont_result is not None:
        return dupont_result
    # Fall back to single-year decomposition
    dupont = getattr(ratioset, "dupont", None)
    if dupont:
        try:
            from core.models.ratios import DuPontResult
            return DuPontResult(by_year=[], driver_observation="", trend_note="")
        except Exception:
            return None
    return None


def _get_cf_quality(snapshot) -> object:
    """Return CashFlowQualityResult from analyzer or a stub."""
    ratioset = getattr(snapshot, "ratios", None)
    if ratioset is None:
        try:
            from core.analyzer import EquityAnalyzer
            ratioset = EquityAnalyzer().compute_all(snapshot)
        except Exception:
            return None
    cfq_result = getattr(ratioset, "cf_quality_result", None)
    if cfq_result is not None:
        return cfq_result
    cf_quality = getattr(ratioset, "cash_flow_quality", None)
    if cf_quality:
        try:
            from core.models.ratios import CashFlowQualityResult
            return CashFlowQualityResult(
                by_year=[],
                overall_signal=getattr(cf_quality, "quality_signal", "UNKNOWN"),
                observations=[getattr(cf_quality, "note", "")],
            )
        except Exception:
            return None
    return None


def _get_red_flags(snapshot) -> object:
    """Return RedFlagScanResult from analyzer."""
    ratioset = getattr(snapshot, "ratios", None)
    if ratioset is None:
        try:
            from core.analyzer import EquityAnalyzer
            ratioset = EquityAnalyzer().compute_all(snapshot)
        except Exception:
            return None
    return getattr(ratioset, "red_flag_result", None)


def _get_altman(snapshot) -> Optional[dict]:
    """Return Altman Z-Score dict from analyzer."""
    ratioset = getattr(snapshot, "ratios", None)
    if ratioset is None:
        try:
            from core.analyzer import EquityAnalyzer
            ratioset = EquityAnalyzer().compute_all(snapshot)
        except Exception:
            return None
    return getattr(ratioset, "altman_result", None)


def _get_ticker(snapshot) -> str:
    """Extract ticker from any snapshot-like object."""
    ticker = getattr(snapshot, "ticker", None)
    if ticker:
        return str(ticker).upper()
    company = getattr(snapshot, "company", None)
    if company:
        return str(getattr(company, "ticker", "UNKNOWN")).upper()
    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Main exporter
# ---------------------------------------------------------------------------

class PDFReportExporter:
    """
    Generates PDF reports from CompanySnapshot / peer / scenario data
    using Weasyprint (HTML → PDF) and Jinja2 templates.
    """

    def __init__(self, dest_dir: Optional[str] = None):
        self.dest_dir    = Path(dest_dir).expanduser() if dest_dir else DEFAULT_DEST
        self.dest_dir.mkdir(parents=True, exist_ok=True)
        self.env         = _make_env()
        self.font_config = FontConfiguration()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def export_analysis(self, snapshot, dest_dir: Optional[str] = None) -> str:
        """Render a full company analysis report to PDF. Returns the file path."""
        context  = self._analysis_context(snapshot)
        html_str = self._render("report.html.j2", context)
        ticker   = _get_ticker(snapshot)
        return self._to_pdf(html_str, f"{ticker}_equilis", dest_dir)

    def export_peer_comparison(self, peer_result, dest_dir: Optional[str] = None) -> str:
        """Render a peer comparison PDF. Returns the file path."""
        context = self._peer_context(peer_result)
        tickers = getattr(peer_result, "tickers", None) or [getattr(peer_result, "ticker", "PEER")]
        label   = "PEER_" + "_".join(str(t) for t in tickers[:3])
        html_str = self._render("peer_report.html.j2", context)
        return self._to_pdf(html_str, label, dest_dir)

    def export_scenario(self, scenario_result, snapshot, dest_dir: Optional[str] = None) -> str:
        """Render a scenario analysis PDF. Returns the file path."""
        context  = {**self._analysis_context(snapshot), **self._scenario_context(scenario_result)}
        html_str = self._render("scenario_report.html.j2", context)
        ticker   = _get_ticker(snapshot)
        return self._to_pdf(html_str, f"{ticker}_SCENARIO", dest_dir)

    def render_html(self, snapshot) -> str:
        """Return the rendered HTML string for debugging/preview."""
        return self._render("report.html.j2", self._analysis_context(snapshot))

    # ------------------------------------------------------------------
    # Context builders
    # ------------------------------------------------------------------

    def _analysis_context(self, snapshot) -> dict:
        ticker       = _get_ticker(snapshot)
        company_name = getattr(snapshot, "company_name", "") or ticker

        company = SimpleNamespace(
            ticker   = ticker,
            name     = company_name,
            sector   = getattr(snapshot, "sector",   ""),
            industry = getattr(snapshot, "industry", ""),
            bse_code = getattr(snapshot, "bse_code", None),
            exchange = getattr(snapshot, "exchange", "NSE"),
        )

        return {
            "report_date":       datetime.now(),
            "report_version":    REPORT_VERSION,
            "disclaimer":        render_disclaimer(
                ticker=ticker,
                data_date=getattr(snapshot, "snapshot_date", None),
                prepared_at=datetime.now(),
            ),
            "company":           company,
            "price":             getattr(snapshot, "price",            None),
            "market":            getattr(snapshot, "market",           None),
            "ratios":            _flatten_ratios(snapshot),
            "dupont":            _get_dupont(snapshot),
            "cf_quality":        _get_cf_quality(snapshot),
            "red_flags":         _get_red_flags(snapshot),
            "altman":            _get_altman(snapshot),
            "history":           getattr(snapshot, "history",          []),
            "validation_issues": getattr(snapshot, "validation_issues", []),
            "sources":           getattr(snapshot, "sources",          []),
            "scenarios":         getattr(snapshot, "scenarios",        None),
            "macro_context":     getattr(snapshot, "macro_context",    None),
        }

    def _peer_context(self, peer_result) -> dict:
        tickers = getattr(peer_result, "tickers", None) or [getattr(peer_result, "ticker", "PEER")]
        return {
            "report_date":      datetime.now(),
            "report_version":   REPORT_VERSION,
            "disclaimer":       DISCLAIMER_FULL,
            "tickers":          tickers,
            "comparison_table": getattr(peer_result, "comparison_table", {}),
            "sector_medians":   getattr(peer_result, "sector_medians",   {}),
            "snapshots":        getattr(peer_result, "snapshots",        {}),
            "errors":           getattr(peer_result, "errors",           {}),
            "sources":          getattr(peer_result, "sources",          {}),
            # legacy fields kept for backward compat
            "ticker":           getattr(peer_result, "ticker",       ""),
            "company_name":     getattr(peer_result, "company_name", ""),
            "sector":           getattr(peer_result, "sector",       ""),
            "peers":            getattr(peer_result, "peers",        []),
        }

    def _scenario_context(self, scenario_result) -> dict:
        return {
            "scenario_result":   scenario_result,
            "scenarios":         getattr(scenario_result, "scenarios",         []),
            "sensitivity_table": getattr(scenario_result, "sensitivity_table", {}),
            "macro_context":     getattr(scenario_result, "macro_context",     None),
        }

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------

    def _render(self, template_name: str, context: dict) -> str:
        tpl = self.env.get_template(template_name)
        return tpl.render(**context)

    def _to_pdf(self, html_str: str, label: str, dest_dir: Optional[str]) -> str:
        folder   = Path(dest_dir).expanduser() if dest_dir else self.dest_dir
        folder.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{label.upper()}_{date_str}.pdf"
        filepath = folder / filename
        HTML(string=html_str, base_url=str(TEMPLATES_DIR)).write_pdf(
            str(filepath),
            font_config=self.font_config,
            presentational_hints=True,
        )
        return str(filepath)
