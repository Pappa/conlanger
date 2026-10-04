"""Run a named ingest parse pass on an ``IndexRule`` copy."""

from __future__ import annotations

from conlanger.tools.ingest.index_models import IndexRule
from conlanger.tools.ingest.index_rule_passes import run_ingest_parse_pass
from conlanger.tools.ingest.ingest_parse_context import ingest_parse_pass

__all__ = ["with_ingest_pass"]


def with_ingest_pass(name: str, rule: IndexRule) -> IndexRule:
    """Run a named ingest pass on a copy of ``rule`` (``rule.env = …`` uses field validators)."""
    with ingest_parse_pass(name):
        updated = rule.model_copy(deep=True)
        run_ingest_parse_pass(updated)
        return updated
