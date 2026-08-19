"""Rule-string splitting and HTML text extraction shared across ingest modules."""

from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from typing import Any

from lxml import html

ARROW = "→"
ENV_SEP = " / "
GLUED_ENV_SEP = "/ "

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

BANG_EXCEPTION_RE = re.compile(r"\s*!\s*")
TRAILING_EXCEPTION_RE = re.compile(r"(?:,\s*|\s+)except\s+(.*)$", re.IGNORECASE)
LEADING_EXCEPTION_RE = re.compile(r"^(?:,\s*)?except\s+(.*)$", re.IGNORECASE)

_LEADING_INDEX_LIST_MARKER_RE = re.compile(r"^—\s*")


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


def normalize_rule_arrows(text: str) -> str:
    """Map Index rule arrow ``→`` to ASCA ``>`` in one field value."""
    if not text or ARROW not in text:
        return text
    return text.replace(ARROW, ">")


def to_subscript(text: str) -> str:
    return "".join(
        ch.translate(SUBSCRIPT_MAP)
        if ch.lower() in "0123456789aehijklmnoprstuvx"
        else ch
        for ch in text
    )


def strip_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ").replace("\r", " ")).strip()


_SUB_TAG_RE = re.compile(r"<sub>(.*?)</sub>", re.DOTALL | re.IGNORECASE)


def normalize_html_sub_tags(html_text: str) -> str:
    """Replace ``<sub>…</sub>`` with Unicode subscripts before lxml parse.

    Tags whose inner content contains nested markup are left unchanged.
    """

    def replace(match: re.Match[str]) -> str:
        inner = match.group(1)
        if "<" in inner or ">" in inner:
            return match.group(0)
        return to_subscript(inner)

    return _SUB_TAG_RE.sub(replace, html_text)


def load_html_document(html_path: Path) -> html.HtmlElement:
    """Load HTML from disk with pre-lxml ``<sub>`` normalisation (in-memory only)."""
    text = normalize_html_sub_tags(html_path.read_text(encoding="utf-8"))
    parser = html.HTMLParser(encoding="utf-8")
    doc = html.parse(BytesIO(text.encode("utf-8")), parser=parser)
    return doc.getroot()


def extract_text_with_subs(el) -> str:
    """Element text (``<sub>`` should already be Unicode from pre-parse normalisation)."""
    parts: list[str] = []

    def walk(node) -> None:
        if node.text:
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
    """Split post-arrow text on the first env delimiter into output and rest.

    Usual Index form is ``\" / \"``. A slash glued to the output (``∅/ _#``)
    is the same delimiter without the preceding space, but only when the
    remainder looks like an environment (starts with ``_``, ``#``, or ``!``)
    so phonemic slashes like ``/š/`` are not treated as delimiters.
    """
    text = post_arrow.strip()
    if ENV_SEP in text:
        out, rest = text.split(ENV_SEP, 1)
        out, rest = out.strip(), rest.strip()
        return out, rest or None
    if GLUED_ENV_SEP in text:
        out, rest = text.split(GLUED_ENV_SEP, 1)
        out, rest = out.strip(), rest.strip()
        if out and rest[:1] in "#_!":
            return out, rest
    return text, None


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
        trail = TRAILING_EXCEPTION_RE.search(out)
        if trail:
            return out[: trail.start()].rstrip(), None, trail.group(1).strip() or None
        return out, None, None
    env, exception = split_env_exception(rest)
    return out, env, exception


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


def parse_section_heading(h2_text: str) -> tuple[str, str]:
    m = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", h2_text.strip())
    if not m:
        return "", h2_text.strip()
    return m.group(1).strip(), m.group(2).strip()
