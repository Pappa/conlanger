import shutil
from pathlib import Path

import pytest

from conlanger.tools.rules import (
    DebugRules,
    RuleChange,
    RuleCitation,
    RuleComment,
    SoundChangeRuleSet,
    _expand_grouping_letter,
    apply_asca_group_mappings_to_string,
    normalize_asca_ejective_marks,
    normalize_asca_length_marks,
    normalize_asca_optional_grouping_ellipsis,
    normalize_typographic_apostrophes,
)


@pytest.mark.parametrize(
    "section, format, expected",
    [
        (
            {
                "index": "1",
                "section": "sec",
                "rules": [{"input": "a", "output": "b", "env": "c", "exception": "d"}],
            },
            "asca",
            "@ 1 - sec\n\ta > b / c // d",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "rules": [{"input": "a", "output": "b", "env": "c", "exception": "d"}],
            },
            "brassica",
            "; 1 - sec\na / b / c // d",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "rules": [{"skip": True, "input": "a", "output": "b"}],
            },
            "asca",
            "@ 1 - sec\n#\ta > b",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "rules": [{"skip": True, "input": "a", "output": "b"}],
            },
            "brassica",
            "; 1 - sec\n;;\ta / b",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "citation": "citation text",
                "rules": [{"input": "a", "output": "b"}],
            },
            "asca",
            "@ 1 - sec\n# citation: citation text\n\ta > b",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "citation": "citation text",
                "rules": [{"input": "a", "output": "b"}],
            },
            "brassica",
            "; 1 - sec\n; citation: citation text\na / b",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "comment": "comment text",
                "rules": [{"input": "a", "output": "b"}],
            },
            "asca",
            "@ 1 - sec\n\t# comment text\n\ta > b",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "comment": "comment text",
                "rules": [{"input": "a", "output": "b"}],
            },
            "brassica",
            "; 1 - sec\n; comment text\na / b",
        ),
        ({"index": "1", "section": "sec"}, "asca", "@ 1 - sec"),
        ({"index": "1", "section": "sec"}, "brassica", "; 1 - sec"),
    ],
)
def test_SoundChangeRuleSet(section, format, expected):
    rule = SoundChangeRuleSet(section, format)
    assert str(rule) == expected
    assert rule.title == section["index"] + " - " + section["section"]


@pytest.mark.parametrize(
    "section, format",
    [
        (
            {"index": "1", "section": "sec", "rules": [{"input": "a", "output": "b"}]},
            "invalid",
        ),
        ({"index": "1", "section": "sec", "rules": [{"input": "a"}]}, "asca"),
        ({"index": "1", "section": "sec", "rules": [{"output": "b"}]}, "brassica"),
    ],
)
def test_SoundChangeRuleSet_invalid_input(section, format):
    with pytest.raises(ValueError):
        SoundChangeRuleSet(section, format)


def test_DebugRules():
    rules = DebugRules(
        {"index": "1", "section": "sec", "rules": [{"input": "a", "output": "b"}]},
        "asca",
    )

    assert len(rules) == 1

    _, rule = rules[0]

    assert rule.title == "1 - 0"
    assert str(rule) == "@ 1 - 0\n\ta > b"

    for index, rule in rules:
        assert rule.title == f"1 - {index}"
        assert str(rule) == f"@ 1 - {index}\n\ta > b"


@pytest.mark.parametrize(
    "value, format, expected",
    [
        ("citation text", "asca", "# citation: citation text"),
        ("citation text", "brassica", "; citation: citation text"),
    ],
)
def test_RuleCitation(value, format, expected):
    rule = RuleCitation(value, format)
    assert str(rule) == expected


@pytest.mark.parametrize(
    "value, format, expected",
    [
        ("comment text", "asca", "\t# comment text"),
        ("comment text", "brassica", "; comment text"),
    ],
)
def test_RuleComment(value, format, expected):
    rule = RuleComment(value, format)
    assert str(rule) == expected


def test_format_not_supported():
    with pytest.raises(ValueError):
        RuleCitation("citation text", "invalid")
    with pytest.raises(ValueError):
        RuleComment("comment text", "invalid")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("aː", "a:[+long]"),
        ("Vː", "V:[+long]"),
        ("e(ː)", "e:[+long]"),
        ("tsː", "ts:[+long]"),
        ("_{i,e(ː),a}", "_{i,e:[+long],a}"),
        ("VNC > VːC[+voiced]", "VNC > V:[+long]C[+voiced]"),
        ("tʷː", "tʷ:[+long]"),
        ("æː", "æ:[+long]"),
        ("{e,ɤ}ː", "{e,ɤ}:[+long]"),
        ("C_C{ː,C}V", "C_C{V:[+long],C}V"),
        ("e(ː,j)", "{e:[+long],ej}"),
        ("{o,u}(ː)", "{o,u}:[+long]"),
        ("s:[+long]ː", "s:[+long]"),
        ("aj aw > e(ː,j) o(ː,w)", "aj aw > {e:[+long],ej} {o:[+long],ow}"),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_asca_length_marks(text, expected):
    assert normalize_asca_length_marks(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("_(C…)", "_(C,0)"),
        ("o(C…)_(C…)#", "o(C,0)_(C,0)#"),
        ("_(C…)i", "_(C,0)i"),
        ("_(C...)", "_(C,0)"),
        ("_(C..)", "_(C,0)"),
        ("_(V…)", "_(V,0)"),
        ("_(%…)", "_(%,0)"),
        ("_(S…)", "_(S,0)"),
        ("_C(C…)i#", "_C(C,0)i#"),
        ("e > i / _(C…)i(C…)#", "e > i / _(C,0)i(C,0)#"),
        ("V_(VC…)", "V_(VC,0)"),
        ("ə(C…?)_", "ə(C,0)_"),
        ("_C(…C){a,e}", "_C(..)C{a,e}"),
        ("_V(…V)", "_V(..)V"),
        ("a", "a"),
        ("", ""),
        ("[+hi](C…)", "[+hi](C,0)"),
    ],
)
def test_normalize_asca_optional_grouping_ellipsis(text, expected):
    assert normalize_asca_optional_grouping_ellipsis(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("{O:[+delrel],O\u2019}", "{O:[+delrel],O\u02bc}"),
        ("C\u2019 > C", "C\u02bc > C"),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_typographic_apostrophes(text, expected):
    assert normalize_typographic_apostrophes(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ts:[+long]ʼ", "ts:[+long,+cg]"),
        ("tʃ:[+long]ʼ > tʃ:[+long]", "tʃ:[+long,+cg] > tʃ:[+long]"),
        ("dʒ > {tʃ:[+long]ʼ,dʒ}", "dʒ > {tʃ:[+long,+cg],dʒ}"),
        ("{ts:[+long]ʼ,z}", "{ts:[+long,+cg],z}"),
        ("{t,ts}ʼ", "{t:[+cg],ts:[+cg]}"),
        ("dʼ > tʼ", "d:[+cg] > t:[+cg]"),
        ("tʃʼ > tsʼ", "tʃ:[+cg] > ts:[+cg]"),
        ("ts ts:[+long] tsʼ", "ts ts:[+long] ts:[+cg]"),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_asca_ejective_marks(text, expected):
    assert normalize_asca_ejective_marks(text) == expected


def test_normalize_asca_ejective_marks_preserves_existing_cg():
    assert normalize_asca_ejective_marks("ts:[+cg]ʼ") == "ts:[+cg]"


def test_normalize_asca_ejective_marks_repairs_malformed_feature_colon():
    assert normalize_asca_ejective_marks("t:brokenʼ") == "t:broken:[+cg]"


def test_apply_asca_group_mappings_native_labialized_grouping():
    mappings = {"K": "C:[-front,+back,+hi,-lo]"}
    assert apply_asca_group_mappings_to_string("Sʷ", mappings) == "S:[+round]"


def test_apply_asca_group_mappings_labializes_set_mapping_values():
    mappings = {"M": "{C:[+hi],O:[+delrel]}"}
    assert apply_asca_group_mappings_to_string("Mʷ", mappings) == (
        "{C:[+hi,+round],O:[+delrel,+round]}"
    )


def test_apply_asca_group_mappings_optional_labial_at_set_start():
    mappings = {"K": "C:[-front,+back,+hi,-lo]"}
    assert (
        apply_asca_group_mappings_to_string(
            "i > ə / {K(ʷ),s}_",
            mappings,
        )
        == "i > ə / {C:[-front,+back,+hi,-lo,+round],C:[-front,+back,+hi,-lo],s}_"
    )


def test_normalize_asca_ejective_marks_skips_blank_set_members():
    assert normalize_asca_ejective_marks("{t,,ts}ʼ") == "{t:[+cg],ts:[+cg]}"


def test_normalize_asca_ejective_marks_adds_cg_to_set_members_with_features():
    assert normalize_asca_ejective_marks("{ts:[+long]}ʼ") == "{ts:[+long,+cg]}"


def test_normalize_asca_ejective_marks_repairs_malformed_set_member_features():
    assert normalize_asca_ejective_marks("{t:broken}ʼ") == "{t:broken:[+cg]}"


def test_apply_asca_group_mappings_leaves_unknown_letters_unchanged():
    mappings = {"K": "C:[-front,+back,+hi,-lo]"}
    assert apply_asca_group_mappings_to_string("X > y", mappings) == "X > y"


def test_apply_asca_group_mappings_noop_when_mappings_empty():
    assert apply_asca_group_mappings_to_string("S > P", {}) == "S > P"


def test_apply_asca_group_mappings_optional_labial_outside_set_wraps_pair():
    mappings = {"K": "C:[-front,+back,+hi,-lo]"}
    assert apply_asca_group_mappings_to_string("K(ʷ) > k", mappings) == (
        "{C:[-front,+back,+hi,-lo,+round],C:[-front,+back,+hi,-lo]} > k"
    )


def test_apply_asca_group_mappings_labializes_non_matrix_mapping():
    mappings = {"M": "Kr"}
    assert apply_asca_group_mappings_to_string("Mʷ", mappings) == "Kr"


def test_rule_change_apply_asca_group_mappings_noop_for_non_asca():
    part = RuleChange(
        {"input": "S", "output": "P"},
        "brassica",
        group_mappings={"S": "[+cont]"},
    )
    assert part._apply_asca_group_mappings("S > P", "brassica") == "S > P"


def test_expand_grouping_letter_leaves_unmapped_non_native_letters():
    assert (
        _expand_grouping_letter("X", {"K": "C:[-front,+back,+hi,-lo]"}, labial=False)
        == "X"
    )
    assert (
        _expand_grouping_letter("X", {"K": "C:[-front,+back,+hi,-lo]"}, labial=True)
        == "X"
    )


def test_rule_change_format_alias_matches_compile():
    part = RuleChange({"input": "a", "output": "e"}, "asca")
    assert part._format("asca") == part.value


def test_rule_change_skips_group_mappings_for_brassica():
    part = RuleChange(
        {"input": "S", "output": "P"},
        "brassica",
        group_mappings={"S": "[+cont]"},
    )
    assert part.value == "S / P"


def test_rule_change_compiles_ejective_at_instantiation():
    part = RuleChange({"input": "tʃ:[+long]ʼ", "output": "tʃ:[+long]"}, "asca")
    assert part.value == "tʃ:[+long,+cg] > tʃ:[+long]"
    assert "ʼ" not in part.value
    assert part.input == "tʃ:[+long]ʼ"


def test_rule_change_compiles_typographic_apostrophe_ejective():
    part = RuleChange(
        {"input": "{O:[+delrel],O\u2019}", "output": "F", "env": "_$"}, "asca"
    )
    assert part.value == "{O:[+delrel],O:[+cg]} > F / _$"
    assert "\u2019" not in part.value


def test_rule_change_compiles_length_at_instantiation():
    part = RuleChange({"input": "a(ː)", "output": "e(ː)"}, "asca")
    assert part.value == "a:[+long] > e:[+long]"
    assert "ː" not in part.value
    assert part.input == "a(ː)"


def test_rule_change_compiles_optional_grouping_ellipsis_at_instantiation():
    part = RuleChange(
        {"input": "o", "output": "u", "env": "_(C…)i"},
        "asca",
    )
    assert part.value == "o > u / _(C,0)i"
    assert "…" not in part.value
    assert part.env == "_(C…)i"


def test_rule_change_compiles_chain_arrows_in_output():
    part = RuleChange({"input": "dʒ", "output": "tʃ > ʃ"}, "asca")
    assert part.value == "dʒ > tʃ > ʃ"
    assert "→" not in part.value


def test_rule_change_skips_length_for_brassica():
    part = RuleChange({"input": "aː", "output": "eː"}, "brassica")
    assert part.value == "aː / eː"


def test_sound_change_ruleset_compiles_length_at_instantiation():
    section = {
        "index": "6.1",
        "section": "Test",
        "rules": [{"input": "Vː", "output": "V", "env": "#C_C"}],
    }
    ruleset = SoundChangeRuleSet(section, "asca")
    rule_part = ruleset._parts[-1]
    assert rule_part.value == "V:[+long] > V / #C_C"


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_length_marker_fixtures():
    from conlanger.tools.asca_validator import validate_asca

    section = {
        "index": "6.1",
        "section": "Proto-Afro-Asiatic to Proto-Omotic",
        "rules": [
            {"input": "a(ː)", "output": "e(ː)", "env": "_{ʕ,q}$"},
            {
                "input": "Vː",
                "output": "V",
                "env": "#C:[-front,+back,+hi,-lo][-voice]_C",
            },
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_tilde_notation_fixtures():
    from conlanger.tools.asca_validator import validate_asca

    section = {
        "index": "9.1.2.2",
        "section": "Middle Vietnamese to Saigon Vietnamese",
        "rules": [
            {"input": "{β,w}", "output": "bj~vj~v"},
            {"input": "ɣ", "output": "ɣ~ɡ"},
            {"input": "ts", "output": "{ts~tsʰ,ts,s}"},
            {"input": "ʃ(~ʃ:[+long]) ʒ", "output": "sʲ sʲ"},
            {"input": "h", "output": "j~ʔ", "env": "_ V:[+front]"},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_expanded_chain_fixtures():
    from conlanger.tools.asca_validator import validate_asca

    section = {
        "index": "1.0",
        "section": "Chain",
        "rules": [{"input": "dʒ", "output": "tʃ > ʃ"}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_ejective_marker_fixtures():
    from conlanger.tools.asca_validator import validate_asca

    section = {
        "index": "11.5.1",
        "section": "Proto-Lezgic to Agul",
        "rules": [
            {"input": "tʃ:[+long]ʼ", "output": "tʃ:[+long]"},
            {"input": "dʒ", "output": "{tʃ:[+long]ʼ,dʒ}"},
            {"input": "dʼ", "output": "tʼ"},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_optional_grouping_ellipsis_fixtures():
    from conlanger.tools.asca_validator import validate_asca

    section = {
        "index": "33.1.1.4",
        "section": "Proto-Costanoan to Rumsen",
        "rules": [
            {"input": "o", "output": "u", "env": "_(C…)i"},
            {"input": "ə", "output": "a", "env": "_(C…)#"},
            {"input": "o", "output": "u", "exception": "o(C…)_(C…)#"},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_extended_grouping_ellipsis_fixtures():
    from conlanger.tools.asca_validator import validate_asca

    section = {
        "index": "17.12.1.1.6",
        "section": "Extended grouping ellipsis",
        "rules": [
            {"input": "ɡ", "output": "∅", "env": "V_(VC…)V"},
            {"input": "V", "output": "V:[+long]", "env": "ə(C…?)_"},
            {"input": "C", "output": "C:[+long]", "env": "_V(…V)"},
            {
                "input": "i u",
                "output": "e o",
                "env": "_C(…C){a:[+long],e:[+long],o:[+long]}",
            },
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_em_dash_rule_marker_fixtures():
    from conlanger.tools.asca_validator import validate_asca

    section = {
        "index": "6.2.2.1.18",
        "section": "Proto-Semitic to Biblical Hebrew",
        "rules": [
            {"input": "aː", "output": "oː", "exception": "_#"},
            {"input": "j w", "output": "i u", "env": "#_CV"},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)
