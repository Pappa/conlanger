Type: task
Status: wontfix
Blocked by: 08

# Rule-derived probe synthesis for compile validation

## Answer

**Wontfix.** Use ASCA directly for **compile validation** via existing `validate_asca` (`asca run` + baseline wordlist). Rule-derived candidate word generation (formerly "probe synthesis") is redundant with a parse/apply gate for error clustering — ~98% of provisional inventory failures are Tier 1–2 syntax, catchable without per-rule word synthesis. See tickets [11](11-minimal-extract-only-ingest.md) → [12](12-full-corpus-validation-inventory.md) → cluster-driven [13+](13-correction-pass-template.md).

## Question

How should **compile validation** drive **Tier 4** ASCA runtime checks when `asca run` is wordlist-dependent — and what is the MVP for a **Python probe synthesizer** that builds per-rule input words from compiled rule fields?

## Notes

- Context: [Create an ASCA validator for SoundChangeRule](08-asca-validator.md) uses `asca run` on a fixed five-word probe list; Tier 1–3 run on every apply, but Tier 4 errors (e.g. `UnevenSet`, `LonelySet`, `DeletionOnlySeg`, insertion env errors) only fire when probes **match** the rule. See [../research/asca-rule-validity.md](../research/asca-rule-validity.md) §5.
- **Decision (charting):** implement option **B** — rule-derived probes on top of existing `asca run`, **not** a Rust `ParsedRules::try_from` wrapper in the first slice.
- **Language:** Python only (`src/conlanger/tools/`, alongside `asca_validator.py`).
- **Input surface:** **post-mapping** compiled strings — the same `input` / `output` / `env` / `exception` fields that `SoundChangeRule` emits after group-letter expansion (not Index-shaped `raw`).
- **MVP synthesizer scope:**
  - IPA literals from rule tokens
  - ASCA groupings → representative segments (static table, same spirit as `group_mappings.csv`)
  - Feature matrices → representative segments (small feature→segment table)
  - Sets `{a,b,c}` → one probe per choice + a default
  - Env `_` focus → prefix/focus/suffix word shapes
  - Boundaries `#`, `$`, `%` → word-edge / multi-syllable variants
  - Insertion (`*` / `∅` input) → env-shaped probes where env is present
  - Emit **3–8** `.wsca` lines per rule
- **Fallback:** frozen global baseline lexicon (`tests/fixtures/asca_probe_words.wsca` + optional ASCA-test-derived shapes) when synthesis is partial; record **coverage** metadata (`full` | `partial` | `baseline_only`) for validation CSV / debugging.
- **Deferred (phase 2 / fog):** structures `⟨CV⟩`, ellipses, alpha notation, references, env sets, optional counts — synthesizer reports partial coverage; do not block MVP.
- **Out of scope for this ticket:** seeded random fuzz (optional nightly script later); porting ASCA’s full unit-test corpus wholesale.
- **Integration:** `validate_asca` uses synthesized probes by default when `probe_words` is omitted (or explicit `synthesize_probes=True` flag — decide at implementation).
- **Tests:** deterministic unit tests on `synthesize_probes(rule_dict) → list[str]`; integration cases where fixed probes miss Tier 4 but synthesized probes catch it (e.g. uneven set with plosive in input).
- Skills: `/prototype` if a stub helps review the table layout before full integration.
- AFK-capable once claimed.

## Deliverables

1. `src/conlanger/tools/asca_probe_synth.py` (name may vary) — public `synthesize_probes(...)` API.
2. Static tables (CSV or inline dict) for grouping→segment and feature→segment representatives.
3. Wire into `validate_asca` (default probe path).
4. `tests/conlanger/tools/test_asca_probe_synth.py` + extended validator integration tests.
5. Brief note in ticket **Answer** on coverage limits and example before/after (fixed probe vs synthesized).
