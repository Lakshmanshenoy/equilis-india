"""
core/renderer.py
ReportRenderer — generates markdown (and optionally PDF) analysis reports.

Outputs are saved to ~/Downloads/equilis-reports/ per workspace convention.
Every report ends with the compliance footer. No buy/sell/hold language.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional

from core.compliance import render_disclaimer
from core.models.company import CompanySnapshot
from core.models.ratios import (
    CashFlowQualityResult,
    DuPontResult,
    RatioSet,
    RedFlagScanResult,
)
from core.models.scenario import ScenarioResult
from core.validator import ValidationIssue

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.expanduser("~/Downloads/equilis-reports")

COMPLIANCE_FOOTER = render_disclaimer(ticker="TICKER")


def _pct(value: Optional[float]) -> str:
    if value is None:
        return "N/A"
    return f"{value * 100:.1f}%"


def _val(value: Optional[float], decimals: int = 2, suffix: str = "") -> str:
    if value is None:
        return "N/A"
    return f"{value:,.{decimals}f}{suffix}"


class ReportRenderer:
    """
    Renders analysis context (snapshot + ratios + scenarios + flags) to markdown.
    """

    def __init__(self, output_dir: str = OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def render_markdown(
        self,
        snapshot: CompanySnapshot,
        ratios: Optional[RatioSet] = None,
        scenarios: Optional[ScenarioResult] = None,
        red_flags: Optional[list[dict]] = None,
        validation_issues: Optional[list[ValidationIssue]] = None,
        # Phase 2 optional sections
        dupont_trend: Optional[DuPontResult] = None,
        cf_quality_trend: Optional[CashFlowQualityResult] = None,
        red_flag_result: Optional[RedFlagScanResult] = None,
        peer_result=None,  # PeerComparisonResult — avoid circular import
    ) -> str:
        """Build and return the full markdown report string."""
        sections = [
            self._header_section(snapshot),
            self._price_market_section(snapshot),
        ]
        if validation_issues:
            sections.append(self._validation_banner(validation_issues))
        if ratios:
            sections.append(self._ratios_table(ratios))
            if ratios.dupont:
                sections.append(self._dupont_section(ratios))
            if ratios.cash_flow_quality:
                sections.append(self._cash_flow_quality_section(ratios))
        # Phase 2 trend sections (multi-year)
        if dupont_trend:
            sections.append(self._dupont_trend_section(dupont_trend))
        if cf_quality_trend:
            sections.append(self._cf_quality_trend_section(cf_quality_trend))
        if red_flag_result:
            sections.append(self._red_flag_result_section(red_flag_result))
        elif red_flags:
            sections.append(self._red_flags_section(red_flags))
        if scenarios:
            sections.append(self._scenarios_section(scenarios))
        if peer_result:
            sections.append(self._peer_section(peer_result))
        sections.append(self._sources_section(snapshot))
        sections.append(self._footer(snapshot))
        return "\n\n".join(filter(None, sections))

    def save(
        self,
        content: str,
        ticker: str,
        extension: str = "md",
    ) -> str:
        """Save rendered content to ~/Downloads/equilis-reports/. Returns file path."""
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{ticker.upper()}_{date_str}.{extension}"
        out_path = os.path.join(self.output_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"[renderer] Report saved: {out_path}")
        return out_path

    # ── Section builders ──────────────────────────────────────────────────────

    def _header_section(self, s: CompanySnapshot) -> str:
        name = s.company_name or s.ticker
        sector = f" | {s.sector}" if s.sector else ""
        return (
            f"# {name} ({s.ticker} : {s.exchange}){sector}\n"
            f"*Snapshot date: {s.snapshot_date.strftime('%d %b %Y') if s.snapshot_date else 'N/A'}*"
        )

    def _price_market_section(self, s: CompanySnapshot) -> str:
        lines = ["## Price & Market Data", ""]
        if s.price:
            lines += [
                f"| Metric | Value |",
                "| --- | --- |",
                f"| CMP | ₹{_val(s.price.cmp)} |",
                f"| 52W High | ₹{_val(s.price.week52_high)} |",
                f"| 52W Low | ₹{_val(s.price.week52_low)} |",
                f"| Price Source | {s.price.source} |",
                f"| Price Fetched | {s.price.fetched_at.strftime('%d %b %Y %H:%M') if s.price.fetched_at else 'N/A'} |",
            ]
        if s.market:
            lines += [
                f"| Market Cap | ₹{_val(s.market.market_cap, 0)} Cr |",
                f"| Enterprise Value | ₹{_val(s.market.enterprise_value, 0)} Cr |",
                f"| Shares Outstanding | {_val(s.market.shares_outstanding, 2)} M |",
            ]
        return "\n".join(lines)

    def _validation_banner(self, issues: list[ValidationIssue]) -> str:
        from core.validator import Severity
        lines = ["## ⚠ Data Quality Notes", ""]
        for issue in issues:
            if issue.severity in (Severity.WARNING, Severity.ERROR):
                icon = "🔴" if issue.severity == Severity.ERROR else "🟡"
                lines.append(f"- {icon} **{issue.field}**: {issue.message}")
        return "\n".join(lines) if len(lines) > 2 else ""

    def _ratios_table(self, ratios: RatioSet) -> str:
        rows = ["## Key Financial Ratios", "", "| Category | Metric | Value |", "| --- | --- | --- |"]

        def add(category, metric, value):
            rows.append(f"| {category} | {metric} | {value} |")

        p = ratios.profitability
        if p:
            add("Profitability", "Gross Margin", _pct(p.gross_margin))
            add("Profitability", "EBITDA Margin", _pct(p.ebitda_margin))
            add("Profitability", "PAT Margin", _pct(p.pat_margin))
            add("Profitability", "ROE", _pct(p.roe))
            add("Profitability", "ROA", _pct(p.roa))
            add("Profitability", "ROCE", _pct(p.roce))

        l = ratios.leverage
        if l:
            add("Leverage", "Debt/Equity", _val(l.debt_to_equity, 2, "x"))
            add("Leverage", "Debt/EBITDA", _val(l.debt_to_ebitda, 2, "x"))
            add("Leverage", "Interest Coverage", _val(l.interest_coverage, 2, "x"))
            add("Leverage", "Current Ratio", _val(l.current_ratio, 2, "x"))
            add("Leverage", "Quick Ratio", _val(l.quick_ratio, 2, "x"))

        v = ratios.valuation
        if v:
            add("Valuation", "P/E (TTM)", _val(v.pe_ttm, 1, "x"))
            add("Valuation", "P/B", _val(v.pb, 2, "x"))
            add("Valuation", "EV/EBITDA", _val(v.ev_ebitda, 1, "x"))
            add("Valuation", "EV/Sales", _val(v.ev_sales, 2, "x"))
            add("Valuation", "PEG", _val(v.peg, 2))
            add("Valuation", "Dividend Yield", _pct(v.div_yield))

        e = ratios.efficiency
        if e:
            add("Efficiency", "Receivables Days", _val(e.receivables_days, 0, " days"))
            add("Efficiency", "Inventory Days", _val(e.inventory_days, 0, " days"))
            add("Efficiency", "Payables Days", _val(e.payables_days, 0, " days"))
            add("Efficiency", "Cash Conversion Cycle", _val(e.cash_conversion_cycle, 0, " days"))
            add("Efficiency", "Asset Turnover", _val(e.asset_turnover, 2, "x"))

        return "\n".join(rows)

    def _dupont_section(self, ratios: RatioSet) -> str:
        d = ratios.dupont
        if not d:
            return ""
        return (
            "## DuPont Decomposition\n\n"
            f"ROE = Net Profit Margin × Asset Turnover × Equity Multiplier\n\n"
            f"| Component | Value |\n"
            f"| --- | --- |\n"
            f"| Net Profit Margin | {_pct(d.net_profit_margin)} |\n"
            f"| Asset Turnover | {_val(d.asset_turnover, 2, 'x')} |\n"
            f"| Equity Multiplier | {_val(d.equity_multiplier, 2, 'x')} |\n"
            f"| **ROE (DuPont)** | **{_pct(d.roe_dupont)}** |\n"
            f"| ROE (Reported) | {_pct(d.roe_reported)} |"
        )

    def _cash_flow_quality_section(self, ratios: RatioSet) -> str:
        cq = ratios.cash_flow_quality
        if not cq:
            return ""
        signal_icon = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(cq.quality_signal, "⚪")
        return (
            f"## Cash Flow Quality\n\n"
            f"{signal_icon} **Signal: {cq.quality_signal}**\n\n"
            f"{cq.note}"
        )

    def _red_flags_section(self, flags: list[dict]) -> str:
        if not flags:
            return ""
        # Support both old format (flag/severity/evidence keys) and new format (flag_id/category/severity/observation/source keys)
        severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "RED": "🔴", "MEDIUM": "🟡", "YELLOW": "🟡"}
        lines = ["## Red Flag Scan", ""]
        for f in flags:
            icon = severity_icon.get(f.get("severity", "MEDIUM"), "⚪")
            flag_label = f.get("flag_id") or f.get("flag", "Unknown")
            evidence   = f.get("observation") or f.get("evidence", "")
            lines.append(
                f"- {icon} **[{f.get('severity')}]** {flag_label}  "
                f"*{evidence}*"
            )
        return "\n".join(lines)

    def _red_flag_result_section(self, result: RedFlagScanResult) -> str:
        """Phase 2 red flag section using structured RedFlagScanResult."""
        lines = [
            "## Red Flag Scan (Phase 2)",
            "",
            f"> {result.summary}",
            "",
            f"**Summary**: 🔴 {result.red_count} high-priority · "
            f"🟡 {result.yellow_count} noteworthy",
            "",
        ]
        if result.flags:
            severity_icon = {"RED": "🔴", "YELLOW": "🟡"}
            lines += ["| Severity | ID | Category | Observation | Source |", "| --- | --- | --- | --- | --- |"]
            for f in result.flags:
                icon = severity_icon.get(f.get("severity", ""), "⚪")
                obs = f.get("observation", "").replace("|", "\\|")
                lines.append(
                    f"| {icon} {f.get('severity')} | {f.get('flag_id')} | "
                    f"{f.get('category')} | {obs} | {f.get('source')} |"
                )
        else:
            lines.append("*No flags raised — all checks passed.*")
        return "\n".join(lines)

    def _dupont_trend_section(self, result: DuPontResult) -> str:
        """Multi-year DuPont table (Phase 2)."""
        if not result.by_year:
            return ""
        lines = [
            "## DuPont Decomposition — Multi-Year Trend",
            "",
            "> ROE = Net Profit Margin × Asset Turnover × Equity Multiplier",
            "",
            "| Year | NPM | Asset Turnover | Equity Multiplier | ROE (DuPont) | ROE (Reported) |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for yr in result.by_year:
            lines.append(
                f"| {yr['fiscal_year']} "
                f"| {yr['net_profit_margin']:.1%} "
                f"| {yr['asset_turnover']:.2f}x "
                f"| {yr['equity_multiplier']:.2f}x "
                f"| {yr['roe_dupont']:.1%} "
                f"| {yr['roe_reported']:.1%} |"
            )
        lines += ["", f"**Driver**: {result.driver_observation}", "", f"**Trend**: {result.trend_note}"]
        return "\n".join(lines)

    def _cf_quality_trend_section(self, result: CashFlowQualityResult) -> str:
        """Multi-year CFO quality table (Phase 2)."""
        if not result.by_year:
            return ""
        signal_icon = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴", "RED": "🔴", "INSUFFICIENT_DATA": "⚪"}
        icon = signal_icon.get(result.overall_signal, "⚪")
        lines = [
            "## Cash Flow Quality — Multi-Year Trend",
            "",
            f"{icon} **Overall Signal: {result.overall_signal}**",
            "",
            "| Year | CFO (₹Cr) | PAT (₹Cr) | CFO/PAT | Signal |",
            "| --- | --- | --- | --- | --- |",
        ]
        for yr in result.by_year:
            cfo_pat_str = f"{yr['cfo_pat']:.2f}" if yr["cfo_pat"] is not None else "N/A"
            yr_icon = signal_icon.get(yr["signal"], "⚪")
            lines.append(
                f"| {yr['fiscal_year']} "
                f"| ₹{yr['cfo_cr']:,.0f} "
                f"| ₹{yr['pat_cr']:,.0f} "
                f"| {cfo_pat_str} "
                f"| {yr_icon} {yr['signal']} |"
            )
        if result.observations:
            lines += ["", "**Observations:**", ""]
            for obs in result.observations:
                lines.append(f"- {obs}")
        return "\n".join(lines)

    def _peer_section(self, result) -> str:
        """Peer comparison table (Phase 2). result: PeerComparisonResult."""
        if not result or not result.comparison_table:
            return ""
        tickers = [t for t in result.tickers if t in result.snapshots]
        lines = [
            "## Peer Comparison",
            "",
            f"*Peer group: {', '.join(result.tickers)}*",
            "",
        ]
        if result.errors:
            lines.append("**Errors (data unavailable):**")
            for t, err in result.errors.items():
                lines.append(f"- {t}: {err}")
            lines.append("")

        # Build table header
        col_header = "| Metric | " + " | ".join(tickers) + " | Sector Median |"
        col_sep    = "| --- |" + " --- |" * (len(tickers) + 1)
        lines += [col_header, col_sep]

        for metric, row in result.comparison_table.items():
            cells = [str(row.get(t)) if row.get(t) is not None else "N/A" for t in tickers]
            median_val = result.sector_medians.get(metric)
            median_str = f"{median_val:.2f}" if median_val is not None else "N/A"
            lines.append(f"| {metric} | " + " | ".join(cells) + f" | {median_str} |")
        return "\n".join(lines)

    def _scenarios_section(self, sc: ScenarioResult) -> str:
        lines = [
            "## Earnings Scenarios",
            "",
            "> All values are mathematical outputs of stated assumptions only. "
            "Not forecasts or price targets.",
            "",
            f"Base PAT (TTM): ₹{_val(sc.base_pat_ttm, 0)} Cr | "
            f"Base EPS: ₹{_val(sc.base_eps_ttm)} | "
            f"Trailing P/E: {_val(sc.base_pe_ttm, 1)}x",
            "",
        ]
        for scenario in sc.scenarios:
            lines.append(f"### {scenario.label} Case ({scenario.assumption_pat_growth} PAT CAGR)")
            lines.append("")
            lines.append(f"Projected PAT: ₹{_val(scenario.projected_pat_cr, 0)} Cr | "
                         f"Projected EPS: ₹{_val(scenario.projected_eps)}")
            if scenario.pe_scenarios:
                lines.append("")
                lines.append("| PE Multiple | Implied Value |")
                lines.append("| --- | --- |")
                for pe_key, val in scenario.pe_scenarios.items():
                    lines.append(f"| {pe_key} | ₹{val:,.1f} |")
            lines.append("")
        lines.append(f"> {sc.compliance_note}")
        return "\n".join(lines)

    def _sources_section(self, s: CompanySnapshot) -> str:
        if not s.sources:
            return ""
        lines = ["## Data Sources", ""]
        for src in s.sources:
            fallback = " *(fallback)*" if src.is_fallback else ""
            ts = src.fetched_at.strftime("%d %b %Y %H:%M") if src.fetched_at else "N/A"
            lines.append(
                f"- **{src.source_name}**{fallback}: [{src.source_url}]({src.source_url}) "
                f"— fetched {ts}"
            )
        return "\n".join(lines)

    def _footer(self, snapshot: CompanySnapshot) -> str:
        return render_disclaimer(
            ticker=snapshot.ticker,
            data_date=snapshot.snapshot_date,
            prepared_at=datetime.now(),
        )
