"""Compile-time RNG from operator config."""

from __future__ import annotations

import random

from conlanger.compile.models.config import CompilerConfig


def rng_for_compile_config(config: CompilerConfig | None) -> random.Random:
    """Return compile RNG from ``config.seed``, or an unseeded generator when absent."""
    if config is not None and config.seed is not None:
        return random.Random(config.seed)
    return random.Random()
