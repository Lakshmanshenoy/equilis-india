/**
 * cli/commands/compare.js
 * equilis compare <tickers...> — peer comparison table.
 */

import { spawn } from "child_process";
import path from "path";
import { withSpinner } from "../utils/spinner.js";
import { fmt, printHeader, printResult } from "../utils/formatter.js";

const REPO_ROOT = new URL("../../", import.meta.url).pathname;
const PIPELINE_SCRIPT = path.join(REPO_ROOT, "core", "_cli_runner.py");

export async function compareCommand(tickers, options) {
  if (tickers.length < 2) {
    console.error(fmt.red("Error: provide at least 2 tickers to compare."));
    process.exit(1);
  }
  printHeader(`Comparing: ${tickers.map((t) => t.toUpperCase()).join(" vs ")}`);

  const args = [
    PIPELINE_SCRIPT,
    "--command", "compare",
    "--tickers", ...tickers.map((t) => t.toUpperCase()),
    "--output", options.output || "markdown",
  ];

  try {
    const result = await withSpinner(
      `Fetching data for ${tickers.length} tickers`,
      () => runPython(args),
    );
    console.log("\n" + result.stdout);
    if (result.reportPath) {
      printResult(true, `Report saved to: ${fmt.cyan(result.reportPath)}`);
    }
  } catch (err) {
    printResult(false, `Compare failed: ${err.message}`);
    process.exit(1);
  }
}

function runPython(args) {
  return new Promise((resolve, reject) => {
    const proc = spawn("python3", args, {
      cwd: REPO_ROOT,
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (d) => (stdout += d));
    proc.stderr.on("data", (d) => (stderr += d));
    proc.on("close", (code) => {
      if (code !== 0) reject(new Error(stderr || `exit ${code}`));
      else {
        try { resolve(JSON.parse(stdout)); } catch { resolve({ stdout, reportPath: null }); }
      }
    });
  });
}
