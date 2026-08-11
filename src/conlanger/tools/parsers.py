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
field-level glosses and env qualifiers. Index word-internal ``medial`` / ``medially`` env
prose becomes ``env: _`` with boundary ``exception: :{#_, _#}:`` (``apply_medial_env_conditions``).
Class-letter expansion is deferred to compile time (``PhonologicalRuleSet`` +
``group_mappings.csv``).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from lxml import html

from conlanger.utils.gloss import (
    extract_field_wrapped_quoted_gloss_from_field,
    extract_trailing_gloss_from_field,
    is_gloss_only_rule,
    is_quoted_prose_paragraph,
)
from conlanger.utils.mappings import (
    FeatureMapping,
    ManualMapping,
    ManualMappingMatch,
    ParserConfig,
    apply_feature_mappings,
    apply_ipa_mappings,
    apply_manual_mappings,
)
from conlanger.utils.parsing import (
    extract_rule_parts,
    extract_text_with_subs,
    finalize_stages_shape,
    parse_section_heading,
    strip_whitespace,
)
from conlanger.utils.series import (
    SeriesMapping,
    apply_series_mappings,
    section_abbreviations_for_index,
)

# Protect Index stem ``$`` while remapping syllable-boundary ``%`` → ASCA ``$``.
_STEM_BOUNDARY_PLACEHOLDER = "\ue000"

_CORPUS_CONTEXT_FIELD_KEYS = ("env", "exception")


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


_UNCERTAINTY_WORDS = r"sporadic(?:ally)?|sometimes|occasionally"
_UNCERTAINTY_WORD_RE = re.compile(rf"\b(?:{_UNCERTAINTY_WORDS})\b", re.IGNORECASE)
_LONE_UNCERTAINTY_RE = re.compile(rf"^(?:{_UNCERTAINTY_WORDS})\??\.?$", re.IGNORECASE)
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


MEDIAL_BOUNDARY_EXCEPTION = ":{#_, _#}:"
_BARE_MEDIAL_ENV_RE = re.compile(r"^\s*medial(?:ly)?\s*,?\s*$", re.IGNORECASE)
_BARE_WHEN_MEDIAL_ENV_RE = re.compile(r"^\s*when\s+medial(?:ly)?\s*$", re.IGNORECASE)
_WHEN_MEDIAL_SUFFIX_RE = re.compile(r"(?:,\s*)?when\s+medial(?:ly)?\s*$", re.IGNORECASE)


def normalize_medial_env_field(text: str) -> tuple[str, bool]:
    """Normalize Index ``medial`` / ``medially`` env prose for ASCA word-internal focus."""
    if not text:
        return text, False
    stripped = text.strip()
    if _BARE_MEDIAL_ENV_RE.match(stripped) or _BARE_WHEN_MEDIAL_ENV_RE.match(stripped):
        return "_", True
    match = _WHEN_MEDIAL_SUFFIX_RE.search(stripped)
    if match:
        return stripped[: match.start()].rstrip(), True
    return text, False


def apply_medial_env_conditions(parts: dict[str, Any]) -> dict[str, Any]:
    """Rewrite Index word-internal ``medial`` env prose to ``_`` + boundary exception."""
    result: dict[str, Any] = dict(parts)
    if result.get("exception"):
        return result
    env = result.get("env")
    if not env:
        return result
    normalized, is_medial = normalize_medial_env_field(env)
    if not is_medial:
        return result
    result["env"] = normalized
    result["exception"] = MEDIAL_BOUNDARY_EXCEPTION
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
                            key: value
                            for key, value in resolved.items()
                            if key != "env"
                        }
                        resolved["exception"] = prev_env
        resolved_rules.append(resolved)
    return resolved_rules


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


def note_from_element(el, *, source_file: str) -> dict[str, Any]:
    raw = extract_text_with_subs(el)
    line = getattr(el, "sourceline", None) or 0
    return {
        "raw": raw,
        "source": f"{source_file}:{line}",
    }


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
        *,
        series_mappings: list[SeriesMapping],
        manual_mappings: list[ManualMapping],
        parser_config: ParserConfig,
        feature_mappings: dict[str, FeatureMapping],
        ipa_mappings: dict[str, str],
    ) -> None:
        self._series_mappings = series_mappings
        self._manual_mappings = manual_mappings
        self._parser_config = parser_config
        self._feature_mappings = feature_mappings
        self._ipa_mappings = ipa_mappings
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
        parts = apply_medial_env_conditions(parts)
        parts = apply_feature_mappings(parts, self._feature_mappings)
        parts = apply_ipa_mappings(parts, self._ipa_mappings)
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

            rules: list[dict[str, Any]] = []
            citation: str | None = None
            comments: list[dict[str, Any]] = []
            saw_first_p = False

            for p in sec.xpath("./p"):
                cls = p.get("class") or ""
                if "schg" in cls:
                    saw_first_p = True
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
    parser: IndexDiachronicaParser,
) -> list[dict[str, Any]]:
    """Delegate to an injected parser instance (callers must supply tables)."""
    return parser.parse_rule_element(
        el,
        source_file=source_file,
        section_index=section_index,
    )
