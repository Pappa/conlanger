"""Tests for ``validate_rules`` CLI."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from conlanger.scripts import validate_rules as validate
from conlanger.tools.index_inventory import FieldIsolationRow, ValidationRow


def _write_fake_fork(root: Path) -> Path:
    fork = root / "bin" / "bin" / "asca"
    fork.parent.mkdir(parents=True, exist_ok=True)
    fork.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fork.chmod(0o755)
    return fork


def test_validate_rules_errors_when_yaml_missing(tmp_path: Path):
    with patch.object(
        sys,
        "argv",
        [
            "validate_rules",
            "--yaml-in",
            str(tmp_path / "missing.yml"),
        ],
    ):
        assert validate.main() == 1


def test_validate_rules_errors_when_probe_missing(tmp_path: Path):
    yaml_in = tmp_path / "index.yml"
    yaml_in.write_text("sections: []\n", encoding="utf-8")
    _write_fake_fork(tmp_path)

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(validate, "asca_supports_validate", return_value=True),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--yaml-in",
                str(yaml_in),
                "--inventory-dir",
                str(tmp_path / "inventory"),
                "--probe-words",
                str(tmp_path / "missing.wsca"),
            ],
        ),
    ):
        assert validate.main() == 1


def test_validate_rules_errors_when_asca_fork_missing(
    tmp_path: Path,
    capsys,
):
    yaml_in = tmp_path / "index.yml"
    yaml_in.write_text("sections: []\n", encoding="utf-8")
    probe = tmp_path / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--yaml-in",
                str(yaml_in),
                "--inventory-dir",
                str(tmp_path / "inventory"),
                "--probe-words",
                str(probe),
            ],
        ),
    ):
        assert validate.main() == 1

    assert "fork not found" in capsys.readouterr().err


def test_validate_rules_errors_when_asca_missing_on_path(tmp_path: Path):
    yaml_in = tmp_path / "index.yml"
    yaml_in.write_text("sections: []\n", encoding="utf-8")
    probe = tmp_path / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(validate, "_validation_asca_command", return_value=None),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--yaml-in",
                str(yaml_in),
                "--inventory-dir",
                str(tmp_path / "inventory"),
                "--probe-words",
                str(probe),
                "--no-use-asca-fork",
            ],
        ),
    ):
        assert validate.main() == 1


@patch.object(validate, "_asca_version", return_value="asca-test-0.10")
@patch.object(validate, "append_ok_flip_changelog", return_value=2)
@patch.object(validate, "write_field_isolation_csvs")
@patch.object(validate, "write_error_cluster_csvs")
@patch.object(validate, "write_filtered_inventory_csvs")
@patch.object(validate, "ok_flip_changelog_rows")
@patch.object(validate, "load_inventory_csv", return_value=None)
@patch.object(validate, "iter_inventory_with_field_isolation")
@patch.object(validate, "read_cleaned_index")
def test_validate_rules_writes_validation_inventory(
    mock_read_index,
    mock_iter_rows,
    _mock_load_inventory,
    mock_flip_rows,
    _mock_write_filtered,
    _mock_write_error_clusters,
    mock_write_field_isolation,
    _mock_append_changelog,
    _mock_asca_version,
    tmp_path: Path,
):
    work = tmp_path / "work"
    work.mkdir()
    yaml_in = work / "index.yml"
    yaml_in.write_text("sections: []\n", encoding="utf-8")
    probe = work / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")
    inventory_dir = work / "inventory"
    mock_read_index.return_value = {
        "sections": [
            {
                "rules": [
                    {"stages": ["a", "b"]},
                    {"stages": [], "status": "skipped"},
                ]
            }
        ],
    }
    rows = [
        ValidationRow("1", "A", 0, "s:1", True, "", "", "", "", ""),
        ValidationRow(
            "1",
            "A",
            1,
            "s:2",
            False,
            "syntax_other",
            "broken-syntax",
            "",
            "",
            "err",
        ),
    ]
    field_rows = [
        FieldIsolationRow(
            "1",
            "A",
            0,
            "s:1",
            True,
            True,
            True,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "none",
        ),
    ]
    mock_iter_rows.return_value = (rows[:1], field_rows[:1])
    mock_flip_rows.return_value = MagicMock()
    _write_fake_fork(tmp_path)

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(validate, "asca_supports_validate", return_value=True),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--yaml-in",
                str(yaml_in),
                "--inventory-dir",
                str(inventory_dir),
                "--probe-words",
                str(probe),
                "--limit",
                "1",
            ],
        ),
    ):
        assert validate.main() == 0

    mock_read_index.assert_called_once_with(yaml_in)
    mock_iter_rows.assert_called_once()
    assert mock_iter_rows.call_args.kwargs["probe_words"] == probe
    assert mock_iter_rows.call_args.kwargs["asca_bin"] == str(
        tmp_path / "bin" / "bin" / "asca"
    )
    mock_flip_rows.assert_called_once()
    summary_path = inventory_dir / "asca-rule-inventory-summary.md"
    assert summary_path.is_file()
    assert "asca-test-0.10" in summary_path.read_text(encoding="utf-8")


@patch.object(validate, "_asca_version", return_value="asca-test-0.10")
@patch.object(validate, "append_ok_flip_changelog", return_value=1)
@patch.object(validate, "write_field_isolation_csvs")
@patch.object(validate, "write_error_cluster_csvs")
@patch.object(validate, "write_filtered_inventory_csvs")
@patch.object(validate, "ok_flip_changelog_rows")
@patch.object(validate, "load_inventory_csv", return_value=None)
@patch.object(validate, "iter_inventory_with_field_isolation")
@patch.object(validate, "read_cleaned_index")
def test_validate_rules_reset_changelog_overwrites_existing(
    mock_read_index,
    mock_iter_rows,
    _mock_load_inventory,
    mock_flip_rows,
    _mock_write_filtered,
    _mock_write_error_clusters,
    _mock_write_field_isolation,
    mock_append_changelog,
    _mock_asca_version,
    tmp_path: Path,
    capsys,
):
    work = tmp_path / "work"
    work.mkdir()
    yaml_in = work / "index.yml"
    yaml_in.write_text("sections: []\n", encoding="utf-8")
    probe = work / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")
    inventory_dir = work / "inventory"
    inventory_dir.mkdir()
    changelog_path = inventory_dir / "asca-rule-inventory-changelog.csv"
    changelog_path.write_text(
        "section_index,rule_id,source,ok,timestamp\nold,r0,s:0,True,old\n",
        encoding="utf-8",
    )
    mock_read_index.return_value = {
        "sections": [{"rules": [{"stages": ["a", "b"]}]}],
    }
    mock_iter_rows.return_value = (
        [ValidationRow("1", "A", 0, "s:1", True, "", "", "", "", "")],
        [
            FieldIsolationRow(
                "1",
                "A",
                0,
                "s:1",
                True,
                True,
                True,
                None,
                None,
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "none",
            )
        ],
    )
    mock_flip_rows.return_value = MagicMock()

    def _assert_cleared_then_append(flips, path):
        assert not path.is_file()
        return 1

    mock_append_changelog.side_effect = _assert_cleared_then_append
    _write_fake_fork(tmp_path)

    with (
        patch.object(validate, "ROOT", tmp_path),
        patch.object(validate, "asca_supports_validate", return_value=True),
        patch.object(
            sys,
            "argv",
            [
                "validate_rules",
                "--yaml-in",
                str(yaml_in),
                "--inventory-dir",
                str(inventory_dir),
                "--probe-words",
                str(probe),
                "--reset-changelog",
            ],
        ),
    ):
        assert validate.main() == 0

    mock_append_changelog.assert_called_once()
    assert "reset" in capsys.readouterr().out


def test_asca_version_reads_stdout():
    proc = MagicMock(stdout="asca 0.10.5\n", returncode=0)
    with patch.object(validate.subprocess, "run", return_value=proc):
        assert validate._asca_version("/usr/bin/asca") == "asca 0.10.5"


def test_asca_version_falls_back_on_subprocess_error():
    with patch.object(validate.subprocess, "run", side_effect=OSError("boom")):
        assert validate._asca_version("/usr/bin/asca") == "0.10.x"


def test_validation_asca_command_uses_fork_or_path(tmp_path: Path):
    fork = validate._fork_asca_command(repo_root=tmp_path)
    _write_fake_fork(tmp_path)
    assert validate._validation_asca_command(use_fork=True, repo_root=tmp_path) == str(
        fork
    )
    with patch.object(validate, "resolve_asca_bin", return_value="/usr/bin/asca"):
        assert validate._validation_asca_command(
            use_fork=False, repo_root=tmp_path
        ) == ("/usr/bin/asca")
