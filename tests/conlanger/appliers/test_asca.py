"""Tests for ASCA validation of DiachronicSeries (asca 0.10.x)."""

import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from conlanger.appliers.asca import (
    ASCAValidationError,
    resolve_asca_bin,
    validate_asca,
    validate_asca_part,
    validate_asca_syntax,
)
from conlanger.tools.rules import DiachronicSeries
from tests.conftest import ASCA_INSTALLED, ASCA_VALIDATE_INSTALLED

_FIXTURE_CSV = (
    Path(__file__).resolve().parents[2] / "fixtures" / "sound_change_rules.csv"
)
_PROBE = Path(__file__).resolve().parents[2] / "fixtures" / "asca_probe_words.wsca"


@pytest.fixture
def mock_asca(tmp_path: Path) -> Path:
    """Minimal executable stand-in for the asca CLI (subprocess is mocked separately)."""
    asca = tmp_path / "asca"
    asca.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    asca.chmod(0o755)
    return asca


@pytest.fixture
def mock_asca_on_path(mock_asca, mocker):
    mocker.patch(
        "conlanger.appliers.asca.shutil.which",
        return_value=str(mock_asca),
    )
    return mock_asca


@pytest.fixture
def mock_asca_subprocess(mocker):
    return mocker.patch("conlanger.appliers.asca.subprocess.run")


@pytest.mark.skipif(not ASCA_INSTALLED, reason="asca binary not found on PATH")
def test_validate_asca_smoke_with_installed_binary():
    """Single integration check that validate_asca invokes the real asca binary."""
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    assert validate_asca(scr, probe_words=_PROBE) is True


def test_validate_asca_returns_true_when_subprocess_succeeds(
    mock_asca_subprocess, mock_asca_on_path
):
    mock_asca_subprocess.return_value = MagicMock(returncode=0, stderr="")
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    assert validate_asca(scr, probe_words=_PROBE) is True


@pytest.mark.parametrize(
    "scr",
    [
        DiachronicSeries({"index": "1", "section": "sec", "rules": []}, format="asca"),
        DiachronicSeries(
            {
                "index": "1",
                "section": "sec",
                "rules": [{"stages": ["# a", "b"]}],
            },
            format="asca",
        ),
    ],
)
def test_validate_asca_rejects_inactive_rules(scr):
    with pytest.raises(ASCAValidationError, match="no active SoundChangeRule"):
        validate_asca(scr)


def test_resolve_asca_bin_honors_env_override(mocker, tmp_path: Path):
    asca = tmp_path / "custom-asca"
    asca.write_text("#!/bin/sh\n", encoding="utf-8")
    asca.chmod(0o755)
    mocker.patch.dict(os.environ, {"ASCA_BIN": str(asca)}, clear=False)
    mocker.patch("conlanger.appliers.asca.shutil.which", return_value="/other/asca")

    assert resolve_asca_bin() == str(asca)


def test_resolve_asca_bin_falls_back_to_path(mocker):
    mocker.patch.dict(os.environ, {}, clear=True)
    os.environ.pop("ASCA_BIN", None)
    mocker.patch("conlanger.appliers.asca.shutil.which", return_value="/path/asca")

    assert resolve_asca_bin() == "/path/asca"


def test_resolve_asca_bin_returns_none_when_missing(mocker):
    mocker.patch.dict(os.environ, {}, clear=True)
    os.environ.pop("ASCA_BIN", None)
    mocker.patch("conlanger.appliers.asca.shutil.which", return_value=None)

    assert resolve_asca_bin() is None


def test_validate_asca_missing_binary(mocker):
    mocker.patch("conlanger.appliers.asca.resolve_asca_bin", return_value=None)
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    with pytest.raises(ASCAValidationError, match="asca binary not found"):
        validate_asca(scr)


def test_validate_asca_missing_probe_words(mock_asca_on_path, tmp_path: Path):
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    with pytest.raises(ASCAValidationError, match="probe wordlist not found"):
        validate_asca(scr, probe_words=tmp_path / "missing.wsca")


def test_validate_asca_timeout(mock_asca_subprocess, mock_asca_on_path):
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    mock_asca_subprocess.side_effect = subprocess.TimeoutExpired(
        cmd="asca", timeout=0.01
    )
    with pytest.raises(ASCAValidationError, match="timed out") as exc_info:
        validate_asca(scr, probe_words=_PROBE)
    assert exc_info.value.returncode == 124


def test_validate_asca_stderr_error_with_zero_returncode(
    mock_asca_subprocess, mock_asca_on_path
):
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    mock_asca_subprocess.return_value = MagicMock(
        returncode=0, stderr="Syntax Error: boom\n"
    )
    with pytest.raises(ASCAValidationError, match="Syntax Error"):
        validate_asca(scr, probe_words=_PROBE)


def test_validate_asca_nonzero_without_stderr(mock_asca_subprocess, mock_asca_on_path):
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    mock_asca_subprocess.return_value = MagicMock(returncode=2, stderr="")
    with pytest.raises(ASCAValidationError, match="exited with status 2"):
        validate_asca(scr, probe_words=_PROBE)


def test_validate_asca_default_probe_words(mock_asca_subprocess, mock_asca_on_path):
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    captured: dict[str, str] = {}

    def fake_run(cmd, **_kwargs):
        captured["words"] = Path(cmd[2]).read_text(encoding="utf-8")
        return MagicMock(returncode=0, stderr="")

    mock_asca_subprocess.side_effect = fake_run
    validate_asca(scr, probe_words=None)
    assert captured["words"] == "a\nba\nkata\nsami\nntu\n"


def test_validate_asca_keeps_trailing_newline(
    mock_asca_subprocess, mock_asca_on_path, tmp_path: Path
):
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    captured: dict[str, str] = {}

    def fake_run(_cmd, **_kwargs):
        captured["body"] = (tmp_path / "check.rsca").read_text(encoding="utf-8")
        return MagicMock(returncode=0, stderr="")

    mock_asca_subprocess.side_effect = fake_run
    with patch("conlanger.appliers.asca.tempfile.TemporaryDirectory") as tmpdir:
        tmpdir.return_value.__enter__.return_value = str(tmp_path)
        with patch.object(scr, "__str__", return_value="@ 1 - test\na > b\n"):
            validate_asca(scr, probe_words=_PROBE)

    assert captured["body"].endswith("\n")
    assert not captured["body"].endswith("\n\n")


def test_validate_asca_appends_trailing_newline(
    mock_asca_subprocess, mock_asca_on_path, tmp_path: Path
):
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    captured: dict[str, str] = {}

    def fake_run(_cmd, **_kwargs):
        captured["body"] = (tmp_path / "check.rsca").read_text(encoding="utf-8")
        return MagicMock(returncode=0, stderr="")

    mock_asca_subprocess.side_effect = fake_run
    with patch("conlanger.appliers.asca.tempfile.TemporaryDirectory") as tmpdir:
        tmpdir.return_value.__enter__.return_value = str(tmp_path)
        validate_asca(scr, probe_words=_PROBE)

    assert captured["body"].endswith("\n")


def test_validate_asca_calls_validate_before_run_when_supported(
    mock_asca_subprocess, mock_asca_on_path
):
    calls: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        calls.append(list(cmd))
        return MagicMock(returncode=0, stderr="")

    mock_asca_subprocess.side_effect = fake_run
    with patch("conlanger.appliers.asca._asca_supports_validate", return_value=True):
        scr = DiachronicSeries(
            {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
            format="asca",
        )
        validate_asca(scr, probe_words=_PROBE)

    assert len(calls) == 2
    assert calls[0][1] == "validate"
    assert calls[0][2] == "-r"
    assert calls[1][1] == "run"


def test_validate_asca_skips_validate_when_unsupported(
    mock_asca_subprocess, mock_asca_on_path
):
    calls: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        calls.append(list(cmd))
        return MagicMock(returncode=0, stderr="")

    mock_asca_subprocess.side_effect = fake_run
    with patch("conlanger.appliers.asca._asca_supports_validate", return_value=False):
        scr = DiachronicSeries(
            {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
            format="asca",
        )
        validate_asca(scr, probe_words=_PROBE)

    assert len(calls) == 1
    assert calls[0][1] == "run"


def test_validate_asca_validate_failure_short_circuits(
    mock_asca_subprocess, mock_asca_on_path
):
    calls: list[list[str]] = []

    def fake_run(cmd, **_kwargs):
        calls.append(list(cmd))
        if cmd[1] == "validate":
            return MagicMock(returncode=1, stderr="Syntax Error: bad rule\n")
        return MagicMock(returncode=0, stderr="")

    mock_asca_subprocess.side_effect = fake_run
    with patch("conlanger.appliers.asca._asca_supports_validate", return_value=True):
        scr = DiachronicSeries(
            {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
            format="asca",
        )
        with pytest.raises(ASCAValidationError, match="Syntax Error"):
            validate_asca(scr, probe_words=_PROBE)

    assert len(calls) == 1
    assert calls[0][1] == "validate"


def test_validate_asca_syntax_invokes_validate_subcommand(
    mock_asca_subprocess, mock_asca_on_path
):
    mock_asca_subprocess.return_value = MagicMock(returncode=0, stderr="")
    with patch("conlanger.appliers.asca._asca_supports_validate", return_value=True):
        assert validate_asca_syntax("a > b / _") is True

    cmd = mock_asca_subprocess.call_args.args[0]
    assert cmd[1:] == ["validate", "-s", "a > b / _"]


def test_validate_asca_syntax_requires_validate_subcommand(
    mock_asca_on_path,
):
    with (
        patch("conlanger.appliers.asca._asca_supports_validate", return_value=False),
        pytest.raises(ASCAValidationError, match="validate subcommand"),
    ):
        validate_asca_syntax("a > b / _")


@pytest.mark.parametrize(
    ("part", "field"),
    [
        ("input", "input"),
        ("output", "output"),
        ("env", "context"),
        ("exception", "exception"),
    ],
)
def test_validate_asca_part_invokes_field_flag(
    mock_asca_subprocess,
    mock_asca_on_path,
    part,
    field,
):
    mock_asca_subprocess.return_value = MagicMock(returncode=0, stderr="")
    with patch("conlanger.appliers.asca._asca_supports_validate", return_value=True):
        assert validate_asca_part(part, "#_") is True

    cmd = mock_asca_subprocess.call_args.args[0]
    assert cmd[1:] == ["validate", "-s", "#_", "-f", field]


def test_validate_asca_invalid_asca_bin_raises(mocker, tmp_path: Path):
    mocker.patch(
        "conlanger.appliers.asca.resolve_asca_bin",
        return_value=str(tmp_path / "missing-asca"),
    )
    scr = DiachronicSeries(
        {"index": "1", "section": "test", "rules": [{"stages": ["a", "b"]}]},
        format="asca",
    )
    with pytest.raises(ASCAValidationError, match="not found at"):
        validate_asca(scr, probe_words=_PROBE)


@pytest.mark.skipif(
    not ASCA_VALIDATE_INSTALLED,
    reason="asca validate subcommand not available",
)
def test_validate_asca_syntax_integration():
    assert validate_asca_syntax("a > b / _") is True


@pytest.mark.skipif(
    not ASCA_VALIDATE_INSTALLED,
    reason="asca validate subcommand not available",
)
def test_validate_asca_part_integration():
    assert validate_asca_part("env", "#_") is True


def test_fixture_asca_guess_count():
    df = pd.read_csv(_FIXTURE_CSV, dtype=str, keep_default_na=False)
    if "kind" not in df.columns:
        pytest.skip("fixture CSV has no asca_guess rows yet")
    guesses = df[df["kind"] == "asca_guess"]
    if guesses.empty:
        pytest.skip("no asca_guess rows in fixture CSV")
    assert len(guesses) == 500
