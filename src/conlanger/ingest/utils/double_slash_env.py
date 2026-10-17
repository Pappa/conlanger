"""Parse-time normalization for Index ``//`` env shorthand and prose exceptions (ticket 108)."""

from __future__ import annotations

import re
from typing import Any

from conlanger.ingest.models.index_models import IndexContext, IndexRule
from conlanger.ingest.utils.prose_position_env import normalize_bare_prose_position_env
from conlanger.utils.gloss import extract_uncertainty_qualifier_from_field

_DOUBLE_SLASH_SEP = " // "

_BEFORE_IDENTICAL_VOWEL_RE = re.compile(
    r"^before\s+an?\s+identical\s+vowel\s*$",
    re.IGNORECASE,
)
_DIALECT_NAME_RE = re.compile(r"^[A-Z][a-zA-Z]+$")
_TYPICALLY_SUFFIX_RE = re.compile(r",\s*typically\s*$", re.IGNORECASE)
_ODD_SYLLABLES_RE = re.compile(r"^(?:in\s+)?odd\s+syllables?\s*$", re.IGNORECASE)
_MAYBE_ENV_RE = re.compile(r"^maybe\??\s*$", re.IGNORECASE)
_VOID_ENV_RE = re.compile(r"^∅$")
_BARE_PERCENT_FEATURE_RE = re.compile(r"^%(\[[^\]]+\]|:[^\s,]+)$")
_BARE_U_FEATURE_RE = re.compile(r"^U(\[[^\]]+\]|:[^\s,]+)$")
_BROKEN_EXCEPTION_TAIL_RE = re.compile(
    r"^(_[^,]+),\s*short\s+only\)\s*$",
    re.IGNORECASE,
)
_COMPLEX_PROSE_EXCEPTION_RE = re.compile(
    r"^#% with the following",
    re.IGNORECASE,
)
_VOICE_EARLIER_RE = re.compile(
    r"^O\[\+voic",
    re.IGNORECASE,
)
_PENULT_RE = re.compile(r"^penult\s*$", re.IGNORECASE)


def split_embedded_double_slash(text: str) -> tuple[str, str | None]:
    """Split ``env`` text on Index `` // `` into env head and optional tail."""
    if not text or _DOUBLE_SLASH_SEP not in text:
        return text, None
    head, tail = text.split(_DOUBLE_SLASH_SEP, 1)
    return head.rstrip(), tail.strip() or None


def _merge_position(
    ctx: IndexContext | None,
    *,
    context: str | None = None,
    position: dict[str, Any] | None = None,
    clear_context: bool = False,
) -> IndexContext | None:
    """Merge parse updates into an ``IndexContext``."""
    if ctx is None and context is None and not position:
        return None
    base_context = None if clear_context else (ctx.context if ctx else None)
    if context is not None:
        base_context = context
    merged_position: dict[str, Any] = dict(ctx.position or {}) if ctx else {}
    if position:
        merged_position.update(position)
    if (
        not base_context
        and not merged_position
        and (ctx is None or ctx.dialect is None)
    ):
        return None
    return IndexContext(
        context=base_context,
        position=merged_position or None,
        dialect=ctx.dialect if ctx else None,
    )


def normalize_prose_exception_or_env_tail(
    text: str,
) -> tuple[IndexContext | None, list[str], dict[str, Any]]:
    """Normalize prose ``//`` exception tails and bare exception-only rules."""
    if not text:
        return None, [], {}
    stripped = text.strip()
    flags: dict[str, Any] = {}
    captures: list[str] = []

    normalized, pos_captures, pos_flags = normalize_bare_prose_position_env(stripped)
    if normalized != stripped or pos_captures or pos_flags:
        captures.extend(pos_captures)
        flags.update(pos_flags)
        return IndexContext(context=normalized), captures, flags

    if _BEFORE_IDENTICAL_VOWEL_RE.match(stripped):
        return IndexContext(context="V_V"), [stripped], flags

    if _PENULT_RE.match(stripped):
        return IndexContext(position={"penult": True}), [stripped], flags

    if _DIALECT_NAME_RE.match(stripped):
        return None, [stripped], flags

    if _COMPLEX_PROSE_EXCEPTION_RE.match(stripped) or _VOICE_EARLIER_RE.match(stripped):
        return IndexContext(context=text), [stripped], flags

    match = _BROKEN_EXCEPTION_TAIL_RE.match(stripped)
    if match:
        captures.append("short only")
        return IndexContext(context=match.group(1)), captures, flags

    match = _BARE_PERCENT_FEATURE_RE.match(stripped) or _BARE_U_FEATURE_RE.match(
        stripped
    )
    if match:
        prefix = stripped[0]
        # TODO: this is not correct
        return IndexContext(context=f"{prefix}{match.group(1)}"), [stripped], flags

    return IndexContext(context=text), captures, flags


def apply_double_slash_env_conditions(rule: IndexRule) -> IndexRule:
    """Normalize Index ``//`` env shorthand and prose exceptions (ticket 108)."""
    comment_fragments: list[str] = []
    flags: dict[str, Any] = {}

    env_ctx = rule.env
    exc_ctx = rule.exception

    if env_ctx is not None and env_ctx.context:
        env_text = env_ctx.context
        head, embedded_tail = split_embedded_double_slash(env_text)
        if embedded_tail:
            env_text = head
            if exc_ctx is not None:
                comment_fragments.append(embedded_tail)
            else:
                exc_ctx = IndexContext(context=embedded_tail)

        normalized_head, head_captures, head_flags = normalize_prose_env_head(env_text)
        if normalized_head != env_text or head_captures or head_flags:
            env_text = normalized_head
            comment_fragments.extend(head_captures)
            flags.update(head_flags)
        elif embedded_tail:
            env_text = head

        env_ctx = _merge_position(
            env_ctx,
            context=env_text if env_text else None,
            clear_context=not env_text,
        )

    if exc_ctx is not None and exc_ctx.context:
        original_exception = exc_ctx.context
        value, uncertainty_captures = extract_uncertainty_qualifier_from_field(
            original_exception
        )
        if uncertainty_captures:
            comment_fragments.extend(uncertainty_captures)
            flags["sporadic"] = True

        normalized_ctx, tail_captures, tail_flags = (
            normalize_prose_exception_or_env_tail(value)
        )
        if (
            normalized_ctx is not None
            or tail_captures
            or tail_flags
            or value != original_exception
        ):
            if normalized_ctx is None:
                exc_ctx = None
            else:
                exc_ctx = _merge_position(
                    exc_ctx,
                    context=normalized_ctx.context,
                    position=dict(normalized_ctx.position or {}),
                    clear_context=normalized_ctx.context is None,
                )
            comment_fragments.extend(tail_captures)
            flags.update(tail_flags)

    rule.env = env_ctx
    rule.exception = exc_ctx
    rule.merge_comment(*comment_fragments)
    if flags.get("sporadic"):
        rule.sporadic = True
    return rule


def normalize_prose_env_head(
    text: str,
) -> tuple[str, list[str], dict[str, Any]]:
    """Normalize prose env heads that block ASCA before ``//`` exception tails."""
    if not text:
        return text, [], {}
    stripped = text.strip()
    flags: dict[str, Any] = {}
    captures: list[str] = []

    match = _TYPICALLY_SUFFIX_RE.search(stripped)
    if match:
        captures.append("typically")
        stripped = stripped[: match.start()].rstrip()

    if _MAYBE_ENV_RE.match(stripped):
        flags["sporadic"] = True
        return "_", ["maybe"], flags

    if _VOID_ENV_RE.match(stripped):
        return "", [], flags

    if _ODD_SYLLABLES_RE.match(stripped):
        return "_", [stripped], flags

    normalized, pos_captures, pos_flags = normalize_bare_prose_position_env(stripped)
    if normalized != stripped or pos_captures or pos_flags:
        captures.extend(pos_captures)
        flags.update(pos_flags)
        return normalized, captures, flags

    match = _BARE_PERCENT_FEATURE_RE.match(stripped) or _BARE_U_FEATURE_RE.match(
        stripped
    )
    if match:
        prefix = stripped[0]
        # TODO: this is not correct
        return f"{prefix}{match.group(1)}", [stripped], flags

    return stripped, captures, flags
