"""
core/models/peer.py
PeerComparisonResult — output of the peer comparison pipeline.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class PeerComparisonResult:
    tickers: List[str]
    snapshots: Dict[str, Any]                        # ticker → CompanySnapshot
    comparison_table: Dict[str, Dict]                # metric → {ticker: value}
    sector_medians: Dict[str, Optional[float]]       # metric → median value
    errors: Dict[str, str]                           # ticker → error message
    sources: Dict[str, str]                          # ticker → source name
