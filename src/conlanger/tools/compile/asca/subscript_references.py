"""Compile-time expansion of Index positional slots and identity subscripts."""

from __future__ import annotations

import re

from conlanger.utils.series import (
    is_identity_subscript_token,
    is_positional_slot_token,
)

_SUBSCRIPT_TO_ASCII = str.maketrans("₀₁₂₃₄₅₆₇₈₉", "0123456789")
_SUBSCRIPT_CHAR_RE = re.compile(r"[₀₁₂₃₄₅₆₇₈₉]")
_PROSE_FIELD_RE = re.compile(
    r"\b(?:if|was|were|when|before|after|includes?|disputed|unclear)\b|=",
    re.IGNORECASE,
)
# Order matters: matrix/diacritic forms before bare slots.
_SLOT_RE = re.compile(
    r"(?P<matrix_sub>(?P<ms_base>[A-Za-z]+):(?P<ms_feats>\[[^\]]+\])"
    r"(?P<ms_sub>[₀₁₂₃₄₅₆₇₈₉]))"
    r"|(?P<sub_matrix>(?P<sm_base>[A-Za-z])(?P<sm_sub>[₀₁₂₃₄₅₆₇₈₉])"
    r"(?P<sm_feats>\[[^\]]+\]))"
    r"|(?P<phar>(?P<p_base>[A-Z]+)(?P<p_sub>[₁₂₃₄₅₆₇₈₉])ˤ)"
    r"|(?P<pos>(?P<po_base>[A-Z]+)(?P<po_sub>[₁₂₃₄₅₆₇₈₉]))"
    r"|(?P<ident>(?P<id_base>[A-Za-z])₀)"
)
_SPACE_BEFORE_LENGTH_OR_MATRIX_RE = re.compile(r"(\d)\s+(?=[ː\[])")
_PAREN_REF_OPTIONAL_RE = re.compile(r"\(\s*(\d+)\s*\)")


def _split_rule_fields(text: str) -> tuple[str, str, str | None, str | None]:
    exception: str | None = None
    if " // " in text:
        text, exception = text.split(" // ", 1)
    env: str | None = None
    if " > " in text:
        inp, rest = text.split(" > ", 1)
        if " / " in rest:
            output, env = rest.split(" / ", 1)
        else:
            output = rest
    else:
        inp = text
        output = ""
    return inp, output, env, exception


def _join_rule_fields(
    inp: str,
    output: str,
    env: str | None,
    exception: str | None,
) -> str:
    result = f"{inp} > {output}"
    if env:
        result += f" / {env}"
    if exception:
        result += f" // {exception}"
    return result


def _normalize_field_spacing(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = _SPACE_BEFORE_LENGTH_OR_MATRIX_RE.sub(r"\1", text)
    # Index ``(C₃)`` → bare ``(3)`` after slot expand; ASCA wants structure ``{3}``.
    return _PAREN_REF_OPTIONAL_RE.sub(r"{\1}", text)


def _is_prose_field(text: str) -> bool:
    """Whether a field is Index editorial prose rather than ASCA structure."""
    return bool(_PROSE_FIELD_RE.search(text))


def _emit_ref(
    base: str,
    digit: int,
    declared: set[int],
    feats: str | None = None,
    *,
    redeclare_with_base: bool = False,
) -> str:
    """Emit ASCA reference declaration or invoke, optionally with a matrix."""
    if feats and redeclare_with_base:
        declared.add(digit)
        return f"{base}:{feats}={digit}"
    if digit not in declared:
        declared.add(digit)
        if feats:
            return f"{base}:{feats}={digit}"
        return f"{base}={digit}"
    if feats:
        return f"{digit}:{feats}"
    return str(digit)


def _expand_field_segment(
    segment: str,
    declared: set[int],
    *,
    redeclare_identity_matrix: bool = False,
) -> str:
    parts: list[str] = []
    last = 0
    for match in _SLOT_RE.finditer(segment):
        parts.append(segment[last : match.start()])
        if match.group("matrix_sub"):
            digit = int(match.group("ms_sub").translate(_SUBSCRIPT_TO_ASCII))
            parts.append(
                _emit_ref(
                    match.group("ms_base"),
                    digit,
                    declared,
                    feats=match.group("ms_feats"),
                )
            )
        elif match.group("sub_matrix"):
            digit = int(match.group("sm_sub").translate(_SUBSCRIPT_TO_ASCII))
            parts.append(
                _emit_ref(
                    match.group("sm_base"),
                    digit,
                    declared,
                    feats=match.group("sm_feats"),
                    redeclare_with_base=redeclare_identity_matrix and digit == 0,
                )
            )
        elif match.group("phar"):
            digit = int(match.group("p_sub").translate(_SUBSCRIPT_TO_ASCII))
            parts.append(
                _emit_ref(
                    match.group("p_base"),
                    digit,
                    declared,
                    feats="[+pharyn]",
                )
            )
        elif match.group("pos"):
            digit = int(match.group("po_sub").translate(_SUBSCRIPT_TO_ASCII))
            parts.append(_emit_ref(match.group("po_base"), digit, declared))
        else:
            parts.append(_emit_ref(match.group("id_base"), 0, declared))
        parts.append(" ")
        last = match.end()
    parts.append(segment[last:])
    return _normalize_field_spacing("".join(parts))


def _expand_field(
    text: str,
    declared: set[int],
    *,
    redeclare_identity_matrix: bool = False,
) -> str:
    if not text:
        return text
    if _is_prose_field(text):
        return text
    return _expand_field_segment(
        text,
        declared,
        redeclare_identity_matrix=redeclare_identity_matrix,
    )


def expand_subscript_references_across_fields(
    inp: str,
    output: str,
    env: str | None,
    exception: str | None,
) -> tuple[str, str, str | None, str | None]:
    """Expand subscripts field-by-field with a shared ``declared`` set (output last)."""
    if not any(
        _SUBSCRIPT_CHAR_RE.search(field or "")
        for field in (inp, output, env, exception)
    ):
        return inp, output, env, exception

    declared: set[int] = set()
    inp = _expand_field(inp, declared, redeclare_identity_matrix=True)

    if env is not None:
        original_env = env
        env = _expand_field(env, declared)
        if env != original_env and not _is_prose_field(original_env) and "_" not in env:
            env = f"_ {env}"

    if exception is not None:
        exception = _expand_field(exception, declared)

    output = _expand_field(output, declared)
    return inp, output, env, exception


def expand_index_subscript_references(text: str) -> str:
    """Map positional slots and identity subscripts to ASCA reference syntax.

    Handles phase-1 bare slots plus phase-2 edge cases: matrix-attached
    identity/positional (``V₀[+nas]``, ``CV:[+stress]₂``), inter-slot
    pharyngeal diacritics (``C₁ˤ`` → ``C:[+pharyn]=1``), identity compounds
    (``mV₀``), and leaves Index prose env/exception fields unexpanded.
    """
    if not text or not _SUBSCRIPT_CHAR_RE.search(text):
        return text

    inp, output, env, exception = _split_rule_fields(text)
    inp, output, env, exception = expand_subscript_references_across_fields(
        inp, output, env, exception
    )
    return _join_rule_fields(inp, output, env, exception)


def is_easy_subscript_rule_text(text: str) -> bool:
    """Whether ``text`` is in scope for phase-1 positional/identity expansion."""
    if re.search(r"[A-Za-z][₀₁₂₃₄₅₆₇₈₉]\[[^\]]+\]", text):
        return False
    if re.search(r"[A-Za-z]+:\[[^\]]+\][₀₁₂₃₄₅₆₇₈₉]", text):
        return False
    if "ˤ" in text:
        return False
    if _is_prose_field(text):
        return False
    for token in re.findall(r"\S+", text):
        if is_positional_slot_token(token) or is_identity_subscript_token(token):
            continue
        if _SUBSCRIPT_CHAR_RE.search(token):
            return False
    return bool(_SUBSCRIPT_CHAR_RE.search(text))
