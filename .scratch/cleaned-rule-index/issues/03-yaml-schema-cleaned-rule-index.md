Type: grilling
Status: resolved

# YAML schema for the cleaned rule index

## Question

What is the YAML schema for the cleaned, applier-neutral **rule index** — required fields, nesting, how sets / environments / exceptions / series indices are represented — such that compilers can target ASCA (and later Brassica)?

## Notes

- Skills: `/grill-with-docs` (or grilling + domain-modeling).
- Must respect ADRs 0002, 0004, 0005; HTML remains current SoT until cleaned index is adopted (ADR-0006).
- Existing `index_diachronica.yml` / `index_diachronica_ai.yml` are migration references, not the schema answer by default.
- Prose-env mapping is still fog; schema should not pretend that spike is solved.
- HTML SoT filename: `data/diachronica/index_diachronica_original.html`; `source` uses e.g. `index_diachronica_original.html:1288`.
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
| `stages` | yes | ordered opaque Index-shaped strings; length 2 = single step; ≥ 3 = chain; `[]` + `status: skipped` = hold-out |
| `raw` | yes | original HTML rule-line text; multi-line via `\|` literal block |
| `source` | yes | `index_diachronica_original.html:<line>` — first line of the span |
| `env` | no | **Environment** — absent = any |
| `exception` | no | **Exception** — absent = none |
| `sporadic` | no | **Uncertainty** — rule application is sporadic or optional; gloss stripped from fields |
| `comment` | no | Inline editorial prose for **this rule line** — qualifiers, semicolon tails, parenthetical notes stripped from fields; see [ticket 30](30-rule-comment-field-on-index-rules.md) |
| `status` | no | **Rule status** — e.g. `skipped` for hold-outs; reasons in **validation report** |

Field values in `stages`, `env`, and `exception` are opaque Index-shaped strings — not an ASCA AST. See **Corpus rule**, **Stages**, **Applier-neutral**, **Subscript notation**, **Rule comment** in `CONTEXT.md`. Abbreviation / feature policy: tickets 06, 07.

### Schema amendment (2026-08-09)

Uniform **`stages`** spine per [ADR-0011](../../docs/adr/0011-index-rule-stages.md) — replaces required `input`/`output`; compile expands adjacent pairs at compile time.

### Schema amendment (2026-08)

Optional **`comment`** on index rules — [Rule comment field on index rules](30-rule-comment-field-on-index-rules.md). Inline prose stripped from rule fields at parse; **`raw`** unchanged. Distinct from section-level **`comments`** array.

### Ingest note

Parse `index_diachronica_original.html` with **lxml** (non-strict HTML).

### Glossary

See `CONTEXT.md` — **Corpus rule**, **Raw**, **Source**, **Environment**, **Exception**, **Rule status**, **Validation report**.
