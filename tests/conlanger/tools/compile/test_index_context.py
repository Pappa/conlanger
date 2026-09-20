from conlanger.tools.compile.index_context import (
    env_exception_input_to_string,
    resolve_index_context_to_string,
)
from conlanger.tools.ingest.index_models import IndexContext
from conlanger.tools.rules import SoundChangeRule


def test_resolve_index_context_uses_context_string():
    ctx = IndexContext(context="#_", position={"adjacent_to": "C"})
    assert resolve_index_context_to_string(ctx) == "#_"


def test_resolve_index_context_adjacent_to_single_char():
    ctx = IndexContext(position={"adjacent_to": "C"})
    assert resolve_index_context_to_string(ctx) == "C_, _C"


def test_sound_change_rule_accepts_structured_env_dict():
    rule = SoundChangeRule(
        input="a",
        output="b",
        env={"context": "_#"},
    )
    assert rule.env is not None
    assert rule.env.raw == "_#"


def test_env_exception_input_to_string_passthrough():
    assert env_exception_input_to_string("_#") == "_#"


def test_resolve_index_context_adjacent_to_single_item_list():
    ctx = IndexContext(position={"adjacent_to": ["C"]})
    assert resolve_index_context_to_string(ctx) == "C_, _C"


def test_resolve_index_context_unhandled_position_returns_empty():
    ctx = IndexContext(position={"medial": True})
    assert resolve_index_context_to_string(ctx) == ""


def test_sound_change_rule_accepts_index_context_instance():
    rule = SoundChangeRule(
        input="a",
        output="b",
        env=IndexContext(context="_#"),
    )
    assert rule.env is not None
    assert rule.env.raw == "_#"


def test_env_exception_input_to_string_accepts_index_context():
    assert env_exception_input_to_string(IndexContext(context="_#")) == "_#"


def test_resolve_index_context_ignores_multi_char_adjacent_to():
    ctx = IndexContext(position={"adjacent_to": "CV"})
    assert resolve_index_context_to_string(ctx) == ""
