"""
core/beneish.py
Computes the Beneish M-score for earnings manipulation risk assessment.
Usage: python core/beneish.py --ticker RELIANCE --file data/RELIANCE.json
Requires two years of financial data in the JSON file.
"""

import argparse
import json


def safe_div(numerator, denominator):
    if denominator == 0 or denominator is None or numerator is None:
        return None
    return numerator / denominator


def compute_beneish(year1: dict, year2: dict) -> dict:
    """
    year1 = more recent year, year2 = prior year.
    Each dict should have: revenue, gross_profit, total_assets, current_assets,
    ppe (property plant equipment), depreciation, sga (selling general admin),
    total_debt, trade_receivables, net_income, ocf, cogs.
    Returns dict with each component and final M-score.
    """
    # 1. DSRI — Days Sales Receivable Index
    dsri = safe_div(
        safe_div(year1.get("trade_receivables"), year1.get("revenue")),
        safe_div(year2.get("trade_receivables"), year2.get("revenue"))
    )

    # 2. GMI — Gross Margin Index
    gm1 = safe_div(year1.get("gross_profit"), year1.get("revenue"))
    gm2 = safe_div(year2.get("gross_profit"), year2.get("revenue"))
    gmi = safe_div(gm2, gm1)

    # 3. AQI — Asset Quality Index
    aqi = safe_div(
        1 - safe_div(
            (year1.get("current_assets", 0) or 0) + (year1.get("ppe", 0) or 0),
            year1.get("total_assets")
        ),
        1 - safe_div(
            (year2.get("current_assets", 0) or 0) + (year2.get("ppe", 0) or 0),
            year2.get("total_assets")
        )
    )

    # 4. SGI — Sales Growth Index
    sgi = safe_div(year1.get("revenue"), year2.get("revenue"))

    # 5. DEPI — Depreciation Index
    dep_rate1 = safe_div(year1.get("depreciation"), (year1.get("depreciation", 0) or 0) + (year1.get("ppe", 1) or 1))
    dep_rate2 = safe_div(year2.get("depreciation"), (year2.get("depreciation", 0) or 0) + (year2.get("ppe", 1) or 1))
    depi = safe_div(dep_rate2, dep_rate1)

    # 6. SGAI — SG&A Index
    sgai = safe_div(
        safe_div(year1.get("sga"), year1.get("revenue")),
        safe_div(year2.get("sga"), year2.get("revenue"))
    )

    # 7. LVGI — Leverage Index
    lev1 = safe_div(year1.get("total_debt"), year1.get("total_assets"))
    lev2 = safe_div(year2.get("total_debt"), year2.get("total_assets"))
    lvgi = safe_div(lev1, lev2)

    # 8. TATA — Total Accruals to Total Assets
    tata = safe_div(
        (year1.get("net_income", 0) or 0) - (year1.get("ocf", 0) or 0),
        year1.get("total_assets")
    )

    components = {
        "DSRI": dsri, "GMI": gmi, "AQI": aqi, "SGI": sgi,
        "DEPI": depi, "SGAI": sgai, "LVGI": lvgi, "TATA": tata
    }

    # M-score formula (Beneish 1999)
    none_count = sum(1 for v in components.values() if v is None)
    if none_count > 2:
        m_score = None
    else:
        def n(v): return v if v is not None else 1.0
        m_score = (
            -4.840
            + 0.920 * n(dsri)
            + 0.528 * n(gmi)
            + 0.404 * n(aqi)
            + 0.892 * n(sgi)
            + 0.115 * n(depi)
            - 0.172 * n(sgai)
            + 4.679 * n(tata)
            - 0.327 * n(lvgi)
        )

    return {"components": components, "m_score": m_score, "missing_fields": none_count}


def interpret(m_score) -> str:
    if m_score is None:
        return "INCONCLUSIVE — insufficient data"
    if m_score > -1.78:
        return "🔴 MANIPULATION LIKELY — investigate further (M > -1.78)"
    elif m_score > -2.22:
        return "🟡 GREY ZONE — review flagged components (–2.22 < M < –1.78)"
    else:
        return "✅ LOW RISK — unlikely manipulation based on this model alone"


def main():
    parser = argparse.ArgumentParser(description="Compute Beneish M-score.")
    parser.add_argument("--file", required=True, help="JSON data file with two years of financials")
    args = parser.parse_args()

    with open(args.file) as f:
        data = json.load(f)

    fundamentals = data.get("fundamentals", {})
    # Expect fundamentals to contain year1 and year2 sub-dicts
    year1 = fundamentals.get("year1")
    year2 = fundamentals.get("year2")

    if not year1 or not year2:
        print("ERROR: Data file must contain fundamentals.year1 and fundamentals.year2")
        return

    result = compute_beneish(year1, year2)
    score = result["m_score"]

    print(f"\nBeneish M-score: {score:.4f}" if score else "\nBeneish M-score: N/A")
    print(f"Interpretation: {interpret(score)}")
    print(f"Missing fields: {result['missing_fields']}/8")
    print("\nComponents:")
    for k, v in result["components"].items():
        print(f"  {k}: {v:.4f}" if v is not None else f"  {k}: N/A")
    print("\nNote: Beneish was calibrated on US data. Apply with India-specific judgment.")
    print("RPT (related-party transactions) manipulation is not captured by this model.")


if __name__ == "__main__":
    main()
