"""Tests for ``validate_rules`` CLI."""

from __future__ import annotations

import csv
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from conlanger.scripts import validate_rules as validate
from conlanger.scripts import validation_cli
from conlanger.tools.index_inventory import (
    CHANGELOG_CSV_COLUMNS,
    OK_TRUE,
    FieldIsolationRow,
    IndexRuleInventoryBundle,
    ValidationRow,
    validation_rows_to_dataframe,
)
from conlanger.tools.inventory_targets import InventoryTarget


def _bundle(
    section: dict,
    rule: dict,
    rule_id: str,
    rows: list[ValidationRow],
) -> IndexRuleInventoryBundle:
    return IndexRuleInventoryBundle(
        section=section,
        rule=rule,
        rule_id=rule_id,
        rows=rows,
        targets=[InventoryTarget()],
    )


def _write_fake_fork(root: Path) -> Path:
    fork = root / "lib" / "bin" / "asca"
    fork.parent.mkdir(parents=True, exist_ok=True)
    fork.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fork.chmod(0o755)
    return fork


def _write_min_compiled_yaml(path: Path) -> None:
    path.write_text(
        "schema_version: 3\nsections: []\n",
        encoding="utf-8",
    )


def test_validate_rules_errors_when_compiled_yaml_missing(tmp_path: Path):
    with patch.object(
        sys,
        "argv",
        [
            "validate_rules",
            "--compiled-in",
            str(tmp_path / "missing.yml"),
        ],
    ):
        assert validate.main() == 1


def test_validate_rules_errors_when_probe_missing(tmp_path: Path):
    compiled_in = tmp_path / "asca_rules.yml"
    _write_min_compiled_yaml(compiled_in)
    _write_fake_fork(tmp_path)

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(validate, "asca_supports_validate", return_value=True),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--compiled-in",
                str(compiled_in),
                "--inventory-dir",
                str(tmp_path / "inventory"),
                "--probe-words",
                str(tmp_path / "missing.wsca"),
            ],
        ),
    ):
        assert validate.main() == 1


@pytest.mark.parametrize(
    "asca_supports_validate, asca_command, use_fork_flag, expected_error",
    [
        (True, None, "--use-asca-fork", "fork not found"),
        (
            False,
            "/usr/bin/asca",
            "--no-use-asca-fork",
            "asca binary lacks the validate subcommand",
        ),
        (
            True,
            None,
            "--no-use-asca-fork",
            "asca binary not found",
        ),
    ],
)
def test_validate_rules_errors_when_asca_fork_missing(
    tmp_path: Path,
    capsys,
    asca_supports_validate,
    asca_command,
    use_fork_flag,
    expected_error,
):
    compiled_in = tmp_path / "asca_rules.yml"
    _write_min_compiled_yaml(compiled_in)
    probe = tmp_path / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(validate, "validation_asca_command", return_value=asca_command),
        patch.object(
            validate, "asca_supports_validate", return_value=asca_supports_validate
        ),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--compiled-in",
                str(compiled_in),
                "--inventory-dir",
                str(tmp_path / "inventory"),
                "--probe-words",
                str(probe),
                use_fork_flag,
            ],
        ),
    ):
        assert validate.main() == 1

    assert expected_error in capsys.readouterr().err


@patch.object(validate, "asca_version", return_value="asca-test-0.10")
@patch.object(validate, "write_ok_flip_changelog", return_value=2)
@patch.object(validate, "write_field_isolation_csvs")
@patch.object(validate, "write_error_cluster_csvs")
@patch.object(validate, "write_filtered_inventory_csvs")
@patch.object(validate, "ok_flip_changelog_rows")
@patch.object(validate, "load_inventory_csv", return_value=None)
@patch.object(validate, "iter_compiled_inventory_bundles")
@patch.object(validate, "read_compiled_rules_yaml")
@patch.object(validate, "filter_field_isolation_error")
@patch.object(validate, "filter_field_isolation_success")
@patch.object(validate, "filter_field_isolation_skipped")
@patch.object(validate, "field_isolation_rows_to_dataframe")
@pytest.mark.parametrize("field_isolation", [True, False])
def test_validate_rules_writes_validation_inventory(
    mock_field_isolation_rows_to_dataframe,
    mock_filter_field_isolation_skipped,
    mock_filter_field_isolation_success,
    mock_filter_field_isolation_error,
    mock_read_compiled,
    mock_iter_bundles,
    _mock_load_inventory,
    mock_flip_rows,
    _mock_write_filtered,
    _mock_write_error_clusters,
    mock_write_field_isolation,
    mock_write_changelog,
    _mock_asca_version,
    tmp_path: Path,
    field_isolation,
):
    work = tmp_path / "work"
    work.mkdir()
    compiled_in = work / "asca_rules.yml"
    _write_min_compiled_yaml(compiled_in)
    probe = work / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")
    inventory_dir = work / "inventory"
    section = {
        "index": "1",
        "section": "A",
        "rules": [
            {"stages": ["a", "b"]},
            {"stages": [], "status": "skipped"},
        ],
    }
    mock_read_compiled.return_value = {"schema_version": 1, "sections": [section]}
    rows = [
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=0,
            source="s:1",
            ok=True,
            rule="",
        ),
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=1,
            source="s:2",
            ok=False,
            rule="",
            failure_class="syntax_other",
            description="err",
        ),
    ]
    field_rows = [
        FieldIsolationRow(
            section_index="1",
            section_name="A",
            rule_id=0,
            source="s:1",
            whole_ok=True,
            input_ok=True,
            output_ok=True,
            env_ok=None,
            exception_ok=None,
            input_class="",
            output_class="",
            env_class="",
            exception_class="",
            input_description="",
            output_description="",
            env_description="",
            exception_description="",
            blame="none",
        ),
    ]
    mock_iter_bundles.return_value = [
        _bundle(section, section["rules"][0], "0", [rows[0]]),
        _bundle(section, section["rules"][1], "1", [rows[1]]),
    ]
    mock_flip_rows.return_value = MagicMock()
    _write_fake_fork(tmp_path)

    field_isolation_flag = (
        "--field-isolation" if field_isolation else "--no-field-isolation"
    )

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(validate, "asca_supports_validate", return_value=True),
        patch.object(
            validate,
            "field_isolation_rows_for_validation_rows",
            return_value=field_rows[:1],
        ),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--compiled-in",
                str(compiled_in),
                "--inventory-dir",
                str(inventory_dir),
                "--probe-words",
                str(probe),
                "--limit",
                "1",
                field_isolation_flag,
            ],
        ),
    ):
        assert validate.main() == 0

    mock_read_compiled.assert_called_once_with(compiled_in)
    mock_iter_bundles.assert_called_once()
    assert mock_iter_bundles.call_args.kwargs["probe_words"] == probe
    assert mock_iter_bundles.call_args.kwargs["asca_bin"] == str(
        tmp_path / "lib" / "bin" / "asca"
    )
    mock_flip_rows.assert_called_once()
    summary_path = inventory_dir / "rule-inventory-summary.md"
    assert summary_path.is_file()
    assert "asca-test-0.10" in summary_path.read_text(encoding="utf-8")

    if field_isolation:
        mock_field_isolation_rows_to_dataframe.assert_called_once()
        mock_filter_field_isolation_skipped.assert_called_once()
        mock_filter_field_isolation_success.assert_called_once()
        mock_filter_field_isolation_error.assert_called_once()
        mock_write_field_isolation.assert_called_once()
    else:
        mock_field_isolation_rows_to_dataframe.assert_not_called()
        mock_filter_field_isolation_skipped.assert_not_called()
        mock_filter_field_isolation_success.assert_not_called()
        mock_filter_field_isolation_error.assert_not_called()
        mock_write_field_isolation.assert_not_called()


@patch.object(validate, "asca_version", return_value="asca-test-0.10")
@patch.object(validate, "write_ok_flip_changelog", return_value=1)
@patch.object(validate, "write_field_isolation_csvs")
@patch.object(validate, "write_error_cluster_csvs")
@patch.object(validate, "write_filtered_inventory_csvs")
@patch.object(validate, "ok_flip_changelog_rows")
@patch.object(validate, "load_inventory_csv", return_value=None)
@patch.object(validate, "iter_compiled_inventory_bundles")
@patch.object(validate, "read_compiled_rules_yaml")
def test_validate_rules_reset_changelog_overwrites_existing(
    mock_read_compiled,
    mock_iter_bundles,
    _mock_load_inventory,
    mock_flip_rows,
    _mock_write_filtered,
    _mock_write_error_clusters,
    _mock_write_field_isolation,
    mock_write_changelog,
    _mock_asca_version,
    tmp_path: Path,
    capsys,
):
    work = tmp_path / "work"
    work.mkdir()
    compiled_in = work / "asca_rules.yml"
    _write_min_compiled_yaml(compiled_in)
    probe = work / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")
    inventory_dir = work / "inventory"
    inventory_dir.mkdir()
    changelog_path = inventory_dir / "rule-inventory-changelog.csv"
    changelog_path.write_text(
        "section_index,rule_id,source,ok,timestamp\nold,r0,s:0,True,old\n",
        encoding="utf-8",
    )
    section = {"index": "1", "section": "A", "rules": [{"stages": ["a", "b"]}]}
    mock_read_compiled.return_value = {"schema_version": 1, "sections": [section]}
    row = ValidationRow("1", "A", 0, "s:1", True, "", "", "", "", "")
    mock_iter_bundles.return_value = [_bundle(section, section["rules"][0], "0", [row])]
    mock_flip_rows.return_value = MagicMock()

    def _assert_reset_write(flips, path, *, reset):
        assert reset is True
        return 1

    mock_write_changelog.side_effect = _assert_reset_write
    _write_fake_fork(tmp_path)

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(validate, "asca_supports_validate", return_value=True),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--compiled-in",
                str(compiled_in),
                "--inventory-dir",
                str(inventory_dir),
                "--probe-words",
                str(probe),
                "--reset-changelog",
            ],
        ),
    ):
        assert validate.main() == 0

    mock_write_changelog.assert_called_once()
    assert "reset" in capsys.readouterr().out


@patch.object(validate, "asca_version", return_value="asca-test-0.10")
@patch.object(validate, "write_field_isolation_csvs")
@patch.object(validate, "write_error_cluster_csvs")
@patch.object(validate, "write_filtered_inventory_csvs")
@patch.object(validate, "load_inventory_csv")
@patch.object(validate, "iter_compiled_inventory_bundles")
@patch.object(validate, "read_compiled_rules_yaml")
def test_validate_rules_reset_changelog_empty_flips_writes_header_only(
    mock_read_compiled,
    mock_iter_bundles,
    mock_load_inventory,
    _mock_write_filtered,
    _mock_write_error_clusters,
    _mock_write_field_isolation,
    _mock_asca_version,
    tmp_path: Path,
):
    work = tmp_path / "work"
    work.mkdir()
    compiled_in = work / "asca_rules.yml"
    _write_min_compiled_yaml(compiled_in)
    probe = work / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")
    inventory_dir = work / "inventory"
    inventory_dir.mkdir()
    changelog_path = inventory_dir / "rule-inventory-changelog.csv"
    changelog_path.write_text("old,data\n", encoding="utf-8")
    row = ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", "")
    section = {"index": "1", "section": "A", "rules": [{"stages": ["a", "b"]}]}
    mock_read_compiled.return_value = {"schema_version": 1, "sections": [section]}
    mock_iter_bundles.return_value = [
        _bundle(section, section["rules"][0], "r0", [row]),
    ]
    mock_load_inventory.return_value = validation_rows_to_dataframe([row])
    _write_fake_fork(tmp_path)

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(validate, "asca_supports_validate", return_value=True),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--compiled-in",
                str(compiled_in),
                "--inventory-dir",
                str(inventory_dir),
                "--probe-words",
                str(probe),
                "--reset-changelog",
            ],
        ),
    ):
        assert validate.main() == 0

    rows = list(csv.DictReader(changelog_path.open(encoding="utf-8")))
    assert rows == []
    with changelog_path.open(encoding="utf-8") as handle:
        assert handle.readline().strip() == ",".join(CHANGELOG_CSV_COLUMNS)


def test_asca_version_reads_stdout():
    proc = MagicMock(stdout="asca 0.10.5\n", returncode=0)
    with patch.object(validation_cli.subprocess, "run", return_value=proc):
        assert validation_cli.asca_version("/usr/bin/asca") == "asca 0.10.5"


def test_asca_version_falls_back_on_subprocess_error():
    with patch.object(validation_cli.subprocess, "run", side_effect=OSError("boom")):
        assert validation_cli.asca_version("/usr/bin/asca") == "0.10.x"


def test_validation_asca_command_uses_fork_or_path(tmp_path: Path):
    fork = validation_cli.fork_asca_command(repo_root=tmp_path)
    _write_fake_fork(tmp_path)
    assert validation_cli.validation_asca_command(
        use_fork=True, repo_root=tmp_path
    ) == str(fork)
    with patch.object(validation_cli, "resolve_asca_bin", return_value="/usr/bin/asca"):
        assert validation_cli.validation_asca_command(
            use_fork=False, repo_root=tmp_path
        ) == ("/usr/bin/asca")
