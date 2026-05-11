"""
core/beneish.py
Computes the Beneish M-score for earnings manipulation risk assessment.
Usage: python core/beneish.py --file data/RELIANCE.json

Requires two years of financial data in the JSON file under:
  fundamentals.year1  (more recent year)
  fundamentals.year2  (prior year)

Each year dict should contain:
  revenue, gross_profit, total_assets, current_assets,
  ppe, depreciation, sga, total_debt, trade_receivables,
  net_income, ocf, cogs
"""

import argparse
import json


# FIX: Components with the highest formula coefficients.
# If any of these are None, the model refuses to produce a score
# rather than silently substituting 1.0 and distorting the result.
# Coefficients: TATA=4.679, SGI=0.892, DSRI=0.920
HIGH_WEIGHT_COMPONENTS = {"TATA", "SGI", "DSRI"}


def safe_div(numerator, denominator):
    if denominator == 0 or denominator is None or numerator is None:
        return None
    return numerator / denominator


def compute_beneish(year1: dict, year2: dict) -> dict:
    """
    year1 = more recent year, year2 = prior year.
    Returns dict with each component, final M-score, and missing_fields count.
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
    dep_rate1 = safe_div(
        year1.get("depreciation"),
        (year1.get("depreciation", 0) or 0) + (year1.get("ppe", 1) or 1)
    )
    dep_rate2 = safe_div(
        year2.get("depreciation"),
        (year2.get("depreciation", 0) or 0) + (year2.get("ppe", 1) or 1)
    )
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

    none_count = sum(1 for v in components.values() if v is None)

    # FIX: Refuse to score if any high-weight component is missing.
    # Previously, None was substituted with 1.0, which silently added
    # up to +4.679 (TATA coefficient) to the score, potentially flagging
    # a clean company as a manipulator due to missing data alone.
    missing_high_weight = any(
        components[k] is None for k in HIGH_WEIGHT_COMPONENTS
    )

    if none_count > 2 or missing_high_weight:
        m_score = None
        score_refused = True
    else:
        score_refused = False
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

    return {
        "components": components,
        "m_score": m_score,
        "missing_fields": none_count,
        "score_refused": score_refused,
    }


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

    # FIX: --ticker removed from argparse; ticker and fetch date now read
    # from the data file itself (set by fetch.py), so the output header
    # is always consistent with the data being scored.
    ticker = data.get("ticker", "UNKNOWN")
    fetched_at = data.get("fetched_at", "N/A")

    print(f"\n{'=' * 52}")
    print(f"  Beneish M-score — {ticker}  |  Fetched: {fetched_at}")
    print(f"{'=' * 52}")

    fundamentals = data.get("fundamentals", {})
    year1 = fundamentals.get("year1")
    year2 = fundamentals.get("year2")

    if not year1 or not year2:
        print("ERROR: Data file must contain fundamentals.year1 and fundamentals.year2")
        return

    result = compute_beneish(year1, year2)
    score = result["m_score"]

    print(f"\nM-score:        {f'{score:.4f}' if score is not None else 'N/A (refused)'}")
    print(f"Interpretation: {interpret(score)}")
    print(f"Missing fields: {result['missing_fields']}/8")

    if result["score_refused"] and result["missing_fields"] <= 2:
        missing = [k for k in HIGH_WEIGHT_COMPONENTS if result["components"][k] is None]
        print(f"Score refused:  high-weight component(s) missing — {', '.join(missing)}")
        print("                Ensure trade_receivables and revenue are present in both years.")

    print("\nComponents:")
    for k, v in result["components"].items():
        flag = " ← high weight" if k in HIGH_WEIGHT_COMPONENTS else ""
        print(f"  {k:<6} {f'{v:.4f}' if v is not None else 'N/A':>10}{flag}")

    print("\nNotes:")
    print("  Beneish was calibrated on US data. Apply with India-specific judgment.")
    print("  RPT (related-party transactions) manipulation is not captured by this model.")
    print("  A flag here means investigate further — not a conclusion of fraud.")


if __name__ == "__main__":
    main()
