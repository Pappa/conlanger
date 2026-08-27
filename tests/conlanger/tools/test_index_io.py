from pathlib import Path

from conlanger.tools.index_io import dump_cleaned_index, write_cleaned_index


def test_dump_cleaned_index_uses_literal_block_for_multiline_raw():
    doc = {
        "sections": [
            {
                "section": "Test",
                "index": "1.0",
                "rules": [
                    {
                        "stages": ["a", "b"],
                        "raw": "line one\nline two",
                        "source": "sample.html:10",
                    }
                ],
            }
        ],
    }
    text = dump_cleaned_index(doc)
    assert "raw: |" in text
    assert "line one" in text
    assert "line two" in text
    assert "line one\\nline two" not in text


def test_dump_cleaned_index_single_line_raw_uses_plain_scalar():
    doc = {
        "sections": [
            {
                "section": "Test",
                "index": "1.0",
                "rules": [
                    {
                        "stages": ["a", "b"],
                        "raw": "a → b",
                        "source": "sample.html:10",
                    }
                ],
            }
        ],
    }
    text = dump_cleaned_index(doc)
    assert "raw: |\n" not in text
    assert "raw: a → b" in text


def test_write_cleaned_index(tmp_path: Path):
    doc = {
        "sections": [
            {
                "section": "Test",
                "index": "1.0",
                "rules": [
                    {
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
    text = out.read_text(encoding="utf-8")
    assert "raw: a → b" in text
    assert out.is_file()
