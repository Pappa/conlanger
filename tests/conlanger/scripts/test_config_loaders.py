"""Tests for scripts-only YAML config loaders (ticket 101)."""

from pathlib import Path

import pytest

from conlanger.scripts.config_loaders import load_compiler_config, load_parser_config
from conlanger.utils.mappings import IpaMapping, ManualMapping, ParserConfig


def _write_parser_fragments(
    tmp_path: Path,
    *,
    parser_config: str,
    ipa_mappings: str = "",
    manual_mappings: str = "[]\n",
    feature_mappings: str = "{}\n",
    corrections: str = "rules: []\n",
) -> Path:
    config_path = tmp_path / "parser_config.yml"
    config_path.write_text(parser_config, encoding="utf-8")
    (tmp_path / "ipa_mappings.yml").write_text(ipa_mappings or "{}\n", encoding="utf-8")
    (tmp_path / "manual_mappings.yml").write_text(manual_mappings, encoding="utf-8")
    (tmp_path / "feature_mappings.yml").write_text(feature_mappings, encoding="utf-8")
    (tmp_path / "index_diachronica_corrections.yml").write_text(
        corrections, encoding="utf-8"
    )
    return config_path


def test_load_group_mappings_from_yaml(tmp_path: Path):
    compiler_path = tmp_path / "compiler_config.yml"
    compiler_path.write_text("series_mappings:\n  global: {}\n", encoding="utf-8")
    (tmp_path / "group_mappings.yml").write_text(
        "S:\n  mapping: P\n  comment: plosive\n",
        encoding="utf-8",
    )
    config = load_compiler_config(compiler_path)
    assert config.group_mappings == {"S": "P"}


def test_load_parser_config_high_only_override(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence:\n    - high\n",
    )
    config = load_parser_config(path)
    assert config.ipa_mappings_confidence == frozenset({"high"})


def test_load_parser_config_ignores_non_list_series_expansion_entries(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config=(
            "ipa_mappings:\n  confidence: [high]\nseries_expansions:\n  Hₓ: not-a-list\n"
        ),
    )
    config = load_parser_config(path)
    assert config.series_expansions == {}


def test_load_parser_config_omitted_confidence_is_none(tmp_path: Path):
    path = _write_parser_fragments(tmp_path, parser_config="ipa_mappings: {}\n")
    config = load_parser_config(path)
    assert config.ipa_mappings_confidence is None


def test_load_parser_config_skip_sections(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config=(
            "ipa_mappings:\n  confidence: [high]\n"
            "skip_sections:\n"
            '  - id: "37.1.2.4.2"\n'
            '    reason: "bad source"\n'
        ),
    )
    config = load_parser_config(path)
    assert config.skip_section_ids == frozenset({"37.1.2.4.2"})


def test_load_parser_config_skip_sections_ignores_malformed_entries(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config=(
            "ipa_mappings:\n  confidence: [high]\n"
            "skip_sections:\n"
            "  - not-a-mapping\n"
            "  - id: ''\n"
        ),
    )
    config = load_parser_config(path)
    assert config.skip_section_ids == frozenset()


def test_load_parser_config_section_mappings(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config=(
            "ipa_mappings:\n  confidence: [high]\n"
            "section_mappings:\n"
            '  "10.1":\n'
            '    "*D": "D"\n'
            '    "*R": "R"\n'
            '    "*T": "T"\n'
        ),
    )
    config = load_parser_config(path)
    assert config.section_mappings_sections == {
        "10.1": {"*D": "D", "*R": "R", "*T": "T"},
    }


def test_load_parser_config_section_mappings_empty_or_absent(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
    )
    config = load_parser_config(path)
    assert config.section_mappings_sections == {}


def test_load_parser_config_skip_rules(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config=(
            "ipa_mappings:\n  confidence: [high]\n"
            "skip_rules:\n"
            "  - id: Pre-Slavic-Vowel-Changes-i\n"
            '    reason: "structural hold-out"\n'
        ),
    )
    config = load_parser_config(path)
    assert config.skip_rule_ids == frozenset({"Pre-Slavic-Vowel-Changes-i"})
    assert (
        config.skip_rule_comments["Pre-Slavic-Vowel-Changes-i"] == "structural hold-out"
    )


def test_resolved_ipa_mappings_high_only_config_excludes_medium(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence:\n    - high\n",
        ipa_mappings=(
            "ḱ:\n  ipa_target: kʲ\n  confidence: high\n"
            "è:\n  ipa_target: ɛ\n  confidence: high\n"
            "é:\n  ipa_target: e\n  confidence: medium\n"
        ),
    )
    config = load_parser_config(path)
    mappings = config.resolved_ipa_mappings()
    assert mappings["ḱ"] == "kʲ"
    assert mappings["è"] == "ɛ"
    assert "é" not in mappings


def test_resolved_ipa_mappings_none_confidence_includes_all(tmp_path: Path):
    config = ParserConfig(
        ipa_mappings=(
            IpaMapping("ḱ", "kʲ", confidence="high"),
            IpaMapping("é", "e", confidence="medium"),
            IpaMapping("x", "", confidence="low"),
        ),
        ipa_mappings_confidence=None,
    )
    mappings = config.resolved_ipa_mappings()
    assert mappings == {"ḱ": "kʲ", "é": "e"}


def test_load_ipa_mappings_returns_empty_when_file_missing(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
    )
    (tmp_path / "ipa_mappings.yml").unlink()
    config = load_parser_config(path)
    assert config.ipa_mappings == ()


def test_load_manual_mappings_returns_empty_when_file_missing(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
    )
    (tmp_path / "manual_mappings.yml").unlink()
    config = load_parser_config(path)
    assert config.manual_mappings == []


def test_load_manual_mappings_rejects_duplicate_from(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
        manual_mappings=("- from: a → b\n  to: a → c\n- from: a → b\n  to: a → d\n"),
    )
    with pytest.raises(ValueError, match="duplicate"):
        load_parser_config(path)


def test_load_manual_mappings_preserves_use_regex(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
        manual_mappings="- from: foo\n  to: bar\n  use_regex: true\n",
    )
    config = load_parser_config(path)
    assert config.manual_mappings == [
        ManualMapping(from_text="foo", to_text="bar", use_regex=True),
    ]


@pytest.mark.parametrize(
    ("case_id", "yaml_content"),
    [
        ("non_dict_rule_block", "rules:\n  - rule: not-a-dict\n"),
        (
            "entry_without_id",
            "rules:\n  - rule:\n      content: a → b\n      reason: no id\n",
        ),
        (
            "whitespace_only_content",
            (
                "rules:\n"
                "  - rule:\n"
                "      id: blank\n"
                "      content: '   '\n"
                "      reason: skip\n"
            ),
        ),
        ("rules_not_a_list", "rules: not-a-list\n"),
        ("missing_rules_list", "other: {}\n"),
        ("non_dict_yaml", "- not a dict\n"),
    ],
)
def test_load_corrections_returns_empty(
    case_id: str, yaml_content: str, tmp_path: Path
):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
        corrections=yaml_content,
    )
    config = load_parser_config(path)
    assert config.corrections == {}


def test_load_corrections_missing_file(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
    )
    (tmp_path / "index_diachronica_corrections.yml").unlink()
    config = load_parser_config(path)
    assert config.corrections == {}


def test_load_corrections_skips_empty_content(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
        corrections=(
            "rules:\n"
            "  - rule:\n"
            "      id: good\n"
            "      content: a → b\n"
            "      reason: ok\n"
            "  - rule:\n"
            "      id: empty\n"
            "      content:\n"
            "      reason: skip\n"
        ),
    )
    config = load_parser_config(path)
    assert config.corrections == {"good": "a → b"}


def test_load_corrections_reads_rules_list_schema(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
        corrections=(
            "rules:\n"
            "  - rule:\n"
            "      id: Test-id\n"
            "      content: x → y\n"
            "      reason: author note\n"
        ),
    )
    config = load_parser_config(path)
    assert config.corrections == {"Test-id": "x → y"}


def test_load_corrections_skips_malformed_entries(tmp_path: Path):
    path = _write_parser_fragments(
        tmp_path,
        parser_config="ipa_mappings:\n  confidence: [high]\n",
        corrections=(
            "rules:\n  - not-a-rule\n  - rule:\n      id: ok\n      content: a → b\n"
        ),
    )
    config = load_parser_config(path)
    assert config.corrections == {"ok": "a → b"}


def test_section_row_beats_global_on_longest_prefix(tmp_path: Path):
    path = tmp_path / "compiler_config.yml"
    path.write_text(
        "series_mappings:\n"
        "  global:\n"
        "    h₁: h\n"
        "    s₁: ʃ\n"
        "  sections:\n"
        "    - section: '17'\n"
        "      h₁: ɦ\n"
        "    - section: '17.10'\n"
        "      h₁: ʔ\n",
        encoding="utf-8",
    )
    (tmp_path / "group_mappings.yml").write_text("{}\n", encoding="utf-8")
    config = load_compiler_config(path)
    assert config.lookup_series_mapping("17.10.1", "h₁") == "ʔ"
    assert config.lookup_series_mapping("17.2", "h₁") == "ɦ"
    assert config.lookup_series_mapping("6.1", "h₁") == "h"
    assert config.lookup_series_mapping("17.10", "s₁") == "ʃ"
    assert config.lookup_series_mapping("17.10", "s₂") is None


def test_load_compiler_config_skips_malformed_section_rows(tmp_path: Path):
    path = tmp_path / "compiler_config.yml"
    path.write_text(
        "series_mappings:\n"
        "  global:\n"
        "    h₁: h\n"
        "  sections:\n"
        "    - not-a-map\n"
        "    - h₁: ʔ\n"
        "    - section: '17.10'\n"
        "      h₁: ʔ\n",
        encoding="utf-8",
    )
    (tmp_path / "group_mappings.yml").write_text("{}\n", encoding="utf-8")
    config = load_compiler_config(path)
    assert config.lookup_series_mapping("17.10", "h₁") == "ʔ"
    assert config.lookup_series_mapping("1", "h₁") == "h"
