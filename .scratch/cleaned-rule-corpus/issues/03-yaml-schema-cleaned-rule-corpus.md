Type: grilling
Status: resolved

# YAML schema for the cleaned rule corpus

## Question

What is the YAML schema for the cleaned, applier-neutral **rule corpus** — required fields, nesting, how sets / environments / exceptions / series indices are represented — such that compilers can target ASCA (and later Brassica)?

## Notes

- Skills: `/grill-with-docs` (or grilling + domain-modeling).
- Must respect ADRs 0002, 0004, 0005; HTML remains current SoT until cleaned corpus is adopted (ADR-0006).
- Existing `index_diachronica.yml` / `index_diachronica_ai.yml` are migration references, not the schema answer by default.
- Prose-env mapping is still fog; schema should not pretend that spike is solved.
- HTML SoT filename: `notebooks/data/index_diachronica_original.html`; `source` uses e.g. `index_diachronica_original.html:1288`.
- Follow-on: [Resolve abbreviations unsupported by ASCA and Brassica](06-resolve-applier-unsupported-abbreviations.md); [Normalise segment feature matrices for appliers](07-normalise-segment-features.md).

## Answer

### Document shape

```yaml
abbreviations:          # global abbreviation table (string → string)
sections:
  - section: <title>    # required
    index: <dotted>     # required; ancestry key for abbreviation inheritance
    citation: ...       # optional
    abbreviations: {}   # optional section overrides (more specific wins)
    rules: []           # optional (heading-only sections omit)
```

### Corpus rule fields

| Field | Required | Notes |
|-------|----------|--------|
| `input` | yes | Index Diachronica–shaped string; `""` when `status: skipped` |
| `output` | yes | same |
| `raw` | yes | original HTML rule-line text; multi-line via `\|` literal block |
| `source` | yes | `index_diachronica_original.html:<line>` — first line of the span |
| `env` | no | absent = any environment |
| `exception` | no | absent = no exceptions |
| `status` | no | `needs-validation` \| `skipped`; omit = `ok`. **Amended by** [Historical fidelity vs valid-but-inaccurate fallback](04-historical-fidelity-vs-validity.md) (replaces earlier `skipped` reason string). Reasons/`description` live in a temporary validation CSV, not on the rule. |

Field values stay **opaque Index Diachronica–shaped strings** (sets, series indices, feature matrices inline) — not an ASCA AST and not deep YAML structure. Compilers + abbreviation tables own applier targeting. Series indices are retained in strings; resolution uses hierarchical **abbreviation tables**. Feature-matrix synonym policy is deferred to ticket 07. Edge *splits* (one HTML line → multiple corpus rules) deferred; interim is `status: skipped`.

### Ingest note

Parse `index_diachronica_original.html` with **lxml** (non-strict HTML).

### Glossary locked this ticket

**Abbreviation**, **Abbreviation table**, **Raw**, **Source**, **Feature matrix** — see `CONTEXT.md`. (**Skipped** / **Rule status** / **Validation report** refined in ticket 04.)
