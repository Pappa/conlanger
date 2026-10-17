"""Tests for ``compiled_rules_yaml``."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from conlanger.compile.models.config import CompilerConfig
from conlanger.compile.models.rules import SoundChangeRule
from conlanger.tools.compiled_rules_yaml import (
    COMPILED_RULES_SCHEMA_VERSION,
    COMPILED_RULES_YAML_NAME,
    _skipped_rule_line,
    build_asca_rules_document,
    compiled_rule_entry,
    read_compiled_rules_yaml,
    write_compiled_rules_yaml,
)
from conlanger.tools.index_inventory import IndexRuleInventoryBundle
from conlanger.tools.inventory_targets import (
    InventoryTarget,
    resolve_inventory_targets,
)
from tests.conlanger.tools.test_sporadic_sampling import _RecordingRandom

_SECTION = {"index": "1.0", "section": "Test"}


def _bundle(
    rule: dict,
    *,
    rule_id: str = "r0",
    targets: list[InventoryTarget] | None = None,
) -> IndexRuleInventoryBundle:
    if targets is None:
        targets = resolve_inventory_targets(_SECTION, rule, rule_id)
    return IndexRuleInventoryBundle(
        section=_SECTION,
        rule=rule,
        rule_id=rule_id,
        rows=[],
        targets=targets,
    )


def test_compiled_rule_entry_single_target():
    rule = {"stages": ["a", "b"], "source": "s:1"}
    entry = compiled_rule_entry(
        rule,
        rule_id="r0",
        source="s:1",
        targets=resolve_inventory_targets(_SECTION, rule, "r0"),
        section=_SECTION,
    )
    assert entry["rule_id"] == "r0"
    assert entry["source"] == "s:1"
    assert len(entry["targets"]) == 1
    assert entry["targets"][0]["rule"] == "a > b"
    assert "valid" not in entry


def test_compiled_rule_entry_alternatives_and_steps():
    alt_rule = {"stages": ["d", "{∅,ð}"], "env": "V_V", "source": "s:1"}
    alt_entry = compiled_rule_entry(
        alt_rule,
        rule_id="opt",
        source="s:1",
        targets=resolve_inventory_targets(_SECTION, alt_rule, "opt"),
        section=_SECTION,
    )
    assert len(alt_entry["targets"]) == 2
    assert alt_entry["targets"][0]["alt_idx"] == 0
    assert alt_entry["targets"][1]["alt_idx"] == 1

    chain_rule = {"stages": ["p", "t", "k"], "source": "s:2"}
    chain_entry = compiled_rule_entry(
        chain_rule,
        rule_id="chain",
        source="s:2",
        targets=resolve_inventory_targets(_SECTION, chain_rule, "chain"),
        section=_SECTION,
    )
    assert len(chain_entry["targets"]) == 2
    assert chain_entry["targets"][0]["step_idx"] == 0
    assert chain_entry["targets"][1]["step_idx"] == 1


def test_compiled_rule_entry_skipped_rule_line():
    rule = {
        "stages": ["x", "y"],
        "raw": "x → y",
        "status": "skipped",
        "source": "s:1",
    }
    entry = compiled_rule_entry(
        rule,
        rule_id="hold",
        source="s:1",
        targets=[InventoryTarget()],
        section=_SECTION,
    )
    assert entry["status"] == "skipped"
    assert entry["rule"] == "#\tx → y"


def test_build_document_omits_section_skipped():
    skipped_bundle = IndexRuleInventoryBundle(
        section={
            "index": "9",
            "section": "Skipped",
            "status": "skipped",
        },
        rule={"stages": ["a", "b"], "rule_id": "x"},
        rule_id="x",
        rows=[],
        targets=[InventoryTarget()],
    )
    active = _bundle(
        {"stages": ["a", "b"], "rule_id": "active", "source": "s:1"},
        rule_id="active",
    )
    doc = build_asca_rules_document([skipped_bundle, active])
    assert doc["schema_version"] == COMPILED_RULES_SCHEMA_VERSION
    assert len(doc["sections"]) == 1
    assert doc["sections"][0]["rules"][0]["rule_id"] == "active"


def test_compiled_rule_entry_format_error():
    entry = compiled_rule_entry(
        {"stages": ["a", "b"], "source": "s:1"},
        rule_id="bad",
        source="s:1",
        targets=[
            InventoryTarget(format_error="format_error: missing stages"),
        ],
        section=_SECTION,
    )
    assert entry["compile_error"] == "missing stages"


def test_skipped_rule_line_compiles_active_rule_shape():
    line = _skipped_rule_line(
        _SECTION,
        {"stages": ["a", "b"], "raw": "a → b"},
        "r0",
        compiler_config=None,
    )
    assert line == "a > b"


def test_build_document_target_format_error():
    bundle = _bundle(
        {"stages": ["a", "b"], "rule_id": "bad", "source": "s:1"},
        rule_id="bad",
        targets=[
            InventoryTarget(format_error="format_error: no compile steps"),
        ],
    )
    doc = build_asca_rules_document([bundle])
    assert doc["sections"][0]["rules"][0]["compile_error"] == "no compile steps"


def test_compiled_rule_entry_sporadic_skip():
    sporadic_rule = SoundChangeRule(
        input="p",
        output="h",
        env="V_V",
        sporadic=True,
        compiler_config=CompilerConfig(sample_sporadic=True, sample_dialect=True),
        rng=_RecordingRandom(random_values=[0.9]),
    )
    bundle = IndexRuleInventoryBundle(
        section=_SECTION,
        rule={
            "stages": ["p", "h"],
            "env": "V_V",
            "sporadic": True,
            "rule_id": "sp",
            "source": "s:1",
        },
        rule_id="sp",
        rows=[],
        targets=[InventoryTarget.model_construct(field_rule=sporadic_rule)],
    )
    doc = build_asca_rules_document([bundle])
    skipped = doc["sections"][0]["rules"][0]
    assert skipped["status"] == "compile_skipped"
    assert skipped["rule"] == "#\tp > h / V_V"


def test_build_document_multiple_sections():
    other_section = {"index": "2.0", "section": "Other"}
    doc = build_asca_rules_document(
        [
            _bundle({"stages": ["a", "b"], "rule_id": "r0", "source": "s:1"}),
            IndexRuleInventoryBundle(
                section=other_section,
                rule={"stages": ["c", "d"], "rule_id": "r1", "source": "s:2"},
                rule_id="r1",
                rows=[],
                targets=resolve_inventory_targets(
                    other_section, {"stages": ["c", "d"]}, "r1"
                ),
            ),
        ]
    )
    assert [section["index"] for section in doc["sections"]] == ["1.0", "2.0"]


def test_write_compiled_rules_yaml_smoke(tmp_path: Path):
    doc = build_asca_rules_document(
        [_bundle({"stages": ["a", "b"], "rule_id": "r0", "source": "s:1"})]
    )
    path = tmp_path / COMPILED_RULES_YAML_NAME
    write_compiled_rules_yaml(doc, path)
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == COMPILED_RULES_SCHEMA_VERSION
    target = loaded["sections"][0]["rules"][0]["targets"][0]
    assert target["rule"] == "a > b"
    assert "series" not in target


def test_read_compiled_rules_yaml_rejects_bad_document(tmp_path: Path):
    path = tmp_path / "bad.yml"
    path.write_text("not a mapping\n", encoding="utf-8")
    with pytest.raises(TypeError, match="mapping"):
        read_compiled_rules_yaml(path)

    path.write_text("schema_version: 99\nsections: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="schema_version"):
        read_compiled_rules_yaml(path)


def test_compiled_rule_entry_no_targets():
    entry = compiled_rule_entry(
        {"stages": ["a", "b"]},
        rule_id="empty",
        source="s:1",
        targets=[],
        section=_SECTION,
    )
    assert entry["compile_error"] == "no compile targets"
