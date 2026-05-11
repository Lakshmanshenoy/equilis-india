"""
core/validate.py
Validates fetched financial data against expected ranges and cross-source consistency.
Usage: python core/validate.py --file data/RELIANCE.json
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

    # Required fields
    required = [
        "fundamentals.revenue_5y",
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

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate fetched financial data.")
    parser.add_argument("--file", required=True, help="Path to JSON data file from fetch.py")
    args = parser.parse_args()

    with open(args.file) as f:
        data = json.load(f)

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
