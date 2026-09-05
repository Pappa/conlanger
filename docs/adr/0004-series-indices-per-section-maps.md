# Keep Index Diachronica series indices; map per section

Subscript digits and letters on segments in Index Diachronica (e.g. `x₂`) are **correspondence-series indices**, not decorative typography. They are unusable in applier parsers as-is. Resolution uses **per-section mapping tables** extracted from the HTML (citations, phonology tables, inferable rule context), not silent stripping to the base letter.

## Considered Options

- **Retain indices + per-section maps (chosen)** — preserves author intent in `raw`; index fields expand when mapped.
- **Strip subscripts at ingest** — simpler strings; wrong when the letter stands for a series member.
- **Expand only inside the ASCA compiler** — rejected as the long-term home; maps belong to parse/ingest policy, not a compile-only secret.

## Consequences

- Ingest must not “fix” indices by deleting them (neither from `raw` nor as a silent fallback for unmapped tokens).
- Unmapped series should be reportable (e.g. validation inventory / `unmapped_series` style), not silently guessed.
- Applier compilers consume ASCA-parseable strings from index fields; `raw` remains the Index audit surface.

## Amendment (2026-08)

Wayfinder session on **subscript notation** (`CONTEXT.md`) and owner clarification:

### Interim (current correction phase)

- Leave **correspondence-series indices** literal in index `input`/`output`/`env`/`exception` when no section map exists.
- Let **compile validation** report failures (e.g. `unknown_character` for `₁`).
- Do **not** assign `status: skipped` pre-emptively for unmapped indices — skipping is for post-correction triage per [ADR-0010](0010-historical-fidelity-class-first-status.md) and the edit ladder (ticket 04), not for missing map rows.

### Amendment (2026-08-18)

Grill [72](.scratch/rule-index/issues/72-grill-series-mapping-manual-sot.md) retired parse-time `series_mappings.csv` expansion:

- **No parse-time series CSV** — I/O-inferred rows conflated sound changes with notation definitions and could collapse multi-step rules to identity.
- Corpus **stages** / env / exception keep Index-shaped **correspondence-series indices** until compile mapping; **collective subscripts** fan out to member indices at parse via `parser_config.yml` `series_expansions` ([ticket 73](.scratch/rule-index/issues/73-grill-series-mapping-config-sot.md)).
- **Series mappings** (index → segment) live in `config/compile/asca/compiler_config.yml` at compile ([ticket 75](.scratch/rule-index/issues/75-implement-compiler-config-series-mappings.md)); replaces `PIE_LARYNGEAL_ALIASES` Python.
- `section_abbreviations.yml` is advisory only; not regenerated from extract tooling.
- Inventory `ok` may drop when incorrect parse expansions are removed; that regression is accepted.

See also [ADR-0012](0012-index-diachronica-corrections-overlay.md) for the corrections overlay.

### Amendment (2026-08-18, grill 73)

Split **series expansion** (parse, global collectives in `parser_config.yml`) from **series mapping** (compile, hierarchical `compiler_config.yml`). Correspondence-series indices remain literal in the YAML index until compile; collectives expand to flat member lists in index fields with `raw` unchanged.

### Target (parse-time expansion) — superseded 2026-08-18

**Superseded** by amendment above. Future expansion (if any) is config-driven per ticket 73, not `series_mappings.csv` at parse.

### Out of scope for this ADR (separate tickets)

- **Positional slots** (`C₁`, `V₂`) and **identity subscripts** (`V₀`) — require ASCA reference/alpha syntax mapping, not correspondence-series tables.
- **`status: skipped`** during bulk correction — deferred until class-first passes are exhausted.

### Glossary

See `CONTEXT.md`: **Subscript notation**, **Correspondence-series index**, **Correspondence series**, **Collective subscript**, **Positional slot**, **Identity subscript**.
