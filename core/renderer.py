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

from core.models.company import CompanySnapshot
from core.models.ratios import RatioSet
from core.models.scenario import ScenarioResult
from core.validator import ValidationIssue

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.expanduser("~/Downloads/equilis-reports")

COMPLIANCE_FOOTER = """\
---
**COMPLIANCE DISCLAIMER**

This document has been prepared by Equilis India for research and educational purposes only.
It does not constitute investment advice, a solicitation, or a recommendation to buy or sell
any security. All figures are sourced from public filings and third-party data providers;
accuracy cannot be guaranteed. Scenario outputs are mathematical computations of stated
assumptions only — they are not earnings forecasts or price targets.

Equilis India is not a registered Investment Adviser under SEBI (Investment Advisers)
Regulations, 2013. Past performance is not indicative of future results.
Readers should conduct their own due diligence and consult a SEBI-registered financial
adviser before making any investment decision.

*Generated: {ts} | Version: equilis-india/2.0*
"""


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
        if red_flags:
            sections.append(self._red_flags_section(red_flags))
        if scenarios:
            sections.append(self._scenarios_section(scenarios))
        sections.append(self._sources_section(snapshot))
        sections.append(self._footer())
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
        severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡"}
        lines = ["## Red Flag Scan", ""]
        for f in flags:
            icon = severity_icon.get(f.get("severity", "MEDIUM"), "⚪")
            lines.append(
                f"- {icon} **[{f.get('severity')}]** {f.get('flag')}  "
                f"*{f.get('evidence', '')}*"
            )
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

    def _footer(self) -> str:
        ts = datetime.now().strftime("%d %b %Y %H:%M IST")
        return COMPLIANCE_FOOTER.format(ts=ts)
