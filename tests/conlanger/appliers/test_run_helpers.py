"""Tests for ASCA / Brassica CLI apply helpers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock

from conlanger.appliers.asca import run_asca
from conlanger.appliers.brassica import run_brassica


def test_run_asca_success(mocker):
    proc = MagicMock()
    proc.check_returncode = MagicMock()
    mocker.patch(
        "conlanger.appliers.asca.resolve_asca_bin", return_value="/lib/bin/asca"
    )
    run = mocker.patch("conlanger.appliers.asca.subprocess.run", return_value=proc)

    result = run_asca("words.wsca", "rule.rsca", "/tmp/rules")
    assert result == {"rule": "rule.rsca", "returncode": 0, "error": ""}
    assert run.call_args.args[0] == [
        "/lib/bin/asca",
        "run",
        "words.wsca",
        "--rules",
        "/tmp/rules/rule.rsca",
    ]


def test_run_asca_uses_asca_bin_env(mocker, tmp_path):
    asca = tmp_path / "custom-asca"
    asca.write_text("#!/bin/sh\n", encoding="utf-8")
    asca.chmod(0o755)
    mocker.patch.dict(os.environ, {"ASCA_BIN": str(asca)}, clear=False)
    proc = MagicMock()
    proc.check_returncode = MagicMock()
    run = mocker.patch("conlanger.appliers.asca.subprocess.run", return_value=proc)

    result = run_asca("words.wsca", "rule.rsca", "/tmp/rules")
    assert result["returncode"] == 0
    assert run.call_args.args[0][0] == str(asca)


def test_run_asca_missing_binary(mocker):
    mocker.patch("conlanger.appliers.asca.resolve_asca_bin", return_value=None)

    result = run_asca("words.wsca", "rule.rsca", "/tmp/rules")
    assert result["returncode"] == 127
    assert "not found" in result["error"]


def test_run_asca_called_process_error(mocker):
    exc = subprocess.CalledProcessError(2, "asca")
    exc.stderr = "\x1b[31mbad\x1b[0m\n"
    mocker.patch(
        "conlanger.appliers.asca.resolve_asca_bin", return_value="/lib/bin/asca"
    )
    mocker.patch(
        "conlanger.appliers.asca.subprocess.run",
        side_effect=exc,
    )

    result = run_asca("words.wsca", "rule.rsca", "/tmp/rules")
    assert result["returncode"] == 2
    assert result["error"] == "bad"


def test_run_asca_timeout(mocker):
    mocker.patch(
        "conlanger.appliers.asca.resolve_asca_bin", return_value="/lib/bin/asca"
    )
    mocker.patch(
        "conlanger.appliers.asca.subprocess.run",
        side_effect=subprocess.TimeoutExpired("asca", 10, output=b"slow"),
    )

    result = run_asca("words.wsca", "rule.rsca", "/tmp/rules")
    assert result["returncode"] == 124
    assert result["error"] == "slow"


def test_run_asca_invalid_asca_bin(mocker, tmp_path: Path):
    mocker.patch(
        "conlanger.appliers.asca.resolve_asca_bin",
        return_value=str(tmp_path / "missing-asca"),
    )

    result = run_asca("words.wsca", "rule.rsca", "/tmp/rules")
    assert result["returncode"] == 127
    assert "not found at" in result["error"]


def test_run_brassica_success(mocker):
    proc = MagicMock()
    proc.check_returncode = MagicMock()
    mocker.patch("conlanger.appliers.brassica.subprocess.run", return_value=proc)

    result = run_brassica("words.txt", "rule.bsc", "/tmp/rules")
    assert result == {"rule": "rule.bsc", "returncode": 0, "error": ""}


def test_run_brassica_called_process_error(mocker):
    exc = subprocess.CalledProcessError(3, "brassica")
    exc.output = "fail\nline"
    mocker.patch(
        "conlanger.appliers.brassica.subprocess.run",
        side_effect=exc,
    )

    result = run_brassica("words.txt", "rule.bsc", "/tmp/rules")
    assert result["returncode"] == 3
    assert result["error"] == "fail\\nline"


def test_run_brassica_timeout(mocker):
    mocker.patch(
        "conlanger.appliers.brassica.subprocess.run",
        side_effect=subprocess.TimeoutExpired("brassica", 10, output=b"slow"),
    )

    result = run_brassica("words.txt", "rule.bsc", "/tmp/rules")
    assert result["returncode"] == 124
    assert result["error"] == "slow"
