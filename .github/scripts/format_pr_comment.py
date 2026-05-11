"""Render the per-page freshness delta as a sticky PR comment.

Reads two freshness.json reports (the current PR ref and the base ref baseline),
emits the markdown the freshness workflow posts as a sticky comment.

The headline uses **mean** (not median) because a single failing page in
an otherwise-clean set must move the number -- median is robust to outliers,
which makes for a misleading PR signal. Median is shown alongside as a trend.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path
from typing import Any

CRITICAL_FLOOR = 60


def reason_for(current: dict[str, Any], baseline: dict[str, Any]) -> str:
    cur_missing = set(current.get("missing_symbols", []))
    base_missing = set(baseline.get("missing_symbols", []))
    new_missing = sorted(cur_missing - base_missing)
    if new_missing:
        return f"signature drift on `{new_missing[0]}`"

    ttl = current.get("ttl_days")
    age = current.get("doc_age_days", 0)
    if ttl and age > ttl:
        return f"TTL exceeded by {age - ttl} days"

    cur_src = current.get("source_age_days", 0)
    base_src = baseline.get("source_age_days", 0)
    if cur_src < base_src:
        return "referenced source files were edited"

    return "score decreased"


def _mean(scores: list[int]) -> int:
    return round(statistics.mean(scores)) if scores else 100


def _median(scores: list[int]) -> int:
    return int(statistics.median(scores)) if scores else 100


def _emoji(score: int, critical: bool) -> str:
    if critical and score <= CRITICAL_FLOOR:
        return "🔴"
    if score < 65:
        return "🟠"
    if score < 85:
        return "🟡"
    return "🟢"


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
                "critical": bool(cur.get("critical", False)),
                "delta": cur["score"] - base["score"],
            }
        )
    drops.sort(key=lambda d: (d["delta"], d["path"]))

    breaches = [
        {"path": r["path"], "score": r["score"]}
        for r in current
        if r.get("critical") and r["score"] <= CRITICAL_FLOOR
    ]

    cur_scores = [r["score"] for r in current]
    base_scores = [r["score"] for r in baseline]
    current_mean = _mean(cur_scores)
    baseline_mean = _mean(base_scores)
    return {
        "current_mean": current_mean,
        "baseline_mean": baseline_mean,
        "delta_mean": current_mean - baseline_mean,
        "current_median": _median(cur_scores),
        "baseline_median": _median(base_scores),
        "drops": drops,
        "breaches": breaches,
        "page_count": len(current),
    }


def _signed(n: int) -> str:
    return f"+{n}" if n >= 0 else str(n)


def render(diff: dict[str, Any]) -> str:
    delta = diff["delta_mean"]
    lines = [
        f"## 📚 Documentation freshness — {diff['baseline_mean']} → "
        f"{diff['current_mean']} ({_signed(delta)})",
        "",
    ]

    if diff["breaches"]:
        plural = "s" if len(diff["breaches"]) != 1 else ""
        lines.append(
            f"🚨 **SLO breach** — {len(diff['breaches'])} "
            f"critical page{plural} at or below the floor of {CRITICAL_FLOOR}:"
        )
        for b in diff["breaches"]:
            lines.append(f"- `{b['path']}` (score {b['score']})")
        lines.append("")

    drops = diff["drops"]
    if drops:
        noun = "page" if len(drops) == 1 else "pages"
        lines.append(f"### ⚠️ {len(drops)} {noun} dropped")
        lines.append("")
        lines.append("| Page | Before → After | Reason |")
        lines.append("|---|---|---|")
        for d in drops:
            badge = _emoji(d["after"], d["critical"])
            lines.append(
                f"| {badge} `{d['path']}` | {d['before']} → {d['after']} | {d['reason']} |"
            )
        lines.append("")
    else:
        lines.append("✅ No pages dropped.")
        lines.append("")

    median_delta = diff["current_median"] - diff["baseline_median"]
    lines.append(
        f"<sub>{diff['page_count']} pages scored • "
        f"median {diff['baseline_median']} → {diff['current_median']} "
        f"({_signed(median_delta)})</sub>"
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
