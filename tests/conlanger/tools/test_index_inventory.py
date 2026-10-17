import csv
from pathlib import Path
from unittest.mock import patch

import pytest

from conlanger.appliers.asca import ASCAValidationError
from conlanger.compile.models.rules import SoundChangeRule
from conlanger.tools.index_inventory import (
    CHANGELOG_CSV_COLUMNS,
    OK_FALSE,
    OK_SKIPPED,
    OK_TRUE,
    RULE_SKIPPED_FAILURE_CLASS,
    SECTION_SKIPPED_FAILURE_CLASS,
    FieldIsolationRow,
    IndexRuleInventoryBundle,
    ValidationRow,
    _coerce_ok_value,
    append_ok_flip_changelog,
    build_field_isolation_row,
    bundles_for_row_prefix,
    classify_error,
    corrections_outcome_stats,
    count_field_blame_categories,
    derive_blame,
    field_isolation_rows_for_validation_rows,
    field_isolation_rows_to_dataframe,
    filter_field_isolation_error,
    filter_field_isolation_skipped,
    filter_field_isolation_success,
    filter_inventory_by_ok,
    filter_inventory_skipped,
    iter_compiled_inventory_bundles,
    iter_index_compile_bundles,
    iter_index_rule_inventory_bundles,
    load_inventory_csv,
    matched_correction_rule_ids,
    ok_flip_changelog_rows,
    parse_error_description,
    parse_unknown_token_error,
    section_all_ok_stats,
    section_outcome_stats,
    summarize_inventory,
    top_error_descriptions_from_dataframe,
    top_error_tokens,
    top_error_tokens_with_suggested_from_dataframe,
    validate_index_rule_with_targets,
    validation_rows_to_dataframe,
    write_field_isolation_csvs,
    write_filtered_inventory_csvs,
    write_ok_flip_changelog,
    write_validation_csv,
)
from conlanger.tools.inventory_targets import (
    _series_for_alternative,
    resolve_inventory_targets,
)
from tests.conftest import ASCA_VALIDATE_INSTALLED

_SECTION = {"index": "1.0", "section": "Test Section"}


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        ("", ""),
        ("nested brackets in rule", "nested_brackets"),
        ("Unknown feature foo", "unknown_feature"),
        ("Unknown grouping X", "unknown_grouping"),
        ("Expected '>' but got foo", "prose_or_expected_arrow"),
        ("Expected '_'", "expected_underscore"),
        ("after the end of a word", "stuff_after_word_bound"),
        ("prerequisite properties for diacritic", "diacritic_prereq"),
        ("Input is empty", "empty_io_panic"),
        ("Can't delete a word's only segment", "runtime_delete_only_segment"),
        ("Expected number", "expected_number"),
        ("Unknown reference '3'", "unknown_reference"),
        (
            "Expected an IPA character, Primative or Matrix, but received '('",
            "expected_ipa",
        ),
        ("Expected '..', but received .'ʃ'", "expected_range_dots"),
        ("forget a '/' between the output and environment", "missing_slash_output_env"),
        ("Floating diacritic", "floating_diacritic"),
        (
            "Cannot have multiple underlines in an environment",
            "multiple_underlines_env",
        ),
        ("before the beginning of a word", "segments_before_word"),
        ("An incomplete matrix cannot be inserted", "incomplete_matrix"),
        ("Unknown character x", "unknown_character"),
        ("Malformed Comment: bad", "malformed_comment"),
        ("missing separator '→'", "missing_arrow"),
        ("format_error: input is required", "format_error"),
        ("Syntax Error: something else", "syntax_other"),
        ("Runtime Error: boom", "runtime_other"),
        ("the compiler panicked", "panic_other"),
        ("something entirely different", "other"),
    ],
)
def test_classify_error(error, expected):
    assert classify_error(error) == expected


@pytest.mark.parametrize(
    ("error", "expected_token", "expected_suggested", "expected"),
    [
        ("", "", "", ""),
        (
            "Syntax Error: Unknown character '₁' | dz ʃ tʃ > ʒ s₁ s₂",
            "₁",
            "",
            "",
        ),
        (
            "Syntax Error: Unknown grouping 'Z'. Known groupings are (C)onsonant",
            "Z",
            "",
            "",
        ),
        (
            "Syntax Error: Unknown feature 'voiced'. Did you mean voice? | e > i",
            "voiced",
            "voice",
            "",
        ),
        (
            "Syntax Error: Expected '_', but received '' | p > x",
            "",
            "",
            "_",
        ),
        (
            "Syntax Error: Expected number, but received ɡ | CVʕ > ħʔ",
            "ɡ",
            "",
            "number",
        ),
        (
            "Syntax Error: Expected an IPA character, Primative or Matrix, but received '(' | a > b",
            "(",
            "",
            "IPA character",
        ),
        (
            "Syntax Error: Expected '..', but received .'ʃ' | ttʃ > t.ʃ",
            "ʃ",
            "",
            "..",
        ),
        (
            "Syntax Error: Expected '_'",
            "",
            "",
            "",
        ),
    ],
)
def test_parse_unknown_token_error(error, expected_token, expected_suggested, expected):
    assert parse_unknown_token_error(error) == (
        expected_token,
        expected_suggested,
        expected,
    )


def test_validation_row_as_csv_dict():
    row = ValidationRow(
        section_index="1.0",
        section_name="Test",
        rule_id="Test-2",
        source="sample.html:10",
        ok=OK_FALSE,
        failure_class="syntax_other",
        error_token="",
        suggested="",
        description="Syntax Error: …",
    )
    assert row.as_csv_dict() == {
        "section_index": "1.0",
        "section_name": "Test",
        "rule_id": "Test-2",
        "alt_idx": "",
        "step_idx": "",
        "source": "sample.html:10",
        "ok": OK_FALSE,
        "rule": "",
        "failure_class": "syntax_other",
        "error_token": "",
        "suggested": "",
        "expected": "",
        "description": "Syntax Error: …",
    }


def test_series_for_alternative_wraps_compiled_rule_without_reparse():
    """Ticket 99: inventory alternatives reuse compiled peers, not index stages."""
    alternative = SoundChangeRule(
        input="d", output="∅", env="V_V", detect_alternatives=False
    )
    series = _series_for_alternative(_SECTION, {}, "r0", alternative, None)
    rule_parts = [part for part in series.parts if isinstance(part, SoundChangeRule)]
    assert len(rule_parts) == 1
    assert rule_parts[0] is alternative
    assert str(series).endswith("d > ∅ / V_V\n")


def test_ok_flip_changelog_rows_keys_on_source_and_alt_idx():
    previous = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "file:1", OK_TRUE, alt_idx=0),
            ValidationRow("1", "A", "r0", "file:1", OK_TRUE, alt_idx=1),
        ]
    )
    # alt_idx 0 unchanged; alt_idx 1 flips to failing under the same source
    current = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "file:1", OK_TRUE, alt_idx=0),
            ValidationRow(
                "1",
                "A",
                "r0",
                "file:1",
                OK_FALSE,
                failure_class="syntax_other",
                description="err",
                alt_idx=1,
            ),
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-08-12T00:00:00Z")
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS
    assert list(flips["source"]) == ["file:1"]
    assert list(flips["alt_idx"]) == ["1"]
    assert list(flips["ok"]) == [OK_FALSE]


def test_write_validation_csv(tmp_path: Path):
    rows = [
        ValidationRow(
            section_index="1.0",
            section_name="A",
            rule_id="r0",
            source="s:1",
            ok=OK_TRUE,
            failure_class="",
            error_token="",
            suggested="",
            description="",
        ),
        ValidationRow(
            section_index="1.0",
            section_name="A",
            rule_id="r1",
            source="s:2",
            ok=OK_FALSE,
            failure_class="unknown_feature",
            error_token="voiced",
            suggested="voice",
            description="Syntax Error: Unknown feature 'voiced'. Did you mean voice?",
        ),
    ]
    out = tmp_path / "nested" / "inventory.csv"
    write_validation_csv(rows, out)
    with out.open(encoding="utf-8") as handle:
        parsed = list(csv.DictReader(handle))
    assert parsed[0]["ok"] == "OK"
    assert parsed[0]["section_index"] == "1.0"
    assert parsed[1]["error_token"] == "voiced"
    assert parsed[1]["suggested"] == "voice"
    assert list(parsed[0].keys())[-1] == "description"


def test_top_error_tokens():
    rows = [
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=0,
            source="s:1",
            ok=OK_FALSE,
            failure_class="unknown_character",
            error_token="→",
            suggested="",
            description="err",
        ),
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=1,
            source="s:2",
            ok=OK_FALSE,
            failure_class="unknown_character",
            error_token="→",
            suggested="",
            description="err",
        ),
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=2,
            source="s:3",
            ok=OK_FALSE,
            failure_class="unknown_character",
            error_token="ː",
            suggested="",
            description="err",
        ),
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=3,
            source="s:4",
            ok=OK_FALSE,
            failure_class="unknown_feature",
            error_token="voiced",
            suggested="voice",
            description="err",
        ),
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=4,
            source="s:5",
            ok=OK_FALSE,
            failure_class="unknown_feature",
            error_token="voiced",
            suggested="voice",
            description="err",
        ),
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=5,
            source="s:6",
            ok=OK_FALSE,
            failure_class="unknown_feature",
            error_token="sibilant",
            suggested="sonorant",
            description="err",
        ),
    ]
    assert top_error_tokens(rows, "unknown_character") == [("→", 2), ("ː", 1)]
    assert top_error_tokens(rows, "unknown_feature") == [("voiced", 2), ("sibilant", 1)]
    assert top_error_tokens(rows, "unknown_grouping") == []


def test_top_error_tokens_with_suggested_from_dataframe():
    df = validation_rows_to_dataframe(
        [
            ValidationRow(
                section_index="1",
                section_name="A",
                rule_id=0,
                source="s:1",
                ok=OK_FALSE,
                failure_class="unknown_feature",
                error_token="voiced",
                suggested="voice",
                description="err",
            ),
            ValidationRow(
                section_index="1",
                section_name="A",
                rule_id=1,
                source="s:2",
                ok=OK_FALSE,
                failure_class="unknown_feature",
                error_token="voiced",
                suggested="voice",
                description="err",
            ),
            ValidationRow(
                section_index="1",
                section_name="A",
                rule_id=2,
                source="s:3",
                ok=OK_FALSE,
                failure_class="unknown_feature",
                error_token="sibilant",
                suggested="sonorant",
                description="err",
            ),
        ]
    )
    assert top_error_tokens_with_suggested_from_dataframe(df, "unknown_feature") == [
        ("voiced", 2, "voice"),
        ("sibilant", 1, "sonorant"),
    ]


def test_top_error_tokens_with_suggested_uses_modal_suggestion():
    df = validation_rows_to_dataframe(
        [
            ValidationRow(
                section_index="1",
                section_name="A",
                rule_id=0,
                source="s:1",
                ok=OK_FALSE,
                failure_class="unknown_feature",
                error_token="voiced",
                suggested="voice",
                description="err",
            ),
            ValidationRow(
                section_index="1",
                section_name="A",
                rule_id=1,
                source="s:2",
                ok=OK_FALSE,
                failure_class="unknown_feature",
                error_token="voiced",
                suggested="voice",
                description="err",
            ),
            ValidationRow(
                section_index="1",
                section_name="A",
                rule_id=2,
                source="s:3",
                ok=OK_FALSE,
                failure_class="unknown_feature",
                error_token="voiced",
                suggested="voice",
                description="err",
            ),
        ]
    )
    assert top_error_tokens_with_suggested_from_dataframe(df, "unknown_feature") == [
        ("voiced", 3, "voice"),
    ]


def test_top_error_descriptions_from_dataframe():
    df = validation_rows_to_dataframe(
        [
            ValidationRow(
                section_index="1",
                section_name="A",
                rule_id="r0",
                source="s:1",
                ok=OK_FALSE,
                failure_class="syntax_other",
                error_token="",
                suggested="",
                description="Syntax Error: Floating diacritic | a > b",
            ),
            ValidationRow(
                section_index="1",
                section_name="A",
                rule_id="r1",
                source="s:2",
                ok=OK_FALSE,
                failure_class="syntax_other",
                error_token="",
                suggested="",
                description="Runtime Error: Floating diacritic | c > d",
            ),
            ValidationRow(
                section_index="1",
                section_name="A",
                rule_id="r2",
                source="s:3",
                ok=OK_FALSE,
                failure_class="syntax_other",
                error_token="",
                suggested="",
                description="Syntax Error: Floating diacritic | e > f",
            ),
        ]
    )
    assert top_error_descriptions_from_dataframe(df, "syntax_other") == [
        ("Floating diacritic", 3),
    ]


@pytest.mark.parametrize(
    ("error", "failure_class", "expected"),
    [
        (
            "thread 'main' panicked at src/foo.rs",
            "panic_other",
            "thread panicked at src/foo.rs",
        ),
        ("Syntax Error: bad token", "syntax_other", "Syntax Error: bad token"),
    ],
)
def test_parse_error_description(error, failure_class, expected):
    assert parse_error_description(error, failure_class) == expected


def test_top_error_tokens_unlimited():
    rows = [
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=index,
            source=f"s:{index}",
            ok=OK_FALSE,
            failure_class="unknown_grouping",
            error_token=token,
            description="err",
        )
        for index, token in enumerate(("R", "E", "U", "H", "B", "X"))
    ]
    assert top_error_tokens(rows, "unknown_grouping", limit=5) == [
        ("R", 1),
        ("E", 1),
        ("U", 1),
        ("H", 1),
        ("B", 1),
    ]
    assert len(top_error_tokens(rows, "unknown_grouping", limit=None)) == 6


def test_section_outcome_stats():
    validation_rows = [
        ("1", "A", "r0", "s:1", OK_TRUE, ""),
        ("1", "A", "r1", "s:2", OK_TRUE, ""),
        ("2", "B", "r0", "s:3", OK_TRUE, ""),
        ("2", "B", 1, "s:4", OK_FALSE, "syntax_other"),
        ("3", "C", 0, "s:5", OK_FALSE, "syntax_other"),
        (
            "9.9.9",
            "Skipped",
            "r0",
            "s:6",
            OK_SKIPPED,
            SECTION_SKIPPED_FAILURE_CLASS,
        ),
    ]
    rows = [
        ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_id=rule_id,
            source=source,
            ok=ok,
            failure_class=failure_class,
        )
        for (
            section_index,
            section_name,
            rule_id,
            source,
            ok,
            failure_class,
        ) in validation_rows
    ]
    outcomes = section_outcome_stats(rows)
    assert outcomes.total == 4
    assert outcomes.all_ok == 1
    assert outcomes.some_ok == 1
    assert outcomes.none_ok == 1
    assert outcomes.skipped == 1


def test_section_outcome_stats_empty():
    outcomes = section_outcome_stats([])
    assert outcomes.total == 0
    assert outcomes.all_ok == 0
    assert outcomes.some_ok == 0
    assert outcomes.none_ok == 0
    assert outcomes.skipped == 0


def test_section_all_ok_stats():
    rows = [
        ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", ""),
        ValidationRow("1", "A", "r1", "s:2", OK_TRUE, "", "", "", "", ""),
        ValidationRow("2", "B", "r0", "s:3", OK_TRUE, "", "", "", "", ""),
        ValidationRow("2", "B", 1, "s:4", OK_FALSE, "syntax_other", "", "", ""),
        ValidationRow("3", "C", 0, "s:5", OK_FALSE, "syntax_other", "", "", ""),
    ]
    assert section_all_ok_stats(rows) == (1, 3, 100.0 / 3)


def test_section_all_ok_stats_empty():
    assert section_all_ok_stats([]) == (0, 0, 0.0)


def test_summarize_inventory_common_errors():
    validation_rows = [
        ("1", "A", 0, "s:1", OK_FALSE, "unknown_character", "→", ""),
        ("1", "A", 1, "s:2", OK_FALSE, "unknown_feature", "voiced", "voice"),
    ]
    rows = [
        ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_id=rule_id,
            source=source,
            ok=ok,
            failure_class=failure_class,
            error_token=error_token,
            suggested=suggested,
        )
        for (
            section_index,
            section_name,
            rule_id,
            source,
            ok,
            failure_class,
            error_token,
            suggested,
        ) in validation_rows
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
    )
    assert "## Common Errors" in text
    assert "### unknown_character (error_token)" in text
    assert "| 1 | `→` |" in text
    assert "### unknown_feature (error_token)" in text
    assert "| 1 | `voiced` | `voice` |" in text
    assert "### unknown_grouping (error_token)" in text
    assert "| — | _(none)_ |" in text
    assert text.index("## Failure classes") < text.index("## Common Errors")
    assert text.index("## Common Errors") < text.index("## Notes")


def test_summarize_inventory():
    validation_rows = [
        ("1", "A", 0, "s:1", OK_TRUE, ""),
        ("1", "A", 1, "s:2", OK_FALSE, "syntax_other"),
        ("1", "A", 2, "s:3", OK_FALSE, "syntax_other"),
    ]
    rows = [
        ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_id=rule_id,
            source=source,
            ok=ok,
            failure_class=failure_class,
        )
        for (
            section_index,
            section_name,
            rule_id,
            source,
            ok,
            failure_class,
        ) in validation_rows
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        asca_version="0.10.x",
    )
    assert "Rows: **3**" in text
    assert "## Rules" in text
    assert "OK: **1** (33.3%)" in text
    assert "Fail: **2** (66.7%)" in text
    assert "Skipped: **0** (0.0%)" in text
    assert "## Sections" in text
    assert "All OK: **0 / 1** (0.0%)" in text
    assert "Some OK: **1 / 1** (100.0%)" in text
    assert "None OK: **0 / 1** (0.0%)" in text
    assert "Sections skipped: **0 / 1** (0.0%)" in text
    assert "| 2 | `syntax_other` |" in text
    assert "## Common Errors" in text
    assert "rule-inventory-success.csv" in text
    assert "rule-inventory-error.csv" in text
    assert "rule-inventory-skipped.csv" in text
    assert "rule-inventory-changelog.csv" in text
    assert "rule-inventory.csv" not in text
    assert "syntax_other_errors.csv" in text
    assert "runtime_other_errors.csv" in text
    assert "unknown_character_errors.csv" in text
    assert "unknown_grouping_errors.csv" in text
    assert "expected_underscore_errors.csv" in text
    assert "nested_brackets_errors.csv" in text
    assert "unknown_features_errors.csv" in text
    assert "expected_number_errors.csv" in text
    assert "prose_or_expected_arrow_errors.csv" in text
    assert "expected_ipa_errors.csv" in text
    assert "unknown_reference_errors.csv" in text


def test_summarize_inventory_empty():
    text = summarize_inventory(
        [],
        source_yaml="out.yml",
        probe_words="probe.wsca",
    )
    assert "Rows: **0**" in text
    assert "OK: **0** (0.0%)" in text
    assert "Skipped: **0** (0.0%)" in text
    assert "All OK: **0 / 0** (0.0%)" in text
    assert "Some OK: **0 / 0** (0.0%)" in text
    assert "None OK: **0 / 0** (0.0%)" in text
    assert "Sections skipped: **0 / 0** (0.0%)" in text
    assert "### unknown_character (error_token)" in text
    assert "| — | _(none)_ |" in text


def test_summarize_inventory_section_skipped():
    validation_rows = [
        (
            "9.9.9",
            "Skipped",
            "r0",
            "s:1",
            OK_SKIPPED,
            SECTION_SKIPPED_FAILURE_CLASS,
        ),
        ("1", "A", "r0", "s:2", OK_TRUE, ""),
        ("1", "A", 1, "s:3", OK_FALSE, "syntax_other"),
    ]
    rows = [
        ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_id=rule_id,
            source=source,
            ok=ok,
            failure_class=failure_class,
        )
        for (
            section_index,
            section_name,
            rule_id,
            source,
            ok,
            failure_class,
        ) in validation_rows
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
    )
    assert "Rows: **3**" in text
    assert "OK: **1** (33.3%)" in text
    assert "Fail: **1** (33.3%)" in text
    assert "Skipped: **1** (33.3%)" in text
    assert "All OK: **0 / 2** (0.0%)" in text
    assert "Some OK: **1 / 2** (50.0%)" in text
    assert "None OK: **0 / 2** (0.0%)" in text
    assert "Sections skipped: **1 / 2** (50.0%)" in text


def test_filter_inventory_by_ok_splits_success_and_error():
    rows = [
        ValidationRow("1", "A", "r0", "file:1", OK_TRUE, "", "", "", "", ""),
        ValidationRow(
            "1",
            "A",
            1,
            "file:2",
            OK_FALSE,
            "syntax_other",
            "",
            "",
            "err",
        ),
        ValidationRow("1", "A", "r2", "file:3", OK_TRUE, "", "", "", "", ""),
        ValidationRow(
            "9.9.9",
            "Skipped",
            "r3",
            "file:4",
            OK_SKIPPED,
            SECTION_SKIPPED_FAILURE_CLASS,
            "",
            "",
            "",
            "section skipped",
        ),
        ValidationRow(
            "1",
            "A",
            "r4",
            "file:5",
            OK_SKIPPED,
            RULE_SKIPPED_FAILURE_CLASS,
            "",
            "",
            "",
            "held-out (commented rule)",
        ),
    ]
    df = validation_rows_to_dataframe(rows)
    success = filter_inventory_by_ok(df, ok=True)
    error = filter_inventory_by_ok(df, ok=False)
    skipped = filter_inventory_skipped(df)
    assert list(success["source"]) == ["file:1", "file:3"]
    assert list(error["source"]) == ["file:2"]
    assert set(skipped["source"]) == {"file:4", "file:5"}
    assert list(success.columns) == list(df.columns)
    assert list(error.columns) == list(df.columns)
    assert list(skipped.columns) == list(df.columns)


def test_ok_flip_changelog_rows_emits_flips_by_source():
    previous = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "file:1", OK_TRUE, "", "", "", "", ""),
            ValidationRow(
                "1",
                "A",
                1,
                "file:2",
                OK_FALSE,
                "syntax_other",
                "",
                "",
                "err",
            ),
            ValidationRow("1", "A", "r2", "file:3", OK_TRUE, "", "", "", "", ""),
        ]
    )
    # rule_id changed; file:3 ok unchanged; file:1 and file:2 flip
    current = validation_rows_to_dataframe(
        [
            ValidationRow(
                "1",
                "A",
                "r5",
                "file:1",
                OK_FALSE,
                "syntax_other",
                "",
                "",
                "err",
            ),
            ValidationRow("1", "A", "r6", "file:2", OK_TRUE, "", "", "", "", ""),
            ValidationRow("1", "A", "r7", "file:3", OK_TRUE, "", "", "", "", ""),
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-08-06T12:00:00Z")
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS
    assert list(flips["source"]) == ["file:1", "file:2"]
    assert list(flips["ok"]) == [OK_FALSE, OK_TRUE]
    assert list(flips["rule_id"]) == ["r5", "r6"]
    assert list(flips["timestamp"]) == [
        "2026-08-06T12:00:00Z",
        "2026-08-06T12:00:00Z",
    ]


def test_ok_flip_changelog_rows_tolerates_previous_without_alt_idx():
    # Inventories written before ticket 66 have no ``alt_idx`` column.
    previous = validation_rows_to_dataframe(
        [ValidationRow("1", "A", "r0", "file:1", OK_TRUE, "", "", "", "", "")]
    ).drop(columns=["alt_idx"])
    current = validation_rows_to_dataframe(
        [
            ValidationRow(
                "1",
                "A",
                0,
                "file:1",
                OK_FALSE,
                "syntax_other",
                "",
                "",
                "err",
            )
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-08-12T00:00:00Z")
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS
    assert list(flips["source"]) == ["file:1"]
    assert list(flips["ok"]) == [OK_FALSE]


def test_ok_flip_changelog_rows_empty_when_ok_unchanged():
    df = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "file:1", OK_TRUE, "", "", "", "", ""),
            ValidationRow(
                "1",
                "A",
                1,
                "file:2",
                OK_FALSE,
                "syntax_other",
                "",
                "",
                "err",
            ),
        ]
    )
    flips = ok_flip_changelog_rows(df, df, timestamp="2026-08-06T12:00:00Z")
    assert flips.empty
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS


def test_ok_flip_changelog_rows_empty_without_previous_inventory():
    current = validation_rows_to_dataframe(
        [ValidationRow("1", "A", "r0", "file:1", OK_TRUE, "", "", "", "", "")]
    )
    flips = ok_flip_changelog_rows(None, current, timestamp="2026-08-06T12:00:00Z")
    assert flips.empty
    assert list(flips.columns) == CHANGELOG_CSV_COLUMNS


def test_load_inventory_csv_returns_none_when_missing(tmp_path: Path):
    assert load_inventory_csv(tmp_path) is None


def test_load_inventory_csv_reads_success_error_and_skipped_splits(tmp_path: Path):
    write_filtered_inventory_csvs(
        validation_rows_to_dataframe(
            [
                ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", ""),
                ValidationRow(
                    "1",
                    "A",
                    1,
                    "s:2",
                    OK_FALSE,
                    "syntax_other",
                    "",
                    "",
                    "err",
                ),
                ValidationRow(
                    "9.9.9",
                    "Skipped",
                    "r2",
                    "s:3",
                    OK_SKIPPED,
                    SECTION_SKIPPED_FAILURE_CLASS,
                    "",
                    "",
                    "",
                    "section skipped",
                ),
            ]
        ),
        tmp_path,
    )
    loaded = load_inventory_csv(tmp_path)
    assert loaded is not None
    assert len(loaded) == 3
    assert set(loaded["source"]) == {"s:1", "s:2", "s:3"}


def test_write_filtered_inventory_csvs(tmp_path: Path):
    df = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", ""),
            ValidationRow(
                "1",
                "A",
                1,
                "s:2",
                OK_FALSE,
                "syntax_other",
                "",
                "",
                "err",
            ),
            ValidationRow(
                "1",
                "A",
                "r2",
                "s:3",
                OK_SKIPPED,
                RULE_SKIPPED_FAILURE_CLASS,
                "",
                "",
                "",
                "held-out (commented rule)",
            ),
        ]
    )
    write_filtered_inventory_csvs(df, tmp_path)
    success = tmp_path / "rule-inventory-success.csv"
    error = tmp_path / "rule-inventory-error.csv"
    skipped = tmp_path / "rule-inventory-skipped.csv"
    assert success.is_file()
    assert error.is_file()
    assert skipped.is_file()
    assert len(list(csv.DictReader(success.open()))) == 1
    assert len(list(csv.DictReader(error.open()))) == 1
    skipped_rows = list(csv.DictReader(skipped.open()))
    assert len(skipped_rows) == 1
    assert skipped_rows[0]["ok"] == OK_SKIPPED


def test_write_ok_flip_changelog_reset_empty_writes_header_only(tmp_path: Path):
    path = tmp_path / "changelog.csv"
    path.write_text("old,data\n", encoding="utf-8")
    assert (
        write_ok_flip_changelog(
            ok_flip_changelog_rows(
                validation_rows_to_dataframe(
                    [ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", "")]
                ),
                validation_rows_to_dataframe(
                    [ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", "")]
                ),
                timestamp="2026-09-10T00:00:00Z",
            ),
            path,
            reset=True,
        )
        == 0
    )
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert rows == []
    with path.open(encoding="utf-8") as handle:
        header = handle.readline().strip()
    assert header == ",".join(CHANGELOG_CSV_COLUMNS)


def test_write_ok_flip_changelog_reset_with_flips_overwrites(tmp_path: Path):
    path = tmp_path / "changelog.csv"
    path.write_text("old,data\n", encoding="utf-8")
    flips = ok_flip_changelog_rows(
        validation_rows_to_dataframe(
            [ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", "")]
        ),
        validation_rows_to_dataframe(
            [
                ValidationRow(
                    "1",
                    "A",
                    "r0",
                    "s:1",
                    OK_FALSE,
                    "syntax_other",
                    "",
                    "",
                    "err",
                )
            ],
        ),
        timestamp="2026-09-10T12:00:00Z",
    )
    assert write_ok_flip_changelog(flips, path, reset=True) == 1
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    assert len(rows) == 1
    assert rows[0]["source"] == "s:1"
    assert rows[0]["ok"] == OK_FALSE


def test_write_ok_flip_changelog_append_empty_leaves_existing_file(tmp_path: Path):
    path = tmp_path / "changelog.csv"
    path.write_text(
        "section_index,rule_id,alt_idx,step_idx,source,ok,timestamp\n"
        "1,r0,,,s:1,1,old\n",
        encoding="utf-8",
    )
    assert (
        write_ok_flip_changelog(
            ok_flip_changelog_rows(
                validation_rows_to_dataframe(
                    [ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", "")]
                ),
                validation_rows_to_dataframe(
                    [ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", "")]
                ),
                timestamp="2026-09-10T00:00:00Z",
            ),
            path,
            reset=False,
        )
        == 0
    )
    assert "old" in path.read_text(encoding="utf-8")


def test_matched_correction_rule_ids_excludes_orphans():
    rows = [
        ValidationRow("1", "A", "matched-a", "s:1", OK_TRUE, "", "", "", "", ""),
        ValidationRow(
            "1", "A", "matched-b", "s:2", OK_FALSE, "syntax_other", "", "", "err"
        ),
    ]
    matched = matched_correction_rule_ids(
        rows,
        {
            "matched-a": "a > b",
            "matched-b": "c > d",
            "orphan": "x > y",
        },
    )
    assert matched == frozenset({"matched-a", "matched-b"})


def test_corrections_outcome_stats_rollup_per_rule():
    validation_rows = [
        ("1", "A", "r-multi", "s:1", OK_TRUE, "", 0),
        ("1", "A", "r-multi", "s:1", OK_TRUE, "", 1),
        ("1", "A", "r-fail", "s:2", OK_FALSE, "expected_underscore", None),
        ("1", "A", "r-mixed", "s:3", OK_TRUE, "", None),
        ("1", "A", "r-mixed", "s:3", OK_SKIPPED, RULE_SKIPPED_FAILURE_CLASS, None),
        ("1", "A", "r-skipped", "s:4", OK_SKIPPED, RULE_SKIPPED_FAILURE_CLASS, None),
    ]
    rows = [
        ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_id=rule_id,
            source=source,
            ok=ok,
            failure_class=failure_class,
            alt_idx=alt_idx,
        )
        for (
            section_index,
            section_name,
            rule_id,
            source,
            ok,
            failure_class,
            alt_idx,
        ) in validation_rows
    ]
    stats = corrections_outcome_stats(
        rows,
        frozenset({"r-multi", "r-fail", "r-mixed", "r-skipped", "orphan"}),
    )
    assert stats is not None
    assert stats.total == 4
    assert stats.ok == 2
    assert stats.fail == 1
    assert stats.skipped == 1
    assert stats.failed_rules == (("r-fail", "expected_underscore"),)
    assert stats.skipped_rules == (("r-skipped", RULE_SKIPPED_FAILURE_CLASS),)


def test_corrections_outcome_stats_modal_failure_class_on_tie():
    validation_rows = [
        ("expected_underscore", 0),
        ("syntax_other", 1),
    ]
    rows = [
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id="r-fail",
            source="s:1",
            ok=OK_FALSE,
            failure_class=failure_class,
            alt_idx=alt_idx,
        )
        for (
            failure_class,
            alt_idx,
        ) in validation_rows
    ]
    stats = corrections_outcome_stats(rows, frozenset({"r-fail"}))
    assert stats.failed_rules == (("r-fail", "expected_underscore"),)


def test_summarize_inventory_corrections_section():
    validation_rows = [
        ("r-ok", "s:1", OK_TRUE, ""),
        ("r-fail", "s:2", OK_FALSE, "expected_underscore"),
        ("r-skipped", "s:3", OK_SKIPPED, "rule_skipped"),
    ]
    rows = [
        ValidationRow(
            section_index="1",
            section_name="A",
            rule_id=rule_id,
            source=source,
            ok=ok,
            failure_class=failure_class,
        )
        for (
            rule_id,
            source,
            ok,
            failure_class,
        ) in validation_rows
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        correction_rule_ids=frozenset({"r-ok", "r-fail", "r-skipped"}),
    )
    assert text.index("## Rules") < text.index("## Corrections")
    assert text.index("## Corrections") < text.index("## Sections")
    assert text.index("## Corrections") < text.index("## Failure classes")
    assert "OK: **1/3**" in text
    assert "Fail: **1/3**" in text
    assert "Skipped: **1/3**" in text
    assert "### Failed corrections" in text
    assert "- `r-fail` — `expected_underscore`" in text
    assert "### Skipped corrections" in text
    assert f"- `r-skipped` — `{RULE_SKIPPED_FAILURE_CLASS}`" in text


def test_summarize_inventory_corrections_section_skipped_only():
    validation_rows = [
        (
            "9.9.9",
            "Skipped",
            "Early-Icelandic-bbc",
            "s:1",
            OK_SKIPPED,
            SECTION_SKIPPED_FAILURE_CLASS,
        ),
        (
            "1",
            "A",
            "Early-Icelandic-xxy",
            "s:2",
            OK_SKIPPED,
            RULE_SKIPPED_FAILURE_CLASS,
        ),
    ]
    rows = [
        ValidationRow(
            section_index=section_index,
            section_name=section_name,
            rule_id=rule_id,
            source=source,
            ok=ok,
            failure_class=failure_class,
        )
        for (
            section_index,
            section_name,
            rule_id,
            source,
            ok,
            failure_class,
        ) in validation_rows
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        correction_rule_ids=frozenset({"Early-Icelandic-bbc", "Early-Icelandic-xxy"}),
    )
    assert "Skipped: **2/2**" in text
    assert "### Failed corrections" not in text
    assert "### Skipped corrections" in text
    assert f"- `Early-Icelandic-xxy` — `{RULE_SKIPPED_FAILURE_CLASS}`" in text
    assert f"- `Early-Icelandic-bbc` — `{SECTION_SKIPPED_FAILURE_CLASS}`" in text


def test_summarize_inventory_corrections_omits_fail_list_when_all_ok():
    rows = [
        ValidationRow("1", "A", "r-ok", "s:1", OK_TRUE, "", "", "", "", ""),
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        correction_rule_ids=frozenset({"r-ok"}),
    )
    assert "## Corrections" in text
    assert "OK: **1/1**" in text
    assert "Fail:" not in text.split("## Corrections")[1].split("## Sections")[0]
    assert "### Failed corrections" not in text


def test_summarize_inventory_corrections_omits_skipped_list_when_none_skipped():
    rows = [
        ValidationRow("1", "A", "r-ok", "s:1", OK_TRUE, "", "", "", "", ""),
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        correction_rule_ids=frozenset({"r-ok"}),
    )
    assert "## Corrections" in text
    assert "### Skipped corrections" not in text


def test_summarize_inventory_omits_corrections_without_matches():
    rows = [
        ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", ""),
    ]
    text = summarize_inventory(
        rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        correction_rule_ids=frozenset({"orphan-only"}),
    )
    assert "## Corrections" not in text


def test_append_ok_flip_changelog_writes_and_appends(tmp_path: Path):
    flips = ok_flip_changelog_rows(
        None,
        validation_rows_to_dataframe(
            [ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", "")]
        ),
        timestamp="2026-08-06T12:00:00Z",
    )
    path = tmp_path / "changelog.csv"
    assert append_ok_flip_changelog(flips, path) == 0

    flips = ok_flip_changelog_rows(
        validation_rows_to_dataframe(
            [ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", "")]
        ),
        validation_rows_to_dataframe(
            [
                ValidationRow(
                    "1",
                    "A",
                    0,
                    "s:1",
                    OK_FALSE,
                    "syntax_other",
                    "",
                    "",
                    "err",
                )
            ],
        ),
        timestamp="2026-08-06T13:00:00Z",
    )
    assert append_ok_flip_changelog(flips, path) == 1


def test_ok_flip_changelog_rows_emits_flip_to_skipped():
    previous = validation_rows_to_dataframe(
        [ValidationRow("1", "A", "r0", "file:1", OK_TRUE, "", "", "", "", "")]
    )
    current = validation_rows_to_dataframe(
        [
            ValidationRow(
                "1",
                "A",
                "r0",
                "file:1",
                OK_SKIPPED,
                RULE_SKIPPED_FAILURE_CLASS,
                "",
                "",
                "",
                "held-out (commented rule)",
            )
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-08-06T14:00:00Z")
    assert len(flips) == 1
    assert flips.iloc[0]["ok"] == OK_SKIPPED


def test_ok_flip_changelog_rows_empty_after_inventory_csv_roundtrip(tmp_path: Path):
    rows = [
        ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", ""),
        ValidationRow(
            "1",
            "A",
            "r1",
            "s:2",
            OK_FALSE,
            "syntax_other",
            "",
            "",
            "err",
        ),
        ValidationRow(
            "9",
            "S",
            "r2",
            "s:3",
            OK_SKIPPED,
            RULE_SKIPPED_FAILURE_CLASS,
            "",
            "",
            "",
            "held-out (commented rule)",
        ),
    ]
    current = validation_rows_to_dataframe(rows)
    write_filtered_inventory_csvs(current, tmp_path)
    previous = load_inventory_csv(tmp_path)
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-08-06T15:00:00Z")
    assert flips.empty


def test_coerce_ok_value_maps_legacy_and_numeric_literals():
    assert _coerce_ok_value(True) == OK_TRUE
    assert _coerce_ok_value(False) == OK_FALSE
    assert _coerce_ok_value(1) == OK_TRUE
    assert _coerce_ok_value(0) == OK_FALSE
    assert _coerce_ok_value(2) == OK_SKIPPED
    assert _coerce_ok_value("") == OK_SKIPPED
    assert _coerce_ok_value("True") == OK_TRUE
    assert _coerce_ok_value("False") == OK_FALSE
    assert _coerce_ok_value("OK") == OK_TRUE
    assert _coerce_ok_value("FAILED") == OK_FALSE
    assert _coerce_ok_value("SKIPPED") == OK_SKIPPED


def test_ok_flip_changelog_rows_reads_legacy_numeric_previous():
    import pandas as pd

    previous = pd.DataFrame(
        [
            {
                "section_index": "1",
                "rule_id": "r0",
                "alt_idx": "",
                "source": "s:1",
                "ok": 1,
            }
        ]
    )
    current = validation_rows_to_dataframe(
        [
            ValidationRow(
                "1",
                "A",
                "r0",
                "s:1",
                OK_FALSE,
                "syntax_other",
                "",
                "",
                "err",
            )
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-10-17T12:00:00Z")
    assert len(flips) == 1
    assert flips.iloc[0]["ok"] == OK_FALSE


def test_filter_inventory_by_ok_empty_dataframe():
    import pandas as pd

    empty = pd.DataFrame(columns=validation_rows_to_dataframe([]).columns)
    assert filter_inventory_by_ok(empty, ok=True).empty


@pytest.mark.parametrize(
    (
        "whole_ok",
        "input_ok",
        "output_ok",
        "env_ok",
        "exception_ok",
        "expected",
    ),
    [
        (OK_TRUE, True, True, True, True, "none"),
        (OK_TRUE, False, True, None, None, "input"),
        (OK_FALSE, False, True, None, None, "input"),
        (OK_FALSE, True, False, None, None, "output"),
        (OK_FALSE, True, True, False, None, "env"),
        (OK_FALSE, True, True, None, False, "exception"),
        (OK_FALSE, False, False, False, False, "input|output|env|exception"),
        (OK_FALSE, False, True, False, None, "input|env"),
        (OK_FALSE, True, True, True, True, "multi"),
        (OK_FALSE, None, None, None, None, "multi"),
    ],
)
def test_derive_blame(
    whole_ok,
    input_ok,
    output_ok,
    env_ok,
    exception_ok,
    expected,
):
    assert (
        derive_blame(
            whole_ok,
            input_ok=input_ok,
            output_ok=output_ok,
            env_ok=env_ok,
            exception_ok=exception_ok,
        )
        == expected
    )


def test_filter_field_isolation_splits_success_and_error():
    rows = [
        FieldIsolationRow(
            "1",
            "A",
            "r0",
            "s:1",
            OK_TRUE,
            True,
            True,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "none",
        ),
        FieldIsolationRow(
            "1",
            "A",
            "r1",
            "s:2",
            OK_FALSE,
            False,
            True,
            None,
            None,
            "unknown_feature",
            "",
            "",
            "",
            "err",
            "",
            "",
            "",
            "input",
        ),
        FieldIsolationRow(
            "1",
            "A",
            "r2",
            "s:3",
            OK_TRUE,
            False,
            True,
            None,
            None,
            "unknown_feature",
            "",
            "",
            "",
            "err",
            "",
            "",
            "",
            "input",
        ),
        FieldIsolationRow(
            "9",
            "Skipped",
            "r3",
            "s:4",
            OK_SKIPPED,
            None,
            None,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "none",
            failure_class=SECTION_SKIPPED_FAILURE_CLASS,
        ),
    ]
    df = field_isolation_rows_to_dataframe(rows)
    success = filter_field_isolation_success(df)
    error = filter_field_isolation_error(df)
    skipped = filter_field_isolation_skipped(df)
    assert list(success["source"]) == ["s:1"]
    assert set(error["source"]) == {"s:2", "s:3"}
    assert list(skipped["source"]) == ["s:4"]
    assert list(success.columns) == list(df.columns)


def test_build_field_isolation_row_without_field_rule():
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        OK_FALSE,
        "format_error",
        "",
        "",
        "bad",
    )
    row = build_field_isolation_row(validation_row, None)
    assert row.whole_ok == OK_FALSE
    assert row.input_ok is None
    assert row.blame == "multi"


def test_write_field_isolation_csvs_writes_success_error_and_skipped(tmp_path: Path):
    rows = [
        FieldIsolationRow(
            "1",
            "A",
            "r0",
            "s:1",
            OK_TRUE,
            True,
            True,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "none",
        ),
        FieldIsolationRow(
            "1",
            "A",
            "r1",
            "s:2",
            OK_FALSE,
            False,
            True,
            None,
            None,
            "unknown_feature",
            "",
            "",
            "",
            "err",
            "",
            "",
            "",
            "input",
        ),
        FieldIsolationRow(
            "9",
            "Skipped",
            "r2",
            "s:3",
            OK_SKIPPED,
            None,
            None,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "none",
            failure_class=SECTION_SKIPPED_FAILURE_CLASS,
        ),
    ]
    write_field_isolation_csvs(rows, tmp_path)
    success = list(csv.DictReader((tmp_path / "field-isolation-success.csv").open()))
    error = list(csv.DictReader((tmp_path / "field-isolation-error.csv").open()))
    skipped = list(csv.DictReader((tmp_path / "field-isolation-skipped.csv").open()))
    assert not (tmp_path / "field-isolation.csv").exists()
    assert len(success) == 1
    assert success[0]["source"] == "s:1"
    assert len(error) == 1
    assert error[0]["source"] == "s:2"
    assert len(skipped) == 1
    assert skipped[0]["source"] == "s:3"
    assert skipped[0]["whole_ok"] == OK_SKIPPED


def test_summarize_inventory_links_field_isolation_csvs():
    validation_rows = [
        ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", ""),
    ]
    field_rows = [
        FieldIsolationRow(
            "1",
            "A",
            "r1",
            "s:2",
            OK_FALSE,
            False,
            True,
            None,
            None,
            "unknown_feature",
            "",
            "",
            "",
            "err",
            "",
            "",
            "",
            "input",
        ),
    ]
    text = summarize_inventory(
        validation_rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        field_isolation_rows=field_rows,
    )
    assert "field-isolation-success.csv" in text
    assert "field-isolation-error.csv" in text
    assert "field-isolation-skipped.csv" in text
    assert "rule-inventory-skipped.csv" in text
    assert "field-isolation.csv" not in text
    assert "## Field isolation blame (error rows)" in text
    assert "| 1 | `input` |" in text


def test_summarize_inventory_blame_section_counts_whole_rule_failures_only():
    validation_rows = [
        ValidationRow("1", "A", "r0", "s:1", OK_TRUE, "", "", "", "", ""),
        ValidationRow("1", "A", "r1", "s:2", OK_FALSE, "", "", "", "", ""),
        ValidationRow("1", "A", "r2", "s:3", OK_FALSE, "", "", "", "", ""),
    ]
    field_rows = [
        FieldIsolationRow(
            "1",
            "A",
            "r0",
            "s:1",
            OK_TRUE,
            False,
            True,
            None,
            None,
            "unknown_feature",
            "",
            "",
            "",
            "err",
            "",
            "",
            "",
            "input",
        ),
        FieldIsolationRow(
            "1",
            "A",
            "r1",
            "s:2",
            OK_FALSE,
            True,
            True,
            False,
            None,
            "",
            "",
            "expected_underscore",
            "",
            "",
            "",
            "bad env",
            "",
            "env",
        ),
        FieldIsolationRow(
            "1",
            "A",
            "r2",
            "s:3",
            OK_FALSE,
            True,
            True,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "multi",
        ),
    ]
    text = summarize_inventory(
        validation_rows,
        source_yaml="out.yml",
        probe_words="probe.wsca",
        field_isolation_rows=field_rows,
    )
    assert "| 1 | `env` |" in text
    assert "| 1 | `multi` |" in text
    assert (
        "`input`"
        not in text.split("## Field isolation blame (error rows)")[1].split("## Notes")[
            0
        ]
    )


def test_count_field_blame_categories_splits_composite_blame():
    rows = [
        FieldIsolationRow(
            "1",
            "A",
            "r0",
            "s:1",
            OK_FALSE,
            False,
            False,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "input|output",
        ),
        FieldIsolationRow(
            "1",
            "A",
            "r1",
            "s:2",
            OK_FALSE,
            True,
            True,
            None,
            None,
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "multi",
        ),
    ]
    df = field_isolation_rows_to_dataframe(rows)
    counts = count_field_blame_categories(df)
    assert counts["input"] == 1
    assert counts["output"] == 1
    assert counts["multi"] == 1
    assert len(counts) == 3


@patch("conlanger.tools.index_inventory.validate_asca_part", return_value=True)
def test_build_field_isolation_row_unknown_feature_on_input(mock_validate_part):
    def side_effect(part, fragment, **kwargs):
        if part == "input":
            raise ASCAValidationError("Syntax Error: Unknown feature 'voiced'")
        return True

    mock_validate_part.side_effect = side_effect

    field_rule = SoundChangeRule(input="C:[+voiced]", output="e")
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        OK_FALSE,
        "unknown_feature",
        "voiced",
        "voice",
        "whole fail",
    )
    row = build_field_isolation_row(validation_row, field_rule)
    assert row.blame == "input"
    assert row.input_ok is False
    assert row.input_class == "unknown_feature"
    assert row.output_ok is True


@patch("conlanger.tools.index_inventory.validate_asca_part")
def test_build_field_isolation_row_missing_underscore_on_env(mock_validate_part):
    def side_effect(part, fragment, **kwargs):
        if part == "env":
            raise ASCAValidationError("Syntax Error: Expected '_'")
        return True

    mock_validate_part.side_effect = side_effect

    field_rule = SoundChangeRule(input="a", output="e", env="word-initially")
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        OK_FALSE,
        "expected_underscore",
        "",
        "",
        "whole fail",
    )
    row = build_field_isolation_row(validation_row, field_rule)
    assert row.blame == "env"
    assert row.env_ok is False
    assert row.env_class == "expected_underscore"
    assert row.input_ok is True
    assert row.output_ok is True


@patch("conlanger.tools.index_inventory.validate_asca_part")
def test_build_field_isolation_row_two_fields_fail(mock_validate_part):
    def side_effect(part, _fragment, **kwargs):
        if part in {"input", "env"}:
            raise ASCAValidationError(f"Syntax Error: bad {part}")
        return True

    mock_validate_part.side_effect = side_effect

    field_rule = SoundChangeRule(input="bad", output="e", env="bad-env")
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        OK_FALSE,
        "syntax_other",
        "",
        "",
        "whole fail",
    )
    row = build_field_isolation_row(validation_row, field_rule)
    assert row.blame == "input|env"


@pytest.mark.skipif(not ASCA_VALIDATE_INSTALLED, reason="asca validate not available")
@patch("conlanger.tools.index_inventory.validate_asca", return_value=True)
def test_iter_index_rule_inventory_bundles_one_per_rule(mock_validate):
    doc = {
        "sections": [
            {
                "index": "1",
                "section": "A",
                "rules": [
                    {"stages": ["a", "b"], "rule_id": "r0", "source": "s:1"},
                    {"stages": ["c", "d"], "rule_id": "r1", "source": "s:2"},
                ],
            }
        ]
    }
    bundles = iter_index_rule_inventory_bundles(doc, probe_words=None)
    assert len(bundles) == 2
    assert [bundle.rule_id for bundle in bundles] == ["r0", "r1"]
    assert len(bundles[0].rows) == 1


@patch("conlanger.tools.index_inventory.validate_asca", return_value=True)
def test_validate_index_rule_chain_emits_one_row_per_step(mock_validate):
    rule = {
        "stages": ["p", "t", "k"],
        "raw": "p → t → k",
        "source": "chain:1",
    }
    rows, targets = validate_index_rule_with_targets(
        _SECTION,
        rule,
        "chain-r0",
        probe_words=None,
    )
    assert len(rows) == 2
    assert [row.step_idx for row in rows] == [0, 1]
    assert all(row.alt_idx is None for row in rows)
    assert mock_validate.call_count == 2
    for row, target in zip(rows, targets, strict=True):
        series_rules = [
            part for part in target.series.parts if isinstance(part, SoundChangeRule)
        ]
        assert len(series_rules) == 1
        assert row.rule == str(series_rules[0]).strip()


@patch("conlanger.tools.index_inventory.validate_asca", return_value=True)
def test_validate_index_rule_optional_output_is_stable_across_calls(mock_validate):
    rule = {
        "stages": ["d", "{∅,ð}"],
        "env": "V_V",
        "raw": "d → {∅,ð} / V_V",
        "source": "opt:1",
    }
    first_rows, _ = validate_index_rule_with_targets(
        _SECTION, rule, "opt-r0", probe_words=None
    )
    second_rows, _ = validate_index_rule_with_targets(
        _SECTION, rule, "opt-r0", probe_words=None
    )
    assert len(first_rows) == 2
    assert [(r.alt_idx, r.ok, r.rule) for r in first_rows] == [
        (r.alt_idx, r.ok, r.rule) for r in second_rows
    ]
    assert mock_validate.call_count == 4


def test_ok_flip_changelog_rows_keys_on_step_idx():
    previous = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "chain:1", OK_TRUE, step_idx=0),
            ValidationRow("1", "A", "r0", "chain:1", OK_TRUE, step_idx=1),
        ]
    )
    current = validation_rows_to_dataframe(
        [
            ValidationRow("1", "A", "r0", "chain:1", OK_TRUE, step_idx=0),
            ValidationRow(
                "1",
                "A",
                "r0",
                "chain:1",
                OK_FALSE,
                failure_class="syntax_other",
                description="err",
                step_idx=1,
            ),
        ]
    )
    flips = ok_flip_changelog_rows(previous, current, timestamp="2026-10-17T12:00:00Z")
    assert list(flips["source"]) == ["chain:1"]
    assert list(flips["step_idx"]) == ["1"]
    assert list(flips["ok"]) == [OK_FALSE]


def test_field_isolation_integration_multi_blame():
    validation_row = ValidationRow(
        "1",
        "A",
        "r0",
        "s:1",
        OK_FALSE,
        "runtime_other",
        "",
        "",
        "uneven set",
    )
    field_rule = SoundChangeRule(input="{p,t}", output="{b}")
    row = build_field_isolation_row(validation_row, field_rule)
    assert row.input_ok is True
    assert row.output_ok is True
    assert row.blame == "multi"

    rows, targets = validate_index_rule_with_targets(
        _SECTION,
        {"stages": ["{p,t}", "{b}"], "raw": "{p,t} → {b}", "source": "s:multi"},
        "r0",
        probe_words=None,
    )
    assert len(rows) == 1
    assert rows[0].ok == OK_FALSE
    field_rows = field_isolation_rows_for_validation_rows(rows, targets)
    assert field_rows[0].blame == "multi"


def test_bundles_for_row_prefix_truncates_mid_rule():
    section = {"index": "1", "section": "A"}
    rule = {"stages": ["a", "b", "c"], "source": "s:1"}
    targets = resolve_inventory_targets(section, rule, "chain")
    rows = [
        ValidationRow("1", "A", "chain", "s:1", OK_TRUE, rule="a > b", step_idx=0),
        ValidationRow("1", "A", "chain", "s:1", OK_TRUE, rule="b > c", step_idx=1),
    ]
    bundles = [
        IndexRuleInventoryBundle(
            section=section,
            rule=rule,
            rule_id="chain",
            rows=rows,
            targets=targets,
        )
    ]
    trimmed = bundles_for_row_prefix(bundles, rows[:1])
    assert len(trimmed) == 1
    assert len(trimmed[0].rows) == 1
    assert bundles_for_row_prefix(bundles, []) == []


def test_iter_index_compile_bundles_skips_section_status():
    doc = {
        "sections": [
            {"index": "9", "section": "Skip", "status": "skipped", "rules": []},
            {
                "index": "1",
                "section": "A",
                "rules": [{"stages": ["a", "b"], "rule_id": "r0"}],
            },
        ]
    }
    bundles = iter_index_compile_bundles(doc)
    assert len(bundles) == 1
    assert bundles[0].rule_id == "r0"
    assert bundles[0].rows == []


@patch("conlanger.tools.index_inventory.validate_asca_body", return_value=True)
def test_iter_compiled_inventory_bundles_from_v1_document(mock_validate):
    from conlanger.tools.compiled_rules_yaml import build_asca_rules_document

    doc = {
        "sections": [
            {
                "index": "1",
                "section": "A",
                "rules": [
                    {
                        "stages": ["a", "b"],
                        "rule_id": "r0",
                        "source": "s:1",
                    }
                ],
            }
        ]
    }
    compile_bundles = iter_index_compile_bundles(doc)
    compiled = build_asca_rules_document(compile_bundles)
    bundles = iter_compiled_inventory_bundles(compiled, probe_words=None)
    assert len(bundles) == 1
    assert bundles[0].rows[0].ok == OK_TRUE
    assert bundles[0].rows[0].rule == "a > b"


@patch("conlanger.tools.index_inventory.validate_asca_body", return_value=True)
def test_compiled_validation_uses_rule_line_without_series_round_trip(mock_body):
    compiled = {
        "schema_version": 3,
        "sections": [
            {
                "index": "17.7.2",
                "section": "Common Germanic to West Germanic",
                "rules": [
                    {
                        "rule_id": "West-Germanic-C",
                        "source": "index_diachronica.html:5693",
                        "rule": "{C,-r} > C:[+long] / _j",
                    },
                    {
                        "rule_id": "Tocharian-A-V",
                        "source": "index_diachronica.html:8297",
                        "rule": "V:[+front] > j / V:[+front]_nʲtʲ // V:[+front]_E",
                    },
                ],
            }
        ],
    }
    bundles = iter_compiled_inventory_bundles(compiled, probe_words=None)
    assert bundles[0].rows[0].ok == OK_TRUE
    assert bundles[0].rows[0].rule == "{C,-r} > C:[+long] / _j"
    mock_body.assert_any_call(
        "{C,-r} > C:[+long] / _j",
        probe_words=None,
        asca_bin=None,
    )
    assert bundles[1].rows[0].ok == OK_TRUE


def test_iter_compiled_inventory_rejects_ambiguous_rule_shape():
    compiled = {
        "schema_version": 3,
        "sections": [
            {
                "index": "1",
                "section": "A",
                "rules": [
                    {
                        "rule_id": "bad",
                        "source": "s:1",
                        "rule": "a > b",
                        "alternatives": ["a > b"],
                    },
                ],
            }
        ],
    }
    bundles = iter_compiled_inventory_bundles(compiled, probe_words=None)
    assert bundles[0].rows[0].ok == OK_FALSE
    assert bundles[0].rows[0].failure_class == "format_error"


def test_iter_compiled_inventory_handles_skipped_and_compile_error():
    compiled = {
        "schema_version": 3,
        "sections": [
            {
                "index": "1",
                "section": "A",
                "rules": [
                    {
                        "rule_id": "hold",
                        "source": "s:1",
                        "status": "skipped",
                        "rule": "#\tx",
                    },
                    {
                        "rule_id": "bad",
                        "source": "s:2",
                        "compile_error": "missing stages",
                    },
                    {
                        "rule_id": "sp",
                        "source": "s:3",
                        "status": "compile_skipped",
                        "rule": "#\tp > h",
                    },
                ],
            }
        ],
    }
    bundles = iter_compiled_inventory_bundles(compiled, probe_words=None)
    assert bundles[0].rows[0].ok == OK_SKIPPED
    assert bundles[1].rows[0].failure_class == "format_error"
    assert bundles[2].rows[0].ok == OK_TRUE
