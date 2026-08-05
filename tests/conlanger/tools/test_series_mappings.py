"""Tests for correspondence-series mapping extraction and lookup."""

from __future__ import annotations

from pathlib import Path

import pytest

from conlanger.tools.series_mappings import (
    SeriesExtractionAudit,
    SeriesMapping,
    apply_series_mappings,
    asca_digit_segment,
    audit_series_extraction,
    classify_subscript_token,
    expand_series_tokens_in_field,
    extract_series_mappings_from_html,
    find_correspondence_series_tokens,
    find_subscript_tokens,
    infer_parallel_rule_mappings,
    infer_singleton_rule_mappings,
    in_scope_series_token,
    is_collective_subscript_token,
    is_correspondence_series_token,
    is_identity_subscript_token,
    is_positional_slot_token,
    load_series_mappings,
    lookup_series_target,
    section_abbreviations_for_index,
    section_index_prefixes,
    survey_all_subscript_tokens_in_html,
    survey_html_defined_series,
    survey_subscript_tokens_in_html,
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

_HTML_CITATION_ONLY = """\
<!doctype html>
<html><body>
<section id="CitationOnly">
<h2>6 Afro-Asiatic</h2>
<p>For these changes, s<sub>1</sub> and s<sub>2</sub> are fricatives.
</section>
</body></html>
"""

_HTML_WITH_GAPS = """\
<!doctype html>
<html><body>
<section id="Parent">
<h2>6 Afro-Asiatic</h2>
<p>s<sub>1</sub> and s<sub>2</sub> are fricatives.
</section>
<section id="Child">
<h2>6.9 Unmapped subsection</h2>
<p class="schg">x<sub>1</sub> → k
<p class="schg">C<sub>1</sub> → C<sub>2</sub>
</section>
<section id="Abbreviations">
<h2>5 Abbreviations</h2>
<p>s<sub>1</sub> is listed here but must not pollute series maps.
</section>
<section id="Malformed">
<p class="schg">s<sub>1</sub> → ʃ
</section>
<section id="EnvRule">
<h2>6.9.1 With environment</h2>
<p class="schg">s<sub>1</sub> → ʃ / _ h<sub>2</sub> | h<sub>1</sub> → ∅
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


def test_series_extraction_audit_empty_counts_report_full_coverage():
    audit = SeriesExtractionAudit(
        csv_rows=0,
        html_defined_pairs=0,
        html_defined_mapped=0,
        in_scope_rule_pairs=0,
        in_scope_rule_mapped=0,
        out_of_scope_rule_pairs=0,
        in_scope_gaps=(),
        family_in_scope={},
    )
    assert audit.html_definition_coverage == 1.0
    assert audit.in_scope_rule_coverage == 1.0


def test_classify_subscript_token_without_subscript():
    assert classify_subscript_token("plain") == "none"


def test_find_correspondence_series_tokens_includes_collective():
    tokens = find_correspondence_series_tokens("sₓ s₁")
    assert tokens == {"sₓ", "s₁"}


def test_find_subscript_tokens_in_rule_fields():
    tokens = find_subscript_tokens("s₁ → ʃ / _ {C₁,V₀}")
    assert tokens == {"s₁", "C₁", "V₀"}


def test_load_series_mappings_missing_columns(tmp_path: Path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("token\ns₁\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing required columns"):
        load_series_mappings(bad_csv)


def test_load_series_mappings_without_optional_columns(tmp_path: Path):
    csv_path = tmp_path / "minimal.csv"
    csv_path.write_text(
        "section_index,token,asca_target\n6,h₁,h1\n",
        encoding="utf-8",
    )
    assert load_series_mappings(csv_path) == [
        SeriesMapping("6", "h₁", "h1", "", ""),
    ]


def test_lookup_series_target_global_fallback():
    rows = [SeriesMapping("*", "h₁", "h1", "global", "Index key default")]
    hit = lookup_series_target("99.1", "h₁", rows)
    assert hit is not None
    assert hit.asca_target == "h1"


def test_infer_singleton_rule_mappings():
    rows = infer_singleton_rule_mappings(
        "h₂ → x",
        section_index="17.2.1",
        source="index.html:100",
    )
    assert rows == [
        SeriesMapping(
            section_index="17.2.1",
            token="h₂",
            asca_target="x",
            source="index.html:100",
            notes="inferred from rule I/O",
        )
    ]


@pytest.mark.parametrize(
    ("rule", "expected_notes"),
    [
        ("not a rule", []),
        ("s₁ s₂ → ʃ", []),
        ("s₁ → s₂", []),
        ("sₓ → ʃ", []),
        ("h₁ h₂ → x y", []),
    ],
)
def test_infer_singleton_rule_mappings_rejects_invalid_rules(rule, expected_notes):
    rows = infer_singleton_rule_mappings(
        rule,
        section_index="6",
        source="index.html:1",
    )
    assert rows == expected_notes


def test_infer_parallel_rule_mappings_skips_brace_input_groups():
    assert (
        infer_parallel_rule_mappings(
            "{s₁,s₂} → ɡ",
            section_index="6.1.2.1",
            source="index.html:1",
        )
        == []
    )


@pytest.mark.parametrize(
    "rule",
    [
        "not a rule",
        "s₁ s₂ → ʃ",
        "s₁ → s₂",
        "C₁ → C₂",
        "s₁ → *ʃ",
        "s₁ → C₁",
        "s₁ → S",
        "s₁ → h₁",
    ],
)
def test_infer_parallel_rule_mappings_rejects_invalid_rules(rule):
    assert (
        infer_parallel_rule_mappings(rule, section_index="6", source="index.html:1")
        == []
    )


def test_write_series_mappings_csv_dedupes_rows(tmp_path: Path):
    csv_path = tmp_path / "series_mappings.csv"
    write_series_mappings_csv(
        [
            SeriesMapping("6", "h₁", "h1", "first", "keep"),
            SeriesMapping("6", "h₁", "ignored", "second", "drop"),
        ],
        csv_path,
    )
    assert load_series_mappings(csv_path) == [
        SeriesMapping("6", "h₁", "h1", "first", "keep"),
    ]


def test_extract_series_mappings_skips_malformed_sections(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_WITH_GAPS, encoding="utf-8")
    rows = extract_series_mappings_from_html(html_path)
    by_key = {(row.section_index, row.token) for row in rows}
    assert ("6", "s₁") in by_key
    assert ("6.9", "x₁") in by_key
    rule_inferred_s1 = [
        row
        for row in rows
        if row.token == "s₁" and row.notes.startswith("inferred")
    ]
    assert len(rule_inferred_s1) == 1
    assert rule_inferred_s1[0].section_index == "6.9.1"


def test_survey_html_defined_series_skips_abbreviations_section(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_WITH_GAPS, encoding="utf-8")
    defined = survey_html_defined_series(html_path)
    assert "5" not in defined
    assert "s₁" in defined["6"]


def test_survey_subscript_tokens_includes_env_and_exception_fields(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_WITH_GAPS, encoding="utf-8")
    by_section = survey_subscript_tokens_in_html(html_path)
    assert by_section["6.9.1"] == {"s₁", "h₂", "h₁"}


def test_survey_all_subscript_tokens_includes_positional_slots(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_WITH_GAPS, encoding="utf-8")
    by_section = survey_all_subscript_tokens_in_html(html_path)
    assert "C₁" in by_section["6.9"]


def test_audit_series_extraction_reports_in_scope_gaps(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_WITH_GAPS, encoding="utf-8")
    csv_path = tmp_path / "series_mappings.csv"
    write_series_mappings_csv(
        [
            SeriesMapping("6", "s₁", "f1", "index.html:1", ""),
            SeriesMapping("6", "s₂", "f2", "index.html:1", ""),
        ],
        csv_path,
    )
    audit = audit_series_extraction(html_path, csv_path)
    assert ("6.9", "x₁") in audit.in_scope_gaps
    assert audit.in_scope_rule_coverage < 1.0


def test_write_coverage_report_documents_gaps_and_out_of_scope(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_WITH_GAPS, encoding="utf-8")
    csv_path = tmp_path / "series_mappings.csv"
    write_series_mappings_csv(
        [
            SeriesMapping("6", "s₁", "f1", "index.html:1", ""),
            SeriesMapping("6", "s₂", "f2", "index.html:1", ""),
        ],
        csv_path,
    )
    report_path = tmp_path / "coverage.md"
    write_coverage_report(html_path, csv_path, report_path)
    text = report_path.read_text(encoding="utf-8")
    assert "`x₁`" in text
    assert "In-scope gaps" in text
    assert "Out-of-scope subscript tokens" in text
    assert "`C₁` (positional)" in text


def test_write_coverage_report_when_no_correspondence_series_rules(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_CITATION_ONLY, encoding="utf-8")
    csv_path = tmp_path / "series_mappings.csv"
    write_series_mappings_csv(extract_series_mappings_from_html(html_path), csv_path)
    report_path = tmp_path / "coverage.md"
    write_coverage_report(html_path, csv_path, report_path)
    text = report_path.read_text(encoding="utf-8")
    assert "_No correspondence-series tokens in rule fields._" in text
    assert "_None._" in text


def test_infer_parallel_rule_mappings_skips_collective_tokens_in_chain():
    rows = infer_parallel_rule_mappings(
        "sₓ s₁ → x ʃ",
        section_index="6.1.2.1",
        source="index.html:1",
    )
    assert rows == [
        SeriesMapping(
            section_index="6.1.2.1",
            token="s₁",
            asca_target="ʃ",
            source="index.html:1",
            notes="inferred from parallel rule I/O",
        ),
    ]


def test_infer_singleton_rule_mappings_accepts_brace_output_group():
    rows = infer_singleton_rule_mappings(
        "s₁ → {ʃ,z}",
        section_index="6.1.2.1",
        source="index.html:1",
    )
    assert rows == [
        SeriesMapping(
            section_index="6.1.2.1",
            token="s₁",
            asca_target="{ʃ,z}",
            source="index.html:1",
            notes="inferred from rule I/O",
        ),
    ]


def test_survey_subscript_tokens_falls_back_to_raw_rule_on_unparseable(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(
        """\
<!doctype html><html><body>
<section id="BadRule">
<h2>6.9.2 Bad rule syntax</h2>
<p class="schg">not a valid rule but s<sub>1</sub> appears
</section>
</body></html>
""",
        encoding="utf-8",
    )
    by_section = survey_subscript_tokens_in_html(html_path)
    assert "s₁" in by_section["6.9.2"]


def test_survey_html_defined_series_reads_inventory_tables(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(
        """\
<!doctype html><html><body>
<section id="TableOnly">
<h2>17 Indo-European</h2>
<p>Intro without indexed tokens.
<table><tr><td>h<sub>3</sub></table>
</section>
</body></html>
""",
        encoding="utf-8",
    )
    defined = survey_html_defined_series(html_path)
    assert defined["17"] == {"h₃"}


def test_extract_series_mappings_ignores_positional_slots_in_citation_and_table(
    tmp_path: Path,
):
    html_path = tmp_path / "index.html"
    html_path.write_text(
        """\
<!doctype html><html><body>
<section id="PositionalOnly">
<h2>10 Austronesian</h2>
<p>C<sub>1</sub> and C<sub>2</sub> are positional slots, not series members.
<table><tr><td>C<sub>1</sub> C<sub>2</sub></table>
</section>
</body></html>
""",
        encoding="utf-8",
    )
    rows = extract_series_mappings_from_html(html_path)
    assert rows == []


def test_audit_series_extraction_counts_html_defined_mappings(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(_HTML_FIXTURE, encoding="utf-8")
    csv_path = tmp_path / "series_mappings.csv"
    write_series_mappings_csv(extract_series_mappings_from_html(html_path), csv_path)
    audit = audit_series_extraction(html_path, csv_path)
    assert audit.html_defined_mapped == audit.html_defined_pairs


def test_collective_subscript_not_created_for_single_member_series(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(
        """\
<!doctype html><html><body>
<section id="SingleMember">
<h2>30 Niger-Congo</h2>
<p>Only d<sub>2</sub> appears in this family citation.
</section>
</body></html>
""",
        encoding="utf-8",
    )
    rows = extract_series_mappings_from_html(html_path)
    assert ("30", "d₂") in {(row.section_index, row.token) for row in rows}
    assert ("30", "dₓ") not in {(row.section_index, row.token) for row in rows}


def test_extract_series_mappings_skips_sections_without_headings(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(
        """\
<!doctype html><html><body>
<section id="NoHeading">
<p class="schg">s<sub>1</sub> → ʃ
</section>
<section id="BadHeading">
<h2>Not a numbered section</h2>
<p class="schg">s<sub>1</sub> → ʃ
</section>
<section id="EmptyParagraph">
<h2>6.8 Empty paragraph</h2>
<p></p>
<p>Only s<sub>1</sub> in the real citation.
</section>
</body></html>
""",
        encoding="utf-8",
    )
    rows = extract_series_mappings_from_html(html_path)
    by_key = {(row.section_index, row.token) for row in rows}
    assert ("6.8", "s₁") in by_key
    assert not any(token == "s₁" and section_index != "6.8" for section_index, token in by_key)


def test_survey_functions_skip_sections_without_headings(tmp_path: Path):
    html_path = tmp_path / "index.html"
    html_path.write_text(
        """\
<!doctype html><html><body>
<section id="NoHeading">
<p class="schg">s<sub>1</sub> → ʃ
</section>
<section id="Listed">
<h2>6.8 Listed</h2>
<p class="schg">s<sub>1</sub> → ʃ
</section>
</body></html>
""",
        encoding="utf-8",
    )
    assert survey_subscript_tokens_in_html(html_path) == {"6.8": {"s₁"}}
    assert survey_all_subscript_tokens_in_html(html_path) == {"6.8": {"s₁"}}


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


def test_expand_series_tokens_in_field_uses_hierarchical_lookup():
    rows = [
        SeriesMapping("6", "s₁", "f1", "index.html:1", ""),
        SeriesMapping("6.1.2.1", "s₁", "ʃ", "index.html:2", "override"),
    ]
    assert expand_series_tokens_in_field("s₁ → x", "6", rows) == "f1 → x"
    assert expand_series_tokens_in_field("s₁ → x", "6.1.2.1", rows) == "ʃ → x"


def test_expand_series_tokens_in_field_expands_collective_and_env():
    rows = [
        SeriesMapping("6", "h₁", "h1", "index.html:1", ""),
        SeriesMapping("6", "h₂", "h2", "index.html:1", ""),
        SeriesMapping("6", "hₓ", "{h1,h2}", "index.html:1", ""),
    ]
    text = "sₓ → ʃ / _ {h₁,h₂}"
    assert expand_series_tokens_in_field(text, "6", rows) == "sₓ → ʃ / _ {h1,h2}"


def test_expand_series_tokens_in_field_leaves_positional_slots():
    rows = [SeriesMapping("10.2.1", "s₁", "f1", "index.html:1", "")]
    text = "C₁ → C₂ / _ s₁"
    assert expand_series_tokens_in_field(text, "10.2.1", rows) == "C₁ → C₂ / _ f1"


def test_apply_series_mappings_on_rule_parts():
    rows = [SeriesMapping("6.1.2.1", "s₁", "ʃ", "index.html:1", "")]
    assert apply_series_mappings(
        {"input": "s₁", "output": "z", "env": "_ h₂"},
        "6.1.2.1",
        rows,
    ) == {"input": "ʃ", "output": "z", "env": "_ h₂"}


def test_section_abbreviations_for_index_more_specific_wins():
    rows = [
        SeriesMapping("6", "s₁", "f1", "index.html:1", ""),
        SeriesMapping("6.1.2.1", "s₁", "ʃ", "index.html:2", ""),
        SeriesMapping("6", "sₓ", "{f1,f2,f3}", "index.html:1", ""),
    ]
    assert section_abbreviations_for_index("6.1.2.1", rows) == {
        "s₁": "ʃ",
        "sₓ": "{f1,f2,f3}",
    }
