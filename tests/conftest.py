"""Shared pytest helpers."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def require_executable(name: str) -> bool:
    """Return True when *name* can be invoked on this system.

    For ``asca``, also checks ``ASCA_BIN`` and ``~/.cargo/bin/asca`` so the
    helper matches ``conlanger.tools.asca_validator._asca_bin`` resolution.
    """
    if shutil.which(name) is not None:
        return True
    if name == "asca":
        override = os.environ.get("ASCA_BIN")
        if override and Path(override).is_file():
            return True
        return (Path.home() / ".cargo" / "bin" / "asca").is_file()
    return False


# Use with ``@pytest.mark.skipif(not ASCA_INSTALLED, reason=...)``.
ASCA_INSTALLED = require_executable("asca")
