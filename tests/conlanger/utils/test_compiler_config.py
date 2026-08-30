"""Tests for compile-time ``CompilerConfig`` series mappings (ticket 75)."""

from pathlib import Path

from conlanger.scripts.config_loaders import load_compiler_config


def test_overlay_path_not_supported(tmp_path: Path):
    """``load_compiler_config`` accepts only a single YAML path (ticket 101)."""
    package = tmp_path / "compiler_config.yml"
    package.write_text(
        "series_mappings:\n  global:\n    h₁: h\n",
        encoding="utf-8",
    )
    (tmp_path / "group_mappings.yml").write_text("{}\n", encoding="utf-8")
    config = load_compiler_config(package)
    assert config.lookup_series_mapping("1", "h₁") == "h"
