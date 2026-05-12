"""
core/peer.py
Peer comparison pipeline — async concurrent fetch + side-by-side ratio table.

All outputs are factual data comparisons. No investment recommendations.
"""

from __future__ import annotations

import asyncio
import statistics
from typing import Dict, List, Optional

from core.models.peer import PeerComparisonResult


# ── Metrics registry ─────────────────────────────────────────────────────────
# Each entry: (display_name, dotted_attr_path, format_spec)
# Paths use `snapshot.ratios.*` populated by EquityAnalyzer.compute_all()
# and `snapshot.income.*`, `snapshot.market.*` for raw fields.

PEER_COMPARISON_METRICS: List[tuple] = [
    ("Revenue TTM (₹Cr)",   "income.revenue_ttm",             ",.0f"),
    ("PAT TTM (₹Cr)",       "income.pat_ttm",                 ",.0f"),
    ("EBITDA Margin",        "ratios.profitability.ebitda_margin", ".1%"),
    ("PAT Margin",           "ratios.profitability.pat_margin",    ".1%"),
    ("ROE",                  "ratios.profitability.roe",           ".1%"),
    ("ROCE",                 "ratios.profitability.roce",          ".1%"),
    ("D/E Ratio",            "ratios.leverage.debt_to_equity",     ".2f"),
    ("Current Ratio",        "ratios.leverage.current_ratio",      ".2f"),
    ("P/E (TTM)",            "ratios.valuation.pe_ttm",            ".1f"),
    ("EV/EBITDA",            "ratios.valuation.ev_ebitda",         ".1f"),
    ("Market Cap (₹Cr)",     "market.market_cap",                  ",.0f"),
]


class PeerComparisonPipeline:
    """
    Fetches and analyses a peer group concurrently, then builds a comparison table.
    """

    def __init__(self, fetcher, validator, analyzer):
        self.fetcher   = fetcher
        self.validator = validator
        self.analyzer  = analyzer

    async def run(
        self,
        tickers: List[str],
        metrics: Optional[List[str]] = None,
    ) -> PeerComparisonResult:
        """
        Fetch, normalise, analyse each ticker concurrently.
        Returns PeerComparisonResult with comparison table + sector medians.
        """
        tasks   = [self._fetch_and_analyze(t) for t in tickers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        snapshots: Dict[str, object] = {}
        errors:    Dict[str, str]    = {}

        for ticker, result in zip(tickers, results):
            if isinstance(result, Exception):
                errors[ticker] = str(result)
            else:
                snapshots[ticker] = result

        active_metrics = metrics or [m[0] for m in PEER_COMPARISON_METRICS]
        table   = self._build_comparison_table(snapshots, active_metrics)
        medians = self._compute_sector_medians(snapshots, active_metrics)
        sources = {
            ticker: (snap.sources[0].source_name if snap.sources else "unknown")
            for ticker, snap in snapshots.items()
        }

        return PeerComparisonResult(
            tickers=tickers,
            snapshots=snapshots,
            comparison_table=table,
            sector_medians=medians,
            errors=errors,
            sources=sources,
        )

    async def _fetch_and_analyze(self, ticker: str) -> object:
        """Fetch raw data, normalise to CompanySnapshot, attach ratios."""
        from core.normalizer import DataNormalizer

        raw      = await self.fetcher.fetch_all(ticker)
        snapshot = DataNormalizer().normalise(raw, ticker=ticker)
        if self.validator is not None:
            snapshot.validation_issues = self.validator.validate(snapshot)
        snapshot.ratios = self.analyzer.compute_all(snapshot)
        return snapshot

    def _build_comparison_table(
        self,
        snapshots: Dict[str, object],
        active_metrics: List[str],
    ) -> Dict[str, Dict[str, object]]:
        """
        Returns {metric_name: {ticker: value, ...}, ...}.
        """
        metric_map = {m[0]: m for m in PEER_COMPARISON_METRICS}
        table: Dict[str, Dict[str, object]] = {}

        for metric_name in active_metrics:
            if metric_name not in metric_map:
                continue
            _, attr_path, _ = metric_map[metric_name]
            row: Dict[str, object] = {}
            for ticker, snapshot in snapshots.items():
                try:
                    row[ticker] = self._resolve_path(snapshot, attr_path)
                except (AttributeError, TypeError):
                    row[ticker] = None
            table[metric_name] = row

        return table

    def _compute_sector_medians(
        self,
        snapshots: Dict[str, object],
        active_metrics: List[str],
    ) -> Dict[str, Optional[float]]:
        """
        Returns {metric_name: median_value_or_None}.
        """
        metric_map = {m[0]: m for m in PEER_COMPARISON_METRICS}
        medians: Dict[str, Optional[float]] = {}

        for metric_name in active_metrics:
            if metric_name not in metric_map:
                continue
            _, attr_path, _ = metric_map[metric_name]
            vals: List[float] = []
            for snapshot in snapshots.values():
                try:
                    v = self._resolve_path(snapshot, attr_path)
                    if v is not None:
                        vals.append(float(v))
                except (AttributeError, TypeError, ValueError):
                    pass
            medians[metric_name] = statistics.median(vals) if vals else None

        return medians

    def _resolve_path(self, obj: object, path: str) -> object:
        """
        Traverse a dotted attribute path on an object.
        e.g. "ratios.profitability.roe"
        """
        for part in path.split("."):
            obj = getattr(obj, part)
        return obj
