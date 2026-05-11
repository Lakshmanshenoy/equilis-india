/**
 * cli/commands/screen.js
 * equilis screen — filter stocks by financial criteria.
 */

import { spawn } from "child_process";
import path from "path";
import { withSpinner } from "../utils/spinner.js";
import { fmt, printHeader, printResult } from "../utils/formatter.js";

const REPO_ROOT = new URL("../../", import.meta.url).pathname;
const PIPELINE_SCRIPT = path.join(REPO_ROOT, "core", "_cli_runner.py");

export async function screenCommand(options) {
  printHeader("Stock Screener");

  const args = [PIPELINE_SCRIPT, "--command", "screen"];
  if (options.sector) args.push("--sector", options.sector);
  if (options.minRoe != null) args.push("--min-roe", String(options.minRoe));
  if (options.maxPe != null) args.push("--max-pe", String(options.maxPe));
  if (options.minMcap != null) args.push("--min-mcap", String(options.minMcap));

  try {
    const result = await withSpinner("Screening stocks", () => runPython(args));
    console.log("\n" + result.stdout);
  } catch (err) {
    printResult(false, `Screen failed: ${err.message}`);
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
