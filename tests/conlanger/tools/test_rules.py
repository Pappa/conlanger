import shutil
from pathlib import Path

import pytest

from conlanger.tools.rules import (
    DiachronicSeries,
    RuleCitation,
    RuleComment,
    SoundChangeRule,
)
from conlanger.utils.mappings import CompilerConfig


def test_diachronic_series_does_not_mutate_index_rules(fx_sample_group_mappings):
    section = {
        "index": "1.0",
        "section": "Test",
        "rules": [
            {
                "stages": ["f", "p"],
                "env": "#_V{Z,C[-voice],r}",
                "raw": "f → p / #_V{Z,C[-voice],r}",
                "source": "sample.html:1",
            }
        ],
    }
    assert section["rules"][0]["env"] == "#_V{Z,C[-voice],r}"
    rendered = str(DiachronicSeries(section, group_mappings=fx_sample_group_mappings))
    assert "[+cont]" in rendered


def test_sound_change_ruleset_applies_group_mappings_for_asca(fx_sample_group_mappings):
    section = {
        "index": "1.0",
        "section": "Test",
        "rules": [
            {
                "stages": ["f", "p"],
                "env": "#_V{Z,C[-voice],r}",
                "raw": "f → p / #_V{Z,C[-voice],r}",
                "source": "sample.html:1",
            }
        ],
    }
    rendered = str(DiachronicSeries(section, group_mappings=fx_sample_group_mappings))
    assert "[+cont]" in rendered
    assert "\tf > p / #_V{[+cont],C[-voice],r}" in rendered


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_phonological_ruleset_validates_labialized_class_letter_fixtures(
    fx_sample_group_mappings,
):
    section = {
        "index": "17.10",
        "section": "PIE labiovelars",
        "rules": [
            {
                "stages": ["Kʷ", "K"],
                "env": "",
                "raw": "Kʷ → K",
                "source": "index_diachronica.html:334",
            },
            {
                "stages": ["i", "ə"],
                "env": "{P,K(ʷ),s}_",
                "raw": "i → ə / {P,K(ʷ),s}_",
                "source": "index_diachronica.html:7340",
            },
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    from conlanger.appliers.asca import validate_asca

    validate_asca(
        DiachronicSeries(section, group_mappings=fx_sample_group_mappings),
        probe_words=probe,
    )


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_diachronic_series_validates_known_unknown_grouping_fixtures(
    fx_sample_group_mappings,
):
    section = {
        "index": "6.2.2.1.2",
        "section": "Proto-Boreafrasian to Egypto-Berber",
        "rules": [
            {
                "input": "f",
                "output": "p",
                "env": "#_V{Z,C[-voice],r}",
                "raw": "f → p / #_V{Z,C[-voice],r}",
                "source": "index_diachronica_original.html:1261",
            },
            {
                "stages": ["ʕ", "i"],
                "env": "#_VR",
                "raw": "ʕ → i / #_VR",
                "source": "index_diachronica_original.html:1274",
            },
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    from conlanger.appliers.asca import validate_asca

    validate_asca(
        DiachronicSeries(section, group_mappings=fx_sample_group_mappings),
        probe_words=probe,
    )


@pytest.mark.parametrize(
    "section, expected",
    [
        (
            {
                "index": "1",
                "section": "sec",
                "rules": [{"stages": ["a", "b"], "env": "c", "exception": "d"}],
            },
            "@ 1 - sec\n\ta > b / c // d\n",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "rules": [
                    {
                        "status": "skipped",
                        "stages": ["a", "b"],
                        "raw": "a → b",
                    }
                ],
            },
            "@ 1 - sec\n#\ta → b\n",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "citation": "citation text",
                "rules": [{"stages": ["a", "b"]}],
            },
            "@ 1 - sec\n# citation: citation text\n\ta > b\n",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "comment": "comment text",
                "rules": [{"stages": ["a", "b"]}],
            },
            "@ 1 - sec\n\t# comment text\n\ta > b\n",
        ),
        ({"index": "1", "section": "sec"}, "@ 1 - sec\n"),
        (
            {
                "index": "9.9.9",
                "section": "Skipped",
                "status": "skipped",
                "rules": [{"stages": ["a", "b"], "raw": "a → b", "source": "x:1"}],
            },
            "@ 9.9.9 - Skipped\n",
        ),
        (
            {
                "index": "6.1",
                "section": "Test",
                "rules": [{"stages": ["Vː", "V"], "env": "#C_C"}],
            },
            "@ 6.1 - Test\n\tV:[+long] > V / #C_C\n",
        ),
        (
            {
                "index": "1",
                "section": "sec",
                "comment": "section note",
                "rules": [{"stages": ["a", "b"]}],
            },
            "@ 1 - sec\n\t# section note\n\ta > b\n",
        ),
    ],
)
def test_DiachronicSeries(section, expected):
    ruleset = DiachronicSeries(section)
    assert str(ruleset) == expected


def test_sound_change_rule_comments_raw_when_status_skipped():
    rule = SoundChangeRule(status="skipped", raw="a → b")
    assert str(rule) == "#\ta → b"


def test_diachronic_series_ignores_boolean_skip_fields():
    section = {
        "index": "1",
        "section": "sec",
        "skipped": True,
        "rules": [{"stages": ["a", "b"], "skip": True, "raw": "a → b"}],
    }
    assert str(DiachronicSeries(section)) == "@ 1 - sec\n\ta > b\n"


def test_diachronic_series_applies_section_series_mappings():
    config = CompilerConfig(
        series_mappings_global={"h₁": "h"},
        series_mappings_sections={"17.10": {"h₁": "ʔ"}},
    )
    section = {
        "index": "17.10",
        "section": "test",
        "rules": [{"stages": ["h₁", "a"], "raw": "h₁ → a", "source": "t:1"}],
    }
    rendered = str(DiachronicSeries(section, compiler_config=config))
    assert "ʔ > a" in rendered


@pytest.mark.parametrize(
    "section, format",
    [
        (
            {"index": "1", "section": "sec", "rules": [{"stages": ["a", "b"]}]},
            "invalid",
        ),
        (
            {"index": "1", "section": "sec", "rules": [{"stages": ["a", "b"]}]},
            "brassica",
        ),
    ],
)
def test_DiachronicSeries_invalid_format(section, format):
    with pytest.raises(ValueError, match="Unsupported format"):
        DiachronicSeries(section, format)


@pytest.mark.parametrize(
    "value, expected",
    [
        ("citation text", "# citation: citation text"),
    ],
)
def test_RuleCitation(value, expected):
    rule = RuleCitation(value)
    assert str(rule) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("comment text", "\t# comment text"),
    ],
)
def test_RuleComment(value, expected):
    rule = RuleComment(value)
    assert str(rule) == expected


@pytest.mark.parametrize(
    "fields, expected",
    [
        ({"input": "a", "output": "b"}, "\ta > b"),
        (
            {"input": "tʃ:[+long]ʼ", "output": "tʃ:[+long]"},
            "\ttʃ:[+long,+cg] > tʃ:[+long]",
        ),
        (
            {"input": "{O:[+delrel],O\u2019}", "output": "F", "env": "_$"},
            "\t{O:[+delrel],O:[+cg]} > F / _$",
        ),
        ({"input": "a(ː)", "output": "e(ː)"}, "\ta:[+long] > e:[+long]"),
        ({"input": "o", "output": "u", "env": "_(C…)i"}, "\to > u / _(C,0)i"),
        ({"input": "dʒ", "output": "tʃ > ʃ"}, "\tdʒ > tʃ > ʃ"),
        ({"input": "c ɲ", "output": "∅ n"}, "\tc ɲ > n"),
        (
            {"input": "∅ ʃ", "output": "k ʃ", "env": "V_$#"},
            "\tʃ > k ʃ / V_$#",
        ),
        (
            {"input": "k ʃ", "output": "∅ ʃ", "env": "V_V"},
            "\tk ʃ > ʃ / V_V",
        ),
        (
            {"input": "ɡ", "output": "∅", "env": "V_(VC…)V"},
            "\tɡ > ∅ / V_(VC,0)V",
        ),
        ({"input": "∅", "output": "x"}, "\t∅ > x"),
        ({"input": "a", "output": "æ", "env": "{i_,iC_}"}, "\ta > æ / :{i_,iC_}:"),
    ],
    ids=[
        "basic",
        "ejective_long",
        "grouping_ellipsis",
        "length_marker",
        "optional_grouping_ellipsis_env",
        "chained_output",
        "parallel_column_output_null",
        "parallel_column_input_null",
        "parallel_column_output_null_with_env",
        "pure_deletion",
        "pure_insertion",
        "environment_set",
    ],
)
def test_SoundChangeRule(fields, expected):
    rule = SoundChangeRule(**fields)
    assert str(rule) == expected


@pytest.mark.parametrize(
    "fields, expected_values",
    [
        (
            {"input": "{r,h}", "output": "{∅,h}"},
            ["r > ∅", "h > h"],
        ),
        (
            {"input": "{m,ɲ} n", "output": "{ɲ,∅} {ŋ,∅}", "env": "_#"},
            ["m n > ɲ ŋ / _#", "ɲ n > ∅ / _#"],
        ),
        (
            {"input": "d", "output": "{∅,ð}", "env": "V_V"},
            ["d > ∅ / V_V", "d > ð / V_V"],
        ),
    ],
    ids=[
        "paired_null_set",
        "multi_column_null_set",
        "optional_output_over_parallel_null",
    ],
)
def test_sound_change_rule_parallel_null_alternatives(fields, expected_values):
    rule = SoundChangeRule(**fields)
    assert len(rule.alternatives) == len(expected_values)
    assert [alt.value for alt in rule.alternatives] == expected_values
    for alt in rule.alternatives:
        assert alt.alternatives == []


def test_diachronic_series_parallel_column_from_stages():
    section = {
        "index": "10.3.9.2",
        "section": "Proto-Utupua to Nebao",
        "rules": [{"stages": ["c ɲ", "∅ n"]}],
    }
    ruleset = DiachronicSeries(section, "asca")
    rule_parts = [part for part in ruleset._parts if isinstance(part, SoundChangeRule)]
    assert len(rule_parts) == 1
    assert rule_parts[0].value == "c ɲ > n"


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_rule_parallel_null_alternatives_validate_independently():
    from conlanger.appliers.asca import validate_asca

    probe = Path("tests/fixtures/asca_probe_words.wsca")
    rule = SoundChangeRule(input="{r,h}", output="{∅,h}")
    for alt in rule.alternatives:
        section = {
            "index": "10.1.1.1",
            "section": "Balinese",
            "rules": [{"stages": [alt.input, alt.output]}],
        }
        validate_asca(DiachronicSeries(section), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_length_marker_fixtures():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "6.1",
        "section": "Proto-Afro-Asiatic to Proto-Omotic",
        "rules": [
            {"stages": ["a(ː)", "e(ː)"], "env": "_{ʕ,q}$"},
            {
                "stages": ["Vː", "V"],
                "env": "#C:[-front,+back,+hi,-lo][-voice]_C",
            },
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_tilde_notation_fixtures():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "9.1.2.2",
        "section": "Middle Vietnamese to Saigon Vietnamese",
        "rules": [
            {"stages": ["{β,w}", "bj~vj~v"]},
            {"stages": ["ɣ", "ɣ~ɡ"]},
            {"stages": ["ts", "{ts~tsʰ,ts,s}"]},
            {"stages": ["ʃ(~ʃ:[+long]) ʒ", "sʲ sʲ"]},
            {"stages": ["h", "j~ʔ"], "env": "_ V:[+front]"},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_expanded_chain_fixtures():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "1.0",
        "section": "Chain",
        "rules": [{"stages": ["dʒ", "tʃ > ʃ"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_ejective_marker_fixtures():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "11.5.1",
        "section": "Proto-Lezgic to Agul",
        "rules": [
            {"stages": ["tʃ:[+long]ʼ", "tʃ:[+long]"]},
            {"stages": ["dʒ", "{tʃ:[+long]ʼ,dʒ}"]},
            {"stages": ["dʼ", "tʼ"]},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_optional_grouping_ellipsis_fixtures():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "33.1.1.4",
        "section": "Proto-Costanoan to Rumsen",
        "rules": [
            {"stages": ["o", "u"], "env": "_(C…)i"},
            {"stages": ["ə", "a"], "env": "_(C…)#"},
            {"stages": ["o", "u"], "exception": "o(C…)_(C…)#"},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_extended_grouping_ellipsis_fixtures():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "17.12.1.1.6",
        "section": "Extended grouping ellipsis",
        "rules": [
            {"stages": ["ɡ", "∅"], "env": "V_(VC…)V"},
            {"stages": ["V", "V:[+long]"], "env": "ə(C…?)_"},
            {"stages": ["C", "C:[+long]"], "env": "_V(…V)"},
            {
                "stages": ["i u", "e o"],
                "env": "_C(…C){a:[+long],e:[+long],o:[+long]}",
            },
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sound_change_ruleset_validates_em_dash_rule_marker_fixtures():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "6.2.2.1.18",
        "section": "Proto-Semitic to Biblical Hebrew",
        "rules": [
            {"stages": ["aː", "oː"], "exception": "_#"},
            {"stages": ["j w", "i u"], "env": "#_CV"},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)
