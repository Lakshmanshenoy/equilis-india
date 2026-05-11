/**
 * cli/commands/report.js
 * equilis report <ticker> — generate a full PDF research report.
 */

import { spawn } from "child_process";
import os from "os";
import path from "path";
import { withSpinner } from "../utils/spinner.js";
import { fmt, printHeader, printResult } from "../utils/formatter.js";

const REPO_ROOT = new URL("../../", import.meta.url).pathname;
const PIPELINE_SCRIPT = path.join(REPO_ROOT, "core", "_cli_runner.py");
const DEFAULT_OUTPUT_DIR = path.join(os.homedir(), "Downloads", "equilis-reports");

export async function reportCommand(ticker, options) {
  printHeader(`Generating PDF Report — ${ticker.toUpperCase()}`);

  const outputDir = options.outputDir || DEFAULT_OUTPUT_DIR;
  const args = [
    PIPELINE_SCRIPT,
    "--command", "report",
    "--ticker", ticker.toUpperCase(),
    "--output", "pdf",
    "--output-dir", outputDir,
    "--exchange", options.exchange || "NSE",
  ];

  try {
    const result = await withSpinner(
      `Building PDF report for ${ticker.toUpperCase()}`,
      () => runPython(args),
    );
    const reportPath = result.reportPath || `${outputDir}/${ticker.toUpperCase()}_*.pdf`;
    printResult(true, `PDF report saved to: ${fmt.cyan(reportPath)}`);
  } catch (err) {
    printResult(false, `Report generation failed: ${err.message}`);
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
      else { try { resolve(JSON.parse(stdout)); } catch { resolve({ stdout, reportPath: null }); } }
    });
  });
}
