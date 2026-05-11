"""Render a Shields.io endpoint badge from a freshness.json report.

Output schema: https://shields.io/badges/endpoint-badge
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any


def color_for(median: int) -> str:
    if median >= 85:
        return "green"
    if median >= 65:
        return "yellow"
    return "red"


def build_badge(scores: list[int]) -> dict[str, Any]:
    if not scores:
        return {
            "schemaVersion": 1,
            "label": "Docs Freshness",
            "message": "no docs/100",
            "color": "lightgrey",
        }
    median = int(statistics.median(scores))
    return {
        "schemaVersion": 1,
        "label": "Docs Freshness",
        "message": f"{median}/100",
        "color": color_for(median),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, default=None)
    args = p.parse_args(argv)

    data = json.loads(args.input.read_text())
    scores = [r["score"] for r in data]
    badge = build_badge(scores)
    rendered = json.dumps(badge, indent=2) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        args.output.write_text(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
