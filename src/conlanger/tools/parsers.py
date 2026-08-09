"""Parse Index Diachronica HTML into the cleaned rule-corpus shape (incremental).

Phase 1: section structure + per-rule ``stages`` split on every ``→`` in the change
spine (whitespace around arrows is trimmed).
Phase 2: optional ``/ env`` then optional ``! exception``
(usual form ``input → output /env ! exception``). Word ``except`` and a
second `` / `` are edge-case fallbacks.
Phase 3: first ``<p>`` after ``<h2>`` → section ``citation`` (whole text, cleanup later);
other non-``schg`` paragraphs → ``comments``.
Phase 4: **Manual mapping** substring rewrites from ``manual_mappings.csv`` run first on a
working copy (``raw`` keeps the HTML surface). Then **Symbol** normalization on corpus
fields only (``#``, ``$``, ``%``, ``∅``, Index stress ``”`` → ``:[+stress]``; ``raw``
unchanged). Leading em dash list-item markers (``— ``) are stripped from the rule line
before field split. Remaining Index rule arrows (``→``) in field values become ASCA ``>``.
Chained rules store each spine segment in ``stages``; compile-time expansion is deferred.
Uncertainty glosses
(``sporadic``, ``sometimes``, ``occasionally``, …) are stripped from field values
and recorded as ``sporadic: true``. **Feature matrix** synonym replacement inside ``[...]`` via
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
import yaml
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
DEFAULT_MANUAL_MAPPINGS_CSV = (
    Path(__file__).resolve().parents[3] / "data" / "common" / "manual_mappings.csv"
)
DEFAULT_PARSER_CONFIG_PATH = (
    Path(__file__).resolve().parents[3] / "data" / "parser_config.yml"
)
DEFAULT_IPA_MAPPING_CONFIDENCE = ["high"]
_SUPPORTED_FEATURE_MAPPING_KINDS = frozenset(
    {"rename", "rename_invert", "rename_polarity", "bundle"}
)

# Protect Index stem ``$`` while remapping syllable-boundary ``%`` → ASCA ``$``.
_STEM_BOUNDARY_PLACEHOLDER = "\ue000"

# Index list-item em dash (U+2014) at the start of a rule line — not phonological.
_LEADING_INDEX_LIST_MARKER_RE = re.compile(r"^—\s*")
_CORPUS_CONTEXT_FIELD_KEYS = ("env", "exception")


def strip_leading_index_list_marker(text: str) -> str:
    """Remove Index list-item em dash from the start of a rule line."""
    if not text:
        return text
    return _LEADING_INDEX_LIST_MARKER_RE.sub("", text, count=1)


def build_stages_from_spine(inp: str, out: str) -> list[str]:
    """Split a change spine into ordered opaque stage strings."""
    stages = [inp.strip()]
    if ARROW in out:
        stages.extend(
            segment.strip() for segment in out.split(ARROW) if segment.strip()
        )
    elif out.strip():
        stages.append(out.strip())
    return stages


def non_empty_stages(stages: list[str]) -> list[str]:
    return [stage for stage in stages if stage and stage.strip()]


def finalize_stages_shape(parts: dict[str, Any]) -> dict[str, Any]:
    """Hold out rules with fewer than two non-empty stages."""
    stages = parts.get("stages", [])
    kept = non_empty_stages(stages)
    if len(kept) >= 2:
        parts["stages"] = kept
        return parts
    result = {key: value for key, value in parts.items() if key != "stages"}
    result["stages"] = []
    if result.get("status") != "skipped":
        result["status"] = "skipped"
    return result


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


_UNCERTAINTY_WORDS = r"sporadic(?:ally)?|sometimes|occasionally"
_UNCERTAINTY_WORD_RE = re.compile(rf"\b(?:{_UNCERTAINTY_WORDS})\b", re.IGNORECASE)
_LONE_UNCERTAINTY_RE = re.compile(
    rf"^(?:{_UNCERTAINTY_WORDS})\??\.?$", re.IGNORECASE
)
_ENV_UNCERTAINTY_PREFIX_RE = re.compile(
    r"^sporadic(?:ally)?(?:,\s*usually)?\s*,?\s*",
    re.IGNORECASE,
)
_TRAILING_PAREN_WITH_UNCERTAINTY_RE = re.compile(
    rf"\s*\([^)]*(?:{_UNCERTAINTY_WORDS})[^)]*\)\s*$",
    re.IGNORECASE,
)
_TRAILING_QUOTED_WITH_UNCERTAINTY_RE = re.compile(
    rf'\s*(?:[("\u201c][^"\u201d)]*(?:{_UNCERTAINTY_WORDS})[^"\u201d)]*[)\u201d"]|"[^"]*(?:{_UNCERTAINTY_WORDS})[^"]*")\s*$',
    re.IGNORECASE,
)
_TRAILING_BARE_UNCERTAINTY_RE = re.compile(
    rf"(?:,\s*|\s*(?:\()?)[\s\u201c\"']*(?:{_UNCERTAINTY_WORDS})\??[\s\u201d\"')]*\)?\s*$",
    re.IGNORECASE,
)


def field_has_uncertainty_qualifier(text: str) -> bool:
    """Return whether ``text`` mentions sporadic / sometimes / occasionally uncertainty."""
    return bool(text and _UNCERTAINTY_WORD_RE.search(text))


def extract_uncertainty_qualifier_from_field(text: str) -> tuple[str, list[str]]:
    """Remove sporadic / sometimes / occasionally glosses; return captured prose."""
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
    """Remove sporadic / sometimes / occasionally glosses from one rule field value."""
    cleaned, _ = extract_uncertainty_qualifier_from_field(text)
    return cleaned


def apply_sporadic_qualifier(parts: dict[str, str]) -> dict[str, Any]:
    """Strip uncertainty glosses from rule fields; set ``sporadic: true`` when found."""
    sporadic = False
    cleaned: dict[str, Any] = {}
    if "comment" in parts:
        cleaned["comment"] = parts["comment"]
    comment_fragments: list[str] = []
    stages = parts.get("stages")
    if stages is not None:
        new_stages: list[str] = []
        for stage in stages:
            value = stage
            if field_has_uncertainty_qualifier(value):
                sporadic = True
            value, captures = extract_uncertainty_qualifier_from_field(value)
            comment_fragments.extend(captures)
            new_stages.append(value)
        cleaned["stages"] = new_stages
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key not in parts:
            continue
        value = parts[key]
        if field_has_uncertainty_qualifier(value):
            sporadic = True
        value, captures = extract_uncertainty_qualifier_from_field(value)
        comment_fragments.extend(captures)
        if value:
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


_FIELD_WRAPPED_QUOTED_GLOSS_RE = re.compile(r'^[\u201c"]([^\u201d"]+)[\u201d"]\s*$')
_FIELD_LEADING_QUOTED_GLOSS_RE = re.compile(r'^[\u201c"]([^\u201d"]{10,})[\u201d"]?\s*')
_EMBEDDED_QUOTED_GLOSS_RE = re.compile(
    r'[\s,]*[\u201c"]([^\u201d"]{3,})[\u201d"][\s,]*'
)
_UNCLOSED_QUOTED_GLOSS_RE = re.compile(r'[\s,]*[\u201c"]([^\u201d"]{3,})\s*$')
_ORPHAN_CLOSING_QUOTE_END_RE = re.compile(r'[\s,]*[\u201c\u201d"]\s*$')
_ORPHAN_CLOSING_QUOTE_MID_RE = re.compile(r'[\s,]+[\u201d"]+(?=\s|$)')


def _quoted_inner_is_gloss(inner: str) -> bool:
    if re.search(r"[a-z]{3,}", inner):
        return True
    if re.search(r"\blike\b", inner, re.IGNORECASE):
        return True
    return paren_inner_is_gloss(inner)


def extract_field_wrapped_quoted_gloss_from_field(
    text: str,
) -> tuple[str, list[str]]:
    """Remove a field that is entirely a quoted prose gloss."""
    if not text:
        return text, []
    match = _FIELD_WRAPPED_QUOTED_GLOSS_RE.match(text)
    if match and _quoted_inner_is_gloss(match.group(1)):
        return "", [match.group(0).strip()]
    return text, []


def extract_leading_quoted_gloss_from_field(text: str) -> tuple[str, list[str]]:
    """Remove field-leading quoted prose glosses."""
    if not text:
        return text, []
    match = _FIELD_LEADING_QUOTED_GLOSS_RE.match(text)
    if match and _quoted_inner_is_gloss(match.group(1)):
        return text[match.end() :].strip(), [match.group(0).strip()]
    return text, []


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
        extract_field_wrapped_quoted_gloss_from_field,
        extract_leading_quoted_gloss_from_field,
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
    stages = parts.get("stages")
    if stages is not None:
        new_stages: list[str] = []
        for original in stages:
            wrapped_cleaned, wrapped_caps = (
                extract_field_wrapped_quoted_gloss_from_field(original)
            )
            if wrapped_caps:
                value = wrapped_cleaned
                comment_fragments.extend(wrapped_caps)
            else:
                value, captures = extract_trailing_gloss_from_field(original)
                comment_fragments.extend(captures)
                if not value:
                    value = original
            new_stages.append(value)
        cleaned["stages"] = new_stages
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key not in parts:
            continue
        original = parts[key]
        wrapped_cleaned, wrapped_caps = extract_field_wrapped_quoted_gloss_from_field(
            original
        )
        if wrapped_caps:
            value = wrapped_cleaned
            comment_fragments.extend(wrapped_caps)
        else:
            value, captures = extract_trailing_gloss_from_field(original)
            comment_fragments.extend(captures)
        if value:
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


_CATCH_ALL_ELSE_ENV_RE = re.compile(r"^\s*else\??\s*$", re.IGNORECASE)
_ELSE_ENV_CANDIDATE_RE = re.compile(r"\belse\b", re.IGNORECASE)


def is_catch_all_else_env(env: str) -> bool:
    """Return whether ``env`` is a bare Index catch-all ``else`` / ``else?``."""
    return bool(env and _CATCH_ALL_ELSE_ENV_RE.match(env))


def _strip_else_env_glosses(env: str) -> tuple[str, list[str]]:
    """Strip trailing glosses and uncertainty qualifiers from an else env field."""
    captures: list[str] = []
    value, caps = extract_uncertainty_qualifier_from_field(env)
    captures.extend(caps)
    value, caps = extract_trailing_gloss_from_field(value)
    captures.extend(caps)
    return value.strip(), captures


def resolve_catch_all_else_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rewrite complementary ``/ else`` rules using the immediately preceding env.

    When the previous rule in the same section has ``env`` and no ``exception``,
    the else rule omits ``env`` (any environment) and sets ``exception`` to that
    previous ``env``. Deferred shapes (previous rule with both env and exception,
    neither, or else-after-else) keep ``env: else`` / ``else?``.
    """
    if not rules:
        return rules
    resolved_rules: list[dict[str, Any]] = []
    for rule in rules:
        resolved = dict(rule)
        env = resolved.get("env")
        if env and _ELSE_ENV_CANDIDATE_RE.search(env):
            env, gloss_captures = _strip_else_env_glosses(env)
            if gloss_captures:
                _append_rule_comment_parts(resolved, gloss_captures)
            if env:
                resolved["env"] = env
            elif "env" in resolved:
                del resolved["env"]

            if is_catch_all_else_env(env):
                prev = resolved_rules[-1] if resolved_rules else None
                if prev:
                    prev_env = prev.get("env")
                    prev_exc = prev.get("exception")
                    if (
                        prev_env
                        and not prev_exc
                        and not is_catch_all_else_env(prev_env)
                    ):
                        resolved = {
                            key: value for key, value in resolved.items() if key != "env"
                        }
                        resolved["exception"] = prev_env
        resolved_rules.append(resolved)
    return resolved_rules


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
                f"{row.index_feature!r} (supported: rename, rename_invert, rename_polarity, bundle)"
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
        if mapping.mapping_kind == "bundle":
            # Literal signed features in asca_target; index polarity ignored (Q12 deferred).
            return mapping.asca_target
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
    stages = result.get("stages")
    if stages is not None:
        result["stages"] = [
            normalize_feature_matrices_in_field(stage, table) for stage in stages
        ]
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key in result:
            result[key] = normalize_feature_matrices_in_field(result[key], table)
    return result


@dataclass(frozen=True)
class ParserConfig:
    ipa_mapping_confidence: frozenset[str]


def load_parser_config(path: Path | None = None) -> ParserConfig:
    """Load parser runtime settings from YAML."""
    config_path = DEFAULT_PARSER_CONFIG_PATH if path is None else Path(path)
    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    confidence = raw.get("ipa_mapping", {}).get(
        "confidence", DEFAULT_IPA_MAPPING_CONFIDENCE
    )
    return ParserConfig(ipa_mapping_confidence=frozenset(confidence))


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


def ipa_mappings_dict(
    path: Path | None = None,
    *,
    config: ParserConfig | None = None,
) -> dict[str, str]:
    """Return IPA mappings keyed by Index character for configured confidence levels."""
    confidences = (
        config.ipa_mapping_confidence
        if config is not None
        else load_parser_config().ipa_mapping_confidence
    )
    return {
        row.index_feature: row.ipa_target
        for row in load_ipa_mappings(path)
        if row.confidence in confidences and row.ipa_target
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
    *,
    config: ParserConfig | None = None,
) -> dict[str, str]:
    """Normalize Index IPA characters in rule fields; ``raw`` unchanged upstream."""
    table = mappings if mappings is not None else ipa_mappings_dict(config=config)
    if not table:
        return parts
    result = dict(parts)
    stages = result.get("stages")
    if stages is not None:
        result["stages"] = [normalize_ipa_in_field(stage, table) for stage in stages]
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key in result:
            result[key] = normalize_ipa_in_field(result[key], table)
    return result


def load_manual_mappings(path: Path | None = None) -> list[ManualMapping]:
    """Load owner-authored rule rewrites from CSV (``from``, ``to``; optional ``reason``)."""
    csv_path = DEFAULT_MANUAL_MAPPINGS_CSV if path is None else Path(path)
    if not csv_path.is_file():
        return []
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    required = {"from", "to"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"manual mappings CSV missing required columns: {sorted(missing)}"
        )
    has_reason = "reason" in df.columns
    seen: set[str] = set()
    out: list[ManualMapping] = []
    for record in df.to_dict(orient="records"):
        from_text = record["from"]
        if from_text in seen:
            raise ValueError(f"duplicate manual mapping from key: {from_text!r}")
        seen.add(from_text)
        out.append(
            ManualMapping(
                from_text=from_text,
                to_text=record["to"],
                reason=record["reason"] if has_reason else "",
            )
        )
    return out


def apply_manual_mappings(
    text: str,
    mappings: list[ManualMapping] | None = None,
) -> tuple[str, list[ManualMappingHit]]:
    """Replace ``from`` substrings with ``to`` (first occurrence each).

    Mappings are applied longest-``from`` first so a shorter pattern cannot steal
    a longer match when both would apply. Relative order among equal-length
    ``from`` keys follows CSV order (stable sort).
    """
    rows = mappings if mappings is not None else load_manual_mappings()
    if not text or not rows:
        return text, []
    # Prefer longest from first when order ambiguity matters.
    ordered = sorted(rows, key=lambda row: len(row.from_text), reverse=True)
    working = text
    hits: list[ManualMappingHit] = []
    for row in ordered:
        if row.from_text and row.from_text in working:
            working = working.replace(row.from_text, row.to_text, 1)
            hits.append(ManualMappingHit(from_text=row.from_text, to_text=row.to_text))
    return working, hits


MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS = [
    "section_index",
    "section_name",
    "rule_idx",
    "source",
    "manual_mapping",
]
MANUAL_MAPPINGS_MATCHED_CSV_NAME = "manual_mappings_matched_rules.csv"


def write_manual_mappings_matched_csv(
    matches: list[ManualMappingMatch],
    path: Path,
) -> Path:
    """Rewrite debug CSV of manual mapping hits (one row per applied pattern)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        {
            "section_index": match.section_index,
            "section_name": match.section_name,
            "rule_idx": match.rule_idx,
            "source": match.source,
            "manual_mapping": match.manual_mapping,
        }
        for match in matches
    ]
    df = pd.DataFrame(rows, columns=MANUAL_MAPPINGS_MATCHED_CSV_COLUMNS)
    df.to_csv(path, index=False)
    return path


# Index Diachronica stress mark (Key to Abbreviations: ” = Stress).
_INDEX_STRESS = "\u201d"

# Class letter or IPA vowel segment — not an English word continuation.
_STRESS_BOUNDARY = (
    r"(?=$|[\s→/\[,!\]_\.\)]|[A-Za-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF])"
)
_STRESS_VOWEL_CONTINUE = r"[aeiouyæøœɑɛɪɔʊəɨʉɯɤɐɒʌɜɞɶɤ]*"
_STRESS_SEGMENT = (
    rf"([A-Z]{_STRESS_VOWEL_CONTINUE}"
    rf"|[a-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]+{_STRESS_BOUNDARY})"
)
_STRESS_FEAT_SUFFIX = r"(\[[^\]]*\])?"

# P”_(C,0)B → P:[+stress]_(C,0)B.
_STRESS_CLASS_BEFORE_UNDERSCORE_RE = re.compile(
    rf"([A-Z]){re.escape(_INDEX_STRESS)}(?=_)"
)
# V(C)”(C)CaCV → V(C):[+stress](C)CaCV.
_STRESS_AFTER_CLOSE_PAREN_RE = re.compile(rf"\){re.escape(_INDEX_STRESS)}(?=\()")
# ” before a segment (rule input, e.g. ”V → …).
_STRESS_PREFIX_RE = re.compile(
    rf"{re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
# Boundary symbol then stress: #”U → #U:[+stress].
_STRESS_AFTER_BOUNDARY_RE = re.compile(
    rf"([#$_∅%]){re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
# After underscore boundary: #_”a → #_a:[+stress].
_STRESS_AFTER_UNDERSCORE_RE = re.compile(
    rf"(?<=_){re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
# After // comment boundary: // ”ə_V → // ə:[+stress]_V.
_STRESS_AFTER_DOUBLE_SLASH_RE = re.compile(
    rf"(//\s*){re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
# After Kleene star: _C*”{i,e}V → _C*{i:[+stress],e:[+stress]}V.
_STRESS_AFTER_STAR_SET_RE = re.compile(rf"\*{re.escape(_INDEX_STRESS)}\{{([^{{}}]+)\}}")
_STRESS_AFTER_STAR_SEGMENT_RE = re.compile(
    rf"\*{re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
)
# ”{i,e}V → {i:[+stress],e:[+stress]}V.
_STRESS_BEFORE_SET_RE = re.compile(
    rf"{re.escape(_INDEX_STRESS)}\{{([^{{}}]+)\}}(?:\s+{_STRESS_SEGMENT})?"
)
# After closing brace: {ʃ,ʒ}"{a,e}_ → {ʃ,ʒ}{a:[+stress],e:[+stress]}_.
_STRESS_BEFORE_SET_AFTER_CLOSE_RE = re.compile(
    rf"(?<=[}}]){re.escape(_INDEX_STRESS)}\{{([^{{}}]+)\}}"
)
# _(”u) → _(u:[+stress]).
_STRESS_IN_PAREN_RE = re.compile(
    rf"\({re.escape(_INDEX_STRESS)}([a-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]+)"
    rf"{_STRESS_FEAT_SUFFIX}\)"
)
# ”_$ɪ:[+long] → _$ɪ:[+stress,+long].
_STRESS_QUOTE_UNDERSCORE_SEGMENT_RE = re.compile(
    rf"{re.escape(_INDEX_STRESS)}_\$?"
    rf"([a-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]+)(:\[[^\]]+\])?"
)
# ”el:[+long] → el:[+stress,+long].
_STRESS_PREFIX_COLON_FEAT_RE = re.compile(
    rf"{re.escape(_INDEX_STRESS)}"
    rf"([a-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF]+)(:\[[^\]]+\])"
)
# V”(C) → V:[+stress](C).
_STRESS_BEFORE_PAREN_RE = re.compile(
    rf"(?<=[A-Za-z\u0250-\u02AF\u1D00-\u1DBF]){re.escape(_INDEX_STRESS)}(?=\()"
)
# ($,0)” in → ($,0):[+stress] in.
_STRESS_ORPHAN_AFTER_PAREN_RE = re.compile(
    rf"(\([^)]+\)){re.escape(_INDEX_STRESS)}(?=\s)"
)
# Infix stress between segments: C”V → CV:[+stress] (class letter after C).
_STRESS_INFIX_RE = re.compile(
    rf"(?<=[A-Za-z\u0250-\u02AF\u1D00-\u1DBF\u0370-\u03FF])"
    rf"{re.escape(_INDEX_STRESS)}{_STRESS_SEGMENT}{_STRESS_FEAT_SUFFIX}"
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
class ManualMapping:
    """One owner-authored substring rewrite from ``manual_mappings.csv``."""

    from_text: str
    to_text: str
    reason: str = ""


@dataclass(frozen=True)
class ManualMappingHit:
    """A single substring replace performed by ``apply_manual_mappings``."""

    from_text: str
    to_text: str


@dataclass(frozen=True)
class ManualMappingMatch:
    """Debug row for a manual mapping applied during ingest."""

    section_index: str
    section_name: str
    rule_idx: int
    source: str
    manual_mapping: str


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


def is_quoted_prose_paragraph(raw: str) -> bool:
    """True when a ``schg`` line is editorial prose wrapped in typographic quotes."""
    text = raw.strip()
    if not text.startswith(("\u201c", '"')):
        return False
    body = text[1:]
    if _quoted_inner_is_gloss(body):
        return True
    return len(text) > 40 and ARROW in text and bool(re.search(r"[a-z]{5,}", text))


def is_gloss_only_rule(parts: dict[str, Any]) -> bool:
    """True when gloss stripping removed all phonological stages."""
    return len(non_empty_stages(parts.get("stages", []))) < 2 and bool(
        parts.get("comment")
    )


def extract_rule_parts(raw: str) -> dict[str, Any] | None:
    """Split a raw rule string into ``stages`` and optional env/exception.

    Returns None if ``→`` is missing. Optional keys are omitted when absent.
    """
    raw = strip_leading_index_list_marker(raw)
    split = split_input_output(raw)
    if split is None:
        return None
    inp, post_arrow = split
    out, env, exception = split_post_arrow(post_arrow)
    stages = build_stages_from_spine(inp, out)
    parts: dict[str, Any] = {"stages": stages}
    if env is not None:
        parts["env"] = env
    if exception is not None:
        parts["exception"] = exception
    parts["stages"] = [normalize_rule_arrows(stage) for stage in parts["stages"]]
    if env is not None:
        parts["env"] = normalize_rule_arrows(parts["env"])
    if exception is not None:
        parts["exception"] = normalize_rule_arrows(parts["exception"])
    return parts


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

    def __init__(
        self,
        series_mappings: list | None = None,
        parser_config: ParserConfig | None = None,
        parser_config_path: Path | None = None,
        manual_mappings: list[ManualMapping] | None = None,
        manual_mappings_path: Path | None = None,
    ) -> None:
        if series_mappings is None:
            from conlanger.tools.series_mappings import load_series_mappings

            self._series_mappings = load_series_mappings()
        else:
            self._series_mappings = series_mappings

        if parser_config is not None:
            self._parser_config = parser_config
        else:
            self._parser_config = load_parser_config(parser_config_path)

        if manual_mappings is not None:
            self._manual_mappings = manual_mappings
        else:
            self._manual_mappings = load_manual_mappings(manual_mappings_path)

        self.manual_mapping_matches: list[ManualMappingMatch] = []
        self._matched_manual_froms: set[str] = set()

    def abbreviations(self) -> dict[str, str]:
        """Global abbreviation table for the cleaned corpus (empty at ingest)."""
        return {}

    def unmatched_manual_mappings(self) -> list[ManualMapping]:
        """Return loaded mappings whose ``from`` never matched during this parse."""
        return [
            row
            for row in self._manual_mappings
            if row.from_text not in self._matched_manual_froms
        ]

    def parse_rule_element(
        self,
        el,
        *,
        source_file: str,
        section_index: str = "",
        section_name: str = "",
        rule_idx: int = 0,
    ) -> list[dict[str, Any]]:
        raw = extract_text_with_subs(el)
        line = getattr(el, "sourceline", None) or 0
        source = f"{source_file}:{line}"
        working, hits = apply_manual_mappings(raw, self._manual_mappings)
        for hit in hits:
            self._matched_manual_froms.add(hit.from_text)
            self.manual_mapping_matches.append(
                ManualMappingMatch(
                    section_index=section_index,
                    section_name=section_name,
                    rule_idx=rule_idx,
                    source=source,
                    manual_mapping=hit.to_text,
                )
            )
        if is_quoted_prose_paragraph(working):
            return [
                {
                    "stages": [],
                    "raw": raw,
                    "source": source,
                    "comment": raw.strip(),
                    "status": "skipped",
                }
            ]
        normalized = normalize_symbols(working)
        parts = extract_rule_parts(normalized)
        if parts is None:
            return [
                {
                    "stages": [],
                    "raw": raw,
                    "source": source,
                    "status": "skipped",
                }
            ]
        parts = apply_semicolon_field_comments(parts)
        parts = apply_sporadic_qualifier(parts)
        sporadic = parts.pop("sporadic", False)
        sporadic_flag = {"sporadic": True} if sporadic else {}
        parts = apply_trailing_glosses(parts)
        if is_gloss_only_rule(parts):
            return [
                {
                    "stages": [],
                    "raw": raw,
                    "source": source,
                    "comment": parts["comment"],
                    "status": "skipped",
                    **sporadic_flag,
                }
            ]
        parts = apply_stress_conditions(parts)
        parts = apply_feature_mappings(parts)
        parts = apply_ipa_mappings(parts, config=self._parser_config)
        from conlanger.tools.series_mappings import apply_series_mappings

        parts = apply_series_mappings(parts, section_index, self._series_mappings)
        parts = finalize_stages_shape(parts)
        return [{**parts, "raw": raw, "source": source, **sporadic_flag}]

    def parse(
        self,
        html_path: Path,
        *,
        source_file: str | None = None,
    ) -> dict[str, Any]:
        """Parse HTML into ``{abbreviations, sections: [...]}``."""
        source_file = source_file or html_path.name
        self.manual_mapping_matches = []
        self._matched_manual_froms = set()
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
                            section_name=name,
                            rule_idx=len(rules),
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
                section_obj["rules"] = resolve_catch_all_else_rules(rules)
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
