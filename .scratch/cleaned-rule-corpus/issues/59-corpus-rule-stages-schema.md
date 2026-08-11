Type: task
Status: resolved

# Corpus rule `stages` schema cutover

## Question

Implement ADR-0011: replace corpus-rule `input`/`output` with uniform **`stages`**, keep compile-time chain expansion, one-shot cutover.

## Decision (grill 2026-08-09)

See [ADR-0011](../../../docs/adr/0011-corpus-rule-stages.md) and glossary **Stages** / **Corpus rule** in `CONTEXT.md`.

### Schema

- Required: `stages` (list of opaque Index-shaped strings), `raw`, `source`.
- Optional: `env`, `exception`, `comment`, `sporadic`, `status` (unchanged roles).
- **Delete** `input` / `output` from YAML SoT.
- Length 2 = single step; ≥ 3 = chain; `[]` + `status: skipped` = hold-out.
- After parse, &lt; 2 non-empty stages → `stages: []` + `status: skipped` (do not abort regen).
- At most one `env` and one `exception` per corpus rule (never per-stage).

### Parse

- Isolate `env` / `exception` from the Index line; split the change spine on **every** `→` into `stages`.
- Existing field cleanups may still make `stages` diverge from `raw` (same policy as former I/O).

### Compile

- Per-stage string normalizers (e.g. tilde) run on each stage **before** pairing.
- Expand to `n−1` ASCA rules: `stages[i] > stages[i+1]`; copy rule-level `env` / `exception` / `comment` / `sporadic` onto each step.
- Empty `stages` emit nothing.

### Cutover

- No dual-read of legacy `input`/`output`.
- Regen YAML + update parsers, `asca_compile` chains/tilde, `DiachronicSeries`, inventory, tests, and docs in one change set.
- Sync ticket 03 schema answer; fold remaining ADR-0005 doc lag ([adr-0005 ticket 05](../../adr-0005-no-ingest-split/issues/05-update-docs-and-parent-map.md)) into this work where it still mentions opaque I/O / parse-time chain split.

## Acceptance criteria

- [x] Regenerated `index_diachronica_parsed.yml` uses `stages` only (no rule `input`/`output`).
- [x] Chain examples compile to the same sequential ASCA steps as before (env stamped on each step).
- [x] Inventory regen + tests green; skip-shaped rows use `stages: []`.
- [x] Docs/ADR-0005 amendment text no longer prescribe opaque `input`/`output` as the spine.
- [x] CONTEXT.md already matches; keep it aligned if wording drifts during impl.

## Answer

Implemented ADR-0011 one-shot cutover:

- **Parse:** `IndexDiachronicaParser` emits `stages` (split on every `→` after env/exception isolation); hold-outs use `stages: []` + `status: skipped`.
- **Compile:** `expand_chained_corpus_rule` expands adjacent stage pairs; `normalize_corpus_rule_tilde_fields` normalizes per stage before pairing.
- **Inventory:** `validate_corpus_rule` compiles via `PhonologicalRuleSet` (no direct `RuleChange` on corpus rows).
- **Regenerated** `data/diachronica/index_diachronica_parsed.yml` with `stages` only.
- **Docs:** ticket 03 schema answer + ADR-0005 amendment synced to ADR-0011.

## References

- Grill: chained rule I/O → uniform `stages` (2026-08-09)
- [ADR-0011](../../../docs/adr/0011-corpus-rule-stages.md)
