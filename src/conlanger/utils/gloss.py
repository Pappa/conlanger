"""Index prose gloss detection and stripping for rule field values."""

from __future__ import annotations

import re
from typing import Any

from conlanger.utils.parsing import ARROW, non_empty_stages

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
_FIELD_WRAPPED_QUOTED_GLOSS_RE = re.compile(r'^[\u201c"]([^\u201d"]+)[\u201d"]\s*$')
_FIELD_LEADING_QUOTED_GLOSS_RE = re.compile(r'^[\u201c"]([^\u201d"]{10,})[\u201d"]?\s*')
_EMBEDDED_QUOTED_GLOSS_RE = re.compile(
    r'[\s,]*[\u201c"]([^\u201d"]{3,})[\u201d"][\s,]*'
)
_UNCLOSED_QUOTED_GLOSS_RE = re.compile(r'[\s,]*[\u201c"]([^\u201d"]{3,})\s*$')
_ORPHAN_CLOSING_QUOTE_END_RE = re.compile(r'[\s,]*[\u201c\u201d"]\s*$')
_ORPHAN_CLOSING_QUOTE_MID_RE = re.compile(r'[\s,]+[\u201d"]+(?=\s|$)')


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
    if ("…" in text or "..." in text) and re.fullmatch(r"[A-Z#_\[\].…]+", text):
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


def _quoted_inner_is_gloss(inner: str) -> bool:
    if re.search(r"[a-z]{3,}", inner):
        return True
    if re.search(r"\blike\b", inner, re.IGNORECASE):
        return True
    return paren_inner_is_gloss(inner)


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
    if (
        re.match(r'[a-z"\u201c(]', tail)
        and re.search(r"[a-z]{3,}", tail)
        and not re.match(r"[_#\[\{]", tail.lstrip())
    ):
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
