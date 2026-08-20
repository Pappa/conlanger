"""Shared pytest helpers."""

from __future__ import annotations

import os
import shutil
import subprocess

from helpers import default_index_parser

__all__ = [
    "ASCA_INSTALLED",
    "ASCA_VALIDATE_INSTALLED",
    "default_index_parser",
    "require_executable",
]


def require_executable(name: str) -> bool:
    """Return True when *name* is available on ``PATH``."""
    return shutil.which(name) is not None


def _asca_supports_validate(asca_bin: str) -> bool:
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


def _resolved_asca_bin() -> str | None:
    if override := os.environ.get("ASCA_BIN"):
        return override
    return shutil.which("asca")


ASCA_INSTALLED = _resolved_asca_bin() is not None
ASCA_VALIDATE_INSTALLED = bool(
    _resolved_asca_bin() and _asca_supports_validate(_resolved_asca_bin())  # type: ignore[arg-type]
)
