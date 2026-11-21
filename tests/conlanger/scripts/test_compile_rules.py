"""Tests for ``compile_rules`` CLI."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from conlanger.scripts import compile_rules as compile_script
from conlanger.scripts.config_loaders import compiler_config_for_compile


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


def test_compile_rules_cli_passes_seed_override_to_config_builder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    captured: dict[str, object] = {}

    def _capture_config(path=None, **kwargs: object):
        captured["path"] = path
        captured.update(kwargs)
        from conlanger.scripts.config_loaders import compiler_config_for_compile

        return compiler_config_for_compile(path, **kwargs)

    monkeypatch.setattr(compile_script, "compiler_config_for_compile", _capture_config)
    yaml_in = tmp_path / "index.yml"
    yaml_in.write_text(
        """
sections:
- index: "1.0"
  section: Test
  rules:
  - rule_id: r0
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
                "--seed",
                "7",
                "--sample-sporadic",
            ],
        ),
    ):
        assert compile_script.main() == 0
    assert captured["seed"] == 7
    assert captured["sample_sporadic"] is True


def test_compile_rules_smoke_writes_v4_yaml(tmp_path: Path):
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
    assert loaded["schema_version"] == 4
    rule = loaded["sections"][0]["rules"][0]
    assert rule["rule_id"] == "r0"
    assert rule["rule"] == "a > b"
    assert rule["input"] == "a"
    assert rule["output"] == "b"


def test_compiler_config_for_compile_cli_seed_overrides_defaults():
    config = compiler_config_for_compile(seed=42)
    assert config.seed == 42
    assert config.sample_sporadic is True


def test_compiler_config_for_compile_cli_boolean_overrides_defaults():
    config = compiler_config_for_compile(sample_sporadic=False)
    assert config.sample_sporadic is False
    assert config.sample_dialect is True


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
