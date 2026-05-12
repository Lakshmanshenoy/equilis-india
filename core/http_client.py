"""HTTP helpers for resilient aiohttp sessions across data plugins."""

from __future__ import annotations

import os
import ssl


def build_ssl_context() -> ssl.SSLContext:
    """Build an SSL context that prefers certifi CA roots when available."""
    disable_verify = os.getenv("EQUILIS_DISABLE_SSL_VERIFY", "").strip() == "1"
    if disable_verify:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx

    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def build_aiohttp_connector():
    """Create an aiohttp TCPConnector with the configured SSL context."""
    import aiohttp

    return aiohttp.TCPConnector(ssl=build_ssl_context())
