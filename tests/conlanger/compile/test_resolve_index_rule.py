"""Compile-time projection of structured index env/exception fields."""

from __future__ import annotations

from conlanger.compile.models.config import CompilerConfig
from conlanger.compile.resolve_index_rule import materialize_index_rule_env_exception


def test_materialize_position_in_from_inventory_rule_shape():
    rule = {
        "rule_id": "Vowel-Shifts_3-em-emˀ_2",
        "env": {"position": {"in": "U[-stress]"}},
        "exception": "{p(’),m(ˀ)}_",
    }
    result = materialize_index_rule_env_exception(
        rule, compiler_config=CompilerConfig()
    )
    assert result["env"] == "in U[-stress]"
    assert result["exception"] == "{p(’),m(ˀ)}_"
