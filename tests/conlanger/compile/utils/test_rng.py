"""Compile RNG helper from ``CompilerConfig.seed`` (ticket 0055)."""

from conlanger.compile.models.config import CompilerConfig
from conlanger.compile.models.rules import DiachronicSeries
from conlanger.compile.utils.rng import rng_for_compile_config


def test_seeded_compile_optional_output_is_reproducible():
    section = {
        "index": "1",
        "section": "sec",
        "rules": [{"stages": ["d", "{∅,ð}"], "env": "V_V"}],
    }
    config = CompilerConfig(seed=0)
    rng_a = rng_for_compile_config(config)
    rng_b = rng_for_compile_config(config)
    first = str(
        DiachronicSeries(section, compiler_config=config, rng=rng_a),
    )
    second = str(
        DiachronicSeries(section, compiler_config=config, rng=rng_b),
    )
    assert first == second


def test_rng_for_compile_config_seeded_matches_for_equal_seeds():
    a = rng_for_compile_config(CompilerConfig(seed=0))
    b = rng_for_compile_config(CompilerConfig(seed=0))
    assert a.random() == b.random()


def test_rng_for_compile_config_omitted_seed_is_unseeded():
    first = rng_for_compile_config(CompilerConfig())
    second = rng_for_compile_config(CompilerConfig())
    assert first.getstate() != second.getstate()
