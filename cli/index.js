#!/usr/bin/env node
/**
 * cli/index.js
 * Equilis India CLI — equity research tool for Indian markets.
 * Entry point: registers all sub-commands and delegates to command handlers.
 */

import { Command } from "commander";
import { analyzeCommand } from "./commands/analyze.js";
import { compareCommand } from "./commands/compare.js";
import { screenCommand } from "./commands/screen.js";
import { scenarioCommand } from "./commands/scenario.js";
import { reportCommand } from "./commands/report.js";
import { registerWarmup } from "./commands/warmup.js";

const program = new Command();

program
  .name("equilis")
  .description("Equilis India — fundamental equity research for Indian markets")
  .version("2.0.0");

program
  .command("analyze <ticker>")
  .description("Full fundamental analysis for a single ticker")
  .option("-o, --output <format>", "Output format: markdown | pdf | json", "markdown")
  .option("--no-cache", "Bypass cache and force live fetch")
  .option("--skip-validation", "Skip data quality validation gate")
  .option("--exchange <exchange>", "Exchange: NSE | BSE", "NSE")
  .action(analyzeCommand);

program
  .command("compare <tickers...>")
  .description("Peer-to-peer comparison table for 2–5 tickers")
  .option("-o, --output <format>", "Output format: markdown | pdf", "markdown")
  .option("--no-cache", "Bypass cache and force live fetch")
  .action(compareCommand);

program
  .command("screen")
  .description("Screen stocks by financial criteria")
  .option("--sector <sector>", "Filter by sector (e.g. IT, Banking, FMCG)")
  .option("--min-roe <pct>", "Minimum ROE (%)", parseFloat)
  .option("--max-pe <multiple>", "Maximum P/E multiple", parseFloat)
  .option("--min-mcap <crore>", "Minimum market cap (₹ Crore)", parseFloat)
  .option("--no-cache", "Bypass cache and force live fetch")
  .action(screenCommand);

program
  .command("scenario <ticker>")
  .description("Bear / Base / Bull scenario analysis")
  .option("--bear <growth>", "Bear case PAT growth rate as percent (e.g. 5)", parseFloat)
  .option("--base <growth>", "Base case PAT growth rate as percent (e.g. 12)", parseFloat)
  .option("--bull <growth>", "Bull case PAT growth rate as percent (e.g. 20)", parseFloat)
  .option("--horizon <years>", "Projection horizon in years (default 3)", parseInt)
  .option("--no-cache", "Bypass cache and force live fetch")
  .option("--skip-validation", "Skip data quality validation gate")
  .action(scenarioCommand);

program
  .command("report <ticker>")
  .description("Generate full PDF research report")
  .option("-o, --output-dir <dir>", "Output directory (default ~/Downloads/equilis-reports)")
  .option("--exchange <exchange>", "Exchange: NSE | BSE", "NSE")
  .option("--format <type>", "pdf | html (html for preview/debug)", "pdf")
  .option("--no-cache", "Bypass cache and force live fetch")
  .option("--skip-validation", "Skip data quality validation gate")
  .action(reportCommand);

registerWarmup(program);

program.parse(process.argv);
