"""``asca_rules.yml`` v4 per-rule shapes: decomposed fields plus ``rule`` / ``steps`` / ``alternatives``."""

from __future__ import annotations

from typing import Any

from conlanger.compile.models.compile_fields import RuleEnv, RuleInput, RuleOutput
from conlanger.tools.compiled_target_serde import inventory_target_from_yaml
from conlanger.tools.inventory_targets import InventoryTarget

CompiledStepItem = dict[str, Any]
AlternativeItem = dict[str, Any]


def _compiled_segment_value(
    part: RuleInput | RuleOutput | RuleEnv | None,
) -> str | None:
    if part is None:
        return None
    text = (part.compiled or part.raw or "").strip()
    return text or None


def target_to_compiled_object(target: InventoryTarget) -> dict[str, Any]:
    """Serialize one compile target to v4 decomposed fields plus joined ``rule``."""
    rule = target.field_rule
    if rule is not None:
        obj: dict[str, Any] = {}
        for key, part in (
            ("input", rule.input),
            ("output", rule.output),
            ("env", rule.env),
            ("exception", rule.exception),
        ):
            value = _compiled_segment_value(part)
            if value is not None:
                obj[key] = value
        obj["rule"] = str(rule).strip().lstrip("\t")
        return obj
    if target.asca_rule:
        return {"rule": target.asca_rule.strip()}
    msg = "compile target missing ASCA rule line"
    raise ValueError(msg)


def target_rule_line(target: InventoryTarget) -> str:
    return target_to_compiled_object(target)["rule"]


def _compiled_rule_line(item: Any) -> str:
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        rule = item.get("rule")
        if rule is not None:
            return str(rule).strip()
        msg = "compiled object missing rule line"
        raise ValueError(msg)
    msg = f"invalid compiled item type: {type(item)!r}"
    raise TypeError(msg)


def _ok_targets(targets: list[InventoryTarget]) -> list[InventoryTarget]:
    return [t for t in targets if t.format_error is None and t.field_rule is not None]


def _group_targets_by_step(
    targets: list[InventoryTarget],
) -> list[list[InventoryTarget]]:
    ok = _ok_targets(targets)
    if not ok:
        return []
    groups: list[list[InventoryTarget]] = [[ok[0]]]
    for target in ok[1:]:
        if target.step_idx == groups[-1][0].step_idx:
            groups[-1].append(target)
        else:
            groups.append([target])
    return groups


def _ordered_by_alt_idx(group: list[InventoryTarget]) -> list[InventoryTarget]:
    return sorted(group, key=lambda t: (t.alt_idx is None, t.alt_idx or 0))


def _is_correlated_branch_chain(step_groups: list[list[InventoryTarget]]) -> bool:
    """True when each chain stage has the same optional-output branch count."""
    if len(step_groups) < 2:
        return False
    sizes = [len(group) for group in step_groups]
    if not all(size > 1 for size in sizes):
        return False
    if len(set(sizes)) != 1:
        return False
    branch_count = sizes[0]
    for group in step_groups:
        ordered = _ordered_by_alt_idx(group)
        if len(ordered) != branch_count:
            return False
        for branch_idx, target in enumerate(ordered):
            if target.alt_idx is not None and target.alt_idx != branch_idx:
                return False
    return True


def _correlated_branches_yaml(
    step_groups: list[list[InventoryTarget]],
) -> dict[str, Any]:
    branch_count = len(step_groups[0])
    branches: list[dict[str, list[dict[str, Any]]]] = []
    for branch_idx in range(branch_count):
        steps = [
            target_to_compiled_object(_ordered_by_alt_idx(group)[branch_idx])
            for group in step_groups
        ]
        branches.append({"steps": steps})
    return {"alternatives": branches}


def _step_group_to_yaml_item(group: list[InventoryTarget]) -> CompiledStepItem:
    ordered = _ordered_by_alt_idx(group)
    if len(ordered) == 1:
        return target_to_compiled_object(ordered[0])
    return {"alternatives": [target_to_compiled_object(t) for t in ordered]}


def inventory_targets_to_compiled_fields(
    targets: list[InventoryTarget],
) -> dict[str, Any]:
    """Map compile targets to exactly one of top-level fields, ``alternatives``, or ``steps``."""
    groups = _group_targets_by_step(targets)
    if not groups:
        return {}

    if _is_correlated_branch_chain(groups):
        return _correlated_branches_yaml(groups)

    step_items: list[CompiledStepItem] = [_step_group_to_yaml_item(g) for g in groups]
    if len(step_items) == 1 and "alternatives" not in step_items[0]:
        return dict(step_items[0])
    if len(step_items) == 1:
        return {"alternatives": step_items[0]["alternatives"]}
    return {"steps": step_items}


def _alternative_item_validation_specs(
    alt_idx: int,
    item: Any,
) -> list[tuple[str, int | None, int | None]]:
    if isinstance(item, str):
        return [(item.strip(), None, alt_idx)]
    if isinstance(item, dict):
        steps = item.get("steps")
        if isinstance(steps, list):
            return [
                (_compiled_rule_line(line), step_idx, alt_idx)
                for step_idx, line in enumerate(steps)
            ]
        if "rule" in item:
            return [(_compiled_rule_line(item), None, alt_idx)]
        msg = "alternative branch must include a steps list or rule object"
        raise TypeError(msg)
    msg = f"invalid alternatives item type: {type(item)!r}"
    raise TypeError(msg)


def _step_item_validation_specs(
    step_idx: int,
    item: Any,
) -> list[tuple[str, int | None, int | None]]:
    if isinstance(item, str):
        return [(item.strip(), step_idx, None)]
    if isinstance(item, list):
        return [
            (_compiled_rule_line(line), step_idx, branch_idx)
            for branch_idx, line in enumerate(item)
        ]
    if isinstance(item, dict):
        alts = item.get("alternatives")
        if isinstance(alts, list):
            return [
                (_compiled_rule_line(line), step_idx, branch_idx)
                for branch_idx, line in enumerate(alts)
            ]
        if "rule" in item:
            return [(_compiled_rule_line(item), step_idx, None)]
        msg = "step item must be a rule object or alternatives block"
        raise TypeError(msg)
    msg = f"invalid steps item type: {type(item)!r}"
    raise TypeError(msg)


def compiled_rule_validation_specs(
    rule_entry: dict[str, Any],
) -> list[tuple[str, int | None, int | None]]:
    """Return ASCA lines with inventory ``step_idx`` / ``alt_idx`` for validation."""
    if rule_entry.get("targets"):
        specs: list[tuple[str, int | None, int | None]] = []
        for yaml_target in rule_entry["targets"]:
            target = inventory_target_from_yaml(yaml_target)
            line = (target.asca_rule or "").strip()
            if not line:
                msg = "compiled target missing rule line"
                raise ValueError(msg)
            specs.append((line, target.step_idx, target.alt_idx))
        return specs

    has_steps = "steps" in rule_entry
    has_alternatives = "alternatives" in rule_entry
    if has_steps and has_alternatives:
        msg = "compiled rule must have exactly one of rule, alternatives, or steps"
        raise ValueError(msg)
    if has_steps:
        if "rule" in rule_entry and "input" not in rule_entry:
            msg = "compiled rule must have exactly one of rule, alternatives, or steps"
            raise ValueError(msg)
        specs = []
        for step_idx, item in enumerate(rule_entry["steps"] or []):
            specs.extend(_step_item_validation_specs(step_idx, item))
        return specs
    if has_alternatives:
        if "rule" in rule_entry and "input" not in rule_entry:
            msg = "compiled rule must have exactly one of rule, alternatives, or steps"
            raise ValueError(msg)
        specs: list[tuple[str, int | None, int | None]] = []
        for alt_idx, item in enumerate(rule_entry["alternatives"] or []):
            specs.extend(_alternative_item_validation_specs(alt_idx, item))
        return specs
    if "rule" in rule_entry:
        return [(_compiled_rule_line(rule_entry), None, None)]

    msg = "compiled rule must have exactly one of rule, alternatives, or steps"
    raise ValueError(msg)
