"""Parse-time rule index models (applier-neutral YAML shape)."""

from __future__ import annotations

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

from conlanger.ingest.models.mappings import PositionTemplates
from conlanger.ingest.utils.transform_fields import MEDIAL_BOUNDARY_EXCEPTION
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
    """Partition the first ``;`` on a working rule line into remainder and rule-comment tail."""
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
            return self.context if self.context else None
        return handler(self)

    def with_dialects_extracted(self) -> IndexContext | None:
        """Parse dialect prose in ``context`` into ``dialect`` (and trimmed ``context``)."""
        result = apply_dialects_to_context(self.context or "")
        if isinstance(result, str):
            if not result:
                if self.position is not None or self.dialect is not None:
                    return self.model_copy(update={"context": None})
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

    rule_id: str | None = None
    source: str
    raw: str
    stages: list[str] = Field(default_factory=list)
    env: IndexContext | None = None
    exception: IndexContext | None = None
    comment: str | None = None
    sporadic: bool | None = None
    status: str | None = None

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

    @property
    def contexts(self) -> tuple[IndexContext, ...]:
        return tuple(
            context for context in (self.env, self.exception) if context is not None
        )

    def init(self) -> Self:
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


class IndexSection(BaseModel):
    """One sound-change section in a parsed Index Diachronica document."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    section: str
    index: str
    citation: str | None = None
    comments: list[str] | None = None
    rules: list[IndexRule] | None = None
    status: str | None = None


class Index(BaseModel):
    """Parsed Index Diachronica document (cleaned-index YAML root)."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str
    sections: list[IndexSection] = Field(default_factory=list)

    def add_section(self, section: IndexSection) -> None:
        self.sections.append(section)


DEFAULT_POSITION_TEMPLATES: dict[str, str] = PositionTemplates().model_dump()


def _position_target_value(value: PositionValue) -> str | None:
    if isinstance(value, list):
        if not value:
            return None
        value = value[0]
    if isinstance(value, str) and value:
        return value
    return None


def _project_position_relation(
    ctx: IndexContext,
    relation: str,
    templates: dict[str, str],
) -> str | None:
    if not ctx.position:
        return None
    target = _position_target_value(ctx.position.get(relation))
    if target is None:
        return None
    template = templates.get(relation) or templates.get("adjacent_to", "{v}_, _{v}")
    return template.format(v=target)


def resolve_index_context_to_string(
    ctx: IndexContext,
    position_templates: dict[str, str] | None = None,
) -> str:
    """Project ``IndexContext`` to a compile env/exception string.

    Joins structural ``context`` with the first projected neighbour relation
    (``adjacent_to``, then ``near``) using comma separation. Medial boundary
    pairing is applied at rule level in ``resolve_rule_env_exception_for_compile``.
    """
    templates = position_templates or DEFAULT_POSITION_TEMPLATES
    parts: list[str] = []
    if ctx.context:
        parts.append(ctx.context)
    for relation in ("adjacent_to", "near"):
        projected = _project_position_relation(ctx, relation, templates)
        if projected is not None:
            parts.append(projected)
            break
    return ", ".join(parts)


def _coerce_optional_index_context(
    value: EnvExceptionInput | None,
) -> IndexContext | None:
    if value is None:
        return None
    if isinstance(value, IndexContext):
        return value
    if isinstance(value, str):
        return IndexContext.model_validate({"context": value})
    if isinstance(value, dict):
        return IndexContext.model_validate(value)
    raise TypeError(f"Invalid env/exception value: {value!r}")


def resolve_rule_env_exception_for_compile(
    env: EnvExceptionInput | None,
    exception: EnvExceptionInput | None,
    *,
    position_templates: dict[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Project rule-level ``env`` / ``exception`` to compile strings (ticket 144)."""
    env_ctx = _coerce_optional_index_context(env)
    exc_ctx = _coerce_optional_index_context(exception)

    env_str: str | None = None
    exc_str: str | None = None

    if env_ctx is not None:
        env_str = resolve_index_context_to_string(env_ctx, position_templates) or None
        if (
            env_ctx.position
            and env_ctx.position.get("medial")
            and exc_ctx is None
            and not env_str
        ):
            env_str = "_"
    if exc_ctx is not None:
        exc_str = resolve_index_context_to_string(exc_ctx, position_templates) or None

    if (
        env_ctx is not None
        and env_ctx.position
        and env_ctx.position.get("medial")
        and exc_ctx is None
    ):
        exc_str = MEDIAL_BOUNDARY_EXCEPTION

    return env_str, exc_str


def env_exception_input_to_string(
    value: EnvExceptionInput,
    *,
    position_templates: dict[str, str] | None = None,
) -> str:
    """Coerce YAML ``env`` / ``exception`` field to a compile string."""
    if isinstance(value, str):
        return value
    ctx = (
        value if isinstance(value, IndexContext) else IndexContext.model_validate(value)
    )
    return resolve_index_context_to_string(ctx, position_templates)
