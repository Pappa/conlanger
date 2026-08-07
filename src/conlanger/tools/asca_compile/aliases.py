"""PIE laryngeal alias substitution."""

_ALIASES = {
    "h₁": "h",
    "h₂": "x",
    "h₃": "ɣʷ",
}


def apply_asca_aliases(text: str) -> str:
    for alias, replacement in _ALIASES.items():
        text = text.replace(alias, replacement)
    return text
