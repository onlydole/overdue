"""Tests for the artifact-only comment renderer in the freshness workflow."""

from __future__ import annotations

import json
import subprocess
import types
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "freshness.yml"


@pytest.fixture(scope="module")
def workflow():
    return yaml.safe_load(WORKFLOW.read_text())


@pytest.fixture(scope="module")
def renderer_command(workflow):
    steps = workflow["jobs"]["pr-comment"]["steps"]
    return next(step["run"] for step in steps if step["name"] == "Build PR comment body")


@pytest.fixture(scope="module")
def renderer_source(renderer_command):
    return renderer_command.split("<<'PY' > /tmp/comment.md\n", 1)[1].split("\nPY", 1)[0]


@pytest.fixture(scope="module")
def formatter(renderer_source):
    module = types.ModuleType("format_pr_comment")
    exec(compile(renderer_source, str(WORKFLOW), "exec"), module.__dict__)
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
        assert formatter.reason_for(cur, base) == "signature drift on createUser"

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

    def test_medians_use_statistics_median(self, formatter):
        cur = [_page("a.md", 80), _page("b.md", 90), _page("c.md", 70)]
        base = [_page("a.md", 90), _page("b.md", 90), _page("c.md", 90)]
        diff = formatter.compute_diff(cur, base)
        assert diff["current_median"] == 80
        assert diff["baseline_median"] == 90
        assert diff["delta"] == -10


class TestRender:
    def test_header_format_with_negative_delta(self, formatter):
        cur = [_page("a.md", 80)]
        base = [_page("a.md", 90)]
        out = formatter.render(formatter.compute_diff(cur, base))
        # baseline -> current, matching the per-page drop lines
        assert out.splitlines()[0] == "Documentation freshness: 90 -> 80 (-10)"

    def test_header_format_with_positive_delta(self, formatter):
        cur = [_page("a.md", 95)]
        base = [_page("a.md", 80)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert out.splitlines()[0] == "Documentation freshness: 80 -> 95 (+15)"

    def test_header_format_with_zero_delta(self, formatter):
        cur = [_page("a.md", 90)]
        base = [_page("a.md", 90)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert out.splitlines()[0] == "Documentation freshness: 90 -> 90 (+0)"

    def test_drop_lines_match_post_format(self, formatter):
        cur = [
            _page(
                "docs/api/users.md",
                71,
                doc_age_days=60,
                source_age_days=60,
                missing=["createUser"],
            ),
            _page(
                "docs/guides/auth.md",
                78,
                doc_age_days=104,
                source_age_days=104,
                ttl_days=90,
            ),
            _page(
                "docs/quickstart.md",
                79,
                doc_age_days=30,
                source_age_days=2,
            ),
        ]
        base = [
            _page(
                "docs/api/users.md",
                92,
                doc_age_days=60,
                source_age_days=60,
                missing=[],
            ),
            _page(
                "docs/guides/auth.md",
                88,
                doc_age_days=80,
                source_age_days=80,
                ttl_days=90,
            ),
            _page(
                "docs/quickstart.md",
                85,
                doc_age_days=30,
                source_age_days=50,
            ),
        ]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "3 pages dropped:" in out
        assert "  docs/api/users.md         92 -> 71  (signature drift on createUser)" in out
        assert "  docs/guides/auth.md       88 -> 78  (TTL exceeded by 14 days)" in out
        assert "  docs/quickstart.md        85 -> 79  (referenced source files were edited)" in out

    def test_no_drops_emits_friendly_line(self, formatter):
        cur = [_page("a.md", 90)]
        base = [_page("a.md", 90)]
        out = formatter.render(formatter.compute_diff(cur, base))
        assert "No pages dropped" in out


class TestCLI:
    def test_main_reads_files_and_prints_to_stdout(self, formatter, tmp_path, capsys):
        cur_path = tmp_path / "current.json"
        base_path = tmp_path / "main.json"
        cur_page = _page("docs/x.md", 80, missing=["fooBar"])
        base_page = _page("docs/x.md", 95)
        cur_path.write_text(json.dumps([cur_page]))
        base_path.write_text(json.dumps([base_page]))

        rc = formatter.main(["--current", str(cur_path), "--baseline", str(base_path)])
        out = capsys.readouterr().out
        assert rc == 0
        assert "Documentation freshness: 95 -> 80 (-15)" in out
        assert "(signature drift on fooBar)" in out

    def test_workflow_shell_command(self, renderer_command, tmp_path):
        cur_path = tmp_path / "current.json"
        base_path = tmp_path / "main.json"
        cur_path.write_text(json.dumps([_page("docs/x.md", 80, missing=["fooBar"])]))
        base_path.write_text(json.dumps([_page("docs/x.md", 95)]))
        command = (
            renderer_command.replace("/tmp/freshness-current/freshness.current.json", str(cur_path))
            .replace("/tmp/freshness-baseline/freshness.main.json", str(base_path))
            .replace("/tmp/comment.md", str(tmp_path / "comment.md"))
        )
        result = subprocess.run(
            ["bash", "-c", command],
            text=True,
            capture_output=True,
            check=True,
        )
        assert "Documentation freshness: 95 -> 80 (-15)" in result.stdout
        assert "signature drift on fooBar" in result.stdout


class TestLoadReport:
    @pytest.mark.parametrize(
        "page",
        [
            None,
            [],
            {},
            _page("docs/../x.md", 80),
            _page("docs/x.md\n@someone", 80),
            _page("docs/[x].md", 80),
            _page("src/x.md", 80),
            _page("docs/x.md", True),
            _page("docs/x.md", "80"),
            _page("docs/x.md", -1),
            _page("docs/x.md", 101),
        ],
    )
    def test_invalid_records_are_skipped(self, formatter, tmp_path, page):
        report = tmp_path / "report.json"
        report.write_text(json.dumps([page, _page("docs/safe.md", 80)]))
        assert [r["path"] for r in formatter.load_report(report)] == ["docs/safe.md"]

    def test_filters_untrusted_symbols(self, formatter, tmp_path):
        report = tmp_path / "report.json"
        report.write_text(
            json.dumps(
                [
                    _page(
                        "docs/x.md",
                        80,
                        missing=["fooBar", "Thing.method", "@someone", "<script>", {}, 42],
                    )
                ]
            )
        )
        assert formatter.load_report(report)[0]["missing_symbols"] == ["fooBar", "Thing.method"]

    @pytest.mark.parametrize("missing", [None, "fooBar", {"fooBar": True}])
    def test_non_list_symbols_are_ignored(self, formatter, tmp_path, missing):
        report = tmp_path / "report.json"
        report.write_text(json.dumps([_page("docs/x.md", 80, missing=missing)]))
        assert formatter.load_report(report)[0]["missing_symbols"] == []

    def test_non_list_report_is_ignored(self, formatter, tmp_path):
        report = tmp_path / "report.json"
        report.write_text("{}")
        assert formatter.load_report(report) == []

    def test_malformed_metadata_does_not_crash_or_reach_comment(self, formatter, tmp_path, capsys):
        cur_path = tmp_path / "current.json"
        base_path = tmp_path / "main.json"
        cur_path.write_text(
            json.dumps(
                [
                    _page(
                        "docs/x.md",
                        80,
                        ttl_days="@someone",
                        doc_age_days={},
                        source_age_days=[],
                        missing=[{"bad": "symbol"}, "@someone"],
                    )
                ]
            )
        )
        base_path.write_text(json.dumps([_page("docs/x.md", 95)]))
        assert formatter.main(["--current", str(cur_path), "--baseline", str(base_path)]) == 0
        out = capsys.readouterr().out
        assert "(score decreased)" in out
        assert "@someone" not in out


def test_workflow_preserves_privilege_isolation(workflow):
    assert workflow["permissions"] == {}
    freshness = workflow["jobs"]["freshness"]
    assert freshness["permissions"] == {"contents": "read"}
    semantic = next(step for step in freshness["steps"] if step["name"] == "Claude semantic check")
    assert "github.event_name != 'pull_request'" in semantic["if"]
    comment = workflow["jobs"]["pr-comment"]
    assert comment["permissions"] == {"pull-requests": "write"}
    assert comment["needs"] == "freshness"
    assert "github.event_name == 'pull_request'" in comment["if"]
    assert all("actions/checkout@" not in step.get("uses", "") for step in comment["steps"])
    assert [step["name"] for step in comment["steps"] if "run" in step] == ["Build PR comment body"]
