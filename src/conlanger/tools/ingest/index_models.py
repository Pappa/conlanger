"""Parse-time rule index models (applier-neutral YAML shape)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer,
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

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

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

    def with_dialects_extracted(self) -> IndexContext | None:
        """Parse dialect prose in ``context`` into ``dialect`` (and trimmed ``context``)."""
        result = apply_dialects_to_context(self.context or "")
        if isinstance(result, str):
            if not result:
                return None
            return self.model_copy(update={"context": result})
        merged: dict[str, Any] = dict(result)
        if self.position is not None:
            merged["position"] = self.position
        return IndexContext.model_validate(merged)


EnvExceptionInput = str | dict[str, Any] | IndexContext | None


def _coerce_env_exception_value(value: object) -> IndexContext | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return None
        return IndexContext(context=stripped)
    if isinstance(value, IndexContext):
        if value.context is None and value.position is None and value.dialect is None:
            return None
        return value
    if isinstance(value, dict):
        ctx = IndexContext.model_validate(value)
        if ctx.context is None and ctx.position is None and ctx.dialect is None:
            return None
        return ctx
    return value


class IndexRule(BaseModel):
    """Parse-time counterpart to compile-time ``SoundChangeRule``."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

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

    @field_validator("env", "exception", mode="before")
    @classmethod
    def coerce_env_exception(cls, value: EnvExceptionInput) -> IndexContext | None:
        return _coerce_env_exception_value(value)

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
        self.env = env_str
        self.exception = exc_str
        return self

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

    def finalize_stages_shape(self) -> Self:
        self.stages = non_empty_stages(self.stages)
        return self

    def to_index_dict(self) -> dict[str, Any]:
        """Serialize for cleaned-index YAML (omit false defaults and nulls)."""
        return self.model_dump(exclude_none=True, mode="python")
