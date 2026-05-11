/**
 * cli/commands/warmup.js
 * `equilis warmup` — pre-populate the cache for one or more tickers.
 *
 * Usage:
 *   equilis warmup INFY
 *   equilis warmup INFY TCS WIPRO
 */

import { runPython } from "../utils/runner.js";

export function registerWarmup(program) {
  program
    .command("warmup <tickers...>")
    .description("Pre-populate the local cache for one or more tickers")
    .option("--no-cache", "Disable cache (dry-run — fetches but does not store)")
    .action(async (tickers, options) => {
      const ora = (await import("ora")).default;
      const spinner = ora(`Warming cache for ${tickers.join(", ")}…`).start();

      try {
        const pyArgs = [
          "--command", "warmup",
          "--tickers", ...tickers,
        ];
        if (options.noCache) pyArgs.push("--no-cache");

        const result = await runPython(pyArgs);

        if (result.success) {
          spinner.succeed("Cache warm-up complete");
          console.log(result.stdout);
        } else {
          spinner.fail("Cache warm-up failed");
          console.error(result.stdout);
          process.exit(1);
        }
      } catch (err) {
        spinner.fail(`Error: ${err.message}`);
        process.exit(1);
      }
    });
}
