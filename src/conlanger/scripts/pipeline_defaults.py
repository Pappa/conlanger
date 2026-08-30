"""Shared default paths for Index Diachronica pipeline operator scripts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

DEFAULT_HTML = ROOT / "data" / "diachronica" / "index_diachronica_original.html"
DEFAULT_YAML = ROOT / "data" / "diachronica" / "index_diachronica_parsed.yml"
DEFAULT_INVENTORY_DIR = ROOT / ".scratch" / "cleaned-rule-index" / "inventory"
DEFAULT_PARSE_DIR = ROOT / ".scratch" / "cleaned-rule-index" / "parse"
DEFAULT_COMMENT_SUMMARY = DEFAULT_PARSE_DIR / "rule-comment-phrases.md"
DEFAULT_PROBE = ROOT / "tests" / "fixtures" / "asca_probe_words.wsca"
