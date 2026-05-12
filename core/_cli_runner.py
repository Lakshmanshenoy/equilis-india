"""
core/_cli_runner.py
Python entry point called by CLI JS commands via child_process.
Parses CLI args, runs the pipeline, and prints a JSON envelope to stdout.

This file is intentionally thin — it wires CLI args to pipeline.py.
"""

import argparse
import asyncio
from datetime import datetime
import json
import logging
import os
import sys
logger = logging.getLogger(__name__)

# Ensure repo root is on the path when called from CLI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import AnalysisPipeline, PipelineConfig
from core.compliance import render_disclaimer
from core.validator import DataValidator
from core.cache import CacheManager


def build_plugins(no_cache: bool = False) -> dict:
    """Instantiate available plugins. Returns {name: plugin_instance}."""
    plugins = {}
    try:
        from plugins.nse_api import NseApiPlugin
        plugins["nse_api"] = NseApiPlugin()
    except Exception:
        pass
    try:
        from plugins.screener_in import ScreenerInPlugin
        plugins["screener_in"] = ScreenerInPlugin()
    except Exception:
        pass
    try:
        from plugins.tickertape import TickertapePlugin
        plugins["tickertape"] = TickertapePlugin()
    except Exception:
        pass
    try:
        from plugins.bse_filings import BseFilingsPlugin
        plugins["bse_filings"] = BseFilingsPlugin()
    except Exception:
        pass
    return plugins


def build_cache(no_cache: bool = False) -> CacheManager:
    """Return a cache instance, respecting CLI no-cache semantics."""
    return CacheManager(disabled=True) if no_cache else CacheManager()


def normalise_growth_arg(value: float | None) -> float | None:
    """
    CLI growth inputs are percentages: 5 means 5%.
    For backwards compatibility, decimal inputs below 1 are accepted as-is.
    """
    if value is None:
        return None
    return value / 100.0 if abs(value) >= 1 else value


def validate_snapshot(snapshot, skip_validation: bool = False) -> list:
    """Run the canonical object-level validation gate and attach issues."""
    if skip_validation:
        snapshot.validation_issues = []
        return []
    issues = DataValidator().validate(snapshot)
    snapshot.validation_issues = issues
    return issues


async def run_analyze(args) -> dict:
    cache = build_cache(args.no_cache)
    pipeline = AnalysisPipeline(plugins=build_plugins(args.no_cache), cache=cache)
    config = PipelineConfig(
        ticker=args.ticker,
        exchange=args.exchange,
        output_format=args.output,
        skip_validation=args.skip_validation,
        save_report=True,
    )
    result = await pipeline.run(config)
    return {
        "success": result.success,
        "stdout": result.report_markdown or result.error or "No output",
        "reportPath": result.report_path,
        "stage": result.stage,
        "elapsed": result.elapsed_seconds,
    }


async def run_scenario(args) -> dict:
    from core.fetcher import DataFetcher
    from core.normalizer import DataNormalizer
    from core.renderer import ReportRenderer
    from core.scenarios import earnings_scenarios

    cache = build_cache(args.no_cache)
    fetcher = DataFetcher(plugins=build_plugins(args.no_cache), cache=cache)
    bundle = await fetcher.fetch_all(args.ticker)
    normalizer = DataNormalizer()
    snapshot = normalizer.normalise(bundle, ticker=args.ticker, exchange=args.exchange)
    validation_issues = validate_snapshot(snapshot, args.skip_validation)

    assumptions = {}
    if args.bear is not None:
        assumptions["Bear"] = normalise_growth_arg(args.bear)
    if args.base is not None:
        assumptions["Base"] = normalise_growth_arg(args.base)
    if args.bull is not None:
        assumptions["Bull"] = normalise_growth_arg(args.bull)

    sc = earnings_scenarios(
        snapshot,
        assumptions=assumptions or None,
        horizon_years=args.horizon or 3,
    )

    renderer = ReportRenderer()
    snapshot.scenarios = sc
    md = renderer.render_markdown(
        snapshot=snapshot,
        scenarios=sc,
        validation_issues=validation_issues,
    )
    path = renderer.save(md, args.ticker + "_scenario")
    return {"success": True, "stdout": md, "reportPath": path}


async def run_compare(args) -> dict:
    """
    Fetch and compare a peer group. Tickers passed via --tickers.
    Returns a JSON envelope with a markdown comparison table.
    """
    from core.fetcher import DataFetcher
    from core.analyzer import EquityAnalyzer
    from core.peer import PeerComparisonPipeline

    tickers = args.tickers or (args.ticker.split(",") if args.ticker else [])
    if not tickers:
        return {"success": False, "stdout": "No tickers provided for compare.", "reportPath": None}

    cache    = build_cache(args.no_cache)
    fetcher  = DataFetcher(plugins=build_plugins(args.no_cache), cache=cache)
    analyzer = EquityAnalyzer()

    pipeline = PeerComparisonPipeline(fetcher=fetcher, validator=DataValidator(), analyzer=analyzer)
    result   = await pipeline.run(tickers)

    # Build a simple markdown table
    md_lines = [f"# Peer Comparison — {', '.join(tickers)}\n"]
    if result.errors:
        md_lines.append("## Errors\n")
        for t, err in result.errors.items():
            md_lines.append(f"- {t}: {err}")
        md_lines.append("")

    if result.comparison_table:
        active = list(result.comparison_table.keys())
        header = "| Metric | " + " | ".join(result.snapshots.keys()) + " | Sector Median |"
        sep    = "| --- |" + " --- |" * (len(result.snapshots) + 1)
        md_lines += [header, sep]
        for metric in active:
            row = result.comparison_table[metric]
            cells = [
                str(row.get(t)) if row.get(t) is not None else "N/A"
                for t in result.snapshots
            ]
            median = result.sector_medians.get(metric)
            median_str = f"{median:.2f}" if median is not None else "N/A"
            md_lines.append(f"| {metric} | " + " | ".join(cells) + f" | {median_str} |")

    from core.renderer import ReportRenderer
    renderer  = ReportRenderer()
    md        = "\n".join(md_lines)
    md        = md + "\n\n" + render_disclaimer(ticker="_".join(tickers))
    label     = "_".join(t.upper() for t in tickers[:3])
    path      = renderer.save(md, f"{label}_peer")
    return {"success": True, "stdout": md, "reportPath": path}


async def run_warmup(args) -> dict:
    """Pre-populate cache for one or more tickers."""
    from core.fetcher import DataFetcher

    tickers = args.tickers or ([args.ticker] if args.ticker else [])
    if not tickers:
        return {"success": False, "stdout": "No tickers provided for warmup.", "reportPath": None}

    cache   = build_cache(False)
    fetcher = DataFetcher(plugins=build_plugins(), cache=cache)

    output_lines: list[str] = []
    for ticker in tickers:
        results = cache.warm_ticker(ticker.upper(), fetcher)
        output_lines.append(f"{ticker.upper()}:")
        for data_type, status in results.items():
            output_lines.append(f"  {data_type}: {status}")

    return {"success": True, "stdout": "\n".join(output_lines), "reportPath": None}


async def run_report(args) -> dict:
    """
    Generate a branded PDF (or HTML) report using PDFReportExporter.
    Falls back to run_analyze() markdown if Weasyprint is unavailable.
    """
    cache = build_cache(args.no_cache)
    pipeline = AnalysisPipeline(plugins=build_plugins(args.no_cache), cache=cache)
    config = PipelineConfig(
        ticker=args.ticker,
        exchange=args.exchange,
        output_format="markdown",
        skip_validation=args.skip_validation,
        save_report=False,
    )
    result = await pipeline.run(config)
    if not result.success:
        return {
            "success": False,
            "stdout": result.error or "Report generation failed before render.",
            "reportPath": None,
            "stage": result.stage,
        }
    snapshot = result.snapshot

    dest_dir = args.output_dir or None

    try:
        from plugins.pdf_export import PDFReportExporter
        exporter = PDFReportExporter(dest_dir=dest_dir)

        if getattr(args, "format", "pdf") == "html":
            import os
            html_str = exporter.render_html(snapshot)
            from pathlib import Path
            html_dir = Path(dest_dir).expanduser() if dest_dir else Path.home() / "Downloads"
            html_dir.mkdir(parents=True, exist_ok=True)
            html_path = html_dir / f"{snapshot.ticker.upper()}_equilis_{datetime.now():%Y%m%d}.html"
            html_path.write_text(html_str, encoding="utf-8")
            filepath = str(html_path)
            return {"success": True, "stdout": f"HTML report saved: {filepath}", "reportPath": filepath}
        else:
            filepath = exporter.export_analysis(snapshot, dest_dir=dest_dir)
            return {"success": True, "stdout": f"PDF report saved: {filepath}", "reportPath": filepath}
    except Exception as exc:
        logger.warning("PDF export failed (%s), falling back to markdown", exc)
        return await run_analyze(args)


async def run_screen(args) -> dict:
    """Run a quantitative screen and append the standard disclaimer."""
    from core.fetcher import DataFetcher
    from core.screener import FundamentalScreener
    from core.renderer import ReportRenderer

    filters = []
    if args.min_roe is not None:
        filters.append(f"roe>={args.min_roe}")
    if args.max_pe is not None:
        filters.append(f"pe_ratio<={args.max_pe}")
    if args.min_mcap is not None:
        filters.append(f"market_cap>={args.min_mcap}")

    fetcher = DataFetcher(plugins=build_plugins(args.no_cache), cache=build_cache(args.no_cache))
    screener = FundamentalScreener(fetcher)
    result = await screener.run(sector=args.sector or None, filters=filters)

    lines = [
        "# Quantitative Screen",
        "",
        f"Universe size: {result.universe_size}",
        f"Matched: {result.matched_count}",
        "",
        "| Ticker | Sector |",
        "| --- | --- |",
    ]
    for row in result.results:
        lines.append(f"| {row.get('ticker')} | {row.get('sector', 'Unknown')} |")
    md = "\n".join(lines) + "\n\n" + render_disclaimer(ticker="SCREEN")
    path = ReportRenderer().save(md, "SCREEN")
    return {"success": True, "stdout": md, "reportPath": path}


async def main():
    parser = argparse.ArgumentParser(description="Equilis India CLI Python runner")
    parser.add_argument("--command", default="analyze",
                        choices=["analyze", "compare", "scenario", "report", "screen", "warmup"])
    parser.add_argument("--ticker", default="")
    parser.add_argument("--tickers", nargs="+", default=[])
    parser.add_argument("--output", default="markdown", choices=["markdown", "pdf", "json"])
    parser.add_argument("--output-dir", default="")
    parser.add_argument("--exchange", default="NSE")
    parser.add_argument("--skip-validation", action="store_true")
    parser.add_argument("--no-cache", action="store_true")
    parser.add_argument("--bear", type=float, default=None)
    parser.add_argument("--base", type=float, default=None)
    parser.add_argument("--bull", type=float, default=None)
    parser.add_argument("--horizon", type=int, default=3)
    parser.add_argument("--sector", default="")
    parser.add_argument("--min-roe", type=float, default=None)
    parser.add_argument("--max-pe", type=float, default=None)
    parser.add_argument("--min-mcap", type=float, default=None)
    parser.add_argument("--format", default="pdf", choices=["pdf", "html"])

    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

    try:
        if args.command == "report":
            result = await run_report(args)
        elif args.command == "analyze":
            result = await run_analyze(args)
        elif args.command == "scenario":
            result = await run_scenario(args)
        elif args.command == "compare":
            result = await run_compare(args)
        elif args.command == "warmup":
            result = await run_warmup(args)
        elif args.command == "screen":
            result = await run_screen(args)
        else:
            result = {
                "success": False,
                "stdout": f"Command '{args.command}' not yet implemented.",
                "reportPath": None,
            }
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "stdout": str(e), "reportPath": None}))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
