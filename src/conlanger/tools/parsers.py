"""Parse Index Diachronica HTML into the cleaned rule-corpus shape (incremental).

Phase 1: section structure + per-rule ``input`` / ``output`` split on ``→``
(whitespace around the arrow is trimmed).
Phase 2: optional ``/ env`` then optional ``! exception``
(usual form ``input → output /env ! exception``). Word ``except`` and a
second `` / `` are edge-case fallbacks.
Phase 3: first ``<p>`` after ``<h2>`` → section ``citation`` (whole text, cleanup later);
other non-``schg`` paragraphs → ``comments``.
Phase 4: **Symbol** normalization on corpus fields only (``#``, ``$``, ``%``, ``∅``,
Index stress ``”`` → ``:[+stress]``; ``raw`` unchanged). Leading em dash list-item
markers (``— ``) are stripped from the rule line before field split. Remaining
Index rule arrows (``→``) in field values become ASCA ``>``. Chained rules keep a
multi-segment ``output`` (``a > b > c``); compile-time expansion is deferred.
Uncertainty glosses
(``sporadic``, ``sometimes``, …) are stripped from field values and recorded as
``sporadic: true``. **Feature matrix** synonym replacement inside ``[...]`` via
``feature_mappings.csv`` (``raw`` unchanged). **IPA character** substitution via
``ipa_mapping.csv`` (``raw`` unchanged). **Correspondence-series** and
**collective subscript** expansion via ``series_mappings.csv`` (``raw`` unchanged).
Inline prose stripped for ASCA is captured in optional ``comment`` on each corpus
rule: semicolon tails in ``env`` / ``exception`` first (``apply_semicolon_field_comments``), then
field-level glosses and env qualifiers. Class-letter expansion is deferred to compile time (``PhonologicalRuleSet`` +
``group_mappings.csv``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
from lxml import html

ARROW = "→"
ENV_SEP = " / "
BANG_EXCEPTION_RE = re.compile(r"\s*!\s*")
# Edge cases that use the word "except" instead of "!"
TRAILING_EXCEPTION_RE = re.compile(r"(?:,\s*|\s+)except\s+(.*)$", re.IGNORECASE)
LEADING_EXCEPTION_RE = re.compile(r"^(?:,\s*)?except\s+(.*)$", re.IGNORECASE)

SUBSCRIPT_MAP = str.maketrans(
    {
        "0": "₀",
        "1": "₁",
        "2": "₂",
        "3": "₃",
        "4": "₄",
        "5": "₅",
        "6": "₆",
        "7": "₇",
        "8": "₈",
        "9": "₉",
        "a": "ₐ",
        "e": "ₑ",
        "h": "ₕ",
        "i": "ᵢ",
        "j": "ⱼ",
        "k": "ₖ",
        "l": "ₗ",
        "m": "ₘ",
        "n": "ₙ",
        "o": "ₒ",
        "p": "ₚ",
        "r": "ᵣ",
        "s": "ₛ",
        "t": "ₜ",
        "u": "ᵤ",
        "v": "ᵥ",
        "x": "ₓ",
    }
)

DEFAULT_GROUP_MAPPINGS_CSV = (
    Path(__file__).resolve().parents[3] / "data" / "asca" / "group_mappings.csv"
)
DEFAULT_FEATURE_MAPPINGS_CSV = (
    Path(__file__).resolve().parents[3] / "data" / "asca" / "feature_mappings.csv"
)
DEFAULT_IPA_MAPPINGS_CSV = (
    Path(__file__).resolve().parents[3] / "data" / "common" / "ipa_mapping.csv"
)
_SUPPORTED_FEATURE_MAPPING_KINDS = frozenset({"rename", "rename_invert", "rename_polarity"})

# Protect Index stem ``$`` while remapping syllable-boundary ``%`` → ASCA ``$``.
_STEM_BOUNDARY_PLACEHOLDER = "\ue000"

# Index list-item em dash (U+2014) at the start of a rule line — not phonological.
_LEADING_INDEX_LIST_MARKER_RE = re.compile(r"^—\s*")


def strip_leading_index_list_marker(text: str) -> str:
    """Remove Index list-item em dash from the start of a rule line."""
    if not text:
        return text
    return _LEADING_INDEX_LIST_MARKER_RE.sub("", text, count=1)


def join_rule_comment(*fragments: str | None) -> str | None:
    """Join captured prose fragments into one ``comment`` string."""
    parts = [
        fragment.strip() for fragment in fragments if fragment and fragment.strip()
    ]
    if not parts:
        return None
    return "; ".join(parts)


def split_field_semicolon_comment(text: str) -> tuple[str, str | None]:
    """Treat the first ``;`` and following text as ``comment`` prose in one field."""
    if not text or ";" not in text:
        return text, None
    head, _semicolon, tail = text.partition(";")
    head = head.rstrip()
    comment = tail.strip()
    return head, comment or None


def apply_semicolon_field_comments(parts: dict[str, str]) -> dict[str, Any]:
    """Strip semicolon tails from ``env`` and ``exception``; first comment pass."""
    result: dict[str, Any] = dict(parts)
    fragments: list[str] = []
    for key in ("env", "exception"):
        if key not in result:
            continue
        value, comment = split_field_semicolon_comment(result[key])
        result[key] = value
        if comment:
            fragments.append(comment)
    _append_rule_comment_parts(result, fragments)
    return result


def _append_rule_comment_parts(parts: dict[str, Any], fragments: list[str]) -> None:
    """Merge newly captured prose into optional ``comment`` on rule parts."""
    addition = join_rule_comment(*fragments)
    if not addition:
        return
    existing = parts.get("comment")
    merged = join_rule_comment(existing, addition)
    if merged:
        parts["comment"] = merged


def normalize_rule_arrows(text: str) -> str:
    """Map Index rule arrow ``→`` to ASCA ``>`` in one field value."""
    if not text or ARROW not in text:
        return text
    return text.replace(ARROW, ">")


_UNCERTAINTY_WORD_RE = re.compile(r"\b(?:sporadic(?:ally)?|sometimes)\b", re.IGNORECASE)
_LONE_UNCERTAINTY_RE = re.compile(
    r"^(?:sporadic(?:ally)?|sometimes)\??\.?$", re.IGNORECASE
)
_ENV_UNCERTAINTY_PREFIX_RE = re.compile(
    r"^sporadic(?:ally)?(?:,\s*usually)?\s*,?\s*",
    re.IGNORECASE,
)
_TRAILING_PAREN_WITH_UNCERTAINTY_RE = re.compile(
    r"\s*\([^)]*(?:sporadic(?:ally)?|sometimes)[^)]*\)\s*$",
    re.IGNORECASE,
)
_TRAILING_QUOTED_WITH_UNCERTAINTY_RE = re.compile(
    r'\s*(?:[("\u201c][^"\u201d)]*(?:sporadic(?:ally)?|sometimes)[^"\u201d)]*[)\u201d"]|"[^"]*(?:sporadic(?:ally)?|sometimes)[^"]*")\s*$',
    re.IGNORECASE,
)
_TRAILING_BARE_UNCERTAINTY_RE = re.compile(
    r"\s*(?:\()?[\s\u201c\"']*(?:sporadic(?:ally)?|sometimes)\??[\s\u201d\"')]*\)?\s*$",
    re.IGNORECASE,
)


def field_has_uncertainty_qualifier(text: str) -> bool:
    """Return whether ``text`` mentions sporadic / sometimes uncertainty."""
    return bool(text and _UNCERTAINTY_WORD_RE.search(text))


def extract_uncertainty_qualifier_from_field(text: str) -> tuple[str, list[str]]:
    """Remove sporadic / sometimes glosses; return captured prose fragments."""
    captures: list[str] = []
    if not text:
        return text, captures
    text = text.strip()
    if _LONE_UNCERTAINTY_RE.match(text):
        return "", [text]
    prefix = _ENV_UNCERTAINTY_PREFIX_RE.match(text)
    if prefix:
        captures.append(prefix.group(0).strip())
        text = text[prefix.end() :].strip()
    if field_has_uncertainty_qualifier(text):
        match = _TRAILING_PAREN_WITH_UNCERTAINTY_RE.search(text)
        if match:
            captures.append(match.group(0).strip())
            text = _TRAILING_PAREN_WITH_UNCERTAINTY_RE.sub("", text).strip()
    if field_has_uncertainty_qualifier(text):
        match = _TRAILING_QUOTED_WITH_UNCERTAINTY_RE.search(text)
        if match:
            captures.append(match.group(0).strip())
            text = _TRAILING_QUOTED_WITH_UNCERTAINTY_RE.sub("", text).strip()
    if field_has_uncertainty_qualifier(text):
        match = _TRAILING_BARE_UNCERTAINTY_RE.search(text)
        if match:
            captures.append(match.group(0).strip())
            text = _TRAILING_BARE_UNCERTAINTY_RE.sub("", text).strip()
    return text.strip(), captures


def strip_uncertainty_qualifier_from_field(text: str) -> str:
    """Remove sporadic / sometimes glosses from one rule field value."""
    cleaned, _ = extract_uncertainty_qualifier_from_field(text)
    return cleaned


def apply_sporadic_qualifier(parts: dict[str, str]) -> dict[str, Any]:
    """Strip uncertainty glosses from rule fields; set ``sporadic: true`` when found."""
    sporadic = False
    cleaned: dict[str, Any] = {}
    if "comment" in parts:
        cleaned["comment"] = parts["comment"]
    comment_fragments: list[str] = []
    for key in ("input", "output", "env", "exception"):
        if key not in parts:
            continue
        value = parts[key]
        if field_has_uncertainty_qualifier(value):
            sporadic = True
        value, captures = extract_uncertainty_qualifier_from_field(value)
        comment_fragments.extend(captures)
        if key in ("input", "output") or value:
            cleaned[key] = value
    result: dict[str, Any] = cleaned
    if sporadic:
        result["sporadic"] = True
    _append_rule_comment_parts(result, comment_fragments)
    return result


_GLOSS_KEYWORD_RE = re.compile(
    r"\b(?:"
    r"except|only|not|unclear|unsure|depending|marked|conjectured|article|"
    r"dialect|languages|Celtic|Polynesian|similarity|impossible|universal|"
    r"common|below|above|short only|long only|inland|coastal|typical|"
    r"across-the-board|across the board|not sure|not certain|not universal|"
    r"not common|not a complete|may have|did not occur|Whimemsz"
    r")\b",
    re.IGNORECASE,
)
_URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
_TRAILING_QUOTED_GLOSS_RE = re.compile(r'\s*["\u201c]([^"\u201d]+)["\u201d]\s*$')
_TRAILING_PAREN_RE = re.compile(r"\(([^()]*)\)\s*$")
_PHONOLOGICAL_PAREN_INNER_RE = re.compile(
    r"^(?:"
    r"\?"
    r"|\u02d0"
    r"|…|\.\.\."
    r"|C…C"
    r"|[\u0250-\u02AFa-zA-Z:\+\-\[\],_#\$%0-9ʷʼ\"]+"
    r")$"
)


def paren_inner_is_gloss(inner: str) -> bool:
    """Return True when parenthetical content is an Index prose gloss, not phonology."""
    text = inner.strip()
    if not text:
        return True
    if _URL_RE.search(text):
        return True
    if ";" in text:
        return True
    if "→" in text or re.search(r"\s>\s", text):
        return True
    if text.startswith(("NB:", "NB ", "Note:", "note ")):
        return True
    if _GLOSS_KEYWORD_RE.search(text):
        return True
    if "…" in text or "..." in text:
        if re.fullmatch(r"[A-Z#_\[\].…]+", text):
            return False
    if "," in text and re.search(r"[a-z]{3,}", text):
        return True
    if " " in text and re.search(r"[a-z]{3,}", text):
        return True
    if re.fullmatch(r"[A-Z][a-zA-Z\u00C0-\u024F\-]+", text):
        return True
    if (
        " " not in text
        and re.fullmatch(r"[\u0041-\u024F\u1E00-\u1EFF]+", text)
        and not re.search(r"[\u0250-\u02AF:\+\-\[\]]", text)
    ):
        return True
    if _PHONOLOGICAL_PAREN_INNER_RE.fullmatch(text):
        return False
    return False


def extract_trailing_quoted_gloss_from_field(text: str) -> tuple[str, list[str]]:
    """Remove trailing quoted prose glosses; return captured fragments."""
    captures: list[str] = []
    if not text:
        return text, captures
    while True:
        match = _TRAILING_QUOTED_GLOSS_RE.search(text)
        if not match:
            break
        inner = match.group(1)
        if paren_inner_is_gloss(inner) or re.search(r"[a-z]{3,}", inner):
            captures.append(match.group(0).strip())
            text = text[: match.start()].rstrip()
            continue
        break
    return text, captures


def strip_trailing_quoted_gloss_from_field(text: str) -> str:
    """Remove trailing curly- or straight-quoted prose glosses."""
    cleaned, _ = extract_trailing_quoted_gloss_from_field(text)
    return cleaned


_EMBEDDED_QUOTED_GLOSS_RE = re.compile(
    r'[\s,]*[\u201c"]([^\u201d"]{3,})[\u201d"][\s,]*'
)
_UNCLOSED_QUOTED_GLOSS_RE = re.compile(r'[\s,]*[\u201c"]([^\u201d"]{3,})\s*$')
_ORPHAN_CLOSING_QUOTE_END_RE = re.compile(r'[\s,]*[\u201c\u201d"]\s*$')
_ORPHAN_CLOSING_QUOTE_MID_RE = re.compile(r'[\s,]+[\u201d"]+(?=\s|$)')


def _quoted_inner_is_gloss(inner: str) -> bool:
    return bool(re.search(r"[a-z]{3,}", inner)) or paren_inner_is_gloss(inner)


def extract_embedded_quoted_gloss_from_field(text: str) -> tuple[str, list[str]]:
    """Remove embedded quoted Index prose glosses; return captured fragments."""
    captures: list[str] = []
    if not text:
        return text, captures
    while True:
        match = _EMBEDDED_QUOTED_GLOSS_RE.search(text)
        if not match:
            break
        inner = match.group(1)
        if _quoted_inner_is_gloss(inner):
            captures.append(match.group(0).strip())
            text = text[: match.start()] + text[match.end() :]
            continue
        break
    match = _UNCLOSED_QUOTED_GLOSS_RE.search(text)
    if match and _quoted_inner_is_gloss(match.group(1)):
        captures.append(match.group(0).strip())
        text = text[: match.start()].rstrip()
    orphan_mid = _ORPHAN_CLOSING_QUOTE_MID_RE.search(text)
    if orphan_mid:
        captures.append(orphan_mid.group(0).strip())
        text = _ORPHAN_CLOSING_QUOTE_MID_RE.sub("", text)
    orphan_end = _ORPHAN_CLOSING_QUOTE_END_RE.search(text)
    if orphan_end:
        captures.append(orphan_end.group(0).strip())
        text = _ORPHAN_CLOSING_QUOTE_END_RE.sub("", text)
    return text, captures


def strip_embedded_quoted_gloss_from_field(text: str) -> str:
    """Remove embedded ``"…"`` / ``"…"`` Index prose glosses from one field."""
    cleaned, _ = extract_embedded_quoted_gloss_from_field(text)
    return cleaned


def extract_trailing_paren_glosses_from_field(text: str) -> tuple[str, list[str]]:
    """Remove trailing ``(… )`` prose glosses; return captured fragments."""
    captures: list[str] = []
    if not text:
        return text, captures
    while True:
        match = _TRAILING_PAREN_RE.search(text)
        if not match or not paren_inner_is_gloss(match.group(1)):
            break
        captures.append(match.group(0).strip())
        text = text[: match.start()].rstrip()
    return text, captures


def strip_trailing_paren_glosses_from_field(text: str) -> str:
    """Remove trailing ``(… )`` prose glosses from one rule field."""
    cleaned, _ = extract_trailing_paren_glosses_from_field(text)
    return cleaned


def extract_semicolon_prose_from_field(text: str) -> tuple[str, list[str]]:
    """Remove trailing ``; …`` English prose; return captured tail."""
    if not text or "; " not in text:
        return text, []
    idx = text.find("; ")
    tail = text[idx + 2 :]
    if re.match(r'[a-z"\u201c(]', tail) and re.search(r"[a-z]{3,}", tail):
        if not re.match(r"[_#\[\{]", tail.lstrip()):
            return text[:idx].rstrip(), [tail.strip()]
    return text, []


def extract_trailing_gloss_from_field(text: str) -> tuple[str, list[str]]:
    """Strip Index trailing glosses; return cleaned field and captured prose."""
    if not text:
        return text, []
    captures: list[str] = []
    for extractor in (
        extract_embedded_quoted_gloss_from_field,
        extract_trailing_quoted_gloss_from_field,
        extract_trailing_paren_glosses_from_field,
        extract_semicolon_prose_from_field,
    ):
        text, frags = extractor(text)
        captures.extend(frags)
    return text.strip(), captures


def strip_trailing_gloss_from_field(text: str) -> str:
    """Strip Index trailing glosses (parens, quotes, semicolon prose) from one field."""
    cleaned, _ = extract_trailing_gloss_from_field(text)
    return cleaned


def apply_trailing_glosses(parts: dict[str, str]) -> dict[str, Any]:
    """Remove trailing bracket/quote glosses from rule fields; capture ``comment``."""
    cleaned: dict[str, Any] = {}
    if "comment" in parts:
        cleaned["comment"] = parts["comment"]
    comment_fragments: list[str] = []
    for key in ("input", "output", "env", "exception"):
        if key not in parts:
            continue
        original = parts[key]
        value, captures = extract_trailing_gloss_from_field(original)
        comment_fragments.extend(captures)
        if key in ("input", "output") and not value:
            value = original
        if key in ("input", "output") or value:
            cleaned[key] = value
    _append_rule_comment_parts(cleaned, comment_fragments)
    return cleaned


_STRESS_CONDITION_RE = re.compile(r"when (?:un)?stressed\b", re.IGNORECASE)
_COMMA_BEFORE_STRESS_RE = re.compile(
    r",\s*(?=when (?:un)?stressed\b)",
    re.IGNORECASE,
)
_TRAILING_STRESS_AFTER_HASH_RE = re.compile(
    r"\s+when (?:un)?stressed\b.*$",
    re.IGNORECASE,
)
_PROSE_BEFORE_STRESS_RE = re.compile(
    r"^.*?(when (?:un)?stressed\b.*)$",
    re.IGNORECASE,
)


def normalize_stress_conditions(text: str) -> tuple[str, list[str]]:
    """Normalize Index stress env prose for ASCA; capture removed trailing prose."""
    captures: list[str] = []
    if not text or not _STRESS_CONDITION_RE.search(text):
        return text, captures
    text = _COMMA_BEFORE_STRESS_RE.sub(" ", text)
    if "#" in text:
        match = _TRAILING_STRESS_AFTER_HASH_RE.search(text)
        if match:
            captures.append(match.group(0).strip())
            text = _TRAILING_STRESS_AFTER_HASH_RE.sub("", text).rstrip()
    elif re.match(r"when (?:un)?stressed\b", text, re.IGNORECASE):
        text = f"_ {text}"
    elif "_" not in text:
        match = _PROSE_BEFORE_STRESS_RE.match(text)
        if match:
            text = f"_ {match.group(1)}"
    return text.strip(), captures


def apply_stress_conditions(parts: dict[str, str]) -> dict[str, Any]:
    """Normalize ``when stressed`` / ``when unstressed`` in env and exception fields."""
    result: dict[str, Any] = dict(parts)
    comment_fragments: list[str] = []
    for key in ("env", "exception"):
        if key in result:
            value, captures = normalize_stress_conditions(result[key])
            result[key] = value
            comment_fragments.extend(captures)
    _append_rule_comment_parts(result, comment_fragments)
    return result


def load_feature_mappings(path: Path | None = None) -> list[FeatureMapping]:
    """Load Index→ASCA feature-matrix synonym mappings from CSV."""
    csv_path = DEFAULT_FEATURE_MAPPINGS_CSV if path is None else Path(path)
    if not csv_path.is_file():
        return []
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    required = {"index_feature", "mapping_kind", "asca_target", "confidence"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"feature mappings CSV missing required columns: {sorted(missing)}"
        )
    out: list[FeatureMapping] = []
    for row in df.itertuples(index=False):
        kind = row.mapping_kind.strip()
        if kind not in _SUPPORTED_FEATURE_MAPPING_KINDS:
            raise ValueError(
                f"unsupported feature mapping_kind {kind!r} for "
                f"{row.index_feature!r} (Phase 1: rename, rename_invert, rename_polarity)"
            )
        out.append(
            FeatureMapping(
                index_feature=row.index_feature,
                mapping_kind=kind,
                asca_target=row.asca_target,
                host=getattr(row, "host", "") if "host" in df.columns else "",
                confidence=row.confidence,
                notes=getattr(row, "notes", "") if "notes" in df.columns else "",
            )
        )
    return out


def feature_mappings_dict(
    path: Path | None = None,
) -> dict[str, FeatureMapping]:
    """Return feature mappings keyed by ``index_feature``."""
    return {row.index_feature: row for row in load_feature_mappings(path)}


def normalize_feature_matrices_in_field(
    text: str,
    mappings: dict[str, FeatureMapping],
) -> str:
    """Replace Index matrix feature names inside ``[...]`` with ASCA targets."""
    if not text or not mappings:
        return text
    names = sorted(mappings.keys(), key=len, reverse=True)
    feature_re = re.compile(
        r"([+-])\s*(" + "|".join(re.escape(name) for name in names) + r")(?![a-zA-Z])"
    )

    def replace_polarity_and_name(match: re.Match[str]) -> str:
        polarity, index_name = match.group(1), match.group(2)
        mapping = mappings[index_name]
        if mapping.mapping_kind == "rename":
            return f"{polarity}{mapping.asca_target}"
        if mapping.mapping_kind in ("rename_invert", "rename_polarity"):
            flipped = "-" if polarity == "+" else "+"
            return f"{flipped}{mapping.asca_target}"
        return match.group(0)

    def replace_bracket_inner(match: re.Match[str]) -> str:
        inner = feature_re.sub(replace_polarity_and_name, match.group(1))
        return f"[{inner}]"

    return re.sub(r"\[([^\]]*)\]", replace_bracket_inner, text)


def apply_feature_mappings(
    parts: dict[str, str],
    mappings: dict[str, FeatureMapping] | None = None,
) -> dict[str, str]:
    """Normalize Index feature matrix names in rule fields; ``raw`` unchanged upstream."""
    table = mappings if mappings is not None else feature_mappings_dict()
    if not table:
        return parts
    result = dict(parts)
    for key in ("input", "output", "env", "exception"):
        if key in result:
            result[key] = normalize_feature_matrices_in_field(result[key], table)
    return result


def load_ipa_mappings(path: Path | None = None) -> list[IpaMapping]:
    """Load Index→ASCA IPA character mappings from CSV."""
    csv_path = DEFAULT_IPA_MAPPINGS_CSV if path is None else Path(path)
    if not csv_path.is_file():
        return []
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    required = {"index_feature", "ipa_target", "confidence"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"IPA mappings CSV missing required columns: {sorted(missing)}"
        )
    has_notes = "notes" in df.columns
    out: list[IpaMapping] = []
    for row in df.itertuples(index=False):
        out.append(
            IpaMapping(
                index_feature=row.index_feature,
                ipa_target=row.ipa_target,
                confidence=row.confidence,
                notes=row.notes if has_notes else "",
            )
        )
    return out


def ipa_mappings_dict(path: Path | None = None) -> dict[str, str]:
    """Return high-confidence IPA mappings keyed by Index character or digraph."""
    return {
        row.index_feature: row.ipa_target
        for row in load_ipa_mappings(path)
        if row.confidence == "high" and row.ipa_target
    }


def normalize_ipa_in_field(text: str, mappings: dict[str, str]) -> str:
    """Replace Index IPA characters in one rule field with ASCA targets."""
    if not text or not mappings:
        return text
    for source in sorted(mappings.keys(), key=len, reverse=True):
        text = text.replace(source, mappings[source])
    return text


def apply_ipa_mappings(
    parts: dict[str, str],
    mappings: dict[str, str] | None = None,
) -> dict[str, str]:
    """Normalize Index IPA characters in rule fields; ``raw`` unchanged upstream."""
    table = mappings if mappings is not None else ipa_mappings_dict()
    if not table:
        return parts
    result = dict(parts)
    for key in ("input", "output", "env", "exception"):
        if key in result:
            result[key] = normalize_ipa_in_field(result[key], table)
    return result


# Index Diachronica stress mark (Key to Abbreviations: ” = Stress).
_INDEX_STRESS = "\u201d"

# Class letter or IPA vowel segment — not an English word continuation.
_STRESS_SEGMENT = r"([A-Z](?![a-z])|[a-z\u0250-\u02AF\u1D00-\u1DBF]+(?=[\s→/\[,!\]|$]))"
_STRESS_FEAT_SUFFIX = r"(\[[^\]]*\])?"

# ” before a segment (rule input, e.g. ”V → …).
_STRESS_PREFIX_RE = re.compile(
    rf"{re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
# Boundary symbol then stress: #”U → #U:[+stress].
_STRESS_AFTER_BOUNDARY_RE = re.compile(
    rf"([#$_∅%]){re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
# Infix stress between segments: C”V → CV:[+stress] (class letter after C).
_STRESS_INFIX_RE = re.compile(
    rf"(?<=[A-Za-z\u0250-\u02AF]){re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
# Inside sets: {”V,j} → {V:[+stress],j}.
_STRESS_IN_SET_RE = re.compile(
    rf"(?<=[{{,])\s*{re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)


@dataclass(frozen=True)
class GroupMapping:
    grouping: str
    mapping: str
    comment: str = ""


@dataclass(frozen=True)
class IpaMapping:
    index_feature: str
    ipa_target: str
    confidence: str = ""
    notes: str = ""


@dataclass(frozen=True)
class FeatureMapping:
    index_feature: str
    mapping_kind: str
    asca_target: str
    host: str = ""
    confidence: str = ""
    notes: str = ""


def to_subscript(text: str) -> str:
    return "".join(
        ch.translate(SUBSCRIPT_MAP)
        if ch.lower() in "0123456789aehijklmnoprstuvx"
        else ch
        for ch in text
    )


def strip_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ").replace("\r", " ")).strip()


def extract_text_with_subs(el) -> str:
    """Element text with ``<sub>`` converted to Unicode subscripts."""
    parts: list[str] = []

    def walk(node) -> None:
        if node.text:
            if getattr(node, "tag", None) == "sub":
                parts.append(to_subscript(node.text))
            else:
                parts.append(node.text)
        for child in node:
            walk(child)
            if child.tail:
                parts.append(child.tail)

    walk(el)
    return strip_whitespace("".join(parts))


def split_input_output(raw: str) -> tuple[str, str] | None:
    """Split on the first ``→``. Returns None if that separator is absent."""
    if ARROW not in raw:
        return None
    left, right = raw.split(ARROW, 1)
    return left.strip(), right.strip()


def split_output_rest(post_arrow: str) -> tuple[str, str | None]:
    """Split post-arrow text on the first ``\" / \"`` into output and optional rest."""
    text = post_arrow.strip()
    if ENV_SEP not in text:
        return text, None
    out, rest = text.split(ENV_SEP, 1)
    out, rest = out.strip(), rest.strip()
    return out, rest or None


def split_env_exception(rest: str) -> tuple[str | None, str | None]:
    """Parse the post-``/`` remainder into optional env and exception.

    Usual form: ``/env ! exception``. ``!`` starts the exception string.
    Fallbacks: word ``except``, or a second `` / ``.
    """
    text = rest.strip()
    if not text:
        return None, None

    bang = BANG_EXCEPTION_RE.search(text)
    if bang:
        env = text[: bang.start()].rstrip()
        exception = text[bang.end() :].strip()
        return (env or None), (exception or None)

    lead = LEADING_EXCEPTION_RE.match(text)
    if lead:
        return None, lead.group(1).strip() or None

    trail = TRAILING_EXCEPTION_RE.search(text)
    if trail:
        env = text[: trail.start()].rstrip()
        return (env or None), (trail.group(1).strip() or None)

    if ENV_SEP in text:
        env, exception = text.split(ENV_SEP, 1)
        env, exception = env.strip(), exception.strip()
        return (env or None), (exception or None)

    return text, None


def split_post_arrow(post_arrow: str) -> tuple[str, str | None, str | None]:
    """``output``, optional ``env``, optional ``exception`` from post-arrow text."""
    out, rest = split_output_rest(post_arrow)
    if rest is None:
        # No slash: exception may still trail the output (``, except …``).
        trail = TRAILING_EXCEPTION_RE.search(out)
        if trail:
            return out[: trail.start()].rstrip(), None, trail.group(1).strip() or None
        return out, None, None
    env, exception = split_env_exception(rest)
    return out, env, exception


def _apply_stress_re(match: re.Match[str]) -> str:
    """Expand Index stress mark to ASCA ``segment:[+stress]`` (+ optional features)."""
    groups = match.groups()
    if len(groups) == 3:
        prefix, segment, feats = groups
        return f"{prefix}{segment}:[+stress]{feats or ''}"
    segment, feats = groups[0], groups[1] if len(groups) > 1 else None
    return f"{segment}:[+stress]{feats or ''}"


def normalize_stress_marks(text: str) -> str:
    """Map Index ``”`` stress marks to ASCA ``:[+stress]`` on the marked segment.

    Prose curly quotes (``"…"``) and English env prose after ``/`` are left
    unchanged — only phonological stress positions are rewritten.
    """
    if _INDEX_STRESS not in text:
        return text
    text = _STRESS_AFTER_BOUNDARY_RE.sub(_apply_stress_re, text)
    text = _STRESS_IN_SET_RE.sub(_apply_stress_re, text)
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


def extract_rule_parts(raw: str) -> dict[str, str] | None:
    """Split a raw rule string into input, output, and optional env/exception.

    Returns None if ``→`` is missing. Optional keys are omitted when absent.
    """
    raw = strip_leading_index_list_marker(raw)
    split = split_input_output(raw)
    if split is None:
        return None
    inp, post_arrow = split
    out, env, exception = split_post_arrow(post_arrow)
    parts: dict[str, str] = {
        "input": inp,
        "output": out,
    }
    if env is not None:
        parts["env"] = env
    if exception is not None:
        parts["exception"] = exception
    return {key: normalize_rule_arrows(value) for key, value in parts.items()}


def note_from_element(el, *, source_file: str) -> dict[str, Any]:
    raw = extract_text_with_subs(el)
    line = getattr(el, "sourceline", None) or 0
    return {
        "raw": raw,
        "source": f"{source_file}:{line}",
    }


def parse_section_heading(h2_text: str) -> tuple[str, str]:
    m = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", h2_text.strip())
    if not m:
        return "", h2_text.strip()
    return m.group(1).strip(), m.group(2).strip()


def load_group_mappings(path: Path | None = None) -> list[GroupMapping]:
    """Load Index→ASCA group letter mappings from CSV."""
    csv_path = DEFAULT_GROUP_MAPPINGS_CSV if path is None else Path(path)
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    missing = {"grouping", "mapping"} - set(df.columns)
    if missing:
        raise ValueError(
            f"group mappings CSV missing required columns: {sorted(missing)}"
        )
    has_comment = "comment" in df.columns
    out: list[GroupMapping] = []
    for row in df.itertuples(index=False):
        out.append(
            GroupMapping(
                grouping=row.grouping,
                mapping=row.mapping,
                comment=row.comment if has_comment else "",
            )
        )
    return out


_RULE_COMMENT_QUALIFIER_PHRASES = (
    "short only",
    "long only",
    "when unstressed",
    "when stressed",
    "except as below",
    "sporadic",
    "sometimes",
    "not sure",
    "not universal",
    "short vowel",
    "unstressed",
)


def write_rule_comment_phrase_summary(doc: dict[str, Any], path: Path) -> int:
    """Write qualifier-phrase counts from corpus rule ``comment`` fields."""
    comments: list[str] = []
    for section in doc.get("sections") or []:
        for rule in section.get("rules") or []:
            comment = rule.get("comment")
            if comment:
                comments.append(str(comment))

    phrase_counts: dict[str, int] = {}
    for phrase in _RULE_COMMENT_QUALIFIER_PHRASES:
        count = sum(1 for comment in comments if phrase.lower() in comment.lower())
        if count:
            phrase_counts[phrase] = count

    semicolon_count = sum(1 for comment in comments if ";" in comment)

    lines = [
        "# Rule comment phrase summary",
        "",
        f"- Corpus rules with **`comment`**: **{len(comments)}**",
        f"- Comments containing ``; `` (semicolon tails): **{semicolon_count}**",
        "",
        "## Qualifier phrases",
        "",
        "| phrase | rules |",
        "| --- | ---: |",
    ]
    for phrase, count in sorted(
        phrase_counts.items(), key=lambda item: (-item[1], item[0])
    ):
        lines.append(f"| `{phrase}` | {count} |")

    if not phrase_counts:
        lines.append("| _(none matched)_ | 0 |")

    lines.extend(
        [
            "",
            "## Sample comments (first 10)",
            "",
        ]
    )
    for comment in comments[:10]:
        lines.append(f"- {comment}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(comments)


class IndexDiachronicaParser:
    """Parse Index Diachronica HTML into applier-neutral cleaned-corpus YAML."""

    def __init__(self, series_mappings: list | None = None) -> None:
        if series_mappings is None:
            from conlanger.tools.series_mappings import load_series_mappings

            self._series_mappings = load_series_mappings()
        else:
            self._series_mappings = series_mappings

    def abbreviations(self) -> dict[str, str]:
        """Global abbreviation table for the cleaned corpus (empty at ingest)."""
        return {}

    def parse_rule_element(
        self,
        el,
        *,
        source_file: str,
        section_index: str = "",
    ) -> list[dict[str, Any]]:
        raw = extract_text_with_subs(el)
        line = getattr(el, "sourceline", None) or 0
        source = f"{source_file}:{line}"
        normalized = normalize_symbols(raw)
        parts = extract_rule_parts(normalized)
        if parts is None:
            return [
                {
                    "input": "",
                    "output": "",
                    "raw": raw,
                    "source": source,
                    "skipped": f"missing separator {ARROW!r}",
                }
            ]
        parts = apply_semicolon_field_comments(parts)
        parts = apply_sporadic_qualifier(parts)
        sporadic = parts.pop("sporadic", False)
        sporadic_flag = {"sporadic": True} if sporadic else {}
        parts = apply_trailing_glosses(parts)
        parts = apply_stress_conditions(parts)
        parts = apply_feature_mappings(parts)
        parts = apply_ipa_mappings(parts)
        from conlanger.tools.series_mappings import apply_series_mappings

        parts = apply_series_mappings(parts, section_index, self._series_mappings)
        return [{**parts, "raw": raw, "source": source, **sporadic_flag}]

    def parse(
        self,
        html_path: Path,
        *,
        source_file: str | None = None,
    ) -> dict[str, Any]:
        """Parse HTML into ``{abbreviations, sections: [...]}``."""
        source_file = source_file or html_path.name
        parser = html.HTMLParser(encoding="utf-8")
        doc = html.parse(str(html_path), parser=parser)
        root = doc.getroot()
        sections_out: list[dict[str, Any]] = []

        for sec in root.xpath("//section[@id]"):
            h2s = sec.xpath("./h2")
            if not h2s:
                continue
            h2_text = strip_whitespace("".join(h2s[0].itertext()))
            index, name = parse_section_heading(h2_text)
            if not name:
                continue

            # First <p> after <h2> is citation (whole line). Other non-schg → comments.
            rules: list[dict[str, Any]] = []
            citation: str | None = None
            comments: list[dict[str, Any]] = []
            saw_first_p = False

            for p in sec.xpath("./p"):
                cls = p.get("class") or ""
                if "schg" in cls:
                    saw_first_p = (
                        True  # citation slot consumed even if first p was a rule
                    )
                    rules.extend(
                        self.parse_rule_element(
                            p,
                            source_file=source_file,
                            section_index=index or "",
                        )
                    )
                    continue

                note = note_from_element(p, source_file=source_file)
                if not note["raw"]:
                    continue

                if not saw_first_p:
                    citation = note["raw"]
                    saw_first_p = True
                else:
                    comments.append(note)

            section_obj: dict[str, Any] = {
                "section": name,
                "index": index,
            }
            section_abbrevs: dict[str, str] = {}
            if index:
                from conlanger.tools.series_mappings import (
                    section_abbreviations_for_index,
                )

                section_abbrevs = section_abbreviations_for_index(
                    index, self._series_mappings
                )
            if section_abbrevs:
                section_obj["abbreviations"] = section_abbrevs
            if citation is not None:
                section_obj["citation"] = citation
            if comments:
                section_obj["comments"] = comments
            if rules:
                section_obj["rules"] = rules
            sections_out.append(section_obj)

        return {
            "abbreviations": self.abbreviations(),
            "sections": sections_out,
        }


def parse_rule_element(
    el,
    *,
    source_file: str,
    section_index: str = "",
) -> list[dict[str, Any]]:
    return IndexDiachronicaParser().parse_rule_element(
        el,
        source_file=source_file,
        section_index=section_index,
    )
