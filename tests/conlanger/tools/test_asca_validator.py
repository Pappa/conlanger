"""Tests for ASCA validation of SoundChangeRuleSet (asca 0.10.2)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from conlanger.tools.rules import SoundChangeRuleSet
from conlanger.tools.asca_validator import ASCAValidationError, validate_asca

_FIXTURE_CSV = (
    Path(__file__).resolve().parents[2] / "fixtures" / "sound_change_rules.csv"
)
_PROBE = Path(__file__).resolve().parents[2] / "fixtures" / "asca_probe_words.wsca"


def _scr(change: dict) -> SoundChangeRuleSet:
    return SoundChangeRuleSet(
        {"index": "1", "section": "test", "rules": [change]},
        format="asca",
    )


@pytest.mark.parametrize(
    "change",
    [
        {"input": "a", "output": "b"},
        {"input": "t", "output": "s", "env": "_i"},
        {"input": "r", "output": "∅", "env": "{ð,f}_{ɡ,ɣ}"},
        {"input": "∅", "output": "n", "env": "#_i"},
        {"input": "ab", "output": "&"},
        {"input": "a", "output": "e", "env": "_#", "exception": "_s"},
    ],
)
def test_validate_asca_accepts_valid_rules(change):
    assert validate_asca(_scr(change), probe_words=_PROBE) is True


@pytest.mark.parametrize(
    "change, match",
    [
        ({"input": "a", "output": ""}, r"empty|deletion|\*|Unknown character"),
        ({"input": "", "output": "a"}, r"empty|insertion|\*|Unknown character"),
        ({"input": "*", "output": "*"}, r"Insertion|Deletion"),
        ({"input": "a", "output": "b", "env": "no underscore"}, r"_|underline|Expected|Unknown"),
        ({"input": "a", "output": "b", "env": "_ _"}, r"underline|_|Too many|Expected"),
    ],
)
def test_validate_asca_rejects_invalid_rules(change, match):
    with pytest.raises(ASCAValidationError, match=match):
        validate_asca(_scr(change), probe_words=_PROBE)


def test_validate_asca_rejects_title_only():
    rule = SoundChangeRuleSet({"index": "1", "section": "sec"}, format="asca")
    with pytest.raises(ASCAValidationError, match="no active RuleChange"):
        validate_asca(rule)


def test_validate_asca_rejects_skipped_only():
    rule = SoundChangeRuleSet(
        {
            "index": "1",
            "section": "sec",
            "rules": [{"skip": True, "input": "a", "output": "b"}],
        },
        format="asca",
    )
    with pytest.raises(ASCAValidationError, match="no active RuleChange"):
        validate_asca(rule)


def test_validate_asca_missing_binary(tmp_path: Path):
    with pytest.raises(ASCAValidationError, match="asca binary not found"):
        validate_asca(_scr({"input": "a", "output": "b"}), asca_bin=tmp_path / "nope")


def test_validate_asca_missing_probe_words(tmp_path: Path):
    with pytest.raises(ASCAValidationError, match="probe wordlist not found"):
        validate_asca(
            _scr({"input": "a", "output": "b"}),
            probe_words=tmp_path / "missing.wsca",
        )


def test_validate_asca_timeout():
    with patch(
        "conlanger.tools.asca_validator.subprocess.run",
        side_effect=__import__("subprocess").TimeoutExpired(cmd="asca", timeout=0.01),
    ):
        with pytest.raises(ASCAValidationError, match="timed out") as exc_info:
            validate_asca(_scr({"input": "a", "output": "b"}), probe_words=_PROBE)
    assert exc_info.value.returncode == 124


def test_validate_asca_stderr_error_with_zero_returncode():
    proc = MagicMock(returncode=0, stderr="Syntax Error: boom\n")
    with patch("conlanger.tools.asca_validator.subprocess.run", return_value=proc):
        with pytest.raises(ASCAValidationError, match="Syntax Error"):
            validate_asca(_scr({"input": "a", "output": "b"}), probe_words=_PROBE)


def test_validate_asca_nonzero_without_stderr():
    proc = MagicMock(returncode=2, stderr="")
    with patch("conlanger.tools.asca_validator.subprocess.run", return_value=proc):
        with pytest.raises(ASCAValidationError, match="exited with status 2"):
            validate_asca(_scr({"input": "a", "output": "b"}), probe_words=_PROBE)


def test_validate_asca_respects_env_bin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    monkeypatch.setenv("ASCA_BIN", str(tmp_path / "missing-asca"))
    with pytest.raises(ASCAValidationError, match="asca binary not found"):
        validate_asca(_scr({"input": "a", "output": "b"}))


def test_validate_asca_default_probe_words(tmp_path: Path):
    asca = tmp_path / "asca"
    asca.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    asca.chmod(0o755)

    captured: dict[str, str] = {}

    def fake_run(cmd, **_kwargs):
        captured["words"] = Path(cmd[2]).read_text(encoding="utf-8")
        return MagicMock(returncode=0, stderr="")

    with patch("conlanger.tools.asca_validator.subprocess.run", fake_run):
        validate_asca(
            _scr({"input": "a", "output": "b"}),
            asca_bin=asca,
            probe_words=None,
        )

    assert captured["words"] == "a\nba\nkata\nsami\nntu\n"


def test_validate_asca_keeps_trailing_newline(tmp_path: Path):
    asca = tmp_path / "asca"
    asca.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    asca.chmod(0o755)

    captured: dict[str, str] = {}

    def fake_run(_cmd, **_kwargs):
        captured["body"] = (tmp_path / "check.rsca").read_text(encoding="utf-8")
        return MagicMock(returncode=0, stderr="")

    rule = _scr({"input": "a", "output": "b"})
    with patch("conlanger.tools.asca_validator.subprocess.run", fake_run):
        with patch(
            "conlanger.tools.asca_validator.tempfile.TemporaryDirectory"
        ) as tmpdir:
            tmpdir.return_value.__enter__.return_value = str(tmp_path)
            with patch.object(rule, "__str__", return_value="@ 1 - test\na > b\n"):
                validate_asca(rule, asca_bin=asca, probe_words=_PROBE)

    assert captured["body"].endswith("\n")
    assert not captured["body"].endswith("\n\n")


def test_validate_asca_appends_trailing_newline(tmp_path: Path):
    asca = tmp_path / "asca"
    asca.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    asca.chmod(0o755)

    captured: dict[str, str] = {}

    def fake_run(_cmd, **_kwargs):
        captured["body"] = (tmp_path / "check.rsca").read_text(encoding="utf-8")
        return MagicMock(returncode=0, stderr="")

    rule = _scr({"input": "a", "output": "b"})
    with patch("conlanger.tools.asca_validator.subprocess.run", fake_run):
        with patch(
            "conlanger.tools.asca_validator.tempfile.TemporaryDirectory"
        ) as tmpdir:
            tmpdir.return_value.__enter__.return_value = str(tmp_path)
            validate_asca(rule, asca_bin=asca, probe_words=_PROBE)

    assert captured["body"].endswith("\n")


def _load_asca_guess_rows():
    df = pd.read_csv(_FIXTURE_CSV, dtype=str, keep_default_na=False)
    if "kind" not in df.columns:
        pytest.skip("fixture CSV has no asca_guess rows yet")
    guesses = df[df["kind"] == "asca_guess"]
    if guesses.empty:
        pytest.skip("no asca_guess rows in fixture CSV")
    return guesses


def test_fixture_asca_guess_count():
    guesses = _load_asca_guess_rows()
    assert len(guesses) == 500


@pytest.mark.parametrize("case_id", ["bulk"])
def test_validate_asca_guess_fixture_rows(case_id):
    del case_id
    guesses = _load_asca_guess_rows()
    failures = []
    for row in guesses.itertuples(index=False):
        if not row.asca_input or not row.asca_output:
            if row.asca_expect_ok == "True":
                failures.append((row.id, "empty asca fields but expect_ok"))
            continue
        change = {"input": row.asca_input, "output": row.asca_output}
        if row.asca_env:
            change["env"] = row.asca_env
        if row.asca_exception:
            change["exception"] = row.asca_exception
        rule = _scr(change)
        expect_ok = row.asca_expect_ok == "True"
        try:
            validate_asca(rule, probe_words=_PROBE)
            if not expect_ok:
                failures.append((row.id, "expected failure but validated"))
        except ASCAValidationError as exc:
            if expect_ok:
                failures.append((row.id, f"expected ok: {exc}"))
    assert failures == [], f"{len(failures)} fixture mismatches: {failures[:10]}"
