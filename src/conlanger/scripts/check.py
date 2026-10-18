"""Run the full local quality gate (pytest, coverage, ruff, import-linter)."""

from __future__ import annotations

import subprocess


def _run(command: list[str]) -> int:
    print(f"+ {' '.join(command)}", flush=True)
    return subprocess.call(command)


def main() -> int:
    steps: list[list[str]] = [
        ["uv", "run", "pytest"],
        ["uv", "run", "per_file_coverage_gate"],
        ["uvx", "ruff", "check", "src", "tests"],
        ["uvx", "ruff", "format", "src", "tests", "--check"],
        ["uv", "run", "lint-imports"],
    ]
    for command in steps:
        if _run(command) != 0:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
