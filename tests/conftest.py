"""Shared pytest helpers."""

from __future__ import annotations

import shutil


def require_executable(name: str) -> bool:
    """Return True when *name* is available on ``PATH``."""
    return shutil.which(name) is not None


ASCA_INSTALLED = require_executable("asca")
