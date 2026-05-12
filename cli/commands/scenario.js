/**
 * cli/commands/scenario.js
 * equilis scenario <ticker> — Bear / Base / Bull scenario analysis.
 */

import { spawn } from "child_process";
import path from "path";
import { withSpinner } from "../utils/spinner.js";
import { fmt, printHeader, printResult } from "../utils/formatter.js";

const REPO_ROOT = new URL("../../", import.meta.url).pathname;
const PIPELINE_SCRIPT = path.join(REPO_ROOT, "core", "_cli_runner.py");

export async function scenarioCommand(ticker, options) {
  printHeader(`Scenario Analysis — ${ticker.toUpperCase()}`);

  const args = [
    PIPELINE_SCRIPT,
    "--command", "scenario",
    "--ticker", ticker.toUpperCase(),
  ];
  if (options.bear != null) args.push("--bear", String(options.bear));
  if (options.base != null) args.push("--base", String(options.base));
  if (options.bull != null) args.push("--bull", String(options.bull));
  if (options.horizon != null) args.push("--horizon", String(options.horizon));
  if (options.skipValidation) args.push("--skip-validation");
  if (options.noCache) args.push("--no-cache");

  try {
    const result = await withSpinner(
      `Running scenarios for ${ticker.toUpperCase()}`,
      () => runPython(args),
    );
    console.log("\n" + result.stdout);
    if (result.reportPath) {
      printResult(true, `Report saved to: ${fmt.cyan(result.reportPath)}`);
    }
  } catch (err) {
    printResult(false, `Scenario analysis failed: ${err.message}`);
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
      if (code !== 0) reject(new Error(stderr || `exit ${code}`));
      else { try { resolve(JSON.parse(stdout)); } catch { resolve({ stdout }); } }
    });
  });
}
