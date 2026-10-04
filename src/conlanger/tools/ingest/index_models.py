"""Parse-time rule index models (applier-neutral YAML shape)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    field_validator,
    model_serializer,
    SerializerFunctionWrapHandler,
)

from conlanger.utils.gloss import apply_dialects_to_context
from conlanger.utils.parsing import (
    extract_missing_arrow_rule_parts,
    extract_rule_parts,
    non_empty_stages,
)
from conlanger.utils.symbols import normalize_symbols

PositionValue = bool | str | list[str]
DialectValue = bool | str | list[str]


def join_rule_comment(*fragments: str | None) -> str | None:
    """Join captured prose fragments into one ``comment`` string."""
    parts = [
        fragment.strip() for fragment in fragments if fragment and fragment.strip()
    ]
    if not parts:
        return None
    return "; ".join(parts)


def split_semicolon_comment(text: str) -> tuple[str, str | None]:
    """Peel the first ``;`` on a working rule line into remainder and rule-comment tail."""
    head, _, tail = text.partition(";")
    return head.rstrip(), tail.strip() or None


class IndexContext(BaseModel):
    """Structured environment or exception (ADR-0017)."""

    model_config = ConfigDict(extra="forbid")

    context: str | None = None
    position: dict[str, PositionValue] | None = None
    dialect: DialectValue | None = None

    @model_serializer(mode="wrap")
    def serialize_model(
        self, handler: SerializerFunctionWrapHandler
    ) -> str | dict[str, Any]:
        if self.position is None and self.dialect is None:
            return self.context or ""
        return handler(self)


def _coerce_env_exception_value(value: object) -> IndexContext | None:
    if value is None:
        return None
    if isinstance(value, IndexContext):
        return value
    if isinstance(value, str):
        return IndexContext(context=value)
    if isinstance(value, dict):
        return IndexContext.model_validate(value)
    return value


def _apply_dialects_to_context_field(
    ctx: IndexContext | None,
) -> IndexContext | None:
    if ctx is None:
        return None
    text = ctx.context or ""
    result = apply_dialects_to_context(text)
    if isinstance(result, str):
        if not result:
            return None
        return ctx.model_copy(update={"context": result})
    merged: dict[str, Any] = dict(result)
    if ctx.position is not None:
        merged["position"] = ctx.position
    return IndexContext.model_validate(merged)


class IndexRule(BaseModel):
    """Parse-time counterpart to compile-time ``SoundChangeRule``."""

    model_config = ConfigDict(extra="forbid")

    stages: list[str] = Field(default_factory=list)
    env: IndexContext | None = None
    exception: IndexContext | None = None
    raw: str
    source: str
    comment: str | None = None
    sporadic: bool | None = None
    status: str | None = None
    rule_id: str | None = None

    _working_line: str = PrivateAttr()

    def model_post_init(self, __context: Any, /) -> None:
        self._working_line = self.raw

    def working_text(self) -> str:
        """Current parse working line (not emitted in YAML)."""
        return self._working_line

    def update_rule(self, text: str) -> Self:
        """Replace the working line during pre-structural parse overlays."""
        self._working_line = text
        return self

    def update_model(self) -> Self:
        """Peel first ``;`` comment, normalize symbols, and split into index fields."""
        self._working_line, rule_comment = split_semicolon_comment(self._working_line)
        if rule_comment:
            self.comment = join_rule_comment(self.comment, rule_comment)

        self._working_line = normalize_symbols(self._working_line)
        parts = extract_rule_parts(self._working_line)
        if parts is None:
            parts = extract_missing_arrow_rule_parts(self._working_line)

        self.stages = list(parts.get("stages") or [])
        env_str = parts.get("env")
        exc_str = parts.get("exception")
        self.env = IndexContext(context=env_str) if env_str else None
        self.exception = IndexContext(context=exc_str) if exc_str else None
        return self

    @field_validator("env", "exception", mode="before")
    @classmethod
    def coerce_structured_env_exception(cls, value: object) -> object:
        return _coerce_env_exception_value(value)

    def merge_comment(self, *fragments: str | None) -> Self:
        """Append prose fragments to optional ``comment``."""
        merged = join_rule_comment(self.comment, *fragments)
        self.comment = merged
        return self

    def mark_sporadic(self) -> Self:
        self.sporadic = True
        return self

    def map_stages(self, fn: Callable[[str], str]) -> Self:
        self.stages = [fn(stage) for stage in self.stages]
        return self

    def env_context(self) -> str | None:
        if self.env is None:
            return None
        return self.env.context

    def exception_context(self) -> str | None:
        if self.exception is None:
            return None
        return self.exception.context

    def set_env_context(self, value: str | None) -> Self:
        if value is None or value == "":
            self.env = None
        elif self.env is None:
            self.env = IndexContext(context=value)
        else:
            self.env = self.env.model_copy(update={"context": value})
        return self

    def set_exception_context(self, value: str | None) -> Self:
        if value is None or value == "":
            self.exception = None
        elif self.exception is None:
            self.exception = IndexContext(context=value)
        else:
            self.exception = self.exception.model_copy(update={"context": value})
        return self

    def map_env_context(self, fn: Callable[[str], str]) -> Self:
        if self.env is None:
            return self
        new_text = fn(self.env.context or "")
        return self.set_env_context(new_text if new_text else None)

    def map_exception_context(self, fn: Callable[[str], str]) -> Self:
        if self.exception is None:
            return self
        new_text = fn(self.exception.context or "")
        return self.set_exception_context(new_text if new_text else None)

    def map_env_and_exception_context(self, fn: Callable[[str], str]) -> Self:
        self.map_env_context(fn)
        self.map_exception_context(fn)
        return self

    def apply_dialects_to_env_fields(self) -> Self:
        self.env = _apply_dialects_to_context_field(self.env)
        self.exception = _apply_dialects_to_context_field(self.exception)
        return self

    def finalize_stages_shape(self) -> Self:
        self.stages = non_empty_stages(self.stages)
        return self

    def to_index_dict(self) -> dict[str, Any]:
        """Serialize for cleaned-index YAML (omit false defaults and nulls)."""
        return self.model_dump(exclude_none=True, mode="python")
