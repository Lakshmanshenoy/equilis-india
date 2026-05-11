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


async def main():
    parser = argparse.ArgumentParser(description="Equilis India CLI Python runner")
    parser.add_argument("--command", default="analyze",
                        choices=["analyze", "compare", "scenario", "report", "screen"])
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
