"""Tests for compile-time ``compiler_config.yml`` series mappings (ticket 75)."""

from pathlib import Path

from conlanger.utils.file_io import load_compiler_config


def test_load_compiler_config_default_includes_pie_laryngeals():
    config = load_compiler_config()
    assert config.lookup_series_mapping("17.2", "h₁") == "h"
    assert config.lookup_series_mapping("17.2", "h₂") == "x"
    assert config.lookup_series_mapping("17.2", "h₃") == "ɣʷ"


def test_section_row_beats_global_on_longest_prefix(tmp_path: Path):
    path = tmp_path / "compiler_config.yml"
    path.write_text(
        "series_mappings:\n"
        "  global:\n"
        "    h₁: h\n"
        "    s₁: ʃ\n"
        "  sections:\n"
        "    - section: '17'\n"
        "      h₁: ɦ\n"
        "    - section: '17.10'\n"
        "      h₁: ʔ\n",
        encoding="utf-8",
    )
    config = load_compiler_config(path)
    assert config.lookup_series_mapping("17.10.1", "h₁") == "ʔ"
    assert config.lookup_series_mapping("17.2", "h₁") == "ɦ"
    assert config.lookup_series_mapping("6.1", "h₁") == "h"
    assert config.lookup_series_mapping("17.10", "s₁") == "ʃ"
    assert config.lookup_series_mapping("17.10", "s₂") is None


def test_load_compiler_config_skips_malformed_section_rows(tmp_path: Path):
    path = tmp_path / "compiler_config.yml"
    path.write_text(
        "series_mappings:\n"
        "  global:\n"
        "    h₁: h\n"
        "  sections:\n"
        "    - not-a-map\n"
        "    - h₁: ʔ\n"
        "    - section: '17.10'\n"
        "      h₁: ʔ\n",
        encoding="utf-8",
    )
    config = load_compiler_config(path)
    assert config.lookup_series_mapping("17.10", "h₁") == "ʔ"
    assert config.lookup_series_mapping("1", "h₁") == "h"


def test_overlay_path_is_ignored_until_merge_exists(tmp_path: Path):
    package = tmp_path / "compiler_config.yml"
    overlay = tmp_path / "overlay.yml"
    package.write_text(
        "series_mappings:\n  global:\n    h₁: h\n",
        encoding="utf-8",
    )
    overlay.write_text(
        "series_mappings:\n  global:\n    h₁: Q\n    s₁: ʃ\n",
        encoding="utf-8",
    )
    config = load_compiler_config(package, overlay_path=overlay)
    assert config.lookup_series_mapping("1", "h₁") == "h"
    assert config.lookup_series_mapping("1", "s₁") is None
