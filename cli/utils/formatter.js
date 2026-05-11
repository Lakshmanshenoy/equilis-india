/**
 * cli/utils/formatter.js
 * Terminal output formatting utilities.
 */

const RESET = "\x1b[0m";
const BOLD = "\x1b[1m";
const RED = "\x1b[31m";
const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const CYAN = "\x1b[36m";
const DIM = "\x1b[2m";

export const fmt = {
  bold: (s) => `${BOLD}${s}${RESET}`,
  red: (s) => `${RED}${s}${RESET}`,
  green: (s) => `${GREEN}${s}${RESET}`,
  yellow: (s) => `${YELLOW}${s}${RESET}`,
  cyan: (s) => `${CYAN}${s}${RESET}`,
  dim: (s) => `${DIM}${s}${RESET}`,
};

/** Print a section header */
export function printHeader(text) {
  const line = "─".repeat(Math.min(process.stdout.columns || 80, 80));
  console.log(`\n${fmt.bold(fmt.cyan(text))}`);
  console.log(fmt.dim(line));
}

/** Print key-value pairs in a simple table */
export function printKV(pairs) {
  const maxKey = Math.max(...pairs.map(([k]) => k.length));
  for (const [key, value] of pairs) {
    const padding = " ".repeat(maxKey - key.length);
    console.log(`  ${fmt.bold(key)}${padding}  ${value}`);
  }
}

/** Print a 2D table from headers + rows */
export function printTable(headers, rows) {
  const widths = headers.map((h, i) =>
    Math.max(h.length, ...rows.map((r) => String(r[i] ?? "").length))
  );
  const sep = widths.map((w) => "─".repeat(w + 2)).join("┼");
  const row = (cells) =>
    cells.map((c, i) => ` ${String(c ?? "N/A").padEnd(widths[i])} `).join("│");
  console.log(`┌${widths.map((w) => "─".repeat(w + 2)).join("┬")}┐`);
  console.log(`│${row(headers)}│`);
  console.log(`├${sep}┤`);
  for (const r of rows) {
    console.log(`│${row(r)}│`);
  }
  console.log(`└${widths.map((w) => "─".repeat(w + 2)).join("┴")}┘`);
}

/** Print success/failure summary */
export function printResult(success, message) {
  if (success) {
    console.log(`\n${fmt.green("✓")} ${message}`);
  } else {
    console.log(`\n${fmt.red("✗")} ${message}`);
  }
}

/** Format a float as INR (₹ Crore) */
export function fmtCrore(value) {
  if (value == null) return "N/A";
  return `₹${Number(value).toLocaleString("en-IN", { maximumFractionDigits: 0 })} Cr`;
}

/** Format a float as percentage */
export function fmtPct(value, decimals = 1) {
  if (value == null) return "N/A";
  return `${(value * 100).toFixed(decimals)}%`;
}
