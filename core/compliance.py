"""
Compliance helpers shared by markdown, PDF, and CLI report paths.

The canonical disclaimer text lives in the equity-research skill reference file.
This module renders its placeholders at the last possible point so every output
uses the same compliance language.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional


DISCLAIMER_PATH = (
    Path(__file__).parent.parent
    / "skills"
    / "equity-research"
    / "references"
    / "compliance-disclaimer.md"
)


def render_disclaimer(
    *,
    ticker: str = "N/A",
    data_date: Optional[datetime] = None,
    prepared_at: Optional[datetime] = None,
) -> str:
    """Return the standard disclaimer with report-specific placeholders filled."""
    prepared = prepared_at or datetime.now()
    data_as_of = data_date or prepared

    text = DISCLAIMER_PATH.read_text(encoding="utf-8")
    marker = "---"
    start = text.find(marker)
    if start != -1:
        text = text[start:]

    return (
        text.replace("[Equilis India Research / individual researcher name]", "Equilis India Research")
        .replace("<DATE>", prepared.strftime("%Y-%m-%d %H:%M IST"))
        .replace("<TICKER>", ticker.upper() if ticker else "N/A")
        .replace("<DATA_DATE>", data_as_of.strftime("%Y-%m-%d %H:%M IST"))
    )
