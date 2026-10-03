"""End-to-end tests for the cleaned rule index pipeline.

Primary seam (spec): HTML → IndexDiachronicaParser → index document →
DiachronicSeries compile → validate_asca per index rule.
"""

from __future__ import annotations

import pytest
from fixtures.minimal_mappings import minimal_feature_mappings
from lxml import html

from conlanger.tools.ingest import IndexDiachronicaParser
from conlanger.utils.mappings import ParserConfig

_INDEX_HTML = """\
<!doctype html>
<html><body>
<section id="{section_id}">
{section_body}
</section>
</body></html>
"""

# Representative ingest cases from ``sound_change_rules.csv`` (ids for traceability).
_E2E_PARSE_SMOKE: list[tuple[str, str, dict[str, str | None]]] = [
    (
        "e1e33459",
        "r → ∅ / {ð,f}_{ɡ,ɣ}",
        {
            "stages": ["r", "∅"],
            "env": "{ð,f}_{ɡ,ɣ}",
        },
    ),
    ("4335174c", "dʒ → tʃ / _#", {"stages": ["dʒ", "tʃ"], "env": "_#"}),
    (
        "4f873820",
        "a → e / _j when stressed",
        {
            "stages": ["a", "e"],
            "env": "_j when stressed",
        },
    ),
    ("63f9e7f4", "SN → N[- voice]", {"stages": ["SN", "N[- voice]"]}),
    (
        "9f237660",
        "C[+ voice] → C[- voice] / _#",
        {
            "stages": ["C[+ voice]", "C[- voice]"],
            "env": "_#",
        },
    ),
    ("f8cd1a6f", "ɑ → ə", {"stages": ["ɑ", "ə"]}),
    ("65372311", "qh → k", {"stages": ["qh", "k"]}),
    ("e71a2977", "ŋ → n", {"stages": ["ŋ", "n"]}),
]


def _parse_section(
    *,
    section_id: str,
    section_body: str,
    source_file: str,
) -> dict:
    root = html.document_fromstring(
        _INDEX_HTML.format(section_id=section_id, section_body=section_body)
    )
    config = ParserConfig(feature_mappings=minimal_feature_mappings())
    doc = IndexDiachronicaParser(config).parse(doc=root, source_file=source_file)
    assert len(doc["sections"]) == 1
    return doc["sections"][0]


def _assert_index_rule_shape(rule: dict) -> None:
    for key in ("stages", "raw", "source"):
        assert key in rule
    if not rule.get("env"):
        assert "env" not in rule
    if not rule.get("exception"):
        assert "exception" not in rule


def test_e2e_minimal_html_fixture_shape_and_raw_preservation():
    """Parse a minimal Index-shaped section and assert index schema + raw audit."""
    source_file = "minimal.html"
    section = _parse_section(
        section_id="E2E",
        source_file=source_file,
        section_body="""\
<h2>1.0 Pipeline smoke</h2>
<p><i>Fixture citation</i></p>
<p class="schg">a → b</p>
<p class="schg">C[+voiced] → C[-voice] / _#</p>
<p>Interleaved section comment</p>
<p class="schg">no arrow here</p>""",
    )

    assert section["index"] == "1.0"
    assert section["section"] == "Pipeline smoke"
    assert section["citation"] == "Fixture citation"
    assert section["comments"][0] == "Interleaved section comment"
    assert len(section["rules"]) == 3

    ok_rule, feature_rule, bad_rule = section["rules"]
    _assert_index_rule_shape(ok_rule)
    assert ok_rule["stages"] == ["a", "b"]
    assert ok_rule["raw"] == "a → b"
    assert ok_rule["source"].startswith(source_file)

    assert feature_rule["stages"] == ["C[+voice]", "C[-voice]"]
    assert feature_rule["env"] == "_#"
    assert "voiced" in feature_rule["raw"]

    assert bad_rule["stages"] == ["no arrow here"]
    assert "status" not in bad_rule


@pytest.mark.parametrize(
    ("case_id", "raw", "expected"),
    _E2E_PARSE_SMOKE,
    ids=[case_id for case_id, _, _ in _E2E_PARSE_SMOKE],
)
def test_e2e_html_extract_pipeline_parse(
    case_id: str,
    raw: str,
    expected: dict[str, str | None],
):
    """HTML rule line → parser → index fields match fixture expectations."""
    section = _parse_section(
        section_id=case_id,
        source_file=f"{case_id}.html",
        section_body=(f'<h2>99.0 Fixture {case_id}</h2>\n<p class="schg">{raw}</p>'),
    )
    assert len(section["rules"]) == 1
    rule = section["rules"][0]
    _assert_index_rule_shape(rule)
    assert rule["raw"] == raw

    for key, value in expected.items():
        assert rule.get(key) == value, case_id
