"""Shared ASCA binary resolution for inventory validation CLIs."""

from __future__ import annotations

import subprocess
from pathlib import Path

from conlanger.appliers.asca import resolve_asca_bin
from conlanger.scripts.pipeline_defaults import ROOT


def fork_asca_command(*, repo_root: Path = ROOT) -> Path:
    return repo_root / "bin" / "bin" / "asca"


def validation_asca_command(*, use_fork: bool, repo_root: Path = ROOT) -> str | None:
    """Return the asca executable path for inventory validation."""
    if use_fork:
        fork = fork_asca_command(repo_root=repo_root)
        return str(fork) if fork.is_file() else None
    return resolve_asca_bin()


def asca_version(asca_bin: str) -> str:
    try:
        proc = subprocess.run(  # noqa: PLW1510
            [asca_bin, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if proc.stdout.strip():
            return proc.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return "0.10.x"
