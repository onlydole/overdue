"""Tests for the docs freshness scoring pipeline at .github/scripts/freshness.py."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "freshness.py"


@pytest.fixture(scope="module")
def freshness():
    spec = importlib.util.spec_from_file_location("freshness", SCRIPT)
    assert spec and spec.loader, f"could not load {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["freshness"] = module
    spec.loader.exec_module(module)
    return module


class TestCamelCaseFilter:
    def test_includes_camelcase(self, freshness):
        assert freshness.extract_referenced_symbols("see `getUser`") == {"getUser"}

    def test_includes_dotted(self, freshness):
        assert freshness.extract_referenced_symbols("see `users.create`") == {"users.create"}

    def test_excludes_screaming_snake(self, freshness):
        text = "env: `OVERDUE_DEWEY_DECAY_SECONDS` and `ANTHROPIC_API_KEY`"
        assert freshness.extract_referenced_symbols(text) == set()

    def test_excludes_all_lowercase(self, freshness):
        text = "`main`, `bcrypt`, `casual`, `volumes`, `librarians`"
        assert freshness.extract_referenced_symbols(text) == set()

    def test_excludes_capitalized_word_with_no_internal_transition(self, freshness):
        text = "press `Enter` or `Escape`; use `Bash`; header `Authorization`"
        assert freshness.extract_referenced_symbols(text) == set()

    def test_keeps_camelcase_and_dotted_drops_noise(self, freshness):
        text = "use `getUser` and `users.create` not `MAX_RETRY` or `main`"
        assert freshness.extract_referenced_symbols(text) == {"getUser", "users.create"}

    def test_keeps_pascalcase_with_internal_transition(self, freshness):
        # MyClass has yC (lower->upper) so it counts as a candidate
        assert freshness.extract_referenced_symbols("see `MyClass`") == {"MyClass"}


class TestAllowlist:
    def test_empty_patterns_returns_missing_unchanged(self, freshness):
        missing = {"PyJWT", "currentColor", "getUser"}
        assert freshness.apply_allowlist(missing, []) == missing

    def test_exact_match_filters(self, freshness):
        missing = {"PyJWT", "getUser"}
        assert freshness.apply_allowlist(missing, ["PyJWT"]) == {"getUser"}

    def test_glob_pattern_filters_prefix(self, freshness):
        missing = {"currentColor", "currentValue", "getUser"}
        assert freshness.apply_allowlist(missing, ["current*"]) == {"getUser"}

    def test_load_strips_blank_and_comment_lines(self, freshness, tmp_path):
        f = tmp_path / "allow.txt"
        f.write_text("# a comment\n\nPyJWT\ncurrentColor\n# another\n")
        assert freshness.load_allowlist(f) == ["PyJWT", "currentColor"]

    def test_load_missing_file_returns_empty(self, freshness, tmp_path):
        assert freshness.load_allowlist(tmp_path / "missing.txt") == []


class TestFrontmatter:
    def test_parse_returns_block(self, freshness):
        raw = "---\ntitle: Hi\nfreshness:\n  ttl_days: 90\n---\n# body\n"
        assert freshness.parse_frontmatter(raw) == {
            "title": "Hi",
            "freshness": {"ttl_days": 90},
        }

    def test_parse_returns_empty_dict_when_absent(self, freshness):
        assert freshness.parse_frontmatter("# no frontmatter here\n") == {}

    def test_is_excluded_true(self, freshness):
        assert freshness.is_excluded({"freshness": {"exclude": True}}) is True

    def test_is_excluded_false_when_freshness_block_lacks_exclude(self, freshness):
        assert freshness.is_excluded({"freshness": {"ttl_days": 90}}) is False

    def test_is_excluded_false_when_no_freshness_block(self, freshness):
        assert freshness.is_excluded({}) is False


class TestScoreFormula:
    def test_perfect_score_with_no_penalties(self, freshness):
        assert (
            freshness.compute_score(
                doc_age=10, youngest_source_age=10, ttl=None, missing_count=0
            )
            == 100
        )

    def test_drift_only(self, freshness):
        # 3 missing -> 30 penalty -> 70
        assert (
            freshness.compute_score(
                doc_age=10, youngest_source_age=10, ttl=None, missing_count=3
            )
            == 70
        )

    def test_drift_caps_at_40(self, freshness):
        # 7 missing -> cap at 40 -> 60
        assert (
            freshness.compute_score(
                doc_age=10, youngest_source_age=10, ttl=None, missing_count=7
            )
            == 60
        )

    def test_age_penalty_floors_at_zero_when_doc_is_younger(self, freshness):
        # doc fresher than source -> no penalty
        assert (
            freshness.compute_score(
                doc_age=5, youngest_source_age=30, ttl=None, missing_count=0
            )
            == 100
        )

    def test_age_penalty_integer_division_by_three(self, freshness):
        # delta of 30 days -> 10 penalty
        assert (
            freshness.compute_score(
                doc_age=40, youngest_source_age=10, ttl=None, missing_count=0
            )
            == 90
        )

    def test_age_penalty_caps_at_30(self, freshness):
        assert (
            freshness.compute_score(
                doc_age=1000, youngest_source_age=0, ttl=None, missing_count=0
            )
            == 70
        )

    def test_ttl_penalty_zero_when_under_ttl(self, freshness):
        assert (
            freshness.compute_score(
                doc_age=30, youngest_source_age=30, ttl=90, missing_count=0
            )
            == 100
        )

    def test_ttl_penalty_two_per_day_over(self, freshness):
        # 14 days past 90-day TTL -> 28 penalty
        assert (
            freshness.compute_score(
                doc_age=104, youngest_source_age=104, ttl=90, missing_count=0
            )
            == 72
        )

    def test_score_floors_at_zero(self, freshness):
        # massive penalties -> still 0, never negative
        assert (
            freshness.compute_score(
                doc_age=10_000, youngest_source_age=0, ttl=1, missing_count=10
            )
            == 0
        )


class TestDottedSymbols:
    def test_simple_token_present(self, freshness):
        assert freshness.compute_missing({"getUser"}, {"getUser"}) == set()

    def test_simple_token_missing(self, freshness):
        assert freshness.compute_missing({"getUser"}, set()) == {"getUser"}

    def test_dotted_present_when_all_components_live(self, freshness):
        assert freshness.compute_missing(
            {"MyClass.my_method"}, {"MyClass", "my_method"}
        ) == set()

    def test_dotted_missing_when_only_some_components_live(self, freshness):
        assert freshness.compute_missing(
            {"MyClass.my_method"}, {"MyClass"}
        ) == {"MyClass.my_method"}

    def test_three_part_dotted(self, freshness):
        assert freshness.compute_missing(
            {"users.api.create"}, {"users", "api", "create"}
        ) == set()


class TestFrontmatterDefensive:
    def test_invalid_yaml_returns_empty(self, freshness):
        raw = "---\ntitle: [unclosed\n---\n# doc\n"
        assert freshness.parse_frontmatter(raw) == {}

    def test_yaml_scalar_returns_empty(self, freshness):
        raw = "---\njust a string\n---\n# doc\n"
        assert freshness.parse_frontmatter(raw) == {}

    def test_is_excluded_with_null_freshness(self, freshness):
        assert freshness.is_excluded({"freshness": None}) is False

    def test_is_excluded_with_scalar_freshness(self, freshness):
        assert freshness.is_excluded({"freshness": "weird"}) is False

    def test_is_excluded_with_list_freshness(self, freshness):
        assert freshness.is_excluded({"freshness": []}) is False


class TestLastTouchedFallback:
    def test_falls_back_when_git_subprocess_fails(
        self, freshness, tmp_path, monkeypatch
    ):
        import subprocess as sp

        def boom(*a, **kw):
            raise sp.CalledProcessError(128, ["git", "log"])

        monkeypatch.setattr(freshness.subprocess, "check_output", boom)
        p = tmp_path / "x.md"
        p.write_text("hi")
        result = freshness.last_touched(p)
        from datetime import datetime
        assert isinstance(result, datetime)

    def test_falls_back_when_git_not_installed(
        self, freshness, tmp_path, monkeypatch
    ):
        def boom(*a, **kw):
            raise FileNotFoundError("git not on PATH")

        monkeypatch.setattr(freshness.subprocess, "check_output", boom)
        p = tmp_path / "x.md"
        p.write_text("hi")
        result = freshness.last_touched(p)
        from datetime import datetime
        assert isinstance(result, datetime)


class TestScoreIntegration:
    def test_excluded_doc_returns_none(self, freshness, tmp_path, monkeypatch):
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(
            freshness, "last_touched", lambda p: freshness.NOW
        )
        doc = tmp_path / "x.md"
        doc.write_text("---\nfreshness:\n  exclude: true\n---\n# Hi\n")
        assert freshness.score(doc, allowlist=[]) is None

    def test_basic_score_for_doc_with_no_references(
        self, freshness, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(
            freshness, "last_touched", lambda p: freshness.NOW
        )
        doc = tmp_path / "x.md"
        doc.write_text("# A doc with no backticks at all\n")
        result = freshness.score(doc, allowlist=[])
        assert result is not None
        assert result["score"] == 100
        assert result["missing_symbols"] == []

    def test_allowlist_strips_noise_from_missing(
        self, freshness, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(
            freshness, "last_touched", lambda p: freshness.NOW
        )
        doc = tmp_path / "x.md"
        doc.write_text("references `PyJWT` and `getUser`\n")
        result = freshness.score(doc, allowlist=["PyJWT"])
        assert result is not None
        assert result["missing_symbols"] == ["getUser"]
