/**
 * cli/utils/spinner.js
 * Terminal spinner utility using ora (graceful fallback if not installed).
 */

let ora;
try {
  const oraModule = await import("ora");
  ora = oraModule.default;
} catch {
  // Graceful fallback — plain console logging
  ora = (text) => ({
    start: () => { process.stdout.write(`⏳ ${text}...\n`); return { succeed: (t) => console.log(`✓ ${t || text}`), fail: (t) => console.error(`✗ ${t || text}`), text: "" }; },
  });
}

/**
 * Wrap an async operation with a spinner.
 * @param {string} label - Spinner text
 * @param {Function} fn  - Async function to execute
 * @returns {*} Result of fn()
 */
export async function withSpinner(label, fn) {
  const spinner = ora(label).start();
  try {
    const result = await fn();
    spinner.succeed(label);
    return result;
  } catch (err) {
    spinner.fail(`${label} — ${err.message}`);
    throw err;
  }
}

export { ora };
