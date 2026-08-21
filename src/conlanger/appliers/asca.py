"""ASCA applier: CLI apply helper and compile validation."""

from __future__ import annotations

import functools
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Literal

from strip_ansi import strip_ansi

from conlanger.tools.rules import DiachronicSeries, SoundChangeRule

# Minimal probe lexicon for ``asca run`` (Tier 4 boundary). Override with ASCA_PROBE_WORDS.
_DEFAULT_PROBE_WORDS = "a\nba\nkata\nsami\nntu\n"

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

ASCARulePart = Literal["input", "output", "env", "exception"]

_ASCA_FIELD_FLAGS: dict[ASCARulePart, str] = {
    "input": "input",
    "output": "output",
    "env": "context",
    "exception": "exception",
}


class ASCAValidationError(ValueError):
    """Raised when a ``DiachronicSeries`` is not valid for ASCA."""

    def __init__(self, message: str, *, returncode: int | None = None):
        super().__init__(message)
        self.returncode = returncode


def resolve_asca_bin() -> str | None:
    """Return the asca binary path, honoring ``ASCA_BIN`` then ``PATH``."""
    override = os.environ.get("ASCA_BIN")
    if override:
        return override
    return shutil.which("asca")


def fork_asca_bin(*, repo_root: Path | None = None) -> Path:
    """Return the repo-local asca fork installed under ``bin/bin/asca``."""
    root = repo_root or Path(__file__).resolve().parents[3]
    return root / "bin" / "bin" / "asca"


@functools.lru_cache(maxsize=8)
def _asca_supports_validate(asca_bin: str) -> bool:
    """Return True when *asca_bin* exposes the ``validate`` subcommand."""
    try:
        proc = subprocess.run(  # noqa: PLW1510
            [asca_bin, "validate", "--help"],
            capture_output=True,
            text=True,
            timeout=5.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0


def _require_asca_bin(*, asca_bin: str | None = None) -> str:
    asca = asca_bin if asca_bin is not None else resolve_asca_bin()
    if asca is None:
        raise ASCAValidationError(
            "asca binary not found (set ASCA_BIN or install asca 0.10.x on PATH)"
        )
    return asca


def _require_validate_support(asca: str) -> None:
    if not _asca_supports_validate(asca):
        raise ASCAValidationError(
            "asca binary lacks the validate subcommand "
            "(install the fork from docs/DEV.md)"
        )


def _active_rule_changes(rule: DiachronicSeries) -> list[SoundChangeRule]:
    """Return SoundChangeRule parts that are not commented out (``#\\t`` prefix)."""
    active: list[SoundChangeRule] = []
    for part in rule._parts:
        if not isinstance(part, SoundChangeRule):
            continue
        # Skipped rules render as ASCA comments (``#\t…``).
        if str(part).lstrip().startswith("#"):
            continue
        active.append(part)
    return active


def _clean_asca_stderr(stderr: str) -> str:
    text = _ANSI_RE.sub("", stderr or "").strip()
    return re.sub(r"\s+", " ", text)


def _raise_if_asca_failed(
    proc: subprocess.CompletedProcess[str],
    *,
    timeout: float,
) -> None:
    err = _clean_asca_stderr(proc.stderr)
    if proc.returncode != 0:
        message = err or f"asca exited with status {proc.returncode}"
        raise ASCAValidationError(message, returncode=proc.returncode)
    if err and re.search(r"(?i)(syntax error|runtime error)", err):
        raise ASCAValidationError(err, returncode=proc.returncode)


def _run_asca_command(
    cmd: list[str],
    *,
    timeout: float,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(  # noqa: PLW1510
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise ASCAValidationError(
            f"asca timed out after {timeout}s validating rule",
            returncode=124,
        ) from exc
    except OSError as exc:
        raise ASCAValidationError(
            f"asca binary not found at {cmd[0]}",
            returncode=127,
        ) from exc


def asca_supports_validate(*, asca_bin: str | None = None) -> bool:
    """Return True when the asca binary exposes ``validate``."""
    asca = asca_bin if asca_bin is not None else resolve_asca_bin()
    if asca is None:
        return False
    return _asca_supports_validate(asca)


def validate_asca_syntax(
    rule: str,
    *,
    asca_bin: str | None = None,
    timeout: float = 15.0,
) -> bool:
    """Return ``True`` when a whole rule line passes ``asca validate -s``."""
    asca = _require_asca_bin(asca_bin=asca_bin)
    _require_validate_support(asca)
    proc = _run_asca_command([asca, "validate", "-s", rule], timeout=timeout)
    _raise_if_asca_failed(proc, timeout=timeout)
    return True


def validate_asca_part(
    part: ASCARulePart,
    fragment: str,
    *,
    asca_bin: str | None = None,
    timeout: float = 15.0,
) -> bool:
    """Return ``True`` when a rule field fragment passes ``asca validate -s -f``."""
    asca = _require_asca_bin(asca_bin=asca_bin)
    _require_validate_support(asca)
    field = _ASCA_FIELD_FLAGS[part]
    proc = _run_asca_command(
        [asca, "validate", "-s", fragment, "-f", field],
        timeout=timeout,
    )
    _raise_if_asca_failed(proc, timeout=timeout)
    return True


def validate_asca(
    rule: DiachronicSeries,
    *,
    probe_words: Path | None = None,
    asca_bin: str | None = None,
    timeout: float = 15.0,
) -> bool:
    """Return ``True`` if ``rule`` is valid for ASCA; otherwise raise.

    When the asca binary supports ``validate``, runs ``asca validate -r`` on the
    rendered rule file first (Tiers 1–3), then ``asca run`` with probe words
    (Tier 4). Inventory ``ok`` still requires a successful ``run`` pass.

    Requires ``asca`` 0.10.x to be installed (``ASCA_BIN`` or ``PATH``).
    """
    if not _active_rule_changes(rule):
        raise ASCAValidationError(
            "DiachronicSeries has no active SoundChangeRule lines to validate"
        )

    asca = _require_asca_bin(asca_bin=asca_bin)

    body = str(rule)

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

        if _asca_supports_validate(asca):
            proc = _run_asca_command(
                [asca, "validate", "-r", str(rsca)],
                timeout=timeout,
            )
            _raise_if_asca_failed(proc, timeout=timeout)

        proc = _run_asca_command(
            [asca, "run", str(words_path), "--rules", str(rsca)],
            timeout=timeout,
        )
        _raise_if_asca_failed(proc, timeout=timeout)

    return True


def run_asca(asca_word_file, rule_file, rule_path):
    """Run ``asca`` on a word file and rule file; return a result dict."""
    asca = resolve_asca_bin()
    file_name = f"{rule_path}/{rule_file}"
    result = {"rule": rule_file, "returncode": 0, "error": ""}

    if asca is None:
        result["returncode"] = 127
        result["error"] = "asca binary not found (set ASCA_BIN or install on PATH)"
        return result

    cmd = [asca, "run", asca_word_file, "--rules", file_name]

    try:
        output = subprocess.run(
            cmd, capture_output=True, timeout=10, text=True, check=True
        )
        output.check_returncode()

    except subprocess.CalledProcessError as exc:
        result["returncode"] = exc.returncode
        result["error"] = strip_ansi(exc.stderr.strip()).replace("\n", " ")
    except OSError:
        result["returncode"] = 127
        result["error"] = f"asca binary not found at {asca}"
    except subprocess.TimeoutExpired as exc:
        result["returncode"] = 124
        result["error"] = exc.output.decode("utf-8").replace("\n", " ")

    return result
