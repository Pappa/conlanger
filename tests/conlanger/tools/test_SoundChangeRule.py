import pytest
from conlanger.tools.SoundChangeRule import SoundChangeRule, DebugRules, RuleCitation, RuleComment

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
def test_SoundChangeRule(section, format, expected):
    rule = SoundChangeRule(section, format)
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
def test_SoundChangeRule_invalid_input(section, format):
    with pytest.raises(ValueError):
        SoundChangeRule(section, format)
        

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