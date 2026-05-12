"""
core/validator.py
Class-based data quality validator.

Raises DataQualityError for ERROR-severity issues; emits WARNINGs for softer flags.
Cross-source consistency checks require at least two sources to disagree by >5%.
Operates on CompanySnapshot, which is the normalised data model.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from core.models.company import CompanySnapshot

logger = logging.getLogger(__name__)

CROSS_SOURCE_TOLERANCE = 0.05   # 5% divergence triggers a warning
STALE_PRICE_MINUTES = 30        # CMP older than this → WARNING
STALE_FINANCIALS_HOURS = 24     # Financials older than this → WARNING


class Severity(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ValidationIssue:
    field: str
    severity: Severity
    message: str
    source_a: Optional[str] = None
    source_b: Optional[str] = None
    value_a: Optional[float] = None
    value_b: Optional[float] = None


class DataQualityError(Exception):
    """Raised when validation finds ERROR-severity issues."""
    def __init__(self, issues: list[ValidationIssue]):
        self.issues = issues
        messages = [f"[{i.field}] {i.message}" for i in issues]
        super().__init__("Data quality errors:\n" + "\n".join(messages))


class DataValidator:
    """
    Validates a CompanySnapshot before it enters the analysis pipeline.
    Call validate(snapshot) — raises DataQualityError on hard failures.
    """

    def validate(self, snapshot: CompanySnapshot) -> list[ValidationIssue]:
        """
        Run all checks. Raises DataQualityError if any ERROR issue found.
        Returns the full list of issues (WARNINGs + ERRORs + INFOs).
        """
        issues: list[ValidationIssue] = []
        issues.extend(self._check_completeness(snapshot))
        issues.extend(self._check_freshness(snapshot))
        issues.extend(self._check_internal_consistency(snapshot))
        issues.extend(self._check_cross_source_consistency(snapshot))

        errors = [i for i in issues if i.severity == Severity.ERROR]
        for issue in issues:
            level = logger.warning if issue.severity != Severity.INFO else logger.info
            level(f"[validator] {issue.severity.value} — {issue.field}: {issue.message}")

        if errors:
            raise DataQualityError(errors)

        return issues

    # ─────────────────────────── completeness ────────────────────────────────

    def _check_completeness(self, s: CompanySnapshot) -> list[ValidationIssue]:
        issues = []
        required_sections = {
            "price":       s.price,
            "income":      s.income,
            "market":      s.market,
            "balance_sheet": s.balance_sheet,
            "cash_flow":   s.cash_flow,
        }
        for name, section in required_sections.items():
            if section is None:
                issues.append(ValidationIssue(
                    field=name,
                    severity=Severity.ERROR,
                    message=f"Section '{name}' is missing entirely from snapshot.",
                ))

        if s.income and not s.income.revenue_5y:
            issues.append(ValidationIssue(
                field="income.revenue_5y",
                severity=Severity.WARNING,
                message="5-year revenue series is empty — trend analysis will be limited.",
            ))

        if s.income and not s.income.pat_5y:
            issues.append(ValidationIssue(
                field="income.pat_5y",
                severity=Severity.WARNING,
                message="5-year PAT series is empty — growth analysis will be limited.",
            ))

        critical_metrics = [
            ("price.cmp", getattr(s.price, "cmp", None)),
            ("income.revenue_ttm", getattr(s.income, "revenue_ttm", None)),
            ("income.pat_ttm", getattr(s.income, "pat_ttm", None)),
            ("income.ebitda_ttm", getattr(s.income, "ebitda_ttm", None)),
        ]
        missing_critical = [field for field, value in critical_metrics if value is None]
        for field in missing_critical:
            issues.append(ValidationIssue(
                field=field,
                severity=Severity.ERROR,
                message=(
                    "Critical metric missing — report would be materially incomplete. "
                    "Retry/fallback source should be used before rendering."
                ),
            ))

        advisory_metrics = [
            ("balance_sheet.total_debt", getattr(s.balance_sheet, "total_debt", None)),
            ("cash_flow.cfo_ttm", getattr(s.cash_flow, "cfo_ttm", None)),
            ("shareholding.promoter_holding", getattr(s.shareholding, "promoter_holding", None)),
        ]
        for field, value in advisory_metrics:
            if value is None:
                issues.append(ValidationIssue(
                    field=field,
                    severity=Severity.WARNING,
                    message="Advisory metric missing — some ratio and quality sections may show N/A.",
                ))

        return issues

    # ─────────────────────────── freshness ───────────────────────────────────

    def _check_freshness(self, s: CompanySnapshot) -> list[ValidationIssue]:
        issues = []
        now = datetime.now()

        if s.price:
            age = (now - s.price.fetched_at).total_seconds() / 60
            if age > STALE_PRICE_MINUTES:
                issues.append(ValidationIssue(
                    field="price.fetched_at",
                    severity=Severity.WARNING,
                    message=(
                        f"CMP is {age:.0f} min old (> {STALE_PRICE_MINUTES} min threshold). "
                        "Re-fetch for accurate valuation ratios."
                    ),
                ))

        if s.shareholding and s.shareholding.fetched_at:
            age_days = (now - s.shareholding.fetched_at).days
            if age_days > 95:   # quarterly report ~90 days
                issues.append(ValidationIssue(
                    field="shareholding.fetched_at",
                    severity=Severity.WARNING,
                    message=(
                        f"Shareholding data is {age_days} days old. "
                        "Latest quarterly filing may be available."
                    ),
                ))

        return issues

    # ─────────────────────────── internal consistency ────────────────────────

    def _check_internal_consistency(self, s: CompanySnapshot) -> list[ValidationIssue]:
        issues = []

        # FCF = CFO - Capex
        if s.cash_flow and s.cash_flow.cfo_ttm and s.cash_flow.capex_ttm:
            expected_fcf = s.cash_flow.cfo_ttm - abs(s.cash_flow.capex_ttm)
            if s.cash_flow.fcf_ttm is not None:
                diff = abs(expected_fcf - s.cash_flow.fcf_ttm)
                tolerance = abs(expected_fcf) * 0.02   # 2%
                if diff > tolerance:
                    issues.append(ValidationIssue(
                        field="cash_flow.fcf_ttm",
                        severity=Severity.WARNING,
                        message=(
                            f"FCF mismatch: stored={s.cash_flow.fcf_ttm:.0f}, "
                            f"computed={expected_fcf:.0f} (CFO-Capex)."
                        ),
                    ))

        # EPS = PAT / shares outstanding
        if (
            s.income and s.income.pat_ttm and
            s.market and s.market.shares_outstanding and
            s.income.eps_ttm
        ):
            computed_eps = s.income.pat_ttm / s.market.shares_outstanding
            diff_pct = abs(computed_eps - s.income.eps_ttm) / abs(s.income.eps_ttm)
            if diff_pct > 0.05:   # 5% tolerance
                issues.append(ValidationIssue(
                    field="income.eps_ttm",
                    severity=Severity.WARNING,
                    message=(
                        f"EPS mismatch: stored={s.income.eps_ttm:.2f}, "
                        f"computed={computed_eps:.2f}. "
                        "Confirm shares outstanding figure."
                    ),
                ))

        # Working capital sanity
        if s.balance_sheet:
            ca = s.balance_sheet.current_assets
            cl = s.balance_sheet.current_liabilities
            if ca is not None and cl is not None and ca < 0:
                issues.append(ValidationIssue(
                    field="balance_sheet.current_assets",
                    severity=Severity.ERROR,
                    message="Current assets is negative — likely a data entry error.",
                ))

        return issues

    # ─────────────────────────── cross-source consistency ────────────────────

    def _check_cross_source_consistency(self, s: CompanySnapshot) -> list[ValidationIssue]:
        issues = []
        sources = {
            "screener": s.screener_raw,
            "tickertape": s.tickertape_raw,
            "nse": s.nse_raw,
        }
        # Fields to compare across sources
        cross_check_fields = ["revenue_ttm", "pat_ttm", "ebitda_ttm", "cmp", "market_cap"]

        populated = {k: v for k, v in sources.items() if v}
        source_names = list(populated.keys())
        for i in range(len(source_names)):
            for j in range(i + 1, len(source_names)):
                sa, sb = source_names[i], source_names[j]
                for field in cross_check_fields:
                    va = populated[sa].get(field)
                    vb = populated[sb].get(field)
                    if va and vb and va != 0:
                        diff_pct = abs(va - vb) / abs(va)
                        if diff_pct > CROSS_SOURCE_TOLERANCE:
                            issues.append(ValidationIssue(
                                field=field,
                                severity=Severity.WARNING,
                                message=(
                                    f"Cross-source divergence {diff_pct:.1%} on {field}: "
                                    f"{sa}={va}, {sb}={vb}."
                                ),
                                source_a=sa, source_b=sb,
                                value_a=va, value_b=vb,
                            ))
        return issues
