"""Tests for ASCA / Brassica CLI apply helpers."""

from __future__ import annotations

import subprocess
from unittest.mock import MagicMock

from conlanger.appliers.asca import run_asca
from conlanger.appliers.brassica import run_brassica


def test_run_asca_success(mocker):
    proc = MagicMock()
    proc.check_returncode = MagicMock()
    mocker.patch("conlanger.appliers.asca.subprocess.run", return_value=proc)

    result = run_asca("words.wsca", "rule.rsca", "/tmp/rules")
    assert result == {"rule": "rule.rsca", "returncode": 0, "error": ""}


def test_run_asca_called_process_error(mocker):
    exc = subprocess.CalledProcessError(2, "asca")
    exc.stderr = "\x1b[31mbad\x1b[0m\n"
    mocker.patch(
        "conlanger.appliers.asca.subprocess.run",
        side_effect=exc,
    )

    result = run_asca("words.wsca", "rule.rsca", "/tmp/rules")
    assert result["returncode"] == 2
    assert result["error"] == "bad"


def test_run_asca_timeout(mocker):
    mocker.patch(
        "conlanger.appliers.asca.subprocess.run",
        side_effect=subprocess.TimeoutExpired("asca", 10, output=b"slow"),
    )

    result = run_asca("words.wsca", "rule.rsca", "/tmp/rules")
    assert result["returncode"] == 124
    assert result["error"] == "slow"


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
