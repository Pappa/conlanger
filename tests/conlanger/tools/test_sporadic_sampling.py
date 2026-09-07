"""Sporadic apply/skip sampling on ``SoundChangeRule`` (ticket 68)."""

from __future__ import annotations

import random

from conlanger.tools.index_inventory import OK_TRUE, validate_index_rule
from conlanger.tools.rules import DiachronicSeries, SoundChangeRule


class _RecordingRandom(random.Random):
    """``Random`` subclass that records draw order for sporadic gate tests."""

    def __init__(
        self,
        *,
        random_values: list[float] | None = None,
        randrange_values: list[int] | None = None,
    ) -> None:
        super().__init__(0)
        self._random_values = list(random_values or [])
        self._randrange_values = list(randrange_values or [])
        self.calls: list[str | tuple[str, int]] = []

    def random(self) -> float:
        self.calls.append("random")
        return self._random_values.pop(0)

    def randrange(self, n: int) -> int:
        self.calls.append(("randrange", n))
        return self._randrange_values.pop(0)


def test_sporadic_skip_renders_commented_compiled_fields():
    """Only sporadic skip test: injected rng forces skip on the render path."""
    rng = _RecordingRandom(random_values=[0.9])
    rule = SoundChangeRule(
        input="p",
        output="h",
        env="V_V",
        sporadic=True,
        sample_sporadic=True,
        rng=rng,
    )
    assert rule.sporadic_skipped is True
    assert rng.calls == ["random"]
    assert str(rule) == "#\tp > h / V_V"


def test_sporadic_apply_renders_normally_with_sample_disabled():
    rule = SoundChangeRule(
        input="p",
        output="h",
        env="V_V",
        sporadic=True,
        sample_sporadic=False,
    )
    assert rule.sporadic_skipped is False
    assert str(rule) == "\tp > h / V_V"


def test_sporadic_gate_draws_before_optional_output_pick():
    rng = _RecordingRandom(random_values=[0.1], randrange_values=[1])
    rule = SoundChangeRule(
        input="d",
        output="{∅,ð}",
        env="V_V",
        sporadic=True,
        sample_sporadic=True,
        rng=rng,
    )
    assert rule.sporadic_skipped is False
    assert rng.calls == ["random", ("randrange", 2)]
    assert rule.value == rule.alternatives[1].value


def test_sporadic_render_is_frozen():
    rule = SoundChangeRule(
        input="p",
        output="h",
        sporadic=True,
        sample_sporadic=False,
    )
    first_render = str(rule)
    assert first_render == str(rule)


def test_diachronic_series_samples_sporadic_on_render_path():
    section = {
        "index": "1",
        "section": "sec",
        "rules": [{"stages": ["p", "h"], "sporadic": True, "env": "V_V"}],
    }
    rendered = str(
        DiachronicSeries(
            section,
            sample_sporadic=True,
            rng=random.Random(4),
        )
    )
    assert rendered.endswith("\tp > h / V_V\n")


def test_inventory_always_applies_sporadic_rules():
    section = {
        "index": "1",
        "section": "sec",
        "rules": [
            {
                "stages": ["p", "h"],
                "sporadic": True,
                "env": "V_V",
                "source": "test:1",
                "rule_id": "1",
            }
        ],
    }
    rule = section["rules"][0]
    rows = validate_index_rule(
        section,
        rule,
        "1",
        probe_words=None,
    )
    assert len(rows) == 1
    assert rows[0].ok == OK_TRUE
