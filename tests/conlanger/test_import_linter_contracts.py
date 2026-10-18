"""Import-layer contracts enforced by import-linter."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ingest_must_not_import_compile_contract_passes() -> None:
    result = subprocess.run(
        ["uv", "run", "lint-imports"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
