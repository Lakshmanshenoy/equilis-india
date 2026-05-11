"""
core/fetch.py
Fetches financial data for a given NSE ticker from Screener.in.
Usage: python core/fetch.py --ticker RELIANCE --output data/RELIANCE.json
"""

import argparse
import json
import datetime
import sys


def fetch_screener(ticker: str) -> dict:
    """
    Placeholder: implement web scraping or Screener.in API call here.
    Returns a dict with standardised field names.

    Fields to fetch:
    - revenue_5y: list of last 5 years' revenue (₹ Cr)
    - ebitda_5y: list of last 5 years' EBITDA (₹ Cr)
    - pat_5y: list of last 5 years' PAT (₹ Cr)
    - ocf_5y: list of last 5 years' operating cash flow (₹ Cr)
    - total_debt: latest (₹ Cr)
    - cash: latest (₹ Cr)
    - book_value_per_share: latest (₹)
    - eps_ttm: latest TTM diluted EPS (₹)
    - roce_5y: list of last 5 years' ROCE (%)
    - roe_5y: list of last 5 years' ROE (%)
    - promoter_holding: latest (%)
    - promoter_pledging: latest (%)
    - trade_receivables_5y: list (₹ Cr)
    - inventory_5y: list (₹ Cr)
    - trade_payables_5y: list (₹ Cr)
    """
    raise NotImplementedError(
        "Implement Screener.in fetch here. "
        "Use requests + BeautifulSoup or Screener.in export API."
    )


def fetch_live_price(ticker: str) -> dict:
    """
    Fetches live CMP, 52W high, 52W low from NSE.
    Placeholder: implement NSE API call here.
    """
    raise NotImplementedError(
        "Implement NSE live price fetch here. "
        "Use nseindia.com/api/quote-equity?symbol=<TICKER>"
    )


def main():
    parser = argparse.ArgumentParser(description="Fetch financial data for an NSE ticker.")
    parser.add_argument("--ticker", required=True, help="NSE ticker symbol, e.g. RELIANCE")
    parser.add_argument("--output", default=None, help="Output JSON file path")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    print(f"Fetching data for {ticker}...")

    try:
        fundamentals = fetch_screener(ticker)
        price_data = fetch_live_price(ticker)
    except NotImplementedError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    output = {
        "ticker": ticker,
        "fetched_at": datetime.datetime.utcnow().isoformat() + "Z",
        "fundamentals": fundamentals,
        "price": price_data,
    }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"Saved to {args.output}")
    else:
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
