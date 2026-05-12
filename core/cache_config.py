"""Shared cache TTL configuration used by fetch and cache layers."""

# TTL values in seconds
CACHE_TTL_SECONDS = {
    "price": 60 * 15,
    "financials": 60 * 60 * 6,
    "shareholding": 60 * 60 * 24,
    "corporate_actions": 60 * 60 * 24,
    "concall": 60 * 60 * 24 * 7,
    "peers": 60 * 60 * 24,
    "news": 60 * 60 * 4,
}
