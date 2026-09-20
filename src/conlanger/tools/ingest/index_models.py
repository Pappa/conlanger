"""Parse-time rule index models (applier-neutral YAML shape)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
    sporadic: bool = False
    status: str | None = None
    rule_id: str | None = None

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
        if not self.sporadic:
            out.pop("sporadic", None)
        return out

    @classmethod
    def from_parse_fields(
        cls,
        fields: dict[str, Any],
        *,
        raw: str,
        source: str,
        sporadic: bool = False,
        rule_id: str | None = None,
    ) -> IndexRule:
        """Build from post-transform parse field dict (``stages``, ``env``, …)."""
        stages = list(fields.get("stages") or [])
        env = fields.get("env")
        exception = fields.get("exception")
        comment = fields.get("comment")
        status = fields.get("status")
        return cls(
            stages=stages,
            env=env,
            exception=exception,
            raw=raw,
            source=source,
            comment=comment,
            sporadic=sporadic,
            status=status,
            rule_id=rule_id,
        )
