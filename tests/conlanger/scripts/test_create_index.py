"""Tests for ``create_index`` CLI (parse-only)."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from conlanger.scripts import create_index as regen


@pytest.fixture(autouse=True)
def tmp_root(tmp_path: Path, mocker):
    return mocker.patch("conlanger.scripts.create_index.ROOT", tmp_path)


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
    parse_dir = tmp_path / "parse"
    _configure_parser_mock(
        mock_parser_cls,
        matches=[
            ManualMappingMatch(
                section_index="17.5.1",
                section_name="Proto-Indo-European to Old Irish",
                rule_id="r0",
                source="index.html:10",
                from_text="s → z / _C[+voice]",
                to_text="s → z / _C[+voice]",
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
            "--parse-dir",
            str(parse_dir),
        ],
    ):
        assert regen.main() == 0

    matched_path = parse_dir / "manual_mappings_matched_rules.csv"
    assert matched_path.is_file()
    text = matched_path.read_text(encoding="utf-8")
    assert "from_text" in text
    assert "to_text" in text
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
        ],
    ):
        assert regen.main() == 1
