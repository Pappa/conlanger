"""Tests for ``compile_rules`` CLI."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import yaml

from conlanger.scripts import compile_rules as compile_script


def test_compile_rules_errors_when_yaml_missing(tmp_path: Path):
    with patch.object(
        sys,
        "argv",
        [
            "compile_rules",
            "--yaml-in",
            str(tmp_path / "missing.yml"),
        ],
    ):
        assert compile_script.main() == 1


def test_compile_rules_smoke_writes_v3_yaml(tmp_path: Path):
    yaml_in = tmp_path / "index.yml"
    yaml_in.write_text(
        """
sections:
- index: "1.0"
  section: Test
  rules:
  - rule_id: r0
    source: test:1
    stages: [a, b]
""".strip(),
        encoding="utf-8",
    )
    compiled_out = tmp_path / "asca_rules.yml"

    with (
        patch.object(compile_script, "ROOT", tmp_path),
        patch.object(
            sys,
            "argv",
            [
                "compile_rules",
                "--yaml-in",
                str(yaml_in),
                "--compiled-out",
                str(compiled_out),
            ],
        ),
    ):
        assert compile_script.main() == 0

    loaded = yaml.safe_load(compiled_out.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == 3
    rule = loaded["sections"][0]["rules"][0]
    assert rule["rule_id"] == "r0"
    assert rule["rule"] == "a > b"


def test_compile_rules_limit(tmp_path: Path):
    yaml_in = tmp_path / "index.yml"
    yaml_in.write_text(
        """
sections:
- index: "1.0"
  section: Test
  rules:
  - rule_id: r0
    stages: [a, b]
  - rule_id: r1
    stages: [c, d]
""".strip(),
        encoding="utf-8",
    )
    compiled_out = tmp_path / "asca_rules.yml"

    with (
        patch.object(compile_script, "ROOT", tmp_path),
        patch.object(
            sys,
            "argv",
            [
                "compile_rules",
                "--yaml-in",
                str(yaml_in),
                "--compiled-out",
                str(compiled_out),
                "--limit",
                "1",
            ],
        ),
    ):
        assert compile_script.main() == 0

    loaded = yaml.safe_load(compiled_out.read_text(encoding="utf-8"))
    assert len(loaded["sections"][0]["rules"]) == 1
