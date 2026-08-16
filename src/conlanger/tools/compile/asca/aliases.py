"""PIE laryngeal alias substitution."""

PIE_LARYNGEAL_ALIASES = {
    "h₁": "h",
    "h₂": "x",
    "h₃": "ɣʷ",
}


def apply_asca_aliases(text: str) -> str:
    for alias, replacement in PIE_LARYNGEAL_ALIASES.items():
        text = text.replace(alias, replacement)
    return text
