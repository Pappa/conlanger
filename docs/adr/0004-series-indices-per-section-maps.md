# Keep Index Diachronica series indices; map per section

Subscript digits and letters on segments in Index Diachronica (e.g. `x₂`) are **correspondence-series indices**, not decorative typography. They are unusable in applier parsers as-is. Resolution uses **per-section mapping tables** (as with `legacy/data/series_mapping.yaml`), not silent stripping to the base letter.

## Considered Options

- **Retain indices + per-section maps (chosen)** — preserves author intent in `raw`; corpus fields expand when mapped.
- **Strip subscripts at ingest** — simpler strings; wrong when the letter stands for a series member.
- **Expand only inside the ASCA compiler** — rejected as the long-term home; maps belong to parse/ingest policy, not a compile-only secret.

## Consequences

- Ingest must not “fix” indices by deleting them (neither from `raw` nor as a silent fallback for unmapped tokens).
- Unmapped series should be reportable (e.g. validation inventory / `unmapped_series` style), not silently guessed.
- Applier compilers consume ASCA-parseable strings from corpus fields; `raw` remains the Index audit surface.

## Amendment (2026-08)

Wayfinder session on **subscript notation** (`CONTEXT.md`) and owner clarification:

### Interim (current correction phase)

- Leave **correspondence-series indices** literal in corpus `input`/`output`/`env`/`exception` when no section map exists.
- Let **compile validation** report failures (e.g. `unknown_character` for `₁`).
- Do **not** assign `status: skipped` pre-emptively for unmapped indices — skipping is for post-correction triage per [ADR-0010](0010-historical-fidelity-class-first-status.md) and the edit ladder (ticket 04), not for missing map rows.

### Target (parse-time expansion)

- At **HTML→YAML parse**, expand mapped **correspondence-series indices** and **collective subscripts** (`Xₓ`) in corpus fields to **ASCA-parseable** targets (IPA segments, feature matrices, sets) — same pattern as **Symbol** normalization and legacy `resolve_series_labels()`.
- **`raw`** always keeps Index subscripts unchanged.
- Section **`abbreviations`** (and/or package CSV keyed by section index) holds the mapping; longest-prefix section match wins; global `*` fallback allowed.
- **Unmapped** tokens stay literal in corpus fields (option A); validation fails; cluster-driven map authoring adds rows.

### Out of scope for this ADR (separate tickets)

- **Positional slots** (`C₁`, `V₂`) and **identity subscripts** (`V₀`) — require ASCA reference/alpha syntax mapping, not correspondence-series tables.
- **`status: skipped`** during bulk correction — deferred until class-first passes are exhausted.

### Glossary

See `CONTEXT.md`: **Subscript notation**, **Correspondence-series index**, **Correspondence series**, **Collective subscript**, **Positional slot**, **Identity subscript**.
