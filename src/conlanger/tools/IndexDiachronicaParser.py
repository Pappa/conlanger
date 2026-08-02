"""Parse Index Diachronica HTML into the cleaned rule-corpus shape (incremental).

Phase 1: section structure + per-rule ``input`` / ``output`` split on ``→``
(whitespace around the arrow is trimmed).
Phase 2: optional ``/ env`` then optional ``! exception``
(usual form ``input → output /env ! exception``). Word ``except`` and a
second `` / `` are edge-case fallbacks.
Phase 3: first ``<p>`` after ``<h2>`` → section ``citation`` (whole text, cleanup later);
other non-``schg`` paragraphs → ``comments``.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
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
    Path(__file__).resolve().parents[1] / "data" / "group_mappings.csv"
)

GroupMappingTuple = tuple[str, str] | tuple[str, str, str]


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


def extract_rule_parts(raw: str) -> dict[str, str] | None:
    """Split a raw rule string into input, output, and optional env/exception.

    Returns None if ``→`` is missing. Optional keys are omitted when absent.
    """
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


def _coerce_group_mapping(item: GroupMapping | GroupMappingTuple) -> GroupMapping:
    if isinstance(item, GroupMapping):
        return item
    if isinstance(item, tuple):
        if len(item) == 2:
            return GroupMapping(item[0], item[1])
        if len(item) == 3:
            return GroupMapping(item[0], item[1], item[2])
    raise TypeError(
        "group_mappings items must be GroupMapping or 2-/3-tuples "
        f"(grouping, mapping[, comment]); got {item!r}"
    )


class IndexDiachronicaParser:
    """Parse Index Diachronica HTML, optionally remapping group letters."""

    def __init__(
        self,
        group_mappings: Sequence[GroupMapping | GroupMappingTuple] | None = None,
    ) -> None:
        self._group_mappings = (
            [_coerce_group_mapping(item) for item in group_mappings]
            if group_mappings
            else []
        )
        self._abbreviations = {
            m.grouping: m.mapping for m in self._group_mappings
        }
        self._trans = (
            str.maketrans(self._abbreviations) if self._abbreviations else None
        )

    def abbreviations(self) -> dict[str, str]:
        return dict(self._abbreviations)

    def apply_group_mappings(self, text: str) -> str:
        if self._trans is None:
            return text
        return text.translate(self._trans)

    def parse_rule_element(self, el, *, source_file: str) -> dict[str, Any]:
        raw = extract_text_with_subs(el)
        line = getattr(el, "sourceline", None) or 0
        source = f"{source_file}:{line}"
        parts = extract_rule_parts(self.apply_group_mappings(raw))
        if parts is None:
            return {
                "input": "",
                "output": "",
                "raw": raw,
                "source": source,
                "skipped": f"missing separator {ARROW!r}",
            }
        return {
            **parts,
            "raw": raw,
            "source": source,
        }

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
                    saw_first_p = True  # citation slot consumed even if first p was a rule
                    rules.append(self.parse_rule_element(p, source_file=source_file))
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


def parse_rule_element(
    el,
    *,
    source_file: str,
    group_mappings: Sequence[GroupMapping | GroupMappingTuple] | None = None,
) -> dict[str, Any]:
    return IndexDiachronicaParser(group_mappings).parse_rule_element(
        el, source_file=source_file
    )
