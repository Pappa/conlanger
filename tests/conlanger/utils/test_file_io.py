from pathlib import Path

import pandas as pd

from conlanger.utils.file_io import (
    write_manual_mappings_matched_csv,
    write_rule_comment_phrase_summary,
)


def test_write_rule_comment_phrase_summary(tmp_path: Path):
    doc = {
        "sections": [
            {
                "rules": [
                    {"comment": "when stressed; sporadic in some dialects"},
                    {"comment": "plain gloss"},
                    {"stages": ["a", "b"]},
                ]
            }
        ]
    }
    out = tmp_path / "comment-summary.md"
    count = write_rule_comment_phrase_summary(doc, out)
    text = out.read_text(encoding="utf-8")
    assert count == 2
    assert "when stressed" in text
    assert "sporadic" in text
    assert "plain gloss" in text


def test_write_rule_comment_phrase_summary_empty_doc(tmp_path: Path):
    out = tmp_path / "comment-summary.md"
    count = write_rule_comment_phrase_summary({"sections": []}, out)
    text = out.read_text(encoding="utf-8")
    assert count == 0
    assert "_(none matched)_" in text


def test_write_manual_mappings_matched_csv(tmp_path: Path):
    from conlanger.utils.mappings import ManualMappingMatch

    path = tmp_path / "manual_mappings_matched_rules.csv"
    write_manual_mappings_matched_csv(
        [
            ManualMappingMatch(
                section_index="17.5.1",
                section_name="Proto-Indo-European to Old Irish",
                rule_id="Old-Irish-mn",
                source="index_diachronica_original.html:5509",
                from_text="m̩ n̩ → am an / _{s,({m,j,w})V}",
                to_text="m̩ n̩ → am an / _{s,({m,j,w})V}",
            )
        ],
        path,
    )
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    assert list(df.columns) == [
        "section_index",
        "section_name",
        "rule_id",
        "source",
        "from_text",
        "to_text",
    ]
    assert df.iloc[0]["rule_id"] == "Old-Irish-mn"
    assert "_{s,({m,j,w})V}" in df.iloc[0]["from_text"]
    assert "_{s,({m,j,w})V}" in df.iloc[0]["to_text"]
