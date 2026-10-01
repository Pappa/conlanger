from pathlib import Path

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
