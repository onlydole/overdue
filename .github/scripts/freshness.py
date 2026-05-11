"""Documentation freshness scoring pipeline.

Computes a per-page freshness score in [0, 100] from three deterministic signals:
git age delta (doc age vs. youngest referenced source age), TTL contract from
frontmatter, and symbol drift (backticked references missing from source files).

Refinements over the post's minimal script:
  - Inline-code candidates are restricted to tokens that contain a period or a
    lowercase->uppercase transition. Filters env vars, SCREAMING_SNAKE_CASE,
    lowercase enum values, and capitalized single words that aren't symbols.
  - Allowlist at .github/freshness-allowlist.txt filters remaining noise via
    fnmatch globs (one pattern per line, '#' comments allowed).
  - Pages with `freshness: { exclude: true }` are dropped from the report.

Known gap: age delta uses absolute timestamps. A long-lived feature branch
accumulates age penalty even when code and docs moved together within the
branch. The fix is computing against `git merge-base origin/main HEAD`, left
as a follow-up.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / os.environ.get("DOCS_DIR", "docs")
ALLOWLIST_FILE = REPO_ROOT / ".github" / "freshness-allowlist.txt"
NOW = datetime.now(UTC)

INLINE_CODE_RE = re.compile(r"`([A-Za-z_][A-Za-z0-9_.]*)`")
CAMEL_TRANSITION_RE = re.compile(r"[a-z][A-Z]")


def last_touched(path: Path) -> datetime:
    """Last commit time, falling back to mtime for new/untracked files."""
    iso = subprocess.check_output(
        ["git", "log", "-1", "--follow", "--format=%cI", "--", str(path)],
        cwd=REPO_ROOT,
        text=True,
    ).strip()
    if iso:
        return datetime.fromisoformat(iso)
    if path.exists():
        return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    return NOW


def days(d: datetime) -> int:
    return max(0, (NOW - d).days)


def _looks_like_symbol(token: str) -> bool:
    return "." in token or bool(CAMEL_TRANSITION_RE.search(token))


def extract_referenced_symbols(raw: str) -> set[str]:
    return {t for t in INLINE_CODE_RE.findall(raw) if _looks_like_symbol(t)}


def load_allowlist(path: Path = ALLOWLIST_FILE) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]


def apply_allowlist(missing: set[str], patterns: list[str]) -> set[str]:
    if not patterns:
        return set(missing)
    return {s for s in missing if not any(fnmatch.fnmatch(s, p) for p in patterns)}


def parse_frontmatter(raw: str) -> dict[str, Any]:
    fm_match = re.match(r"^---\n(.*?)\n---\n", raw, re.DOTALL)
    if not fm_match:
        return {}
    parsed = yaml.safe_load(fm_match.group(1))
    return parsed if isinstance(parsed, dict) else {}


def is_excluded(front: dict[str, Any]) -> bool:
    return bool(front.get("freshness", {}).get("exclude"))


def compute_score(
    *,
    doc_age: int,
    youngest_source_age: int,
    ttl: int | None,
    missing_count: int,
) -> int:
    age_penalty = min(30, max(0, (doc_age - youngest_source_age) // 3))
    ttl_penalty = max(0, (doc_age - ttl) * 2) if ttl else 0
    drift_penalty = min(40, missing_count * 10)
    return max(0, 100 - age_penalty - drift_penalty - ttl_penalty)


def _live_symbols(sources: list[Path]) -> set[str]:
    """Python-only via regex. Swap for tree-sitter or LSP for polyglot repos."""
    symbols: set[str] = set()
    for s in sources:
        if not s.is_file():
            continue
        text = s.read_text()
        symbols.update(re.findall(r"def\s+([A-Za-z_][A-Za-z0-9_]*)", text))
        symbols.update(re.findall(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", text))
    return symbols


def score(doc: Path, allowlist: list[str] | None = None) -> dict[str, Any] | None:
    if allowlist is None:
        allowlist = load_allowlist()
    raw = doc.read_text()
    front = parse_frontmatter(raw)
    if is_excluded(front):
        return None
    freshness = front.get("freshness", {}) if isinstance(front.get("freshness"), dict) else {}

    sources: list[Path] = []
    for pattern in freshness.get("sources", []):
        sources.extend(REPO_ROOT.glob(pattern))

    doc_age = days(last_touched(doc))
    youngest_source_age = min((days(last_touched(s)) for s in sources), default=doc_age)

    referenced = extract_referenced_symbols(raw)
    missing = referenced - _live_symbols(sources)
    missing = apply_allowlist(missing, allowlist)

    ttl = freshness.get("ttl_days")
    return {
        "path": str(doc.relative_to(REPO_ROOT)),
        "score": compute_score(
            doc_age=doc_age,
            youngest_source_age=youngest_source_age,
            ttl=ttl,
            missing_count=len(missing),
        ),
        "doc_age_days": doc_age,
        "source_age_days": youngest_source_age,
        "ttl_days": ttl,
        "critical": bool(front.get("critical", False)),
        "missing_symbols": sorted(missing),
        "source_count": len(sources),
    }


def main() -> int:
    allowlist = load_allowlist()
    report: list[dict[str, Any]] = []
    for p in sorted(DOCS_DIR.rglob("*.md")):
        result = score(p, allowlist)
        if result is not None:
            report.append(result)
    out = REPO_ROOT / "freshness.json"
    out.write_text(json.dumps(report, indent=2))
    print(f"Wrote {len(report)} pages to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
