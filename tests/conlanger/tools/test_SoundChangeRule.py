import shutil
from pathlib import Path

import pytest

from conlanger.tools.rules import (
    DebugRules,
    RuleChange,
    RuleCitation,
    RuleComment,
    SoundChangeRuleSet,
    normalize_asca_ejective_marks,
    normalize_asca_length_marks,
)

@pytest.mark.parametrize(
    "section, format, expected",
    [
        ({"index": "1", "section": "sec", "rules": [{"input": "a", "output": "b", "env": "c", "exception": "d"}]}, "asca", "@ 1 - sec\n\ta > b / c // d"),
        ({"index": "1", "section": "sec", "rules": [{"input": "a", "output": "b", "env": "c", "exception": "d"}]}, "brassica", "; 1 - sec\na / b / c // d"),
        ({"index": "1", "section": "sec", "rules": [{"skip": True,"input": "a", "output": "b"}]}, "asca", "@ 1 - sec\n#\ta > b"),
        ({"index": "1", "section": "sec", "rules": [{"skip": True,"input": "a", "output": "b"}]}, "brassica", "; 1 - sec\n;;\ta / b"),
        ({"index": "1", "section": "sec", "citation": "citation text","rules": [{"input": "a", "output": "b"}]}, "asca", "@ 1 - sec\n# citation: citation text\n\ta > b"),
        ({"index": "1", "section": "sec", "citation": "citation text","rules": [{"input": "a", "output": "b"}]}, "brassica", "; 1 - sec\n; citation: citation text\na / b"),
        ({"index": "1", "section": "sec", "comment": "comment text","rules": [{"input": "a", "output": "b"}]}, "asca", "@ 1 - sec\n\t# comment text\n\ta > b"),
        ({"index": "1", "section": "sec", "comment": "comment text","rules": [{"input": "a", "output": "b"}]}, "brassica", "; 1 - sec\n; comment text\na / b"),
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
        ({"index": "1", "section": "sec", "rules": [{"input": "a", "output": "b"}]}, "invalid"),
        ({"index": "1", "section": "sec", "rules": [{"input": "a"}]}, "asca"),
        ({"index": "1", "section": "sec", "rules": [{"output": "b"}]}, "brassica"),
    ],
)
def test_SoundChangeRuleSet_invalid_input(section, format):
    with pytest.raises(ValueError):
        SoundChangeRuleSet(section, format)
        

def test_DebugRules():
    rules = DebugRules({"index": "1", "section": "sec", "rules": [{"input": "a", "output": "b"}]}, "asca")

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
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_asca_length_marks(text, expected):
    assert normalize_asca_length_marks(text) == expected


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


def test_rule_change_compiles_ejective_at_instantiation():
    part = RuleChange({"input": "tʃ:[+long]ʼ", "output": "tʃ:[+long]"}, "asca")
    assert part.value == "tʃ:[+long,+cg] > tʃ:[+long]"
    assert "ʼ" not in part.value
    assert part.input == "tʃ:[+long]ʼ"


def test_rule_change_compiles_length_at_instantiation():
    part = RuleChange({"input": "a(ː)", "output": "e(ː)"}, "asca")
    assert part.value == "a:[+long] > e:[+long]"
    assert "ː" not in part.value
    assert part.input == "a(ː)"


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
            {"input": "Vː", "output": "V", "env": "#C:[-front,+back,+hi,-lo][-voice]_C"},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_expanded_chain_fixtures():
    from conlanger.tools.asca_validator import validate_asca

    section = {
        "index": "1.0",
        "section": "Chain split",
        "rules": [
            {"input": "dʒ", "output": "tʃ"},
            {"input": "tʃ", "output": "ʃ"},
        ],
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
