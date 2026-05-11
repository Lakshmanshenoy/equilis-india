"""
core/_cli_runner.py
Python entry point called by CLI JS commands via child_process.
Parses CLI args, runs the pipeline, and prints a JSON envelope to stdout.

This file is intentionally thin — it wires CLI args to pipeline.py.
"""

import argparse
import asyncio
import json
import logging
import os
import sys

# Ensure repo root is on the path when called from CLI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import AnalysisPipeline, PipelineConfig


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


async def run_analyze(args) -> dict:
    from core.cache import CacheManager
    cache = None if args.no_cache else CacheManager()
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
    from core.cache import CacheManager
    from core.fetcher import DataFetcher
    from core.normalizer import DataNormalizer
    from core.scenarios import earnings_scenarios

    cache = CacheManager()
    fetcher = DataFetcher(plugins=build_plugins(), cache=cache)
    bundle = await fetcher.fetch_all(args.ticker)
    normalizer = DataNormalizer()
    snapshot = normalizer.normalise(bundle, ticker=args.ticker, exchange=args.exchange)

    assumptions = {}
    if args.bear is not None:
        assumptions["Bear"] = args.bear
    if args.base is not None:
        assumptions["Base"] = args.base
    if args.bull is not None:
        assumptions["Bull"] = args.bull

    sc = earnings_scenarios(
        snapshot,
        assumptions=assumptions or None,
        horizon_years=args.horizon or 3,
    )

    from core.renderer import ReportRenderer
    renderer = ReportRenderer()
    from core.pipeline import AnalysisPipeline  # reuse render helper
    md_lines = [f"# Scenario Analysis — {args.ticker.upper()}\n"]
    for s in sc.scenarios:
        md_lines.append(f"## {s.label} ({s.assumption_pat_growth} PAT CAGR)")
        if s.pe_scenarios:
            md_lines.append("| PE | Value |")
            md_lines.append("| --- | --- |")
            for k, v in s.pe_scenarios.items():
                md_lines.append(f"| {k} | ₹{v:,.1f} |")
        md_lines.append("")
    md_lines.append(f"\n> {sc.compliance_note}")
    md = "\n".join(md_lines)
    path = renderer.save(md, args.ticker + "_scenario")
    return {"success": True, "stdout": md, "reportPath": path}


async def run_compare(args) -> dict:
    """
    Fetch and compare a peer group. Tickers passed via --tickers.
    Returns a JSON envelope with a markdown comparison table.
    """
    from core.cache import CacheManager
    from core.fetcher import DataFetcher
    from core.analyzer import EquityAnalyzer
    from core.peer import PeerComparisonPipeline
    from core.normalizer import DataNormalizer

    tickers = args.tickers or (args.ticker.split(",") if args.ticker else [])
    if not tickers:
        return {"success": False, "stdout": "No tickers provided for compare.", "reportPath": None}

    cache    = None if args.no_cache else CacheManager()
    fetcher  = DataFetcher(plugins=build_plugins(args.no_cache), cache=cache)
    analyzer = EquityAnalyzer()

    pipeline = PeerComparisonPipeline(fetcher=fetcher, validator=None, analyzer=analyzer)
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
    label     = "_".join(t.upper() for t in tickers[:3])
    path      = renderer.save(md, f"{label}_peer")
    return {"success": True, "stdout": md, "reportPath": path}


async def run_warmup(args) -> dict:
    """Pre-populate cache for one or more tickers."""
    from core.cache import CacheManager
    from core.fetcher import DataFetcher

    tickers = args.tickers or ([args.ticker] if args.ticker else [])
    if not tickers:
        return {"success": False, "stdout": "No tickers provided for warmup.", "reportPath": None}

    cache   = CacheManager()
    fetcher = DataFetcher(plugins=build_plugins(), cache=cache)

    output_lines: list[str] = []
    for ticker in tickers:
        results = cache.warm_ticker(ticker.upper(), fetcher)
        output_lines.append(f"{ticker.upper()}:")
        for data_type, status in results.items():
            output_lines.append(f"  {data_type}: {status}")

    return {"success": True, "stdout": "\n".join(output_lines), "reportPath": None}


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

    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

    try:
        if args.command in ("analyze", "report"):
            result = await run_analyze(args)
        elif args.command == "scenario":
            result = await run_scenario(args)
        elif args.command == "compare":
            result = await run_compare(args)
        elif args.command == "warmup":
            result = await run_warmup(args)
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
