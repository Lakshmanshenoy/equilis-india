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
    CashFlowQualityResult,
    DuPontDecomposition,
    DuPontResult,
    EfficiencyRatios,
    LeverageRatios,
    ProfitabilityRatios,
    RatioSet,
    RedFlagScanResult,
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

    # ── Phase 2: Multi-year trend analysis ────────────────────────────────────

    def compute_dupont_trend(self, snapshot: CompanySnapshot) -> DuPontResult:
        """
        3-factor DuPont decomposition across history (newest first).
        ROE = NPM × Asset Turnover × Equity Multiplier.
        """
        results_by_year = []
        for year in snapshot.history:
            if not all([year.pat, year.revenue, year.total_assets, year.equity]):
                continue
            npm = year.pat / year.revenue
            at = year.revenue / year.total_assets
            em = year.total_assets / year.equity
            roe_dupont = npm * at * em
            roe_reported = year.pat / year.equity
            results_by_year.append({
                "fiscal_year":        year.fiscal_year,
                "net_profit_margin":  round(npm, 4),
                "asset_turnover":     round(at, 4),
                "equity_multiplier":  round(em, 4),
                "roe_dupont":         round(roe_dupont, 4),
                "roe_reported":       round(roe_reported, 4),
                "reconciliation_gap": round(abs(roe_dupont - roe_reported), 4),
            })

        latest = results_by_year[0] if results_by_year else {}
        return DuPontResult(
            by_year=results_by_year,
            driver_observation=self._identify_roe_driver(latest, results_by_year),
            trend_note=self._dupont_trend_note(results_by_year),
        )

    def _identify_roe_driver(self, latest: dict, history: list) -> str:
        if not latest:
            return "Insufficient data for driver analysis."
        npm = latest["net_profit_margin"]
        at  = latest["asset_turnover"]
        em  = latest["equity_multiplier"]
        factors = {"net profit margin": npm, "asset turnover": at, "equity multiplier": em}
        dominant = max(factors, key=lambda k: abs(factors[k] - 1.0))
        if dominant == "equity multiplier" and em > 3.0:
            return (
                f"ROE is substantially amplified by leverage (equity multiplier: {em:.2f}x). "
                f"Asset turnover is {at:.2f}x and net profit margin is {npm:.1%}. "
                f"Research note: high equity multiplier warrants examination of debt levels "
                f"relative to sector norms."
            )
        elif dominant == "net profit margin":
            return (
                f"ROE is primarily driven by net profit margin ({npm:.1%}), "
                f"with asset turnover at {at:.2f}x and equity multiplier at {em:.2f}x."
            )
        else:
            return (
                f"ROE is driven by asset turnover efficiency ({at:.2f}x), "
                f"with net profit margin at {npm:.1%} and equity multiplier at {em:.2f}x."
            )

    def _dupont_trend_note(self, history: list) -> str:
        if len(history) < 3:
            return "Insufficient history for trend analysis."
        latest_npm = history[0]["net_profit_margin"]
        oldest_npm = history[-1]["net_profit_margin"]
        latest_em  = history[0]["equity_multiplier"]
        oldest_em  = history[-1]["equity_multiplier"]
        npm_dir = "expanded" if latest_npm > oldest_npm else "compressed"
        em_dir  = "increased" if latest_em > oldest_em else "decreased"
        return (
            f"Net profit margin has {npm_dir} from {oldest_npm:.1%} "
            f"({history[-1]['fiscal_year']}) to {latest_npm:.1%} ({history[0]['fiscal_year']}). "
            f"Financial leverage (equity multiplier) has {em_dir} from {oldest_em:.2f}x "
            f"to {latest_em:.2f}x over the same period."
        )

    def compute_cf_quality_trend(self, snapshot: CompanySnapshot) -> CashFlowQualityResult:
        """
        CFO/PAT quality score across history (newest first).
        Signals earnings quality — higher is generally associated with better cash conversion.
        """
        cf_data = []
        for year in snapshot.history:
            if year.cfo is None or year.pat is None:
                continue
            if year.pat == 0:
                ratio  = None
                signal = "INDETERMINATE"
            else:
                ratio  = year.cfo / year.pat
                signal = self._cf_signal(ratio, year.cfo, year.pat)
            cf_data.append({
                "fiscal_year": year.fiscal_year,
                "cfo_cr":  round(year.cfo, 1),
                "pat_cr":  round(year.pat, 1),
                "cfo_pat": round(ratio, 2) if ratio is not None else None,
                "signal":  signal,
            })

        consecutive_low = self._consecutive_low_cf(cf_data)
        overall_signal  = self._overall_cf_signal(cf_data)
        observations    = self._cf_observations(cf_data, consecutive_low)
        return CashFlowQualityResult(
            by_year=cf_data,
            overall_signal=overall_signal,
            consecutive_low_years=consecutive_low,
            observations=observations,
        )

    def _cf_signal(self, ratio: float, cfo: float, pat: float) -> str:
        if cfo < 0 and pat > 0:
            return "RED"
        if ratio >= 1.0:
            return "HIGH"
        if ratio >= 0.8:
            return "MEDIUM"
        return "LOW"

    def _consecutive_low_cf(self, cf_data: list) -> int:
        count = 0
        for year in cf_data:   # newest first
            if year["signal"] in ("LOW", "RED"):
                count += 1
            else:
                break
        return count

    def _overall_cf_signal(self, cf_data: list) -> str:
        if not cf_data:
            return "INSUFFICIENT_DATA"
        signals = [d["signal"] for d in cf_data[:3]]
        if "RED" in signals:
            return "RED"
        if signals.count("LOW") >= 2:
            return "LOW"
        if signals.count("HIGH") >= 2:
            return "HIGH"
        return "MEDIUM"

    def _cf_observations(self, cf_data: list, consecutive_low: int) -> list:
        obs = []
        for year in cf_data:
            if year["signal"] == "RED":
                obs.append(
                    f"{year['fiscal_year']}: CFO was ₹{year['cfo_cr']}Cr (negative) while PAT "
                    f"was ₹{year['pat_cr']}Cr (positive). Significant accruals divergence "
                    f"warrants examination of working capital movements and non-cash items."
                )
            elif year["signal"] == "LOW":
                obs.append(
                    f"{year['fiscal_year']}: CFO/PAT ratio was {year['cfo_pat']:.2f} — "
                    f"cash conversion below 0.80. Research note: accruals may be elevated."
                )
        if consecutive_low >= 2:
            obs.append(
                f"CFO/PAT has been below 0.80 for {consecutive_low} consecutive years. "
                f"Sustained low cash conversion warrants examination of receivables, "
                f"inventory, and deferred revenue trends."
            )
        return obs

    def run_red_flag_scan(self, snapshot: CompanySnapshot) -> RedFlagScanResult:
        """
        Comprehensive red flag scan across accounting, governance, and capital allocation.
        All flags are research observations — not investment conclusions.
        """
        flags: list[dict] = []
        flags.extend(self._check_receivables_growth(snapshot))
        flags.extend(self._check_other_income(snapshot))
        flags.extend(self._check_cf_divergence_history(snapshot))
        flags.extend(self._check_sustained_low_cf(snapshot))
        flags.extend(self._check_promoter_pledge(snapshot))
        flags.extend(self._check_promoter_selling(snapshot))
        flags.extend(self._check_capex_returns(snapshot))
        flags.extend(self._check_equity_dilution(snapshot))

        red_count    = sum(1 for f in flags if f["severity"] == "RED")
        yellow_count = sum(1 for f in flags if f["severity"] == "YELLOW")
        return RedFlagScanResult(
            flags=flags,
            red_count=red_count,
            yellow_count=yellow_count,
            summary=self._flag_summary(flags, red_count, yellow_count),
        )

    def _cagr(self, history: list, field: str, years: int) -> Optional[float]:
        """Compute CAGR from history (newest first). vals[0]=newest, vals[-1]=oldest."""
        vals = [getattr(y, field, None) for y in history[:years + 1]]
        vals = [v for v in vals if v is not None and v > 0]
        if len(vals) < 2:
            return None
        return (vals[0] / vals[-1]) ** (1 / (len(vals) - 1)) - 1

    def _check_receivables_growth(self, snapshot: CompanySnapshot) -> list:
        flags = []
        if len(snapshot.history) < 4:   # need 3-year CAGR = 4 data points
            return flags
        rev_cagr = self._cagr(snapshot.history, "revenue", years=3)
        rec_cagr = self._cagr(snapshot.history, "receivables", years=3)
        if rev_cagr and rec_cagr and rec_cagr > rev_cagr * 1.2:
            flags.append({
                "flag_id":     "RECEIVABLES_GROWTH_EXCEEDS_REVENUE",
                "category":    "Accounting & Accruals",
                "severity":    "YELLOW",
                "observation": (
                    f"Receivables 3-year CAGR ({rec_cagr:.1%}) exceeds revenue 3-year CAGR "
                    f"({rev_cagr:.1%}) by more than 20%. "
                    f"Warrants examination of debtor ageing and collection efficiency."
                ),
                "source": "financials",
            })
        return flags

    def _check_other_income(self, snapshot: CompanySnapshot) -> list:
        flags = []
        years_checked = [y for y in snapshot.history[:3]
                         if y.other_income is not None and y.pbt and y.pbt > 0]
        high_oi_years = [y for y in years_checked if (y.other_income / y.pbt) > 0.15]
        if len(high_oi_years) >= 2:
            avg_ratio = sum(y.other_income / y.pbt for y in high_oi_years) / len(high_oi_years)
            flags.append({
                "flag_id":     "HIGH_OTHER_INCOME",
                "category":    "Accounting & Accruals",
                "severity":    "YELLOW",
                "observation": (
                    f"Other income exceeded 15% of PBT in {len(high_oi_years)} of the last "
                    f"3 years (average: {avg_ratio:.1%}). Warrants examination of recurring "
                    f"vs one-time nature of other income."
                ),
                "source": "financials",
            })
        return flags

    def _check_cf_divergence_history(self, snapshot: CompanySnapshot) -> list:
        flags = []
        for year in snapshot.history[:3]:
            if year.cfo is not None and year.pat is not None:
                if year.cfo < 0 and year.pat > 0:
                    flags.append({
                        "flag_id":     "NEGATIVE_CFO_POSITIVE_PAT",
                        "category":    "Accounting & Accruals",
                        "severity":    "RED",
                        "observation": (
                            f"{year.fiscal_year}: CFO was ₹{year.cfo:.0f}Cr (negative) while "
                            f"PAT was ₹{year.pat:.0f}Cr (positive). Significant accruals "
                            f"divergence. Warrants examination of working capital movements, "
                            f"capitalised expenses, and deferred revenue."
                        ),
                        "source": "financials",
                    })
        return flags

    def _check_sustained_low_cf(self, snapshot: CompanySnapshot) -> list:
        flags = []
        low_years = []
        for year in snapshot.history[:3]:
            if year.cfo is not None and year.pat and year.pat > 0:
                if (year.cfo / year.pat) < 0.8:
                    low_years.append(year.fiscal_year)
        if len(low_years) >= 2:
            flags.append({
                "flag_id":     "SUSTAINED_LOW_CF_QUALITY",
                "category":    "Accounting & Accruals",
                "severity":    "YELLOW",
                "observation": (
                    f"CFO/PAT below 0.80 in {', '.join(low_years)}. Sustained low cash "
                    f"conversion warrants examination of receivables, inventory, and "
                    f"deferred revenue trends."
                ),
                "source": "financials",
            })
        return flags

    def _check_promoter_pledge(self, snapshot: CompanySnapshot) -> list:
        flags = []
        sh = snapshot.shareholding
        if sh is None:
            return flags
        pledge = sh.promoter_pledging
        if pledge and pledge > 30:
            flags.append({
                "flag_id":     "HIGH_PROMOTER_PLEDGE",
                "category":    "Corporate Governance",
                "severity":    "YELLOW",
                "observation": (
                    f"Promoter pledge is {pledge:.1f}% of promoter holding (latest quarter). "
                    f"Context note: pledge levels above 30% are commonly flagged for closer "
                    f"examination."
                ),
                "source": "BSE shareholding filings",
            })
        # Check rising pledge from history (last 4 quarters)
        ph = sh.promoter_holding_history
        if ph and len(ph) >= 4:
            # promoter_holding_history is already shareholding %, use pledging trend if available
            pass
        return flags

    def _check_promoter_selling(self, snapshot: CompanySnapshot) -> list:
        flags = []
        sh = snapshot.shareholding
        if sh is None or not sh.promoter_holding_history or len(sh.promoter_holding_history) < 2:
            return flags
        latest  = sh.promoter_holding_history[0]
        oldest  = sh.promoter_holding_history[-1]
        if oldest and latest and (latest - oldest) < -3:
            flags.append({
                "flag_id":     "PROMOTER_SELLING",
                "category":    "Corporate Governance",
                "severity":    "YELLOW",
                "observation": (
                    f"Promoter holding reduced by {abs(latest - oldest):.1f} percentage points "
                    f"over the tracked period. Source: BSE shareholding filings. Context note: "
                    f"reductions can reflect diversification, estate planning, or liquidity needs."
                ),
                "source": "BSE shareholding filings",
            })
        return flags

    def _check_capex_returns(self, snapshot: CompanySnapshot) -> list:
        flags = []
        if len(snapshot.history) < 3:
            return flags
        high_capex_years = [
            y for y in snapshot.history[:3]
            if y.capex and y.revenue and (y.capex / y.revenue) > 0.15
        ]
        roce_declining = (
            snapshot.history[0].roce is not None and
            snapshot.history[2].roce is not None and
            snapshot.history[0].roce < snapshot.history[2].roce
        )
        if len(high_capex_years) >= 2 and roce_declining:
            flags.append({
                "flag_id":     "CAPEX_WITHOUT_RETURN",
                "category":    "Capital Allocation",
                "severity":    "YELLOW",
                "observation": (
                    f"Capex exceeded 15% of revenue in {len(high_capex_years)} of the last "
                    f"3 years, while ROCE declined from "
                    f"{snapshot.history[2].roce:.1%} ({snapshot.history[2].fiscal_year}) "
                    f"to {snapshot.history[0].roce:.1%} ({snapshot.history[0].fiscal_year}). "
                    f"Warrants examination of capex project status and expected return timeline."
                ),
                "source": "financials",
            })
        return flags

    def _check_equity_dilution(self, snapshot: CompanySnapshot) -> list:
        flags = []
        if len(snapshot.history) < 2:
            return flags
        shares_new = snapshot.history[0].shares_outstanding
        shares_old = snapshot.history[-1].shares_outstanding
        if shares_old and shares_new and shares_old > 0:
            dilution = (shares_new - shares_old) / shares_old
            if dilution > 0.05:
                flags.append({
                    "flag_id":     "EQUITY_DILUTION",
                    "category":    "Capital Allocation",
                    "severity":    "YELLOW",
                    "observation": (
                        f"Shares outstanding grew by {dilution:.1%} over "
                        f"{len(snapshot.history) - 1} years "
                        f"({shares_old:.2f}Cr to {shares_new:.2f}Cr). Warrants examination of "
                        f"the purpose of equity issuance (acquisitions, QIP, ESOPs, rights issue)."
                    ),
                    "source": "financials",
                })
        return flags

    def _flag_summary(self, flags: list, red_count: int, yellow_count: int) -> str:
        if not flags:
            return "No anomalies detected across the standard red flag checklist."
        parts = []
        if red_count:
            parts.append(f"{red_count} high-priority observation(s) require attention")
        if yellow_count:
            parts.append(f"{yellow_count} observation(s) warrant further examination")
        return (
            ". ".join(parts) + ". "
            "All flags are factual observations based on publicly available data. "
            "They do not constitute conclusions about management integrity or investment quality."
        )
