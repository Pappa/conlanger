"""Index Symbol mark normalization for ASCA-canonical index fields."""

from __future__ import annotations

import re

# Protect Index stem ``$`` while remapping syllable-boundary ``%`` → ASCA ``$``.
_STEM_BOUNDARY_PLACEHOLDER = "\ue000"

# Index Diachronica stress mark (Key to Abbreviations: ” = Stress).
_INDEX_STRESS = "\u201d"

_STRESS_BOUNDARY = (
    r"(?=$|[\s→/\[,!\]_\.\)]|[A-Za-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF])"
)
_STRESS_VOWEL_CONTINUE = r"[aeiouyæøœɑɛɪɔʊəɨʉɯɤɐɒʌɜɞɶɤ]*"
_STRESS_SEGMENT = (
    rf"([A-Z]{_STRESS_VOWEL_CONTINUE}"
    rf"|[a-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]+{_STRESS_BOUNDARY})"
)
_STRESS_FEAT_SUFFIX = r"(\[[^\]]*\])?"

_STRESS_CLASS_BEFORE_UNDERSCORE_RE = re.compile(
    rf"([A-Z]){re.escape(_INDEX_STRESS)}(?=_)"
)
_STRESS_AFTER_CLOSE_PAREN_RE = re.compile(rf"\){re.escape(_INDEX_STRESS)}(?=\()")
_STRESS_PREFIX_RE = re.compile(
    rf"{re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
_STRESS_AFTER_BOUNDARY_RE = re.compile(
    rf"([#$_∅%]){re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
_STRESS_AFTER_UNDERSCORE_RE = re.compile(
    rf"(?<=_){re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
_STRESS_AFTER_DOUBLE_SLASH_RE = re.compile(
    rf"(//\s*){re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
_STRESS_AFTER_STAR_SET_RE = re.compile(rf"\*{re.escape(_INDEX_STRESS)}\{{([^{{}}]+)\}}")
_STRESS_AFTER_STAR_SEGMENT_RE = re.compile(
    rf"\*{re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
_STRESS_BEFORE_SET_RE = re.compile(
    rf"{re.escape(_INDEX_STRESS)}\{{([^{{}}]+)\}}(?:\s+{_STRESS_SEGMENT})?"
)
_STRESS_BEFORE_SET_AFTER_CLOSE_RE = re.compile(
    rf"(?<=[}}]){re.escape(_INDEX_STRESS)}\{{([^{{}}]+)\}}"
)
_STRESS_IN_PAREN_RE = re.compile(
    rf"\({re.escape(_INDEX_STRESS)}([a-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]+)"
    rf"{_STRESS_FEAT_SUFFIX}\)"
)
_STRESS_QUOTE_UNDERSCORE_SEGMENT_RE = re.compile(
    rf"{re.escape(_INDEX_STRESS)}_\$?"
    rf"([a-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]+)(:\[[^\]]+\])?"
)
_STRESS_PREFIX_COLON_FEAT_RE = re.compile(
    rf"{re.escape(_INDEX_STRESS)}"
    rf"([a-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]+)(:\[[^\]]+\])"
)
_STRESS_BEFORE_PAREN_RE = re.compile(
    rf"(?<=[A-Za-z\u0250-\u02AF\u1D00-\u1DBF]){re.escape(_INDEX_STRESS)}(?=\()"
)
_STRESS_ORPHAN_AFTER_PAREN_RE = re.compile(
    rf"(\([^)]+\)){re.escape(_INDEX_STRESS)}(?=\s)"
)
_STRESS_INFIX_RE = re.compile(
    rf"(?<=[A-Za-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF])"
    rf"{re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
_STRESS_IN_SET_RE = re.compile(
    rf"(?<=[{{,])\s*{re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)


def _apply_stress_re(match: re.Match[str]) -> str:
    """Expand Index stress mark to ASCA ``segment:[+stress]`` (+ optional features)."""
    groups = match.groups()
    if len(groups) == 3:
        prefix, segment, feats = groups
        return f"{prefix}{segment}:[+stress]{feats or ''}"
    segment, feats = groups[0], groups[1] if len(groups) > 1 else None
    return f"{segment}:[+stress]{feats or ''}"


def _apply_stress_set_re(match: re.Match[str]) -> str:
    members = [member.strip() for member in match.group(1).split(",")]
    body = ",".join(f"{member}:[+stress]" for member in members)
    tail = match.group(2) or ""
    if tail:
        tail = f"{tail}:[+stress]"
    return "{" + body + "}" + tail


def _apply_stress_paren_re(match: re.Match[str]) -> str:
    segment, feats = match.group(1), match.group(2) or ""
    return f"({segment}:[+stress]{feats})"


def _apply_stress_colon_feat_re(match: re.Match[str]) -> str:
    segment, feat = match.group(1), match.group(2)
    inner = feat[2:-1].lstrip("[").rstrip("]")
    return f"{segment}:[+stress,{inner}]"


def _apply_stress_quote_underscore_re(match: re.Match[str]) -> str:
    segment, feat = match.group(1), match.group(2) or ""
    if feat:
        inner = feat[2:-1].lstrip("[").rstrip("]")
        return f"_${segment}:[+stress,{inner}]"
    return f"_${segment}:[+stress]"


def _apply_stress_set_after_close_re(match: re.Match[str]) -> str:
    members = [member.strip() for member in match.group(1).split(",")]
    return "{" + ",".join(f"{member}:[+stress]" for member in members) + "}"


def _apply_stress_star_set_re(match: re.Match[str]) -> str:
    members = [member.strip() for member in match.group(1).split(",")]
    return "*{" + ",".join(f"{member}:[+stress]" for member in members) + "}"


def normalize_stress_marks(text: str) -> str:
    """Map Index ``”`` stress marks to ASCA ``:[+stress]`` on the marked segment.

    Prose curly quotes (``"…"``) and English env prose after ``/`` are left
    unchanged — only phonological stress positions are rewritten.
    """
    if _INDEX_STRESS not in text:
        return text
    text = _STRESS_CLASS_BEFORE_UNDERSCORE_RE.sub(
        lambda m: f"{m.group(1)}:[+stress]", text
    )
    text = _STRESS_AFTER_CLOSE_PAREN_RE.sub("):[+stress](", text)
    text = _STRESS_AFTER_BOUNDARY_RE.sub(_apply_stress_re, text)
    text = _STRESS_AFTER_UNDERSCORE_RE.sub(_apply_stress_re, text)
    text = _STRESS_AFTER_DOUBLE_SLASH_RE.sub(_apply_stress_re, text)
    text = _STRESS_AFTER_STAR_SET_RE.sub(_apply_stress_star_set_re, text)
    text = _STRESS_AFTER_STAR_SEGMENT_RE.sub(_apply_stress_re, text)
    text = _STRESS_BEFORE_SET_RE.sub(_apply_stress_set_re, text)
    text = _STRESS_BEFORE_SET_AFTER_CLOSE_RE.sub(_apply_stress_set_after_close_re, text)
    text = _STRESS_IN_PAREN_RE.sub(_apply_stress_paren_re, text)
    text = _STRESS_QUOTE_UNDERSCORE_SEGMENT_RE.sub(
        _apply_stress_quote_underscore_re, text
    )
    text = _STRESS_IN_SET_RE.sub(_apply_stress_re, text)
    text = _STRESS_PREFIX_COLON_FEAT_RE.sub(_apply_stress_colon_feat_re, text)
    text = _STRESS_BEFORE_PAREN_RE.sub(":[+stress]", text)
    text = _STRESS_ORPHAN_AFTER_PAREN_RE.sub(r"\1:[+stress]", text)
    text = _STRESS_INFIX_RE.sub(_apply_stress_re, text)
    text = _STRESS_PREFIX_RE.sub(_apply_stress_re, text)
    return text


def normalize_symbols(text: str) -> str:
    """Map Index **Symbol** marks to ASCA-canonical form before rule parsing.

    Applied to the full rule line (not the stored ``raw``). Index ``%`` (syllable
    boundary) → ASCA ``$``; Index ``$`` (stem boundary) is preserved. ``#`` and ``∅``
    pass through unchanged. Index stress ``”`` → ``segment:[+stress]``.
    """
    if not text:
        return text
    text = text.replace("$", _STEM_BOUNDARY_PLACEHOLDER)
    text = text.replace("%", "$")
    text = text.replace(_STEM_BOUNDARY_PLACEHOLDER, "$")
    return normalize_stress_marks(text)
