from pathlib import Path

import pytest

from conlanger.tools.index_io import (
    read_cleaned_index,
    write_cleaned_index,
)


def test_write_and_read_cleaned_index_round_trip(tmp_path: Path):
    doc = {
        "sections": [
            {
                "section": "Test",
                "index": "1.0",
                "rules": [
                    {
                        "rule_id": "Anglish-v1",
                        "stages": ["a", "b"],
                        "raw": "a → b",
                        "source": "sample.html:10",
                    }
                ],
            }
        ],
    }
    out = tmp_path / "nested" / "index.yml"
    write_cleaned_index(doc, out)

    index_text = out.read_text(encoding="utf-8")

    assert (
        index_text
        == """sections:
- section: Test
  index: '1.0'
  rules:
  - rule_id: Anglish-v1
    stages:
    - a
    - b
    raw: a → b
    source: sample.html:10
"""
    )
    loaded = read_cleaned_index(out)
    assert loaded == doc


def test_write_uses_literal_block_style_for_multiline_strings(tmp_path: Path) -> None:
    doc = {
        "sections": [
            {
                "section": "Test",
                "index": "1.0",
                "rules": [
                    {
                        "rule_id": "Anglish-v1",
                        "comment": "first line\nsecond line",
                        "stages": ["a"],
                        "raw": "a",
                        "source": "sample.html:1",
                    }
                ],
            }
        ],
    }
    out = tmp_path / "index.yml"
    write_cleaned_index(doc, out)

    index_text = out.read_text(encoding="utf-8")
    assert "comment: |" in index_text
    assert "first line" in index_text
    assert "second line" in index_text
    assert read_cleaned_index(out) == doc


def test_read_cleaned_index_rejects_non_mapping_root(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yml"
    bad.write_text("- not a mapping\n", encoding="utf-8")
    with pytest.raises(TypeError, match=r"expected mapping at root"):
        read_cleaned_index(bad)
