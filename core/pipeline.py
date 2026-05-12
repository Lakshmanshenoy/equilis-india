"""
core/pipeline.py
AnalysisPipeline — chains fetch → validate → normalize → analyze → render.

Each stage is fault-tolerant: failures produce a PipelineResult with stage/error
rather than crashing. The caller decides whether to abort or render partial output.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from core.analyzer import EquityAnalyzer
from core.cache import CacheManager
from core.fetcher import DataFetcher, FetchBundle
from core.models.company import CompanySnapshot
from core.models.ratios import RatioSet
from core.models.scenario import ScenarioResult
from core.normalizer import DataNormalizer
from core.renderer import ReportRenderer
from core.scenarios import earnings_scenarios
from core.validator import DataQualityError, DataValidator

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    ticker: str
    exchange: str = "NSE"
    analysis_type: str = "full"          # "full" | "quick" | "peers"
    output_format: str = "markdown"      # "markdown" | "pdf" | "json"
    peers: list[str] = field(default_factory=list)
    scenario_params: dict = field(default_factory=dict)
    skip_validation: bool = False
    save_report: bool = True


@dataclass
class PipelineResult:
    success: bool
    ticker: str
    stage: str = ""                      # last stage reached
    error: Optional[str] = None
    snapshot: Optional[CompanySnapshot] = None
    ratios: Optional[RatioSet] = None
    scenarios: Optional[ScenarioResult] = None
    red_flags: Optional[list[dict]] = None
    report_path: Optional[str] = None
    report_markdown: Optional[str] = None
    validation_issues: list = field(default_factory=list)
    elapsed_seconds: float = 0.0


class AnalysisPipeline:
    """
    Orchestrates a full equity analysis run.

    Usage:
        pipeline = AnalysisPipeline(plugins={"nse_api": NseApiPlugin(), ...})
        result = await pipeline.run(PipelineConfig(ticker="INFY"))
        print(result.report_markdown)
    """

    def __init__(
        self,
        plugins: dict,
        cache: Optional[CacheManager] = None,
        renderer: Optional[ReportRenderer] = None,
    ):
        self._cache = cache or CacheManager()
        self._fetcher = DataFetcher(plugins=plugins, cache=self._cache)
        self._normalizer = DataNormalizer()
        self._validator = DataValidator()
        self._analyzer = EquityAnalyzer()
        self._renderer = renderer or ReportRenderer()

    async def run(self, config: PipelineConfig) -> PipelineResult:
        t0 = datetime.now()
        result = PipelineResult(success=False, ticker=config.ticker)

        # ── Stage 1: Fetch ────────────────────────────────────────────────────
        result.stage = "fetch"
        try:
            bundle: FetchBundle = await self._fetcher.fetch_all(config.ticker)
            if not bundle.financials and not bundle.price:
                result.error = "All data sources returned no data."
                return result
        except Exception as e:
            result.error = f"Fetch stage failed: {e}"
            logger.exception("[pipeline] Fetch error")
            return result

        # ── Stage 2: Normalise ────────────────────────────────────────────────
        result.stage = "normalise"
        try:
            snapshot = self._normalizer.normalise(
                bundle,
                ticker=config.ticker,
                exchange=config.exchange,
            )
            result.snapshot = snapshot
        except Exception as e:
            result.error = f"Normalise stage failed: {e}"
            logger.exception("[pipeline] Normalise error")
            return result

        # ── Stage 3: Validate ─────────────────────────────────────────────────
        result.stage = "validate"
        if not config.skip_validation:
            try:
                issues = self._validator.validate(snapshot)
                result.validation_issues = issues
                snapshot.validation_issues = issues
            except DataQualityError as dqe:
                result.error = str(dqe)
                result.validation_issues = dqe.issues
                logger.warning(f"[pipeline] Validation errors for {config.ticker}")
                return result
            except Exception as e:
                result.error = f"Validate stage failed: {e}"
                return result

        # ── Stage 4: Analyse ──────────────────────────────────────────────────
        result.stage = "analyse"
        try:
            ratios = self._analyzer.compute_all(snapshot)
            red_flags = self._analyzer.red_flag_scan(snapshot)
            snapshot.ratios = ratios
            result.ratios = ratios
            result.red_flags = red_flags
        except Exception as e:
            result.error = f"Analyse stage failed: {e}"
            logger.exception("[pipeline] Analyse error")
            return result

        # ── Stage 5: Scenarios ────────────────────────────────────────────────
        result.stage = "scenarios"
        try:
            sc = earnings_scenarios(snapshot, **config.scenario_params)
            snapshot.scenarios = sc
            result.scenarios = sc
        except Exception as e:
            logger.warning(f"[pipeline] Scenarios failed (non-fatal): {e}")

        # ── Stage 6: Render ───────────────────────────────────────────────────
        result.stage = "render"
        try:
            markdown = self._renderer.render_markdown(
                snapshot=snapshot,
                ratios=ratios,
                scenarios=result.scenarios,
                red_flags=red_flags,
                validation_issues=result.validation_issues,
            )
            result.report_markdown = markdown

            if config.save_report:
                if config.output_format == "pdf":
                    from plugins.pdf_export import PDFReportExporter
                    exporter = PDFReportExporter()
                    result.report_path = exporter.export_analysis(snapshot)
                else:
                    result.report_path = self._renderer.save(markdown, config.ticker)

        except Exception as e:
            result.error = f"Render stage failed: {e}"
            logger.exception("[pipeline] Render error")
            return result

        result.success = True
        result.stage = "complete"
        result.elapsed_seconds = (datetime.now() - t0).total_seconds()
        logger.info(
            f"[pipeline] {config.ticker} completed in {result.elapsed_seconds:.1f}s"
        )
        return result
