"""Live smoke checks for production-like fetch paths (opt-in only)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.live_smoke
@pytest.mark.skipif(
    os.getenv("EQUILIS_ENABLE_LIVE_SMOKE") != "1",
    reason="Set EQUILIS_ENABLE_LIVE_SMOKE=1 to run live network smoke checks.",
)
def test_live_reliance_analyze_smoke():
    repo_root = Path(__file__).resolve().parent.parent
    cmd = [
        sys.executable,
        str(repo_root / "core" / "_cli_runner.py"),
        "--command",
        "analyze",
        "--ticker",
        "RELIANCE",
        "--no-cache",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=240, cwd=str(repo_root))
    assert proc.returncode == 0, proc.stderr

    payload = json.loads(proc.stdout.strip())
    assert payload.get("success") is True, payload
    assert "Field Coverage" in payload.get("stdout", "")
