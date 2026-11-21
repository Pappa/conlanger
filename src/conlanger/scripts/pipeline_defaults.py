"""Shared default paths for Index Diachronica pipeline operator scripts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

DEFAULT_HTML = ROOT / "data" / "diachronica" / "index_diachronica.html"
DEFAULT_YAML = ROOT / "data" / "diachronica" / "index_diachronica.yml"
DEFAULT_DIAGNOSTICS_DIR = ROOT / "diagnostics"
DEFAULT_INVENTORY_DIR = ROOT / DEFAULT_DIAGNOSTICS_DIR / "inventory"
DEFAULT_PARSE_DIR = ROOT / DEFAULT_DIAGNOSTICS_DIR / "parse"
DEFAULT_COMPILE_DIR = ROOT / DEFAULT_DIAGNOSTICS_DIR / "compile"
DEFAULT_COMPILED_YAML = DEFAULT_COMPILE_DIR / "asca_rules.yml"
DEFAULT_PROBE = ROOT / "tests" / "fixtures" / "asca_probe_words.wsca"


def path_for_operator_message(path: Path) -> str:
    """Repo-relative path when under ``ROOT``, else resolved absolute.

    CLI paths are often relative strings; resolve against cwd before comparing to ``ROOT``.
    """
    resolved = path.resolve()
    root = ROOT.resolve()
    if resolved.is_relative_to(root):
        return str(resolved.relative_to(root))
    return str(resolved)
