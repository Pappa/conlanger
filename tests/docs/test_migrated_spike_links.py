"""Living docs must reference migrated spike findings under .backlog/spike/."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

LIVING_PATHS = (
    REPO / "docs/system/index-diachronica-parser.md",
    REPO / "docs/system/sound-change-applier.md",
    REPO / "docs/system/validate.md",
    REPO / "src/conlanger/compile/tools/asca/clicks.py",
)

SCRATCH_RESEARCH = ".scratch/rule-index/research/"


def test_living_docs_do_not_link_scratch_research_for_migrated_spikes() -> None:
    offenders: list[str] = []
    for path in LIVING_PATHS:
        text = path.read_text(encoding="utf-8")
        if SCRATCH_RESEARCH in text:
            offenders.append(str(path.relative_to(REPO)))
    assert not offenders, f"Update links to .backlog/spike/: {offenders}"


def test_backlog_spike_findings_exist() -> None:
    spike_dir = REPO / ".backlog/spike"
    expected = [
        "0032-asca-rule-validity.md",
        "0033-positional-slots-and-identity-subscripts.md",
        "0034-subscript-notation-index-asca-brassica.md",
        "0035-asca-khoisan-click-representation.md",
        "0036-asca-class-letter-mappings.md",
        "0037-asca-ejective-notation.md",
        "0038-index-feature-matrices-to-asca-targets.md",
        "0039-index-syllable-position-u-hash.md",
        "0040-inter-segment-whitespace-phoneme-boundaries.md",
        "0041-io-optionals-asca-and-convention.md",
        "0042-breve-vowel-notation.md",
        "0043-field-isolation-compile-validation.md",
        "0044-asca-native-per-field-validation.md",
    ]
    missing = [name for name in expected if not (spike_dir / name).is_file()]
    assert not missing, f"Missing spike findings: {missing}"
