# Index Diachronica corrections overlay keyed by rule id

Maintainers can replace individual Index rule lines without editing `index_diachronica_original.html`. Overrides live in `data/diachronica/index_diachronica_corrections.yml` as a `rules` list of entries with `rule.id`, `rule.content` (Unicode Index rule string, no `<sub>` markup), and optional `rule.reason`.

When a correction exists for a rule id, that string is the rule’s **`raw`** after HTML text extraction — an updated phonological claim while provenance **`source`** still points at the original HTML line. The HTML file remains the published artifact; corrections are project overlays for known errata.

## Considered Options

- **YAML overlay keyed by rule id (chosen)** — stable across HTML edits that would shift positional indices; aligns with inventory and debug CSVs.
- **Edit the HTML file in place** — recreates hand-edit bottlenecks and loses a clean separation between published Index and project fixes.
- **Nested section/index/idx structure** — harder to match and merge; rejected in grill 72.

## Consequences

- Parse loads corrections after `<sub>`→Unicode normalisation and element text extract; before Manual mapping on the working copy.
- Unknown correction keys warn at regen; they do not block parse.
- Distinct from **Manual mapping** (substring rewrite on working copy, `raw` unchanged) and from correspondence-series expansion (deferred to config grill / ADR-0004 amendment).
