"""Tests for ``regenerate_corpus`` CLI."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from conlanger.scripts import regenerate_corpus as regen
from conlanger.tools.corpus_inventory import ValidationRow


def _configure_parser_mock(
    mock_parser_cls, *, sections=None, matches=None, unmatched=None
):
    mock_parser = mock_parser_cls.return_value
    mock_parser.parse.return_value = {"sections": sections or []}
    mock_parser.manual_mapping_matches = matches or []
    mock_parser.unmatched_manual_mappings.return_value = unmatched or []
    return mock_parser


@patch.object(regen, "update_series_mappings_from_html", return_value=3)
@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_corpus")
@patch.object(regen, "IndexDiachronicaParser")
def test_regenerate_corpus_runs_series_update_before_parse(
    mock_parser_cls,
    _mock_write_corpus,
    _mock_comment_summary,
    mock_update,
    tmp_path: Path,
):
    html_path = tmp_path / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    yaml_out = tmp_path / "out.yml"
    inventory_dir = tmp_path / "inventory"
    mock_parser = _configure_parser_mock(mock_parser_cls)

    with patch.object(
        sys,
        "argv",
        [
            "regenerate_corpus",
            "--html",
            str(html_path),
            "--yaml-out",
            str(yaml_out),
            "--inventory-dir",
            str(inventory_dir),
            "--skip-validation",
            "--update-series-mappings",
        ],
    ):
        assert regen.main() == 0

    mock_update.assert_called_once_with(
        html_path,
        csv_path=regen.DEFAULT_SERIES_MAPPINGS_CSV,
        report_path=regen.DEFAULT_SERIES_MAPPINGS_REPORT,
    )
    mock_parser.parse.assert_called_once_with(html_path)


@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_corpus")
@patch.object(regen, "IndexDiachronicaParser")
def test_regenerate_corpus_skips_series_update_by_default(
    mock_parser_cls,
    _mock_write_corpus,
    _mock_comment_summary,
    tmp_path: Path,
):
    html_path = tmp_path / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    yaml_out = tmp_path / "out.yml"
    inventory_dir = tmp_path / "inventory"
    mock_parser = _configure_parser_mock(mock_parser_cls)

    with (
        patch.object(regen, "update_series_mappings_from_html") as mock_update,
        patch.object(
            sys,
            "argv",
            [
                "regenerate_corpus",
                "--html",
                str(html_path),
                "--yaml-out",
                str(yaml_out),
                "--inventory-dir",
                str(inventory_dir),
                "--skip-validation",
            ],
        ),
    ):
        assert regen.main() == 0

    mock_update.assert_not_called()
    mock_parser.parse.assert_called_once()


@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_corpus")
@patch.object(regen, "IndexDiachronicaParser")
def test_regenerate_corpus_writes_manual_mappings_matched_csv(
    mock_parser_cls,
    _mock_write_corpus,
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
                rule_idx=0,
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
            "regenerate_corpus",
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


def test_regenerate_corpus_errors_when_html_missing(tmp_path: Path):
    with patch.object(
        sys,
        "argv",
        [
            "regenerate_corpus",
            "--html",
            str(tmp_path / "missing.html"),
            "--skip-validation",
        ],
    ):
        assert regen.main() == 1


@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_corpus")
@patch.object(regen, "IndexDiachronicaParser")
def test_regenerate_corpus_errors_when_probe_missing(
    mock_parser_cls,
    _mock_write_corpus,
    _mock_comment_summary,
    tmp_path: Path,
):
    html_path = tmp_path / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    _configure_parser_mock(mock_parser_cls)

    with (
        patch.object(regen.shutil, "which", return_value="/usr/bin/asca"),
        patch.object(
            sys,
            "argv",
            [
                "regenerate_corpus",
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


@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_corpus")
@patch.object(regen, "IndexDiachronicaParser")
def test_regenerate_corpus_errors_when_asca_missing(
    mock_parser_cls,
    _mock_write_corpus,
    _mock_comment_summary,
    tmp_path: Path,
):
    html_path = tmp_path / "index.html"
    html_path.write_text("<html><body></body></html>", encoding="utf-8")
    probe = tmp_path / "probe.wsca"
    probe.write_text("probe", encoding="utf-8")
    _configure_parser_mock(mock_parser_cls)

    with (
        patch.object(regen.shutil, "which", return_value=None),
        patch.object(
            sys,
            "argv",
            [
                "regenerate_corpus",
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
        assert regen.main() == 1


@patch.object(regen, "_asca_version", return_value="asca-test-0.10")
@patch.object(regen, "append_ok_flip_changelog", return_value=2)
@patch.object(regen, "write_filtered_inventory_csvs")
@patch.object(regen, "write_validation_csv")
@patch.object(regen, "ok_flip_changelog_rows")
@patch.object(regen, "load_inventory_csv", return_value=None)
@patch.object(regen, "iter_validation_rows")
@patch.object(regen, "write_rule_comment_phrase_summary", return_value=0)
@patch.object(regen, "write_cleaned_corpus")
@patch.object(regen, "IndexDiachronicaParser")
def test_regenerate_corpus_writes_validation_inventory(
    mock_parser_cls,
    _mock_write_corpus,
    _mock_comment_summary,
    mock_iter_rows,
    _mock_load_inventory,
    mock_flip_rows,
    _mock_write_csv,
    _mock_write_filtered,
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
    mock_iter_rows.return_value = rows
    mock_flip_rows.return_value = MagicMock()

    with (
        patch.object(regen, "ROOT", tmp_path),
        patch.object(regen.shutil, "which", return_value="/usr/bin/asca"),
        patch.object(
            sys,
            "argv",
            [
                "regenerate_corpus",
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
    mock_flip_rows.assert_called_once()
    summary_path = inventory_dir / "asca-rule-inventory-summary.md"
    assert summary_path.is_file()
    assert "asca-test-0.10" in summary_path.read_text(encoding="utf-8")


def test_asca_version_when_binary_not_on_path():
    with patch.object(regen.shutil, "which", return_value=None):
        assert regen._asca_version() == "not found on PATH"


def test_asca_version_reads_stdout():
    proc = MagicMock(stdout="asca 0.10.5\n", returncode=0)
    with (
        patch.object(regen.shutil, "which", return_value="/usr/bin/asca"),
        patch.object(regen.subprocess, "run", return_value=proc),
    ):
        assert regen._asca_version() == "asca 0.10.5"


def test_asca_version_falls_back_on_subprocess_error():
    with (
        patch.object(regen.shutil, "which", return_value="/usr/bin/asca"),
        patch.object(regen.subprocess, "run", side_effect=OSError("boom")),
    ):
        assert regen._asca_version() == "0.10.x"
