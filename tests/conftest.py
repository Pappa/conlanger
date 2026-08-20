"""Shared pytest helpers."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from helpers import default_index_parser

__all__ = [
    "ASCA_INSTALLED",
    "ASCA_VALIDATE_INSTALLED",
    "default_index_parser",
    "require_executable",
]

_REPO_ROOT = Path(__file__).resolve().parents[1]
_FORK_ASCA = _REPO_ROOT / "bin" / "bin" / "asca"


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


@pytest.fixture(autouse=True)
def mock_env_vars(mocker):
    if _FORK_ASCA.is_file() and "ASCA_BIN" not in os.environ:
        mocker.patch.dict(os.environ, {"ASCA_BIN": str(_FORK_ASCA)})


# Evaluated at collection time for ``skipif`` (before autouse fixtures run).
ASCA_INSTALLED = _FORK_ASCA.is_file() or require_executable("asca")
ASCA_VALIDATE_INSTALLED = _FORK_ASCA.is_file()
