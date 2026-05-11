"""Tests for .github/scripts/build_badge.py."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "build_badge.py"


@pytest.fixture(scope="module")
def build_badge():
    spec = importlib.util.spec_from_file_location("build_badge", SCRIPT)
    assert spec and spec.loader, f"could not load {SCRIPT}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_badge"] = module
    spec.loader.exec_module(module)
    return module


class TestColorThresholds:
    @pytest.mark.parametrize("median", [85, 86, 90, 100])
    def test_green_at_85_and_above(self, build_badge, median):
        assert build_badge.color_for(median) == "green"

    @pytest.mark.parametrize("median", [65, 66, 75, 84])
    def test_yellow_between_65_and_84(self, build_badge, median):
        assert build_badge.color_for(median) == "yellow"

    @pytest.mark.parametrize("median", [0, 30, 64])
    def test_red_below_65(self, build_badge, median):
        assert build_badge.color_for(median) == "red"


class TestBadgeShape:
    def test_required_fields_present(self, build_badge):
        badge = build_badge.build_badge([90, 95, 100])
        assert badge["schemaVersion"] == 1
        assert badge["label"] == "Docs Freshness"
        assert badge["message"] == "95/100"
        assert badge["color"] == "green"

    def test_empty_input_emits_neutral_badge(self, build_badge):
        badge = build_badge.build_badge([])
        assert badge["message"] == "no docs/100"
        assert badge["color"] == "lightgrey"

    def test_message_uses_integer_median(self, build_badge):
        badge = build_badge.build_badge([80, 90])
        assert badge["message"] == "85/100"


class TestCLI:
    def test_writes_json_to_stdout(self, build_badge, tmp_path, capsys):
        report = tmp_path / "freshness.json"
        report.write_text(
            json.dumps([{"path": "a.md", "score": 90}, {"path": "b.md", "score": 100}])
        )
        rc = build_badge.main(["--input", str(report)])
        out = capsys.readouterr().out
        assert rc == 0
        parsed = json.loads(out)
        assert parsed["schemaVersion"] == 1
        assert parsed["message"] == "95/100"
        assert parsed["color"] == "green"

    def test_writes_to_file_when_output_given(
        self, build_badge, tmp_path, capsys
    ):
        report = tmp_path / "freshness.json"
        out_path = tmp_path / "badge.json"
        report.write_text(json.dumps([{"path": "a.md", "score": 70}]))
        rc = build_badge.main(
            ["--input", str(report), "--output", str(out_path)]
        )
        assert rc == 0
        assert capsys.readouterr().out == ""
        parsed = json.loads(out_path.read_text())
        assert parsed["color"] == "yellow"
