Type: task
Status: resolved
Blocked by: 01

# Create an ASCA validator for SoundChangeRuleSet

## Question

Implement an ASCA validator that takes a `SoundChangeRuleSet` instance, returns `True` when the rule is valid for ASCA, and raises an error with an appropriate message when it is not. Validity criteria come from [What counts as a valid ASCA rule string?](01-valid-asca-rule-string.md) findings: [../research/asca-rule-validity.md](../research/asca-rule-validity.md) (pinned to **asca 0.10.2**; follow §5 internal pipeline for Python).

## Notes

- Wayfinder role: AFK task that makes post-compile ASCA checking concrete so [Correction workflow for invalid rules](05-correction-workflow-invalid-rules.md) can decide workflow against a real validator (does not deliver the cleaned corpus itself).
- Aligns with ADR-0003 (validate after applier compile): this is the ASCA-side check, not an HTML→YAML ingest gate.
- Spec source of truth for accept/reject behaviour: `.scratch/cleaned-rule-corpus/research/asca-rule-validity.md` — whole-rule form, per-field checklists, operators, ID failure patterns, CLI/`ParsedRules::try_from` validation (§4), and the lexer→parser→split_into_subrules→runtime map for a Python implementation (§5).
- API contract (required):
  - **Input:** an instance of `SoundChangeRuleSet` (`src/conlanger/tools/SoundChangeRuleSet.py`).
  - **Valid:** return `True`.
  - **Invalid:** raise an error whose message explains the failure appropriately (surface ASCA/syntax reason when available; prefer names mappable to `RuleSyntaxError` / `RuleRuntimeError`).
- Prefer driving validation via asca’s parse path (`ParsedRules::try_from` / CLI as documented in the research file) or a faithful Tier 1–3 port — not a docs-only ad-hoc grammar. Optional Tier 4 via apply-on-dummy-words.
- Target installed CLI/crate: **asca 0.10.2**.
- AFK-capable once claimed; add unit tests covering valid and invalid cases drawn from the research checklists, known Index Diachronica failure patterns, and the fixture below.

## Fixture work (required before / with validator tests)

1. Randomly sample **500** `p.schg` rules from `data/diachronica/index_diachronica_original.html` (record the RNG seed in the ticket Answer or a short note beside the fixture).
2. For each sampled rule, **guess** the correct **ASCA** field forms (what should go into `SoundChangeRuleSet` / `RuleChange` so the emitted rule string is ASCA-valid under 0.10.2 — e.g. `∅`/`*` for delete/insert, ASCA feature names, ` > `-ready segments, env with `_`, `|`/`//` exception content without prose).
3. **Append one CSV row per sample** to [`tests/fixtures/sound_change_rules.csv`](../../../tests/fixtures/sound_change_rules.csv).
   - Preserve existing columns and existing rows (HTML-extract expectations already in the file).
   - Extend the schema as needed so each new row carries the guessed ASCA fields (recommended: `asca_input`, `asca_output`, `asca_env`, `asca_exception`, plus a `kind` or similar discriminator such as `html_extract` vs `asca_guess` so parser tests and validator tests can filter). Empty optional ASCA env/exception cells mean “omit that part”.
   - Keep `id` / `source` / `raw` pointing at the HTML line for auditability.
4. Validator unit tests should load the `asca_guess` rows (via pandas) and assert validate-success (or documented expected failure) against `SoundChangeRuleSet` built from those guessed fields.

## Answer

**Gist:** `validate_asca(SoundChangeRuleSet) -> True` lives in `src/conlanger/tools/asca_validator.py`; invalid rules raise `ASCAValidationError` with ASCA’s Syntax/Runtime Error text. Validation drives installed **asca 0.10.2** via `asca run` on a probe wordlist (hybrid Tier 1–4; same path as inventory). Fixture: 500 `asca_guess` rows (seed **20260802**) appended to `tests/fixtures/sound_change_rules.csv` — **370** validate ok, **130** documented expected failures (`asca_expect_ok=False`).

**API:**
```python
from conlanger.tools.asca_validator import validate_asca, ASCAValidationError
validate_asca(sound_change_rule)  # True or raises
```

**Artifacts:**
- Validator: [`src/conlanger/tools/asca_validator.py`](../../../src/conlanger/tools/asca_validator.py)
- Tests: [`tests/conlanger/tools/test_asca_validator.py`](../../../tests/conlanger/tools/test_asca_validator.py)
- Fixture + seed note: [`tests/fixtures/sound_change_rules.csv`](../../../tests/fixtures/sound_change_rules.csv), [`tests/fixtures/sound_change_rules.asca_guess_seed.txt`](../../../tests/fixtures/sound_change_rules.asca_guess_seed.txt)
- Regenerator: [`sample_asca_guess_fixtures.py`](../../../src/conlanger/scripts/sample_asca_guess_fixtures.py) (`--replace-guesses`, seed `20260802`)

**Guess heuristics (for fixtures):** strip ID prose; `0`→`∅`; bare `ː`→`:[+long]`; syllabic mark→`:[+syll]`; feature aliases (`voiced`→`voice`); subscripts→ASCII; unwrap I/O optionals; space-parallel I/O→commas; ensure env `_`. Remaining failures are mostly unknown ID groupings/features, nested/prose junk, and Tier-4 delete-only-segment cases.

**Note:** A thin Rust `ParsedRules::try_from` helper was attempted but blocked by crates.io network in this environment; CLI `asca run` is the shipped check (still surfaces ASCA error enums in messages).
