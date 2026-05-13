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


class TestDiscovery:
    def test_walks_docs_dir(self, freshness, tmp_path, monkeypatch):
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "DOCS_DIR", tmp_path / "docs")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "a.md").write_text("# a")
        (tmp_path / "docs" / "sub").mkdir()
        (tmp_path / "docs" / "sub" / "b.md").write_text("# b")
        found = freshness.discover_docs()
        assert {p.name for p in found} == {"a.md", "b.md"}

    def test_picks_up_root_md_with_freshness_frontmatter(
        self, freshness, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "DOCS_DIR", tmp_path / "docs")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "page.md").write_text("# page")
        (tmp_path / "CLAUDE.md").write_text(
            "---\nfreshness:\n  ttl_days: 365\n  sources:\n    - 'src/main.py'\n---\n# guide\n"
        )
        found = freshness.discover_docs()
        assert {p.name for p in found} == {"page.md", "CLAUDE.md"}

    def test_skips_root_md_without_freshness_frontmatter(
        self, freshness, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "DOCS_DIR", tmp_path / "docs")
        (tmp_path / "docs").mkdir()
        (tmp_path / "README.md").write_text("# Overdue\n\nA readme without frontmatter.\n")
        (tmp_path / "CONTRIBUTING.md").write_text(
            "---\ntitle: Contributing\n---\n# Contributing\n"
        )
        found = freshness.discover_docs()
        # neither root file opts in (no freshness: block)
        assert found == []

    def test_no_duplicates_when_doc_lives_under_docs_root(
        self, freshness, tmp_path, monkeypatch
    ):
        # If DOCS_DIR happens to equal REPO_ROOT, a root file with frontmatter
        # should not be returned twice.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "DOCS_DIR", tmp_path)
        (tmp_path / "CLAUDE.md").write_text(
            "---\nfreshness:\n  ttl_days: 90\n---\n"
        )
        found = freshness.discover_docs()
        assert len(found) == 1


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


class TestLiveSymbolsPython:
    def test_extracts_def_and_class(self, freshness):
        text = "def alpha():\n    pass\n\nclass Beta:\n    pass\n"
        assert freshness._live_symbols_python(text) == {"alpha", "Beta"}

    def test_no_matches_returns_empty(self, freshness):
        assert freshness._live_symbols_python("# comment\n") == set()


class TestLiveSymbolsTypeScript:
    def test_extracts_function_class_interface_type_method(self, freshness):
        ts_source = """
        export function getUser(id: string): User {
            return null as any;
        }

        export class SessionStore {
            save(token: string): void {}
            invalidate(): void {}
        }

        export interface User {
            id: string;
            name: string;
        }

        export type AuthMode = "oauth" | "saml";
        """
        result = freshness._live_symbols_typescript(ts_source)
        assert {"getUser", "SessionStore", "save", "invalidate", "User", "AuthMode"} <= result

    def test_imports_only_returns_empty(self, freshness):
        ts = "import { foo } from './bar';\nimport * as baz from 'qux';\n"
        assert freshness._live_symbols_typescript(ts) == set()

    def test_extracts_arrow_function_const_and_enum_and_method_signature(
        self, freshness
    ):
        # Modern TS API shapes the docs are likely to reference: arrow
        # functions assigned to `const`, `enum` declarations, and the
        # method signatures inside interfaces.
        ts_source = """
        export const getUserId = (id: string): number => 42;
        export let computeChecksum = (data: Uint8Array): string => "";
        var legacyCounter = 0;
        export enum AuthScope {
            Read,
            Write,
        }
        export interface Repo {
            save(item: unknown): Promise<void>;
            close(): void;
        }
        """
        result = freshness._live_symbols_typescript(ts_source)
        assert {"getUserId", "computeChecksum", "legacyCounter", "AuthScope",
                "save", "close"} <= result

    def test_empty_or_comment_only_returns_empty(self, freshness):
        assert freshness._live_symbols_typescript("") == set()
        assert freshness._live_symbols_typescript("// just a comment\n") == set()


class TestLiveSymbolsDispatch:
    def test_dispatches_python_and_typescript(self, freshness, tmp_path):
        py = tmp_path / "a.py"
        py.write_text("def alpha():\n    pass\n\nclass Beta:\n    pass\n")
        ts = tmp_path / "b.ts"
        ts.write_text("export function gamma() {}\nexport class Delta {}\n")
        assert freshness._live_symbols([py, ts]) == {"alpha", "Beta", "gamma", "Delta"}

    def test_dispatches_mts_and_cts_as_typescript(self, freshness, tmp_path):
        mts = tmp_path / "a.mts"
        mts.write_text("export function fromMts() {}\n")
        cts = tmp_path / "b.cts"
        cts.write_text("export class FromCts {}\n")
        assert freshness._live_symbols([mts, cts]) == {"fromMts", "FromCts"}

    def test_skips_unknown_extensions(self, freshness, tmp_path):
        go = tmp_path / "a.go"
        go.write_text("func MyFunction() {}\n")
        rs = tmp_path / "b.rs"
        rs.write_text("fn another() {}\n")
        # Until per-language extractors are wired up, unknown suffixes
        # contribute nothing rather than crashing or guessing.
        assert freshness._live_symbols([go, rs]) == set()

    def test_skips_directories(self, freshness, tmp_path):
        # Glob resolution can include directories; the dispatcher should
        # silently skip them rather than crash on `read_text()`.
        d = tmp_path / "subdir"
        d.mkdir()
        assert freshness._live_symbols([d]) == set()


class TestScoreIntegrationTypeScript:
    def test_score_runs_drift_against_typescript_source(
        self, freshness, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "api.ts").write_text(
            "export function getUser(id: string): User { return null as any; }\n"
            "export interface User { id: string; }\n"
        )
        doc = tmp_path / "x.md"
        doc.write_text(
            "---\nfreshness:\n  sources:\n    - 'src/api.ts'\n---\n"
            "Uses `getUser` and `missingFn`.\n"
        )
        result = freshness.score(doc, allowlist=[])
        assert result is not None
        assert result["source_count"] == 1
        assert result["score"] == 90  # one missing -> 10 drift penalty
        assert "missingFn" in result["missing_symbols"]
        assert "getUser" not in result["missing_symbols"]


class TestBootstrap:
    def test_bootstrapped_field_defaults_false(
        self, freshness, tmp_path, monkeypatch
    ):
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        doc = tmp_path / "x.md"
        doc.write_text("# Hi\n")
        result = freshness.score(doc, allowlist=[])
        assert result is not None
        assert result["bootstrapped"] is False

    def test_bootstrap_skips_drift_when_page_has_no_sources(
        self, freshness, tmp_path, monkeypatch
    ):
        # A page with several backticked candidates but no `freshness.sources`
        # block: without bootstrap the drift penalty caps the score at 60,
        # with bootstrap drift is skipped entirely and the score is 100.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        doc = tmp_path / "x.md"
        doc.write_text(
            "References `getUser`, `MyClass`, `users.create`, `apiClient` here.\n"
        )

        without = freshness.score(doc, allowlist=[], bootstrap=False)
        assert without is not None
        assert without["bootstrapped"] is False
        assert without["score"] == 60
        assert len(without["missing_symbols"]) == 4

        with_bootstrap = freshness.score(doc, allowlist=[], bootstrap=True)
        assert with_bootstrap is not None
        assert with_bootstrap["bootstrapped"] is True
        assert with_bootstrap["score"] == 100
        assert with_bootstrap["missing_symbols"] == []

    def test_bootstrap_still_applies_drift_when_sources_declared(
        self, freshness, tmp_path, monkeypatch
    ):
        # A page that opted in via `freshness.sources` is no longer in
        # bootstrap territory: drift detection runs against the declared
        # sources, and a missing symbol counts.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "api.py").write_text("def realFn():\n    pass\n")
        doc = tmp_path / "x.md"
        doc.write_text(
            "---\nfreshness:\n  sources:\n    - 'src/api.py'\n---\n"
            "References `realFn` and `missingFn`.\n"
        )
        result = freshness.score(doc, allowlist=[], bootstrap=True)
        assert result is not None
        assert result["bootstrapped"] is False
        assert "missingFn" in result["missing_symbols"]
        assert "realFn" not in result["missing_symbols"]
        assert result["score"] == 90  # one missing symbol = -10

    def test_bootstrap_still_applies_ttl_for_unmapped_page(
        self, freshness, tmp_path, monkeypatch
    ):
        # Even in bootstrap mode, a `ttl_days` contract still bites. The
        # author opted into a soft deadline by declaring it; we honour that.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)

        from datetime import timedelta

        old = freshness.NOW - timedelta(days=120)
        monkeypatch.setattr(freshness, "last_touched", lambda p: old)
        doc = tmp_path / "x.md"
        doc.write_text(
            "---\nfreshness:\n  ttl_days: 90\n---\n"
            "References `getUser` here.\n"
        )
        result = freshness.score(doc, allowlist=[], bootstrap=True)
        assert result is not None
        assert result["bootstrapped"] is True
        # 120 days, 30 past TTL of 90 => ttl_penalty = 60 => score 40
        assert result["ttl_days"] == 90
        assert result["score"] == 40

    def test_main_argparse_accepts_flag(self, freshness, tmp_path, monkeypatch):
        # End-to-end through main(): page with no sources gets a 100 under
        # --bootstrap and a sub-100 under default settings.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "DOCS_DIR", tmp_path / "docs")
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "x.md").write_text(
            "References `getUser`, `MyClass`, `users.create`, `apiClient`.\n"
        )

        import json as _json

        rc = freshness.main([])
        assert rc == 0
        baseline = _json.loads((tmp_path / "freshness.json").read_text())
        assert baseline[0]["score"] == 60
        assert baseline[0]["bootstrapped"] is False

        rc = freshness.main(["--bootstrap"])
        assert rc == 0
        bootstrapped = _json.loads((tmp_path / "freshness.json").read_text())
        assert bootstrapped[0]["score"] == 100
        assert bootstrapped[0]["bootstrapped"] is True

    def test_score_accepts_sources_as_single_string(
        self, freshness, tmp_path, monkeypatch
    ):
        # YAML allows scalars where a list is expected: `sources: 'src/api.py'`
        # rather than `sources: ['src/api.py']`. Normalize to [str] so the
        # glob loop doesn't iterate over individual characters of the string.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "api.py").write_text("def realFn():\n    pass\n")
        doc = tmp_path / "x.md"
        doc.write_text(
            "---\nfreshness:\n  sources: 'src/api.py'\n---\n"
            "Uses `realFn` and `missingFn`.\n"
        )
        result = freshness.score(doc, allowlist=[])
        assert result is not None
        assert result["source_count"] == 1
        assert "missingFn" in result["missing_symbols"]
        assert "realFn" not in result["missing_symbols"]

    def test_score_skips_live_symbols_when_no_inline_references(
        self, freshness, tmp_path, monkeypatch
    ):
        # Perf: when a doc has no backticked candidate symbols, the script
        # shouldn't read or parse the referenced source files at all.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)

        calls: list[list] = []

        def spy(sources):
            calls.append(sources)
            return set()

        monkeypatch.setattr(freshness, "_live_symbols", spy)
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "api.py").write_text("def realFn(): pass\n")
        doc = tmp_path / "x.md"
        doc.write_text(
            "---\nfreshness:\n  sources: ['src/api.py']\n---\n"
            "A doc with no backticks at all.\n"
        )
        result = freshness.score(doc, allowlist=[])
        assert result is not None
        assert result["score"] == 100
        assert result["missing_symbols"] == []
        assert calls == []  # _live_symbols was never invoked

    def test_bootstrap_does_not_mask_stale_sources_declaration(
        self, freshness, tmp_path, monkeypatch
    ):
        # A page declares `sources: ['src/missing.py']` but the file has
        # since been renamed or deleted. This is a broken config, NOT a
        # day-one page. Bootstrap must not mask it: drift signal should
        # still fire so the author notices their stale path.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        doc = tmp_path / "x.md"
        doc.write_text(
            "---\nfreshness:\n  sources:\n    - 'src/missing.py'\n---\n"
            "References `getUser` and `MyClass`.\n"
        )
        result = freshness.score(doc, allowlist=[], bootstrap=True)
        assert result is not None
        assert result["bootstrapped"] is False
        assert result["source_count"] == 0
        assert result["score"] == 80  # 2 missing symbols -> 20 drift penalty

    def test_bootstrap_skips_drift_when_sources_is_explicit_empty_list(
        self, freshness, tmp_path, monkeypatch
    ):
        # Explicit `sources: []` is treated as "I have no sources to declare
        # yet" — same bootstrap treatment as omitting the key entirely.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        doc = tmp_path / "x.md"
        doc.write_text(
            "---\nfreshness:\n  sources: []\n---\n"
            "References `getUser`, `MyClass`, `apiClient`, `users.create`.\n"
        )
        result = freshness.score(doc, allowlist=[], bootstrap=True)
        assert result is not None
        assert result["bootstrapped"] is True
        assert result["score"] == 100
        assert result["missing_symbols"] == []

    def test_bootstrap_skips_drift_when_freshness_has_only_ttl(
        self, freshness, tmp_path, monkeypatch
    ):
        # A `freshness:` block with `ttl_days` but no `sources` key is
        # still a "no sources declared" page and should be bootstrapped.
        # TTL still applies separately.
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        doc = tmp_path / "x.md"
        doc.write_text(
            "---\nfreshness:\n  ttl_days: 365\n---\n"
            "References `getUser` and `MyClass`.\n"
        )
        result = freshness.score(doc, allowlist=[], bootstrap=True)
        assert result is not None
        assert result["bootstrapped"] is True
        assert result["score"] == 100  # doc_age=0, no drift, no TTL breach

    def test_main_reads_env_var(self, freshness, tmp_path, monkeypatch):
        monkeypatch.setattr(freshness, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(freshness, "DOCS_DIR", tmp_path / "docs")
        monkeypatch.setattr(freshness, "last_touched", lambda p: freshness.NOW)
        monkeypatch.setenv("FRESHNESS_BOOTSTRAP", "1")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "x.md").write_text(
            "References `getUser`, `MyClass`, `users.create`, `apiClient`.\n"
        )

        import json as _json

        rc = freshness.main([])
        assert rc == 0
        report = _json.loads((tmp_path / "freshness.json").read_text())
        assert report[0]["score"] == 100
        assert report[0]["bootstrapped"] is True
