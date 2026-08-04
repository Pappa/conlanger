"""Validate ``SoundChangeRuleSet`` instances against ASCA (0.10.x).

Drives the ``asca`` CLI on ``PATH`` (``run`` on a probe wordlist) so syntax and
apply-time structural checks (Tier 1–4 in
``.scratch/cleaned-rule-corpus/research/asca-rule-validity.md`` §5) stay aligned
with ``ParsedRules`` / ``Rule::split_into_subrules`` rather than a docs-only
grammar.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from conlanger.tools.rules import RuleChange, SoundChangeRuleSet

# Minimal probe lexicon for ``asca run`` (Tier 4 boundary). Override with ASCA_PROBE_WORDS.
_DEFAULT_PROBE_WORDS = "a\nba\nkata\nsami\nntu\n"

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


class ASCAValidationError(ValueError):
    """Raised when a ``SoundChangeRuleSet`` is not valid for ASCA."""

    def __init__(self, message: str, *, returncode: int | None = None):
        super().__init__(message)
        self.returncode = returncode


def _active_rule_changes(rule: SoundChangeRuleSet) -> list[RuleChange]:
    """Return RuleChange parts that are not commented out (``skip``)."""
    active: list[RuleChange] = []
    for part in rule._parts:
        if not isinstance(part, RuleChange):
            continue
        # Skipped rules render as ASCA comments (``#\t…``).
        if str(part).lstrip().startswith("#"):
            continue
        active.append(part)
    return active


def _clean_asca_stderr(stderr: str) -> str:
    text = _ANSI_RE.sub("", stderr or "").strip()
    return re.sub(r"\s+", " ", text)


def validate_asca(
    rule: SoundChangeRuleSet,
    *,
    probe_words: Path | None = None,
    timeout: float = 15.0,
) -> bool:
    """Return ``True`` if ``rule`` is valid for ASCA; otherwise raise.

    Writes the rendered ``SoundChangeRuleSet`` to a temporary ``.rsca`` and runs
    ``asca run <probe_words> --rules <file>``. Non-zero exit or ASCA
    Syntax/Runtime Error text on stderr becomes ``ASCAValidationError``.

    Requires ``asca`` 0.10.x to be installed and available on ``PATH``.
    """
    if not _active_rule_changes(rule):
        raise ASCAValidationError(
            "SoundChangeRuleSet has no active RuleChange lines to validate"
        )

    asca = shutil.which("asca")
    if asca is None:
        raise ASCAValidationError(
            "asca binary not found on PATH (install asca 0.10.x and ensure it is on PATH)"
        )

    body = str(rule)
    if not body.endswith("\n"):
        body += "\n"

    words_override = probe_words or (
        Path(os.environ["ASCA_PROBE_WORDS"])
        if os.environ.get("ASCA_PROBE_WORDS")
        else None
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        rsca = tmp_path / "check.rsca"
        rsca.write_text(body, encoding="utf-8")

        if words_override is not None:
            if not words_override.is_file():
                raise ASCAValidationError(
                    f"probe wordlist not found at {words_override}"
                )
            words_path = words_override
        else:
            words_path = tmp_path / "probe.wsca"
            words_path.write_text(_DEFAULT_PROBE_WORDS, encoding="utf-8")

        try:
            proc = subprocess.run(  # noqa: PLW1510
                [asca, "run", str(words_path), "--rules", str(rsca)],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise ASCAValidationError(
                f"asca timed out after {timeout}s validating rule",
                returncode=124,
            ) from exc

        err = _clean_asca_stderr(proc.stderr)
        if proc.returncode != 0:
            message = err or f"asca exited with status {proc.returncode}"
            raise ASCAValidationError(message, returncode=proc.returncode)
        if err and re.search(r"(?i)(syntax error|runtime error)", err):
            raise ASCAValidationError(err, returncode=proc.returncode)

    return True
