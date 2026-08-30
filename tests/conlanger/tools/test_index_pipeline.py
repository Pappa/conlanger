"""End-to-end tests for the cleaned rule index pipeline.

Primary seam (spec): HTML → IndexDiachronicaParser → index document →
DiachronicSeries compile → validate_asca per index rule.
"""

from __future__ import annotations

import html as html_module
from pathlib import Path

import pytest
from helpers import default_index_parser

from conlanger.appliers.asca import validate_asca
from conlanger.tools.index_inventory import validate_index_rule
from conlanger.tools.rules import DiachronicSeries
from tests.conftest import ASCA_INSTALLED
from tests.fixtures.minimal_mappings import MINIMAL_GROUP_MAPPINGS

_PROBE = Path(__file__).resolve().parents[2] / "fixtures" / "asca_probe_words.wsca"

_INDEX_HTML = """\
<!doctype html>
<html><body>
<section id="{section_id}">
{section_body}
</section>
</body></html>
"""

# Curated rules verified through HTML ingest → compile → validate.
# ``asca_guess`` CSV rows use hand-edited asca_* fields and are not reliable
# for full-pipeline expectation without re-baselining from raw HTML.
_E2E_VALIDATE_SMOKE: list[tuple[str, str, bool, str]] = [
    # id, raw, expect_ok, section_index (for series lookup)
    ("simple-io", "a → b", True, "1.0"),
    ("env-boundary", "dʒ → tʃ / _#", True, "1.0"),
    ("feature-matrix", "C[+voiced] → C[-voice] / _#", True, "1.0"),
    ("complex-env", "r → ∅ / {ð,f}_{ɡ,ɣ}", True, "1.0"),
    ("stress-env", "a → e / _j when stressed", True, "47.1"),
    ("chain-split", "dʒ → tʃ → ʃ", True, "1.0"),
    ("metathesis", "uɛ → ɛu", True, "1.0"),
    ("group-compile", "SN → N[- voice]", True, "1.0"),
    ("sebirwa-atr", "i u VS → j w A / _V[+high +ATR]", True, "30.1.1.1"),
    ("prose-env-medial", "z → ð / medial", True, "1.0"),
    ("collective-expanded", "sₓ → ʃ", True, "6.1.2.1"),
    ("positional-literal", "C₁ → C₂", True, "10.2.1"),
    ("held-out-parse", "no arrow here", False, "1.0"),
]

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


def _write_section_html(
    path: Path,
    *,
    section_id: str,
    section_body: str,
) -> None:
    path.write_text(
        _INDEX_HTML.format(section_id=section_id, section_body=section_body),
        encoding="utf-8",
    )


def _parse_section(
    html_path: Path,
    *,
    source_file: str = "e2e.html",
) -> dict:
    doc = default_index_parser().parse(html_path, source_file=source_file)
    assert len(doc["sections"]) == 1
    return doc["sections"][0]


def _assert_index_rule_shape(rule: dict) -> None:
    for key in ("stages", "raw", "source"):
        assert key in rule
    if not rule.get("env"):
        assert "env" not in rule
    if not rule.get("exception"):
        assert "exception" not in rule


def test_e2e_minimal_html_fixture_shape_and_raw_preservation(tmp_path: Path):
    """Parse a minimal Index-shaped section and assert index schema + raw audit."""
    html_path = tmp_path / "minimal.html"
    _write_section_html(
        html_path,
        section_id="E2E",
        section_body="""\
<h2>1.0 Pipeline smoke</h2>
<p><i>Fixture citation</i></p>
<p class="schg">a → b</p>
<p class="schg">C[+voiced] → C[-voice] / _#</p>
<p>Interleaved section comment</p>
<p class="schg">no arrow here</p>""",
    )
    section = _parse_section(html_path, source_file="minimal.html")

    assert section["index"] == "1.0"
    assert section["section"] == "Pipeline smoke"
    assert section["citation"] == "Fixture citation"
    assert [c["raw"] for c in section["comments"]] == ["Interleaved section comment"]
    assert len(section["rules"]) == 3

    ok_rule, feature_rule, bad_rule = section["rules"]
    _assert_index_rule_shape(ok_rule)
    assert ok_rule["stages"] == ["a", "b"]
    assert ok_rule["raw"] == "a → b"
    assert ok_rule["source"].startswith("minimal.html:")

    assert feature_rule["stages"] == ["C[+voice]", "C[-voice]"]
    assert feature_rule["env"] == "_#"
    assert "voiced" in feature_rule["raw"]

    assert bad_rule["stages"] == ["no arrow here"]
    assert "status" not in bad_rule


@pytest.mark.skipif(not ASCA_INSTALLED, reason="asca binary not on PATH")
@pytest.mark.skipif(not _PROBE.is_file(), reason="probe wordlist missing")
def test_e2e_minimal_html_fixture_compile_and_validate(tmp_path: Path):
    """Active rules compile through DiachronicSeries and pass validate_asca."""
    html_path = tmp_path / "validate.html"
    _write_section_html(
        html_path,
        section_id="Validate",
        section_body="""\
<h2>47.1 Stress conditions</h2>
<p class="schg">a → b</p>
<p class="schg">dʒ → tʃ / _#</p>""",
    )
    section = _parse_section(html_path)
    rows: list = []
    for rule in section.get("rules") or []:
        rule_id = str(rule.get("rule_id", ""))
        rows.extend(
            validate_index_rule(
                section,
                rule,
                rule_id,
                probe_words=_PROBE,
                group_mappings=MINIMAL_GROUP_MAPPINGS,
            )
        )

    assert len(rows) == 2
    assert all(row.ok for row in rows)
    assert rows[0].failure_class == ""
    assert rows[0].reason == ""

    validate_asca(
        DiachronicSeries(section, group_mappings=MINIMAL_GROUP_MAPPINGS),
        probe_words=_PROBE,
    )


@pytest.mark.parametrize(
    ("case_id", "raw", "expected"),
    _E2E_PARSE_SMOKE,
    ids=[case_id for case_id, _, _ in _E2E_PARSE_SMOKE],
)
def test_e2e_html_extract_pipeline_parse(
    case_id: str,
    raw: str,
    expected: dict[str, str | None],
    tmp_path: Path,
):
    """HTML rule line → parser → index fields match fixture expectations."""
    html_path = tmp_path / f"{case_id}.html"
    escaped = html_module.escape(raw)
    _write_section_html(
        html_path,
        section_id=case_id,
        section_body=(
            f'<h2>99.0 Fixture {case_id}</h2>\n<p class="schg">{escaped}</p>'
        ),
    )
    section = _parse_section(html_path, source_file=f"{case_id}.html")
    assert len(section["rules"]) == 1
    rule = section["rules"][0]
    _assert_index_rule_shape(rule)
    assert rule["raw"] == raw

    for key, value in expected.items():
        assert rule.get(key) == value, case_id


@pytest.mark.skipif(not ASCA_INSTALLED, reason="asca binary not on PATH")
@pytest.mark.skipif(not _PROBE.is_file(), reason="probe wordlist missing")
@pytest.mark.parametrize(
    ("case_id", "raw", "expect_ok", "section_index"),
    _E2E_VALIDATE_SMOKE,
    ids=[case_id for case_id, _, _, _ in _E2E_VALIDATE_SMOKE],
)
def test_e2e_smoke_pipeline_validate(
    case_id: str,
    raw: str,
    expect_ok: bool,
    section_index: str,
    tmp_path: Path,
):
    """Representative HTML rules → parse → compile → validate_asca outcomes."""
    html_path = tmp_path / f"smoke_{case_id}.html"
    escaped = html_module.escape(raw)
    _write_section_html(
        html_path,
        section_id=case_id,
        section_body=(
            f'<h2>{section_index} Smoke {case_id}</h2>\n<p class="schg">{escaped}</p>'
        ),
    )
    section = _parse_section(html_path, source_file=f"smoke_{case_id}.html")
    assert section["index"] == section_index

    rules = section.get("rules") or []
    assert rules, case_id
    rows = [
        row
        for rule in rules
        for row in validate_index_rule(
            section,
            rule,
            str(rule.get("rule_id", "")),
            probe_words=_PROBE,
            group_mappings=MINIMAL_GROUP_MAPPINGS,
        )
    ]

    if case_id == "collective-expanded":
        assert rules[0]["stages"] == ["{s₁,s₂,s₃}", "ʃ"]
        assert rules[0]["raw"] == "sₓ → ʃ"

    if case_id == "held-out-parse":
        assert not rows[0].ok
        assert rows[0].failure_class != "format_error"
        assert "no compile steps" not in rows[0].description
        return

    if expect_ok:
        assert all(row.ok for row in rows), (
            f"{case_id}: {rows[0].description if rows else 'no rules'}"
        )
    else:
        assert any(not row.ok for row in rows), case_id
