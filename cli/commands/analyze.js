/**
 * cli/commands/analyze.js
 * equilis analyze <ticker> — full fundamental analysis.
 * Calls the Python pipeline via child_process and streams output.
 */

import { spawn } from "child_process";
import path from "path";
import { withSpinner } from "../utils/spinner.js";
import { fmt, printHeader, printResult } from "../utils/formatter.js";

const REPO_ROOT = new URL("../../", import.meta.url).pathname;
const PIPELINE_SCRIPT = path.join(REPO_ROOT, "core", "_cli_runner.py");

/**
 * @param {string} ticker
 * @param {object} options
 */
export async function analyzeCommand(ticker, options) {
  printHeader(`Analyzing ${ticker.toUpperCase()}`);

  const args = [
    PIPELINE_SCRIPT,
    "--ticker", ticker.toUpperCase(),
    "--output", options.output || "markdown",
    "--exchange", options.exchange || "NSE",
  ];
  if (options.skipValidation) args.push("--skip-validation");
  if (options.noCache) args.push("--no-cache");

  try {
    const result = await withSpinner(
      `Fetching and analysing ${ticker.toUpperCase()}`,
      () => runPython(args),
    );
    console.log("\n" + result.stdout);
    if (result.reportPath) {
      printResult(true, `Report saved to: ${fmt.cyan(result.reportPath)}`);
    }
  } catch (err) {
    printResult(false, `Analysis failed: ${err.message}`);
    process.exit(1);
  }
}

function runPython(args) {
  return new Promise((resolve, reject) => {
    const proc = spawn("python3", args, { cwd: REPO_ROOT });
    let stdout = "";
    let stderr = "";
    proc.stdout.on("data", (d) => (stdout += d));
    proc.stderr.on("data", (d) => (stderr += d));
    proc.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr || `python3 exited with code ${code}`));
      } else {
        // Parse simple JSON envelope if present, else return raw stdout
        try {
          const parsed = JSON.parse(stdout);
          resolve(parsed);
        } catch {
          resolve({ stdout, reportPath: null });
        }
      }
    });
  });
}
