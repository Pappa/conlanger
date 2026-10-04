"""Parse-time rule index models (applier-neutral YAML shape)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, ClassVar, Self

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
    extract_rule_parts,
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

    # def update(self, new_value: str | dict[str, Any] | IndexContext) -> Self:
    #     if isinstance(new_value, str):
    #         self.context = new_value
    #         return self
    #     if isinstance(new_value, dict):
    #         return self.model_validate(new_value)
    #     if isinstance(new_value, IndexContext):
    #         self = self.model_validate(new_value)
    #         return
    #     raise ValueError(f"Invalid update value: {new_value}")

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


class IndexRule(BaseModel):
    """Parse-time counterpart to compile-time ``SoundChangeRule``."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    context_fields: ClassVar[frozenset[str]] = frozenset(["env", "exception"])

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
    _initialised: bool = PrivateAttr(default=False)

    def model_post_init(self, __context: Any, /) -> None:
        self._working_line = self.raw

    @field_validator("env", "exception", mode="before")
    @classmethod
    def coerce_env_exception(cls, value: EnvExceptionInput) -> IndexContext | None:
        if value is None:
            return None
        if isinstance(value, str):
            return IndexContext.model_validate({"context": value.strip()})
        if isinstance(value, (IndexContext, dict)):
            return IndexContext.model_validate(value)
        raise ValueError(f"Invalid env/exception value: {value}")

    @property
    def text(self) -> str:
        return self._working_line

    @text.setter
    def text(self, new_text: str) -> None:
        self._working_line = new_text

    def build(self) -> Self:
        """Peel first ``;`` comment, normalize symbols, and split into index fields."""
        if self._initialised:
            raise RuntimeError("IndexRule already initialised")
        self._working_line, rule_comment = split_semicolon_comment(self._working_line)
        if rule_comment:
            self.comment = join_rule_comment(self.comment, rule_comment)

        self._working_line = normalize_symbols(self._working_line)
        parts = extract_rule_parts(self._working_line)

        self.stages = list(parts.get("stages") or [])
        self.env = parts.get("env")
        self.exception = parts.get("exception")
        self._initialised = True
        return self

    def merge_comment(self, *fragments: str | None) -> Self:
        """Append prose fragments to optional ``comment``."""
        merged = join_rule_comment(self.comment, *fragments)
        self.comment = merged
        return self

    def map_stages(self, fn: Callable[[str], str]) -> Self:
        self.stages = [fn(stage) for stage in self.stages]
        return self

    def finalize_stages_shape(self) -> Self:
        self.stages = [stage for stage in self.stages if stage and stage.strip()]
        return self

    def apply_dialects_to_env_fields(self) -> Self:
        """Parse dialect prose in env/exception ``context`` into structured ``dialect``."""
        rule = self.model_copy(deep=True)
        if rule.env is not None:
            rule.env = rule.env.with_dialects_extracted()
        if rule.exception is not None:
            rule.exception = rule.exception.with_dialects_extracted()
        return rule

    def to_index_dict(self) -> dict[str, Any]:
        """Serialize for cleaned-index YAML (omit false defaults and nulls)."""
        return self.model_dump(exclude_none=True, mode="python")


def resolve_index_context_to_string(ctx: IndexContext) -> str:
    """Project ``IndexContext`` to a single env/exception string for compile.

    Full position/dialect resolution expands in ticket 144; v1 uses ``context``
    when present and ignores ``dialect`` until render gating is specified.
    """
    if ctx.context:
        return ctx.context
    if ctx.position:
        adjacent = ctx.position.get("adjacent_to")
        if isinstance(adjacent, str) and len(adjacent) == 1:
            return f"{adjacent}_, _{adjacent}"
        if isinstance(adjacent, list) and len(adjacent) == 1 and len(adjacent[0]) == 1:
            char = adjacent[0]
            return f"{char}_, _{char}"
    return ""


def env_exception_input_to_string(value: EnvExceptionInput) -> str:
    """Coerce YAML ``env`` / ``exception`` field to a compile string."""
    if isinstance(value, str):
        return value
    ctx = (
        value if isinstance(value, IndexContext) else IndexContext.model_validate(value)
    )
    return resolve_index_context_to_string(ctx)
