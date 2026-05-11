"""Tests for .github/scripts/format_pr_comment.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "format_pr_comment.py"


@pytest.fixture(scope="module")
def formatter():
    spec = importlib.util.spec_from_file_location("format_pr_comment", SCRIPT)
    assert spec and spec.loader, f"could not load {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["format_pr_comment"] = module
    spec.loader.exec_module(module)
    return module


def _page(
    path,
    score,
    *,
    doc_age_days=10,
    source_age_days=10,
    ttl_days=None,
    missing=None,
    critical=False,
):
    return {
        "path": path,
        "score": score,
        "doc_age_days": doc_age_days,
        "source_age_days": source_age_days,
        "ttl_days": ttl_days,
        "missing_symbols": missing or [],
        "critical": critical,
        "source_count": 1,
    }


class TestReasonFor:
    def test_signature_drift_named_after_new_missing_symbol(self, formatter):
        cur = _page("a.md", 70, missing=["createUser"])
        base = _page("a.md", 90, missing=[])
        assert formatter.reason_for(cur, base) == "signature drift on `createUser`"

    def test_ttl_exceeded(self, formatter):
        cur = _page("a.md", 70, doc_age_days=104, source_age_days=104, ttl_days=90)
        base = _page("a.md", 90, doc_age_days=80, source_age_days=80, ttl_days=90)
        assert formatter.reason_for(cur, base) == "TTL exceeded by 14 days"

    def test_source_files_were_edited(self, formatter):
        cur = _page("a.md", 70, doc_age_days=60, source_age_days=2)
        base = _page("a.md", 90, doc_age_days=60, source_age_days=50)
        assert formatter.reason_for(cur, base) == "referenced source files were edited"

    def test_falls_back_when_no_specific_cause(self, formatter):
        cur = _page("a.md", 70, doc_age_days=10, source_age_days=10)
        base = _page("a.md", 90, doc_age_days=10, source_age_days=10)
        assert formatter.reason_for(cur, base) == "score decreased"


class TestComputeDelta:
    def test_drops_listed_in_order_of_largest_drop_first(self, formatter):
        cur = [
            _page("small.md", 88, missing=["foo"]),
            _page("big.md", 71, missing=["bar"]),
        ]
        base = [_page("small.md", 92), _page("big.md", 92)]
        diff = formatter.compute_diff(cur, base)
        assert [d["path"] for d in diff["drops"]] == ["big.md", "small.md"]

    def test_unchanged_pages_excluded_from_drops(self, formatter):
        cur = [_page("a.md", 100), _page("b.md", 80, missing=["x"])]
        base = [_page("a.md", 100), _page("b.md", 95)]
        diff = formatter.compute_diff(cur, base)
        assert [d["path"] for d in diff["drops"]] == ["b.md"]

    def test_improvements_excluded_from_drops(self, formatter):
        cur = [_page("a.md", 95)]
        base = [_page("a.md", 80)]
        diff = formatter.compute_diff(cur, base)
        assert diff["drops"] == []

    def test_new_page_in_current_not_listed_as_drop(self, formatter):
        cur = [_page("new.md", 70)]
        base: list[dict] = []
        diff = formatter.compute_diff(cur, base)
        assert diff["drops"] == []

    def test_mean_and_median_both_returned(self, formatter):
        cur = [_page("a.md", 60, critical=True), _page("b.md", 100), _page("c.md", 100)]
        base = [_page("a.md", 100, critical=True), _page("b.md", 100), _page("c.md", 100)]
        diff = formatter.compute_diff(cur, base)
        # 1 page at 60 + 2 at 100 -> mean 87, median 100
        assert diff["current_mean"] == 87
        assert diff["current_median"] == 100
        assert diff["delta_mean"] == -13

    def test_critical_breach_reported(self, formatter):
        cur = [
            _page("a.md", 60, critical=True),
            _page("b.md", 100, critical=True),
            _page("c.md", 30),  # not critical, no breach
        ]
        diff = formatter.compute_diff(cur, [])
        assert diff["breaches"] == [{"path": "a.md", "score": 60}]


class TestRender:
    def test_headline_uses_mean(self, formatter):
        # 1 drop from 100 -> 60 across 11 pages: mean goes 100 -> 96
        cur = [_page("a.md", 60, missing=["x"])] + [_page(f"p{i}.md", 100) for i in range(10)]
        base = [_page("a.md", 100)] + [_page(f"p{i}.md", 100) for i in range(10)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "## 📚 Documentation freshness — 100 → 96 (-4)" in out.splitlines()[0]

    def test_headline_positive_delta_shows_plus(self, formatter):
        cur = [_page("a.md", 95)]
        base = [_page("a.md", 80)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "→ 95 (+15)" in out

    def test_headline_zero_delta_shows_plus_zero(self, formatter):
        cur = [_page("a.md", 90)]
        base = [_page("a.md", 90)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "→ 90 (+0)" in out

    def test_drop_table_format(self, formatter):
        cur = [_page("docs/api/users.md", 71, missing=["createUser"])]
        base = [_page("docs/api/users.md", 92)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "| Page | Before → After | Reason |" in out
        assert "|---|---|---|" in out
        assert "`docs/api/users.md`" in out
        assert "92 → 71" in out
        assert "signature drift on `createUser`" in out

    def test_no_drops_shows_check_mark(self, formatter):
        cur = [_page("a.md", 90)]
        base = [_page("a.md", 90)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "✅ No pages dropped." in out

    def test_singular_noun_for_one_drop(self, formatter):
        cur = [_page("a.md", 80, missing=["fooBar"])]
        base = [_page("a.md", 100)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "1 page dropped" in out
        assert "1 pages dropped" not in out

    def test_slo_breach_callout_when_critical_at_floor(self, formatter):
        cur = [_page("docs/api/auth.md", 60, critical=True, missing=["x"])]
        base = [_page("docs/api/auth.md", 100, critical=True)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "🚨 **SLO breach**" in out
        assert "`docs/api/auth.md` (score 60)" in out

    def test_no_breach_section_when_none(self, formatter):
        cur = [_page("a.md", 70)]
        base = [_page("a.md", 100)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "SLO breach" not in out

    def test_critical_drop_uses_red_emoji(self, formatter):
        cur = [_page("a.md", 60, critical=True, missing=["x"])]
        base = [_page("a.md", 100, critical=True)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "🔴" in out

    def test_footer_lists_median_and_page_count(self, formatter):
        cur = [_page("a.md", 60, missing=["x"]), _page("b.md", 100)]
        base = [_page("a.md", 100), _page("b.md", 100)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "2 pages scored" in out
        assert "median" in out


class TestCLI:
    def test_main_reads_files_and_prints_to_stdout(
        self, formatter, tmp_path, capsys
    ):
        cur_path = tmp_path / "current.json"
        base_path = tmp_path / "main.json"
        cur_page = _page("docs/x.md", 80, missing=["fooBar"])
        base_page = _page("docs/x.md", 95)
        cur_path.write_text(json.dumps([cur_page]))
        base_path.write_text(json.dumps([base_page]))

        rc = formatter.main(
            ["--current", str(cur_path), "--baseline", str(base_path)]
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "95 → 80 (-15)" in out
        assert "signature drift on `fooBar`" in out
