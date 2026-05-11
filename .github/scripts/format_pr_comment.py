"""Render the per-page freshness delta as a sticky PR comment.

Reads two freshness.json reports (the current PR ref and the base ref baseline),
emits the markdown the freshness workflow posts as a sticky comment.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any


def reason_for(current: dict[str, Any], baseline: dict[str, Any]) -> str:
    cur_missing = set(current.get("missing_symbols", []))
    base_missing = set(baseline.get("missing_symbols", []))
    new_missing = sorted(cur_missing - base_missing)
    if new_missing:
        return f"signature drift on {new_missing[0]}"

    ttl = current.get("ttl_days")
    age = current.get("doc_age_days", 0)
    if ttl and age > ttl:
        return f"TTL exceeded by {age - ttl} days"

    cur_src = current.get("source_age_days", 0)
    base_src = baseline.get("source_age_days", 0)
    if cur_src < base_src:
        return "referenced source files were edited"

    return "score decreased"


def _median(scores: list[int]) -> int:
    return int(statistics.median(scores)) if scores else 100


def compute_diff(
    current: list[dict[str, Any]], baseline: list[dict[str, Any]]
) -> dict[str, Any]:
    by_path = {r["path"]: r for r in baseline}
    drops: list[dict[str, Any]] = []
    for cur in current:
        base = by_path.get(cur["path"])
        if base is None:
            continue
        if cur["score"] >= base["score"]:
            continue
        drops.append(
            {
                "path": cur["path"],
                "before": base["score"],
                "after": cur["score"],
                "reason": reason_for(cur, base),
                "delta": cur["score"] - base["score"],
            }
        )
    drops.sort(key=lambda d: (d["delta"], d["path"]))

    current_median = _median([r["score"] for r in current])
    baseline_median = _median([r["score"] for r in baseline])
    return {
        "current_median": current_median,
        "baseline_median": baseline_median,
        "delta": current_median - baseline_median,
        "drops": drops,
    }


def render(diff: dict[str, Any]) -> str:
    delta = diff["delta"]
    sign = "+" if delta >= 0 else ""
    lines = [
        f"Documentation freshness: {diff['current_median']} -> "
        f"{diff['baseline_median']} ({sign}{delta})",
        "",
    ]
    drops = diff["drops"]
    if not drops:
        lines.append("No pages dropped.")
        return "\n".join(lines) + "\n"

    lines.append(f"{len(drops)} pages dropped:")
    max_path = max(len(d["path"]) for d in drops)
    path_col = max_path + 7
    for d in drops:
        lines.append(
            f"  {d['path']:<{path_col}}{d['before']} -> {d['after']}  ({d['reason']})"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--current", type=Path, required=True)
    p.add_argument("--baseline", type=Path, required=True)
    args = p.parse_args(argv)

    current = json.loads(args.current.read_text())
    baseline = json.loads(args.baseline.read_text()) if args.baseline.exists() else []
    sys.stdout.write(render(compute_diff(current, baseline)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
