"""Brassica applier: CLI apply helper."""

from __future__ import annotations

import subprocess


def run_brassica(brassica_word_file, rule_file, rule_path):
    """Run ``brassica`` on a word file and rule file; return a result dict."""
    file_name = f"{rule_path}/{rule_file}"
    cmd = f"brassica {file_name} -i {brassica_word_file}"

    result = {"rule": rule_file, "returncode": 0, "error": ""}

    try:
        output = subprocess.run(  # noqa: PLW1510
            cmd, capture_output=True, timeout=10, shell=True, text=True
        )
        output.check_returncode()

    except subprocess.CalledProcessError as exc:
        result["returncode"] = exc.returncode
        result["error"] = exc.output.replace("\n", "\\n")
    except subprocess.TimeoutExpired as exc:
        result["returncode"] = 124
        result["error"] = exc.output.decode("utf-8").replace("\n", "\\n")

    return result
