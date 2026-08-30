"""Tests for ``create_index`` CLI."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from conlanger.scripts import create_index as regen
from conlanger.tools.index_inventory import FieldIsolationRow, ValidationRow


def _write_fake_fork(root: Path) -> Path:
    fork = root / "bin" / "bin" / "asca"
    fork.parent.mkdir(parents=True, exist_ok=True)
    fork.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    fork.chmod(0o755)
    return fork


def _configure_parser_mock(
    mock_parser_cls, *, sections=None, matches=None, unmatched=None
):
    mock_parser = mock_parser_cls.return_value
    mock_parser.parse.return_value = {"sections": sections or []}
    mock_parser.manual_mapping_matches = matches or []
    mock_parser.unmatched_manual_mappings.return_value = unmatched or []
    return mock_parser


@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_index")
@patch.object(regen, "IndexDiachronicaParser")
def test_create_index_writes_manual_mappings_matched_csv(
    mock_parser_cls,
    _mock_write_index,
    _mock_comment_summary,
    tmp_path: Path,
    capsys,
):
    from conlanger.utils.mappings import ManualMapping, ManualMappingMatch

    html_path = tmp_path / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    inventory_dir = tmp_path / "inventory"
    _configure_parser_mock(
        mock_parser_cls,
        matches=[
            ManualMappingMatch(
                section_index="17.5.1",
                section_name="Proto-Indo-European to Old Irish",
                rule_id="r0",
                source="index.html:10",
                manual_mapping="s → z / _C[+voice]",
            )
        ],
        unmatched=[ManualMapping(from_text="unused-from", to_text="x", reason="")],
    )

    with patch.object(
        sys,
        "argv",
        [
            "create_index",
            "--html",
            str(html_path),
            "--yaml-out",
            str(tmp_path / "out.yml"),
            "--inventory-dir",
            str(inventory_dir),
            "--skip-validation",
        ],
    ):
        assert regen.main() == 0

    matched_path = inventory_dir / "manual_mappings_matched_rules.csv"
    assert matched_path.is_file()
    text = matched_path.read_text(encoding="utf-8")
    assert "manual_mapping" in text
    assert "s → z / _C[+voice]" in text
    err = capsys.readouterr().err
    assert "unused-from" in err
    assert "manual mapping" in err.lower()


def test_create_index_errors_when_html_missing(tmp_path: Path):
    with patch.object(
        sys,
        "argv",
        [
            "create_index",
            "--html",
            str(tmp_path / "missing.html"),
            "--skip-validation",
        ],
    ):
        assert regen.main() == 1


@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_index")
@patch.object(regen, "IndexDiachronicaParser")
def test_create_index_errors_when_probe_missing(
    mock_parser_cls,
    _mock_write_index,
    _mock_comment_summary,
    tmp_path: Path,
):
    html_path = tmp_path / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    _configure_parser_mock(mock_parser_cls)

    _write_fake_fork(tmp_path)

    with (
        patch.object(regen, "ROOT", tmp_path),
        patch.object(regen, "asca_supports_validate", return_value=True),
        patch.object(
            sys,
            "argv",
            [
                "create_index",
                "--html",
                str(html_path),
                "--yaml-out",
                str(tmp_path / "out.yml"),
                "--inventory-dir",
                str(tmp_path / "inventory"),
                "--probe-words",
                str(tmp_path / "missing.wsca"),
            ],
        ),
    ):
        assert regen.main() == 1


def test_create_index_errors_when_asca_fork_missing(
    tmp_path: Path,
    capsys,
):
    html_path = tmp_path / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    probe = tmp_path / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")

    with (
        patch.object(regen, "write_rule_comment_phrase_summary", return_value=0),
        patch.object(regen, "write_cleaned_index"),
        patch.object(regen, "IndexDiachronicaParser") as mock_parser_cls,
        patch.object(regen, "ROOT", tmp_path),
        patch.object(
            sys,
            "argv",
            [
                "create_index",
                "--html",
                str(html_path),
                "--yaml-out",
                str(tmp_path / "out.yml"),
                "--inventory-dir",
                str(tmp_path / "inventory"),
                "--probe-words",
                str(probe),
            ],
        ),
    ):
        _configure_parser_mock(mock_parser_cls)
        assert regen.main() == 1

    assert "fork not found" in capsys.readouterr().err


@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_index")
@patch.object(regen, "IndexDiachronicaParser")
def test_create_index_errors_when_asca_missing_on_path(
    mock_parser_cls,
    _mock_write_index,
    _mock_comment_summary,
    tmp_path: Path,
):
    html_path = tmp_path / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    probe = tmp_path / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")
    _configure_parser_mock(mock_parser_cls)

    with (
        patch.object(regen, "ROOT", tmp_path),
        patch.object(regen, "_validation_asca_command", return_value=None),
        patch.object(
            sys,
            "argv",
            [
                "create_index",
                "--html",
                str(html_path),
                "--yaml-out",
                str(tmp_path / "out.yml"),
                "--inventory-dir",
                str(tmp_path / "inventory"),
                "--probe-words",
                str(probe),
                "--no-use-asca-fork",
            ],
        ),
    ):
        assert regen.main() == 1


@patch.object(regen, "_asca_version", return_value="asca-test-0.10")
@patch.object(regen, "append_ok_flip_changelog", return_value=2)
@patch.object(regen, "write_field_isolation_csvs")
@patch.object(regen, "write_error_cluster_csvs")
@patch.object(regen, "write_filtered_inventory_csvs")
@patch.object(regen, "ok_flip_changelog_rows")
@patch.object(regen, "load_inventory_csv", return_value=None)
@patch.object(regen, "iter_inventory_with_field_isolation")
@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_index")
@patch.object(regen, "IndexDiachronicaParser")
def test_create_index_writes_validation_inventory(
    mock_parser_cls,
    _mock_write_index,
    _mock_comment_summary,
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
    html_path = work / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    yaml_out = work / "out.yml"
    probe = work / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")
    inventory_dir = work / "inventory"
    _configure_parser_mock(
        mock_parser_cls,
        sections=[
            {
                "rules": [
                    {"stages": ["a", "b"]},
                    {"stages": [], "status": "skipped"},
                ]
            }
        ],
    )
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
        patch.object(regen, "ROOT", tmp_path),
        patch.object(regen, "asca_supports_validate", return_value=True),
        patch.object(
            sys,
            "argv",
            [
                "create_index",
                "--html",
                str(html_path),
                "--yaml-out",
                str(yaml_out),
                "--inventory-dir",
                str(inventory_dir),
                "--probe-words",
                str(probe),
                "--limit",
                "1",
            ],
        ),
    ):
        assert regen.main() == 0

    mock_iter_rows.assert_called_once()
    assert mock_iter_rows.call_args.kwargs["probe_words"] == probe
    assert mock_iter_rows.call_args.kwargs["asca_bin"] == str(
        tmp_path / "bin" / "bin" / "asca"
    )
    mock_flip_rows.assert_called_once()
    summary_path = inventory_dir / "asca-rule-inventory-summary.md"
    assert summary_path.is_file()
    assert "asca-test-0.10" in summary_path.read_text(encoding="utf-8")


@patch.object(regen, "_asca_version", return_value="asca-test-0.10")
@patch.object(regen, "append_ok_flip_changelog", return_value=1)
@patch.object(regen, "write_field_isolation_csvs")
@patch.object(regen, "write_error_cluster_csvs")
@patch.object(regen, "write_filtered_inventory_csvs")
@patch.object(regen, "ok_flip_changelog_rows")
@patch.object(regen, "load_inventory_csv", return_value=None)
@patch.object(regen, "iter_inventory_with_field_isolation")
@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_index")
@patch.object(regen, "IndexDiachronicaParser")
def test_create_index_reset_changelog_overwrites_existing(
    mock_parser_cls,
    _mock_write_index,
    _mock_comment_summary,
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
    html_path = work / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    probe = work / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")
    inventory_dir = work / "inventory"
    inventory_dir.mkdir()
    changelog_path = inventory_dir / "asca-rule-inventory-changelog.csv"
    changelog_path.write_text(
        "section_index,rule_id,source,ok,timestamp\nold,r0,s:0,True,old\n",
        encoding="utf-8",
    )
    _configure_parser_mock(
        mock_parser_cls, sections=[{"rules": [{"stages": ["a", "b"]}]}]
    )
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
        patch.object(regen, "ROOT", tmp_path),
        patch.object(regen, "asca_supports_validate", return_value=True),
        patch.object(
            sys,
            "argv",
            [
                "create_index",
                "--html",
                str(html_path),
                "--yaml-out",
                str(work / "out.yml"),
                "--inventory-dir",
                str(inventory_dir),
                "--probe-words",
                str(probe),
                "--reset-changelog",
            ],
        ),
    ):
        assert regen.main() == 0

    mock_append_changelog.assert_called_once()
    assert "reset" in capsys.readouterr().out


def test_asca_version_reads_stdout():
    proc = MagicMock(stdout="asca 0.10.5\n", returncode=0)
    with patch.object(regen.subprocess, "run", return_value=proc):
        assert regen._asca_version("/usr/bin/asca") == "asca 0.10.5"


def test_asca_version_falls_back_on_subprocess_error():
    with patch.object(regen.subprocess, "run", side_effect=OSError("boom")):
        assert regen._asca_version("/usr/bin/asca") == "0.10.x"


def test_validation_asca_command_uses_fork_or_path(tmp_path: Path):
    fork = regen._fork_asca_command(repo_root=tmp_path)
    _write_fake_fork(tmp_path)
    assert regen._validation_asca_command(use_fork=True, repo_root=tmp_path) == str(
        fork
    )
    with patch.object(regen, "resolve_asca_bin", return_value="/usr/bin/asca"):
        assert regen._validation_asca_command(use_fork=False, repo_root=tmp_path) == (
            "/usr/bin/asca"
        )
