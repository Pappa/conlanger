from pathlib import Path

from conlanger.tools.corpus_io import dump_cleaned_corpus, write_cleaned_corpus


def test_dump_cleaned_corpus_uses_literal_block_for_multiline_raw():
    doc = {
        "abbreviations": {},
        "sections": [
            {
                "section": "Test",
                "index": "1.0",
                "rules": [
                    {
                        "input": "a",
                        "output": "b",
                        "raw": "line one\nline two",
                        "source": "sample.html:10",
                    }
                ],
            }
        ],
    }
    text = dump_cleaned_corpus(doc)
    assert "raw: |" in text
    assert "line one" in text
    assert "line two" in text
    assert "line one\\nline two" not in text


def test_dump_cleaned_corpus_single_line_raw_uses_plain_scalar():
    doc = {
        "abbreviations": {},
        "sections": [
            {
                "section": "Test",
                "index": "1.0",
                "rules": [
                    {
                        "input": "a",
                        "output": "b",
                        "raw": "a → b",
                        "source": "sample.html:10",
                    }
                ],
            }
        ],
    }
    text = dump_cleaned_corpus(doc)
    assert "raw: |\n" not in text
    assert "raw: a → b" in text


def test_write_cleaned_corpus(tmp_path: Path):
    doc = {
        "abbreviations": {},
        "sections": [
            {
                "section": "Test",
                "index": "1.0",
                "rules": [
                    {
                        "input": "a",
                        "output": "b",
                        "raw": "a → b",
                        "source": "sample.html:10",
                    }
                ],
            }
        ],
    }
    out = tmp_path / "nested" / "corpus.yml"
    write_cleaned_corpus(doc, out)
    text = out.read_text(encoding="utf-8")
    assert "raw: a → b" in text
    assert out.is_file()
