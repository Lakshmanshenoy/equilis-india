/**
 * cli/utils/runner.js
 * Shared helper — spawn the Python CLI runner and return a Promise.
 * All CLI commands should import this instead of duplicating child_process logic.
 */

import { spawn } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const RUNNER_PATH = path.resolve(__dirname, "../../core/_cli_runner.py");

/**
 * Run the Python CLI runner with the given args array.
 *
 * @param {string[]} pyArgs  - CLI args to pass, e.g. ["--command", "analyze", "--ticker", "INFY"]
 * @returns {Promise<{success: boolean, stdout: string, reportPath: string|null}>}
 */
export function runPython(pyArgs) {
  return new Promise((resolve, reject) => {
    const child = spawn("python3", [RUNNER_PATH, ...pyArgs], {
      cwd: path.resolve(__dirname, "../.."),
      env: { ...process.env },
    });

    let stdoutBuf = "";
    let stderrBuf = "";

    child.stdout.on("data", (chunk) => {
      stdoutBuf += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderrBuf += chunk.toString();
    });

    child.on("close", (code) => {
      try {
        const result = JSON.parse(stdoutBuf.trim());
        resolve(result);
      } catch {
        if (code !== 0) {
          reject(new Error(stderrBuf || `Python exited with code ${code}`));
        } else {
          resolve({ success: true, stdout: stdoutBuf, reportPath: null });
        }
      }
    });

    child.on("error", (err) => reject(err));
  });
}
