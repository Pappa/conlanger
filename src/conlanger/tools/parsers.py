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
Index rule arrows (``→``) in field values become ASCA ``>``. Chained rules without
``env``/``exception`` expand into sequential single-step rules. Uncertainty glosses
(``sporadic``, ``sometimes``, …) are stripped from field values and recorded as
``sporadic: true``. Class-letter expansion is deferred to compile time
(``PhonologicalRuleSet`` + ``group_mappings.csv``).
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

# Protect Index stem ``$`` while remapping syllable-boundary ``%`` → ASCA ``$``.
_STEM_BOUNDARY_PLACEHOLDER = "\ue000"

# Index list-item em dash (U+2014) at the start of a rule line — not phonological.
_LEADING_INDEX_LIST_MARKER_RE = re.compile(r"^—\s*")


def strip_leading_index_list_marker(text: str) -> str:
    """Remove Index list-item em dash from the start of a rule line."""
    if not text:
        return text
    return _LEADING_INDEX_LIST_MARKER_RE.sub("", text, count=1)


def normalize_rule_arrows(text: str) -> str:
    """Map Index rule arrow ``→`` to ASCA ``>`` in one field value."""
    if not text or ARROW not in text:
        return text
    return text.replace(ARROW, ">")


_UNCERTAINTY_WORD_RE = re.compile(r"\b(?:sporadic(?:ally)?|sometimes)\b", re.I)
_LONE_UNCERTAINTY_RE = re.compile(r"^(?:sporadic(?:ally)?|sometimes)\??\.?$", re.I)
_ENV_UNCERTAINTY_PREFIX_RE = re.compile(
    r"^sporadic(?:ally)?(?:,\s*usually)?\s*,?\s*",
    re.I,
)
_TRAILING_PAREN_WITH_UNCERTAINTY_RE = re.compile(
    r"\s*\([^)]*(?:sporadic(?:ally)?|sometimes)[^)]*\)\s*$",
    re.I,
)
_TRAILING_QUOTED_WITH_UNCERTAINTY_RE = re.compile(
    r'\s*(?:[("\u201c][^"\u201d)]*(?:sporadic(?:ally)?|sometimes)[^"\u201d)]*[)\u201d"]|"[^"]*(?:sporadic(?:ally)?|sometimes)[^"]*")\s*$',
    re.I,
)
_TRAILING_BARE_UNCERTAINTY_RE = re.compile(
    r"\s*(?:\()?[\s\u201c\"']*(?:sporadic(?:ally)?|sometimes)\??[\s\u201d\"')]*\)?\s*$",
    re.I,
)


def field_has_uncertainty_qualifier(text: str) -> bool:
    """Return whether ``text`` mentions sporadic / sometimes uncertainty."""
    return bool(text and _UNCERTAINTY_WORD_RE.search(text))


def strip_uncertainty_qualifier_from_field(text: str) -> str:
    """Remove sporadic / sometimes glosses from one rule field value."""
    if not text:
        return text
    text = text.strip()
    if _LONE_UNCERTAINTY_RE.match(text):
        return ""
    text = _ENV_UNCERTAINTY_PREFIX_RE.sub("", text).strip()
    if field_has_uncertainty_qualifier(text):
        text = _TRAILING_PAREN_WITH_UNCERTAINTY_RE.sub("", text).strip()
    if field_has_uncertainty_qualifier(text):
        text = _TRAILING_QUOTED_WITH_UNCERTAINTY_RE.sub("", text).strip()
    if field_has_uncertainty_qualifier(text):
        text = _TRAILING_BARE_UNCERTAINTY_RE.sub("", text).strip()
    return text.strip()


def apply_sporadic_qualifier(parts: dict[str, str]) -> dict[str, Any]:
    """Strip uncertainty glosses from rule fields; set ``sporadic: true`` when found."""
    sporadic = False
    cleaned: dict[str, str] = {}
    for key in ("input", "output", "env", "exception"):
        if key not in parts:
            continue
        value = parts[key]
        if field_has_uncertainty_qualifier(value):
            sporadic = True
        value = strip_uncertainty_qualifier_from_field(value)
        if key in ("input", "output") or value:
            cleaned[key] = value
    result: dict[str, Any] = cleaned
    if sporadic:
        result["sporadic"] = True
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


def expand_chained_rule_parts(parts: dict[str, str]) -> list[dict[str, str]]:
    """Split a no-env chain ``a > b > c`` into sequential single-step rules.

    Only applies when ``output`` contains `` > `` and there is no ``env`` or
    ``exception`` — chained rules with environments stay as one corpus row.
    """
    if parts.get("env") or parts.get("exception"):
        return [parts]
    output = parts.get("output", "")
    if " > " not in output:
        return [parts]
    segments = [segment.strip() for segment in output.split(" > ") if segment.strip()]
    if len(segments) < 2:
        return [parts]
    expanded: list[dict[str, str]] = []
    current_input = parts["input"]
    for segment in segments:
        expanded.append({"input": current_input, "output": segment})
        current_input = segment
    return expanded


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


class IndexDiachronicaParser:
    """Parse Index Diachronica HTML into applier-neutral cleaned-corpus YAML."""

    def abbreviations(self) -> dict[str, str]:
        """Global abbreviation table for the cleaned corpus (empty at ingest)."""
        return {}

    def parse_rule_element(self, el, *, source_file: str) -> list[dict[str, Any]]:
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
        parts = apply_sporadic_qualifier(parts)
        sporadic = parts.pop("sporadic", False)
        sporadic_flag = {"sporadic": True} if sporadic else {}
        return [
            {**entry, "raw": raw, "source": source, **sporadic_flag}
            for entry in expand_chained_rule_parts(parts)
        ]

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
                        self.parse_rule_element(p, source_file=source_file)
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


def parse_rule_element(el, *, source_file: str) -> list[dict[str, Any]]:
    return IndexDiachronicaParser().parse_rule_element(el, source_file=source_file)
