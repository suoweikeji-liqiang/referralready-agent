#!/usr/bin/env python3
"""Run the internal competition scorecard for the local repository."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.scorecard import evaluate_submission, render_scorecard_report


def main() -> int:
    report = evaluate_submission(ROOT)
    print(render_scorecard_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
