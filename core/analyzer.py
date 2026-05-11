"""
core/analyzer.py
EquityAnalyzer — computes financial ratios and red-flag signals from a CompanySnapshot.

All ratio methods return typed dataclasses from core.models.ratios.
No price targets. No buy/sell/hold. Analytical outputs only.

Academic reference: Altman Z-Score (1968) is provided as a research reference
only. It was calibrated for US manufacturing firms and must not be interpreted
as a creditworthiness conclusion for Indian companies.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from core.models.company import CompanySnapshot
from core.models.ratios import (
    CashFlowQuality,
    DuPontDecomposition,
    EfficiencyRatios,
    LeverageRatios,
    ProfitabilityRatios,
    RatioSet,
    ValuationRatios,
)

logger = logging.getLogger(__name__)

ALTMAN_DISCLAIMER = (
    "Altman Z-Score is an academic model calibrated on US manufacturing data (1968). "
    "Interpret with caution for Indian companies, service sectors, and financial entities."
)


def _safe_div(numerator: Optional[float], denominator: Optional[float]) -> Optional[float]:
    if numerator is None or denominator is None:
        return None
    if denominator == 0:
        return None
    return numerator / denominator


class EquityAnalyzer:
    """
    Computes financial ratios, DuPont decomposition, cash-flow quality,
    red flags, and Altman Z-Score from a normalised CompanySnapshot.
    """

    def compute_all(self, snapshot: CompanySnapshot) -> RatioSet:
        """Convenience: compute and return all ratios in one call."""
        return RatioSet(
            ticker=snapshot.ticker,
            fiscal_year=str(datetime.now().year),
            profitability=self.compute_profitability(snapshot),
            dupont=self.dupont_decomposition(snapshot),
            leverage=self.leverage_ratios(snapshot),
            valuation=self.valuation_ratios(snapshot),
            efficiency=self.efficiency_ratios(snapshot),
            cash_flow_quality=self.cash_flow_quality(snapshot),
            computed_at=datetime.now().isoformat(),
        )

    def compute_profitability(self, snapshot: CompanySnapshot) -> ProfitabilityRatios:
        inc = snapshot.income
        bs = snapshot.balance_sheet

        if not inc:
            return ProfitabilityRatios()

        gross_margin = _safe_div(inc.gross_profit, inc.revenue_ttm)
        ebitda_margin = _safe_div(inc.ebitda_ttm, inc.revenue_ttm)
        pat_margin = _safe_div(inc.pat_ttm, inc.revenue_ttm)

        roe = roa = roce = None
        if bs:
            roe = _safe_div(inc.pat_ttm, bs.equity)
            roa = _safe_div(inc.pat_ttm, bs.total_assets)
            ebit = inc.ebit or (
                inc.ebitda_ttm - (inc.depreciation or 0) if inc.ebitda_ttm else None
            )
            capital_employed = (
                (bs.total_assets - bs.current_liabilities)
                if bs.total_assets and bs.current_liabilities else None
            )
            roce = _safe_div(ebit, capital_employed)

        return ProfitabilityRatios(
            gross_margin=gross_margin,
            ebitda_margin=ebitda_margin,
            pat_margin=pat_margin,
            roe=roe,
            roa=roa,
            roce=roce,
        )

    def dupont_decomposition(self, snapshot: CompanySnapshot) -> DuPontDecomposition:
        inc = snapshot.income
        bs = snapshot.balance_sheet

        if not inc or not bs:
            return DuPontDecomposition()

        npm = _safe_div(inc.pat_ttm, inc.revenue_ttm)
        asset_turn = _safe_div(inc.revenue_ttm, bs.total_assets)
        equity_mult = _safe_div(bs.total_assets, bs.equity)
        roe_dupont = None
        if npm and asset_turn and equity_mult:
            roe_dupont = npm * asset_turn * equity_mult
        roe_reported = _safe_div(inc.pat_ttm, bs.equity)

        return DuPontDecomposition(
            net_profit_margin=npm,
            asset_turnover=asset_turn,
            equity_multiplier=equity_mult,
            roe_dupont=roe_dupont,
            roe_reported=roe_reported,
        )

    def cash_flow_quality(self, snapshot: CompanySnapshot) -> CashFlowQuality:
        cf = snapshot.cash_flow
        inc = snapshot.income

        if not cf or not inc or not inc.pat_ttm or not cf.cfo_ttm:
            return CashFlowQuality(quality_signal="UNKNOWN", note="Insufficient data.")

        ratio = _safe_div(cf.cfo_ttm, inc.pat_ttm)
        if ratio is None:
            return CashFlowQuality(quality_signal="UNKNOWN")

        if ratio >= 1.1:
            signal = "HIGH"
            note = f"CFO/PAT = {ratio:.2f}. Operating cash well above reported profit."
        elif ratio >= 0.8:
            signal = "MEDIUM"
            note = f"CFO/PAT = {ratio:.2f}. Reasonable alignment between cash and profits."
        else:
            signal = "LOW"
            note = (
                f"CFO/PAT = {ratio:.2f}. Operating cash significantly below reported profit — "
                "investigate working capital changes and revenue recognition."
            )

        return CashFlowQuality(
            cfo_pat_ratio=ratio,
            quality_signal=signal,
            note=note,
        )

    def leverage_ratios(self, snapshot: CompanySnapshot) -> LeverageRatios:
        bs = snapshot.balance_sheet
        inc = snapshot.income

        if not bs:
            return LeverageRatios()

        de = _safe_div(bs.total_debt, bs.equity)
        d_ebitda = _safe_div(bs.total_debt, inc.ebitda_ttm) if inc else None
        interest_coverage = None
        if inc and inc.ebitda_ttm and inc.interest_expense:
            interest_coverage = _safe_div(inc.ebitda_ttm, inc.interest_expense)
        cr = _safe_div(bs.current_assets, bs.current_liabilities)
        qr = None
        if bs.current_assets and bs.inventory and bs.current_liabilities:
            qr = _safe_div(bs.current_assets - bs.inventory, bs.current_liabilities)

        return LeverageRatios(
            debt_to_equity=de,
            debt_to_ebitda=d_ebitda,
            interest_coverage=interest_coverage,
            current_ratio=cr,
            quick_ratio=qr,
        )

    def valuation_ratios(self, snapshot: CompanySnapshot) -> ValuationRatios:
        price = snapshot.price
        inc = snapshot.income
        bs = snapshot.balance_sheet
        mkt = snapshot.market

        if not price or not inc:
            return ValuationRatios()

        pe = _safe_div(price.cmp, inc.eps_ttm)
        pb = None
        if bs and bs.book_value_per_share:
            pb = _safe_div(price.cmp, bs.book_value_per_share)
        ev_ebitda = ev_sales = None
        if mkt and mkt.enterprise_value:
            ev_ebitda = _safe_div(mkt.enterprise_value, inc.ebitda_ttm)
            ev_sales = _safe_div(mkt.enterprise_value, inc.revenue_ttm)
        peg = None
        if pe and inc.eps_growth_5yr and inc.eps_growth_5yr > 0:
            peg = pe / (inc.eps_growth_5yr * 100)   # growth as %
        div_yield = None
        if inc.dividend_per_share and price.cmp:
            div_yield = _safe_div(inc.dividend_per_share, price.cmp)

        return ValuationRatios(
            pe_ttm=pe,
            pb=pb,
            ev_ebitda=ev_ebitda,
            ev_sales=ev_sales,
            peg=peg,
            div_yield=div_yield,
        )

    def efficiency_ratios(self, snapshot: CompanySnapshot) -> EfficiencyRatios:
        inc = snapshot.income
        bs = snapshot.balance_sheet

        if not inc or not bs:
            return EfficiencyRatios()

        rev = inc.revenue_ttm
        rec_days = _safe_div(bs.receivables, rev) * 365 if bs.receivables and rev else None
        inv_days = None
        cogs = None
        if inc.revenue_ttm and inc.gross_profit:
            cogs = inc.revenue_ttm - inc.gross_profit
        if bs.inventory and cogs:
            inv_days = _safe_div(bs.inventory, cogs) * 365
        pay_days = _safe_div(bs.payables, cogs) * 365 if bs.payables and cogs else None
        ccc = None
        if rec_days and inv_days and pay_days:
            ccc = rec_days + inv_days - pay_days
        asset_turn = _safe_div(rev, bs.total_assets)

        return EfficiencyRatios(
            receivables_days=rec_days,
            inventory_days=inv_days,
            payables_days=pay_days,
            cash_conversion_cycle=ccc,
            asset_turnover=asset_turn,
        )

    def red_flag_scan(
        self,
        snapshot: CompanySnapshot,
        history: Optional[list[CompanySnapshot]] = None,
    ) -> list[dict]:
        """
        Returns a list of red flag dicts with keys: flag, severity, evidence.
        Severity: "CRITICAL", "HIGH", "MEDIUM".
        """
        flags: list[dict] = []
        cf = snapshot.cash_flow
        inc = snapshot.income
        bs = snapshot.balance_sheet
        sh = snapshot.shareholding

        # CFO < 0 while PAT > 0
        if cf and inc:
            if cf.cfo_ttm and cf.cfo_ttm < 0 and inc.pat_ttm and inc.pat_ttm > 0:
                flags.append({
                    "flag": "Negative operating cash flow despite positive profits",
                    "severity": "CRITICAL",
                    "evidence": f"CFO={cf.cfo_ttm:.0f} Cr, PAT={inc.pat_ttm:.0f} Cr",
                })

        # High promoter pledging
        if sh and sh.promoter_pledging and sh.promoter_pledging > 30:
            flags.append({
                "flag": "High promoter pledge",
                "severity": "HIGH",
                "evidence": f"{sh.promoter_pledging:.1f}% of promoter holding pledged",
            })

        # Declining promoter holding
        if sh and len(sh.promoter_holding_history) >= 4:
            oldest = sh.promoter_holding_history[-1]
            latest = sh.promoter_holding_history[0]
            if latest < oldest - 5:
                flags.append({
                    "flag": "Sustained promoter holding decline",
                    "severity": "HIGH",
                    "evidence": (
                        f"Promoter holding fell from {oldest:.1f}% to {latest:.1f}% "
                        "(last 4 quarters)"
                    ),
                })

        # Debt/equity > 3
        if bs and bs.total_debt and bs.equity:
            de = _safe_div(bs.total_debt, bs.equity)
            if de and de > 3:
                flags.append({
                    "flag": "Very high leverage",
                    "severity": "HIGH",
                    "evidence": f"Debt/Equity = {de:.1f}x",
                })

        # Revenue declining for 3+ years
        if inc and len(inc.revenue_5y) >= 3:
            rev3 = inc.revenue_5y[-3:]
            if rev3[0] > rev3[1] > rev3[2]:
                flags.append({
                    "flag": "Revenue declining three consecutive years",
                    "severity": "MEDIUM",
                    "evidence": (
                        f"Revenue trend: {rev3[0]:.0f} → {rev3[1]:.0f} → {rev3[2]:.0f} Cr"
                    ),
                })

        return flags

    def altman_z_score(self, snapshot: CompanySnapshot) -> dict:
        """
        Altman Z-Score (academic reference model).
        Returns score + interpretation + mandatory disclaimer.
        Original formula for non-financial manufacturing firms.
        """
        bs = snapshot.balance_sheet
        inc = snapshot.income
        mkt = snapshot.market
        cf = snapshot.cash_flow

        if not bs or not inc or not mkt:
            return {
                "score": None,
                "interpretation": "Insufficient data",
                "disclaimer": ALTMAN_DISCLAIMER,
            }

        wc = None
        if bs.current_assets and bs.current_liabilities:
            wc = bs.current_assets - bs.current_liabilities

        x1 = _safe_div(wc, bs.total_assets)
        x2 = _safe_div(bs.retained_earnings, bs.total_assets)
        x3_num = inc.ebit or (
            inc.ebitda_ttm - (inc.depreciation or 0) if inc.ebitda_ttm else None
        )
        x3 = _safe_div(x3_num, bs.total_assets)
        x4 = _safe_div(mkt.market_cap, bs.total_liabilities if hasattr(bs, 'total_liabilities') else None)
        # total_liabilities via property if available
        try:
            total_liab = bs.total_assets - bs.equity if bs.total_assets and bs.equity else None
            x4 = _safe_div(mkt.market_cap, total_liab)
        except Exception:
            x4 = None
        x5 = _safe_div(inc.revenue_ttm, bs.total_assets)

        if None in (x1, x2, x3, x4, x5):
            return {
                "score": None,
                "interpretation": "Insufficient data for full Z-Score calculation",
                "disclaimer": ALTMAN_DISCLAIMER,
            }

        z = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

        if z > 2.99:
            interpretation = "Safe zone (academic reference only)"
        elif z > 1.81:
            interpretation = "Grey zone (academic reference only)"
        else:
            interpretation = "Distress zone (academic reference only)"

        return {
            "score": round(z, 2),
            "x1_working_capital_ratio": round(x1, 3),
            "x2_retained_earnings_ratio": round(x2, 3),
            "x3_ebit_ratio": round(x3, 3),
            "x4_equity_to_liabilities": round(x4, 3),
            "x5_asset_turnover": round(x5, 3),
            "interpretation": interpretation,
            "disclaimer": ALTMAN_DISCLAIMER,
        }
