"""Index Diachronica HTML → cleaned corpus YAML (ingest)."""

from conlanger.tools.ingest.parser import IndexDiachronicaParser
from conlanger.tools.ingest.reports import write_rule_comment_phrase_summary

__all__ = ["IndexDiachronicaParser", "write_rule_comment_phrase_summary"]
