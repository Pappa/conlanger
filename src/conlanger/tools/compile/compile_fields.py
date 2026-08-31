"""Pydantic compile-field types for ``SoundChangeRule`` (ADR-0015)."""

from __future__ import annotations

from typing import Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from conlanger.tools.compile.field_tokens import (
    FieldToken,
    parse_field_tokens,
    render_field_tokens,
)


class RuleFieldBase(BaseModel):
    """Index-raw, field-token IR, and compiled ASCA for one compile field."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    raw: str = ""
    tokens: tuple[FieldToken, ...] = ()
    compiled: str = ""

    @field_validator("tokens", mode="before")
    @classmethod
    def default_tokens_from_raw(cls, value: object, info) -> object:
        if value not in (None, ()):
            return value
        raw = info.data.get("raw", "")
        if raw:
            return parse_field_tokens(raw)
        return ()

    @model_validator(mode="before")
    @classmethod
    def coerce_from_string(cls, data: object) -> object:
        if isinstance(data, str):
            return {"raw": data, "tokens": parse_field_tokens(data)}
        return data

    @classmethod
    def from_raw(cls, raw: str) -> Self:
        return cls(raw=raw, tokens=parse_field_tokens(raw))

    def with_tokens(self, tokens: tuple[FieldToken, ...]) -> Self:
        return self.model_copy(
            update={"tokens": tokens, "raw": render_field_tokens(tokens)}
        )

    def with_compiled(self, compiled: str) -> Self:
        return self.model_copy(update={"compiled": compiled})

    def render(self) -> str:
        return self.compiled

    def __str__(self) -> str:
        return self.compiled

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return (self.compiled or self.raw) == other
        if isinstance(other, type(self)):
            return (
                self.raw == other.raw
                and self.tokens == other.tokens
                and self.compiled == other.compiled
            )
        return NotImplemented

    def __hash__(self) -> int:
        return hash((self.raw, self.tokens, self.compiled))


class RuleInput(RuleFieldBase):
    """Compile field for rule input."""


class RuleOutput(RuleFieldBase):
    """Compile field for rule output."""


class RuleEnv(RuleFieldBase):
    """Compile field for rule environment or exception."""
