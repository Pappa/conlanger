"""Tests for ``regenerate_corpus`` CLI."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

from conlanger.scripts import regenerate_corpus as regen


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
    mock_parser_cls.return_value.parse.return_value = {"sections": []}

    with patch.object(
        sys,
        "argv",
        [
            "regenerate_corpus",
            "--html",
            str(html_path),
            "--yaml-out",
            str(yaml_out),
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
    mock_parser_cls.return_value.parse.assert_called_once_with(html_path)


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
    mock_parser_cls.return_value.parse.return_value = {"sections": []}

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
                "--skip-validation",
            ],
        ),
    ):
        assert regen.main() == 0

    mock_update.assert_not_called()
    mock_parser_cls.return_value.parse.assert_called_once()
