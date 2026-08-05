Type: grilling
Status: resolved
Blocked by: None

# Parse-time resolution for correspondence-series indices

## Question

When and how should **correspondence-series indices** and **collective subscripts** be resolved relative to HTML→YAML ingest — and what happens for unmapped tokens and `status: skipped` during the correction phase?

## Notes

- Glossary: `CONTEXT.md` — **Subscript notation** (four uses); this ticket covers **correspondence-series index** and **collective subscript** only.
- Prior art: `legacy/data/series_mapping.yaml`, `legacy/scripts/parse_index_diachronica.py` (`resolve_series_labels`).
- ADR: [0004-series-indices-per-section-maps](../../../docs/adr/0004-series-indices-per-section-maps.md) (amended 2026-08).
- **Positional slots** and **identity subscripts** — separate tickets; not decided here.
- Follow-on implementation: [Implement parse-time correspondence-series expansion](27-implement-parse-time-correspondence-series-expansion.md).

## Answer

### Parse-time, not compile-time

Expand at **HTML→YAML parse** (same seam as **Symbol** normalization), not inside `RuleChange` / compile transforms. Owner intent for ADR-0004 was interim literal tokens until the correction loop surfaced clusters — **not** permanent compile-time deferral.

### Target representation

Rewrite corpus `input`/`output`/`env`/`exception` to **ASCA-parseable** phonological notation (IPA segments, feature matrices, sets) when a section map entry exists. Do not invent a parallel applier-neutral symbol set beyond ASCA's segment/matrix/set vocabulary (grouping-letter syntax differences remain compile concerns).

**`raw`** always preserves Index subscripts unchanged (`s₁`, etc.) for audit and [historical fidelity](04-historical-fidelity-vs-validity.md).

### Mapping source

- Section **`abbreviations`** table in cleaned YAML (hierarchical: section overrides global).
- Package CSV keyed by section index acceptable (migrate/consolidate `legacy/data/series_mapping.yaml`).
- Longest-prefix section match; optional global `*` fallback rows.
- Values are ASCA-valid targets (see comments in legacy `series_mapping.yaml`).

### Unmapped tokens (option A)

When no map row exists for a token (e.g. `s₁` in a section without a defined series):

- Leave the literal token in corpus fields.
- Do **not** set `status: skipped`.
- Let compile validation fail (`unknown_character`, etc.); cluster drives map authoring.

### Skip policy during correction phase

**No pre-emptive `status: skipped`** for unmapped correspondence-series indices or validation failures still being worked through correction passes 14+.

Apply `status: skipped` only after class-first transforms are exhausted, per edit ladder (ticket 04) / ADR-0010 — e.g. ASCA-unrepresentable with clear phonology, valid-but-inaccurate rewrite forbidden, trailing-comment hold-outs. Permanent skips: project owner.

Current corpus: zero `status: skipped` rules (correct for this phase).

### Collective subscripts

`Hₓ`, `sₓ`, etc. — same parse-time map mechanism (map full token or subscript `ₓ` to set expansion, e.g. `sₓ` → `{ s, ʃ }`).

### Not in scope here

- **Positional slots** (`C₁C₂ → C₂`) — ASCA reference/alpha syntax; spike required.
- **Identity subscripts** (`V₀V₀ → V₀`) — ASCA co-reference syntax; spike required.
- **Section-local abbreviations** (`TŠ`, `TS`) — separate abbreviation mechanism, not subscripts.
