"""Scan and split Index / ASCA surface text by paired bracket delimiters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BracketScanner:
    """Match and measure one open/close delimiter pair (e.g. ``{`` / ``}``)."""

    open: str
    close: str

    def closing_index(self, text: str, start: int) -> int | None:
        """Return the index of the closing delimiter matching ``open`` at ``start``."""
        if start >= len(text) or text[start] != self.open:
            return None
        depth = 0
        for index in range(start, len(text)):
            char = text[index]
            if char == self.open:
                depth += 1
            elif char == self.close:
                depth -= 1
                if depth == 0:
                    return index
        return None

    def balance(self, text: str) -> int:
        """Net open-minus-close count; negative if a close appears without a match."""
        depth = 0
        for char in text:
            if char == self.open:
                depth += 1
            elif char == self.close:
                depth -= 1
                if depth < 0:
                    return depth
        return depth

    def is_balanced(self, text: str) -> bool:
        return self.balance(text) == 0

    def wraps(self, text: str) -> bool:
        """True when ``text`` has length ≥ 2 and starts/ends with this pair's delimiters."""
        return (
            len(text) >= 2 and text.startswith(self.open) and text.endswith(self.close)
        )

    def max_depth(self, text: str) -> int:
        depth = 0
        maximum = 0
        for char in text:
            if char == self.open:
                depth += 1
                maximum = max(maximum, depth)
            elif char == self.close:
                depth -= 1
        return maximum

    def top_level_spans(self, text: str) -> list[tuple[int, int]]:
        """``(start, end)`` slices for each top-level region opened with ``open``."""
        spans: list[tuple[int, int]] = []
        index = 0
        while index < len(text):
            if text[index] == self.open:
                close = self.closing_index(text, index)
                if close is None:
                    return []
                spans.append((index, close + 1))
                index = close + 1
            else:
                index += 1
        return spans


BRACES = BracketScanner("{", "}")
PARENS = BracketScanner("(", ")")
BRACKETS = BracketScanner("[", "]")

INDEX_GROUPERS: tuple[BracketScanner, ...] = (BRACES, PARENS, BRACKETS)


def is_brace_wrapped(text: str) -> bool:
    """True when ``text`` is wrapped in a single ``{…}`` pair (surface check only)."""
    return BRACES.wraps(text)


def is_square_bracket_wrapped(text: str) -> bool:
    """True when ``text`` is wrapped in a single ``[…]`` pair (surface check only)."""
    return BRACKETS.wraps(text)


def split_outside_brackets(
    text: str,
    separator: str,
    *,
    respect: tuple[BracketScanner, ...] = INDEX_GROUPERS,
    strip_parts: bool = False,
    flush_on_separator: str = "if_non_empty",
    omit_empty_tail: bool = False,
) -> list[str]:
    """Split on ``separator`` only when every respected bracket depth is zero.

    ``flush_on_separator``:
    - ``if_non_empty`` — drop empty segments at separators (field token split).
    - ``always`` — emit a segment on every separator (set member lists).
    """
    if len(separator) != 1:
        msg = "separator must be a single character"
        raise ValueError(msg)
    if flush_on_separator not in {"if_non_empty", "always"}:
        msg = "flush_on_separator must be 'if_non_empty' or 'always'"
        raise ValueError(msg)
    parts: list[str] = []
    current: list[str] = []
    depths = {scanner: 0 for scanner in respect}

    def piece_from_buffer() -> str:
        piece = "".join(current)
        return piece.strip() if strip_parts else piece

    for char in text:
        for scanner in respect:
            if char == scanner.open:
                depths[scanner] += 1
            elif char == scanner.close:
                depths[scanner] -= 1
        if char == separator and all(depth == 0 for depth in depths.values()):
            if flush_on_separator == "always" or current:
                parts.append(piece_from_buffer())
            current = []
            continue
        current.append(char)

    if current:
        tail = piece_from_buffer()
        if tail or not omit_empty_tail:
            parts.append(tail)
    return parts
