"""Tests for ASCA validation of SoundChangeRuleSet (asca 0.10.x)."""

from pathlib import Path
from unittest.mock import MagicMock, patch
import subprocess

import pandas as pd
import pytest

from conlanger.tools.asca_validator import ASCAValidationError, validate_asca
from conlanger.tools.rules import SoundChangeRuleSet
from tests.conftest import ASCA_INSTALLED

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
        "conlanger.tools.asca_validator.shutil.which",
        return_value=str(mock_asca),
    )
    return mock_asca


@pytest.fixture
def mock_asca_subprocess(mocker):
    return mocker.patch("conlanger.tools.asca_validator.subprocess.run")


@pytest.mark.skipif(not ASCA_INSTALLED, reason="asca binary not found on PATH")
def test_validate_asca_smoke_with_installed_binary():
    """Single integration check that validate_asca invokes the real asca binary."""
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
        format="asca",
    )
    assert validate_asca(scr, probe_words=_PROBE) is True


def test_validate_asca_returns_true_when_subprocess_succeeds(
    mock_asca_subprocess, mock_asca_on_path
):
    mock_asca_subprocess.return_value = MagicMock(returncode=0, stderr="")
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
        format="asca",
    )
    assert validate_asca(scr, probe_words=_PROBE) is True


@pytest.mark.parametrize(
    "scr",
    [
        SoundChangeRuleSet(
            {"index": "1", "section": "sec", "rules": []}, format="asca"
        ),
        SoundChangeRuleSet(
            {
                "index": "1",
                "section": "sec",
                "rules": [{"input": "# a", "output": "b"}],
            },
            format="asca",
        ),
    ],
)
def test_validate_asca_rejects_inactive_rules(scr):
    with pytest.raises(ASCAValidationError, match="no active RuleChange"):
        validate_asca(scr)


def test_validate_asca_missing_binary(mocker):
    mocker.patch("conlanger.tools.asca_validator.shutil.which", return_value=None)
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
        format="asca",
    )
    with pytest.raises(ASCAValidationError, match="asca binary not found on PATH"):
        validate_asca(scr)


def test_validate_asca_missing_probe_words(mock_asca_on_path, tmp_path: Path):
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
        format="asca",
    )
    with pytest.raises(ASCAValidationError, match="probe wordlist not found"):
        validate_asca(scr, probe_words=tmp_path / "missing.wsca")


def test_validate_asca_timeout(mock_asca_subprocess, mock_asca_on_path):
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
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
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
        format="asca",
    )
    mock_asca_subprocess.return_value = MagicMock(
        returncode=0, stderr="Syntax Error: boom\n"
    )
    with pytest.raises(ASCAValidationError, match="Syntax Error"):
        validate_asca(scr, probe_words=_PROBE)


def test_validate_asca_nonzero_without_stderr(mock_asca_subprocess, mock_asca_on_path):
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
        format="asca",
    )
    mock_asca_subprocess.return_value = MagicMock(returncode=2, stderr="")
    with pytest.raises(ASCAValidationError, match="exited with status 2"):
        validate_asca(scr, probe_words=_PROBE)


def test_validate_asca_default_probe_words(mock_asca_subprocess, mock_asca_on_path):
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
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
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
        format="asca",
    )
    captured: dict[str, str] = {}

    def fake_run(_cmd, **_kwargs):
        captured["body"] = (tmp_path / "check.rsca").read_text(encoding="utf-8")
        return MagicMock(returncode=0, stderr="")

    mock_asca_subprocess.side_effect = fake_run
    with patch("conlanger.tools.asca_validator.tempfile.TemporaryDirectory") as tmpdir:
        tmpdir.return_value.__enter__.return_value = str(tmp_path)
        with patch.object(scr, "__str__", return_value="@ 1 - test\na > b\n"):
            validate_asca(scr, probe_words=_PROBE)

    assert captured["body"].endswith("\n")
    assert not captured["body"].endswith("\n\n")


def test_validate_asca_appends_trailing_newline(
    mock_asca_subprocess, mock_asca_on_path, tmp_path: Path
):
    scr = SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [{"input": "a", "output": "b"}]},
        format="asca",
    )
    captured: dict[str, str] = {}

    def fake_run(_cmd, **_kwargs):
        captured["body"] = (tmp_path / "check.rsca").read_text(encoding="utf-8")
        return MagicMock(returncode=0, stderr="")

    mock_asca_subprocess.side_effect = fake_run
    with patch("conlanger.tools.asca_validator.tempfile.TemporaryDirectory") as tmpdir:
        tmpdir.return_value.__enter__.return_value = str(tmp_path)
        validate_asca(scr, probe_words=_PROBE)

    assert captured["body"].endswith("\n")


def test_fixture_asca_guess_count():
    df = pd.read_csv(_FIXTURE_CSV, dtype=str, keep_default_na=False)
    if "kind" not in df.columns:
        pytest.skip("fixture CSV has no asca_guess rows yet")
    guesses = df[df["kind"] == "asca_guess"]
    if guesses.empty:
        pytest.skip("no asca_guess rows in fixture CSV")
    assert len(guesses) == 500
