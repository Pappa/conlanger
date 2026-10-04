"""Parse-time rule index models (applier-neutral YAML shape)."""

from __future__ import annotations

from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator

from conlanger.tools.ingest.transforms import (
    split_semicolon_comment,
    join_rule_comment,
)
from conlanger.utils.parsing import (
    extract_rule_parts,
    extract_missing_arrow_rule_parts,
)
from conlanger.utils.symbols import normalize_symbols

PositionValue = bool | str | list[str]
DialectValue = bool | str | list[str]


class IndexContext(BaseModel):
    """Structured environment or exception (ADR-0017)."""

    model_config = ConfigDict(extra="forbid")

    context: str | None = None
    position: dict[str, PositionValue] | None = None
    dialect: DialectValue | None = None


EnvExceptionField = str | IndexContext


class IndexRule(BaseModel):
    """Parse-time counterpart to compile-time ``SoundChangeRule``."""

    model_config = ConfigDict(extra="forbid")

    stages: list[str] = Field(default_factory=list)
    env: EnvExceptionField | None = None
    exception: EnvExceptionField | None = None
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
        self.env = parts.get("env")
        self.exception = parts.get("exception")
        return self

    @field_validator("env", "exception", mode="before")
    @classmethod
    def coerce_structured_env_exception(cls, value: object) -> object:
        if value is None or isinstance(value, str):
            return value
        if isinstance(value, IndexContext):
            return value
        if isinstance(value, dict):
            return IndexContext.model_validate(value)
        return value

    def to_index_dict(self) -> dict[str, Any]:
        """Serialize for cleaned-index YAML (omit false defaults and nulls)."""
        out = self.model_dump(exclude_none=True)
        return out

    @classmethod
    def from_parse_fields(
        cls,
        fields: dict[str, Any],
        *,
        raw: str,
        source: str,
        rule_id: str | None = None,
    ) -> IndexRule:
        """Build from post-transform parse field dict (``stages``, ``env``, …)."""
        return cls(
            stages=list(fields.get("stages") or []),
            env=fields.get("env"),
            exception=fields.get("exception"),
            raw=raw,
            source=source,
            comment=fields.get("comment"),
            sporadic=fields.get("sporadic"),
            status=fields.get("status"),
            rule_id=rule_id,
        )
