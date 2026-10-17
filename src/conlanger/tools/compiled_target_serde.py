"""Serialize and deserialize compiled inventory targets for ``asca_rules.yml`` v1."""

from __future__ import annotations

import random
from typing import Any

from conlanger.compile.models.compile_fields import RuleEnv, RuleInput, RuleOutput
from conlanger.compile.models.config import CompilerConfig
from conlanger.compile.models.rules import (
    DiachronicSeries,
    RuleCitation,
    RuleComment,
    RulePartBase,
    RuleTitle,
    SoundChangeRule,
)
from conlanger.tools.inventory_targets import InventoryTarget


def _serialize_rule_part(part: RulePartBase) -> dict[str, Any]:
    if isinstance(part, RuleTitle):
        index, section = part.value.split(" - ", 1)
        return {"type": "title", "index": index, "section": section}
    if isinstance(part, RuleCitation):
        return {"type": "citation", "value": part.value}
    if isinstance(part, RuleComment):
        return {"type": "comment", "value": part.value}
    if isinstance(part, SoundChangeRule):
        payload = part.model_dump(
            exclude={
                "compiler_config",
                "rng",
                "alternatives",
                "detect_alternatives",
            }
        )
        payload["type"] = "sound_change_rule"
        return payload
    msg = f"unsupported rule part type: {type(part)!r}"
    raise TypeError(msg)


def _deserialize_rule_part(data: dict[str, Any]) -> RulePartBase:
    kind = data.get("type")
    if kind == "title":
        return RuleTitle(str(data["index"]), str(data["section"]))
    if kind == "citation":
        return RuleCitation(str(data.get("value", "")))
    if kind == "comment":
        return RuleComment(str(data.get("value", "")))
    if kind == "sound_change_rule":
        part_data = {key: value for key, value in data.items() if key != "type"}

        def _field_model(
            name: str, cls: type[RuleInput | RuleOutput | RuleEnv]
        ) -> None:
            field_value = part_data.get(name)
            if field_value is None:
                return
            if isinstance(field_value, dict):
                if field_value.get("compiled") is None:
                    field_value = {
                        **field_value,
                        "compiled": field_value.get("raw") or "",
                    }
                part_data[name] = cls.model_validate(field_value)

        _field_model("input", RuleInput)
        _field_model("output", RuleOutput)
        _field_model("env", RuleEnv)
        _field_model("exception", RuleEnv)

        return SoundChangeRule.model_construct(
            **part_data,
            detect_alternatives=False,
            alternatives=[],
            compiler_config=CompilerConfig(),
            rng=random.Random(0),
        )
    msg = f"unsupported compiled part type: {kind!r}"
    raise ValueError(msg)


def serialize_series(series: DiachronicSeries) -> dict[str, Any]:
    return {"parts": [_serialize_rule_part(part) for part in series.parts]}


def deserialize_series(data: dict[str, Any]) -> DiachronicSeries:
    parts = [_deserialize_rule_part(part) for part in data.get("parts") or []]
    return DiachronicSeries.from_parts(parts)


def sound_change_rule_from_series(series: DiachronicSeries) -> SoundChangeRule | None:
    for part in series.parts:
        if isinstance(part, SoundChangeRule):
            return part
    return None


def inventory_target_to_yaml(target: InventoryTarget) -> dict[str, Any]:
    if target.series is None or target.field_rule is None:
        msg = "compile target missing series or field rule"
        raise ValueError(msg)
    rule_line = str(target.field_rule).strip()
    return {
        "step_idx": target.step_idx,
        "alt_idx": target.alt_idx,
        "rule": rule_line,
        "series": serialize_series(target.series),
    }


def inventory_target_from_yaml(data: dict[str, Any]) -> InventoryTarget:
    series = deserialize_series(data["series"])
    field_rule = sound_change_rule_from_series(series)
    return InventoryTarget.model_construct(
        alt_idx=data.get("alt_idx"),
        series=series,
        field_rule=field_rule,
        step_idx=data.get("step_idx"),
    )
