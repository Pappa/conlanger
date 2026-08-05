"""Tests for correspondence-series mapping extraction and lookup."""

from __future__ import annotations

from pathlib import Path

import pytest

from conlanger.tools.series_mappings import (
    SeriesMapping,
    asca_digit_segment,
    audit_series_extraction,
    classify_subscript_token,
    extract_series_mappings_from_html,
    find_correspondence_series_tokens,
    infer_parallel_rule_mappings,
    in_scope_series_token,
    is_collective_subscript_token,
    is_correspondence_series_token,
    is_identity_subscript_token,
    is_positional_slot_token,
    load_series_mappings,
    lookup_series_target,
    section_index_prefixes,
    survey_html_defined_series,
    write_coverage_report,
    write_series_mappings_csv,
)

_HTML_FIXTURE = """\
<!doctype html>
<html><body>
<section id="Afro-Asiatic">
<h2>6 Afro-Asiatic</h2>
<p>For these Afro-Asiatic changes, s<sub>1</sub>, s<sub>2</sub>, s<sub>3</sub>,
h<sub>1</sub>, and h<sub>2</sub> are consonants, believed to have most likely been
fricatives, of indeterminate reconstruction.
</section>
<section id="Aari">
<h2>6.1.2.1 South Omotic to Aari</h2>
<p><i>Mecislau</i>
<p class="schg">s<sub>1</sub> s<sub>2</sub> s<sub>3</sub> → ʃ z tʃ
<p class="schg">h<sub>1</sub> → ∅
</section>
<section id="Indo-European">
<h2>17 Indo-European</h2>
<table>
<tr><td>Fricative <td> <td> s <td> <td> <td> h<sub>1</sub> h<sub>2</sub> h<sub>3</sub>
</table>
</section>
<section id="Chamic">
<h2>10.2.1 Proto-Malayo-Polynesian to Proto-Chamic</h2>
<p class="schg">C<sub>1</sub>C<sub>2</sub> → C<sub>2</sub>
</section>
</body></html>
"""


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("s₁", True),
        ("h₂", True),
        ("xₓ", True),
        ("sₓ", True),
        ("C₁", False),
        ("V₀", False),
        ("s", False),
        ("ʃ", False),
    ],
)
def test_is_correspondence_series_token(token, expected):
    assert is_correspondence_series_token(token) is expected


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("C₁", True),
        ("N₂", True),
        ("s₁", False),
    ],
)
def test_is_positional_slot_token(token, expected):
    assert is_positional_slot_token(token) is expected


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("V₀", True),
        ("h₀", True),
        ("s₁", False),
    ],
)
def test_is_identity_subscript_token(token, expected):
    assert is_identity_subscript_token(token) is expected


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("sₓ", True),
        ("hₓ", True),
        ("s₁", False),
    ],
)
def test_is_collective_subscript_token(token, expected):
    assert is_collective_subscript_token(token) is expected


def test_section_index_prefixes_longest_first():
    assert section_index_prefixes("6.1.2.1") == ["6.1.2.1", "6.1.2", "6.1", "6"]


def test_asca_digit_segment_avoids_grouping_letters():
    assert asca_digit_segment("h", "₁") == "h1"
    assert asca_digit_segment("x", "₂") == "x2"
    assert asca_digit_segment("s", "₁") == "f1"


def test_find_correspondence_series_tokens_in_text():
    tokens = find_correspondence_series_tokens("s₁ s₂ → ʃ z / _{h₁,h₂}")
    assert tokens == {"s₁", "s₂", "h₁", "h₂"}


def test_infer_parallel_rule_mappings_from_aari_chain():
    rows = infer_parallel_rule_mappings(
        "s₁ s₂ s₃ → ʃ z tʃ",
        section_index="6.1.2.1",
        source="index_diachronica_original.html:1152",
    )
    assert rows == [
        SeriesMapping(
            section_index="6.1.2.1",
            token="s₁",
            asca_target="ʃ",
            source="index_diachronica_original.html:1152",
            notes="inferred from parallel rule I/O",
        ),
        SeriesMapping(
            section_index="6.1.2.1",
            token="s₂",
            asca_target="z",
            source="index_diachronica_original.html:1152",
            notes="inferred from parallel rule I/O",
        ),
        SeriesMapping(
            section_index="6.1.2.1",
            token="s₃",
            asca_target="tʃ",
            source="index_diachronica_original.html:1152",
            notes="inferred from parallel rule I/O",
        ),
    ]


def test_infer_parallel_rule_mappings_skips_positional_slots():
    assert (
        infer_parallel_rule_mappings(
            "C₁C₂ → C₂",
            section_index="10.2.1",
            source="index_diachronica_original.html:2793",
        )
        == []
    )


def test_lookup_series_target_longest_prefix():
    rows = [
        SeriesMapping("6", "h₁", "h1", "index_diachronica_original.html:933", ""),
        SeriesMapping("6.1.2.1", "s₁", "ʃ", "index_diachronica_original.html:1152", ""),
    ]
    assert lookup_series_target("6.1.2.1", "s₁", rows).asca_target == "ʃ"
    assert lookup_series_target("6.1.2.1", "h₁", rows).asca_target == "h1"
    assert lookup_series_target("6.2", "h₁", rows).asca_target == "h1"
    assert lookup_series_target("6.1.2.1", "s₂", rows) is None


def test_extract_series_mappings_from_html_fixture(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    rows = extract_series_mappings_from_html(html_path)
    by_key = {(r.section_index, r.token): r for r in rows}
    assert ("6", "h₁") in by_key
    assert ("6", "s₁") in by_key
    assert ("17", "h₃") in by_key
    assert by_key[("17", "h₂")].asca_target == "h2"
    assert by_key[("6.1.2.1", "s₁")].asca_target == "ʃ"
    assert ("10.2.1", "C₁") not in by_key


def test_load_series_mappings_round_trip(tmp_path: Path):
    csv_path = tmp_path / "series_mappings.csv"
    write_series_mappings_csv(
        [
            SeriesMapping("6", "h₁", "h1", "index.html:933", "citation"),
            SeriesMapping("6.1.2.1", "s₁", "ʃ", "index.html:1152", "inferred"),
        ],
        csv_path,
    )
    loaded = load_series_mappings(csv_path)
    assert loaded == [
        SeriesMapping("6", "h₁", "h1", "index.html:933", "citation"),
        SeriesMapping("6.1.2.1", "s₁", "ʃ", "index.html:1152", "inferred"),
    ]


def test_write_coverage_report(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    csv_path = tmp_path / "series_mappings.csv"
    rows = extract_series_mappings_from_html(html_path)
    write_series_mappings_csv(rows, csv_path)
    report_path = tmp_path / "coverage.md"
    write_coverage_report(html_path, csv_path, report_path)
    text = report_path.read_text(encoding="utf-8")
    assert "Afro-Asiatic" in text
    assert "Indo-European" in text
    assert "Extraction confidence" in text
    assert "In-scope tokens in rules mapped" in text


@pytest.mark.parametrize(
    ("token", "kind"),
    [
        ("s₁", "correspondence"),
        ("sₓ", "collective"),
        ("C₁", "positional"),
        ("V₀", "identity"),
        ("CV₁", "compound"),
    ],
)
def test_classify_subscript_token(token, kind):
    assert classify_subscript_token(token) == kind


def test_survey_html_defined_series_fixture(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    defined = survey_html_defined_series(html_path)
    assert "s₁" in defined["6"]
    assert "h₃" in defined["17"]


def test_audit_series_extraction_fixture(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    csv_path = tmp_path / "series_mappings.csv"
    write_series_mappings_csv(extract_series_mappings_from_html(html_path), csv_path)
    audit = audit_series_extraction(html_path, csv_path)
    assert audit.html_definition_coverage == 1.0
    assert audit.in_scope_rule_coverage == 1.0
    assert audit.in_scope_gaps == ()


_HTML = Path(__file__).resolve().parents[3] / "data" / "diachronica" / "index_diachronica_original.html"
_CSV = Path(__file__).resolve().parents[3] / "data" / "asca" / "series_mappings.csv"


@pytest.mark.skipif(not _HTML.is_file(), reason="Index HTML fixture missing")
@pytest.mark.skipif(not _CSV.is_file(), reason="series_mappings.csv missing")
def test_extraction_confidence_benchmarks_on_full_html():
    """Regression guard: ticket-28 benchmark families stay largely extracted."""
    audit = audit_series_extraction(_HTML, _CSV)
    assert audit.html_definition_coverage == 1.0
    total_6, mapped_6 = audit.family_in_scope.get("6", (0, 0))
    total_17, mapped_17 = audit.family_in_scope.get("17", (0, 0))
    assert total_6 > 0 and mapped_6 / total_6 >= 0.95
    assert total_17 > 0 and mapped_17 / total_17 >= 0.65
    assert in_scope_series_token("s₁")
    assert not in_scope_series_token("C₁")
