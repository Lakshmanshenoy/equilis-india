"""
core/validate.py
Validates fetched financial data against expected ranges and cross-source consistency.
Usage: python core/validate.py --file data/RELIANCE.json

Expected JSON structure:
{
  "ticker": "RELIANCE",
  "fetched_at": "2025-05-01T10:00:00Z",
  "fundamentals": {
    "revenue_5y":         [450000, 480000, 510000, 530000, 560000],
    "ebitda_5y":          [80000,  85000,  90000,  95000, 100000],
    "pat_5y":             [23000,  25000,  28000,  30000,  32000],
    "ocf_5y":             [20000,  22000,  25000,  27000,  29000],
    "total_debt":         120000,
    "cash":               35000,
    "eps_ttm":            47.5,
    "promoter_holding":   50.1,
    "promoter_pledging":  0.0,
    "trade_receivables_5y": [18000, 20000, 22000, 24000, 26000],
    "inventory_5y":       [60000, 65000, 70000, 72000, 75000],
    "trade_payables_5y":  [40000, 43000, 46000, 48000, 51000],
    "screener": {
      "revenue_ttm":          560000,
      "pat_ttm":               32000,
      "total_debt":           120000,
      "book_value_per_share":    185
    },
    "bse": {
      "revenue_ttm":          561200,
      "pat_ttm":               32100,
      "total_debt":           120000,
      "book_value_per_share":    185
    }
  },
  "price": {
    "cmp":        2850.0,
    "week52_high": 3024.0,
    "week52_low":  2220.0
  }
}
"""

import argparse
import json
import sys

TOLERANCE = 0.05  # 5% tolerance for cross-source discrepancy


def validate_field_present(data: dict, field: str, path: str = "") -> list:
    """Returns a list of error strings if field is missing."""
    errors = []
    keys = field.split(".")
    node = data
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            errors.append(f"MISSING FIELD: {path or field}")
            return errors
        node = node[key]
    if node is None:
        errors.append(f"NULL VALUE: {path or field}")
    return errors


def validate_positive(value, field: str) -> list:
    """Returns errors if value is not positive."""
    if value is not None and value <= 0:
        return [f"EXPECTED POSITIVE: {field} = {value}"]
    return []


def validate_range(value, field: str, low: float, high: float) -> list:
    """Returns errors if value is outside expected range."""
    if value is not None and not (low <= value <= high):
        return [f"OUT OF RANGE: {field} = {value} (expected {low}–{high})"]
    return []


def validate_cross_source(val_a, source_a: str, val_b, source_b: str, field: str) -> list:
    """Flags if two sources differ by more than TOLERANCE."""
    errors = []
    if val_a is not None and val_b is not None and val_a != 0:
        diff = abs(val_a - val_b) / abs(val_a)
        if diff > TOLERANCE:
            errors.append(
                f"CROSS-SOURCE MISMATCH ({TOLERANCE*100:.0f}% tolerance): "
                f"{field} — {source_a}: {val_a}, {source_b}: {val_b} "
                f"(diff: {diff*100:.1f}%)"
            )
    return errors


def run_validation(data: dict) -> list:
    """Run all validation checks. Returns list of error strings."""
    errors = []
    fundamentals = data.get("fundamentals", {})
    price = data.get("price", {})

    # FIX 1: ebitda_5y added to required fields
    required = [
        "fundamentals.revenue_5y",
        "fundamentals.ebitda_5y",        # FIX: was missing
        "fundamentals.pat_5y",
        "fundamentals.ocf_5y",
        "fundamentals.total_debt",
        "fundamentals.cash",
        "fundamentals.eps_ttm",
        "fundamentals.promoter_holding",
        "price.cmp",
        "price.week52_high",
        "price.week52_low",
    ]
    for field in required:
        errors.extend(validate_field_present(data, field, field))

    # Sanity ranges
    if "promoter_holding" in fundamentals:
        errors.extend(validate_range(
            fundamentals["promoter_holding"],
            "promoter_holding", 0, 100
        ))
    if "promoter_pledging" in fundamentals:
        errors.extend(validate_range(
            fundamentals["promoter_pledging"],
            "promoter_pledging", 0, 100
        ))
    if "cmp" in price:
        errors.extend(validate_positive(price["cmp"], "price.cmp"))

    # Structural checks on 52W range
    if "week52_high" in price and "week52_low" in price and "cmp" in price:
        if price["cmp"] > price["week52_high"]:
            errors.append(
                f"ANOMALY: CMP {price['cmp']} > 52W High {price['week52_high']} — "
                "fetch may be stale. Re-fetch."
            )
        if price["cmp"] < price["week52_low"]:
            errors.append(
                f"ANOMALY: CMP {price['cmp']} < 52W Low {price['week52_low']} — "
                "fetch may be stale. Re-fetch."
            )

    # FIX 2: validate_cross_source is now actually called
    # Compares Screener.in figures against BSE filing figures for key fields.
    # fetch.py must populate fundamentals.screener and fundamentals.bse sub-dicts.
    screener = fundamentals.get("screener", {})
    bse = fundamentals.get("bse", {})
    cross_check_fields = [
        "revenue_ttm",
        "pat_ttm",
        "total_debt",
        "book_value_per_share",
    ]
    for field in cross_check_fields:
        if field in screener and field in bse:
            errors.extend(validate_cross_source(
                screener[field], "Screener.in",
                bse[field], "BSE filing",
                field
            ))

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate fetched financial data.")
    parser.add_argument("--file", required=True, help="Path to JSON data file from fetch.py")
    args = parser.parse_args()

    with open(args.file) as f:
        data = json.load(f)

    ticker = data.get("ticker", "UNKNOWN")
    fetched_at = data.get("fetched_at", "N/A")
    print(f"\nValidating: {ticker}  |  Fetched: {fetched_at}")
    print("-" * 50)

    errors = run_validation(data)

    if errors:
        print(f"VALIDATION FAILED — {len(errors)} issue(s) found:\n")
        for err in errors:
            print(f"  ✗ {err}")
        sys.exit(1)
    else:
        print("VALIDATION PASSED — all required fields present and within expected ranges.")
        sys.exit(0)


if __name__ == "__main__":
    main()
