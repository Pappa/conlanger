"""Index length marks → ASCA ``:[+long]`` feature notation.

Transforms (compile layer only; index ``raw`` unchanged per ADR-0010):

- ``segmentː`` / ``segment(ː)`` → ``segment:[+long]`` (ticket 15 collapse policy)
- ``{set}ː`` / ``{set}(ː)`` / bare ``ː`` set members → set or ``V:[+long]`` member
- ``Matrix]ː`` → ``Matrix, +long]`` (matrix-suffix length; ticket 79)

Parenthesized optional length ``(ː)`` on matrices/templates (``V:[+front](ː)``,
``V3(ː)``) is **out of scope** here — defer to optional-length / parenthetical
policy (tickets 15/48/71), not matrix-suffix collapse.

Hold-outs (Iroquoian stress meta — defer to ticket 64 follow-ons):

- ``ː2`` / ``1:[+stress] ː2``
- ``Vː:[+stress]`` inside complex stressed sets
"""

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT

_LENGTH = "\u02d0"
_IPA_SEGMENT = IPA_SEGMENT
_OPT_LENGTH_COMMA_RE = re.compile(rf"({_IPA_SEGMENT}|[A-Z])\({_LENGTH},([^)]+)\)")
_OPT_LENGTH_RE = re.compile(rf"({_IPA_SEGMENT}|[A-Z])\({_LENGTH}\)")
_SET_OPT_LENGTH_RE = re.compile(rf"\}}\({_LENGTH}\)")
_GROUPING_LENGTH_RE = re.compile(r"([A-Z])" + re.escape(_LENGTH) + r"(?!:)")
_REF_LENGTH_RE = re.compile(r"(\d)" + re.escape(_LENGTH))
_SEGMENT_LENGTH_RE = re.compile(rf"({_IPA_SEGMENT}){re.escape(_LENGTH)}(?!:)")
_SET_SUFFIX_LENGTH_RE = re.compile(r"\}" + re.escape(_LENGTH))
_DOUBLE_LENGTH_RE = re.compile(r":\[\+long\]" + re.escape(_LENGTH))
_BARE_SET_LENGTH_RE = re.compile(rf"(^|,)\s*{re.escape(_LENGTH)}(?=,|$)")
_POST_MATRIX_LENGTH_RE = re.compile(r"\]" + re.escape(_LENGTH))
_SYLLABLE_LENGTH_RE = re.compile(r"%" + re.escape(_LENGTH))


def _expand_bare_length_in_sets(text: str) -> str:
    if _LENGTH not in text:
        return text

    def repl(match: re.Match[str]) -> str:
        inner = _BARE_SET_LENGTH_RE.sub(r"\1V:[+long]", match.group(1))
        return "{" + inner + "}"

    return re.sub(r"\{([^}]*)\}", repl, text)


def normalize_asca_length_marks(text: str) -> str:
    """Map Index ``ː`` / ``(ː)`` length notation to ASCA ``:[+long]``."""
    if not text or (_LENGTH not in text and f"({_LENGTH})" not in text):
        return text
    text = _OPT_LENGTH_COMMA_RE.sub(r"{\1:[+long],\1\2}", text)
    text = _SET_OPT_LENGTH_RE.sub("}:[+long]", text)
    text = _OPT_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _GROUPING_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _REF_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _SEGMENT_LENGTH_RE.sub(r"\1:[+long]", text)
    text = _SYLLABLE_LENGTH_RE.sub("%:[+long]", text)
    text = _SET_SUFFIX_LENGTH_RE.sub("}:[+long]", text)
    text = _DOUBLE_LENGTH_RE.sub(":[+long]", text)
    text = _POST_MATRIX_LENGTH_RE.sub(", +long]", text)
    text = _expand_bare_length_in_sets(text)
    return text
